import os
import sqlite3
import psycopg2
import psycopg2.extras
from config import DB_PATH, DB_HOST, DB_NAME, DB_USER, DB_PASS, USE_CLOUD


def get_connection():
    if USE_CLOUD:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
        )
        conn.autocommit = True
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
