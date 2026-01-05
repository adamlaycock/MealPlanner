import streamlit as st

st.title('Stored Recipes')

st.dataframe(
    st.session_state.recipes_df, 
    column_config={
        1: 'Name',
        2: 'Link'
    },
    hide_index=True
)

