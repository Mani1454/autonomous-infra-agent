import streamlit as st
import pandas as pd
import time
import re
import os
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
st.title("🚀 Autonomous Infrastructure Agent")
st.subheader("Verification & Audit Dashboard")
st.caption("Auto-refresh: 15s | Human-in-the-Loop enabled")

st.info(
    "ℹ️ **Hosted Demo**: Metrics shown reflect the **cloud server** running this app. "
    "Enter a Gemini API key in the sidebar to activate live AI diagnostics.",
    icon="☁️"
)


with st.sidebar:
    st.header("🧠 AI Brain Config")
    st.markdown(
        "Get a **free** Gemini API key → "
        "[Google AI Studio](https://aistudio.google.com/app/apikey)",
        unsafe_allow_html=False
    )
    gemini_api_key = st.text_input(
        "Gemini API Key", type="password",
        help="Enter your Google Gemini API key to enable AI diagnostics. Get one free at aistudio.google.com"
    )
    brain = None
    if gemini_api_key:
        try:
            brain = AIBrain(api_key=gemini_api_key)
            st.success("AI Brain is ready ✅")
        except Exception as e:
            st.error(f"Invalid API Key: {e}")

    st.divider()
    autonomous_mode = st.toggle(
        "🤖 Fully Autonomous Mode", value=False,
        help="If enabled, the AI will automatically terminate rogue processes without human approval."
    )
    if autonomous_mode:
        st.warning("⚡ Autonomous mode is ACTIVE. Rogue processes will be terminated automatically.")

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
# Audit Log Helper
# ──────────────────────────────────────────────
AUDIT_LOG_PATH = os.path.join(os.path.dirname(__file__), "audit.log")


def load_audit_log() -> pd.DataFrame:
    """
    Reads and parses the audit.log file into a Pandas DataFrame.

    Each line is expected to follow the format:
      [YYYY-MM-DD HH:MM:SS] ACTION=<action> | PID=<pid> | STATUS=<status>

    Returns:
        A DataFrame with columns: Timestamp, Action, PID, Status.
    """
    if not os.path.exists(AUDIT_LOG_PATH):
        return pd.DataFrame(columns=["Timestamp", "Action", "PID", "Status"])

    pattern = re.compile(
        r"\[(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]\s*"
        r"ACTION=(?P<action>[^|]+?)\s*\|\s*"
        r"PID=(?P<pid>[^|]+?)\s*\|\s*"
        r"STATUS=(?P<status>.+)"
    )

    records = []
    try:
        with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                match = pattern.match(line)
                if match:
                    records.append(match.groupdict())
    except Exception:
        return pd.DataFrame(columns=["Timestamp", "Action", "PID", "Status"])

    if not records:
        return pd.DataFrame(columns=["Timestamp", "Action", "PID", "Status"])

    df = pd.DataFrame(records)
    df.columns = ["Timestamp", "Action", "PID", "Status"]
    return df


# ──────────────────────────────────────────────
# Tabs: Live Monitor | Incident Audit Log
# ──────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊 Live Monitor", "📜 Incident Audit Log"])

# ══════════════════════════════════════════════
# Tab 1 — Live Monitor
# ══════════════════════════════════════════════
with tab1:

    # ──────────────────────────────────────────
    # Critical Alerts
    # ──────────────────────────────────────────
    cpu = metrics['cpu_usage_percent']
    mem = metrics['memory']['percent']

    alerts = []
    if cpu > 80:
        alerts.append(f"🔴 CRITICAL: High CPU Usage ({cpu}%)")
    if mem > 90:
        alerts.append(f"🔴 CRITICAL: High Memory Usage ({mem}%)")

    for alert in alerts:
        st.markdown(f'<div class="critical-alert">{alert}</div>', unsafe_allow_html=True)

    # ──────────────────────────────────────────
    # 🤖 AI Diagnosis (with 60s cooldown)
    # ──────────────────────────────────────────
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

            # ──────────────────────────────────
            # 🛡️ Remediation (Manual or Autonomous)
            # ──────────────────────────────────
            target_pid = diagnosis.get('recommended_action', {}).get('target_pid')
            if target_pid is not None:
                if not autonomous_mode:
                    # ── Manual: Human-in-the-Loop ──
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

                        # Verification loop: wait for OS to drop the process,
                        # then fetch fresh metrics
                        with st.spinner("Verifying system health recovery..."):
                            time.sleep(3)
                        st.rerun()
                else:
                    # ── Autonomous: No human approval needed ──
                    action_mgr = ActionManager()
                    result = action_mgr.kill_process(target_pid)

                    st.error(f"🛑 AUTONOMOUS ACTION TAKEN: Terminated PID {target_pid} based on AI diagnosis.")
                    action_mgr.log_action("autonomous_kill", target_pid, result)
                    st.toast(result, icon="🤖")

                    # Reset state so the system immediately re-verifies
                    st.session_state.last_analysis_result = None
                    st.session_state.cached_diagnosis = None
                    st.session_state.last_api_call_time = 0.0

                    # Verification loop: wait for OS to drop the process,
                    # then fetch fresh metrics
                    with st.spinner("Verifying system health recovery..."):
                        time.sleep(3)
                    st.rerun()

    # ──────────────────────────────────────────
    # Metrics Overview
    # ──────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("CPU Usage", f"{cpu}%")
    with col2:
        st.metric("Memory Usage", f"{mem}%", f"{metrics['memory']['used_gb']} GB Used")
    with col3:
        st.metric("Disk Usage", f"{metrics['disk_usage_percent']}%")

    # ──────────────────────────────────────────
    # Charts & Processes
    # ──────────────────────────────────────────
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

# ══════════════════════════════════════════════
# Tab 2 — Incident Audit Log
# ══════════════════════════════════════════════
with tab2:
    st.write("### 📜 Historical AI Actions")
    st.caption("All remediation actions taken by the agent are logged here.")

    audit_df = load_audit_log()

    if audit_df.empty:
        st.info("No audit records found. The log is empty or has not been created yet.")
    else:
        st.dataframe(audit_df, use_container_width=True)

    st.divider()

    if st.button("🗑️ Clear Log", help="Empties the audit.log file permanently."):
        try:
            with open(AUDIT_LOG_PATH, "w", encoding="utf-8") as f:
                f.truncate(0)
            st.success("Audit log cleared successfully.")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Failed to clear log: {e}")

# ──────────────────────────────────────────────
# Auto-Refresh (no while loop)
# ──────────────────────────────────────────────
time.sleep(15)
st.rerun()
