# Stratigo - Project Portfolio App
# Version: 1.0

import pandas as pd
import random
from faker import Faker
from datetime import timedelta
import streamlit as st

# Initialise Faker
fake = Faker()

# Generate 25 sample project records
def generate_projects(n=25):
    statuses = ["On Track", "At Risk", "Delayed", "Completed"]
    phases = ["Initiation", "Planning", "Execution", "Closure"]
    data = []

    for _ in range(n):
        start = fake.date_between(start_date='-1y', end_date='today')
        end = start + timedelta(days=random.randint(90, 360))
        budget = round(random.uniform(100000, 1000000), 2)
        spend = round(budget * random.uniform(0.3, 0.95), 2)
        benefit = round(random.uniform(50000, 2000000), 2)
        data.append({
            "Project Name": fake.bs().title(),
            "Status": random.choice(statuses),
            "Phase": random.choice(phases),
            "Start Date": start,
            "End Date": end,
            "Budget (NZD)": budget,
            "Spend to Date (NZD)": spend,
            "Forecast Benefit (NZD)": benefit
        })
    return pd.DataFrame(data)

# Create dataset in memory
project_df = generate_projects()

# App config
st.set_page_config("Stratigo", layout="wide")
st.title("📘 Stratigo – Project Portfolio Manager")

# Navigation Tabs
tabs = st.tabs(["🏠 Dashboard", "📁 Projects", "💰 Financials", "🧩 CRAID Register"])

with tabs[0]:
    st.header("Dashboard")
    st.metric("Total Budget", f"${project_df['Budget (NZD)'].sum():,.0f}")
    st.metric("Total Spend", f"${project_df['Spend to Date (NZD)'].sum():,.0f}")
    st.metric("Forecast Benefit", f"${project_df['Forecast Benefit (NZD)'].sum():,.0f}")
    st.bar_chart(project_df.groupby("Status")["Budget (NZD)"].sum())

with tabs[1]:
    st.header("Projects")
    st.dataframe(project_df)

with tabs[2]:
    st.header("Financial Overview")
    st.dataframe(project_df[["Project Name", "Budget (NZD)", "Spend to Date (NZD)", "Forecast Benefit (NZD)"]])

with tabs[3]:
    st.header("CRAID Register")
    st.info("This section will include entries for Constraints, Risks, Assumptions, Issues, and Dependencies in future releases.")
