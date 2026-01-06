import streamlit as st
import sqlite3
import time

def get_all_recipes() -> list:
    conn = sqlite3.connect('meal_planner.db')
    cur = conn.cursor()
    cur.execute('PRAGMA foreign_keys = ON;')

    recipes = cur.execute("""
        SELECT name FROM recipes
    """).fetchall()

    conn.close()
    
    return [row[0] for row in recipes]

def get_all_ingredients() -> list:
    conn = sqlite3.connect('meal_planner.db')
    cur = conn.cursor()
    cur.execute('PRAGMA foreign_keys = ON;')

    ingredients = cur.execute("""
        SELECT ingredient FROM ingredients
    """).fetchall()

    conn.close()
    
    return [row[0] for row in ingredients]

def get_recipe_info(recipe: str) -> tuple[list, str]:
    conn = sqlite3.connect('meal_planner.db')
    cur = conn.cursor()
    cur.execute('PRAGMA foreign_keys = ON;')

    res = cur.execute(
        """
        SELECT ingredients.ingredient, recipes.link 
        FROM ingredients
        JOIN recipes ON ingredients.recipe_id = recipes.id
        WHERE recipes.name = ?
        """, 
        (recipe,)
    ).fetchall()

    conn.close()
    
    if res:
        return [row[0] for row in res], res[0][1]
    else:
        return [], None


def add_to_db(name, link, ingredients) -> True:
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

def remove_from_db(name) -> True:
    conn = sqlite3.connect('meal_planner.db')
    cur = conn.cursor()
    cur.execute('PRAGMA foreign_keys = ON;')

    cur.execute(
        'DELETE FROM recipes WHERE name=?', 
        (name,)
    )

    #conn.commit()
    conn.close()

    return True


def build_ingredient_selector(mode):
    if 'ingredient_list' not in st.session_state:
        st.session_state.ingredient_list = get_all_ingredients()
    if 'ingredient_selections' not in st.session_state:
        st.session_state.ingredient_selections = []
    if 'ready_to_save' not in st.session_state:
        st.session_state.ready_to_save = False

    options = st.session_state.ingredient_list + ['Add new ingredient...']
    selected_item = st.selectbox(
        'Search or Select Ingredient:',
        options=options,
        key=f'ingredient_selector_{mode}',
        index=None
    )

    if selected_item == 'Add new ingredient...':
        new_ingred = st.text_input('Enter the name of the new ingredient:')
        if st.button('Save & Add'):
            if new_ingred and new_ingred not in st.session_state.ingredient_list:
                st.session_state.ingredient_list.append(new_ingred)
                st.session_state.ingredient_selections.append(new_ingred)
                st.success(f'Added {new_ingred}!')
                st.rerun()

    elif selected_item and selected_item != '':
        if st.button(f'Add {selected_item} to Recipe', key=f'add_btn_{mode}'):
            if selected_item not in st.session_state.ingredient_selections:
                st.session_state.ingredient_selections.append(selected_item)
                st.toast(f'{selected_item} added!')

    for ingred in st.session_state.ingredient_selections:
        st.write(f'- {ingred}')

    if st.session_state.ingredient_selections:
        if st.button('Clear Selections', key=f'clear_btn_{mode}'):
            st.session_state.ingredient_selections = []
            st.session_state.ready_to_save = False
            st.rerun()

    if st.button('Save Recipe', key=f'save_btn_{mode}'):
        if not st.session_state.ingredient_selections:
            st.error('Please provide ingredients!')
        else:
            st.session_state.ready_to_save = True

def build_authenticator(mode) -> bool:
        st.info('Authentication required to modify the database.')
        pwd = st.text_input('Enter Database Password:', type='password', key=f'pwd_field_{mode}')

        if st.button('Cancel Save', key=f'cancel_btn_{mode}'):
            st.session_state.ready_to_save = False
            st.rerun()
        
        if pwd == st.secrets['db_pwd']:
            return True
        elif pwd:
            st.error('Incorrect Password')
            return False
        
@st.dialog('Confirm Action')
def confirm_dialog(name, link, ingredients, mode):
    st.write(
        f'Are you sure you want to {mode} **{name}** with {len(ingredients)} ingredients?'
    )
    
    col1, col2 = st.columns(2)
    if col1.button('Confirm and Save'):
        if mode == 'edit':
            remove_from_db(name)
        if add_to_db(name, link, ingredients):
            st.success('Recipe saved successfully!')
            time.sleep(2)
            reset_session_state(mode)
            st.rerun()
            
    if col2.button('Cancel'):
        reset_session_state(mode)
        st.rerun()

def reset_session_state(mode):
    if mode == 'add':
        st.session_state.name_input_add = ''
        st.session_state.link_input_add = ''
        st.session_state.ingredient_selector_add = None
    if mode == 'edit':
        st.session_state.name_input_edit = None
        st.session_state.link_input_edit = ''
        st.session_state.ingredient_selector_edit = None
    st.session_state.ingredient_selections = []
    st.session_state.ready_to_save = False
        
st.title('Add, Edit, or Remove Recipes')

tab1, tab2, tab3 = st.tabs(['Add', 'Edit', 'Remove'])

with tab1:
    st.header('Add Recipe')

    st.subheader('Name & Link')
    name = st.text_input('Enter Recipe Name:', key='name_input_add')
    link = st.text_input('Enter Recipe Link (If Applicable):', key='link_input_add')

    st.subheader('Ingredients')
    build_ingredient_selector('add')

    if st.session_state.ready_to_save and name:
        st.subheader('Authentication')
        if build_authenticator('add') and name:
            confirm_dialog(name, link, st.session_state.ingredient_selections, 'add')

with tab2:
    st.header('Edit Recipe')
    name = st.selectbox(
        'Select Existing Recipe:',
        options=get_all_recipes(),
        index=None,
        key='name_input_edit'
    )

    if name:
        ingredients, link = get_recipe_info(name)
        build_ingredient_selector('edit')

        if st.session_state.ready_to_save and name:
            st.subheader('Authentication')
            if build_authenticator('edit') and name:
                confirm_dialog(name, link, st.session_state.ingredient_selections, 'edit')