import pandas as pd
from collections import defaultdict
import sqlite3

# INGREDS_DF = pd.read_csv(
#     r'C:\Users\adamm\OneDrive\Documents\R&D\MealPlanner\ingredients.csv'
# )

# RECIPE_DF = pd.read_csv(
#     r'C:\Users\adamm\OneDrive\Documents\R&D\MealPlanner\recipes.csv'
# )

def build_list(ids: list) -> pd.DataFrame:
    filt_ingreds_df = INGREDS_DF[INGREDS_DF['ID'].isin(ids)]['Ingredient']
    ingreds = pd.DataFrame(
        filt_ingreds_df.value_counts()
    ).reset_index()
    ingreds['count'] = ('x' + ingreds['count'].astype(str)).replace('x1', '')
    ingreds.columns = ['ingredient', 'occurrences']
    ingreds = ingreds.sort_values(by='ingredient')

    return(ingreds)

def remove_recipe(name:str):
    global RECIPE_DF, INGREDS_DF

    remove_id = RECIPE_DF.loc[RECIPE_DF['Name'] == name, 'ID'].iloc[0]
    RECIPE_DF = RECIPE_DF[RECIPE_DF['ID'] != remove_id]
    INGREDS_DF = INGREDS_DF[INGREDS_DF['ID'] != remove_id]

    # RECIPE_DF.to_csv(
    #     r'C:\Users\adamm\OneDrive\Documents\R&D\MealPlanner\recipes.csv',
    #     index=False
    # )
    # INGREDS_DF.to_csv(
    #     r'C:\Users\adamm\OneDrive\Documents\R&D\MealPlanner\ingredients.csv',
    #     index=False
    # )

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
