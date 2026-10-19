# EPIC 6: Interface, Testing, and Deployment
## Activity 6.2: Launch Optional Streamlit Dashboard

---

### 1. Activity Overview

In **Activity 6.2**, an optional Streamlit-based dashboard was designed and launched to visualize system outputs in an interactive, user-friendly format. The dashboard displays:
- **Attendance Records:** Real-time presence logs, cumulative durations, status categorization (`PRESENT`, `LATE`, `INTERMITTENT`, `WALKBY_FILTERED`), and cryptographic audit hashes.
- **Engagement Timelines:** Multi-signal temporal profiles, focus zones (High Focus $>75\%$, Balanced $50-75\%$, Distraction $<50\%$), and statistical fluctuation metrics.
- **Instructor Suggestions:** Context-aware pedagogical coaching recommendations with rule attributions and a comprehensive Teacher Analytics Profile.
- **Student Session Analytics:** Privacy-preserving, reflective individual participation summaries without social comparison, rankings, or evaluative grades.
- **Core Application Pipeline Execution (Activity 6.1 Integration):** Visual stream monitor, source selector, and on-demand 5-module pipeline verification widget.

> **Design Principle:**  
> The visualization layer was explicitly designed to improve the **interpretability of system outputs** rather than to serve as a mandatory interface. Charts, tables, and expandable sections allow educators, students, and system administrators to explore session data and pedagogical insights effectively without requiring cloud connectivity.

---

### 2. Dashboard Architecture & Dual-Mode Operation

```
+-----------------------------------------------------------------------------------+
|                        NeuroClass Streamlit Dashboard                             |
|                           (streamlit_app.py :8501)                                |
+-----------------------------------------------------------------------------------+
                                         |
               +-------------------------+-------------------------+
               | (If FastAPI Online)                               | (If FastAPI Offline)
               v                                                   v
+-------------------------------+                  +-------------------------------+
|    FastAPI REST & Streaming   |                  |   Direct Local Fallback       |
|    Engine (server.py :8000)   |                  |   - SQLite (classroom.db)     |
|    - /api/attendance/summary  |                  |   - DatabaseManager           |
|    - /api/suggestions/history |                  |   - RecommendationsEngine     |
|    - /api/analytics/activity_*|                  |   - AnalyticsService          |
|    - /api/activity_6_1/*      |                  |   - PipelineVerifier          |
+-------------------------------+                  +-------------------------------+
```

The dashboard operates seamlessly in two operational modes:
1. **Live Backend Mode (Connected to FastAPI at `http://127.0.0.1:8000`):**
   - Renders live 60 FPS MJPEG computer vision feed with bounding box and pose overlays.
   - Dispatches dynamic AI recommendations via asynchronous endpoints.
   - Synchronizes live presence roster and active visual tracks.
2. **Standalone Database Mode (Offline / Direct SQLite):**
   - Automatically activates if the FastAPI server is offline.
   - Directly reads from `classroom_intelligence.db` via `DatabaseManager`.
   - Uses local fallback engine classes (`RecommendationsEngine`, `TeacherProfileService`, `AnalyticsService`, `PipelineVerifier`) ensuring zero crashes and full functionality.

---

### 3. Detailed Implementation of the Four Core Pillars

#### Pillar 1: Attendance Records (Activity 2.2)
- **Presence Verification Logic:** Tracks sustained presence time ($\ge 30$ seconds) across video sessions. Brief walk-bys ($< 15$ seconds) are filtered out automatically.
- **Status Categorization:**
  - `PRESENT`: Cumulative duration $\ge 80\%$ of active session.
  - `LATE`: Arrival detected after session start with sustained presence.
  - `INTERMITTENT`: Multiple discontinuous appearances below continuous threshold.
  - `WALKBY_FILTERED`: Incidental appearance below minimum duration ($< 30$s).
- **Interactive Controls:**
  - Status dropdown filter (`All Statuses`, `PRESENT`, `LATE`, `INTERMITTENT`, `WALKBY_FILTERED`).
  - Real-time search filter by Student ID or Student Name.
- **Cryptographic Audit:** Displays SHA-256 verification hash per record for tamper-evident attendance audit.
- **Exports:** One-click CSV download via official backend API and local table CSV download.

#### Pillar 2: Engagement Timelines (Activity 4.3 & 5.2)
- **Multimodal Temporal Profiles:** Multi-line trajectory combining:
  - Fused Composite Engagement Index ($E_t$)
  - Visual Attentiveness Score ($V_t$)
  - Acoustic / Speech Activity Score ($A_t$)
