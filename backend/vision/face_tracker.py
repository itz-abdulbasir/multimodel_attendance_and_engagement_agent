"""
Multimodal Attendance & Engagement Agent - Participant Tracking & Privacy Blurring
Epic 2: Task 4 (TASK-04) - Participant Detection & Centroid Tracker
"""

import time
import math
from typing import List, Dict, Tuple, Any, Optional
import numpy as np
import cv2

try:
    from deep_sort_realtime.deepsort_tracker import DeepSort
    DEEPSORT_AVAILABLE = True
except ImportError:
    DEEPSORT_AVAILABLE = False

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False


class ParticipantTrack:
    def __init__(self, track_id: int, centroid: Tuple[int, int], bbox: Tuple[int, int, int, int], student_id: Optional[str] = None):
        self.track_id = track_id
        self.centroid = centroid
        self.bbox = bbox  # (x, y, w, h)
        self.student_id = student_id or f"TRK-{track_id:03d}"
        self.disappeared_frames = 0
        self.first_detected_time = time.time()
        self.last_detected_time = time.time()
        self.total_frames_active = 1
        self.last_face_roi: Optional[np.ndarray] = None
        
        # Behavior history
        self.yaw = 0.0
        self.pitch = 0.0
        self.attention_score = 1.0
        self.motion_energy = 0.05
        self.is_dormant = False
        self.dormant_since: Optional[float] = None
        self.is_walkby = False

    def update(self, centroid: Tuple[int, int], bbox: Tuple[int, int, int, int]) -> None:
        self.centroid = centroid
        self.bbox = bbox
        self.disappeared_frames = 0
        self.last_detected_time = time.time()
        self.total_frames_active += 1


