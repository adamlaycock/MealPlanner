import pandas as pd
from collections import defaultdict
import sqlite3

def find_recipes(search_ingredients: list):
    search_set = set(search_ingredients)
    recipe_groups = INGREDS_DF.groupby('ID')['Ingredient'].apply(set)

    matches = recipe_groups[recipe_groups.apply(search_set.issubset)].index.tolist()
    selected_recipes = list(RECIPE_DF[RECIPE_DF['ID'].isin(matches)]['Name'])

    return selected_recipes







def add_recipe(name: str, link: str, ingredients: list):
    conn = sqlite3.connect('meal_planner.db')
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    ingredients = [i.lower() for i in ingredients]
    name = name.lower()

    cur.execute('INSERT INTO recipes (name, link) VALUES (?, ?)', (name, link))
    new_id = cur.lastrowid
    
    ingredient_data = [(i.lower(), new_id) for i in ingredients]
    cur.executemany(
        'INSERT INTO ingredients (ingredient, recipe_id) VALUES (?, ?)', 
        ingredient_data
    )
    
    confirmation = input(
        f'Add "{name}"? (Y/N):'
    ).strip().upper()
    
    if confirmation == 'Y':
        #conn.commit()
        print(f'Successfully saved "{name}"')
    else:
        print(f'"{name}" was not added.')

    conn.close()

def remove_recipe(name: str):
    conn = sqlite3.connect('meal_planner.db')
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    cur.execute('DELETE FROM recipes WHERE name=?', (name,))

    confirmation = input(
    f'Remove "{name}"? (Y/N):'
    ).strip().upper()

    if confirmation == 'Y':
        #conn.commit()
        print(f'Successfully removed "{name}"')
    else:
        print(f'"{name}" was not removed.')

    conn.close()

def build_list(names: list):
    conn = sqlite3.connect('meal_planner.db')
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    placeholders = ', '.join(['?'] * len(names))
    query = f"""
        SELECT ingredients.ingredient FROM recipes
        JOIN ingredients ON recipes.id = ingredients.recipe_id
        WHERE name IN ({placeholders})
    """
    res = pd.DataFrame(
        pd.DataFrame(
            cur.execute(query, names)
        ).value_counts()
    ).reset_index().sort_values(by=0)

    shopping_list = (
        res[0].str.title() + ' x' + res['count'].astype(str)
    ).str.replace('x1', '')

    conn.close()
    
    return shopping_list

def find_recipes(ingredients: list):
    conn = sqlite3.connect('meal_planner.db')
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    placeholders = ', '.join(['?'] * len(ingredients))
    query = f"""
        SELECT recipes.name FROM recipes
        JOIN ingredients ON recipes.id = ingredients.recipe_id
        WHERE ingredients.ingredient IN ({placeholders})
    """

    res = cur.execute(query, ingredients).fetchall()
    print(res)

    conn.close()

find_recipes(['white onions'])