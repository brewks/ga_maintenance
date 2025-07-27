import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# === CONFIG ===
DB_PATH = "ga_maintenance.db"

# === PAGE SETUP ===
st.set_page_config(page_title="GA Predictive Maintenance", layout="wide")

# === CUSTOM STYLING ===
st.markdown("""
<style>
    .stApp {
        background-color: #e6f2f5; /* Light teal-blue */
    }
    .dashboard-header {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 10px;
    }
    .dashboard-title {
        font-size: 28px;
        font-weight: bold;
        color: #002244;
    }
    .big-font {
        font-size: 18px !important;
        color: #002244;
    }
    .stDataFrame, .stTable {
        background-color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# === HEADER: LOGO + TITLE ===
col1, col2 = st.columns([1, 10])
with col1:
    st.image("logo.png", width=80)
with col2:
    st.markdown('<div class="dashboard-title">General Aviation Predictive Maintenance Dashboard</div>', unsafe_allow_html=True)

st.markdown('<p class="big-font">Live aircraft system health, predictive maintenance insights, and alerts</p>', unsafe_allow_html=True)

# === DATA LOADING FUNCTION ===
def load_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# === SIDEBAR FILTERS ===
st.sidebar.title("Controls")
selected_option = st.sidebar.radio("Choose a View", ("Sensor Trends", "RUL Insights", "Alerts"))

# === SENSOR TRENDS VIEW ===
if selected_option == "Sensor Trends":
    st.subheader("Sensor Data Trends")

    df = load_data("SELECT * FROM sensor_data")
    
    sensor = st.selectbox("Select Sensor", df.columns[2:])  # skip id and timestamp

    fig, ax = plt.subplots()
    sns.lineplot(data=df, x='timestamp', y=sensor, ax=ax)
    ax.set_title(f"{sensor} Over Time")
    st.pyplot(fig)

# === RUL INSIGHTS VIEW ===
elif selected_option == "RUL Insights":
    st.subheader("Remaining Useful Life (RUL) Distribution")

    df = load_data("SELECT * FROM rul_predictions")

    fig, ax = plt.subplots()
    sns.histplot(data=df, x='RUL', bins=30, kde=True, color="teal")
    ax.set_title("RUL Histogram")
    st.pyplot(fig)

    st.dataframe(df)

# === ALERTS VIEW ===
else:
    st.subheader("Maintenance Alerts")

    df = load_data("SELECT * FROM alerts")

    st.dataframe(df)
