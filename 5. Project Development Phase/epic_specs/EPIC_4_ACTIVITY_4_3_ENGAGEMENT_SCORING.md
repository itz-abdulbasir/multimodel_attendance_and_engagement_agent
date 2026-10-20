# 📈 EPIC 4: AI Implementation
## Activity 4.3: Engagement Scoring Logic

> **Document Version:** 1.0.0  
> **Milestone Status:** Implemented, Integrated & Validated (100% Passed)  
> **Target Subsystem:** Multimodal Engagement Scoring Engine, Predefined Adjustable Thresholds, Temporal Engagement Profiler, Fluctuation & Peak/Disengagement Detectors, Downstream Pedagogical Intelligence  
> **Source Files:** [`backend/core/engagement_scoring.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/engagement_scoring.py), [`backend/fusion/engagement_scoring.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/fusion/engagement_scoring.py), [`backend/api/server.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/api/server.py), [`frontend/index.html`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/index.html), [`frontend/js/app.js`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/js/app.js), [`tests/test_system.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/tests/test_system.py)

---

## 1. Executive Summary & Objective

In **Activity 4.3: Engagement Scoring Logic**, synchronized and fused multimodal signals are transformed into interpretable, transparent, and actionable engagement scores. 

Rather than computing a single opaque aggregate score for an entire session, rule-based logic and predefined, adjustable thresholds are applied across discrete regular time segments (e.g., 10-second intervals) to construct a **Temporal Engagement Profile**. This temporal approach captures the dynamic ebb and flow of classroom instruction, allowing educators to:
1. **Identify Attention Fluctuations:** Measure cognitive volatility, rolling score variance, and attention stability across lecture phases.
2. **Detect Peak Engagement Periods:** Pinpoint contiguous high-flow segments ($\ge 80\%$) and isolate the dominant sensory drivers behind collaborative breakthroughs.
3. **Flag Extended Disengagement Phases:** Automatically detect persistent drop-offs ($< 50\%$ over $\ge 30-60\text{s}$) and diagnose root causes (e.g., dormant stillness, room cross-talk, visual drifting).
4. **Fine-Tune Scoring Thresholds:** Dynamically adjust factor weights and threshold profiles using pedagogical presets (`LECTURE_STANDARD`, `INTERACTIVE_DISCUSSION`, `HANDS_ON_LAB`, `QUIET_EXAM`) or custom tuning based on classroom requirements.
5. **Feed Downstream Intelligence:** Provide direct inputs to generate AI teaching suggestions, granular per-student participation quadrants, and post-session analytical summaries.

---

## 2. Technical Architecture: Engagement Scoring Pipeline

