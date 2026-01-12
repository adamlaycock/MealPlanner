import streamlit as st
import sqlite3
import pandas as pd
from functions import *

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