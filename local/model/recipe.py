from psycopg2.extras import execute_values

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
