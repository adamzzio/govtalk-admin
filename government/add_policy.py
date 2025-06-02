import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Initialize your DB connection here (modify according to your config)
def init_postgres_connection(uri):
    if "conn" not in st.session_state or st.session_state.conn.closed:
        st.session_state.conn = psycopg2.connect(uri, cursor_factory=RealDictCursor)
    return st.session_state.conn

# Get government ID based on username
def get_gov_id(conn, username):
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM government WHERE username = %s", (username,))
        result = cursor.fetchone()
        return result['id'] if result else None

# Render Add Policy form with specified columns
def render_add_policy_form(uri):
    st.header("Add New Policy")
    with st.form(key="add_policy_form", clear_on_submit=True):
        title = st.text_input("Policy Title", max_chars=150)
        category = st.selectbox(
            "Category", ["Perpajakan", "Perizinan", "Kesehatan", "Lingkungan", "Pendidikan", "Lainnya"]
        )
        policy_content = st.text_area("Policy Content", height=300, help="Masukkan teks lengkap kebijakan di sini")
        status = st.radio("Status", ["Draft", "Published"])

        submitted = st.form_submit_button("Submit Policy")

        if submitted:
            # Validation
            if not title or not policy_content:
                st.warning("Pastikan Judul dan Konten Kebijakan diisi.")
            else:
                conn = init_postgres_connection(uri)
                gov_id = get_gov_id(conn, st.session_state.username)
                if not gov_id:
                    st.error("Gagal mendapatkan government ID. Pastikan session sudah benar.")
                    return

                now = datetime.now()
                created_at = now
                updated_at = now

                # Insert logic to save metadata and content to DB
                with conn.cursor() as cursor:
                    insert_query = """
                    INSERT INTO policy
                    (gov_id, title, category, content, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        gov_id, title, category, policy_content, status, created_at, updated_at
                    ))
                    conn.commit()

                st.success(f"Policy '{title}' berhasil disimpan dengan status {status}!")

# Usage example

def main():
    uri = st.secrets["uri"]
    render_add_policy_form(uri)

if __name__ == "__main__":
    main()
