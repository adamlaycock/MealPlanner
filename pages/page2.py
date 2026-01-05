import streamlit as st
import sqlite3
import time

if 'show_auth' not in st.session_state:
    st.session_state.show_auth = False
if 'recipe_basket' not in st.session_state:
    st.session_state.recipe_basket = []
if 'show_password_field' not in st.session_state:
    st.session_state.show_password_field = False

st.title('Add, Edit, or Remove Recipes')

tab1, tab2, tab3 = st.tabs(['Add', 'Edit', 'Remove'])

def save_to_db(name, link, ingredients):
    conn = sqlite3.connect('meal_planner.db')
    cur = conn.cursor()
    cur.execute('PRAGMA foreign_keys = ON;')
    
    cur.execute(
        'INSERT INTO recipes (name, link) VALUES (?, ?)', 
        (name.lower(), link)
    )
    new_id = cur.lastrowid
    
    ingredient_data = [(i.lower(), new_id) for i in ingredients]
    cur.executemany(
        'INSERT INTO ingredients (ingredient, recipe_id) VALUES (?, ?)', 
        ingredient_data
    )
    
    #conn.commit()
    conn.close()
    return True

@st.dialog('Confirm Recipe')
def confirm_save_dialog(name, link, ingredients):
    st.write(f'Are you sure you want to save **{name}** with {len(ingredients)} ingredients?')
    
    col1, col2 = st.columns(2)
    if col1.button('Confirm and Save'):
        if save_to_db(name, link, ingredients):
            st.success('Recipe saved successfully!')
            time.sleep(3)
            st.session_state.recipe_basket = []
            st.session_state.ingredient_selector = ''
            st.session_state.name_input = ''
            st.session_state.link_input = ''
            st.rerun()
            
    if col2.button('Cancel'):
        st.rerun()

with tab1:
    st.header('Add Recipe')

    st.subheader('Name & Link')
    name = st.text_input('Enter Recipe Name:', key='name_input')
    link = st.text_input('Enter Recipe Link (If Applicable):', key='link_input')

    st.subheader('Ingredients')
    options = [''] + st.session_state.ingredient_list + ['Add new ingredient...']
    selected_item = st.selectbox(
        'Search or Select Ingredient',
        options=options,
        key='ingredient_selector' 
    )

    if selected_item == 'Add new ingredient...':
        new_ingred = st.text_input('Enter the name of the new ingredient:')
        if st.button('Save & Add'):
            if new_ingred and new_ingred not in st.session_state.ingredient_list:
                st.session_state.ingredient_list.append(new_ingred)
                st.session_state.recipe_basket.append(new_ingred)
                st.success(f'Added {new_ingred}!')
                st.session_state.ingredient_selector = ''
                st.rerun()

    elif selected_item and selected_item != '':
        if st.button(f'Add {selected_item} to Recipe'):
            if selected_item not in st.session_state.recipe_basket:
                st.session_state.recipe_basket.append(selected_item)
                st.toast(f'{selected_item} added!')

    for ingred in st.session_state.recipe_basket:
        st.write(f'- {ingred}')

    if st.button('Clear Selections'):
        st.session_state.recipe_basket = []
        st.rerun()
    
    st.divider()

    if st.button('Save Recipe'):
        if not name or not st.session_state.recipe_basket:
            st.error('Please provide a name and ingredients!')
        else:
            st.session_state.show_auth = True

    if st.session_state.show_auth:
        st.info('Authentication required to modify the database.')
        pwd = st.text_input('Enter Database Password:', type='password', key='pwd_field')
        
        col_auth1, col_auth2 = st.columns([1, 5])
        
        if pwd == st.secrets['db_pwd']:
            st.session_state.show_auth = False
            confirm_save_dialog(name, link, st.session_state.recipe_basket)
        elif pwd:
            st.error('Incorrect Password')

        if col_auth1.button('Cancel Save'):
            st.session_state.show_auth = False
            st.rerun()