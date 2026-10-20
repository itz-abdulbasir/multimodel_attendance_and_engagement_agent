"""
Multimodal Attendance & Engagement Agent - Engagement Scoring Logic
Epic 4: AI Implementation - Activity 4.3: Engagement Scoring Logic

Transforms fused multimodal signals into interpretable, explainable engagement scores.
Applies rule-based logic and predefined, adjustable thresholds across time segments.
Collectively considers:
  1. Sustained visual presence (gaze focus, tracking duration, presence ratio)
  2. Movement frequency (micro-movement patterns, posture stability, fidgeting)
  3. Inactivity duration (dormancy duration, lack of posture shift, stillness penalty)
  4. Speech activity intensity (calibrated dB SPL, speech state, turn-taking density)

Generates a temporal engagement profile across session intervals to identify:
  - Attention fluctuations (variance, standard deviation, stability index)
  - Peak engagement periods (contiguous high-flow intervals with top drivers)
  - Extended disengagement phases (sustained drop-offs with diagnostic root causes)

Provides downstream feeds into teaching suggestions, student analytics, and session summaries.
"""

import time
import math
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Tuple


class EngagementLevel:
    """Standardized categorical engagement tiers."""
    HIGH = "HIGH"                         # >= 75.0%
    MODERATE = "MODERATE"                 # 55.0% - 74.9%
    LOW = "LOW"                           # 40.0% - 54.9%
    CRITICAL_DISENGAGED = "CRITICAL_DISENGAGED"  # < 40.0%


class ClassroomPreset:
    """Predefined pedagogical threshold presets."""
    LECTURE_STANDARD = "LECTURE_STANDARD"
    INTERACTIVE_DISCUSSION = "INTERACTIVE_DISCUSSION"
    HANDS_ON_LAB = "HANDS_ON_LAB"
    QUIET_EXAM = "QUIET_EXAM"
    CUSTOM = "CUSTOM"


class ScoringRules:
    """Explainable diagnostic rule codes for engagement scoring."""
    RULE_SUSTAINED_VISUAL_FOCUS = "RULE_SUSTAINED_VISUAL_FOCUS"
    RULE_OPTIMAL_POSTURAL_FLOW = "RULE_OPTIMAL_POSTURAL_FLOW"
    RULE_PROLONGED_INACTIVITY_DORMANCY = "RULE_PROLONGED_INACTIVITY_DORMANCY"
    RULE_RESTLESS_POSTURE_JITTER = "RULE_RESTLESS_POSTURE_JITTER"
    RULE_VIBRANT_SPEECH_RESONANCE = "RULE_VIBRANT_SPEECH_RESONANCE"
    RULE_ACOUSTIC_CHAOS_DISRUPTION = "RULE_ACOUSTIC_CHAOS_DISRUPTION"
    RULE_QUESTION_CONCEPT_FREEZE = "RULE_QUESTION_CONCEPT_FREEZE"
    RULE_EXTENDED_DISENGAGEMENT = "RULE_EXTENDED_DISENGAGEMENT"
    RULE_PEAK_ENGAGEMENT_MOMENT = "RULE_PEAK_ENGAGEMENT_MOMENT"


