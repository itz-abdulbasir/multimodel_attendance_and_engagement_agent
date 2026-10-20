"""
NeuroClass Core Vision Module - Camera Service
EPIC 2: Vision Module Development
Activity 2.1: Face Detection and Tracking

Captures video input either from a live webcam feed or a pre-recorded classroom video.
Provides synchronous frame acquisition, video looping for pre-recorded classroom datasets,
and asynchronous WebSocket streaming for real-time video distribution.
"""

import os
import cv2
import time
import asyncio
from typing import Optional, Dict, Any, Tuple
import numpy as np
from fastapi import WebSocket


class CameraService:
    """
    Video ingestion and camera service.
    
    Supports:
    - Live webcam feed (`camera_id=0`, `camera_id=1`, etc.)
    - Pre-recorded classroom video files (`video_path="path/to/video.mp4"`)
    - Asynchronous WebSocket streaming
    - Safe start, stop, and source switching
    """

    def __init__(
        self,
        camera_id: int = 0,
        video_path: Optional[str] = None,
        fps: int = 15,
        width: int = 640,
        height: int = 480
    ):
        self.camera_id = camera_id
        self.video_path = video_path
        self.fps = fps
        self.width = width
        self.height = height

        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.frame_count = 0
        self.start_time: Optional[float] = None
        self.last_frame_time: float = 0.0

    def start(self) -> bool:
        """Starts video capture from webcam or video file."""
        if self.cap is None:
            # Determine capture source
            if self.video_path and os.path.exists(self.video_path):
                source = self.video_path
            else:
                source = self.camera_id

            try:
                self.cap = cv2.VideoCapture(source)
                if not self.cap.isOpened():
                    # Fallback to webcam index if file failed
                    if isinstance(source, str):
                        self.cap = cv2.VideoCapture(self.camera_id)

                if self.cap and self.cap.isOpened():
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                    self.cap.set(cv2.CAP_PROP_FPS, self.fps)
                    self.is_running = True
                    self.start_time = time.time()
                    self.frame_count = 0
                    return True
                else:
                    self.is_running = False
                    return False
            except Exception as e:
                print(f"[CameraService] Start error: {e}")
                self.is_running = False
                return False
        return True

    def stop(self) -> None:
        """Stops video capture and releases the camera resource."""
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None
            self.is_running = False

    def get_frame(self) -> Optional[np.ndarray]:
        """
        Retrieves the next video frame.
        If reading from a video file and end-of-file is reached,
        rewinds back to the first frame for continuous classroom session monitoring.
        """
        if self.is_running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                self.frame_count += 1
                self.last_frame_time = time.time()
                # Ensure consistent target resolution
                if frame.shape[1] != self.width or frame.shape[0] != self.height:
                    frame = cv2.resize(frame, (self.width, self.height))
                return frame
            elif self.video_path:
                # Video file reached EOF -> rewind to frame 0
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret_retry, frame_retry = self.cap.read()
                if ret_retry:
                    self.frame_count += 1
                    self.last_frame_time = time.time()
                    if frame_retry.shape[1] != self.width or frame_retry.shape[0] != self.height:
                        frame_retry = cv2.resize(frame_retry, (self.width, self.height))
                    return frame_retry

        return None

    def get_frame_jpeg(self, quality: int = 80) -> Optional[bytes]:
        """Encodes the current frame to JPEG bytes for network transfer."""
        frame = self.get_frame()
        if frame is not None:
            ret, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
            if ret:
                return buf.tobytes()
        return None

    async def stream_websocket(self, websocket: WebSocket) -> None:
        """
        Streams video frames over a FastAPI WebSocket connection.
        Sends binary JPEG bytes paced according to target FPS.
        """
        await websocket.accept()
        frame_interval = 1.0 / max(1, self.fps)
        try:
            if not self.is_running:
                self.start()

            while self.is_running:
                t0 = time.time()
                frame_bytes = self.get_frame_jpeg()
                if frame_bytes:
                    await websocket.send_bytes(frame_bytes)
                
                # Sleep to maintain FPS pacing
                elapsed = time.time() - t0
                sleep_dur = max(0.005, frame_interval - elapsed)
                await asyncio.sleep(sleep_dur)
        except Exception as e:
            # Client disconnected or error
            pass
        finally:
            try:
                await websocket.close()
            except Exception:
                pass

    def switch_source(self, camera_id: Optional[int] = None, video_path: Optional[str] = None) -> bool:
        """Dynamically switches between live webcam and pre-recorded video."""
        self.stop()
        if camera_id is not None:
            self.camera_id = camera_id
        if video_path is not None:
            self.video_path = video_path
        return self.start()

    def get_status(self) -> Dict[str, Any]:
        """Returns structured status dictionary."""
        source_desc = f"File: {os.path.basename(self.video_path)}" if self.video_path else f"Webcam ID: {self.camera_id}"
        return {
            "is_running": self.is_running,
            "source_type": "video_file" if self.video_path else "webcam",
            "source_description": source_desc,
            "camera_id": self.camera_id,
            "video_path": self.video_path,
            "target_fps": self.fps,
            "resolution": f"{self.width}x{self.height}",
            "frames_captured": self.frame_count,
            "uptime_seconds": round(time.time() - self.start_time, 1) if self.start_time and self.is_running else 0.0
        }
