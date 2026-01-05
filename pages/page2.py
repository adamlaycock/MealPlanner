import streamlit as st

st.title('Add, Edit, or Remove Recipes')

tab1, tab2, tab3 = st.tabs(['Add', 'Edit', 'Remove'])

with tab1:
    st.header('Add Recipe')

    st.subheader('Name & Link')
    name = st.text_input('Enter Recipe Name:')
    link = st.text_input('Enter Recipe Link (If Applicable):')

    st.subheader('Ingredients')
    options = st.session_state.ingredient_list + ['Add new ingredient...']
    selected_item = st.selectbox(
        'Search or Select Ingredient',
        options=options,
        index=0,
        key='ingredient_selector'
    )

    if selected_item == 'Add new ingredient...':
        new_ingred = st.text_input('Enter the name of the new ingredient:')
        if st.button('Save & Add'):
            if new_ingred and new_ingred not in st.session_state.ingredient_list:
                st.session_state.ingredient_list.append(new_ingred)
                st.session_state.recipe_basket.append(new_ingred)
                st.success(f'Added {new_ingred}!')
                st.rerun()

    elif selected_item and selected_item != '':
        if st.button(f'Add {selected_item} to Recipe'):
            if selected_item not in st.session_state.recipe_basket:
                st.session_state.recipe_basket.append(selected_item)
                st.toast(f'{selected_item} added!')

    for ingred in st.session_state.recipe_basket:
        st.write(f'- {ingred}')

    if st.button('Clear Basket'):
        st.session_state.recipe_basket = []
        st.rerun()