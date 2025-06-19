# Stratigo v1.1.1 – Fixed Form + Reports

import streamlit as st
import pandas as pd
import json
from google.oauth2.service_account import Credentials
import gspread
import plotly.express as px

# ───────────────────────────
# Config
st.set_page_config("Stratigo", layout="wide")
st.title("📘 Stratigo")

# ───────────────────────────
# Auth
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if not st.session_state.authenticated:
    st.subheader("🔐 Login Required")
    password = st.text_input("Enter password:", type="password")
    if password == "Stratigo2025":
        st.session_state.authenticated = True
        st.experimental_rerun()
    else:
        st.stop()

# ───────────────────────────
# Google Sheets
try:
    credentials_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
    gc = gspread.authorize(credentials)
    sheet = gc.open_by_key("1-3nm4rATb0nOm4P3cjgtEVRhJATkJBsjQJRdsx4rnKs").sheet1
except Exception as e:
    st.error(f"Google Sheets error: {e}")
    st.stop()

# ───────────────────────────
# Helpers
def get_all_projects():
    try:
        df = pd.DataFrame(sheet.get_all_records())
        return df
    except:
        return pd.DataFrame()

def save_project(data):
    sheet.append_row(list(data.values()))

# ───────────────────────────
# Navigation
menu = st.radio("Menu", ["🏠 Home", "➕ Add Project", "📋 Projects", "📈 Reports"])

# ───────────────────────────
if menu == "🏠 Home":
    st.header("🏠 Welcome to Stratigo")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Add Project"):
            st.session_state.menu = "➕ Add Project"
    with col2:
        if st.button("📋 View Projects"):
            st.session_state.menu = "📋 Projects"
    with col3:
        if st.button("📈 View Reports"):
            st.session_state.menu = "📈 Reports"

elif menu == "➕ Add Project":
    st.header("Add New Project")
    with st.form("project_form"):
        name = st.text_input("Project Name")
        sponsor = st.text_input("Sponsor")
        start_date = st.date_input("Start Date")
        end_date = st.date_input("Finish Date")
        timeframe = st.text_input("Timeframe / Phases")
        budget = st.number_input("Budget", min_value=0.0)
        spend = st.number_input("Spend to Date", min_value=0.0)
        etc = st.number_input("Estimate to Complete", min_value=0.0)

        deliverables = st.text_area("Deliverables (one per line)", "")
        scope = st.text_area("Scope (one per line)", "")
        benefits = st.text_area("Benefits (one per line)", "")

        submitted = st.form_submit_button("✅ Submit Project")

    if submitted:
        data = {
            "Project Name": name,
            "Sponsor": sponsor,
            "Start Date": str(start_date),
            "Finish Date": str(end_date),
            "Timeframe / Phases": timeframe,
            "Budget": budget,
            "Spend to Date": spend,
            "Estimate to Complete": etc,
            "Deliverables": "; ".join(deliverables.strip().splitlines()),
            "Scope": "; ".join(scope.strip().splitlines()),
            "Benefits": "; ".join(benefits.strip().splitlines())
        }
        save_project(data)
        st.success("✅ Project saved!")

elif menu == "📋 Projects":
    st.header("📋 Projects Overview")
    df = get_all_projects()
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No projects yet.")

elif menu == "📈 Reports":
    st.header("📈 Portfolio Insights")
    df = get_all_projects()

    if df.empty:
        st.warning("No data available.")
    else:
        if all(c in df.columns for c in ["Project Name", "Budget", "Spend to Date", "Estimate to Complete"]):
            st.subheader("🔵 Budget vs Spend")
            fig = px.bar(df, x="Project Name", y=["Budget", "Spend to Date", "Estimate to Complete"], barmode="group")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Missing one or more of: 'Project Name', 'Budget', 'Spend to Date', 'Estimate to Complete'.")

        if "Benefits" in df.columns:
            st.subheader("🔶 Benefits Overview")
            for i, row in df.iterrows():
                st.markdown(f"**{row['Project Name']}**: {row['Benefits']}")
        else:
            st.info("No 'Benefits' column in data.")
