# Stratigo v1.1.4 – Stable Login & Sheets Auth

import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread
import plotly.express as px

# ───────────────────────────
st.set_page_config("Stratigo", layout="wide")
st.title("📘 Stratigo")

# ───────────────────────────
# Auth
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.subheader("🔐 Login Required")
    pw = st.text_input("Enter password:", type="password")
    if pw == "Stratigo2025":
        st.session_state.authenticated = True
        st.success("✅ Logged in")

if not st.session_state.authenticated:
    st.info("Please enter the correct password to continue.")
    st.stop()

# ───────────────────────────
# Google Sheets
try:
    creds = st.secrets["GOOGLE_SERVICE_ACCOUNT"]  # FIXED: No json.loads
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(creds, scopes=scope)
    gc = gspread.authorize(credentials)
    sheet = gc.open_by_key("1-3nm4rATb0nOm4P3cjgtEVRhJATkJBsjQJRdsx4rnKs").sheet1
except Exception as e:
    st.error(f"Google Sheets error: {e}")
    st.stop()

# ───────────────────────────
# Helpers
def get_all_projects():
    try:
        return pd.DataFrame(sheet.get_all_records())
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
        start = st.date_input("Start Date")
        end = st.date_input("Finish Date")
        phase = st.text_input("Timeframe / Phases")
        budget = st.number_input("Budget", min_value=0.0)
        spend = st.number_input("Spend to Date", min_value=0.0)
        etc = st.number_input("Estimate to Complete", min_value=0.0)
        deliverables = st.text_area("Deliverables (one per line)")
        scope = st.text_area("Scope items (one per line)")
        benefits = st.text_area("Benefits (one per line)")
        submit = st.form_submit_button("✅ Submit Project")

    if submit:
        row = {
            "Project Name": name,
            "Sponsor": sponsor,
            "Start Date": str(start),
            "Finish Date": str(end),
            "Timeframe / Phases": phase,
            "Budget": budget,
            "Spend to Date": spend,
            "Estimate to Complete": etc,
            "Deliverables": "; ".join(deliverables.splitlines()),
            "Scope": "; ".join(scope.splitlines()),
            "Benefits": "; ".join(benefits.splitlines())
        }
        save_project(row)
        st.success("✅ Project saved!")

elif menu == "📋 Projects":
    st.header("📋 Projects Overview")
    df = get_all_projects()
    st.dataframe(df) if not df.empty else st.info("No projects available.")

elif menu == "📈 Reports":
    st.header("📈 Portfolio Insights")
    df = get_all_projects()
    if df.empty:
        st.warning("No data available.")
    else:
        if all(col in df.columns for col in ["Project Name", "Budget", "Spend to Date", "Estimate to Complete"]):
            fig = px.bar(df, x="Project Name", y=["Budget", "Spend to Date", "Estimate to Complete"], barmode="group")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Missing columns for budget report.")

        if "Benefits" in df.columns and "Project Name" in df.columns:
            st.subheader("🔶 Benefits Overview")
            for i, row in df.iterrows():
                st.markdown(f"**{row['Project Name']}**: {row['Benefits']}")
