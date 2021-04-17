from fastapi import FastAPI, WebSocket
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from binance_client import BinanceClient
import app_logger

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

@app.get("/symbols", tags=["todos"])
async def get_all_symbols() -> list[dict]:
    #for i in range(3):
    #    await binance_client.get_all_symbols()
    res = await binance_client.get_all_symbols() #or []
    _logger.debug(res)
    return res

@app.get("/todo", tags=["todos"])
async def get_todos() -> dict:
    return { "data": todos }