@dataclass
class ScoringThresholdConfig:
    """
    Adjustable scoring thresholds and configuration parameters.
    Allows fine-tuning based on classroom requirements or preset pedagogical modes.
    """
    preset_name: str = ClassroomPreset.LECTURE_STANDARD

    # Proportional factor weights (must sum to 1.0; normalized automatically)
    weight_visual: float = 0.35            # Sustained visual presence weight
    weight_movement: float = 0.20          # Movement frequency weight
    weight_inactivity: float = 0.15        # Inactivity duration penalty weight
    weight_speech: float = 0.30            # Speech activity intensity weight

    # 1. Sustained Visual Presence Thresholds
    min_sustained_presence_ratio: float = 0.50  # Minimum presence ratio threshold
    optimal_gaze_threshold: float = 0.70        # Focus ratio for full visual score

    # 2. Movement Frequency & Pattern Thresholds
    optimal_motion_min: float = 0.02           # Below this is static dormancy
    optimal_motion_max: float = 0.25           # Above this is elevated movement
    restless_motion_threshold: float = 0.45    # Above this is restless fidgeting
    optimal_movement_shifts_per_min: float = 3.0

    # 3. Inactivity Duration Thresholds (seconds)
    inactivity_soft_threshold_sec: float = 30.0     # Normal cognitive stillness
    inactivity_warning_threshold_sec: float = 60.0  # Mild drowsiness / daydreaming
    inactivity_critical_threshold_sec: float = 90.0 # Severe dormant disengagement

    # 4. Speech Activity Intensity Thresholds
    noise_quiet_spl: float = 50.0              # Quiet classroom floor (dB SPL)
    noise_moderate_spl: float = 65.0           # Moderate interactive volume (dB SPL)
    noise_disruptive_spl: float = 75.0         # Acoustic chaos threshold (dB SPL)
    min_discussion_turn_rate: float = 1.0      # Turns per minute during Q&A
    silence_freeze_threshold_sec: float = 20.0 # Stagnant silence in interaction

    # 5. Temporal Profile Analysis Thresholds
    peak_engagement_threshold: float = 80.0    # Threshold for peak periods (0-100%)
    disengagement_threshold: float = 50.0      # Threshold for disengagement (0-100%)
    extended_disengagement_min_segments: int = 3  # Min consecutive low segments
    interval_seconds: float = 10.0             # Segment duration in temporal profile

    def __post_init__(self):
        self.normalize_weights()

    def normalize_weights(self) -> None:
        """Ensures that the four factor weights strictly sum to 1.0."""
        total = self.weight_visual + self.weight_movement + self.weight_inactivity + self.weight_speech
        if total > 0 and not math.isclose(total, 1.0, rel_tol=1e-5):
            self.weight_visual = round(self.weight_visual / total, 4)
            self.weight_movement = round(self.weight_movement / total, 4)
            self.weight_inactivity = round(self.weight_inactivity / total, 4)
            self.weight_speech = round(self.weight_speech / total, 4)

    def apply_preset(self, preset_name: str) -> None:
        """Applies predefined threshold configuration for specific classroom environments."""
        preset = preset_name.upper()
        if preset == ClassroomPreset.LECTURE_STANDARD:
            self.preset_name = ClassroomPreset.LECTURE_STANDARD
            self.weight_visual = 0.40
            self.weight_movement = 0.15
            self.weight_inactivity = 0.20
            self.weight_speech = 0.25
            self.optimal_gaze_threshold = 0.70
            self.noise_disruptive_spl = 70.0
            self.inactivity_critical_threshold_sec = 90.0
        elif preset == ClassroomPreset.INTERACTIVE_DISCUSSION:
            self.preset_name = ClassroomPreset.INTERACTIVE_DISCUSSION
            self.weight_visual = 0.25
            self.weight_movement = 0.20
            self.weight_inactivity = 0.10
            self.weight_speech = 0.45
            self.optimal_gaze_threshold = 0.55
            self.noise_disruptive_spl = 80.0
            self.min_discussion_turn_rate = 1.5
            self.inactivity_critical_threshold_sec = 120.0
        elif preset == ClassroomPreset.HANDS_ON_LAB:
            self.preset_name = ClassroomPreset.HANDS_ON_LAB
            self.weight_visual = 0.20
            self.weight_movement = 0.40
            self.weight_inactivity = 0.15
            self.weight_speech = 0.25
            self.optimal_motion_max = 0.45
            self.restless_motion_threshold = 0.65
            self.optimal_gaze_threshold = 0.45
            self.noise_disruptive_spl = 82.0
        elif preset == ClassroomPreset.QUIET_EXAM:
            self.preset_name = ClassroomPreset.QUIET_EXAM
            self.weight_visual = 0.45
            self.weight_movement = 0.25
            self.weight_inactivity = 0.05
            self.weight_speech = 0.25
            self.noise_disruptive_spl = 58.0
            self.optimal_motion_max = 0.15
            self.restless_motion_threshold = 0.30
        else:
            self.preset_name = ClassroomPreset.CUSTOM

        self.normalize_weights()

    def update_thresholds(self, updates: Dict[str, Any]) -> None:
        """Updates specific thresholds dynamically at runtime."""
        for key, val in updates.items():
            if hasattr(self, key):
                setattr(self, key, type(getattr(self, key))(val))
        self.preset_name = ClassroomPreset.CUSTOM
        self.normalize_weights()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FactorAttribution:
    """Detailed mathematical factor breakdown contributing to an engagement score."""
    visual_presence_contribution: float       # Points from sustained visual presence
    movement_frequency_contribution: float    # Points from posture/movement
    inactivity_contribution: float            # Points from active posture (or penalty)
    speech_intensity_contribution: float       # Points from acoustic participation
    dominant_driver: str                      # Strongest positive contributor
    dominant_penalty: Optional[str] = None    # Strongest negative drag

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EngagementSegmentScore:
    """
    Engagement score computed for a discrete time segment of the session.
    Provides transparent factor breakdown and rule-based diagnostic flags.
    """
    segment_id: int
    start_time: float
    end_time: float
    duration_seconds: float
    composite_score: float                     # 0.0 to 100.0%
    engagement_level: str                      # HIGH, MODERATE, LOW, CRITICAL_DISENGAGED

    # Four Sub-Scores (0.0 to 100.0%)
    visual_presence_score: float               # Sustained visual presence
    movement_frequency_score: float            # Movement frequency & posture stability
    inactivity_score: float                    # Inactivity penalty factor (100 = zero penalty)
    speech_intensity_score: float              # Speech activity intensity

    factor_attribution: FactorAttribution
    rules_triggered: List[str]                 # Diagnostic rule codes triggered
    explainable_summary: str                   # Plain-English pedagogical assessment
    raw_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["factor_attribution"] = self.factor_attribution.to_dict()
        return d


