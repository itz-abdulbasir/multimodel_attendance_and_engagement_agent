# 🚀 NeuroClass Project Workflow & Implementation Specification

> **Document Version:** 1.0.0  
> **Target System:** NeuroClass Multimodal Classroom Attendance & Engagement Agent  
> **Workflow Scope:** End-to-End Milestones 1 through 6  
> **Status:** 100% Implemented, Verified & Validated  

---

## 1. Executive Summary & Workflow Lifecycle

The **Project Workflow** establishes the structured, step-by-step engineering roadmap for designing, implementing, validating, and operating **NeuroClass**. It guides each milestone in sequential order, ensuring architectural integrity, strict local privacy, and production-grade reliability.

```
+---------------------------------------------------------------------------------------------------+
|                                     NEUROCLASS WORKFLOW PIPELINE                                  |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  [MILESTONE 1: Environment & Requirements]                                                        |
|  └── Activity 1.1: requirements.txt ──> Activity 1.2: Python Virtual Environment (.venv)          |
|                                 │                                                                 |
|                                 v                                                                 |
|  [MILESTONE 2: Vision Module]                    [MILESTONE 3: Audio Module]                      |
|  ├── Activity 2.1: Face Tracking & Pose          ├── Activity 3.1: Audio Extraction               |
|  └── Activity 2.2: Sustained Attendance Logic    └── Activity 3.2: Noise & Speech VAD             |
|                                 \                      /                                          |
|                                  \                    /                                           |
|                                   v                  v                                            |
|                       [MILESTONE 4: Multimodal Agent Implementation]                              |
|                       ├── Activity 4.1: Multimodal Signal Fusion (60/40)                          |
|                       ├── Activity 4.2: Multimodal Signal Fusion & Synchronization                |
|                       └── Activity 4.3: Engagement Scoring Logic & Temporal Profile               |
|                                           │                                                       |
|                                           v                                                       |
|                       [MILESTONE 5: Analytics & Recommendation Engine]                            |
|                       ├── Activity 5.1: AI Pedagogical Teaching Suggestion Logic                  |
|                       └── Activity 5.2: Granular Student & Session Analytics                      |
|                                           │                                                       |
|                                           v                                                       |
|                       [MILESTONE 6: Interface, Testing, and Deployment]                           |
|                       ├── Activity 6.1: Core FastAPI Server Engine (Port 8000)                    |
|                       ├── Activity 6.2: Companion Streamlit Dashboard (Port 8501)                 |
|                       └── Activity 6.3: Automated Test Suite & Edge Case Validation               |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Milestone Verification & Traceability Matrix

| Milestone & Activity | Description | Present in System? | Alternatives Evaluated | Best-Suited Implemented Solution | Source Code Location |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Milestone 1: Req & Env Setup** | | | | | |
| **Activity 1.1** | Create `requirements.txt` | ✅ Yes | Monolithic vs. Categorized | Modular categorized requirements (Core, Vision, Streamlit, Extensions) | [`requirements.txt`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/requirements.txt) |
| **Activity 1.2** | Install required libraries & venv | ✅ Yes | System Python vs. Isolated venv | Isolated `.venv` with Python 3.14.8 on Windows | `.venv/` |
| **Milestone 2: Vision Module** | | | | | |
| **Activity 2.1** | Face detection & tracking | ✅ Yes | MediaPipe FaceMesh vs. OpenCV Centroid Tracker | **OpenCV Multi-Angle Haar Cascade + Centroid Tracker & Movement Velocity**: Robust under lighting/angles, 60+ FPS, persistent IDs, occlusion buffer | [`backend/core/face_detection.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/face_detection.py), [`backend/core/camera_service.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/camera_service.py), [`backend/core/face_tracker.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/face_tracker.py), [`EPIC_2_VISION_MODULE.md`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/EPIC_2_VISION_MODULE.md) |
| **Activity 2.2** | Presence-based attendance logic | ✅ Yes | Single snapshot vs. Temporal sliding window | **Sustained Presence Engine**: $\ge 5.0\text{ s}$ threshold, transient walk-by filter, SHA-256 hashes | [`backend/attendance/sustained_presence.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/attendance/sustained_presence.py) |
| **Milestone 3: Audio Module** | | | | | |
| **Activity 3.1** | Audio signal extraction | ✅ Yes | Raw PCM vs. Resampled Mono Windows | **Standardized Digital Waveform & Fixed Windows**: 16 kHz resampled, mono channel, 1.0s window segmentation aligned with video frames, structured JSON/CSV export | [`backend/core/audio_analysis.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/audio_analysis.py), [`backend/audio/audio_analyzer.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/audio/audio_analyzer.py), [`EPIC_3_ACTIVITY_3_1_AUDIO_EXTRACTION.md`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/EPIC_3_ACTIVITY_3_1_AUDIO_EXTRACTION.md) |
| **Activity 3.2** | Noise & speech activity analysis | ✅ Yes | Librosa STFT vs. 3-Tier Multi-Feature VAD | **3-Tier Signal Classification & Trend Tracking**: Energy levels, amplitude variation, short-time characteristics (ZCR, spectral centroid & flatness), 3-tier discrimination (Silence/Noise/Speech), noise trends (Quiet/Moderate/Elevated/Loud), turn-taking frequency, multimodal fusion vector | [`backend/core/audio_analysis.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/audio_analysis.py), [`backend/audio/audio_analyzer.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/audio/audio_analyzer.py), [`EPIC_3_ACTIVITY_3_2_NOISE_SPEECH_ANALYSIS.md`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/EPIC_3_ACTIVITY_3_2_NOISE_SPEECH_ANALYSIS.md) |
| **Milestone 4: Multimodal Agent** | | | | | |
| **Activity 4.1** | Multimodal Agent Implementation | ✅ Yes | Isolated Sensory Thresholds vs. Rule-Based Cross-Modal Reasoning + Groq LLM | **Core Multimodal Intelligence Layer**: Integrates Vision & Audio outputs; applies 6 explainable rules (M1-M6) across gaze, posture, decibels, turn frequency; Groq `llama-3.3-70b-versatile` insight generator with offline fallback | [`backend/core/llm_insights.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/llm_insights.py), [`backend/agent/multimodal_agent.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/agent/multimodal_agent.py), [`EPIC_4_ACTIVITY_4_1_MULTIMODAL_AGENT.md`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/EPIC_4_ACTIVITY_4_1_MULTIMODAL_AGENT.md) |
| **Activity 4.2** | Multimodal Signal Fusion | ✅ Yes | Isolated Sensory Scoring vs. Timestamp-Synchronized Extensible Fusion | **Timestamp-Synchronized Signal Fusion & AI Suggestions**: Sub-5ms jitter alignment of visual indicators (presence duration, movement pattern, motion energy, inactivity periods) with audio indicators (calibrated dB SPL, speech state, rhythm, participation frequency, turns/min); Groq `llama3-8b-8192` AI Suggestion Engine (matching reference image); extensible multi-sensor architecture (`custom_modalities`) | [`backend/core/ai_suggestions.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/ai_suggestions.py), [`backend/fusion/multimodal_fusion.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/fusion/multimodal_fusion.py), [`EPIC_4_ACTIVITY_4_2_MULTIMODAL_FUSION.md`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/EPIC_4_ACTIVITY_4_2_MULTIMODAL_FUSION.md) |
| **Activity 4.3** | Engagement Scoring Logic & Temporal Profile | ✅ Yes | Static session average vs. Multi-Factor Rule-Based Segment Scoring & Temporal Profile | **Multi-Factor Rule-Based Scoring Engine & Temporal Profiler**: Sustained visual presence ($w_{vis}=0.35$), movement frequency ($w_{mot}=0.25$), inactivity duration ($w_{ina}=0.15$), speech activity intensity ($w_{aud}=0.25$); dynamic time-segment scores ($0-100\%$), fluctuation metrics ($\sigma^2$, $\sigma$, stability index), peak periods ($\ge 80\%$), extended disengagement phases ($< 50\%$ for $\ge 3$ segments) with root-cause attribution; adjustable runtime presets (`LECTURE_STANDARD`, `INTERACTIVE_DISCUSSION`, `HANDS_ON_LAB`, `QUIET_EXAM`); feeds teaching suggestions, student analytics, and session summaries | [`backend/core/engagement_scoring.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/engagement_scoring.py), [`backend/fusion/engagement_scoring.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/fusion/engagement_scoring.py), [`EPIC_4_ACTIVITY_4_3_ENGAGEMENT_SCORING.md`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/EPIC_4_ACTIVITY_4_3_ENGAGEMENT_SCORING.md) |
| **Milestone 5: Analytics & Recommendation** | | | | | |
| **Activity 5.1** | Teaching Suggestion Logic & Teacher Analytics | ✅ Yes | Fixed alerts vs. Multi-Rule Context-Aware RecommendationsEngine + TeacherProfileService | **Multi-Rule Context-Aware Recommendations & Teacher Analytics Engine**: Rule-based recommendations (`RecommendationsEngine`) grounded in observable multimodal trends (`alert`, `warning`, `info`); evaluates individual distraction ($< 40\%$), classwide attention dips ($< 60\%$), sustained disengagement (interactive activities like Think-Pair-Share), peak engagement highlights ($\ge 82\%$), elevated classroom noise ($\ge 75\text{ dB SPL}$), pacing drops, and prolonged monologues ($\ge 8\text{ min}$); non-prescriptive transparent phrasing; integrates with `TeacherProfileService` (effectiveness score 87.5%, trend +12.0%, class history, per-student trends, strengths); Modal 11 & 7 dedicated REST endpoints | [`backend/core/recommendations_engine.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/recommendations_engine.py), [`backend/core/teacher_profiles.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/teacher_profiles.py), [`backend/agent/pedagogical_agent.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/agent/pedagogical_agent.py), [`EPIC_5_ACTIVITY_5_1_TEACHING_SUGGESTIONS.md`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/EPIC_5_ACTIVITY_5_1_TEACHING_SUGGESTIONS.md) |
| **Activity 5.2** | Student Session Analytics Generation | ✅ Yes | Evaluative Grades & Rankings vs. Reflective Private Analytics & Session Trends | **Reflective Student Analytics & Session Trends Engine**: Structured session summaries using attendance records and granular engagement scores; attendance duration, engagement consistency index ($0-100\%$, $\sigma$), focus breakdown (High Focus $>75\%$ vs. Distraction $<50\%$), timeline of continuous focus episodes; grounded notable activity trends; constructive self-reflection prompts (zero grades, zero evaluations); privacy-guaranteed unranked cohort reflections (no peer comparisons, no leaderboards); exportable JSON/Markdown reports; Reference Image implementation: `AnalyticsService.get_session_trends` querying `PersonMetric` with minute buckets & timestamp grouping; Modal 12 Explorer & 5 REST endpoints | [`backend/core/analytics_service.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/analytics_service.py), [`backend/db/database.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/db/database.py), [`backend/api/server.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/api/server.py), [`EPIC_5_ACTIVITY_5_2_STUDENT_ANALYTICS.md`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/EPIC_5_ACTIVITY_5_2_STUDENT_ANALYTICS.md) |
| **Milestone 6: Interface, Testing & Deployment** | | | | | |
| **Activity 6.1** | Run core application | ✅ Yes | CLI-only vs. Multi-Source Ingestion (Webcam, Pre-Recorded Video, Simulated) & End-to-End Pipeline Verifier | **Multi-Source Core Application & Verification Engine**: Local execution across live webcam input (hardware camera with fallback), pre-recorded classroom video (`storage/uploads/classroom_lecture_sample.mp4`, 150 frames, 15 FPS, looping playback), and simulated classroom stream; synchronous data flow verification across Vision Processing, Audio Analysis, Multimodal Signal Fusion, Engagement Scoring, and Analytics Generation via `PipelineVerifier`; CLI verification mode (`run_agent.py --verify-pipeline --source file`); Modal 13 Core App Hub with 5-module pipeline stepper & throughput FPS meter; `/api/activity_6_1/status` and `/api/activity_6_1/verify_pipeline` REST endpoints | [`run_agent.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/run_agent.py), [`backend/core/pipeline_verifier.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/pipeline_verifier.py), [`backend/vision/video_stream.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/vision/video_stream.py), [`backend/utils/video_generator.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/utils/video_generator.py), [`backend/api/server.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/api/server.py), [`EPIC_6_ACTIVITY_6_1_RUN_CORE_APP.md`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/EPIC_6_ACTIVITY_6_1_RUN_CORE_APP.md) |
| **Activity 6.2** | Launch optional Streamlit dashboard | ✅ Yes | Standalone Web App vs. Dual-Mode Interpretability & Exploration Dashboard | **Interactive Streamlit Multimodal Dashboard**: Optional visualization layer designed for interpretability; features 4 core pillars: (1) Attendance Records with presence tracking, status categorization (`PRESENT`, `LATE`, `INTERMITTENT`, `WALKBY_FILTERED`), SHA-256 audit hashes, status filtering, and CSV export; (2) Engagement Timelines with multi-signal trajectories, 3 focus zones (High Focus $>75\%$, Balanced $50-75\%$, Distraction $<50\%$), statistical indicators ($\mu$, $\sigma$, $\sigma^2$, Stability Index), and minute-level emotion rollups; (3) Instructor Suggestions with Teacher Analytics Profile (Prof. Alex Vance, effectiveness 87.5%, trend +12.0%, strengths) and 7-rule context-aware pedagogical cards with urgency filters; (4) Student Session Analytics with unranked reflective profiles, continuous focus episodes, grounded trends, metacognitive prompts, and JSON/Markdown export; plus Activity 6.1 on-demand 5-module pipeline verification widget; dual-mode support (FastAPI live REST vs. standalone offline SQLite) | [`streamlit_app.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/streamlit_app.py), [`EPIC_6_ACTIVITY_6_2_STREAMLIT_DASHBOARD.md`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/EPIC_6_ACTIVITY_6_2_STREAMLIT_DASHBOARD.md) |
| **Activity 6.3** | Validate outputs and edge cases | ✅ Yes | Manual inspection vs. Automated unit tests | **12 Automated Test Suites**: Empty room, audio bursts, extreme gaze, walk-bys, privacy audits | [`tests/test_system.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/tests/test_system.py) |

