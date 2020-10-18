import db_init
import os

import psycopg2;

class RecipeManager:
    def __init__(self, db_conn):
        db_init.init_database(db_conn)
        self.conn = db_conn

    def new_from_env():
        return RecipeManager(
            psycopg2.connect(os.environ['DATABASE'])
        )

    def get_cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()
