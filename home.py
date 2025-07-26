import streamlit as st
import pandas as pd
import sqlite3
import json
import altair as alt
from utils import load_df, validate_metrics

DB_PATH = "C:/Users/workd/Desktop/ga_maintenance/PdM/ga_maintenance.db"


# Function to load data from the database
def load_df(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Function to validate performance metrics
def validate_metrics(metrics_json):
    try:
        data = json.loads(metrics_json)
        required = ["precision", "recall", "accuracy", "f1_score"]
        for key in required:
            if key not in data:
                return False
        return True
    except:
        return False

# Set page config
st.set_page_config(page_title="General Aviation Predictive Maintenance Dashboard", layout="wide")

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Home", "Model Monitoring", "Predictive Maintenance Dashboard"])

# Load the data
components_df = load_df("""
    SELECT component_id, tail_number, name, condition, remaining_useful_life, last_health_score
    FROM components
""")

predictions_df = load_df("""
    SELECT * FROM component_predictions
    ORDER BY prediction_time DESC
""")

# Dark Mode Styling
dark_mode = st.sidebar.checkbox("🌙 Enable Dark Mode")
if dark_mode:
    background_gradient = "linear-gradient(135deg, #121212, #2c3e50)"
    card_bg = "#1e272e"
    text_color = "#f1f1f1"
    metric_bg = "#34495e"
    button_bg = "#2980b9"
else:
    background_gradient = "linear-gradient(135deg, #e8f0f8, #ffffff)"
    card_bg = "#ffffff"
    text_color = "#333333"
    metric_bg = "#00796b"
    button_bg = "#1565c0"

st.markdown(f"""
<style>
.stApp {{
    background: {background_gradient};
    font-family: 'Segoe UI', sans-serif;
    color: {text_color};
}}
.header-bar {{
    background: {metric_bg};
    padding: 15px;
    border-radius: 10px;
    color: white;
    font-size: 26px;
    font-weight: bold;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
}}
.card {{
    background: {card_bg};
    color: {text_color};
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    margin-bottom: 15px;
}}
</style>
""", unsafe_allow_html=True)

# Home Page
if page == "Home":
    st.markdown("<div class='header-bar'>General Aviation Predictive Maintenance Dashboard</div>", unsafe_allow_html=True)
    st.image("logo.png", width=200)
    st.write("Welcome to the **Predictive Maintenance Dashboard**!")
    st.write("Use the sidebar to navigate between different pages.")

# Model Monitoring Page
elif page == "Model Monitoring":
    st.markdown("<div class='header-bar'>Model Monitoring</div>", unsafe_allow_html=True)
    
    # Selector for components
    component_names = [f"{row['tail_number']} - {row['name']}" for _, row in components_df.iterrows()]
    component_map = {f"{row['tail_number']} - {row['name']}": row['component_id'] for _, row in components_df.iterrows()}
    selected_component = st.selectbox("Select Aircraft Component:", component_names)
    
    comp_id = component_map[selected_component]
    comp_data = components_df[components_df['component_id'] == comp_id].iloc[0]
    comp_preds = predictions_df[predictions_df['component_id'] == comp_id]
    
    # Display component information
    st.markdown(f"""
    <div class="card" style="background:#3b5998; color:white;">
    <h4 style="color:white; font-weight:700; margin-bottom:10px;">{selected_component}</h4>
    <b>Condition:</b> {comp_data['condition']}<br>
    <b>Remaining Useful Life:</b> {comp_data['remaining_useful_life']:.2f} hours<br>
    <b>Health Score:</b> {comp_data['last_health_score']}
    </div>
    """, unsafe_allow_html=True)

    # Alerts and charts (same as your existing code)
    # -- Add your code for critical alerts, charting, etc.

# Predictive Maintenance Dashboard Page
elif page == "Predictive Maintenance Dashboard":
    st.markdown("<div class='header-bar'>Predictive Maintenance Dashboard</div>", unsafe_allow_html=True)
    st.write("This is where you would display your predictive maintenance dashboard.")
    # Add your content here for the predictive maintenance dashboard.