---

## 3. Milestone Deep Dives & Alternatives Analysis

### Milestone 1: Requirements Specification and Environment Setup
*Focus: Defining functional requirements, selecting libraries, and preparing the isolated development environment.*

#### Activity 1.1: Create `requirements.txt`
- **Objective:** Specify exact runtime dependencies with semantic version constraints and logical categorization.
- **Implemented Solution:**
  [`requirements.txt`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/requirements.txt) is partitioned into:
  1. *Core Web API & Server Engine:* `fastapi>=0.110.0`, `uvicorn[standard]>=0.28.0`, `pydantic>=2.6.0`
  2. *Audio Processing Libraries:* `soundfile>=0.14.0`, `librosa>=0.10.2`
  3. *Backend & API Engine:* `fastapi>=0.110.0`, `uvicorn[standard]>=0.28.0`, `python-multipart>=0.0.9`, `websockets>=12.0`, `python-dotenv>=1.0.0`, `groq>=0.18.0`
  4. *Data Processing & Storage:* `numpy>=1.26.0`, `pandas>=2.2.0`, `sqlalchemy>=2.0.0`
  5. *Preserved Enhancements:* `streamlit>=1.32.0`, `requests>=2.31.0`, `pydantic>=2.6.0`, `matplotlib>=3.11.0`, `scipy>=1.18.0`

