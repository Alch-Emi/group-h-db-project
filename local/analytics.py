from model.recipe_manager import RecipeManager
from model.user import User
from model.ingredient import Ingredient
from model.recipe import Recipe

import matplotlib.pyplot as plt
from textwrap import wrap

import datetime

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

def top_10_recipes_graph(manager):
    pairs = Recipe.get_popular_recipes(manager, 5)

    X = []
    Y = []

    for rec, count in pairs:
        X.append("\n".join(wrap(rec.name, 15)))
        Y.append(count)

    fig1, ax1 = plt.subplots()
    ax1.set_title("Most Made Recipes this Week")
    ax1.bar(height=Y, x=X, width=0.4)
    plt.show()


def recipes_by_week_graph(manager):
    pairs = manager.recipes_by_week()

    X = []
    Y = []

    lastX = None

    for week, count in pairs:
        if(lastX is None):
            lastX = week
        while (week - lastX) > datetime.timedelta(7):
            lastX += datetime.timedelta(7)
            X.append(lastX)
            Y.append(0)



        X.append(week)
        Y.append(count)

        lastX = week

    fig1, ax1 = plt.subplots()
    ax1.set_title("Recipes Made Weekly")
    plt.plot(X, Y)
    plt.xticks(X)
    plt.show()


def analytics(manager):
    make_ingredients_graph(manager)
    top_10_recipes_graph(manager)
    recipes_by_week_graph(manager)