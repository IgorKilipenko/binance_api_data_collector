from asyncio.tasks import Task
from fastapi import FastAPI, WebSocket, BackgroundTasks
import typing as typing
from binance_client import BinanceClient
import app_logger
import re as re
import db as datebase
import asyncio
from binance_manager import BinanceManager


_logger = app_logger.get_logger(__name__)
# _logger.debug('test')
# _logger.debug('test')

app = FastAPI()

binance_manager = BinanceManager(binance_client=BinanceClient(), db=datebase.Db())

##binaceapi_get_stock_exchange_worker : asyncio.Task = None
##binaceapi_get_furures_klines_worker : asyncio.Task = None

@app.on_event("startup")
async def startup_event():
    _logger.info('Server started')
    #binaceapi_get_stock_exchange_worker = asyncio.create_task(load_stock_exchange_info_task())
    # binaceapi_get_furures_klines_worker = asyncio.create_task(binance_manager.load_furures_klines_task())
    # stock_info = await binance_client.get_stock_exchange_info()
    # db.insert_stock_exchange_info(stock_info)
    binance_manager.load_furures_klines_task()

@app.on_event("shutdown")
def shutdown_event():
    _logger.info('Stoped stopped')
    binance_manager.stop_all_tasks()
    ##if binaceapi_get_stock_exchange_worker:
    ##    binaceapi_get_stock_exchange_worker.cancel()

@app.get("/")
async def root():
    return {"message": "Hello World"}

todos = [
    {
        "id": "1",
        "item": "Read a book."
    },
    {
        "id": "2",
        "item": "Cycle around town."
    }
]


@app.get("/symbols")
async def get_all_symbols() -> list[dict]:
    # for i in range(3):
    #    await binance_client.get_all_symbols()
    res = await binance_manager.client.get_all_symbols() or []
    _logger.debug(res)
    return res


@app.get("/kline")
async def get_klines() -> list[list]:
    # for i in range(3):
    #    await binance_client.get_all_symbols()
    res = await binance_manager.client.get_all_symbols()  # or []
    _logger.debug(res)
    return res


@app.get("/todo", tags=["todos"])
async def get_todos() -> dict:
    return {"data": todos}


@app.get("/testklines")
async def get_usdt_future_symbols() -> list[list]:
    symbols = await binance_manager.get_all_usdt_future_symbols()
    res = []
    if symbols:
        res = await binance_manager.client.get_futures_continous_klines(pair=symbols, limit=10)
    return res