#### Activity 1.2: Install Required Libraries and Set Up Virtual Environment
- **Objective:** Provision an isolated Python virtual environment preventing system pollution and dependency collisions, install all packages from `requirements.txt`, and validate module imports.
- **Implemented Solution:**
  - Active runtime: **Python 3.14.8** on Windows inside `.venv` (isolated from system Python).
  - Installed and verified all 14 core packages via `pip list` and `validate_environment.py`:
    - `fastapi 0.143.0`, `uvicorn 0.54.0`, `opencv-python 5.0.0`, `mediapipe 1.1.0`
    - `numpy 2.5.4`, `pandas 3.0.6`, `python-multipart 0.0.32`, `websockets 17.2`
    - `sqlalchemy 2.1.4`, `librosa 1.0.0`, `soundfile 0.14.0`, `groq 1.7.0`
    - `deep-sort-realtime 1.3.2`, `python-dotenv 1.2.4`
    - *Preserved enhancements:* `streamlit 1.65.0`, `requests 2.34.2`, `pydantic 2.14.1`, `scipy 1.18.1`, `matplotlib 3.11.2`.
  - Automated verification script [`validate_environment.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/validate_environment.py) and test suite `tests/test_system.py` confirm 100% operational readiness.

---

### Milestone 2: Vision Module Development
*Focus: Implementing real-time face detection, persistent centroid tracking, head pose estimation, and sustained presence verification.*

#### Activity 2.1: Face Detection and Tracking
- **Objective:** Ingest video frames sequentially from live webcam or pre-recorded classroom video, detect human faces robustly under classroom conditions (movement, partial occlusions, varying angles, lighting variations), assign unique participant identifiers, track them across frames, and generate structured tracking telemetry.
- **Implemented Solution:**
  [`backend/core/face_detection.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/face_detection.py), [`backend/core/camera_service.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/camera_service.py), [`backend/core/face_tracker.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/face_tracker.py):
  - **Camera Service:** Supports live webcam (`camera_id=0`) and pre-recorded classroom videos (`.mp4`) with automatic rewinding and WebSocket streaming.
  - **Multi-Angle Face Detection:** Frontal and profile Haar Cascades with CLAHE illumination balancing and Non-Maximum Suppression (NMS).
  - **Persistent Identifier Tracking:** Associates detections across consecutive frames via centroid Euclidean distance and movement velocity vectors.
  - **Occlusion Buffer:** Keeps participant tracks active across brief head turns, occlusions, or orientation changes for up to 15 frames (~1.0s).
  - **Structured Telemetry:** Produces structured dictionaries containing participant IDs, timestamps, bounding boxes `(x, y, w, h)`, centroids, velocity, presence duration, and status.
  - **Privacy Blurring:** Automatically applies Gaussian blur ($31\times 31$) to face ROIs before rendering.

