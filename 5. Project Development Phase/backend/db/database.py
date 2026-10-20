"""
Multimodal Attendance & Engagement Agent - Edge Data Persistence & Privacy Schema
Epic 1: Task 2 (TASK-02) - Privacy-Preserving Edge Storage
"""

import sqlite3
import hashlib
import json
import time
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "classroom_intelligence.db", salt: str = "privacy_salt_offline_classroom_2026"):
        self.db_path = db_path
        self.salt = salt
        self._lock = threading.Lock()
        self._open_connections = set()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        with self._lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self._open_connections.add(conn)
            return conn

    def close(self) -> None:
        """Explicitly closes all active sqlite database connections."""
        with self._lock:
            for conn in list(self._open_connections):
                try:
                    conn.close()
                except Exception:
                    pass
            self._open_connections.clear()

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Sessions Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                course_name TEXT NOT NULL,
                instructor_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT DEFAULT 'ACTIVE',
                total_enrolled INTEGER DEFAULT 0,
                total_present INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Students / Enrolled Participants Table (Local pseudonymized IDs)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                pseudonym_hash TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                seat_label TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Attendance Logs (Sustained Presence Audit Records)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                first_detected_at TEXT NOT NULL,
                last_detected_at TEXT NOT NULL,
                total_active_seconds REAL NOT NULL,
                presence_ratio REAL NOT NULL,
                status TEXT NOT NULL, -- 'PRESENT', 'LATE', 'INTERMITTENT', 'ABSENT', 'WALKBY_FILTERED'
                verification_hash TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id),
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
            """)

            # Multimodal Engagement Time-Series Intervals (Epoch records)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS engagement_intervals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                epoch_seconds REAL NOT NULL,
                visual_attention_score REAL NOT NULL,
                motion_energy_score REAL NOT NULL,
                audio_energy_score REAL NOT NULL,
                audio_rhythm_mode TEXT NOT NULL,
                overall_engagement_index REAL NOT NULL,
                active_participants INTEGER NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
            """)

            # AI Teaching Suggestions / Agent Decisions
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS teaching_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                alert_level TEXT NOT NULL, -- 'INFO', 'ADVISORY', 'ACTIONABLE'
                title TEXT NOT NULL,
                reason TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                context_metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
            """)

            # Individual Participant Session Metrics (EPIC 5: Activity 5.2 - Reference Image: PersonMetric)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS person_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                epoch_seconds REAL NOT NULL,
                attention_score REAL NOT NULL,
                emotion_state TEXT DEFAULT 'NEUTRAL',
                motion_energy REAL DEFAULT 0.05,
                inactivity_seconds REAL DEFAULT 0.0,
                FOREIGN KEY (session_id) REFERENCES sessions(id),
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
            """)

            conn.commit()

    def generate_pseudonym(self, raw_identifier: str) -> str:
        """Create a one-way irreversible salted hash for student privacy."""
        salted = f"{self.salt}_{raw_identifier}".encode("utf-8")
        return hashlib.sha256(salted).hexdigest()[:16]

    def create_session(self, session_id: str, course_name: str, instructor_name: str, total_enrolled: int = 10) -> Dict[str, Any]:
        start_time = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sessions (id, course_name, instructor_name, start_time, status, total_enrolled)
                VALUES (?, ?, ?, ?, 'ACTIVE', ?)
            """, (session_id, course_name, instructor_name, start_time, total_enrolled))
            conn.commit()
        return {
            "session_id": session_id,
            "course_name": course_name,
            "instructor_name": instructor_name,
            "start_time": start_time,
            "status": "ACTIVE"
        }

    def seed_default_students(self, students_list: List[Dict[str, str]]) -> None:
        """Seed default enrolled students for offline classroom simulations."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for s in students_list:
                s_id = s["id"]
                pseudo = self.generate_pseudonym(s_id)
                cursor.execute("""
                    INSERT OR IGNORE INTO students (id, pseudonym_hash, display_name, seat_label)
                    VALUES (?, ?, ?, ?)
                """, (s_id, pseudo, s.get("name", s_id), s.get("seat", "Desk")))
            conn.commit()

    def enroll_student(self, student_id: str, display_name: str, seat_label: str = "Live Desk") -> Dict[str, Any]:
        """Enroll or update an individual student in the database."""
        pseudo = self.generate_pseudonym(student_id)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO students (id, pseudonym_hash, display_name, seat_label)
                VALUES (?, ?, ?, ?)
            """, (student_id, pseudo, display_name, seat_label))
            conn.commit()
        return {
            "id": student_id,
            "student_id": student_id,
            "display_name": display_name,
            "name": display_name,
            "pseudonym_hash": pseudo,
            "seat_label": seat_label
        }

    def get_enrolled_students(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students ORDER BY seat_label, display_name")
            return [dict(row) for row in cursor.fetchall()]

    def log_attendance_entry(self, session_id: str, student_id: str, first_seen: str, last_seen: str,
                             active_sec: float, presence_ratio: float, status: str) -> None:
        """Record or update attendance audit record with verification hash."""
        verification_content = f"{session_id}:{student_id}:{active_sec}:{status}:{self.salt}"
        verif_hash = hashlib.sha256(verification_content.encode("utf-8")).hexdigest()[:24]

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Check existing
            cursor.execute("SELECT id FROM attendance_logs WHERE session_id = ? AND student_id = ?", (session_id, student_id))
            existing = cursor.fetchone()
            if existing:
                cursor.execute("""
                    UPDATE attendance_logs
                    SET last_detected_at = ?, total_active_seconds = ?, presence_ratio = ?, status = ?, verification_hash = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (last_seen, active_sec, presence_ratio, status, verif_hash, existing["id"]))
            else:
                cursor.execute("""
                    INSERT INTO attendance_logs (session_id, student_id, first_detected_at, last_detected_at, total_active_seconds, presence_ratio, status, verification_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (session_id, student_id, first_seen, last_seen, active_sec, presence_ratio, status, verif_hash))
            conn.commit()

    def get_session_attendance(self, session_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.*, s.display_name, s.seat_label, s.pseudonym_hash
                FROM attendance_logs a
                JOIN students s ON a.student_id = s.id
                WHERE a.session_id = ?
                ORDER BY a.total_active_seconds DESC
            """, (session_id,))
            return [dict(row) for row in cursor.fetchall()]

    def record_engagement_interval(self, session_id: str, visual_att: float, motion_eng: float,
                                    audio_eng: float, audio_rhythm: str, overall_eng: float,
                                    active_count: int, epoch_sec: float) -> None:
        ts = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO engagement_intervals 
                (session_id, timestamp, epoch_seconds, visual_attention_score, motion_energy_score, audio_energy_score, audio_rhythm_mode, overall_engagement_index, active_participants)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (session_id, ts, epoch_sec, visual_att, motion_eng, audio_eng, audio_rhythm, overall_eng, active_count))
            conn.commit()

    def get_session_engagement_history(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM engagement_intervals
                WHERE session_id = ?
                ORDER BY id DESC LIMIT ?
            """, (session_id, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in reversed(rows)]

    def record_teaching_suggestion(self, session_id: str, alert_level: str, title: str, reason: str,
                                    recommendation: str, context_metadata: Dict[str, Any]) -> None:
        ts = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO teaching_suggestions (session_id, timestamp, alert_level, title, reason, recommendation, context_metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, ts, alert_level, title, reason, recommendation, json.dumps(context_metadata)))
            conn.commit()

    def get_session_suggestions(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM teaching_suggestions
                WHERE session_id = ?
                ORDER BY id DESC LIMIT ?
            """, (session_id, limit))
            return [dict(row) for row in cursor.fetchall()]

    def end_session(self, session_id: str) -> None:
        end_time = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Count present
            cursor.execute("SELECT COUNT(*) as cnt FROM attendance_logs WHERE session_id = ? AND status IN ('PRESENT', 'LATE')", (session_id,))
            present_count = cursor.fetchone()["cnt"]
            cursor.execute("""
                UPDATE sessions
                SET end_time = ?, status = 'COMPLETED', total_present = ?
                WHERE id = ?
            """, (end_time, present_count, session_id))
            conn.commit()

    def record_person_metric(self, session_id: str, student_id: str, attention_score: float,
                             emotion_state: str = "NEUTRAL", motion_energy: float = 0.05,
                             inactivity_seconds: float = 0.0, epoch_seconds: Optional[float] = None) -> None:
        """Records granular per-student metric interval (Reference: PersonMetric)."""
        ts = datetime.now().isoformat()
        ep = epoch_seconds if epoch_seconds is not None else time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO person_metrics 
                (session_id, student_id, timestamp, epoch_seconds, attention_score, emotion_state, motion_energy, inactivity_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (session_id, student_id, ts, ep, attention_score, emotion_state, motion_energy, inactivity_seconds))
            conn.commit()

    def get_person_metrics(self, session_id: str, student_id: Optional[str] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """Queries person metrics ordered by timestamp (Reference: PersonMetric query)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if student_id:
                cursor.execute("""
                    SELECT * FROM person_metrics
                    WHERE session_id = ? AND student_id = ?
                    ORDER BY epoch_seconds ASC
                    LIMIT ?
                """, (session_id, student_id, limit))
            else:
                cursor.execute("""
                    SELECT * FROM person_metrics
                    WHERE session_id = ?
                    ORDER BY epoch_seconds ASC
                    LIMIT ?
                """, (session_id, limit))
            return [dict(row) for row in cursor.fetchall()]
