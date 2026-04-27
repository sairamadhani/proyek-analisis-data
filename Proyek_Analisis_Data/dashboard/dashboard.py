import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Konfigurasi Halaman
st.set_page_config(page_title="E-Commerce Data Analysis Dashboard", layout="wide")

# Fungsi Load Data
@st.cache_data
def load_data():
        current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "main_data.csv")
    
    df = pd.read_csv(file_path)
    
        if 'order_purchase_timestamp' in df.columns:
        df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    if 'product_category_name_english' not in df.columns:
        if 'product_category_name' in df.columns:
            df.rename(columns={'product_category_name': 'product_category_name_english'}, inplace=True)
            
    return df

main_df = load_data()

# 3. SIDEBAR (Filter Waktu)
with st.sidebar:
    st.title("Filter Data")
    min_date = main_df["order_purchase_timestamp"].min()
    max_date = main_df["order_purchase_timestamp"].max()
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter dataframe berdasarkan sidebar
filtered_df = main_df[(main_df["order_purchase_timestamp"] >= pd.to_datetime(start_date)) & 
                       (main_df["order_purchase_timestamp"] <= pd.to_datetime(end_date))]

# 4. MAIN DASHBOARD
st.title("E-Commerce Public Analysis Dashboard")

# Visualisasi 1: Kategori Produk Revenue Tertinggi
st.subheader("1. Kategori Produk dengan Revenue Tertinggi")
category_revenue_df = filtered_df.groupby("product_category_name_english").agg({
    "price": "sum"
}).sort_values(by="price", ascending=False).reset_index().head(10)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x="price", y="product_category_name_english", data=category_revenue_df, palette="viridis", ax=ax)
ax.set_xlabel("Total Revenue")
ax.set_ylabel("Kategori Produk")
st.pyplot(fig)

# Visualisasi 2: Skor Ulasan
st.subheader("2. Distribusi Skor Ulasan")
review_score_dist = filtered_df['review_score'].value_counts().sort_index()
fig2, ax2 = plt.subplots()
sns.barplot(x=review_score_dist.index, y=review_score_dist.values, ax=ax2, color="skyblue")
st.pyplot(fig2)

# 5. RFM ANALYSIS
st.divider()
st.subheader("Customer Segmentation (RFM Analysis)")

# Hitung RFM secara lokal
now = filtered_df['order_purchase_timestamp'].max()
rfm_df = filtered_df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp": lambda x: (now - x.max()).days, # Recency
    "order_id": "nunique", # Frequency
    "price": "sum" # Monetary
})
rfm_df.columns = ["customer_id", "recency", "frequency", "monetary"]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Avg Recency (Days)", round(rfm_df.recency.mean(), 1))
with col2:
    st.metric("Avg Frequency", round(rfm_df.frequency.mean(), 2))
with col3:
    st.metric("Avg Monetary", f"R$ {round(rfm_df.monetary.mean(), 2)}")

st.write("Top 5 Customers by RFM:")
st.dataframe(rfm_df.head(5))
