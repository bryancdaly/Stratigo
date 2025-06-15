# app.py – Stratigo v1.0.4

import streamlit as st
import pandas as pd
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -------------------
# CONFIGURATION
# -------------------
st.set_page_config(page_title="Stratigo", layout="wide")
st.markdown("<h1 style='text-align: center;'>📊 Stratigo</h1>", unsafe_allow_html=True)

# -------------------
# AUTH
# -------------------
PASSWORD = "Stratigo2025"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pw = st.text_input("Enter password", type="password")
    if pw == PASSWORD:
        st.session_state.authenticated = True
        st.experimental_rerun()
    else:
        st.stop()

# -------------------
# GOOGLE SHEETS SETUP
# -------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(creds)
SHEET_ID = st.secrets["GOOGLE_SHEET_ID"]
sheet = client.open_by_key(SHEET_ID).sheet1

# -------------------
# DATA FUNCTIONS
# -------------------
def load_projects():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def save_project(row):
    sheet.append_row(row)

# -------------------
# FORM FUNCTIONS
# -------------------
def render_project_form():
    st.subheader("➕ Add New Project")
    with st.form("project_form"):
        name = st.text_input("Project Name")
        sponsor = st.text_input("Sponsor")
        start_date = st.date_input("Start Date")
        end_date = st.date_input("Finish Date")
        timeframe = st.text_input("Timeframe / Phases")
        budget = st.number_input("Total Budget", min_value=0.0, step=100.0)
        spend = st.number_input("Spend to Date", min_value=0.0, step=100.0)
        etc = st.number_input("Estimate to Complete", min_value=0.0, step=100.0)

        st.markdown("### Deliverables")
        deliverables = st.text_area("Enter deliverables separated by commas")

        st.markdown("### Scope")
        scope = st.text_area("Enter scope items separated by commas")

        st.markdown("### Benefits")
        benefits = st.text_area("Enter benefits separated by commas")

        submitted = st.form_submit_button("Save Project")
        if submitted:
            row = [
                name, sponsor, str(start_date), str(end_date), timeframe,
                budget, spend, etc, deliverables, scope, benefits
            ]
            save_project(row)
            st.success("Project saved!")

# -------------------
# DASHBOARD
# -------------------
def render_dashboard():
    st.subheader("📋 Project Portfolio")
    df = load_projects()
    if df.empty:
        st.warning("No project data available.")
        return

    for i, row in df.iterrows():
        with st.expander(f"📌 {row['Project Name']}"):
            st.write(f"**Sponsor:** {row['Sponsor']}")
            st.write(f"**Timeframe:** {row['Timeframe / Phases']}")
            st.write(f"**Budget:** ${row['Total Budget']}, **Spend:** ${row['Spend to Date']}, **ETC:** ${row['Estimate to Complete']}")
            st.write("**Deliverables:**", row["Deliverables"])
            st.write("**Scope:**", row["Scope"])
            st.write("**Benefits:**", row["Benefits"])

# -------------------
# REPORTS
# -------------------
def render_reports():
    st.subheader("📊 Reports")
    df = load_projects()
    report_type = st.selectbox("Choose report:", ["Benefits Overview", "Budget Summary", "Timeline View"])

    if report_type == "Benefits Overview":
        st.markdown("### Projects & Their Benefits")
        if "Benefits" in df.columns:
            for _, row in df.iterrows():
                st.markdown(f"- **{row['Project Name']}**: {row['Benefits']}")
        else:
            st.warning("Missing 'Benefits' column in data.")

    elif report_type == "Budget Summary":
        st.markdown("### Budget vs Spend")
        if all(col in df.columns for col in ["Project Name", "Total Budget", "Spend to Date"]):
            st.dataframe(df[["Project Name", "Total Budget", "Spend to Date", "Estimate to Complete"]])
        else:
            st.warning("Budget-related columns are missing.")

    elif report_type == "Timeline View":
        st.markdown("### Project Timeframes")
        if all(col in df.columns for col in ["Project Name", "Start Date", "Finish Date"]):
            st.dataframe(df[["Project Name", "Start Date", "Finish Date"]])
        else:
            st.warning("Timeline columns are missing.")

# -------------------
# HOME
# -------------------
def render_home():
    st.subheader("🏡 Welcome to Stratigo")
    st.write("Use the menu to get started managing your project portfolio.")
    st.markdown("### Quick Tips")
    st.markdown("- Add new projects with budget and scope")
    st.markdown("- View reports by benefits or budget")
    st.markdown("- Edit projects in the portfolio section")

# -------------------
# MAIN NAVIGATION
# -------------------
menu = st.sidebar.radio("Navigate", ["🏡 Home", "➕ Add Project", "📋 Portfolio", "📊 Reports"])

if menu == "🏡 Home":
    render_home()
elif menu == "➕ Add Project":
    render_project_form()
elif menu == "📋 Portfolio":
    render_dashboard()
elif menu == "📊 Reports":
    render_reports()
