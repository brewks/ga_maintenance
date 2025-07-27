import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import time
import os

# === CONFIG ===
DB_PATH = "ga_maintenance.db"

# === FUNCTIONS ===
def load_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def plot_rul_bar(df):
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=df, x=df['component_id'].astype(str), y='predicted_value', ax=ax, palette='Blues')
    ax.set_xlabel("Component ID")
    ax.set_ylabel("Predicted RUL (hours)")
    ax.set_title("Latest Component RUL Predictions")
    plt.xticks(rotation=45)
    st.pyplot(fig)

def plot_confidence_rul(df):
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(data=df, x='component_id', y='predicted_value', size='confidence', hue='confidence', palette='coolwarm', ax=ax, sizes=(50, 300))
    ax.set_title("RUL vs Component ID (Size = Confidence)")
    plt.xticks(rotation=45)
    st.pyplot(fig)

def plot_rul_trend(df):
    if 'prediction_time' in df.columns:
        df['prediction_time'] = pd.to_datetime(df['prediction_time'], errors='coerce')
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=df, x='prediction_time', y='predicted_value', hue='component_id', marker="o", ax=ax)
        ax.set_title("RUL Predictions Over Time")
        plt.xticks(rotation=45)
        st.pyplot(fig)

# === APP LAYOUT ===
st.set_page_config(page_title="GA PdM Dashboard", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f2f6fc; }
    .dashboard-header {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 10px;
    }
    .dashboard-title {
        font-size: 28px;
        font-weight: bold;
        color: #003366;
    }
    .big-font {
        font-size: 18px !important;
        color: #003366;
    }
</style>
""", unsafe_allow_html=True)

# === HEADER: LOGO + TITLE INLINE ===
col1, col2 = st.columns([1, 5])

with col1:
    st.image("logo.png", width=50)  # logo.png is in the same directory as app.py

with col2:
    st.markdown(
        "<h1 style='color:#003366; margin-bottom: 0;'>General Aviation Predictive Maintenance Dashboard</h1>"
        "<p style='color:#005580; font-size: 16px;'>Live aircraft system health, predictive maintenance insights, and alerts</p>",
        unsafe_allow_html=True
    )

# === SIDEBAR CONTROLS ===
refresh_interval = st.sidebar.slider("Auto-refresh (seconds)", 0, 60, 10)

view_choice = st.sidebar.radio(
    "Select View",
    ["Components Needing Attention", "Dashboard Snapshot", "Latest Predictions", "Engine Health Overview"]
)

# === LOAD DATA ===
if view_choice == "Components Needing Attention":
    df = load_data("SELECT * FROM components_needing_attention;")
elif view_choice == "Dashboard Snapshot":
    df = load_data("SELECT * FROM dashboard_snapshot_view;")
elif view_choice == "Engine Health Overview":
    df = load_data("SELECT * FROM engine_health_view;")
else:
    df = load_data("SELECT * FROM component_predictions ORDER BY prediction_time DESC LIMIT 100;")

# === DISPLAY DATA ===
st.subheader(view_choice)
st.write(f"### Data Summary: {len(df)} records loaded")
st.dataframe(df)

if df.empty:
    st.warning("⚠ No data available for this view.")
else:
    if view_choice == "Latest Predictions":
        st.write("### Predicted Remaining Useful Life (RUL)")
        plot_rul_bar(df)

        st.write("### RUL vs Component ID with Confidence")
        plot_confidence_rul(df)

        st.write("### RUL Prediction Trends")
        plot_rul_trend(df)

    if "confidence" in df.columns and "prediction_type" in df.columns:
        critical_alerts = df[(df["confidence"] > 0.9) & (df["prediction_type"] == "failure")]
        if not critical_alerts.empty:
            st.error(f"🚨 {len(critical_alerts)} CRITICAL failure predictions detected!")

    if "confidence" in df.columns:
        conf_level = st.slider("Minimum Confidence", 0.0, 1.0, 0.7)
        filtered_df = df[df['confidence'] >= conf_level]
        st.write(f"### Filtered Predictions (Confidence ≥ {conf_level})")
        st.dataframe(filtered_df)

        if not filtered_df.empty:
            st.download_button(
                "Download Filtered Data",
                filtered_df.to_csv(index=False).encode(),
                file_name="filtered_predictions.csv",
                mime="text/csv"
            )

# === AUTO-REFRESH ===
if refresh_interval > 0:
    st.info(f"⏳ Auto-refreshing every {refresh_interval} seconds...")
    time.sleep(refresh_interval)
    st.experimental_rerun()


