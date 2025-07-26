import streamlit as st
import pandas as pd
import sqlite3
import json
import altair as alt

DB_PATH = "C:/Users/workd/Desktop/ga_maintenance/PdM/ga_maintenance.db"


def load_df(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

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

# === LOAD DATA ===
components_df = load_df("""
    SELECT component_id, tail_number, name, condition, remaining_useful_life, last_health_score
    FROM components
""")

predictions_df = load_df("""
    SELECT * FROM component_predictions
    ORDER BY prediction_time DESC
""")

# === DARK MODE ===
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
.metric-card {{
    background: {metric_bg};
    padding: 12px;
    border-radius: 10px;
    color: #ffffff;
    text-align: center;
    box-shadow: 0 6px 15px rgba(0,0,0,0.3);
}}
.stButton > button {{
    background-color: {button_bg};
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 5px;
    padding: 6px 12px;
}}
.stButton > button:hover {{
    background-color: #004d99;
}}
textarea.stTextArea textarea {{
    background-color: {"#2c3e50" if dark_mode else "#ffffff"};
    color: {"#f1f1f1" if dark_mode else "#333333"};
    border: 1px solid #888;
    border-radius: 5px;
    font-size: 14px;
}}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-bar">General Aviation Predictive Maintenance Dashboard</div>', unsafe_allow_html=True)

# === SELECTOR ===
component_names = [f"{row['tail_number']} - {row['name']}" for _, row in components_df.iterrows()]
component_map = {f"{row['tail_number']} - {row['name']}": row['component_id'] for _, row in components_df.iterrows()}
selected_component = st.selectbox("Select Aircraft Component:", component_names)

comp_id = component_map[selected_component]
comp_data = components_df[components_df['component_id'] == comp_id].iloc[0]
comp_preds = predictions_df[predictions_df['component_id'] == comp_id]

# === LAYOUT ===
col1, col2 = st.columns([2,1])

with col1:
    st.markdown(f"""
    <div class="card" style=background:#3b5998; color:white;">
    <h4 style="color:white; font-weight:700; margin-bottom:10px;">{selected_component}</h4>
    <b>Condition:</b> {comp_data['condition']}<br>
    <b>Remaining Useful Life:</b> {comp_data['remaining_useful_life']:.2f} hours<br>
    <b>Health Score:</b> {comp_data['last_health_score']}
    </div>
    """, unsafe_allow_html=True)

    crit = comp_preds[(comp_preds['prediction_type'] == 'failure') & (comp_preds['confidence'] > 0.9)]
    if not crit.empty:
        row = crit.iloc[0]
        st.markdown(f"""
        <div class="card" style="background:#e53935; color:white;">
        <b>⚠ Critical Alert</b><br>
        Predicted Failure: {row['time_horizon']}<br>
        Confidence: {row['confidence']*100:.1f}%<br>
        Explanation: {row['explanation']}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="card" style="background:#43a047; color:white;">
        <b>No Critical Alerts</b>
        </div>
        """, unsafe_allow_html=True)

    # Altair chart
    if not comp_preds.empty:
        alt_data = comp_preds[comp_preds['prediction_type'] == 'remaining_life']
        if not alt_data.empty:
            alt_data['prediction_time'] = pd.to_datetime(alt_data['prediction_time'])
            chart = alt.Chart(alt_data).mark_line(point=True).encode(
                x=alt.X('prediction_time:T', title='Prediction Time'),
                y=alt.Y('predicted_value:Q', title='Remaining Useful Life (hrs)'),
                tooltip=['prediction_time:T', 'predicted_value', 'confidence']
            ).properties(
                title="Remaining Useful Life Over Time",
                width=600,
                height=300
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No remaining life predictions available for Altair chart.")

with col2:
    avg_conf = comp_preds['confidence'].mean() * 100 if not comp_preds.empty else 0
    crit_count = crit.shape[0]
    avg_rul = comp_data['remaining_useful_life']

    st.markdown(f"""
    <div class="metric-card">
    <b>Avg Confidence</b><br>
    <span style="font-size:22px;">{avg_conf:.1f}%</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metric-card" style="background:#c62828;">
    <b>Critical Failures</b><br>
    <span style="font-size:22px;">{crit_count}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metric-card" style="background:#1565c0;">
    <b>Remaining Useful Life</b><br>
    <span style="font-size:22px;">{avg_rul:.2f}h</span>
    </div>
    """, unsafe_allow_html=True)

    # Performance metrics
    if not comp_preds.empty:
        selected_model_id = comp_preds['model_id'].iloc[0]
        metrics_df = load_df(f"""
            SELECT performance_metrics FROM predictive_models
            WHERE model_id = {selected_model_id}
        """)
        if not metrics_df.empty and metrics_df['performance_metrics'].iloc[0]:
            metrics_json = metrics_df['performance_metrics'].iloc[0]
            if validate_metrics(metrics_json):
                metrics = json.loads(metrics_json)
                precision = f"{metrics.get('precision', 0) * 100:.1f}%"
                recall = f"{metrics.get('recall', 0) * 100:.1f}%"
                accuracy = f"{metrics.get('accuracy', 0) * 100:.1f}%"
                f1_score = f"{metrics.get('f1_score', 0) * 100:.1f}%"
            else:
                precision = recall = accuracy = f1_score = "N/A"
                st.warning("⚠ Invalid performance metrics.")
        else:
            precision = recall = accuracy = f1_score = "N/A"

        st.markdown(f"""
        <div class="card" style="background:{metric_bg}; color:white;">
        <b>Model Performance</b><br>
        Precision: {precision} | Recall: {recall} | Accuracy: {accuracy} | F1: {f1_score}
        </div>
        """, unsafe_allow_html=True)

# === JSON validator ===
st.markdown("---")
st.markdown(f"""
<div class="card">
<h4 style="margin-bottom:10px;">Test Performance Metrics JSON</h4>
</div>
""", unsafe_allow_html=True)

input_metrics = st.text_area("Enter Performance Metrics JSON:", height=150)

if st.button("Validate JSON"):
    if validate_metrics(input_metrics):
        st.success("✅ Valid performance metrics JSON!")
    else:
        st.error("❌ Invalid or missing required fields (precision, recall, accuracy, f1_score).")