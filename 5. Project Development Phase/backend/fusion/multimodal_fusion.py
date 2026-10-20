"""
Multimodal Attendance & Engagement Agent - Multimodal Signal Fusion
Epic 4: AI Implementation - Activity 4.2: Multimodal Signal Fusion
Synchronizes and aggregates visual indicators (presence, movement, inactivity)
and audio indicators (noise levels, speech activity) into a unified, extensible data structure.
"""

import time
import math
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

from backend.core.ai_suggestions import AISuggestionEngine


class MovementPattern:
    """Standardized movement and posture patterns for visual signal fusion."""
    STATIC_DORMANT = "STATIC_DORMANT"
    FOCUSED_STABLE = "FOCUSED_STABLE"
    ELEVATED_ACTIVE = "ELEVATED_ACTIVE"
    RESTLESS_JITTER = "RESTLESS_JITTER"


class DominantModality:
    """Classification of sensory channel influence in fused telemetry."""
    VISUAL_DOMINANT = "VISUAL_DOMINANT"
    AUDIO_DOMINANT = "AUDIO_DOMINANT"
    BALANCED = "BALANCED"


@dataclass
class UnifiedMultimodalRepresentation:
    """
    Unified Multimodal Representation (Activity 4.2).
    Synchronized data representation fusing Vision and Audio signals,
    designed with an extensible architecture for future sensory modalities.
    """
    timestamp: float
    epoch_id: int
    session_id: str
    sync_jitter_ms: float

    # 1. Visual Indicators (aligned with timestamps)
    average_visual_attention: float        # 0.0 to 1.0
    presence_duration_seconds: float       # Cumulative seconds
    presence_ratio_percent: float          # 0.0 to 100.0%
    movement_pattern: str                  # FOCUSED_STABLE, RESTLESS_JITTER, STATIC_DORMANT, ELEVATED_ACTIVE
    average_motion_energy: float           # Normalized 0.0 to 1.0
    inactivity_seconds: float              # Dormant posture duration
    active_participants_count: int         # Count of detected learners
    gaze_direction_distribution: Dict[str, int]
    per_student_visuals: List[Dict[str, Any]]

    # 2. Audio Indicators (aligned with timestamps)
    noise_level_spl: float                 # Calibrated dB SPL
    noise_level_db: float                  # Digital dBFS
    ambient_noise_level: str               # QUIET, MODERATE, ELEVATED, LOUD_DISRUPTIVE
    ambient_noise_trend: str               # RISING, FALLING, STABLE
    speech_state: str                      # SILENCE, BACKGROUND_NOISE, ACTIVE_SPEECH
    vad_active: bool                       # Voice activity presence
    rhythm_state: str                      # INSTRUCTOR_MONOLOGUE, QA_INTERACTION, etc.
    interaction_intensity: float           # 0.0 to 1.0
    participation_frequency: float         # Turns per minute
    speaker_turns_count: int               # Cumulative speaker turns

    # 3. Cross-Modal Correlation & Coherence
    cross_modal_correlation: float         # -1.0 to 1.0 (Pearson correlation over time window)
    cross_modal_coherence: float           # 0.0 to 1.0 (Harmonious sensory alignment)
    dominant_modality: str                 # VISUAL_DOMINANT, AUDIO_DOMINANT, BALANCED

    # 4. Proportional Multimodal Contributions
    weight_visual: float                   # Default: 0.50
    weight_motion: float                   # Default: 0.20
    weight_audio: float                    # Default: 0.30
    visual_contribution: float             # w_vis * S_vis * 100
    motion_contribution: float             # w_mot * S_mot * 100
    audio_contribution: float              # w_aud * S_aud * 100
    composite_engagement_index: float      # 0.0 to 100.0%
    trend: str                             # RISING, DROPPING, STABLE
    trend_delta: float                     # Delta change in rolling window
    attention_drop_alert: bool             # Anomaly flag

    # 5. Extensibility Hook for Future Enhancements
    custom_modalities: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes unified representation to JSON-compliant dictionary."""
        d = asdict(self)
        # Ensure backward compatibility keys matching earlier consumers
        d["engagement_index"] = self.composite_engagement_index
        d["active_participants"] = self.active_participants_count
        d["visual_attention_score"] = self.average_visual_attention
        d["motion_balance_score"] = round(self.motion_contribution / (self.weight_motion * 100.0), 3) if self.weight_motion > 0 else 0.95
        d["audio_engagement_score"] = round(self.audio_contribution / (self.weight_audio * 100.0), 3) if self.weight_audio > 0 else 0.85
        return d

    def add_custom_modality(self, modality_name: str, payload: Dict[str, Any]) -> None:
        """Extensibility method: attaches external sensors (e.g. EDA, smart pen, EEG)."""
        self.custom_modalities[modality_name] = {
            "timestamp": time.time(),
            "data": payload
        }


class MultimodalFusionEngine:
    """
    Multimodal Signal Fusion Engine (Activity 4.2).
    Synchronizes signals from the Vision Module and Audio Module via timestamps,
    aligns visual indicators with audio dynamics, ensures proportional multimodal contribution,
    and supports extensibility for future educational sensory modalities.
    """

    def __init__(self,
                 weight_visual: float = 0.50,
                 weight_motion: float = 0.20,
                 weight_audio: float = 0.30,
                 drop_alert_threshold: float = 20.0,
                 window_size: int = 30,
                 groq_api_key: Optional[str] = None):
        self.weight_visual = weight_visual
        self.weight_motion = weight_motion
        self.weight_audio = weight_audio
        self.drop_alert_threshold = drop_alert_threshold
        self.window_size = window_size
        
        # Historical buffers for temporal synchronization and correlation
        self.epoch_counter = 0
        self.fused_history: List[UnifiedMultimodalRepresentation] = []
        self.running_scores: List[float] = []
        self.visual_history: List[float] = []
        self.audio_history: List[float] = []
        
        # AI Suggestion Engine (Reference image: backend/core/ai_suggestions.py)
        self.ai_suggestion_engine = AISuggestionEngine(api_key=groq_api_key)

    def synchronize_and_fuse(self,
                             visual_data: Dict[str, Any],
                             audio_data: Dict[str, Any],
                             session_id: str = "DEFAULT-SESSION",
                             custom_modalities: Optional[Dict[str, Any]] = None) -> UnifiedMultimodalRepresentation:
        """
        Synchronizes Vision and Audio signals using timestamp alignment and generates
        a unified, proportional, and extensible multimodal data representation.
        """
        now = time.time()
        self.epoch_counter += 1

        # -------------------------------------------------------------
        # 1. Timestamp-Based Synchronization & Jitter Calculation
        # -------------------------------------------------------------
        t_vis = float(visual_data.get("timestamp", now))
        t_aud = float(audio_data.get("timestamp", now))
        sync_jitter_ms = round(abs(t_vis - t_aud) * 1000.0, 2)

        # -------------------------------------------------------------
        # 2. Extract & Normalize Visual Indicators
        # -------------------------------------------------------------
        raw_v_att = visual_data.get("average_visual_attention", 0.75)
        v_attention = raw_v_att if raw_v_att <= 1.0 else (raw_v_att / 100.0)
        v_attention = max(0.0, min(1.0, float(v_attention)))

        raw_motion = float(visual_data.get("average_motion_energy", 0.05))
        presence_duration = float(visual_data.get("presence_duration_seconds", visual_data.get("active_seconds", 300.0)))
        presence_ratio = float(visual_data.get("presence_ratio_percent", visual_data.get("presence_ratio", 85.0)))
        inactivity_sec = float(visual_data.get("inactivity_seconds", 0.0))
        active_count = int(visual_data.get("active_participants_count", 0))
        gaze_dist = visual_data.get("gaze_direction_distribution", {
            "FORWARD_BOARD": 6, "LATERAL_PEER": 1, "DOWNWARD_NOTE": 1, "DIVERTED": 0
        })
        per_student_visuals = visual_data.get("per_student_visuals", visual_data.get("student_metrics", []))

        # Classify Movement Pattern
        if raw_motion < 0.02:
            movement_pattern = "STATIC_DORMANT"
            motion_balance = 0.40  # Static posture penalty
        elif raw_motion > 0.45:
            movement_pattern = "RESTLESS_JITTER"
            motion_balance = 0.35  # Restlessness penalty
        elif raw_motion > 0.25:
            movement_pattern = "ELEVATED_ACTIVE"
            motion_balance = 0.70  # Active movement
        else:
            movement_pattern = "FOCUSED_STABLE"
            motion_balance = 0.95  # Healthy note-taking & focus

        # -------------------------------------------------------------
        # 3. Extract & Normalize Audio Indicators
        # -------------------------------------------------------------
        spl_db = float(audio_data.get("noise_level_spl", 55.0))
        db_level = float(audio_data.get("noise_level_db", -30.0))
        ambient_noise = audio_data.get("ambient_noise_level", "MODERATE")
        noise_trend = audio_data.get("ambient_noise_trend", "STABLE")
        speech_state = audio_data.get("speech_state", audio_data.get("signal_classification", "ACTIVE_SPEECH"))
        vad_active = bool(audio_data.get("vad_active", True))
        rhythm_state = audio_data.get("rhythm_state", audio_data.get("sound_activity_pattern", "INSTRUCTOR_MONOLOGUE"))
        part_freq = float(audio_data.get("participation_frequency", 1.0))
        interaction_intensity = float(audio_data.get("interaction_intensity", 0.40))
        speaker_turns = int(audio_data.get("speaker_turns", audio_data.get("speaker_turns_count", 0)))

        # Evaluate Audio Proportional Score based on instructional rhythm
        if rhythm_state in ["QA_INTERACTION", "COLLABORATIVE_BUZZ"]:
            # Active participatory interaction indicates healthy classroom resonance
            audio_score = min(1.0, 0.40 + (part_freq / 4.0) * 0.40 + interaction_intensity * 0.20)
        elif rhythm_state == "INSTRUCTOR_MONOLOGUE":
            # During lecture, attentive quiet listening indicates optimal reception
            if ambient_noise in ["QUIET", "MODERATE"] and spl_db < 65.0:
                audio_score = 0.85 if v_attention >= 0.60 else 0.50
            else:
                audio_score = 0.40  # Classroom cross-talk during presentation
        else:  # SILENT_STUDY
            audio_score = 0.90 if ambient_noise == "QUIET" else 0.50

        audio_score = max(0.0, min(1.0, float(audio_score)))

        # -------------------------------------------------------------
        # 4. Proportional Multimodal Contribution & Engagement Index
        # -------------------------------------------------------------
        vis_contrib = round(self.weight_visual * v_attention * 100.0, 2)
        mot_contrib = round(self.weight_motion * motion_balance * 100.0, 2)
        aud_contrib = round(self.weight_audio * audio_score * 100.0, 2)

        composite_ei = round(vis_contrib + mot_contrib + aud_contrib, 1)
        composite_ei = max(0.0, min(100.0, composite_ei))

        # Update historical score buffers
        self.running_scores.append(composite_ei)
        self.visual_history.append(v_attention)
        self.audio_history.append(audio_score)
        if len(self.running_scores) > self.window_size:
            self.running_scores.pop(0)
            self.visual_history.pop(0)
            self.audio_history.pop(0)

        # -------------------------------------------------------------
        # 5. Cross-Modal Correlation & Coherence Analysis
        # -------------------------------------------------------------
        cross_modal_correlation = self._compute_cross_modal_correlation()
        cross_modal_coherence = self._compute_cross_modal_coherence(v_attention, audio_score, rhythm_state, spl_db)

        # Dominant Modality Determination
        if abs(vis_contrib - aud_contrib) <= 8.0:
            dominant_modality = "BALANCED"
        elif vis_contrib > aud_contrib:
            dominant_modality = "VISUAL_DOMINANT"
        else:
            dominant_modality = "AUDIO_DOMINANT"

        # Trend & Anomaly Drop Detection
        if len(self.running_scores) >= 10:
            past_mean = sum(self.running_scores[:5]) / 5.0
            recent_mean = sum(self.running_scores[-5:]) / 5.0
            trend_delta = round(recent_mean - past_mean, 1)
            if trend_delta > 5.0:
                trend = "RISING"
            elif trend_delta < -5.0:
                trend = "DROPPING"
            else:
                trend = "STABLE"
        else:
            trend_delta = 0.0
            trend = "STABLE"

        attention_drop_alert = False
        if len(self.running_scores) >= 15:
            baseline = sum(self.running_scores[:10]) / 10.0
            if (baseline - composite_ei) >= self.drop_alert_threshold:
                attention_drop_alert = True

        # -------------------------------------------------------------
        # 6. Assemble Unified Multimodal Representation
        # -------------------------------------------------------------
        unified_packet = UnifiedMultimodalRepresentation(
            timestamp=now,
            epoch_id=self.epoch_counter,
            session_id=session_id,
            sync_jitter_ms=sync_jitter_ms,
            average_visual_attention=round(v_attention, 3),
            presence_duration_seconds=round(presence_duration, 1),
            presence_ratio_percent=round(presence_ratio, 1),
            movement_pattern=movement_pattern,
            average_motion_energy=round(raw_motion, 3),
            inactivity_seconds=round(inactivity_sec, 1),
            active_participants_count=active_count,
            gaze_direction_distribution=gaze_dist,
            per_student_visuals=per_student_visuals,
            noise_level_spl=round(spl_db, 1),
            noise_level_db=round(db_level, 1),
            ambient_noise_level=ambient_noise,
            ambient_noise_trend=noise_trend,
            speech_state=speech_state,
            vad_active=vad_active,
            rhythm_state=rhythm_state,
            interaction_intensity=round(interaction_intensity, 3),
            participation_frequency=round(part_freq, 2),
            speaker_turns_count=speaker_turns,
            cross_modal_correlation=round(cross_modal_correlation, 3),
            cross_modal_coherence=round(cross_modal_coherence, 3),
            dominant_modality=dominant_modality,
            weight_visual=self.weight_visual,
            weight_motion=self.weight_motion,
            weight_audio=self.weight_audio,
            visual_contribution=vis_contrib,
            motion_contribution=mot_contrib,
            audio_contribution=aud_contrib,
            composite_engagement_index=composite_ei,
            trend=trend,
            trend_delta=trend_delta,
            attention_drop_alert=attention_drop_alert,
            custom_modalities=custom_modalities or {}
        )

        self.fused_history.append(unified_packet)
        if len(self.fused_history) > 200:
            self.fused_history.pop(0)

        return unified_packet

    def fuse_signals(self, visual_data: Dict[str, Any], audio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Backward-compatible entry point returning a flat dictionary."""
        unified = self.synchronize_and_fuse(visual_data, audio_data)
        return unified.to_dict()

    def generate_ai_suggestions(self, unified_data: Optional[UnifiedMultimodalRepresentation] = None) -> List[Dict[str, Any]]:
        """Invokes AISuggestionEngine using the latest unified multimodal data packet."""
        if unified_data is None:
            if not self.fused_history:
                return []
            unified_data = self.fused_history[-1]

        session_telemetry = unified_data.to_dict()
        return self.ai_suggestion_engine.generate_suggestions(session_telemetry)

    def _compute_cross_modal_correlation(self) -> float:
        """Calculates Pearson correlation between rolling visual attention and audio score."""
        n = len(self.visual_history)
        if n < 5:
            return 0.50  # Baseline neutral positive correlation

        mean_v = sum(self.visual_history) / n
        mean_a = sum(self.audio_history) / n

        num = sum((v - mean_v) * (a - mean_a) for v, a in zip(self.visual_history, self.audio_history))
        den_v = sum((v - mean_v) ** 2 for v in self.visual_history)
        den_a = sum((a - mean_a) ** 2 for a in self.audio_history)

        denominator = math.sqrt(den_v * den_a)
        if denominator < 1e-6:
            return 0.0

        corr = num / denominator
        return max(-1.0, min(1.0, corr))

    def _compute_cross_modal_coherence(self, v_att: float, a_score: float, rhythm: str, spl_db: float) -> float:
        """
        Calculates cross-modal coherence (0.0 to 1.0).
        High coherence indicates that visual and audio channels reinforce the expected pedagogical state.
        """
        # Baseline difference between normalized scores
        similarity = 1.0 - abs(v_att - a_score)

        # Context adjustments
        if rhythm == "INSTRUCTOR_MONOLOGUE":
            # Coherent if students look at board and ambient noise is low
            if v_att >= 0.70 and spl_db < 60.0:
                coherence = 0.90
            elif v_att < 0.50 and spl_db >= 68.0:
                coherence = 0.30  # Simultaneous distraction and room chatter
            else:
                coherence = similarity * 0.85
        elif rhythm == "QA_INTERACTION":
            # Coherent if visual gaze is active and vocal turn-taking is active
            if v_att >= 0.65 and a_score >= 0.60:
                coherence = 0.95
            elif v_att >= 0.70 and a_score < 0.40:
                coherence = 0.50  # Visual alignment but speech freeze
            else:
                coherence = similarity * 0.90
        else:
            coherence = similarity * 0.80

        return max(0.0, min(1.0, coherence))
