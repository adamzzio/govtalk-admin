# ===== Import Library =====
import pandas as pd
import streamlit as st
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor
import re

# ===== Set Title =====
st.header("Change Password")
st.write(f"Hi {st.session_state.username}! You are logged in as {st.session_state.role}.")

# ===== Password Hashing Function =====
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ===== Password Validation Function =====
def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),_.?\":{}|<>]", password):
        return "Password must contain at least one special symbol."
    return None

# ===== Connect to Database =====
uri = st.secrets['uri']

def init_postgres_connection():
    if "conn" not in st.session_state or st.session_state.conn.closed != 0:
        st.session_state.conn = psycopg2.connect(uri, cursor_factory=RealDictCursor)

init_postgres_connection()

# ---- Input Fields for Password Change ----
current_password = st.text_input("Enter Current Password", type="password")
new_password = st.text_input("Enter New Password", type="password")
confirm_password = st.text_input("Confirm New Password", type="password")

# ---- Password Change Logic ----
if st.button("Change Password"):
    validation_error = validate_password(new_password)
    if validation_error:
        st.error(validation_error)
    elif new_password != confirm_password:
        st.error("New password and confirmation do not match.")
    else:
        conn = st.session_state.conn
        with conn.cursor() as cursor:
            # Fetch current hashed password
            cursor.execute("SELECT password FROM users WHERE username = %s;", (st.session_state.username,))
            result = cursor.fetchone()
            if not result:
                st.error("User not found.")
            else:
                current_password_db = result['password']
                if hash_password(current_password) != current_password_db:
                    st.error("Current password is incorrect.")
                else:
                    # Hash new password
                    hashed_new_password = hash_password(new_password)
                    # Update password and updated_at timestamp
                    cursor.execute("""
                        UPDATE users 
                        SET password = %s, updated_at = NOW() 
                        WHERE username = %s;
                    """, (hashed_new_password, st.session_state.username))
                    conn.commit()
                    st.success("Password updated successfully!")
                    st.toast('Yay, Password Successfully Changed!', icon='🎉')
                    st.rerun()