import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Konfigurasi Halaman (UX)
st.set_page_config(page_title="Operational Audit Dashboard", layout="wide")

# 2. Fungsi Load & Cleaning Data
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv', sep=';')
    # Membersihkan kolom numerik
    numeric_cols = ['TOTAL.1', 'GOLD.1', 'SILVER.1']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', ''), errors='coerce')
    
    # Logika Audit: Benchmark sederhana berdasarkan rata-rata
    avg_perf = df['TOTAL.1'].mean()
    df['Status'] = df['TOTAL.1'].apply(lambda x: '✅ Normal' if x >= avg_perf else '⚠️ Perlu Perhatian')
    return df

df = load_data()

# 3. Sidebar (Slicer/Filter)
st.sidebar.header("Filter & Slicer")
branch_filter = st.sidebar.multiselect("Pilih Cabang:", options=df['BRANCH'].unique(), default=df['BRANCH'].unique())
channel_filter = st.sidebar.multiselect("Pilih Channel:", options=df['CHANNEL TYPE'].unique(), default=df['CHANNEL TYPE'].unique())
grade_filter = st.sidebar.multiselect("Pilih Grade:", options=df['GRADE STORE'].unique(), default=df['GRADE STORE'].unique())

# Terapkan Filter
df_f = df[
    (df['BRANCH'].isin(branch_filter)) & 
    (df['CHANNEL TYPE'].isin(channel_filter)) & 
    (df['GRADE STORE'].isin(grade_filter))
]

# 4. Main Dashboard UI
st.title("📊 Operational Audit Dashboard")
st.markdown("Dashboard ini memantau kepatuhan dan performa operasional toko.")

# KPI Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Outstanding", f"Rp {df_f['TOTAL.1'].sum():,.0f}")
col2.metric("Total Toko Aktif", f"{df_f['SITE ID'].nunique()}")
col3.metric("Avg Performance", f"Rp {df_f['TOTAL.1'].mean():,.0f}")

st.markdown("---")

# 5. Tabs Layout
tab1, tab2, tab3 = st.tabs(["📊 Analisis Performa", "🔍 Audit Control & Anomaly", "📋 Raw Data"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Tren Penjualan per Cabang")
        # Perbaikan bar chart (menggunakan reset_index dan set_index agar stabil)
        chart_data = df_f.groupby('BRANCH')['TOTAL.1'].sum().reset_index()
        st.bar_chart(chart_data.set_index('BRANCH'))
    
    with col_b:
        st.subheader("Distribusi Status (Benchmark)")
        status_count = df_f['Status'].value_counts()
        fig, ax = plt.subplots()
        status_count.plot(kind='pie', autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'], ax=ax)
        st.pyplot(fig)

with tab2:
    st.subheader("Deep Dive & Correlation")
    # Heatmap Analisis
    fig_heat, ax_heat = plt.subplots()
    sns.heatmap(df_f[['GOLD.1', 'SILVER.1', 'TOTAL.1']].corr(), annot=True, cmap='coolwarm', ax=ax_heat)
    st.pyplot(fig_heat)
    
    st.subheader("Daftar Temuan (Anomaly Check)")
    st.dataframe(df_f[['BRANCH', 'SITE NAME', 'TOTAL.1', 'Status']].sort_values(by='TOTAL.1'), use_container_width=True)

with tab3:
    st.subheader("Raw Data Detail")
    st.dataframe(df_f, use_container_width=True)
    csv = df_f.to_csv(index=False).encode('utf-8')
    st.download_button("Download Laporan CSV", data=csv, file_name="audit_report.csv", mime="text/csv")

st.sidebar.markdown("---")
st.sidebar.write("Last Update: 2026-07-24")
