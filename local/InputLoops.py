"""
@filename - InputLoops.py
@author - Nicholas Antiochos
@author - Caitlin Arf
File that defines all input collection/input loop logic
"""

from model.recipe_manager import RecipeManager
from model.user import User
from model.ingredient import Ingredient
from model.recipe import Recipe

import analytics

import help
import sys
from state import State

PROGRAM_STATE = State.MAIN #TODO change to State.LOGIN once log in functionality complete

def set_program_state(state):
    global PROGRAM_STATE
    PROGRAM_STATE = state

    print('\n' + HEADER_BORDER + ' ' + HEADER_MAP[state] + ' ' + HEADER_BORDER)

INPUT_MSG = "\nEnter command ('help' for more info)\n>"

#Program state headers
HEADER_BORDER = "====="

HEADER_MAP = {
    State.LOGIN: "LOG IN",
    State.INGREDIENT_LIST: "INGREDIENT LIST",
    State.RECIPE_CREATE: "RECIPE CREATION",
    State.RECIPE_LIST: "RECIPE LIST",
    State.MAIN: "RECIPE DB",
    State.RECIPE_VIEW: "RECIPE"
}


#Common commands
QUIT = "quit"
LOGOUT = 'logout'
HELP = "help"
BACK = "back"


#Login Loop Commands
LOGIN = "login"
SIGNUP = "signup"


#Main Loop Commands

SEARCH = "search"
NAME_FLAG = "-n"
INGREDIENT_FLAG = "-i"

COMPATIBLE = "compatible"
RECENT = "recent"
POPULAR = "popular"
MY_RECENT = "myrecent"
CREATE = "create"
INVENTORY = "inventory"
LOGOUT = "logout"

#Recipe Create Commands
TIME = "time"
SERVINGS = "servings"
ADD_STEP = "addStep"
EDIT_STEP = "editStep"
ADD_INGREDIENT_RECIPE = "addIngredient"
DELETE_INGREDIENT = "deleteIngredient"
ADD_EQUIPMENT = "addEquipment"
REMOVE_EQUIPMENT = "removeEquipment"
SAVE = "save"

#Recipe List Commands
SELECT = "select"

#Recipe View Commands
MAKE = "make"
HALVE = "halve"
DOUBLE = "double"
DELETE_RECIPE = "delete"
EDIT_RECIPE = "edit"
SIMILAR = "similar"
RECOMMENDED = "recommended"

#Ingredient List Commands
ADD_INGREDIENT = "add"
REMOVE = "remove"

MANAGER = None
USER = None

def displayIngredients(ingredients):
    """
    Pretty prints a list of ingredients
    :param ingredients: list of ingredients
    :return: None
    """
    objs = ingredients.keys()
    storages = {}
    for ing in objs:
        if ing.storage_location in storages:
            storages[ing.storage_location].append(ing)
        else:
            storages[ing.storage_location] = [ing]

    for key in storages.keys():
        print(key + ": ")
        for ing in storages[key]:
            print("\t", ingredients[ing], ing.unit, ing.iname)


def displayRecipe(recipe):
    """
    Pretty prints a recipe
    :param recipe: recipe
    :return: None
    """

    print(recipe.name)

    dates = list(USER.listDatesMade(recipe))

    if(len(dates) != 0):
        print("(last made", max(dates)[0], ')')
    print()
    print("Author -", recipe.owner.username if recipe.owner else "Unknown", "\n")

    print("Servings:", recipe.servings if recipe.servings is not None else "?")
    print("Prep Time:", recipe.time if recipe.time is not None else "?", "minutes\n")

    if (len(recipe.equipment) > 0):
        print("Required Equipment:")
        for equipment in recipe.equipment:
            print("\t +", equipment)
    else:
        print("No required Equipment")

    print("\nIngredients:")
    ingredients = list(recipe.ingredients.keys())
    for i in range(len(recipe.ingredients)):
        print("\t", recipe.ingredients[ingredients[i]], ingredients[i].unit,
               ingredients[i].iname)

    print("\nDirections:")
    steps = list(recipe.steps)
    for i in range(len(steps)):
        print("\t", i + 1, ") ", steps[i], sep='')

    # TODO dates made?