- **Focus Classification Zones:**
  - 🟢 **High Focus Zone (>75%):** Active visual gaze, aligned head pose, minimal distraction.
  - 🟡 **Balanced Attention Zone (50–75%):** Steady routine attention, note-taking, listening.
  - 🔴 **Distraction Alert Zone (<50%):** Gaze aversion, head down, or extended inactivity alert.
- **Statistical Fluctuation & Stability Metrics:**
  - Session Mean Engagement ($\mu$)
  - Standard Deviation ($\sigma$) & Variance ($\sigma^2$)
  - Attention Stability Index ($100 - 2.5 \times \sigma$)
  - Disengagement Alert Counter
- **Expandable Drill-Downs:**
  - **Minute-Level Session Trends:** Displays rolling minute-by-minute engagement, visual focus, audio ratio, and emotion distribution (`Engaged`, `Neutral`, `Confused`, `Distracted`).
  - **Structured Audio Window Telemetry (Activity 3.1):** Normalized 16 kHz mono digital waveform, 1.0s window segmentation, SPL dB levels, and video-frame synchronization.

#### Pillar 3: Instructor Suggestions (Activity 5.1)
- **Teacher Analytics Profile:**
  - Instructor: Prof. Alex Vance
  - Current Effectiveness Score: $87.5\%$ (+12.0% semester trend)
  - Strengths Tags: *High engagement 85%+*, *Emotion diversity management*, *Balanced pacing recovery*
  - Expandable Teaching History log.
- **Context-Aware Pedagogical Stream:**
  - Urgency indicators: 🔴 `ALERT` (High), 🟡 `WARNING` (Medium), 🔵 `INFO` (Low).
  - Explicit rule attribution across all 7 pedagogical rules:
    - *Rule 1: Sustained Disengagement Mitigation*
    - *Rule 2: Sudden Drop Detection*
    - *Rule 3: Low Class Attendance Check*
    - *Rule 4: High Interaction & Vocal Dialogue*
    - *Rule 5: High Noise / Classroom Chatter*
    - *Rule 6: Extended Inactivity Mitigation*
    - *Rule 7: Dynamic Re-engagement Affirmation*
  - Interactive urgency filter and "✨ Request AI Recommendation" button.

#### Pillar 4: Student Session Analytics (Activity 5.2)
- **Reflective, Privacy-Compliant Design:** Strictly avoids social comparison, leaderboard ranking, or evaluative grading.
- **Interactive Student Selector:** Enables inspection of any enrolled learner (`STU-101: Emma Watson` through `STU-108: Noah Wilson`).
- **Individual Profile Card:**
  - Attendance Status, Active Presence Duration (min), Presence Ratio (%), Consistency Index (%).
- **Focus Distribution Progress Breakdown:**
  - High Focus ($>75\%$) ratio
  - Balanced Focus ($50-75\%$) ratio
  - Distracted ($<50\%$) ratio
- **Continuous Focus Episodes:** Formatted table identifying sustained deep focus intervals (Start, End, Duration min, Mean Score).
- **Grounded Activity Trends:** Actionable qualitative patterns grounded in session data.
- **Metacognitive Self-Reflection Prompts:** Guiding reflective questions for student self-awareness.
- **Dual Export:** One-click download of individual reflection summary in JSON and formatted Markdown.
- **Unranked Cohort Reflection Overview:** Cohort-wide table with zero peer ranking or grades.

---

### 4. Activity 6.1 Integration: Core Pipeline & Live Feed

- **Multi-Source Switching:** Supports `simulated`, `file` (`storage/uploads/classroom_lecture_sample.mp4`), and `webcam`.
- **Live Feed & Fusion Telemetry:** Real-time stream monitor and progress bars.
- **On-Demand 5-Module Pipeline Verifier:**
  - Select source and frame count (1–30 frames).
  - Runs full verification across:
    1. 👁️ Vision Ingestion & Face Detection
    2. 🎙️ Audio Feature Extraction & VAD
    3. ⚡ Multimodal Signal Fusion
    4. 🎯 Engagement Scoring & Temporal Profile
    5. 📊 Analytics & Recommendation Engine
  - Displays elapsed execution time, average FPS, latency per frame, and pass/fail diagnostics.

---

### 5. Launch & Execution

To launch the Streamlit dashboard:
```powershell
# From project root with activated virtual environment
.venv\Scripts\streamlit.exe run streamlit_app.py --server.port 8501
```

Access the interactive dashboard in your browser:
```
http://localhost:8501
```
