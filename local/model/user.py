import bcrypt
from psycopg2.extras import execute_values

from model.ingredient import *
from model.recipe import Recipe

class User:
    # If owned_ingredients is set to None, it will be populated from the database
    def __init__(self, manager, uid, username, pass_hash, owned_ingredients = None):
        self.manager = manager
        self.uid = uid
        self.username = username
        self.pass_hash = pass_hash
        self.cached_owned_ingredients = owned_ingredients

    @property
    def owned_ingredients(self):
        if self.cached_owned_ingredients is None:
            cur = self.manager.get_cursor()
            cur.execute("""
                SELECT iname,qtyowned
                FROM ingredient_ownership
                WHERE uid = %s;
            """, (self.uid,))
            self.cached_owned_ingredients = dict(
                (Ingredient.get_ingredient(self.manager, record[0]), record[1])
                for record in cur
            )
            cur.close()

        return self.cached_owned_ingredients

    @owned_ingredients.setter
    def owned_ingredients(self, new):
        self.cached_owned_ingredients = new

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

    @staticmethod
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
        if self.cached_owned_ingredients is None:
            return

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
            for (ingr, quant) in self.cached_owned_ingredients.items()
        ))
        self.manager.commit()
        cur.close()

    @staticmethod
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

    @staticmethod
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

            DELETE FROM dates_made
            WHERE uid = %s;

            DELETE FROM users
            WHERE uid = %s;
        """, [self.uid] * 7)

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
                owner.*,
                SUM(LEAST(1.0, qtyowned / ownd_comp.amount)) / (
                    SELECT COUNT(iname)
                    FROM requires_ingredient
                    WHERE requires_ingredient.rid = recipes.rid
                ) AS percent_owned
            FROM ingredient_ownership
            JOIN requires_ingredient
                AS ownd_comp
                ON ownd_comp.iname = ingredient_ownership.iname
            JOIN recipes
                ON ownd_comp.rid = recipes.rid
            JOIN users
                AS owner
                ON owner.uid = recipes.owner_id
            WHERE ingredient_ownership.uid = %s
            GROUP BY recipes.rid, owner.uid
            ORDER BY percent_owned DESC
            LIMIT %s;
        """, (self.uid, limit))

        results = (
            (
                Recipe.new_from_combined_record(self.manager, record),
                record[8]
            )
            for record in cur.fetchall()
        )

        cur.close()
        return results

    def recommended_recipes(self, limit = 10):
        cur = self.manager.get_cursor()

        cur.execute("""
            WITH user_commonality AS (
                SELECT
                    others_made.uid as uid,
                    COUNT(others_made.rid)::float / (
                        SELECT COUNT(rid)
                        FROM dates_made
                        WHERE uid = others_made.uid
                            OR uid = %s
                    ) AS percent_shared
                FROM dates_made AS personally_made
                JOIN dates_made
                    AS others_made
                    ON others_made.rid = personally_made.rid
                WHERE personally_made.uid = %s
                    AND others_made.uid != %s
                GROUP BY others_made.uid
            ),
            users_by_recipe AS (
                SELECT
                    uid,
                    rid,
                    LOG(COUNT(id)) + 1 as degree
                FROM dates_made
                GROUP BY uid, rid
            ),
            recipe_ownership AS (
                SELECT
                    recipes.rid,
                    SUM(LEAST(1.0, qtyowned / ownd_comp.amount)) / (
                        SELECT COUNT(iname)
                        FROM requires_ingredient
                        WHERE requires_ingredient.rid = recipes.rid
                    ) AS percent_owned
                FROM ingredient_ownership
                JOIN requires_ingredient
                    AS ownd_comp
                    ON ownd_comp.iname = ingredient_ownership.iname
                JOIN recipes
                    ON ownd_comp.rid = recipes.rid
                WHERE ingredient_ownership.uid = %s
                GROUP BY recipes.rid
            ),
            scores AS (
                SELECT
                    users_by_recipe.rid,
                    SUM(user_commonality.percent_shared * users_by_recipe.degree) as score,
                    SUM(percent_owned) AS percent_owned
                FROM users_by_recipe
                JOIN user_commonality ON users_by_recipe.uid = user_commonality.uid
                JOIN recipe_ownership ON users_by_recipe.rid = recipe_ownership.rid
                GROUP BY users_by_recipe.rid
            )
            SELECT
                recipes.*,
                users.*,
                percent_owned,
                (percent_owned/2 + 0.5) * score AS recommendation_degree
            FROM scores
            JOIN recipes ON recipes.rid = scores.rid
            JOIN users ON recipes.owner_id = users.uid
            ORDER BY recommendation_degree DESC;
        """, [self.uid] * 4)

        results = (
            (
                Recipe.new_from_combined_record(self.manager, record),
                record[8],
                record[9]
            )
            for record in cur.fetchall()
        )

        cur.close()
        return results
