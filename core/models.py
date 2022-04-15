import math
from datetime import datetime
from typing import List

import core.hardcode
from config import DataBase
from utils.sqlite_wrap import SQLite3Instance


class BaseModel:
    def __init__(self):
        self.db = SQLite3Instance(DataBase.SQL_MAIN)
        self.table_name = str()
        self.table_columns = list()

    def select_from_db(self, columns=None, where='order by id'):
        columns_needed = self.table_columns if columns is None else columns
        return self.db.select(
            table=self.table_name,
            columns=columns_needed,
            where=where)

    def select_from_db_one(self, columns=None, where='order by id'):
        return self.select_from_db(columns, where)[0]

    def select_limit_from_db(self, columns='*', where='order by id',
                             limit=0, offset=0):
        columns_needed = columns if columns == '*' else self.table_columns
        return self.db.select_limit(
            table=self.table_name,
            columns=columns_needed,
            where=where,
            limit=limit,
            offset=offset)

    def delete_from_db(self, where: str):
        self.db.delete(table=self.table_name, where=where)

    def insert_to_db(self, values: dict):
        self.db.insert(table=self.table_name, column_values=values)

    def update_to_db(self, values: dict, where: str):
        self.db.update(table=self.table_name, column_values=values, where=where)


class NoSmokingStages(BaseModel):
    def __init__(self):
        super().__init__()
        self.table_name = 'main_nosmokingstages'
        self.table_columns = ['name', 'time', 'time_descr', 'text']

    def get_stages(self):
        return self.select_from_db()

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
    def __init__(self, page=1, post_id=1):
        super().__init__()
        self.current_page = page
        self.current_post_id = post_id

        self.table_name = 'main_blog'
        self.table_columns = ['id', 'icon', 'title', 'intro', 'text', 'date']
        self.posts_per_page = 10

        self.pages_count = self._get_pages_count()

    def _get_pages_count(self):
        sql = f'SELECT count(1) FROM {self.table_name}'
        posts_count = self.db.pure_select(sql)[0]

        return math.ceil(posts_count['count(1)'] / self.posts_per_page)

    @staticmethod
    def _fix_date_fmt(posts: List[dict]):
        for post in posts:
            dt = post['date'].split('.')[0]
            time_obj = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
            post['date'] = time_obj.strftime('%d-%m-%y')
        if len(posts) != 1:
            return posts
        return posts[0]

    def get_post(self):
        post = self.select_from_db(where=f'WHERE id={self.current_post_id}')
        return self._fix_date_fmt(post)

    def get_posts(self):
        posts = self.select_limit_from_db(
            where='order by date desc',
            limit=self.posts_per_page,
            offset=self.posts_per_page * (self.current_page - 1)
        )
        return self._fix_date_fmt(posts)

    def commit_post(self, icon, title, intro, text):
        post = {
            'icon': icon,
            'title': title,
            'intro': intro,
            'text': text,
            'date': datetime.now()
        }
        self.insert_to_db(values=post)

    def delete_post(self):
        self.delete_from_db(where=f'WHERE id={self.current_post_id}')

    def update_post(self, icon, title, intro, text):
        post = {
            'icon': icon,
            'title': title,
            'intro': intro,
            'text': text,
        }
        self.update_to_db(values=post, where=f'WHERE id={self.current_post_id}')

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


class Chrods(BaseModel):
    def __init__(self, instrument=''):
        super().__init__()
        self.table_name = 'main_chords'
        self.table_columns = ['id', 'instrument', 'song_text', 'date', 'song_name']
        self.instrument_map = {'guitar': 'Гитара',
                               'ukulele': 'Укулеле'}
        self.instrument = instrument

    @staticmethod
    def _parse_chords(text):
        return set(text.split()) & core.hardcode.chords

    def get_instrument_name_rus(self):
        return self.instrument_map[self.instrument]

    def get_songs(self):
        songs = self.select_from_db(
            where=f'where instrument="{self.instrument}" order by song_name')
        for song in songs:
            song['chords'] = ', '.join(self._parse_chords(song['song_text']))
        return songs

    def get_song(self, song_id):
        song = self.select_from_db_one(where=f'where id={song_id}')
        song['chords'] = self._parse_chords(song['song_text'])
        return song

    def delete_song(self, song_id):
        self.delete_from_db(where=f'WHERE id={song_id}')

    def commit_song(self, instrument, song_name, song_text):
        song = {
            'instrument': instrument,
            'song_name': song_name,
            'song_text': song_text,
            'date': datetime.now()
        }
        self.insert_to_db(values=song)

    def update_song(self, song_id, instrument, song_name, song_text):
        song = {
            'instrument': instrument,
            'song_name': song_name,
            'song_text': song_text
        }
        self.update_to_db(values=song, where=f'WHERE id={song_id}')
