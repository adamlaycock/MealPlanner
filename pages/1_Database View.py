import streamlit as st
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

if recipes and st.session_state.search_btn_find:
    clean_recipes = "\n".join(recipes)
    st.code(
        clean_recipes,
        language=None
    )
elif st.session_state.search_btn_find:
    st.code(
        'No Recipes Found'
    )