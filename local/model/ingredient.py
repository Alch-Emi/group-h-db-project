class Ingredient:
    def __init__(self, manager, iname, unit, storage_location):
        self.manager = manager
        self.iname = iname
        self.unit = unit
        self.storage_location = storage_location

    def __eq__(self, other):
        return self.iname == other.iname

    def __hash__(self):
        return hash(self.iname)

    def register_ingredient(manager, name, unit, storage_location):
        cur = manager.get_cursor()
        cur.execute("""
            INSERT INTO ingredients(iname, unit, storage_location)
            VALUES (%s, %s, %s);
        """, (name, unit, storage_location))
        #TODO Handle conflict

        manager.commit()
        cur.close()

        return Ingredient(manager, name, unit, storage_location)

    def save(self):
        cur = self.manager.get_cursor()
        cur.execute("""
            UPDATE ingredients
            SET
                unit = %s,
                storage_location = %s
            WHERE
                iname = %s;
        """, (self.unit, self.iname, self.iname))

        self.manager.commit()
        cur.close()

    def get_ingredient(manager, iname):
        cur = manager.get_cursor()
        cur.execute("""
            SELECT unit, storage_location
            FROM ingredients
            WHERE iname = %s;
        """, (iname, ))
        data = cur.fetchone()
        cur.close()

        return Ingredient(manager, iname, data[0], data[1]) if data != None else None

    def list_all_ingredients(manager):
        cur = manager.get_cursor()
        cur.execute("""
            SELECT iname, unit, storage_location
            FROM ingredients
        """)

        results = [
            Ingredient(manager, result[0], result[1], result[2])
            for result in cur.fetchall()
        ]

        cur.close()
        return results
