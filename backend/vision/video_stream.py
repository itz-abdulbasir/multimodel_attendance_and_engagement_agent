"""
Multimodal Attendance & Engagement Agent - Video Stream Ingestion
Epic 2: Task 3 (TASK-03) - Multi-Source Video Stream Ingestion Engine
"""

import time
import math
import random
import threading
from typing import Generator, Optional, Tuple, Dict, Any, List
import numpy as np
import cv2

class SimulatedStudent:
    def __init__(self, student_id: str, name: str, base_x: int, base_y: int, seat: str):
        self.student_id = student_id
        self.name = name
        self.base_x = base_x
        self.base_y = base_y
        self.seat = seat
        
        # State dynamics
        self.yaw = 0.0      # -45 to +45 deg (looking left/right)
        self.pitch = 0.0    # -30 to +30 deg (looking up/down)
        self.attentive = True
        self.motion_energy = 0.05
        self.hand_raised = False
        self.present = True
        self.color = (
            random.randint(60, 180),
            random.randint(80, 200),
            random.randint(120, 240)
        )
        self.last_state_change = time.time()
        self.behavior_profile = random.choice(["high_attentive", "moderate", "fidgety", "occasional_distracted"])

    def update(self, session_time: float, acoustic_state: str) -> None:
        now = time.time()
        dt = now - self.last_state_change
        
        # Behavior state transition
        if dt > random.uniform(3.0, 8.0):
            self.last_state_change = now
            if self.behavior_profile == "high_attentive":
                self.attentive = random.random() > 0.12
            elif self.behavior_profile == "moderate":
                self.attentive = random.random() > 0.28
            elif self.behavior_profile == "fidgety":
                self.attentive = random.random() > 0.45
            else: # occasional_distracted
                self.attentive = random.random() > 0.40

            # Hand raise during Q&A
            if acoustic_state == "QA_INTERACTION" and random.random() > 0.65:
                self.hand_raised = True
            else:
                self.hand_raised = False

        # Natural micro-movement
        if self.attentive:
            target_yaw = random.uniform(-10.0, 10.0)
            target_pitch = random.uniform(-8.0, 8.0)
            self.motion_energy = max(0.02, min(0.20, self.motion_energy + random.uniform(-0.02, 0.03)))
        else:
            # Distracted: looking at phone/laptop or whispering to peer
            target_yaw = random.choice([-32.0, 32.0, random.uniform(-35.0, 35.0)])
            target_pitch = random.choice([25.0, -18.0, 30.0]) # looking down
            self.motion_energy = max(0.08, min(0.60, self.motion_energy + random.uniform(-0.05, 0.08)))

        # Smooth interpolation
        self.yaw += (target_yaw - self.yaw) * 0.15
        self.pitch += (target_pitch - self.pitch) * 0.15


