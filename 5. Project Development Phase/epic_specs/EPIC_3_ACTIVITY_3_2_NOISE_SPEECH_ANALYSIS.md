# 🎙️ EPIC 3: Audio Module Development
## Activity 3.2: Noise and Speech Activity Analysis

> **Document Version:** 1.0.0  
> **Milestone Status:** Implemented, Integrated & Validated (100% Passed)  
> **Target Subsystem:** Acoustic Feature Extractor, 3-Tier Signal Classifier, Ambient Noise Trend Tracker, Speech Activity Detector & Multimodal Audio Context Aggregator  
> **Source Files:** [`backend/core/audio_analysis.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/audio_analysis.py), [`backend/audio/audio_analyzer.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/audio/audio_analyzer.py), [`backend/agent/pedagogical_agent.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/agent/pedagogical_agent.py), [`backend/api/server.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/api/server.py), [`frontend/src/components/AudioCapture.jsx`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/src/components/AudioCapture.jsx), [`frontend/index.html`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/index.html), [`frontend/js/app.js`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/js/app.js)

---

## 1. Executive Summary & Objective

In modern intelligent classroom environments, understanding acoustic dynamics is fundamental to gauging student engagement, teaching rhythm, and ambient environmental conditions. While computer vision provides critical spatial metrics such as facial gaze, head pose orientation, and motion energy, audio signals capture the conversational pulse and acoustic comfort of the learning space.

**Activity 3.2: Noise and Speech Activity Analysis** focuses on analyzing extracted audio signals to identify ambient noise levels and speech activity patterns:
1. **Multi-Dimensional Audio Feature Extraction:** For each audio segment, compute energy levels (RMS, short-time energy, decibels full-scale $\text{dB}_{\text{FS}}$, and calibrated sound pressure level $\text{dB SPL}$), amplitude variation (peak-to-peak amplitude, standard deviation, crest factor, and subframe dynamic range in $\text{dB}$), and short-time signal characteristics (zero-crossing rate $\text{ZCR}$, spectral centroid, and spectral flatness).
2. **Three-Tier Signal Discrimination:** Differentiate between periods of **Silence**, **Background Noise**, and **Active Speech** using a calibrated hierarchical decision tree combining sound pressure level, dynamic range, crest factor, and spectral flatness.
3. **Ambient Noise Level & Trend Tracking:** Track continuous environmental conditions (`QUIET`, `MODERATE`, `ELEVATED`, `LOUD_DISRUPTIVE`) and moving-average noise trends (`RISING`, `FALLING`, `STABLE` with rate of change $\Delta\text{dB}$) alongside an adaptive noise floor tracking background acoustics.
4. **Speech Activity Detection & Interaction Metrics:** Quantify interaction intensity (percentage of active speech time) and participation frequency (speaker conversational turn-taking frequency in turns per minute).
5. **Session-Level Temporal Aggregation:** Aggregate acoustic metrics across the entire session to construct persistent session-level context (mean/peak noise, speech/silence ratios, conversational turn counts).
6. **Multimodal Fusion & Agent Reasoning:** Structure audio insights into standardized normalized vectors ($[0.0, 1.0]$) suitable for synchronous fusion with visual engagement telemetry, empowering the Pedagogical Agent to trigger assistive teaching recommendations when ambient noise disrupts learning or conversational turn-taking is deficient.
7. **Privacy-Preserving Edge Architecture:** Execute all processing 100% offline at the edge with zero verbal speech-to-text transcription or eavesdropping, ensuring compliance with student privacy regulations (FERPA, GDPR).

---

## 2. Technical Architecture: Noise & Speech Activity Pipeline

