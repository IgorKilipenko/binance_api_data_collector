import typing
from binance.client import Client
from user_config import UserConfig
from binance.websockets import BinanceSocketManager
import binance.exceptions as bexceptions
import binance.helpers as helpers
import asyncio
from functools import wraps, partial, partialmethod
import app_logger
import datetime as dt

_logger = app_logger.get_logger(__name__)

class BinanceClient():
    __instance = None
    _req_cond = asyncio.Condition()
    _req_delay = 0.3
    __req_state = type('__req_state', (), {
        'req_count': 0
    })
    
    def __new__(cls):
        if not hasattr(cls, '__instance'):
            cls.__instance = super(BinanceClient, cls).__new__(cls)
        return cls.__instance
    
    def __init__(self, api_key:str=None, api_secret:str=None):
        if (api_key is None and api_key is None):
            self.client = Client(UserConfig.api_key, UserConfig.api_secret)
        else: 
            self.client = Client(api_key, api_secret)
        self.bm = None
        
    def _async_wrap(func):
        @wraps(func)
        async def run(*args, loop=None, executor=None, **kwargs):
            if loop is None:
                loop = asyncio.get_event_loop()
            pfunc = partial(func, *args, **kwargs)
            #pfunc = partialmethod(func, *args, **kwargs).func
            
            #if BinanceClient.__req_state.req_count >= 5:
            #    _logger.debug(f"start await at {time.time()}, request count = {BinanceClient.__req_state.req_count}")
            #    await asyncio.sleep(BinanceClient._req_delay)
            #    _logger.debug(f"end await at {time.time()}")
                
            res = await loop.run_in_executor(executor, pfunc)
            return res
        return run 
    
        
    def open_websocket(self):
        if self.bm is None:
            self.bm = BinanceSocketManager(self.client, user_timeout=60)
            #self._trade_conn_key = self.bm.start_trade_socket('BNBBTC', self.trade_process_message)
            #<symbol>@kline_<interval>
            self._multiplex_conn_key = self.bm.start_multiplex_socket(['bnbusdt@kline_1m', 'btcusdt@kline_1m'], self.process_multiplex_message)
            self.bm.start()
    
    def trade_process_message(self, msg):
        print("message type: {}".format(msg['e']))
        print(msg)
               
    def process_multiplex_message(self, msg):
        print("stream: {} data: {}".format(msg['stream'], msg['data']))
        
    def watch_trades(self, symbols:list[str]):
        if self.bm is not None:
            if self._watch_trades_conn_key is not None and self._watch_trades_conn_key != False:
                #self.bm.stop_socket(self._watch_trades_conn_key)
                return True
            else:
                self._watch_trades_conn_key = self.bm.start_multiplex_socket([f'{s.lower()}@trade' for s in symbols], self.process_multiplex_message)
                return self._watch_trades_conn_key != False
        
    
    def _process_watch_trades(self, msg) -> None:
        print("stream: {} data: {}".format(msg['stream'], msg['data']))
    
    
    async def get_all_symbols(self) -> typing.Coroutine[typing.Union[list[dict], None], None, None]:
        info = await  self.get_stock_exchange_info()
        if info is not None:
            return info['symbols']
        else: return None
    
    async def get_all_futures_symbols(self) -> typing.Coroutine[typing.Union[list[dict], None], None, None]:
        info = await  self.get_futures_exchange_info()
        if info is not None:
            return info['symbols']
        else: return None
        
    async def get_stock_exchange_info(self) -> typing.Coroutine[typing.Union[dict, None], None, None]:
        info = await BinanceClient._async_wrap(self.client.get_exchange_info)()
        return info
    
    async def get_futures_exchange_info(self) -> typing.Coroutine[typing.Union[dict, None], None, None]:
        info = await BinanceClient._async_wrap(self.client.futures_exchange_info)()
        return info
    
    async  def get_klines0(self, symbol, interval, start_str, end_str=None, limit=500):
        await  BinanceClient._async_wrap(self.client.get_historical_klines)(symbol, interval, start_str, end_str, limit)
    
    async def get_futures_continous_klines(self, pair:typing.Union[list, str]='BNBUSDT', interval:str=Client.KLINE_INTERVAL_1HOUR, contractType='PERPETUAL', startTime=0, endTime=None, limit=None) -> typing.Coroutine[list[list], None, None]:
        res = []
        if not pair:
            return res
        
        assert(isinstance(pair, str) or isinstance(pair, list))
        
        interval_ms = helpers.interval_to_milliseconds(interval)
        assert(interval_ms)
        
        pair = [pair] if isinstance(pair, str) else pair
        #if pair and isinstance(pair, str):
        #    return await BinanceClient._async_wrap(self.client.futures_continous_klines)(pair=pair, interval=interval, contractType=contractType, startTime=startTime, endTime=endTime, limit=limit)
        #    pairs 

        tasks = []
        
        async def tryLoad(pair:str) -> typing.Coroutine[list[list], None, None]:
            res = []
            try:
                res = await BinanceClient._async_wrap(self.client.futures_continous_klines)(pair=pair, interval=interval, contractType=contractType, startTime=startTime, endTime=endTime, limit=limit)
            except bexceptions.BinanceAPIException as err:
                _logger.warn(err)
            return res
        
        for i in range(0, len(pair)):
            tasks.append(tryLoad(pair[i]))
            if i % 5 == 0:
                buffer = await asyncio.gather(
                    *tasks
                )
                res += [b for b in buffer if b]
                tasks.clear()
        
        return res

    
    def calc_max_limit(start_time:typing.Union[str,int,dt.datetime], end_time, interval:str = Client.KLINE_INTERVAL_1DAY):
        interval_ms = helpers.interval_to_milliseconds(interval)
        assert(interval_ms)
        
        if isinstance(start_time, str):
            helpers.date_to_milliseconds()