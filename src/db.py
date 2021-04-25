#from pymongo import MongoClient
import motor.motor_asyncio
import app_logger
import typing

_logger = app_logger.get_logger(__name__)

class DbCollections():
    trades_collection = 'trades'
    
    stock_exchange_info_collection = 'stock-exchange-info'
    stock_symbols = 'stock-symbols'
    
    futures_exchange_info_collection = 'futures-exchange-info'
    futures_symbols = 'futures-symbols'

class Db():
    
    __instance = None
    
    def __new__(cls):
        if not hasattr(cls, '__instance'):
            cls.__instance = super(Db, cls).__new__(cls)
        return cls.__instance
    
    def __init__(self, host='localhost', port=27017, db_name = 'binance-web-cache'):
        self._client :motor.motor_asyncio.core.AgnosticClient = motor.motor_asyncio.AsyncIOMotorClient(host = host, port = port)
        self.db : motor.motor_asyncio.core.AgnosticDatabase = self._client[db_name]
        self.db_name : str = db_name
        
        self._collection_names = self.db.list_collection_names()
        self._init_collections()

        
    def _init_collections(self):
        assert(self.db)
        collection_names = self.db.list_collection_names()
        
        
        self.trades_collection : motor.motor_asyncio.core.AgnosticCollection = self.db.get_collection(DbCollections.trades_collection)
        self.stock_exchange_info_collection : motor.motor_asyncio.core.AgnosticCollection = self.db.get_collection(DbCollections.stock_exchange_info_collection)
        self.futures_exchange_info_collection : motor.motor_asyncio.core.AgnosticCollection = self.db.get_collection(DbCollections.futures_exchange_info_collection)
        
    def _create_collection(self, name:str, collection_names : typing.Optional[list[str]] = None) -> motor.motor_asyncio.core.AgnosticCollection:
        assert(self.db)
        collection_names :list[str] = collection_names or self.db.list_collection_names()
        if name not in collection_names:
            return self[name]   
    
    def get_collection(self, name) -> typing.Union[motor.motor_asyncio.core.AgnosticCollection, None]:
        assert(self.db)
        if name in self._collection_names:
            return self.db[name]
        else: return None
    
    @property
    def collection_names(self) -> list[str]:
        return self._collection_names
    
    async def insert_stock_exchange_info(self, data:dict, drop_collection=False):
        if drop_collection:
            self.stock_exchange_info_collection.drop()
        res = await self.stock_exchange_info_collection.insert_one(data)
        _logger.debug(f'Insert stock_exchange_info, id = {res.inserted_id}')
    
    async def insert_futures_exchange_info(self, data:dict, drop_collection=False):
        if drop_collection:
            self.stock_exchange_info_collection.drop()
        res = await self.stock_exchange_info_collection.insert_one(data)
        _logger.debug(f'Insert stock_exchange_info, id = {res.inserted_id}')
    
