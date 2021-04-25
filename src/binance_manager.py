from binance_client import BinanceClient
from binance.client import Client
import db as datebase
import asyncio
from functools import wraps, partial, partialmethod
import app_logger
import datetime as dt
import typing as typing

_logger = app_logger.get_logger(__name__)

class BinanceManager():
    def __init__(self, binance_client:BinanceClient, db: datebase.Db):
        self.client = binance_client
        self.db = db
        self._tasks: list[asyncio.Task] = []
    
    def load_stock_exchange_info_task(self):
        async  def task():
            while True:
                _logger.debug(f'Run task...')
                stock_info = await self.client.get_stock_exchange_info()
                insert_res = await self.db.insert_stock_exchange_info(stock_info)
                _logger.debug(f'Insert id ${type(insert_res)}')
                _logger.debug(f'Sleep...')
                await asyncio.sleep(60)
        self._run_tasks(task, name = 'load_furures_klines_task')

    def load_furures_klines_task(self):
        async  def task():
            symbols : list[list] = await self.get_all_usdt_future_symbols()
            startTime=startTime=dt.datetime(2021, 4, 1, tzinfo=dt.timezone.utc)
            while True:
                if symbols:
                    _logger.debug(f'Load klines from: {startTime}...')
                    klines = await self.client.get_futures_continous_klines(pair=symbols[0], startTime=startTime.timestamp()*1000, endTime=dt.datetime.utcnow().timestamp()*1000, interval=Client.KLINE_INTERVAL_1HOUR)
                    if not klines:
                        _logger.warn(f'Invalid pair: {symbols[0]}')
                    startTime += dt.timedelta(hours=1)
                    _logger.debug(f'Load klines: {klines}')
                _logger.debug(f'Sleep...')
                await asyncio.sleep(10)
        self._run_tasks(task, name = 'load_furures_klines_task')
            
    async def get_all_usdt_future_symbols(self) -> list[list]:
        import re
        symbols = await self.client.get_all_futures_symbols() or []
        if symbols:
            regex_symbol = re.compile(r'^[\w]{1,8}USDT$', re.IGNORECASE)
            symbols = list(set([s['pair']
                for s in symbols if regex_symbol.fullmatch(s['symbol']) and s['contractType'] == "PERPETUAL" and s['status'] == "TRADING"]))
        return symbols
    
    def _run_tasks(self, task:typing.Awaitable, name: str, restart = True, **kwargs) -> asyncio.Task:
        import sys
        def done_callback(res_task:asyncio.Task):
            _logger.debug(f'Done {res_task}')
            
            err = None
            try:
                err = res_task.exception()
            except asyncio.exceptions.CancelledError as e:
                err = e
            except BaseException as e:
                err = e
            if err:
                _logger.error(err)
                
            if err and restart and not isinstance(err, asyncio.exceptions.CancelledError): ## != 'force_shutdown':
                run()
            else:
                if res_task in self._tasks:
                    self._tasks.remove(res_task)
        def run():            
            res_task = asyncio.create_task(task(**kwargs), name=name)
            res_task.add_done_callback(done_callback)
            self._tasks.append(res_task); 
            
        run() 
    
    def get_tasks(self):
        return self._tasks
    
    def stop_all_tasks(self):
        for t in self._tasks:
            if not t.cancelled():
                t.cancel('force_shutdown')