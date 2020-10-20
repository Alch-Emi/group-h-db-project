"""
@filename - InputLoops.py
@author - Nicholas Antiochos
File that defines all input collection/input loop logic
"""

from recipe_manager import RecipeManager
from user import User

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

GET = "get"
CREATE = "create"
INVENTORY = "inventory"
LOGOUT = "logout"


#Recipe List Commands
SELECT = "select"


MANAGER = RecipeManager.new_from_env()
USER = None

def displayRecipes(recipeList):
    for i in range(len(recipeList)):
        print("\t", i+1, ") ", recipeList[i].name, sep='')

def select(tokens):
    i = 0
    try:
        i = int(tokens[1])
    except ValueError:
        print("The index you provided is not an integer, please try again")
        return

    return i

def search(tokens):
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


def quit(tokens):
    global QUIT_REQUESTED
    QUIT_REQUESTED = True

def back(tokens):
    global BACK_OUT_REQUESTED
    BACK_OUT_REQUESTED = True

def logout(tokens):
    global LOGOUT_REQUESTED
    LOGOUT_REQUESTED = True

    print(f"Farewell, {USER.username}")

def login(tokens):
    global USER

    account = User.get_user(MANAGER, tokens[1])
    if(account.check_password(tokens[2])):
        print(f"Welcome, {tokens[1]}")
        USER = account
        return MainLoop()
    else:
        print("Invalid username or password. Please try again.")

def signup(tokens):
    account = User.register_new_user(MANAGER, tokens[1], tokens[2])
    if(account):
        print(f"Account successfully created. You are now signed in as {tokens[1]}")
        USER = account
        return MainLoop()
    else:
        print("Something went wrong when creating your account. Please try a different username and/or password")



def getHelp(tokens):
    print(help.HELP_MESSAGE_MAP[PROGRAM_STATE])
    print(help.COMMON_HELP)

def nothing(tokens):
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
    GET: nothing,
    CREATE: nothing,
    INVENTORY: nothing,
}

loginCommands = {
    LOGIN: login,
    SIGNUP: signup
}

recipeListCommands = {
    SELECT: select
}

COMMAND_SET_MAP = {
    State.INGREDIENT_LIST: {},
    State.LOGIN: loginCommands,
    State.MAIN: mainLoopCommands,
    State.RECIPE_CREATE: {},
    State.RECIPE_LIST: recipeListCommands,
    State.RECIPE_VIEW: {}
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
    elif BACK_OUT_REQUESTED:
        BACK_OUT_REQUESTED = False
        return True
    return False




def applyCommand(tokens):
    loopCommands = COMMAND_SET_MAP[PROGRAM_STATE]
    response = None
    try:
        first = tokens[0]
        if first in loopCommands:
                response = loopCommands[first](tokens)
        elif first in commonCommands:
                response = commonCommands[first](tokens)
        else:
            print("INVALID COMMAND")
    except IndexError:
        print("invalid arguments for given command")
    return response

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
    pass

def RecipeListLoop(recipeList):
    global PROGRAM_STATE

    while not shouldBackOut():
        set_program_state(State.RECIPE_LIST)
        displayRecipes(recipeList)
        tokens = get_tokenized_input()

        i = applyCommand(tokens)

        if i != None and i >= 1 and i <= len(recipeList):
            RecipeViewLoop(recipeList[i-1])


    pass

def RecipeViewLoop(recipe):
    while not shouldBackOut():
        set_program_state(State.RECIPE_VIEW)

        print(recipe.name, "\n")
        print("Author -", recipe.owner.username, "\n")

        print("Servings:", recipe.servings)
        print("Prep Time:", recipe.time, "minutes\n")

        if(len(recipe.equipment) > 0):
            print("Required Equipment:")
            for equipment in recipe.equipment:
                print("\t +", equipment[0])
        else:
            print("No required Equipment")

        print("\nIngredients:")
        ingredients = list(recipe.ingredients.keys())
        for i in range(len(recipe.ingredients)):
                print("\t", recipe.ingredients[ingredients[i]], ingredients[i].unit, "of", ingredients[i].iname)

        print("\nDirections:")
        steps = list(recipe.steps)
        for i in range(len(steps)):
            print("\t", i+1, ") ", steps[i], sep='')
        tokens = get_tokenized_input()

        applyCommand(tokens)



def IngredientListLoop():
    pass


def main():
    LoginLoop()


if __name__ == '__main__':
    main()