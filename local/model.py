import bcrypt
import db_init
import psycopg2

import os

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

class User:
    def __init__(self, manager, uid, username, pass_hash):
        self.manager = manager
        self.uid = uid
        self.username = username
        self.pass_hash = pass_hash

    def register_new_user(manager, username, password):
        pass_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

        cur = manager.get_cursor()
        cur.execute("""
            INSERT INTO users(username, password_hash)
            VALUES (%s, %s)
            RETURNING uid;
        """, (username, pass_hash))
        #TODO Handle existing user

        uid = cur.fetchone()[0]

        manager.commit()
        cur.close()

        return User(manager, uid, username, pass_hash)

    def save(self):
        cur = self.manager.get_cursor()
        cur.execute("""
            UPDATE users
            SET
                username = %s,
                password_hash = %s
            WHERE
                uid = %s;
        """, (self.username, self.pass_hash, self.uid))
        self.manager.commit()
        cur.close()

if __name__ == '__main__':
    man = RecipeManager.new_from_env()
    user = User.register_new_user(man, 'emi', 'Secure Password Lol')
    print(f'{user.uid} : {user.username} {user.pass_hash}')
    user.username = 'thea'
    user.save()
    print(f'{user.uid} : {user.username} {user.pass_hash}')
