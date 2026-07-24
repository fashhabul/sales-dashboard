import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Konfigurasi Halaman - Menggunakan layout 'wide' agar proporsional
st.set_page_config(page_title="Audit Control Tower", layout="wide")

# Styling CSS untuk memberikan efek WYSIWYG/Card
st.markdown("""
    <style>
    .metric-card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #2e86c1; }
    .stDataFrame { border: 1px solid #ddd; }
    </style>
""", unsafe_allow_html=True)

# 2. Data Processing
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv', sep=';')
    # Membersihkan Data
    for col in ['TOTAL.1', 'GOLD.1', 'SILVER.1']:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', '').str.replace('-', '0'), errors='coerce').fillna(0)
    
    # Logika Risiko (Quantile)
    threshold_low = df['TOTAL.1'].quantile(0.2)
    threshold_mid = df['TOTAL.1'].quantile(0.5)
    
    def assign_risk(val):
        if val < threshold_low: return 'High'
        elif val < threshold_mid: return 'Medium'
        else: return 'Low'
    
    df['Risk Level'] = df['TOTAL.1'].apply(assign_risk)
    
    # Simulasi Akar Masalah (Root Cause) - Ini adalah bagian untuk input/analisa auditor
    # Dalam implementasi nyata, ini bisa dari database atau input manual
    df['Potential Root Cause'] = np.where(df['Risk Level'] == 'High', 
                                          np.random.choice(['Lokasi', 'Stok', 'Operasional'], len(df)), '-')
    return df

df = load_data()

# 3. Sidebar
st.sidebar.title("🛠️ Audit Tools")
branch_filter = st.sidebar.multiselect("Filter Cabang:", options=df['BRANCH'].unique(), default=df['BRANCH'].unique())
df_f = df[df['BRANCH'].isin(branch_filter)]

# 4. Main Layout (Proporsional Grid)
st.title("🛡️ Audit Control Tower")

# --- ROW 1: KPI CARD (WYSIWYG Style) ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Outstanding", f"Rp {df_f['TOTAL.1'].sum():,.0f}")
c2.metric("High Risk Stores", len(df_f[df_f['Risk Level'] == 'High']))
c3.metric("Avg Performance", f"Rp {df_f['TOTAL.1'].mean():,.0f}")
c4.metric("Risk Coverage", f"{len(df_f[df_f['Risk Level']!='Low'])} Units")

st.markdown("---")

# --- ROW 2: ANALISA & VISUAL (50/50 Split) ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📝 Laporan Eksekutif")
    st.write(f"""Unit kerja terpantau sebanyak **{len(df_f)}**. Berdasarkan analisis data, unit dengan **High Risk** memerlukan tindakan segera. Analisis ini menggunakan standar kuartil untuk objektivitas audit.""")
    
    st.subheader("Tren Penjualan per Cabang")
    chart_data = df_f.groupby('BRANCH')['TOTAL.1'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.bar(chart_data['BRANCH'], chart_data['TOTAL.1'], color='#2e86c1')
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

with col_right:
    st.subheader("Audit Workbench (Risk & Root Cause)")
    st.write("Tabel ini adalah alat bantu audit untuk mengidentifikasi penyebab masalah.")
    
    # Fungsi Warna Tabel
    def color_risk(val):
        color = '#e74c3c' if val == 'High' else '#f1c40f' if val == 'Medium' else '#2ecc71'
        return f'background-color: {color}; color: white'

    st.dataframe(
        df_f[['BRANCH', 'SITE NAME', 'Risk Level', 'Potential Root Cause']].style.map(color_risk, subset=['Risk Level']),
        use_container_width=True,
        column_config={"Potential Root Cause": "Root Cause Finding"}
    )

# --- ROW 3: METODOLOGI (Footer) ---
st.markdown("---")
with st.expander("ℹ️ Lihat Metodologi Penilaian Risiko"):
    st.markdown("""
    | Risk Level | Logika | Penjelasan |
    | :--- | :--- | :--- |
    | **High** | < 20% terbawah | Target prioritas audit untuk mencari akar masalah (Lokasi, Stok, Operasional). |
    | **Medium** | 20% - 50% | Zona perhatian; perlu dimonitor agar tidak jatuh ke kategori High Risk. |
    | **Low** | > 50% teratas | Toko Sehat; audit rutin/periodik. |
    """)
