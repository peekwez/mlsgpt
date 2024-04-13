import os
import json
import psycopg2
from psycopg2 import sql

from mlsgpt import logger


def create_pg_connection(database: str = "postgres"):
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST"),
        port=os.environ.get("POSTGRES_PORT"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        dbname=database,
    )


class BaseStore(object):
    def __init__(self):
        self.log = logger.get_logger("data-store")
        self.create_database()
        self.conn = create_pg_connection(database=os.environ.get("POSTGRES_DB"))
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_database(self):
        conn = create_pg_connection()
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        try:
            cmd = sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(os.environ.get("POSTGRES_DB"))
            )
            cursor.execute(cmd)
            conn.commit()
            self.log.info(f"Database {os.environ.get('POSTGRES_DB')} created")
        except psycopg2.errors.DuplicateDatabase:
            pass

        cursor.close()
        conn.close()

    def create_table(self):
        cmd = sql.SQL(
            "CREATE TABLE IF NOT EXISTS results (id TEXT, data JSON, created_at TIMESTAMP DEFAULT (now() at time zone 'utc'))"
        )
        self.cursor.execute(cmd)
        self.conn.commit()
        self.log.info("Table results created")

    def close(self):
        self.cursor.close()
        self.conn.close()

    def __del__(self):
        self.close()


class StoreWriter(BaseStore):
    def save(self, result):
        cmd = sql.SQL("INSERT INTO results (id, data) VALUES (%s, %s)")
        request_id = result["request_id"]
        data = json.dumps(result["data"])
        self.cursor.execute(cmd, (request_id, data))
        self.conn.commit()


class StoreReader(BaseStore):
    def fetch(self, request_id):
        cmd = sql.SQL("SELECT data FROM results WHERE request_id = %s")
        self.cursor.execute(cmd, (request_id,))
        return self.cursor.fetchall()
