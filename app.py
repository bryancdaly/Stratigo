# Stratigo v1.0 — Clean base app with login, navigation, and placeholder pages

import streamlit as st

# --- App Title ---
st.set_page_config(page_title="Stratigo", layout="wide")

# --- Password Protection ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Welcome to Stratigo")
    password = st.text_input("Enter password to continue:", type="password")
    if st.button("Login"):
        if password == "Stratigo2025":
            st.session_state.logged_in = True
            st.success("Login successful. Use the sidebar to navigate.")
        else:
            st.error("Incorrect password. Try again.")

# --- Navigation Menu ---
def sidebar_menu():
    with st.sidebar:
        st.title("📊 Stratigo Menu")
        return st.radio("Go to:", ["🏠 Home", "📁 Projects", "📈 Reports"])

# --- Placeholder Pages ---
def show_home():
    st.title("🏠 Welcome to Stratigo")
    st.markdown("Use the sidebar to navigate to different features. This is your project portfolio management hub.")

def show_projects():
    st.title("📁 Projects")
    st.markdown("This is the Projects section. Functionality for adding, editing, and viewing projects will appear here.")

def show_reports():
    st.title("📈 Reports")
    st.markdown("Reports and insights will appear here. You can later add charts and metrics.")

# --- Main App Logic ---
if st.session_state.logged_in:
    page = sidebar_menu()
    if page == "🏠 Home":
        show_home()
    elif page == "📁 Projects":
        show_projects()
    elif page == "📈 Reports":
        show_reports()
else:
    login()