def displayRecipeList(recipeList):
    """
    Pretty prints a list of recipes with the name and author of each
    :param recipeList: list of recipes
    :return:
    """

    if(len(recipeList) == 0):
        print("No recipes found with the given search criteria.")

    for i in range(len(recipeList)):
        owner = recipeList[i].owner
        author = " - "
        if(owner != None):
            author += owner.username
        else:
            author = ""

        print("\t", i+1, ") ", recipeList[i].name, author, sep='')

def halveRecipe(tokens, recipe):
    """
    function that halves the servings size and ingredient amounts of the given
    recipe.
    :param tokens: Not important
    :param recipe: Recipe object being halved
    :return:
    """
    newServings = recipe.servings/2
    recipe.ingredients = recipe.changeServings(newServings)
    recipe.servings = newServings

def doubleRecipe(tokens, recipe):
    """
    function that doubles the servings size and ingredient amounts of the given
    recipe.
    :param tokens: Not important
    :param recipe: Recipe object being doubled
    :return:
    """
    newServings = 2*recipe.servings
    recipe.ingredients = recipe.changeServings(newServings)
    recipe.servings = newServings


def select(tokens, optional = None):
    """
    returns the index number of the recipe selected
    :param tokens: processed command tokens
    :param optional: N/A
    :return: index of recipe selected
    """
    i = 0
    try:
        i = int(tokens[1])
    except ValueError:
        print("The index you provided is not an integer, please try again")
        return

    return i

def search(tokens, optional = None):
    """
    Searched recipe DB by name or ingredient, taking user to RecipeListView
    :param tokens: processed command tokens
    :param optional: N/A
    :return: N/A
    """
    termIndex = 1
    if tokens[1] == INGREDIENT_FLAG:
        termIndex += 1
        ing = Ingredient.get_ingredient(MANAGER, tokens[2])
        if ing is None:
            print("Ingredient", tokens[2], "does not exist in the database")
        print("Searching for recipes containing '" + tokens[termIndex] + "'")
        return RecipeListLoop(list(MANAGER.search_by_ingredient(ing)))
    elif tokens[1] == NAME_FLAG:
        termIndex += 1
        return search_name(tokens[termIndex])
    else:
        return search_name(tokens[termIndex])

def search_name(name):
    """
    Searches the DB for the recipe with the given name, returning the list of recipes
    :param name: set of terms separated by spaces to search for recipes by
    :return: list of recipe objects
    """
    print("Searching Recipe DB for '" + name + "'")
    return RecipeListLoop(list(MANAGER.searchRecipes(name)))

def deleteRecipe(tokens, recipe):
    """
    Deletes the recipe passed in from the DB if the current user owns it
    :param tokens: N/A
    :param recipe: recipe object being deleted from the DB
    :return: None
    """
    if(USER.username != recipe.owner.username):
        print("This recipe is owned by " + recipe.owner.username + ", you do not have permission to delete it.")
        return

    recipe.delete()

    print("recipe deleted successfully")

    back(tokens)


def editRecipe(tokens, recipe):
    """
    Enter edit mode with the current recipe if the current user owns it
    :param tokens: processed line of input
    :param recipe: recipe to edit
    :return:
    """
    if USER.uid == recipe.owner.uid:
        print("Now editing '", recipe.name, "'", sep='')
        return RecipeCreateLoop(recipe)
    else:
        print("You cannot edit a recipe that is not yours.")


def make(tokens, optional=None):
    """
    Marks the current recipe as made for the given user, updates their ingredient list
    :param tokens: N/A
    :param optional: Recipe being marked as made
    :return:
    """
    if optional is not None:
        if(canMake(USER, optional)):
            optional.mark_made(USER)
            keys = list(USER.owned_ingredients.keys())
            for ing in keys:
                if(USER.owned_ingredients[ing] == 0):
                    USER.owned_ingredients.pop(ing)
            print("recipe made successfully!")
        else:
            print("Could not make recipe, insufficient ingredients.")
    else:
        print("UNKOWN ERROR - Recipe could not be made.")
        return False
    return True


