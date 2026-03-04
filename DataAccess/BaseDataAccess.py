import os
import sqlite3

class BaseDataAccess:
    def __init__(self, db_connection_str: str = None):
        self.__db_connection_str = db_connection_str or os.environ.get(
            "DB_FILE", "Databank/StandplaetzeDatabank.db"
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

    def get_next_id(self, table_name: str, id_column: str) -> int:
        seq_row = self.fetchone("SELECT seq FROM sqlite_sequence WHERE name = ?", (table_name,))
        if seq_row and seq_row[0] is not None:
            return int(seq_row[0]) + 1
        max_row = self.fetchone(f"SELECT MAX({id_column}) FROM {table_name}")
        max_value = max_row[0] if max_row else None
        return (int(max_value) + 1) if max_value is not None else 1
