"""
Multimodal Attendance & Engagement Agent - Core Multimodal Agent
Epic 4: AI Implementation - Activity 4.1: Multimodal Agent Implementation
Integrates Vision and Audio module outputs using rule-based reasoning and LLM insight generation.
"""

import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

from backend.core.llm_insights import InsightGenerator


@dataclass
class MultimodalReasoningResult:
    """Dataclass holding explainable multimodal agent reasoning telemetry."""
    timestamp: float
    engagement_index: float                # 0.0 to 100.0%
    engagement_state: str                  # HIGH_FLOW, PASSIVE_DISENGAGEMENT, COLLABORATIVE_ACTIVE, etc.
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
    raw_inputs: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MultimodalAgent:
    """
    Multimodal Agent - Core Intelligence Layer (Epic 4 / Activity 4.1).
    Fuses visual behavior (gaze, posture, motion) and acoustic dynamics (energy, noise levels, turn-taking)
    into contextual, interpretable, and explainable educational insights using deterministic rules and LLM generation.
    """

    def __init__(self,
                 weight_visual: float = 0.50,
                 weight_motion: float = 0.20,
                 weight_audio: float = 0.30,
                 drop_threshold: float = 20.0,
                 history_limit: int = 100,
                 groq_api_key: Optional[str] = None):
        self.w_visual = weight_visual
        self.w_motion = weight_motion
        self.w_audio = weight_audio
        self.drop_threshold = drop_threshold
        self.history_limit = history_limit
        
        self.insight_generator = InsightGenerator(api_key=groq_api_key)
        self.reasoning_history: List[MultimodalReasoningResult] = []
        self.running_scores: List[float] = []

    def evaluate(self, visual_data: Dict[str, Any], audio_data: Dict[str, Any]) -> MultimodalReasoningResult:
        """
        Executes unified multimodal reasoning across Vision and Audio inputs.
        Applies interpretable, contextual rules to diagnose classroom engagement.
        """
        now = time.time()

        # -------------------------------------------------------------
        # 1. Parse & Normalize Vision Features
        # -------------------------------------------------------------
        raw_v_att = visual_data.get("average_visual_attention", 0.75)
        v_attention = raw_v_att if raw_v_att <= 1.0 else (raw_v_att / 100.0)
        v_attention = max(0.0, min(1.0, float(v_attention)))

        raw_motion = float(visual_data.get("average_motion_energy", 0.05))
        # Motion balance: moderate motion is healthy; extreme restlessness or static dormancy penalized
        if raw_motion < 0.02:
            motion_balance = 0.40  # Static dormancy penalty
        elif raw_motion > 0.45:
            motion_balance = 0.35  # Restless jitter penalty
        elif raw_motion > 0.25:
            motion_balance = 0.70  # Elevated movement
        else:
            motion_balance = 0.95  # Normal focused responsiveness

        active_participants = int(visual_data.get("active_participants_count", 0))

        # -------------------------------------------------------------
        # 2. Parse & Normalize Audio Features
        # -------------------------------------------------------------
        spl_db = float(audio_data.get("noise_level_spl", 55.0))
        ambient_noise = audio_data.get("ambient_noise_level", "MODERATE")
        noise_trend = audio_data.get("ambient_noise_trend", "STABLE")
        rhythm_state = audio_data.get("rhythm_state", "INSTRUCTOR_MONOLOGUE")
        speech_state = audio_data.get("signal_classification", "ACTIVE_SPEECH")
        part_freq = float(audio_data.get("participation_frequency", 1.0))
        interaction_intensity = float(audio_data.get("interaction_intensity", 0.40))
        monologue_sec = float(audio_data.get("consecutive_monologue_sec", 0.0))
        silence_sec = float(audio_data.get("consecutive_silence_sec", 0.0))

        # Acoustic interaction score [0.0 - 1.0] based on educational context
        if rhythm_state in ["QA_INTERACTION", "COLLABORATIVE_BUZZ"]:
            # Active verbal interaction is positive
            audio_score = min(1.0, 0.40 + (part_freq / 4.0) * 0.40 + interaction_intensity * 0.20)
        elif rhythm_state == "INSTRUCTOR_MONOLOGUE":
            # Attentive quiet listening is positive during lecture
            if ambient_noise in ["QUIET", "MODERATE"] and spl_db < 65.0:
                audio_score = 0.85 if v_attention >= 0.60 else 0.50
            else:
                audio_score = 0.40  # Room cross-talk during lecture
        else:  # SILENT_STUDY
            audio_score = 0.90 if ambient_noise == "QUIET" else 0.50

        audio_score = max(0.0, min(1.0, float(audio_score)))

        # -------------------------------------------------------------
        # 3. Dynamic Composite Engagement Index (EI: 0 to 100%)
        # -------------------------------------------------------------
        composite_ei = (
            self.w_visual * v_attention +
            self.w_motion * motion_balance +
            self.w_audio * audio_score
        ) * 100.0
        composite_ei = round(max(0.0, min(100.0, composite_ei)), 1)

        # Track rolling score history
        self.running_scores.append(composite_ei)
        if len(self.running_scores) > 30:
            self.running_scores.pop(0)

        # Trend & Anomaly Calculation
        if len(self.running_scores) >= 10:
            past_mean = sum(self.running_scores[:5]) / 5.0
            recent_mean = sum(self.running_scores[-5:]) / 5.0
            trend_delta = round(recent_mean - past_mean, 1)
            if trend_delta > 5.0:
                trend = "RISING"
            elif trend_delta < -5.0:
                trend = "FALLING"
            else:
                trend = "STABLE"
        else:
            trend_delta = 0.0
            trend = "STABLE"

        attention_drop_alert = False
        if len(self.running_scores) >= 15:
            baseline = sum(self.running_scores[:10]) / 10.0
            if (baseline - composite_ei) >= self.drop_threshold:
                attention_drop_alert = True

        # Dominant modality detection
        vis_contrib = self.w_visual * v_attention * 100.0
        aud_contrib = self.w_audio * audio_score * 100.0
        if abs(vis_contrib - aud_contrib) < 8.0:
            dominant_modality = "BALANCED"
        elif vis_contrib > aud_contrib:
            dominant_modality = "VISUAL_DOMINANT"
        else:
            dominant_modality = "AUDIO_DOMINANT"

        # -------------------------------------------------------------
        # 4. Contextual Rule-Based Multimodal Reasoning
        # -------------------------------------------------------------
        rule_triggered = "M0_BALANCED_LEARNING"
        engagement_state = "BALANCED_FLOW"
        confidence = 0.80
        diagnosis = "Classroom demonstrates stable visual attention and acoustic balance."

        # Rule M4: Acoustic Chaos / Cross-Talk Disruption
        if ambient_noise == "LOUD_DISRUPTIVE" or spl_db >= 75.0 or (spl_db >= 70.0 and raw_motion > 0.30):
            rule_triggered = "M4_ACOUSTIC_CHAOS_DISRUPTION"
            engagement_state = "ACOUSTIC_DISRUPTION"
            confidence = 0.95
            diagnosis = (
                f"Elevated ambient sound ({spl_db:.1f} dB SPL, {ambient_noise}) accompanied by physical movement "
                f"indicates room cross-talk or background disruption rather than structured participation."
            )

        # Rule M6: Extended Monologue Fatigue & Restlessness
        elif monologue_sec >= 480.0 and (motion_balance < 0.60 or v_attention < 0.60):
            rule_triggered = "M6_EXTENDED_MONOLOGUE_FATIGUE"
            engagement_state = "FATIGUE_RESTLESSNESS"
            confidence = 0.89
            minutes = int(monologue_sec // 60)
            diagnosis = (
                f"Continuous instructor monologue exceeding {minutes} minutes has saturated working memory, "
                f"manifested through physical fidgeting (motion balance {motion_balance:.2f}) and wandering visual focus."
            )

        # Rule M5: Concept Barrier / Question Freeze
        elif rhythm_state == "QA_INTERACTION" and (silence_sec >= 20.0 or part_freq < 0.8) and v_attention >= 0.65:
            rule_triggered = "M5_QUESTION_CONCEPT_FREEZE"
            engagement_state = "CONCEPT_HESITATION"
            confidence = 0.87
            diagnosis = (
                f"Learners maintain board/instructor visual alignment ({v_attention*100:.1f}%) but verbal turn-taking "
                f"is stagnant ({part_freq:.1f} turns/min), signaling conceptual hesitation or fear of answering."
            )

        # Rule M2: Passive Visual Distraction in Quiet Room
        elif v_attention < 0.55 and spl_db < 55.0 and rhythm_state != "QA_INTERACTION":
            rule_triggered = "M2_PASSIVE_VISUAL_DISENGAGEMENT"
            engagement_state = "PASSIVE_DISENGAGEMENT"
            confidence = 0.88
            diagnosis = (
                f"Room is acoustically quiet ({spl_db:.1f} dB SPL) but visual gaze has significantly drifted ({v_attention*100:.1f}% focus), "
                f"indicating passive daydreaming or disengagement from lecture content."
            )

        # Rule M3: Vibrant Interactive Discussion Resonance
        elif (rhythm_state in ["QA_INTERACTION", "COLLABORATIVE_BUZZ"] or part_freq >= 1.5) and v_attention >= 0.60 and interaction_intensity >= 0.35:
            rule_triggered = "M3_VIBRANT_INTERACTIVE_RESONANCE"
            engagement_state = "COLLABORATIVE_ACTIVE"
            confidence = 0.91
            diagnosis = (
                f"High-frequency student-teacher turn-taking ({part_freq:.1f} turns/min) aligned with active visual engagement "
                f"({v_attention*100:.1f}%) confirms collaborative learning resonance."
            )

        # Rule M1: High Instructional Flow
        elif v_attention >= 0.70 and motion_balance >= 0.70 and spl_db < 65.0:
            rule_triggered = "M1_HIGH_INSTRUCTIONAL_FLOW"
            engagement_state = "HIGH_FLOW"
            confidence = 0.92
            diagnosis = (
                f"High visual gaze convergence ({v_attention*100:.1f}%) combined with quiet, responsive listening "
                f"establishes optimal cognitive absorption and instructional flow."
            )

        # -------------------------------------------------------------
        # 5. LLM Insights Synthesis (InsightGenerator)
        # -------------------------------------------------------------
        session_telemetry = {
            "engagement_index": composite_ei,
            "visual_attention_score": v_attention,
            "motion_balance_score": motion_balance,
            "rhythm_state": rhythm_state,
            "noise_level_spl": spl_db,
            "ambient_noise_level": ambient_noise,
            "signal_classification": speech_state,
            "participation_frequency": part_freq,
            "trend": trend,
            "active_participants": active_participants,
            "rule_triggered": rule_triggered,
            "attention_drop_alert": attention_drop_alert
        }

        llm_output = self.insight_generator.generate_classroom_insight(session_telemetry)
        actionable_insight = llm_output.get("insight", "Classroom dynamics are stable.")
        teaching_recommendation = llm_output.get("recommendation", "Maintain current instructional rhythm.")

        factor_breakdown = {
            "visual_attention_component": round(vis_contrib, 1),
            "motion_balance_component": round(self.w_motion * motion_balance * 100.0, 1),
            "audio_interaction_component": round(aud_contrib, 1),
            "composite_score": composite_ei
        }

        result = MultimodalReasoningResult(
            timestamp=now,
            engagement_index=composite_ei,
            engagement_state=engagement_state,
            confidence=round(confidence, 2),
            dominant_modality=dominant_modality,
            rule_triggered=rule_triggered,
            explainable_diagnosis=diagnosis,
            actionable_insight=actionable_insight,
            teaching_recommendation=teaching_recommendation,
            trend=trend,
            trend_delta=trend_delta,
            attention_drop_alert=attention_drop_alert,
            factor_breakdown=factor_breakdown,
            raw_inputs={
                "visual_attention_ratio": round(v_attention, 3),
                "motion_energy": round(raw_motion, 3),
                "sound_pressure_spl": round(spl_db, 1),
                "ambient_condition": ambient_noise,
                "rhythm_state": rhythm_state,
                "turn_taking_rate": round(part_freq, 2),
                "llm_model": llm_output.get("model", "offline_rule_reasoner"),
                "is_offline_llm": llm_output.get("is_offline", True)
            }
        )

        self.reasoning_history.append(result)
        if len(self.reasoning_history) > self.history_limit:
            self.reasoning_history.pop(0)

        return result

    def get_reasoning_history(self) -> List[Dict[str, Any]]:
        """Returns historical reasoning logs."""
        return [r.to_dict() for r in self.reasoning_history]

    def get_latest_result(self) -> Optional[Dict[str, Any]]:
        """Returns the most recent reasoning evaluation."""
        if not self.reasoning_history:
            return None
        return self.reasoning_history[-1].to_dict()
