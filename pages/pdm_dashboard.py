import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# === CONFIG ===
DB_PATH = "ga_maintenance.db"

# === LIGHT THEME STYLING ===
st.markdown("""
<style>
    .stApp {
        background-color: #f2f4f7;
        color: #1c1c1c;
        font-family: "Segoe UI", sans-serif;
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
        color: #003366;
    }

    .big-font {
        font-size: 18px !important;
        color: #333333;
    }

    section[data-testid="stSidebar"] {
        background-color: #e0e6ed !important;
        color: #1c1c1c !important;
    }

    label, .css-16idsys p, .css-1cpxqw2, .css-17eq0hr {
        color: #1c1c1c !important;
        font-size: 16px;
    }

    .stButton>button {
        background-color: #3366cc;
        color: white;
        border-radius: 8px;
    }

    .stButton>button:hover {
        background-color: #5a8dee;
    }

    h1, h2, h3, h4 {
        color: #003366 !important;
    }
</style>
""", unsafe_allow_html=True)

# === HEADER SECTION ===
col1, col2 = st.columns([1, 6])
with col1:
    st.image("logo.png", width=70)
with col2:
    st.markdown("### General Aviation Predictive Maintenance Dashboard")

st.markdown('<p class="big-font">Live aircraft system health, predictive maintenance insights, and alerts</p>', unsafe_allow_html=True)

# === FUNCTIONS ===
def load_data(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def plot_rul_bar(df):
    plt.style.use("seaborn-whitegrid")
    plt.figure(figsize=(10, 5))
    sns.barplot(x='component', y='rul_days', data=df, palette='Blues_d')
    plt.title('Remaining Useful Life (RUL) by Component')
    plt.xticks(rotation=45)
    plt.xlabel("Component")
    plt.ylabel("Remaining Useful Life (Days)")
    st.pyplot(plt)

# === MAIN DASHBOARD ===
query = "SELECT * FROM sensor_data LIMIT 100"
df = load_data(query)

option = st.radio("Choose a view:", ["Raw Data", "RUL Chart"])

if option == "Raw Data":
    st.dataframe(df)
elif option == "RUL Chart":
    plot_rul_bar(df)
