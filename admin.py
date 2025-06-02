# ---- Import Library ----
import pandas as pd
import numpy as np
import streamlit as st
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor

# ---- Hashing Password Function ----
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---- Page Config ----
st.set_page_config(page_title="List Policy", layout="wide")

# ---- Get data from ENV ----
uri = st.secrets['uri']

# ---- Create Connection & Save in Session State ----
def init_postgres_connection():
    if "conn" not in st.session_state or st.session_state.conn.closed:
        st.session_state.conn = psycopg2.connect(uri, cursor_factory=RealDictCursor)

# ---- Validation Login in PostgreSQL ----
def validate_login(username, password):
    init_postgres_connection()  # Open Connection
    cursor = st.session_state.conn.cursor()

    # Query to Get Data User from Username
    query = "SELECT username, password, role FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()

    # Username & Password Validation
    if result:
        db_username = result['username']
        db_password = result['password']
        db_role = result['role']
        if db_password == hash_password(password):  # Hashing Password Verification
            return db_role  # Return Role if Success
    return None  # Return None if Failed

# ---- Session State Initialization ----
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None
if "conn" not in st.session_state:
    init_postgres_connection()

# ---- Login Logic ----
def login():
    st.header("Log in")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log in"):
        role = validate_login(username, password)
        if role:
            st.session_state.role = role
            st.session_state.username = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

# ---- Logout Logic ----
def logout():
    st.session_state.role = None
    st.session_state.username = None
    # Tutup koneksi saat logout
    if "conn" in st.session_state and not st.session_state.conn.closed:
        st.session_state.conn.close()
    st.rerun()

# ---- Optional Navigation (if using multipage) ----
role = st.session_state.role
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Change Password", icon=":material/settings:")

# ---- Create Pages Based on Roles ----
# Admin Role
master_gov = st.Page("admin/master_gov.py", title="Master Government", icon=":material/account_balance:", default=(role == "Admin"))
feedback = st.Page('admin/feedback.py', title='Master Feedback', icon=':material/sms:')

# Government Role
gov_profile = st.Page("government/profile.py", title="Your Profile", icon=":material/manage_accounts:", default=(role == "Government"))
gov_edit_profile = st.Page("government/edit_profile.py", title="Edit Profile", icon=":material/manage_accounts:")
gov_add_policy = st.Page("government/add_policy.py", title="Add Policy", icon=":material/policy:")
gov_edit_policy = st.Page("government/edit_policy.py", title="Edit Policy", icon=":material/policy_alert:")
gov_policy = st.Page("government/policy.py", title="List Policy", icon=":material/privacy_tip:")

account_pages = [logout_page, settings]
admin_pages = [master_gov, feedback]
gov_pages = [gov_profile, gov_edit_profile, gov_policy, gov_add_policy, gov_edit_policy]

page_dict = {}
if st.session_state.role == 'Admin':
    page_dict['Admin'] = admin_pages
if st.session_state.role in ['Government']:
    page_dict['Government'] = gov_pages

if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()