from pymongo import MongoClient
import app_logger

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
        self._client = MongoClient(host, port)
        self.db = self._client[db_name]
        self.db_name = db_name
        
        self._init_collections()

        
    def _init_collections(self):
        self.trades_collection = self.db[DbCollections.trades_collection]
        self.stock_exchange_info_collection = self.db[DbCollections.stock_exchange_info_collection]
        self.futures_exchange_info_collection = self.db[DbCollections.futures_exchange_info_collection]
        

    def insert_stock_exchange_info(self, data:dict, drop_collection=False):
        if drop_collection:
            self.stock_exchange_info_collection.drop()
        res = self.stock_exchange_info_collection.insert_one(data)
        _logger.debug(f'Insert stock_exchange_info, id = {res.inserted_id}')
    
    def insert_futures_exchange_info(self, data:dict, drop_collection=False):
        if drop_collection:
            self.stock_exchange_info_collection.drop()
        res = self.stock_exchange_info_collection.insert_one(data)
        _logger.debug(f'Insert stock_exchange_info, id = {res.inserted_id}')
        
    