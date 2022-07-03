import re
import json
from datetime import datetime

import pymongo
from bson import json_util

from config import DataBase


URL_REGEX = re.compile(
    r'(https?://[a-z0-9.:]+/)([a-z0-9/._]+)(\?[a-zA-Z0-9=.%]+)?')


class MongoDB:
    def __init__(self):
        mongodb = pymongo.MongoClient(DataBase.MONGO_CONN_STRING)
        database = mongodb.lab15_ru
        self.collection = database.api_requests
        self.logs_limit = 50

    @staticmethod
    def update_logs(logs):
        for log in logs:
            uri = log.get('uri', None)
            if uri:
                match = URL_REGEX.match(uri)
                if match:
                    short_uri = match.group(2)
                    log['short_uri'] = short_uri
            yield log

    def get_logs_all(self):
        logs = self.collection.find().sort("_id", -1).limit(self.logs_limit)
        return list(self.update_logs(logs))

    def get_logs_errors(self):
        logs = self.collection.find({'status': 'error'}).sort("_id", -1).limit(self.logs_limit)
        return list(self.update_logs(logs))

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
