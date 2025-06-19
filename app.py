# Stratigo Project Portfolio Tracker v2.1

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials

# -------------- LOGIN ----------------
def login():
    st.title("📘 Stratigo")
    st.header("🔐 Login Required")
    password = st.text_input("Enter password:", type="password")
    if password == "Stratigo2025":
        st.success("✅ Logged in")
        st.session_state.logged_in = True
        st.experimental_rerun()
    elif password:
        st.error("Incorrect password")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    login()
    st.stop()

# -------------- GOOGLE SHEETS SETUP ----------------
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
client = gspread.authorize(credentials)

SHEET_ID = st.secrets["GOOGLE_SHEET_ID"]
sheet = client.open_by_key(SHEET_ID).sheet1

# -------------- NAVIGATION ----------------
st.title("📊 Stratigo Project Portfolio")
page = st.selectbox("📚 Navigate", ["🏠 Home", "➕ Add Project", "📈 Reports"])

# -------------- DATA HELPERS ----------------
def get_data():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def save_data(row):
    sheet.append_row(row)

def update_data(df):
    sheet.clear()
    sheet.append_row(df.columns.tolist())
    for i in df.values.tolist():
        sheet.append_row(i)

# -------------- FORM COMPONENTS ----------------
def edit_list(title, items, key_prefix):
    st.subheader(f"📌 {title}")
    for i in range(len(items)):
        items[i] = st.text_input(f"{title} {i+1}", items[i], key=f"{key_prefix}_{i}")
    if st.button(f"➕ Add {title}", key=f"{key_prefix}_add"):
        items.append("")
    if len(items) > 1 and st.button(f"➖ Remove Last {title}", key=f"{key_prefix}_remove"):
        items.pop()
    return items

# -------------- PAGES ----------------
def render_home():
    st.header("🏠 Welcome to Stratigo")
    st.markdown("Use the menu to get started managing your project portfolio.")

def render_add_project():
    st.header("➕ Add Project")
    with st.form("project_form", clear_on_submit=True):
        name = st.text_input("Project Name")
        sponsor = st.text_input("Sponsor")
        start = st.date_input("Start Date")
        finish = st.date_input("Finish Date")
        timeframe = st.text_input("Timeframe / Phases")
        budget = st.number_input("Total Budget", step=100.0)
        spend = st.number_input("Spend to Date", step=100.0)

        if "deliverables" not in st.session_state:
            st.session_state.deliverables = [""]
        if "scope" not in st.session_state:
            st.session_state.scope = [""]
        if "benefits" not in st.session_state:
            st.session_state.benefits = [""]

        st.session_state.deliverables = edit_list("Key Deliverables", st.session_state.deliverables, "deliverables")
        st.session_state.scope = edit_list("Scope", st.session_state.scope, "scope")
        st.session_state.benefits = edit_list("Benefits", st.session_state.benefits, "benefits")

        submitted = st.form_submit_button("✅ Save Project")
        if submitted:
            row = [
                name, sponsor, str(start), str(finish), timeframe,
                budget, spend, budget - spend,
                "; ".join(st.session_state.deliverables),
                "; ".join(st.session_state.scope),
                "; ".join(st.session_state.benefits)
            ]
            save_data(row)
            st.success("✅ Project added successfully!")

def render_reports():
    st.header("📈 Reports")
    df = get_data()
    if df.empty:
        st.warning("No data found.")
        return

    report_type = st.selectbox("Choose report", ["Benefits Overview", "Budget Summary"])
    
    if report_type == "Benefits Overview":
        if "Benefits" not in df.columns:
            st.error("Missing 'Benefits' column.")
            return
        st.subheader("🧩 Benefits Overview")
        df["Benefit Count"] = df["Benefits"].str.split(";").apply(len)
        fig = px.bar(df, x="Project Name", y="Benefit Count", title="Benefit Count per Project")
        st.plotly_chart(fig)

    elif report_type == "Budget Summary":
        if "Total Budget" not in df.columns or "Spend to Date" not in df.columns:
            st.error("Missing budget columns.")
            return
        st.subheader("💰 Budget Summary")
        df["ETC"] = df["Total Budget"] - df["Spend to Date"]
        fig = px.bar(df.set_index("Project Name")[["Total Budget", "Spend to Date", "ETC"]],
                     title="Budget Summary by Project")
        st.plotly_chart(fig)

# -------------- MAIN ----------------
if page == "🏠 Home":
    render_home()
elif page == "➕ Add Project":
    render_add_project()
elif page == "📈 Reports":
    render_reports()
