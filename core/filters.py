from app import app
from datetime import datetime


@app.template_filter('zfill')
def zfill(value, width):
    return str(value).zfill(width)


@app.template_filter('percent_left')
def percent_left(date_start: str, total_days):
    date_start = datetime.strptime(date_start, '%Y-%m-%d')
    date_now = datetime.now()
    date_delta = date_now-date_start
    res = date_delta.days/float(total_days)*100
    return round(res, 2) if res <= 100 else 100
