import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd

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

# Fetch semua policy untuk gov_id tertentu, termasuk kolom content
def fetch_all_policies(conn, gov_id):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT 
                id,
                title,
                category,
                content,
                status,
                created_at,
                updated_at
            FROM policy
            WHERE gov_id = %s
            ORDER BY created_at DESC
            """,
            (gov_id,)
        )
        return cursor.fetchall()

# Definisi dialog untuk menampilkan detail policy
@st.dialog("Isi Policy")
def show_policy_dialog(title, category, status, created_at, updated_at, content):
    st.subheader(title)
    st.markdown(f"**Kategori:** {category}  \n**Status:** {status}")
    st.markdown(f"**Dibuat pada:** {created_at}  •  **Diperbarui pada:** {updated_at}")
    st.markdown("---")
    # Tampilkan content lengkap di dalam text_area read-only
    st.text_area("Content Lengkap", value=content, height=400)
    # Tombol “Tutup” memicu rerun untuk menutup dialog
    if st.button("Tutup"):
        st.rerun()

# Render halaman list policy dengan header dan tombol yang memanggil dialog
def render_list_policy_page(uri):
    st.header("Daftar Policy Anda")
    conn = init_postgres_connection(uri)

    gov_id = get_gov_id(conn, st.session_state.username)
    if not gov_id:
        st.error("Gagal mendapatkan government ID. Pastikan Anda sudah login dengan benar.")
        return

    records = fetch_all_policies(conn, gov_id)
    if not records:
        st.info("Belum ada kebijakan yang ditambahkan.")
        return

    # Konversi list of dict ke DataFrame untuk formatting tanggal
    df = pd.DataFrame(records)
    df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")

    st.markdown("---")

    # Menampilkan header kolom secara manual
    header_cols = st.columns([4, 2, 2, 2, 2, 1])  # atur proporsi sesuai kebutuhan
    header_cols[0].write("**Kebijakan**")
    header_cols[1].write("**Kategori**")
    header_cols[2].write("**Status**")
    header_cols[3].write("**Dibuat pada**")
    header_cols[4].write("**Diupdate pada**")
    header_cols[5].write("**Detail**")

    st.markdown("---")
    st.write("Klik tombol 📄 Lihat Isi untuk menampilkan detail kebijakan di pop-up:")

    # Iterasi setiap baris supaya bisa menambahkan tombol “Lihat Isi”
    for row in df.itertuples():
        id_policy  = row.id
        title      = row.title
        category   = row.category
        status     = row.status
        created_at = row.created_at
        updated_at = row.updated_at
        content    = row.content

        # Sesuaikan proporsi kolom agar teks tidak terpotong
        cols = st.columns([4, 2, 2, 2, 2, 1])
        cols[0].write(f"**{title}**")
        cols[1].write(category)
        cols[2].write(status)          # Lebar 2 memastikan “Published” muat
        cols[3].write(created_at)
        cols[4].write(updated_at)

        # Tombol di kolom terakhir memanggil dialog show_policy_dialog
        btn_key = f"view_{id_policy}"
        if cols[5].button("📄", key=btn_key):
            show_policy_dialog(
                title,
                category,
                status,
                created_at,
                updated_at,
                content
            )

def main():
    uri = st.secrets["uri"]
    render_list_policy_page(uri)

if __name__ == "__main__":
    main()
