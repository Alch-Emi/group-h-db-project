"""
Filename - generator.py
Author - Nicholas Antiochos

Generates random recipes and #TODO saves them
"""

import random
from InputLoops import get_tokenized_input as tokenize, displayRecipe
from model.ingredient import Ingredient
from model.recipe import Recipe
from model.recipe_manager import RecipeManager
from model.user import User

ADJECTIVES = 'adjectives'
FOOD_GENRES = "food_genres"
PERSONS = "persons"
PT_VERBS = "pt_verbs"
INGREDIENTS = "ingredients"

ADDITION_METHODS = "addition_methods"
FINAL_STEPS = "final_steps"

EQUIPMENT = "equipment"

PERSON_CHANCE = 0.25
ADJECTIVE_CHANCE = 0.5
FOOD_GENRES_CHANCE = 1
PT_VERBS_CHANCE = 0.9

MEASUREMENTS = [0.25, 0.5, 1, 1.5, 2, 3, 4]

MAX_INGREDIENTS_PER_RECIPE = 8

VOLUME = 200

UID = 3
MANAGER = RecipeManager.new_from_env()
USER = User.get_user_by_uid(MANAGER, UID)


def file_to_string_list(filename):
    file = open(filename, "r")

    contained = set()
    lst = []

    for line in file:
        st = line.strip()
        if not st in contained:
            lst.append(st)
            contained.add(st)

    return lst


def get_one(lst):
    return random.choice(lst)

def assemble_name(persons, adjectives, pt_verbs, ingredient, food_genres):
    name = ""

    if(random.random() <= PERSON_CHANCE):
        name += get_one(persons) + " "

    if(random.random() <= ADJECTIVE_CHANCE):
        name += get_one(adjectives) + " "
    elif(random.random() <= PT_VERBS_CHANCE):
        name += get_one(pt_verbs) + " "

    name += ingredient.iname + " "

    name += get_one(food_genres) + " "

    return name.strip()


def ingredient_from_st(st):
    tokens = tokenize(st)

    ing = Ingredient.get_ingredient(MANAGER, tokens[0])

    if ing is None:
        ing = Ingredient.register_ingredient(MANAGER, tokens[0], tokens[1], tokens[2])
    return ing

def gen_ingredient_dictionary(ingredients_lst):
    dic = {}
    for ing in ingredients_lst:
        dic[ing] = random.choice(MEASUREMENTS)
    return dic

def gen_steps_lst(addition_methods, ingredients_lst, equip_map, final_steps):

    steps = []

    stuff = set([0, 1])
    ingredients_left = set(ingredients_lst)

    equipsleft = set(list(equip_map.keys()))

    if len(equipsleft) == 0:
        stuff.remove(1)

    which = 0
    while len(stuff) > 0:
        step = ""

        if which == 0:

            ing_this_step = random.sample(list(ingredients_left), k=random.randrange(1, len(ingredients_left) - 1) if len(ingredients_left) > 2 else 1)
            ingredients_left.difference_update(set(ing_this_step))

            if len(ingredients_left) == 0:
                stuff.remove(0)

            for i in range(len(ing_this_step)):
                print(ing_this_step[i].iname)
                step += ing_this_step[i].iname

                if i != len(ing_this_step) - 1:
                    step += ", "
            step = random.choice(addition_methods).format(step)


        elif which == 1:
            equip = random.choice(list(equipsleft))

            step = equip_map[equip].pop(0).format(random.randint(20, 500))

            if len(equip_map[equip]) == 0:
                equipsleft.remove(equip)

            if len(equipsleft) == 0:
                stuff.remove(1)


        steps.append(step)

        if len(stuff) > 0:
            which = random.choice(list(stuff))

    steps.append(random.choice(final_steps))
    return steps


def readEquipment(filename):

    eqdict = {}
    file = open(filename, "r")

    equip = None

    for line in file:
        line = line.strip()
        if line == "":
            equip = None
        elif equip is None:
            equip = line
            eqdict[equip] = []
        else:
            eqdict[equip].append(line)

    return eqdict

def generate():
    adjectives = file_to_string_list(ADJECTIVES)
    food_genres = file_to_string_list(FOOD_GENRES)
    persons = file_to_string_list(PERSONS)
    pt_verbs = file_to_string_list(PT_VERBS)
    ingredients = list(map(lambda x: ingredient_from_st(x), file_to_string_list(INGREDIENTS)))

    addition_methods = file_to_string_list(ADDITION_METHODS)
    final_steps = file_to_string_list(FINAL_STEPS)

    for i in range(VOLUME):
        recipe_ingredients = random.sample(ingredients, k=random.randint(1, min(len(ingredients)-1, MAX_INGREDIENTS_PER_RECIPE)))

        title_ingredient = random.choice(recipe_ingredients)
        name = assemble_name(persons, adjectives, pt_verbs, title_ingredient, food_genres)

        equip_dictionary = readEquipment(EQUIPMENT)

        selected_equips = random.sample(list(equip_dictionary.keys()), k=random.randint(0, len(list(equip_dictionary.keys()))))

        selected_equips_dict = {}
        for eq in selected_equips:
            selected_equips_dict[eq] = equip_dictionary[eq]

        recipe_steps = gen_steps_lst(addition_methods, recipe_ingredients, selected_equips_dict, final_steps)

        ingredients_dict = gen_ingredient_dictionary(recipe_ingredients)

        rec = Recipe(MANAGER, 0, random.randint(1, 4), random.randint(5, 360), name, list(selected_equips_dict.keys()), None, ingredients_dict, recipe_steps)

        print("====================")
        displayRecipe(rec)

        Recipe.register_recipe(manager=MANAGER, name=name,
                               servings=random.randrange(1, 4),
                               time=random.randint(5, 360),
                               equip=list(selected_equips_dict.keys()),
                               owner=USER, ingr=ingredients_dict,
                               steps=recipe_steps, owner_id=USER.uid)
        #def __init__(self, manager, rid, servings, time, name, equip, owner,
         #            ingr, steps)



generate()
MANAGER.disconnect()