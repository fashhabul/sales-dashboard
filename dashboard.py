import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Konfigurasi Halaman (UX Enterprise)
st.set_page_config(page_title="Operational Audit Dashboard", layout="wide")

# 2. Fungsi Load & Cleaning Data
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv', sep=';')
    numeric_cols = ['TOTAL.1', 'GOLD.1', 'SILVER.1']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', '').str.replace('-', '0'), errors='coerce')
        df[col] = df[col].fillna(0)
    
    # Logika Risiko Audit
    # High Risk = 20% terbawah, Medium = 20-50%, Low = Di atas itu
    threshold_low = df['TOTAL.1'].quantile(0.2)
    threshold_mid = df['TOTAL.1'].quantile(0.5)
    
    def assign_risk(val):
        if val < threshold_low: return 'High'
        elif val < threshold_mid: return 'Medium'
        else: return 'Low'
    
    df['Risk Level'] = df['TOTAL.1'].apply(assign_risk)
    return df

df = load_data()

# 3. Fungsi Formatting Warna untuk Tabel
def color_risk_df(val):
    if val == 'High': return 'background-color: #e74c3c; color: white' # Merah
    elif val == 'Medium': return 'background-color: #f1c40f; color: black' # Kuning
    else: return 'background-color: #2ecc71; color: white' # Hijau

# 4. Sidebar (Slicer)
st.sidebar.header("Filter & Slicer")
branch_filter = st.sidebar.multiselect("Pilih Cabang:", options=df['BRANCH'].unique(), default=df['BRANCH'].unique())
df_f = df[df['BRANCH'].isin(branch_filter)]

# 5. Main Dashboard UI
st.title("📊 Operational Audit Dashboard")

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Outstanding", f"Rp {df_f['TOTAL.1'].sum():,.0f}")
col2.metric("High Risk Stores", len(df_f[df_f['Risk Level'] == 'High']))
col3.metric("Avg Performance", f"Rp {df_f['TOTAL.1'].mean():,.0f}")
col4.metric("Status", "Monitoring")

st.markdown("---")

# 6. Tabs Layout
tab1, tab2, tab3 = st.tabs(["📊 Analisis Performa", "🔍 Audit Control & Anomaly", "📋 Raw Data"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Tren Penjualan per Cabang")
        if not df_f.empty:
            chart_data = df_f.groupby('BRANCH')['TOTAL.1'].sum().reset_index()
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(chart_data['BRANCH'], chart_data['TOTAL.1'], color='#2e86c1')
            plt.xticks(rotation=45, ha='right')
            st.pyplot(fig)
    with col_b:
        st.subheader("Distribusi Risiko Toko")
        risk_count = df_f['Risk Level'].value_counts()
        fig, ax = plt.subplots()
        risk_count.plot(kind='pie', autopct='%1.1f%%', colors=['#2ecc71', '#f1c40f', '#e74c3c'], ax=ax)
        st.pyplot(fig)

with tab2:
    st.subheader("Tabel Risiko Operasional")
    st.write("Tabel ini menunjukkan toko dengan urgensi audit tinggi berdasarkan volume penjualan.")
    
    # Menampilkan tabel dengan warna
    styled_df = df_f[['BRANCH', 'SITE NAME', 'TOTAL.1', 'Risk Level']].style.map(
        color_risk_df, subset=['Risk Level']
    )
    st.dataframe(styled_df, use_container_width=True)

with tab3:
    st.subheader("Raw Data Detail")
    st.dataframe(df_f, use_container_width=True)
    csv = df_f.to_csv(index=False).encode('utf-8')
    st.download_button("Download Laporan CSV", data=csv, file_name="audit_report.csv", mime="text/csv")