```
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                NEUROCLASS NOISE & SPEECH ACTIVITY PIPELINE                              |
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                                                                                         |
|       +───────────────────────────────────+           +─────────────────────────────────────────+       |
|       |     CLIENT AUDIO CAPTURE          |           |      EXTRACTED AUDIO SEGMENTS           |       |
|       |  (AudioCapture.jsx / Web Audio    |           |   (Activity 3.1 Segmented Waveforms     |       |
|       |   16-bit PCM streaming WebSocket) |           |    16 kHz Mono Float32 Arrays)          |       |
|       +───────────────────────────────────+           +─────────────────────────────────────────+       |
|                         │                                                  │                            |
|                         └─────────────────────────┬────────────────────────┘                            |
|                                                   v                                                     |
|                                 +───────────────────────────────────+                                   |
|                                 |    Digital Waveform Ingestion     |                                   |
|                                 |    L = 16,000 samples (1.0 sec)   |                                   |
|                                 +───────────────────────────────────+                                   |
|                                                   │                                                     |
|                         ┌─────────────────────────┼─────────────────────────┐                           |
|                         v                         v                         v                           |
|         +────────────────────────+ +─────────────────────────+ +──────────────────────────+             |
|         |     ENERGY LEVELS      | |   AMPLITUDE VARIATION   | |  SHORT-TIME SIGNAL CHAR  |             |
|         | - RMS Energy           | | - Peak-to-Peak Range    | | - Zero-Crossing Rate     |             |
|         | - Short-Time Energy    | | - Amplitude Std Dev     | | - Spectral Centroid (Hz) |             |
|         | - dBFS Power           | | - Crest Factor (Pk/RMS) | | - Spectral Flatness      |             |
|         | - Calibrated dB SPL    | | - Dynamic Range (dB)    | |   (Wiener Entropy)       |             |
|         +────────────────────────+ +─────────────────────────+ +──────────────────────────+             |
|                         │                         │                         │                           |
|                         └─────────────────────────┼─────────────────────────┘                           |
|                                                   v                                                     |
|                              +─────────────────────────────────────────+                                |
|                              |   3-TIER SIGNAL DISCRIMINATION ENGINE   |                                |
|                              |  RMS < 0.015 or SPL < 42 dB  ──> SILENCE|                                |
|                              |  Flatness > 0.40 or DR < 4dB ──> NOISE  |                                |
|                              |  Dynamic Harmonic Energy     ──> SPEECH |                                |
|                              +─────────────────────────────────────────+                                |
|                                                   │                                                     |
|                         ┌─────────────────────────┴─────────────────────────┐                           |
|                         v                                                   v                           |
|         +─────────────────────────────────+                 +─────────────────────────────────+         |
|         |   AMBIENT NOISE LEVEL & TREND   |                 |    SPEECH ACTIVITY & TURNS      |         |
|         | - Condition: QUIET to LOUD      |                 | - Voice Activity Flag (VAD)     |         |
|         | - Adaptive Noise Floor (dB)     |                 | - Interaction Intensity (0-100%)|         |
|         | - Trend: RISING, FALLING, STABLE|                 | - Participation Frequency       |         |
|         | - Delta dB Slope Tracking       |                 |   (Speaker Turns / Minute)      |         |
|         +─────────────────────────────────+                 +─────────────────────────────────+         |
|                         │                                                   │                           |
|                         └─────────────────────────┬─────────────────────────┘                           |
|                                                   v                                                     |
|                                 +───────────────────────────────────+                                   |
|                                 |   SESSION-LEVEL TEMPORAL CONTEXT  |                                   |
|                                 | - Mean & Peak Noise Level (dB SPL)|                                   |
|                                 | - Aggregate Speech/Silence Ratios |                                   |
|                                 | - Cumulative Conversational Turns |                                   |
|                                 +───────────────────────────────────+                                   |
|                                                   │                                                     |
|                         ┌─────────────────────────┴─────────────────────────┐                           |
|                         v                                                   v                           |
|         +─────────────────────────────────+                 +─────────────────────────────────+         |
|         |     MULTIMODAL FUSION VECTOR    |                 |   PEDAGOGICAL AGENT REASONING   |         |
|         | Normalized Acoustic Vector:     |                 | Rule 5: Ambient Noise Alert     |         |
|         | [speech_activity, noise_penalty,|                 | Rule 6: Low Turn-Taking Alert   |         |
|         |  turn_taking, rhythm_stability] |                 | Adaptive Teaching Interventions |         |
|         +─────────────────────────────────+                 +─────────────────────────────────+         |
|                                                                                                         |
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
```

---

## 3. Mathematical & Algorithmic Formulation

### 3.1 Energy Levels Computation
For a digital segment waveform $y[n]$ containing $N$ samples ($N = 16{,}000$ for $1.0\text{ s}$ at $16\text{ kHz}$):

1. **Root-Mean-Square (RMS) Energy:**
   $$\text{RMS} = \sqrt{\frac{1}{N} \sum_{n=1}^N y[n]^2}$$

