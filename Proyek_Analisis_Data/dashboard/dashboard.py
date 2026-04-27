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
    file_path = os.path.join(base_path, "main_data.csv")
    
    df = pd.read_csv(file_path)
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
                      (main_df["order_purchase_timestamp"] <= pd.to_datetime(end_date))].copy()

# MAIN PAGE
st.title("E-Commerce Public Analysis Dashboard")

# 1. Kategori Produk (Revenue)
st.subheader("1. Kategori Produk dengan Revenue Tertinggi")
col1, col2 = st.columns([2, 1])

target_col = 'product_category_name_english'

with col1:
    category_revenue_df = filtered_df.groupby(target_col).agg({
        "price": "sum"
    }).sort_values(by="price", ascending=False).reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x="price", 
        y=target_col, 
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

# 2. Shipping vs Rating 
st.subheader("2. Pengaruh Biaya Pengiriman terhadap Skor Ulasan")

filtered_df['freight_group'] = pd.cut(filtered_df['freight_value'], 
                                      bins=[0, 20, 50, 100, 500], 
                                      labels=['Murah', 'Sedang', 'Mahal', 'Sangat Mahal'])

freight_impact_df = filtered_df.groupby('freight_group', observed=True).agg({
    'review_score': 'mean'
}).reset_index()

fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.barplot(
    x="freight_group", 
    y="review_score", 
    data=freight_impact_df, 
    palette=["#3B1E54", "#9B4486", "#D36B7D", "#E8A081"], 
    ax=ax2
)
ax2.set_ylim(0, 5)
ax2.set_title("Rata-rata Skor Ulasan Berdasarkan Kelompok Biaya Pengiriman", fontsize=15)
ax2.set_xlabel("Kelompok Biaya Pengiriman")
ax2.set_ylabel("Rata-rata Skor Ulasan")

for p in ax2.patches:
    ax2.annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width() / 2., p.get_height()), 
                 ha='center', va='center', xytext=(0, 10), textcoords='offset points')

st.pyplot(fig2)

# RFM Analysis
st.divider()
st.subheader("Pelanggan Terbaik Berdasarkan Parameter RFM")
now = filtered_df['order_purchase_timestamp'].max()
rfm_df = filtered_df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp": lambda x: (now - x.max()).days,
    "order_id": "nunique",
    "price": "sum"
})
rfm_df.columns = ["customer_id", "recency", "frequency", "monetary"]

col_r, col_f, col_m = st.columns(3)
with col_r:
    st.metric("Rata Recency (days)", round(rfm_df.recency.mean(), 1))
with col_f:
    st.metric("Rata Frequency", round(rfm_df.frequency.mean(), 2))
with col_m:
    st.metric("Rata Monetary (BRL)", f"R$ {round(rfm_df.monetary.mean(), 2)}")

st.dataframe(rfm_df.sort_values(by="monetary", ascending=False).head(5))