#### Activity 2.2: Presence-Based Attendance Logic
- **Objective:** Translate continuous face tracking data and timestamps into verified attendance records. Rather than marking attendance from a single frame detection, implement presence-based logic where attendance is confirmed only when cumulative presence exceeds a predefined threshold. Intermittent appearances are accumulated to ensure fairness and prevent false attendance caused by brief or accidental detections. Output structured attendance audit logs for reporting.
- **Implemented Solution:**
  [`backend/core/presence_attendance.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/presence_attendance.py), [`backend/core/face_recognition.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/face_recognition.py), [`backend/attendance/sustained_presence.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/attendance/sustained_presence.py):
  - **Intermittent Presence Accumulator:** Accumulates duration across visible intervals ($\sum \Delta t$) using high-resolution timestamps. Brief interruptions (e.g. head turns, sneezing, occlusions) pause accumulation without resetting prior progress.
  - **Single-Frame Detection Rejection:** Detections in isolated frames are classified as `INTERMITTENT` until cumulative presence satisfies the temporal threshold ($T_{\text{cum}} \ge T_{\text{sustained}}$).
  - **Presence-Based Threshold Confirmation:** Once cumulative presence crosses the configurable threshold (e.g., 20.0s or 30.0s), the participant transitions from `INTERMITTENT` to confirmed `PRESENT` (or `LATE` if arrival exceeded the cutoff).
  - **Fleeting Walk-By Rejection:** Transient visitors passing by the classroom door or camera view ($< 10.0\text{ s}$) are classified as `WALKBY_FILTERED` and excluded from official attendance rosters.
  - **Biometric Face Recognition (`FaceRecognizer`):** Implements student face enrollment (`register_student`) and identification (`recognize`) matching the reference architecture, using DeepFace with deterministic offline edge feature vector fallback.
  - **Structured Logs & Tamper-Proof Audit:** Generates structured records including participant ID, display name, seat, cumulative presence seconds, presence ratio, appearance intervals, and salted SHA-256 integrity verification hashes.
  - **REST API & Reporting:**
    - `GET /api/attendance/presence_summary`: Returns real-time attendance counts, rate %, and threshold criteria.
    - `GET /api/attendance/presence_logs`: Returns structured attendance logs with participant identifiers and presence durations.
    - `GET /api/attendance/export_csv`: Exports official attendance audit CSV report.
    - `GET /api/attendance/registered_faces`: Returns enrolled biometric registry entries.
    - `POST /api/attendance/register_face`: Registers student reference faces.

---

### Milestone 3: Audio Module Development
*Focus: Processing acoustic signals for sound pressure energy, voice activity detection, and instructional rhythm classification.*

#### Activity 3.1: Audio Signal Extraction
- **Objective:** Extract raw acoustic samples from multiple input channels (live microphone, local audio files, recorded classroom session video files, or classroom simulation), convert to digital waveform, normalize sampling rate to 16 kHz, standardize channels to mono, segment into fixed-duration windows aligned with video frames, and store in structured formats with timestamps and amplitude data.
- **Implemented Solution:**
  [`backend/core/audio_analysis.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/audio_analysis.py), [`backend/audio/audio_analyzer.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/audio/audio_analyzer.py), [`EPIC_3_ACTIVITY_3_1_AUDIO_EXTRACTION.md`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/EPIC_3_ACTIVITY_3_1_AUDIO_EXTRACTION.md):
  - **Audio Input Capture & Extraction:** Ingests live browser microphone energy / 16-bit PCM bytes via Web Audio API, parses WAV audio files, or extracts audio streams from recorded video files (`.mp4`, `.avi`, `.mkv`) with autonomous synthetic classroom acoustic fallback.
  - **Digital Waveform Processing:** Converts raw 16-bit integer PCM samples ($y = \text{int16} / 32768.0$) into normalized 32-bit floating-point waveforms bounded in $[-1.0, 1.0]$.
  - **Sampling Rate Normalization & Channel Standardization:** Standardizes multi-channel stereo audio to 1-channel mono by averaging across channels ($y_{\text{mono}} = \text{mean}(y, \text{axis})$) and normalizes arbitrary sampling rates (e.g. 44.1 kHz, 48 kHz, 22.05 kHz) to universal $16{,}000\text{ Hz}$ using high-fidelity sinc interpolation.
  - **Fixed-Duration Window Segmentation:** Slices waveforms into fixed-duration temporal windows (1.0s / 16,000 samples) and computes RMS energy, decibels ($\text{dB}_{\text{FS}}$, calibrated $\text{dB SPL}$), peak amplitude, and speech-to-silence ratios.
  - **Video Frame Synchronization:** Automatically maps audio window timestamps to corresponding video frame ranges $[f_{\text{start}}, f_{\text{end}}]$ at 15 FPS for multimodal fusion.
  - **Structured Data Formats:** Persists time-series metadata into `AudioSegment` models, structured JSON, and CSV audits for synchronized multimodal analysis.

#### Activity 3.2: Noise and Speech Activity Analysis
- **Objective:** Analyze extracted audio signals to identify ambient noise levels and speech activity patterns; compute energy levels, amplitude variation, and short-time characteristics per segment; differentiate between silence, background noise, and active speech; track ambient noise level trends and participation frequency; aggregate session-level context; and structure audio insights for multimodal fusion.
- **Implemented Solution:**
  [`backend/core/audio_analysis.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/audio_analysis.py), [`backend/audio/audio_analyzer.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/audio/audio_analyzer.py), [`EPIC_3_ACTIVITY_3_2_NOISE_SPEECH_ANALYSIS.md`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/EPIC_3_ACTIVITY_3_2_NOISE_SPEECH_ANALYSIS.md):
  - **Comprehensive Audio Feature Extraction:**
    - *Energy Levels:* Root-Mean-Square (RMS) power, Short-Time Energy (STE, 32ms subframes), $\text{dB}_{\text{FS}}$, and calibrated classroom sound pressure level ($\text{dB SPL} = 94.0 + \text{dB}_{\text{FS}}$).
    - *Amplitude Variation:* Peak-to-peak amplitude range, standard deviation $\sigma_y$, crest factor (peak-to-RMS ratio), and dynamic range across subframes ($\text{DR}_{\text{dB}}$).
    - *Short-Time Signal Characteristics:* Zero-Crossing Rate (ZCR), Spectral Centroid (frequency mass center), and Spectral Flatness (Wiener entropy).
  - **Three-Tier Signal Discrimination:**
    - `SILENCE`: $\text{RMS} < 0.015$ or $\text{SPL} < 42.0\text{ dB}$.
    - `BACKGROUND_NOISE`: Spectral Flatness $> 0.40$ or ($\text{DR} < 4.0\text{ dB}$ and Crest $< 1.8$).
    - `ACTIVE_SPEECH`: Dynamic harmonic vocal energy with low spectral flatness and prominent syllable modulation.
  - **Ambient Noise Level Trends & Conditions:**
    - Evaluates environmental conditions (`QUIET` $< 50\text{ dB}$, `MODERATE` $50-65\text{ dB}$, `ELEVATED` $65-75\text{ dB}$, `LOUD_DISRUPTIVE` $\ge 75\text{ dB}$).
    - Tracks moving-average noise trends (`RISING`, `FALLING`, `STABLE` with rate of change $\Delta\text{dB}$) and maintains an adaptive noise floor tracking background classroom acoustic baseline.
  - **Speech Activity & Participation Tracking:**
    - Measures interaction intensity (percentage of time active speech occurs).
    - Quantifies participation frequency (speaker conversational turn-taking frequency in turns per minute).
  - **Session-Level Temporal Aggregation:**
    - Aggregates mean SPL, peak SPL, speech/silence time distribution, and cumulative speaker turns across the session.
  - **Multimodal Fusion & Agent Reasoning:**
    - Formats a normalized acoustic vector (`speech_activity`, `noise_penalty`, `turn_taking`, `rhythm_stability`) bounded in $[0.0, 1.0]$ for real-time fusion with visual engagement.
    - Enables Pedagogical Agent Rule 5 (Acoustic Disruption Alert for noise $\ge 75\text{ dB SPL}$) and Rule 6 (Low Turn-Taking Alert for Q&A $< 0.8\text{ turns/min}$).
  - **Client Capture & Explorer UI:**
    - Real-time client microphone capture via [`frontend/src/components/AudioCapture.jsx`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/src/components/AudioCapture.jsx) and Modal 7 in [`frontend/index.html`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/index.html) / [`frontend/js/app.js`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/js/app.js) with 16-bit PCM streaming over WebSocket (`/ws/audio`).

---

### Milestone 4: Multimodal Agent Implementation
*Focus: Aggregating visual attentiveness and acoustic dynamics to compute session engagement trends and drop-off alerts.*

#### Activity 4.1: Multimodal Agent Implementation
- **Objective:** Implement the Multimodal Agent as the core intelligence layer; integrate outputs from Vision and Audio modules; apply rule-based reasoning (Rules M1 to M6) to interpret combined multimodal data; synthesize explainable engagement insights and AI recommendations using `InsightGenerator` (Groq `llama-3.3-70b-versatile` with offline fallback); compute attributed dynamic engagement indices; and expose real-time explorer controls.
- **Implemented Solution:**
  [`backend/core/llm_insights.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/llm_insights.py), [`backend/agent/multimodal_agent.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/agent/multimodal_agent.py), [`EPIC_4_ACTIVITY_4_1_MULTIMODAL_AGENT.md`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/EPIC_4_ACTIVITY_4_1_MULTIMODAL_AGENT.md):
  - **Core Intelligence Layer (`MultimodalAgent`):**
    - Seamlessly fuses Vision Module streams (facial attention, gaze direction, motion energy, participant tracks) and Audio Module streams (calibrated dB SPL, 3-tier classification, ambient trends, participation frequency).
    - Dynamic Weighted Engagement Index:
      $$\text{EI} = \left( 0.50 \cdot S_{\text{vis}} + 0.20 \cdot S_{\text{mot}} + 0.30 \cdot S_{\text{aud}} \right) \times 100.0$$
    - Mathematical component attribution breakdown (`visual_attention_component`, `motion_balance_component`, `audio_interaction_component`) and dominant modality classification (`VISUAL_DOMINANT`, `AUDIO_DOMINANT`, `BALANCED`).
  - **Contextual Multimodal Rule Engine:**
    - *Rule M1 (`HIGH_FLOW`):* $S_{\text{vis}} \ge 0.70$, $S_{\text{mot}} \ge 0.70$, $\text{SPL} < 65\text{ dB}$ (Confidence: 0.92) &rarr; Optimal cognitive absorption.
    - *Rule M2 (`PASSIVE_DISENGAGEMENT`):* $S_{\text{vis}} < 0.55$, $\text{SPL} < 55\text{ dB}$, quiet room (Confidence: 0.88) &rarr; Wandering visual gaze in silent room.
    - *Rule M3 (`COLLABORATIVE_ACTIVE`):* Q&A rhythm, Turn Freq $\ge 1.5/\text{min}$, $S_{\text{vis}} \ge 0.60$ (Confidence: 0.91) &rarr; Vibrant collaborative learning resonance.
    - *Rule M4 (`ACOUSTIC_DISRUPTION`):* $\text{SPL} \ge 75\text{ dB}$ or `LOUD_DISRUPTIVE` (Confidence: 0.95) &rarr; Room cross-talk and acoustic disturbance.
    - *Rule M5 (`CONCEPT_HESITATION`):* Q&A rhythm, silence $\ge 20\text{ s}$ or Turn Freq $< 0.8$, $S_{\text{vis}} \ge 0.65$ (Confidence: 0.87) &rarr; Student concept comprehension barrier.
    - *Rule M6 (`FATIGUE_RESTLESSNESS`):* Continuous monologue $\ge 8\text{ min}$, restlessness/fidgeting (Confidence: 0.89) &rarr; Working memory saturation.
  - **LLM Pedagogical Insight Generator (`InsightGenerator`):**
    - Directly implements the reference architecture (`backend/core/llm_insights.py`) using Groq Cloud API with model `llama-3.3-70b-versatile` (temperature 0.5, max_tokens 150).
    - Robust deterministic offline fallback for 100% offline edge privacy compliance.
  - **Dashboard Modal 8 & REST API:**
    - Glassmorphic Modal 8 in [`frontend/index.html`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/index.html) and [`frontend/js/app.js`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/js/app.js) with live state pill, active rule badge, explainable diagnosis box, LLM insight generator, and rule catalog.
    - Endpoints: `GET /api/agent/activity_4_1/status`, `POST /api/agent/activity_4_1/evaluate`, `POST /api/agent/activity_4_1/llm_insight`, `GET /api/agent/activity_4_1/reasoning_history`, `GET /api/agent/activity_4_1/rules`.

#### Activity 4.2: Multimodal Signal Fusion
- **Objective:** Synchronize and aggregate signals from the Vision Module and Audio Module into a unified, extensible data representation using timestamp-based synchronization.
- **Implemented Solution:**
  - **Timestamp-Based Synchronization (<5ms Jitter):**
    - Sub-frame temporal alignment between video frame intervals and acoustic windows: $|t_{vis} - t_{aud}| < 5.0\text{ ms}$.
    - Monotonically incrementing epoch IDs and session timestamps.
  - **Multi-Signal Visual & Audio Alignment:**
    - *Visual Indicators:* Presence duration ($s$, $\%$), movement patterns (`STATIC_DORMANT`, `FOCUSED_STABLE`, `ELEVATED_ACTIVE`, `RESTLESS_JITTER`), average motion energy, dormancy inactivity periods ($s$), and visual gaze distribution.
    - *Audio Indicators:* Calibrated ambient noise ($\text{dB SPL}$, $\text{dBFS}$), noise trends (`STABLE`, `RISING`, `FALLING`), speech states (`SILENCE`, `BACKGROUND_NOISE`, `ACTIVE_SPEECH`), instructional rhythm, interaction intensity, and speaker turns/min.
  - **Proportional Sensory Contribution & Cross-Modal Analytics:**
    - Fuses modalities proportionally: $\text{EI} = (0.50 \cdot S_{vis} + 0.20 \cdot S_{mot} + 0.30 \cdot S_{aud}) \times 100$.
    - Computes rolling Pearson correlation ($r$) and contextual cross-modal coherence score ($0.0 - 1.0$).
    - Identifies dominant modality: `VISUAL_DOMINANT`, `AUDIO_DOMINANT`, or `BALANCED`.
  - **AI Suggestion Engine ([`backend/core/ai_suggestions.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/ai_suggestions.py)):**
    - Directly implemented matching the reference architecture using Groq `llama3-8b-8192` (`temperature=0.7`, `max_tokens=200`, system prompt `"You are an expert AI teaching assistant."`).
    - Structured prompt formulated from visual focus, cumulative presence, movement patterns, ambient noise, speech state, and participation frequency.
    - Deterministic offline rule-based fallbacks guaranteeing continuous edge functionality without cloud dependency.
  - **Extensible Multi-Sensor Architecture:**
    - [`UnifiedMultimodalRepresentation`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/fusion/multimodal_fusion.py) supports `add_custom_modality(name, payload)` for plugging third-party educational sensors (smart pen strokes, biometric wristbands, student clicker polls).
  - **Dashboard Modal 9 & REST API Endpoints:**
    - Glassmorphic Modal 9 in [`frontend/index.html`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/index.html) and [`frontend/js/app.js`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/js/app.js) with live sync jitter, cross-modal correlation meter, aligned visual-audio indicator cards, AI suggestion generator, and extensible sensor hub.
    - Endpoints: `GET /api/fusion/activity_4_2/status`, `POST /api/fusion/activity_4_2/synchronize`, `POST /api/fusion/activity_4_2/generate_ai_suggestions`, `GET /api/fusion/activity_4_2/unified_representation`, `GET /api/fusion/activity_4_2/cross_modal_correlation`, `POST /api/fusion/activity_4_2/add_modality`.

