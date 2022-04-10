import sqlite3

from typing import List


class SQLite3Instance:
    def __init__(self, db_path):
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()

    def pure_select(self, sql_statement):
        self.cur.execute(sql_statement)
        return [dict(zip([desc[0] for desc in self.cur.description], row))
                for row in self.cur.fetchall()]

    def select(self, table: str, columns: List[str], where: str = '') -> List[dict]:
        columns_joined = ', '.join(columns) if columns else '*'
        sql = f'SELECT {columns_joined} FROM {table} ' + where
        return self.pure_select(sql)

    def insert(self, table: str, column_values: dict) -> None:
        columns = ', '.join(column_values.keys())
        values = [tuple(column_values.values())]
        placeholders = ', '.join('?' * len(column_values.keys()))
        sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
        self.cur.executemany(sql, values)
        self.con.commit()

    def delete(self, table: str, where: str) -> None:
        sql = f'DELETE FROM {table} ' + where
        self.cur.execute(sql)
        self.con.commit()
