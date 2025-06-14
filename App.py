import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

st.set_page_config(page_title="Project Portfolio App")

# App title
st.title("📊 Project Portfolio Tracker")

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
gc = gspread.authorize(credentials)

sheet = gc.open_by_key(st.secrets["GOOGLE_SHEET_KEY"]).worksheet("Projects")

# Sidebar menu
menu = st.sidebar.radio("Menu", ["Add New Project", "View Portfolio"])

# Data headers (must match sheet)
headers = ["Project Name", "Sponsor", "Start Date", "Finish Date", "Timeframe",
           "Budget", "Spend to Date", "Estimate to Complete", "Key Deliverables", "Scope", "Benefits"]

if menu == "Add New Project":
    st.subheader("📝 Add New Project")

    project_data = [
        st.text_input("Project Name"),
        st.text_input("Sponsor"),
        str(st.date_input("Start Date", value=date.today())),
        str(st.date_input("Finish Date")),
        st.text_input("Timeframe / Phases"),
        st.number_input("Budget", min_value=0.0, step=1000.0),
        st.number_input("Spend to Date", min_value=0.0, step=1000.0),
        st.number_input("Estimate to Complete", min_value=0.0, step=1000.0),
        st.text_area("Key Deliverables"),
        st.text_area("Scope"),
        st.text_area("Benefits")
    ]

    if st.button("Save Project"):
        sheet.append_row(project_data)
        st.success("✅ Project saved to Google Sheet!")

elif menu == "View Portfolio":
    st.subheader("📋 Portfolio Overview")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    st.dataframe(df)

    if not df.empty:
        st.subheader("💰 Budget vs Spend")
        st.bar_chart(df[["Budget", "Spend to Date"]].set_index(df["Project Name"]))
