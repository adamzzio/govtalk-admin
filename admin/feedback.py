import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd

# Inisialisasi koneksi PostgreSQL dan cache
@st.cache_resource(ttl=3600)
def init_db():
    conn = psycopg2.connect(st.secrets['uri'], cursor_factory=RealDictCursor)
    return conn

conn = init_db()

# Fungsi ambil data feedback dari table policy
@st.cache_data(ttl=600)
def load_feedback_data():
    with conn.cursor() as cur:
        cur.execute("SELECT id, gov_name, feedback, star_rating FROM feedback")
        rows = cur.fetchall()
        return pd.DataFrame(rows)

df = load_feedback_data()

# Tambahkan judul
st.title('Dashboard Feedback User')

# Hitung KPI
total_pejabat = df['gov_name'].nunique()
total_feedback = df['id'].count()
avg_rating = round(df['star_rating'].mean(), 2) if not df.empty else 0

# Tampilkan KPI dalam 3 kolom
col1, col2, col3 = st.columns(3)
col1.metric("Total Pejabat", total_pejabat)
col2.metric("Total Feedback", total_feedback)
col3.metric("Avg Rating", avg_rating)

# Garis pemisah
st.markdown("---")

# Tampilkan dataframe feedback
df = df.rename(columns={'id':'ID',
                        'gov_name':'Nama Pejabat',
                        'feedback':'Feedback',
                        'star_rating':'Rating'})

st.dataframe(df)
