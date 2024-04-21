import os
import json

import psycopg
from openai import OpenAI
from pgvector.psycopg import register_vector
from psycopg import sql
import psycopg.rows

from mlsgpt import logger, constants

from decimal import Decimal

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def create_pg_connection(database: str = "postgres"):
    return psycopg.connect(
        host=os.environ.get("POSTGRES_HOST"),
        port=os.environ.get("POSTGRES_PORT"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        dbname=database,
        autocommit=True,
    )


class DataIO(object):
    def __init__(self, mode:str="r", log: logger.logging.Logger|None = None):
        self.log = log or logger.get_logger("results-table")
        if mode == "r":
            self.conn = create_pg_connection(database=os.environ.get("POSTGRES_DB"))
            self.cursor = self.conn.cursor(row_factory=psycopg.rows.dict_row)
        elif mode == "w":
            self.create_database()
            self.conn = create_pg_connection(database=os.environ.get("POSTGRES_DB"))
            self.cursor = self.conn.cursor(row_factory=psycopg.rows.dict_row)
            self.create_schema()
            self.create_table()
        self.llm = OpenAI()

    def create_database(self):
        conn = create_pg_connection()
        cursor = conn.cursor()

        try:
            cmd = sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(os.environ.get("POSTGRES_DB"))
            )
            cursor.execute(cmd)
            self.log.info(f"Database `{os.environ.get('POSTGRES_DB')}` created")
        except psycopg.errors.DuplicateDatabase:
            pass
        finally:
            cursor.close()
            conn.close()

    def create_schema(self):
        cmd = sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
            sql.Identifier(os.environ.get("POSTGRES_SCHEMA"))
        )
        self.cursor.execute(cmd)
        self.log.info(f"Schema `{os.environ.get('POSTGRES_SCHEMA')}` created")

    def create_table(self):
        cmd = sql.SQL("CREATE EXTENSION IF NOT EXISTS pgcrypto CASCADE")
        self.cursor.execute(cmd)

        cmd = sql.SQL("CREATE EXTENSION IF NOT EXISTS vector CASCADE")
        self.cursor.execute(cmd)
        register_vector(self.conn)

        cmd = sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS {}.results (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                data JSON,
                content TEXT,
                embedding vector(1536),
                created_at TIMESTAMP DEFAULT (now() at time zone 'utc')
            )
            """
        ).format(sql.Identifier(os.environ.get("POSTGRES_SCHEMA")))

        self.cursor.execute(cmd)
        self.log.info("Table `results` created")

    def close(self):
        self.cursor.close()
        self.conn.close()

    def embed(self, text):
        response = self.llm.embeddings.create(input=text, model="text-embedding-3-small")
        return response.data[0].embedding

    def __del__(self):
        self.close()

class DataWriter(DataIO):
    def __init__(self, **kwargs):
        super().__init__(mode="w", **kwargs)

    def save(self, result: dict):
        if "status" in result:
            result.pop("status")
        content = f"Client remarks: {result["data"]["client_remarks"]}: \n Extras:{result["data"]["extras"]}"
        embedding = self.embed(content)
        cmd = sql.SQL("INSERT INTO {}.results (id, data, content, embedding) VALUES (%s, %s, %s, %s)").format(
            sql.Identifier(os.environ.get("POSTGRES_SCHEMA"))
        )
        request_id = result["request_id"]
        data = json.dumps(result["data"], default=decimal_default)
        self.cursor.execute(cmd, (request_id, data, content, embedding))


class DataReader(DataIO):
    def __init__(self, **kwargs):
        super().__init__(mode="r", **kwargs)

    def read(self):
        cmd = sql.SQL(constants.LISTINGS_ALL).format(
            sql.Identifier(os.environ.get("POSTGRES_SCHEMA"))
        )
        self.cursor.execute(cmd)
        return self.cursor.fetchall()

    def search(self, address:str=None, mls_number:str=None):
        conditions = []
        if address:
            conditions.append(f"data->'listing_address'->>'street_address' ILIKE '%{address}%'")

        if mls_number:
            conditions.append(f"data->>'mls_number' = '{mls_number}'")
        
        where_clause = " AND ".join(conditions) if conditions else "TRUE"
        cmd = sql.SQL(constants.LISTINGS_QUERY).format(
            sql.Identifier(os.environ.get("POSTGRES_SCHEMA")),
            sql.SQL(where_clause)
        )
        self.cursor.execute(cmd)
        return self.cursor.fetchall()
    
    def nl_search(self, query: str, threshold: float = 0.3):
        embedding = self.embed(query)
        cmd = sql.SQL(constants.LISTINGS_SEARCH).format(
            sql.Literal(1.0),
            sql.Literal(embedding),
            sql.Identifier(os.environ.get("POSTGRES_SCHEMA")), 
            sql.Literal(1.0), sql.Literal(embedding), sql.Literal(threshold)
        )
        self.cursor.execute(cmd)
        return self.cursor.fetchall()
