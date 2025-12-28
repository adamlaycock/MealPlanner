import pandas as pd

INGREDS_DF = pd.read_csv(
    r'C:\Users\adamm\OneDrive\Documents\R&D\MealPlanner\ingredients.csv'
)

def build_list(ids: list) -> pd.DataFrame:
    filt_ingreds_df = INGREDS_DF[INGREDS_DF['ID'].isin(ids)]['Ingredient']
    ingreds = pd.DataFrame(
        filt_ingreds_df.value_counts()
    ).reset_index()
    ingreds['count'] = ('x' + ingreds['count'].astype(str)).replace('x1', '')

    return(ingreds)

df = build_list([1, 9, 10])
df