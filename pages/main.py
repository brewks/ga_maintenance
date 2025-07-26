import streamlit as st
import json
from utils import load_df, validate_metrics

# === DARK MODE ===
dark_mode = st.sidebar.checkbox("\U0001F319 Enable Dark Mode")

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
.metric-card {{
    background: {metric_bg};
    padding: 12px;
    border-radius: 10px;
    color: #ffffff;
    text-align: center;
    box-shadow: 0 6px 15px rgba(0,0,0,0.3);
}}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-bar">Model Monitoring Dashboard</div>', unsafe_allow_html=True)

# === LOAD PREDICTIVE MODELS ===
models_df = load_df("""
    SELECT model_id, model_name, version, created_at, performance_metrics
    FROM predictive_models
    ORDER BY created_at DESC
""")

if models_df.empty:
    st.warning("No predictive models found.")
else:
    for _, row in models_df.iterrows():
        metrics_raw = row['performance_metrics']
        metrics_valid = validate_metrics(metrics_raw)
        metrics = json.loads(metrics_raw) if metrics_valid else {}

        precision = f"{metrics.get('precision', 0) * 100:.1f}%" if metrics_valid else "N/A"
        recall = f"{metrics.get('recall', 0) * 100:.1f}%" if metrics_valid else "N/A"
        accuracy = f"{metrics.get('accuracy', 0) * 100:.1f}%" if metrics_valid else "N/A"
        f1 = f"{metrics.get('f1_score', 0) * 100:.1f}%" if metrics_valid else "N/A"

        st.markdown(f"""
        <div class="card">
        <b>{row['model_name']} (v{row['version']})</b><br>
        <i>Created at:</i> {row['created_at']}<br><br>
        <b>Performance:</b><br>
        Precision: {precision} | Recall: {recall} | Accuracy: {accuracy} | F1 Score: {f1}
        </div>
        """, unsafe_allow_html=True)

# === JSON Validator ===
st.markdown("---")
st.subheader("\U0001F4DD Validate Custom Model Metrics JSON")
input_metrics = st.text_area("Enter JSON:", height=150)

if st.button("Validate"):
    if validate_metrics(input_metrics):
        st.success("✅ Valid performance metrics JSON!")
    else:
        st.error("❌ Invalid or missing required fields: precision, recall, accuracy, f1_score.")
