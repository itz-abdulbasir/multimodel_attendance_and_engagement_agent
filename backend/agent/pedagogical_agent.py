"""
Multimodal Attendance & Engagement Agent - AI Pedagogical Decision Support
Epic 7: Tasks 13 & 14 (TASK-13, TASK-14) - Reasoning Engine & Pedagogical Suggestion Generator
"""

import time
from typing import Dict, List, Any, Optional
from backend.db.database import DatabaseManager
from backend.core.recommendations_engine import RecommendationsEngine, RecommendationItem

class TeachingSuggestion:
    def __init__(self, alert_level: str, title: str, reason: str, recommendation: str, context: Dict[str, Any]):
        self.alert_level = alert_level      # 'INFO', 'ADVISORY', 'ACTIONABLE'
        self.title = title
        self.reason = reason
        self.recommendation = recommendation
        self.context = context
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_level": self.alert_level,
            "title": self.title,
            "reason": self.reason,
            "recommendation": self.recommendation,
            "context": self.context,
            "timestamp": self.timestamp
        }


class PedagogicalReasoningAgent:
    """
    Intelligent assistive agent providing context-aware teaching recommendations
    based on multimodal classroom dynamics and pedagogical heuristics.
    """

    def __init__(self, db: DatabaseManager, session_id: str, cooldown_seconds: float = 40.0):
        self.db = db
        self.session_id = session_id
        self.cooldown_seconds = cooldown_seconds
        self.last_suggestion_time = 0.0
        self.recent_suggestions: List[Dict[str, Any]] = []
        self.recommendations_engine = RecommendationsEngine(cooldown_seconds=cooldown_seconds)

    def evaluate_classroom_state(self, fused_data: Dict[str, Any], audio_data: Dict[str, Any],
                                 session_elapsed: float) -> Optional[Dict[str, Any]]:
        """
        Applies pedagogical decision rules to detect instructional friction and generate suggestions.
        """
        now = time.time()
        if (now - self.last_suggestion_time) < self.cooldown_seconds:
            return None  # Under cooldown to prevent cognitive overload

        ei = fused_data.get("engagement_index", 75.0)
        trend = fused_data.get("trend", "STABLE")
        v_att = fused_data.get("visual_attention_score", 0.70)
        drop_alert = fused_data.get("attention_drop_alert", False)
        
        monologue_sec = audio_data.get("consecutive_monologue_sec", 0.0)
        silence_sec = audio_data.get("consecutive_silence_sec", 0.0)
        rhythm_state = audio_data.get("rhythm_state", "INSTRUCTOR_MONOLOGUE")

        suggestion: Optional[TeachingSuggestion] = None

        # Rule 1: Sudden Collective Attention Drop
        if drop_alert or (trend == "DROPPING" and ei < 58.0):
            suggestion = TeachingSuggestion(
                alert_level="ACTIONABLE",
                title="Pacing Check: Engagement Dip Detected",
                reason=f"Classroom Engagement Index dropped by over {fused_data.get('trend_delta', 15)}% in recent minutes.",
                recommendation="Pause current slide. Pose a quick comprehension check question or run a 60-second interactive poll.",
                context={"engagement_index": ei, "trend": trend}
            )

        # Rule 2: Prolonged Monologue (> 10-12 minutes)
        elif monologue_sec > 600.0 and v_att < 0.65:
            minutes = int(monologue_sec // 60)
            suggestion = TeachingSuggestion(
                alert_level="ADVISORY",
                title=f"Lecture Fatigue: {minutes}m Continuous Monologue",
                reason="Sustained continuous presentation with declining visual focus indicates cognitive saturation.",
                recommendation="Transition to a 2-minute 'Think-Pair-Share' peer discussion or ask for student reflections.",
                context={"monologue_minutes": minutes, "visual_attention": v_att}
            )

        # Rule 3: Prolonged Silence Disconnect (> 5 min during lecture)
        elif silence_sec > 300.0 and rhythm_state != "SILENT_STUDY":
            suggestion = TeachingSuggestion(
                alert_level="ADVISORY",
                title="Classroom Acoustic Hesitation",
                reason="Extended classroom silence detected outside scheduled quiet exercise time.",
                recommendation="Clarify if students need additional scaffolding or reframe the previous concept with an example.",
                context={"silence_sec": silence_sec}
            )

        # Rule 4: High Restlessness / Fidgeting
        elif fused_data.get("motion_balance_score", 1.0) < 0.40 and ei < 60.0:
            suggestion = TeachingSuggestion(
                alert_level="ACTIONABLE",
                title="Physical Restlessness Spike",
                reason="Multiple participants exhibit elevated fidgeting and distracted lateral gaze.",
                recommendation="Introduce a 30-second stand-up stretch or switch presentation media (e.g., live demo / code walkthrough).",
                context={"motion_balance": fused_data.get("motion_balance_score")}
            )

        # Rule 5: Ambient Noise Disruption (Activity 3.2)
        spl_db = audio_data.get("noise_level_spl", 55.0)
        ambient_noise = audio_data.get("ambient_noise_level", "MODERATE")
        part_freq = audio_data.get("participation_frequency", 1.0)
        
        if ambient_noise == "LOUD_DISRUPTIVE" or spl_db >= 75.0:
            suggestion = TeachingSuggestion(
                alert_level="ACTIONABLE",
                title="Acoustic Disruption: Elevated Ambient Noise",
                reason=f"Classroom ambient noise reached {spl_db:.1f} dB SPL (Disruptive noise threshold exceeded).",
                recommendation="Pause lecture briefly to address room cross-talk or adjust microphone/speaker gain levels.",
                context={"noise_level_spl": spl_db, "ambient_condition": ambient_noise}
            )

        # Rule 6: Low Participation during Interactive Phase (Activity 3.2)
        elif rhythm_state == "QA_INTERACTION" and part_freq < 0.8 and session_elapsed > 120.0:
            suggestion = TeachingSuggestion(
                alert_level="ADVISORY",
                title="Low Discussion Turn-Taking Frequency",
                reason=f"Q&A phase is active but student vocal participation is minimal ({part_freq:.1f} turns/min).",
                recommendation="Use structured prompts, cold-call a student group, or invite anonymous digital question submissions.",
                context={"participation_frequency": part_freq, "rhythm_state": rhythm_state}
            )

        # Rule 7: Positive Engagement Reinforcement
        elif ei >= 85.0 and rhythm_state == "QA_INTERACTION":
            # Occasional positive reinforcement
            if len(self.recent_suggestions) == 0 or (now - self.last_suggestion_time) > 180.0:
                suggestion = TeachingSuggestion(
                    alert_level="INFO",
                    title="High Participatory Resonance",
                    reason="Strong visual attention aligned with active acoustic question-and-answer exchanges.",
                    recommendation="Great pacing! Good moment to introduce the next challenging challenge or problem set.",
                    context={"engagement_index": ei}
                )

        if suggestion:
            self.last_suggestion_time = now
            s_dict = suggestion.to_dict()
            self.recent_suggestions.insert(0, s_dict)
            if len(self.recent_suggestions) > 15:
                self.recent_suggestions.pop()

            # Save in database
            self.db.record_teaching_suggestion(
                session_id=self.session_id,
                alert_level=suggestion.alert_level,
                title=suggestion.title,
                reason=suggestion.reason,
                recommendation=suggestion.recommendation,
                context_metadata=suggestion.context
            )
            return s_dict

        return None

    def get_recent_suggestions(self) -> List[Dict[str, Any]]:
        return self.recent_suggestions

    def generate_recommendations(self, session_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Delegates to RecommendationsEngine for immediate feedback."""
        return self.recommendations_engine.generate_realtime_recommendations(session_status)

    def analyze_temporal_profile(self, temporal_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyzes full temporal engagement profile to produce recommendations."""
        return self.recommendations_engine.analyze_temporal_profile_for_recommendations(temporal_profile)
