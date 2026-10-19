"""
Multimodal Attendance & Engagement Agent - Visual Attention & Movement Dynamics
Epic 4: Tasks 7 & 8 (TASK-07, TASK-08) - Head Pose & Movement Dynamics
"""

import time
from typing import List, Dict, Any, Tuple
from backend.vision.face_tracker import ParticipantTrack

class VisualAttentionAnalyzer:
    """Estimates participant gaze/head orientation and movement dynamics."""

    def __init__(self, yaw_threshold: float = 25.0, pitch_threshold: float = 20.0,
                 inactivity_seconds: float = 120.0, restless_threshold: float = 0.45):
        self.yaw_threshold = yaw_threshold
        self.pitch_threshold = pitch_threshold
        self.inactivity_seconds = inactivity_seconds
        self.restless_threshold = restless_threshold
        self.track_motion_history: Dict[int, List[float]] = {}

    def analyze_tracks(self, tracks: List[ParticipantTrack], frame_dt: float = 0.066) -> Dict[str, Any]:
        """
        Analyzes head pose, gaze focus, and physical motion for each tracked participant.
        Returns:
            Dictionary containing aggregate metrics and per-student visual telemetry.
        """
        per_student_metrics: List[Dict[str, Any]] = []
        total_attentive = 0
        total_motion = 0.0

        now = time.time()

        for track in tracks:
            # 1. Head Pose & Gaze Heuristic (TASK-07)
            # Frontal attention: yaw within +/- threshold and pitch within +/- threshold
            yaw_abs = abs(track.yaw)
            pitch_abs = abs(track.pitch)

            # Continuous attention score [0.0 to 1.0]
            yaw_penalty = max(0.0, (yaw_abs - 12.0) / (self.yaw_threshold - 12.0)) if yaw_abs > 12.0 else 0.0
            pitch_penalty = max(0.0, (pitch_abs - 10.0) / (self.pitch_threshold - 10.0)) if pitch_abs > 10.0 else 0.0
            
            raw_att = 1.0 - min(1.0, (yaw_penalty * 0.65 + pitch_penalty * 0.45))
            # Smooth tracking attention
            track.attention_score = round(track.attention_score * 0.70 + raw_att * 0.30, 3)

            # Classify Focus Direction
            if yaw_abs <= 12.0 and pitch_abs <= 12.0:
                focus_direction = "FORWARD_BOARD"
            elif yaw_abs > 20.0:
                focus_direction = "LATERAL_DISTRACTED"
            elif pitch_abs > 18.0 and track.pitch > 0:
                focus_direction = "DOWNWARD_NOTES"
            else:
                focus_direction = "MODERATE_FOCUS"

            track.focus_direction = focus_direction
            track.gaze_direction = focus_direction

            # 2. Movement Dynamics & Inactivity (TASK-08)
            motion = track.motion_energy
            total_motion += motion

            # Track dormancy
            if motion < 0.03:
                if track.dormant_since is None:
                    track.dormant_since = now
                elif (now - track.dormant_since) > self.inactivity_seconds:
                    track.is_dormant = True
            else:
                track.dormant_since = None
                track.is_dormant = False

            # Motion State
            if motion > self.restless_threshold:
                motion_state = "RESTLESS"
            elif track.is_dormant:
                motion_state = "DORMANT_STATIC"
            else:
                motion_state = "BALANCED"

            is_attentive = track.attention_score >= 0.65
            if is_attentive and not track.is_walkby:
                total_attentive += 1

            per_student_metrics.append({
                "student_id": track.student_id,
                "track_id": track.track_id,
                "attention_score": track.attention_score,
                "focus_direction": focus_direction,
                "yaw": track.yaw,
                "pitch": track.pitch,
                "motion_energy": motion,
                "motion_state": motion_state,
                "is_dormant": track.is_dormant,
                "is_walkby": track.is_walkby
            })

        count = max(1, len([t for t in tracks if not t.is_walkby]))
        avg_attention = round(total_attentive / count, 3) if count > 0 else 0.0
        avg_motion = round(total_motion / count, 3) if count > 0 else 0.0

        return {
            "average_visual_attention": avg_attention,
            "average_motion_energy": avg_motion,
            "active_participants_count": count,
            "student_metrics": per_student_metrics
        }