def saveRecipe(tokens, recipe):
    """
    Saves the recipe if it is fully filled in, otherwise gives an error message
    :param tokens: processed line of input
    :param recipe: recipe being saved
    :return:
    """
    ready = True
    if len(recipe.ingredients.keys()) == 0:
        print("Cannot save recipe with zero ingredients")
        ready = False
    if len(recipe.steps) == 0:
        print("Cannot save recipe with no steps")
        ready = False
    if( recipe.servings is None):
        print("Must set servings size of recipe before saving")
        ready = False
    if(recipe.time is None):
        print("Must set prep time of recipe before saving")
        ready = False

    if not ready:
        return
    #displayRecipe(recipe)
    if recipe.rid is not None:
        recipe.delete()

    Recipe.register_recipe(MANAGER, name=recipe.name, prep_time=recipe.time,
                           servings=recipe.servings, equipment=recipe.equipment,
                           owner=USER, steps=recipe.steps,
                           ingredients=recipe.ingredients)

    print(recipe.name + " saved successfully!")
    back(tokens)


def canMake(USER, Recipe):
    """
    Returns true if user can make recipe
    :param USER: user
    :param Recipe: recipe user wants to make
    :return:
    """
    for ingredient in list(Recipe.ingredients.keys()):
        if(ingredient in USER.owned_ingredients):
            if(Recipe.ingredients[ingredient] <= USER.owned_ingredients[ingredient]):
                continue
        return False
    return True

def time(tokens, recipe):
    """
    Adds or updates the time required to make the given recipe
    :param tokens: Processed command tokens
    :param recipe: Recipe having time added or changed
    :return:
    """
    try:
        timeReq = int(tokens[1])
    except(ValueError):
        try:
            timeReq = float(tokens[1])
        except:
            print("Failure to add time, value not a number")
            return

    if (timeReq <= 0):
        print("prep time must be a positive value")
        return

    recipe.time = timeReq
    print("recipe time added successfully")

def servings(tokens, recipe):
    """
    Add or update the number of servings for the given recipe
    :param tokens: Processed command tokens
    :param recipe: Recipe have servings added or changed
    :return:
    """
    try:
        serv = int(tokens[1])
    except(ValueError):
        try:
            serv = float(tokens[1])
        except:
            print("Failure to add servings, value not a number")
            return

    if (serv <= 0):
        print("Servings amount must be a positive value")
        return

    recipe.servings = serv
    print("servings added successfully")

def addStep(tokens, recipe):
    """
    Add a new step to the given recipe
    :param tokens: Processed command tokens
    :param recipe: Recipe that a step is being added to
    :return:
    """

    recipe.steps.append(tokens[1])
    print("Step " + str(len(recipe.steps)) + " added successfully")

def editStep(tokens, recipe):
    """
    Edit a step in the given recipe
    :param tokens: Processed command tokens
    :param recipe: Recipe that the step being edited is from
    :return:
    """
    try:
        num = int(tokens[1])
    except(ValueError):
        print("Failure to edit step, stepNum not an integer")
        return

    num -= 1

    if num < 0 or num >= len(recipe.steps):
        print("Failure to edit step, recipe doesn't have step of number", num + 1)
        return

    recipe.steps[num] = tokens[2]
    print("step " + str(num) + " edited successfully")

def addIngredient(tokens, recipe):
    """
    Add an ingredient to the given recipe
    :param tokens: Processed command tokens
    :param recipe: The recipe an ingredient is being added to
    :return:
    """
    iname = tokens[1]

    amt = 0
    try:
        amt = int(tokens[2])
    except(ValueError):
        try:
            amt = float(tokens[2])
        except:
            print("Failure to add ingredient, amount not a number")
            return

    if(amt <= 0):
        print("Ingredient amount must be a positive value")
        return

    ing = Ingredient.get_ingredient(MANAGER, iname)

    if not ing:
        ing = register_ing_prompt(iname)
        if not ing:
            print("Cannot add nonexistent ingredient")

    recipe.ingredients[ing] = amt
    print(amt, ing.unit, iname, "added successfully to recipe")



    pass

