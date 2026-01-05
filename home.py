import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect('meal_planner.db')
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

if 'recipes_df' not in st.session_state:
    st.session_state.recipes_df = pd.DataFrame(cur.execute("""
        SELECT * FROM RECIPES        
    """))[[1,2]]

if 'ingredient_list' not in st.session_state:
    raw_data = cur.execute("""
        SELECT DISTINCT ingredient FROM ingredients
    """).fetchall()
    st.session_state.ingredient_list = [row[0] for row in raw_data]

if 'recipe_basket' not in st.session_state:
    st.session_state.recipe_basket = []

conn.close()

st.title('Meal Planner')