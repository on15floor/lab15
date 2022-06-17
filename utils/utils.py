import os
import calendar

import bcrypt
import markdown
from datetime import datetime

from config import STATIC_PATH


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


def gen_calender():
    year = datetime.now().year
    for month in range(1, 13):
        days = calendar.monthcalendar(year, month)
        if len(days) != 6:
            days.append([0 for _ in range(7)])
        month_addr = calendar.month_abbr[month]
        yield month_addr, days


def get_this_month_abbr():
    date = datetime.now()
    return calendar.month_abbr[date.month]
