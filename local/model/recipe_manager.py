import bcrypt
import db_init
import os

import psycopg2

from local.model.user import User


class RecipeManager:
    def __init__(self, db_conn):
        db_init.init_database(db_conn)
        self.conn = db_conn

    def searchRecipes(self, name):
        cur = self.get_cursor()
        partialName = [x.strip() for x in name.split(' ')]
        sqlQuery = "SELECT * FROM RECIPES WHERE "
        for partial in partialName:
            sqlQuery += "rName LIKE '%" + partial + "%' OR"
        sqlQuery = sqlQuery[:-2]
        cur.execute(sqlQuery)
        record = cur.fetchall()
        return record

    def getUser(self, username):
        cur = self.get_cursor()
        cur.execute("""
            SELECT * FROM USERS WHERE username = %s
            """, username)
        record = cur.fetchall()
        return record

    def createUser(self, username, password):
        cur = self.get_cursor()
        p_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()
        cur.execute("""
            INSERT INTO USER (username, passwordHash)
            VALUES (%s, %s);
            RETURNING uid;
            """, (username, p_hash))

        uid = cur.fetchone()[0]

        self.commit()
        cur.close()

        return User(self, uid, username, p_hash)

    def new_from_env(self):
        return RecipeManager(
            psycopg2.connect(os.environ['DATABASE'])
        )

    def get_cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()
