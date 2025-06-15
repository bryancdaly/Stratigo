# Stratigo v1.0 - Stable, Clean, Bug-Resilient
import streamlit as st
import pandas as pd
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Stratigo", layout="wide")
st.markdown("<h1 style='text-align: center;'>📘 Stratigo</h1>", unsafe_allow_html=True)

# ----------------- Google Sheet Setup -----------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(credentials)
sheet = client.open_by_key(st.secrets["GOOGLE_SHEET_ID"]).sheet1

# ----------------- Helper Functions -----------------
def get_data():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def save_data(df):
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

def init_example_data():
    if len(sheet.get_all_values()) <= 1:
        df = pd.DataFrame([{
            "Project Name": "Example Project",
            "Sponsor": "Jane Doe",
            "Start Date": "2025-06-01",
            "Finish Date": "2025-12-31",
            "Timeframe": "Q3-Q4",
            "Total Budget": 150000,
            "Spend": 25000,
            "ETC": 125000,
            "Deliverables": "MVP, Launch",
            "Scope": "User onboarding, Core feature set",
            "Benefits": "Revenue growth, Customer retention"
        }])
        save_data(df)

def show_success(msg):
    st.success(f"✅ {msg}")

# ----------------- Navigation -----------------
menu = st.sidebar.radio("Navigate", ["🏠 Home", "➕ Add Project", "📋 Projects", "📈 Reports"])

# ----------------- Pages -----------------
def home_page():
    st.markdown("### 🏠 Welcome to Stratigo\nUse the menu to get started managing your project portfolio.")

def add_project():
    st.markdown("### ➕ Add Project")

    with st.form("add_project_form"):
        name = st.text_input("Project Name")
        sponsor = st.text_input("Sponsor")
        start = st.date_input("Start Date")
        end = st.date_input("Finish Date")
        timeframe = st.text_input("Timeframe")
        budget = st.number_input("Total Budget", min_value=0)
        spend = st.number_input("Spend", min_value=0)
        etc = budget - spend

        deliverables = st.text_area("Deliverables (comma-separated)")
        scope = st.text_area("Scope (comma-separated)")
        benefits = st.text_area("Benefits (comma-separated)")

        submitted = st.form_submit_button("Submit")

        if submitted:
            df = get_data()
            new_row = {
                "Project Name": name,
                "Sponsor": sponsor,
                "Start Date": str(start),
                "Finish Date": str(end),
                "Timeframe": timeframe,
                "Total Budget": budget,
                "Spend": spend,
                "ETC": etc,
                "Deliverables": deliverables,
                "Scope": scope,
                "Benefits": benefits
            }
            df = df.append(new_row, ignore_index=True)
            save_data(df)
            show_success("Project added successfully.")

def view_projects():
    st.markdown("### 📋 All Projects")
    df = get_data()
    if df.empty:
        st.warning("No projects available.")
        return

    selected = st.selectbox("Select a project to edit", df["Project Name"])
    st.dataframe(df)

    if selected:
        row = df[df["Project Name"] == selected].iloc[0]
        with st.form("edit_form"):
            name = st.text_input("Project Name", row["Project Name"])
            sponsor = st.text_input("Sponsor", row["Sponsor"])
            start = st.date_input("Start Date", pd.to_datetime(row["Start Date"]))
            end = st.date_input("Finish Date", pd.to_datetime(row["Finish Date"]))
            timeframe = st.text_input("Timeframe", row["Timeframe"])
            budget = st.number_input("Total Budget", value=row.get("Total Budget", 0))
            spend = st.number_input("Spend", value=row.get("Spend", 0))
            etc = budget - spend
            deliverables = st.text_area("Deliverables", row["Deliverables"])
            scope = st.text_area("Scope", row["Scope"])
            benefits = st.text_area("Benefits", row["Benefits"])

            submit_edit = st.form_submit_button("Update Project")
            if submit_edit:
                idx = df[df["Project Name"] == selected].index[0]
                df.loc[idx] = [
                    name, sponsor, str(start), str(end), timeframe,
                    budget, spend, etc, deliverables, scope, benefits
                ]
                save_data(df)
                show_success("Project updated.")

def reports_page():
    st.markdown("### 📈 Reports")

    df = get_data()
    report = st.selectbox("Choose report", ["Benefits Overview", "Budget Summary"])

    if report == "Benefits Overview":
        if "Benefits" not in df.columns:
            st.error("Missing 'Benefits' column.")
        else:
            st.write("### 📊 Benefits by Project")
            for i, row in df.iterrows():
                st.markdown(f"- **{row['Project Name']}**: {row['Benefits']}")

    elif report == "Budget Summary":
        if not {"Project Name", "Total Budget", "Spend", "ETC"}.issubset(df.columns):
            st.error("Missing required columns for budget summary.")
        else:
            chart_data = df.set_index("Project Name")[["Total Budget", "Spend", "ETC"]]
            st.bar_chart(chart_data)

# ----------------- Run Pages -----------------
init_example_data()

if menu == "🏠 Home":
    home_page()
elif menu == "➕ Add Project":
    add_project()
elif menu == "📋 Projects":
    view_projects()
elif menu == "📈 Reports":
    reports_page()
