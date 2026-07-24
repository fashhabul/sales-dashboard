import streamlit as st
import pandas as pd

# Konfigurasi Layout (Wide agar terlihat seperti aplikasi bisnis)
st.set_page_config(page_title="Executive Audit Dashboard", layout="wide")

# Custom CSS agar tampilannya lebih "Enterprise" (Card Style)
st.markdown("""
    <style>
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        color: #004d40;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #555;
    }
    .css-1r6slp0 { /* Card container */
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv('data.csv', sep=';')
    df['TOTAL.1'] = pd.to_numeric(df['TOTAL.1'].astype(str).str.replace('.', ''), errors='coerce')
    return df

df = load_data()

# 1. Sidebar - Filter (Seperti di contoh gambar Anda)
st.sidebar.header("Filter Navigasi")
branch_filter = st.sidebar.multiselect("Pilih Cabang:", options=df['BRANCH'].unique(), default=df['BRANCH'].unique())
channel_filter = st.sidebar.multiselect("Pilih Channel:", options=df['CHANNEL TYPE'].unique(), default=df['CHANNEL TYPE'].unique())

df_f = df[(df['BRANCH'].isin(branch_filter)) & (df['CHANNEL TYPE'].isin(channel_filter))]

# 2. Judul Dashboard
st.title("📊 Executive Operational Dashboard")
st.markdown("---")

# 3. KPI Cards (Baris Atas - Poin Penting di Gambar)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Revenue", value=f"Rp {df_f['TOTAL.1'].sum():,.0f}")
with col2:
    st.metric(label="Total Sites", value=df_f['SITE ID'].nunique())
with col3:
    st.metric(label="Avg Performance", value=f"Rp {df_f['TOTAL.1'].mean():,.0f}")
with col4:
    # Contoh perbandingan (Benchmark)
    diff = (df_f['TOTAL.1'].sum() / df['TOTAL.1'].sum()) * 100
    st.metric(label="% Contribution", value=f"{diff:.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# 4. Grid Layout (Visualisasi)
row1_col1, row1_col2 = st.columns([2, 1]) # Kolom kiri lebih lebar

with row1_col1:
    st.subheader("Tren Penjualan per Cabang")
    chart_data = df_f.groupby('BRANCH')['TOTAL.1'].sum().reset_index()
    st.bar_chart(chart_data.set_index('BRANCH'))

with row1_col2:
    st.subheader("Proporsi Channel")
    # Menggunakan Pie chart sederhana
    fig = df_f['CHANNEL TYPE'].value_counts().plot.pie(autopct='%1.1f%%', startangle=90).get_figure()
    st.pyplot(fig)

# 5. Detail Data (Seperti Tabel di Contoh)
st.subheader("Detail Performa Toko")
st.dataframe(df_f[['BRANCH', 'SITE NAME', 'GRADE STORE', 'TOTAL.1']].sort_values(by='TOTAL.1', ascending=False), use_container_width=True)
