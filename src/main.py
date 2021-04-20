from functools import cache
from fastapi import FastAPI, WebSocket
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from binance_client import BinanceClient
import binance.exceptions as bex
import app_logger
import re as re

_logger = app_logger.get_logger(__name__)
_logger.debug('test')
_logger.debug('test')
app = FastAPI()

binance_client = BinanceClient()
#binance_client.open_websocket()

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
    #for i in range(3):
    #    await binance_client.get_all_symbols()
    res = await binance_client.get_all_symbols() or []
    _logger.debug(res)
    return res

@app.get("/kline")
async def get_klines() -> list[list]:
    #for i in range(3):
    #    await binance_client.get_all_symbols()
    res = await binance_client.get_all_symbols() #or []
    _logger.debug(res)
    return res

@app.get("/todo", tags=["todos"])
async def get_todos() -> dict:
    return { "data": todos }

@app.get("/testklines")
async def get_usdt_future_symbols() -> list[list]:
    symbols = await binance_client.get_all_futures_symbols() or []
    if symbols:
        regex = re.compile(r'^[\w]{1,8}USDT$', re.IGNORECASE)
        symbols = list(set([s['symbol'] for s in symbols if regex.fullmatch(s['symbol'])]))
        res = []
        if symbols:
            #for pair in symbols:
            #    try:
            #        res += await binance_client.get_futures_continous_klines(pair=pair)
            #    except bex.BinanceAPIException as err:
            #        _logger.warn(err)
            res = await binance_client.get_futures_continous_klines(pair=symbols, limit=10)
    #_logger.debug(res)
    return res