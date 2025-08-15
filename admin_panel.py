import streamlit as st
import hashlib
import mysql.connector
import pandas as pd

# ================== MySQL Connection ==================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Change if needed
        password="Sandip",  # Your MySQL password
        database="whatsapp_analyzer"
    )

# ================== Password Hashing ==================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ================== Register Admin ==================
def register_admin(full_name, mobile, username, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM admins WHERE username=%s", (username,))
    if cursor.fetchone():
        conn.close()
        return False

    cursor.execute(
        "INSERT INTO admins (full_name, mobile, username, password_hash) VALUES (%s, %s, %s, %s)",
        (full_name, mobile, username, hash_password(password))
    )
    conn.commit()
    conn.close()
    return True

# ================== Record Login ==================
def record_login(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM admins WHERE username=%s", (username,))
    admin = cursor.fetchone()
    if admin:
        cursor.execute("INSERT INTO admin_logins (admin_id) VALUES (%s)", (admin[0],))
        conn.commit()

    conn.close()

# ================== Login Admin ==================
def login_admin(username, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM admins WHERE username=%s", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and user["password_hash"] == hash_password(password):
        record_login(username)
        st.session_state.current_admin = username
        return True
    return False

# ================== Admin Features ==================
def view_all_admins():
    conn = get_db_connection()
    df = pd.read_sql("SELECT id, full_name, mobile, username FROM admins", conn)
    conn.close()
    st.subheader("👥 Registered Admins")
    st.dataframe(df)

def view_login_history():
    conn = get_db_connection()
    df = pd.read_sql("""
        SELECT a.username, l.login_time
        FROM admin_logins l
        JOIN admins a ON l.admin_id = a.id
        ORDER BY l.login_time DESC
    """, conn)
    conn.close()
    st.subheader("📜 Admin Login History")
    st.dataframe(df)

def change_password():
    st.subheader("🔑 Change Password")
    old_pass = st.text_input("Old Password", type="password")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Update Password"):
        if login_admin(st.session_state.current_admin, old_pass):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE admins SET password_hash=%s WHERE username=%s",
                           (hash_password(new_pass), st.session_state.current_admin))
            conn.commit()
            conn.close()
            st.success("✅ Password updated successfully!")
        else:
            st.error("❌ Old password is incorrect")

def delete_admin():
    st.subheader("🗑 Delete Admin")
    conn = get_db_connection()
    df = pd.read_sql("SELECT username FROM admins", conn)
    conn.close()
    user_to_delete = st.selectbox("Select Admin to Delete", df["username"])

    if st.button("Delete"):
        if user_to_delete != st.session_state.current_admin:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM admins WHERE username=%s", (user_to_delete,))
            conn.commit()
            conn.close()
            st.success(f"✅ Admin '{user_to_delete}' deleted successfully!")
        else:
            st.error("⚠ You cannot delete yourself.")

# ================== Registration Form ==================
def show_registration_form():
    st.subheader("📝 Register New Admin")
    full_name = st.text_input("Full Name")
    mobile = st.text_input("Mobile Number")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Register"):
        if not full_name or not mobile or not new_user or not new_pass:
            st.error("⚠ All fields are required.")
        elif register_admin(full_name, mobile, new_user, new_pass):
            st.success("✅ Admin registered successfully! Please log in.")
            st.session_state.show_login = True
            st.rerun()
        else:
            st.error("❌ Username already exists!")

# ================== Login Form ==================
def show_login_form():
    st.subheader("🔑 Admin Login")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_admin(user, pw):
            st.session_state.admin_logged_in = True
            st.success("✅ Logged in successfully!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")

# ================== Admin Panel ==================
def admin_panel():
    st.subheader("🔐 Admin Panel")

    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
    if "show_login" not in st.session_state:
        st.session_state.show_login = False

    if st.session_state.show_login:
        st.session_state.show_login = False
        show_login_form()
        return

    if not st.session_state.admin_logged_in:
        choice = st.radio("Choose Option", ["Login", "Register"])
        if choice == "Register":
            show_registration_form()
        elif choice == "Login":
            show_login_form()
    else:
        st.success(f"✅ Welcome, {st.session_state.current_admin}!")
        view_all_admins()
        view_login_history()
        change_password()
        delete_admin()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Go to Chat Analyzer"):
                st.session_state.page = "Chat Analyzer"
                st.rerun()
        with col2:
            if st.button("🚪 Logout"):
                st.session_state.admin_logged_in = False
                st.rerun()
