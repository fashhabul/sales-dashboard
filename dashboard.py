import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Pro Analytics Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('data.csv', sep=';')
    df['TOTAL.1'] = pd.to_numeric(df['TOTAL.1'].astype(str).str.replace('.', ''), errors='coerce')
    df['GOLD.1'] = pd.to_numeric(df['GOLD.1'].astype(str).str.replace('.', ''), errors='coerce')
    df['SILVER.1'] = pd.to_numeric(df['SILVER.1'].astype(str).str.replace('.', ''), errors='coerce')
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("Filter Analisis")
branch_filter = st.sidebar.multiselect("Pilih Cabang:", options=df['BRANCH'].unique(), default=df['BRANCH'].unique())
df_f = df[df['BRANCH'].isin(branch_filter)]

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Executive", "💡 Advanced Analytics", "📋 Raw Data"])

with tab1:
    st.subheader("Ringkasan Performa")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"Rp {df_f['TOTAL.1'].sum():,.0f}")
    col2.metric("Top Branch", df_f.groupby('BRANCH')['TOTAL.1'].sum().idxmax())
    col3.metric("Total Sites", df_f['SITE ID'].nunique())
    
    st.bar_chart(df_f.groupby('BRANCH')['TOTAL.1'].sum())

with tab2:
    st.subheader("Analisis Mendalam & Benchmarking")
    
    # 1. Correlation Analysis
    st.write("### Korelasi Produk (Gold vs Silver)")
    fig, ax = plt.subplots()
    sns.heatmap(df_f[['GOLD.1', 'SILVER.1', 'TOTAL.1']].corr(), annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)
    
    # 2. Benchmarking (Top vs Bottom Performers)
    st.write("### Benchmarking Performa Toko")
    avg_sales = df_f['TOTAL.1'].mean()
    df_f['Performance'] = df_f['TOTAL.1'].apply(lambda x: 'Above Avg' if x > avg_sales else 'Below Avg')
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("Toko di atas rata-rata")
        st.write(df_f[df_f['Performance'] == 'Above Avg'][['SITE NAME', 'TOTAL.1']].head(5))
    with col_b:
        st.write("Toko di bawah rata-rata")
        st.write(df_f[df_f['Performance'] == 'Below Avg'][['SITE NAME', 'TOTAL.1']].head(5))

with tab3:
    st.dataframe(df_f, use_container_width=True)
    csv = df_f.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name="analisa_lengkap.csv")
