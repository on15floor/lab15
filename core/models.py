import math

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
        return self.db.select(
            table=self.table_name,
            columns=self.table_columns,
            where='order by id')

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


class Blog(BaseModel):
    def __init__(self, page):
        super().__init__()
        self.current_page = page

        self.table_name = 'main_blog'
        self.table_columns = ['icon', 'title', 'intro', 'text', 'date']
        self.posts_per_page = 10

        self.pages_count = self._get_pages_count()

    def _get_pages_count(self):
        sql = f'SELECT count(1) FROM {self.table_name}'
        posts_count = self.db.pure_select(sql)[0]

        return math.ceil(posts_count['count(1)'] / self.posts_per_page)

    def get_posts(self):
        posts = self.db.select_limit(
            table=self.table_name,
            columns=self.table_columns,
            where='order by date desc',
            limit=self.posts_per_page,
            offset=self.posts_per_page * (self.current_page - 1)
        )

        for post in posts:
            dt = post['date'].split('.')[0]
            time_obj = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
            post['date'] = time_obj.strftime('%d-%m-%y')

        return posts

    def has_next_page(self):
        return self.current_page < self.pages_count

    def has_previous_page(self):
        return self.current_page > 1

    def previous_page_number(self):
        return self.current_page - 1

    def next_page_number(self):
        return self.current_page + 1

    def get_page_count(self):
        return self.pages_count

    def get_page(self):
        return self.current_page
