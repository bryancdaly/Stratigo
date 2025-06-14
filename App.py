import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# App setup
st.set_page_config(page_title="Stratigo Project Portfolio", layout="wide")
st.title("📊 Stratigo Project Portfolio Manager")

# Authorise access using credentials from Streamlit secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
import json
credentials_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
gc = gspread.authorize(credentials)

# Connect to your Google Sheet
sheet = gc.open_by_key(st.secrets["GOOGLE_SHEET_KEY"]).worksheet("Projects")

# Sidebar menu
menu = st.sidebar.radio("Navigation", ["➕ Add New Project", "📋 Portfolio Dashboard"])

# Define headers for consistency
headers = ["Project Name", "Sponsor", "Start Date", "Finish Date", "Timeframe",
           "Budget", "Spend to Date", "Estimate to Complete", "Key Deliverables", "Scope", "Benefits"]

# --- Add New Project Form ---
if menu == "➕ Add New Project":
    st.subheader("Add New Project")

    with st.form("project_form"):
        project_name = st.text_input("Project Name")
        sponsor = st.text_input("Sponsor")
        start_date = st.date_input("Start Date", value=date.today())
        finish_date = st.date_input("Finish Date")
        timeframe = st.text_input("Timeframe / Phases")
        budget = st.number_input("Budget", min_value=0.0, step=1000.0)
        spend_to_date = st.number_input("Spend to Date", min_value=0.0, step=1000.0)
        estimate_to_complete = st.number_input("Estimate to Complete", min_value=0.0, step=1000.0)
        key_deliverables = st.text_area("Key Deliverables")
        scope = st.text_area("Scope")
        benefits = st.text_area("Expected Benefits")

        submitted = st.form_submit_button("Save Project")

    if submitted:
        new_row = [
            project_name, sponsor, str(start_date), str(finish_date), timeframe,
            budget, spend_to_date, estimate_to_complete, key_deliverables, scope, benefits
        ]
        sheet.append_row(new_row)
        st.success("✅ Project saved successfully!")

# --- Portfolio Dashboard ---
elif menu == "📋 Portfolio Dashboard":
    st.subheader("Project Portfolio Dashboard")

    try:
        data = sheet.get_all_records()
        if not data:
            st.info("No projects found yet.")
        else:
            df = pd.DataFrame(data)

            st.dataframe(df)

            if not df.empty:
                st.subheader("💰 Budget vs Spend")
                chart_data = df[["Project Name", "Budget", "Spend to Date"]].set_index("Project Name")
                st.bar_chart(chart_data)

                st.subheader("📅 Timeline Overview")
                df["Start Date"] = pd.to_datetime(df["Start Date"])
                df["Finish Date"] = pd.to_datetime(df["Finish Date"])
                timeline = df[["Project Name", "Start Date", "Finish Date"]].sort_values("Start Date")
                st.dataframe(timeline)

    except Exception as e:
        st.error(f"Error loading project data: {e}")
