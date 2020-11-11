from model.recipe_manager import RecipeManager
from model.user import User
from model.ingredient import Ingredient
from model.recipe import Recipe

import matplotlib.pyplot as plt


"""
@filename - analytics.py
@author - Nicholas Antiochos

provides functionality for getting recipe database analytics.
"""

def make_ingredients_graph(manager):
    pairs = Ingredient.get_common_ingredients(manager, 10)

    X = []
    Y = []

    for ing, count in pairs:
        X.append(ing.iname)
        Y.append(count)

    fig1, ax1 = plt.subplots()
    ax1.set_title("Most Common Ingredients")
    ax1.pie(Y, labels=X, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis(
        'equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.show()

def analytics(manager):
    make_ingredients_graph(manager)