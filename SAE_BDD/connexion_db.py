import pymysql
from flask import g
from dotenv import load_dotenv
import os

load_dotenv()


def get_db():
    if 'db' not in g:
        # Print connection details for debugging (remove in production)
        print(f"Connecting to database: {os.getenv('DATABASE')} on host: {os.getenv('MYSQL_HOST')}")

        g.db = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('DATABASE'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()