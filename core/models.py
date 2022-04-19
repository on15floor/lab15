import math
from datetime import datetime
from typing import List

from core import hardcode
from config import DataBase
from utils.sqlite_wrap import SQLite3Instance


class BaseModel:
    def __init__(self):
        self.db = SQLite3Instance(DataBase.SQL_MAIN)
        self.table_name = str()
        self.table_columns = list()
        self.order_by = 'ORDER BY id'

    def select_from_db(self, columns=None, where=None):
        columns_needed = self.table_columns if columns is None else columns
        condition = self.order_by if not where else f'{where} {self.order_by}'
        return self.db.select(
            table=self.table_name,
            columns=columns_needed,
            where=condition)

    def select_from_db_one(self, columns=None, where=None):
        return self.select_from_db(columns, where)[0]

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
    def get_statistic(context=None) -> dict:
        time_now = datetime.now()
        data = context if context else hardcode.no_smoking

        time_start = datetime.strptime(data.get('time_start'), '%Y-%m-%d')
        time_stop = datetime.strptime(data.get('time_stop'), '%Y-%m-%d')
        price_start = int(data.get('price_start'))
        price_stop = int(data.get('price_stop'))

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
    def __init__(self, page=1):
        super().__init__()
        self.table_name = 'main_blog'
        self.table_columns = ['id', 'icon', 'title', 'intro', 'text', 'date']

        self.current_page = page
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

    def get_post(self, post_id):
        post = self.select_from_db(where=f'WHERE id={post_id}')
        return self._fix_date_fmt(post)

    def get_posts(self):
        posts = self.db.select_limit(
            table=self.table_name,
            columns=self.table_columns,
            where='order by date desc',
            limit=self.posts_per_page,
            offset=self.posts_per_page * (self.current_page - 1))
        return self._fix_date_fmt(posts)

    def commit_post(self, context: dict):
        context.pop('files')    # wtf?
        context.update({'date': datetime.now()})
        self.insert_to_db(values=context)

    def delete_post(self, post_id):
        self.delete_from_db(where=f'WHERE id={post_id}')

    def update_post(self, post_id, context):
        context.pop('files')    # wtf?
        self.update_to_db(values=context, where=f'WHERE id={post_id}')

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
        self.order_by = 'ORDER BY song_name'

        self.instrument_map = {'guitar': 'Гитара', 'ukulele': 'Укулеле'}
        self.instrument = instrument

    @staticmethod
    def _parse_chords(text):
        return set(text.split()) & hardcode.chords

    def get_instrument_name_rus(self):
        return self.instrument_map[self.instrument]

    def get_songs(self):
        songs = self.select_from_db(
            where=f'WHERE instrument="{self.instrument}"')
        for song in songs:
            song['chords'] = ', '.join(self._parse_chords(song['song_text']))
        return songs

    def get_song(self, song_id):
        song = self.select_from_db_one(where=f'WHERE id={song_id}')
        song['chords'] = self._parse_chords(song['song_text'])
        return song

    def delete_song(self, song_id):
        self.delete_from_db(where=f'WHERE id={song_id}')

    def commit_song(self, context):
        context.update({'date': datetime.now()})
        self.insert_to_db(values=context)

    def update_song(self, song_id, context):
        self.update_to_db(values=context, where=f'WHERE id={song_id}')

    def search(self, q):
        songs = self.select_from_db(
            where=f'WHERE instrument="{self.instrument}" '
                  f'AND song_name LIKE "%{q}%"')
        for song in songs:
            song['chords'] = ', '.join(self._parse_chords(song['song_text']))
        return songs


class Birthdays(BaseModel):
    def __init__(self):
        super().__init__()
        self.table_name = 'main_birthdays'
        self.table_columns = ['id', 'name', 'male', 'birthdate',
                              'birthdate_checked', 'comment']
        self.order_by = 'ORDER BY name'

    def get_birthdays(self, scope='all'):
        if scope == 'all':
            birthdays = self.select_from_db()
        else:
            scope_map = {
                'month': f"strftime('%m',birthdate)=strftime('%m',date('now'))",
                'w': f'male={False}',
                'm': f'male={True}',
            }
            where = f'WHERE {scope_map.get(scope)}'
            birthdays = self.select_from_db(where=where)

        return self.update_age(birthdays)

    @staticmethod
    def update_age(birthdays):
        for el in birthdays:
            date_now = datetime.now().date()
            birth_date = datetime.strptime(el['birthdate'], '%Y-%m-%d').date()
            el['age'] = int((date_now - birth_date).days / 365.25)
        return birthdays

    def search(self, q):
        birthdays = self.select_from_db(where=f'WHERE name LIKE "%{q}%"')
        return self.update_age(birthdays)

    def get_birthday(self, birthday_id):
        song = self.select_from_db_one(where=f'WHERE id={birthday_id}')
        return song

    def commit_birthday(self, context):
        context['male'] = bool(context.get('male', None))
        context['birthdate_checked'] = bool(context.get('birthdate_checked', None))
        self.insert_to_db(values=context)

    def delete_birthday(self, birthday_id):
        self.delete_from_db(where=f'WHERE id={birthday_id}')

    def update_birthday(self, birthday_id, context):
        context['male'] = bool(context.get('male', None))
        context['birthdate_checked'] = bool(context.get('birthdate_checked', None))
        self.update_to_db(values=context, where=f'WHERE id={birthday_id}')
