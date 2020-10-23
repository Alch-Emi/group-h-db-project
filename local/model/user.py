import bcrypt
from psycopg2.extras import execute_values

from model.ingredient import *
from model.recipe import *

class User:
    # If owned_ingredients is set to None, it will be populated from the database
    def __init__(self, manager, uid, username, pass_hash, owned_ingredients):
        self.manager = manager
        self.uid = uid
        self.username = username
        self.pass_hash = pass_hash

        if owned_ingredients == None:
            cur = self.manager.get_cursor()
            cur.execute("""
                SELECT iname,qtyowned
                FROM ingredient_ownership
                WHERE uid = %s;
            """, (self.uid,))
            owned_ingredients = dict(
                (Ingredient.get_ingredient(manager, record[0]), record[1])
                for record in cur
            )
            cur.close()

        self.owned_ingredients = owned_ingredients

    def listDatesMade(self, recipe):
        cur = self.manager.get_cursor()
        uid = self.uid
        rid = recipe.getRID()
        cur.execute("""
            SELECT dateMade FROM dates_made WHERE uid = %s AND RID = %s
            """, (uid, rid))
        record = cur.fetchall()
        cur.close()
        return record

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

        return User(manager, uid, username, pass_hash, {})

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
        #TODO Handle existing user
        self.manager.commit()
        cur.close()

    def save_owned_ingredients(self):
        cur = self.manager.get_cursor()
        cur.execute("""
            BEGIN;

            DELETE FROM ingredient_ownership
            WHERE uid = %s;
        """, (self.uid,))

        execute_values(cur, """
            INSERT INTO ingredient_ownership
            VALUES %s;

            COMMIT;
        """, (
            (self.uid, ingr.iname, quant)
            for (ingr, quant) in self.owned_ingredients.items()
        ))
        self.manager.commit()
        cur.close()

    def get_user_by_uid(manager, uid):
        cur = manager.get_cursor()
        cur.execute("""
            SELECT username, password_hash
            FROM users
            WHERE uid = %s;
        """, (uid, ))
        user_data = cur.fetchone()
        cur.close()

        return User(manager, uid, user_data[0], user_data[1], None) if user_data != None else None

    def get_user(manager, username):
        cur = manager.get_cursor()
        cur.execute("""
            SELECT uid, password_hash
            FROM users
            WHERE username = %s;
        """, (username, ))
        user_data = cur.fetchone()
        cur.close()

        return User(manager, user_data[0], username, user_data[1], None) if user_data != None else None

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.pass_hash.encode())

    def delete(self):
        cur = self.manager.get_cursor()

        cur.execute("""
            DELETE FROM steps
            WHERE rid IN (
                SELECT rid
                FROM recipes
                WHERE owner_id = %s
            );

            DELETE FROM requires_equipment
            WHERE rid IN (
                SELECT rid
                FROM recipes
                WHERE owner_id = %s
            );

            DELETE FROM requires_ingredient
            WHERE rid IN (
                SELECT rid
                FROM recipes
                WHERE owner_id = %s
            );

            DELETE FROM recipes
            WHERE owner_id = %s;

            DELETE FROM ingredient_ownership
            WHERE uid = %s;

            DELETE FROM users
            WHERE uid = %s;
        """, [self.uid] * 6)

        self.manager.commit()
        cur.close()

    # Requires a call to save() still
    def change_password(self, new_pass):
        self.pass_hash = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode()

    # Returns an iterable of tuples, where each tuple is a recipe and it's compatibility,
    # where 1 is fully compatible and < 1 is missing some (but not all) ingredients.
    # Tuples are in order by compatibility, descending.
    def compatible_recipes(self, limit = 10):
        cur = self.manager.get_cursor()

        cur.execute("""
            SELECT
                recipes.*,
                SUM(LEAST(1.0, qtyowned / ownd_comp.amount)) / (
                    SELECT COUNT(iname)
                    FROM requires_ingredient
                    WHERE requires_ingredient.rid = recipes.rid
                ) AS percent_owned
            FROM users
            JOIN ingredient_ownership
                ON ingredient_ownership.uid = users.uid
            JOIN requires_ingredient
                AS ownd_comp
                ON ownd_comp.iname = ingredient_ownership.iname
            JOIN recipes
                ON ownd_comp.rid = recipes.rid
            WHERE users.uid = %s
            GROUP BY recipes.rid
            ORDER BY percent_owned DESC
            LIMIT %s;
        """, (self.uid, limit))

        results = (
            (
                Recipe.new_from_record(self.manager, record),
                record[5]
            )
            for record in cur.fetchall()
        )

        cur.close()
        return results
