import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Load the data
@st.cache_data
def load_data():
    df = pd.read_parquet("dataframes/sales.parquet")
    return df

# Clean the data
def clean_data(df):
    df['date_announcement'] = pd.to_datetime(df['date_announcement'], format='%d/%m/%Y')
    df = df[['date_announcement', 'city', 'price']]
    df = df.loc[(df['date_announcement'] > '2023-01-01') & (df['date_announcement'] < datetime.now())]
    return df

def remove_price_outliers(df):
    Q1 = df['price'].quantile(0.01)
    Q3 = df['price'].quantile(0.95)
    IQR = Q3 - Q1
    df = df[(df['price'] > (Q1 - 1.5 * IQR)) & (df['price'] < (Q3 + 1.5 * IQR))]
    return df

# Create the time series plot
def plot_average_prices(df, cities):
    # Filter by selected cities
    df = df[df['city'].isin(cities)]
    
    # Aggregate data by month
    df['month'] = df['date_announcement'].dt.to_period('M').dt.to_timestamp()
    df = df.groupby(['month', 'city'])['price'].mean().reset_index()
    
    # Plot
    fig = px.line(df, x='month', y='price', color='city', 
                  title='',
                  labels={'month': 'Month', 'price': 'Average Price'},
                  markers=True)
    
    fig.update_layout(xaxis_title='Month', yaxis_title='Average Price')
    st.plotly_chart(fig)

# Page Title
st.title("Average Prices Over Time by City")

# Load and clean data
df = load_data()
df = clean_data(df)
df = remove_price_outliers(df)

# Get unique cities
cities = df['city'].unique()

# Dropdown menu for city selection
selected_cities = st.multiselect(
    'Select cities to display:',
    options=cities,
    default=['Milano', 'Genova', 'Roma', 'Torino']
)

# Plot the data for the selected cities
plot_average_prices(df, selected_cities)
