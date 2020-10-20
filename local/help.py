"""
@filename - help.py
@author - Nicholas Antiochos

Contains map of help messages for each Program State
"""

from state import State

COMMON_HELP = \
    "> help (tells you more about the current program state and commands)\n" \
    "> logout (log out of current account) \n" \
    "> quit (exit the program)"

MAIN_HELP = \
    "> search [1 flag] 'search term'\n" \
    "\t-n : search by recipe name (default)\n" \
    "\t-i : search by ingredient name\n" \
    "> recent (returns list of recipes recently created)\n" \
    "> compatible (returns list of recipes that share ingredients with your storage)\n" \
    "> create 'name' (creates a recipe with the given name)\n" \
    "> inventory 'storage location' (returns a list of ingredients stored at the given location)\n"




HELP_MESSAGE_MAP = {
    State.MAIN: MAIN_HELP,
    State.LOGIN: "temp",
    State.RECIPE_VIEW: "temp",
    State.RECIPE_LIST: "temp",
    State.RECIPE_CREATE: "temp",
    State.INGREDIENT_LIST: "temp"
}