```
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                ACTIVITY 4.3: ENGAGEMENT SCORING PIPELINE                                |
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                                                                                         |
|       +───────────────────────────────────+           +─────────────────────────────────────────+       |
|       |       ALIGNED VISUAL SIGNALS      |           |          ALIGNED AUDIO SIGNALS          |       |
|       |  - Average Visual Attention       |           |  - Calibrated Noise Level (dB SPL)      |       |
|       |  - Sustained Presence Duration    |           |  - Speech State (Silence/Noise/Speech)  |       |
|       |  - Movement Energy & Pattern      |           |  - Instructional Rhythm Mode            |       |
|       |  - Inactivity Duration (Dormancy) |           |  - Turn-Taking Frequency (Turns/Min)    |       |
|       +───────────────────────────────────+           +─────────────────────────────────────────+       |
|                         │                                                  │                            |
|                         └─────────────────────────┬────────────────────────┘                            |
|                                                   v                                                     |
|                                 +───────────────────────────────────+                                   |
|                                 |   FOUR-FACTOR SUB-SCORE ENGINE    |                                   |
|                                 |  - S_vis: Sustained Visual Score  |                                   |
|                                 |  - S_mot: Movement Frequency Score|                                   |
|                                 |  - S_ina: Inactivity Penalty Score|                                   |
|                                 |  - S_aud: Speech Intensity Score  |                                   |
|                                 +───────────────────────────────────+                                   |
|                                                   │                                                     |
|                         ┌─────────────────────────┴─────────────────────────┐                           |
|                         v                                                   v                           |
|         +─────────────────────────────────+                 +─────────────────────────────────+         |
|         | PREDEFINED ADJUSTABLE THRESHOLDS|                 |    EXPLAINABLE RULE EVALUATION  |         |
|         | - Preset: LECTURE_STANDARD      |                 | - RULE_SUSTAINED_VISUAL_FOCUS   |         |
|         | - Preset: INTERACTIVE_DISCUSSION|                 | - RULE_OPTIMAL_POSTURAL_FLOW    |         |
|         | - Preset: HANDS_ON_LAB          |                 | - RULE_PROLONGED_INACTIVITY     |         |
|         | - Preset: QUIET_EXAM            |                 | - RULE_RESTLESS_POSTURE_JITTER  |         |
|         | - Normalized Weights (Sum=1.0)  |                 | - RULE_VIBRANT_SPEECH_RESONANCE |         |
|         +─────────────────────────────────+                 +─────────────────────────────────+         |
|                         │                                                   │                           |
|                         └─────────────────────────┬─────────────────────────┘                           |
|                                                   v                                                     |
|                                 +───────────────────────────────────+                                   |
|                                 |      COMPOSITE SEGMENT SCORER     |                                   |
|                                 |  EI = w_vis*S_vis + w_mot*S_mot + |                                   |
|                                 |       w_ina*S_ina + w_aud*S_aud   |                                   |
|                                 |  Attribution & Dominant Driver    |                                   |
|                                 +───────────────────────────────────+                                   |
|                                                   │                                                     |
|                                                   v                                                     |
|                                 +───────────────────────────────────+                                   |
|                                 |    TEMPORAL ENGAGEMENT PROFILE    |                                   |
|                                 |  - Sequential Regular Segments    |                                   |
|                                 |  - Attention Fluctuation Index    |                                   |
|                                 |  - Stability Score (0 - 100%)     |                                   |
|                                 |  - Peak Flow Periods (>=80%)      |                                   |
|                                 |  - Extended Disengagements (<50%) |                                   |
|                                 +───────────────────────────────────+                                   |
|                                                   │                                                     |
|                         ┌─────────────────────────┼─────────────────────────┐                           |
|                         v                         v                         v                           |
|         +─────────────────────────+ +─────────────────────────+ +─────────────────────────+         |
|         |   TEACHING SUGGESTIONS  | |    STUDENT ANALYTICS    | |    SESSION SUMMARIES    |         |
|         | - Pacing Disengagement  | | - Per-Student Trajectory| | - Class Mean / Min / Max|         |
|         | - Comprehension Pauses  | | - Quadrant Tiers        | | - Fluctuation Rating    |         |
|         | - Stretch / Poll Alerts | | - Presence Verification | | - Export Signed JSON/CSV|         |
|         +─────────────────────────+ +─────────────────────────+ +─────────────────────────+         |
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
```

---

## 3. Mathematical & Algorithmic Formulation

### 3.1 Four Core Engagement Factors

The scoring logic systematically evaluates four foundational factors:

#### 1. Sustained Visual Presence ($S_{\text{vis}}$)
Combines forward instructional gaze ($A_{\text{gaze}} \in [0.0, 1.0]$) and the ratio of active presence time to segment duration ($R_{\text{presence}} = \frac{T_{\text{active}}}{T_{\text{segment}}}$):
$$S_{\text{vis}} = \left( 0.60 \cdot \frac{A_{\text{gaze}}}{\max(0.01, \theta_{\text{gaze}})} + 0.40 \cdot R_{\text{presence}} \right) \times 100.0$$
If active presence drops below the minimum sustained presence threshold ($\theta_{\text{min\_pres}}$), a non-linear stepped attenuation is enforced:
$$S_{\text{vis}} \leftarrow S_{\text{vis}} \times \left( \frac{R_{\text{presence}}}{\theta_{\text{min\_pres}}} \right)^{1.5}$$

