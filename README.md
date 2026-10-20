# NeuroClass: Multimodal Attendance & Engagement Agent

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.143.0-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-5.0.0-5C3EE8.svg?logo=opencv&logoColor=white)](https://opencv.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.65.0-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Librosa](https://img.shields.io/badge/Librosa-1.0.0-orange.svg)](https://librosa.org/)
[![Tests Passing](https://img.shields.io/badge/Tests-91%2F91%20Passing-brightgreen.svg)](file:///c:/Users/91970/OneDrive/Music/SmartBridge/6.Project%20Testing/Performance%20Testing%20%26%20Validation%20Report.pdf)
[![Privacy Certified](https://img.shields.io/badge/Privacy-100%25%20Offline%20Edge-success.svg)](#privacy-guarantee)
[![Solo Project](https://img.shields.io/badge/Project-Solo%20Developer-purple.svg)](#project-ownership)

> **Submission Template:** Formatted to strictly match the [AI/ML & GenAI Track Project Template](https://github.com/Ravi-teja-777/AI-ML-and-GEN-AI-Track-Project-Template).

---

## Executive Overview

**NeuroClass** is an **edge-native multimodal classroom intelligence agent** engineered to eliminate administrative roll-call friction, provide quantitative continuous engagement telemetry, and assist instructors in real time—all with **certified zero-cloud offline privacy**.

```
+---------------------------------------------------------------------------------------------------+
|                                  THE NEUROCLASS MULTIMODAL PIPELINE                               |
+---------------------------------------------------------------------------------------------------+
|  [Classroom Sensors]    -->  [Computer Vision: Yaw/Pitch Attention + 65% Sustained Presence]     |
|                              [Acoustic Dynamics: Librosa RMS + VAD - Strict ZERO Speech-to-Text]  |
|                                                      |                                            |
|  [Multimodal Fusion]    -->  [Composite Engagement Index: 50% Vision + 20% Motion + 30% Audio]    |
|                                                      |                                            |
|  [Pedagogical Copilot]  -->  [Real-Time Teaching Nudges (Monologue / Silence / Fatigue Cooldown)]  |
|                                                      |                                            |
|  [Edge Telemetry & HUD] -->  [FastAPI WebSocket Stream (15 FPS) + Streamlit Longitudinal Cockpit] |
+---------------------------------------------------------------------------------------------------+
```

---

## Submission Template Structure (The 8 Mandatory Folders)

This repository strictly implements the standardized 8-folder submission structure. Click on any deliverable link below to inspect the submission report:

```
.
├── 1. Brainstorming & Ideation/
│   └── Brainstorming & Ideation.pdf      [Official PDF Deliverable]
│
├── 2.Requirement Analysis/
│   ├── Customer Journey Map.pdf          [Official PDF Deliverable]
│   ├── Data Flow Diagram.pdf             [Official PDF Deliverable]
│   ├── Solution Requirements.pdf         [Official PDF Deliverable]
│   └── Technology Stack.pdf              [Official PDF Deliverable]
│
├── 3. Project Design Phase/
│   ├── Problem-Solution Fit.pdf          [Official PDF Deliverable]
│   ├── Proposed Solution.pdf             [Official PDF Deliverable]
│   └── Solution Architecture.pdf         [Official PDF Deliverable]
│
├── 4. Project Planning Phase/
│   └── Project Planning.pdf              [Official PDF Deliverable]
│
├── 5. Project Development Phase/         <--- [APPLICATION CODE & SPECIFICATIONS]
│   ├── backend/                          # FastAPI server, Computer Vision, DSP, Agent
│   ├── frontend/                         # Vanilla ES6 Live HUD & Static Assets
│   ├── student_db/                       # Local Enrolled Student Face Biometrics
│   ├── storage/                          # Local Exports, Audio & Code Artifacts
│   ├── tests/                            # 91-Test Automated System Verification Suite
│   ├── epic_specs/                       # All 13 Detailed EPIC Activity Specs
│   ├── classroom_intelligence.db         # Edge SQLite Database (ACID WAL Mode)
│   ├── requirements.txt                  # Python Dependency Manifest
│   ├── run_agent.py                      # Core ASGI Application Launcher & Verifier
│   ├── streamlit_app.py                  # Companion Streamlit Analytics Cockpit
│   ├── validate_environment.py           # Pre-Flight Environment & Import Verifier
│   ├── Functional Features & Coding Solution.md   [Architecture Summary]
│   └── Functional Features & Coding Solution.pdf  [Architecture PDF Deliverable]
│
├── 6.Project Testing/
│   └── Performance Testing & Validation Report.pdf [Official PDF - 91 Tests / 100% Pass]
│
├── 7.Project Documentation/
│   └── Project Documentation & User Manual.pdf    [Official PDF Deliverable]
│
├── 8.Project Demonstration/
│   ├── Project Demo Planning.pdf         [Official PDF Deliverable]
│   ├── Demonstration of Proposed Features.pdf [Official PDF Deliverable]
│   ├── Communication.pdf                 [Official PDF Deliverable]
│   └── Scalability & Future Plan.pdf     [Official PDF Deliverable]
│
├── .gitignore                            # Repository Git Ignore Rules
└── README.md                             # Master Project Landing Page
```

---

## Quickstart: How to Run the Application

Navigate directly into **`5. Project Development Phase/`** to run all components:

```powershell
cd "5. Project Development Phase"

# 1. Validate environment and 14 core dependencies
python validate_environment.py

# 2. Run end-to-end 5-module pipeline verification
python run_agent.py --verify-pipeline

# 3. Launch the core FastAPI server & Web HUD (Port 8000)
python run_agent.py

# 4. In a separate terminal, launch the Streamlit analytics cockpit (Port 8501)
streamlit run streamlit_app.py

# 5. Run the 91-test automated verification suite
python tests/test_system.py
```

- **Live Web HUD:** [`http://127.0.0.1:8000`](http://127.0.0.1:8000)
- **Streamlit Analytics Cockpit:** [`http://127.0.0.1:8501`](http://127.0.0.1:8501)
- **Interactive OpenAPI Documentation:** [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)

---

## The 3 Core Scenarios & Key Innovations

### 1. Sustained Presence vs. Walk-By Attendance
- **Walk-By Discrimination:** Persons detected for $<15$ seconds (such as people walking past an open door) are filtered as non-participant noise.
- **Sustained Presence Window:** Candidates earn verified attendance only after remaining visible for $\ge 65\%$ of the observation window.
- **Punctuality Tracking:** First detected after $>10$ minutes marks status as **Late**.

### 2. Multimodal Engagement Analysis
- **Visual Attention:** 3D Head Pose tracking estimates Yaw ($\le 25^\circ$) and Pitch ($\le 20^\circ$) angles to classify attentive vs. distracted gaze.
- **Posture & Motion Balance:** Flags dormant posture ($>120$s freeze) and restless jitter ($>0.45$).
- **Acoustic Signal Dynamics:** Ingests 16 kHz raw PCM audio via Librosa to compute RMS energy and Voice Activity Detection (VAD). **Strictly zero speech-to-text or word transcription.**
- **Explainable Composite Metric:**
  $$\text{Engagement Index} = (0.50 \times \text{Visual}) + (0.20 \times \text{Motion}) + (0.30 \times \text{Acoustic})$$

### 3. Context-Aware AI Teaching Suggestions
- **Monologue Alert:** Warns the instructor after $>12$ minutes of continuous monologue without student vocal participation.
- **Silence Alert:** Triggers if the room remains silent for $>6$ minutes during group activities.
- **Anti-Fatigue Cooldown:** Enforces a rigid 45-second silence between suggestions to eliminate alert fatigue.

### 4. The 3-Way Hybrid Biometric Enrollment
Never let missing student photos block live attendance:
1. **Directory File Drop:** Add `STU-101.jpg` directly into `5. Project Development Phase/student_db/`.
2. **Web Portal Upload:** Register photos and names via the `/api/students/register` drawer.
3. **Live 1-Click Track Linking (`[Identify / Link]`):** Click the link button next to any anonymous track (`TRK-001`) on the live HUD to bind their Student ID, save their face crop, and update all attendance logs retroactively.

---

## Performance Benchmarks & 91-Test Verification

Every component is validated by a rigorous 91-test automated suite (`tests/test_system.py`):

| Test Suite Metric | Verified Benchmark Result |
|:---|:---|
| **Total Automated Tests** | **91 / 91 Passed (100.0% Success)** |
| **Test Execution Time** | **43.36 seconds** |
| **Vision Processing Throughput** | **16.3 – 20.3 FPS on Standard CPU** |
| **Vision Processing Latency** | **33.7 ms per frame** |
| **Acoustic Processing Latency** | **3.6 ms per chunk (<1% of window)** |
| **Offline Telemetry Audit** | **CERTIFIED (0 bytes external network traffic)** |
| **Acoustic Privacy Audit** | **CERTIFIED (0 words recorded or transcribed)** |

---

## Project Ownership & Ethical AI Commitment

- **Solo Developer Project:** Conceptualized, architected, and built end-to-end by an independent solo developer. No multi-person team splits or external delegations.
- **Ethical Boundaries:** Attendance is strictly derived from physical presence and gaze orientation. **Subjective facial emotion recognition is strictly prohibited** to prevent racial, cultural, and neurodivergent biases.
- **Privacy-by-Design:** Facial ROI blurring, salted SHA-256 database identifiers, and local edge processing guarantee total institutional autonomy.