2. **Short-Time Energy (STE):**
   Computed over sliding subframes of length $M = 512$ samples ($\sim 32\text{ ms}$):
   $$\text{STE}[m] = \frac{1}{M} \sum_{k=0}^{M-1} y[m \cdot M + k]^2$$

3. **Decibels Relative to Full Scale ($\text{dB}_{\text{FS}}$):**
   $$\text{dB}_{\text{FS}} = 20 \log_{10}\left(\max(\text{RMS}, 10^{-5})\right)$$

4. **Calibrated Sound Pressure Level (dB SPL):**
   Maps digital waveform energy to standard classroom acoustic decibels:
   $$\text{SPL} = \min\left(95.0, \max\left(30.0, 94.0 + \text{dB}_{\text{FS}}\right)\right)$$

### 3.2 Amplitude Variation Characteristics
1. **Peak-to-Peak Amplitude:**
   $$A_{\text{p2p}} = \max_{n} y[n] - \min_{n} y[n]$$

2. **Amplitude Standard Deviation:**
   $$\sigma_y = \sqrt{\frac{1}{N} \sum_{n=1}^N \left(y[n] - \mu_y\right)^2}$$

3. **Crest Factor:**
   Measures signal peakiness relative to average energy (high for impulsive speech consonants; lower for continuous ambient hum):
   $$C = \frac{\max_{n} |y[n]|}{\max(\text{RMS}, 10^{-5})}$$

4. **Dynamic Range Across Subframes ($\text{dB}$):**
   Evaluates the difference between maximum and minimum subframe energy:
   $$\text{DR}_{\text{dB}} = 10 \log_{10}\left(\frac{\max_m \text{STE}[m]}{\max(\min_m \text{STE}[m], 10^{-8})}\right)$$

### 3.3 Short-Time Signal Characteristics
1. **Zero-Crossing Rate (ZCR):**
   Quantifies the rate at which the waveform alternates across zero:
   $$\text{ZCR} = \frac{1}{2(N-1)} \sum_{n=1}^{N-1} \left| \text{sgn}(y[n]) - \text{sgn}(y[n-1]) \right|$$

2. **Spectral Centroid:**
   Represents the frequency center of mass of the signal spectrum:
   $$f_c = \frac{\sum_{k=0}^{K-1} f_k \cdot |Y[k]|}{\sum_{k=0}^{K-1} |Y[k]|}$$
   where $Y[k]$ is the Discrete Fourier Transform (DFT) magnitude at frequency $f_k$.

3. **Spectral Flatness (Wiener Entropy):**
   Ratio of the geometric mean to the arithmetic mean of the power spectrum:
   $$\text{SF} = \frac{\exp\left(\frac{1}{K} \sum_{k=0}^{K-1} \ln(|Y[k]|^2 + \epsilon)\right)}{\frac{1}{K} \sum_{k=0}^{K-1} |Y[k]|^2 + \epsilon}$$
   - Near $1.0$: White/broadband noise, HVAC hiss, background fans.
   - Near $0.0$: Harmonic structure characteristic of human voiced speech.

### 3.4 Three-Tier Signal Discrimination Logic
The classifier partitions segments into three mutually exclusive states:
```
                                 [ Input Segment ]
                                         │
                         Is RMS < 0.015 OR SPL < 42.0 dB?
                                  /            \
                               YES              NO
                               /                  \
                        [ SILENCE ]       Is Flatness > 0.40 OR
                                         (DR < 4.0 dB AND Crest < 1.8)?
                                                 /            \
                                               YES             NO
                                               /                 \
                                    [ BACKGROUND_NOISE ]   [ ACTIVE_SPEECH ]
```

### 3.5 Ambient Noise Level & Trend Dynamics
1. **Classroom Condition Categories:**
   - $\text{SPL} < 50.0\text{ dB}$: `QUIET` (Optimal for silent study or testing)
   - $50.0 \le \text{SPL} < 65.0\text{ dB}$: `MODERATE` (Healthy conversational level)
   - $65.0 \le \text{SPL} < 75.0\text{ dB}$: `ELEVATED` (Lively discussion or heightened ambient buzz)
   - $\text{SPL} \ge 75.0\text{ dB}$: `LOUD_DISRUPTIVE` (Acoustic disruption requiring intervention)