class VideoStreamEngine:
    """Multi-source stream ingestion supporting Webcam, Video File, and Synthetic Classroom Stream."""

    def __init__(self, source_type: str = "simulated", video_path: Optional[str] = None,
                 webcam_index: int = 0, target_fps: int = 15, width: int = 640, height: int = 480):
        self.source_type = source_type
        self.video_path = video_path
        self.webcam_index = webcam_index
        self.target_fps = target_fps
        self.width = width
        self.height = height
        
        from backend.core.camera_service import CameraService
        self.camera_service: Optional[CameraService] = None
        self.cap: Optional[cv2.VideoCapture] = None
        self.running = False
        self.current_frame: Optional[np.ndarray] = None
        self.frame_lock = threading.Lock()
        self.frame_counter = 0
        self.start_time = time.time()
        
        # Classroom students for simulation
        self.simulated_students: List[SimulatedStudent] = []
        self.walkby_person: Optional[Dict[str, Any]] = None
        self._init_simulation_students()

    def _init_simulation_students(self) -> None:
        """Seed a standard 8-student classroom layout with 2 rows of 4 desks."""
        seats = [
            ("STU-101", "Emma Watson", 120, 180, "Row 1 - Left"),
            ("STU-102", "Liam Smith", 240, 180, "Row 1 - Center L"),
            ("STU-103", "Sophia Chen", 380, 180, "Row 1 - Center R"),
            ("STU-104", "Noah Patel", 500, 180, "Row 1 - Right"),
            ("STU-105", "Olivia Brown", 100, 320, "Row 2 - Left"),
            ("STU-106", "Ethan Davis", 230, 320, "Row 2 - Center L"),
            ("STU-107", "Ava Miller", 400, 320, "Row 2 - Center R"),
            ("STU-108", "Lucas Garcia", 520, 320, "Row 2 - Right"),
        ]
        self.simulated_students = [
            SimulatedStudent(sid, name, x, y, seat) for sid, name, x, y, seat in seats
        ]

    def start(self) -> None:
        self.running = True
        from backend.core.camera_service import CameraService
        if self.source_type in ["webcam", "file"]:
            self.camera_service = CameraService(
                camera_id=self.webcam_index,
                video_path=self.video_path,
                fps=self.target_fps,
                width=self.width,
                height=self.height
            )
            self.camera_service.start()
            self.cap = self.camera_service.cap

    def stop(self) -> None:
        self.running = False
        if self.camera_service:
            self.camera_service.stop()
            self.camera_service = None
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

    def set_source(self, source_type: str, video_path: Optional[str] = None, webcam_index: int = 0) -> None:
        self.stop()
        self.source_type = source_type
        self.video_path = video_path
        self.webcam_index = webcam_index
        self.start()

    def read_frame(self, acoustic_state: str = "INSTRUCTOR_MONOLOGUE") -> Tuple[bool, np.ndarray, List[Dict[str, Any]]]:
        """
        Returns:
            (success, frame_bgr, ground_truth_or_detected_metadata)
        """
        self.frame_counter += 1
        elapsed = time.time() - self.start_time

        if self.source_type in ["webcam", "file"] and self.camera_service and self.camera_service.is_running:
            frame = self.camera_service.get_frame()
            if frame is not None:
                with self.frame_lock:
                    self.current_frame = frame.copy()
                return True, frame, []
        elif self.source_type in ["webcam", "file"] and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (self.width, self.height))
                with self.frame_lock:
                    self.current_frame = frame.copy()
                return True, frame, []
            elif self.source_type == "file":
                # Loop video file
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if ret:
                    frame = cv2.resize(frame, (self.width, self.height))
                    return True, frame, []

        # Default high-fidelity simulation engine
        frame, meta = self._generate_simulated_frame(elapsed, acoustic_state)
        with self.frame_lock:
            self.current_frame = frame.copy()
        return True, frame, meta

    def _generate_simulated_frame(self, elapsed: float, acoustic_state: str) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """Synthesize a clean, photorealistic classroom scene with student entities."""
        # Create a modern smart classroom background (dark academy slate gradient)
        h, w = self.height, self.width
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Classroom wall and chalkboard/screen gradient
        for y in range(h):
            ratio = y / h
            r = int(18 + 12 * ratio)
            g = int(24 + 16 * ratio)
            b = int(36 + 22 * ratio)
            frame[y, :] = (b, g, r)

        # Classroom Smartboard / Projection screen in top center
        cv2.rectangle(frame, (160, 20), (480, 110), (45, 52, 65), -1)
        cv2.rectangle(frame, (160, 20), (480, 110), (70, 85, 110), 2)
        cv2.putText(frame, "LECTURE: MACHINE LEARNING & MULTIMODAL AI", (175, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 220, 240), 1, cv2.LINE_AA)
        cv2.putText(frame, f"Session Time: {int(elapsed // 60):02d}:{int(elapsed % 60):02d}", (175, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (150, 180, 200), 1, cv2.LINE_AA)
        cv2.putText(frame, f"Acoustic Rhythm: {acoustic_state}", (175, 95),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (120, 220, 150), 1, cv2.LINE_AA)

        # Classroom Desks (Perspectives)
        # Row 1 Desks
        cv2.rectangle(frame, (60, 210), (580, 235), (32, 40, 52), -1)
        cv2.line(frame, (60, 210), (580, 210), (60, 75, 95), 2)
        # Row 2 Desks
        cv2.rectangle(frame, (40, 350), (600, 385), (28, 36, 48), -1)
        cv2.line(frame, (40, 350), (600, 350), (55, 70, 90), 2)

        metadata: List[Dict[str, Any]] = []

        # Render each student entity
        for student in self.simulated_students:
            student.update(elapsed, acoustic_state)
            
            # Head position & offset with yaw/pitch
            hx = int(student.base_x + math.sin(math.radians(student.yaw)) * 14)
            hy = int(student.base_y + math.sin(math.radians(student.pitch)) * 8)
            radius = 28 if "Row 1" in student.seat else 34

            # Body / Torso
            torso_top = hy + radius - 4
            cv2.ellipse(frame, (hx, torso_top + 35), (radius + 12, 35), 0, 180, 360, student.color, -1)

            # Head Circle
            cv2.circle(frame, (hx, hy), radius, (210, 195, 180), -1)
            cv2.circle(frame, (hx, hy), radius, (130, 115, 100), 2)

            # Hair
            cv2.ellipse(frame, (hx, hy - int(radius * 0.4)), (radius, int(radius * 0.65)), 0, 180, 360, (40, 30, 25), -1)

            # Eyes (simulate gaze & head direction)
            eye_offset_x = int(math.sin(math.radians(student.yaw)) * (radius * 0.45))
            eye_offset_y = int(math.sin(math.radians(student.pitch)) * (radius * 0.35))
            left_eye_x = hx - int(radius * 0.35) + eye_offset_x
            right_eye_x = hx + int(radius * 0.35) + eye_offset_x
            eye_y = hy - 2 + eye_offset_y
            
            # Draw eyes
            cv2.circle(frame, (left_eye_x, eye_y), 4, (250, 250, 250), -1)
            cv2.circle(frame, (right_eye_x, eye_y), 4, (250, 250, 250), -1)
            # Pupils
            cv2.circle(frame, (left_eye_x, eye_y), 2, (30, 30, 30), -1)
            cv2.circle(frame, (right_eye_x, eye_y), 2, (30, 30, 30), -1)

            # Hand raise if active
            if student.hand_raised:
                cv2.line(frame, (hx + radius, hy + 20), (hx + radius + 15, hy - 35), (210, 195, 180), 5)
                cv2.circle(frame, (hx + radius + 15, hy - 38), 6, (210, 195, 180), -1)

            # Bounding box calculation for face detection
            bbox = (hx - radius, hy - radius, radius * 2, radius * 2)

            metadata.append({
                "student_id": student.student_id,
                "name": student.name,
                "seat": student.seat,
                "bbox": bbox,
                "center": (hx, hy),
                "yaw": round(student.yaw, 1),
                "pitch": round(student.pitch, 1),
                "attentive": student.attentive,
                "motion_energy": round(student.motion_energy, 3),
                "hand_raised": student.hand_raised,
                "is_walkby": False
            })

        # Scenario 1 Verification: Simulate an occasional transient walk-by visitor (every 40-60s)
        # Walk-by crosses classroom doorway on left in 6-8 seconds to test sustained presence filter
        walkby_cycle = int(elapsed) % 45
        if 20 <= walkby_cycle <= 27:
            # Person walking across hallway/doorway
            walk_progress = (walkby_cycle - 20) / 7.0
            wx = int(20 + walk_progress * 110)
            wy = 260
            cv2.circle(frame, (wx, wy), 24, (190, 180, 170), -1)
            cv2.ellipse(frame, (wx, wy + 32), (28, 30), 0, 180, 360, (110, 70, 60), -1)
            cv2.putText(frame, "VISITOR (WALK-BY)", (wx - 35, wy - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.30, (100, 180, 255), 1, cv2.LINE_AA)
            metadata.append({
                "student_id": "GUEST_WALKBY",
                "name": "Hallway Walk-By Visitor",
                "seat": "Aisle / Doorway",
                "bbox": (wx - 24, wy - 24, 48, 48),
                "center": (wx, wy),
                "yaw": 45.0,
                "pitch": 0.0,
                "attentive": False,
                "motion_energy": 0.85,
                "hand_raised": False,
                "is_walkby": True
            })

        return frame, metadata
