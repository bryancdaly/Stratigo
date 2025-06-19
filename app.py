# Version: Stratigo v1.3
import streamlit as st
import pandas as pd
import json
import plotly.express as px
from google.oauth2.service_account import Credentials
import gspread

# --- Google Sheets Setup ---
scope = ["https://www.googleapis.com/auth/spreadsheets"]
credentials_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key(st.secrets["SHEET_ID"])
sheet = spreadsheet.worksheet("Projects")

# --- Session State Setup ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None
if "page" not in st.session_state:
    st.session_state.page = "Home"

# --- Login Function ---
def login():
    st.set_page_config(page_title="Stratigo", layout="wide")
    st.title("🔐 Stratigo Login")
    password = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if password == "Stratigo2025":
            st.session_state.logged_in = True
        else:
            st.error("Incorrect password.")

# --- Navigation ---
def nav():
    st.sidebar.title("Stratigo")
    page = st.sidebar.radio("Navigate", [
        "Home", "Add Project", "Reports", "Projects List"
    ])
    st.session_state.page = page

# --- Home Page ---
def render_home():
    st.title("🏠 Welcome to Stratigo")
    col1, col2 = st.columns(2)
    with col1:
        st.button("➕ Add Project", on_click=lambda: set_page("Add Project"))
        st.button("📊 View Reports", on_click=lambda: set_page("Reports"))
    with col2:
        st.button("📁 Projects List", on_click=lambda: set_page("Projects List"))

# --- Add/Edit Project Form ---
def render_form(edit_index=None):
    st.title("📝 Add/Edit Project")

    with st.form("project_form", clear_on_submit=not edit_index):
        name = st.text_input("Project Name")
        timeframe = st.text_input("Timeframe / Phases")

        if "deliverables" not in st.session_state:
            st.session_state.deliverables = [""]
        if st.form_submit_button("➕ Add Deliverable"):
            st.session_state.deliverables.append("")

        for i, d in enumerate(st.session_state.deliverables):
            st.session_state.deliverables[i] = st.text_input(f"Deliverable {i+1}", value=d, key=f"deliverable_{i}")

        if "scope" not in st.session_state:
            st.session_state.scope = [""]
        if st.form_submit_button("➕ Add Scope Item"):
            st.session_state.scope.append("")

        for i, s in enumerate(st.session_state.scope):
            st.session_state.scope[i] = st.text_input(f"Scope {i+1}", value=s, key=f"scope_{i}")

        if "benefits" not in st.session_state:
            st.session_state.benefits = [""]
        if st.form_submit_button("➕ Add Benefit"):
            st.session_state.benefits.append("")

        for i, b in enumerate(st.session_state.benefits):
            st.session_state.benefits[i] = st.text_input(f"Benefit {i+1}", value=b, key=f"benefit_{i}")

        submitted = st.form_submit_button("✅ Submit")
        if submitted:
            sheet.append_row([
                name, timeframe,
                "; ".join(st.session_state.deliverables),
                "; ".join(st.session_state.scope),
                "; ".join(st.session_state.benefits)
            ])
            st.success("Project saved.")
            st.session_state.page = "Home"

# --- Reports Page ---
def render_reports():
    st.title("📊 Reports")
    data = pd.DataFrame(sheet.get_all_records())
    if data.empty:
        st.info("No data to report on.")
        return

    col = st.selectbox("Select column to analyse", data.columns)
    fig = px.histogram(data, x=col)
    st.plotly_chart(fig)

# --- List Page ---
def render_projects_list():
    st.title("📁 Projects")
    data = pd.DataFrame(sheet.get_all_records())
    if data.empty:
        st.info("No projects yet.")
        return

    for i, row in data.iterrows():
        with st.expander(row["Project Name"]):
            st.write(f"Timeframe: {row['Timeframe / Phases']}")
            st.write(f"Deliverables: {row['Deliverables']}")
            st.write(f"Scope: {row['Scope']}")
            st.write(f"Benefits: {row['Benefits']}")
            if st.button("✏️ Edit", key=f"edit_{i}"):
                st.session_state.edit_index = i
                st.session_state.page = "Add Project"

# --- Page Switcher ---
def set_page(page_name):
    st.session_state.page = page_name

# --- Main App ---
if not st.session_state.logged_in:
    login()
else:
    nav()
    if st.session_state.page == "Home":
        render_home()
    elif st.session_state.page == "Add Project":
        render_form(edit_index=st.session_state.edit_index)
    elif st.session_state.page == "Reports":
        render_reports()
    elif st.session_state.page == "Projects List":
        render_projects_list()
