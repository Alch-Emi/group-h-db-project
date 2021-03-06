import datetime
import uuid

from psycopg2.extras import execute_values

from model.ingredient import *
from model import user

from typing import List
from typing import Tuple
from typing import Generator
from typing import Any

class Recipe:
    def __init__(
        self,
        manager,
        rid,
        servings,
        time,
        name,
        owner_id,
        equip = None,
        owner = None,
        ingr = None,
        steps = None
    ):
        self.manager = manager
        self.rid = rid
        self.servings = servings
        self.time = time
        self.name = name
        self.cached_equip = equip
        self.owner_id = owner_id
        self.cached_owner = owner
        self.cached_ingredients = ingr
        self.cached_steps = steps

    @staticmethod
    def new_from_record(manager, record):
        # Produce recipe
        return Recipe(
            manager,
            record[0],
            record[1],
            record[2],
            record[3],
            record[4]
        )

    @staticmethod
    def new_from_combined_record(manager, record):
        owner = user.User(manager, record[5], record[6], record[7])
        # Produce recipe
        return Recipe(
            manager,
            record[0],
            record[1],
            record[2],
            record[3],
            record[4],
            owner = owner
        )

    @property
    def ingredients(self):
        if self.cached_ingredients == None:
            cur = self.manager.get_cursor()

            # Retrieve ingredients
            cur.execute("""
                SELECT ingredients.*, amount
                FROM requires_ingredient
                JOIN ingredients ON ingredients.iname = requires_ingredient.iname
                WHERE rid = %s;
            """, (self.rid,))

            self.cached_ingredients = dict(
                (Ingredient(self.manager, *ingr_rec[:-1]), ingr_rec[3])
                for ingr_rec in cur
            )

            cur.close()

        return self.cached_ingredients

    @ingredients.setter
    def ingredients(self, new):
        self.cached_ingredients = new

    @property
    def steps(self):
        if self.cached_steps == None:
            cur = self.manager.get_cursor()

            # Retrieve steps
            cur.execute("""
                SELECT stepnum, description FROM steps WHERE rid = %s ORDER BY stepnum;
            """, (self.rid,))

            self.cached_steps = [
                step_rec[1]
                for step_rec in cur
            ]

            cur.close()

        return self.cached_steps

    @steps.setter
    def steps(self, new):
        self.cached_steps = new

    @property
    def equipment(self):
        if self.cached_equip == None:
            cur = self.manager.get_cursor()

            # Retrieve equipment
            cur.execute("SELECT ename FROM requires_equipment WHERE rid = %s;", (self.rid,))
            self.cached_equip = [e for (e,) in cur]

            cur.close()

        return self.cached_equip

    @equipment.setter
    def equipment(self, new):
        self.cached_equip = new

    @property
    def owner(self):
        if self.cached_owner == None and self.owner_id != None:
            # Retrieve owner
            self.cached_owner = user.User.get_user_by_uid(self.manager, self.owner_id)

        return self.cached_owner

    @owner.setter
    def owner(self, new):
        self.cached_owner = new
        self.owner_id = new.uid

    def dates_made(self):
        cur = self.manager.get_cursor()
        rid = self.rid
        cur.execute("SELECT dateMade FROM dates_made WHERE rid = %s", (rid,))
        record = cur.fetchall()
        cur.close()
        return record

    def mark_made(self, user):
        cur = self.manager.get_cursor()
        cur.execute("""
            INSERT INTO dates_made (uid, rid)
            VALUES (%s, %s);

            UPDATE ingredient_ownership
            SET qtyowned = GREATEST(0, qtyowned - requires_ingredient.amount)
            FROM requires_ingredient
            WHERE
                rid = %s
                AND uid = %s
                AND requires_ingredient.iname = ingredient_ownership.iname
            RETURNING ingredient_ownership.iname, qtyowned;
        """, (user.uid, self.rid, self.rid, user.uid))
        self.manager.commit()

        for (iname, amount) in cur:
            user.owned_ingredients[Ingredient(None, iname, None, None)] = amount

        cur.close()

    def changeServings(self, targetServings):
        return dict(
            (ingredient[0], ingredient[1] * (targetServings / self.servings))
            for ingredient in self.ingredients.items()
        )

    def getRID(self):
        return self.rid

    @staticmethod
    def register_recipe(
            manager,
            name,
            servings,
            prep_time,
            equipment,
            owner,
            ingredients,
            steps
    ):
        cur = manager.get_cursor()

        cur.execute("""
            INSERT INTO recipes(servings, prep_time, rname, owner_id)
            VALUES (%s, %s, %s, %s)
            RETURNING rid;
        """, (servings, prep_time, name, owner.uid))
        rid = cur.fetchone()[0]

        insert_ingredients = """
            INSERT INTO requires_ingredient
            VALUES
        """ + \
\
        ", ".join([
                cur.mogrify(f"({rid}, %s, %s)", (ingredient.iname, amt)).decode()
                for (ingredient, amt)
                in ingredients.items()
            ]) + ";\n" if len(ingredients) > 0 else ""

        insert_equipment = """
            INSERT INTO requires_equipment
            VALUES
        """ + \
\
        ", ".join([
                cur.mogrify(f"({rid}, %s)", (ename,)).decode()
                for ename
                in equipment
            ]) + ";\n" if len(equipment) > 0 else ""

        insert_steps = """
            INSERT INTO steps(rid, stepnum, description)
            VALUES
        """ +\
\
        ", ".join([
                cur.mogrify(f"({rid}, %s, %s)", step).decode()
                for step
                in enumerate(steps)
            ]) +\
