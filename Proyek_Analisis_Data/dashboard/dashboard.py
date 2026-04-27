import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime
import os

# Set page title
st.set_page_config(page_title="E-Commerce Data Analysis Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__)
    df = pd.read_csv(os.path.join(base_path, "main_data.csv"))
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

main_df = load_data()

# SIDEBAR
with st.sidebar:
    st.title("Filter Data")
    min_date = main_df["order_purchase_timestamp"].min()
    max_date = main_df["order_purchase_timestamp"].max()
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[datetime.date(2017, 1, 1), max_date.date()]
    )

# Filter dataframe
filtered_df = main_df[(main_df["order_purchase_timestamp"] >= pd.to_datetime(start_date)) & 
                      (main_df["order_purchase_timestamp"] <= pd.to_datetime(end_date))]

# MAIN PAGE
st.title("E-Commerce Public Analysis Dashboard")

# 1. Kategori Produk
st.subheader("1. Kategori Produk dengan Revenue Tertinggi")
category_revenue_df = filtered_df.groupby("product_category_name_english").agg({
    "price": "sum"
}).sort_values(by="price", ascending=False).reset_index()

fig1, ax1 = plt.subplots(figsize=(10, 6))
sns.barplot(
    x="price", 
    y="product_category_name_english", 
    data=category_revenue_df.head(5), 
    palette="viridis",
    ax=ax1
)
st.pyplot(fig1)

# 2. Shipping vs Rating
st.subheader("2. Pengaruh Biaya Ongkir terhadap Skor Ulasan")

filtered_df['freight_group'] = pd.cut(filtered_df['freight_value'], bins=[0, 20, 50, 100, 500], labels=['Murah', 'Sedang', 'Mahal', 'Sangat Mahal'])
freight_impact_df = filtered_df.groupby('freight_group', observed=True).agg({
    'review_score': 'mean'
}).reset_index()

fig2, ax2 = plt.subplots(figsize=(8, 6))
sns.barplot(
    x="freight_group", 
    y="review_score", 
    data=freight_impact_df, 
    palette=["#3B1E54", "#9B4486", "#D36B7D", "#E8A081"],
    ax=ax2
)
ax2.set_ylim(0, 5)
st.pyplot(fig2)

# RFM Analysis
st.subheader("Pelanggan Terbaik (RFM)")
now = filtered_df['order_purchase_timestamp'].max()
rfm_df = filtered_df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp": lambda x: (now - x.max()).days,
    "order_id": "nunique",
    "price": "sum"
})
rfm_df.columns = ["customer_id", "recency", "frequency", "monetary"]
st.dataframe(rfm_df.sort_values(by="monetary", ascending=False).head(5))
