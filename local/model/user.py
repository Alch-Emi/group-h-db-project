import bcrypt

class User:
    def __init__(self, manager, uid, username, pass_hash):
        self.manager = manager
        self.uid = uid
        self.username = username
        self.pass_hash = pass_hash
        self.owned_ingredients = {}

    def substractOwnedIngr(self, ingr_name, qty_used):
        self.owned_ingredients[ingr_name] -= qty_used

    def listDatesMade(self, recipe):
        cur = self.manager.get_cursor()
        uid = self.uid
        rid = recipe.getRID()
        cur.execute("""
            SELECT dateMade FROM DATE_MADE WHERE uid = %s AND RID = %s
            """, uid, rid)
        record = cur.fetchall()
        return record

    def get_owned_ingr(self):
        return self.owned_ingredients

    def add_owned_ingr(self, ingr_name, qty):
        self.owned_ingredients[ingr_name] = qty

    def register_new_user(self, manager, username, password):
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
        #TODO Handle existing user
        self.manager.commit()
        cur.close()

    def get_user(self, manager, username):
        cur = manager.get_cursor()
        cur.execute("""
            SELECT uid, password_hash
            FROM users
            WHERE username = %s;
        """, (username, ))
        user_data = cur.fetchone()
        cur.close()

        return User(manager, user_data[0], username, user_data[1])

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.pass_hash.encode())

    # Requires a call to save() still
    def change_password(self, new_pass):
        self.pass_hash = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode()
