# 🤖 EPIC 4: AI Implementation
## Activity 4.1: Multimodal Agent Implementation

> **Document Version:** 1.0.0  
> **Milestone Status:** Implemented, Integrated & Validated (100% Passed)  
> **Target Subsystem:** Multimodal Agent Core Intelligence Layer, Cross-Modal Rule Engine, Contextual Engagement Estimator & Groq LLM Insight Generator  
> **Source Files:** [`backend/core/llm_insights.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/llm_insights.py), [`backend/agent/multimodal_agent.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/agent/multimodal_agent.py), [`backend/api/server.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/api/server.py), [`frontend/index.html`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/index.html), [`frontend/js/app.js`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/js/app.js)

---

## 1. Executive Summary & Objective

In multimodal educational intelligence systems, isolated sensory streams often lead to false or ambiguous conclusions:
- A quiet classroom might indicate deep concentration or passive daydreaming.
- Active speech might reflect rich collaborative inquiry or disruptive side conversations.
- High motion might indicate engaged note-taking or restless cognitive fatigue.

To resolve these ambiguities, **EPIC 4: AI Implementation (Activity 4.1: Multimodal Agent Implementation)** establishes the **Core Intelligence Layer** of NeuroClass. Rather than relying on isolated video or audio metrics, the Multimodal Agent integrates outputs from both the Vision Module and the Audio Module to form a unified, coherent understanding of classroom dynamics.

The primary goals of this milestone are:
1. **Unified Cross-Modal Ingestion:** Synchronize visual behaviors (facial attention, gaze direction, head pose, posture movement velocity) and acoustic telemetry (sound pressure level in $\text{dB SPL}$, 3-tier classification, ambient noise trends, participation frequency, turns/min).
2. **Contextual, Interpretable, and Explainable Logic:** Apply deterministic rule-based reasoning (Rules M1 through M6) that interpret combined multimodal data, providing educators with transparent diagnoses rather than opaque black-box scores.
3. **LLM-Powered Pedagogical Insights:** Integrate [`InsightGenerator`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/llm_insights.py) matching the reference architecture to synthesize concise, natural-language classroom insights and actionable teaching suggestions via Groq Cloud (`llama-3.3-70b-versatile`) with deterministic offline fallback.
4. **Attributed Engagement Scoring:** Quantify classroom flow using a dynamic Composite Engagement Index ($\text{EI}: 0-100\%$) with mathematical factor attribution (Visual, Motion, Audio components) and dominant modality detection.
5. **Privacy-Preserving Offline Operation:** Retain zero verbal recording or eavesdropping, executing all feature extraction and heuristic reasoning locally on edge hardware.

---

## 2. Technical Architecture: Multimodal Agent Pipeline

```
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                    NEUROCLASS MULTIMODAL AGENT PIPELINE                                 |
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                                                                                         |
|       +───────────────────────────────────+           +─────────────────────────────────────────+       |
|       |          VISION MODULE            |           |              AUDIO MODULE               |       |
|       |  (Facial Gaze, Head Pose,         |           |  (dB SPL, 3-Tier Classification,        |       |
|       |   Motion Energy, Participant IDs) |           |   Noise Trends, Speaker Turns/Min)      |       |
|       +───────────────────────────────────+           +─────────────────────────────────────────+       |
|                         │                                                  │                            |
|                         └─────────────────────────┬────────────────────────┘                            |
|                                                   v                                                     |
|                                 +───────────────────────────────────+                                   |
|                                 |    Temporal Signal Normalizer     |                                   |
|                                 |  - S_vis: Visual Attention [0, 1] |                                   |
|                                 |  - S_mot: Motion Balance [0, 1]   |                                   |
|                                 |  - S_aud: Audio Score [0, 1]      |                                   |
|                                 +───────────────────────────────────+                                   |
|                                                   │                                                     |
|                         ┌─────────────────────────┴─────────────────────────┐                           |
|                         v                                                   v                           |
|         +─────────────────────────────────+                 +─────────────────────────────────+         |
|         |   DYNAMIC COMPOSITE ENGAGEMENT  |                 |  CONTEXTUAL MULTIMODAL RULES    |         |
|         | EI = (0.50*vis + 0.20*mot +     |                 | M1: High Instructional Flow     |         |
|         |       0.30*aud) * 100           |                 | M2: Passive Visual Distraction  |         |
|         | Component Attribution Breakdown |                 | M3: Discussion Resonance        |         |
|         | Trend & Anomaly Drop Detector   |                 | M4: Acoustic Chaos Disruption   |         |
|         | Dominant Modality Detection     |                 | M5: Question Concept Freeze     |         |
|         | (Visual, Audio, or Balanced)    |                 | M6: Extended Monologue Fatigue  |         |
|         +─────────────────────────────────+                 +─────────────────────────────────+         |
|                         │                                                   │                           |
|                         └─────────────────────────┬─────────────────────────┘                           |
|                                                   v                                                     |
|                                 +───────────────────────────────────+                                   |
|                                 |    Explainable Multimodal State   |                                   |
|                                 |  - State: HIGH_FLOW, DISRUPTION.. |                                   |
|                                 |  - Confidence Score [0.0 - 1.0]   |                                   |
|                                 |  - Plain-English Diagnosis String |                                   |
|                                 +───────────────────────────────────+                                   |
|                                                   │                                                     |
|                                                   v                                                     |
|                                 +───────────────────────────────────+                                   |
|                                 |         INSIGHT GENERATOR         |                                   |
|                                 |   (backend/core/llm_insights.py)  |                                   |
|                                 |  - Groq API / llama-3.3-70b-versatile |                                   |
|                                 |  - Contextual Educational Prompt  |                                   |
|                                 |  - Offline Heuristic Fallback     |                                   |
|                                 +───────────────────────────────────+                                   |
|                                                   │                                                     |
|                         ┌─────────────────────────┴─────────────────────────┐                           |
|                         v                                                   v                           |
|         +─────────────────────────────────+                 +─────────────────────────────────+         |
|         |     STRUCTURED REASONING LOG    |                 |  UI EXPLORER & REST API SUITE   |         |
|         | - MultimodalReasoningResult     |                 | - Modal 8 (Glassmorphic)        |         |
|         | - JSON Telemetry Stream         |                 | - /api/agent/activity_4_1/...   |         |
|         | - Session History Buffer        |                 | - Live Telemetry Integration    |         |
|         +─────────────────────────────────+                 +─────────────────────────────────+         |
|                                                                                                         |
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
```

---

## 3. Mathematical & Algorithmic Formulation

### 3.1 Composite Engagement Index ($\text{EI}$)
The composite classroom engagement index is formulated as a weighted linear combination of normalized visual, postural, and acoustic sub-scores:

$$\text{EI} = \left( w_{\text{vis}} \cdot S_{\text{vis}} + w_{\text{mot}} \cdot S_{\text{mot}} + w_{\text{aud}} \cdot S_{\text{aud}} \right) \times 100.0$$

where default calibrated weights are:
$$w_{\text{vis}} = 0.50, \quad w_{\text{mot}} = 0.20, \quad w_{\text{aud}} = 0.30 \quad \left(\sum w = 1.00\right)$$

#### 1. Visual Attention Score ($S_{\text{vis}} \in [0.0, 1.0]$)
Calculated from frontal facial gaze ratio and yaw/pitch alignment within $\pm 25^\circ$:
$$S_{\text{vis}} = \frac{1}{K} \sum_{k=1}^K \mathbb{I}\left(|\text{yaw}_k| \le 25^\circ \land |\text{pitch}_k| \le 20^\circ\right)$$

#### 2. Motion Balance Score ($S_{\text{mot}} \in [0.0, 1.0]$)
Derived from optical flow motion energy $E_{\text{mot}}$. Moderate movement (e.g. note-taking) is optimal, whereas complete dormancy or restless fidgeting is penalized:
$$S_{\text{mot}} = \begin{cases} 
0.40, & E_{\text{mot}} < 0.02 \quad (\text{Static Dormancy Penalty}) \\
0.95, & 0.02 \le E_{\text{mot}} \le 0.25 \quad (\text{Normal Focused Responsiveness}) \\
0.70, & 0.25 < E_{\text{mot}} \le 0.45 \quad (\text{Elevated Movement}) \\
0.35, & E_{\text{mot}} > 0.45 \quad (\text{Restless Fidgeting Penalty})
\end{cases}$$

#### 3. Acoustic Interaction Score ($S_{\text{aud}} \in [0.0, 1.0]$)
Contextualized by instructional rhythm mode:
$$S_{\text{aud}} = \begin{cases}
\min\left(1.0, 0.40 + \frac{F_{\text{turns}}}{4.0} \times 0.40 + I_{\text{speech}} \times 0.20\right), & \text{Rhythm} \in \{\text{QA\_INTERACTION}, \text{COLLABORATIVE\_BUZZ}\} \\
0.85, & \text{Rhythm} = \text{INSTRUCTOR\_MONOLOGUE} \land \text{SPL} < 65\text{ dB} \land S_{\text{vis}} \ge 0.60 \\
0.40, & \text{Rhythm} = \text{INSTRUCTOR\_MONOLOGUE} \land (\text{SPL} \ge 65\text{ dB} \lor S_{\text{vis}} < 0.60) \\
0.90, & \text{Rhythm} = \text{SILENT\_STUDY} \land \text{SPL} < 50\text{ dB} \\
0.50, & \text{otherwise}
\end{cases}$$

### 3.2 Dominant Modality Determination
To provide explainable feedback on which sensory channel drove the score:
$$\text{Contrib}_{\text{vis}} = w_{\text{vis}} \cdot S_{\text{vis}} \times 100, \quad \text{Contrib}_{\text{aud}} = w_{\text{aud}} \cdot S_{\text{aud}} \times 100$$
$$\text{Modality} = \begin{cases}
\text{BALANCED}, & |\text{Contrib}_{\text{vis}} - \text{Contrib}_{\text{aud}}| \le 8.0 \\
\text{VISUAL\_DOMINANT}, & \text{Contrib}_{\text{vis}} > \text{Contrib}_{\text{aud}} + 8.0 \\
\text{AUDIO\_DOMINANT}, & \text{Contrib}_{\text{aud}} > \text{Contrib}_{\text{vis}} + 8.0
\end{cases}$$

### 3.3 Contextual Multimodal Rule Catalog

Rather than relying on isolated thresholding, the Multimodal Agent executes a hierarchical rule engine:

| Rule ID | Engagement State | Trigger Criteria | Confidence | Explainable Educational Diagnosis |
| :--- | :--- | :--- | :--- | :--- |
| **M4** | `ACOUSTIC_DISRUPTION` | $\text{SPL} \ge 75\text{ dB}$ OR Ambient = `LOUD_DISRUPTIVE` OR ($\text{SPL} \ge 70\text{ dB} \land E_{\text{mot}} > 0.30$) | **0.95** | Elevated ambient sound accompanied by physical movement indicates room cross-talk or background disruption rather than structured participation. |
| **M6** | `FATIGUE_RESTLESSNESS` | $T_{\text{mono}} \ge 480\text{ s}$ (8 min) AND ($S_{\text{mot}} < 0.60 \lor S_{\text{vis}} < 0.60$) | **0.89** | Continuous instructor monologue exceeding optimal duration has saturated learner working memory, manifested through physical restlessness. |
| **M5** | `CONCEPT_HESITATION` | Rhythm = `QA_INTERACTION` AND ($T_{\text{silence}} \ge 20\text{ s} \lor F_{\text{turns}} < 0.8$) AND $S_{\text{vis}} \ge 0.65$ | **0.87** | Learners maintain board/instructor visual alignment but verbal turn-taking is stagnant, signaling conceptual hesitation or uncertainty. |
| **M2** | `PASSIVE_DISENGAGEMENT` | $S_{\text{vis}} < 0.55$ AND $\text{SPL} < 55\text{ dB}$ AND Rhythm $\neq$ `QA_INTERACTION` | **0.88** | Room is acoustically quiet but visual gaze has significantly drifted away from the presentation area, indicating passive disengagement. |
| **M3** | `COLLABORATIVE_ACTIVE` | (Rhythm $\in$ {`QA_INTERACTION`, `COLLABORATIVE_BUZZ`} OR $F_{\text{turns}} \ge 1.5$) AND $S_{\text{vis}} \ge 0.60$ AND $I_{\text{speech}} \ge 0.35$ | **0.91** | High-frequency student-teacher turn-taking aligned with active visual engagement confirms collaborative learning resonance. |
| **M1** | `HIGH_FLOW` | $S_{\text{vis}} \ge 0.70$ AND $S_{\text{mot}} \ge 0.70$ AND $\text{SPL} < 65\text{ dB}$ | **0.92** | High visual gaze convergence combined with quiet, responsive listening establishes optimal cognitive absorption and instructional flow. |
| **M0** | `BALANCED_FLOW` | Default baseline when no anomalous friction is detected | **0.80** | Classroom demonstrates stable visual attention and acoustic balance. |

---

## 4. Implementation Details

### 4.1 Reference Class: `InsightGenerator`
Located in [`backend/core/llm_insights.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/llm_insights.py), directly implementing the user's reference specification:

