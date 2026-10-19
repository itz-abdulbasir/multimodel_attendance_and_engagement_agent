# NeuroClass • Multimodal Attendance & Engagement Agent
### AI-Powered, Privacy-Preserving Classroom Intelligence System (100% Offline)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.143-009688.svg)](https://fastapi.tiangolo.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-Headless-5C3EE8.svg)](https://opencv.org)
[![Offline Certified](https://img.shields.io/badge/Offline-100%25%20Edge%20Ready-emerald.svg)]()
[![Privacy Shield](https://img.shields.io/badge/Privacy-Zero%20Raw%20Persistence-brightgreen.svg)]()

---

## 1. Project Overview & Problem Statement
In educational institutions and professional training environments, attendance tracking remains largely manual or limited to basic biometric systems that fail to capture meaningful engagement and participation context. These traditional approaches are time-consuming, prone to inaccuracies, and provide no insight into learner attention, interaction patterns, or session effectiveness.

As classrooms increasingly adopt digital tools, there is a growing need for intelligent systems that can move beyond simple presence detection.

To address this challenge, the **Multimodal Attendance & Engagement Agent** was developed as an AI-powered, privacy-preserving classroom intelligence system. The project integrates **computer vision**, **audio signal processing**, and **agent-based reasoning** to automatically track attendance, analyze engagement trends, generate AI-driven teaching suggestions, and provide student session analytics. Designed to operate **entirely offline**, the system ensures ethical deployment while offering actionable insights that support educators and learners.

---

## 2. Project Statistics

| Metric | Target | Verified in Codebase |
| :--- | :--- | :--- |
| **Total Epics** | **9** | **9 Epics Implemented** |
| **Total Tasks (Stories)** | **17** | **17 Tasks Implemented** |
| **Total Subtasks** | **0** | **0 Subtasks** |
| **Deployment Mode** | 100% Offline Edge | Zero cloud transmission, local SQLite, on-device compute |

---

## 3. Operational Scenarios

### Scenario 1: Automated Attendance Tracking
- **Sustained Presence vs. Fleeting Appearance**: Tracks participants across frames using a sliding-window temporal filter (minimum persistence threshold, e.g. >= 60-75% presence).
- **False-Positive Elimination**: Accidental walk-bys or transient visitors passing the classroom door (< 12-15s) are automatically filtered (`WALKBY_FILTERED`) and excluded from official attendance logs.
- **Automated Timestamped Audit Logs**: Generates signed, verifiable CSV/JSON check-in and check-out records with SHA-256 verification hashes, eliminating manual roll calls.

### Scenario 2: Engagement and Session Dynamics Analysis
- **Visual Attention & Head Pose**: Real-time yaw, pitch, and roll estimation classifying focus direction (`FORWARD_BOARD`, `DOWNWARD_NOTES`, `LATERAL_DISTRACTED`).
- **Motion & Inactivity Dynamics**: Frame-to-frame motion energy profiling distinguishing healthy attentiveness from restless fidgeting or prolonged static dormancy (> 120s).
- **Classroom Acoustic Signals**: Voice Activity Detection (VAD) and short-time acoustic energy analysis classifying instructional rhythm (`INSTRUCTOR_MONOLOGUE`, `QA_INTERACTION`, `COLLABORATIVE_BUZZ`, `SILENT_STUDY`) **without speech-to-text recording or verbal eavesdropping**.
- **Multimodal Fusion**: Temporal alignment into a unified **Dynamic Engagement Index (EI: 0-100%)** detecting attention drops and engagement peaks.

### Scenario 3: AI-Driven Teaching Suggestions
- **Pedagogical Decision Engine**: Analyzes classroom trends against pedagogical heuristics (e.g., lecture monologue exceeding 12 minutes with visual attention drop, steep 25%+ engagement plunge, or prolonged acoustic hesitation).
- **Context-Aware Assistive Guidance**: Delivers real-time suggestion cards (`ACTIONABLE`, `ADVISORY`, `INFO`) recommending targeted tactics (e.g., 60-second comprehension poll, "Think-Pair-Share" peer discussion, pacing breaks).
- **Non-Coercive Decision Support**: Acts purely as assistive decision support for the instructor without intrusive enforcement, with built-in cooldowns preventing alert fatigue.

---

## 4. Agile Breakdown: 9 Epics & 17 Tasks Traceability

```
Epic 1: Project Environment, Modular Architecture & Privacy Foundation
 ├── Task 01: Environment Setup & Offline Modular Architecture Scaffolding
 └── Task 02: Privacy-Preserving Data Pipeline & Edge Storage Schema

Epic 2: Video Stream Ingestion & Participant Tracking
 ├── Task 03: Multi-Source Video Stream Ingestion Engine (Webcam / File / Simulation)
 └── Task 04: Participant Detection, Re-identification & Centroid Tracker

Epic 3: Sustained Presence & Automated Attendance Logging
 ├── Task 05: Sustained Presence Temporal Filter Engine
 └── Task 06: Automated Timestamped Attendance Registry & Exporter (CSV/JSON)

Epic 4: Visual Behavior & Attention Estimation
 ├── Task 07: Head Pose & Gaze Direction Attention Estimator (Yaw / Pitch)
 └── Task 08: Movement Dynamics & Prolonged Inactivity Analyzer

Epic 5: Classroom Audio Processing & Acoustic Dynamics
 ├── Task 09: Acoustic Voice Activity Detection (VAD) & Energy Profiler
 └── Task 10: Speech Rhythm & Classroom Interaction Pattern Detector

Epic 6: Multimodal Signal Fusion & Engagement Analytics
 ├── Task 11: Temporal Multimodal Fusion Engine
 └── Task 12: Dynamic Engagement Index & Attention Trend Modeler

Epic 7: Agent-Based Reasoning & AI-Driven Pedagogical Suggestions
 ├── Task 13: Context-Aware Rule & Heuristic Agent Reasoner
 └── Task 14: Real-Time Teaching Suggestion & Intervention Generator

Epic 8: Interactive Instructor Dashboard & Real-Time Visualization
 ├── Task 15: Live Classroom Intelligence Dashboard & Video Monitor (Glassmorphic UI)
 └── Task 16: Session Analytics, Timeline Heatmaps & Export Suite

Epic 9: System Validation, Privacy Audit & Performance Benchmarking
 └── Task 17: End-to-End System Evaluation & Offline Privacy Verification
```

---

## 5. Technical Architecture (4-Layer System Model)

The system adheres to the layered architecture model:

```
┌────────────────────────────────────────────────────────┐  ┌──────────────────────────────────────────────────┐
│                   FRONTEND LAYER                       │  │                 AI SERVICE LAYER                 │
│  ┌──────────────────┐  ┌────────────────────────────┐  │  │  ┌────────────────────────────────────────────┐  │
│  │ HTML5 Templates  │  │   FastAPI API Gateway      │──┼──┼─►│          Google Gemini 2.0 Flash           │  │
│  └──────────────────┘  └─────────────┬──────────────┘  │  │  │     (Pedagogical Decision Engine)          │  │
│  ┌──────────────────┐                ▼                 │  │  └─────────────────────┬──────────────────────┘  │
│  │   CSS3 Styling   │  ┌────────────────────────────┐  │  │                        ▼                         │
│  │ (Obsidian Glass) │  │       Route Handlers       │──┼──┼─►┌────────────────────────────────────────────┐  │
│  └──────────────────┘  └─────────────┬──────────────┘  │  │  │       Gemini Image & Diagram Gen       │  │
│  ┌──────────────────┐                ▼                 │  │  │       (SVG Classroom Visual Aids)          │  │
│  │  JS Controllers  │  ┌────────────────────────────┐  │  │  └─────────────────────┬──────────────────────┘  │
│  │     (app.js)     │  │        GenAI Utils         │──┼──┼─►                          ▼                         │
│  └────────┬─────────┘  └─────────────┬──────────────┘  │  │  ┌────────────────────────────────────────────┐  │
│           │                          ▼                 │  │  │           Text-to-Speech Engine            │  │
│           ▼            ┌────────────────────────────┐  │  │  │    (Synthesized Voice & Chime Alerts)      │  │
│  ┌──────────────────┐  │        Audio Utils         │──┼──┼─►└─────────────────────┬──────────────────────┘  │
│  │   Web Browser    │  └─────────────┬──────────────┘  │  │                        ▼                         │
│  │ (Live Dashboard) │                ▼                 │  │  ┌────────────────────────────────────────────┐  │
│  └──────────────────┘  ┌────────────────────────────┐  │  │  │          Code Generation Engine            │  │
│                        │       Code Executor        │──┼──┼─►│     (Python Audit & Analytics Scripts)     │  │
│                        └─────────────┬──────────────┘  │  │  └─────────────────────┬──────────────────────┘  │
└──────────────────────────────────────┼─────────────────┘  └────────────────────────┼─────────────────────────┘
                                       │                                             │
                                       ▼                                             ▼
┌────────────────────────────────────────────────────────┐  ┌──────────────────────────────────────────────────┐
│                    STORAGE LAYER                       │  │                  UTILITY LAYER                   │
│  ┌──────────────────────────┐ ┌──────────────────────┐ │  │  ┌──────────────────┐ ┌────────────────────────┐  │
│  │  Generated Audio Files   │ │ Generated Code Files │ │  │  │  Uploaded Files  │ │ Local Browser Storage  │  │
│  │  (storage/audio/*.wav)   │ │ (storage/code/*.py)  │ │◄─┼──┤ (storage/uploads)│ │ (telemetry/settings) │  │
│  └──────────────────────────┘ └──────────────────────┘ │  │  └──────────────────┘ └────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐ │  │  ┌───────────────────────────────────────────┐  │
│  │       Storage Layer / SQLite Ephemeral DB         │ │  │  │           Edge Privacy Guard              │  │
│  │ (classroom_intelligence.db - Zero Cloud Egress)   │ │  │  │ (Gaussian Face Blur & Salted SHA-256 Hash)│  │
│  └───────────────────────────────────────────────────┘ │  │  └───────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘  └──────────────────────────────────────────────────┘
```

---

## 6. Traceability to the 15 Project Instructions

| # | Instruction | Architecture Layer | Active Component | How to See & Verify in the System |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Define project objectives** | All Layers | System Objectives Framework | Click **"Architecture & 15 Instructions"** modal at the top of the dashboard. |
| **2** | **Design architecture & workflow** | All Layers | 4-Layer Offline Edge Architecture | View interactive 4-layer architecture diagram in the **"Architecture"** modal tab. |
| **3** | **Setup video input** | Frontend & Vision | `VideoStreamEngine` | Switch between *Smart Classroom Simulator* and *Live Webcam Feed* in the top nav dropdown. |
| **4** | **Setup audio input** | Frontend & Audio | `AudioSignalAnalyzer` & Web Mic API | Switch between *Simulated Acoustics* and *Live Web Microphone* to feed real room audio. |
| **5** | **Develop face detection & tracking** | Vision Layer | `CentroidFaceTracker` | Live video feed displays tracked learner bounding boxes, centroid IDs, and privacy blur. |
| **6** | **Implement sustained presence logic** | Attendance Layer | `SustainedPresenceEngine` | Open **"Fusion & Logic"** modal to adjust min seconds (30s), ratio (65%), and walk-by filter (15s). |
| **7** | **Generate timestamp-based logs** | Attendance Layer | Attendance Registry & Exporter | Click **"Attendance Logs"** button to view check-in timestamps and SHA-256 integrity signatures. |
| **8** | **Analyze engagement (visual)** | Vision Layer | `VisualAttentionAnalyzer` | Visual Focus Rate KPI (Yaw/Pitch gaze direction) and dormancy inactivity counter. |
| **9** | **Process audio signals** | Audio Layer | Acoustic VAD & Rhythm Classifier | Acoustic Rhythm KPI displays Monologue, Q&A, Collaborative Buzz, or Silent Study via RMS VAD. |
| **10** | **Combine visual & audio (fusion)** | Fusion Layer | `MultimodalFusionEngine` | Open **"Fusion & Logic"** modal to adjust weights (50% Vision, 20% Motion, 30% Audio) live. |
| **11** | **Calculate engagement scores & trends**| Fusion Layer | Dynamic Engagement Index (0-100%) | Real-time Engagement Timeline Canvas plots live 5Hz waveforms with trend classification. |
| **12** | **Develop AI agent suggestions** | AI Service Layer | `PedagogicalReasoningAgent` & Gemini | Click **"✨ Ask Gemini 2.0 Flash"** or **"🔊 Voice Alert"** to trigger live teaching suggestions. |
| **13** | **Create dashboard & reports** | Frontend Layer | Obsidian Neon Glassmorphic UI | Full live interactive dashboard with live video, canvas waveforms, roster, and modals. |
| **14** | **Ensure privacy & local storage** | Storage & Utility | Edge Privacy Guard & SQLite | 100% offline edge operation, zero cloud calls, Gaussian facial obfuscation, salted SHA-256. |
| **15** | **Test system accuracy & performance** | Testing Suite | Automated Test Runner Suite | Click **"🧪 Run Tests"** in top nav to execute 10 test suites in real-time in <1.0 second. |

---

## 7. Directory Structure

```
SmartBridge/
├── PROJECT_BREAKDOWN.md          # Complete Agile 9 Epics & 17 Tasks specification
├── requirements.txt              # Dependency specification (pip freeze)
├── run_agent.py                  # Single-command application launcher
├── README.md                     # Documentation & setup guide
├── backend/
│   ├── config.py                 # System configuration & threshold management (Task 01)
│   ├── db/
│   │   └── database.py           # SQLite edge persistence & SHA-256 pseudonym hashing (Task 02)
│   ├── vision/
│   │   ├── video_stream.py       # Multi-source stream ingestion & simulation (Task 03)
│   │   ├── face_tracker.py       # Centroid tracking & facial privacy blur (Task 04)
│   │   └── attention_analyzer.py # Head pose, gaze orientation & dormancy (Tasks 07, 08)
│   ├── audio/
│   │   └── audio_analyzer.py     # Acoustic VAD, speech-to-silence rhythms (Tasks 09, 10)
│   ├── attendance/
│   │   └── sustained_presence.py # Sliding-window sustained presence & CSV export (Tasks 05, 06)
│   ├── fusion/
│   │   └── multimodal_fusion.py  # Signal fusion & Dynamic Engagement Index (Tasks 11, 12)
│   ├── agent/
│   │   └── pedagogical_agent.py  # Heuristic reasoner & suggestion generator (Tasks 13, 14)
│   └── api/
│       └── server.py             # FastAPI backend, SSE stream, MJPEG feed, REST (Tasks 15, 16)
├── frontend/
│   ├── index.html                # Obsidian neon glassmorphism dashboard UI (Task 15)
│   ├── css/
│   │   └── styles.css            # Custom Vanilla CSS design tokens & animations
│   └── js/
│       └── app.js                # SSE telemetry listener, live canvas waveform, roster (Task 16)
└── tests/
    └── test_system.py            # Comprehensive test suite & offline privacy audit (Task 17)
```

---

## 7. Quickstart Guide

### Prerequisites & Architecture Documentation
- Python 3.9+ (Verified on Python 3.14 on Windows)
- **[PREREQUISITES.md](file:///c:/Users/91970/OneDrive/Music/SmartBridge/PREREQUISITES.md)**: Prerequisite verification matrix, alternatives analysis, and development knowledge requirements.
- **[PROJECT_WORKFLOW.md](file:///c:/Users/91970/OneDrive/Music/SmartBridge/PROJECT_WORKFLOW.md)**: 6-Milestone step-by-step engineering roadmap, traceability matrix, and execution runbook.

### 1. Activate Environment & Install Dependencies
```powershell
# Create virtual environment if not already created
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install requirements
.\.venv\Scripts\pip install -r requirements.txt
```

### 2. Run Test Suite (Epic 9: Comprehensive 91-Test Verification Suite)
```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\python -m unittest tests/test_system.py
```
*Expected Output:*
```
Ran 91 tests in 45.0s
OK
```

### 3. 3-Way Hybrid Student Enrollment & Live Webcam Identity Linking
NeuroClass features an edge biometric enrollment and live identity linking architecture:
1. **Directory-Based Pre-Enrollment (`student_db/`):**
   - Drop reference JPEG/PNG portraits into `student_db/{student_id}.jpg` (e.g. `student_db/STU-101.jpg`).
   - The facial recognition engine automatically extracts 128-d biometric embeddings and identifies matching students on webcam with confidence > 0.55.
2. **Auto-Tracking Live Learners (`TRK-xxx`):**
   - Unrecognized individuals appearing on camera are automatically assigned anonymous session track IDs (e.g., `Live Learner (TRK-001)`).
   - Their active presence, head pose, visual attention, and sustained engagement are tracked continuously.
3. **Interactive Human-in-the-Loop "🎯 Identify / Link" Modal:**
   - In both the **Live Attendance Roster** and the **Attendance Logs** modal, click **"🎯 Identify / Link"** next to any `TRK-xxx` row.
   - **Option A (Link Existing Student):** Select an existing student from the class database dropdown.
   - **Option B (Enroll New Student):** Enter a new Student ID and Name, and optionally upload a portrait photo or use the live webcam face crop.
   - **Seamless Presence Merging:** Accumulated active seconds, first-seen timestamps, and attention scores are instantly merged into the student profile with **zero lost attendance time**!

### 4. Launch the Applications

#### Option A: FastAPI Core Engine & Glassmorphic Web App (Port 8000)
```powershell
.\.venv\Scripts\python run_agent.py
```
Open your browser to:
👉 **`http://127.0.0.1:8000`** (Web Dashboard)  
👉 **`http://127.0.0.1:8000/docs`** (Interactive Swagger/OpenAPI docs)

#### Option B: Streamlit Analytics Dashboard (Port 8501)
```powershell
.\.venv\Scripts\streamlit run streamlit_app.py
```
Open your browser to:
👉 **`http://localhost:8501`** (Streamlit Dashboard)


---

## 8. Privacy & Ethical Deployment Architecture
1. **Zero External Cloud Telemetry**: All computer vision, acoustic feature extraction, and reasoning operate strictly on the local CPU/device. No frames or biometric data leave the local machine.
2. **Face Obfuscation / Privacy Blur**: Built-in Gaussian ROI blurring over participant faces prevents video storage from exposing learner identities.
3. **One-Way Irreversible Pseudonymization**: Student identifiers in the audit registry are protected using salted SHA-256 cryptographic hashing.
4. **No Acoustic Eavesdropping**: The audio pipeline calculates only Root-Mean-Square (RMS) acoustic energy and Voice Activity Detection (VAD) patterns—**no spoken dialogue is ever recorded, transcribed, or stored**.
