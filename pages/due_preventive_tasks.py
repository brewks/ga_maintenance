import streamlit as st
import pandas as pd
import sqlite3

DB_PATH = "C:\\Users\\workd\\Desktop\\ga_maintenance\\ga_maintenance.db"

st.title("🛠 Due Preventive Maintenance Tasks (FAA-Aligned)")

# Load data from the view
@st.cache_data
def load_due_tasks():
    with sqlite3.connect(DB_PATH) as conn:
        query = """
        SELECT * FROM due_preventive_tasks
        ORDER BY timestamp DESC
        """
        return pd.read_sql_query(query, conn)

# Display section
tasks_df = load_due_tasks()

if tasks_df.empty:
    st.info("✅ No pending preventive maintenance tasks at this time.")
else:
    st.write(f"### 🔧 {len(tasks_df)} Task(s) Requiring Attention")
    st.dataframe(tasks_df)

    # Optional filtering by system or aircraft
    st.sidebar.subheader("🔍 Filter Tasks")
    systems = ["All"] + sorted(tasks_df['system'].dropna().unique().tolist())
    selected_system = st.sidebar.selectbox("System", systems)

    tails = ["All"] + sorted(tasks_df['tail_number'].dropna().unique().tolist())
    selected_tail = st.sidebar.selectbox("Tail Number", tails)

    if selected_system != "All":
        tasks_df = tasks_df[tasks_df['system'] == selected_system]
    if selected_tail != "All":
        tasks_df = tasks_df[tasks_df['tail_number'] == selected_tail]

    st.write("### Filtered View")
    st.dataframe(tasks_df)

    # Optional download
    st.download_button(
        label="📥 Download CSV",
        data=tasks_df.to_csv(index=False).encode(),
        file_name="due_preventive_tasks.csv",
        mime="text/csv"
    )