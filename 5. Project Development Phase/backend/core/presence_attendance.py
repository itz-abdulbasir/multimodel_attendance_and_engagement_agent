"""
NeuroClass Core Vision Module - Presence-Based Attendance Logic
EPIC 2: Vision Module Development
Activity 2.2: Presence-Based Attendance Logic

Translates continuous face tracking data and timestamps into verified attendance records.
Accumulates intermittent presence durations across video frames to prevent false positives
from single-frame or fleeting detections, and confirms attendance only when cumulative presence
exceeds a predefined temporal threshold.
"""

import time
import hashlib
import csv
import io
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional


class PresenceRecord:
    """
    Maintains cumulative presence tracking state for an individual participant.
    Accumulates intermittent appearances across the session duration.
    """

    def __init__(
        self,
        student_id: str,
        display_name: Optional[str] = None,
        seat: Optional[str] = None
    ):
        self.student_id = student_id
        self.display_name = display_name or student_id
        self.seat = seat or "General Seating"

        self.first_seen_time: Optional[float] = None
        self.last_seen_time: Optional[float] = None
        self.cumulative_presence_seconds: float = 0.0
        self.total_detections_count: int = 0
        self.is_currently_visible: bool = False
        self.last_update_timestamp: float = time.time()
        
        # Intermittent presence intervals: [(interval_start, interval_end), ...]
        self.appearance_intervals: List[Tuple[float, float]] = []
        self._current_interval_start: Optional[float] = None

        # Attendance status classification
        self.status: str = "ABSENT"  # 'ABSENT', 'INTERMITTENT', 'PRESENT', 'LATE', 'WALKBY_FILTERED'
        self.presence_ratio: float = 0.0
        self.is_walkby: bool = False

    def record_frame_presence(
        self,
        is_visible: bool,
        current_time: float,
        dt: float,
        session_elapsed: float,
        min_sustained_seconds: float,
        walkby_threshold_seconds: float,
        late_cutoff_seconds: float,
        sustained_ratio_req: float,
        is_flagged_walkby: bool = False
    ) -> None:
        """
        Updates temporal presence duration.
        Accumulates intermittent appearances across frames.
        """
        self.is_currently_visible = is_visible
        self.last_update_timestamp = current_time
        if is_flagged_walkby:
            self.is_walkby = True

        if is_visible:
            self.total_detections_count += 1
            if self.first_seen_time is None:
                self.first_seen_time = current_time

            self.last_seen_time = current_time
            # Accumulate presence duration
            self.cumulative_presence_seconds += dt

            # Manage appearance interval tracking
            if self._current_interval_start is None:
                self._current_interval_start = current_time
        else:
            # Participant temporarily stepped away, turned head, or suffered brief occlusion
            if self._current_interval_start is not None:
                self.appearance_intervals.append((self._current_interval_start, self.last_seen_time or current_time))
                self._current_interval_start = None

        # Calculate presence ratio over observed session elapsed time
        effective_elapsed = max(1.0, session_elapsed)
        self.presence_ratio = min(1.0, round(self.cumulative_presence_seconds / effective_elapsed, 3))

        # Presence-Based Classification Logic:
        # Rule 1: Fleeting walk-by visitor detection
        if self.is_walkby or (
            self.cumulative_presence_seconds < walkby_threshold_seconds
            and not is_visible
            and self.first_seen_time is not None
            and (current_time - self.last_seen_time) > 5.0
        ):
            self.status = "WALKBY_FILTERED"

        # Rule 2: Minimum sustained presence threshold met
        elif self.cumulative_presence_seconds >= min_sustained_seconds:
            # Check if arrived late compared to session start
            session_start_ref = current_time - session_elapsed
            first_arrival_offset = (self.first_seen_time - session_start_ref) if self.first_seen_time else 0.0
            if first_arrival_offset > late_cutoff_seconds:
                self.status = "LATE"
            else:
                self.status = "PRESENT"

        # Rule 3: Participant has intermittent appearances but has not met threshold yet
        elif self.cumulative_presence_seconds > 0.0:
            self.status = "INTERMITTENT"

        # Rule 4: Zero presence
        else:
            self.status = "ABSENT"

    def finalize(self, current_time: float) -> None:
        """Closes any open interval at the end of the session."""
        if self._current_interval_start is not None:
            self.appearance_intervals.append((self._current_interval_start, current_time))
            self._current_interval_start = None

    def generate_audit_hash(self, salt: str = "NEUROCLASS-SALT-2026") -> str:
        """Generates a deterministic salted SHA-256 hash for tamper-proof audit trails."""
        payload = f"{self.student_id}|{round(self.cumulative_presence_seconds, 2)}|{self.status}|{self.first_seen_time}|{salt}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        """Serializes presence record into structured log schema."""
        first_iso = datetime.fromtimestamp(self.first_seen_time).isoformat() if self.first_seen_time else None
        last_iso = datetime.fromtimestamp(self.last_seen_time).isoformat() if self.last_seen_time else None
        return {
            "student_id": self.student_id,
            "display_name": self.display_name,
            "seat": self.seat,
            "status": self.status,
            "is_currently_visible": self.is_currently_visible,
            "cumulative_presence_seconds": round(self.cumulative_presence_seconds, 2),
            "presence_ratio": round(self.presence_ratio, 3),
            "presence_percentage": round(self.presence_ratio * 100, 1),
            "first_seen": first_iso,
            "last_seen": last_iso,
            "total_detections_count": self.total_detections_count,
            "intervals_count": len(self.appearance_intervals) + (1 if self._current_interval_start else 0),
            "audit_hash": self.generate_audit_hash()
        }


class PresenceAttendanceEngine:
    """
    Translates face tracking streams into confirmed, presence-based attendance records.
    
    Features:
    - Multi-frame presence duration accumulation (rejects single-frame false positives).
    - Cumulative temporal thresholding (marks 'PRESENT' once threshold is reached).
    - Fleeting walk-by visitor rejection ('WALKBY_FILTERED').
    - Late arrival detection ('LATE').
    - Structured attendance logging and CSV audit generation.
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        min_sustained_seconds: float = 20.0,
        sustained_ratio: float = 0.60,
        walkby_threshold_seconds: float = 10.0,
        late_cutoff_seconds: float = 300.0,
        salt: str = "NEUROCLASS-PRESENCE-2026"
    ):
        self.session_id = session_id or f"SES-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.min_sustained_seconds = min_sustained_seconds
        self.sustained_ratio = sustained_ratio
        self.walkby_threshold_seconds = walkby_threshold_seconds
        self.late_cutoff_seconds = late_cutoff_seconds
        self.salt = salt

        self.start_wall_time = time.time()
        self.last_process_time = self.start_wall_time
        self._session_initialized = False
        self.records: Dict[str, PresenceRecord] = {}

    def register_enrolled_students(self, students: List[Dict[str, Any]]) -> None:
        """Initializes enrolled students in the attendance roster."""
        for s in students:
            sid = s.get("id") or s.get("student_id")
            if sid:
                name = s.get("name") or s.get("display_name", sid)
                seat = s.get("seat") or s.get("seat_label", "General")
                self.records[sid] = PresenceRecord(
                    student_id=sid,
                    display_name=name,
                    seat=seat
                )

    def process_tracking_frame(
        self,
        active_participant_ids: List[str],
        timestamp: Optional[float] = None,
        dt: Optional[float] = None,
        walkby_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Processes tracking frame data and updates cumulative presence.
        
        Args:
            active_participant_ids: List of student IDs or track IDs detected in this frame.
            timestamp: Optional frame epoch timestamp.
            dt: Optional elapsed step time.
            walkby_ids: Optional list of IDs flagged as walk-by visitors.
            
        Returns:
            List of structured attendance records for the frame.
        """
        now = timestamp if timestamp is not None else time.time()
        if not self._session_initialized:
            self.start_wall_time = now
            self.last_process_time = now
            self._session_initialized = True

        step_dt = dt if dt is not None else max(0.01, min(1.0, now - self.last_process_time))
        self.last_process_time = now
        session_elapsed = max(step_dt, (now - self.start_wall_time) + step_dt)

        walkby_set = set(walkby_ids or [])
        active_set = set(active_participant_ids)

        # 1. Update all currently registered students
        for sid, record in self.records.items():
            is_vis = sid in active_set
            record.record_frame_presence(
                is_visible=is_vis,
                current_time=now,
                dt=step_dt,
                session_elapsed=session_elapsed,
                min_sustained_seconds=self.min_sustained_seconds,
                walkby_threshold_seconds=self.walkby_threshold_seconds,
                late_cutoff_seconds=self.late_cutoff_seconds,
                sustained_ratio_req=self.sustained_ratio,
                is_flagged_walkby=sid in walkby_set
            )

        # 2. Register any newly detected participants / guests
        for sid in active_set:
            if sid not in self.records:
                rec = PresenceRecord(
                    student_id=sid,
                    display_name=f"Participant {sid}",
                    seat="Guest"
                )
                rec.record_frame_presence(
                    is_visible=True,
                    current_time=now,
                    dt=step_dt,
                    session_elapsed=session_elapsed,
                    min_sustained_seconds=self.min_sustained_seconds,
                    walkby_threshold_seconds=self.walkby_threshold_seconds,
                    late_cutoff_seconds=self.late_cutoff_seconds,
                    sustained_ratio_req=self.sustained_ratio,
                    is_flagged_walkby=sid in walkby_set
                )
                self.records[sid] = rec

        return [rec.to_dict() for rec in self.records.values()]

    def update_from_tracker_output(
        self,
        tracks: List[Dict[str, Any]],
        timestamp: Optional[float] = None,
        dt: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Convenience method directly consuming structured tracks from FaceTracker."""
        active_ids = [t.get("student_id") or f"TRK-{t['track_id']:03d}" for t in tracks if t.get("status") != "DISAPPEARED"]
        walkby_ids = [t.get("student_id") for t in tracks if t.get("is_walkby", False)]
        return self.process_tracking_frame(active_ids, timestamp=timestamp, dt=dt, walkby_ids=walkby_ids)

    def get_structured_attendance_logs(self, exclude_walkbys: bool = True) -> List[Dict[str, Any]]:
        """Returns structured logs suitable for classroom analytics and reporting."""
        logs = []
        for rec in self.records.values():
            if exclude_walkbys and rec.status == "WALKBY_FILTERED":
                continue
            logs.append(rec.to_dict())
        # Sort so PRESENT students appear first, followed by LATE, INTERMITTENT, ABSENT
        status_priority = {"PRESENT": 0, "LATE": 1, "INTERMITTENT": 2, "ABSENT": 3, "WALKBY_FILTERED": 4}
        return sorted(logs, key=lambda x: (status_priority.get(x["status"], 5), x["student_id"]))

    def get_summary_stats(self) -> Dict[str, Any]:
        """Calculates aggregated attendance indicators."""
        all_recs = list(self.records.values())
        non_walkbys = [r for r in all_recs if r.status != "WALKBY_FILTERED"]
        present_count = len([r for r in non_walkbys if r.status in ["PRESENT", "LATE"]])
        late_count = len([r for r in non_walkbys if r.status == "LATE"])
        intermittent_count = len([r for r in non_walkbys if r.status == "INTERMITTENT"])
        absent_count = len([r for r in non_walkbys if r.status == "ABSENT"])
        walkby_count = len([r for r in all_recs if r.status == "WALKBY_FILTERED"])

        total_enrolled = max(1, len(non_walkbys))
        attendance_rate = round((present_count / total_enrolled) * 100, 1)

        return {
            "session_id": self.session_id,
            "total_enrolled": len(non_walkbys),
            "present_count": present_count,
            "late_count": late_count,
            "intermittent_count": intermittent_count,
            "absent_count": absent_count,
            "walkby_filtered_count": walkby_count,
            "attendance_rate_percent": attendance_rate,
            "min_sustained_threshold_seconds": self.min_sustained_seconds,
            "walkby_threshold_seconds": self.walkby_threshold_seconds
        }

    def export_attendance_csv(self) -> str:
        """Exports formatted CSV attendance audit sheet for reporting."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Session ID", "Student ID", "Participant Name", "Seat / Location",
            "Attendance Status", "Cumulative Presence (s)", "Cumulative Presence (min)",
            "Presence Ratio %", "First Detected", "Last Detected", "Audit Hash"
        ])

        for rec in self.get_structured_attendance_logs(exclude_walkbys=True):
            writer.writerow([
                self.session_id,
                rec["student_id"],
                rec["display_name"],
                rec["seat"],
                rec["status"],
                rec["cumulative_presence_seconds"],
                round(rec["cumulative_presence_seconds"] / 60.0, 2),
                rec["presence_percentage"],
                rec["first_seen"] or "--",
                rec["last_seen"] or "--",
                rec["audit_hash"]
            ])

        return output.getvalue()
