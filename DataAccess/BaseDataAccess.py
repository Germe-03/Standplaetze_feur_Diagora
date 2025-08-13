import os
import sqlite3

class BaseDataAccess:
    def __init__(self, db_connection_str: str = None):
        self.__db_connection_str = db_connection_str or os.environ.get(
            "DB_FILE", "databank/StandplaetzeDatabank.db"
        )

    def _connect(self):
        return sqlite3.connect(
            self.__db_connection_str
        )

    def fetchone(self, sql: str, params: tuple = ()) -> tuple | None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            row = cur.fetchone()
            cur.close()
        return row

    def fetchall(self, sql: str, params: tuple = ()) -> list[tuple]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
            cur.close()
        return rows

    def execute(self, sql: str, params: tuple = ()) -> tuple[int, int]:
        with self._connect() as conn:
            cur = conn.cursor()
            try:
                cur.execute(sql, params)
                conn.commit()
            except sqlite3.Error:
                conn.rollback()
                raise
            finally:
                lastrowid = cur.lastrowid
                rowcount = cur.rowcount
                cur.close()
        return lastrowid, rowcount