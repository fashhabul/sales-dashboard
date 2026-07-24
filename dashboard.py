import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Konfigurasi Halaman & UX
st.set_page_config(page_title="Audit & Operational Dashboard", layout="wide")

# 2. Fungsi Load Data (Data Processing)
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv', sep=';')
    # Membersihkan angka
    df['TOTAL.1'] = pd.to_numeric(df['TOTAL.1'].astype(str).str.replace('.', ''), errors='coerce')
    
    # Menambah logika 'Context' (Poin 5)
    # Kita buat benchmark sederhana: rata-rata nasional sebagai target
    avg_perf = df['TOTAL.1'].mean()
    df['Status'] = df['TOTAL.1'].apply(lambda x: '✅ Normal' if x >= avg_perf else '⚠️ Perlu Perhatian')
    return df

df = load_data()

# 3. Sidebar (Slicer & Filter - Poin 4)
st.sidebar.header("Filter & Slicer")
branch_filter = st.sidebar.multiselect("Pilih Cabang:", options=df['BRANCH'].unique(), default=df['BRANCH'].unique())
df_f = df[df['BRANCH'].isin(branch_filter)]

# 4. Hierarki Informasi (Poin 2 & KPI)
st.title("📊 Operational Audit Dashboard")
st.markdown("Dashboard ini dipantau berdasarkan kepatuhan dan performa penjualan.")

col1, col2, col3 = st.columns(3)
col1.metric("Total Outstanding", f"Rp {df_f['TOTAL.1'].sum():,.0f}")
col2.metric("Total Toko Aktif", f"{df_f['SITE ID'].nunique()}")
col3.metric("Avg Performance", f"Rp {df_f['TOTAL.1'].mean():,.0f}")

st.markdown("---")

# 5. Visualisasi & Konteks (Poin 3 & 5)
tab1, tab2 = st.tabs(["Analisis Performa", "Audit Control (Anomaly Detection)"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Tren Penjualan per Cabang")
        st.bar_chart(df_f.groupby('BRANCH')['TOTAL.1'].sum())
    
    with col_b:
        st.subheader("Distribusi Status (Benchmark)")
        status_count = df_f['Status'].value_counts()
        fig, ax = plt.subplots()
        status_count.plot(kind='pie', autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'], ax=ax)
        st.pyplot(fig)

with tab2:
    st.subheader("Daftar Temuan (Anomaly Check)")
    # Menampilkan data dengan format conditional formatting (Poin 6)
    def highlight_status(val):
        color = 'red' if '⚠️' in val else 'green'
        return f'color: {color}'
    
    st.dataframe(
        df_f[['BRANCH', 'SITE NAME', 'TOTAL.1', 'Status']].sort_values(by='TOTAL.1'),
        use_container_width=True
    )

st.sidebar.markdown("---")
st.sidebar.write("Audit Date: 2026-07-24")
