# app.py - Stratigo v2.0.0
import streamlit as st
import gspread
import json
from google.oauth2.service_account import Credentials
import pandas as pd

# --- Auth setup ---
st.set_page_config(page_title="Stratigo", layout="wide")

# Password gate
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("📘 Stratigo")
    st.header("🔐 Login Required")
    password = st.text_input("Enter password:", type="password")
    if password == "Stratigo2025":
        st.success("✅ Logged in")
        st.session_state.logged_in = True
        st.experimental_rerun()
    else:
        st.stop()

# --- Google Sheets auth ---
try:
    credentials_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
    gc = gspread.authorize(credentials)
    sheet_id = st.secrets["GOOGLE_SHEET_ID"]
    sheet = gc.open_by_key(sheet_id).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"Google Sheets error: {e}")
    st.stop()

# --- Navigation ---
page = st.sidebar.radio("📚 Navigate", ["🏠 Home", "➕ Add Project", "📊 Reports"])

# --- Pages ---
if page == "🏠 Home":
    st.title("🏠 Welcome to Stratigo")
    st.write("Use the menu to get started managing your project portfolio.")
    st.dataframe(df)

elif page == "➕ Add Project":
    st.title("➕ Add New Project")
    with st.form("project_form"):
        project = st.text_input("Project Name")
        sponsor = st.text_input("Sponsor")
        start = st.date_input("Start Date")
        finish = st.date_input("Finish Date")
        timeframe = st.text_input("Timeframe")
        budget = st.number_input("Total Budget", min_value=0.0, step=100.0)
        spend = st.number_input("Spend to Date", min_value=0.0, step=100.0)
        etc = st.number_input("Estimate to Complete", min_value=0.0, step=100.0)
        submit = st.form_submit_button("✅ Save Project")

    if submit:
        new_row = [project, sponsor, str(start), str(finish), timeframe, budget, spend, etc]
        sheet.append_row(new_row)
        st.success("Project added successfully!")
        st.experimental_rerun()

elif page == "📊 Reports":
    st.title("📊 Reports")
    report = st.selectbox("Choose report", ["Project Overview", "Budget Summary"])

    if report == "Project Overview":
        st.subheader("📋 All Projects")
        st.dataframe(df)

    elif report == "Budget Summary":
        try:
            summary = df[["Project Name", "Total Budget", "Spend to Date", "Estimate to Complete"]]
            st.dataframe(summary)
        except Exception as e:
            st.warning(f"Could not generate summary: {e}")
