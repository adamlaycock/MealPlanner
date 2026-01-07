import streamlit as st
import sqlite3

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

def get_all_ingredients() -> list:
    conn = sqlite3.connect('meal_planner.db')
    cur = conn.cursor()
    cur.execute('PRAGMA foreign_keys = ON;')

    ingredients = cur.execute("""
        SELECT ingredient FROM ingredients
    """).fetchall()

    conn.close()
    
    return [row[0] for row in ingredients]

def build_ingredient_selector(mode):
    if 'ingredient_list' not in st.session_state:
        st.session_state.ingredient_list = get_all_ingredients()
    if 'ingredient_selections' not in st.session_state:
        st.session_state.ingredient_selections = []

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
            st.rerun()

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

build_ingredient_selector('find')

recipes = find_recipes(st.session_state.ingredient_selections)
st.write(recipes)

