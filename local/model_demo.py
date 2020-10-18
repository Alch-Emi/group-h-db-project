from model import RecipeManager, User, Ingredient

if __name__ == '__main__':
    # Create RecipeManager
    man = RecipeManager.new_from_env()

    # Clean out database (for demo only)
    c = man.get_cursor()
    c.execute("""
        DELETE FROM users WHERE username = 'thea';

        DELETE FROM ingredients
        WHERE iname = 'Flour'
        OR iname = 'Soymilk'
        OR iname = 'Water';
    """)
    c.close()

    # Register new user
    user = User.register_new_user(man, 'emi', 'Secure Password Lol')
    print(f'New User: {user.uid} : {user.username} {user.pass_hash}')

    # Change the user's username
    user.username = 'thea'
    user.save()
    print(f'Changed Username: {user.uid} : {user.username} {user.pass_hash}')

    # Fetch the user from the database
    user = None
    user = User.get_user(man, 'thea')
    print(f'Fetched from database: {user.uid} : {user.username} {user.pass_hash}')

    # Validate user password
    password_matches = user.check_password('tosheraoseatnsr')
    print(f'Password matches: {password_matches}')

    # Update password, and try again
    user.change_password('tosheraoseatnsr')
    user.save()

    password_matches = user.check_password('tosheraoseatnsr')
    print(f'Password matches after update: {password_matches}')

    # Create a few ingredients
    flour = Ingredient.register_ingredient(man, 'Flour', 'cups', 'pantry')
    soymilk = Ingredient.register_ingredient(man, 'Soymilk', 'cups', 'fridge')
    water = Ingredient.register_ingredient(man, 'Water', 'pounds', 'tap')

    # Update an ingredient
    water.unit = 'cups'
    water.save()

    # Retrieve a specific ingredient
    flour = None
    flour = Ingredient.get_ingredient(man, 'Flour')
    print(f'Flour is measured in {flour.unit}')

    # List all ingredients
    print('All available ingredients:')
    for ingredient in Ingredient.list_all_ingredients(man):
        print(f'\t{ingredient.iname}')
