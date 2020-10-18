from model import RecipeManager, User, Ingredient, Recipe

if __name__ == '__main__':
    # Create RecipeManager
    man = RecipeManager.new_from_env()

    # Clean out database (for demo only)
    c = man.get_cursor()
    c.execute("""
        DELETE FROM recipes WHERE rname = 'Pancakes!';
        DELETE FROM users WHERE username = 'thea';

        DELETE FROM requires_ingredient;
        DELETE FROM ingredients;
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
    water = Ingredient.register_ingredient(man, 'Water', 'pounds', 'tap')
    sugar = Ingredient.register_ingredient(man, 'Sugar', 'tbs', 'pantry')
    baking_pow = Ingredient.register_ingredient(man, 'Baking Powder', 'tsp', 'pantry')
    salt = Ingredient.register_ingredient(man, 'Salt', 'tsp', 'cupboard')
    oil = Ingredient.register_ingredient(man, 'Oil', 'tbs', 'cupboard')

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

    # Create a recipe
    pancakes = Recipe.register_recipe(
        man,          # RecipeManager
        'Cakes',  # name
        5,            # servings
        20,           # prep time
        ['Pan', 'Stove'], # equipment
        user,         # recipe owner (should be a User)
        {             # Ingredients
            flour: 1.25,
            water: 1.25,
            sugar: 2,
            baking_pow: 2,
            salt: 0.5,
            oil: 1
        },
        [             # steps
            'Combine dry ingredients & mix',
            'Combine wet ingredients and whisk',
            'Combine wet and dry ingredients and stir briefly',
            'Dolop onto pan and cook, flipping partway through'
        ]
    )

    # Update the name
    pancakes.name = 'Pancakes!'
    pancakes.save_properties()

    # Update the required equipment
    pancakes.equipment.append('Spatula')
    pancakes.save_equipment()

    # Update the steps
    pancakes.steps.append('Enjoy!')
    pancakes.save_steps()

    # Display
    print(f'\n{pancakes.name}')
    print('Ingredients:')
    for ingr, ammt in pancakes.ingredients.items():
        print(f'\t{ingr.iname}:   {ammt} {ingr.unit}')
    print('Steps:')
    for step in pancakes.steps:
        print(f'\t{step}')
