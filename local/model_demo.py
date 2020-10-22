from model import RecipeManager, User, Ingredient, Recipe

if __name__ == '__main__':
    # Create RecipeManager
    try:
        man = RecipeManager.new_from_env()
    except KeyError:
        print("Make sure you set $DATABASE to a database url, like user:pass@host:port/db")
        exit(1)

    # Clean out database (for demo only)
    old_thea = User.get_user(man, 'thea')
    if old_thea != None:
        old_thea.delete()
    c = man.get_cursor()
    c.execute("""
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
    brown_sugar = Ingredient.register_ingredient(man, 'Brown Sugar', 'cups', 'pantry')
    almond_milk = Ingredient.register_ingredient(man, 'Almond Milk', 'cups', 'fridge')
    vanilla = Ingredient.register_ingredient(man, 'Vanilla', 'tbs', 'pantry')
    baking_so = Ingredient.register_ingredient(man, 'Baking Soda', 'tsp', 'pantry')
    chocolate_chips = Ingredient.register_ingredient(man, 'Chocolate Chips', 'cups', 'pantry')
    rice = Ingredient.register_ingredient(man, 'Rice', 'cups', 'pantry')

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

    # Create some recipes
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
    cookies = Recipe.register_recipe(
        man,
        'Chocolate Chip Cookies',
        36,
        25,
        ['oven', 'baking sheet'],
        user,
        {
            oil: 3.6,
            brown_sugar: 1,
            almond_milk: 0.25,
            vanilla: 1,
            flour: 2,
            baking_so: 1,
            baking_pow: 1,
            salt: 1,
            chocolate_chips: 1
        },
        [
            'Preheat the oven to 350 degrees',
            'Mix oil, sugar',
            'Add almond milk, vanilla',
            'Combine dry ingredients seperately, leaving out the chocolate chips',
            'Mix dry ingredients with wet ingredients',
            'Add chocolate chips',
            'Dolop onto baking sheet',
            'Bake 5m'
        ]
    )
    rice = Recipe.register_recipe(
        man,
        'Rice',
        8,
        60,
        ['rice cooker'],
        user,
        {
            rice: 2
        },
        [
            'Add washed rice to rice cooker with 2 cups water',
            'Turn on and cook'
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
    print('\nRecipes:')
    for recipe in [pancakes, cookies, rice]:
        print(f'\t{recipe.name}')
        print('\t\tIngredients:')
        for ingr, ammt in recipe.ingredients.items():
            print(f'\t\t\t{ingr.iname}:   {ammt} {ingr.unit}')
        print('\t\tSteps:')
        for step in recipe.steps:
            print(f'\t\t\t{step}')

    # Display with modified servings
    print('\n Ingredients for feeding 10 people')
    for ingr, ammt in pancakes.changeServings(10).items():
        print(f'\t{ingr.iname}:   {ammt} {ingr.unit}')

    # Search for a recipe
    print('\nSearch results for "cake":')
    for recipe in man.searchRecipes('cake'):
        print(f'\t{recipe.name}')

    # Create a new recipe for the delete demo
    sugar_water = Recipe.register_recipe(
        man,
        'Sugar Water',
        1,
        2,
        [],
        user,
        {
            water: 2,
            sugar: 2,
        },
        [
            'Combine  ingredients & mix'
        ]
    )
    in_database = len(list(man.searchRecipes("Sugar"))) > 0;
    print(f"\nSugar water successfully created: {in_database}")

    # Delete recipe
    sugar_water.delete()
    in_database = len(list(man.searchRecipes("Sugar"))) > 0;
    print(f"Sugar water successfully deleted: {not in_database}")

    # Create a new user with one recipe
    new_user = User.register_new_user(man, "min", "haha i know min's password")
    sugar_water = Recipe.register_recipe(
        man,
        'Sugar Water',
        1,
        2,
        [],
        new_user,
        {
            water: 2,
            sugar: 2,
        },
        [
            'Combine  ingredients & mix'
        ]
    )
    min_exists = User.get_user(man, "min") != None
    print(f"User min created: {min_exists}")
    sugar_water_exists = len(list(man.searchRecipes("Sugar Water"))) > 0;
    print(f"Sugar water created for min: {sugar_water_exists}")
    pancakes_exist = len(list(man.searchRecipes("Pancakes"))) > 0;
    print(f"Pancakes still exist: {pancakes_exist}")

    # Delete the new user (and consiquently all their recipes)
    print("Deleting min...")
    new_user.delete()
    min_exists = User.get_user(man, "min") != None
    print(f"User min exists: {min_exists}")
    sugar_water_exists = len(list(man.searchRecipes("Sugar Water"))) > 0;
    print(f"Sugar water exists: {sugar_water_exists}")
    pancakes_exist = len(list(man.searchRecipes("Pancakes"))) > 0;
    print(f"Pancakes still exist: {pancakes_exist}")

    # Add some ingredients to a user's supply
    user.owned_ingredients = {
        flour: 20,
        water: 999,
        sugar: 10,
        baking_pow: 0,
        salt: 500,
        oil: 500
    }
    user.owned_ingredients[baking_pow] += 50 # Just bought some baking powder
    user.save_owned_ingredients() # VERY IMPORTANT, MAKE SURE YOU CALL THIS
    print(f"\n{user.username}'s Inventory:")
    for (ingr, quant) in user.owned_ingredients.items():
        print(f'\t{ingr.iname}: {quant}')

    # Mark pancakes as made
    pancakes.mark_made(user)
    print(f"{user.username} just made {pancakes.name}")
    print(f"\n{user.username}'s Inventory:")
    for (ingr, quant) in user.owned_ingredients.items():
        print(f'\t{ingr.iname}: {quant}')
    print(f"{pancakes.name} dates made: {pancakes.dates_made()}")

    # Get recent recipes
    # Set up: Create a bunch of demo recipes, and prepare them in order
    user_min = User.register_new_user(man, "min", "haha i know min's password")
    demo_recipes = [
        Recipe.register_recipe(man, f"Demo Recipe {n}", 1, 2, [], user, {}, [])
        for n in range(0,4)
    ]
    for r in demo_recipes:
        r.mark_made(user)
        print(f'{user.username} made recipe {r.name}')
    demo_recipes[0].mark_made(user_min)
    print(f'{user_min.username} made recipe {demo_recipes[0].name}')

    # Get 3 most recent recipes
    recents = man.recent_recipes(limit = 3)
    # Display
    print("The three most recently made recipes are:")
    for r in recents:
        print(f'\t{r.name}')

    # Get 3 most recent recipes for a specific user
    recents = man.recent_recipes(limit = 3, user = user)
    # Display
    print(f"{user.username} recently made:")
    for r in recents:
        print(f'\t{r.name}')

    # Display compatible recipes
    print(f"{user.username}'s most compatible recipes are:")
    for (recipe, compatibility) in user.compatible_recipes():
       print(
           f"\t{recipe.name}, for which thea has {compatibility * 100}% of the ingredients"
       )

    # Clean up
    user.delete()
    c = man.get_cursor()
    c.execute("""
        DELETE FROM ingredients;
    """)
    c.close()
    man.commit()
    man.conn.close()
