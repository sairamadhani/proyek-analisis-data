import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Konfigurasi Halaman
st.set_page_config(page_title="E-Commerce Analysis Dashboard", layout="wide")

# Fungsi Load Data
@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, "main_data.csv")
    
    df = pd.read_csv(file_path)
    
    if 'order_purchase_timestamp' in df.columns:
        df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    if 'product_category_name_english' not in df.columns:
        if 'product_category_name' in df.columns:
            df.rename(columns={'product_category_name': 'product_category_name_english'}, inplace=True)
            
    return df

main_df = load_data()

# SIDEBAR (Filter Waktu)
with st.sidebar:
    st.title("Filter Rentang Waktu")
    min_date = main_df["order_purchase_timestamp"].min()
    max_date = main_df["order_purchase_timestamp"].max()
    
    try:
        start_date, end_date = st.date_input(
            label='Pilih Rentang Waktu',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
    except ValueError:
        st.error("Pilih rentang tanggal yang valid (Awal dan Akhir).")
        st.stop()

# Filter data berdasarkan input sidebar
filtered_df = main_df[(main_df["order_purchase_timestamp"] >= pd.to_datetime(start_date)) & 
                       (main_df["order_purchase_timestamp"] <= pd.to_datetime(end_date))]

# DASHBOARD UTAMA
st.title("E-Commerce Performance Dashboard")

# Visualisasi 1: Kategori Produk
st.subheader("Top 10 Kategori Produk Berdasarkan Revenue")
category_revenue = filtered_df.groupby("product_category_name_english")["price"].sum().sort_values(ascending=False).reset_index().head(10)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x="price", y="product_category_name_english", data=category_revenue, palette="magma", ax=ax)
ax.set_xlabel("Total Revenue")
ax.set_ylabel("Kategori")
st.pyplot(fig)

# Visualisasi 2: Analisis RFM
st.divider()
st.subheader("Customer Segmentation (RFM Analysis)")

now = filtered_df['order_purchase_timestamp'].max()
rfm_df = filtered_df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp": lambda x: (now - x.max()).days,
    "order_id": "nunique",
    "price": "sum"
})
rfm_df.columns = ["customer_id", "recency", "frequency", "monetary"]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Avg Recency (Days)", round(rfm_df.recency.mean(), 1))
with col2:
    st.metric("Avg Frequency", round(rfm_df.frequency.mean(), 2))
with col3:
    st.metric("Avg Monetary (BRL)", f"R$ {round(rfm_df.monetary.mean(), 2)}")

st.write("Top 5 Customers by RFM:")
st.dataframe(rfm_df.head(5))