@dataclass
class PeakPeriod:
    """Represents a period of sustained high engagement."""
    peak_id: int
    start_segment: int
    end_segment: int
    start_time: float
    end_time: float
    duration_seconds: float
    peak_score: float
    average_score: float
    dominant_drivers: List[str]
    pedagogical_context: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DisengagementPhase:
    """Represents an extended period of low engagement requiring intervention."""
    phase_id: int
    start_segment: int
    end_segment: int
    start_time: float
    end_time: float
    duration_seconds: float
    average_score: float
    primary_cause: str
    severity: str                              # WARNING or CRITICAL
    suggested_action: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AttentionFluctuationMetrics:
    """Quantifies temporal stability, volatility, and attention fluctuations."""
    fluctuation_index: float                   # Coefficient of variation (std_dev / mean)
    standard_deviation: float                  # Dispersion of segment scores
    variance: float                            # Variance of segment scores
    stability_score: float                     # 100.0 - (fluctuation_index * 100), clamped [0, 100]
    rate_of_change_max: float                  # Maximum score swing between consecutive segments
    attention_drops_count: int                 # Count of sudden negative score drops (>15%)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TemporalEngagementProfile:
    """
    Complete temporal engagement profile generated over regular intervals.
    Captures temporal trajectories, attention fluctuations, peaks, and disengagements.
    """
    session_id: str
    created_at: float
    interval_seconds: float
    total_segments: int
    segments: List[EngagementSegmentScore]
    mean_score: float
    min_score: float
    max_score: float
    fluctuation_metrics: AttentionFluctuationMetrics
    peak_periods: List[PeakPeriod]
    disengagement_phases: List[DisengagementPhase]
    threshold_config: Dict[str, Any]
    downstream_session_summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "interval_seconds": self.interval_seconds,
            "total_segments": self.total_segments,
            "mean_score": round(self.mean_score, 2),
            "min_score": round(self.min_score, 2),
            "max_score": round(self.max_score, 2),
            "segments": [s.to_dict() for s in self.segments],
            "fluctuation_metrics": self.fluctuation_metrics.to_dict(),
            "peak_periods": [p.to_dict() for p in self.peak_periods],
            "disengagement_phases": [d.to_dict() for d in self.disengagement_phases],
            "threshold_config": self.threshold_config,
            "downstream_session_summary": self.downstream_session_summary
        }


