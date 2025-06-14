# Stratigo v2.4 — Full App File
import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

# --- PAGE CONFIG ---
st.set_page_config(page_title="Stratigo", layout="wide")

# --- NAVIGATION MENU ---
st.sidebar.title("📘 Stratigo Menu")
page = st.sidebar.radio("Navigate", ["🏠 Home", "➕ Add Project", "📋 Portfolio", "📊 Reports", "🛠️ Admin"])

# --- AUTHENTICATION ---
if "authenticated" not in st.session_state:
    password = st.text_input("Enter password to access Stratigo:", type="password")
    if password == "Stratigo2025":
        st.session_state.authenticated = True
        st.rerun()
    else:
        st.stop()
elif not st.session_state.authenticated:
    st.stop()

# --- GOOGLE SHEETS SETUP ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1-3nm4rATb0nOm4P3cjgtEVRhJATkJBsjQJRdsx4rnKs").sheet1

# --- SESSION STATE INIT ---
for field in ["deliverables_items", "scope_items", "benefits_items"]:
    if field not in st.session_state:
        st.session_state[field] = [""]

# --- HOME ---
if page == "🏠 Home":
    st.title("🏠 Welcome to Stratigo")
    st.markdown("Use the menu to get started managing your project portfolio.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.page_link("🏠 Home", label="🏠 Home", icon="🏠")
    with col2:
        st.page_link("➕ Add Project", label="➕ Add", icon="➕")
    with col3:
        st.page_link("📊 Reports", label="📊 Reports", icon="📊")

# --- ADD PROJECT FORM ---
elif page == "➕ Add Project":
    st.title("➕ Add Project")

    with st.form("project_form"):
        name = st.text_input("Project Name")
        sponsor = st.text_input("Sponsor")
        status = st.selectbox("Status", ["Not Started", "In Progress", "On Hold", "Completed"])
        start_date = st.date_input("Start Date")
        end_date = st.date_input("Finish Date")
        timeframe = st.text_input("Timeframe / Phases")
        budget = st.number_input("Budget", step=1000.0)
        spend = st.number_input("Spend to Date", step=1000.0)
        etc = st.number_input("Estimate to Complete", step=1000.0)

        # Deliverables
        st.markdown("### Deliverables")
        for i, item in enumerate(st.session_state.deliverables_items):
            st.session_state.deliverables_items[i] = st.text_input(f"Deliverable {i+1}", value=item, key=f"deliv_{i}")
        if st.form_submit_button("Add Deliverable"):
            st.session_state.deliverables_items.append("")

        # Scope
        st.markdown("### Scope")
        for i, item in enumerate(st.session_state.scope_items):
            st.session_state.scope_items[i] = st.text_input(f"Scope Item {i+1}", value=item, key=f"scope_{i}")
        if st.form_submit_button("Add Scope"):
            st.session_state.scope_items.append("")

        # Benefits
        st.markdown("### Benefits")
        for i, item in enumerate(st.session_state.benefits_items):
            st.session_state.benefits_items[i] = st.text_input(f"Benefit {i+1}", value=item, key=f"benefit_{i}")
        if st.form_submit_button("Add Benefit"):
            st.session_state.benefits_items.append("")

        if st.form_submit_button("✅ Submit Project"):
            data = [name, sponsor, status, str(start_date), str(end_date), timeframe, budget, spend, etc,
                    "; ".join(st.session_state.deliverables_items),
                    "; ".join(st.session_state.scope_items),
                    "; ".join(st.session_state.benefits_items)]
            sheet.append_row(data)
            st.success("Project submitted successfully.")
            st.session_state.deliverables_items = [""]
            st.session_state.scope_items = [""]
            st.session_state.benefits_items = [""]

# --- PORTFOLIO VIEW ---
elif page == "📋 Portfolio":
    st.title("📋 Project Portfolio")
    df = pd.DataFrame(sheet.get_all_records())

    status_filter = st.multiselect("Filter by Status", options=df["Status"].unique(), default=df["Status"].unique())
    df_filtered = df[df["Status"].isin(status_filter)]

    st.dataframe(df_filtered, use_container_width=True)

    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="portfolio.csv", mime="text/csv")

# --- REPORTS ---
elif page == "📊 Reports":
    st.title("📊 Reports Dashboard")
    df = pd.DataFrame(sheet.get_all_records())

    col1, col2 = st.columns(2)
    with col1:
        total_budget = df["Budget"].sum()
        st.metric("Total Budget", f"${total_budget:,.0f}")
    with col2:
        spend_to_date = df["Spend to Date"].sum()
        st.metric("Spend to Date", f"${spend_to_date:,.0f}")

    st.markdown("### 🕓 Timeline")
    df["Start Date"] = pd.to_datetime(df["Start Date"])
    df["Finish Date"] = pd.to_datetime(df["Finish Date"])
    fig = px.timeline(df, x_start="Start Date", x_end="Finish Date", y="Project Name", color="Status")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

# --- ADMIN ---
elif page == "🛠️ Admin":
    st.title("🛠️ Admin Panel")
    df = pd.DataFrame(sheet.get_all_records())
    st.dataframe(df, use_container_width=True)

    row_to_delete = st.number_input("Delete Row #", min_value=2, max_value=len(df)+1)
    if st.button("Delete Row"):
        sheet.delete_row(row_to_delete)
        st.success(f"Deleted row {row_to_delete}")
        st.rerun()
