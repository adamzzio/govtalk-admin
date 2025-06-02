# ---- Import Library ----
import pandas as pd
import numpy as np
import streamlit as st
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor

# ---- Get data from ENV ----
uri = st.secrets['uri']

# ---- Function to initialize connection ----
def init_postgres_connection():
    # Cek jika koneksi belum ada di session state atau sudah tertutup, buat baru
    if "conn" not in st.session_state or st.session_state.conn.closed != 0:
        st.session_state.conn = psycopg2.connect(uri, cursor_factory=RealDictCursor)

# ---- Function to get data from table government ----
def get_government_data():
    init_postgres_connection()
    conn = st.session_state.conn
    with conn.cursor() as cursor:

        query = """
        SELECT
           username,
           full_name,
           position,
           institution,
           description,
           start_period,
           end_period
        FROM government 
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        # rows sudah list of dict karena pakai RealDictCursor
        df = pd.DataFrame(rows)
    return df

# ---- Get Data ----
df_users = get_government_data()

# ---- Set Title ----
st.header("Manage Government Users")
st.write(f"You are logged in as {st.session_state.role}.")

# ---- Data Empty Validation ----
if df_users.empty:
    st.warning("Data Master kosong")
    st.stop()  # Menghentikan eksekusi lebih lanjut jika data kosong

# ---- Delete Gov Logic ----
df_users['Delete'] = False

df_users_edited = st.data_editor(
    df_users,
    column_config={
        'Delete': st.column_config.CheckboxColumn(
            "Delete",
            help='Klik untuk menghapus user terkait',
            default=False
        )
    },
    hide_index=True,
    use_container_width=True
)

# Kumpulkan user yang dipilih untuk dihapus
selected_users = df_users_edited.loc[df_users_edited['Delete'], 'username'].tolist()

if st.button('Submit'):
    if selected_users:
        st.write("User yang dipilih untuk dihapus:")
        st.write(selected_users)
        init_postgres_connection()
        conn = st.session_state.conn
        try:
            with conn.cursor() as cursor:
                for username in selected_users:
                    delete_query = "DELETE FROM USERS WHERE username = %s"
                    cursor.execute(delete_query, (username,))
            conn.commit()
            st.success("User berhasil dihapus.")
            st.experimental_rerun()  # Refresh tampilan setelah delete
        except Exception as e:
            st.error(f"Gagal menghapus user: {e}")
    else:
        st.info("Tidak ada user yang dipilih untuk dihapus.")
