import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), "main_data.csv")
    df = pd.read_csv(path)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

main_df = load_data()

# SIDEBAR
with st.sidebar:
    st.title("Filter Data")
    start_date, end_date = st.date_input("Rentang Waktu", [main_df["order_purchase_timestamp"].min(), main_df["order_purchase_timestamp"].max()])

filtered_df = main_df[(main_df["order_purchase_timestamp"] >= pd.to_datetime(start_date)) & 
                       (main_df["order_purchase_timestamp"] <= pd.to_datetime(end_date))]

st.title("E-Commerce Analysis Dashboard")

# VISUALISASI PERTANYAAN 1
st.subheader("1. 5 Kategori Produk dengan Penjualan Tertinggi")
top_5_df = filtered_df.groupby("product_category_name_english").order_id.nunique().sort_values(ascending=False).reset_index().head(5)

fig1, ax1 = plt.subplots(figsize=(12, 6))
sns.barplot(x="order_id", y="product_category_name_english", data=top_5_df, palette=["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"], ax=ax1)
ax1.set_title("Top 5 Product Categories", fontsize=15)
ax1.set_xlabel("Jumlah Order")
ax1.set_ylabel(None)
st.pyplot(fig1)

# VISUALISASI PERTANYAAN 2
st.subheader("2. Distribusi Skor Ulasan Pelanggan (Review Score)")
review_score_df = filtered_df['review_score'].value_counts().sort_index().reset_index()
review_score_df.columns = ['score', 'count']

fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.barplot(x="score", y="count", data=review_score_df, palette="viridis", ax=ax2)
ax2.set_title("Rating Distribution", fontsize=15)
ax2.set_xlabel("Rating (1-5)")
ax2.set_ylabel("Jumlah Review")

for p in ax2.patches:
    ax2.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 9), textcoords = 'offset points')
st.pyplot(fig2)

# RFM ANALYSIS
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
with col1: st.metric("Avg Recency", round(rfm_df.recency.mean(), 1))
with col2: st.metric("Avg Frequency", round(rfm_df.frequency.mean(), 2))
with col3: st.metric("Avg Monetary", f"R$ {round(rfm_df.monetary.mean(), 2)}")

st.write("Top 5 Customers by Monetary:")
st.dataframe(rfm_df.sort_values(by="monetary", ascending=False).head(5))
