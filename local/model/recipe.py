import datetime
import uuid

from psycopg2.extras import execute_values

from model.ingredient import Ingredient
from model.user import User

class Recipe:
    def __init__(self, manager, rid, servings, time, name, equip, owner, ingr, steps):
        self.manager = manager
        self.rid = rid
        self.servings = servings
        self.time = time
        self.name = name
        self.equipment = equip
        self.owner = owner
        self.ingredients = ingr
        self.steps = steps

    def new_from_record(manager, record):
        rid = record[0]
        cur = manager.get_cursor()

        # Retrieve ingredients
        cur.execute("SELECT iname,amount FROM requires_ingredient WHERE rid = %s;", (rid,))
        ingredients = dict(
            (Ingredient.get_ingredient(manager, ingr_rec[0]), ingr_rec[1])
            for ingr_rec in cur
        )

        # Retrieve steps
        cur.execute("""
            SELECT stepnum, description FROM steps WHERE rid = %s ORDER BY stepnum;
        """, (rid,))
        steps = [
            step_rec[1]
            for step_rec in cur
        ]

        # Retrieve equipment
        cur.execute("SELECT ename FROM requires_equipment WHERE rid = %s;", (rid,))
        equipment = cur.fetchall()
        cur.close()

        # Retrieve owner
        owner = User.get_user_by_uid(manager, record[4])

        # Produce recipe
        return Recipe(
            manager,
            rid,
            record[1],
            record[2],
            record[3],
            equipment,
            owner,
            ingredients,
            steps
        )

    def datesMade(self):
        cur = self.manager.get_cursor()
        rid = self.id
        cur.execute("SELECT dateMade FROM DATE_MADE WHERE RID = %s", rid)
        record = cur.fetchall()
        return record

    def markMade(self, user):
        cur = self.manager.get_cursor()
        uid = user.Uid
        rid = self.rid
        for ingredient in self.ingredients:
            if (ingredient not in user.get_owned_ingr()) or \
                    (user.get_owned_ingr()[ingredient] - self.ingredients[ingredient] < 0):
                print("You do not have sufficient ingredient to make this recipe")
                return
            user.substractOwnedIngr(ingredient, self.ingredients[ingredient])
        cur.execute("""
            INSERT INTO DATE_MADE (uid, RID, dateMade) 
            VALUES (%s, %s, %s);
            """, (uid, rid, datetime.datetime.now()))
        self.manager.commit()
        cur.close()

    def changeServings(self, targetServings):
        return dict(
            (ingredient[0], ingredient[1] * (targetServings / self.servings))
            for ingredient in self.ingredients.items()
        )

    def getRID(self):
        return self.rid

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

        execute_values(cur, """
            INSERT INTO requires_ingredient
            VALUES %s;
        """, [
            (rid, ingredient[0].iname, ingredient[1])
            for ingredient in ingredients.items()
        ])

        manager.commit()
        cur.close()

        recipe = Recipe(
            manager,
            rid,
            servings,
            prep_time,
            name,
            equipment,
            owner,
            ingredients,
            steps
        )

        recipe.save_equipment()
        recipe.save_steps()

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
        """, (self.servings, self.time, self.name, self.owner.uid, self.rid))
        self.manager.commit()
        cur.close()

    def save_equipment(self):
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
        """, [(self.rid, ename) for ename in self.equipment])

        self.manager.commit()

    def save_steps(self):
        cur = self.manager.get_cursor()

        # Insert new values
        execute_values(cur, """
            INSERT INTO steps(rid, stepnum, description)
            VALUES %s
            ON CONFLICT (rid, stepnum) DO UPDATE SET description = EXCLUDED.description;
        """, [
            (self.rid, step[0], step[1])
            for step in enumerate(self.steps)
        ])

        # Clean out any old values
        cur.execute("""
            DELETE FROM steps
            WHERE rid = %s
                AND stepnum >= %s;
        """, (self.rid, len(self.steps)))

        self.manager.commit()

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
