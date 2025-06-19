# app.py - Stratigo v1.0

import streamlit as st
import pandas as pd
import numpy as np
import random
import datetime
import matplotlib.pyplot as plt

# ----- Setup -----
st.set_page_config(page_title="Stratigo", layout="wide")
st.title("📊 Stratigo: Project Portfolio Manager")

# ----- Example Data -----
@st.cache_data
def load_data():
    statuses = ["On Track", "At Risk", "Delayed", "Complete"]
    phases = ["Initiation", "Planning", "Execution", "Closure"]
    categories = ["IT", "Business", "Operations", "Marketing"]
    pm_names = ["Alice", "Bob", "Charlie", "Diana", "Ethan"]
    
    data = []
    for i in range(25):
        start = datetime.date(2024, random.randint(1, 12), random.randint(1, 28))
        end = start + datetime.timedelta(days=random.randint(90, 365))
        budget = random.randint(100000, 500000)
        actual = budget * random.uniform(0.7, 1.2)
        craid_count = random.randint(1, 10)
        data.append({
            "Project Name": f"Project {chr(65+i)}",
            "Project Manager": random.choice(pm_names),
            "Status": random.choice(statuses),
            "Phase": random.choice(phases),
            "Category": random.choice(categories),
            "Start Date": start,
            "End Date": end,
            "Budget ($)": round(budget, 2),
            "Actual Spend ($)": round(actual, 2),
            "CRAID Count": craid_count
        })
    return pd.DataFrame(data)

df = load_data()

# ----- Navigation -----
menu = st.sidebar.radio("Navigation", [
    "🏠 Overview Dashboard",
    "📈 Financials",
    "⚠️ CRAID Register",
    "📋 Project Table"
])

# ----- Pages -----
if menu == "🏠 Overview Dashboard":
    st.subheader("Portfolio Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("📁 Total Projects", len(df))
    col2.metric("💰 Total Budget", f"${df['Budget ($)'].sum():,.0f}")
    col3.metric("⚠️ CRAID Items", df['CRAID Count'].sum())

    st.markdown("### 📊 Status Breakdown")
    status_counts = df["Status"].value_counts()
    fig, ax = plt.subplots()
    ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

elif menu == "📈 Financials":
    st.subheader("Budget vs Actual Spend")
    df["Variance ($)"] = df["Budget ($)"] - df["Actual Spend ($)"]
    st.dataframe(df[["Project Name", "Budget ($)", "Actual Spend ($)", "Variance ($)"]])
    
    st.markdown("### 📊 Budget vs Actual Chart")
    st.bar_chart(df.set_index("Project Name")[["Budget ($)", "Actual Spend ($)"]])

elif menu == "⚠️ CRAID Register":
    st.subheader("CRAID Register (Summary)")
    st.dataframe(df[["Project Name", "Project Manager", "Status", "CRAID Count"]])
    
    st.markdown("### CRAID Heatmap")
    heatmap = df.pivot_table(index="Project Manager", values="CRAID Count", aggfunc="sum")
    st.bar_chart(heatmap)

elif menu == "📋 Project Table":
    st.subheader("All Projects")
    st.dataframe(df)
