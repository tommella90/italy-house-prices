
#%%
import pandas as pd
import numpy as np
from datetime import date
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
import streamlit as st
#from streamlit_folium import st_folium
from datetime import datetime
import warnings

# ignore warnings
warnings.filterwarnings("ignore")

## CONFIG ##
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    page_title="spotify_recommender",
    page_icon="🏠"
    )


import streamlit as st

TODAY = np.datetime64(date.today())

FULL_CALENDAR = pd.DataFrame(pd.date_range(start="2023-01-01", end=TODAY), columns=['date_announcement'])

REGIONI = ('ITALY',
           'Abruzzo', 'Basilicata', 'Calabria', 'Campania', 'Emilia-Romagna',
           'Friuli-Venezia Giulia', 'Lazio', 'Liguria', 'Lombardia', 'Marche',
           'Molise', 'Piemonte', 'Puglia', 'Sardegna', 'Sicilia', 'Toscana',
           'Veneto', 'Valle-D-Aosta', 'Trentino-Alto-Adige'
           )


# st.markdown(
#     """
#     <div style="display: flex; align-items: center; justify-content: flex-start;">
#         <a href="https://www.linkedin.com/in/tommaso-ramella/" target="_blank">
#             <img src="icons/linkedin.png" alt="LinkedIn" style="width: 30px; height: 30px;"/>
#         </a>
#         <span style="margin-left: 10px; font-size: 16px;">Connect with me on LinkedIn</span>
#     </div>
#     """,
#     unsafe_allow_html=True
# )


#%% FUNCTIONS
st.title("ITALIAN HOUSE PRICES")

st.markdown("### This app show the average price of rents in Italy")
# st.markdown("###**Data source:** [immobiliare.it](https://www.immobiliare.it/)")


@st.cache_data
def load_data():
    # df = pd.read_parquet("dataframes/italy_housing_price_sale_raw.parquet.gzip")
    df = pd.read_parquet("dataframes/sales.parquet") 
    municipality_coords = pd.read_csv("geodata/municipalities_centroids.csv")
    region_coords = pd.read_csv("geodata/regions_centroids.csv")
    return df, municipality_coords, region_coords


def clean_data(df, coordinates_df):
    df['date_announcement'] = pd.to_datetime(df['date_announcement'], format='%d/%m/%Y')
    df = df.loc[(df['date_announcement'] > '2023-01-01') & (df['date_announcement'] < TODAY)]
    df = pd.merge(df, FULL_CALENDAR, how='outer', on='date_announcement')

    df = df.dropna(subset=['city', 'price'])
    df = df[['date_announcement', 'city', 'price']]

    df = df.merge(coordinates_df, left_on='city', right_on='name', how='left')
    return df


def get_mean_price_by_area(df, area, math_option='mean'):
    if math_option == 'mean':
        return df['price'].groupby(df[area]).mean().sort_values(ascending=True)
    elif math_option == 'median':
        return df['price'].groupby(df[area]).median().sort_values(ascending=True)
    elif math_option == 'max':
        return df['price'].groupby(df[area]).max().sort_values(ascending=True)


def price_per_municipality(df, geo_data, EXTREME_CASES=10):
    prices_by_municipality = get_mean_price_by_area(df, 'city')
    prices_by_municipality = prices_by_municipality.sort_values(ascending=True)
    prices_by_municipality_extremes = pd.concat(
        [prices_by_municipality.head(EXTREME_CASES),
         prices_by_municipality.tail(EXTREME_CASES)],
        axis=0)

    fig1, ax = plt.subplots()
    ax.barh(prices_by_municipality_extremes.index, prices_by_municipality_extremes)
    ax.set_title("ITALIAN RENTS:\n Price by city")
    ax.set_xlabel("Euros")
    ax.set_ylabel("Municipality")
    st.pyplot(fig1)


def map_municipalities(df, date_start, date_end, min_price, max_price, math_option='mean'):
    # Slice dataframe
    df = df.loc[(df['date_announcement'] >= date_start) & (df['date_announcement'] <= date_end)]
    df = df[(df['price'] >= min_price) & (df['price'] <= max_price)]

    # Group by municipality
    if math_option == 'mean':
        df = df.groupby(['city'])['price'].mean().reset_index()
    elif math_option == 'median':
        df = df.groupby(['city'])['price'].median().reset_index()
    elif math_option == 'max':
        df = df.groupby(['city'])['price'].max().reset_index()

    # Merge with coordinates
    df = df.merge(municipalities_centroids, left_on='city', right_on='name', how='left')
    df = df[['city', 'lat', 'lon', 'price']]
    df = df.dropna(subset=['lat', 'lon'])

    # Determine the range for colors based on the data
    min_color = df['price'].min()
    max_color = df['price'].max()

    # Create the map with smaller scatter markers
    fig = px.scatter_mapbox(df, lat="lat", lon="lon",
                            hover_name="city",
                            hover_data=["price"],
                            color="price",
                            color_continuous_scale="turbo",
                            range_color=(min_color, max_color),
                            size="price",
                            size_max=10,  # Adjust this value to control marker size
                            zoom=4.3,
                            center=dict(lat=41.8719, lon=12.5674)
                            )

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":5,"t":0,"l":0,"b":0})

    st.plotly_chart(fig)


provinces = pd.read_excel('geodata/province-italiane.xlsx')
provinces = list(provinces['Provincia'])

# components
price_ranges_city = st.slider('Select a price range',
                         min_value=50000, max_value=5000000,
                         value=(0, 1000000))
min_price = price_ranges_city[0]
max_price = price_ranges_city[1]

today_string = np.datetime_as_string(TODAY, unit='D')
start_time = datetime.strptime("2023-01-01", "%Y-%m-%d")
end_time = datetime.strptime(today_string, "%Y-%m-%d")

date_values = st.slider('Select a date range',
                        min_value=start_time,
                        max_value=end_time,
                        value=(start_time, end_time),
                        format="YYYY-MM-DD")

math_option = st.radio(
    "Select: 👉",   
    key="visibility",
    options=["mean", "median", "max"]
)

select_only_provinces = st.checkbox('Select only provinces')


df, municipalities_centroids, regions_centroids = load_data()

df = clean_data(df, municipalities_centroids)

if select_only_provinces:
    df = df.loc[df['city'].isin(provinces)]


st.write(date_values[0])

map_municipalities(df,
                   date_start=date_values[0], date_end=date_values[1],
                   min_price=min_price, max_price=max_price,
                   math_option=math_option
                   )