def deleteIngredient(tokens, recipe):
    """
    Delete an ingredient from the given recipe
    :param tokens: Processed command tokens
    :param recipe: The recipe an ingredient is being deleted from
    :return:
    """
    iname = tokens[1]

    ing = Ingredient.get_ingredient(MANAGER, iname)

    if ing not in recipe.ingredients:
        print(iname, "was not in the recipe.")
        return

    recipe.ingredients.pop(ing)

    print(iname, "successfully removed from recipe.")


def addEquipment(tokens, recipe):
    """
    Add a piece of equipment to the given recipe
    :param tokens: Processed command tokens
    :param recipe: The recipe a piece of equipment is being added to
    :return:
    """
    equip = tokens[1]

    if equip in recipe.equipment:
        print("Failure to add equipment, equipment already in recipe")
        return

    recipe.equipment.append(equip)
    print(equip + " added successfully")

def removeEquipment(tokens, recipe):
    """
    Remove a piece of equipment from the given recipe
    :param tokens: Processed command tokens
    :param recipe: The recipe a piece of equipment is being deleted from
    :return:
    """
    equip = tokens[1]

    if equip not in recipe.equipment:
        print("Failure to remove equipment, equipment not in recipe")
        return

    recipe.equipment.remove(equip)
    print(equip + " removed successfully")


def createRecipe(tokens, optional=None):
    """
    Enter recipe create loop with a new empty recipe
    :param tokens: processed line of input
    :param optional: N/A
    :return:
    """
    return RecipeCreateLoop(
        Recipe(manager=MANAGER, rid=None, servings=None, time=None, name=tokens[1],
               owner_id=USER.uid, equip=[], owner=USER, ingr={}, steps=[])
    )


def quit(tokens, optional=None):
    """
    Sets the QUIT_REQUESTED flag to true
    :param tokens: N/A
    :param optional: N/A
    :return: None
    """
    global QUIT_REQUESTED
    QUIT_REQUESTED = True

def back(tokens, optional=None):
    """
    Sets the BACKOUT_REQUESTED flag to true
    :param tokens: N/A
    :param optional: N/A
    :return: None
    """
    global BACK_OUT_REQUESTED
    BACK_OUT_REQUESTED = True

def logout(tokens, optional=None):
    """
    Sets the LOGOUT_REQUESTED flag to true
    :param tokens: N/A
    :param optional: N/A
    :return: None
    """
    global LOGOUT_REQUESTED
    LOGOUT_REQUESTED = True

    print(f"Farewell, {USER.username}")

def login(tokens, optional=None):
    """
    Attempts to log in the requested user. Fails if user does not exist or
    passwords do not match. If logged in, USER is set and user is taken to main
    loop.
    :param tokens: list of processed commands
    :param optional: N/A
    :return: None
    """
    global USER

    account = User.get_user(MANAGER, tokens[1])

    if(account != None and account.check_password(tokens[2])):
        print(f"Welcome, {tokens[1]}")
        USER = account
        return MainLoop()
    else:
        print("Invalid username or password. Please try again.")

def signup(tokens, optional=None):
    """
    Attempts to sign the user with the specified username and password up for
    an account. sets USER and takes the user to the main loop if successful.
    :param tokens:
    :param optional:
    :return:
    """
    global USER

    account = User.register_new_user(MANAGER, tokens[1], tokens[2])
    if(account):
        print(f"Account successfully created. You are now signed in as {tokens[1]}")
        USER = account
        return MainLoop()
    else:
        print("Something went wrong when creating your account. Please try a different username and/or password")

def deleteAccount(tokens, optional=None):
    """
    Deletes the user's account from the database
    :param tokens:
    :param optional:
    :return:
    """

    if(input("Are you sure you would like to delete this account? (Y/N)\n>") == "Y"):
        USER.delete()
        print("account deleted.")
        logout(tokens, optional)



def inventory(tokens, optional=None):
    """
    Takes the user to the ingredient list loop
    :param tokens: N/A
    :param optional: N/A
    :return: None
    """
    return IngredientListLoop()