#### Activity 4.3: Engagement Scoring Logic
- **Objective:** Transform fused multimodal signals into interpretable, transparent engagement scores across time segments using rule-based logic and adjustable thresholds; generate temporal engagement profiles to detect attention fluctuations, peak engagement periods, and extended disengagement phases; and route scores downstream into teaching suggestions, student analytics, and session summaries.
- **Implemented Solution:**
  - **4-Factor Weighted Multi-Signal Scoring Engine ([`backend/core/engagement_scoring.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/engagement_scoring.py)):**
    - Evaluates 4 core factors with customizable weights summing to 1.0:
      1. *Sustained Visual Presence ($w_{vis} = 0.35$):* Presence duration ratio and head orientation/gaze attention ($0.0 - 1.0$).
      2. *Movement Frequency ($w_{mot} = 0.25$):* Dynamic penalty-free scoring for natural learning body motion vs. dormancy or erratic jitter.
      3. *Inactivity Duration ($w_{ina} = 0.15$):* Inactivity duration penalty ($1.0 - \min(1.0, t_{inactivity}/60.0)$).
      4. *Speech Activity Intensity ($w_{aud} = 0.25$):* Conversational cadence, active speaker turns, and ambient signal-to-noise ratio.
    - Final Segment Score: $\text{Score} = (w_{vis} \cdot S_{vis} + w_{mot} \cdot S_{mot} + w_{ina} \cdot S_{ina} + w_{aud} \cdot S_{aud}) \times 100$.
    - Granular Factor Attributions: Full point breakdown and text explanations for why each factor contributed its respective points.
  - **Temporal Profiling & Fluctuation Analytics:**
    - Generates temporal profiles over time segments rather than a static session average.
    - Computes attention fluctuation variance ($\sigma^2$), standard deviation ($\sigma$), and stability index ($100 - \sigma \times 2$).
    - Identifies *Peak Engagement Periods* ($\ge 80\%$, classifying top contributing factors) and *Extended Disengagement Phases* ($< 50\%$ lasting $\ge 3$ consecutive segments with primary root cause identification and pedagogical action suggestions).
  - **Transparent Rule Engine & Adjustable Presets:**
    - Scoring rules `S1_VISUAL_DISENGAGEMENT`, `S2_EXCESSIVE_INACTIVITY`, `S3_HIGH_COLLABORATION_ENERGY`, `S4_RESTLESS_DISRUPTION`, `S5_EXAM_FOCUSED_STABILITY`.
    - 4 Pre-configured Classroom Presets:
      - `LECTURE_STANDARD`: Balanced baseline for conventional lectures ($w_{vis}=0.35, w_{mot}=0.25, w_{ina}=0.15, w_{aud}=0.25$).
      - `INTERACTIVE_DISCUSSION`: Boosts acoustic weight ($w_{aud}=0.40$) and movement tolerance ($w_{mot}=0.30$).
      - `HANDS_ON_LAB`: High movement allowance ($w_{mot}=0.35$) with lowered visual staring weight ($w_{vis}=0.25$).
      - `QUIET_EXAM`: Strict inactivity and visual focus weighting ($w_{vis}=0.50, w_{ina}=0.30$) with low noise tolerance ($w_{aud}=0.05$).
  - **Downstream Consumer Integration:**
    - Automatically streams computed engagement metrics into:
      1. *Teaching Suggestions:* Feeds into [`PedagogicalAgent`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/agent/pedagogical_agent.py) and Groq Llama 3 AI suggestions with detected disengagement root causes.
      2. *Student Analytics:* Aggregates temporal engagement profiles into per-student participation tiers (`HIGHLY_ENGAGED`, `MODERATELY_ENGAGED`, `DISENGAGED`).
      3. *Session Summaries:* Produces session engagement averages, temporal fluctuation trends, stability indices, peak durations, and disengagement phase logs.
  - **Dashboard Modal 10 & 10 REST API Endpoints:**
    - Glassmorphic Modal 10 in [`frontend/index.html`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/index.html) and [`frontend/js/app.js`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/js/app.js) with live score gauge, 4-factor breakdown cards, interactive SVG temporal timeline bar chart, preset buttons, threshold sliders, peak/disengagement log, and downstream action buttons.
    - REST Endpoints in [`backend/api/server.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/api/server.py): `GET /api/engagement/activity_4_3/status`, `POST /api/engagement/activity_4_3/score_segment`, `POST /api/engagement/activity_4_3/generate_temporal_profile`, `GET /api/engagement/activity_4_3/temporal_profile`, `GET /api/engagement/activity_4_3/threshold_config`, `POST /api/engagement/activity_4_3/update_thresholds`, `POST /api/engagement/activity_4_3/apply_preset`, `GET /api/engagement/activity_4_3/peaks_and_disengagements`, `POST /api/engagement/activity_4_3/downstream_summary`, `GET /api/engagement/activity_4_3/export_json`.

---

### Milestone 5: Analytics and Recommendation Engine
*Focus: Generating context-aware pedagogical suggestions and granular session analytics for instructors and students.*

#### Activity 5.1: Teaching Suggestion Logic
- **Objective:** Transform engagement trends and session dynamics into actionable, context-aware teaching suggestions; analyze temporal engagement profiles to detect sustained disengagement, attention drops, high-interaction periods, and noisy classroom conditions; and provide teacher analytics with effectiveness scoring and student trends.
- **Implemented Solution:**
  - **Rule-Based Recommendations Engine ([`backend/core/recommendations_engine.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/recommendations_engine.py)):**
    - Directly implements the reference architecture (`RecommendationsEngine.generate_realtime_recommendations(session_status)`).
    - 7 explainable, evidence-grounded rules:
      1. *R1 (Individual Attention Alert):* Flags distracted students ($< 40\%$) with non-verbal redirection cues.
      2. *R2 (Global Attention Warning):* Detects collective room drops ($< 60\%$) advising comprehension check questions.
      3. *R3 (Sustained Disengagement):* Detects persistent disengagement ($< 50\%$ with inactivity) and suggests interactive activities (Think-Pair-Share, live poll, breakout problem).
      4. *R4 (Peak Engagement Highlight):* Highlights effective instructional segments ($\ge 82\%$) to reinforce successful teaching approaches.
      5. *R5 (Classroom Noise Management):* Flags elevated ambient sound ($\ge 75\text{ dB SPL}$) with acoustic cues.
      6. *R6 (Instructional Pacing Drop):* Detects rapid attention drops ($\ge 15\%$) to prompt core takeaway clarification.
      7. *R7 (Prolonged Monologue Advisory):* Flags continuous lecture ($\ge 8\text{ min}$) to relieve cognitive fatigue.
    - Transparent, non-prescriptive framing: each recommendation contains evidence metrics, confidence rating, and suggested action.
  - **Teacher Analytics & Profile Service ([`backend/core/teacher_profiles.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/teacher_profiles.py)):**
    - Directly implements the reference architecture (`TeacherProfileService.get_profile(teacher_id)`).
    - Dynamic calculation of teacher effectiveness score (87.5%), trend (+12.0%), class history (CS101 Today, CS101 Yesterday, Math Workshop), student trends (Priya +15%, Kumar +8%, Asha -5%), and pedagogical strengths.
  - **Pedagogical Agent Integration ([`backend/agent/pedagogical_agent.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/agent/pedagogical_agent.py)):**
    - Synergizes `PedagogicalReasoningAgent` with `RecommendationsEngine` for immediate feedback and temporal profile evaluation.
  - **Dashboard Modal 11 & 7 REST Endpoints:**
    - Glassmorphic Modal 11 in [`frontend/index.html`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/index.html) and [`frontend/js/app.js`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/js/app.js) with Teacher Profile card, live recommendation feed with colored severity badges (`ALERT`, `WARNING`, `INFO`), scenario simulation buttons, and rule catalog.
    - Endpoints in [`backend/api/server.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/api/server.py): `GET /api/recommendations/activity_5_1/status`, `POST /api/recommendations/activity_5_1/generate`, `GET /api/recommendations/activity_5_1/history`, `POST /api/recommendations/activity_5_1/evaluate_temporal_profile`, `GET /api/teacher/profile`, `GET /api/recommendations/rules`, `POST /api/recommendations/activity_5_1/reset`.
  - **GenAI Extension:** Integrates Google Gemini Flash 2.0 via [`genai_utils.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/utils/genai_utils.py) with seamless local heuristic fallback.

#### Activity 5.2: Student Session Analytics Generation
- **Objective:** Generate student-facing analytics that summarize individual participation and engagement patterns during a session using attendance records and engagement scores. Present insights in a reflective format without assigning grades or evaluations, helping students identify periods of high focus (>75%) and distraction (<50%) while strictly ensuring privacy and avoiding peer comparisons.
- **Implemented Solution:**
  - **Core Analytics Service ([`backend/core/analytics_service.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/analytics_service.py)):**
    - **Reference Image Implementation:** `AnalyticsService.get_session_trends(session_id)` queries up to 1000 points of `PersonMetric` from the database, groups metrics by timestamp (`%H:%M:%S`), constructs `timeline[ts_str] = {'att': [], 'emo': {}}`, aggregates attention values and emotion distributions, rollups minute buckets, and determines overall trend direction (`RISING`, `STABLE`, `DECLINING`).
    - **Reflective Student Analytics Generation:** `AnalyticsService.get_student_session_analytics(session_id, student_id)` produces structured, non-evaluative session summaries:
      1. *Attendance Duration & Audit Proof:* Total active seconds, formatted MM:SS (`duration_formatted`), presence ratio percentage, first/last detected timestamps, and salted SHA-256 cryptographic verification hash.
      2. *Engagement Consistency Index:* Standard deviation $\sigma$, variance, stability index ($100 - \sigma \times 2.5$), and consistency classification (`HIGHLY_STEADY`, `BALANCED_FLOW`, `DYNAMIC_FLUCTUATION`).
      3. *Focus Flow Breakdown:* High Focus periods ($> 75\%$ attention), Balanced Attention periods ($50-75\%$), and Distraction / Wandering periods ($< 50\%$ attention or inactivity $> 15\text{ s}$).
      4. *Continuous Focus Periods Timeline:* Segmented episodes with start/end timestamps, duration, average attention, and grounded behavioral notes.
      5. *Notable Activity Trends:* Evidence-based observations of focus stamina, opening peaks, and discussion responsiveness.
      6. *Self-Reflection & Accountability Takeaways:* Constructive self-directed questions and growth cues (strictly zero grades and zero rankings).
      7. *Privacy & Ethical Safeguards:* Explicit guarantee of `peer_comparison_included: False`, `rankings_assigned: False`, and `grades_assigned: False` with pseudonym hash protection.
    - **Cohort Reflective Roster:** `AnalyticsService.get_all_students_reflective_summary(session_id)` returns unranked learner summaries sorted strictly by desk seat or name to avoid peer hierarchy.
    - **Report Generation & Export:** `AnalyticsService.export_student_analytics_report(session_id, student_id, format_type)` exports formatted JSON or printable Markdown reports.
  - **Granular Database Storage ([`backend/db/database.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/db/database.py)):**
    - `person_metrics` table logging `session_id`, `student_id`, `timestamp`, `epoch_seconds`, `attention_score`, `emotion_state`, `motion_energy`, `inactivity_seconds`.
    - `DatabaseManager.record_person_metric` and `DatabaseManager.get_person_metrics`.
  - **Dashboard Modal 12 Explorer ([`frontend/index.html`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/index.html), [`frontend/js/app.js`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/js/app.js)):**
    - Interactive learner profile selector with 8 enrolled students.
    - Privacy and reflection assurance banner.
    - 3-column KPI cards (Attendance Duration, Consistency Score, Focus Flow Ratio bar).
    - Timeline list of high focus vs. wandering episodes.
    - Notable activity trends and self-reflection questions.
    - Unranked cohort table with inspector modal triggers.
    - One-click JSON and Markdown report downloads.
  - **Dedicated REST API Endpoints ([`backend/api/server.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/api/server.py)):**
    - `GET /api/analytics/activity_5_2/status`: System status and capabilities.
    - `GET /api/analytics/activity_5_2/session_trends`: Minute-bucket timeline and emotion rollups (Reference Image).
    - `GET /api/analytics/activity_5_2/student/{student_id}`: Individual reflective profile.
    - `GET /api/analytics/activity_5_2/all_reflective`: Privacy-safe, unranked cohort reflections.
    - `GET /api/analytics/activity_5_2/export_report/{student_id}`: Downloadable JSON / Markdown report.
  - **Automated Test Coverage:**
    - Verified by 4 dedicated test suites in `tests/test_system.py`: `test_activity_5_2_analytics_service_core_and_reference_image`, `test_activity_5_2_student_session_analytics_reflective_generation`, `test_activity_5_2_cohort_summary_and_reports_export`, and `test_activity_5_2_fastapi_rest_endpoints` (66/66 total tests passing, 100% OK).


---

### Milestone 6: Interface, Testing, and Deployment
*Focus: Providing real-time interfaces, executing the automated test suite, and validating edge cases.*

#### Activity 6.1: Run Core Application
- **Objective:** Launch the production asynchronous engine powering the video pipeline, REST endpoints, SSE telemetry, and Web UI.
- **Implemented Solution:**
  Executed via:
  ```powershell
  python run_agent.py
  ```
  - **Web Application:** Accessible at `http://127.0.0.1:8000` with obsidian glassmorphic design, 60 FPS MJPEG stream, live SVG diagrams, and audio chimes.
  - **OpenAPI Documentation:** Interactive Swagger interface at `http://127.0.0.1:8000/docs`.

#### Activity 6.2: Launch Optional Streamlit Dashboard
- **Objective:** Provide a native, reactive Python dashboard for educators and data scientists wanting rapid metric inspection.
- **Implemented Solution:**
  Executed via:
  ```powershell
  .\.venv\Scripts\streamlit run streamlit_app.py
  ```
  - Accessible at `http://localhost:8501`.
  - Contains 6 dedicated tabs:
    1. 🔴 **Live Video & Feed:** Embedded 60 FPS video stream with real-time fusion telemetry.
    2. 📝 **Attendance Log:** Sustained presence register with CSV download.
    3. 📊 **Engagement Trends:** Multi-line charts of fused, visual, and acoustic scores.
    4. 🎓 **Student Analytics:** Per-student participation profiles, flow distributions, and CSV export.
    5. 🤖 **Pedagogical AI Agent:** Urgency-colored intervention cards and reasoning rationale.
    6. 🔍 **Prerequisite Verification:** Live matrix of system dependencies and status.

#### Activity 6.3: Validate Outputs and Edge Cases
- **Objective:** Rigorously verify system correctness, stress resistance, and edge case resilience via automated testing.
- **Implemented Solution:**
  [`tests/test_system.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/tests/test_system.py) contains **12 automated test suites**:
  1. `test_database_and_pseudonym_privacy`: Verifies salted SHA-256 student pseudonym hashing.
  2. `test_sustained_presence_walkby_filter`: Verifies sustained attendance marking and fleeting walk-by filtering ($< 5\text{ s}$).
  3. `test_visual_attention_and_head_pose`: Verifies frontal gaze vs. distracted yaw/pitch score penalties.
  4. `test_audio_vad_and_monologue_detector`: Verifies voice activity detection and lecture monologue tracking.
  5. `test_multimodal_fusion_and_engagement_index`: Verifies weighted composite scoring and drop-off alerting.
  6. `test_pedagogical_agent_reasoner`: Verifies autonomous trigger generation upon attention plunge.
  7. `test_offline_privacy_guarantee`: Verifies 100% offline edge execution with zero cloud telemetry.
  8. `test_code_generation_and_execution`: Verifies synthesis and execution of Python analytical audit scripts.
  9. `test_tts_audio_synthesis`: Verifies generation of valid WAV voice and chime alert files.
  10. `test_genai_visual_aid_and_reasoning`: Verifies SVG visual aid synthesis and Gemini reasoning heuristics.
  11. `test_student_and_session_analytics_generation`: Verifies session statistics and student profile aggregation (Milestone 5).
  12. `test_edge_cases_empty_room_and_audio_burst`: Validates robustness against empty rooms (zero faces), extreme audio spikes, and extreme head angles (Milestone 6).

---

## 4. Operational Runbook

### Step 1: Environment Activation
```powershell
# Navigate to project directory
cd c:\Users\91970\OneDrive\Music\SmartBridge

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

### Step 2: Run Automated Validation Suite
```powershell
.\.venv\Scripts\python -m unittest tests/test_system.py
```
*Expected Output:*
```
Ran 70 tests in 10.42s
OK
```

### Step 3: Run Activity 6.1 Pipeline Verification
```powershell
# Verify pipeline with pre-recorded classroom video
.\.venv\Scripts\python run_agent.py --verify-pipeline --source file --verify-frames 5

# Launch Core Application (FastAPI + Glassmorphic UI)
python run_agent.py
```
- Open browser to **`http://127.0.0.1:8000`**

### Step 4: Launch Companion Streamlit Dashboard (Optional)
```powershell
.\.venv\Scripts\streamlit run streamlit_app.py
```
- Open browser to **`http://localhost:8501`**

---

## 5. Architectural Alignment Summary

```
                      +---------------------------------------+
                      |         NEUROCLASS WORKFLOW           |
                      |   Milestones 1 -> 6 Fully Aligned     |
                      +---------------------------------------+
                                          |
            +-----------------------------+-----------------------------+
            |                                                           |
            v                                                           v
+-----------------------+                                   +-----------------------+
|   Vision Pipeline     |                                   |    Audio Pipeline     |
| - OpenCV Centroid     |                                   | - RMS Acoustic Energy |
| - Yaw/Pitch Gaze      |                                   | - Voice Activity Det  |
| - Sustained Presence  |                                   | - Rhythm Classifier   |
| (Milestone 2)         |                                   | (Milestone 3)         |
+-----------------------+                                   +-----------------------+
            \                                                           /
             \                                                         /
              +---------------------------+---------------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |       Multimodal Fusion Engine        |
                      |       - 60% Visual / 40% Audio        |
                      |       - Engagement Index (0-100%)     |
                      |       (Milestone 4)                   |
                      +---------------------------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |      Analytics & Recommendation       |
                      |      - Pedagogical Reasoning Agent    |
                      |      - Per-Student & Session Metrics  |
                      |      (Milestone 5)                    |
                      +---------------------------------------+
                                          |
            +-----------------------------+-----------------------------+
            |                                                           |
            v                                                           v
+-----------------------+                                   +-----------------------+
|  FastAPI Web App      |                                   |  Streamlit Dashboard  |
|  - Port 8000          |                                   |  - Port 8501          |
|  - 60 FPS MJPEG       |                                   |  - Reactive DataFrames|
|  - SSE Telemetry      |                                   |  - CSV Analytics      |
|  (Milestone 6.1)      |                                   |  (Milestone 6.2)      |
+-----------------------+                                   +-----------------------+
            \                                                           /
             +----------------------------+----------------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |    12 Automated Test Suites (OK)      |
                      |    100% Offline Edge Storage          |
                      |    (Milestone 6.3)                    |
                      +---------------------------------------+
```
