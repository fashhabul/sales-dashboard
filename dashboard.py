import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Operational Audit Dashboard", layout="wide")

# 2. Fungsi Load Data
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv', sep=';')
    numeric_cols = ['TOTAL.1', 'GOLD.1', 'SILVER.1']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', '').str.replace('-', '0'), errors='coerce')
        df[col] = df[col].fillna(0)
    
    mean = df['TOTAL.1'].mean()
    std = df['TOTAL.1'].std()
    df['Is_Anomaly'] = df['TOTAL.1'] < (mean - (1.5 * std))
    
    threshold_low = df['TOTAL.1'].quantile(0.2)
    threshold_mid = df['TOTAL.1'].quantile(0.5)
    def assign_risk(val):
        if val < threshold_low: return 'High'
        elif val < threshold_mid: return 'Medium'
        else: return 'Low'
    df['Risk Level'] = df['TOTAL.1'].apply(assign_risk)
    return df

df = load_data()

# 3. Sidebar Filter
st.sidebar.header("Filter & Slicer")
branch_filter = st.sidebar.multiselect("Pilih Cabang:", options=df['BRANCH'].unique(), default=df['BRANCH'].unique())
df_f = df[df['BRANCH'].isin(branch_filter)]

# 4. Main Dashboard UI (Satu Halaman Penuh)
st.title("📊 Operational Audit Dashboard")

# --- BARIS 1: KPI UTAMA ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Outstanding", f"Rp {df_f['TOTAL.1'].sum():,.0f}")
col2.metric("High Risk Stores", len(df_f[df_f['Risk Level'] == 'High']))
col3.metric("Avg Performance", f"Rp {df_f['TOTAL.1'].mean():,.0f}")
col4.metric("Anomaly Count", len(df_f[df_f['Is_Anomaly'] == True]))

st.markdown("---")

# --- BARIS 2: ANALISIS NARATIF & VISUAL ---
row1_col1, row1_col2 = st.columns([1, 1])

with row1_col1:
    st.subheader("📝 Laporan Eksekutif")
    total_revenue = df_f['TOTAL.1'].sum()
    high_risk_stores = df_f[df_f['Risk Level'] == 'High']
    st.write(f"""Laporan ini menyajikan performa operasional dengan total volume **Rp {total_revenue:,.0f}**. 
    Ditemukan **{len(high_risk_stores)}** unit kerja berisiko tinggi (*High Risk*) dan **{len(df_f[df_f['Is_Anomaly'] == True])}** data anomali. 
    Direkomendasikan melakukan audit lapangan terfokus pada unit berisiko tinggi.""")

with row1_col2:
    st.subheader("Distribusi Risiko")
    risk_count = df_f['Risk Level'].value_counts()
    fig, ax = plt.subplots(figsize=(6, 3))
    risk_count.plot(kind='pie', autopct='%1.1f%%', colors=['#2ecc71', '#f1c40f', '#e74c3c'], ax=ax)
    st.pyplot(fig)

# --- BARIS 3: GRAFIK TREN ---
st.subheader("Tren Penjualan (Rp)")
if not df_f.empty:
    chart_data = df_f.groupby('BRANCH')['TOTAL.1'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(chart_data['BRANCH'], chart_data['TOTAL.1'], color='#2e86c1')
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

# --- BARIS 4: TABEL DATA & METODOLOGI ---
col_tabel, col_metod = st.columns([2, 1])

with col_tabel:
    st.subheader("Daftar Risiko Operasional")
    def style_table(val):
        color = '#e74c3c' if val == 'High' else '#f1c40f' if val == 'Medium' else '#2ecc71'
        return f'background-color: {color}; color: white'
    st.dataframe(df_f[['BRANCH', 'SITE NAME', 'TOTAL.1', 'Risk Level', 'Is_Anomaly']].style.map(style_table, subset=['Risk Level']), use_container_width=True)

with col_metod:
    st.subheader("ℹ️ Metodologi")
    st.write("High Risk (<20%): Prioritas audit. Medium (20-50%): Zona perhatian. Low (>50%): Audit rutin.")
    csv = df_f.to_csv(index=False).encode('utf-8')
    st.download_button("Download Laporan CSV", data=csv, file_name="audit_report.csv")
