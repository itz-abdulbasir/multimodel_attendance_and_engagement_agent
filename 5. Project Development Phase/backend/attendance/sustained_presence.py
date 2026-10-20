"""
Multimodal Attendance & Engagement Agent - Sustained Presence & Attendance Logging
Epic 3: Tasks 5 & 6 (TASK-05, TASK-06) - Sustained Presence Filtering & Attendance Logs
"""

import time
import csv
import io
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from backend.db.database import DatabaseManager

class StudentPresenceRecord:
    def __init__(self, student_id: str, display_name: str, seat: str):
        self.student_id = student_id
        self.display_name = display_name
        self.seat = seat
        
        self.first_seen_time: Optional[float] = None
        self.last_seen_time: Optional[float] = None
        self.total_active_seconds: float = 0.0
        self.last_update_timestamp: float = time.time()
        self.is_currently_visible: bool = False
        
        # Attendance classification
        self.status = "ABSENT"  # 'PRESENT', 'LATE', 'INTERMITTENT', 'ABSENT', 'WALKBY_FILTERED'
        self.presence_ratio: float = 0.0
        self.is_walkby: bool = False

    def update_presence(self, is_visible: bool, dt: float, session_elapsed: float,
                        min_sustained_sec: float, walkby_sec: float, late_cutoff_sec: float,
                        sustained_ratio_req: float) -> None:
        now = time.time()
        self.is_currently_visible = is_visible

        if is_visible:
            if self.first_seen_time is None:
                self.first_seen_time = now
            self.last_seen_time = now
            self.total_active_seconds += dt

        # Calculate presence ratio over observed elapsed session time
        effective_session_time = max(1.0, session_elapsed)
        self.presence_ratio = min(1.0, round(self.total_active_seconds / effective_session_time, 3))

        # Classify status based on sustained temporal rules
        if self.is_walkby or (self.total_active_seconds < walkby_sec and not is_visible and self.first_seen_time is not None):
            self.status = "WALKBY_FILTERED"
        elif self.total_active_seconds >= min_sustained_sec and self.presence_ratio >= sustained_ratio_req:
            # Check if arrived late
            first_seen_offset = (self.first_seen_time - (now - session_elapsed)) if self.first_seen_time else 0.0
            if first_seen_offset > late_cutoff_sec:
                self.status = "LATE"
            else:
                self.status = "PRESENT"
        elif self.total_active_seconds > 0 and self.presence_ratio < sustained_ratio_req:
            self.status = "INTERMITTENT"
        else:
            self.status = "ABSENT"


