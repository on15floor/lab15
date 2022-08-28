import os
import calendar
import pathlib
from datetime import datetime
from collections import defaultdict

import bcrypt
import markdown

from config import STATIC_PATH, PROJECT_PATH
from core.hardcode import weekends, workdays
from services.beget import BegetApi


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


def diff_month(d1: datetime, d2: datetime):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


class Calendar:
    def __init__(self):
        self.dt_now = datetime.now()
        self.this_year = self.dt_now.year
        self.this_date = self.dt_now.strftime('%Y.%m.%d')

    def _get_month_abbr(self, month=0) -> str:
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
            month_addr = self._get_month_abbr(month)
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

    @staticmethod
    def calculate(data):
        date_start = data.get('date_start', None)
        date_end = data.get('date_end', None)
        if not date_start or not date_end:
            return

        date_start = datetime.strptime(date_start, '%Y-%m-%d')
        date_end = datetime.strptime(date_end, '%Y-%m-%d')
        if date_start >= date_end:
            return

        delta_years = date_end.year - date_start.year
        return {
            'days': (date_end - date_start).days,
            'month': 12 * delta_years + date_end.month - date_start.month,
            'years': delta_years
        }


class Statistic:
    indexed_ext = ('.css', '.html', '.js', '.md', '.py', '.sql')
    ignore_dirs = ('venv', 'tmp', '.idea', '.git')
    styles = ['primary', 'info', 'secondary', 'danger', 'success', 'warning']

    def get(self):
        return {
            'code_lines': self._get_code_lines(),
            'hosting': BegetApi().get_info()
        }

    def _get_code_lines(self):
        lines_total = 0

        code_lines = {k: 0 for k in self.indexed_ext}
        for file in self._get_files():
            file_lines_count = get_file_lines_count(file)
            code_lines[_get_file_ext(file)] += file_lines_count
            lines_total += file_lines_count

        result = dict()
        i = 0
        for ext, lines_count in code_lines.items():
            result[ext[1:]] = {
                'lines': lines_count,
                'style': f'bg-{self.styles[i]}',
                'precent': round((lines_count / lines_total) * 100, 2)
            }
            i += 1
        return result

    def _get_files(self):
        for root, dirs, fnames in os.walk(PROJECT_PATH):
            for ignore_dir in self.ignore_dirs:
                if ignore_dir in dirs:
                    dirs.remove(ignore_dir)
            for fname in fnames:
                if _get_file_ext(fname) in self.indexed_ext:
                    yield os.path.join(root, fname)
