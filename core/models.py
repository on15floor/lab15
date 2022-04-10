from utils.sqlite_wrap import SQLite3Instance
from config import DataBase
from datetime import datetime


class BaseModel:
    def __init__(self):
        self.db = SQLite3Instance(DataBase.SQL_MAIN)


class NoSmokingStages(BaseModel):
    def __init__(self):
        super().__init__()
        self.table_name = 'main_nosmokingstages'
        self.table_columns = ['name', 'time', 'time_descr', 'text']

    def get_stages(self):
        return self.db.select(self.table_name, self.table_columns, 'order by id')

    @staticmethod
    def get_statistic(time_start: str, time_stop: str,
                      price_start: int, price_stop: int) -> dict:
        time_start = datetime.strptime(time_start, '%Y-%m-%d')
        time_stop = datetime.strptime(time_stop, '%Y-%m-%d')
        time_now = datetime.now()

        days_smoking = time_stop - time_start
        days_no_smoking = time_now - time_stop
        price_avg = (price_start + price_stop) / 2
        money_spent = days_smoking.days * price_avg
        money_saved = days_no_smoking.days * price_stop

        return {
            'time_start': time_start.strftime('%Y-%m-%d'),
            'time_stop': time_stop.strftime('%Y-%m-%d'),
            'time_now': time_now.strftime('%Y-%m-%d'),
            'days_smoking': (time_stop - time_start).days,
            'days_no_smoking': days_no_smoking.days,
            'price_start': price_start,
            'price_stop': price_stop,
            'price_avg': price_avg,
            'money_spent': money_spent,
            'money_saved': money_saved,
        }
