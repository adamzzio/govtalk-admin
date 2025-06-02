import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Inisialisasi koneksi PostgreSQL
def init_postgres_connection(uri):
    if "conn" not in st.session_state or st.session_state.conn.closed:
        st.session_state.conn = psycopg2.connect(uri, cursor_factory=RealDictCursor)
    return st.session_state.conn

# Ambil gov_id berdasarkan username yang sedang login
def get_gov_id(conn, username):
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM government WHERE username = %s", (username,))
        result = cursor.fetchone()
        return result["id"] if result else None

# Ambil daftar title kebijakan milik gov_id tersebut
def fetch_policy_titles(conn, gov_id):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT title FROM policy WHERE gov_id = %s ORDER BY created_at DESC",
            (gov_id,)
        )
        return [row["title"] for row in cursor.fetchall()]

# Ambil detail satu kebijakan berdasarkan title
def fetch_policy_by_title(conn, title, gov_id):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT title, category, content, status FROM policy WHERE title = %s AND gov_id = %s",
            (title, gov_id)
        )
        return cursor.fetchone()

# Halaman Update Policy saja
def render_update_policy_form(uri):
    st.header("Update Policy")
    conn = init_postgres_connection(uri)
    gov_id = get_gov_id(conn, st.session_state.username)
    if not gov_id:
        st.error("Gagal mendapatkan government ID. Pastikan Anda sudah login dengan benar.")
        return

    # Ambil daftar judul kebijakan milik user
    titles = fetch_policy_titles(conn, gov_id)
    if not titles:
        st.info("Belum ada kebijakan yang dapat diupdate.")
        return

    # Pilih satu judul untuk diedit
    selected_title = st.selectbox("Pilih Judul Policy yang Ingin Diupdate", titles)

    policy = fetch_policy_by_title(conn, selected_title, gov_id)
    if not policy:
        st.error("Kebijakan tidak ditemukan atau Anda tidak berhak mengakses.")
        return

    # Form untuk mengupdate data kebijakan
    with st.form(key="update_policy_form"):
        new_title = st.text_input("Policy Title", value=policy["title"], max_chars=150)
        new_category = st.selectbox(
            "Category",
            ["Perpajakan", "Perizinan", "Kesehatan", "Lingkungan", "Pendidikan", "Lainnya"],
            index=[
                "Perpajakan", "Perizinan", "Kesehatan", "Lingkungan", "Pendidikan", "Lainnya"
            ].index(policy["category"])
        )
        new_content = st.text_area("Policy Content", value=policy["content"], height=300)
        new_status = st.radio(
            "Status",
            ["Draft", "Published"],
            index=0 if policy["status"] == "Draft" else 1
        )

        update_submitted = st.form_submit_button("Update Policy")
        if update_submitted:
            if not new_title or not new_content:
                st.warning("Pastikan Judul dan Konten Kebijakan terisi.")
            else:
                updated_at = datetime.now()
                with conn.cursor() as cursor:
                    update_query = """
                    UPDATE policy
                    SET title = %s,
                        category = %s,
                        content = %s,
                        status = %s,
                        updated_at = %s
                    WHERE title = %s AND gov_id = %s
                    """
                    cursor.execute(
                        update_query,
                        (
                            new_title,
                            new_category,
                            new_content,
                            new_status,
                            updated_at,
                            selected_title,
                            gov_id
                        )
                    )
                    conn.commit()
                st.success(f"Policy '{new_title}' berhasil diupdate pada {updated_at.strftime('%Y-%m-%d %H:%M:%S')}!")

# Panggil fungsi utama
def main():
    uri = st.secrets["uri"]
    render_update_policy_form(uri)

if __name__ == "__main__":
    main()
