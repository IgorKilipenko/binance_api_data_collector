from datetime import datetime
import typing
from binance.client import Client
from user_config import UserConfig
from binance.websockets import BinanceSocketManager
import asyncio
import time
from functools import wraps, partial, partialmethod
import app_logger

logger = app_logger.get_logger(__name__)

class BinanceClient():
    __instance = None
    __last_time_req = time.time()
    
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
    
   
    def _binance_delay_request(req_function: typing.Callable, min_delay:typing.Optional[float] = 0.3) -> typing.Callable[..., typing.Coroutine[typing.Any, None, None]]:   
        @wraps(req_function)
        async def wrapper(*args,**kwargs):
            _a = args
            state = type('', (), {})()
            state.curr_time = time.time()
            state.global_time = max(BinanceClient.__last_time_req, state.curr_time) + min_delay
            state.delay = max(min_delay - (state.curr_time - state.global_time), 0)
        
            BinanceClient.__last_time_req = max(BinanceClient.__last_time_req, state.curr_time) + min_delay
            print(f"start await at {state.curr_time}")
            await asyncio.sleep(state.delay)
            BinanceClient.__last_time_req = max(BinanceClient.__last_time_req, time.time())
            print(f"stop await at {BinanceClient.__last_time_req}")
            
            pfunc = partialmethod(req_function, *args, **kwargs).func
            return await pfunc(*args, **kwargs)
        
        return wrapper
    
    async def get_all_symbols(self) -> typing.Coroutine[typing.Union[list[dict], None], None, None]:
        info = await  self.get_stock_exchange_info()
        if info is not None:
            return info['symbols']
        else: return None
        
    @_binance_delay_request
    async def get_stock_exchange_info(self) -> typing.Coroutine[typing.Union[dict, None], None, None]:
        info = await BinanceClient._async_wrap(self.client.get_exchange_info)()
        return info
    
    def _async_wrap(func):
        @wraps(func)
        async def run(*args, loop=None, executor=None, **kwargs):
            if loop is None:
                loop = asyncio.get_event_loop()
            pfunc = partial(func, *args, **kwargs)
            return await loop.run_in_executor(executor, pfunc)
        return run 