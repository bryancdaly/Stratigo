# Stratigo - Project Portfolio App v1.0.0

import streamlit as st
import pandas as pd
import json
from datetime import date
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Stratigo", layout="wide")

st.markdown("<h1 style='text-align: center; color: #007bff;'>Stratigo</h1>", unsafe_allow_html=True)

PASSWORD = "Stratigo2025"

# ------------------ SESSION INIT ------------------
for key in ["deliverables", "scope", "benefits"]:
    st.session_state.setdefault(key, [""])

# ------------------ AUTH ------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "attempted" not in st.session_state:
    st.session_state.attempted = False

if not st.session_state.authenticated:
    with st.form("login_form"):
        pw = st.text_input("Enter password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            st.session_state.attempted = True
            if pw == PASSWORD:
                st.session_state.authenticated = True
                st.experimental_rerun()

    if st.session_state.attempted and not st.session_state.authenticated:
        st.error("Incorrect password.")
    st.stop()

# ------------------ GOOGLE SHEET SETUP ------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = st.secrets["GOOGLE_SERVICE_ACCOUNT"]
credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
client = gspread.authorize(credentials)
SHEET_ID = "1-3nm4rATb0nOm4P3cjgtEVRhJATkJBsjQJRdsx4rnKs"
sheet = client.open_by_key(SHEET_ID).sheet1

# ------------------ NAVIGATION ------------------
menu = st.sidebar.radio("Navigate", ["🏠 Home", "➕ Add Project", "📝 Edit Projects", "📊 Reports"])

# ------------------ DATA ------------------
def load_data():
    data = pd.DataFrame(sheet.get_all_records())
    if data.empty:
        return pd.DataFrame(columns=[
            "Project Name", "Sponsor", "Start Date", "Finish Date", "Timeframe / Phases",
            "Total Budget", "Spend to Date", "Estimate to Complete", "Deliverables",
            "Scope", "Benefits"
        ])
    return data

def save_data(project_dict):
    data = load_data()
    data = data.append(project_dict, ignore_index=True)
    sheet.update([data.columns.values.tolist()] + data.values.tolist())

# ------------------ HOME ------------------
if menu == "🏠 Home":
    st.markdown("""
    ### 👋 Welcome to Stratigo
    - Use the sidebar to **Add Projects**, **Edit Projects**, or **View Reports**
    """)
    st.image("https://images.unsplash.com/photo-1564866657315-3c38f22ab497?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80", use_column_width=True)

# ------------------ ADD PROJECT ------------------
if menu == "➕ Add Project":
    with st.form("project_form"):
        st.subheader("📌 Project Information")
        name = st.text_input("Project Name")
        sponsor = st.text_input("Sponsor")
        start = st.date_input("Start Date", date.today())
        end = st.date_input("Finish Date", date.today())
        timeframe = st.text_input("Timeframe / Phases")
        budget = st.number_input("Total Budget", min_value=0.0, step=1000.0)
        spend = st.number_input("Spend to Date", min_value=0.0, step=1000.0)
        etc = st.number_input("Estimate to Complete", min_value=0.0, step=1000.0)

        st.markdown("### 📦 Deliverables")
        for i, val in enumerate(st.session_state.deliverables):
            st.session_state.deliverables[i] = st.text_input(f"Deliverable {i+1}", val, key=f"del_{i}")
        if st.button("Add Deliverable"):
            st.session_state.deliverables.append("")
        if len(st.session_state.deliverables) > 1 and st.button("Remove Last Deliverable"):
            st.session_state.deliverables.pop()

        st.markdown("### 📋 Scope")
        for i, val in enumerate(st.session_state.scope):
            st.session_state.scope[i] = st.text_input(f"Scope {i+1}", val, key=f"sc_{i}")
        if st.button("Add Scope"):
            st.session_state.scope.append("")
        if len(st.session_state.scope) > 1 and st.button("Remove Last Scope"):
            st.session_state.scope.pop()

        st.markdown("### 🎯 Benefits")
        for i, val in enumerate(st.session_state.benefits):
            st.session_state.benefits[i] = st.text_input(f"Benefit {i+1}", val, key=f"ben_{i}")
        if st.button("Add Benefit"):
            st.session_state.benefits.append("")
        if len(st.session_state.benefits) > 1 and st.button("Remove Last Benefit"):
            st.session_state.benefits.pop()

        submitted = st.form_submit_button("Submit Project")
        if submitted:
            row = {
                "Project Name": name,
                "Sponsor": sponsor,
                "Start Date": str(start),
                "Finish Date": str(end),
                "Timeframe / Phases": timeframe,
                "Total Budget": budget,
                "Spend to Date": spend,
                "Estimate to Complete": etc,
                "Deliverables": "; ".join(st.session_state.deliverables),
                "Scope": "; ".join(st.session_state.scope),
                "Benefits": "; ".join(st.session_state.benefits)
            }
            save_data(row)
            st.success("Project added successfully!")
            for key in ["deliverables", "scope", "benefits"]:
                st.session_state[key] = [""]

# ------------------ EDIT PROJECTS ------------------
if menu == "📝 Edit Projects":
    df = load_data()
    if df.empty:
        st.warning("No projects found.")
    else:
        selected = st.selectbox("Select a project to edit", df["Project Name"].unique())
        project = df[df["Project Name"] == selected].iloc[0]
        st.write(project)  # Placeholder — can implement actual update later

# ------------------ REPORTS ------------------
if menu == "📊 Reports":
    df = load_data()
    if df.empty:
        st.warning("No data to report on.")
    else:
        st.subheader("💰 Budget vs Spend")
        fig = px.bar(df, x="Project Name", y=["Total Budget", "Spend to Date", "Estimate to Complete"], barmode="group")
        st.plotly_chart(fig)

        st.subheader("📅 Timeline Overview")
        if "Start Date" in df.columns and "Finish Date" in df.columns:
            df["Start Date"] = pd.to_datetime(df["Start Date"])
            df["Finish Date"] = pd.to_datetime(df["Finish Date"])
            st.write(df[["Project Name", "Start Date", "Finish Date"]])
        else:
            st.info("Timeline data incomplete.")