def increaseIngredient(tokens, optional=None):
    """
    If ingredient exists and any amount specified in tokens is within acceptable
    range ingredient is added to user's storage.
    If ingredient is not present in DB, user is prompted to define its
    properties and it is added

    :param tokens: processed input line
    :param optional: N/A
    :return: None
    """
    iname = tokens[1].lower()

    amt = 0
    try:
        amt = int(tokens[2])
    except(ValueError):
        try:
            amt = float(tokens[2])
        except:
            print("Failure to increase ingredient: amount not a number")
            return

    if(amt < 0):
        print("Amount of ingredient to be added must be positive. Please use the 'remove' command to decrease ingredients.")
        return

    ing = Ingredient.get_ingredient(MANAGER, iname)

    if ing is None:
        userin = input("ingredient '" + iname + "' does not currently exist in the database\n\nWould you like to add it? (Y/N)\n>")
        if(userin.strip() == "Y"):
            ing = Ingredient.register_ingredient(MANAGER, iname, input(
                "What unit is " + iname + " measured in?\n>").lower(), input(
                "Where is " + iname + " stored?\n>").lower())
        else:
            return

    if(ing in USER.owned_ingredients):
        USER.owned_ingredients[ing] += amt
    else:
        USER.owned_ingredients[ing] = amt
    USER.save_owned_ingredients()


def register_ing_prompt(iname):
    """
    Prompts to see if user wants to register a new ingredient
    :param iname: name of ingredient
    :return: new ingredient or None
    """
    userin = input("ingredient '" + iname + "' does not currently exist in the database\n\nWould you like to add it? (Y/N)\n>")
    if(userin.strip() == "Y"):
        ing = Ingredient.register_ingredient(MANAGER, iname, input(
            "What unit is " + iname + " measured in?\n>").lower(), input(
            "Where is " + iname + " stored?\n>").lower())
        return ing
    else:
        return None

def decreaseIngredient(tokens, optional=None):
    """
    If ingredient exists and any amount specified in tokens is within acceptable
    range ingredient is removed from user's storage.

    :param tokens: processed input line
    :param optional: N/A
    :return: None
    """
    iname = tokens[1].lower()

    delete = False

    if len(tokens) == 2:
        delete = True
    else:
        amt = 0
        try:
            amt = int(tokens[2])
        except(ValueError):
            try:
                amt = float(tokens[2])
            except:
                print("Failure to decrease ingredient: amount not a number")
                return

    ing = Ingredient.get_ingredient(MANAGER, iname)

    if ing is None:
        print("ingredient '" + iname + "' does not exist in the DB.")
        return
    try:
        if(delete):
            USER.owned_ingredients.pop(ing)
        else:
            if(USER.owned_ingredients[ing] < amt):
                print("You do not have enough '" + iname + "' to remove this amount.")
                return
            elif(amt < 0):
                print("The amount you chose to remove was negative. If you wish to add ingredients use the 'add' command")

            USER.owned_ingredients[ing] -= amt

            if(USER.owned_ingredients[ing] == 0):
                USER.owned_ingredients.pop(ing)
    except(KeyError):
        print("You do not currently own any " + iname + ".")
    USER.save_owned_ingredients()


def compatible(tokens, optional=None):
    """
    Takes user to recipeListLoop with list of recipes compatible with their
    ingredients
    :param tokens: processed line of input
    :param optional: N/A
    :return:
    """
    return RecipeListLoop(list(map(lambda x: x[0], list(USER.compatible_recipes()))))

def recent(tokens, optional=None):
    """
    Takes user to recipe list loop with list of global recently made recipes
    :param tokens: processed line of input
    :param optional: N/A
    :return:
    """
    return RecipeListLoop(list(MANAGER.recent_recipes()))


def similar(tokens, optional=None):
    """
    Takes user to recipe list loop with list of recipes with similar ingredients
    :param tokens: processed line of input
    :param optional: current recipe
    :return:
    """
    return RecipeListLoop(list(item[0] for item in optional.similar_by_ingredient()))


