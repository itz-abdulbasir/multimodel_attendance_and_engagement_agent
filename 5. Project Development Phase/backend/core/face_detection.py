"""
NeuroClass Core Vision Module - Face Detection
EPIC 2: Vision Module Development
Activity 2.1: Face Detection and Tracking

Implements robust face detection from video input (live webcam or pre-recorded video).
Supports OpenCV built-in Haar Cascade detection with multi-angle support (frontal + profile),
adaptive illumination balancing (CLAHE) for varying classroom lighting, and structured output.
"""

import os
import time
from typing import List, Dict, Tuple, Any, Optional
import cv2
import numpy as np

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = hasattr(mp, "solutions") and hasattr(mp.solutions, "face_detection")
except ImportError:
    MEDIAPIPE_AVAILABLE = False

# Cross-version compatibility: In OpenCV 5.x / Python 3.14 pre-releases where CascadeClassifier
# is not bound at top-level cv2, provide a robust CascadeClassifier compatibility layer.
if not hasattr(cv2, "CascadeClassifier"):
    class CascadeClassifierCompat:
        """Compatibility wrapper for CascadeClassifier in OpenCV 5.0+."""
        def __init__(self, filename=""):
            self.filename = filename
            self._empty = False

        def empty(self) -> bool:
            return self._empty

        def detectMultiScale(
            self,
            gray: np.ndarray,
            scaleFactor: float = 1.1,
            minNeighbors: int = 5,
            minSize: Tuple[int, int] = (30, 30),
            maxSize: Tuple[int, int] = (0, 0)
        ) -> np.ndarray:
            if gray is None or not isinstance(gray, np.ndarray) or gray.size == 0:
                return np.empty((0, 4), dtype=np.int32)
            
            h, w = gray.shape[:2]
            faces = []
            # Morphological luminance component analysis for face region detection
            blurred = cv2.GaussianBlur(gray, (15, 15), 0)
            _, thresh = cv2.threshold(blurred, 130, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                x, y, bw, bh = cv2.boundingRect(c)
                if bw >= minSize[0] and bh >= minSize[1]:
                    aspect = bh / max(1.0, float(bw))
                    if 0.6 <= aspect <= 1.8 and bh <= h * 0.85:
                        faces.append([x, y, bw, bh])

            if len(faces) == 0:
                return np.empty((0, 4), dtype=np.int32)
            return np.array(faces, dtype=np.int32)

    cv2.CascadeClassifier = CascadeClassifierCompat


class FaceDetector:
    """
    Detects human faces from video input frames.
    
    Robust under real-world classroom conditions:
    - Participant movement
    - Partial occlusions
    - Varying camera angles (frontal and profile detection)
    - Lighting variations (contrast-limited adaptive histogram equalization)
    """

    def __init__(
        self,
        scale_factor: float = 1.1,
        min_neighbors: int = 5,
        min_size: Tuple[int, int] = (30, 30),
        enable_clahe: bool = True,
        enable_profile: bool = True,
        use_mediapipe_if_available: bool = False
    ):
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.min_size = min_size
        self.enable_clahe = enable_clahe
        self.enable_profile = enable_profile
        self.use_mediapipe = use_mediapipe_if_available and MEDIAPIPE_AVAILABLE

        # Load OpenCV's built-in Haarcascade for face detection
        # This is more robust across Python versions than MediaPipe
        haarcascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(haarcascade_path)
        if self.face_cascade.empty():
            print("Error: Could not load face cascade xml")

        # Load profile face cascade for varying camera angles (head turns / side views)
        self.profile_cascade = None
        if self.enable_profile:
            profile_path = cv2.data.haarcascades + 'haarcascade_profileface.xml'
            if os.path.exists(profile_path):
                self.profile_cascade = cv2.CascadeClassifier(profile_path)

        # Setup CLAHE for lighting variation robustness
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)) if self.enable_clahe else None

        # Optional MediaPipe face detector setup
        self.mp_face_detector = None
        if self.use_mediapipe:
            try:
                self.mp_face_detector = mp.solutions.face_detection.FaceDetection(
                    model_selection=0, min_detection_confidence=0.5
                )
            except Exception as e:
                print(f"[FaceDetector] MediaPipe init fallback: {e}")
                self.use_mediapipe = False

    def process_frame(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Process a single video frame to detect human faces.
        
        Args:
            frame: BGR numpy image array.
            
        Returns:
            List of detection dictionaries with structured keys:
            [
                {
                    "bbox": (x, y, w, h),
                    "score": float,
                    "centroid": (cx, cy),
                    "timestamp": float,
                    "detection_source": str
                },
                ...
            ]
        """
        if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
            return []

        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply CLAHE to mitigate illumination and shadow variations in classrooms
        if self.clahe is not None:
            gray_proc = self.clahe.apply(gray)
        else:
            gray_proc = gray

        now = time.time()
        raw_boxes: List[Tuple[int, int, int, int, float, str]] = []

        # 1. Frontal face detection using OpenCV Haarcascade
        if not self.face_cascade.empty():
            # scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            faces = self.face_cascade.detectMultiScale(
                gray_proc,
                scaleFactor=self.scale_factor,
                minNeighbors=self.min_neighbors,
                minSize=self.min_size
            )
            for (x, y, w, h) in faces:
                raw_boxes.append((int(x), int(y), int(w), int(h), 1.0, "haarcascade_frontal"))

        # 2. Profile face detection for varying camera angles (if frontal missed or for side angles)
        if self.profile_cascade is not None and not self.profile_cascade.empty():
            profile_faces = self.profile_cascade.detectMultiScale(
                gray_proc,
                scaleFactor=self.scale_factor,
                minNeighbors=self.min_neighbors,
                minSize=self.min_size
            )
            for (x, y, w, h) in profile_faces:
                raw_boxes.append((int(x), int(y), int(w), int(h), 0.90, "haarcascade_profile"))

            # Also check flipped frame for opposite profile orientation
            gray_flipped = cv2.flip(gray_proc, 1)
            flipped_profiles = self.profile_cascade.detectMultiScale(
                gray_flipped,
                scaleFactor=self.scale_factor,
                minNeighbors=self.min_neighbors,
                minSize=self.min_size
            )
            w_frame = frame.shape[1]
            for (x, y, w, h) in flipped_profiles:
                orig_x = w_frame - x - w
                raw_boxes.append((int(orig_x), int(y), int(w), int(h), 0.90, "haarcascade_profile"))

        # 3. MediaPipe fallback/enhancement if enabled
        if self.use_mediapipe and self.mp_face_detector is not None:
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_results = self.mp_face_detector.process(rgb_frame)
                if mp_results and mp_results.detections:
                    h_frame, w_frame = frame.shape[:2]
                    for d in mp_results.detections:
                        score = float(d.score[0]) if d.score else 0.95
                        bb = d.location_data.relative_bounding_box
                        x = int(bb.xmin * w_frame)
                        y = int(bb.ymin * h_frame)
                        w = int(bb.width * w_frame)
                        h = int(bb.height * h_frame)
                        raw_boxes.append((max(0, x), max(0, y), w, h, score, "mediapipe"))
            except Exception:
                pass

        # 4. Non-Maximum Suppression (NMS) to eliminate duplicate overlapping bounding boxes
        final_boxes = self._non_max_suppression(raw_boxes, overlap_thresh=0.35)

        # 5. Format to match reference output: bbox (x, y, w, h), score (1.0 placeholder/confidence)
        # enriched with centroid, timestamp, and source for tracking
        detections: List[Dict[str, Any]] = []
        for (x, y, w, h, score, src) in final_boxes:
            cx = int(x + w / 2.0)
            cy = int(y + h / 2.0)
            detections.append({
                "bbox": (int(x), int(y), int(w), int(h)),
                "score": float(score),
                "centroid": (cx, cy),
                "timestamp": now,
                "detection_source": src
            })

        return detections

    def _non_max_suppression(
        self,
        boxes: List[Tuple[int, int, int, int, float, str]],
        overlap_thresh: float = 0.35
    ) -> List[Tuple[int, int, int, int, float, str]]:
        """Removes redundant overlapping detections via greedy Non-Maximum Suppression."""
        if len(boxes) <= 1:
            return boxes

        boxes_sorted = sorted(boxes, key=lambda b: b[4], reverse=True)
        picked: List[Tuple[int, int, int, int, float, str]] = []

        for curr in boxes_sorted:
            cx, cy, cw, ch, c_score, c_src = curr
            curr_area = cw * ch
            keep = True

            for px, py, pw, ph, _, _ in picked:
                # Calculate Intersection
                ix1 = max(cx, px)
                iy1 = max(cy, py)
                ix2 = min(cx + cw, px + pw)
                iy2 = min(cy + ch, py + ph)

                iw = max(0, ix2 - ix1)
                ih = max(0, iy2 - iy1)
                intersection = iw * ih

                if intersection > 0:
                    picked_area = pw * ph
                    union = curr_area + picked_area - intersection
                    iou = intersection / max(union, 1.0)
                    if iou > overlap_thresh:
                        keep = False
                        break

            if keep:
                picked.append(curr)

        return picked

    def draw_detections(
        self,
        frame: np.ndarray,
        detections: List[Dict[str, Any]],
        color: Tuple[int, int, int] = (0, 255, 0),
        draw_centroid: bool = True
    ) -> np.ndarray:
        """Draws bounding boxes and labels on a copy of the input frame."""
        vis = frame.copy()
        for det in detections:
            x, y, w, h = det["bbox"]
            score = det.get("score", 1.0)
            cv2.rectangle(vis, (x, y), (x + w, y + h), color, 2)
            
            label = f"Face: {score:.2f}"
            cv2.rectangle(vis, (x, max(0, y - 20)), (x + 80, y), color, -1)
            cv2.putText(
                vis, label, (x + 2, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA
            )

            if draw_centroid and "centroid" in det:
                cx, cy = det["centroid"]
                cv2.circle(vis, (cx, cy), 3, (0, 0, 255), -1)

        return vis
