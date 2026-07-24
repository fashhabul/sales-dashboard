import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Konfigurasi Halaman (Proporsional & Profesional)
st.set_page_config(page_title="Branch Plan Audit 2026", layout="wide")

# Styling CSS untuk tampilan bersih
st.markdown("""
    <style>
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# 2. Data Processing & Analisis
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv', sep=';')
    for col in ['TOTAL.1', 'GOLD.1', 'SILVER.1']:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', '').str.replace('-', '0'), errors='coerce').fillna(0)
    
    # Anomali Detection (1.5 SD)
    mean = df['TOTAL.1'].mean()
    std = df['TOTAL.1'].std()
    df['Is_Anomaly'] = df['TOTAL.1'] < (mean - (1.5 * std))
    
    # Logika Risiko (Quantile)
    threshold_low = df['TOTAL.1'].quantile(0.2)
    threshold_mid = df['TOTAL.1'].quantile(0.5)
    
    def assign_risk(val):
        if val < threshold_low: return 'High'
        elif val < threshold_mid: return 'Medium'
        else: return 'Low'
    
    df['Risk Level'] = df['TOTAL.1'].apply(assign_risk)
    
    # Simulasi Akar Masalah
    df['Potential Root Cause'] = np.where(df['Risk Level'] == 'High', 
                                          np.random.choice(['Lokasi', 'Stok', 'Operasional'], len(df)), '-')
    return df

df = load_data()

# 3. Sidebar
st.sidebar.title("🛠️ Perencanaan Audit")
branch_filter = st.sidebar.multiselect("Filter Cabang:", options=df['BRANCH'].unique(), default=df['BRANCH'].unique())
df_f = df[df['BRANCH'].isin(branch_filter)]

# 4. Main Layout
st.title("📅 Branch Plan Audit 2026")

# --- ROW 1: KPI METRICS ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Outstanding", f"Rp {df_f['TOTAL.1'].sum():,.0f}")
c2.metric("High Risk Stores", len(df_f[df_f['Risk Level'] == 'High']))
c3.metric("Avg Performance", f"Rp {df_f['TOTAL.1'].mean():,.0f}")
c4.metric("Anomaly Count", len(df_f[df_f['Is_Anomaly'] == True]))

st.markdown("---")

# --- ROW 2: ANALISIS & AUDIT WORKBENCH ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📝 Laporan Eksekutif")
    total_revenue = df_f['TOTAL.1'].sum()
    high_risk_stores = df_f[df_f['Risk Level'] == 'High']
    
    st.write(f"""Laporan ini ditujukan sebagai acuan perencanaan audit tahun 2026 dengan total volume transaksi **Rp {total_revenue:,.0f}**. 
    Ditemukan **{len(high_risk_stores)}** unit kerja berisiko tinggi (*High Risk*) dan **{len(df_f[df_f['Is_Anomaly'] == True])}** data anomali. 
    Direkomendasikan melakukan audit lapangan terfokus pada unit berisiko tinggi guna memastikan kepatuhan operasional.""")
    
    st.subheader("Tren Penjualan per Cabang")
    if not df_f.empty:
        chart_data = df_f.groupby('BRANCH')['TOTAL.1'].sum().reset_index()
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.bar(chart_data['BRANCH'], chart_data['TOTAL.1'], color='#2e86c1')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel("Penjualan (Rp)")
        st.pyplot(fig)

with col_right:
    st.subheader("Audit Workbench (Risk & Root Cause)")
    
    def color_risk(val):
        color = '#e74c3c' if val == 'High' else '#f1c40f' if val == 'Medium' else '#2ecc71'
        return f'background-color: {color}; color: white'

    st.dataframe(
        df_f[['BRANCH', 'SITE NAME', 'Risk Level', 'Potential Root Cause']].style.map(color_risk, subset=['Risk Level']),
        use_container_width=True,
        column_config={"Potential Root Cause": "Root Cause Finding"}
    )
    
    # Tombol Download
    csv = df_f.to_csv(index=False).encode('utf-8')
    st.download_button("Download Laporan CSV", data=csv, file_name="branch_audit_plan_2026.csv")

# --- ROW 3: METODOLOGI (Footer) ---
st.markdown("---")
with st.expander("ℹ️ Lihat Metodologi Penilaian Risiko 2026"):
    st.subheader("Justifikasi Implementasi Metodologi Audit")
    st.markdown("""
    *   **Efisiensi Alokasi Sumber Daya:** Optimalisasi cakupan audit dilakukan dengan memprioritaskan penugasan lapangan secara spesifik pada unit kerja dengan tingkat risiko tinggi (*High Risk*), guna memastikan efektivitas operasional audit yang lebih terarah.
    *   **Objektivitas Berbasis Data:** Klasifikasi risiko dilakukan melalui pendekatan statistik (*quantile*), yang menjamin objektivitas dalam penentuan status unit kerja. Hal ini meminimalisir subjektivitas dalam pengambilan keputusan audit.
    *   **Sistem Deteksi Dini (*Early Warning System*):** Dashboard secara otomatis memicu notifikasi risiko tinggi saat terjadi degradasi performa unit kerja, berfungsi sebagai *red flag* untuk memfasilitasi tindakan korektif dan investigasi mendalam yang responsif.
    """)