#### 2. Movement Frequency & Posture Dynamics ($S_{\text{mot}}$)
Maps optical motion energy ($M \in [0.0, 1.0]$) and posture adjustments into cognitive states:
- **Optimal Attentive Stability ($0.02 \le M \le 0.25$):** $S_{\text{mot}} = 95.0\%$. Indicates focused note-taking, nodding, and natural posture responsiveness.
- **Elevated Purposeful Movement ($0.25 < M \le 0.45$):** $S_{\text{mot}} = 70.0\%$. Reflects active group work or board alignment.
- **Static Dormancy ($M < 0.02$):** $S_{\text{mot}} = 40.0\%$. Indicates physical immobility or passive daydreaming.
- **Restless Jitter ($M > 0.45$):** $S_{\text{mot}} = 35.0\%$. Penalizes excessive fidgeting and wandering chair posture.

#### 3. Inactivity Duration Penalty ($S_{\text{ina}}$)
Evaluates continuous dormant inactivity ($D_{\text{ina}}$ in seconds) without postural adjustments:
$$S_{\text{ina}} = 
\begin{cases} 
100.0\% & \text{if } D_{\text{ina}} \le 30\text{s (Soft Threshold)} \\
100.0 - \left( \frac{D_{\text{ina}} - 30}{30} \right) \times 35.0\% & \text{if } 30\text{s} < D_{\text{ina}} \le 60\text{s (Warning Threshold)} \\
65.0 - \left( \frac{D_{\text{ina}} - 60}{30} \right) \times 40.0\% & \text{if } 60\text{s} < D_{\text{ina}} \le 90\text{s (Critical Threshold)} \\
\max\left(0.0, 25.0 - (D_{\text{ina}} - 90) \times 0.50\right)\% & \text{if } D_{\text{ina}} > 90\text{s (Severe Disengagement)}
\end{cases}$$

#### 4. Speech Activity Intensity ($S_{\text{aud}}$)
Context-aware acoustic scoring based on environmental sound pressure level ($\text{SPL}$ in $\text{dB SPL}$), speech state, and participation frequency ($F_{\text{turn}}$ turns/min):
- **Acoustic Disruption:** If $\text{SPL} \ge \theta_{\text{disruptive}}$ ($75\text{ dB SPL}$), score is penalized to $30.0\%$ (Rule `ACOUSTIC_CHAOS_DISRUPTION`).
- **Interactive Discussion / Q&A:** High turn frequency ($F_{\text{turn}} \ge 1.0$) and active voice receives optimal score ($95.0\%$). Prolonged silence during Q&A ($>20\text{s}$) drops score to $45.0\%$ (Rule `QUESTION_CONCEPT_FREEZE`).
- **Standard Lecture:** Quiet to moderate ambient noise floor ($45-65\text{ dB SPL}$) receives $85-90\%$.
- **Silent Study / Exam:** Strict quiet ($\le 50\text{ dB SPL}$) receives $98.0\%$.

---

### 3.2 Composite Segment Scoring & Explainable Attribution

The segment composite engagement score is formulated as:
$$\text{EI}_{\text{segment}} = w_{\text{vis}} \cdot S_{\text{vis}} + w_{\text{mot}} \cdot S_{\text{mot}} + w_{\text{ina}} \cdot S_{\text{ina}} + w_{\text{aud}} \cdot S_{\text{aud}}$$
Where:
$$\sum_{i} w_i = w_{\text{vis}} + w_{\text{mot}} + w_{\text{ina}} + w_{\text{aud}} = 1.0$$

The engine decomposes every segment into an exact point contribution:
- $\text{Contrib}_{\text{vis}} = w_{\text{vis}} \cdot S_{\text{vis}}$
- $\text{Contrib}_{\text{mot}} = w_{\text{mot}} \cdot S_{\text{mot}}$
- $\text{Contrib}_{\text{ina}} = w_{\text{ina}} \cdot S_{\text{ina}}$
- $\text{Contrib}_{\text{aud}} = w_{\text{aud}} \cdot S_{\text{aud}}$

The system identifies the **Dominant Driver** (highest positive contribution) and **Dominant Penalty** (highest drag deduction) to ensure transparency.

---

### 3.3 Attention Fluctuation Metrics

Attention fluctuation quantifies whether learners maintain consistent focus or experience erratic volatility:
1. **Variance ($\sigma^2$) and Standard Deviation ($\sigma$):**
   $$\sigma^2 = \frac{1}{N} \sum_{k=1}^N (\text{EI}_k - \overline{\text{EI}})^2, \quad \sigma = \sqrt{\sigma^2}$$