```python
class InsightGenerator:
    """
    LLM-Powered Classroom Insight Generator.
    Uses Groq Cloud (llama-3.3-70b-versatile) with robust offline fallback
    to synthesize contextual, interpretable, and actionable educational insights.
    """
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model
        self.client = Groq(api_key=self.api_key) if (self.api_key and GROQ_AVAILABLE) else None

    def generate_classroom_insight(self, session_data: dict) -> dict:
        prompt = self.build_prompt(session_data)
        ...
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational AI assistant. Provide brief, professional, and actionable insights for classroom engagement and pedagogical optimization."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                temperature=0.5,
                max_tokens=150,
            )
            response_text = chat_completion.choices[0].message.content
            # Simple Parsing
            insight = "Class status is stable."
            recommendation = "Maintain current pace."
            ...
        except Exception:
            insight, recommendation = self._generate_offline_insight(session_data)
```

### 4.2 Core Class: `MultimodalAgent`
Located in [`backend/agent/multimodal_agent.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/agent/multimodal_agent.py):
- `evaluate(visual_data, audio_data) -> MultimodalReasoningResult`
- Computes component factor breakdowns (`visual_attention_component`, `motion_balance_component`, `audio_interaction_component`).
- Evaluates Rules M1 through M6.
- Synthesizes natural-language insight and actionable recommendation via `InsightGenerator`.
- Maintains sliding reasoning history for trend tracking.

### 4.3 Container: `MultimodalReasoningResult`
```python
@dataclass
class MultimodalReasoningResult:
    timestamp: float
    engagement_index: float                # 0.0 to 100.0%
    engagement_state: str                  # HIGH_FLOW, PASSIVE_DISENGAGEMENT, etc.
    confidence: float                      # 0.0 to 1.0
    dominant_modality: str                 # VISUAL_DOMINANT, AUDIO_DOMINANT, BALANCED
    rule_triggered: str                    # e.g., "M1_HIGH_INSTRUCTIONAL_FLOW"
    explainable_diagnosis: str             # Pedagogical explanation of why rule triggered
    actionable_insight: str                # AI generated insight
    teaching_recommendation: str           # Concrete instructor recommendation
    trend: str                             # RISING, FALLING, STABLE, VOLATILE
    trend_delta: float                     # Delta change in recent windows
    attention_drop_alert: bool             # Anomaly flag for sudden collective disengagement
    factor_breakdown: Dict[str, float]     # Component attributions (visual, motion, audio)
    raw_inputs: Dict[str, Any]
```

---

## 5. REST API Specifications

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/agent/activity_4_1/status` | Returns agent configuration, rule-based reasoning engine state, weighting matrix, LLM engine status, and latest telemetry result. |
| `POST` | `/api/agent/activity_4_1/evaluate` | Evaluates combined Vision and Audio signals using contextual rule-based reasoning; returns interpretable engagement index and explainable diagnosis. |
| `POST` | `/api/agent/activity_4_1/llm_insight` | Directly invokes `InsightGenerator` matching reference image with session telemetry to generate AI insight and recommendation. |
| `GET` | `/api/agent/activity_4_1/reasoning_history` | Returns sliding window history of multimodal reasoning evaluations. |
| `GET` | `/api/agent/activity_4_1/rules` | Returns the complete catalog of explainable multimodal rules (M1 to M6) with mathematical criteria and educational rationales. |

---

## 6. Frontend Integration

1. **Top Navigation Button:** Added `openMultimodalAgentBtn` ("🤖 Activity 4.1 Agent") to [`frontend/index.html`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/index.html).
2. **Modal 8 (Multimodal Agent Explorer):**
   - Displays real-time Composite Engagement Index with state badge and trend delta.
   - Shows active Rule Triggered badge, Confidence percentage, and Dominant Modality attribution chip.
   - Contains the **Contextual Explainable Diagnosis** callout box.
   - Features the **LLM Pedagogical Insight Generator** card with Groq model badge, live AI insight, actionable teaching recommendation, and "Regenerate Insight" trigger.
   - Includes the complete **Contextual Multimodal Rule Catalog** grid for transparent rule inspection.
3. **Reactive Controller Integration:** Added `openMultimodalAgentModal()`, `closeMultimodalAgentModal()`, `fetchMultimodalAgentStatus()`, `updateMultimodalAgentModalState()`, and `refreshLlmInsight()` in [`frontend/js/app.js`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/frontend/js/app.js).

---

## 7. Verification & Automated Test Coverage

The test suite in [`tests/test_system.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/tests/test_system.py) validates Activity 4.1 through 10 dedicated unit and integration tests:

1. `test_epic4_activity4_1_llm_insights_generator`: Validates `InsightGenerator` initialization, prompt formulation, and insight/recommendation parsing with offline fallback.
2. `test_epic4_activity4_1_multimodal_agent_initialization`: Validates `MultimodalAgent` parameter weights, drop threshold, and history initialization.
3. `test_epic4_activity4_1_rule_based_reasoning_high_flow`: Verifies Rule M1 triggers `HIGH_FLOW` with high visual attention in a quiet room.
4. `test_epic4_activity4_1_rule_based_reasoning_visual_distraction`: Verifies Rule M2 triggers `PASSIVE_DISENGAGEMENT` when gaze drifts in a quiet room.
5. `test_epic4_activity4_1_rule_based_reasoning_interactive_resonance`: Verifies Rule M3 triggers `COLLABORATIVE_ACTIVE` under high turn-taking and active gaze.
6. `test_epic4_activity4_1_rule_based_reasoning_acoustic_disruption`: Verifies Rule M4 triggers `ACOUSTIC_DISRUPTION` when noise level $\ge 75\text{ dB SPL}$.
7. `test_epic4_activity4_1_rule_based_reasoning_concept_freeze`: Verifies Rule M5 triggers `CONCEPT_HESITATION` when silence stalls during Q&A despite focused gaze.
8. `test_epic4_activity4_1_rule_based_reasoning_monologue_fatigue`: Verifies Rule M6 triggers `FATIGUE_RESTLESSNESS` after continuous monologue $\ge 8\text{ min}$.
9. `test_epic4_activity4_1_explainable_engagement_estimation`: Validates factor breakdown attribution percentages, dominant modality determination, and serialization.
10. `test_epic4_activity4_1_api_endpoints`: Verifies all 5 FastAPI Activity 4.1 REST endpoints asynchronously.

### Full Test Execution Results
```powershell
.\.venv\Scripts\python.exe -m unittest tests/test_system.py
.........................................
----------------------------------------------------------------------
Ran 41 tests in 5.697s

OK
```
**Result: 41/41 Tests Passed (100% Success Rate across all Epics 1, 2, 3, and 4).**
