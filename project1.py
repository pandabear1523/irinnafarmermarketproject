import folium
from streamlit_folium import st_folium
import streamlit as st
import pandas as pd
import os 
import numpy as np
import altair as alt
import pydeck as pdk


st.title("USA Farmers Markets 2026")


os.chdir(os.path.dirname(os.path.abspath(__file__)))

STATE_MAP = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
    'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
    'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'
}
 
PRODUCTS_DICT = {
    "Organic": "specialproductionmethods_1", 
    "Bakedgoods": "specialproductionmethods_2",
    "Cheese": "specialproductionmethods_3", 
    "Flowers": "specialproductionmethods_4",
    "Eggs": "specialproductionmethods_5", 
    "Seafood": "specialproductionmethods_6",
    "Herbs": "specialproductionmethods_7", 
    "Vegetables": "specialproductionmethods_8",
    "Honey": "specialproductionmethods_9", 
    "Jams": "specialproductionmethods_10",
    "Maple": "specialproductionmethods_11", 
    "Meat": "specialproductionmethods_12",
    "Nuts": "specialproductionmethods_13", 
    "Poultry": "specialproductionmethods_14",
    "Fruits": "specialproductionmethods_888"
}
PAYMENT_TYPES = {
    "Card": "Debit card/Credit card;", 
    "Cash": "Cash;",
    "Personal Checks": "Personal Checks;", 
    "Digital": "Venmo"
}



def load_data(filepath='farmersmarket_2026.csv', encoding='cp1252'):
  
  df = pd.read_csv(filepath, encoding=encoding)
  df['lat'] = pd.to_numeric(df['location_y'], errors='coerce')
  df['lon'] = pd.to_numeric(df['location_x'], errors='coerce')
  df['Parsed_State'] = df['Parsed_State'].astype(str).str[:2].str.upper().map(STATE_MAP)
  df = df.dropna(subset=['lat', 'lon', 'Parsed_State'])
  return df



df = load_data()

def filter_by_state(df, state_choice="All"):
    if state_choice != "All":
        return df[df['Parsed_State'] == state_choice]
    return df
 
 
def filter_by_products(df, selected_products, products_dict=PRODUCTS_DICT):
    if not selected_products:
        return df
    filtered_df = df.copy()
    for product_name in selected_products:
        if product_name in products_dict:
            filtered_df = filtered_df[filtered_df[products_dict[product_name]] == 1]
    return filtered_df
 


def filter_by_payment(df, selected_payments, payment_types=PAYMENT_TYPES):
    if not selected_payments:
        return df
    filtered_df = df.copy()
    filtered_df['acceptedpayment'] = filtered_df['acceptedpayment'].fillna("")
    for pay_name in selected_payments:
        if pay_name in payment_types:
            filtered_df = filtered_df[filtered_df['acceptedpayment'].str.contains(payment_types[pay_name])]
    return filtered_df
 
 
def filter_by_snap(df, snap_choice="All"):
   
    if snap_choice == "Yes":
        return df[df['FNAP'].str.contains('SNAP', na=False)]
    elif snap_choice == "No":
        return df[~df['FNAP'].str.contains('SNAP', na=False)]
    return df
 


df = load_data()

st.sidebar.title("Navigation")
page = st.sidebar.radio("Select", ['About', "Search List", "Map View"])

if page == "About":
    st.title('About Page')
    st.image('download (1).jfif', caption='USA Farmers Markets 2026')
    st.text("""
    This project analyzes Farmers Markets across the USA for the year 2026. 
    Users can explore the data using the following filters:

    - State: Standardized location data for all 50 states.
    - Products: Filter by specific items like Organic goods, Honey, and Seafood.
    - Payment: Easily identify markets that accept SNAP benefits.
    - Variety: Use the variety score to find the most diverse markets.

    And more!!!
    """)

    st.divider()
    st.subheader("Total Product Bar Chart")
    counts = df[list(PRODUCTS_DICT.values())].sum().tolist()
    
    chart_data = pd.DataFrame({
        "Product": list(PRODUCTS_DICT.keys()),
        "Count": counts
    })
    st.bar_chart(
        data=chart_data, 
        x="Product", 
        y="Count", 
        color="#2e7d32"
    )



if page in ["Search List", "Map View"]:
    st.sidebar.title("Search Options")
    
    state_list = sorted(df['Parsed_State'].unique().tolist())
    state_choice = st.sidebar.selectbox("Select State", ["All"] + state_list)
    
    selected_products = st.sidebar.multiselect("Products Available", list(PRODUCTS_DICT.keys()))
    
    selected_payments = st.sidebar.multiselect("Accepted Payments", list(PAYMENT_TYPES.keys()))
    
    snap_choice = st.sidebar.radio("Accepts SNAP?", ["All", "Yes", "No"])
else:
    state_choice = "All"
    selected_products = []
    selected_payments = []
    snap_choice = "All"





data = filter_by_snap(
    filter_by_payment(
        filter_by_products(
            filter_by_state(df.copy(), state_choice), 
            selected_products
        ), 
        selected_payments
    ), 
    snap_choice
)





if page == "Search List":
    st.title("Table List")
    st.write(f"**{len(data)}** markets found.")
    
    # Display table with relevant columns
    st.dataframe(data[['listing_name', 'location_address', 'Parsed_State']])
    
    # Summary Table
    snap_count = data['FNAP'].str.contains('SNAP', na=False).sum()
    summary_df = pd.DataFrame({
        "Category": ["Total Markets", "Accepts SNAP"],
        "Count": [len(data), snap_count]
    })
    st.write("### Market Summary")
    st.table(summary_df)

elif page == "Map View":
    st.title("Farmers Market Map")
    st.text(f"Showing **{len(data)}** market locations.")
    if not data.empty:
        center_lat = data['lat'].mean()
        center_lon = data['lon'].mean()
        m = folium.Map(location=[center_lat, center_lon], zoom_start=4)

        for index, row in data.iterrows():
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=row['listing_name'], 
                tooltip=row['listing_name'] 
            ).add_to(m)
        st_data = st_folium(m, width=725)