import streamlit as st
import pandas as pd
import time
from monitor import SystemMonitor
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Autonomous Infrastructure Monitor",
    page_icon="📊",
    layout="wide"
)

# Initialize Monitor
@st.cache_resource
def get_monitor():
    return SystemMonitor()

monitor = get_monitor()

# Initialize Session State for History
if 'cpu_history' not in st.session_state:
    st.session_state.cpu_history = pd.DataFrame(columns=['Time', 'CPU %'])

# Title
st.title("🚀 Autonomous Infrastructure Agent - Phase 1")
st.subheader("System Monitor Dashboard")
st.caption("Auto-refresh: 5s")

# Placeholder for dynamic content
placeholder = st.empty()

# Custom CSS for styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
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

# Main loop for auto-refresh
while True:
    metrics = monitor.get_system_metrics()
    
    # Update CPU History
    new_data = pd.DataFrame({
        'Time': [datetime.now().strftime("%H:%M:%S")],
        'CPU %': [metrics['cpu_usage_percent']]
    })
    st.session_state.cpu_history = pd.concat([st.session_state.cpu_history, new_data], ignore_index=True)
    
    # Keep only last 20 data points for the graph
    if len(st.session_state.cpu_history) > 20:
        st.session_state.cpu_history = st.session_state.cpu_history.tail(20)

    with placeholder.container():
        # Critical Alerts
        alerts = []
        if metrics['cpu_usage_percent'] > 80:
            alerts.append(f"🔴 CRITICAL: High CPU Usage ({metrics['cpu_usage_percent']}%)")
        if metrics['memory']['percent'] > 90:
            alerts.append(f"🔴 CRITICAL: High Memory Usage ({metrics['memory']['percent']}%)")
        
        for alert in alerts:
            st.markdown(f'<div class="critical-alert">{alert}</div>', unsafe_allow_html=True)

        # Metrics Overview
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("CPU Usage", f"{metrics['cpu_usage_percent']}%")
        with col2:
            st.metric("Memory Usage", f"{metrics['memory']['percent']}%", f"{metrics['memory']['used_gb']} GB Used")
        with col3:
            st.metric("Disk Usage", f"{metrics['disk_usage_percent']}%")

        # Charts and Tables
        row2_col1, row2_col2 = st.columns([2, 1])
        
        with row2_col1:
            st.write("### CPU Usage History")
            fig = px.line(st.session_state.cpu_history, x='Time', y='CPU %', title='CPU Load Over Time')
            fig.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig, use_container_width=True)

        with row2_col2:
            st.write("### Top 3 Processes")
            top_procs_df = pd.DataFrame(metrics['top_processes'])
            if not top_procs_df.empty:
                st.table(top_procs_df)
            else:
                st.write("Fetching process data...")

    # Wait for 5 seconds
    time.sleep(5)
    # Streamlit will naturally rerun if we use st.experimental_rerun() or if we just let the while loop run with st.empty container
    # However, standard practice for auto-refresh in modern Streamlit is sometimes different but a loop works for a simple agent script.
    # To avoid script timeout/lock, we can use st.rerun() instead of an infinite loop if we want to follow ST best practices, 
    # but for a simple "monitor" app, this logic is often fine. 
    # Let's use st.rerun() to be safe and clean.
    st.rerun()
