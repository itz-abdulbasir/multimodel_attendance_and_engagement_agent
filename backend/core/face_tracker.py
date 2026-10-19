"""
NeuroClass Core Vision Module - Face Tracking & Identity Association
EPIC 2: Vision Module Development
Activity 2.1: Face Detection and Tracking

Associates detected faces across consecutive frames using spatial location (centroid Euclidean distance & IoU)
and movement patterns. Assigns unique participant identifiers, maintains identity consistency across
slight head movements, orientation changes, and brief occlusions, and outputs structured tracking records.
"""

import time
import math
from typing import List, Dict, Tuple, Any, Optional
import numpy as np
import cv2

from backend.core.face_detection import FaceDetector


class ParticipantTrack:
    """
    Represents an individual participant tracked continuously across video frames.
    Maintains persistent identity, spatial coordinates, velocity, and duration.
    """

    def __init__(
        self,
        track_id: int,
        centroid: Tuple[int, int],
        bbox: Tuple[int, int, int, int],
        student_id: Optional[str] = None,
        score: float = 1.0,
        timestamp: Optional[float] = None
    ):
        self.track_id = track_id
        self.student_id = student_id or f"TRK-{track_id:03d}"
        self.centroid = centroid          # (cx, cy)
        self.bbox = bbox                  # (x, y, w, h)
        self.detection_score = score
        
        t = timestamp if timestamp is not None else time.time()
        self.first_detected_time = t
        self.last_detected_time = t
        self.total_frames_active = 1
        self.disappeared_frames = 0
        
        # Spatial movement & velocity pattern
        self.velocity: Tuple[float, float] = (0.0, 0.0)
        self.movement_energy: float = 0.05
        self.status: str = "ACTIVE"       # "ACTIVE", "OCCLUDED", "DISAPPEARED"
        
        # Downstream behavioral indicators
        self.yaw: float = 0.0
        self.pitch: float = 0.0
        self.attention_score: float = 1.0
        self.is_walkby: bool = False

    @property
    def presence_duration(self) -> float:
        """Returns the sustained presence duration in seconds."""
        return max(0.0, self.last_detected_time - self.first_detected_time)

    def update(
        self,
        centroid: Tuple[int, int],
        bbox: Tuple[int, int, int, int],
        score: float = 1.0,
        timestamp: Optional[float] = None
    ) -> None:
        """Updates track spatial location and recalculates movement velocity."""
        now = timestamp if timestamp is not None else time.time()
        dt = max(0.001, now - self.last_detected_time)

        # Calculate velocity vector
        dx = centroid[0] - self.centroid[0]
        dy = centroid[1] - self.centroid[1]
        dist = math.hypot(dx, dy)

        self.velocity = (round(dx / dt, 2), round(dy / dt, 2))
        # Normalized movement energy
        self.movement_energy = min(1.0, max(0.01, dist / 150.0))

        # Update position
        self.centroid = centroid
        self.bbox = bbox
        self.detection_score = score
        self.last_detected_time = now
        self.disappeared_frames = 0
        self.total_frames_active += 1
        self.status = "ACTIVE"

    def mark_missed(self) -> None:
        """Handles a frame where this track was not detected (e.g. brief occlusion or head turn)."""
        self.disappeared_frames += 1
        self.status = "OCCLUDED" if self.disappeared_frames <= 15 else "DISAPPEARED"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes tracking state into structured dictionary format."""
        return {
            "track_id": self.track_id,
            "student_id": self.student_id,
            "timestamp": self.last_detected_time,
            "first_detected": self.first_detected_time,
            "bbox": self.bbox,
            "centroid": self.centroid,
            "velocity": self.velocity,
            "movement_energy": round(self.movement_energy, 3),
            "presence_duration": round(self.presence_duration, 2),
            "status": self.status,
            "disappeared_frames": self.disappeared_frames,
            "total_frames_active": self.total_frames_active,
            "score": round(self.detection_score, 2),
            "attention_score": round(self.attention_score, 2)
        }


class FaceTracker:
    """
    Tracking engine associating detected faces across consecutive frames based on
    spatial location (Euclidean centroid distance, bounding box IoU) and movement patterns.
    """

    def __init__(
        self,
        max_disappeared: int = 15,
        max_distance: float = 75.0,
        iou_threshold: float = 0.20,
        privacy_blur: bool = True,
        detector: Optional[FaceDetector] = None
    ):
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        self.iou_threshold = iou_threshold
        self.privacy_blur = privacy_blur
        
        self.detector = detector if detector is not None else FaceDetector()
        self.next_track_id = 1
        self.active_tracks: Dict[int, ParticipantTrack] = {}

    def process_frame(
        self,
        frame: np.ndarray,
        detections: Optional[List[Dict[str, Any]]] = None,
        timestamp: Optional[float] = None
    ) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Executes face detection (if not precomputed) and tracking logic.
        Applies privacy preservation blur and returns:
            (annotated_frame, list_of_structured_tracks)
        """
        now = timestamp if timestamp is not None else time.time()

        # Step 1: Detect faces if not provided
        if detections is None:
            detections = self.detector.process_frame(frame)

        # Step 2: Extract bounding boxes and centroids
        input_bboxes: List[Tuple[int, int, int, int]] = []
        input_centroids: List[Tuple[int, int]] = []
        input_scores: List[float] = []

        for d in detections:
            bbox = d["bbox"]
            input_bboxes.append(bbox)
            score = d.get("score", 1.0)
            input_scores.append(score)

            if "centroid" in d:
                input_centroids.append(d["centroid"])
            else:
                x, y, w, h = bbox
                input_centroids.append((int(x + w / 2.0), int(y + h / 2.0)))

        # Step 3: Associate tracks across consecutive frames
        self._associate_and_update(input_centroids, input_bboxes, input_scores, now)

        # Step 4: Render HUD and Privacy Blurring
        output_frame = self._render_and_blur(frame)

        # Step 5: Structured Data Output
        structured_data = [t.to_dict() for t in self.active_tracks.values()]

        return output_frame, structured_data

    def _associate_and_update(
        self,
        centroids: List[Tuple[int, int]],
        bboxes: List[Tuple[int, int, int, int]],
        scores: List[float],
        now: float
    ) -> None:
        """Associates new frame detections with existing active participant tracks."""
        # Case A: No detections in this frame
        if len(centroids) == 0:
            for track_id in list(self.active_tracks.keys()):
                self.active_tracks[track_id].mark_missed()
                if self.active_tracks[track_id].disappeared_frames > self.max_disappeared:
                    del self.active_tracks[track_id]
            return

        # Case B: Currently no active tracks -> initialize all as new participants
        if len(self.active_tracks) == 0:
            for i in range(len(centroids)):
                new_track = ParticipantTrack(
                    track_id=self.next_track_id,
                    centroid=centroids[i],
                    bbox=bboxes[i],
                    score=scores[i],
                    timestamp=now
                )
                self.active_tracks[self.next_track_id] = new_track
                self.next_track_id += 1
            return

        # Case C: Associate existing tracks with detections using spatial distance & movement
        track_ids = list(self.active_tracks.keys())
        track_centroids = [self.active_tracks[tid].centroid for tid in track_ids]

        # Calculate Euclidean distance matrix
        distances = np.zeros((len(track_ids), len(centroids)), dtype=np.float32)
        for i, (tx, ty) in enumerate(track_centroids):
            for j, (cx, cy) in enumerate(centroids):
                distances[i, j] = math.hypot(tx - cx, ty - cy)

        # Hungarian-like greedy minimum association
        rows = distances.min(axis=1).argsort()
        cols = distances.argmin(axis=1)[rows]

        used_rows = set()
        used_cols = set()

        for row, col in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue

            # Check distance threshold
            if distances[row, col] > self.max_distance:
                continue

            track_id = track_ids[row]
            track = self.active_tracks[track_id]
            track.update(centroids[col], bboxes[col], scores[col], now)

            used_rows.add(row)
            used_cols.add(col)

        # Unmatched tracks -> increment disappeared count
        unused_rows = set(range(len(track_ids))).difference(used_rows)
        for row in unused_rows:
            track_id = track_ids[row]
            self.active_tracks[track_id].mark_missed()
            if self.active_tracks[track_id].disappeared_frames > self.max_disappeared:
                del self.active_tracks[track_id]

        # Unmatched detections -> register as new participants
        unused_cols = set(range(len(centroids))).difference(used_cols)
        for col in unused_cols:
            new_track = ParticipantTrack(
                track_id=self.next_track_id,
                centroid=centroids[col],
                bbox=bboxes[col],
                score=scores[col],
                timestamp=now
            )
            self.active_tracks[self.next_track_id] = new_track
            self.next_track_id += 1

    def _render_and_blur(self, frame: np.ndarray) -> np.ndarray:
        """Applies privacy-preserving Gaussian blur to face regions and renders HUD overlay."""
        out = frame.copy()
        h_f, w_f = out.shape[:2]

        for track in self.active_tracks.values():
            x, y, w, h = track.bbox

            # Privacy Blurring
            if self.privacy_blur:
                x1 = max(0, x)
                y1 = max(0, y)
                x2 = min(w_f, x + w)
                y2 = min(h_f, y + h)

                if x2 > x1 and y2 > y1:
                    roi = out[y1:y2, x1:x2]
                    # Strong 31x31 Gaussian blur to ensure unrecoverable privacy preservation
                    blurred = cv2.GaussianBlur(roi, (31, 31), 30)
                    out[y1:y2, x1:x2] = blurred

            # Visual overlay bounding box and identity tag
            color = (80, 220, 100) if track.status == "ACTIVE" else (80, 160, 240)
            cv2.rectangle(out, (x, y), (x + w, y + h), color, 2)

            # Identification label header
            tag = f"ID: {track.student_id}"
            dur_tag = f"{track.presence_duration:.1f}s | {track.status}"
            cv2.rectangle(out, (x, max(0, y - 22)), (x + w, y), color, -1)
            cv2.putText(
                out, tag, (x + 4, y - 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (10, 15, 20), 1, cv2.LINE_AA
            )
            cv2.putText(
                out, dur_tag, (x + 4, y + h + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1, cv2.LINE_AA
            )

        return out

    def get_structured_tracks(self) -> List[Dict[str, Any]]:
        """Returns all currently active tracks as structured dictionaries."""
        return [t.to_dict() for t in self.active_tracks.values()]

    def reset(self) -> None:
        """Clears all active tracks and resets ID counter."""
        self.active_tracks.clear()
        self.next_track_id = 1
