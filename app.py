# Stratigo v2.0 — Multi-benefit + Edit functionality + Reporting

import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# App config
st.set_page_config(page_title="Stratigo", layout="wide")
st.title("📊 Stratigo Project Portfolio Manager")

# --- Auth protection ---
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
        st.error("❌ Incorrect password")
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()

# --- Google Sheets connection ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(st.secrets["GOOGLE_SHEET_KEY"]).worksheet("Projects")

# --- Sidebar Navigation ---
menu = st.sidebar.radio("📁 Menu", ["➕ Add Project", "📋 Portfolio", "📊 Reports"])

# --- Dynamic list editor ---
def edit_list(label, key_prefix):
    items = st.session_state.get(f"{key_prefix}_items", [""])
    updated_items = []

    for i, item in enumerate(items):
        updated_items.append(st.text_input(f"{label} {i+1}", value=item, key=f"{key_prefix}_{i}"))

    st.session_state[f"{key_prefix}_items"] = updated_items
    return "\n".join(i for i in updated_items if i.strip())

# --- Shared row-saving function ---
def save_row(values, row_idx=None):
    if row_idx is None:
        sheet.append_row(values)
    else:
        sheet.update(f"A{row_idx+2}", [values])

# --- Form Logic ---
def render_project_form(edit_index=None):
    is_edit = edit_index is not None
    st.subheader("✏️ Edit Project" if is_edit else "➕ Add New Project")

    existing = sheet.get_all_records()
    if is_edit:
        row = existing[edit_index]
        st.session_state["deliverables_items"] = row["Key Deliverables"].split("\n")
        st.session_state["scope_items"] = row["Scope"].split("\n")
        st.session_state["benefits_items"] = row["Benefits"].split("\n")

    with st.form("project_form"):
        col1, col2 = st.columns(2)

        with col1:
            project_name = st.text_input("Project Name", value=row["Project Name"] if is_edit else "")
            sponsor = st.text_input("Sponsor", value=row["Sponsor"] if is_edit else "")
            start_date = st.date_input("Start Date", value=pd.to_datetime(row["Start Date"]).date() if is_edit else date.today())
            finish_date = st.date_input("Finish Date", value=pd.to_datetime(row["Finish Date"]).date() if is_edit else date.today())
            timeframe = st.text_input("Timeframe / Phases", value=row["Timeframe / Phases"] if is_edit else "")

        with col2:
            budget = st.number_input("Total Budget ($)", min_value=0.0, step=1000.0, value=row["Budget"] if is_edit else 0.0)
            spend_to_date = st.number_input("Spend to Date ($)", min_value=0.0, step=1000.0, value=row["Spend to Date"] if is_edit else 0.0)
            estimate_to_complete = st.number_input("Estimate to Complete ($)", min_value=0.0, step=1000.0, value=row["Estimate to Complete"] if is_edit else 0.0)

        st.markdown("### 📦 Deliverables")
        key_deliverables = edit_list("Deliverable", "deliverables")

        st.markdown("### 📋 Scope")
        scope = edit_list("Scope Item", "scope")

        st.markdown("### 🏆 Benefits")
        benefits = edit_list("Benefit", "benefits")

        submitted = st.form_submit_button("💾 Save Project")

    if submitted:
        row_data = [
            project_name, sponsor, str(start_date), str(finish_date), timeframe,
            budget, spend_to_date, estimate_to_complete,
            key_deliverables, scope, benefits
        ]
        save_row(row_data, edit_index)
        st.success("✅ Project saved!" if not is_edit else "✅ Project updated!")

    st.markdown("### ➕ Manage Lists")
    col_d, col_s, col_b = st.columns(3)
    if col_d.button("➕ Add Deliverable"):
        st.session_state["deliverables_items"] = st.session_state.get("deliverables_items", []) + [""]
    if col_s.button("➕ Add Scope Item"):
        st.session_state["scope_items"] = st.session_state.get("scope_items", []) + [""]
    if col_b.button("➕ Add Benefit"):
        st.session_state["benefits_items"] = st.session_state.get("benefits_items", []) + [""]

# --- Portfolio View ---
def render_dashboard():
    st.subheader("📋 Project Portfolio")
    records = sheet.get_all_records()
    if not records:
        st.info("No projects found.")
        return

    df = pd.DataFrame(records)
    st.dataframe(df)

    for i, row in df.iterrows():
        with st.expander(f"🔎 {row['Project Name']}"):
            st.write(f"Sponsor: **{row['Sponsor']}**")
            st.write(f"Timeframe: {row['Timeframe / Phases']}")
            st.write(f"Budget: ${row['Budget']:.0f}, Spend: ${row['Spend to Date']:.0f}, ETC: ${row['Estimate to Complete']:.0f}")
            if st.button(f"✏️ Edit '{row['Project Name']}'", key=f"edit_{i}"):
                st.session_state["edit_index"] = i
                st.experimental_rerun()

# --- Reports View ---
def render_reports():
    st.subheader("📊 Reports")
    report_type = st.selectbox("Choose report:", ["Budget vs Spend", "Benefits Overview", "Timeline Summary"])

    df = pd.DataFrame(sheet.get_all_records())
    if df.empty:
        st.warning("No data available.")
        return

    if report_type == "Budget vs Spend":
        st.bar_chart(df.set_index("Project Name")[["Budget", "Spend to Date"]])
    elif report_type == "Benefits Overview":
        df["# Benefits"] = df["Benefits"].str.split("\n").apply(len)
        st.bar_chart(df.set_index("Project Name")["# Benefits"])
    elif report_type == "Timeline Summary":
        df["Start Date"] = pd.to_datetime(df["Start Date"])
        df["Finish Date"] = pd.to_datetime(df["Finish Date"])
        st.dataframe(df[["Project Name", "Start Date", "Finish Date"]].sort_values("Start Date"))

# --- Navigation ---
if "edit_index" in st.session_state:
    render_project_form(st.session_state.pop("edit_index"))
elif menu == "➕ Add Project":
    render_project_form()
elif menu == "📋 Portfolio":
    render_dashboard()
elif menu == "📊 Reports":
    render_reports()
