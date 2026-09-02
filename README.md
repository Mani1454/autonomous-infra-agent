# 🚀 Autonomous Infrastructure Agent

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://autonomous-infra-agent.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![Gemini AI](https://img.shields.io/badge/Gemini-3.6%20Flash-4285F4?style=for-the-badge&logo=google)](https://aistudio.google.com)

An intelligent IT operations system that reduces **Mean Time To Recovery (MTTR)** by autonomously detecting and remediating infrastructure incidents. Powered by **Agentic AI (Gemini 2.0 Flash)**, this system goes beyond static threshold monitoring to deliver proactive, context-aware infrastructure management.

---

## 🌐 Live Demo

**[→ Try it live](https://autonomous-infra-agent.streamlit.app)**

> **🎬 Demo Mode is ON by default** — all AI features (diagnosis, remediation, autonomous mode) are fully visible without any setup.
>
> **To enable real Gemini AI analysis:**
> 1. Toggle off **Demo Mode** in the sidebar
> 2. Get a free API key at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) *(no credit card needed)*
> 3. Paste it in the **Gemini API Key** field

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Real-time Telemetry** | High-frequency CPU, Memory, Disk & process-level monitoring |
| **AI Root-Cause Analysis** | Gemini 2.0 Flash diagnoses anomalies with SRE-level insights |
| **Human-in-the-Loop** | AI recommends — human approves process termination |
| **Fully Autonomous Mode** | Toggle for zero-human-intervention self-healing |
| **Audit Trail** | Append-only log of every remediation action taken |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.10+ |
| **UI / Dashboard** | Streamlit + Plotly |
| **System Monitoring** | `psutil` |
| **AI Engine** | Google Gemini 2.0 Flash (`google-genai` SDK) |
| **Data Handling** | Pandas |

---

## 📥 Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/Mani1454/autonomous-infra-agent.git
cd autonomous-infra-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the dashboard
streamlit run dashboard.py
```

Then open [http://localhost:8501](http://localhost:8501) and enter your Gemini API key in the sidebar.

---

## 🏗️ Architecture

```
dashboard.py      ← Streamlit UI / orchestrator
monitor.py        ← psutil telemetry engine
brain.py          ← Gemini AI diagnosis layer
remediate.py      ← Process termination + audit logging
```

---

## 🛣️ Roadmap

- [x] **Phase 1** — Real-time telemetry dashboard
- [x] **Phase 2** — AI reasoning engine (Gemini root-cause analysis)
- [x] **Phase 3** — Automated remediation (self-healing)
- [x] **Phase 4** — Human-in-the-Loop + Autonomous Mode + Audit Log
- [ ] **Phase 5** — RAG integration with system runbooks

---

*Built as part of the Autonomous Infrastructure Agent project.*
