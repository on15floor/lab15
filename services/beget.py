import re
import json
from datetime import datetime, timedelta

import requests

from config import Vars

REGEX_TOKEN = re.compile(r'\?token=[a-zA-Z\d]*')
REGEX_LINK = re.compile(r'(https?:\/\/[^?]+)')


class BegetApi:
    TIME_FIELDS = {k: 0 for k in (
        'minutes', 'hours', 'days', 'months', 'weekdays')}

    def __init__(self):
        self.login = Vars.HOST_LGN
        self.password = Vars.HOST_PWD
        self.api_url = 'https://api.beget.com/api/'

    def _url_frmt(self, command) -> str:
        auth = f'login={self.login}&passwd={self.password}'
        return f'{self.api_url}{command}?{auth}&output_format=json'

    def get_info(self):
        response = requests.get(self._url_frmt('user/getAccountInfo'))
        info_json = response.json()
        info = info_json['answer']['result']

        disc_used = info.get('user_quota')
        disc_total = info.get('plan_quota')
        disc_percent = round((disc_used / disc_total) * 100, 2)
        ram_total = info.get('server_memory')
        ram_used = info.get('server_memorycurrent')
        ram_percent = round((ram_used / ram_total) * 100, 2)
        user_days_to_block = info.get('user_days_to_block')
        user_block_date = datetime.now() + timedelta(days=user_days_to_block)
        result = {
            'hardware': {
                'CPU': {
                    'name': info.get('server_name'),
                    'uptime': info.get('server_uptime'),
                    'used_percent': round(info.get('server_loadaverage'), 2),
                },
                'HDD': {
                    'total': disc_total,
                    'used': disc_used,
                    'used_percent': disc_percent
                },
                'RAM': {
                    'total': ram_total,
                    'used': ram_used,
                    'used_percent': ram_percent
                }
            },
            'user_days_to_block': user_days_to_block,
            'user_block_date': user_block_date.strftime("%d-%m-%Y"),
        }
        return result

    def set_time_chunks_size(self, tasks):
        for task in tasks:
            for filed, size in self.TIME_FIELDS.items():
                cur_field_len = len(task[filed])
                if cur_field_len > size:
                    self.TIME_FIELDS[filed] = cur_field_len

    def get_tasks(self) -> list:
        response = requests.get(self._url_frmt('cron/getList'))
        tasks_json = response.json()
        tasks = tasks_json['answer']['result']
        self.set_time_chunks_size(tasks)

        for task in tasks:
            # command _fmt
            command = REGEX_TOKEN.sub('', task.pop('command'))
            task['command'] = REGEX_LINK.search(command).group(1)
            # time _fmt
            time_chunks = []
            for filed, size in self.TIME_FIELDS.items():
                t = task.pop(filed).ljust(size, ' ')
                t = t.replace(' ', '&nbsp')
                time_chunks.append(t)
            task['time'] = '&nbsp'.join(time_chunks)

        return tasks

    def task_del(self, task_id) -> None:
        url = f'{self._url_frmt("cron/delete")}&input_format=json'
        data = {'row_number': task_id}
        requests.get(url=url, params={'input_data': json.dumps(data)})

    def task_change_state(self, task_id: int, state: int) -> None:
        url = f'{self._url_frmt("cron/changeHiddenState")}&input_format=json'
        data = {
            'row_number': task_id,
            'is_hidden': state          # 1 - stop task, 0 - run task
        }
        requests.get(url=url, params={'input_data': json.dumps(data)})
