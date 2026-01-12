import streamlit as st
import time
import pandas as pd
from sqlalchemy import text

def find_recipes(ingredients: list):
    conn = st.connection('postgresql', type='sql')

    params = {f"ing{i}": ing.lower() for i, ing in enumerate(ingredients)}
    params["required_count"] = len(ingredients)

    placeholders = ', '.join([f":{key}" for key in params.keys() if key.startswith("ing")])

    query = f"""
            SELECT recipes.name FROM recipes
            JOIN ingredients ON recipes.id = ingredients.recipe_id
            WHERE ingredients.ingredient IN ({placeholders})
            GROUP BY recipes.name
            HAVING COUNT(DISTINCT ingredients.ingredient) = :required_count
    """

    df = conn.query(query, params=params, ttl='5m')

    return [name.title() for name in df['name'].tolist()]

def get_all_recipes() -> list:
    conn = st.connection('postgresql', type='sql')

    query = """
        SELECT name FROM recipes
    """
    df = conn.query(query)
    
    return [name.title() for name in df['name'].tolist()]

def get_all_ingredients() -> list:
    conn = st.connection('postgresql', type='sql')

    query = """
        SELECT DISTINCT ingredient FROM ingredients
    """

    df = conn.query(query, ttl='5m')

    return [ing.title() for ing in df['ingredient'].tolist()]

def get_recipe_info(recipe: str) -> tuple[list, str]:
    conn = st.connection('postgresql', type='sql')

    query = """
        SELECT ingredients.ingredient, recipes.link 
        FROM ingredients
        JOIN recipes ON ingredients.recipe_id = recipes.id
        WHERE recipes.name = :recipe_name
    """

    df = conn.query(query, params={"recipe_name": recipe.lower()}, ttl='5m')
    
    if not df.empty:
        return [ing.title() for ing in df['ingredient'].to_list()], df['link'].iloc[0]
    else:
        return [], None

def add_to_db(name, link, ingredients) -> True:
    conn = st.connection('postgresql', type='sql')
    
    with conn.session as s:
        recipe_query = text("""
            INSERT INTO recipes (name, link) 
            VALUES (:name, :link) 
            RETURNING id        
        """)

        result = s.execute(recipe_query, {"name": name.lower(), "link": link})
        new_id = result.fetchone()[0]
    
        ing_query = text("""
            INSERT INTO ingredients (ingredient, recipe_id) 
            VALUES (:ingredient, :recipe_id)
        """)

        for i in ingredients:
            s.execute(ing_query, {"ingredient": i.lower(), "recipe_id": new_id})
    
        s.commit()

    return True

def remove_from_db(name) -> True:
    conn = st.connection('postgresql', type='sql')

    with conn.session as s:
        query = text("""
            DELETE FROM recipes WHERE name = :name         
        """)

        s.execute(query, {"name": name.lower()})

        s.commit()

    return True

def build_ingredient_selector(mode: str) -> True:
    if 'permanent_selections' not in st.session_state:
        st.session_state.permanent_selections = []
    if 'ingredient_list' not in st.session_state:
        st.session_state.ingredient_list = get_all_ingredients()
    if 'ready_to_save' not in st.session_state:
        st.session_state.ready_to_save = False

    def sync_selections():
        st.session_state.permanent_selections = st.session_state[f'ingred_ms_{mode}']

    def clear_all():
        st.session_state.permanent_selections = []
        st.session_state.ingred_ms_add = []
        st.session_state.ingred_ms_edit = []
        st.session_state.ingred_ms_find = []
        st.session_state.ready_to_save = False

    st.multiselect(
        'Select Ingredients:',
        options=st.session_state.ingredient_list,
        default=st.session_state.permanent_selections,
        key=f'ingred_ms_{mode}',
        on_change=sync_selections
    )

    if mode != 'find':
        with st.popover('Add New Ingredient'):
                with st.form(f'add_form_{mode}', clear_on_submit=True):
                    new_ingred = st.text_input('Enter new ingredient name:')
                    submitted = st.form_submit_button('Confirm Add')
                    
                    if submitted:
                        if new_ingred and new_ingred.title() not in st.session_state.ingredient_list:
                            st.session_state.ingredient_list.append(new_ingred)
                            st.session_state.permanent_selections.append(new_ingred)
                            st.success('New ingredient added!')
                            st.rerun()
                        elif not new_ingred:
                            st.error('Name is required!')
                        else:
                            st.error('Ingredient already exists!')

    for ingred in st.session_state.permanent_selections:
        st.write(f'- {ingred}')

    if st.session_state.permanent_selections:
        st.button('Clear Selections', key=f'clear_btn_{mode}', on_click=clear_all)

    if mode != 'find':
        if st.button('Save Recipe', key=f'save_btn_{mode}'):
            if not st.session_state.permanent_selections:
                st.error('Please provide ingredients!')
            else:
                st.session_state.ready_to_save = True
    else:
        if st.button('Search', key=f'search_btn_{mode}'):
            if not st.session_state.permanent_selections:
                st.error('Please provide ingredients!')
            else:
                return find_recipes(
                    [i.lower() for i in st.session_state.permanent_selections]
                )


def build_authenticator() -> bool:
        st.info('Authentication required to modify the database.')
        pwd = st.text_input('Enter Database Password:', type='password', key='pwd_field')

        st.button('Cancel', key='cancel_btn', on_click=reset_session_state)
        
        if pwd == st.secrets['db_pwd']:
            return True
        elif pwd:
            st.error('Incorrect Password')
            return False
        
def build_recipe_selector(mode: str):
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
        reset_session_state()
        st.cache_data.clear()
        st.rerun()
            
    if col2.button('Cancel'):
        reset_session_state()
        st.rerun()

def build_list(names: list):
    conn = st.connection('postgresql', type='sql')

    params = {f"name{i}": name for i, name in enumerate(names)}
    placeholders = ', '.join([f":{key}" for key in params.keys()])

    query = f"""
        SELECT ingredients.ingredient FROM recipes
        JOIN ingredients ON recipes.id = ingredients.recipe_id
        WHERE name IN ({placeholders})
    """

    res = pd.DataFrame(
        conn.query(query, params=params, ttl='5m').value_counts()
    ).reset_index().sort_values(by='ingredient')

    shopping_list = (
        res['ingredient'].str.title() + ' x' + res['count'].astype(str)
    ).str.replace('x1', '')
    
    return shopping_list

def reset_session_state():
    st.session_state.name_input_add = ''
    st.session_state.link_input_add = ''
    st.session_state.ingred_ms_add = []
    st.session_state.ingred_ms_edit = []
    st.session_state.ready_to_save = False
    st.session_state.ready_to_del = False
    st.session_state.name_input_edit = None
    st.session_state.name_input_delete = None
    st.session_state.permanent_selections = []

def build_recipe_df() -> pd.DataFrame:
    conn = st.connection('postgresql', type='sql')

    query = """
        SELECT name, link FROM recipes
    """

    df = conn.query(query, ttl='5m')
    df['name'] = df['name'].str.title()
    
    return df
