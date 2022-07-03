import os
import calendar
import pathlib
from datetime import datetime
from collections import defaultdict

import bcrypt
import markdown

from config import STATIC_PATH, PROJECT_PATH
from core.hardcode import weekends, workdays


def get_markdown(fname):
    file_path = os.path.join(STATIC_PATH, f'hints/{fname}')
    with open(file_path) as file:
        return markdown.markdown(file.read())


def check_pw(password, hash_password):
    return bcrypt.checkpw(bytes(password, 'utf-8'), bytes(hash_password, 'utf-8'))


def hash_pw(password):
    password_hash = bcrypt.hashpw(bytes(password, 'utf-8'), bcrypt.gensalt(10))
    return password_hash.decode('utf-8')


def get_ip(request):
    return request.environ.get('HTTP_X_REAL_IP', request.remote_addr)


def get_file_lines_count(file_path):
    with open(file_path, 'r') as f:
        return len(f.readlines())


def _get_file_ext(fname):
    return pathlib.Path(fname).suffix


class Calendar:
    def __init__(self):
        self.dt_now = datetime.now()
        self.this_year = self.dt_now.year
        self.this_date = self.dt_now.strftime('%Y.%m.%d')

    def get_month_abbr(self, month=0) -> str:
        month = month if month else self.dt_now.month
        return calendar.month_abbr[month]

    def _get_digit_days(self, month: int) -> list:
        digit_days = calendar.monthcalendar(self.this_year, month)
        if len(digit_days) != 6:
            digit_days.append([0 for _ in range(7)])
        return digit_days

    def _get_cur_date_fmt(self, month: int, day: int) -> str:
        def fill(num: int) -> str:
            return str(num).zfill(2)

        if day != '&nbsp':
            return f'{self.this_year}.{fill(month)}.{fill(day)}'

    def _is_weekend_day(self, month: int, day: int, day_index: int) -> bool:
        cur_date = self._get_cur_date_fmt(month, day)
        if cur_date:
            if cur_date in workdays:
                return False
            if cur_date in weekends:
                return True
            if day_index in (5, 6):
                return True

        return False

    def _is_current_month(self, month: int) -> bool:
        if month == self.dt_now.month:
            return True
        return False

    def _is_current_day(self, month: int, day: int) -> bool:
        if month == self.dt_now.month and day == self.dt_now.day:
            return True
        return False

    def gen(self):
        result = defaultdict(dict)

        for month in range(1, 13):
            month_addr = self.get_month_abbr(month)
            digit_days = self._get_digit_days(month)

            week_result = dict()
            for w, week in enumerate(digit_days):
                days_result = dict()
                for d, day in enumerate(week):
                    days_result[d] = {
                        'day': str(day) if day else '&nbsp',
                        'weekend': self._is_weekend_day(month, day, d),
                        'current_day': self._is_current_day(month, day)
                    }
                pass
                week_result[w] = days_result
            pass
            result[month_addr] = {
                'weeks': week_result,
                'current_month': self._is_current_month(month)
            }
        pass

        return result


class Statistic:
    indexed_ext = ('.css', '.html', '.js', '.md', '.py', '.sql')
    ignore_dirs = ('venv', 'tmp', '.idea', '.git')

    def get(self):
        result = {k: 0 for k in self.indexed_ext}
        for file in self._get_files():
            result[_get_file_ext(file)] += get_file_lines_count(file)
        return result

    def _get_files(self):
        for root, dirs, fnames in os.walk(PROJECT_PATH):
            for ignore_dir in self.ignore_dirs:
                if ignore_dir in dirs:
                    dirs.remove(ignore_dir)
            for fname in fnames:
                if _get_file_ext(fname) in self.indexed_ext:
                    yield os.path.join(root, fname)
