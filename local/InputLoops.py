"""
@filename - InputLoops.py
@author - Nicholas Antiochos
File that defines all input collection/input loop logic
"""

from model.recipe_manager import RecipeManager
from model.user import User

import help
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
CREATE = "create"
INVENTORY = "inventory"
LOGOUT = "logout"

#Recipe Create Commands
TIME = "time"
SERVINGS = "servings"
ADD_STEP = "addStep"
EDIT_STEP = "editStep"
ADD_INGREDIENT = "addIngredient"
DELETE_INGREDIENT = "deleteIngredient"
ADD_EQUIPMENT = "addEquipment"
REMOVE_EQUIPMENT = "removeEquipment"

#Recipe List Commands
SELECT = "select"

#Recipe View Commands
MAKE = "make"
HALVE = "halve"
DOUBLE = "double"


MANAGER = RecipeManager.new_from_env()
USER = None

def displayRecipe(recipe):
    print(recipe.servings)
    print(recipe.steps)
    print(recipe.equipment)
    print(recipe.time)
    print(recipe.ingredients)

    return

    print(recipe.name, "\n")
    print("Author -", recipe.owner.username if recipe.owner else "Unknown", "\n")

    print("Servings:", recipe.servings)
    print("Prep Time:", recipe.time, "minutes\n")

    if (len(recipe.equipment) > 0):
        print("Required Equipment:")
        for equipment in recipe.equipment:
            print("\t +", equipment[0])
    else:
        print("No required Equipment")

    print("\nIngredients:")
    ingredients = list(recipe.ingredients.keys())
    for i in range(len(recipe.ingredients)):
        print("\t", recipe.ingredients[ingredients[i]], ingredients[i].unit,
              "of", ingredients[i].iname)

    print("\nDirections:")
    steps = list(recipe.steps)
    for i in range(len(steps)):
        print("\t", i + 1, ") ", steps[i], sep='')

    # TODO dates made?


def displayRecipeList(recipeList):
    for i in range(len(recipeList)):
        owner = recipeList[i].owner
        author = " - "
        if(owner != None):
            author += owner.username
        else:
            author = ""

        print("\t", i+1, ") ", recipeList[i].name, author, sep='')

def halveRecipe(tokens, recipe):
    newServings = recipe.servings/2
    recipe.ingredients = recipe.changeServings(newServings)
    recipe.servings = newServings

def doubleRecipe(tokens, recipe):
    newServings = 2*recipe.servings
    recipe.ingredients = recipe.changeServings(newServings)
    recipe.servings = newServings


def select(tokens, optional = None):
    i = 0
    try:
        i = int(tokens[1])
    except ValueError:
        print("The index you provided is not an integer, please try again")
        return

    return i

def search(tokens, optional = None):
    termIndex = 1
    if tokens[1] == INGREDIENT_FLAG:
        termIndex += 1
        print("Searching for recipes containing '" + tokens[termIndex] + "'")
        #TODO Search for recipes containing ingredient
    elif tokens[1] == NAME_FLAG:
        termIndex += 1
        return search_name(tokens[termIndex])
    else:
        return search_name(tokens[termIndex])

def search_name(name):
    print("Searching Recipe DB for '" + name + "'")
    return RecipeListLoop(list(MANAGER.searchRecipes(name)))

def make(tokens, optional=None):

    if(optional):
        if(optional.markMade(USER)):
            print("recipe made successfully!")
    else:
        return False
    return True

def time(tokens):
    pass

def servings(tokens):
    pass

def addStep(tokens):
    pass

def editStep(tokens):
    pass

def addIngredient(tokens):
    pass

def deleteIngredient(tokens):
    pass

def addEquipment(tokens):
    pass

def removeEquipment(tokens):
    pass

def quit(tokens, optional=None):
    global QUIT_REQUESTED
    QUIT_REQUESTED = True

