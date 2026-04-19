import streamlit as st
import pandas as pd
import time
import plotly.express as px
from datetime import datetime
from monitor import SystemMonitor
from brain import AIBrain
from remediate import ActionManager

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Autonomous Infrastructure Monitor",
    page_icon="📊",
    layout="wide"
)

# ──────────────────────────────────────────────
# Cached Resources
# ──────────────────────────────────────────────
@st.cache_resource
def get_monitor():
    return SystemMonitor()

monitor = get_monitor()

# ──────────────────────────────────────────────
# Session State Initialization
# ──────────────────────────────────────────────
if 'cpu_history' not in st.session_state:
    st.session_state.cpu_history = pd.DataFrame(columns=['Time', 'CPU %'])
if 'last_api_call_time' not in st.session_state:
    st.session_state.last_api_call_time = 0.0
if 'cached_diagnosis' not in st.session_state:
    st.session_state.cached_diagnosis = None
if 'last_analysis_result' not in st.session_state:
    st.session_state.last_analysis_result = None

# ──────────────────────────────────────────────
# Fetch Current Metrics
# ──────────────────────────────────────────────
metrics = monitor.get_system_metrics()

# Update CPU History (keep last 20 data points)
new_row = pd.DataFrame({
    'Time': [datetime.now().strftime("%H:%M:%S")],
    'CPU %': [metrics['cpu_usage_percent']]
})
st.session_state.cpu_history = pd.concat(
    [st.session_state.cpu_history, new_row], ignore_index=True
).tail(20)

# ──────────────────────────────────────────────
# Title & Sidebar
# ──────────────────────────────────────────────
st.title("🚀 Autonomous Infrastructure Agent — Phase 3")
st.subheader("Self-Healing Dashboard")
st.caption("Auto-refresh: 15s | Human-in-the-Loop enabled")

with st.sidebar:
    st.header("🧠 AI Brain Config")
    gemini_api_key = st.text_input(
        "Gemini API Key", type="password",
        help="Enter your Google Gemini API key to enable AI diagnostics."
    )
    brain = None
    if gemini_api_key:
        try:
            brain = AIBrain(api_key=gemini_api_key)
            st.success("AI Brain is ready ✅")
        except Exception as e:
            st.error(f"Invalid API Key: {e}")

# ──────────────────────────────────────────────
# Custom CSS
# ──────────────────────────────────────────────
st.markdown("""
    <style>
    .critical-alert {
        color: white;
        background-color: #ff4b4b;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        margin-bottom: 20px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Critical Alerts
# ──────────────────────────────────────────────
cpu = metrics['cpu_usage_percent']
mem = metrics['memory']['percent']

alerts = []
if cpu > 80:
    alerts.append(f"🔴 CRITICAL: High CPU Usage ({cpu}%)")
if mem > 90:
    alerts.append(f"🔴 CRITICAL: High Memory Usage ({mem}%)")

for alert in alerts:
    st.markdown(f'<div class="critical-alert">{alert}</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 🤖 AI Diagnosis (with 60s cooldown)
# ──────────────────────────────────────────────
if alerts and brain:
    cooldown = 60
    elapsed = time.time() - st.session_state.last_api_call_time

    if elapsed > cooldown:
        with st.spinner("🤖 AI Brain is analyzing..."):
            diagnosis = brain.analyze_health(
                cpu_usage=cpu,
                mem_usage=mem,
                top_processes=metrics['top_processes']
            )
        st.session_state.cached_diagnosis = diagnosis
        st.session_state.last_analysis_result = diagnosis
        st.session_state.last_api_call_time = time.time()
    else:
        diagnosis = st.session_state.cached_diagnosis

    if diagnosis:
        st.error(f"🤖 **Agent Diagnosis**\n\n{diagnosis.get('diagnosis', '')}")
        remaining = int(cooldown - (time.time() - st.session_state.last_api_call_time))
        if remaining > 0:
            st.caption(f"⏳ Analysis cached (next update in {remaining}s)")

        # ──────────────────────────────────────────────
        # 🛡️ Human-in-the-Loop Remediation
        # ──────────────────────────────────────────────
        target_pid = diagnosis.get('recommended_action', {}).get('target_pid')
        if target_pid is not None:
            st.warning(f"🎯 AI recommends terminating **PID {target_pid}**")
            if st.button(f"⚠️ Approve Termination of PID {target_pid}"):
                action_mgr = ActionManager()
                result = action_mgr.kill_process(target_pid)

                if "✅" in result:
                    st.success(result)
                elif "🔒" in result:
                    st.error(result)
                else:
                    st.warning(result)

                st.toast(result, icon="🛡️")

                # Reset state so the system immediately re-verifies
                st.session_state.last_analysis_result = None
                st.session_state.cached_diagnosis = None
                st.session_state.last_api_call_time = 0.0
                time.sleep(2)  # Brief pause before re-check
                st.rerun()

# ──────────────────────────────────────────────
# Metrics Overview
# ──────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("CPU Usage", f"{cpu}%")
with col2:
    st.metric("Memory Usage", f"{mem}%", f"{metrics['memory']['used_gb']} GB Used")
with col3:
    st.metric("Disk Usage", f"{metrics['disk_usage_percent']}%")

# ──────────────────────────────────────────────
# Charts & Processes
# ──────────────────────────────────────────────
chart_col, proc_col = st.columns([2, 1])

with chart_col:
    st.write("### CPU Usage History")
    fig = px.line(
        st.session_state.cpu_history, x='Time', y='CPU %',
        title='CPU Load Over Time'
    )
    fig.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

with proc_col:
    st.write("### Top 3 Processes")
    top_procs_df = pd.DataFrame(metrics['top_processes'])
    if not top_procs_df.empty:
        st.table(top_procs_df)
    else:
        st.write("Fetching process data...")

# ──────────────────────────────────────────────
# Auto-Refresh (no while loop)
# ──────────────────────────────────────────────
time.sleep(15)
st.rerun()