2. **Moving-Average Trend Direction:**
   Evaluated over a rolling history of $H = 10$ segments:
   $$\Delta_{\text{dB}} = \overline{\text{SPL}}_{\text{recent}} - \overline{\text{SPL}}_{\text{prior}}$$
   $$\text{Trend} = \begin{cases} \text{RISING}, & \Delta_{\text{dB}} > 1.5 \\ \text{FALLING}, & \Delta_{\text{dB}} < -1.5 \\ \text{STABLE}, & \text{otherwise} \end{cases}$$

3. **Adaptive Noise Floor Tracking:**
   $$\text{NoiseFloor}_{t} = (1 - \alpha) \cdot \text{NoiseFloor}_{t-1} + \alpha \cdot \text{SPL}_t \quad (\text{when } \text{State} \neq \text{ACTIVE\_SPEECH}, \alpha = 0.05)$$

### 3.6 Speech Activity & Participation Frequency
1. **Interaction Intensity ($I_{\text{speech}}$):**
   Ratio of active speech duration to total observation time:
   $$I_{\text{speech}} = \frac{T_{\text{speech}}}{T_{\text{total}}} \in [0.0, 1.0]$$

2. **Participation Frequency ($F_{\text{turns}}$):**
   Rate of alternating speaker conversational turns per minute:
   $$F_{\text{turns}} = \frac{\text{TurnsCount}}{\Delta t_{\text{minutes}}}$$

---

## 4. Key Source Implementations

### 4.1 Core Analyzer: `NoiseAndSpeechActivityAnalyzer`
Located in [`backend/core/audio_analysis.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/audio_analysis.py):

```python
class NoiseAndSpeechActivityAnalyzer:
    def __init__(self, sample_rate: int = 16000, history_len: int = 30):
        self.sample_rate = sample_rate
        self.history_len = history_len
        self.noise_history: List[float] = []
        self.speech_history: List[bool] = []
        self.turn_count: int = 0
        self.last_speech_state: bool = False
        self.session_segments: List[AudioSegmentFeatures] = []
        self.adaptive_noise_floor_db: float = 40.0
```

### 4.2 Segment Feature Dataclass: `AudioSegmentFeatures`
```python
@dataclass
class AudioSegmentFeatures:
    segment_index: int
    timestamp: float
    duration_sec: float
    # Energy Levels
    rms_energy: float
    short_time_energy: float
    db_fs: float
    noise_level_spl: float
    # Amplitude Variation
    peak_to_peak: float
    std_amplitude: float
    crest_factor: float
    dynamic_range_db: float
    # Short-Time Signal Characteristics
    zero_crossing_rate: float
    spectral_centroid: float
    spectral_flatness: float
    # 3-Tier Classification
    signal_classification: str  # SILENCE, BACKGROUND_NOISE, ACTIVE_SPEECH
    # Speech Activity & Noise Trends
    ambient_noise_level: str    # QUIET, MODERATE, ELEVATED, LOUD_DISRUPTIVE
    is_speech_active: bool
    interaction_intensity: float
    participation_frequency: float
```

### 4.3 High-Level Wrapper: `AudioSignalAnalyzer`
Located in [`backend/audio/audio_analyzer.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/audio/audio_analyzer.py), encapsulates both `AudioAnalyzer` and `NoiseAndSpeechActivityAnalyzer`, providing backward compatibility and unified access:
- `compute_segment_features(audio_data, timestamp)`
- `get_noise_level_trend()`
- `aggregate_session_context()`
- `format_for_multimodal_fusion()`

