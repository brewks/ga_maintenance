import streamlit as st
import pandas as pd
import json
from utils import load_df, validate_metrics

st.set_page_config(page_title="Model Monitoring", layout="wide")

# === STYLING ===
dark_mode = st.sidebar.checkbox("🌙 Enable Dark Mode")

if dark_mode:
    background = "linear-gradient(135deg, #121212, #2c3e50)"
    text_color = "#f1f1f1"
    card_color = "#1e272e"
else:
    background = "linear-gradient(135deg, #e8f0f8, #ffffff)"
    text_color = "#333333"
    card_color = "#ffffff"

st.markdown(f"""
<style>
.stApp {{
    background: {background};
    color: {text_color};
    font-family: 'Segoe UI', sans-serif;
}}
.card {{
    background: {card_color};
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    margin-bottom: 20px;
}}
</style>
""", unsafe_allow_html=True)

# === TITLE ===
st.markdown("<div class='card'><h2>📊 Predictive Model Monitoring Dashboard</h2></div>", unsafe_allow_html=True)

# === LOAD DATA ===
model_df = load_df("SELECT model_id, model_name, model_type AS algorithm, performance_metrics FROM predictive_models ORDER BY model_id DESC")

# === DISPLAY MODEL TABLE ===
st.subheader("Available Models")
st.dataframe(model_df[["model_id", "model_name", "algorithm"]])

# === METRIC EXPLORATION ===
selected_model = st.selectbox("Select Model to View Metrics", model_df["model_id"])
metrics_json = model_df[model_df["model_id"] == selected_model]["performance_metrics"].values[0]

st.subheader(f"Performance Metrics for Model ID {selected_model}")

if validate_metrics(metrics_json):
    metrics = json.loads(metrics_json)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Precision", f"{metrics['precision'] * 100:.1f}%")
    col2.metric("Recall", f"{metrics['recall'] * 100:.1f}%")
    col3.metric("Accuracy", f"{metrics['accuracy'] * 100:.1f}%")
    col4.metric("F1 Score", f"{metrics['f1_score'] * 100:.1f}%")

    st.download_button(
        label="📥 Download Metrics as JSON",
        data=json.dumps(metrics, indent=2),
        file_name=f"model_{selected_model}_metrics.json",
        mime="application/json"
    )
else:
    st.error("Invalid or missing metric fields in database JSON.")

# === JSON VALIDATOR ===
st.markdown("---")
st.markdown("<div class='card'><h4>🧪 Test Your Own Metrics JSON</h4></div>", unsafe_allow_html=True)

user_json = st.text_area("Paste JSON:", height=150)
if st.button("Validate JSON"):
    if validate_metrics(user_json):
        st.success("✅ Valid performance metrics JSON!")
    else:
        st.error("❌ Invalid or missing required fields (precision, recall, accuracy, f1_score).")
