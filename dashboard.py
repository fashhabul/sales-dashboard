import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# 1. Konfigurasi Halaman (UX Enterprise)
st.set_page_config(page_title="Operational Audit Dashboard", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    div[data-testid="stMetricValue"] { font-size: 24px; color: #004d40; }
    div[data-testid="stMetricLabel"] { font-size: 14px; color: #555; }
    </style>
""", unsafe_allow_html=True)

# 2. Fungsi Load & Cleaning Data
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv', sep=';')
    numeric_cols = ['TOTAL.1', 'GOLD.1', 'SILVER.1']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', '').str.replace('-', '0'), errors='coerce')
        df[col] = df[col].fillna(0)
    
    # Anomali Detection
    mean = df['TOTAL.1'].mean()
    std = df['TOTAL.1'].std()
    df['Is_Anomaly'] = df['TOTAL.1'] < (mean - (1.5 * std))
    
    # Logika Risk Level (Quantile)
    threshold_low = df['TOTAL.1'].quantile(0.2)
    threshold_mid = df['TOTAL.1'].quantile(0.5)
    def assign_risk(val):
        if val < threshold_low: return 'High'
        elif val < threshold_mid: return 'Medium'
        else: return 'Low'
    df['Risk Level'] = df['TOTAL.1'].apply(assign_risk)
    return df

df = load_data()

# 3. Sidebar
st.sidebar.header("Filter & Slicer")
branch_filter = st.sidebar.multiselect("Pilih Cabang:", options=df['BRANCH'].unique(), default=df['BRANCH'].unique())
df_f = df[df['BRANCH'].isin(branch_filter)]

# 4. Main Dashboard UI
st.title("📊 Operational Audit Dashboard")

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Outstanding", f"Rp {df_f['TOTAL.1'].sum():,.0f}")
col2.metric("High Risk Stores", len(df_f[df_f['Risk Level'] == 'High']))
col3.metric("Avg Performance", f"Rp {df_f['TOTAL.1'].mean():,.0f}")
col4.metric("Anomaly Count", len(df_f[df_f['Is_Anomaly'] == True]))

st.markdown("### 📝 Analisa Audit")
anomalies = df_f[df_f['Is_Anomaly'] == True]
if not anomalies.empty:
    st.error(f"⚠️ Terdeteksi **{len(anomalies)} toko anomali**. Investigasi diperlukan pada cabang: {', '.join(anomalies['BRANCH'].unique())}")
else:
    st.success("✅ Tidak ditemukan anomali data.")

st.markdown("---")

# 5. Tabs Layout
tab1, tab2, tab3, tab4 = st.tabs(["📊 Analisis Performa", "🔍 Audit Control & Anomaly", "📋 Raw Data", "ℹ️ Metodologi Audit"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Tren Penjualan (Rp)")
        if not df_f.empty:
            chart_data = df_f.groupby('BRANCH')['TOTAL.1'].sum().reset_index()
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(chart_data['BRANCH'], chart_data['TOTAL.1'], color='#2e86c1')
            plt.xticks(rotation=45, ha='right')
            plt.ylabel("Total Penjualan (Rp)")
            st.pyplot(fig)
    with col_b:
        st.subheader("Distribusi Risiko")
        risk_count = df_f['Risk Level'].value_counts()
        fig, ax = plt.subplots()
        risk_count.plot(kind='pie', autopct='%1.1f%%', colors=['#2ecc71', '#f1c40f', '#e74c3c'], ax=ax)
        st.pyplot(fig)

with tab2:
    st.subheader("Detail Risiko Operasional")
    def style_table(val):
        color = '#e74c3c' if val == 'High' else '#f1c40f' if val == 'Medium' else '#2ecc71'
        return f'background-color: {color}; color: white'
    
    st.dataframe(
        df_f[['BRANCH', 'SITE NAME', 'TOTAL.1', 'Risk Level', 'Is_Anomaly']].style.map(style_table, subset=['Risk Level']),
        use_container_width=True
    )

with tab3:
    st.dataframe(df_f, use_container_width=True)
    csv = df_f.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name="audit_report.csv")

with tab4:
    st.subheader("2. Pembagian Logika Risk Level")
    st.markdown("""
    | Risk Level | Logika | Penjelasan |
    | :--- | :--- | :--- |
    | **High** | < 20% terbawah | Toko-toko ini adalah **"Underperformer Utama"**. Mereka berada di posisi 20% terendah dari seluruh data. Ini adalah target prioritas audit untuk mencari akar masalah. |
    | **Medium** | 20% - 50% | Toko-toko ini berada di **"Zona Perhatian"**. Performanya masih di bawah rata-rata nasional, tetapi belum berada di titik kritis. |
    | **Low** | > 50% teratas | Toko-toko ini adalah **"Toko Sehat"**. Audit pada toko-toko ini biasanya hanya bersifat rutin (bukan investigatif). |
    """)
    
    st.subheader("3. Mengapa Logika Ini 'Audit-Ready'?")
    st.markdown("""
    *   **Efisiensi Sumber Daya:** Anda tidak mungkin mengaudit semua toko secara bersamaan. Logika ini memungkinkan Anda untuk langsung berkata kepada tim: *"Fokuskan kunjungan audit minggu ini ke toko-toko High Risk saja."*
    *   **Objektivitas:** Karena pembagiannya berdasarkan data statistik (quantile), keputusan Anda untuk melabeli sebuah toko sebagai "High Risk" bersifat objektif dan berbasis data, bukan asumsi subjektif.
    *   **Deteksi Cepat:** Jika sebuah toko tiba-tiba turun dari kategori Low ke High, dashboard akan langsung memberikan sinyal warna merah, yang menjadi *red flag* untuk pengecekan mendalam.
    """)
