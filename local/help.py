"""
@filename - help.py
@author - Nicholas Antiochos
@author - Caitlin Arf
Contains map of help messages for each Program State
"""

from state import State

COMMON_HELP = \
    "> help (tells you more about the current program state and commands)\n" \
    "> back (return to previous screen)\n" \
    "> logout (log out of the program) \n" \
    "> quit (exit the program)\n"

MAIN_HELP = \
    "> search [1 optional flag] 'search term'\n" \
    "\t -n : search by name (default)\n " \
    "\t -i : search by ingredient\n" \
    "> recent (returns list of recipes recently created)\n" \
    "> compatible (returns list of recipes that share ingredients with your storage)\n" \
    "> create 'name' (creates a recipe with the given name)\n" \
    "> inventory 'storage location' (returns a list of ingredients stored at the given location)\n" \
    "> delete (delete the account that's signed in and all associated recipes)\n"

LOGIN_HELP = \
    "> login 'username' 'password'\n" \
    "> signup 'username' 'password'\n"

RECIPE_VIEW_HELP = \
    "> changeServings 'new number of servings' (changes the number of servings and updates ingredient requirements)\n" \
    "> halve (halves recipe)\n" \
    "> double (doubles recipe)\n" \
    "> make (marks recipe as made)\n" \
    "> delete (deletes the recipe)\n" \

RECIPE_LIST_HELP = \
    "> select # (view recipe listed as number '#')\n" \

RECIPE_CREATE_HELP = \
    "> time 'time in minutes' (updates the time required to make the recipe)\n" \
    "> servings 'number of servings' (updates the number of servings made and required ingredient amounts)\n" \
    "> addStep 'description' (adds new step to recipe)\n" \
    "> editStep 'step number' 'description' (updates description of given step)\n" \
    "> addIngredient 'name' 'amount' (adds required amount of given ingredient to recipe)\n" \
    "> deleteIngredient 'name' (deletes ingredient from recipe)\n" \
    "> addEquipment 'name' (adds required piece of equipment to recipe)\n" \
    "> removeEquipment 'name' (removes piece of equipment from recipe)\n" \
    "> save (creates recipe and opens recipe view)\n" \
    "> cancel (cancels and returns to main menu)\n"

INGREDIENT_LIST_HELP = \
    "> add 'name' 'amount' (add ingredient to storage)\n" \
    "> remove 'name' (optional)'amount' (removes ingredient from storage)\n" \

HELP_MESSAGE_MAP = {
    State.MAIN: MAIN_HELP,
    State.LOGIN: LOGIN_HELP,
    State.RECIPE_VIEW: RECIPE_VIEW_HELP,
    State.RECIPE_LIST: RECIPE_LIST_HELP,
    State.RECIPE_CREATE: RECIPE_CREATE_HELP,
    State.INGREDIENT_LIST: INGREDIENT_LIST_HELP
}
