from pymongo import MongoClient

class DbCollections():
    trades_collection = 'trades'
    exchange_stock_info_collection = 'exchange-info'

class Db():
    
    __instance = None
    
    def __new__(cls):
        if not hasattr(cls, '__instance'):
            cls.__instance = super(Db, cls).__new__(cls)
        return cls.__instance
    
    def __init__(self, host='localhost', port=27017, db_name = 'binance-web-cache'):
        self._client = MongoClient(host, port)
        self.db = self._client[Db.db_name]
        self.db_name = db_name
        self.trades_collection = self.db[DbCollections.trade_collection]
        self.stock_exchange_info_collection = self.db[DbCollections.exchange_info_collection]

    def insert_stock_exchange_info(self, data:dict):
        res = self.stock_exchange_info_collection.insert_one(data)
        print(f'Insert stock_exchange_info, id = {res.inserted_id}')
    
    