import json

import requests

from config import Vars


class Crontab:
    def __init__(self):
        self.login = Vars.HOST_LGN
        self.password = Vars.HOST_PWD
        self.api_url = 'https://api.beget.com/api/cron/'

    def get_url(self, command) -> str:
        auth = f'login={self.login}&passwd={self.password}'
        return f'{self.api_url}{command}?{auth}&output_format=json'

    def tasks_get(self) -> list:
        response = requests.get(self.get_url('getList'))
        tasks_json = response.json()
        return tasks_json['answer']['result']

    def task_del(self, task_id) -> None:
        url = f'{self.get_url("delete")}&input_format=json'
        data = {'row_number': task_id}
        requests.get(url=url, params={'input_data': json.dumps(data)})

    def task_change_state(self, task_id: int, state: int) -> None:
        url = f'{self.get_url("changeHiddenState")}&input_format=json'
        data = {
            'row_number': task_id,
            'is_hidden': state          # 1 - stop task, 0 - run task
        }
        requests.get(url=url, params={'input_data': json.dumps(data)})
