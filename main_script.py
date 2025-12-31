import pandas as pd
from collections import defaultdict
import sqlite3

def build_list(ids: list) -> pd.DataFrame:
    filt_ingreds_df = INGREDS_DF[INGREDS_DF['ID'].isin(ids)]['Ingredient']
    ingreds = pd.DataFrame(
        filt_ingreds_df.value_counts()
    ).reset_index()
    ingreds['count'] = ('x' + ingreds['count'].astype(str)).replace('x1', '')
    ingreds.columns = ['ingredient', 'occurrences']
    ingreds = ingreds.sort_values(by='ingredient')

    return(ingreds)

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
        JOIN ingredients on RECIPES.id = ingredients.recipe_id
        WHERE name in ({placeholders})
    """
    res = cur.execute(query, names)

    # Temporary debug
    for row in res:
        print(row[0])
    
    conn.close()
