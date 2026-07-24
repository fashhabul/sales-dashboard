import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Operational Audit Dashboard", layout="wide")

# 2. Fungsi Load & Cleaning Data
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv', sep=';')
    numeric_cols = ['TOTAL.1', 'GOLD.1', 'SILVER.1']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', '').str.replace('-', '0'), errors='coerce')
        df[col] = df[col].fillna(0)
    
    # --- LOGIKA ANOMALI (Statistical Outlier Detection) ---
    mean = df['TOTAL.1'].mean()
    std = df['TOTAL.1'].std()
    # Anomali jika penjualan 1.5 standar deviasi di bawah rata-rata
    df['Is_Anomaly'] = df['TOTAL.1'] < (mean - (1.5 * std))
    
    # Logika Risiko
    threshold_low = df['TOTAL.1'].quantile(0.2)
    threshold_mid = df['TOTAL.1'].quantile(0.5)
    def assign_risk(val):
        if val < threshold_low: return 'High'
        elif val < threshold_mid: return 'Medium'
        else: return 'Low'
    df['Risk Level'] = df['TOTAL.1'].apply(assign_risk)
    return df

df = load_data()

# 3. Fungsi Formatting & Styling
def style_table(df_to_style):
    return df_to_style.style.map(
        lambda x: 'background-color: #e74c3c; color: white' if x == 'High' else 
                  'background-color: #f1c40f; color: black' if x == 'Medium' else 
                  'background-color: #2ecc71; color: white', subset=['Risk Level']
    ).format({'TOTAL.1': 'Rp {:,.0f}'}) # Format Rupiah di tabel

# 4. Sidebar
st.sidebar.header("Filter")
branch_filter = st.sidebar.multiselect("Pilih Cabang:", options=df['BRANCH'].unique(), default=df['BRANCH'].unique())
df_f = df[df['BRANCH'].isin(branch_filter)]

# 5. Main UI
st.title("📊 Operational Audit Dashboard")

# KPI dengan Format Rp
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Outstanding", f"Rp {df_f['TOTAL.1'].sum():,.0f}")
col2.metric("High Risk Stores", len(df_f[df_f['Risk Level'] == 'High']))
col3.metric("Avg Performance", f"Rp {df_f['TOTAL.1'].mean():,.0f}")
col4.metric("Anomaly Count", len(df_f[df_f['Is_Anomaly'] == True]))

# Analisa Otomatis
st.markdown("### 📝 Analisa Audit")
anomalies = df_f[df_f['Is_Anomaly'] == True]
if not anomalies.empty:
    st.error(f"⚠️ Terdeteksi **{len(anomalies)} toko dengan data anomali** (penjualan jauh di bawah rata-rata). Segera lakukan investigasi pada cabang: {', '.join(anomalies['BRANCH'].unique())}")
else:
    st.success("✅ Tidak ditemukan anomali data pada filter saat ini.")

st.markdown("---")

# 6. Visualisasi
tab1, tab2 = st.tabs(["📊 Analisis Performa", "🔍 Audit Control (Anomali)"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Tren Penjualan (Rp)")
        if not df_f.empty:
            chart_data = df_f.groupby('BRANCH')['TOTAL.1'].sum().reset_index()
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(chart_data['BRANCH'], chart_data['TOTAL.1'], color='#2e86c1')
            plt.ylabel("Penjualan (Rp)")
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)
    with col_b:
        st.subheader("Distribusi Risiko")
        risk_count = df_f['Risk Level'].value_counts()
        fig, ax = plt.subplots()
        risk_count.plot(kind='pie', autopct='%1.1f%%', colors=['#2ecc71', '#f1c40f', '#e74c3c'], ax=ax)
        st.pyplot(fig)

with tab2:
    st.subheader("Detail Risiko & Anomali")
    st.dataframe(style_table(df_f[['BRANCH', 'SITE NAME', 'TOTAL.1', 'Risk Level', 'Is_Anomaly']]), use_container_width=True)

# 7. Download
csv = df_f.to_csv(index=False).encode('utf-8')
st.download_button("Download Laporan CSV", data=csv, file_name="audit_report.csv", mime="text/csv")
