# Stratigo App - v1.0.0

import streamlit as st

# --- App Config ---
st.set_page_config(page_title="Stratigo", layout="wide")

# --- Constants ---
APP_PASSWORD = "Stratigo2025"
APP_VERSION = "v1.0.0"
PAGES = ["🏠 Home", "📁 Projects", "📊 Reports", "ℹ️ About"]

# --- Auth Handling ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login_page():
    st.title("🔐 Stratigo Login")
    with st.form("login_form"):
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
        if login_btn:
            if password == APP_PASSWORD:
                st.session_state.authenticated = True
                st.success("Login successful. Redirecting...")
                st.experimental_rerun()
            else:
                st.error("Incorrect password")

# --- Navigation ---
def sidebar_navigation():
    st.sidebar.title("📘 Navigation")
    return st.sidebar.radio("Navigate to:", PAGES)

# --- Pages ---
def home_page():
    st.title("🏠 Home")
    st.write("Welcome to **Stratigo**, your project portfolio hub.")

def projects_page():
    st.title("📁 Projects")
    st.write("Here you'll manage and review your projects. [Placeholder]")

def reports_page():
    st.title("📊 Reports")
    st.write("Insightful reports will be shown here. [Placeholder]")

def about_page():
    st.title("ℹ️ About Stratigo")
    st.markdown(f"""
    **Version:** {APP_VERSION}  
    Stratigo is a simple Streamlit app for managing project portfolios.
    """)

# --- Main App Logic ---
def main():
    if not st.session_state.authenticated:
        login_page()
    else:
        page = sidebar_navigation()
        if page == "🏠 Home":
            home_page()
        elif page == "📁 Projects":
            projects_page()
        elif page == "📊 Reports":
            reports_page()
        elif page == "ℹ️ About":
            about_page()

# --- Run App ---
if __name__ == "__main__":
    main()