def back(tokens, optional=None):
    global BACK_OUT_REQUESTED
    BACK_OUT_REQUESTED = True

def logout(tokens, optional=None):
    global LOGOUT_REQUESTED
    LOGOUT_REQUESTED = True

    print(f"Farewell, {USER.username}")

def login(tokens, optional=None):
    global USER

    account = User.get_user(MANAGER, tokens[1])

    if(account != None and account.check_password(tokens[2])):
        print(f"Welcome, {tokens[1]}")
        USER = account
        return MainLoop()
    else:
        print("Invalid username or password. Please try again.")

def signup(tokens, optional=None):
    account = User.register_new_user(MANAGER, tokens[1], tokens[2])
    if(account):
        print(f"Account successfully created. You are now signed in as {tokens[1]}")
        USER = account
        return MainLoop()
    else:
        print("Something went wrong when creating your account. Please try a different username and/or password")

def compatible(tokens, optional=None):
    return RecipeListLoop([])
    # TODO

def recent(tokens, optional=None):
    return RecipeListLoop([])
    # TODO

def getHelp(tokens, optional=None):
    print(help.HELP_MESSAGE_MAP[PROGRAM_STATE])
    print(help.COMMON_HELP)

def nothing(tokens, optional=None):
    pass

#COMMAND MAPS
commonCommands = {
    HELP: getHelp,
    LOGOUT: logout,
    QUIT: quit,
    BACK: back

}

mainLoopCommands = {
    SEARCH: search,
    RECENT: nothing,
    COMPATIBLE: nothing,
    CREATE: nothing,
    INVENTORY: nothing,
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
    ADD_INGREDIENT: addIngredient,
    DELETE_INGREDIENT: deleteIngredient,
    ADD_EQUIPMENT: addEquipment,
    REMOVE_EQUIPMENT: removeEquipment
}

recipeListCommands = {
    SELECT: select
}

recipeViewCommands = {
    MAKE: make,
    HALVE: halveRecipe,
    DOUBLE: doubleRecipe
}

COMMAND_SET_MAP = {
    State.INGREDIENT_LIST: {},
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
    except IndexError:
        print("invalid arguments for given command")
    ans = None
    if func != None:
        if optional == None:
            ans = func(tokens)
        else:
            ans = func(tokens, optional)
    return ans

def get_tokenized_input():
    """
    Gets a line of input, and returns a list of strings that were separated by
    spaces. Any text between 2 single quotes is kept intact
    :return: List of strings
    """
    uin = input(INPUT_MSG)
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
    global PROGRAM_STATE
    global USER


    while not shouldBackOut():
        set_program_state(State.LOGIN)
        tokens = get_tokenized_input()
        applyCommand(tokens)

        USER = None # if the program returns from the deeper loop, means user was logged out

def MainLoop():
    global PROGRAM_STATE

    while not shouldBackOut():
        set_program_state(State.MAIN)
        tokens = get_tokenized_input()

        applyCommand(tokens)

def RecipeCreateLoop():
    global PROGRAM_STATE

    while not shouldBackOut():
        set_program_state(State.RECIPE_CREATE)
        tokens = get_tokenized_input()

        applyCommand(tokens)

def RecipeListLoop(recipeList):
    global PROGRAM_STATE

    while not shouldBackOut():
        set_program_state(State.RECIPE_LIST)
        displayRecipeList(recipeList)
        tokens = get_tokenized_input()

        i = applyCommand(tokens)

        if i != None and i >= 1 and i <= len(recipeList):
            RecipeViewLoop(recipeList[i-1])


def RecipeViewLoop(recipe):
    while not shouldBackOut():
        set_program_state(State.RECIPE_VIEW)

        displayRecipe(recipe)

        tokens = get_tokenized_input()

        response = applyCommand(tokens, recipe)




def IngredientListLoop(ingredients):
    pass


def main():
    LoginLoop()


if __name__ == '__main__':
    main()