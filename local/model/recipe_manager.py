import bcrypt
import db_init
import os

import psycopg2

from model.user import User
from model.recipe import Recipe


class RecipeManager:
    def __init__(self, db_conn):
        db_init.init_database(db_conn)
        self.conn = db_conn

    def searchRecipes(self, name):
        cur = self.get_cursor()
        partialName = ['%' + x.strip() + '%' for x in name.split(' ')]
        sqlQuery = "SELECT * FROM RECIPES WHERE "
        for partial in partialName:
            sqlQuery += "rName LIKE %s OR "
        sqlQuery = sqlQuery[:-4] + ';'
        cur.execute(sqlQuery, partialName)
        records = cur.fetchall()
        cur.close()

        return (Recipe.new_from_record(self, record) for record in records)

    def new_from_env(self):
        return RecipeManager(
            psycopg2.connect(os.environ['DATABASE'])
        )

    def get_cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()
