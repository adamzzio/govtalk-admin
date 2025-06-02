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
st.header("Edit Profile Government")
st.write(f"You are logged in as {st.session_state.role}.")

# ---- Daftar kementerian untuk pilihan institution jika position Menteri ----
ministries = [
    "Kementerian Dalam Negeri",
    "Kementerian Luar Negeri",
    "Kementerian Pertahanan",
    "Kementerian Agama",
    "Kementerian Hukum dan Hak Asasi Manusia",
    "Kementerian Keuangan",
    "Kementerian Energi dan Sumber Daya Mineral",
    "Kementerian Perindustrian",
    "Kementerian Perdagangan",
    "Kementerian Pertanian",
    "Kementerian Lingkungan Hidup dan Kehutanan",
    "Kementerian Perhubungan",
    "Kementerian Kelautan dan Perikanan",
    "Kementerian Ketenagakerjaan",
    "Kementerian Desa, Pembangunan Daerah Tertinggal dan Transmigrasi",
    "Kementerian Pekerjaan Umum dan Perumahan Rakyat",
    "Kementerian Kesehatan",
    "Kementerian Sosial",
    "Kementerian Pendidikan dan Kebudayaan",
    "Kementerian Riset, Teknologi, dan Pendidikan Tinggi",
    "Kementerian Pariwisata dan Ekonomi Kreatif",
    "Kementerian Komunikasi dan Informatika",
    "Kementerian Koperasi dan Usaha Kecil dan Menengah",
    "Kementerian Pemberdayaan Perempuan dan Perlindungan Anak",
    "Kementerian Pendayagunaan Aparatur Negara dan Reformasi Birokrasi",
    "Kementerian Perencanaan Pembangunan Nasional",
    "Kementerian Agraria dan Tata Ruang",
    "Kementerian Badan Usaha Milik Negara",
    "Kementerian Pemuda dan Olahraga",
    "Kementerian Koordinator Bidang Politik dan Keamanan",
    "Kementerian Koordinator Bidang Hukum, Hak Asasi Manusia, Imigrasi, dan Pemasyarakatan",
    "Kementerian Koordinator Bidang Perekonomian",
    "Kementerian Koordinator Bidang Infrastruktur dan Pembangunan Wilayah",
    "Kementerian Koordinator Bidang Pembangunan Manusia dan Kebudayaan",
    "Kementerian Koordinator Bidang Pemberdayaan Masyarakat",
    "Kementerian Koordinator Bidang Pangan"
]

# ---- Inisialisasi koneksi DB ----
init_postgres_connection()
conn = st.session_state.conn

# ---- Ambil data government berdasar username jika ada ----
def get_government_by_username(username):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM government WHERE username = %s", (username,))
        return cur.fetchone()

# ---- Fungsi insert/update ----
def save_government(data):
    with conn.cursor() as cur:
        # Cek apakah data untuk username sudah ada
        cur.execute("SELECT id FROM government WHERE username = %s", (data['username'],))
        existing = cur.fetchone()

        if existing:
            # Update
            cur.execute("""
                UPDATE government SET
                    full_name = %s,
                    position = %s,
                    institution = %s,
                    description = %s,
                    start_period = %s,
                    end_period = %s
                WHERE username = %s
            """, (
                data['full_name'],
                data['position'],
                data['institution'],
                data['description'],
                data['start_period'],
                data['end_period'],
                data['username']
            ))
            conn.commit()
            return "Data updated successfully."
        else:
            # Insert
            cur.execute("""
                INSERT INTO government (
                    full_name, position, institution, description,
                    start_period, end_period, username
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data['full_name'],
                data['position'],
                data['institution'],
                data['description'],
                data['start_period'],
                data['end_period'],
                data['username']
            ))
            conn.commit()
            return "Data inserted successfully."


# ---- Form Input ----
gov_data = get_government_by_username(st.session_state.username)

with st.form("edit_profile_form"):
    full_name = st.text_input("Full Name", value=gov_data['full_name'] if gov_data else "")
    position = st.selectbox("Position", options=["Presiden", "Wakil Presiden", "Menteri"],
                            index=["Presiden", "Wakil Presiden", "Menteri"].index(
                                gov_data['position']) if gov_data else 0)

    # Institution options tergantung position
    if position == "Presiden":
        institution = st.selectbox("Institution", options=["Presiden"], index=0)
    elif position == "Wakil Presiden":
        institution = st.selectbox("Institution", options=["Wakil Presiden"], index=0)
    else:
        # Menteri
        institution_options = ministries
        # Jika ada data dan institution cocok, pilih indexnya, kalau tidak default ke 0
        idx = institution_options.index(gov_data['institution']) if gov_data and gov_data[
            'institution'] in institution_options else 0
        institution = st.selectbox("Institution", options=institution_options, index=idx)

    description = st.text_area("Description", value=gov_data['description'] if gov_data else "")

    # Untuk tanggal, convert dari string di DB ke datetime, jika ada
    from datetime import datetime


    def str_to_date(date_str):
        if date_str:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except:
                return None
        return None


    start_period_val = str_to_date(gov_data['start_period']) if gov_data else None
    end_period_val = str_to_date(gov_data['end_period']) if gov_data else None

    start_period = st.date_input("Start Period (DD-MM-YYYY)", value=start_period_val)
    end_period = st.date_input("End Period (DD-MM-YYYY)", value=end_period_val)

    submitted = st.form_submit_button("Submit")

if submitted:
    # Validasi sederhana: start_period <= end_period
    if start_period > end_period:
        st.error("Start Period must be before or equal to End Period.")
    else:
        data_to_save = {
            "full_name": full_name,
            "position": position,
            "institution": institution,
            "description": description,
            "start_period": start_period.strftime("%Y-%m-%d"),
            "end_period": end_period.strftime("%Y-%m-%d"),
            "username": st.session_state.username
        }
        msg = save_government(data_to_save)
        st.success(msg)
