import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import datetime

# Set page title
st.set_page_config(page_title="E-Commerce Data Analysis Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

main_df = load_data()

# SIDEBAR
with st.sidebar:
    st.title("Filter Data")
    
    # Filter Rentang Waktu
    min_date = main_df["order_purchase_timestamp"].min()
    max_date = main_df["order_purchase_timestamp"].max()
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[datetime.date(2017, 1, 1), max_date]
    )

# Filter dataframe berdasarkan input sidebar
main_df = main_df[(main_df["order_purchase_timestamp"] >= str(start_date)) & 
                 (main_df["order_purchase_timestamp"] <= str(end_date))]

# MAIN PAGE
st.title("E-Commerce Public Analysis Dashboard")

# Tab 1: Revenue Performance
st.subheader("1. Kategori Produk dengan Revenue Tertinggi")
col1, col2 = st.columns([2, 1])

with col1:
    category_revenue_df = main_df.groupby("product_category_name_english").agg({
        "price": "sum"
    }).sort_values(by="price", ascending=False).reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x="price", 
        y="product_category_name_english", 
        data=category_revenue_df.head(5), 
        palette="viridis",
        ax=ax
    )
    ax.set_title("Top 5 Kategori Produk Berdasarkan Total Revenue", fontsize=15)
    ax.set_xlabel("Total Revenue (BRL)")
    ax.set_ylabel("Kategori Produk")
    st.pyplot(fig)

with col2:
    st.write("Daftar Kategori Teratas:")
    st.dataframe(category_revenue_df.head(5))

# Tab 2: Shipping vs Rating
st.subheader("2. Pengaruh Biaya Ongkir terhadap Skor Ulasan")

# Pastikan kolom binning ada
main_df['freight_group'] = pd.cut(main_df['freight_value'], bins=[0, 20, 50, 100, 500], labels=['Murah', 'Sedang', 'Mahal', 'Sangat Mahal'])
freight_impact_df = main_df.groupby('freight_group', observed=True).agg({
    'review_score': 'mean'
}).reset_index()

fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(
    x="freight_group", 
    y="review_score", 
    data=freight_impact_df, 
    palette="magma",
    ax=ax
)
ax.set_ylim(0, 5)
ax.set_title("Rata-rata Skor Ulasan Berdasarkan Kelompok Biaya Pengiriman", fontsize=15)
ax.set_xlabel("Kelompok Biaya Pengiriman")
ax.set_ylabel("Rata-rata Skor Ulasan")
st.pyplot(fig)

# RFM Analysis
now = main_df['order_purchase_timestamp'].max()
rfm_df = main_df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp": lambda x: (now - x.max()).days,
    "order_id": "nunique",
    "price": "sum"
})
rfm_df.columns = ["customer_id", "recency", "frequency", "monetary"]

st.subheader("Pelanggan Terbaik Berdasarkan Parameter RFM")
st.write("Top 5 Pelanggan Berdasarkan RFM:")
st.dataframe(rfm_df.head(5))
