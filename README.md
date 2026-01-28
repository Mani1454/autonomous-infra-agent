# Autonomous Infrastructure Agent for Self-Healing Systems

An intelligent IT operations system designed to reduce **Mean Time To Recovery (MTTR)** by automating incident detection and remediation. Leveraging **Agentic AI**, this system moves beyond traditional static threshold monitoring to provide proactive, context-aware infrastructure management.

---

## 🚀 Overview

The **Autonomous Infrastructure Agent** is designed to act as a virtual system administrator. In Phase 1, it establishes a robust telemetry and visualization foundation, enabling real-time monitoring of critical system health metrics.

## ✨ Current Capabilities (Phase 1)

-   **Real-time System Telemetry**: High-frequency data collection for CPU, Memory, Disk, and Process-level analysis.
-   **Semantic Anomaly Detection & Alerting**: Intelligent identification of resource exhaustion with visual urgency cues.
-   **Interactive Operations Dashboard**: A high-performance dashboard for at-a-glance infrastructure health assessment.

## 🛠️ Tech Stack

-   **Logic**: Python 3.10+
-   **Monitoring Engine**: `psutil`
-   **Visualization**: Streamlit & Plotly
-   **Data Handling**: Pandas

## 📥 Installation

Ensure you have Python 3.10 or higher installed.

1. **Clone the repository** (or download the source):
   ```bash
   git clone <your-repository-url>
   cd "Autonomous Infrastructure Agent"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🖥️ Usage

Launch the interactive dashboard to start monitoring your infrastructure:

```bash
python -m streamlit run dashboard.py
```

## 🛣️ Roadmap

- **Phase 2**: AI reasoning engine integration for incident root-cause analysis.
- **Phase 3**: Automated remediation (self-healing) scripts.
- **Phase 4**: RAG-based integration with system documentation and runbooks.

---
*Developed as part of the Autonomous Infrastructure Agent project.*
