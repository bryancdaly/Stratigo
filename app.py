import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- Simple password protection ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # cleanup
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.error("❌ Incorrect password")
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()














# App config
st.set_page_config(page_title="Stratigo Project Tracker", layout="wide")
st.title("📊 Stratigo Project Portfolio Tracker")

# Use Streamlit secrets to load credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
gc = gspread.authorize(credentials)

# Connect to worksheet
sheet = gc.open_by_key(st.secrets["GOOGLE_SHEET_KEY"]).worksheet("Projects")

# Sidebar navigation
menu = st.sidebar.radio("Menu", ["➕ Add New Project", "📋 Portfolio Dashboard"])

# Table headers (must match the Google Sheet)
headers = [
    "Project Name", "Sponsor", "Start Date", "Finish Date", "Timeframe",
    "Budget", "Spend to Date", "Estimate to Complete",
    "Key Deliverables", "Scope", "Benefits"
]

# --- Add Project Form ---
if menu == "➕ Add New Project":
    st.subheader("Add a New Project")

    with st.form("new_project_form"):
        col1, col2 = st.columns(2)

        with col1:
            project_name = st.text_input("Project Name")
            sponsor = st.text_input("Sponsor")
            start_date = st.date_input("Start Date", value=date.today())
            finish_date = st.date_input("Finish Date")
            timeframe = st.text_input("Timeframe / Phases")

        with col2:
            budget = st.number_input("Total Budget ($)", min_value=0.0, step=1000.0)
            spend_to_date = st.number_input("Spend to Date ($)", min_value=0.0, step=1000.0)
            estimate_to_complete = st.number_input("Estimate to Complete ($)", min_value=0.0, step=1000.0)

        key_deliverables = st.text_area("Key Deliverables")
        scope = st.text_area("Scope")
        benefits = st.text_area("Expected Benefits")

        submitted = st.form_submit_button("Save Project")

    if submitted:
        row = [
            project_name, sponsor, str(start_date), str(finish_date), timeframe,
            budget, spend_to_date, estimate_to_complete,
            key_deliverables, scope, benefits
        ]
        sheet.append_row(row)
        st.success("✅ Project saved successfully!")

# --- Dashboard View ---
elif menu == "📋 Portfolio Dashboard":
    st.subheader("📋 All Projects")

    try:
        data = sheet.get_all_records()
        if not data:
            st.info("No projects found yet.")
        else:
            df = pd.DataFrame(data)
            st.dataframe(df)

            # Budget comparison
            st.subheader("💰 Budget vs Spend")
            bar_data = df[["Project Name", "Budget", "Spend to Date"]].set_index("Project Name")
            st.bar_chart(bar_data)

            # Timeline table
            st.subheader("📅 Timeline")
            df["Start Date"] = pd.to_datetime(df["Start Date"])
            df["Finish Date"] = pd.to_datetime(df["Finish Date"])
            timeline = df[["Project Name", "Start Date", "Finish Date"]].sort_values("Start Date")
            st.dataframe(timeline)

    except Exception as e:
        st.error(f"⚠️ Error loading data: {e}")