2. **Fluctuation Index ($\text{FI}$):**
   Normalized coefficient of variation:
   $$\text{FI} = \frac{\sigma}{\max(1.0, \overline{\text{EI}})}$$
3. **Stability Score ($\text{SS}$):**
   $$\text{SS} = \max\left(0.0, \min(100.0, 100.0 - \text{FI} \times 100.0)\right)$$
4. **Attention Drop Detector:** Tracks instances where consecutive intervals plunge by $\ge 15.0\%$.

---

### 3.4 Peak Periods & Extended Disengagement Detection

#### Peak Engagement Periods
Contiguous segments where $\text{EI}_{\text{segment}} \ge \theta_{\text{peak}}$ (default $80.0\%$).
- Stores start/end segment indices, start/end timestamps, total duration, average peak score, and top contributing factors.
- Signals opportunities to introduce higher-order conceptual challenges.

#### Extended Disengagement Phases
Contiguous segments where $\text{EI}_{\text{segment}} < \theta_{\text{disengage}}$ (default $50.0\%$) persisting for $\ge K$ intervals (default $\ge 3$ segments, $30\text{s}$).
- Automatically isolates root causes (e.g., prolonged inactivity, auditory chaos, visual gaze drift).
- Emits actionable pedagogical recommendations (e.g., peer discussions, physical stretches, acoustic resets).

---

## 4. Predefined Threshold Presets & Adjustability

| Preset | Pedagogical Focus | $w_{\text{vis}}$ | $w_{\text{mot}}$ | $w_{\text{ina}}$ | $w_{\text{aud}}$ | $\theta_{\text{disruptive}}$ | Optimal Motion Range |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`LECTURE_STANDARD`** | Board visual attention primary; quiet acoustic environment | $0.40$ | $0.15$ | $0.20$ | $0.25$ | $70\text{ dB SPL}$ | $0.02 - 0.25$ |
| **`INTERACTIVE_DISCUSSION`**| Verbal interaction and student turn-taking primary | $0.25$ | $0.20$ | $0.10$ | $0.45$ | $80\text{ dB SPL}$ | $0.02 - 0.35$ |
| **`HANDS_ON_LAB`** | High physical movement and collaborative peer chatter | $0.20$ | $0.40$ | $0.15$ | $0.25$ | $82\text{ dB SPL}$ | $0.05 - 0.45$ |
| **`QUIET_EXAM`** | Strict stationary focus; minimal noise tolerance | $0.45$ | $0.25$ | $0.05$ | $0.25$ | $58\text{ dB SPL}$ | $0.01 - 0.15$ |
| **`CUSTOM`** | Dynamically fine-tuned by educator via sliders | User | User | User | User | User | User |

All factor weights automatically re-normalize to strictly sum to $1.0$ if adjusted dynamically.

---

## 5. Downstream Integration Architecture

```
                  +---------------------------------------+
                  |  TEMPORAL ENGAGEMENT PROFILE (ACT 4.3)|
                  +---------------------------------------+
                                      |
        +-----------------------------+-----------------------------+
        |                                                           |
        v                                                           v
+-------------------------------+                           +-------------------------------+
|     TEACHING SUGGESTIONS      |                           |       STUDENT ANALYTICS       |
| - Proactive alert cards       |                           | - Per-student engagement score|
| - Triggered by disengagement  |                           | - Participation quadrant:     |
|   phases or attention drops   |                           |   HIGHLY_ENGAGED, ATTENTIVE,  |
| - Cooldown-managed delivery   |                           |   FLUCTUATING, AT_RISK        |
+-------------------------------+                           +-------------------------------+
                                      |
                                      v
                        +-------------------------------+
                        |       SESSION SUMMARIES       |
                        | - Engagement distribution     |
                        | - Fluctuation stability index |
                        | - Peak & disengagement counts |
                        | - Downloadable JSON / CSV     |
                        +-------------------------------+
```

---

## 6. REST API Endpoints Specification

