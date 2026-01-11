import streamlit as st
import sqlite3
import pandas as pd

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

def get_all_recipes() -> list:
    conn = sqlite3.connect('meal_planner.db')
    cur = conn.cursor()
    cur.execute('PRAGMA foreign_keys = ON;')

    recipes = cur.execute("""
        SELECT name FROM recipes
    """).fetchall()

    conn.close()
    
    return [row[0].title() for row in recipes]


st.title('Meal Planner & Shopping List')
st.header('Meal Planner')

selections = st.multiselect('Select Recipes:', options=get_all_recipes())

if st.button('Submit Recipes', key='submit_btn'):
    if selections:
        st.header('Shopping List')
        items = build_list([s.lower() for s in selections])
        
        clean_list = "\n".join(items.tolist())
        
        st.code(clean_list, language=None)
    else:
        st.warning("Please select at least one recipe first!")