class EngagementScoringEngine:
    """
    Core Engagement Scoring Engine (Activity 4.3).
    Transforms fused multimodal signals into interpretable engagement scores.
    Features:
      - Rule-based logic with transparent, adjustable thresholds
      - Four core factors: sustained visual presence, movement frequency, inactivity duration, speech activity intensity
      - Regular interval temporal profile generation
      - Fluctuation, peak, and disengagement phase detection
      - Direct downstream feeding into teaching suggestions, student analytics, and session summaries
    """

    def __init__(self, config: Optional[ScoringThresholdConfig] = None):
        self.config = config or ScoringThresholdConfig()
        self.rolling_segments: List[EngagementSegmentScore] = []
        self.session_id: str = f"SES_{int(time.time())}"
        self.segment_counter: int = 0

    # -------------------------------------------------------------------------
    # 1. Sub-Score Rule-Based Calculation Logic
    # -------------------------------------------------------------------------

    def calculate_visual_presence_score(self, visual_data: Dict[str, Any], duration: float) -> Tuple[float, List[str]]:
        """
        Calculates sustained visual presence score [0.0 - 100.0%].
        Combines board/presentation gaze focus with sustained presence duration.
        """
        rules = []
        raw_att = float(visual_data.get("average_visual_attention", visual_data.get("visual_attention_score", 0.75)))
        gaze_att = raw_att if raw_att <= 1.0 else (raw_att / 100.0)
        gaze_att = max(0.0, min(1.0, gaze_att))

        # Presence duration & ratio
        presence_sec = float(visual_data.get("presence_duration_seconds", duration))
        total_sec = max(1.0, float(visual_data.get("session_elapsed_seconds", duration)))
        raw_ratio = float(visual_data.get("presence_ratio_percent", (presence_sec / total_sec) * 100.0))
        presence_ratio = max(0.0, min(1.0, raw_ratio / 100.0 if raw_ratio > 1.0 else raw_ratio))

        # Weighted combination of gaze and presence ratio
        w_gaze = 0.60
        w_ratio = 0.40
        score = (w_gaze * (gaze_att / max(0.01, self.config.optimal_gaze_threshold)) + w_ratio * presence_ratio) * 100.0

        # Stepped penalty if sustained presence is below minimum threshold
        if presence_ratio < self.config.min_sustained_presence_ratio:
            penalty_factor = (presence_ratio / max(0.01, self.config.min_sustained_presence_ratio)) ** 1.5
            score *= penalty_factor

        score = max(0.0, min(100.0, score))

        if gaze_att >= self.config.optimal_gaze_threshold and presence_ratio >= self.config.min_sustained_presence_ratio:
            rules.append(ScoringRules.RULE_SUSTAINED_VISUAL_FOCUS)

        return round(score, 2), rules

    def calculate_movement_frequency_score(self, visual_data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        Calculates movement frequency and posture stability score [0.0 - 100.0%].
        Normalizes optical motion energy and posture shift frequency into cognitive flow.
        """
        rules = []
        raw_motion = float(visual_data.get("average_motion_energy", visual_data.get("motion_energy", 0.05)))
        pattern = visual_data.get("movement_pattern", "")

        # Optimal range indicates active note-taking and posture responsiveness
        if raw_motion < self.config.optimal_motion_min:
            score = 40.0  # Static stillness penalty
        elif raw_motion <= self.config.optimal_motion_max:
            score = 95.0  # Optimal attentive stability
            rules.append(ScoringRules.RULE_OPTIMAL_POSTURAL_FLOW)
        elif raw_motion <= self.config.restless_motion_threshold:
            score = 70.0  # Elevated purposeful classroom activity
        else:
            score = 35.0  # Restless jitter / fidgeting
            rules.append(ScoringRules.RULE_RESTLESS_POSTURE_JITTER)

        # Micro-adjustment based on explicit movement pattern string if provided
        if pattern == "FOCUSED_STABLE":
            score = max(score, 90.0)
        elif pattern == "RESTLESS_JITTER":
            score = min(score, 40.0)
        elif pattern == "STATIC_DORMANT":
            score = min(score, 45.0)

        return round(max(0.0, min(100.0, score)), 2), rules

    def calculate_inactivity_score(self, visual_data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        Calculates inactivity duration factor [0.0 - 100.0%].
        100% means healthy active responsiveness (0 penalty).
        Penalties escalate as continuous dormant inactivity extends past thresholds.
        """
        rules = []
        inactivity_sec = float(visual_data.get("inactivity_seconds", 0.0))

        if inactivity_sec <= self.config.inactivity_soft_threshold_sec:
            score = 100.0  # Normal natural stillness
        elif inactivity_sec <= self.config.inactivity_warning_threshold_sec:
            # Linear decline from 100% to 65%
            delta = inactivity_sec - self.config.inactivity_soft_threshold_sec
            span = self.config.inactivity_warning_threshold_sec - self.config.inactivity_soft_threshold_sec
            score = 100.0 - (delta / max(1.0, span)) * 35.0
        elif inactivity_sec <= self.config.inactivity_critical_threshold_sec:
            # Steep decline from 65% to 25%
            delta = inactivity_sec - self.config.inactivity_warning_threshold_sec
            span = self.config.inactivity_critical_threshold_sec - self.config.inactivity_warning_threshold_sec
            score = 65.0 - (delta / max(1.0, span)) * 40.0
            rules.append(ScoringRules.RULE_PROLONGED_INACTIVITY_DORMANCY)
        else:
            # Severe penalty for critical prolonged dormancy
            excess = inactivity_sec - self.config.inactivity_critical_threshold_sec
            score = max(0.0, 25.0 - (excess * 0.50))
            rules.append(ScoringRules.RULE_PROLONGED_INACTIVITY_DORMANCY)

        return round(max(0.0, min(100.0, score)), 2), rules

    def calculate_speech_intensity_score(self, audio_data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        Calculates speech activity intensity score [0.0 - 100.0%].
        Evaluates sound pressure level (dB SPL), speech state, rhythm, and turn frequency.
        """
        rules = []
        spl_db = float(audio_data.get("noise_level_spl", 55.0))
        rhythm_state = audio_data.get("rhythm_state", audio_data.get("audio_rhythm", "INSTRUCTOR_MONOLOGUE"))
        speech_state = audio_data.get("speech_state", audio_data.get("signal_classification", "ACTIVE_SPEECH"))
        turn_freq = float(audio_data.get("participation_frequency", 1.0))
        silence_sec = float(audio_data.get("consecutive_silence_sec", 0.0))

        # 1. Base acoustic environment check
        if spl_db >= self.config.noise_disruptive_spl:
            # Loud disruptive room cross-talk
            score = 30.0
            rules.append(ScoringRules.RULE_ACOUSTIC_CHAOS_DISRUPTION)
        elif rhythm_state in ["QA_INTERACTION", "COLLABORATIVE_BUZZ"]:
            # Interactive educational modes reward active speech and turns
            if turn_freq >= self.config.min_discussion_turn_rate and speech_state == "ACTIVE_SPEECH":
                score = 95.0
                rules.append(ScoringRules.RULE_VIBRANT_SPEECH_RESONANCE)
            elif silence_sec >= self.config.silence_freeze_threshold_sec:
                score = 45.0  # Concept hesitation or awkward silence
                rules.append(ScoringRules.RULE_QUESTION_CONCEPT_FREEZE)
            else:
                score = 75.0
        elif rhythm_state == "SILENT_STUDY" or self.config.preset_name == ClassroomPreset.QUIET_EXAM:
            # Silent study rewards quiet environment
            if spl_db <= self.config.noise_quiet_spl:
                score = 98.0
            elif spl_db <= self.config.noise_moderate_spl:
                score = 70.0
            else:
                score = 35.0
        else:
            # Standard lecture: instructor monologue in quiet/moderate room
            if spl_db <= self.config.noise_quiet_spl:
                score = 85.0
            elif spl_db <= self.config.noise_moderate_spl:
                score = 90.0
            else:
                score = 60.0

        return round(max(0.0, min(100.0, score)), 2), rules

    # -------------------------------------------------------------------------
    # 2. Composite Scoring & Explainable Attribution
    # -------------------------------------------------------------------------

    def score_segment(self,
                      visual_data: Dict[str, Any],
                      audio_data: Dict[str, Any],
                      start_time: float,
                      duration_seconds: float) -> EngagementSegmentScore:
        """
        Transforms fused visual and audio indicators for a time segment into an interpretable engagement score.
        Computes the four factor sub-scores, applies adjustable threshold weights, and records attribution.
        """
        self.segment_counter += 1
        end_time = start_time + duration_seconds

        # Compute factor sub-scores [0 - 100%]
        s_vis, r_vis = self.calculate_visual_presence_score(visual_data, duration_seconds)
        s_mot, r_mot = self.calculate_movement_frequency_score(visual_data)
        s_ina, r_ina = self.calculate_inactivity_score(visual_data)
        s_aud, r_aud = self.calculate_speech_intensity_score(audio_data)

        # Weighted linear combination
        w_vis = self.config.weight_visual
        w_mot = self.config.weight_movement
        w_ina = self.config.weight_inactivity
        w_aud = self.config.weight_speech

        contrib_vis = round(w_vis * s_vis, 2)
        contrib_mot = round(w_mot * s_mot, 2)
        contrib_ina = round(w_ina * s_ina, 2)
        contrib_aud = round(w_aud * s_aud, 2)

        composite = round(contrib_vis + contrib_mot + contrib_ina + contrib_aud, 2)
        composite = max(0.0, min(100.0, composite))

        # Categorize Engagement Level
        if composite >= 75.0:
            level = EngagementLevel.HIGH
        elif composite >= 55.0:
            level = EngagementLevel.MODERATE
        elif composite >= 40.0:
            level = EngagementLevel.LOW
        else:
            level = EngagementLevel.CRITICAL_DISENGAGED

        # Determine dominant driver and dominant penalty
        contrib_map = {
            "Visual Presence": contrib_vis,
            "Movement Dynamics": contrib_mot,
            "Postural Alertness": contrib_ina,
            "Speech Intensity": contrib_aud
        }
        dominant_driver = max(contrib_map, key=contrib_map.get)

        penalties_map = {
            "Visual Wander": (100.0 - s_vis) * w_vis,
            "Postural Restlessness/Stagnation": (100.0 - s_mot) * w_mot,
            "Prolonged Inactivity": (100.0 - s_ina) * w_ina,
            "Acoustic Disruption/Silence": (100.0 - s_aud) * w_aud
        }
        max_penalty = max(penalties_map.values())
        dominant_penalty = max(penalties_map, key=penalties_map.get) if max_penalty > 8.0 else None

        attribution = FactorAttribution(
            visual_presence_contribution=contrib_vis,
            movement_frequency_contribution=contrib_mot,
            inactivity_contribution=contrib_ina,
            speech_intensity_contribution=contrib_aud,
            dominant_driver=dominant_driver,
            dominant_penalty=dominant_penalty
        )

        # Aggregate triggered rules
        all_rules = list(set(r_vis + r_mot + r_ina + r_aud))
        if composite >= self.config.peak_engagement_threshold:
            all_rules.append(ScoringRules.RULE_PEAK_ENGAGEMENT_MOMENT)
        elif composite < self.config.disengagement_threshold:
            all_rules.append(ScoringRules.RULE_EXTENDED_DISENGAGEMENT)

        # Generate concise explainable summary
        summary = (
            f"Segment #{self.segment_counter}: {level} engagement ({composite:.1f}%). "
            f"Primary driver: {dominant_driver} ({contrib_map[dominant_driver]:.1f} pts). "
        )
        if dominant_penalty:
            summary += f"Drag: {dominant_penalty} (-{max_penalty:.1f} pts)."

        seg_score = EngagementSegmentScore(
            segment_id=self.segment_counter,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            composite_score=composite,
            engagement_level=level,
            visual_presence_score=s_vis,
            movement_frequency_score=s_mot,
            inactivity_score=s_ina,
            speech_intensity_score=s_aud,
            factor_attribution=attribution,
            rules_triggered=all_rules,
            explainable_summary=summary,
            raw_metrics={
                "visual": visual_data,
                "audio": audio_data
            }
        )

        self.rolling_segments.append(seg_score)
        return seg_score

    # -------------------------------------------------------------------------
    # 3. Temporal Engagement Profile Generation & Pattern Detection
    # -------------------------------------------------------------------------

    def generate_temporal_profile(self,
                                   time_series_packets: List[Dict[str, Any]],
                                   interval_seconds: Optional[float] = None,
                                   session_id: Optional[str] = None) -> TemporalEngagementProfile:
        """
        Computes engagement scores at regular intervals to generate a temporal engagement profile
        rather than a single aggregated value.
        Analyzes attention fluctuations, peak periods, and extended disengagement phases.
        """
        interval = interval_seconds or self.config.interval_seconds
        s_id = session_id or self.session_id
        now = time.time()

        if not time_series_packets:
            # Fallback for empty input: synthesize an empty baseline profile
            empty_fluc = AttentionFluctuationMetrics(0.0, 0.0, 0.0, 100.0, 0.0, 0)
            return TemporalEngagementProfile(
                session_id=s_id,
                created_at=now,
                interval_seconds=interval,
                total_segments=0,
                segments=[],
                mean_score=0.0,
                min_score=0.0,
                max_score=0.0,
                fluctuation_metrics=empty_fluc,
                peak_periods=[],
                disengagement_phases=[],
                threshold_config=self.config.to_dict()
            )

        # Process each packet or group packets into regular interval segments
        segments: List[EngagementSegmentScore] = []
        base_t = time_series_packets[0].get("timestamp", now - (len(time_series_packets) * interval))

        for idx, packet in enumerate(time_series_packets):
            seg_start = base_t + (idx * interval)
            vis = packet.get("visual_data", packet)
            aud = packet.get("audio_data", packet)
            score = self.score_segment(vis, aud, seg_start, interval)
            segments.append(score)

        # 1. Overall Aggregate Metrics
        scores = [s.composite_score for s in segments]
        mean_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)

        # 2. Attention Fluctuations Analysis
        variance = sum((x - mean_score) ** 2 for x in scores) / len(scores)
        std_dev = math.sqrt(variance)
        fluc_index = round(std_dev / max(1.0, mean_score), 3)
        stability_score = round(max(0.0, min(100.0, 100.0 - (fluc_index * 100.0))), 2)

        # Consecutive rate of change ($dEI/dt$) & drops
        max_roc = 0.0
        drops_count = 0
        for i in range(1, len(scores)):
            delta = scores[i] - scores[i - 1]
            if abs(delta) > max_roc:
                max_roc = abs(delta)
            if delta <= -15.0:
                drops_count += 1

        fluctuation_metrics = AttentionFluctuationMetrics(
            fluctuation_index=fluc_index,
            standard_deviation=round(std_dev, 2),
            variance=round(variance, 2),
            stability_score=stability_score,
            rate_of_change_max=round(max_roc, 2),
            attention_drops_count=drops_count
        )

        # 3. Peak Engagement Periods Detection
        peak_periods = self._detect_peak_periods(segments)

        # 4. Extended Disengagement Phases Detection
        disengagement_phases = self._detect_disengagement_phases(segments)

        # 5. Build Downstream Summary
        downstream_summary = {
            "session_id": s_id,
            "overall_status": "EXCELLENT" if mean_score >= 75 else ("GOOD" if mean_score >= 60 else "NEEDS_INTERVENTION"),
            "attention_stability": "STABLE" if stability_score >= 80 else ("MODERATE_FLUCTUATION" if stability_score >= 60 else "HIGHLY_VOLATILE"),
            "peak_count": len(peak_periods),
            "disengagement_count": len(disengagement_phases),
            "teaching_intervention_required": len(disengagement_phases) > 0 or drops_count >= 2
        }

        profile = TemporalEngagementProfile(
            session_id=s_id,
            created_at=now,
            interval_seconds=interval,
            total_segments=len(segments),
            segments=segments,
            mean_score=round(mean_score, 2),
            min_score=round(min_score, 2),
            max_score=round(max_score, 2),
            fluctuation_metrics=fluctuation_metrics,
            peak_periods=peak_periods,
            disengagement_phases=disengagement_phases,
            threshold_config=self.config.to_dict(),
            downstream_session_summary=downstream_summary
        )

        return profile

    def _detect_peak_periods(self, segments: List[EngagementSegmentScore]) -> List[PeakPeriod]:
        """Identifies contiguous intervals where engagement scores reach or exceed peak threshold."""
        peaks: List[PeakPeriod] = []
        in_peak = False
        start_idx = 0
        peak_threshold = self.config.peak_engagement_threshold

        for idx, seg in enumerate(segments):
            if seg.composite_score >= peak_threshold:
                if not in_peak:
                    in_peak = True
                    start_idx = idx
            else:
                if in_peak:
                    in_peak = False
                    p_segs = segments[start_idx:idx]
                    p_scores = [s.composite_score for s in p_segs]
                    drivers = list(set([s.factor_attribution.dominant_driver for s in p_segs]))
                    peaks.append(PeakPeriod(
                        peak_id=len(peaks) + 1,
                        start_segment=p_segs[0].segment_id,
                        end_segment=p_segs[-1].segment_id,
                        start_time=p_segs[0].start_time,
                        end_time=p_segs[-1].end_time,
                        duration_seconds=round(p_segs[-1].end_time - p_segs[0].start_time, 1),
                        peak_score=round(max(p_scores), 2),
                        average_score=round(sum(p_scores) / len(p_scores), 2),
                        dominant_drivers=drivers,
                        pedagogical_context=f"High instructional resonance driven primarily by {', '.join(drivers)}."
                    ))

        # Close boundary peak if active at end of session
        if in_peak:
            p_segs = segments[start_idx:]
            p_scores = [s.composite_score for s in p_segs]
            drivers = list(set([s.factor_attribution.dominant_driver for s in p_segs]))
            peaks.append(PeakPeriod(
                peak_id=len(peaks) + 1,
                start_segment=p_segs[0].segment_id,
                end_segment=p_segs[-1].segment_id,
                start_time=p_segs[0].start_time,
                end_time=p_segs[-1].end_time,
                duration_seconds=round(p_segs[-1].end_time - p_segs[0].start_time, 1),
                peak_score=round(max(p_scores), 2),
                average_score=round(sum(p_scores) / len(p_scores), 2),
                dominant_drivers=drivers,
                pedagogical_context=f"High instructional resonance driven primarily by {', '.join(drivers)}."
            ))

        return peaks

    def _detect_disengagement_phases(self, segments: List[EngagementSegmentScore]) -> List[DisengagementPhase]:
        """
        Identifies extended disengagement phases where engagement remains below disengagement
        threshold for consecutive intervals.
        """
        phases: List[DisengagementPhase] = []
        in_disengagement = False
        start_idx = 0
        threshold = self.config.disengagement_threshold
        min_segments = self.config.extended_disengagement_min_segments

        for idx, seg in enumerate(segments):
            if seg.composite_score < threshold:
                if not in_disengagement:
                    in_disengagement = True
                    start_idx = idx
            else:
                if in_disengagement:
                    in_disengagement = False
                    d_segs = segments[start_idx:idx]
                    if len(d_segs) >= min_segments:
                        d_scores = [s.composite_score for s in d_segs]
                        avg_s = sum(d_scores) / len(d_scores)
                        penalties = [s.factor_attribution.dominant_penalty for s in d_segs if s.factor_attribution.dominant_penalty]
                        primary_cause = penalties[0] if penalties else "Low cross-modal engagement"
                        action = self._suggest_intervention_for_cause(primary_cause)
                        phases.append(DisengagementPhase(
                            phase_id=len(phases) + 1,
                            start_segment=d_segs[0].segment_id,
                            end_segment=d_segs[-1].segment_id,
                            start_time=d_segs[0].start_time,
                            end_time=d_segs[-1].end_time,
                            duration_seconds=round(d_segs[-1].end_time - d_segs[0].start_time, 1),
                            average_score=round(avg_s, 2),
                            primary_cause=primary_cause,
                            severity="CRITICAL" if avg_s < 35.0 else "WARNING",
                            suggested_action=action
                        ))

        # Close boundary disengagement if active at end of session
        if in_disengagement:
            d_segs = segments[start_idx:]
            if len(d_segs) >= min_segments:
                d_scores = [s.composite_score for s in d_segs]
                avg_s = sum(d_scores) / len(d_scores)
                penalties = [s.factor_attribution.dominant_penalty for s in d_segs if s.factor_attribution.dominant_penalty]
                primary_cause = penalties[0] if penalties else "Low cross-modal engagement"
                action = self._suggest_intervention_for_cause(primary_cause)
                phases.append(DisengagementPhase(
                    phase_id=len(phases) + 1,
                    start_segment=d_segs[0].segment_id,
                    end_segment=d_segs[-1].segment_id,
                    start_time=d_segs[0].start_time,
                    end_time=d_segs[-1].end_time,
                    duration_seconds=round(d_segs[-1].end_time - d_segs[0].start_time, 1),
                    average_score=round(avg_s, 2),
                    primary_cause=primary_cause,
                    severity="CRITICAL" if avg_s < 35.0 else "WARNING",
                    suggested_action=action
                ))

        return phases

    def _suggest_intervention_for_cause(self, cause: str) -> str:
        """Determines appropriate pedagogical suggestion based on disengagement cause."""
        if "Inactivity" in cause or "Dormancy" in cause:
            return "Introduce a 30-second stand-up stretch or initiate a quick live poll to reset physical alertness."
        elif "Acoustic Disruption" in cause:
            return "Pause presentation to address room cross-talk and regain acoustic focus."
        elif "Visual Wander" in cause:
            return "Direct learner attention to a concrete diagram, slide highlight, or demonstration on the board."
        elif "Restlessness" in cause:
            return "Pacing mismatch detected. Transition from passive lecture to an active peer problem-solving exercise."
        else:
            return "Engagement dip detected. Check for conceptual comprehension or run a brief Q&A checkpoint."

    # -------------------------------------------------------------------------
    # 4. Downstream Consumers: Teaching Suggestions, Student Analytics & Summary
    # -------------------------------------------------------------------------

    def generate_downstream_teaching_suggestions(self, profile: Optional[TemporalEngagementProfile] = None) -> List[Dict[str, Any]]:
        """
        Consumes the temporal engagement profile downstream to generate targeted teaching suggestions.
        """
        suggestions = []
        target_profile = profile
        if not target_profile and self.rolling_segments:
            # Build profile from rolling segments
            scores = [s.composite_score for s in self.rolling_segments]
            mean_s = sum(scores) / len(scores)
            fluc = AttentionFluctuationMetrics(0.1, 5.0, 25.0, 90.0, 5.0, 0)
            target_profile = TemporalEngagementProfile(
                session_id=self.session_id,
                created_at=time.time(),
                interval_seconds=self.config.interval_seconds,
                total_segments=len(self.rolling_segments),
                segments=self.rolling_segments,
                mean_score=mean_s,
                min_score=min(scores),
                max_score=max(scores),
                fluctuation_metrics=fluc,
                peak_periods=[],
                disengagement_phases=self._detect_disengagement_phases(self.rolling_segments),
                threshold_config=self.config.to_dict()
            )

        if not target_profile or not target_profile.segments:
            return [{
                "title": "Baseline Classroom Engagement",
                "alert_level": "INFO",
                "rationale": "Sufficient time segments are being compiled to evaluate temporal profile.",
                "action": "Maintain instructional progression."
            }]

        # 1. Extended Disengagement Phase Alerts
        for phase in target_profile.disengagement_phases:
            suggestions.append({
                "title": f"Extended Disengagement Phase #{phase.phase_id} ({phase.severity})",
                "alert_level": "ACTIONABLE" if phase.severity == "CRITICAL" else "ADVISORY",
                "rationale": f"Classroom engagement averaged {phase.average_score:.1f}% for {phase.duration_seconds:.0f}s due to {phase.primary_cause}.",
                "action": phase.suggested_action,
                "context": {
                    "phase_id": phase.phase_id,
                    "duration_sec": phase.duration_seconds,
                    "avg_score": phase.average_score
                }
            })

        # 2. Attention Fluctuation Alerts
        fluc = target_profile.fluctuation_metrics
        if fluc.stability_score < 65.0:
            suggestions.append({
                "title": "High Attention Fluctuation Detected",
                "alert_level": "ADVISORY",
                "rationale": f"Stability score is {fluc.stability_score:.1f}% with maximum rapid score swing of {fluc.rate_of_change_max:.1f}%.",
                "action": "Stabilize presentation pacing. Segment complex concepts into bite-sized checkpoints.",
                "context": {"stability_score": fluc.stability_score, "drops": fluc.attention_drops_count}
            })

        # 3. Peak Engagement Reinforcement
        if target_profile.peak_periods:
            latest_peak = target_profile.peak_periods[-1]
            suggestions.append({
                "title": f"Instructional Peak Flow (Score: {latest_peak.average_score:.1f}%)",
                "alert_level": "POSITIVE",
                "rationale": f"High engagement sustained across {latest_peak.duration_seconds:.0f}s driven by {', '.join(latest_peak.dominant_drivers)}.",
                "action": "Capitalize on high momentum to introduce deeper, high-order cognitive challenges.",
                "context": {"peak_score": latest_peak.peak_score, "drivers": latest_peak.dominant_drivers}
            })

        return suggestions

    def generate_student_analytics(self, per_student_packets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consumes engagement scoring logic downstream to generate per-student analytics profiles.
        """
        student_profiles = []
        for s in per_student_packets:
            s_id = s.get("student_id", "UNKNOWN")
            display_name = s.get("display_name", s_id)
            vis = s.get("visual_data", s)
            aud = s.get("audio_data", s)

            s_vis, _ = self.calculate_visual_presence_score(vis, 60.0)
            s_mot, _ = self.calculate_movement_frequency_score(vis)
            s_ina, _ = self.calculate_inactivity_score(vis)
            s_aud, _ = self.calculate_speech_intensity_score(aud)

            comp = round(
                self.config.weight_visual * s_vis +
                self.config.weight_movement * s_mot +
                self.config.weight_inactivity * s_ina +
                self.config.weight_speech * s_aud,
                2
            )

            if comp >= 75.0:
                tier = "HIGHLY_ENGAGED"
            elif comp >= 55.0:
                tier = "CONSISTENT_ATTENTIVE"
            elif comp >= 40.0:
                tier = "FLUCTUATING_ENGAGEMENT"
            else:
                tier = "AT_RISK_DISENGAGED"

            student_profiles.append({
                "student_id": s_id,
                "display_name": display_name,
                "engagement_score": comp,
                "participation_quadrant": tier,
                "visual_presence_score": s_vis,
                "movement_frequency_score": s_mot,
                "inactivity_score": s_ina,
                "speech_intensity_score": s_aud,
                "presence_ratio_percent": float(vis.get("presence_ratio_percent", 90.0))
            })

        return {
            "total_students": len(student_profiles),
            "session_id": self.session_id,
            "profiles": student_profiles
        }

    def generate_session_summary(self, profile: Optional[TemporalEngagementProfile] = None) -> Dict[str, Any]:
        """
        Consumes engagement scoring logic downstream to produce a comprehensive session summary.
        """
        target_profile = profile
        if not target_profile and self.rolling_segments:
            target_profile = self.generate_temporal_profile(
                [s.raw_metrics for s in self.rolling_segments],
                self.config.interval_seconds,
                self.session_id
            )

        if not target_profile or not target_profile.segments:
            return {
                "session_id": self.session_id,
                "status": "NO_DATA",
                "summary": "No completed segments to summarize."
            }

        scores = [s.composite_score for s in target_profile.segments]
        high_count = sum(1 for s in target_profile.segments if s.engagement_level == EngagementLevel.HIGH)
        mod_count = sum(1 for s in target_profile.segments if s.engagement_level == EngagementLevel.MODERATE)
        low_count = sum(1 for s in target_profile.segments if s.engagement_level in [EngagementLevel.LOW, EngagementLevel.CRITICAL_DISENGAGED])

        total = len(target_profile.segments)
        return {
            "session_id": target_profile.session_id,
            "total_duration_minutes": round((total * target_profile.interval_seconds) / 60.0, 2),
            "total_segments": total,
            "mean_engagement_index": target_profile.mean_score,
            "min_engagement_index": target_profile.min_score,
            "max_engagement_index": target_profile.max_score,
            "stability_score": target_profile.fluctuation_metrics.stability_score,
            "fluctuation_index": target_profile.fluctuation_metrics.fluctuation_index,
            "peak_engagement_periods_count": len(target_profile.peak_periods),
            "extended_disengagement_phases_count": len(target_profile.disengagement_phases),
            "distribution": {
                "high_engagement_percent": round((high_count / total) * 100.0, 1),
                "moderate_engagement_percent": round((mod_count / total) * 100.0, 1),
                "low_engagement_percent": round((low_count / total) * 100.0, 1)
            },
            "active_threshold_preset": target_profile.threshold_config.get("preset_name", "CUSTOM"),
            "pedagogical_takeaway": (
                f"Classroom maintained {target_profile.mean_score:.1f}% average engagement with "
                f"{len(target_profile.peak_periods)} instructional peaks and "
                f"{len(target_profile.disengagement_phases)} extended disengagement phases."
            )
        }
