import streamlit as st
import sqlite3
import time

def find_recipes(ingredients: list):
    conn = sqlite3.connect('meal_planner.db')
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    placeholders = ', '.join(['?'] * len(ingredients))
    query = f"""
            SELECT recipes.name FROM recipes
            JOIN ingredients ON recipes.id = ingredients.recipe_id
            WHERE ingredients.ingredient IN ({placeholders})
            GROUP BY recipes.name
            HAVING COUNT(DISTINCT ingredients.ingredient) = ?
    """

    params = ingredients + [len(ingredients)]
    res = [row[0] for row in cur.execute(query, params).fetchall()]

    conn.close()

    return res

def get_all_recipes() -> list:
    conn = sqlite3.connect('meal_planner.db')
    cur = conn.cursor()
    cur.execute('PRAGMA foreign_keys = ON;')

    recipes = cur.execute("""
        SELECT name FROM recipes
    """).fetchall()

    conn.close()
    
    return [row[0].title() for row in recipes]

def get_all_ingredients() -> list:
    conn = sqlite3.connect('meal_planner.db')
    cur = conn.cursor()
    cur.execute('PRAGMA foreign_keys = ON;')

    ingredients = cur.execute("""
        SELECT DISTINCT ingredient FROM ingredients
    """).fetchall()

    conn.close()
    
    return [row[0].title() for row in ingredients]

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
        return [row[0].title() for row in res], res[0][1]
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
    
    conn.commit()
    conn.close()

    return True

def remove_from_db(name) -> True:
    conn = sqlite3.connect('meal_planner.db')
    cur = conn.cursor()
    cur.execute('PRAGMA foreign_keys = ON;')

    cur.execute(
        'DELETE FROM recipes WHERE name=?', 
        (name.lower(),)
    )

    conn.commit()
    conn.close()

    return True

def build_ingredient_selector(mode: str) -> True:
    if 'permanent_selections' not in st.session_state:
        st.session_state.permanent_selections = []
    if 'ingredient_list' not in st.session_state:
        st.session_state.ingredient_list = get_all_ingredients()

    def sync_selections():
        st.session_state.permanent_selections = st.session_state[f'ingred_ms_{mode}']

    def clear_all():
        st.session_state.permanent_selections = []
        st.session_state.ingred_ms_add = []
        st.session_state.ingred_ms_edit = []
        st.session_state.ready_to_save = False

    st.multiselect(
        'Select Ingredients:',
        options=st.session_state.ingredient_list,
        default=st.session_state.permanent_selections,
        key=f'ingred_ms_{mode}',
        on_change=sync_selections
    )

    with st.popover('Add New Ingredient'):
            with st.form('add_form', clear_on_submit=True):
                new_ingred = st.text_input('Enter new ingredient name:')
                submitted = st.form_submit_button('Confirm Add')
                
                if submitted:
                    if new_ingred and new_ingred.title() not in st.session_state.ingredient_list:
                        st.session_state.ingredient_list.append(new_ingred)
                        st.session_state.permanent_selections.append(new_ingred)
                        st.success('New ingredient added!')
                        time.sleep(1)
                        st.rerun()
                    elif not new_ingred:
                        st.error('Name is required!')
                    else:
                        st.error('Ingredient already exists!')

    for ingred in st.session_state.permanent_selections:
        st.write(f'- {ingred}')

    if st.session_state.permanent_selections:
        st.button('Clear Selections', key='clear_btn', on_click=clear_all)

    if st.button('Save Recipe', key=f'save_btn_{mode}'):
        if not st.session_state.permanent_selections:
            st.error('Please provide ingredients!')
        else:
            return True

def build_authenticator(mode) -> bool:
        st.info('Authentication required to modify the database.')
        pwd = st.text_input('Enter Database Password:', type='password', key=f'pwd_field_{mode}')

        if st.button('Cancel', key=f'cancel_btn_{mode}'):
            st.session_state.ready_to_save = False
            st.session_state.ready_to_del = False
            st.rerun()
        
        if pwd == st.secrets['db_pwd']:
            return True
        elif pwd:
            st.error('Incorrect Password')
            return False
        
def build_recipe_selector(mode:str):
    name = st.selectbox(
        'Select Existing Recipe:',
        options=get_all_recipes(),
        index=None,
        key=f'name_input_{mode}'
    )

    return name
        
@st.dialog('Confirm Action')
def confirm_dialog(name, link, ingredients, mode):
    st.write(
        f'Are you sure you want to {mode} **{name}** with {len(ingredients)} ingredients?'
    )
    
    col1, col2 = st.columns(2)
    if col1.button('Confirm and Save'):
        if mode == 'add':
            add_to_db(name, link, ingredients)
        if mode == 'edit':
            remove_from_db(name)
            add_to_db(name, link, ingredients)
        if mode == 'delete':
            remove_from_db(name)
        st.success('Action successful!')
        time.sleep(1)
        reset_session_state(mode)
        st.rerun()
            
    if col2.button('Cancel'):
        reset_session_state(mode)
        st.rerun()