def recommended(tokens, optional=None):
    """
    Takes user to recipe list loop with list of other recipes made by users that
    made this one
    :param tokens: processed line of input
    :param optional: current recipe
    :return:
    """
    return RecipeListLoop(list(item[0] for item in optional.similar_by_makers()))


def popular(tokens, optional=None):
    """
    Displays the 10 most made recipes for the week to the user
    :param tokens: processed line of input
    :param optional: N/A
    :return:
    """

    return RecipeListLoop(list(item[0] for item in Recipe.get_popular_recipes(MANAGER, 10)))


def myRecent(tokens, optional=None):
    """
    Takes user to recipe list loop with list of their recently made recipes.
    :param tokens:
    :param optional:
    :return:
    """
    return RecipeListLoop(list(MANAGER.recent_recipes(USER)))


def getHelp(tokens, optional=None):
    """
    Prints the appropriate help message given the current program state
    :param tokens: processed line of input
    :param optional:
    :return:
    """
    print(help.HELP_MESSAGE_MAP[PROGRAM_STATE])
    print(help.COMMON_HELP)

def nothing(tokens, optional=None):
    """
    placeholder command processing function that does nothing
    :param tokens:
    :param optional:
    :return:
    """
    pass

#COMMAND MAPS
#These are maps from command keywords to functions to process them
commonCommands = {
    HELP: getHelp,
    LOGOUT: logout,
    QUIT: quit,
    BACK: back

}

mainLoopCommands = {
    SEARCH: search,
    RECENT: recent,
    COMPATIBLE: compatible,
    CREATE: createRecipe,
    INVENTORY: inventory,
    DELETE_RECIPE: deleteAccount,
    MY_RECENT: myRecent,
    POPULAR: popular
}

loginCommands = {
    LOGIN: login,
    SIGNUP: signup
}

recipeCreateCommands = {
    TIME: time,
    SERVINGS: servings,
    ADD_STEP: addStep,
    EDIT_STEP: editStep,
    ADD_INGREDIENT_RECIPE: addIngredient,
    DELETE_INGREDIENT: deleteIngredient,
    ADD_EQUIPMENT: addEquipment,
    REMOVE_EQUIPMENT: removeEquipment,
    SAVE: saveRecipe
}

recipeListCommands = {
    SELECT: select
}

recipeViewCommands = {
    MAKE: make,
    HALVE: halveRecipe,
    DOUBLE: doubleRecipe,
    DELETE_RECIPE: deleteRecipe,
    EDIT_RECIPE: editRecipe,
    SIMILAR: similar,
    RECOMMENDED: recommended
}

ingredientListCommands = {
    ADD_INGREDIENT: increaseIngredient,
    REMOVE: decreaseIngredient
}

COMMAND_SET_MAP = {
    State.INGREDIENT_LIST: ingredientListCommands,
    State.LOGIN: loginCommands,
    State.MAIN: mainLoopCommands,
    State.RECIPE_CREATE: recipeCreateCommands,
    State.RECIPE_LIST: recipeListCommands,
    State.RECIPE_VIEW: recipeViewCommands
}

#END OF COMMAND MAPS

BACK_OUT_REQUESTED = False
LOGOUT_REQUESTED = False
QUIT_REQUESTED = False

def shouldBackOut():
    """
    Returns true if the program should back out of its current state, false
    otherwise
    :return: T or F
    """
    global QUIT_REQUESTED
    global LOGOUT_REQUESTED
    global BACK_OUT_REQUESTED

    if QUIT_REQUESTED or (LOGOUT_REQUESTED and USER != None):
        return True
    elif USER == None:
        LOGOUT_REQUESTED = False
    elif BACK_OUT_REQUESTED:
        BACK_OUT_REQUESTED = False
        return True
    return False




