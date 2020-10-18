"""
@filename - state.py
@author - Nicholas Antiochos

Contains Enumeration of program states for the DB program.s
"""

from enum import Enum

class State(Enum):
    LOGIN = 0
    MAIN = 1
    RECIPE_LIST = 2
    RECIPE_VIEW = 3
    RECIPE_CREATE = 4
    INGREDIENT_LIST = 5