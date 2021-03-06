import bcrypt
import db_init
import os

import psycopg2
from typing import List, Tuple

from datetime import date

from model.recipe import Recipe


class RecipeManager:
    def __init__(self, db_conn):
        db_init.init_database(db_conn)
        self.conn = db_conn

    def searchRecipes(self, name):
        cur = self.get_cursor()
        partialName = ['%' + x.strip() + '%' for x in name.split(' ')]
        sqlQuery = """
            SELECT recipes.*, owner.*
            FROM recipes
            JOIN users
                AS owner
                ON owner.uid = recipes.owner_id
            WHERE """ + " OR ".join(["rName LIKE %s"] * len(partialName)) + ";"
        cur.execute(sqlQuery, partialName)
        records = cur.fetchall()
        cur.close()

        return (Recipe.new_from_combined_record(self, record) for record in records)

    def search_by_ingredient(self, ingr, limit = 10):
        cur = self.get_cursor()
        cur.execute("""
            SELECT recipes.*, owner.*
            FROM requires_ingredient
            JOIN recipes ON requires_ingredient.rid = recipes.rid
            JOIN users
                AS owner
                ON owner.uid = recipes.owner_id
            WHERE iname = %s
            LIMIT %s;
        """, (ingr.iname, limit))

        results = (Recipe.new_from_combined_record(self, record) for record in cur.fetchall())
        cur.close()
        return results

    def recent_recipes(self, user = None, limit = 5):
        cur = self.get_cursor()
        cur.execute("""
            SELECT
                recipes.*,
                owner.*,
                MAX(datemade) as last_date
            FROM recipes
            JOIN dates_made ON recipes.rid = dates_made.rid
            JOIN users
                AS owner
                ON owner.uid = recipes.owner_id
            %%%
            GROUP BY recipes.rid, owner.uid
            ORDER BY last_date DESC
            LIMIT %s;
        """
        .replace('%%%', (
            'WHERE dates_made.uid = %s'
            if user != None
            else ''
        )), (
            (limit,)
            if user == None
            else (user.uid, limit)
        ))

        results = (Recipe.new_from_combined_record(self, record) for record in cur.fetchall())
        cur.close()
        return results

    def recipes_by_week(self, after = date(1970, 1, 1), limit = 999) -> List[Tuple[date, int]]:
        cur = self.get_cursor()
        cur.execute("""
            SELECT
                make_date(date_part('year', datemade)::int, 1, 1) + (7 * date_part('week', datemade)::int) as week,
                COUNT(DISTINCT rid)
            FROM dates_made
            WHERE datemade > %s
            GROUP BY week
            ORDER BY week
            LIMIT %s;
        """, (after, limit))
        results = cur.fetchall()
        cur.close()
        return results


    @staticmethod
    def new_from_env():
        return RecipeManager(
            psycopg2.connect(os.environ['DATABASE'])
        )

    def get_cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def disconnect(self):
        self.conn.close()
