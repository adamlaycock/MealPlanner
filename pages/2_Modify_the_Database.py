import streamlit as st
import sqlite3
import time
from functions import *
        
st.title('Add, Edit, or Delete Recipes')

tab1, tab2, tab3 = st.tabs(['Add', 'Edit', 'Delete'])

# with tab1:
#     st.header('Add Recipe')

#     st.subheader('Name & Link')
#     name = st.text_input('Enter Recipe Name:', key='name_input_add')
#     link = st.text_input('Enter Recipe Link (If Applicable):', key='link_input_add')

#     st.subheader('Ingredients')
#     build_ingredient_selector('add')

#     if st.session_state.ready_to_save and name:
#         st.subheader('Authentication')
#         if build_authenticator('add') and name:
#             confirm_dialog(
#                 name, 
#                 link, 
#                 st.session_state.ingredient_selections, 
#                 'add'
#             )

# with tab2:
#     st.header('Edit Recipe')
#     name = build_recipe_selector('edit')

#     if name:
#         ingredients, link = get_recipe_info(name)
#         build_ingredient_selector('edit')
#         if st.session_state.ready_to_save and name:
#             st.subheader('Authentication')
#             if build_authenticator('edit') and name:
#                 confirm_dialog(
#                     name,
#                     link, 
#                     st.session_state.ingredient_selections, 
#                     'edit'
#                 )

# with tab3:
#     if 'ready_to_del' not in st.session_state:
#         st.session_state.ready_to_del = False

#     st.header('Delete Recipe')
#     name = build_recipe_selector('delete')

#     if name:
#         ingredients, link = get_recipe_info(name)
#         if st.button('Delete Recipe'):
#             st.session_state.ready_to_del = True
#         if st.session_state.ready_to_del and name:
#             st.subheader('Authentication')
#             if build_authenticator('edit') and name:
#                 confirm_dialog(name, link, ingredients, 'delete')

with tab1:
    st.header('Add Recipe')

    st.subheader('Name & Link')
    name = st.text_input('Enter Recipe Name:', key='name_input_add')
    link = st.text_input('Enter Recipe Link (If Applicable):', key='link_input_add')

    st.subheader('Ingredients')
    build_ingredient_selector('add')

    if st.session_state.ready_to_save and name:
        st.subheader('User Authentication')
        if build_authenticator() and name:
            confirm_dialog(
                name.lower(),
                link,
                st.session_state.permanent_selections,
                'add'
            )

with tab2:
    if 'ready_to_del' not in st.session_state:
        st.session_state.ready_to_del = False


    st.header('Edit Recipe')
    name = build_recipe_selector('edit')

    if name:
        link = get_recipe_info(name.lower())[1]

        st.subheader('Ingredients')
        build_ingredient_selector('edit')

        if st.session_state.ready_to_save and name:
            st.subheader('User Authentication')
            if build_authenticator() and name:
                confirm_dialog(
                    name.lower(),
                    link,
                    st.session_state.permanent_selections,
                    'edit'
                )

with tab3:
    st.header('Delete Recipe')
    name = build_recipe_selector('delete')

    if name:
        ingredients, link = get_recipe_info(name)

        if st.button('Delete Recipe'):
            st.session_state.ready_to_del = True

        if st.session_state.ready_to_del and name:
            st.subheader('User Authentication')
            if build_authenticator() and name:
                confirm_dialog(
                    name.lower(), 
                    link, 
                    ingredients, 
                    'delete'
                )