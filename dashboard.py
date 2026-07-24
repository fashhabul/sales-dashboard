import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Konfigurasi Layout
st.set_page_config(page_title="Advanced Analytics Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('data.csv', sep=';')
    df['TOTAL.1'] = pd.to_numeric(df['TOTAL.1'].astype(str).str.replace('.', ''), errors='coerce')
    return df

df = load_data()

# --- SIDEBAR (Slicer Kompleks) ---
st.sidebar.header("Filter Analisis")
branch_filter = st.sidebar.multiselect("Pilih Cabang:", options=df['BRANCH'].unique(), default=df['BRANCH'].unique())
channel_filter = st.sidebar.multiselect("Pilih Channel:", options=df['CHANNEL TYPE'].unique(), default=df['CHANNEL TYPE'].unique())
grade_filter = st.sidebar.multiselect("Pilih Grade:", options=df['GRADE STORE'].unique(), default=df['GRADE STORE'].unique())

df_f = df[(df['BRANCH'].isin(branch_filter)) & (df['CHANNEL TYPE'].isin(channel_filter)) & (df['GRADE STORE'].isin(grade_filter))]

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "📈 Analisis Produk & Channel", "🔍 Deep Dive Data"])

with tab1:
    st.title("Executive Overview")
    # Metric Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"Rp {df_f['TOTAL.1'].sum():,.0f}")
    c2.metric("Total Toko", f"{df_f['SITE ID'].nunique()}")
    c3.metric("Avg / Toko", f"Rp {df_f['TOTAL.1'].mean():,.0f}")
    c4.metric("Market Share", "100%") # Contoh placeholder
    
    st.subheader("Tren Penjualan per Cabang")
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(data=df_f.groupby('BRANCH')['TOTAL.1'].sum().reset_index(), x='TOTAL.1', y='BRANCH', palette='viridis')
    st.pyplot(fig)

with tab2:
    st.title("Analisis Produk & Channel")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Proporsi Channel")
        fig_pie = plt.figure(figsize=(5, 5))
        df_f['CHANNEL TYPE'].value_counts().plot.pie(autopct='%1.1f%%', startangle=90)
        st.pyplot(fig_pie)
        
    with col2:
        st.subheader("Distribusi Penjualan per Grade")
        fig_box = plt.figure(figsize=(8, 5))
        sns.boxplot(data=df_f, x='GRADE STORE', y='TOTAL.1', palette='magma')
        st.pyplot(fig_box)

with tab3:
    st.title("Deep Dive Data")
    st.write("Tabel ini memungkinkan Anda melakukan sorting dan pencarian mendalam.")
    st.dataframe(df_f, use_container_width=True)
    
    # Download Button
    csv = df_f.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data Filtered", data=csv, file_name="sales_report.csv", mime="text/csv")
