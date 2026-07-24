import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Konfigurasi Halaman
st.set_page_config(page_title="Professional Sales Dashboard", layout="wide")

# Fungsi untuk membersihkan dan memuat data
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv', sep=';')
    # Membersihkan angka dari format "2.342.878" ke integer
    df['TOTAL.1'] = pd.to_numeric(df['TOTAL.1'].astype(str).str.replace('.', ''), errors='coerce')
    return df

df = load_data()

# --- SIDEBAR (SLICER) ---
st.sidebar.header("Filter & Slicer")

# 1. Slicer Cabang
branches = st.sidebar.multiselect("Pilih Cabang:", 
                                  options=df['BRANCH'].unique(), 
                                  default=df['BRANCH'].unique())

# 2. Slicer Channel Type
channels = st.sidebar.multiselect("Pilih Channel:", 
                                  options=df['CHANNEL TYPE'].unique(), 
                                  default=df['CHANNEL TYPE'].unique())

# 3. Slicer Grade Store
grades = st.sidebar.multiselect("Pilih Grade:", 
                                options=df['GRADE STORE'].unique(), 
                                default=df['GRADE STORE'].unique())

# Menerapkan Filter ke Dataframe
df_filtered = df[
    (df['BRANCH'].isin(branches)) & 
    (df['CHANNEL TYPE'].isin(channels)) & 
    (df['GRADE STORE'].isin(grades))
]

# --- DASHBOARD CONTENT ---
st.title("📊 Executive Sales Dashboard")

# 1. KPI Metrics
col1, col2, col3 = st.columns(3)
total_revenue = df_filtered['TOTAL.1'].sum()
total_sites = df_filtered['SITE ID'].nunique()
avg_revenue = df_filtered['TOTAL.1'].mean()

col1.metric("Total Pendapatan", f"Rp {total_revenue:,.0f}")
col2.metric("Total Toko Aktif", f"{total_sites}")
col3.metric("Rata-rata Penjualan/Toko", f"Rp {avg_revenue:,.0f}")

st.markdown("---")

# 2. Visualisasi
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Total Penjualan per Cabang")
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    data_plot = df_filtered.groupby('BRANCH')['TOTAL.1'].sum().sort_values(ascending=False).head(10)
    data_plot.plot(kind='barh', ax=ax1, color='#2e86c1')
    st.pyplot(fig1)

with col_right:
    st.subheader("Distribusi Penjualan per Grade")
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=df_filtered, x='GRADE STORE', y='TOTAL.1', ax=ax2, palette='viridis')
    st.pyplot(fig2)

# 3. Data Detail
st.subheader("Detail Data")
st.dataframe(df_filtered.sort_values(by='TOTAL.1', ascending=False), use_container_width=True)