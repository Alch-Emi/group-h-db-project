"""
@filename - InputLoops.py
@author - Nicholas Antiochos
File that defines all input collection/input loop logic
"""

INPUT_MSG = "Please enter a valid command\n>"

#Common commands
QUIT = "quit"
LOGOUT = 'logout'
HELP = "help"


#Main Loop Commands
SEARCH = "search"
NAME_FLAG = "-n"
INGREDIENT_FLAG = "-i"


GET = "get"
CREATE = "create"
INVENTORY = "inventory"
LOGOUT = "logout"


MANAGER = [] #TODO Create recipe manager on login


def search(tokens):
    termIndex = 1
    if tokens[1] == INGREDIENT_FLAG:
        termIndex += 1
        print("Searching for recipes containing '" + tokens[termIndex] + "'")
    elif tokens[1] == NAME_FLAG:
        termIndex += 1
        search_name(tokens[termIndex])
    else:
        search_name(tokens[termIndex])

def search_name(name):
    print("Searching Recipe DB for '" + name + "'")
    #TODO return recipe list with given name
    return []

def nothing(tokens):
    pass

#TODO COMMAND MAPS
commonCommands = {
    HELP: nothing,
    LOGOUT: nothing,
    QUIT: nothing

}

mainLoopCommands = {
    SEARCH: search,
    GET: nothing,
    CREATE: nothing,
    INVENTORY: nothing,
}
#TODO END OF COMMAND MAPS


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
    pass

def MainLoop():
    while True:
        tokens = get_tokenized_input()

        first = tokens[0]
        if first in mainLoopCommands:
            try:
                mainLoopCommands[first](tokens)
            except IndexError:
                print("invalid arguments for given command")
        else:
            print("INVALID COMMAND")

def RecipeCreateLoop():
    pass

def RecipeListLoop():
    pass

def RecipeViewLoop():
    pass

def IngredientListLoop():
    pass


def main():
    MainLoop()

    tokens = ['hello']
    while(len(tokens) > 0):
        tokens = get_tokenized_input()
        print(tokens)




main()