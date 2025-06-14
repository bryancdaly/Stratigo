# Stratigo v3.0 — Full Portfolio Toolkit
import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date
import plotly.express as px

st.set_page_config(page_title="Stratigo", layout="wide")
st.title("📊 Stratigo Project Portfolio")

# Password Protection
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.error("Incorrect password")
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(st.secrets["GOOGLE_SHEET_KEY"]).worksheet("Projects")

# Helpers
def cast_to_float(val):
    try:
        return float(str(val).replace(",", ""))
    except:
        return 0.0

def edit_list(label, key_prefix):
    items = st.session_state.get(f"{key_prefix}_items", [""])
    updated = [st.text_input(f"{label} {i+1}", value=items[i], key=f"{key_prefix}_{i}") for i in range(len(items))]
    st.session_state[f"{key_prefix}_items"] = updated
    return "\n".join(i for i in updated if i.strip())

def save_row(values, idx=None):
    if idx is None:
        sheet.append_row(values)
    else:
        sheet.update(f"A{idx+2}", [values])

# Project Form
def render_project_form(edit_index=None):
    is_edit = edit_index is not None
    existing = sheet.get_all_records()
    row = existing[edit_index] if is_edit else {}

    if is_edit:
        st.session_state["deliverables_items"] = row.get("Key Deliverables", "").split("\n")
        st.session_state["scope_items"] = row.get("Scope", "").split("\n")
        st.session_state["benefits_items"] = row.get("Benefits", "").split("\n")

    with st.form("project_form"):
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input("Project Name", value=row.get("Project Name", ""))
            sponsor = st.text_input("Sponsor", value=row.get("Sponsor", ""))
            start_date = st.date_input("Start Date", value=pd.to_datetime(row.get("Start Date", date.today())).date())
            finish_date = st.date_input("Finish Date", value=pd.to_datetime(row.get("Finish Date", date.today())).date())
            timeframe = st.text_input("Timeframe / Phases", value=row.get("Timeframe / Phases", ""))
            status = st.selectbox("Status", ["Not Started", "In Progress", "On Hold", "Completed"], index=["Not Started", "In Progress", "On Hold", "Completed"].index(row.get("Status", "Not Started")))
        with col2:
            budget = st.number_input("Budget", value=cast_to_float(row.get("Budget", 0)))
            spend = st.number_input("Spend to Date", value=cast_to_float(row.get("Spend to Date", 0)))
            etc = st.number_input("Estimate to Complete", value=cast_to_float(row.get("Estimate to Complete", 0)))

        st.markdown("#### Key Deliverables")
        key_deliverables = edit_list("Deliverable", "deliverables")
        if st.button("➕ Add Deliverable"): st.session_state["deliverables_items"].append("")

        st.markdown("#### Scope")
        scope = edit_list("Scope", "scope")
        if st.button("➕ Add Scope"): st.session_state["scope_items"].append("")

        st.markdown("#### Benefits")
        benefits = edit_list("Benefit", "benefits")
        if st.button("➕ Add Benefit"): st.session_state["benefits_items"].append("")

        submitted = st.form_submit_button("💾 Save")
        if submitted:
            data = [project_name, sponsor, str(start_date), str(finish_date), timeframe, status, budget, spend, etc, key_deliverables, scope, benefits]
            save_row(data, edit_index)
            st.success("Project saved." if not is_edit else "Project updated.")
            st.session_state.page = "home"
            st.rerun()

# Home Menu
def render_home():
    col1, col2, col3 = st.columns(3)
    if col1.button("➕ Add Project"): st.session_state.page = "add"; st.rerun()
    if col2.button("📋 View Portfolio"): st.session_state.page = "portfolio"; st.rerun()
    if col3.button("📊 Reports"): st.session_state.page = "reports"; st.rerun()

# Dashboard
def render_dashboard():
    st.subheader("📋 Portfolio Overview")
    df = pd.DataFrame(sheet.get_all_records())
    if df.empty:
        st.info("No projects yet."); return

    status_filter = st.selectbox("Filter by status", ["All"] + sorted(df["Status"].unique()))
    if status_filter != "All":
        df = df[df["Status"] == status_filter]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Projects", len(df))
    col2.metric("Total Budget", f"${df['Budget'].sum():,.0f}")
    col3.metric("Total Spend", f"${df['Spend to Date'].sum():,.0f}")
    col4.metric("Total ETC", f"${df['Estimate to Complete'].sum():,.0f}")

    st.dataframe(df)

    for i, row in df.iterrows():
        with st.expander(f"🔍 {row['Project Name']}"):
            st.write(f"**Sponsor**: {row['Sponsor']}")
            st.write(f"**Status**: {row['Status']}")
            st.write(f"**Dates**: {row['Start Date']} → {row['Finish Date']}")
            st.write(f"**Budget**: ${row['Budget']:,.0f} — Spend: ${row['Spend to Date']:,.0f} — ETC: ${row['Estimate to Complete']:,.0f}")
            if st.button(f"✏️ Edit", key=f"edit_{i}"):
                st.session_state.edit_index = i
                st.session_state.page = "edit"
                st.rerun()

# Reports
def render_reports():
    st.subheader("📊 Reports")
    df = pd.DataFrame(sheet.get_all_records())
    if df.empty: st.warning("No data available."); return

    report_type = st.selectbox("Choose report", ["Gantt Timeline", "Benefits Summary", "Export to CSV"])
    if report_type == "Gantt Timeline":
        df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
        df["Finish Date"] = pd.to_datetime(df["Finish Date"], errors="coerce")
        fig = px.timeline(df, x_start="Start Date", x_end="Finish Date", y="Project Name", color="Status")
        st.plotly_chart(fig, use_container_width=True)

    elif report_type == "Benefits Summary":
        df["# Benefits"] = df["Benefits"].astype(str).str.split("\n").apply(len)
        st.bar_chart(df.set_index("Project Name")["# Benefits"])

    elif report_type == "Export to CSV":
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", data=csv, file_name="stratigo_projects.csv", mime="text/csv")

# Admin Tools
def render_admin():
    st.subheader("🛠️ Admin Panel")
    df = pd.DataFrame(sheet.get_all_records())
    st.dataframe(df)
    row_to_delete = st.number_input("Row to delete (1 = top)", min_value=1, max_value=len(df), step=1)
    if st.button("❌ Confirm Delete"):
        sheet.delete_rows(row_to_delete + 1)
        st.success("Row deleted.")
        st.rerun()

# Router
page = st.session_state.get("page", "home")
if page == "home": render_home()
elif page == "add": render_project_form()
elif page == "edit": render_project_form(st.session_state.edit_index)
elif page == "portfolio": render_dashboard()
elif page == "reports": render_reports()
elif page == "admin": render_admin()
