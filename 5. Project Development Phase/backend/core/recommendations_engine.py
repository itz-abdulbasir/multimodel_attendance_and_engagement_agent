"""
Multimodal Classroom Intelligence & Attendance Agent
EPIC 5: Analytics and Recommendation Engine
Activity 5.1: Teaching Suggestion Logic (RecommendationsEngine)

This module implements instructor-facing, context-aware teaching suggestions
derived from multimodal engagement trends and temporal profiles.
Supports real-time alerts, warnings, and informational commendations
grounded in observable data trends and presented non-prescriptively.
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class RecommendationItem:
    """Represents a discrete context-aware pedagogical recommendation."""
    id: str
    type: str                   # 'alert' | 'warning' | 'info' (matching reference image)
    category: str               # 'individual_attention' | 'global_attention' | 'sustained_disengagement' | 'peak_engagement' | 'classroom_noise' | 'instructional_pacing' | 'prolonged_monologue'
    title: str                  # Short, human-readable title
    message: str                # Non-prescriptive, transparent message grounded in observable trends
    pedagogical_action: str     # Concrete teaching intervention
    observable_evidence: Dict[str, Any]  # Grounding data metrics
    confidence: float = 0.85    # Heuristic confidence (0.0 - 1.0)
    timestamp: float = field(default_factory=time.time)
    dismissed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RecommendationsEngine:
    """
    Rule-based recommendations engine for immediate instructional feedback and decision support.
    Bridges low-level signal analysis and high-level pedagogical guidance.
    """

    def __init__(self, cooldown_seconds: float = 20.0):
        self.cooldown_seconds = cooldown_seconds
        self.last_triggered_times: Dict[str, float] = {}
        self.recommendation_history: List[RecommendationItem] = []
        self._counter = 0

    def _generate_id(self, category: str) -> str:
        self._counter += 1
        return f"REC-{category[:3].upper()}-{int(time.time())}-{self._counter}"

    def _is_cooling_down(self, category: str, now: float) -> bool:
        last_t = self.last_triggered_times.get(category, 0.0)
        return (now - last_t) < self.cooldown_seconds

    def generate_realtime_recommendations(self, session_status: dict) -> List[Dict[str, Any]]:
        """
        Rule-based recommendations for immediate feedback.
        Input: Session status dict (people, emotions, attention, acoustic, temporal profiles)
        Output: List of { type: 'alert'|'warning'|'info', message: str, ... }
        
        Matches reference signature:
        def generate_realtime_recommendations(self, session_status: dict):
        """
        now = time.time()
        recs: List[RecommendationItem] = []

        # -------------------------------------------------------------
        # 1. Low Individual Attention Alert (Reference Image 2)
        # -------------------------------------------------------------
        people = session_status.get('people', [])
        avg_att = 0.0
        if people:
            # Calculate average attention across people
            att_values = [p.get('attention', 75.0) for p in people]
            avg_att = sum(att_values) / len(people)

            # Individual check: Flag students whose attention is < 40%
            if not self._is_cooling_down("individual_attention", now):
                for p in people:
                    att = p.get('attention', 75.0)
                    if att < 40:
                        p_id = p.get('id', p.get('name', 'Student'))
                        rec = RecommendationItem(
                            id=self._generate_id("individual"),
                            type="alert",
                            category="individual_attention",
                            title=f"Individual Attention Alert: {p_id}",
                            message=f"Student {p_id} is distracted ({att:.1f}%).",
                            pedagogical_action="Consider redirecting focus non-verbally, establishing brief eye contact, or checking comprehension during group work.",
                            observable_evidence={"student_id": p_id, "attention": att, "threshold": 40.0},
                            confidence=0.90,
                            timestamp=now
                        )
                        recs.append(rec)
                        self.last_triggered_times["individual_attention"] = now
                        break  # Limit to 1 individual alert per cycle to avoid flooding

        # -------------------------------------------------------------
        # 2. Global Attention Warning (Reference Image 2)
        # -------------------------------------------------------------
        if len(people) > 2 and avg_att < 60:
            if not self._is_cooling_down("global_attention", now):
                rec = RecommendationItem(
                    id=self._generate_id("global"),
                    type="warning",
                    category="global_attention",
                    title="Classwide Attention Warning",
                    message=f"Collective attention dipped below threshold (Average: {avg_att:.1f}%).",
                    pedagogical_action="Pacing check: Pose an active question, initiate a 60-second comprehension check, or pause for student questions.",
                    observable_evidence={"average_attention": round(avg_att, 1), "participant_count": len(people), "threshold": 60.0},
                    confidence=0.88,
                    timestamp=now
                )
                recs.append(rec)
                self.last_triggered_times["global_attention"] = now

        # -------------------------------------------------------------
        # 3. Sustained Disengagement (Extended Low-Engagement Periods)
        # -------------------------------------------------------------
        diseng_phases = session_status.get("disengagement_phases", [])
        overall_score = session_status.get("engagement_score", session_status.get("engagement_index", avg_att or 75.0))
        inactivity_sec = session_status.get("inactivity_seconds", 0.0)

        if diseng_phases or (overall_score < 50.0 and inactivity_sec > 45.0):
            if not self._is_cooling_down("sustained_disengagement", now):
                primary_cause = diseng_phases[0].get("primary_cause", "Prolonged Inactivity") if diseng_phases else "Prolonged Inactivity"
                rec = RecommendationItem(
                    id=self._generate_id("diseng"),
                    type="alert",
                    category="sustained_disengagement",
                    title="Extended Disengagement Detected",
                    message=f"Extended disengagement phase detected ({primary_cause}). Average engagement is {overall_score:.1f}%.",
                    pedagogical_action="Transition to an interactive activity: run a quick comprehension poll, initiate a Think-Pair-Share discussion, or take a 60-second cognitive stretch break.",
                    observable_evidence={
                        "engagement_score": round(overall_score, 1),
                        "primary_cause": primary_cause,
                        "inactivity_seconds": inactivity_sec,
                        "phases_count": len(diseng_phases)
                    },
                    confidence=0.92,
                    timestamp=now
                )
                recs.append(rec)
                self.last_triggered_times["sustained_disengagement"] = now

        # -------------------------------------------------------------
        # 4. Peak Engagement Periods (High-Interaction Reinforcement)
        # -------------------------------------------------------------
        peak_periods = session_status.get("peak_periods", [])
        if peak_periods or overall_score >= 82.0:
            if not self._is_cooling_down("peak_engagement", now):
                top_factor = peak_periods[0].get("top_factor", "Visual & Discussion Synergy") if peak_periods else "Visual & Discussion Synergy"
                rec = RecommendationItem(
                    id=self._generate_id("peak"),
                    type="info",
                    category="peak_engagement",
                    title="Peak Engagement Period Highlight",
                    message=f"High instructional resonance observed ({overall_score:.1f}%). Primary driver: {top_factor}.",
                    pedagogical_action="Current instructional modality is highly effective. Bookmark this segment and maintain this interactive pacing before transitioning to independent practice.",
                    observable_evidence={
                        "engagement_score": round(overall_score, 1),
                        "top_factor": top_factor,
                        "peak_periods_count": len(peak_periods)
                    },
                    confidence=0.95,
                    timestamp=now
                )
                recs.append(rec)
                self.last_triggered_times["peak_engagement"] = now

        # -------------------------------------------------------------
        # 5. Elevated Classroom Noise / Acoustic Disruption
        # -------------------------------------------------------------
        noise_spl = session_status.get("noise_level_spl", 55.0)
        ambient_cond = session_status.get("ambient_noise_level", "MODERATE")
        if noise_spl >= 75.0 or ambient_cond in ["LOUD_DISRUPTIVE", "ELEVATED"]:
            if not self._is_cooling_down("classroom_noise", now):
                rec = RecommendationItem(
                    id=self._generate_id("noise"),
                    type="warning",
                    category="classroom_noise",
                    title="Acoustic Classroom Management Cue",
                    message=f"Ambient noise level is elevated ({noise_spl:.1f} dB SPL, {ambient_cond}).",
                    pedagogical_action="Address side-conversations or room cross-talk. If intentional group dialogue, consider structuring speaker turns; otherwise check microphone/speaker gain.",
                    observable_evidence={"noise_level_spl": round(noise_spl, 1), "ambient_condition": ambient_cond, "threshold_spl": 75.0},
                    confidence=0.89,
                    timestamp=now
                )
                recs.append(rec)
                self.last_triggered_times["classroom_noise"] = now

        # -------------------------------------------------------------
        # 6. Attention Drops / Sudden Pacing Dips
        # -------------------------------------------------------------
        trend = session_status.get("trend", "STABLE")
        trend_delta = session_status.get("trend_delta", 0.0)
        if trend == "DROPPING" and (trend_delta >= 15.0 or overall_score < 62.0):
            if not self._is_cooling_down("instructional_pacing", now):
                rec = RecommendationItem(
                    id=self._generate_id("pacing"),
                    type="warning",
                    category="instructional_pacing",
                    title="Sudden Attention Drop Detected",
                    message=f"Engagement dropped by {trend_delta:.1f}% in recent segments.",
                    pedagogical_action="Check concept pacing. Students may be experiencing cognitive overload. Clarify the core takeaway or invite immediate clarifying questions.",
                    observable_evidence={"trend": trend, "trend_delta": round(trend_delta, 1), "current_score": round(overall_score, 1)},
                    confidence=0.87,
                    timestamp=now
                )
                recs.append(rec)
                self.last_triggered_times["instructional_pacing"] = now

        # -------------------------------------------------------------
        # 7. Prolonged Monologue Advisory (> 8-10 minutes)
        # -------------------------------------------------------------
        monologue_sec = session_status.get("consecutive_monologue_sec", 0.0)
        if monologue_sec >= 480.0:  # 8 minutes
            if not self._is_cooling_down("prolonged_monologue", now):
                minutes = int(monologue_sec // 60)
                rec = RecommendationItem(
                    id=self._generate_id("monologue"),
                    type="warning",
                    category="prolonged_monologue",
                    title=f"Lecture Fatigue Advisory ({minutes}m Monologue)",
                    message=f"Continuous instructor presentation for {minutes} minutes without student dialogue.",
                    pedagogical_action="Break the monologue with a 90-second student problem solve, call for questions, or ask a student volunteer to summarize the key point.",
                    observable_evidence={"monologue_seconds": monologue_sec, "monologue_minutes": minutes, "threshold_sec": 480.0},
                    confidence=0.86,
                    timestamp=now
                )
                recs.append(rec)
                self.last_triggered_times["prolonged_monologue"] = now

        # Record generated recommendations into history
        for r in recs:
            self.recommendation_history.insert(0, r)
        if len(self.recommendation_history) > 50:
            self.recommendation_history = self.recommendation_history[:50]

        return [r.to_dict() for r in recs]

    def analyze_temporal_profile_for_recommendations(self, temporal_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Processes a complete TemporalEngagementProfile and generates comprehensive recommendations.
        Analyzes attention fluctuations, peak periods, and disengagement phases.
        """
        session_status = {
            "engagement_score": temporal_profile.get("mean_engagement_score", 75.0),
            "disengagement_phases": temporal_profile.get("disengagement_phases", []),
            "peak_periods": temporal_profile.get("peak_periods", []),
            "people": []
        }

        # Fluctuation metrics
        fluct = temporal_profile.get("fluctuation_metrics", {})
        stability_index = fluct.get("stability_index", 80.0)
        std_dev = fluct.get("std_dev", 5.0)

        results = self.generate_realtime_recommendations(session_status)

        # Additional temporal analysis: High Fluctuation / Instability
        if stability_index < 60.0 or std_dev > 18.0:
            rec = RecommendationItem(
                id=self._generate_id("fluct"),
                type="warning",
                category="instructional_pacing",
                title="High Engagement Fluctuation Profile",
                message=f"High attention volatility observed (Stability Index: {stability_index:.1f}/100, StdDev: {std_dev:.1f}).",
                pedagogical_action="Consider establishing more predictable lesson cadence: anchor concept explanations with consistent review pauses.",
                observable_evidence={"stability_index": stability_index, "std_dev": std_dev},
                confidence=0.88,
                timestamp=time.time()
            )
            results.append(rec.to_dict())
            self.recommendation_history.insert(0, rec)

        return results

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns the most recent recommendations history."""
        return [r.to_dict() for r in self.recommendation_history[:limit]]

    def clear_history(self) -> None:
        """Clears recommendation history and cooldowns."""
        self.recommendation_history.clear()
        self.last_triggered_times.clear()
