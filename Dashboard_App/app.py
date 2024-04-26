import math
import pickle
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_card import card

st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

# --------------USER AUTHENTICATION--------------
# names = ["Peter Parker", "Rebecca Miller"]
# usernames = ["pparker", "rmiller"]

# Load hashed passwords
# file_path = Path(__file__).parent / "hashed_pw.pkl"
# with file_path.open(file_path, "rb") as file:
#     hashed_passwords = pickle.load(file)

# authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "sales_dashboard", "abcdef", cookie_expiry_days = 30)

# name, authentication_status, username = authenticator.login("Login", "main")

# if authentication_status == False:
#     st.error("Username/Password is incorrect!")

# elif authentication_status == None:
#     st.warning("Please enter your username and password!")

# elif authentication_status:
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io = 'supermarkt_sales.xlsx',
        engine = 'openpyxl',
        sheet_name = 'Sales',
        skiprows = 3,
        usecols = 'B:R',
        nrows = 1000,
    )
    # Add 'hour' column to dataframe
    df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
    return df

df = get_data_from_excel()
# -----------------SIDEBAR-----------------
# authenticator.logout("Logout", "sidebar")
# st.sidebar.title = (f"Welcome {name}!")

st.sidebar.header("Please Filter Here:")
city = st.sidebar.multiselect(
    "Select City:",
    options=df["City"].unique(),
    default=df["City"].unique()
)

customer_type = st.sidebar.multiselect(
    "Select Customer Type:",
    options=df["Customer_type"].unique(),
    default=df["Customer_type"].unique()
)

gender = st.sidebar.multiselect(
    "Select Gender:",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
    )

df_selection = df.query(
    "City == @city & Customer_type == @customer_type & Gender == @gender"
)

# st.dataframe(df_selection)

#----------------MAINPAGE----------------
st.title(":bar_chart: Sales Dashboard")
st.markdown("##")

#TOP KPI's
total_sales = int(df_selection["Total"].sum())
average_rating = round(df_selection["Rating"].mean(),1)
star_rating = ":star:" * int(round(average_rating, 0))
average_sale_by_transaction = round(df_selection["Total"].mean(), 2)

left_column, middle_column, right_column = st.columns(3)

with left_column:
    with st.container():
        st.subheader("Total Sales:")
        st.subheader(f"US $ {total_sales:,}")
        
with middle_column:
    st.subheader("Average Rating:")
    st.subheader(f"{average_rating} {star_rating}")
with right_column:
    st.subheader("Average Sales Per Transaction:")
    st.subheader(f"US $ {average_sale_by_transaction}")

st.markdown("---")

# SALES BY PRODUCT LINE [BAR CHART]

sales_by_product_line = (
    df_selection.groupby(by=["Product line"]).sum([["Total"]]).sort_values(by="Total")
)

fig_product_sales = px.bar(
    sales_by_product_line,
    x="Total",
    y=sales_by_product_line.index,
    orientation="h",
    title="<b>Sales By Product Line</b>",
    color_discrete_sequence=["#008388"] * len(sales_by_product_line),
    template="plotly_white",
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0, 0, 0, 0)",
    xaxis = (dict(showgrid=False))
)

# SALES BY HOUR [BAR CHART]
sales_by_hour = df_selection.groupby(by=["hour"]).sum([["Total"]])
fig_hourly_sales = px.bar(
    sales_by_hour,
    x=sales_by_hour.index,
    y="Total",
    title="<b>Sales By Hour</b>",
    color_discrete_sequence = ["#008388"] * len(sales_by_hour),
    template="plotly_white"
)
fig_hourly_sales.update_layout(
    xaxis = dict(tickmode='linear'),
    plot_bgcolor="rgba(0, 0, 0, 0)",
    yaxis = dict(showgrid=False),
)

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
right_column.plotly_chart(fig_product_sales, use_container_width=True)

# ------------HIDE STREAMLIT STYLE----------------
hide_streamlit_style = """
            <style>
                # MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown("---")
left_column, middle_column, right_column = st.columns(3)
        
with middle_column:
    st.write(":star: Created by Ansuman Pati :star:")