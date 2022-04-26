import json
from datetime import datetime

import pymongo
from bson import json_util

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

    def save_log(self, token, uri, message, status='success'):
        log = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': status,
            'token': token,
            'uri': uri,
            'message': message
        }
        self.collection.insert_one(json.loads(json_util.dumps(log)))
        return {'status': status}

    def save_log_from_request(self, request, message):
        return self.save_log(
            token=request.args.get('token'),
            uri=request.url,
            message=message)
