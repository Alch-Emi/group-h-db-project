import os
import psycopg2

def init_database(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            uid             SERIAL      PRIMARY KEY,
            username        VARCHAR(50) NOT NULL UNIQUE,
            password_hash   VARCHAR(60) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS recipes(
            rid             SERIAL      PRIMARY KEY,
            servings        INT         NOT NULL,
            prep_time       INT         NOT NULL,
            rName           VARCHAR(50) NOT NULL,
            owner_id        INT         NOT NULL,
            FOREIGN KEY(owner_id) REFERENCES users(uid)
        );

        CREATE TABLE IF NOT EXISTS steps(
            rid             INT         NOT NULL,
            stepnum         INT         NOT NULL,
            description     TEXT        NOT NULL,
            FOREIGN KEY(rid) REFERENCES recipes(rid),
            UNIQUE(rid, stepnum)
        );

        CREATE TABLE IF NOT EXISTS ingredients(
            iname           VARCHAR(50) PRIMARY KEY NOT NULL,
            unit            VARCHAR(25),
            storage_location VARCHAR(25)
        );

        CREATE TABLE IF NOT EXISTS ingredient_ownership(
            uid             INT         NOT NULL,
            iname           VARCHAR(50) NOT NULL,
            qtyOwned        INT         NOT NULL,
            FOREIGN KEY(uid) REFERENCES users(uid),
            FOREIGN KEY(iname) REFERENCES ingredients(iname),
            PRIMARY KEY(uid, iname)
        );

        CREATE TABLE IF NOT EXISTS requires_equipment(
            rid             INT         NOT NULL,
            ename           VARCHAR(50) NOT NULL,
            FOREIGN KEY(rid) REFERENCES recipes(rid),
            PRIMARY KEY(rid, ename)
        );

        CREATE TABLE IF NOT EXISTS requires_ingredient(
            rid             INT         NOT NULL,
            iname           VARCHAR(50) NOT NULL,
            amount          INT         NOT NULL,
            FOREIGN KEY(rid) REFERENCES recipes(rid),
            FOREIGN KEY(iname) REFERENCES ingredients(iname),
            PRIMARY KEY(rid, iname)
        );

        CREATE TABLE IF NOT EXISTS dates_made(
            id              SERIAL      PRIMARY KEY,
            uid             INT         NOT NULL,
            rid             INT         NOT NULL,
            dateMade        TIMESTAMP   NOT NULL DEFAULT NOW(),
            FOREIGN KEY(uid) REFERENCES users(uid),
            FOREIGN KEY(rid) REFERENCES recipes(rid)
        );
    """)
    conn.commit()
    cursor.close()

if __name__ == '__main__':
    conn = psycopg2.connect(os.environ['DATABASE'])
    init_database(conn)
    conn.close()
