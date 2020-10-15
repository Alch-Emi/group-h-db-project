"""
@filename - InputLoops.py
@author - Nicholas Antiochos
File that defines all input collection/input loop logic
"""

INPUT_MSG = "Please enter a valid command\n>"

#Common commands
QUIT = "quit"
LOGOUT = 'logout'


#Main Loop Commands
SEARCH = "search"
GET = "get"
CREATE = "create"
INVENTORY = "inventory"
LOGOUT = "logout"

mainLoopCommands = {
    SEARCH: nothing,
    GET: nothing,
    CREATE: nothing,
    INVENTORY: nothing,
}

def nothing():
    pass

def get_tokenized_input():
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

    def MainLoop(recipeManager):
        while True:
            tokens = get_tokenized_input()

            first = tokens[0]
            if(first in mainLoopCommands):
                mainLoopCommands[first]()
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
    tokens = ['hello']
    while(len(tokens) > 0):
        tokens = get_tokenized_input()
        print(tokens)




main()