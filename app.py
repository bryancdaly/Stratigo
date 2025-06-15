# Stratigo Project Portfolio App – Version 1.1

import streamlit as st
import pandas as pd
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
st.set_page_config(page_title="Stratigo", layout="wide")

# --- GOOGLE SHEET CONNECTION ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(st.secrets["GOOGLE_SHEET_KEY"]).sheet1

# --- SESSION STATE INITIALISATION ---
for key in ["authenticated", "deliverables_items", "scope_items", "benefits_items", "project_to_edit"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "authenticated" else []

# --- SIMPLE PASSWORD AUTH ---
PASSWORD = "Stratigo2025"
if not st.session_state.authenticated:
    pw = st.text_input("Enter password", type="password")
    if pw == PASSWORD:
        st.session_state.authenticated = True
    else:
        st.warning("Incorrect password.")
        st.stop()

# --- PAGE NAVIGATION ---
page = st.selectbox("📚 Navigate", ["🏠 Home", "📋 Projects", "➕ Add Project", "📊 Reports"])

# --- FUNCTIONS ---

def load_projects():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def save_project(data_dict):
    sheet.append_row(list(data_dict.values()))

def update_project(row_index, data_dict):
    for col, val in enumerate(data_dict.values(), start=1):
        sheet.update_cell(row_index + 2, col, val)  # offset header + 0-based index

def edit_list(title, session_key):
    updated_list = st.session_state[session_key]
    remove_index = None

    for idx, item in enumerate(updated_list):
        cols = st.columns([5, 1])
        updated_list[idx] = cols[0].text_input(f"{title} {idx+1}", value=item, key=f"{session_key}_{idx}")
        if cols[1].button("🗑", key=f"remove_{session_key}_{idx}"):
            remove_index = idx

    if remove_index is not None:
        updated_list.pop(remove_index)

    if st.button(f"➕ Add {title}"):
        updated_list.append("")

    return updated_list

# --- PAGES ---

def render_home():
    st.title("🏡 Welcome to Stratigo")
    st.markdown("Use the menu to get started managing your project portfolio.")

def render_projects():
    st.title("📋 Project Dashboard")
    df = load_projects()

    if df.empty:
        st.info("No projects added yet.")
        return

    for i, row in df.iterrows():
        with st.expander(f"📁 {row['Project Name']}"):
            st.markdown(f"**Sponsor:** {row['Sponsor']}")
            st.markdown(f"**Timeframe:** {row['Timeframe / Phases']}")
            st.markdown(f"**Budget:** ${row['Total Budget']}, **Spend:** ${row['Spend to Date']}, **ETC:** ${row['Estimate to Complete']}")
            st.markdown(f"**Scope:** {row['Scope']}")
            st.markdown(f"**Deliverables:** {row['Deliverables']}")
            st.markdown(f"**Benefits:** {row['Benefits']}")
            if st.button(f"✏️ Edit '{row['Project Name']}'", key=f"edit_{i}"):
                st.session_state.project_to_edit = i
                st.session_state.page = "edit"

def render_project_form(edit_mode=False):
    st.title("📝 Edit Project" if edit_mode else "➕ Add Project")
    df = load_projects()

    if edit_mode:
        index = st.session_state.project_to_edit
        row = df.iloc[index]
        st.session_state.deliverables_items = row["Deliverables"].split("; ") if row["Deliverables"] else []
        st.session_state.scope_items = row["Scope"].split("; ") if row["Scope"] else []
        st.session_state.benefits_items = row["Benefits"].split("; ") if row["Benefits"] else []
    else:
        st.session_state.deliverables_items = []
        st.session_state.scope_items = []
        st.session_state.benefits_items = []

    with st.form("project_form"):
        project_name = st.text_input("Project Name", value=row["Project Name"] if edit_mode else "")
        sponsor = st.text_input("Sponsor", value=row["Sponsor"] if edit_mode else "")
        start = st.date_input("Start Date", value=pd.to_datetime(row["Start Date"]) if edit_mode else None)
        finish = st.date_input("Finish Date", value=pd.to_datetime(row["Finish Date"]) if edit_mode else None)
        timeframe = st.text_input("Timeframe / Phases", value=row["Timeframe / Phases"] if edit_mode else "")
        budget = st.number_input("Total Budget", value=float(row["Total Budget"]) if edit_mode else 0.0)
        spend = st.number_input("Spend to Date", value=float(row["Spend to Date"]) if edit_mode else 0.0)
        etc = st.number_input("Estimate to Complete", value=float(row["Estimate to Complete"]) if edit_mode else 0.0)

        st.markdown("### 📌 Scope")
        scope = edit_list("Scope", "scope_items")
        st.markdown("### 📦 Deliverables")
        deliverables = edit_list("Deliverables", "deliverables_items")
        st.markdown("### 🎯 Benefits")
        benefits = edit_list("Benefits", "benefits_items")

        submitted = st.form_submit_button("💾 Save Project")
        if submitted:
            project_data = {
                "Project Name": project_name,
                "Sponsor": sponsor,
                "Start Date": str(start),
                "Finish Date": str(finish),
                "Timeframe / Phases": timeframe,
                "Total Budget": budget,
                "Spend to Date": spend,
                "Estimate to Complete": etc,
                "Scope": "; ".join(scope),
                "Deliverables": "; ".join(deliverables),
                "Benefits": "; ".join(benefits),
            }

            if edit_mode:
                update_project(index, project_data)
                st.success("✅ Project updated!")
            else:
                save_project(project_data)
                st.success("✅ Project added!")

def render_reports():
    st.title("📊 Reports")
    df = load_projects()

    report_type = st.selectbox("Choose report", ["Benefits Overview", "Budget Summary"])
    if df.empty:
        st.warning("No data available.")
        return

    if report_type == "Benefits Overview":
        if "Benefits" not in df.columns:
            st.error("Missing 'Benefits' column.")
        else:
            df["# Benefits"] = df["Benefits"].str.split("; ").apply(len)
            st.bar_chart(df.set_index("Project Name")["# Benefits"])
    elif report_type == "Budget Summary":
        st.bar_chart(df.set_index("Project Name")[["Total Budget", "Spend to Date", "Estimate to Complete"]])

# --- MAIN ROUTER ---

if page == "🏠 Home":
    render_home()
elif page == "📋 Projects":
    render_projects()
elif page == "➕ Add Project":
    render_project_form(edit_mode=False)
elif page == "📊 Reports":
    render_reports()
elif page == "edit":
    render_project_form(edit_mode=True)