\
        """
            ON CONFLICT (rid, stepnum) DO UPDATE SET description = EXCLUDED.description;
        """ if len(steps) > 0 else ""

        megaquery = insert_ingredients + insert_equipment + insert_steps

        if len(megaquery):
            cur.execute(megaquery)

        manager.commit()
        cur.close()

        recipe = Recipe(
            manager,
            rid,
            servings,
            prep_time,
            name,
            owner.uid,
            equipment,
            owner,
            ingredients,
            steps
        )

        return recipe

    def save_properties(self):
        cur = self.manager.get_cursor()
        cur.execute("""
            UPDATE recipes
            SET
                servings = %s,
                prep_time = %s,
                rname = %s,
                owner_id = %s
            WHERE
                rid = %s;
        """, (self.servings, self.time, self.name, self.owner_id, self.rid))
        self.manager.commit()
        cur.close()

    def save_equipment(self):
        if self.cached_equip == None:
            return

        cur = self.manager.get_cursor()

        # Clean out any old values
        cur.execute("""
            DELETE FROM requires_equipment
            WHERE rid = %s;
        """, (self.rid, ))

        # Insert new values
        execute_values(cur, """
            INSERT INTO requires_equipment
            VALUES %s;
        """, [(self.rid, ename) for ename in self.cached_equip])

        self.manager.commit()
        cur.close()

        self.equip_changed = False

    def save_steps(self):
        if self.cached_steps == None:
            return

        cur = self.manager.get_cursor()

        # Insert new values
        execute_values(cur, """
            INSERT INTO steps(rid, stepnum, description)
            VALUES %s
            ON CONFLICT (rid, stepnum) DO UPDATE SET description = EXCLUDED.description;
        """, [
            (self.rid, step[0], step[1])
            for step in enumerate(self.cached_steps)
        ])

        # Clean out any old values
        cur.execute("""
            DELETE FROM steps
            WHERE rid = %s
                AND stepnum >= %s;
        """, (self.rid, len(self.cached_steps)))

        self.manager.commit()
        cur.close()

        self.steps_changed = False

    def similar_by_makers(self, limit = 10) -> Generator[Tuple['Recipe', int], Any, Any]:
        cur = self.manager.get_cursor()
        cur.execute("""
            SELECT recipes.*, owner.*, COUNT(users.uid)
            FROM dates_made AS self_dates_made
            JOIN users ON users.uid = self_dates_made.uid
            JOIN dates_made
                AS alt_dates_made
                ON alt_dates_made.uid = users.uid
            JOIN recipes ON alt_dates_made.rid = recipes.rid
            JOIN users
                AS owner
                ON owner.uid = recipes.owner_id
            WHERE self_dates_made.rid = %s
                AND recipes.rid != %s
            GROUP BY recipes.rid, owner.uid
            ORDER BY COUNT(users.uid) DESC
            LIMIT %s;
        """, (self.rid, self.rid, limit))

        results = ((Recipe.new_from_combined_record(self.manager, record), record[8]) for record in cur.fetchall())
        cur.close()
        return results

    def similar_by_ingredient(self, limit = 10) -> Generator[Tuple['Recipe', float], Any, Any]:
        cur = self.manager.get_cursor()
        cur.execute("""
            SELECT
                foreign_recipe.*,
                foreign_owner.*,
                COUNT(DISTINCT common_ingredients.iname)::float / COUNT(DISTINCT all_ingredients.iname)::float
                    AS similarity
            FROM requires_ingredient AS self_ingredients
            JOIN requires_ingredient
                AS common_ingredients
                ON common_ingredients.iname = self_ingredients.iname
            JOIN recipes
                AS foreign_recipe
                ON foreign_recipe.rid = common_ingredients.rid
            JOIN requires_ingredient
                AS all_ingredients
                ON all_ingredients.rid = %s
                OR all_ingredients.rid = foreign_recipe.rid
            JOIN users
                AS foreign_owner
                ON foreign_owner.uid = foreign_recipe.owner_id
            WHERE self_ingredients.rid = %s
                AND foreign_recipe.rid != %s
            GROUP BY foreign_recipe.rid, foreign_owner.uid
            ORDER BY similarity DESC
            LIMIT %s;
        """, (self.rid, self.rid, self.rid, limit))

        results = ((Recipe.new_from_combined_record(self.manager, record), record[8]) for record in cur.fetchall())
        cur.close()
        return results

    def delete(self):
        cur = self.manager.get_cursor()

        cur.execute("""
            DELETE FROM steps WHERE rid = %s;
            DELETE FROM requires_equipment WHERE rid = %s;
            DELETE FROM requires_ingredient WHERE rid = %s;
            DELETE FROM recipes WHERE rid = %s;
        """, [self.rid] * 4)
        self.manager.commit()
        cur.close()

    @staticmethod
    def get_popular_recipes(manager, limit = 10) -> Generator[Tuple['Recipe', int], Any, Any]:
        cur = manager.get_cursor()
        cur.execute("""
            SELECT
                recipes.*,
                owner.*,
                COUNT(DISTINCT dates_made.uid) as n_users
            FROM recipes
            JOIN dates_made ON dates_made.rid = recipes.rid
            JOIN users
                AS owner
                ON owner.uid = recipes.owner_id
            GROUP BY recipes.rid, owner.uid
            ORDER BY n_users DESC
            LIMIT %s;
        """, (limit,))

        results = ((Recipe.new_from_combined_record(manager, record), record[8]) for record in cur.fetchall())
        cur.close()
        return results