### 4.4 Pedagogical Agent Reasoning Rules
Located in [`backend/agent/pedagogical_agent.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/agent/pedagogical_agent.py):
- **Rule 5 (Acoustic Disruption Alert):** Triggers if noise level exceeds $75.0\text{ dB SPL}$ or noise trend is `LOUD_DISRUPTIVE` for $\ge 3$ consecutive cycles, suggesting:
  > *"Elevated ambient noise detected (XX dB SPL, LOUD_DISRUPTIVE). Suggest requesting student quiet or pausing to regain room attention."*
- **Rule 6 (Low Turn-Taking in Q&A):** Triggers if current rhythm state is `QA_INTERACTION` but participation turn frequency drops below $0.8\text{ turns/min}$ with high visual gaze, suggesting:
  > *"Q&A interaction turn frequency is low (X.X turns/min). Prompt with a specific targeted student question or initiate a think-pair-share cycle."*

---

## 5. Frontend Audio Capture & Explorer Component

### 5.1 React Component: `AudioCapture.jsx`
Located in [`frontend/src/components/AudioCapture.jsx`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/src/components/AudioCapture.jsx):
- Directly fulfills and enhances the user's reference specification.
- Dynamically derives WebSocket URL (`ws://` / `wss://`) from `window.location.host`.
- Captures microphone input via `navigator.mediaDevices.getUserMedia({ audio: true })`.
- Utilizes an `AudioContext` and `ScriptProcessorNode` to downsample to 16 kHz and stream 16-bit PCM binary chunks.
- Visualizes real-time dB SPL gauges, 3-tier classification badges, ambient noise conditions, and short-time spectral metrics.

### 5.2 Obsidian Glassmorphic Modal: Modal 7
Located in [`frontend/index.html`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/index.html) and [`frontend/js/app.js`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/js/app.js):
- Real-time sound pressure level gauge with color-coded environmental condition chips.
- 3-tier state pill (`SILENCE`, `BACKGROUND_NOISE`, `ACTIVE_SPEECH`).
- Short-time characteristics telemetry: Zero-Crossing Rate, Spectral Centroid, Spectral Flatness, Crest Factor, Dynamic Range.
- Speech activity telemetry: Interaction Intensity and Participation Frequency (speaker turns/min).
- Aggregated session-level context counters and multimodal fusion acoustic vector display.

---

## 6. REST & WebSocket API Reference

| Protocol | Route | Description |
| :--- | :--- | :--- |
| `WS` | `/ws/audio` | Bidirectional WebSocket streaming 16-bit PCM binary audio chunks and returning real-time segment analytics. |
| `GET` | `/api/audio/activity_3_2/status` | Returns verification status, classification tiers, feature definitions, and latest telemetry metrics. |
| `POST` | `/api/audio/activity_3_2/analyze_features` | Analyzes audio data (PCM bytes or float array) and computes all Activity 3.2 energy, variation, and spectral features. |
| `GET` | `/api/audio/activity_3_2/session_context` | Returns aggregated session-level acoustic metrics (average noise, peak noise, speech ratio, turn count). |
| `GET` | `/api/audio/activity_3_2/noise_trends` | Returns ambient noise level condition, moving-average trend direction, delta dB, and adaptive noise floor. |
| `GET` | `/api/audio/activity_3_2/fusion_payload` | Returns formatted normalized acoustic vector ready for multimodal fusion with visual engagement. |

---

## 7. Automated Test Suite Validation

The test suite in [`tests/test_system.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/tests/test_system.py) validates Activity 3.2 via 7 dedicated unit and integration tests:

1. `test_epic3_activity3_2_acoustic_feature_computation`:
   - Verifies mathematical computation of RMS, short-time energy, dBFS, calibrated dB SPL, peak-to-peak amplitude, amplitude std dev, crest factor, dynamic range, zero-crossing rate, spectral centroid, and spectral flatness.
2. `test_epic3_activity3_2_three_tier_classification`:
   - Validates correct discrimination across synthetic signals: low-amplitude noise $\to$ `SILENCE`, high-flatness unmodulated noise $\to$ `BACKGROUND_NOISE`, and vocal formant harmonic signals $\to$ `ACTIVE_SPEECH`.
3. `test_epic3_activity3_2_noise_level_trends`:
   - Tests ambient noise condition assignment (`QUIET`, `MODERATE`, `ELEVATED`, `LOUD_DISRUPTIVE`), rolling history tracking, rising/falling/stable trend determination, and adaptive noise floor updating.
4. `test_epic3_activity3_2_participation_frequency_tracking`:
   - Confirms conversational turn-taking detection on alternating speech/silence transitions and calculates turns per minute.
5. `test_epic3_activity3_2_session_context_aggregation`:
   - Validates session-level temporal summary statistics including average SPL, peak SPL, speech-to-silence ratio, and total turn counts.
6. `test_epic3_activity3_2_multimodal_fusion_vector`:
   - Confirms acoustic features are correctly bounded in $[0.0, 1.0]$ and formatted for multimodal fusion.
7. `test_epic3_activity3_2_api_endpoints`:
   - Exercises all 5 Activity 3.2 FastAPI endpoints asynchronously, verifying responses, HTTP status codes, and JSON payloads.

### Full Test Execution Results
```powershell
.\.venv\Scripts\python.exe -m unittest tests/test_system.py
...............................
----------------------------------------------------------------------
Ran 31 tests in 4.678s

OK
```
**Result: 31/31 Tests Passed (100% Success Rate).**
