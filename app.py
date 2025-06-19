# app.py
# Stratigo Version 1.0

import streamlit as st
import pandas as pd
import random
import numpy as np
from faker import Faker
import matplotlib.pyplot as plt
import seaborn as sns

# Setup
fake = Faker()
st.set_page_config(page_title="Stratigo", layout="wide")
sns.set(style="whitegrid")

# --- Sample Data Generation ---
@st.cache_data
def generate_project_data(n=50):
    phases = ['Initiation', 'Planning', 'Execution', 'Monitoring', 'Closure']
    statuses = ['On Track', 'At Risk', 'Delayed', 'Completed']
    return pd.DataFrame([{
        'Project ID': f"PJT-{i+1:03d}",
        'Project Name': fake.bs().title(),
        'Status': random.choice(statuses),
        'Phase': random.choice(phases),
        'Planned Budget ($k)': round(random.uniform(100, 1500), 2),
        'Actual Cost ($k)': round(random.uniform(50, 1600), 2),
        'Project Owner': fake.name(),
        'Expected Benefits ($k)': round(random.uniform(100, 3000), 2),
    } for i in range(n)])

@st.cache_data
def generate_craid_data(project_ids, n=200):
    types = ['Constraint', 'Risk', 'Assumption', 'Issue', 'Dependency']
    severities = ['Low', 'Medium', 'High', 'Critical']
    return pd.DataFrame([{
        'CRAID ID': fake.uuid4(),
        'Project ID': random.choice(project_ids),
        'Type': random.choice(types),
        'Description': fake.sentence(nb_words=10),
        'Severity': random.choice(severities),
        'Owner': fake.name()
    } for _ in range(n)])

projects = generate_project_data()
craids = generate_craid_data(projects['Project ID'].tolist())

# --- Pages ---
def dashboard():
    st.title("📊 Project Portfolio Dashboard")
    st.dataframe(projects)

    st.subheader("📈 Financial Scatterplot")
    fig, ax = plt.subplots()
    sns.scatterplot(data=projects, x='Planned Budget ($k)', y='Actual Cost ($k)', hue='Status', ax=ax)
    st.pyplot(fig)

    st.subheader("🧩 Projects by Phase")
    st.bar_chart(projects['Phase'].value_counts())

def craid_register():
    st.title("🧾 CRAID Register")
    st.dataframe(craids)

    st.subheader("🔍 CRAID by Type and Severity")
    summary = craids.groupby(['Type', 'Severity']).size().unstack(fill_value=0)
    st.dataframe(summary)

    st.subheader("📊 CRAID Distribution")
    st.bar_chart(craids['Type'].value_counts())

def financials():
    st.title("💰 Financial Overview")
    df = projects.copy()
    df['Variance ($k)'] = df['Planned Budget ($k)'] - df['Actual Cost ($k)']
    st.dataframe(df[['Project ID', 'Project Name', 'Planned Budget ($k)', 'Actual Cost ($k)', 'Variance ($k)', 'Expected Benefits ($k)']])

    st.subheader("📉 Budget Variance Histogram")
    fig, ax = plt.subplots()
    sns.histplot(df['Variance ($k)'], bins=20, kde=True, ax=ax)
    st.pyplot(fig)

# --- Navigation ---
tab = st.sidebar.radio("🔍 Navigate", ["🏠 Dashboard", "📌 CRAID Register", "💼 Financials"])

if tab == "🏠 Dashboard":
    dashboard()
elif tab == "📌 CRAID Register":
    craid_register()
elif tab == "💼 Financials":
    financials()
