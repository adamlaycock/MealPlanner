import streamlit as st
import sqlite3
from functions import *

st.title('Database View')
st.header('Stored Recipes')

# st.dataframe(
#     st.session_state.recipes_df, 
#     column_config={
#         1: 'Name',
#         2: 'Link'
#     },
#     hide_index=True
# )

st.header('Find Recipes')

recipes = build_ingredient_selector('find')

st.write(recipes)