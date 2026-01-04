import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect('meal_planner.db')
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

recipes = pd.DataFrame(cur.execute("""
    SELECT * FROM RECIPES        
"""))[[1,2]]

conn.close()

st.title('Meal Planner')

tab1, tab2, tab3 = st.tabs(['Home', 'Add/Edit Recipes', 'Shopping List'])

with tab1:
    st.header('Home')
    st.subheader('Stored Recipes')

    st.dataframe(
        recipes, 
        column_config={
            1: 'Name',
            2: 'Link'
        },
        hide_index=True
    )

with tab2:
    st.header('Add/Edit Recipes')
    st.subheader('Add Recipe')

    with st.form(key='add_form'):
        name = st.text_input('Enter Recipe Name:')
        link = st.text_input('Enter Recipe Link (If Applicable):')

        pword = st.text_input(
            label='Enter Authentication:',
            type='password'
        )
        st.form_submit_button()

with tab3:
    st.header('Shopping List')