"""
Multimodal Attendance & Engagement Agent - Test Suite & System Verification
Epic 9: Task 17 (TASK-17) - End-to-End System Evaluation & Offline Privacy Verification
"""

import os
import time
import json
import unittest
import numpy as np
import cv2

from backend.config import SystemConfig
from backend.db.database import DatabaseManager
from backend.vision.face_tracker import CentroidFaceTracker, ParticipantTrack
from backend.vision.attention_analyzer import VisualAttentionAnalyzer
from backend.audio.audio_analyzer import AudioSignalAnalyzer
from backend.attendance.sustained_presence import SustainedPresenceEngine
from backend.fusion.multimodal_fusion import MultimodalFusionEngine
from backend.agent.pedagogical_agent import PedagogicalReasoningAgent

def _run_async(coro):
    """Safely runs an async coroutine both from CLI and inside an existing FastAPI event loop."""
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)

class TestMultimodalIntelligenceSystem(unittest.TestCase):
    def setUp(self):
        import uuid
        self.test_db_path = f"test_intelligence_{uuid.uuid4().hex[:8]}.db"
        self.db = DatabaseManager(db_path=self.test_db_path)
        self.session_id = "TEST-SESSION-001"
        self.db.create_session(self.session_id, "Test CS-101", "Dr. Turing", 2)
        self.db.seed_default_students([
            {"id": "STU-001", "name": "Alice Turing", "seat": "Desk 1"},
            {"id": "STU-002", "name": "Bob Shannon", "seat": "Desk 2"}
        ])

    def tearDown(self):
        if hasattr(self, 'db') and self.db:
            try:
                self.db.close()
            except Exception:
                pass
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

    def test_database_and_pseudonym_privacy(self):
        """TASK-02: Verifies salted SHA-256 one-way pseudonym generation and edge storage."""
        h1 = self.db.generate_pseudonym("STU-001")
        h2 = self.db.generate_pseudonym("STU-001")
        h3 = self.db.generate_pseudonym("STU-002")

        self.assertEqual(h1, h2, "Pseudonym should be deterministic for identical input & salt.")
        self.assertNotEqual(h1, h3, "Pseudonyms for different identifiers must differ.")
        self.assertEqual(len(h1), 16, "Pseudonym hash slice must be 16 hex characters.")

    def test_sustained_presence_walkby_filter(self):
        """TASK-05, TASK-06 (Scenario 1): Transient walk-by visitor must be filtered, sustained attendee marked PRESENT."""
        engine = SustainedPresenceEngine(
            db=self.db,
            session_id=self.session_id,
            min_sustained_seconds=20.0,
            sustained_ratio=0.60,
            walkby_threshold_seconds=10.0
        )

        # Simulate 30 seconds of session time in 1-second steps
        for step in range(30):
            # STU-001 is present throughout (sustained)
            active_ids = ["STU-001"]
            walkby_ids = []

            # GUEST_WALKBY enters at step 5 and leaves at step 10 (5 seconds total < 10s threshold)
            if 5 <= step < 10:
                active_ids.append("GUEST_WALKBY")
                walkby_ids.append("GUEST_WALKBY")

            engine.process_frame_tracks(active_ids, dt=1.0, walkby_ids=walkby_ids)

        # Verify STU-001 achieved sustained attendance
        stu1_record = engine.records["STU-001"]
        self.assertEqual(stu1_record.status, "PRESENT", "Sustained attendee must be classified as PRESENT.")
        self.assertGreaterEqual(stu1_record.total_active_seconds, 20.0)

        # Verify GUEST_WALKBY was filtered out
        guest_record = engine.records["GUEST_WALKBY"]
        self.assertEqual(guest_record.status, "WALKBY_FILTERED", "Fleeting visitor (<10s) must be filtered as WALKBY_FILTERED.")

        # Test CSV Export
        csv_text = engine.export_attendance_csv()
        self.assertIn("STU-001", csv_text)
        self.assertIn("Alice Turing", csv_text)
        self.assertNotIn("GUEST_WALKBY", csv_text, "Filtered walk-by visitor must not appear on official audit sheet.")

    def test_visual_attention_and_head_pose(self):
        """TASK-07, TASK-08 (Scenario 2): Yaw/Pitch orientation must penalize distracted gaze."""
        analyzer = VisualAttentionAnalyzer(yaw_threshold=25.0, pitch_threshold=20.0)
        
        # Track 1: Looking forward at the board (yaw=0, pitch=0)
        track_attentive = ParticipantTrack(1, (100, 100), (80, 80, 40, 40), "STU-001")
        track_attentive.yaw = 2.0
        track_attentive.pitch = -3.0

        # Track 2: Distracted lateral look (yaw=35, pitch=25)
        track_distracted = ParticipantTrack(2, (200, 100), (180, 80, 40, 40), "STU-002")
        track_distracted.yaw = 35.0
        track_distracted.pitch = 25.0

        # Simulate 3 frames of continuous distracted vs attentive posture
        for _ in range(4):
            result = analyzer.analyze_tracks([track_attentive, track_distracted])

        self.assertGreater(track_attentive.attention_score, track_distracted.attention_score,
                           "Attentive frontal posture must have higher attention score than distracted gaze.")
        self.assertGreaterEqual(track_attentive.attention_score, 0.70)
        self.assertLessEqual(track_distracted.attention_score, 0.60)

    def test_audio_vad_and_monologue_detector(self):
        """TASK-09, TASK-10 (Scenario 2): Voice activity detection and monologue tracking."""
        analyzer = AudioSignalAnalyzer()
        res = analyzer.process_acoustic_metrics(energy_rms=0.065, vad_active=True, rhythm_hint="INSTRUCTOR_MONOLOGUE")
        
        self.assertEqual(res["rhythm_state"], "INSTRUCTOR_MONOLOGUE")
        self.assertTrue(res["vad_active"])
        self.assertGreater(res["energy_rms"], 0.035)

    def test_multimodal_fusion_and_engagement_index(self):
        """TASK-11, TASK-12 (Scenario 2): Composite index calculation and drop-off alert."""
        engine = MultimodalFusionEngine(drop_alert_threshold=20.0)
        
        # High engagement scenario
        high_visual = {"average_visual_attention": 0.90, "average_motion_energy": 0.08, "active_participants_count": 8}
        high_audio = {"rhythm_state": "QA_INTERACTION", "interaction_density": 0.90, "vad_active": True}
        fused_high = engine.fuse_signals(high_visual, high_audio)
        
        self.assertGreaterEqual(fused_high["engagement_index"], 75.0, "High attention & Q&A interaction should yield high EI.")

        # Simulate steep drop over multiple epochs
        low_visual = {"average_visual_attention": 0.25, "average_motion_energy": 0.01, "active_participants_count": 8}
        low_audio = {"rhythm_state": "SILENT_STUDY", "interaction_density": 0.15, "vad_active": False}

        for _ in range(16):
            fused_low = engine.fuse_signals(low_visual, low_audio)

        self.assertTrue(fused_low["attention_drop_alert"] or fused_low["trend"] == "DROPPING",
                        "Steep sustained decline must trigger trend dropping or drop alert.")

    def test_pedagogical_agent_reasoner(self):
        """TASK-13, TASK-14 (Scenario 3): Agent generates actionable teaching recommendations."""
        agent = PedagogicalReasoningAgent(self.db, self.session_id, cooldown_seconds=0.0)

        # Trigger Monologue Fatigue
        fused_data = {"engagement_index": 52.0, "trend": "DROPPING", "visual_attention_score": 0.50, "attention_drop_alert": True}
        audio_data = {"consecutive_monologue_sec": 750.0, "consecutive_silence_sec": 0.0, "rhythm_state": "INSTRUCTOR_MONOLOGUE"}

        suggestion = agent.evaluate_classroom_state(fused_data, audio_data, session_elapsed=800.0)
        
        self.assertIsNotNone(suggestion, "Agent must generate a suggestion on attention drop and long monologue.")
        self.assertIn("Pacing", suggestion["title"])
        self.assertEqual(suggestion["alert_level"], "ACTIONABLE")

    def test_offline_privacy_guarantee(self):
        """TASK-17: Verifies system runs in strict offline mode with zero telemetry or cloud endpoints."""
        config = SystemConfig()
        self.assertTrue(config.offline_mode)
        self.assertFalse(config.store_raw_frames)
        self.assertTrue(config.privacy_blur_enabled)

    def test_code_generation_and_execution(self):
        """Verifies Code Generation Engine & Code Executor produce and run analytical Python scripts."""
        from backend.utils.code_utils import CodeGenerationEngine, CodeExecutor
        gen_res = CodeGenerationEngine.generate_attendance_audit_script("TEST-AUDIT-SES", 2)
        self.assertTrue(os.path.exists(gen_res["filepath"]), "Generated code file must exist in storage/code/.")
        self.assertIn("audit_session", gen_res["code"])

        exec_res = CodeExecutor.execute_script(gen_res["filepath"])
        self.assertTrue(exec_res["success"], "Generated script should execute successfully.")
        self.assertIn("AUDITING ATTENDANCE", exec_res["output"])

    def test_tts_audio_synthesis(self):
        """Verifies Text-To-Speech Engine synthesizes valid WAV audio in storage/audio/."""
        from backend.utils.audio_utils import TextToSpeechEngine
        tts = TextToSpeechEngine()
        res = tts.synthesize_speech_alert("Attention test chime", alert_id="test_alert_123")
        self.assertTrue(os.path.exists(res["filepath"]), "Synthesized audio file must exist in storage/audio/.")
        self.assertGreater(res["size_bytes"], 1000, "Audio WAV file must have non-trivial size.")

    def test_genai_visual_aid_and_reasoning(self):
        """Verifies Google Gemini 2.0 Flash reasoning and visual SVG diagram generator."""
        from backend.utils.genai_utils import GenAIUtils
        genai = GenAIUtils()
        insight = genai.generate_teaching_insight({"engagement_index": 50.0, "trend": "DROPPING"})
        self.assertIn("diagnosis", insight)
        self.assertIn("action", insight)

        visual_aid = genai.generate_visual_aid("Signal Fusion Architecture")
        self.assertIn("<svg", visual_aid["svg"])
        self.assertIn("Signal Fusion", visual_aid["svg"])

    def test_student_and_session_analytics_generation(self):
        """Milestone 5 Activity 5.2: Verifies student session analytics and aggregated indicators."""
        # Record attendance
        self.db.log_attendance_entry(self.session_id, "STU-001", "2026-10-13T10:00:00", "2026-10-13T10:30:00", 1800.0, 0.95, "PRESENT")
        self.db.log_attendance_entry(self.session_id, "STU-002", "2026-10-13T10:00:00", "2026-10-13T10:15:00", 600.0, 0.35, "LATE")

        # Record intervals
        self.db.record_engagement_interval(self.session_id, 0.85, 0.05, 0.40, "INSTRUCTOR_MONOLOGUE", 78.5, 2, time.time())
        self.db.record_engagement_interval(self.session_id, 0.90, 0.08, 0.65, "QA_INTERACTION", 84.0, 2, time.time() + 10)

        history = self.db.get_session_engagement_history(self.session_id)
        self.assertGreaterEqual(len(history), 2)
        
        scores = [h["overall_engagement_index"] for h in history]
        self.assertGreater(np.mean(scores), 75.0)

        roster = self.db.get_session_attendance(self.session_id)
        self.assertEqual(len(roster), 2)
        self.assertEqual(roster[0]["status"], "PRESENT")

    def test_edge_cases_empty_room_and_audio_burst(self):
        """Milestone 6 Activity 6.3: Validates robustness against empty room, audio spikes, and extreme gaze."""
        # Edge Case 1: Empty Room (Zero participants)
        engine = MultimodalFusionEngine()
        empty_visual = {"average_visual_attention": 0.0, "average_motion_energy": 0.0, "active_participants_count": 0}
        empty_audio = {"rhythm_state": "SILENT_STUDY", "interaction_density": 0.0, "vad_active": False}
        res_empty = engine.fuse_signals(empty_visual, empty_audio)
        self.assertIsNotNone(res_empty["engagement_index"])
        self.assertEqual(res_empty["active_participants"], 0)

        # Edge Case 2: Extreme Audio Burst / Loud Noise
        analyzer = AudioSignalAnalyzer()
        burst_res = analyzer.process_acoustic_metrics(energy_rms=0.98, vad_active=True, rhythm_hint="COLLABORATIVE_BUZZ")
        self.assertTrue(burst_res["vad_active"])
        self.assertEqual(burst_res["rhythm_state"], "COLLABORATIVE_BUZZ")

        # Edge Case 3: Extreme Gaze Angle (Student turned 85 degrees away over 4 frames)
        att_analyzer = VisualAttentionAnalyzer()
        track_extreme = ParticipantTrack(99, (50, 50), (30, 30, 40, 40), "STU-999")
        track_extreme.yaw = 85.0  # looking 85 degrees away
        track_extreme.pitch = 5.0
        for _ in range(5):
            att_res = att_analyzer.analyze_tracks([track_extreme])
            
        self.assertEqual(track_extreme.gaze_direction, "LATERAL_DISTRACTED")
        self.assertLess(track_extreme.attention_score, 0.35)

    def test_epic1_requirements_and_frameworks_integration(self):
        """EPIC 1: Verifies integration of SQLAlchemy, Soundfile, Groq, and DeepSort."""
        # 1. SQLAlchemy ORM Integration
        from backend.db.models import StudentModel, SessionLocal
        session = SessionLocal()
        students_count = session.query(StudentModel).count()
        session.close()
        self.assertGreaterEqual(students_count, 0)

        # 2. Audio Processing (Soundfile / Wave)
        analyzer = AudioSignalAnalyzer()
        self.assertTrue(hasattr(analyzer, "analyze_audio_file"))

        # 3. GenAI / Groq LLM Integration
        from backend.utils.genai_utils import GenAIUtils, GROQ_AVAILABLE
        genai = GenAIUtils()
        self.assertTrue(GROQ_AVAILABLE)
        self.assertIsNotNone(genai.model_name)

        # 4. Computer Vision DeepSORT & MediaPipe Integration
        from backend.vision.face_tracker import DEEPSORT_AVAILABLE, MEDIAPIPE_AVAILABLE
        self.assertTrue(DEEPSORT_AVAILABLE)
        self.assertTrue(MEDIAPIPE_AVAILABLE)

        # 5. Audio Processing Librosa & Soundfile Integration
        from backend.audio.audio_analyzer import LIBROSA_AVAILABLE
        self.assertTrue(LIBROSA_AVAILABLE)


        # 5. EPIC 1 Requirements Specification API Endpoint
        from backend.api.server import get_epic1_requirements
        req_res = _run_async(get_epic1_requirements())
        self.assertEqual(req_res["status"], "VERIFIED & ACTIVE")
        self.assertEqual(len(req_res["dependency_categories"]), 5)
        self.assertIn("Computer Vision Libraries", [c["category"] for c in req_res["dependency_categories"]])
        self.assertIn("Audio Processing Libraries", [c["category"] for c in req_res["dependency_categories"]])
        self.assertIn("Backend and API Libraries", [c["category"] for c in req_res["dependency_categories"]])
        self.assertIn("Data Processing Libraries", [c["category"] for c in req_res["dependency_categories"]])

    def test_epic2_face_detector_and_camera_service(self):
        """EPIC 2 Activity 2.1: Verifies FaceDetector and CameraService (User Reference Implementation)."""
        from backend.core.face_detection import FaceDetector
        from backend.core.camera_service import CameraService

        # 1. FaceDetector verification
        detector = FaceDetector(scale_factor=1.1, min_neighbors=5, min_size=(30, 30))
        self.assertFalse(detector.face_cascade.empty(), "Haar Cascade XML classifier must load successfully.")
        
        # Test frame processing on 640x480 frame
        blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Draw a synthetic face-like circle to test pipeline execution
        cv2.circle(blank_frame, (320, 240), 60, (200, 200, 200), -1)
        dets = detector.process_frame(blank_frame)
        self.assertIsInstance(dets, list, "Detection output must be a list of detections.")

        # Test simulated detection formatting
        sample_dets = [{"bbox": (100, 100, 50, 50), "score": 1.0, "centroid": (125, 125)}]
        vis_frame = detector.draw_detections(blank_frame, sample_dets)
        self.assertEqual(vis_frame.shape, blank_frame.shape)

        # 2. CameraService verification
        camera = CameraService(camera_id=0, fps=15, width=640, height=480)
        self.assertFalse(camera.is_running)
        self.assertEqual(camera.camera_id, 0)
        
        status = camera.get_status()
        self.assertIn("is_running", status)
        self.assertIn("resolution", status)
        self.assertEqual(status["resolution"], "640x480")
        self.assertEqual(status["target_fps"], 15)

    def test_epic2_face_tracking_and_spatial_association(self):
        """EPIC 2 Activity 2.1: Verifies unique identifier consistency, spatial association, and occlusion resilience."""
        from backend.core.face_tracker import FaceTracker

        tracker = FaceTracker(max_disappeared=5, max_distance=60.0, privacy_blur=True)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Step 1: Initial detection at (100, 100)
        dets_frame1 = [{"bbox": (100, 100, 50, 50), "score": 1.0, "centroid": (125, 125)}]
        _, tracks_1 = tracker.process_frame(frame, detections=dets_frame1, timestamp=1000.0)
        self.assertEqual(len(tracks_1), 1)
        t1 = tracks_1[0]
        initial_track_id = t1["track_id"]
        self.assertEqual(t1["status"], "ACTIVE")

        # Step 2: Consecutive frame with slight participant movement to (106, 103)
        dets_frame2 = [{"bbox": (106, 103, 50, 50), "score": 1.0, "centroid": (131, 128)}]
        _, tracks_2 = tracker.process_frame(frame, detections=dets_frame2, timestamp=1001.0)
        self.assertEqual(len(tracks_2), 1)
        t2 = tracks_2[0]
        # Unique identifier must remain consistent across frames!
        self.assertEqual(t2["track_id"], initial_track_id, "Track ID must remain consistent across consecutive movement frames.")
        self.assertEqual(t2["total_frames_active"], 2)
        self.assertGreater(t2["presence_duration"], 0.0)
        self.assertGreater(t2["movement_energy"], 0.0)

        # Step 3: Brief occlusion / head turn (zero detections in frame)
        _, tracks_3 = tracker.process_frame(frame, detections=[], timestamp=1002.0)
        self.assertEqual(len(tracks_3), 1, "Track must persist across brief occlusion frames.")
        t3 = tracks_3[0]
        self.assertEqual(t3["track_id"], initial_track_id)
        self.assertEqual(t3["status"], "OCCLUDED")
        self.assertEqual(t3["disappeared_frames"], 1)

        # Step 4: Re-appearance after occlusion at (110, 105)
        dets_frame4 = [{"bbox": (110, 105, 50, 50), "score": 1.0, "centroid": (135, 130)}]
        _, tracks_4 = tracker.process_frame(frame, detections=dets_frame4, timestamp=1003.0)
        self.assertEqual(len(tracks_4), 1)
        t4 = tracks_4[0]
        self.assertEqual(t4["track_id"], initial_track_id, "Track ID must recover and persist identity after occlusion.")
        self.assertEqual(t4["status"], "ACTIVE")
        self.assertEqual(t4["disappeared_frames"], 0)

        # Step 5: Structured Data Output validation
        record = tracker.get_structured_tracks()[0]
        self.assertIn("track_id", record)
        self.assertIn("student_id", record)
        self.assertIn("timestamp", record)
        self.assertIn("bbox", record)
        self.assertIn("centroid", record)
        self.assertIn("presence_duration", record)
        self.assertIn("velocity", record)

    def test_epic2_vision_api_endpoints(self):
        """EPIC 2 Activity 2.1: Verifies Vision Module API telemetry and status endpoints."""
        from backend.api.server import get_vision_status, get_vision_tracks, get_milestone2_status

        # 1. Vision status endpoint
        status_res = _run_async(get_vision_status())
        self.assertEqual(status_res["status"], "ACTIVE")
        self.assertEqual(status_res["milestone"], "EPIC 2: Vision Module Development")
        self.assertIn("detector", status_res)
        self.assertIn("tracker", status_res)

        # 2. Vision tracks endpoint
        tracks_res = _run_async(get_vision_tracks())
        self.assertIn("active_tracks_count", tracks_res)
        self.assertIn("tracks", tracks_res)

        # 3. Milestone 2 summary endpoint
        m2_res = _run_async(get_milestone2_status())
        self.assertEqual(m2_res["milestone"], "EPIC 2: Vision Module Development")
        self.assertEqual(m2_res["activity_2_1"]["status"], "COMPLETED & VERIFIED")
        self.assertEqual(m2_res["activity_2_2"]["status"], "COMPLETED & VERIFIED")

    def test_epic2_activity2_2_face_recognizer(self):
        """EPIC 2 Activity 2.2: Verifies FaceRecognizer (Student enrollment, recognition, and offline fallback)."""
        import tempfile
        import shutil
        from backend.core.face_recognition import FaceRecognizer

        test_dir = tempfile.mkdtemp(prefix="test_student_db_")
        try:
            recognizer = FaceRecognizer(db_path=test_dir)
            
            # Step 1: Empty database must safely return empty list without crashing
            blank_frame = np.zeros((120, 120, 3), dtype=np.uint8)
            empty_matches = recognizer.recognize(blank_frame)
            self.assertEqual(empty_matches, [], "Recognition on empty student database must return empty list.")

            # Step 2: Register student reference face
            face_img = np.zeros((120, 120, 3), dtype=np.uint8)
            cv2.circle(face_img, (60, 60), 35, (180, 160, 140), -1)
            registered = recognizer.register_student(face_img, student_id="STU-TEST-99", display_name="Test Student 99")
            self.assertTrue(registered, "Student registration must succeed.")
            
            students = recognizer.get_registered_students()
            self.assertEqual(len(students), 1)
            self.assertEqual(students[0]["student_id"], "STU-TEST-99")

            # Step 3: Match against registered face
            matches = recognizer.recognize(face_img)
            self.assertGreaterEqual(len(matches), 1, "Must recognize registered face.")
            self.assertEqual(matches[0]["student_id"], "STU-TEST-99")
            self.assertTrue(matches[0]["verified"])

        finally:
            shutil.rmtree(test_dir, ignore_errors=True)

    def test_epic2_activity2_2_presence_based_attendance_logic(self):
        """EPIC 2 Activity 2.2: Verifies cumulative presence duration, single-frame rejection, and threshold confirmation."""
        from backend.core.presence_attendance import PresenceAttendanceEngine

        engine = PresenceAttendanceEngine(
            session_id="TEST-SES-PRESENCE",
            min_sustained_seconds=15.0,     # Must achieve 15 seconds to be PRESENT
            walkby_threshold_seconds=5.0    # < 5s is filtered as WALKBY_FILTERED
        )
        engine.register_enrolled_students([
            {"id": "STU-REGULAR", "name": "Regular Student", "seat": "Desk A"},
            {"id": "STU-WALKBY", "name": "Fleeting Walkby", "seat": "Hallway"}
        ])

        # Step 1: Single Frame Detection (t = 1.0s, dt = 1.0s)
        # MUST NOT be marked PRESENT! Single frame must only be INTERMITTENT.
        logs_1 = engine.process_tracking_frame(["STU-REGULAR", "STU-WALKBY"], timestamp=1001.0, dt=1.0)
        rec_regular_1 = engine.records["STU-REGULAR"]
        self.assertEqual(rec_regular_1.status, "INTERMITTENT", "Single frame detection must NOT mark attendance.")
        self.assertEqual(rec_regular_1.cumulative_presence_seconds, 1.0)

        # Step 2: Simulate fleeting walkby departing after 3 seconds (3s < 5s threshold)
        for s in range(2, 4):
            engine.process_tracking_frame(["STU-REGULAR", "STU-WALKBY"], timestamp=1000.0 + s, dt=1.0)
        
        # Walkby leaves (not in active_ids anymore)
        for s in range(4, 12):
            engine.process_tracking_frame(["STU-REGULAR"], timestamp=1000.0 + s, dt=1.0)

        # Verify walk-by visitor was filtered out
        rec_walkby = engine.records["STU-WALKBY"]
        self.assertEqual(rec_walkby.status, "WALKBY_FILTERED", "Fleeting visitor (<5s) must be classified as WALKBY_FILTERED.")

        # At t=11s, regular student has accumulated 11 seconds (< 15s threshold -> still INTERMITTENT)
        rec_regular_mid = engine.records["STU-REGULAR"]
        self.assertEqual(rec_regular_mid.status, "INTERMITTENT")
        self.assertEqual(rec_regular_mid.cumulative_presence_seconds, 11.0)

        # Step 3: Regular student reaches threshold (15 seconds total presence)
        for s in range(12, 17):
            engine.process_tracking_frame(["STU-REGULAR"], timestamp=1000.0 + s, dt=1.0)

        # Cumulative presence is now 16.0s >= 15.0s threshold -> Status CONFIRMED PRESENT!
        rec_regular_final = engine.records["STU-REGULAR"]
        self.assertEqual(rec_regular_final.status, "PRESENT", "Cumulative presence exceeding threshold must be marked PRESENT.")
        self.assertGreaterEqual(rec_regular_final.cumulative_presence_seconds, 15.0)

        # Step 4: Verify Structured Attendance Logs & CSV Export
        logs = engine.get_structured_attendance_logs(exclude_walkbys=True)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["student_id"], "STU-REGULAR")
        self.assertEqual(logs[0]["status"], "PRESENT")
        self.assertIn("audit_hash", logs[0])
        self.assertIn("cumulative_presence_seconds", logs[0])

        csv_text = engine.export_attendance_csv()
        self.assertIn("STU-REGULAR", csv_text)
        self.assertIn("PRESENT", csv_text)
        self.assertNotIn("STU-WALKBY", csv_text, "Filtered walk-by visitor must be excluded from official CSV attendance audit.")

    def test_epic2_activity2_2_api_endpoints(self):
        """EPIC 2 Activity 2.2: Verifies Presence Summary, Logs, and Registered Faces API endpoints."""
        from backend.api.server import get_presence_summary, get_presence_logs, get_registered_faces

        # 1. Presence summary endpoint
        summary_res = _run_async(get_presence_summary())
        self.assertIn("present_count", summary_res)
        self.assertIn("attendance_rate_percent", summary_res)
        self.assertIn("min_sustained_threshold_seconds", summary_res)

        # 2. Presence logs endpoint
        logs_res = _run_async(get_presence_logs(exclude_walkbys=True))
        self.assertIn("total_records", logs_res)
        self.assertIn("records", logs_res)

        # 3. Registered faces endpoint
        faces_res = _run_async(get_registered_faces())
        self.assertIn("database_path", faces_res)
        self.assertIn("total_enrolled", faces_res)

    def test_epic3_activity3_1_audio_analyzer_reference(self):
        """EPIC 3 Activity 3.1: Verifies AudioAnalyzer reference implementation from user screenshot."""
        from backend.core.audio_analysis import AudioAnalyzer
        analyzer = AudioAnalyzer(sample_rate=16000)
        self.assertEqual(analyzer.sample_rate, 16000)

        # 1. Empty input returns None
        empty_res = analyzer.analyze_audio_chunk([])
        self.assertIsNone(empty_res, "Empty audio data must return None as shown in reference architecture.")

        # 2. Raw 16-bit PCM bytes input
        t = np.linspace(0, 1.0, 16000, endpoint=False)
        pcm_signal = (0.5 * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16).tobytes()
        res_bytes = analyzer.analyze_audio_chunk(pcm_signal)
        self.assertIsNotNone(res_bytes)
        self.assertIn("noise_level_db", res_bytes)
        self.assertIn("speech_vs_silence_ratio", res_bytes)
        self.assertIn("sound_activity_pattern", res_bytes)
        self.assertIn("rms_energy", res_bytes)
        self.assertIn("audio_engagement_score", res_bytes)
        self.assertTrue(res_bytes["vad_active"])

        # 3. Float32 NumPy array input
        y_float = 0.05 * np.sin(2 * np.pi * 300 * t).astype(np.float32)
        res_array = analyzer.analyze_audio_chunk(y_float)
        self.assertIsNotNone(res_array)
        self.assertGreater(res_array["noise_level_spl"], 30.0)
        self.assertEqual(res_array["sample_count"], 16000)

    def test_epic3_activity3_1_standardization_and_resampling(self):
        """EPIC 3 Activity 3.1: Verifies sampling rate normalization (16kHz) and channel standardization (Mono)."""
        from backend.core.audio_analysis import AudioAnalyzer, standardize_audio_waveform
        analyzer = AudioAnalyzer(sample_rate=16000)

        # 1. Channel Standardization (Stereo [N, 2] -> Mono [N])
        stereo_signal = np.random.randn(8000, 2).astype(np.float32) * 0.1
        mono_result = analyzer.standardize_waveform(stereo_signal, source_sr=16000)
        self.assertEqual(mono_result.ndim, 1, "Multi-channel stereo signal must be standardized to 1D mono.")
        self.assertEqual(len(mono_result), 8000)

        # 2. Sampling Rate Normalization (44.1kHz -> 16kHz)
        sr_source = 44100
        duration_sec = 0.5
        t = np.linspace(0, duration_sec, int(sr_source * duration_sec), endpoint=False)
        sig_44k = (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
        resampled_16k = analyzer.standardize_waveform(sig_44k, source_sr=sr_source)
        expected_samples = int(duration_sec * 16000)
        # Allow +/- 2 samples due to fractional rounding
        self.assertAlmostEqual(len(resampled_16k), expected_samples, delta=5,
                              msg="Sampling rate normalization must produce target 16kHz sample count.")

        # 3. Convenience function test
        conv_res = standardize_audio_waveform(stereo_signal, source_sr=16000, target_sr=16000)
        self.assertEqual(conv_res.ndim, 1)

    def test_epic3_activity3_1_fixed_duration_window_segmentation(self):
        """EPIC 3 Activity 3.1: Verifies fixed-duration window segmentation and video-frame alignment."""
        from backend.core.audio_analysis import AudioAnalyzer
        analyzer = AudioAnalyzer(sample_rate=16000, window_duration_sec=1.0)

        # Create 5.0 seconds of classroom audio waveform
        waveform = analyzer.synthesize_classroom_signal(duration_sec=5.0, rhythm_mode="QA_INTERACTION")
        self.assertEqual(len(waveform), 5 * 16000)

        # Segment into 1.0s windows aligned with 15 FPS video
        segments = analyzer.segment_waveform(waveform, window_duration_sec=1.0, video_fps=15.0)
        self.assertEqual(len(segments), 5, "5.0s waveform segmented into 1.0s windows must produce exactly 5 segments.")

        # Verify structured metadata per window
        for i, seg in enumerate(segments):
            self.assertEqual(seg.segment_index, i)
            self.assertAlmostEqual(seg.duration_sec, 1.0, delta=0.05)
            self.assertEqual(seg.sample_rate, 16000)
            self.assertGreater(seg.rms_energy, 0.0)
            self.assertGreater(seg.noise_level_spl, 30.0)
            self.assertIn("aligned_frame_start", seg.to_dict())
            self.assertIn("aligned_frame_end", seg.to_dict())
            # Frame mapping verification (15 FPS * 1.0s = 15 frames per window)
            self.assertEqual(seg.aligned_frame_start, i * 15)
            self.assertEqual(seg.aligned_frame_end, (i + 1) * 15 - 1)

    def test_epic3_activity3_1_structured_storage_and_export(self):
        """EPIC 3 Activity 3.1: Verifies structured storage (JSON/CSV) with timestamps and amplitude data."""
        import tempfile
        from backend.core.audio_analysis import AudioAnalyzer
        analyzer = AudioAnalyzer(sample_rate=16000)

        waveform = analyzer.synthesize_classroom_signal(duration_sec=3.0, rhythm_mode="INSTRUCTOR_MONOLOGUE")
        segments = analyzer.segment_waveform(waveform, window_duration_sec=1.0)

        with tempfile.TemporaryDirectory() as tmp_dir:
            json_path = os.path.join(tmp_dir, "audio_segments.json")
            csv_path = os.path.join(tmp_dir, "audio_segments.csv")

            # 1. JSON Export
            analyzer.save_structured_data(segments, json_path, format_type="json")
            self.assertTrue(os.path.exists(json_path))
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data["total_segments"], 3)
            self.assertIn("start_time", data["segments"][0])
            self.assertIn("rms_energy", data["segments"][0])
            self.assertIn("db_level", data["segments"][0])

            # 2. CSV Export
            analyzer.save_structured_data(segments, csv_path, format_type="csv")
            self.assertTrue(os.path.exists(csv_path))
            with open(csv_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 4)  # 1 header + 3 segments
            self.assertIn("segment_index", lines[0])
            self.assertIn("rms_energy", lines[0])

    def test_epic3_activity3_1_api_endpoints(self):
        """EPIC 3 Activity 3.1: Verifies Activity 3.1 REST API status and analysis endpoints."""
        from backend.api.server import (
            get_activity_3_1_status,
            analyze_audio_chunk_endpoint,
            segment_waveform_endpoint,
            get_structured_audio_segments
        )

        # 1. Activity 3.1 status endpoint
        status_res = _run_async(get_activity_3_1_status())
        self.assertEqual(status_res["activity_id"], "Activity 3.1")
        self.assertEqual(status_res["status"], "COMPLETED & VERIFIED")
        self.assertEqual(status_res["sampling_rate_hz"], 16000)
        self.assertIn("sampling_rate_normalized", status_res)
        self.assertIn("channel_standardization", status_res)

        # 2. Audio chunk analysis endpoint
        chunk_res = _run_async(analyze_audio_chunk_endpoint({
            "duration_sec": 1.0,
            "rhythm_mode": "QA_INTERACTION"
        }))
        self.assertEqual(chunk_res["status"], "SUCCESS")
        metrics = chunk_res["metrics"]
        self.assertIn("noise_level_db", metrics)
        self.assertIn("speech_vs_silence_ratio", metrics)
        self.assertIn("sound_activity_pattern", metrics)

        # 3. Waveform segmentation endpoint
        seg_res = _run_async(segment_waveform_endpoint(duration_sec=3.0, rhythm_mode="INSTRUCTOR_MONOLOGUE", window_sec=1.0, video_fps=15.0))
        self.assertEqual(seg_res["status"], "SUCCESS")
        self.assertEqual(seg_res["total_segments"], 3)
        self.assertEqual(len(seg_res["segments"]), 3)

        # 4. Structured segments retrieval endpoint
        segs_res = _run_async(get_structured_audio_segments(limit=10))
        self.assertEqual(segs_res["status"], "SUCCESS")
        self.assertIn("segments", segs_res)

    def test_epic3_activity3_2_acoustic_features_computation(self):
        """
        EPIC 3 Activity 3.2: Comprehensive Acoustic Feature Extraction
        Tests computation of energy levels, amplitude variations, and short-time characteristics.
        """
        from backend.core.audio_analysis import NoiseAndSpeechActivityAnalyzer, AudioAnalyzer
        analyzer = NoiseAndSpeechActivityAnalyzer(sample_rate=16000)
        core_audio = AudioAnalyzer(sample_rate=16000)

        # 1. Synthesize active speech signal
        speech_wave = core_audio.synthesize_classroom_signal(duration_sec=1.0, rhythm_mode="QA_INTERACTION")
        features = analyzer.compute_segment_features(speech_wave, segment_index=0)

        # Verify Energy Levels
        self.assertGreater(features.rms_energy, 0.0)
        self.assertGreater(features.short_time_energy, 0.0)
        self.assertLessEqual(features.db_level, 0.0)
        self.assertGreaterEqual(features.db_level, -80.0)
        self.assertGreaterEqual(features.noise_level_spl, 30.0)
        self.assertLessEqual(features.noise_level_spl, 95.0)

        # Verify Amplitude Variation
        self.assertGreater(features.peak_to_peak, 0.0)
        self.assertGreater(features.amplitude_std, 0.0)
        self.assertGreaterEqual(features.crest_factor, 1.0)
        self.assertGreaterEqual(features.dynamic_range_db, 0.0)

        # Verify Short-Time Signal Characteristics
        self.assertGreaterEqual(features.zero_crossing_rate, 0.0)
        self.assertLessEqual(features.zero_crossing_rate, 1.0)
        self.assertGreaterEqual(features.spectral_centroid, 0.0)
        self.assertGreaterEqual(features.spectral_flatness, 0.0)
        self.assertLessEqual(features.spectral_flatness, 1.0)

        # Verify Dict Serialization
        f_dict = features.to_dict()
        self.assertIn("rms_energy", f_dict)
        self.assertIn("noise_level_spl", f_dict)
        self.assertIn("spectral_centroid", f_dict)
        self.assertIn("speech_state", f_dict)

    def test_epic3_activity3_2_three_tier_signal_differentiation(self):
        """
        EPIC 3 Activity 3.2: Three-Tier Signal Classification
        Differentiates between SILENCE, BACKGROUND_NOISE, and ACTIVE_SPEECH.
        """
        from backend.core.audio_analysis import NoiseAndSpeechActivityAnalyzer
        analyzer = NoiseAndSpeechActivityAnalyzer(sample_rate=16000)

        # Tier 1: SILENCE (zero energy)
        silence_wave = np.zeros(16000, dtype=np.float32)
        feat_silence = analyzer.compute_segment_features(silence_wave)
        self.assertEqual(feat_silence.speech_state, "SILENCE")
        self.assertFalse(feat_silence.vad_active)
        self.assertLessEqual(feat_silence.noise_level_spl, 42.0)

        # Tier 2: BACKGROUND_NOISE (flat white noise, no harmonic vocal formants)
        np.random.seed(42)
        noise_wave = np.random.uniform(-0.06, 0.06, 16000).astype(np.float32)
        feat_noise = analyzer.compute_segment_features(noise_wave)
        self.assertEqual(feat_noise.speech_state, "BACKGROUND_NOISE")
        self.assertFalse(feat_noise.vad_active)
        self.assertGreater(feat_noise.spectral_flatness, 0.40)

        # Tier 3: ACTIVE_SPEECH (harmonic tones with syllable dynamic amplitude modulation)
        t = np.linspace(0, 1.0, 16000, endpoint=False)
        envelope = 0.5 * (1.0 + np.sin(2 * np.pi * 3.0 * t)) # 3 Hz syllable rate
        harmonics = (np.sin(2 * np.pi * 220.0 * t) +
                     0.5 * np.sin(2 * np.pi * 440.0 * t) +
                     0.25 * np.sin(2 * np.pi * 880.0 * t))
        speech_wave = (0.20 * envelope * harmonics).astype(np.float32)
        feat_speech = analyzer.compute_segment_features(speech_wave)
        self.assertEqual(feat_speech.speech_state, "ACTIVE_SPEECH")
        self.assertTrue(feat_speech.vad_active)
        self.assertLess(feat_speech.spectral_flatness, 0.45)

    def test_epic3_activity3_2_ambient_noise_level_trends(self):
        """
        EPIC 3 Activity 3.2: Ambient Noise Level Trends & Environment Classification
        Tests rolling noise floor tracking and RISING / FALLING / STABLE direction.
        """
        from backend.core.audio_analysis import NoiseAndSpeechActivityAnalyzer
        analyzer = NoiseAndSpeechActivityAnalyzer(sample_rate=16000)

        # Simulate quiet conditions -> SPL history
        for _ in range(10):
            analyzer.spl_history.append(45.0)
        trend_stable = analyzer.get_noise_level_trend()
        self.assertEqual(trend_stable["trend"], "STABLE")
        self.assertAlmostEqual(trend_stable["mean_spl"], 45.0, delta=1.0)

        # Simulate rising noise levels (e.g. noise spike from 45 to 65 dB SPL)
        analyzer.spl_history = [45.0] * 10 + [65.0] * 10
        trend_rising = analyzer.get_noise_level_trend()
        self.assertEqual(trend_rising["trend"], "RISING")
        self.assertGreater(trend_rising["delta_db"], 3.0)

        # Simulate falling noise levels (e.g. noise calming down from 70 to 45 dB SPL)
        analyzer.spl_history = [70.0] * 10 + [45.0] * 10
        trend_falling = analyzer.get_noise_level_trend()
        self.assertEqual(trend_falling["trend"], "FALLING")
        self.assertLess(trend_falling["delta_db"], -3.0)

    def test_epic3_activity3_2_speech_activity_and_participation(self):
        """
        EPIC 3 Activity 3.2: Speech Activity, Interaction Intensity & Participation Frequency
        """
        from backend.core.audio_analysis import NoiseAndSpeechActivityAnalyzer, AudioAnalyzer
        analyzer = NoiseAndSpeechActivityAnalyzer(sample_rate=16000)
        core_audio = AudioAnalyzer(sample_rate=16000)

        # Simulate speaker turns by transitioning speech state
        t_now = time.time()
        silence_wave = np.zeros(16000, dtype=np.float32)
        speech_wave = core_audio.synthesize_classroom_signal(duration_sec=1.0, rhythm_mode="QA_INTERACTION")

        # 3 turns
        for i in range(3):
            analyzer.compute_segment_features(silence_wave, timestamp=t_now + i * 2.0)
            feat = analyzer.compute_segment_features(speech_wave, timestamp=t_now + i * 2.0 + 1.0)

        self.assertGreaterEqual(analyzer.speaker_turns_count, 3)
        self.assertGreater(feat.participation_frequency, 0.0)
        self.assertIn(feat.ambient_noise_level, ["QUIET", "MODERATE", "ELEVATED", "LOUD_DISRUPTIVE"])

    def test_epic3_activity3_2_session_context_aggregation(self):
        """
        EPIC 3 Activity 3.2: Aggregation of Session-Level Audio Context Metrics
        """
        from backend.core.audio_analysis import NoiseAndSpeechActivityAnalyzer
        analyzer = NoiseAndSpeechActivityAnalyzer(sample_rate=16000)

        # Populate state durations
        analyzer.durations_by_state["ACTIVE_SPEECH"] = 60.0
        analyzer.durations_by_state["BACKGROUND_NOISE"] = 20.0
        analyzer.durations_by_state["SILENCE"] = 20.0
        analyzer.spl_history = [52.0, 54.0, 58.0, 55.0]

        ctx = analyzer.aggregate_session_context()
        self.assertAlmostEqual(ctx["session_duration_sec"], 100.0, delta=1.0)
        self.assertAlmostEqual(ctx["speech_activity_ratio_percent"], 60.0, delta=1.0)
        self.assertAlmostEqual(ctx["background_noise_ratio_percent"], 20.0, delta=1.0)
        self.assertAlmostEqual(ctx["silence_ratio_percent"], 20.0, delta=1.0)
        self.assertIn("environmental_acoustic_quality", ctx)
        self.assertEqual(ctx["environmental_acoustic_quality"], "OPTIMAL_LEARNING")

    def test_epic3_activity3_2_multimodal_fusion_format(self):
        """
        EPIC 3 Activity 3.2: Multimodal Fusion Audio Vector Formatting
        Verifies that audio insights structure cleanly fuses with visual data in MultimodalFusionEngine.
        """
        from backend.core.audio_analysis import NoiseAndSpeechActivityAnalyzer
        from backend.fusion.multimodal_fusion import MultimodalFusionEngine

        analyzer = NoiseAndSpeechActivityAnalyzer(sample_rate=16000)
        fusion = MultimodalFusionEngine(weight_visual=0.50, weight_motion=0.20, weight_audio=0.30)

        # Generate audio vector
        audio_vec = analyzer.format_for_multimodal_fusion()
        self.assertIn("rhythm_state", audio_vec)
        self.assertIn("interaction_density", audio_vec)
        self.assertIn("vad_active", audio_vec)
        self.assertIn("noise_level_spl", audio_vec)
        self.assertIn("session_context", audio_vec)

        # Fuse with visual telemetry
        visual_data = {
            "average_visual_attention": 0.82,
            "average_motion_energy": 0.08,
            "active_participants_count": 8
        }
        fused = fusion.fuse_signals(visual_data, audio_vec)

        self.assertIn("engagement_index", fused)
        self.assertGreater(fused["engagement_index"], 0.0)
        self.assertLessEqual(fused["engagement_index"], 100.0)
        self.assertIn("audio_engagement_score", fused)
        self.assertEqual(fused["rhythm_state"], audio_vec["rhythm_state"])

    def test_epic3_activity3_2_api_endpoints(self):
        """
        EPIC 3 Activity 3.2: REST API Endpoints Verification
        Tests /api/audio/activity_3_2/status, /analyze_features, /session_context, /noise_trends, and /fusion_payload
        """
        from backend.api.server import (
            get_activity_3_2_status,
            analyze_audio_features_endpoint,
            get_session_audio_context_endpoint,
            get_noise_level_trends_endpoint,
            get_audio_fusion_payload_endpoint
        )

        # 1. Status endpoint
        status_res = _run_async(get_activity_3_2_status())
        self.assertEqual(status_res["activity_id"], "Activity 3.2")
        self.assertEqual(status_res["status"], "COMPLETED & VERIFIED")
        self.assertIn("current_state", status_res)
        self.assertIn("noise_trend", status_res)
        self.assertIn("session_context", status_res)

        # 2. Analyze features endpoint
        feat_res = _run_async(analyze_audio_features_endpoint({
            "duration_sec": 1.0,
            "rhythm_mode": "COLLABORATIVE_BUZZ"
        }))
        self.assertEqual(feat_res["status"], "SUCCESS")
        self.assertIn("features", feat_res)
        self.assertIn("rms_energy", feat_res["features"])
        self.assertIn("noise_level_spl", feat_res["features"])

        # 3. Session context endpoint
        ctx_res = _run_async(get_session_audio_context_endpoint())
        self.assertEqual(ctx_res["status"], "SUCCESS")
        self.assertIn("audio_context", ctx_res)

        # 4. Noise trends endpoint
        trends_res = _run_async(get_noise_level_trends_endpoint())
        self.assertEqual(trends_res["status"], "SUCCESS")
        self.assertIn("trend_summary", trends_res)

        # 5. Fusion payload endpoint
        fusion_res = _run_async(get_audio_fusion_payload_endpoint())
        self.assertEqual(fusion_res["status"], "SUCCESS")
        self.assertIn("multimodal_audio_vector", fusion_res)

    # =========================================================================
    # EPIC 4: AI IMPLEMENTATION - ACTIVITY 4.1: MULTIMODAL AGENT IMPLEMENTATION
    # =========================================================================

    def test_epic4_activity4_1_llm_insights_generator(self):
        """
        EPIC 4 Activity 4.1: LLM Insights Generator Verification
        Tests InsightGenerator (backend/core/llm_insights.py) with llama-3.3-70b-versatile
        and robust offline educational reasoning fallback.
        """
        from backend.core.llm_insights import InsightGenerator
        generator = InsightGenerator()
        self.assertEqual(generator.model, "llama-3.3-70b-versatile")

        # 1. Test Prompt Formulation
        session_data = {
            "engagement_index": 78.5,
            "visual_attention_score": 0.82,
            "motion_balance_score": 0.90,
            "rhythm_state": "INSTRUCTOR_MONOLOGUE",
            "noise_level_spl": 52.0,
            "ambient_noise_level": "MODERATE",
            "participation_frequency": 1.2,
            "trend": "STABLE",
            "active_participants": 8
        }
        prompt = generator.build_prompt(session_data)
        self.assertIn("Engagement Index", prompt)
        self.assertIn("Visual Focus Ratio", prompt)
        self.assertIn("Classroom Acoustic Rhythm", prompt)

        # 2. Test Insight Generation (Offline Fallback & Output Structure)
        result = generator.generate_classroom_insight(session_data)
        self.assertEqual(result["status"], "success")
        self.assertIn("insight", result)
        self.assertIn("recommendation", result)
        self.assertGreater(len(result["insight"]), 0)
        self.assertGreater(len(result["recommendation"]), 0)
        self.assertIn("timestamp", result)

    def test_epic4_activity4_1_multimodal_agent_initialization(self):
        """
        EPIC 4 Activity 4.1: Multimodal Agent Initialization
        Tests MultimodalAgent initialization, weight distribution, and integration.
        """
        from backend.agent.multimodal_agent import MultimodalAgent
        agent = MultimodalAgent(
            weight_visual=0.50,
            weight_motion=0.20,
            weight_audio=0.30,
            drop_threshold=20.0
        )
        self.assertEqual(agent.w_visual, 0.50)
        self.assertEqual(agent.w_motion, 0.20)
        self.assertEqual(agent.w_audio, 0.30)
        self.assertIsNotNone(agent.insight_generator)
        self.assertEqual(len(agent.reasoning_history), 0)

    def test_epic4_activity4_1_rule_based_reasoning_high_flow(self):
        """
        EPIC 4 Activity 4.1: Rule M1 High Instructional Flow
        Visual attention >= 70% + Quiet room (<65 dB SPL) -> M1_HIGH_INSTRUCTIONAL_FLOW
        """
        from backend.agent.multimodal_agent import MultimodalAgent
        agent = MultimodalAgent()

        visual_data = {
            "average_visual_attention": 0.85,
            "average_motion_energy": 0.05,
            "active_participants_count": 8
        }
        audio_data = {
            "noise_level_spl": 52.0,
            "ambient_noise_level": "MODERATE",
            "rhythm_state": "INSTRUCTOR_MONOLOGUE",
            "signal_classification": "ACTIVE_SPEECH",
            "participation_frequency": 0.5,
            "interaction_intensity": 0.30
        }

        res = agent.evaluate(visual_data, audio_data)
        self.assertEqual(res.rule_triggered, "M1_HIGH_INSTRUCTIONAL_FLOW")
        self.assertEqual(res.engagement_state, "HIGH_FLOW")
        self.assertGreaterEqual(res.confidence, 0.90)
        self.assertGreaterEqual(res.engagement_index, 75.0)
        self.assertIn("optimal cognitive absorption", res.explainable_diagnosis)

    def test_epic4_activity4_1_rule_based_reasoning_visual_distraction(self):
        """
        EPIC 4 Activity 4.1: Rule M2 Passive Visual Disengagement
        Visual attention < 55% in a quiet room (<55 dB SPL) -> M2_PASSIVE_VISUAL_DISENGAGEMENT
        """
        from backend.agent.multimodal_agent import MultimodalAgent
        agent = MultimodalAgent()

        visual_data = {
            "average_visual_attention": 0.40,
            "average_motion_energy": 0.04,
            "active_participants_count": 8
        }
        audio_data = {
            "noise_level_spl": 46.0,
            "ambient_noise_level": "QUIET",
            "rhythm_state": "INSTRUCTOR_MONOLOGUE",
            "signal_classification": "SILENCE",
            "participation_frequency": 0.0,
            "interaction_intensity": 0.0
        }

        res = agent.evaluate(visual_data, audio_data)
        self.assertEqual(res.rule_triggered, "M2_PASSIVE_VISUAL_DISENGAGEMENT")
        self.assertEqual(res.engagement_state, "PASSIVE_DISENGAGEMENT")
        self.assertIn("drifted", res.explainable_diagnosis)

    def test_epic4_activity4_1_rule_based_reasoning_interactive_resonance(self):
        """
        EPIC 4 Activity 4.1: Rule M3 Vibrant Interactive Discussion Resonance
        High turn-taking (>= 1.5 turns/min) + QA rhythm + active gaze -> M3_VIBRANT_INTERACTIVE_RESONANCE
        """
        from backend.agent.multimodal_agent import MultimodalAgent
        agent = MultimodalAgent()

        visual_data = {
            "average_visual_attention": 0.78,
            "average_motion_energy": 0.09,
            "active_participants_count": 8
        }
        audio_data = {
            "noise_level_spl": 62.0,
            "ambient_noise_level": "MODERATE",
            "rhythm_state": "QA_INTERACTION",
            "signal_classification": "ACTIVE_SPEECH",
            "participation_frequency": 2.5,
            "interaction_intensity": 0.60
        }

        res = agent.evaluate(visual_data, audio_data)
        self.assertEqual(res.rule_triggered, "M3_VIBRANT_INTERACTIVE_RESONANCE")
        self.assertEqual(res.engagement_state, "COLLABORATIVE_ACTIVE")
        self.assertGreaterEqual(res.confidence, 0.90)

    def test_epic4_activity4_1_rule_based_reasoning_acoustic_disruption(self):
        """
        EPIC 4 Activity 4.1: Rule M4 Acoustic Chaos & Cross-Talk Disruption
        LOUD_DISRUPTIVE / SPL >= 75 dB SPL + fidgeting -> M4_ACOUSTIC_CHAOS_DISRUPTION
        """
        from backend.agent.multimodal_agent import MultimodalAgent
        agent = MultimodalAgent()

        visual_data = {
            "average_visual_attention": 0.50,
            "average_motion_energy": 0.38,
            "active_participants_count": 8
        }
        audio_data = {
            "noise_level_spl": 78.5,
            "ambient_noise_level": "LOUD_DISRUPTIVE",
            "rhythm_state": "COLLABORATIVE_BUZZ",
            "signal_classification": "BACKGROUND_NOISE",
            "participation_frequency": 0.8,
            "interaction_intensity": 0.40
        }

        res = agent.evaluate(visual_data, audio_data)
        self.assertEqual(res.rule_triggered, "M4_ACOUSTIC_CHAOS_DISRUPTION")
        self.assertEqual(res.engagement_state, "ACOUSTIC_DISRUPTION")
        self.assertGreaterEqual(res.confidence, 0.95)

    def test_epic4_activity4_1_rule_based_reasoning_concept_freeze(self):
        """
        EPIC 4 Activity 4.1: Rule M5 Concept Barrier / Question Freeze
        QA rhythm + silence >= 20s or turn freq < 0.8 + attentive gaze -> M5_QUESTION_CONCEPT_FREEZE
        """
        from backend.agent.multimodal_agent import MultimodalAgent
        agent = MultimodalAgent()

        visual_data = {
            "average_visual_attention": 0.82,
            "average_motion_energy": 0.03,
            "active_participants_count": 8
        }
        audio_data = {
            "noise_level_spl": 48.0,
            "ambient_noise_level": "QUIET",
            "rhythm_state": "QA_INTERACTION",
            "signal_classification": "SILENCE",
            "consecutive_silence_sec": 25.0,
            "participation_frequency": 0.2,
            "interaction_intensity": 0.05
        }

        res = agent.evaluate(visual_data, audio_data)
        self.assertEqual(res.rule_triggered, "M5_QUESTION_CONCEPT_FREEZE")
        self.assertEqual(res.engagement_state, "CONCEPT_HESITATION")
        self.assertIn("hesitation", res.explainable_diagnosis)

    def test_epic4_activity4_1_rule_based_reasoning_monologue_fatigue(self):
        """
        EPIC 4 Activity 4.1: Rule M6 Extended Monologue Fatigue
        Monologue >= 480s (8 min) + restlessness/fidgeting -> M6_EXTENDED_MONOLOGUE_FATIGUE
        """
        from backend.agent.multimodal_agent import MultimodalAgent
        agent = MultimodalAgent()

        visual_data = {
            "average_visual_attention": 0.52,
            "average_motion_energy": 0.48,  # Restless fidgeting
            "active_participants_count": 8
        }
        audio_data = {
            "noise_level_spl": 58.0,
            "ambient_noise_level": "MODERATE",
            "rhythm_state": "INSTRUCTOR_MONOLOGUE",
            "signal_classification": "ACTIVE_SPEECH",
            "consecutive_monologue_sec": 600.0,  # 10 minutes
            "participation_frequency": 0.0,
            "interaction_intensity": 0.70
        }

        res = agent.evaluate(visual_data, audio_data)
        self.assertEqual(res.rule_triggered, "M6_EXTENDED_MONOLOGUE_FATIGUE")
        self.assertEqual(res.engagement_state, "FATIGUE_RESTLESSNESS")
        self.assertIn("monologue", res.explainable_diagnosis.lower())

    def test_epic4_activity4_1_explainable_engagement_estimation(self):
        """
        EPIC 4 Activity 4.1: Contextual and Explainable Engagement Index
        Tests component factor breakdown, attribution percentages, and dominant modality.
        """
        from backend.agent.multimodal_agent import MultimodalAgent
        agent = MultimodalAgent()

        visual_data = {
            "average_visual_attention": 0.80,
            "average_motion_energy": 0.06,
            "active_participants_count": 8
        }
        audio_data = {
            "noise_level_spl": 54.0,
            "ambient_noise_level": "MODERATE",
            "rhythm_state": "INSTRUCTOR_MONOLOGUE",
            "signal_classification": "ACTIVE_SPEECH",
            "participation_frequency": 0.5,
            "interaction_intensity": 0.35
        }

        res = agent.evaluate(visual_data, audio_data)
        self.assertIsInstance(res.engagement_index, float)
        self.assertGreater(res.engagement_index, 0.0)
        self.assertLessEqual(res.engagement_index, 100.0)
        self.assertIn("visual_attention_component", res.factor_breakdown)
        self.assertIn("motion_balance_component", res.factor_breakdown)
        self.assertIn("audio_interaction_component", res.factor_breakdown)
        self.assertIn(res.dominant_modality, ["VISUAL_DOMINANT", "AUDIO_DOMINANT", "BALANCED"])

        # Serialization check
        r_dict = res.to_dict()
        self.assertIn("explainable_diagnosis", r_dict)
        self.assertIn("actionable_insight", r_dict)
        self.assertIn("teaching_recommendation", r_dict)

    def test_epic4_activity4_1_api_endpoints(self):
        """
        EPIC 4 Activity 4.1: REST API Endpoints Verification
        Tests /api/agent/activity_4_1/status, /evaluate, /llm_insight, /reasoning_history, /rules
        """
        from backend.api.server import (
            get_activity_4_1_status,
            evaluate_multimodal_agent_endpoint,
            generate_llm_insight_endpoint,
            get_reasoning_history_endpoint,
            get_multimodal_rules_endpoint
        )

        # 1. Status Endpoint
        status_res = _run_async(get_activity_4_1_status())
        self.assertEqual(status_res["activity_id"], "Activity 4.1")
        self.assertEqual(status_res["status"], "COMPLETED & VERIFIED")
        self.assertIn("weights", status_res)
        self.assertIn("llm_engine", status_res)

        # 2. Evaluate Endpoint
        eval_res = _run_async(evaluate_multimodal_agent_endpoint({
            "visual_data": {
                "average_visual_attention": 0.88,
                "average_motion_energy": 0.05,
                "active_participants_count": 8
            },
            "audio_data": {
                "noise_level_spl": 52.0,
                "ambient_noise_level": "MODERATE",
                "rhythm_state": "INSTRUCTOR_MONOLOGUE",
                "signal_classification": "ACTIVE_SPEECH",
                "participation_frequency": 1.0,
                "interaction_intensity": 0.40
            }
        }))
        self.assertEqual(eval_res["status"], "SUCCESS")
        self.assertIn("result", eval_res)
        self.assertEqual(eval_res["result"]["engagement_state"], "HIGH_FLOW")

        # 3. LLM Insight Endpoint
        insight_res = _run_async(generate_llm_insight_endpoint())
        self.assertEqual(insight_res["status"], "SUCCESS")
        self.assertIn("insight_result", insight_res)
        self.assertIn("insight", insight_res["insight_result"])
        self.assertIn("recommendation", insight_res["insight_result"])

        # 4. Reasoning History Endpoint
        history_res = _run_async(get_reasoning_history_endpoint(limit=10))
        self.assertEqual(history_res["status"], "SUCCESS")
        self.assertIn("history", history_res)

        # 5. Rules Catalog Endpoint
        rules_res = _run_async(get_multimodal_rules_endpoint())
        self.assertIn("rules", rules_res)
        self.assertEqual(len(rules_res["rules"]), 6)

    # -------------------------------------------------------------
    # EPIC 4: Activity 4.2 Multimodal Signal Fusion Tests
    # -------------------------------------------------------------

    def test_epic4_activity4_2_ai_suggestion_engine(self):
        """
        EPIC 4 Activity 4.2: AI Suggestion Engine (Reference image: backend/core/ai_suggestions.py)
        Tests prompt formatting, deterministic fallback suggestions, and response parser.
        """
        from backend.core.ai_suggestions import AISuggestionEngine
        engine = AISuggestionEngine(api_key="mock_key_test")

        # 1. Test build_prompt format
        session_data = {
            "presence_duration_seconds": 450.0,
            "movement_pattern": "FOCUSED_STABLE",
            "average_motion_energy": 0.045,
            "inactivity_seconds": 15.0,
            "average_visual_attention": 0.82,
            "noise_level_spl": 54.0,
            "ambient_noise_level": "MODERATE",
            "signal_classification": "ACTIVE_SPEECH",
            "rhythm_state": "QA_INTERACTION",
            "participation_frequency": 2.5,
            "engagement_index": 84.0
        }
        prompt = engine.build_prompt(session_data)
        self.assertIn("[Visual Modality]", prompt)
        self.assertIn("Visual Focus / Board Gaze: 82.0%", prompt)
        self.assertIn("Cumulative Presence Duration: 450s", prompt)
        self.assertIn("FOCUSED_STABLE", prompt)
        self.assertIn("[Audio Modality]", prompt)
        self.assertIn("54.0 dB SPL", prompt)
        self.assertIn("QA_INTERACTION", prompt)
        self.assertIn("2.5 turns/min", prompt)
        self.assertIn("Fused Engagement Index: 84.0%", prompt)

        # 2. Test _fallback_suggestions (offline edge resilience)
        # Case A: Loud room acoustic reset
        loud_data = dict(session_data, ambient_noise_level="LOUD_DISRUPTIVE", noise_level_spl=78.0)
        sug_loud = engine._fallback_suggestions(loud_data)
        self.assertTrue(len(sug_loud) > 0)
        self.assertIn("Room Acoustic Reset", sug_loud[0]["title"])

        # Case B: Q&A concept hesitation
        qa_freeze = dict(session_data, rhythm_state="QA_INTERACTION", participation_frequency=0.2, average_visual_attention=0.85)
        sug_qa = engine._fallback_suggestions(qa_freeze)
        self.assertIn("Scaffolding", sug_qa[0]["title"])

        # Case C: Wandering gaze in quiet room
        drift_data = dict(session_data, average_visual_attention=0.45, noise_level_spl=48.0)
        sug_drift = engine._fallback_suggestions(drift_data)
        self.assertIn("Visual Re-Engagement", sug_drift[0]["title"])

        # Case D: Physical stillness / dormancy
        dormant_data = dict(session_data, inactivity_seconds=120.0, average_motion_energy=0.01)
        sug_dormant = engine._fallback_suggestions(dormant_data)
        self.assertIn("Physical Alertness", sug_dormant[0]["title"])

        # Case E: High restlessness
        restless_data = dict(session_data, average_motion_energy=0.55, average_visual_attention=0.50)
        sug_restless = engine._fallback_suggestions(restless_data)
        self.assertIn("Restlessness", sug_restless[0]["title"])

        # Case F: Balanced flow
        flow_data = dict(session_data, engagement_index=85.0, average_visual_attention=0.80, noise_level_spl=55.0)
        sug_flow = engine._fallback_suggestions(flow_data)
        self.assertIn("Flow", sug_flow[0]["title"])

        # 3. Test _parse_response
        sample_llm_output = (
            "TITLE: Scaffolding Pause\n"
            "ACTION: Ask a check question to table 3.\n"
            "RATIONALE: High visual focus with quiet acoustic space."
        )
        parsed = engine._parse_response(sample_llm_output)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["title"], "Scaffolding Pause")
        self.assertEqual(parsed[0]["action"], "Ask a check question to table 3.")
        self.assertEqual(parsed[0]["rationale"], "High visual focus with quiet acoustic space.")

        # 4. Generate suggestions fallback call (without valid Groq token)
        fallback_res = engine.generate_suggestions(session_data)
        self.assertIsInstance(fallback_res, list)
        self.assertGreater(len(fallback_res), 0)

    def test_epic4_activity4_2_timestamp_synchronization_and_jitter(self):
        """
        EPIC 4 Activity 4.2: Timestamp-Based Synchronization
        Verifies timestamp synchronization, sub-frame alignment, and jitter calculation.
        """
        from backend.fusion.multimodal_fusion import MultimodalFusionEngine
        fusion = MultimodalFusionEngine()

        t_base = time.time()
        # Simulated visual packet timestamped at t_base
        vis_packet = {
            "timestamp": t_base,
            "average_visual_attention": 0.85,
            "average_motion_energy": 0.05,
            "presence_duration_seconds": 600.0,
            "presence_ratio_percent": 90.0,
            "inactivity_seconds": 10.0,
            "active_participants_count": 8
        }
        # Simulated audio packet with 3.2 ms sync offset
        aud_packet = {
            "timestamp": t_base + 0.0032,
            "noise_level_spl": 55.0,
            "noise_level_db": -30.0,
            "ambient_noise_level": "MODERATE",
            "ambient_noise_trend": "STABLE",
            "speech_state": "ACTIVE_SPEECH",
            "rhythm_state": "INSTRUCTOR_MONOLOGUE",
            "participation_frequency": 1.0,
            "interaction_intensity": 0.40
        }

        unified = fusion.synchronize_and_fuse(vis_packet, aud_packet, session_id="TEST-SES-01")
        self.assertAlmostEqual(unified.sync_jitter_ms, 3.2, delta=0.1)
        self.assertEqual(unified.session_id, "TEST-SES-01")
        self.assertEqual(unified.epoch_id, 1)

    def test_epic4_activity4_2_visual_audio_indicator_alignment(self):
        """
        EPIC 4 Activity 4.2: Multi-Signal Alignment & Classification
        Verifies alignment of visual indicators (presence duration, movement patterns,
        inactivity periods) with audio indicators (noise levels, speech activity).
        """
        from backend.fusion.multimodal_fusion import MultimodalFusionEngine
        fusion = MultimodalFusionEngine()

        # Test movement pattern classification:
        # 1. Dormant
        u_dormant = fusion.synchronize_and_fuse(
            {"average_motion_energy": 0.01, "inactivity_seconds": 100.0, "average_visual_attention": 0.80},
            {"noise_level_spl": 50.0, "speech_state": "SILENCE"}
        )
        self.assertEqual(u_dormant.movement_pattern, "STATIC_DORMANT")
        self.assertEqual(u_dormant.inactivity_seconds, 100.0)

        # 2. Restless
        u_restless = fusion.synchronize_and_fuse(
            {"average_motion_energy": 0.50, "inactivity_seconds": 0.0, "average_visual_attention": 0.50},
            {"noise_level_spl": 72.0, "speech_state": "BACKGROUND_NOISE"}
        )
        self.assertEqual(u_restless.movement_pattern, "RESTLESS_JITTER")

        # 3. Focused Stable
        u_focused = fusion.synchronize_and_fuse(
            {"average_motion_energy": 0.08, "inactivity_seconds": 5.0, "average_visual_attention": 0.88},
            {"noise_level_spl": 55.0, "speech_state": "ACTIVE_SPEECH", "rhythm_state": "INSTRUCTOR_MONOLOGUE"}
        )
        self.assertEqual(u_focused.movement_pattern, "FOCUSED_STABLE")
        self.assertEqual(u_focused.speech_state, "ACTIVE_SPEECH")
        self.assertEqual(u_focused.rhythm_state, "INSTRUCTOR_MONOLOGUE")

    def test_epic4_activity4_2_proportional_multimodal_contributions(self):
        """
        EPIC 4 Activity 4.2: Proportional Multimodal Contribution
        Verifies that visual attention, motion balance, and acoustic dynamics contribute
        proportionally to composite engagement estimation.
        """
        from backend.fusion.multimodal_fusion import MultimodalFusionEngine
        fusion = MultimodalFusionEngine(weight_visual=0.50, weight_motion=0.20, weight_audio=0.30)

        vis_data = {
            "average_visual_attention": 0.80,
            "average_motion_energy": 0.05,
            "presence_duration_seconds": 300.0
        }
        aud_data = {
            "noise_level_spl": 54.0,
            "ambient_noise_level": "MODERATE",
            "rhythm_state": "INSTRUCTOR_MONOLOGUE",
            "speech_state": "ACTIVE_SPEECH"
        }

        unified = fusion.synchronize_and_fuse(vis_data, aud_data)
        # Visual contrib: 0.50 * 0.80 * 100 = 40.0
        self.assertAlmostEqual(unified.visual_contribution, 40.0, delta=0.5)
        # Motion contrib: 0.20 * 0.95 * 100 = 19.0
        self.assertAlmostEqual(unified.motion_contribution, 19.0, delta=0.5)
        # Audio contrib: 0.30 * 0.85 * 100 = 25.5
        self.assertAlmostEqual(unified.audio_contribution, 25.5, delta=0.5)
        # Composite EI: ~84.5
        self.assertAlmostEqual(unified.composite_engagement_index, 84.5, delta=1.0)
        self.assertIn(unified.dominant_modality, ["VISUAL_DOMINANT", "AUDIO_DOMINANT", "BALANCED"])

    def test_epic4_activity4_2_cross_modal_correlation_and_coherence(self):
        """
        EPIC 4 Activity 4.2: Cross-Modal Correlation & Coherence Analysis
        Verifies rolling Pearson correlation between modalities and instructional coherence.
        """
        from backend.fusion.multimodal_fusion import MultimodalFusionEngine
        fusion = MultimodalFusionEngine()

        # Simulate 10 synchronized epochs of harmonious interactive teaching
        for i in range(10):
            vis = {"average_visual_attention": 0.70 + (i * 0.02), "average_motion_energy": 0.05}
            aud = {
                "noise_level_spl": 58.0 + (i * 0.5),
                "rhythm_state": "QA_INTERACTION",
                "participation_frequency": 1.0 + (i * 0.2),
                "interaction_intensity": 0.40 + (i * 0.03)
            }
            u = fusion.synchronize_and_fuse(vis, aud)

        self.assertIsInstance(u.cross_modal_correlation, float)
        self.assertGreaterEqual(u.cross_modal_correlation, -1.0)
        self.assertLessEqual(u.cross_modal_correlation, 1.0)
        self.assertGreater(u.cross_modal_coherence, 0.70, "Active interactive Q&A should yield high coherence.")

    def test_epic4_activity4_2_extensible_architecture(self):
        """
        EPIC 4 Activity 4.2: Extensible Architecture for Future Modalities
        Verifies that additional sensory modalities (e.g., smart pen, physiological wristband)
        can be registered without breaking existing telemetry schemas.
        """
        from backend.fusion.multimodal_fusion import MultimodalFusionEngine
        fusion = MultimodalFusionEngine()

        vis = {"average_visual_attention": 0.85, "average_motion_energy": 0.04}
        aud = {"noise_level_spl": 52.0, "rhythm_state": "INSTRUCTOR_MONOLOGUE"}

        # 1. Fuse with initial custom modality
        initial_ext = {"smart_whiteboard": {"pen_strokes": 42, "board_active": True}}
        unified = fusion.synchronize_and_fuse(vis, aud, custom_modalities=initial_ext)
        self.assertIn("smart_whiteboard", unified.custom_modalities)

        # 2. Add second custom modality at runtime
        unified.add_custom_modality("wearable_eda", {"skin_conductance_microsiemens": 2.4, "stress_index": 0.15})
        self.assertIn("wearable_eda", unified.custom_modalities)

        # 3. Serialization verification
        d = unified.to_dict()
        self.assertIn("custom_modalities", d)
        self.assertIn("smart_whiteboard", d["custom_modalities"])
        self.assertIn("wearable_eda", d["custom_modalities"])

    def test_epic4_activity4_2_api_endpoints(self):
        """
        EPIC 4 Activity 4.2: REST API Endpoints Verification
        Tests /api/fusion/activity_4_2/status, /synchronize, /generate_ai_suggestions,
        /unified_representation, /cross_modal_correlation, /add_modality
        """
        from backend.api.server import (
            get_activity_4_2_status,
            synchronize_multimodal_signals_endpoint,
            generate_ai_suggestions_endpoint,
            get_unified_representation_endpoint,
            get_cross_modal_correlation_endpoint,
            add_custom_modality_endpoint
        )

        # 1. Status Endpoint
        status_res = _run_async(get_activity_4_2_status())
        self.assertEqual(status_res["activity_id"], "Activity 4.2")
        self.assertEqual(status_res["status"], "COMPLETED & VERIFIED")
        self.assertIn("synchronization", status_res)
        self.assertIn("cross_modal", status_res)
        self.assertIn("ai_suggestion_engine", status_res)

        # 2. Synchronize Endpoint
        sync_res = _run_async(synchronize_multimodal_signals_endpoint({
            "visual_data": {
                "timestamp": time.time(),
                "average_visual_attention": 0.85,
                "average_motion_energy": 0.05,
                "presence_duration_seconds": 400.0,
                "presence_ratio_percent": 92.0,
                "inactivity_seconds": 15.0,
                "active_participants_count": 8
            },
            "audio_data": {
                "timestamp": time.time(),
                "noise_level_spl": 54.0,
                "noise_level_db": -28.0,
                "ambient_noise_level": "MODERATE",
                "ambient_noise_trend": "STABLE",
                "speech_state": "ACTIVE_SPEECH",
                "rhythm_state": "INSTRUCTOR_MONOLOGUE",
                "participation_frequency": 1.0,
                "interaction_intensity": 0.40,
                "speaker_turns": 5
            }
        }))
        self.assertEqual(sync_res["status"], "SUCCESS")
        self.assertIn("unified_representation", sync_res)
        self.assertEqual(sync_res["unified_representation"]["movement_pattern"], "FOCUSED_STABLE")

        # 3. Generate AI Suggestions Endpoint
        sug_res = _run_async(generate_ai_suggestions_endpoint())
        self.assertEqual(sug_res["status"], "SUCCESS")
        self.assertIn("suggestions", sug_res)
        self.assertEqual(sug_res["model"], "llama-3.3-70b-versatile")

        # 4. Unified Representation Endpoint
        rep_res = _run_async(get_unified_representation_endpoint())
        self.assertEqual(rep_res["status"], "SUCCESS")
        self.assertIn("unified_representation", rep_res)

        # 5. Cross-Modal Correlation Endpoint
        corr_res = _run_async(get_cross_modal_correlation_endpoint())
        self.assertEqual(corr_res["status"], "SUCCESS")
        self.assertIn("cross_modal_correlation", corr_res)
        self.assertIn("cross_modal_coherence", corr_res)
        self.assertIn("dominant_modality", corr_res)

        # 6. Add Custom Modality Extensibility Endpoint
        ext_res = _run_async(add_custom_modality_endpoint({
            "modality_name": "student_clicker_poll",
            "data": {"question_id": "Q4", "active_responses": 8, "accuracy_pct": 87.5}
        }))
        self.assertEqual(ext_res["status"], "SUCCESS")
        self.assertEqual(ext_res["modality_registered"], "student_clicker_poll")

    # =========================================================================
    # EPIC 4: AI IMPLEMENTATION - ACTIVITY 4.3: ENGAGEMENT SCORING LOGIC TESTS
    # =========================================================================

    def test_epic4_activity4_3_rule_based_scoring_logic(self):
        """
        EPIC 4 Activity 4.3: Rule-Based Scoring Logic Verification
        Validates individual factor calculations for sustained visual presence,
        movement frequency, inactivity duration penalty, and speech activity intensity,
        as well as composite weighted combination and explainable attribution.
        """
        from backend.core.engagement_scoring import EngagementScoringEngine, ScoringThresholdConfig

        engine = EngagementScoringEngine()

        # 1. Optimal engaged classroom segment
        vis_opt = {
            "average_visual_attention": 0.85,
            "average_motion_energy": 0.08,
            "presence_duration_seconds": 600.0,
            "presence_ratio_percent": 95.0,
            "inactivity_seconds": 10.0
        }
        aud_opt = {
            "noise_level_spl": 56.0,
            "speech_state": "ACTIVE_SPEECH",
            "rhythm_state": "INSTRUCTOR_MONOLOGUE",
            "participation_frequency": 1.0
        }

        score_opt = engine.score_segment(vis_opt, aud_opt, start_time=100.0, duration_seconds=10.0)
        self.assertGreaterEqual(score_opt.composite_score, 75.0)
        self.assertEqual(score_opt.engagement_level, "HIGH")
        self.assertGreaterEqual(score_opt.visual_presence_score, 80.0)
        self.assertGreaterEqual(score_opt.movement_frequency_score, 85.0)
        self.assertEqual(score_opt.inactivity_score, 100.0)  # No dormancy penalty
        self.assertGreaterEqual(score_opt.speech_intensity_score, 80.0)

        # Factor attribution verification
        attr = score_opt.factor_attribution
        total_attr = (
            attr.visual_presence_contribution +
            attr.movement_frequency_contribution +
            attr.inactivity_contribution +
            attr.speech_intensity_contribution
        )
        self.assertAlmostEqual(score_opt.composite_score, total_attr, delta=0.2)
        self.assertIn("Visual Presence", attr.dominant_driver)

        # 2. Critical dormant segment (high inactivity, zero speech, wandering gaze)
        vis_dormant = {
            "average_visual_attention": 0.25,
            "average_motion_energy": 0.005,
            "presence_duration_seconds": 120.0,
            "presence_ratio_percent": 30.0,
            "inactivity_seconds": 110.0  # Exceeds critical 90s threshold
        }
        aud_dormant = {
            "noise_level_spl": 78.0,  # Disruptive room noise
            "speech_state": "SILENCE",
            "rhythm_state": "INSTRUCTOR_MONOLOGUE",
            "participation_frequency": 0.0
        }

        score_dormant = engine.score_segment(vis_dormant, aud_dormant, start_time=110.0, duration_seconds=10.0)
        self.assertLess(score_dormant.composite_score, 45.0)
        self.assertIn(score_dormant.engagement_level, ["LOW", "CRITICAL_DISENGAGED"])
        self.assertLess(score_dormant.inactivity_score, 25.0)  # Severe dormancy penalty
        self.assertEqual(score_dormant.speech_intensity_score, 30.0)  # Noise disruption penalty
        self.assertIsNotNone(score_dormant.factor_attribution.dominant_penalty)

    def test_epic4_activity4_3_predefined_and_adjustable_thresholds(self):
        """
        EPIC 4 Activity 4.3: Predefined Thresholds & Dynamic Fine-Tuning
        Validates predefined classroom presets (LECTURE_STANDARD, INTERACTIVE_DISCUSSION,
        HANDS_ON_LAB, QUIET_EXAM) and dynamic threshold updates with automatic weight normalization.
        """
        from backend.core.engagement_scoring import ScoringThresholdConfig, ClassroomPreset

        cfg = ScoringThresholdConfig()

        # 1. Default LECTURE_STANDARD preset
        self.assertEqual(cfg.preset_name, ClassroomPreset.LECTURE_STANDARD)
        total_w = cfg.weight_visual + cfg.weight_movement + cfg.weight_inactivity + cfg.weight_speech
        self.assertAlmostEqual(total_w, 1.0, places=3)

        # 2. Apply INTERACTIVE_DISCUSSION preset
        cfg.apply_preset(ClassroomPreset.INTERACTIVE_DISCUSSION)
        self.assertEqual(cfg.preset_name, ClassroomPreset.INTERACTIVE_DISCUSSION)
        self.assertGreater(cfg.weight_speech, 0.40)  # High speech weight in discussion
        total_w = cfg.weight_visual + cfg.weight_movement + cfg.weight_inactivity + cfg.weight_speech
        self.assertAlmostEqual(total_w, 1.0, places=3)

        # 3. Apply HANDS_ON_LAB preset
        cfg.apply_preset(ClassroomPreset.HANDS_ON_LAB)
        self.assertEqual(cfg.preset_name, ClassroomPreset.HANDS_ON_LAB)
        self.assertGreater(cfg.weight_movement, 0.30)  # Higher movement tolerance in lab

        # 4. Apply QUIET_EXAM preset
        cfg.apply_preset(ClassroomPreset.QUIET_EXAM)
        self.assertEqual(cfg.preset_name, ClassroomPreset.QUIET_EXAM)
        self.assertLessEqual(cfg.noise_disruptive_spl, 60.0)  # Low tolerance for noise

        # 5. Dynamic Custom Update & Auto-Normalization
        cfg.update_thresholds({
            "weight_visual": 0.50,
            "weight_movement": 0.50,
            "weight_inactivity": 0.50,
            "weight_speech": 0.50
        })
        self.assertEqual(cfg.preset_name, ClassroomPreset.CUSTOM)
        # Weights should automatically normalize from 2.0 down to 1.0 (each 0.25)
        self.assertAlmostEqual(cfg.weight_visual, 0.25, places=2)
        self.assertAlmostEqual(cfg.weight_movement, 0.25, places=2)
        total_w = cfg.weight_visual + cfg.weight_movement + cfg.weight_inactivity + cfg.weight_speech
        self.assertAlmostEqual(total_w, 1.0, places=3)

    def test_epic4_activity4_3_temporal_profile_generation(self):
        """
        EPIC 4 Activity 4.3: Temporal Engagement Profile Generation
        Validates generating a temporal engagement profile over regular time segments
        rather than a single aggregated value.
        """
        import time
        from backend.core.engagement_scoring import EngagementScoringEngine

        engine = EngagementScoringEngine()

        # Create 8 sequential interval packets (10s each)
        now = time.time()
        packets = []
        for i in range(8):
            packets.append({
                "timestamp": now + (i * 10.0),
                "visual_data": {
                    "average_visual_attention": 0.70 + (0.03 * i),
                    "average_motion_energy": 0.05,
                    "presence_duration_seconds": 60.0 * (i + 1),
                    "presence_ratio_percent": 90.0,
                    "inactivity_seconds": 12.0
                },
                "audio_data": {
                    "noise_level_spl": 54.0,
                    "speech_state": "ACTIVE_SPEECH",
                    "rhythm_state": "INSTRUCTOR_MONOLOGUE",
                    "participation_frequency": 1.0
                }
            })

        profile = engine.generate_temporal_profile(packets, interval_seconds=10.0, session_id="TEST_SES_01")
        self.assertEqual(profile.total_segments, 8)
        self.assertEqual(len(profile.segments), 8)
        self.assertEqual(profile.interval_seconds, 10.0)
        self.assertEqual(profile.session_id, "TEST_SES_01")
        self.assertGreaterEqual(profile.mean_score, 70.0)
        self.assertGreaterEqual(profile.max_score, profile.min_score)

        # Confirm sequential segment numbering and timestamps
        for idx, seg in enumerate(profile.segments):
            self.assertEqual(seg.segment_id, idx + 1)
            self.assertEqual(seg.duration_seconds, 10.0)
            self.assertGreater(seg.composite_score, 0.0)

    def test_epic4_activity4_3_attention_fluctuations_detection(self):
        """
        EPIC 4 Activity 4.3: Attention Fluctuations & Stability Analysis
        Validates calculating rolling variance, standard deviation, fluctuation index,
        and stability rating across steady vs. volatile attention profiles.
        """
        from backend.core.engagement_scoring import EngagementScoringEngine

        engine = EngagementScoringEngine()

        # 1. Steady engaged profile -> High stability score, low fluctuation index
        steady_packets = [
            {
                "visual_data": {"average_visual_attention": 0.80, "average_motion_energy": 0.05, "presence_duration_seconds": 200, "inactivity_seconds": 10},
                "audio_data": {"noise_level_spl": 55.0, "speech_state": "ACTIVE_SPEECH", "rhythm_state": "INSTRUCTOR_MONOLOGUE"}
            }
            for _ in range(6)
        ]
        steady_profile = engine.generate_temporal_profile(steady_packets, interval_seconds=10.0)
        fluc_steady = steady_profile.fluctuation_metrics
        self.assertLess(fluc_steady.fluctuation_index, 0.05)
        self.assertGreaterEqual(fluc_steady.stability_score, 95.0)
        self.assertEqual(fluc_steady.attention_drops_count, 0)

        # 2. Volatile swinging profile -> Low stability score, elevated fluctuation index
        engine2 = EngagementScoringEngine()
        volatile_packets = []
        for i in range(6):
            if i % 2 == 0:
                # High engagement peak
                volatile_packets.append({
                    "visual_data": {"average_visual_attention": 0.95, "average_motion_energy": 0.08, "presence_duration_seconds": 300, "inactivity_seconds": 5},
                    "audio_data": {"noise_level_spl": 55.0, "speech_state": "ACTIVE_SPEECH", "rhythm_state": "INSTRUCTOR_MONOLOGUE"}
                })
            else:
                # Severe disengagement dip
                volatile_packets.append({
                    "visual_data": {"average_visual_attention": 0.20, "average_motion_energy": 0.005, "presence_duration_seconds": 100, "inactivity_seconds": 95},
                    "audio_data": {"noise_level_spl": 80.0, "speech_state": "SILENCE", "rhythm_state": "INSTRUCTOR_MONOLOGUE"}
                })
        volatile_profile = engine2.generate_temporal_profile(volatile_packets, interval_seconds=10.0)
        fluc_vol = volatile_profile.fluctuation_metrics
        self.assertGreater(fluc_vol.fluctuation_index, 0.20)
        self.assertLess(fluc_vol.stability_score, 80.0)
        self.assertGreater(fluc_vol.rate_of_change_max, 25.0)
        self.assertGreaterEqual(fluc_vol.attention_drops_count, 1)

    def test_epic4_activity4_3_peak_engagement_periods_detection(self):
        """
        EPIC 4 Activity 4.3: Peak Engagement Periods Detection
        Validates identifying contiguous intervals of high flow exceeding the peak threshold (>=80%).
        """
        from backend.core.engagement_scoring import EngagementScoringEngine

        engine = EngagementScoringEngine()
        packets = []

        # Segments 1-2: Normal engagement (~70%)
        for _ in range(2):
            packets.append({
                "visual_data": {"average_visual_attention": 0.68, "average_motion_energy": 0.06, "presence_duration_seconds": 100, "inactivity_seconds": 15},
                "audio_data": {"noise_level_spl": 55.0, "speech_state": "ACTIVE_SPEECH", "rhythm_state": "INSTRUCTOR_MONOLOGUE"}
            })

        # Segments 3-5: Sustained Peak Flow (>82%)
        for _ in range(3):
            packets.append({
                "visual_data": {"average_visual_attention": 0.95, "average_motion_energy": 0.08, "presence_duration_seconds": 300, "presence_ratio_percent": 98.0, "inactivity_seconds": 5},
                "audio_data": {"noise_level_spl": 58.0, "speech_state": "ACTIVE_SPEECH", "rhythm_state": "QA_INTERACTION", "participation_frequency": 2.0}
            })

        # Segments 6-7: Normal engagement (~70%)
        for _ in range(2):
            packets.append({
                "visual_data": {"average_visual_attention": 0.65, "average_motion_energy": 0.06, "presence_duration_seconds": 500, "inactivity_seconds": 20},
                "audio_data": {"noise_level_spl": 55.0, "speech_state": "ACTIVE_SPEECH", "rhythm_state": "INSTRUCTOR_MONOLOGUE"}
            })

        profile = engine.generate_temporal_profile(packets, interval_seconds=10.0)
        self.assertGreaterEqual(len(profile.peak_periods), 1)

        peak = profile.peak_periods[0]
        self.assertEqual(peak.peak_id, 1)
        self.assertGreaterEqual(peak.duration_seconds, 25.0)
        self.assertGreaterEqual(peak.peak_score, 80.0)
        self.assertIn("Visual Presence", peak.dominant_drivers)

    def test_epic4_activity4_3_extended_disengagement_phases_detection(self):
        """
        EPIC 4 Activity 4.3: Extended Disengagement Phases Detection
        Validates identifying persistent drop-offs (<50%) lasting >=3 consecutive segments.
        """
        from backend.core.engagement_scoring import EngagementScoringEngine

        engine = EngagementScoringEngine()
        packets = []

        # Segments 1-2: Normal engagement
        for _ in range(2):
            packets.append({
                "visual_data": {"average_visual_attention": 0.75, "average_motion_energy": 0.05, "presence_duration_seconds": 150, "inactivity_seconds": 15},
                "audio_data": {"noise_level_spl": 55.0, "speech_state": "ACTIVE_SPEECH", "rhythm_state": "INSTRUCTOR_MONOLOGUE"}
            })

        # Segments 3-6: Consecutive extended disengagement (4 segments, severe inactivity)
        for _ in range(4):
            packets.append({
                "visual_data": {"average_visual_attention": 0.25, "average_motion_energy": 0.005, "presence_duration_seconds": 50, "presence_ratio_percent": 25.0, "inactivity_seconds": 105},
                "audio_data": {"noise_level_spl": 78.0, "speech_state": "SILENCE", "rhythm_state": "INSTRUCTOR_MONOLOGUE"}
            })

        # Segment 7: Recovery
        packets.append({
            "visual_data": {"average_visual_attention": 0.80, "average_motion_energy": 0.05, "presence_duration_seconds": 250, "inactivity_seconds": 10},
            "audio_data": {"noise_level_spl": 55.0, "speech_state": "ACTIVE_SPEECH", "rhythm_state": "INSTRUCTOR_MONOLOGUE"}
        })

        profile = engine.generate_temporal_profile(packets, interval_seconds=10.0)
        self.assertGreaterEqual(len(profile.disengagement_phases), 1)

        phase = profile.disengagement_phases[0]
        self.assertEqual(phase.phase_id, 1)
        self.assertGreaterEqual(phase.duration_seconds, 30.0)
        self.assertLess(phase.average_score, 50.0)
        self.assertIn(phase.primary_cause, ["Prolonged Inactivity", "Visual Wander", "Acoustic Disruption/Silence"])
        self.assertTrue(len(phase.suggested_action) > 10)

    def test_epic4_activity4_3_downstream_integration_and_analytics(self):
        """
        EPIC 4 Activity 4.3: Downstream Consumers Verification
        Validates generating teaching suggestions, student analytics profiles,
        and session summaries directly from computed engagement scores.
        """
        from backend.core.engagement_scoring import EngagementScoringEngine

        engine = EngagementScoringEngine()

        # 1. Downstream Teaching Suggestions
        packets = [
            {
                "visual_data": {"average_visual_attention": 0.25, "average_motion_energy": 0.005, "presence_duration_seconds": 50, "presence_ratio_percent": 20.0, "inactivity_seconds": 100},
                "audio_data": {"noise_level_spl": 78.0, "speech_state": "SILENCE", "rhythm_state": "INSTRUCTOR_MONOLOGUE"}
            }
            for _ in range(4)
        ]
        profile = engine.generate_temporal_profile(packets, interval_seconds=10.0)
        suggestions = engine.generate_downstream_teaching_suggestions(profile)
        self.assertGreaterEqual(len(suggestions), 1)
        self.assertIn("Disengagement Phase", suggestions[0]["title"])
        self.assertIn("action", suggestions[0])

        # 2. Downstream Student Analytics
        students_data = [
            {
                "student_id": "STU-01",
                "display_name": "Alice Cooper",
                "visual_data": {"average_visual_attention": 0.90, "average_motion_energy": 0.06, "inactivity_seconds": 5, "presence_ratio_percent": 98.0},
                "audio_data": {"noise_level_spl": 55.0, "speech_state": "ACTIVE_SPEECH", "rhythm_state": "INSTRUCTOR_MONOLOGUE"}
            },
            {
                "student_id": "STU-02",
                "display_name": "Bob Vance",
                "visual_data": {"average_visual_attention": 0.20, "average_motion_energy": 0.005, "inactivity_seconds": 110, "presence_ratio_percent": 25.0},
                "audio_data": {"noise_level_spl": 78.0, "speech_state": "SILENCE", "rhythm_state": "INSTRUCTOR_MONOLOGUE"}
            }
        ]
        student_analytics = engine.generate_student_analytics(students_data)
        self.assertEqual(student_analytics["total_students"], 2)
        p1 = student_analytics["profiles"][0]
        p2 = student_analytics["profiles"][1]
        self.assertEqual(p1["participation_quadrant"], "HIGHLY_ENGAGED")
        self.assertEqual(p2["participation_quadrant"], "AT_RISK_DISENGAGED")

        # 3. Downstream Session Summary
        summary = engine.generate_session_summary(profile)
        self.assertEqual(summary["total_segments"], 4)
        self.assertIn("mean_engagement_index", summary)
        self.assertIn("distribution", summary)
        self.assertIn("pedagogical_takeaway", summary)

    def test_epic4_activity4_3_api_endpoints(self):
        """
        EPIC 4 Activity 4.3: REST API Endpoints Verification
        Tests all 9 Activity 4.3 REST API endpoints asynchronously.
        """
        from backend.api.server import (
            get_activity_4_3_status,
            score_engagement_segment_endpoint,
            generate_temporal_profile_endpoint,
            get_current_temporal_profile_endpoint,
            get_threshold_config_endpoint,
            update_thresholds_endpoint,
            apply_preset_endpoint,
            get_peaks_and_disengagements_endpoint,
            downstream_summary_endpoint,
            export_engagement_scoring_json
        )

        # 1. Status Endpoint
        status_res = _run_async(get_activity_4_3_status())
        self.assertEqual(status_res["activity_id"], "Activity 4.3")
        self.assertEqual(status_res["status"], "COMPLETED & VERIFIED")
        self.assertIn("threshold_config", status_res)

        # 2. Score Segment Endpoint
        seg_res = _run_async(score_engagement_segment_endpoint({
            "visual_data": {"average_visual_attention": 0.85, "average_motion_energy": 0.05, "presence_duration_seconds": 300, "inactivity_seconds": 10},
            "audio_data": {"noise_level_spl": 55.0, "speech_state": "ACTIVE_SPEECH", "rhythm_state": "INSTRUCTOR_MONOLOGUE"},
            "duration_seconds": 10.0
        }))
        self.assertEqual(seg_res["status"], "SUCCESS")
        self.assertIn("segment_score", seg_res)
        self.assertGreaterEqual(seg_res["segment_score"]["composite_score"], 70.0)

        # 3. Generate Temporal Profile Endpoint
        prof_res = _run_async(generate_temporal_profile_endpoint({
            "time_series_packets": [
                {
                    "visual_data": {"average_visual_attention": 0.80, "average_motion_energy": 0.05, "presence_duration_seconds": 100, "inactivity_seconds": 10},
                    "audio_data": {"noise_level_spl": 55.0, "speech_state": "ACTIVE_SPEECH", "rhythm_state": "INSTRUCTOR_MONOLOGUE"}
                }
                for _ in range(5)
            ],
            "interval_seconds": 10.0
        }))
        self.assertEqual(prof_res["status"], "SUCCESS")
        self.assertEqual(prof_res["profile"]["total_segments"], 5)

        # 4. Get Current Temporal Profile Endpoint
        curr_prof = _run_async(get_current_temporal_profile_endpoint())
        self.assertEqual(curr_prof["status"], "SUCCESS")
        self.assertIn("profile", curr_prof)

        # 5. Threshold Config Endpoint
        cfg_res = _run_async(get_threshold_config_endpoint())
        self.assertEqual(cfg_res["status"], "SUCCESS")
        self.assertIn("weight_visual", cfg_res["config"])

        # 6. Update Thresholds Endpoint
        upd_res = _run_async(update_thresholds_endpoint({"weight_visual": 0.40, "weight_speech": 0.30}))
        self.assertEqual(upd_res["status"], "SUCCESS")

        # 7. Apply Preset Endpoint
        preset_res = _run_async(apply_preset_endpoint("INTERACTIVE_DISCUSSION"))
        self.assertEqual(preset_res["status"], "SUCCESS")
        self.assertEqual(preset_res["preset_applied"], "INTERACTIVE_DISCUSSION")

        # 8. Peaks & Disengagements Endpoint
        pd_res = _run_async(get_peaks_and_disengagements_endpoint())
        self.assertEqual(pd_res["status"], "SUCCESS")
        self.assertIn("peak_engagement_periods", pd_res)
        self.assertIn("extended_disengagement_phases", pd_res)

        # 9. Downstream Summary Endpoint
        down_res = _run_async(downstream_summary_endpoint())
        self.assertEqual(down_res["status"], "SUCCESS")
        self.assertIn("teaching_suggestions", down_res)
        self.assertIn("student_analytics", down_res)
        self.assertIn("session_summary", down_res)

        # 10. Export JSON Endpoint
        export_res = _run_async(export_engagement_scoring_json())
        self.assertEqual(export_res.media_type, "application/json")

    # =========================================================================
    # EPIC 5: Activity 5.1 - Teaching Suggestion Logic Tests
    # =========================================================================

    def test_epic5_activity5_1_recommendations_engine_individual_and_global_rules(self):
        """
        EPIC 5 Activity 5.1: Rule 1 & Rule 2 Verification (Reference Image 2)
        Validates individual attention alert (attention < 40%) and global attention warning (avg < 60%).
        """
        from backend.core.recommendations_engine import RecommendationsEngine

        engine = RecommendationsEngine(cooldown_seconds=0.0)

        # 1. Test Low Attention Alert (Image 2: student distracted < 40%)
        status_distracted = {
            "people": [
                {"id": "STU-102", "name": "Liam Smith", "attention": 32.0},
                {"id": "STU-101", "name": "Emma Watson", "attention": 85.0},
                {"id": "STU-103", "name": "Sophia Chen", "attention": 80.0}
            ],
            "engagement_score": 75.0
        }
        recs = engine.generate_realtime_recommendations(status_distracted)
        self.assertGreaterEqual(len(recs), 1)
        alert_rec = next((r for r in recs if r["type"] == "alert" and r["category"] == "individual_attention"), None)
        self.assertIsNotNone(alert_rec)
        self.assertIn("Student STU-102 is distracted (32.0%).", alert_rec["message"])
        self.assertEqual(alert_rec["observable_evidence"]["threshold"], 40.0)

        # 2. Test Global Attention Warning (Image 2: len(people) > 2 and avg_att < 60)
        engine.clear_history()
        status_global_dip = {
            "people": [
                {"id": "STU-101", "name": "Emma Watson", "attention": 52.0},
                {"id": "STU-102", "name": "Liam Smith", "attention": 55.0},
                {"id": "STU-103", "name": "Sophia Chen", "attention": 48.0}
            ],
            "engagement_score": 51.6
        }
        recs_global = engine.generate_realtime_recommendations(status_global_dip)
        warn_rec = next((r for r in recs_global if r["type"] == "warning" and r["category"] == "global_attention"), None)
        self.assertIsNotNone(warn_rec)
        self.assertIn("Collective attention dipped below threshold", warn_rec["message"])
        self.assertEqual(warn_rec["observable_evidence"]["threshold"], 60.0)

    def test_epic5_activity5_1_sustained_disengagement_and_peak_period_rules(self):
        """
        EPIC 5 Activity 5.1: Rule 3 & Rule 4 Verification
        Validates recommending interactive activities during sustained disengagement (< 50%)
        and highlighting effective teaching segments during peak periods (>= 82%).
        """
        from backend.core.recommendations_engine import RecommendationsEngine

        engine = RecommendationsEngine(cooldown_seconds=0.0)

        # 1. Test Sustained Disengagement (Rule 3)
        status_disengaged = {
            "people": [{"id": "STU-101", "attention": 45.0}],
            "engagement_score": 42.0,
            "inactivity_seconds": 60.0,
            "disengagement_phases": [
                {"phase_id": 1, "primary_cause": "Visual Wander", "average_score": 42.0, "duration_seconds": 40.0}
            ]
        }
        recs_diseng = engine.generate_realtime_recommendations(status_disengaged)
        diseng_rec = next((r for r in recs_diseng if r["category"] == "sustained_disengagement"), None)
        self.assertIsNotNone(diseng_rec)
        self.assertEqual(diseng_rec["type"], "alert")
        self.assertIn("interactive activity", diseng_rec["pedagogical_action"].lower())

        # 2. Test Peak Engagement Highlight (Rule 4)
        engine.clear_history()
        status_peak = {
            "people": [{"id": "STU-101", "attention": 92.0}],
            "engagement_score": 88.0,
            "peak_periods": [
                {"period_id": 1, "top_factor": "Visual Presence & Dynamic Speech", "average_score": 88.0}
            ]
        }
        recs_peak = engine.generate_realtime_recommendations(status_peak)
        peak_rec = next((r for r in recs_peak if r["category"] == "peak_engagement"), None)
        self.assertIsNotNone(peak_rec)
        self.assertEqual(peak_rec["type"], "info")
        self.assertIn("Bookmark this segment", peak_rec["pedagogical_action"])

    def test_epic5_activity5_1_noise_and_pacing_and_monologue_rules(self):
        """
        EPIC 5 Activity 5.1: Rule 5, 6 & 7 Verification
        Validates classroom noise management (>= 75 dB SPL), instructional pacing drop,
        and continuous monologue advisory.
        """
        from backend.core.recommendations_engine import RecommendationsEngine

        engine = RecommendationsEngine(cooldown_seconds=0.0)

        # 1. Elevated Noise Management Cue (Rule 5)
        status_noise = {
            "noise_level_spl": 78.5,
            "ambient_noise_level": "LOUD_DISRUPTIVE",
            "engagement_score": 65.0
        }
        recs_noise = engine.generate_realtime_recommendations(status_noise)
        noise_rec = next((r for r in recs_noise if r["category"] == "classroom_noise"), None)
        self.assertIsNotNone(noise_rec)
        self.assertEqual(noise_rec["type"], "warning")
        self.assertIn("Ambient noise level is elevated", noise_rec["message"])

        # 2. Attention Drop (Rule 6)
        engine.clear_history()
        status_drop = {
            "trend": "DROPPING",
            "trend_delta": 18.5,
            "engagement_score": 58.0
        }
        recs_drop = engine.generate_realtime_recommendations(status_drop)
        drop_rec = next((r for r in recs_drop if r["category"] == "instructional_pacing"), None)
        self.assertIsNotNone(drop_rec)
        self.assertIn("dropped by 18.5%", drop_rec["message"])

        # 3. Monologue Fatigue Advisory (Rule 7: >= 8 minutes)
        engine.clear_history()
        status_monologue = {
            "consecutive_monologue_sec": 540.0,  # 9 minutes
            "engagement_score": 70.0
        }
        recs_mono = engine.generate_realtime_recommendations(status_monologue)
        mono_rec = next((r for r in recs_mono if r["category"] == "prolonged_monologue"), None)
        self.assertIsNotNone(mono_rec)
        self.assertIn("9 minutes", mono_rec["message"])

    def test_epic5_activity5_1_teacher_profile_service(self):
        """
        EPIC 5 Activity 5.1: TeacherProfileService Verification (Reference Image 1)
        Validates teacher analytics, effectiveness score (87.5%), trend (+12.0%),
        class history, student trends, and pedagogical strengths.
        """
        from backend.core.teacher_profiles import TeacherProfileService

        service = TeacherProfileService()
        profile = service.get_profile("Prof. Alex Vance")

        self.assertIn("teacher_id", profile)
        self.assertIn("effectiveness_score", profile)
        self.assertIn("trend", profile)
        self.assertEqual(profile["trend"], 12.0)

        # Check Class History (matching Image 1)
        self.assertIn("class_history", profile)
        class_names = [c["name"] for c in profile["class_history"]]
        self.assertTrue(any("CS101" in name or "Math" in name for name in class_names))

        # Check Student Trends (matching Image 1: Priya, Kumar, Asha)
        self.assertIn("student_trends", profile)
        student_names = [s["name"] for s in profile["student_trends"]]
        self.assertIn("Priya", student_names)
        self.assertIn("Kumar", student_names)
        self.assertIn("Asha", student_names)

        priya = next(s for s in profile["student_trends"] if s["name"] == "Priya")
        self.assertEqual(priya["status"], "improved")
        self.assertEqual(priya["change"], 15)

        asha = next(s for s in profile["student_trends"] if s["name"] == "Asha")
        self.assertEqual(asha["status"], "declining")
        self.assertEqual(asha["change"], -5)

        # Check Strengths (matching Image 1)
        self.assertIn("strengths", profile)
        self.assertTrue(any("85%+" in st for st in profile["strengths"]))
        self.assertTrue(any("Emotion diversity" in st for st in profile["strengths"]))

    def test_epic5_activity5_1_pedagogical_agent_integration(self):
        """
        EPIC 5 Activity 5.1: Agent Integration Verification
        Verifies PedagogicalReasoningAgent exposes recommendations_engine methods.
        """
        from backend.agent.pedagogical_agent import PedagogicalReasoningAgent
        from backend.db.database import DatabaseManager

        db_mgr = DatabaseManager()
        agent = PedagogicalReasoningAgent(db=db_mgr, session_id="TEST-SES-001", cooldown_seconds=0.0)

        status_test = {
            "people": [{"id": "STU-99", "attention": 25.0}],
            "engagement_score": 50.0
        }
        recs = agent.generate_recommendations(status_test)
        self.assertGreaterEqual(len(recs), 1)
        self.assertEqual(recs[0]["type"], "alert")

    def test_epic5_activity5_1_api_endpoints_integration(self):
        """
        EPIC 5 Activity 5.1: REST API Endpoints Verification
        Tests all 6 new Activity 5.1 endpoints:
        - GET /api/recommendations/activity_5_1/status
        - POST /api/recommendations/activity_5_1/generate
        - GET /api/recommendations/activity_5_1/history
        - POST /api/recommendations/activity_5_1/evaluate_temporal_profile
        - GET /api/teacher/profile
        - GET /api/recommendations/rules
        - POST /api/recommendations/activity_5_1/reset
        """
        import asyncio
        from backend.api.server import (
            get_activity_5_1_status,
            generate_recommendations_endpoint,
            get_recommendations_history_endpoint,
            evaluate_temporal_profile_for_recommendations_endpoint,
            get_teacher_profile_endpoint,
            get_recommendation_rules_catalog,
            reset_recommendations_endpoint
        )

        def _run_async(coro):
            return asyncio.run(coro)

        # 1. Reset endpoint
        res_reset = _run_async(reset_recommendations_endpoint())
        self.assertEqual(res_reset["status"], "SUCCESS")

        # 2. Status endpoint
        status_res = _run_async(get_activity_5_1_status())
        self.assertEqual(status_res["activity_id"], "Activity 5.1")
        self.assertEqual(status_res["status"], "COMPLETED & VERIFIED")
        self.assertIn("teacher_profile", status_res)

        # 3. Generate recommendations endpoint
        gen_res = _run_async(generate_recommendations_endpoint({
            "people": [{"id": "STU-105", "name": "Olivia Brown", "attention": 30.0}],
            "engagement_score": 60.0
        }))
        self.assertEqual(gen_res["status"], "SUCCESS")
        self.assertGreaterEqual(gen_res["recommendations_count"], 1)

        # 4. History endpoint
        hist_res = _run_async(get_recommendations_history_endpoint(limit=10))
        self.assertEqual(hist_res["status"], "SUCCESS")
        self.assertGreaterEqual(hist_res["total_in_history"], 1)

        # 5. Temporal profile evaluation endpoint
        prof_eval_res = _run_async(evaluate_temporal_profile_for_recommendations_endpoint({
            "mean_engagement_score": 45.0,
            "disengagement_phases": [{"primary_cause": "Prolonged Inactivity", "average_score": 45.0}],
            "peak_periods": [],
            "fluctuation_metrics": {"stability_index": 50.0, "std_dev": 22.0}
        }))
        self.assertEqual(prof_eval_res["status"], "SUCCESS")
        self.assertGreaterEqual(prof_eval_res["recommendations_count"], 1)

        # 6. Teacher profile endpoint
        teach_res = _run_async(get_teacher_profile_endpoint("Prof. Alex Vance"))
        self.assertEqual(teach_res["status"], "SUCCESS")
        self.assertEqual(teach_res["profile"]["trend"], 12.0)
        self.assertGreaterEqual(len(teach_res["profile"]["class_history"]), 3)

        # 7. Rules catalog endpoint
        rules_res = _run_async(get_recommendation_rules_catalog())
        self.assertEqual(rules_res["status"], "SUCCESS")
        self.assertEqual(rules_res["total_rules"], 7)

    def test_activity_5_2_analytics_service_core_and_reference_image(self):
        """
        EPIC 5: Activity 5.2 - Reference Image Verification
        Tests AnalyticsService.get_session_trends(session_id) querying PersonMetric:
        - Granular PersonMetric storage and retrieval
        - Timestamp grouping ('%H:%M:%S') with 'att' array and 'emo' dictionary
        - Minute-bucket aggregations and session trend direction
        """
        from backend.core.analytics_service import AnalyticsService, PersonMetric

        analytics_svc = AnalyticsService(db=self.db)
        
        # 1. Record several PersonMetrics across 2 students and timestamps
        now = time.time()
        self.db.record_person_metric(
            session_id=self.session_id,
            student_id="STU-001",
            attention_score=0.88,
            emotion_state="ENGAGED",
            motion_energy=0.06,
            inactivity_seconds=0.0,
            epoch_seconds=now - 20
        )
        self.db.record_person_metric(
            session_id=self.session_id,
            student_id="STU-002",
            attention_score=0.45,
            emotion_state="DISTRACTED",
            motion_energy=0.03,
            inactivity_seconds=12.0,
            epoch_seconds=now - 20
        )
        self.db.record_person_metric(
            session_id=self.session_id,
            student_id="STU-001",
            attention_score=0.92,
            emotion_state="ENGAGED",
            motion_energy=0.05,
            inactivity_seconds=0.0,
            epoch_seconds=now - 5
        )

        # 2. Call get_session_trends (matching Reference Image)
        trends = analytics_svc.get_session_trends(self.session_id)
        
        self.assertEqual(trends["session_id"], self.session_id)
        self.assertGreaterEqual(trends["total_points"], 3)
        self.assertIn("timeline", trends)
        self.assertIn("minute_buckets", trends)
        self.assertIn("session_summary", trends)
        
        # Verify timeline structure matching image: timeline[ts_str] = {'att': [...], 'emo': {...}}
        for ts_str, bucket in trends["timeline"].items():
            self.assertIn("att", bucket)
            self.assertIn("emo", bucket)
            self.assertIsInstance(bucket["att"], list)
            self.assertIsInstance(bucket["emo"], dict)

        self.assertIn("average_attention_percent", trends["session_summary"])
        self.assertIn("trend_direction", trends["session_summary"])

    def test_activity_5_2_student_session_analytics_reflective_generation(self):
        """
        EPIC 5: Activity 5.2 - Student Session Analytics Generation & Reflective Profile
        Tests individual student-facing session summary:
        - Attendance duration and sustained presence verification
        - Engagement consistency score and stability categorization
        - Engagement timeline with high focus (>75%) and distraction (<50%) periods
        - Notable activity trends grounded in observable data
        - Self-reflection prompts without grading or evaluation
        - Privacy assurance (zero peer rankings, zero peer comparisons)
        """
        from backend.core.analytics_service import AnalyticsService

        # Seed attendance record for STU-001
        self.db.log_attendance_entry(
            session_id=self.session_id,
            student_id="STU-001",
            first_seen="10:00:00",
            last_seen="10:30:00",
            active_sec=1650.0,
            presence_ratio=0.916,
            status="PRESENT"
        )

        analytics_svc = AnalyticsService(db=self.db)
        stu_analytics = analytics_svc.get_student_session_analytics(self.session_id, "STU-001")

        # 1. Identity & Attendance
        self.assertEqual(stu_analytics["student_id"], "STU-001")
        self.assertEqual(stu_analytics["display_name"], "Alice Turing")
        self.assertEqual(stu_analytics["attendance"]["status"], "PRESENT")
        self.assertAlmostEqual(stu_analytics["attendance"]["duration_seconds"], 1650.0, places=1)
        self.assertIn("27m", stu_analytics["attendance"]["duration_formatted"])
        self.assertAlmostEqual(stu_analytics["attendance"]["presence_ratio_percent"], 91.6, places=1)

        # 2. Consistency Score
        self.assertIn("consistency_score", stu_analytics["consistency"])
        self.assertIn("consistency_classification", stu_analytics["consistency"])
        self.assertIn("stability_description", stu_analytics["consistency"])
        self.assertGreaterEqual(stu_analytics["consistency"]["consistency_score"], 0.0)
        self.assertLessEqual(stu_analytics["consistency"]["consistency_score"], 100.0)

        # 3. Focus Distribution (High Focus vs. Distraction)
        focus_dist = stu_analytics["focus_distribution"]
        self.assertIn("high_focus_percent", focus_dist)
        self.assertIn("balanced_attention_percent", focus_dist)
        self.assertIn("distraction_wandering_percent", focus_dist)
        total_pct = focus_dist["high_focus_percent"] + focus_dist["balanced_attention_percent"] + focus_dist["distraction_wandering_percent"]
        self.assertAlmostEqual(total_pct, 100.0, delta=1.0)

        # 4. Structured Focus Periods
        self.assertIsInstance(stu_analytics["focus_periods"], list)
        if stu_analytics["focus_periods"]:
            fp0 = stu_analytics["focus_periods"][0]
            self.assertIn(fp0["zone_type"], ["HIGH_FOCUS", "BALANCED_ATTENTION", "DISTRACTION_WANDERING"])
            self.assertIn("average_attention", fp0)
            self.assertIn("notable_behavior", fp0)

        # 5. Notable Trends
        self.assertIsInstance(stu_analytics["notable_trends"], list)
        self.assertGreaterEqual(len(stu_analytics["notable_trends"]), 1)

        # 6. Reflective Insights (Zero Grading)
        refl = stu_analytics["reflective_insights"]
        self.assertIn("primary_takeaway", refl)
        self.assertIn("reflection_questions", refl)
        self.assertGreaterEqual(len(refl["reflection_questions"]), 2)
        self.assertIn("actionable_self_cues", refl)

        # 7. Privacy Safeguards
        priv = stu_analytics["privacy_safeguards"]
        self.assertFalse(priv["peer_comparison_included"])
        self.assertFalse(priv["rankings_assigned"])
        self.assertFalse(priv["grades_assigned"])
        self.assertIn("confidential", priv["privacy_statement"].lower())

    def test_activity_5_2_cohort_summary_and_reports_export(self):
        """
        EPIC 5: Activity 5.2 - Cohort Unranked Overview & Report Generation
        Tests:
        - Unranked cohort summaries ordered by student/seat
        - JSON report export
        - Markdown report export with reflective formatting
        """
        from backend.core.analytics_service import AnalyticsService

        analytics_svc = AnalyticsService(db=self.db)

        # 1. All Students Reflective Summary (Cohort unranked)
        cohort = analytics_svc.get_all_students_reflective_summary(self.session_id)
        self.assertEqual(len(cohort), 2)
        self.assertEqual(cohort[0]["student_id"], "STU-001")
        self.assertEqual(cohort[1]["student_id"], "STU-002")
        for s in cohort:
            self.assertIn("consistency_score", s)
            self.assertIn("top_reflection", s)
            self.assertNotIn("rank", s)
            self.assertNotIn("grade", s)

        # 2. JSON Report Export
        json_report = analytics_svc.export_student_analytics_report(self.session_id, "STU-001", format_type="json")
        self.assertEqual(json_report["format"], "json")
        self.assertIn("reflective_report_STU-001", json_report["filename"])
        self.assertEqual(json_report["report_data"]["student_id"], "STU-001")

        # 3. Markdown Report Export
        md_report = analytics_svc.export_student_analytics_report(self.session_id, "STU-001", format_type="markdown")
        self.assertEqual(md_report["format"], "markdown")
        self.assertTrue(md_report["filename"].endswith(".md"))
        md_content = md_report["content"]
        self.assertIn("# 🎓 Student Session Reflection", md_content)
        self.assertIn("Attendance & Participation Duration", md_content)
        self.assertIn("Privacy & Reflection Assurance", md_content)
        self.assertIn("no grades", md_content)

    def test_activity_5_2_fastapi_rest_endpoints(self):
        """
        EPIC 5: Activity 5.2 - FastAPI REST Endpoints Verification
        Tests:
        - GET /api/analytics/activity_5_2/status
        - GET /api/analytics/activity_5_2/session_trends
        - GET /api/analytics/activity_5_2/student/{student_id}
        - GET /api/analytics/activity_5_2/all_reflective
        - GET /api/analytics/activity_5_2/export_report/{student_id}?format_type=json
        - GET /api/analytics/activity_5_2/export_report/{student_id}?format_type=markdown
        """
        import asyncio
        from backend.api.server import (
            get_activity_5_2_status,
            get_session_trends_endpoint,
            get_student_session_analytics_endpoint,
            get_all_students_reflective_endpoint,
            export_student_report_endpoint
        )

        def _run_async(coro):
            return asyncio.run(coro)

        # 1. Status endpoint
        status_res = _run_async(get_activity_5_2_status())
        self.assertEqual(status_res["activity_id"], "Activity 5.2")
        self.assertEqual(status_res["status"], "COMPLETED & VERIFIED")
        self.assertIn("features", status_res)
        self.assertGreaterEqual(len(status_res["features"]), 5)

        # 2. Session trends endpoint (Reference Image)
        trends_res = _run_async(get_session_trends_endpoint())
        self.assertIn("session_id", trends_res)
        self.assertIn("timeline", trends_res)
        self.assertIn("session_summary", trends_res)

        # 3. Individual student analytics endpoint
        stu_res = _run_async(get_student_session_analytics_endpoint("STU-101"))
        self.assertEqual(stu_res["student_id"], "STU-101")
        self.assertIn("attendance", stu_res)
        self.assertIn("consistency", stu_res)
        self.assertIn("focus_distribution", stu_res)
        self.assertIn("reflective_insights", stu_res)
        self.assertFalse(stu_res["privacy_safeguards"]["rankings_assigned"])

        # 4. Cohort unranked summaries endpoint
        all_res = _run_async(get_all_students_reflective_endpoint())
        self.assertEqual(all_res["status"], "SUCCESS")
        self.assertGreaterEqual(len(all_res["summaries"]), 1)

        # 5. Export JSON report endpoint
        export_json_res = _run_async(export_student_report_endpoint("STU-101", format_type="json"))
        self.assertEqual(export_json_res["format"], "json")
        self.assertIn("report_data", export_json_res)

        # 6. Export Markdown report endpoint
        export_md_res = _run_async(export_student_report_endpoint("STU-101", format_type="markdown"))
        self.assertIn("content-disposition", [k.lower() for k in export_md_res.headers.keys()])
        self.assertIn(b"Student Session Reflection", export_md_res.body)

    # -------------------------------------------------------------------------
    # EPIC 6: Interface, Testing, and Deployment
    # Activity 6.1: Run Core Application Tests
    # -------------------------------------------------------------------------

    def test_activity_6_1_video_stream_multi_source_ingestion(self):
        """
        EPIC 6: Activity 6.1 - Video Stream Multi-Source Ingestion
        Validates stream ingestion across simulated classroom, pre-recorded MP4 video,
        and webcam with graceful fallback.
        """
        import os
        from backend.vision.video_stream import VideoStreamEngine
        from backend.utils.video_generator import generate_prerecorded_classroom_video

        sample_video = "storage/uploads/classroom_lecture_sample.mp4"
        if not os.path.exists(sample_video):
            sample_video = generate_prerecorded_classroom_video(sample_video)

        # 1. High-fidelity Simulated Stream
        engine_sim = VideoStreamEngine(source_type="simulated", width=640, height=480)
        engine_sim.start()
        ret_sim, frame_sim, meta_sim = engine_sim.read_frame("INSTRUCTOR_MONOLOGUE")
        self.assertTrue(ret_sim)
        self.assertIsNotNone(frame_sim)
        self.assertEqual(frame_sim.shape, (480, 640, 3))
        self.assertGreaterEqual(len(meta_sim), 1)
        engine_sim.stop()

        # 2. Pre-Recorded Video File Ingestion
        engine_file = VideoStreamEngine(source_type="file", video_path=sample_video, width=640, height=480)
        engine_file.start()
        ret_file, frame_file, _ = engine_file.read_frame("INSTRUCTOR_MONOLOGUE")
        self.assertTrue(ret_file)
        self.assertIsNotNone(frame_file)
        self.assertEqual(frame_file.shape, (480, 640, 3))
        engine_file.stop()

        # 3. Dynamic Source Switching
        engine_switch = VideoStreamEngine(source_type="simulated", width=640, height=480)
        engine_switch.start()
        self.assertEqual(engine_switch.source_type, "simulated")
        engine_switch.set_source("file", video_path=sample_video)
        self.assertEqual(engine_switch.source_type, "file")
        ret_sw, frame_sw, _ = engine_switch.read_frame()
        self.assertTrue(ret_sw)
        self.assertIsNotNone(frame_sw)
        engine_switch.stop()

    def test_activity_6_1_camera_service_prerecorded_video_looping(self):
        """
        EPIC 6: Activity 6.1 - Camera Service Pre-Recorded Video Looping
        Verifies that CameraService correctly opens video files, retrieves frames,
        and rewinds at EOF for continuous session playback.
        """
        import os
        from backend.core.camera_service import CameraService
        from backend.utils.video_generator import generate_prerecorded_classroom_video

        sample_video = "storage/uploads/classroom_lecture_sample.mp4"
        if not os.path.exists(sample_video):
            sample_video = generate_prerecorded_classroom_video(sample_video)

        cam = CameraService(camera_id=0, video_path=sample_video, fps=15, width=640, height=480)
        started = cam.start()
        self.assertTrue(started)
        self.assertTrue(cam.is_running)

        # Retrieve multiple frames
        frames_read = 0
        for _ in range(5):
            f = cam.get_frame()
            if f is not None:
                frames_read += 1

        self.assertGreaterEqual(frames_read, 1)
        cam.stop()
        self.assertFalse(cam.is_running)

    def test_activity_6_1_end_to_end_pipeline_verification(self):
        """
        EPIC 6: Activity 6.1 - End-to-End Pipeline Verification Engine
        Executes complete multi-frame pipeline across:
        1. Vision Processing
        2. Audio Analysis
        3. Multimodal Signal Fusion
        4. Engagement Scoring Logic
        5. Analytics & Recommendation Generation
        """
        from backend.core.pipeline_verifier import PipelineVerifier

        verifier = PipelineVerifier()

        # Test with pre-recorded classroom video
        res_file = verifier.verify_pipeline(source="file", num_frames=3)
        self.assertEqual(res_file["status"], "SUCCESS")
        self.assertTrue(res_file["end_to_end_verified"])
        self.assertEqual(res_file["input_source_tested"], "file")
        self.assertEqual(res_file["total_frames_processed"], 3)
        self.assertGreater(res_file["throughput_fps"], 0.0)

        # Verify all 5 core modules are verified
        mods = res_file["modules_verified"]
        expected_mods = [
            "vision_processing", "audio_analysis", "multimodal_fusion",
            "engagement_scoring", "analytics_generation"
        ]
        for m in expected_mods:
            self.assertIn(m, mods)
            self.assertTrue(mods[m]["verified"])

        # Test with simulated classroom stream
        res_sim = verifier.verify_pipeline(source="simulated", num_frames=3)
        self.assertEqual(res_sim["status"], "SUCCESS")
        self.assertTrue(res_sim["end_to_end_verified"])
        self.assertEqual(res_sim["input_source_tested"], "simulated")
        for m in expected_mods:
            self.assertTrue(res_sim["modules_verified"][m]["verified"])

    def test_activity_6_1_fastapi_rest_endpoints(self):
        """
        EPIC 6: Activity 6.1 - FastAPI REST Endpoints Verification
        Tests /api/activity_6_1/status, /api/activity_6_1/verify_pipeline,
        and /api/config/source endpoint updates.
        """
        import asyncio
        from backend.api.server import (
            get_activity_6_1_status,
            verify_pipeline_endpoint,
            change_source
        )

        def _run_async(coro):
            return asyncio.run(coro)

        # 1. Status endpoint
        status_res = _run_async(get_activity_6_1_status())
        self.assertEqual(status_res["activity_id"], "Activity 6.1")
        self.assertEqual(status_res["status"], "COMPLETED & VERIFIED")
        self.assertIn("supported_sources", status_res)
        self.assertGreaterEqual(len(status_res["supported_sources"]), 3)
        self.assertEqual(len(status_res["data_flow_pipeline"]), 5)

        # 2. Pipeline verification endpoint (file)
        verify_file_res = _run_async(verify_pipeline_endpoint(source="file", num_frames=3))
        self.assertEqual(verify_file_res["status"], "SUCCESS")
        self.assertTrue(verify_file_res["end_to_end_verified"])
        self.assertIn("modules_verified", verify_file_res)
        self.assertEqual(len(verify_file_res["modules_verified"]), 5)

        # 3. Pipeline verification endpoint (simulated)
        verify_sim_res = _run_async(verify_pipeline_endpoint(source="simulated", num_frames=3))
        self.assertEqual(verify_sim_res["status"], "SUCCESS")
        self.assertTrue(verify_sim_res["end_to_end_verified"])

        # 4. Source switching endpoint with file
        switch_res = _run_async(change_source(source="file", video_path="storage/uploads/classroom_lecture_sample.mp4"))
        self.assertEqual(switch_res["status"], "SUCCESS")
        self.assertEqual(switch_res["source"], "file")

    def test_activity_6_2_streamlit_dashboard_data_fetchers(self):
        """
        EPIC 6: Activity 6.2 - Launch Optional Streamlit Dashboard
        Verifies all data fetchers and fallback routines in streamlit_app.py
        for attendance records, engagement timelines, instructor suggestions,
        student session analytics, and pipeline status.
        """
        import streamlit_app as sapp

        # 1. Teacher Analytics Profile (Activity 5.1)
        prof = sapp.fetch_activity_5_1_profile()
        self.assertIsInstance(prof, dict)
        self.assertIn("instructor_name", prof)
        self.assertIn("effectiveness_score", prof)
        self.assertIn("strengths", prof)
        self.assertGreaterEqual(prof["effectiveness_score"], 50.0)

        # 2. Teaching Suggestion History (Activity 5.1)
        rec_history = sapp.fetch_activity_5_1_history()
        self.assertIsInstance(rec_history, list)

        # 3. Minute-Level Session Trends (Activity 5.2)
        trends = sapp.fetch_activity_5_2_session_trends()
        self.assertIsInstance(trends, dict)

        # 4. Individual Student Reflective Analytics (Activity 5.2)
        student_analytics = sapp.fetch_activity_5_2_student("STU-101")
        self.assertIsInstance(student_analytics, dict)
        self.assertEqual(student_analytics.get("student_id"), "STU-101")
        self.assertIn("focus_distribution", student_analytics)
        self.assertIn("continuous_focus_episodes", student_analytics)
        self.assertIn("grounded_activity_trends", student_analytics)
        self.assertIn("self_reflection_prompts", student_analytics)

        # 5. Cohort Reflective Summaries (Activity 5.2)
        cohort = sapp.fetch_activity_5_2_all_reflective()
        self.assertIsInstance(cohort, list)

        # 6. Pipeline Status & Verification (Activity 6.1)
        p_status = sapp.fetch_activity_6_1_status()
        self.assertIsInstance(p_status, dict)
        self.assertIn("supported_sources", p_status)

        v_res = sapp.run_pipeline_verification(source="simulated", num_frames=2)
        self.assertIsInstance(v_res, dict)
        self.assertIn(v_res.get("status"), ["PASSED", "SUCCESS", "COMPLETED"])

    def test_activity_6_2_streamlit_interpretability_and_export(self):
        """
        EPIC 6: Activity 6.2 - Interpretability Layer & Structured Export
        Verifies attendance filtering, stability index calculation, and
        reflective summary export in JSON and Markdown formats.
        """
        import pandas as pd
        import numpy as np
        import json

        # 1. Attendance status filtering
        sample_records = [
            {"student_id": "STU-101", "name": "Emma Watson", "status": "PRESENT", "presence_seconds": 285.0},
            {"student_id": "STU-104", "name": "Lucas Garcia", "status": "LATE", "presence_seconds": 210.0},
            {"student_id": "STU-106", "name": "Ethan Davis", "status": "INTERMITTENT", "presence_seconds": 120.0},
            {"student_id": "STU-108", "name": "Noah Wilson", "status": "WALKBY_FILTERED", "presence_seconds": 12.0}
        ]
        df = pd.DataFrame(sample_records)
        self.assertEqual(len(df[df["status"] == "PRESENT"]), 1)
        self.assertEqual(len(df[df["status"] == "LATE"]), 1)
        self.assertEqual(len(df[df["status"] == "INTERMITTENT"]), 1)
        self.assertEqual(len(df[df["status"] == "WALKBY_FILTERED"]), 1)

        # 2. Stability Index & Statistical Indicators
        scores = [75.0, 78.0, 82.0, 80.0, 85.0, 83.0, 88.0, 85.0, 87.0, 89.0]
        mean_score = float(np.mean(scores))
        std_score = float(np.std(scores))
        var_score = float(np.var(scores))
        stability_index = max(0.0, min(100.0, round(100.0 - (std_score * 2.5), 1)))

        self.assertAlmostEqual(mean_score, 83.2, delta=0.5)
        self.assertGreater(stability_index, 80.0)
        self.assertGreater(var_score, 0.0)

        # 3. JSON Export validation
        reflection_payload = {
            "student_id": "STU-101",
            "name": "Emma Watson",
            "status": "PRESENT",
            "active_presence_duration_minutes": 28.5,
            "consistency_index_percent": 88.2,
            "focus_distribution": {"high_focus_percent": 68.0, "balanced_percent": 24.0, "distracted_percent": 8.0}
        }
        json_str = json.dumps(reflection_payload, indent=2)
        parsed = json.loads(json_str)
        self.assertEqual(parsed["student_id"], "STU-101")
        self.assertEqual(parsed["consistency_index_percent"], 88.2)

        # 4. Markdown Report validation
        md_report = f"# Student Reflective Session Summary\n**Student:** {reflection_payload['name']}\n**Status:** {reflection_payload['status']}"
        self.assertIn("Student Reflective Session Summary", md_report)
        self.assertIn("Emma Watson", md_report)

    # =========================================================================
    # EPIC 6: Activity 6.3 - Validate Outputs and Edge Cases
    # Comprehensive validation of system accuracy and robustness under
    # real-world conditions: fluctuating lighting, background noise,
    # partial occlusions, short participant appearances, intermittent audio,
    # attendance accuracy, engagement score stability, and analytics interpretability.
    # =========================================================================

    def test_activity_6_3_fluctuating_lighting_visual_robustness(self):
        """
        EPIC 6 Activity 6.3 - Edge Case: Fluctuating Lighting Conditions.
        Simulates rapid visual attention variations caused by changing classroom
        lighting (e.g., projector on/off, curtain opening, flickering lights).
        Engagement scores must remain stable and not oscillate wildly.
        """
        from backend.core.engagement_scoring import EngagementScoringEngine, ScoringThresholdConfig

        engine = EngagementScoringEngine(ScoringThresholdConfig())

        # Simulate 20 segments with alternating high/low visual attention
        # (mimicking lighting fluctuations causing detection variability)
        packets = []
        for i in range(20):
            # Fluctuating attention: alternating 0.85 and 0.40 simulates
            # detector confidence drops during lighting changes
            if i % 2 == 0:
                visual_att = 0.85  # Good lighting
            else:
                visual_att = 0.40  # Poor lighting / shadows

            packets.append({
                "average_visual_attention": visual_att,
                "average_motion_energy": 0.08,
                "presence_ratio_percent": 90.0,
                "inactivity_seconds": 5.0,
                "noise_level_spl": 55.0,
                "rhythm_state": "INSTRUCTOR_MONOLOGUE",
                "speech_state": "ACTIVE_SPEECH",
                "participation_frequency": 1.0,
            })

        profile = engine.generate_temporal_profile(packets, interval_seconds=10.0, session_id="LIGHTING-TEST")

        # 1. Mean score should still be in a reasonable range (not tank to zero)
        self.assertGreater(profile.mean_score, 40.0,
                           "Mean engagement must remain above 40% despite lighting fluctuations.")
        self.assertLess(profile.mean_score, 95.0)

        # 2. Fluctuation metrics should detect the oscillation
        self.assertIsNotNone(profile.fluctuation_metrics)
        self.assertGreater(profile.fluctuation_metrics.standard_deviation, 0.0,
                           "Standard deviation must be non-zero for fluctuating inputs.")

        # 3. Individual segment scores must be within valid [0, 100] range
        for seg in profile.segments:
            self.assertGreaterEqual(seg.composite_score, 0.0)
            self.assertLessEqual(seg.composite_score, 100.0)

        # 4. Profile must serialize without errors
        profile_dict = profile.to_dict()
        self.assertIn("segments", profile_dict)
        self.assertIn("fluctuation_metrics", profile_dict)

    def test_activity_6_3_background_noise_engagement_stability(self):
        """
        EPIC 6 Activity 6.3 - Edge Case: Background Noise Variations.
        Tests that engagement scores handle noisy audio signals (construction,
        HVAC, crowd noise) without producing invalid or extreme scores.
        """
        from backend.core.engagement_scoring import EngagementScoringEngine, ScoringThresholdConfig

        engine = EngagementScoringEngine(ScoringThresholdConfig())

        noise_scenarios = [
            # (spl_db, rhythm_state, description)
            (35.0, "SILENT_STUDY", "Ultra-quiet empty room"),
            (50.0, "INSTRUCTOR_MONOLOGUE", "Normal quiet lecture"),
            (65.0, "QA_INTERACTION", "Moderate discussion"),
            (78.0, "COLLABORATIVE_BUZZ", "Loud group work"),
            (92.0, "COLLABORATIVE_BUZZ", "Extreme noise / construction"),
            (30.0, "SILENT_STUDY", "Near-silent environment"),
        ]

        scores = []
        for spl, rhythm, desc in noise_scenarios:
            visual_data = {
                "average_visual_attention": 0.75,
                "average_motion_energy": 0.08,
                "presence_ratio_percent": 85.0,
                "inactivity_seconds": 10.0,
            }
            audio_data = {
                "noise_level_spl": spl,
                "rhythm_state": rhythm,
                "speech_state": "ACTIVE_SPEECH" if spl > 45 else "SILENCE",
                "participation_frequency": 1.5 if rhythm == "QA_INTERACTION" else 0.5,
                "consecutive_silence_sec": 0.0,
            }
            seg = engine.score_segment(visual_data, audio_data, start_time=1000.0, duration_seconds=10.0)
            scores.append(seg.composite_score)

            # Every score must be valid
            self.assertGreaterEqual(seg.composite_score, 0.0, f"Score invalid for: {desc}")
            self.assertLessEqual(seg.composite_score, 100.0, f"Score exceeds 100 for: {desc}")
            self.assertIn(seg.engagement_level,
                          ["HIGH", "MODERATE", "LOW", "CRITICAL_DISENGAGED"],
                          f"Invalid engagement level for: {desc}")

        # Extreme noise should produce lower speech score than normal
        self.assertLess(scores[4], scores[1],
                        "Extreme noise scenario must score lower than normal quiet lecture.")

    def test_activity_6_3_partial_occlusion_attendance_accuracy(self):
        """
        EPIC 6 Activity 6.3 - Edge Case: Partial Occlusions.
        Simulates a student being partially occluded (e.g., behind another student,
        turning head, temporarily blocked by object) and verifies attendance remains
        accurate through intermittent visibility gaps.
        """
        from backend.core.presence_attendance import PresenceAttendanceEngine

        engine = PresenceAttendanceEngine(
            session_id="OCCLUSION-TEST",
            min_sustained_seconds=15.0,
            walkby_threshold_seconds=5.0
        )
        engine.register_enrolled_students([
            {"id": "STU-OCCLUDED", "name": "Occluded Student", "seat": "Desk B"},
        ])

        # Simulate 40 seconds: student visible for 3s, occluded for 2s, visible 3s, etc.
        # Total visible: ~24s out of 40s (above 15s threshold)
        base_time = 5000.0
        for step in range(40):
            # Pattern: 3 visible, 2 hidden, repeat
            cycle = step % 5
            is_visible = cycle < 3  # visible for first 3 of every 5 steps

            active_ids = ["STU-OCCLUDED"] if is_visible else []
            engine.process_tracking_frame(active_ids, timestamp=base_time + step, dt=1.0)

        rec = engine.records["STU-OCCLUDED"]

        # Student should be marked PRESENT (cumulative ~24s > 15s threshold)
        self.assertEqual(rec.status, "PRESENT",
                         "Student with intermittent occlusions but sufficient cumulative presence must be PRESENT.")
        self.assertGreaterEqual(rec.cumulative_presence_seconds, 15.0)

        # Presence ratio should reflect partial visibility
        self.assertGreater(rec.presence_ratio, 0.0)
        self.assertLess(rec.presence_ratio, 1.0,
                        "Partially occluded student should have presence ratio < 100%.")

    def test_activity_6_3_short_participant_appearance_filtering(self):
        """
        EPIC 6 Activity 6.3 - Edge Case: Short Participant Appearances.
        Multiple brief visitors appearing for 1-4 seconds each should all be
        filtered as WALKBY_FILTERED and not corrupt the attendance roster.
        """
        from backend.core.presence_attendance import PresenceAttendanceEngine

        engine = PresenceAttendanceEngine(
            session_id="WALKBY-EDGE-TEST",
            min_sustained_seconds=15.0,
            walkby_threshold_seconds=8.0
        )
        engine.register_enrolled_students([
            {"id": "STU-REAL", "name": "Real Student", "seat": "Desk 1"},
        ])

        base_time = 6000.0
        # Real student present throughout 30s
        # 3 different visitors pop in briefly at different times
        for step in range(30):
            active = ["STU-REAL"]

            # Visitor A: steps 3-5 (3 seconds < 8s threshold)
            if 3 <= step <= 5:
                active.append("VISITOR-A")
            # Visitor B: steps 10-11 (2 seconds)
            if 10 <= step <= 11:
                active.append("VISITOR-B")
            # Visitor C: steps 20-23 (4 seconds)
            if 20 <= step <= 23:
                active.append("VISITOR-C")

            engine.process_tracking_frame(active, timestamp=base_time + step, dt=1.0)

        # Wait a few more steps with no visitors to trigger walkby classification
        for step in range(30, 40):
            engine.process_tracking_frame(["STU-REAL"], timestamp=base_time + step, dt=1.0)

        # Real student should be PRESENT
        self.assertEqual(engine.records["STU-REAL"].status, "PRESENT")

        # All visitors should be WALKBY_FILTERED
        for vid in ["VISITOR-A", "VISITOR-B", "VISITOR-C"]:
            self.assertIn(vid, engine.records,
                          f"{vid} should be tracked in records.")
            self.assertEqual(engine.records[vid].status, "WALKBY_FILTERED",
                             f"{vid} (brief appearance) must be WALKBY_FILTERED.")

        # CSV export must exclude walkbys
        csv_text = engine.export_attendance_csv()
        self.assertIn("STU-REAL", csv_text)
        self.assertNotIn("VISITOR-A", csv_text)
        self.assertNotIn("VISITOR-B", csv_text)
        self.assertNotIn("VISITOR-C", csv_text)

    def test_activity_6_3_intermittent_audio_input_handling(self):
        """
        EPIC 6 Activity 6.3 - Edge Case: Intermittent Audio Input.
        Tests that the system handles audio signal gaps (microphone disconnects,
        zero-energy frames, NaN values) gracefully without crashing or
        producing invalid scores.
        """
        from backend.audio.audio_analyzer import AudioSignalAnalyzer

        analyzer = AudioSignalAnalyzer()

        # Scenario 1: Zero energy (microphone muted/disconnected)
        res_zero = analyzer.process_acoustic_metrics(energy_rms=0.0, vad_active=False, rhythm_hint="SILENT_STUDY")
        self.assertIsNotNone(res_zero)
        self.assertFalse(res_zero["vad_active"])
        self.assertEqual(res_zero["speech_state"], "SILENCE")
        self.assertIsInstance(res_zero["noise_level_spl"], float)
        self.assertFalse(np.isnan(res_zero["noise_level_spl"]),
                          "SPL must not be NaN for zero energy.")
        self.assertFalse(np.isinf(res_zero["noise_level_spl"]),
                          "SPL must not be infinite for zero energy.")

        # Scenario 2: Very small energy (near-silent)
        res_tiny = analyzer.process_acoustic_metrics(energy_rms=0.00001, vad_active=False, rhythm_hint="SILENT_STUDY")
        self.assertIsNotNone(res_tiny)
        self.assertGreater(res_tiny["noise_level_spl"], 0.0,
                           "SPL should be clamped above 0 for near-zero energy.")

        # Scenario 3: Normal range recovery after silence
        res_normal = analyzer.process_acoustic_metrics(energy_rms=0.06, vad_active=True, rhythm_hint="QA_INTERACTION")
        self.assertTrue(res_normal["vad_active"])
        self.assertEqual(res_normal["speech_state"], "ACTIVE_SPEECH")

        # Scenario 4: Extreme clipping energy (microphone overload)
        res_clip = analyzer.process_acoustic_metrics(energy_rms=1.0, vad_active=True, rhythm_hint="COLLABORATIVE_BUZZ")
        self.assertIsNotNone(res_clip)
        self.assertLessEqual(res_clip["noise_level_spl"], 100.0,
                             "SPL must be clamped for clipping audio.")

    def test_activity_6_3_multimodal_fusion_edge_case_inputs(self):
        """
        EPIC 6 Activity 6.3 - Edge Case: Multimodal Fusion with extreme/missing inputs.
        Verifies fusion engine handles boundary values and produces valid composite indices.
        """
        engine = MultimodalFusionEngine()

        # Edge Case: All zeros (empty classroom, no audio)
        res1 = engine.fuse_signals(
            {"average_visual_attention": 0.0, "average_motion_energy": 0.0,
             "active_participants_count": 0, "inactivity_seconds": 300.0},
            {"rhythm_state": "SILENT_STUDY", "interaction_density": 0.0,
             "vad_active": False, "noise_level_spl": 30.0}
        )
        self.assertGreaterEqual(res1["engagement_index"], 0.0)
        self.assertLessEqual(res1["engagement_index"], 100.0)

        # Edge Case: All maximum values (fully engaged, very loud)
        res2 = engine.fuse_signals(
            {"average_visual_attention": 1.0, "average_motion_energy": 0.10,
             "active_participants_count": 30, "inactivity_seconds": 0.0},
            {"rhythm_state": "QA_INTERACTION", "interaction_density": 1.0,
             "vad_active": True, "noise_level_spl": 70.0,
             "participation_frequency": 5.0}
        )
        self.assertGreater(res2["engagement_index"], 60.0,
                           "Fully engaged scenario should yield high EI.")

        # Edge Case: Visual attention > 1.0 (percentage passed instead of ratio)
        res3 = engine.fuse_signals(
            {"average_visual_attention": 85.0, "average_motion_energy": 0.05,
             "active_participants_count": 5},
            {"rhythm_state": "INSTRUCTOR_MONOLOGUE", "vad_active": True}
        )
        self.assertGreaterEqual(res3["engagement_index"], 0.0)
        self.assertLessEqual(res3["engagement_index"], 100.0,
                             "Fusion must handle attention > 1.0 (percentage format) gracefully.")

        # Edge Case: Negative motion energy (sensor error)
        res4 = engine.fuse_signals(
            {"average_visual_attention": 0.70, "average_motion_energy": -0.05,
             "active_participants_count": 3},
            {"rhythm_state": "INSTRUCTOR_MONOLOGUE", "vad_active": True}
        )
        self.assertGreaterEqual(res4["engagement_index"], 0.0)
        self.assertLessEqual(res4["engagement_index"], 100.0)

    def test_activity_6_3_engagement_score_stability_under_stress(self):
        """
        EPIC 6 Activity 6.3 - Engagement Score Stability Under Stress.
        Runs a long simulated session (100+ segments) with varying conditions
        and verifies scores remain bounded, means are stable, and no outliers.
        """
        from backend.core.engagement_scoring import EngagementScoringEngine, ScoringThresholdConfig

        engine = EngagementScoringEngine(ScoringThresholdConfig())
        import random
        random.seed(42)

        packets = []
        for i in range(100):
            # Randomly vary all inputs within plausible classroom ranges
            packets.append({
                "average_visual_attention": random.uniform(0.3, 0.95),
                "average_motion_energy": random.uniform(0.01, 0.40),
                "presence_ratio_percent": random.uniform(50.0, 100.0),
                "inactivity_seconds": random.uniform(0.0, 120.0),
                "noise_level_spl": random.uniform(40.0, 80.0),
                "rhythm_state": random.choice(["INSTRUCTOR_MONOLOGUE", "QA_INTERACTION",
                                                "COLLABORATIVE_BUZZ", "SILENT_STUDY"]),
                "speech_state": random.choice(["ACTIVE_SPEECH", "SILENCE", "BACKGROUND_NOISE"]),
                "participation_frequency": random.uniform(0.0, 3.0),
                "consecutive_silence_sec": random.uniform(0.0, 30.0),
            })

        profile = engine.generate_temporal_profile(packets, interval_seconds=10.0, session_id="STRESS-TEST")

        # 1. All segments must be valid
        self.assertEqual(profile.total_segments, 100)
        for seg in profile.segments:
            self.assertGreaterEqual(seg.composite_score, 0.0)
            self.assertLessEqual(seg.composite_score, 100.0)
            self.assertIn(seg.engagement_level, ["HIGH", "MODERATE", "LOW", "CRITICAL_DISENGAGED"])
            self.assertIsNotNone(seg.factor_attribution)
            self.assertIsNotNone(seg.explainable_summary)
            self.assertGreater(len(seg.explainable_summary), 10)

        # 2. Aggregate metrics must be valid
        self.assertGreater(profile.mean_score, 0.0)
        self.assertLessEqual(profile.mean_score, 100.0)
        self.assertLessEqual(profile.min_score, profile.mean_score)
        self.assertGreaterEqual(profile.max_score, profile.mean_score)

        # 3. Fluctuation metrics must be computed
        self.assertGreaterEqual(profile.fluctuation_metrics.stability_score, 0.0)
        self.assertLessEqual(profile.fluctuation_metrics.stability_score, 100.0)
        self.assertGreaterEqual(profile.fluctuation_metrics.variance, 0.0)

        # 4. Downstream summary must be populated
        self.assertIn("session_id", profile.downstream_session_summary)
        self.assertIn("overall_status", profile.downstream_session_summary)

    def test_activity_6_3_analytics_output_interpretability(self):
        """
        EPIC 6 Activity 6.3 - Analytics Output Interpretability.
        Validates that generated analytics outputs (session summaries, teaching
        suggestions, student profiles) are complete, well-structured, and human-readable.
        """
        from backend.core.engagement_scoring import EngagementScoringEngine, ScoringThresholdConfig

        engine = EngagementScoringEngine(ScoringThresholdConfig())

        # Create a mix of high and low engagement packets
        packets = []
        for i in range(15):
            if i < 5:
                # High engagement phase
                packets.append({
                    "average_visual_attention": 0.90,
                    "average_motion_energy": 0.08,
                    "presence_ratio_percent": 95.0,
                    "inactivity_seconds": 2.0,
                    "noise_level_spl": 55.0,
                    "rhythm_state": "QA_INTERACTION",
                    "speech_state": "ACTIVE_SPEECH",
                    "participation_frequency": 2.0,
                })
            elif i < 10:
                # Low engagement phase (disengagement)
                packets.append({
                    "average_visual_attention": 0.25,
                    "average_motion_energy": 0.01,
                    "presence_ratio_percent": 60.0,
                    "inactivity_seconds": 80.0,
                    "noise_level_spl": 40.0,
                    "rhythm_state": "SILENT_STUDY",
                    "speech_state": "SILENCE",
                    "participation_frequency": 0.0,
                    "consecutive_silence_sec": 25.0,
                })
            else:
                # Recovery phase
                packets.append({
                    "average_visual_attention": 0.80,
                    "average_motion_energy": 0.06,
                    "presence_ratio_percent": 88.0,
                    "inactivity_seconds": 5.0,
                    "noise_level_spl": 58.0,
                    "rhythm_state": "INSTRUCTOR_MONOLOGUE",
                    "speech_state": "ACTIVE_SPEECH",
                    "participation_frequency": 1.0,
                })

        profile = engine.generate_temporal_profile(packets, interval_seconds=10.0, session_id="INTERPRET-TEST")

        # 1. Session summary must be complete and interpretable
        summary = engine.generate_session_summary(profile)
        self.assertIn("session_id", summary)
        self.assertIn("total_segments", summary)
        self.assertIn("mean_engagement_index", summary)
        self.assertIn("distribution", summary)
        self.assertIn("pedagogical_takeaway", summary)
        self.assertGreater(len(summary["pedagogical_takeaway"]), 20,
                           "Pedagogical takeaway must be a meaningful sentence.")

        # Distribution percentages must sum to ~100%
        dist = summary["distribution"]
        total_pct = dist["high_engagement_percent"] + dist["moderate_engagement_percent"] + dist["low_engagement_percent"]
        self.assertAlmostEqual(total_pct, 100.0, delta=1.0,
                               msg="Engagement distribution percentages must sum to ~100%.")

        # 2. Teaching suggestions must be actionable and non-empty
        suggestions = engine.generate_downstream_teaching_suggestions(profile)
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0, "Suggestions must be generated for mixed engagement session.")
        for sug in suggestions:
            self.assertIn("title", sug)
            self.assertIn("alert_level", sug)
            self.assertIn("rationale", sug)
            self.assertIn("action", sug)
            self.assertGreater(len(sug["title"]), 3)
            self.assertGreater(len(sug["action"]), 10)

        # 3. Student analytics must produce valid profiles
        student_packets = [
            {"student_id": "STU-A", "display_name": "Alice",
             "average_visual_attention": 0.90, "average_motion_energy": 0.06,
             "presence_ratio_percent": 95.0, "inactivity_seconds": 5.0,
             "noise_level_spl": 55.0, "rhythm_state": "INSTRUCTOR_MONOLOGUE",
             "participation_frequency": 1.0},
            {"student_id": "STU-B", "display_name": "Bob",
             "average_visual_attention": 0.30, "average_motion_energy": 0.50,
             "presence_ratio_percent": 45.0, "inactivity_seconds": 100.0,
             "noise_level_spl": 72.0, "rhythm_state": "COLLABORATIVE_BUZZ",
             "participation_frequency": 0.2},
        ]
        analytics = engine.generate_student_analytics(student_packets)
        self.assertEqual(analytics["total_students"], 2)
        for prof in analytics["profiles"]:
            self.assertIn("student_id", prof)
            self.assertIn("engagement_score", prof)
            self.assertIn("participation_quadrant", prof)
            self.assertGreaterEqual(prof["engagement_score"], 0.0)
            self.assertLessEqual(prof["engagement_score"], 100.0)

    def test_activity_6_3_attendance_accuracy_end_to_end(self):
        """
        EPIC 6 Activity 6.3 - Attendance Marking Accuracy End-to-End.
        Verifies that the complete attendance pipeline produces correct status
        classifications for various student attendance patterns.
        """
        from backend.core.presence_attendance import PresenceAttendanceEngine

        engine = PresenceAttendanceEngine(
            session_id="ACCURACY-TEST",
            min_sustained_seconds=20.0,
            walkby_threshold_seconds=8.0,
            late_cutoff_seconds=60.0
        )
        engine.register_enrolled_students([
            {"id": "STU-FULL", "name": "Full Attendee", "seat": "Desk 1"},
            {"id": "STU-LATE", "name": "Late Arrival", "seat": "Desk 2"},
            {"id": "STU-BRIEF", "name": "Brief Visit", "seat": "Desk 3"},
            {"id": "STU-ABSENT", "name": "Never Appeared", "seat": "Desk 4"},
        ])

        base = 7000.0
        # Simulate 120 seconds of session
        for step in range(120):
            active = []

            # STU-FULL: present from step 0 onwards
            active.append("STU-FULL")

            # STU-LATE: arrives at step 70 (after 60s late cutoff)
            if step >= 70:
                active.append("STU-LATE")

            # STU-BRIEF: only steps 10-15 (6 seconds < 8s walkby threshold)
            if 10 <= step <= 15:
                active.append("STU-BRIEF")

            # STU-ABSENT: never appears

            engine.process_tracking_frame(active, timestamp=base + step, dt=1.0)

        # Validate statuses
        self.assertEqual(engine.records["STU-FULL"].status, "PRESENT",
                         "Full attendee must be PRESENT.")
        self.assertGreaterEqual(engine.records["STU-FULL"].cumulative_presence_seconds, 100.0)

        self.assertIn(engine.records["STU-LATE"].status, ["LATE", "PRESENT"],
                      "Late arrival must be LATE or PRESENT (depending on threshold interplay).")
        self.assertGreaterEqual(engine.records["STU-LATE"].cumulative_presence_seconds, 20.0)

        self.assertEqual(engine.records["STU-BRIEF"].status, "WALKBY_FILTERED",
                         "Brief visitor must be WALKBY_FILTERED.")

        self.assertEqual(engine.records["STU-ABSENT"].status, "ABSENT",
                         "Never-appeared student must remain ABSENT.")
        self.assertEqual(engine.records["STU-ABSENT"].cumulative_presence_seconds, 0.0)

        # Structured logs should include only real attendees
        logs = engine.get_structured_attendance_logs(exclude_walkbys=True)
        log_ids = [l["student_id"] for l in logs]
        self.assertIn("STU-FULL", log_ids)
        self.assertNotIn("STU-BRIEF", log_ids,
                          "Walkby-filtered students must be excluded from official logs.")

    def test_activity_6_3_classroom_preset_threshold_edge_cases(self):
        """
        EPIC 6 Activity 6.3 - Parameter Adjustments: Classroom Presets.
        Verifies that all classroom presets produce valid scoring and that
        custom threshold updates don't break the scoring pipeline.
        """
        from backend.core.engagement_scoring import (
            EngagementScoringEngine, ScoringThresholdConfig, ClassroomPreset
        )

        presets = [
            ClassroomPreset.LECTURE_STANDARD,
            ClassroomPreset.INTERACTIVE_DISCUSSION,
            ClassroomPreset.HANDS_ON_LAB,
            ClassroomPreset.QUIET_EXAM,
        ]

        sample_visual = {
            "average_visual_attention": 0.70,
            "average_motion_energy": 0.10,
            "presence_ratio_percent": 80.0,
            "inactivity_seconds": 20.0,
        }
        sample_audio = {
            "noise_level_spl": 60.0,
            "rhythm_state": "INSTRUCTOR_MONOLOGUE",
            "speech_state": "ACTIVE_SPEECH",
            "participation_frequency": 1.0,
        }

        preset_scores = {}
        for preset_name in presets:
            config = ScoringThresholdConfig()
            config.apply_preset(preset_name)

            # Weights must sum to 1.0 after applying preset
            total_weight = config.weight_visual + config.weight_movement + config.weight_inactivity + config.weight_speech
            self.assertAlmostEqual(total_weight, 1.0, delta=0.01,
                                   msg=f"Weights must sum to 1.0 for preset {preset_name}.")

            engine = EngagementScoringEngine(config)
            seg = engine.score_segment(sample_visual, sample_audio, start_time=1000.0, duration_seconds=10.0)
            preset_scores[preset_name] = seg.composite_score

            self.assertGreaterEqual(seg.composite_score, 0.0)
            self.assertLessEqual(seg.composite_score, 100.0)
            self.assertIsNotNone(seg.factor_attribution)

        # Custom threshold update test
        config = ScoringThresholdConfig()
        config.update_thresholds({
            "weight_visual": 0.50,
            "weight_speech": 0.50,
            "weight_movement": 0.0,
            "weight_inactivity": 0.0,
            "optimal_gaze_threshold": 0.50
        })
        self.assertEqual(config.preset_name, ClassroomPreset.CUSTOM)

        engine = EngagementScoringEngine(config)
        seg = engine.score_segment(sample_visual, sample_audio, start_time=1000.0, duration_seconds=10.0)
        self.assertGreaterEqual(seg.composite_score, 0.0)
        self.assertLessEqual(seg.composite_score, 100.0)

    def test_activity_6_3_face_tracking_occlusion_recovery_stability(self):
        """
        EPIC 6 Activity 6.3 - Edge Case: Face Tracking Through Occlusion Recovery.
        Verifies that the face tracker maintains identity through multiple
        occlusion/recovery cycles without creating duplicate tracks.
        """
        from backend.core.face_tracker import FaceTracker

        tracker = FaceTracker(max_disappeared=5, max_distance=60.0, privacy_blur=True)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Cycle 1: Initial appearance
        dets = [{"bbox": (200, 200, 50, 50), "score": 1.0, "centroid": (225, 225)}]
        _, tracks = tracker.process_frame(frame, detections=dets, timestamp=2000.0)
        self.assertEqual(len(tracks), 1)
        original_id = tracks[0]["track_id"]

        # Cycle 2-3: Visible
        for t in range(1, 3):
            dets = [{"bbox": (200 + t*2, 200, 50, 50), "score": 1.0, "centroid": (225 + t*2, 225)}]
            _, tracks = tracker.process_frame(frame, detections=dets, timestamp=2000.0 + t)

        # Cycle 4-6: Occluded (3 frames, < max_disappeared=5)
        for t in range(3, 6):
            _, tracks = tracker.process_frame(frame, detections=[], timestamp=2000.0 + t)
            self.assertEqual(len(tracks), 1, "Track must persist through occlusion.")
            self.assertEqual(tracks[0]["track_id"], original_id)

        # Cycle 7: Reappears nearby
        dets = [{"bbox": (210, 200, 50, 50), "score": 1.0, "centroid": (235, 225)}]
        _, tracks = tracker.process_frame(frame, detections=dets, timestamp=2006.0)
        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0]["track_id"], original_id,
                         "Track ID must survive occlusion recovery cycle.")
        self.assertEqual(tracks[0]["status"], "ACTIVE")

        # Cycle 8-10: Second occlusion cycle
        for t in range(7, 10):
            _, tracks = tracker.process_frame(frame, detections=[], timestamp=2000.0 + t)
        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0]["track_id"], original_id)

        # Cycle 11: Re-emerges again
        dets = [{"bbox": (215, 203, 50, 50), "score": 1.0, "centroid": (240, 228)}]
        _, tracks = tracker.process_frame(frame, detections=dets, timestamp=2010.0)
        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0]["track_id"], original_id,
                         "Track identity must persist through multiple occlusion cycles.")

    def test_activity_6_3_cross_modal_coherence_edge_cases(self):
        """
        EPIC 6 Activity 6.3 - Edge Case: Cross-Modal Coherence Validation.
        Tests that cross-modal correlation and coherence metrics are within
        valid ranges for contradictory signal combinations.
        """
        engine = MultimodalFusionEngine()

        # Scenario 1: Visual high, Audio low (student watching but no interaction)
        res1 = engine.synchronize_and_fuse(
            {"average_visual_attention": 0.95, "average_motion_energy": 0.05,
             "active_participants_count": 5},
            {"rhythm_state": "SILENT_STUDY", "vad_active": False,
             "noise_level_spl": 35.0, "interaction_density": 0.0}
        )
        self.assertGreaterEqual(res1.cross_modal_coherence, 0.0)
        self.assertLessEqual(res1.cross_modal_coherence, 1.0)

        # Scenario 2: Visual low, Audio high (students not looking but talking)
        res2 = engine.synchronize_and_fuse(
            {"average_visual_attention": 0.15, "average_motion_energy": 0.40,
             "active_participants_count": 10},
            {"rhythm_state": "COLLABORATIVE_BUZZ", "vad_active": True,
             "noise_level_spl": 72.0, "interaction_density": 0.85,
             "participation_frequency": 3.0}
        )
        self.assertGreaterEqual(res2.cross_modal_coherence, 0.0)
        self.assertLessEqual(res2.cross_modal_coherence, 1.0)

        # Scenario 3: Both channels aligned high
        res3 = engine.synchronize_and_fuse(
            {"average_visual_attention": 0.90, "average_motion_energy": 0.08,
             "active_participants_count": 8},
            {"rhythm_state": "QA_INTERACTION", "vad_active": True,
             "noise_level_spl": 60.0, "interaction_density": 0.80,
             "participation_frequency": 2.5}
        )
        self.assertGreaterEqual(res3.cross_modal_coherence, 0.5,
                                "Aligned high signals should produce high coherence.")

        # Cross-modal correlation must be in [-1, 1]
        self.assertGreaterEqual(res3.cross_modal_correlation, -1.0)
        self.assertLessEqual(res3.cross_modal_correlation, 1.0)

        # Dominant modality must be a valid category
        for res in [res1, res2, res3]:
            self.assertIn(res.dominant_modality,
                          ["VISUAL_DOMINANT", "AUDIO_DOMINANT", "BALANCED"])

    def test_activity_6_3_database_edge_cases_and_data_integrity(self):
        """
        EPIC 6 Activity 6.3 - Edge Case: Database Operations Under Edge Conditions.
        Validates database handles empty sessions, duplicate entries, and
        boundary queries gracefully.
        """
        # 1. Empty session engagement history
        history = self.db.get_session_engagement_history("NONEXISTENT-SESSION-XYZ")
        self.assertIsInstance(history, list)
        self.assertEqual(len(history), 0,
                         "Non-existent session should return empty history list.")

        # 2. Empty session attendance
        attendance = self.db.get_session_attendance("NONEXISTENT-SESSION-XYZ")
        self.assertIsInstance(attendance, list)
        self.assertEqual(len(attendance), 0)

        # 3. Recording engagement interval for current test session
        ts = time.time()
        self.db.record_engagement_interval(
            self.session_id, 0.80, 0.05, 0.50, "INSTRUCTOR_MONOLOGUE", 75.0, 2, ts
        )
        self.db.record_engagement_interval(
            self.session_id, 0.85, 0.08, 0.60, "QA_INTERACTION", 80.0, 2, ts + 10
        )

        history = self.db.get_session_engagement_history(self.session_id)
        self.assertGreaterEqual(len(history), 2,
                                "Recorded intervals should be retrievable.")

        # 4. Pseudonym determinism and uniqueness
        p1 = self.db.generate_pseudonym("STU-001")
        p2 = self.db.generate_pseudonym("STU-001")
        p3 = self.db.generate_pseudonym("STU-002")
        self.assertEqual(p1, p2, "Same input must produce same pseudonym.")
        self.assertNotEqual(p1, p3, "Different inputs must produce different pseudonyms.")

    def test_activity_6_3_temporal_profile_serialization_integrity(self):
        """
        EPIC 6 Activity 6.3 - Output Validation: Temporal Profile Serialization.
        Ensures the entire temporal profile can be serialized to dict/JSON
        without errors or data loss.
        """
        import json
        from backend.core.engagement_scoring import EngagementScoringEngine, ScoringThresholdConfig

        engine = EngagementScoringEngine(ScoringThresholdConfig())

        packets = []
        for i in range(10):
            packets.append({
                "average_visual_attention": 0.70 + (i * 0.02),
                "average_motion_energy": 0.06,
                "presence_ratio_percent": 85.0,
                "inactivity_seconds": 10.0,
                "noise_level_spl": 55.0,
                "rhythm_state": "INSTRUCTOR_MONOLOGUE",
                "speech_state": "ACTIVE_SPEECH",
                "participation_frequency": 1.0,
            })

        profile = engine.generate_temporal_profile(packets, interval_seconds=10.0, session_id="SERIAL-TEST")

        # Serialize to dict
        profile_dict = profile.to_dict()
        self.assertIsInstance(profile_dict, dict)
        self.assertIn("segments", profile_dict)
        self.assertIn("fluctuation_metrics", profile_dict)
        self.assertIn("peak_periods", profile_dict)
        self.assertIn("disengagement_phases", profile_dict)
        self.assertEqual(len(profile_dict["segments"]), 10)

        # Serialize to JSON string (must not raise)
        json_str = json.dumps(profile_dict, default=str)
        self.assertGreater(len(json_str), 100)

        # Parse back and verify key fields
        parsed = json.loads(json_str)
        self.assertEqual(parsed["session_id"], "SERIAL-TEST")
        self.assertEqual(parsed["total_segments"], 10)
        self.assertAlmostEqual(parsed["mean_score"], profile.mean_score, delta=0.01)

    def test_hybrid_enrollment_and_track_linking(self):
        """Verifies 3-Way Hybrid Student Enrollment and Live Identity Linking workflow."""
        from backend.attendance.sustained_presence import SustainedPresenceEngine

        engine = SustainedPresenceEngine(
            db=self.db,
            session_id=self.session_id,
            min_sustained_seconds=10.0,
            sustained_ratio=0.5
        )

        # 1. Unrecognized person appears on webcam -> TRK-042
        engine.process_frame_tracks(active_student_ids=["TRK-042"], dt=5.0)

        roster = {r["student_id"]: r for r in engine.get_live_attendance_roster()}
        self.assertIn("TRK-042", roster)
        self.assertTrue(roster["TRK-042"]["is_unlinked_track"])
        self.assertGreaterEqual(roster["TRK-042"]["active_seconds"], 5.0)

        # 2. Database student enrollment (Option B)
        new_stu = self.db.enroll_student("STU-999", "Ada Lovelace", "Desk 9")
        self.assertEqual(new_stu["student_id"], "STU-999")
        enrolled = self.db.get_enrolled_students()
        self.assertIn("STU-999", [s["id"] for s in enrolled])

        # 3. Seamless track linking & presence merge (Option A / B)
        success = engine.link_track_to_student("TRK-042", "STU-999", display_name="Ada Lovelace", seat="Desk 9")
        self.assertTrue(success)

        # Roster verification: TRK-042 removed from anonymous list, STU-999 now has the accumulated presence
        updated_roster = {r["student_id"]: r for r in engine.get_live_attendance_roster()}
        self.assertNotIn("TRK-042", updated_roster)
        self.assertIn("STU-999", updated_roster)
        self.assertEqual(updated_roster["STU-999"]["display_name"], "Ada Lovelace")
        self.assertFalse(updated_roster["STU-999"]["is_unlinked_track"])
        self.assertGreaterEqual(updated_roster["STU-999"]["active_seconds"], 5.0)

    def test_invalid_identity_link_payloads(self):
        """Phase 4 Edge Case 1: Verifies link-identity endpoint rejects invalid payloads with clean 400/422 responses and zero 500 errors."""
        from fastapi.testclient import TestClient
        from backend.api.server import app

        with TestClient(app) as client:
            # 1. Non-existent tracker ID
            res = client.post("/api/v1/attendance/link-identity", json={
                "track_id": "TRK-999-NONEXISTENT",
                "student_id": "STU-001"
            })
            self.assertEqual(res.status_code, 400)
            self.assertEqual(res.json()["status"], "error")
            self.assertIn("not found", res.json()["message"].lower())

            # 2. Missing track_id
            res = client.post("/api/v1/attendance/link-identity", json={
                "student_id": "STU-001"
            })
            self.assertEqual(res.status_code, 400)
            self.assertIn("missing", res.json()["message"].lower())

            # 3. Missing / empty student_id
            res = client.post("/api/v1/attendance/link-identity", json={
                "track_id": "TRK-001",
                "student_id": ""
            })
            self.assertEqual(res.status_code, 400)

            # 4. enroll_new is True but student_name is empty
            from backend.api.server import presence_engine
            presence_engine.process_frame_tracks(["TRK-TEMP-99"], dt=1.0)
            res = client.post("/api/v1/attendance/link-identity", json={
                "track_id": "TRK-TEMP-99",
                "student_id": "STU-NEW-888",
                "enroll_new": True,
                "student_name": ""
            })
            self.assertEqual(res.status_code, 400)
            self.assertIn("student_name", res.json()["message"].lower())

            # 5. Non-dict / malformed payload
            res = client.post("/api/v1/attendance/link-identity", content="not json", headers={"Content-Type": "application/json"})
            self.assertIn(res.status_code, [400, 422])

    def test_zero_loss_attendance_time_and_timestamp_merging(self):
        """Phase 4 Edge Case 2: Simulates TRK-xxx accumulating time, verifies 100% time & timestamp preservation upon link."""
        from backend.attendance.sustained_presence import SustainedPresenceEngine

        engine = SustainedPresenceEngine(
            db=self.db,
            session_id=self.session_id,
            min_sustained_seconds=20.0,
            sustained_ratio=0.5
        )

        t_base = time.time() - 100.0

        # Simulate TRK-077 arriving first at t_base and being active for 15.0 seconds
        engine.process_frame_tracks(["TRK-077"], dt=15.0)
        trk_rec = engine.records["TRK-077"]
        trk_rec.first_seen_time = t_base
        self.assertAlmostEqual(trk_rec.total_active_seconds, 15.0, delta=0.01)

        # Simulate STU-001 arriving at t_base + 10.0 and active for 10.0 seconds
        engine.process_frame_tracks(["STU-001"], dt=10.0)
        stu_rec = engine.records["STU-001"]
        stu_rec.first_seen_time = t_base + 10.0
        self.assertAlmostEqual(stu_rec.total_active_seconds, 10.0, delta=0.01)

        # Merge TRK-077 into STU-001
        success = engine.link_track_to_student("TRK-077", "STU-001", display_name="Alice Turing", seat="Desk 1")
        self.assertTrue(success)

        # Verify zero loss
        merged_rec = engine.records["STU-001"]
        self.assertAlmostEqual(merged_rec.total_active_seconds, 25.0, delta=0.01, msg="Cumulative active seconds must be 15.0 + 10.0 = 25.0")
        self.assertEqual(merged_rec.first_seen_time, t_base, "Earliest first_seen_time must be preserved.")
        self.assertNotIn("TRK-077", engine.records)

    def test_websocket_audio_resilience(self):
        """Phase 4 Edge Case 3: Verifies WebSocket /ws/audio resilience against rapid disconnects, empty payloads, and clipping."""
        from fastapi.testclient import TestClient
        from backend.api.server import app

        with TestClient(app) as client:
            # 1. Rapid connect and disconnect
            with client.websocket_connect("/ws/audio") as ws:
                pass  # Immediate disconnect

            # 2. Empty byte payload and odd-length PCM buffer
            with client.websocket_connect("/ws/audio") as ws:
                ws.send_bytes(b"")  # Zero-byte payload
                ws.send_bytes(b"\x00\x01\x02\x03\x04")  # 5-byte odd buffer

                # 3. Extreme clipping PCM array (int16 extremes)
                clipping_pcm = (np.ones(1600, dtype=np.int16) * 32767).tobytes()
                ws.send_bytes(clipping_pcm)
                resp = ws.receive_json()
                self.assertEqual(resp["type"], "audio_metrics")
                self.assertIn("metrics", resp)
                self.assertIn("rms_energy", resp["metrics"])

                # 4. JSON text message with client_disconnect
                ws.send_text(json.dumps({"type": "client_disconnect"}))

    def test_empty_vs_populated_student_db_biometric_verification(self):
        """Phase 4 Edge Case 4: Verifies FaceRecognizer and CentroidFaceTracker behave cleanly with 0 and populated student_db."""
        import tempfile
        import shutil
        from backend.core.face_recognition import FaceRecognizer
        from backend.vision.face_tracker import CentroidFaceTracker

        temp_db = tempfile.mkdtemp(prefix="test_student_db_")
        try:
            # 1. Empty database verification
            recognizer = FaceRecognizer(db_path=temp_db)
            self.assertEqual(len(recognizer.known_embeddings), 0)

            dummy_face = np.zeros((64, 64, 3), dtype=np.uint8)
            cv2.rectangle(dummy_face, (10, 10), (50, 50), (200, 200, 200), -1)

            # Recognize on empty DB should return [] without throwing
            res = recognizer.recognize(dummy_face)
            self.assertEqual(res, [])

            # Tracker integration with empty DB
            tracker = CentroidFaceTracker(face_recognizer=recognizer, privacy_blur=False)
            dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            # Add simulated detection
            sim_meta = [{"bbox": (100, 100, 80, 80), "student_id": None}]
            _, active = tracker.detect_and_track(dummy_frame, simulated_meta=sim_meta)
            self.assertEqual(len(active), 1)
            self.assertTrue(active[0].student_id.startswith("TRK-"))

            # 2. Populated database verification
            registered = recognizer.register_student(dummy_face, student_id="STU-777", display_name="Grace Hopper")
            self.assertTrue(registered)
            self.assertIn("STU-777", recognizer.known_embeddings)

            # Recognize sample face - should find STU-777
            res_populated = recognizer.recognize(dummy_face)
            self.assertGreaterEqual(len(res_populated), 1)
            self.assertEqual(res_populated[0]["student_id"], "STU-777")
            self.assertTrue(res_populated[0]["verified"])
        finally:
            shutil.rmtree(temp_db, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()





