# Stratigo v2.3 — Improved Functionality + Bug Fixes

# Version: 2.3.0

# Release Date: 2025-06-14

# Changes: Fixed navigation conflicts, improved session state management,

# added error handling, form validation, and better list management

import streamlit as st
import pandas as pd
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# ––––––––––

# Page Config & Theme

# ––––––––––

st.set_page_config(page_title=“Stratigo”, layout=“wide”)
st.markdown(”<h1 style='text-align: center; color: #154360;'>📊 Stratigo</h1>”, unsafe_allow_html=True)

# ––––––––––

# Password Protection

# ––––––––––

def check_password():
def password_entered():
if st.session_state[“password”] == st.secrets[“APP_PASSWORD”]:
st.session_state[“password_correct”] = True
del st.session_state[“password”]
else:
st.session_state[“password_correct”] = False

```
if "password_correct" not in st.session_state:
    st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
    st.stop()
elif not st.session_state["password_correct"]:
    st.error("❌ Incorrect password")
    st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
    st.stop()
```

check_password()

# ––––––––––

# Google Sheets Setup with Error Handling

# ––––––––––

@st.cache_resource
def init_google_sheets():
try:
scope = [“https://spreadsheets.google.com/feeds”, “https://www.googleapis.com/auth/drive”]
credentials_dict = json.loads(st.secrets[“GOOGLE_SERVICE_ACCOUNT”])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(st.secrets[“GOOGLE_SHEET_KEY”]).worksheet(“Projects”)
return sheet
except Exception as e:
st.error(f”❌ Failed to connect to Google Sheets: {str(e)}”)
st.stop()

sheet = init_google_sheets()

# ––––––––––

# Session State Management

# ––––––––––

def clear_form_state():
“”“Clear all form-related session state”””
keys_to_clear = [
“deliverables_items”, “scope_items”, “benefits_items”,
“edit_index”, “current_page”
]
for key in keys_to_clear:
if key in st.session_state:
del st.session_state[key]

def set_page(page_name):
“”“Set current page and clear form state”””
clear_form_state()
st.session_state[“current_page”] = page_name
st.rerun()

# ––––––––––

# Navigation

# ––––––––––

# Handle page navigation from buttons

if “nav_action” in st.session_state:
action = st.session_state.pop(“nav_action”)
set_page(action)

menu = st.sidebar.radio(“📁 Navigation”, [“🏠 Home”, “➕ Add Project”, “📋 Portfolio”, “📊 Reports”])

# ––––––––––

# Shared Functions

# ––––––––––

def edit_list(label, key_prefix, existing_items=None):
“”“Improved list editing with better state management”””
if existing_items and f”{key_prefix}_items” not in st.session_state:
st.session_state[f”{key_prefix}_items”] = [item for item in existing_items if item.strip()]

```
if f"{key_prefix}_items" not in st.session_state:
    st.session_state[f"{key_prefix}_items"] = [""]

items = st.session_state[f"{key_prefix}_items"]
updated_items = []

for i, item in enumerate(items):
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        updated_item = st.text_input(f"{label} {i+1}", value=item, key=f"{key_prefix}_{i}")
        updated_items.append(updated_item)
    with col2:
        if len(items) > 1:
            if st.button("🗑️", key=f"del_{key_prefix}_{i}", help="Delete this item"):
                items.pop(i)
                st.session_state[f"{key_prefix}_items"] = items
                st.rerun()

st.session_state[f"{key_prefix}_items"] = updated_items
return "\n".join(item for item in updated_items if item.strip())
```

def save_row(values, row_idx=None):
“”“Save data with error handling”””
try:
if row_idx is None:
sheet.append_row(values)
else:
# Convert to range format for updating
range_name = f”A{row_idx+2}:K{row_idx+2}”
sheet.update(range_name, [values])
return True
except Exception as e:
st.error(f”❌ Failed to save data: {str(e)}”)
return False

def get_sheet_data():
“”“Get sheet data with error handling”””
try:
return sheet.get_all_records()
except Exception as e:
st.error(f”❌ Failed to load data: {str(e)}”)
return []

def cast_to_float(val):
“”“Improved number conversion with better error handling”””
if val is None or val == “”:
return 0.0
try:
# Handle string representations of numbers with commas
if isinstance(val, str):
val = val.replace(”,”, “”).replace(”$”, “”)
return float(val)
except (ValueError, TypeError):
return 0.0

def validate_form_data(project_name, sponsor, start_date, finish_date, budget, spend, etc):
“”“Validate form inputs”””
errors = []

```
if not project_name.strip():
    errors.append("Project Name is required")
if not sponsor.strip():
    errors.append("Sponsor is required")
if start_date > finish_date:
    errors.append("Start Date must be before Finish Date")
if budget < 0:
    errors.append("Budget cannot be negative")
if spend < 0:
    errors.append("Spend cannot be negative")
if etc < 0:
    errors.append("Estimate to Complete cannot be negative")
if spend + etc > budget * 1.5:  # Allow some tolerance
    errors.append("Spend + ETC significantly exceeds budget - please verify")

return errors
```

# ––––––––––

# Home Page

# ––––––––––

def render_home():
st.markdown(”### Welcome to **Stratigo** — your simple, cloud-based Project Portfolio Tracker.”)
st.write(“Use the tiles below to manage your portfolio:”)

```
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("➕ Add Project", use_container_width=True, key="home_add"):
        st.session_state["nav_action"] = "add"
        st.rerun()
with col2:
    if st.button("📋 View Portfolio", use_container_width=True, key="home_portfolio"):
        st.session_state["nav_action"] = "portfolio"
        st.rerun()
with col3:
    if st.button("📊 View Reports", use_container_width=True, key="home_reports"):
        st.session_state["nav_action"] = "reports"
        st.rerun()

# Show quick stats
try:
    records = get_sheet_data()
    if records:
        df = pd.DataFrame(records)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Projects", len(df))
        with col2:
            total_budget = sum(cast_to_float(row.get("Budget", 0)) for row in records)
            st.metric("Total Budget", f"${total_budget:,.0f}")
        with col3:
            total_spend = sum(cast_to_float(row.get("Spend to Date", 0)) for row in records)
            st.metric("Total Spend", f"${total_spend:,.0f}")
        with col4:
            if total_budget > 0:
                utilization = (total_spend / total_budget) * 100
                st.metric("Budget Utilization", f"{utilization:.1f}%")
except:
    pass  # Silently handle any errors in stats display
```

# ––––––––––

# Add or Edit Project

# ––––––––––

def render_project_form(edit_index=None):
is_edit = edit_index is not None
st.subheader(“✏️ Edit Project” if is_edit else “➕ Add New Project”)

```
existing = get_sheet_data()
if is_edit and (edit_index >= len(existing) or edit_index < 0):
    st.error("❌ Invalid project index")
    return

row = existing[edit_index] if is_edit else {}

# Initialize list items for editing
if is_edit:
    deliverables_list = row.get("Key Deliverables", "").split("\n") if row.get("Key Deliverables") else [""]
    scope_list = row.get("Scope", "").split("\n") if row.get("Scope") else [""]
    benefits_list = row.get("Benefits", "").split("\n") if row.get("Benefits") else [""]
else:
    deliverables_list = None
    scope_list = None
    benefits_list = None

with st.form("project_form"):
    col1, col2 = st.columns(2)

    with col1:
        project_name = st.text_input("Project Name *", value=row.get("Project Name", ""))
        sponsor = st.text_input("Sponsor *", value=row.get("Sponsor", ""))
        
        # Handle date conversion more robustly
        try:
            start_default = pd.to_datetime(row.get("Start Date", date.today())).date()
        except:
            start_default = date.today()
        try:
            finish_default = pd.to_datetime(row.get("Finish Date", date.today())).date()
        except:
            finish_default = date.today()
            
        start_date = st.date_input("Start Date *", value=start_default)
        finish_date = st.date_input("Finish Date *", value=finish_default)
        timeframe = st.text_input("Timeframe / Phases", value=row.get("Timeframe / Phases", ""))

    with col2:
        budget = st.number_input("Total Budget ($) *", value=cast_to_float(row.get("Budget", 0)), min_value=0.0, format="%.2f")
        spend = st.number_input("Spend to Date ($)", value=cast_to_float(row.get("Spend to Date", 0)), min_value=0.0, format="%.2f")
        etc = st.number_input("Estimate to Complete ($)", value=cast_to_float(row.get("Estimate to Complete", 0)), min_value=0.0, format="%.2f")

    st.markdown("### 📦 Deliverables")
    key_deliverables = edit_list("Deliverable", "deliverables", deliverables_list)

    st.markdown("### 📋 Scope")
    scope = edit_list("Scope Item", "scope", scope_list)

    st.markdown("### 🏆 Benefits")
    benefits = edit_list("Benefit", "benefits", benefits_list)

    submitted = st.form_submit_button("💾 Save Project")

if submitted:
    # Validate form data
    validation_errors = validate_form_data(project_name, sponsor, start_date, finish_date, budget, spend, etc)
    
    if validation_errors:
        for error in validation_errors:
            st.error(f"❌ {error}")
    else:
        row_data = [
            project_name, sponsor, str(start_date), str(finish_date), timeframe,
            budget, spend, etc,
            key_deliverables, scope, benefits
        ]
        
        if save_row(row_data, edit_index):
            st.success("✅ Project updated!" if is_edit else "✅ Project saved!")
            # Clear form state and redirect to portfolio
            clear_form_state()
            st.session_state["nav_action"] = "portfolio"
            st.rerun()

# List management buttons
st.markdown("### ➕ Manage Lists")
col_d, col_s, col_b = st.columns(3)

if col_d.button("➕ Add Deliverable"):
    if "deliverables_items" not in st.session_state:
        st.session_state["deliverables_items"] = [""]
    st.session_state["deliverables_items"].append("")
    st.rerun()
    
if col_s.button("➕ Add Scope Item"):
    if "scope_items" not in st.session_state:
        st.session_state["scope_items"] = [""]
    st.session_state["scope_items"].append("")
    st.rerun()
    
if col_b.button("➕ Add Benefit"):
    if "benefits_items" not in st.session_state:
        st.session_state["benefits_items"] = [""]
    st.session_state["benefits_items"].append("")
    st.rerun()

# Show required fields note
st.caption("* Required fields")
```

# ––––––––––

# Dashboard View

# ––––––––––

def render_dashboard():
st.subheader(“📋 Project Portfolio”)

```
records = get_sheet_data()
if not records:
    st.info("No projects found. Add your first project to get started!")
    if st.button("➕ Add First Project"):
        st.session_state["nav_action"] = "add"
        st.rerun()
    return

df = pd.DataFrame(records)

# Add calculated columns for better display
df["Total Forecast"] = df.apply(lambda row: cast_to_float(row.get("Spend to Date", 0)) + cast_to_float(row.get("Estimate to Complete", 0)), axis=1)
df["Budget Variance"] = df.apply(lambda row: cast_to_float(row.get("Budget", 0)) - (cast_to_float(row.get("Spend to Date", 0)) + cast_to_float(row.get("Estimate to Complete", 0))), axis=1)

# Display summary metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Projects", len(df))
with col2:
    total_budget = df.apply(lambda row: cast_to_float(row.get("Budget", 0)), axis=1).sum()
    st.metric("Total Budget", f"${total_budget:,.0f}")
with col3:
    total_spend = df.apply(lambda row: cast_to_float(row.get("Spend to Date", 0)), axis=1).sum()
    st.metric("Total Spend", f"${total_spend:,.0f}")
with col4:
    total_variance = df["Budget Variance"].sum()
    st.metric("Total Variance", f"${total_variance:,.0f}")

# Filter and search
search = st.text_input("🔍 Search projects:", placeholder="Enter project name or sponsor...")
if search:
    mask = df["Project Name"].str.contains(search, case=False, na=False) | df["Sponsor"].str.contains(search, case=False, na=False)
    df = df[mask]

# Display table with key columns
display_cols = ["Project Name", "Sponsor", "Start Date", "Finish Date", "Budget", "Spend to Date", "Budget Variance"]
display_df = df[display_cols].copy()

# Format currency columns
for col in ["Budget", "Spend to Date", "Budget Variance"]:
    if col in display_df.columns:
        display_df[col] = display_df[col].apply(lambda x: f"${cast_to_float(x):,.0f}")

st.dataframe(display_df, use_container_width=True)

# Project details in expanders
for i, row in df.iterrows():
    project_name = row.get('Project Name', f'Project {i+1}')
    with st.expander(f"🔎 {project_name}"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Sponsor:** {row.get('Sponsor', 'N/A')}")
            st.write(f"**Timeframe:** {row.get('Timeframe / Phases', 'N/A')}")
            st.write(f"**Budget:** ${cast_to_float(row.get('Budget', 0)):,.0f}")
            st.write(f"**Spend:** ${cast_to_float(row.get('Spend to Date', 0)):,.0f}")
            st.write(f"**ETC:** ${cast_to_float(row.get('Estimate to Complete', 0)):,.0f}")
            st.write(f"**Variance:** ${row['Budget Variance']:,.0f}")
        
        with col2:
            if row.get('Key Deliverables'):
                st.write("**Key Deliverables:**")
                for deliverable in row['Key Deliverables'].split('\n'):
                    if deliverable.strip():
                        st.write(f"• {deliverable.strip()}")
            
            if row.get('Benefits'):
                st.write("**Benefits:**")
                for benefit in row['Benefits'].split('\n'):
                    if benefit.strip():
                        st.write(f"• {benefit.strip()}")
        
        if st.button(f"✏️ Edit '{project_name}'", key=f"edit_{i}"):
            st.session_state["edit_index"] = i
            st.session_state["nav_action"] = "edit"
            st.rerun()
```

# ––––––––––

# Reporting

# ––––––––––

def render_reports():
st.subheader(“📊 Reports”)

```
records = get_sheet_data()
if not records:
    st.warning("No data available for reporting.")
    return

df = pd.DataFrame(records)

# Ensure numeric columns are properly converted
numeric_cols = ["Budget", "Spend to Date", "Estimate to Complete"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = df[col].apply(cast_to_float)

report_type = st.selectbox("Choose report:", ["Budget vs Spend", "Benefits Overview", "Timeline Summary", "Budget Variance Analysis"])

if report_type == "Budget vs Spend":
    if all(col in df.columns for col in ["Project Name", "Budget", "Spend to Date"]):
        chart_data = df[["Project Name", "Budget", "Spend to Date"]].set_index("Project Name")
        st.bar_chart(chart_data)
        
        # Add summary table
        st.subheader("Budget Summary")
        summary_df = chart_data.copy()
        summary_df["Remaining"] = summary_df["Budget"] - summary_df["Spend to Date"]
        summary_df["% Spent"] = (summary_df["Spend to Date"] / summary_df["Budget"] * 100).round(1)
        st.dataframe(summary_df)
    else:
        st.error("Missing required columns for Budget vs Spend report.")

elif report_type == "Benefits Overview":
    if "Benefits" in df.columns:
        df["# Benefits"] = df["Benefits"].astype(str).apply(lambda x: len([b for b in x.split("\n") if b.strip()]))
        chart_data = df[["Project Name", "# Benefits"]].set_index("Project Name")
        st.bar_chart(chart_data)
    else:
        st.error("Missing 'Benefits' column.")

elif report_type == "Timeline Summary":
    if all(col in df.columns for col in ["Start Date", "Finish Date"]):
        df["Start Date"] = pd.to_datetime(df["Start Date"], errors='coerce')
        df["Finish Date"] = pd.to_datetime(df["Finish Date"], errors='coerce')
        df["Duration (Days)"] = (df["Finish Date"] - df["Start Date"]).dt.days
        
        timeline_df = df[["Project Name", "Start Date", "Finish Date", "Duration (Days)"]].sort_values("Start Date")
        st.dataframe(timeline_df, use_container_width=True)
    else:
        st.error("Missing date columns.")

elif report_type == "Budget Variance Analysis":
    if all(col in df.columns for col in ["Project Name", "Budget", "Spend to Date", "Estimate to Complete"]):
        df["Total Forecast"] = df["Spend to Date"] + df["Estimate to Complete"]
        df["Variance"] = df["Budget"] - df["Total Forecast"]
        df["Variance %"] = (df["Variance"] / df["Budget"] * 100).round(1)
        
        # Chart
        chart_data = df[["Project Name", "Budget", "Total Forecast"]].set_index("Project Name")
        st.bar_chart(chart_data)
        
        # Variance table
        st.subheader("Variance Analysis")
        variance_df = df[["Project Name", "Budget", "Total Forecast", "Variance", "Variance %"]]
        
        # Color code the variance
        def color_variance(val):
            if val < -10:
                return 'background-color: #ffcccc'  # Red for over budget
            elif val > 10:
                return 'background-color: #ccffcc'  # Green for under budget
            return ''
        
        styled_df = variance_df.style.applymap(color_variance, subset=['Variance %'])
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.error("Missing required columns for variance analysis.")
```

# ––––––––––

# App Router

# ––––––––––

# Handle edit index from dashboard

if “edit_index” in st.session_state and st.session_state.get(“nav_action”) == “edit”:
render_project_form(st.session_state.pop(“edit_index”))
st.session_state.pop(“nav_action”, None)

# Handle session state page navigation

elif “current_page” in st.session_state:
page = st.session_state[“current_page”]
if page == “add”:
render_project_form()
elif page == “portfolio”:
render_dashboard()
elif page == “reports”:
render_reports()
else:
render_home()

# Handle sidebar menu navigation

elif menu == “🏠 Home”:
clear_form_state()
render_home()
elif menu == “➕ Add Project”:
clear_form_state()
render_project_form()
elif menu == “📋 Portfolio”:
clear_form_state()
render_dashboard()
elif menu == “📊 Reports”:
clear_form_state()
render_reports()
else:
render_home()
