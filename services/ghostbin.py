from datetime import datetime

import requests


class Gostbin:
    def __init__(self):
        self.url = 'https://pst.klgrth.io/paste/new'

    def post_traceback(self, traceback):
        params = {
            'text': traceback,
            'lang': 'py3tb',
            'expire': -1,
            'title': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        response = requests.post(self.url, params=params)
        return response.url