def applyCommand(tokens, optional = None):
    """
    Applies the command given by the user.
    :param tokens: processed line of user input
    :param optional: optional argument used by some commands
    :return:
    """
    loopCommands = COMMAND_SET_MAP[PROGRAM_STATE]
    func = None
    try:
        first = tokens[0]
        if first in loopCommands:
                func = loopCommands[first]
        elif first in commonCommands:
                func = commonCommands[first]
        else:
            print("INVALID COMMAND")

        ans = None
        if func != None:
            if optional == None:
                ans = func(tokens)
            else:
                ans = func(tokens, optional)
    except IndexError:
        print("invalid arguments for given command")
    return ans

def get_tokenized_input(st=None):
    """
    Gets a line of input, and returns a list of strings that were separated by
    spaces. Any text between 2 single quotes is kept intact
    :return: List of strings
    """
    uin = ""
    if st is None:
        uin = input(INPUT_MSG)
    else:
        uin = st

    in_chunks = []
    dont_strip = []

    start = -1
    end = -1
    for i in range(len(uin)):
        if uin[i] == "'":
            if start == -1:
                start = i
            else:

                dont_strip.append(uin[start+1:i])
                in_chunks.append(uin[end + 1:start])

                end=i
                start = -1
    in_chunks.append(uin[end + 1:len(uin)])
    tokens = []
    for i in range(len(in_chunks)):
        chunk = in_chunks[i].strip()
        if len(chunk) > 0:
            tokens += in_chunks[i].strip().split(' ')
        if i < len(dont_strip):
            tokens.append(dont_strip[i])
    return tokens


def LoginLoop():
    """
    Loop representing a login screen. User can log in / create an account here
    :return:
    """
    global PROGRAM_STATE
    global USER


    while not shouldBackOut():
        set_program_state(State.LOGIN)
        tokens = get_tokenized_input()
        applyCommand(tokens)

        USER = None # if the program returns from the deeper loop, means user was logged out

def MainLoop():
    """
    Loop representing home screen of DB. User can search recipes, create
    recipes, manage ingredients, etc.
    :return:
    """
    global PROGRAM_STATE

    while not shouldBackOut():
        set_program_state(State.MAIN)
        tokens = get_tokenized_input()

        applyCommand(tokens)

def RecipeCreateLoop(recipe):
    global PROGRAM_STATE

    while not shouldBackOut():
        set_program_state(State.RECIPE_CREATE)
        displayRecipe(recipe)
        tokens = get_tokenized_input()

        applyCommand(tokens, recipe)

def RecipeListLoop(recipeList):
    """
    Loop that displays a list of recipes and allows the user to act on them
    :param recipeList:
    :return:
    """
    global PROGRAM_STATE

    while not shouldBackOut():
        set_program_state(State.RECIPE_LIST)
        displayRecipeList(recipeList)
        tokens = get_tokenized_input()

        i = applyCommand(tokens)

        if i != None and i >= 1 and i <= len(recipeList):
            RecipeViewLoop(recipeList[i-1])


def RecipeViewLoop(recipe):
    """
    Loop that displays a recipe to a user and allows them to mark it as made,
    or delete it if they own it.
    :param recipe:
    :return:
    """
    while not shouldBackOut():
        set_program_state(State.RECIPE_VIEW)

        displayRecipe(recipe)

        tokens = get_tokenized_input()

        response = applyCommand(tokens, recipe)




def IngredientListLoop():
    """
    Loop that displays the user's current list of ingredients to them. Allows
    them to manipulate their current set of ingredients.
    :return:
    """
    global PROGRAM_STATE

    while not shouldBackOut():
        set_program_state(State.INGREDIENT_LIST)

        displayIngredients(USER.owned_ingredients)

        tokens = get_tokenized_input()

        applyCommand(tokens)


def main():
    """
    Main loop that initializes and calls function to start program
    :return:
    """
    global MANAGER

    try:
        MANAGER = RecipeManager.new_from_env()
    except(KeyError):
        print("To run the database, the system must have a DATABASE environment variable defined with connection info to the database")
        return

    if len(sys.argv) == 1:
        LoginLoop()
    elif len(sys.argv) == 2 and sys.argv[1] == "-a":
        analytics.analytics(MANAGER)
    else:
        print("ERROR: Too many command line arguments")
        exit()

    MANAGER.disconnect()

if __name__ == '__main__':
    main()