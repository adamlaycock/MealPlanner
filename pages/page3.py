import streamlit as st
import sqlite3
import pandas as pd

DAYS = [
    'Monday', 'Tuesday', 'Wednesday', 
    'Thursday', 'Friday', 'Saturday', 'Sunday'
]

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
    
    return [row[0] for row in recipes]


st.title('Meal Planner & Shopping List')
st.header('Meal Planner')

for day in DAYS:
    st.selectbox(
        f'Recipe for {day}:',
        options=get_all_recipes(),
        index=None,
        key=f'recipe_selector_{day}'
    )

if st.button('Submit Recipes', key='submit_btn'):
    selected_recipes = [
        st.session_state[f'recipe_selector_{day}'] 
        for day in DAYS 
        if st.session_state[f'recipe_selector_{day}'] is not None
    ]
    st.header('Shopping List')
    st.write(build_list(selected_recipes))