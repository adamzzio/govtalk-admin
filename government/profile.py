# ---- Import Library ----
import pandas as pd
import numpy as np
import streamlit as st
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor

# ---- Get data from ENV ----
uri = st.secrets['uri']

# ---- Create Connection & Save in Session State ----
def init_postgres_connection():
    if "conn" not in st.session_state or st.session_state.conn.closed:
        st.session_state.conn = psycopg2.connect(uri, cursor_factory=RealDictCursor)

# ---- Set Title ----
st.header("Your Profile")
st.write(f"You are logged in as {st.session_state.role}.")

# ---- Inisialisasi koneksi DB ----
init_postgres_connection()
conn = st.session_state.conn

# ---- Ambil data government berdasar username jika ada ----
def get_government_by_username(username):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM government WHERE username = %s", (username,))
        return cur.fetchone()

# ---- Form Input ----
gov_data = get_government_by_username(st.session_state.username)

# ---- Show Profile ----
if gov_data:
    st.write(f"Welcome! {st.session_state.username}")
    st.subheader("Profile Information")
    st.write(f"**Full Name:** {gov_data['full_name']}")
    st.write(f"**Position:** {gov_data['position']}")
    st.write(f"**Institution:** {gov_data['institution']}")
    st.write(f"**Description:** {gov_data['description']}")
    # Jika kolom start_period dan end_period bertipe date/datetime, bisa langsung ditampilkan
    st.write(f"**Start Period:** {gov_data['start_period']}")
    st.write(f"**End Period:** {gov_data['end_period']}")
else:
    st.warning("Profile data not found for this user.")