class CentroidFaceTracker:
    """Tracks detected faces across video frames, matches biometric identities, and applies privacy preservation."""

    def __init__(self, max_disappeared: int = 15, max_distance: float = 75.0, privacy_blur: bool = True,
                 face_recognizer: Optional[Any] = None, on_identity_recognized: Optional[Any] = None):
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        self.privacy_blur = privacy_blur
        self.face_recognizer = face_recognizer
        self.on_identity_recognized = on_identity_recognized
        
        self.next_track_id = 1
        self.active_tracks: Dict[int, ParticipantTrack] = {}
        self.frame_count = 0
        
        # Load FaceDetector from backend.core
        from backend.core.face_detection import FaceDetector
        self.detector = FaceDetector()
        self.face_cascade = self.detector.face_cascade

    def remap_track_id(self, old_id: str, new_id: str) -> bool:
        """Remap a live track from an anonymous TRK-xxx identifier to an enrolled student ID."""
        for track in self.active_tracks.values():
            if track.student_id == old_id:
                track.student_id = new_id
                return True
        return False

    def get_track_crop(self, track_id: str) -> Optional[np.ndarray]:
        """Returns the most recent unblurred face crop for a given track ID."""
        for track in self.active_tracks.values():
            if track.student_id == track_id:
                return track.last_face_roi
        return None

    def detect_and_track(self, frame: np.ndarray, simulated_meta: Optional[List[Dict[str, Any]]] = None) -> Tuple[np.ndarray, List[ParticipantTrack]]:
        """
        Processes frame, updates tracks, applies privacy blur if enabled, and renders HUD.
        Returns:
            (annotated_or_blurred_frame, active_tracks_list)
        """
        detections: List[Tuple[Tuple[int, int, int, int], Optional[str], Optional[Dict[str, Any]]]] = []

        if simulated_meta:
            # High-fidelity simulation metadata
            for item in simulated_meta:
                detections.append((item["bbox"], item["student_id"], item))
        elif self.detector is not None:
            # OpenCV robust detection on webcam / file frame (multi-angle + CLAHE)
            dets = self.detector.process_frame(frame)
            for d in dets:
                detections.append((d["bbox"], None, d))

        # Centroid association
        input_centroids = []
        input_bboxes = []
        input_meta = []
        
        for bbox, sid, meta in detections:
            x, y, w, h = bbox
            cx = int(x + w / 2.0)
            cy = int(y + h / 2.0)
            input_centroids.append((cx, cy))
            input_bboxes.append(bbox)
            input_meta.append((sid, meta))

        self._update_tracks(input_centroids, input_bboxes, input_meta)

        # Render & Privacy Blurring
        self.frame_count += 1
        output_frame = frame.copy()
        for track in list(self.active_tracks.values()):
            x, y, w, h = track.bbox
            x1 = max(0, x)
            y1 = max(0, y)
            x2 = min(frame.shape[1], x + w)
            y2 = min(frame.shape[0], y + h)

            # 1. Cache unblurred face crop for UI linking and biometric matching
            if x2 > x1 and y2 > y1:
                track.last_face_roi = frame[y1:y2, x1:x2].copy()

            # 2. Periodic Automatic Recognition against student_db/ photos (every 12 frames)
            if self.face_recognizer and (self.frame_count % 12 == 0) and track.student_id.startswith("TRK-"):
                if track.last_face_roi is not None and track.last_face_roi.size > 0:
                    try:
                        matches = self.face_recognizer.recognize(track.last_face_roi)
                        if matches:
                            top_match = matches[0]
                            if top_match.get("verified", False) and top_match.get("confidence", 0.0) >= 0.55:
                                matched_id = top_match["student_id"]
                                old_trk_id = track.student_id
                                track.student_id = matched_id
                                if self.on_identity_recognized:
                                    self.on_identity_recognized(old_trk_id, matched_id)
                    except Exception:
                        pass

            # 3. Privacy Blurring
            if self.privacy_blur:
                if x2 > x1 and y2 > y1:
                    face_roi = output_frame[y1:y2, x1:x2]
                    blurred_roi = cv2.GaussianBlur(face_roi, (31, 31), 30)
                    output_frame[y1:y2, x1:x2] = blurred_roi

            # Visual overlay box & status
            color = (80, 220, 100) if track.attention_score >= 0.70 else (50, 160, 255)
            if track.is_walkby:
                color = (180, 180, 220)
            
            cv2.rectangle(output_frame, (x, y), (x + w, y + h), color, 2)
            
            # Badge header
            tag = f"ID: {track.student_id}"
            att_label = f"Attn: {int(track.attention_score * 100)}%"
            cv2.rectangle(output_frame, (x, y - 22), (x + w, y), color, -1)
            cv2.putText(output_frame, tag, (x + 4, y - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (10, 15, 20), 1, cv2.LINE_AA)
            cv2.putText(output_frame, att_label, (x + 4, y + h + 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1, cv2.LINE_AA)

        return output_frame, list(self.active_tracks.values())

    def _update_tracks(self, centroids: List[Tuple[int, int]], bboxes: List[Tuple[int, int, int, int]],
                       meta_list: List[Tuple[Optional[str], Optional[Dict[str, Any]]]]) -> None:
        if len(centroids) == 0:
            for track_id in list(self.active_tracks.keys()):
                self.active_tracks[track_id].disappeared_frames += 1
                if self.active_tracks[track_id].disappeared_frames > self.max_disappeared:
                    del self.active_tracks[track_id]
            return

        if len(self.active_tracks) == 0:
            for i in range(len(centroids)):
                sid, meta = meta_list[i]
                new_track = ParticipantTrack(self.next_track_id, centroids[i], bboxes[i], sid)
                if meta:
                    new_track.yaw = meta.get("yaw", 0.0)
                    new_track.pitch = meta.get("pitch", 0.0)
                    new_track.motion_energy = meta.get("motion_energy", 0.05)
                    new_track.is_walkby = meta.get("is_walkby", False)
                self.active_tracks[self.next_track_id] = new_track
                self.next_track_id += 1
            return

        # Associate existing tracks with input centroids using Euclidean distance
        track_ids = list(self.active_tracks.keys())
        track_centroids = [self.active_tracks[tid].centroid for tid in track_ids]

        # Distance matrix
        distances = np.zeros((len(track_ids), len(centroids)), dtype=np.float32)
        for i, (tx, ty) in enumerate(track_centroids):
            for j, (cx, cy) in enumerate(centroids):
                distances[i, j] = math.hypot(tx - cx, ty - cy)

        rows = distances.min(axis=1).argsort()
        cols = distances.argmin(axis=1)[rows]

        used_rows = set()
        used_cols = set()

        for row, col in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue
            if distances[row, col] > self.max_distance:
                continue

            track_id = track_ids[row]
            sid, meta = meta_list[col]
            track = self.active_tracks[track_id]
            track.update(centroids[col], bboxes[col])
            if sid:
                track.student_id = sid
            if meta:
                track.yaw = meta.get("yaw", track.yaw)
                track.pitch = meta.get("pitch", track.pitch)
                track.motion_energy = meta.get("motion_energy", track.motion_energy)
                track.is_walkby = meta.get("is_walkby", False)

            used_rows.add(row)
            used_cols.add(col)

        # Mark disappeared
        unused_rows = set(range(len(track_ids))).difference(used_rows)
        for row in unused_rows:
            track_id = track_ids[row]
            self.active_tracks[track_id].disappeared_frames += 1
            if self.active_tracks[track_id].disappeared_frames > self.max_disappeared:
                del self.active_tracks[track_id]

        # Register new detections
        unused_cols = set(range(len(centroids))).difference(used_cols)
        for col in unused_cols:
            sid, meta = meta_list[col]
            new_track = ParticipantTrack(self.next_track_id, centroids[col], bboxes[col], sid)
            if meta:
                new_track.yaw = meta.get("yaw", 0.0)
                new_track.pitch = meta.get("pitch", 0.0)
                new_track.motion_energy = meta.get("motion_energy", 0.05)
                new_track.is_walkby = meta.get("is_walkby", False)
            self.active_tracks[self.next_track_id] = new_track
            self.next_track_id += 1