| Endpoint | Method | Role & Description |
| :--- | :--- | :--- |
| `/api/engagement/activity_4_3/status` | `GET` | Returns active threshold configuration, factor weights, latest segment score, total segments scored, and summary diagnostics. |
| `/api/engagement/activity_4_3/score_segment` | `POST` | Scores a discrete time segment using rule-based logic and returns an `EngagementSegmentScore` with full factor attribution. |
| `/api/engagement/activity_4_3/generate_temporal_profile` | `POST` | Computes engagement scores at regular intervals across input packets to generate a complete `TemporalEngagementProfile`. |
| `/api/engagement/activity_4_3/temporal_profile` | `GET` | Returns the active session's temporal engagement profile with fluctuation metrics and peak/disengagement lists. |
| `/api/engagement/activity_4_3/threshold_config` | `GET` | Returns the current predefined thresholds, weights, and active preset name. |
| `/api/engagement/activity_4_3/update_thresholds` | `POST` | Dynamically updates thresholds and weights with automatic re-normalization for classroom fine-tuning. |
| `/api/engagement/activity_4_3/apply_preset` | `POST` | Applies one of four predefined classroom presets (`LECTURE_STANDARD`, `INTERACTIVE_DISCUSSION`, `HANDS_ON_LAB`, `QUIET_EXAM`). |
| `/api/engagement/activity_4_3/peaks_and_disengagements` | `GET` | Returns isolated peak flow periods and extended disengagement phases with root causes and suggested actions. |
| `/api/engagement/activity_4_3/downstream_summary` | `POST` | Synthesizes downstream teaching suggestions, per-student analytics profiles, and post-session summaries. |
| `/api/engagement/activity_4_3/export_json` | `GET` | Exports complete temporal engagement profile and downstream analytics as a downloadable JSON audit document. |

---

## 7. Interactive UI Explorer (Modal 10)

Accessible via the top navigation button **📈 Activity 4.3 Scoring** in [`frontend/index.html`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/index.html):
1. **Live KPI Ribbon:** Instant Segment Composite Score, Attention Stability Rating, Peak Flow Periods Count, and Disengagement Warnings.
2. **Four-Factor Breakdown Gauges:** Visual Presence, Movement Frequency, Inactivity Penalty, and Speech Activity Intensity with point contributions.
3. **Temporal Engagement Profile Timeline:** Interactive segmented bar chart displaying the session timeline with emerald peak highlights and amber/red disengagement zones.
4. **Preset Selector & Threshold Sliders:** Instant switching between Lecture, Discussion, Lab, and Exam presets, plus real-time weight adjustment sliders.
5. **Peak & Disengagement Diagnostics:** Detailed breakdown of active peaks (drivers) and disengagement phases (causes and recommended interventions).
6. **Downstream Intelligence Actions:** One-click triggers for generating pedagogical suggestions and downloading JSON export reports.

---

## 8. Verification & Automated Test Suite

A comprehensive test suite of 8 dedicated unit and integration tests was implemented in [`tests/test_system.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/tests/test_system.py):

1. `test_epic4_activity4_3_rule_based_scoring_logic`: Validates four factor sub-scores, mathematical factor attribution summation, and boundary clamps ($[0.0, 100.0\%]$).
2. `test_epic4_activity4_3_predefined_and_adjustable_thresholds`: Validates all 4 pedagogical presets and automatic weight normalization upon custom updates.
3. `test_epic4_activity4_3_temporal_profile_generation`: Validates sequential segment processing over regular intervals and aggregate summary generation.
4. `test_epic4_activity4_3_attention_fluctuations_detection`: Validates variance, standard deviation, fluctuation index, stability scores, and attention drop alerting across steady vs. volatile profiles.
5. `test_epic4_activity4_3_peak_engagement_periods_detection`: Validates detecting contiguous high-flow segments ($\ge 80\%$) and identifying dominant drivers.
6. `test_epic4_activity4_3_extended_disengagement_phases_detection`: Validates detecting sustained drop-offs ($< 50\%$) lasting $\ge 3$ consecutive intervals with root cause diagnosis.
7. `test_epic4_activity4_3_downstream_integration_and_analytics`: Validates generating teaching suggestions, student analytics (quadrant categorization), and session summaries.
8. `test_epic4_activity4_3_api_endpoints`: Validates all 10 Activity 4.3 REST API endpoints asynchronously.

---

## 9. Execution Verification Command

```powershell
.\.venv\Scripts\python.exe -m unittest tests/test_system.py
```
**Milestone Verification Status:** 100% Passed.
