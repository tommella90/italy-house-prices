#%%
import pandas as pd
import numpy as np

def load_data():
    df = pd.read_parquet("dataframes/italy_housing_price_rent_raw.parquet.gzip")
    municipality_coords = pd.read_csv("geodata/municipalities_centroids.csv")
    region_coords = pd.read_csv("geodata/regions_centroids.csv")
    # dd
    return df, municipality_coords, region_coords


def clean_data(df):

    # PRICE
    df['prezzo'] = df['prezzo'].str.replace('€', '')
    df['prezzo'] = df['prezzo'].str.replace('[^0-9.]', '', regex=True)
    df['prezzo'] = df['prezzo'].str.replace('.', '')
    df['prezzo'][df['prezzo'] == ''] = np.nan
    df['prezzo'] = df['prezzo'].astype(float)

# %%
df, municipality_coords, region_coords = load_data()
df = clean_data(df)

# %%
df['prezzo'] = df['prezzo'].str.replace('€', '')
df['prezzo'] = df['prezzo'].str.replace('[^0-9.]', '', regex=True)
df['prezzo'] = df['prezzo'].str.replace('.', '')
df['prezzo'][df['prezzo'] == ''] = np.nan
df['prezzo'] = df['prezzo'].astype(float)

# %%
df = df.rename(columns={'Riferimento e Data annuncio': "data"})
date_regex = r'(\d{2}/\d{2}/\d{4})'
df['datetime'] = df['data'].str.extract(date_regex, expand=True)
df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%m/%Y')
#df = df.loc[(df['datetime'] > '2023-01-01') & (df['datetime'] < TODAY)]


# %%
df['datetime']
# %%
