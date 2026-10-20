"""
NeuroClass Core Vision Module - Unified Vision Pipeline
EPIC 2: Vision Module Development
Activity 2.1: Face Detection and Tracking

Integrates CameraService (live webcam / pre-recorded video), FaceDetector (Haar Cascade / multi-angle),
and FaceTracker (spatial association, continuous tracking, identity consistency, and structured data output).
"""

from typing import Optional, Dict, Any, List, Tuple
import numpy as np

from backend.core.camera_service import CameraService
from backend.core.face_detection import FaceDetector
from backend.core.face_tracker import FaceTracker, ParticipantTrack


class VisionModulePipeline:
    """
    Unified end-to-end vision module.
    
    Coordinates:
    1. Video input acquisition (live webcam or pre-recorded video).
    2. Sequential frame processing with FaceDetector.
    3. Multi-frame participant tracking with FaceTracker.
    4. Structured telemetry generation (participant IDs, timestamps, bounding boxes, duration).
    """

    def __init__(
        self,
        camera_id: int = 0,
        video_path: Optional[str] = None,
        privacy_blur: bool = True,
        fps: int = 15,
        width: int = 640,
        height: int = 480
    ):
        self.camera_service = CameraService(
            camera_id=camera_id,
            video_path=video_path,
            fps=fps,
            width=width,
            height=height
        )
        self.detector = FaceDetector()
        self.tracker = FaceTracker(privacy_blur=privacy_blur, detector=self.detector)

    def start(self) -> bool:
        """Starts the camera ingestion engine."""
        return self.camera_service.start()

    def stop(self) -> None:
        """Stops the camera ingestion engine."""
        self.camera_service.stop()

    def process_next_frame(self) -> Tuple[bool, Optional[np.ndarray], List[Dict[str, Any]]]:
        """
        Reads next frame from webcam or pre-recorded video and processes detection & tracking.
        
        Returns:
            (success, annotated_frame, structured_tracks_list)
        """
        frame = self.camera_service.get_frame()
        if frame is None:
            return False, None, []

        annotated_frame, structured_tracks = self.tracker.process_frame(frame)
        return True, annotated_frame, structured_tracks

    def get_status(self) -> Dict[str, Any]:
        """Returns comprehensive vision pipeline operational status."""
        cam_status = self.camera_service.get_status()
        active_tracks = self.tracker.get_structured_tracks()
        return {
            "pipeline_status": "ACTIVE" if cam_status["is_running"] else "STOPPED",
            "camera": cam_status,
            "detector": {
                "algorithm": "OpenCV Haar Cascades (Frontal + Profile)",
                "scale_factor": self.detector.scale_factor,
                "min_neighbors": self.detector.min_neighbors,
                "clahe_enabled": self.detector.enable_clahe,
                "profile_detection_enabled": self.detector.enable_profile
            },
            "tracker": {
                "active_participants_count": len(active_tracks),
                "max_disappeared_frames": self.tracker.max_disappeared,
                "max_distance_threshold": self.tracker.max_distance,
                "privacy_blur_enabled": self.tracker.privacy_blur
            },
            "active_tracks": active_tracks
        }