class SustainedPresenceEngine:
    """Automates classroom roll calls via temporal sustained presence filtering."""

    def __init__(self, db: DatabaseManager, session_id: str,
                 min_sustained_seconds: float = 25.0,
                 sustained_ratio: float = 0.60,
                 walkby_threshold_seconds: float = 12.0,
                 late_threshold_seconds: float = 300.0):
        self.db = db
        self.session_id = session_id
        self.min_sustained_seconds = min_sustained_seconds
        self.sustained_ratio = sustained_ratio
        self.walkby_threshold_seconds = walkby_threshold_seconds
        self.late_threshold_seconds = late_threshold_seconds
        
        self.start_wall_time = time.time()
        self.records: Dict[str, StudentPresenceRecord] = {}
        self._load_enrolled_roster()

    def _load_enrolled_roster(self) -> None:
        students = self.db.get_enrolled_students()
        for s in students:
            sid = s["id"]
            self.records[sid] = StudentPresenceRecord(
                student_id=sid,
                display_name=s["display_name"],
                seat=s["seat_label"]
            )

    def process_frame_tracks(self, active_student_ids: List[str], dt: float, walkby_ids: Optional[List[str]] = None) -> None:
        """Updates presence state for all students and logs updates."""
        elapsed = time.time() - self.start_wall_time
        walkby_set = set(walkby_ids or [])

        # Process enrolled
        for sid, record in self.records.items():
            is_vis = sid in active_student_ids
            if sid in walkby_set:
                record.is_walkby = True

            record.update_presence(
                is_visible=is_vis,
                dt=dt,
                session_elapsed=elapsed,
                min_sustained_sec=self.min_sustained_seconds,
                walkby_sec=self.walkby_threshold_seconds,
                late_cutoff_sec=self.late_threshold_seconds,
                sustained_ratio_req=self.sustained_ratio
            )

        # Also handle live webcam learners (TRK-xxx) and guest detections
        for sid in active_student_ids:
            if sid not in self.records:
                display_label = f"Live Learner ({sid})" if sid.startswith("TRK-") else f"Guest ({sid})"
                seat_label = "Webcam Live Desk" if sid.startswith("TRK-") else "Guest Desk"
                rec = StudentPresenceRecord(sid, display_label, seat_label)
                rec.is_walkby = sid in walkby_set
                rec.update_presence(True, dt, elapsed, self.min_sustained_seconds,
                                    self.walkby_threshold_seconds, self.late_threshold_seconds, self.sustained_ratio)
                self.records[sid] = rec

    def link_track_to_student(self, track_id: str, student_id: str, display_name: str, seat: str = "Webcam Live Desk") -> bool:
        """
        Seamlessly transfers/merges accumulated presence and attendance metrics from
        an anonymous live track (e.g. 'TRK-000') into an enrolled student record (e.g. 'STU-101').
        Guarantees zero lost attendance duration!
        """
        track_rec = self.records.get(track_id)
        if not track_rec:
            return False

        if student_id in self.records and student_id != track_id:
            # Merge into existing enrolled student record
            target_rec = self.records[student_id]
            target_rec.total_active_seconds += track_rec.total_active_seconds
            if track_rec.first_seen_time:
                if target_rec.first_seen_time is None:
                    target_rec.first_seen_time = track_rec.first_seen_time
                else:
                    target_rec.first_seen_time = min(target_rec.first_seen_time, track_rec.first_seen_time)
            if track_rec.last_seen_time:
                target_rec.last_seen_time = max(target_rec.last_seen_time or 0.0, track_rec.last_seen_time)
            target_rec.is_currently_visible = track_rec.is_currently_visible
            target_rec.presence_ratio = max(target_rec.presence_ratio, track_rec.presence_ratio)
            if track_rec.status in ["PRESENT", "LATE"]:
                target_rec.status = track_rec.status
            # Remove the anonymous track record
            del self.records[track_id]
        else:
            # Direct rename and update of track record
            track_rec.student_id = student_id
            track_rec.display_name = display_name
            track_rec.seat = seat
            self.records[student_id] = track_rec
            if track_id != student_id and track_id in self.records:
                del self.records[track_id]

        self.persist_attendance_snapshot()
        return True

    def persist_attendance_snapshot(self) -> None:
        """Writes current attendance states to edge database."""
        for sid, rec in self.records.items():
            if rec.status == "WALKBY_FILTERED":
                continue
            first_seen_str = datetime.fromtimestamp(rec.first_seen_time).isoformat() if rec.first_seen_time else "N/A"
            last_seen_str = datetime.fromtimestamp(rec.last_seen_time).isoformat() if rec.last_seen_time else "N/A"
            self.db.log_attendance_entry(
                session_id=self.session_id,
                student_id=sid,
                first_seen=first_seen_str,
                last_seen=last_seen_str,
                active_sec=rec.total_active_seconds,
                presence_ratio=rec.presence_ratio,
                status=rec.status
            )

    def get_live_attendance_roster(self) -> List[Dict[str, Any]]:
        roster: List[Dict[str, Any]] = []
        for sid, rec in self.records.items():
            if rec.is_walkby and rec.status == "WALKBY_FILTERED":
                continue
            roster.append({
                "student_id": rec.student_id,
                "display_name": rec.display_name,
                "seat": rec.seat,
                "status": rec.status,
                "is_visible": rec.is_currently_visible,
                "is_unlinked_track": rec.student_id.startswith("TRK-"),
                "active_seconds": round(rec.total_active_seconds, 1),
                "presence_ratio": round(rec.presence_ratio * 100, 1),
                "first_seen": datetime.fromtimestamp(rec.first_seen_time).strftime("%H:%M:%S") if rec.first_seen_time else "--",
                "last_seen": datetime.fromtimestamp(rec.last_seen_time).strftime("%H:%M:%S") if rec.last_seen_time else "--"
            })
        return sorted(roster, key=lambda x: (x["status"] != "PRESENT", x["student_id"]))

    def export_attendance_csv(self) -> str:
        """Generates formatted CSV attendance audit sheet (TASK-06)."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Student ID", "Full Name", "Seat / Location", "Attendance Status",
                         "Total Active Minutes", "Presence Ratio %", "First Detected", "Last Detected"])
        
        for rec in self.get_live_attendance_roster():
            writer.writerow([
                rec["student_id"],
                rec["display_name"],
                rec["seat"],
                rec["status"],
                round(rec["active_seconds"] / 60.0, 2),
                rec["presence_ratio"],
                rec["first_seen"],
                rec["last_seen"]
            ])
        return output.getvalue()
