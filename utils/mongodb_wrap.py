import pymongo

from config import DataBase


class MongoDB:
    def __init__(self):
        mongodb = pymongo.MongoClient(DataBase.MONGO_CONN_STRING)
        database = mongodb.lab15_ru
        self.collection = database.api_requests
        self.logs_limit = 50

    def get_logs_all(self):
        return self.collection.find().sort("_id", -1).limit(self.logs_limit)

    def get_logs_errors(self):
        return self.collection.find({'status': 'error'}).sort("_id", -1).limit(self.logs_limit)
