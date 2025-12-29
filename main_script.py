import pandas as pd

INGREDS_DF = pd.read_csv(
    r'C:\Users\adamm\OneDrive\Documents\R&D\MealPlanner\ingredients.csv'
)

RECIPE_DF = pd.read_csv(
    r'C:\Users\adamm\OneDrive\Documents\R&D\MealPlanner\recipes.csv'
)

def build_list(ids: list) -> pd.DataFrame:
    filt_ingreds_df = INGREDS_DF[INGREDS_DF['ID'].isin(ids)]['Ingredient']
    ingreds = pd.DataFrame(
        filt_ingreds_df.value_counts()
    ).reset_index()
    ingreds['count'] = ('x' + ingreds['count'].astype(str)).replace('x1', '')
    ingreds.columns = ['ingredient', 'occurrences']
    ingreds = ingreds.sort_values(by='ingredient')

    return(ingreds)

def add_recipe(name: str, link: str, ingreds: list):
    global RECIPE_DF, INGREDS_DF

    ingreds = [ing.lower() for ing in ingreds]

    new_id = RECIPE_DF['ID'].max() + 1
    RECIPE_DF.loc[len(RECIPE_DF)] = [name, link, new_id]

    new_rows = pd.DataFrame({
        'Ingredient': ingreds,
        'ID': new_id
    })
    INGREDS_DF = pd.concat([INGREDS_DF, new_rows])

    # INGREDS_DF.to_csv(
    #     r'C:\Users\adamm\OneDrive\Documents\R&D\MealPlanner\ingredients.csv',
    #     index=False
    # )

def remove_recipe(name:str):
    global RECIPE_DF, INGREDS_DF

    remove_id = RECIPE_DF.loc[RECIPE_DF['Name'] == name, 'ID'].iloc[0]
    RECIPE_DF = RECIPE_DF[RECIPE_DF['ID'] != remove_id]
    INGREDS_DF = INGREDS_DF[INGREDS_DF['ID'] != remove_id]

    # RECIPE_DF.to_csv(
    #     r'C:\Users\adamm\OneDrive\Documents\R&D\MealPlanner\recipes.csv',
    #     index=False
    # )
    # INGREDS_DF.to_csv(
    #     r'C:\Users\adamm\OneDrive\Documents\R&D\MealPlanner\ingredients.csv',
    #     index=False
    # )