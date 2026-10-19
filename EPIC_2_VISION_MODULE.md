# 👁️ EPIC 2: Vision Module Development

> **Document Version:** 1.0.0  
> **Milestone Status:** Implemented, Integrated & Validated (100% Passed)  
> **Target Module:** Multimodal Classroom Vision & Spatial Tracking Engine  
> **Core Components:** [`backend/core/face_detection.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/face_detection.py), [`backend/core/camera_service.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/camera_service.py), [`backend/core/face_tracker.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/face_tracker.py), [`backend/core/vision_pipeline.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/vision_pipeline.py)

---

## 1. Executive Summary & Milestone Objectives

The **Vision Module** constitutes the sensory foundation of the **NeuroClass Multimodal Attendance & Engagement Agent**. Its primary mission is to detect participants from video input, track them persistently across frames, and determine sustained presence for accurate, touchless attendance marking and downstream multimodal reasoning.

Real-world classrooms exhibit complex visual challenges:
- **Participant Movement:** Students shift posture, lean forward/backward, and adjust seating.
- **Partial Occlusions:** Hands, laptops, water bottles, and walking peers frequently obscure facial features temporarily.
- **Varying Camera Angles:** Cameras mounted at the front, ceiling, or teacher's desk capture frontal, angled (oblique), and profile faces.
- **Illumination & Lighting Variations:** Flickering classroom projectors, sunlit windows, shadows, and varying fluorescent lighting.

EPIC 2 addresses these realities by implementing a modular computer vision pipeline featuring:
1. **Activity 2.1: Face Detection and Tracking** (Sequential frame ingestion, Haar Cascade + Multi-angle profile detection, CLAHE contrast balancing, centroid spatial association, movement velocity analysis, and persistent unique tracking IDs).
2. **Activity 2.2: Presence-Based Attendance Logic** (Temporal sliding window accumulation, transient walk-by filtering, and privacy-preserving pseudonymized audit logs).

---

## 2. Technical Architecture: Vision Pipeline

```
+---------------------------------------------------------------------------------------------------------+
|                                    NEUROCLASS VISION MODULE ARCHITECTURE                                |
+---------------------------------------------------------------------------------------------------------+
|                                                                                                         |
|     +-------------------------+               +-------------------------------+                         |
|     |     VIDEO INPUT         |               |   PRE-RECORDED CLASSROOM      |                         |
|     |  (Live USB/RTSP Webcam) |   --- OR ---  |    VIDEO FEED (.mp4, .avi)    |                         |
|     +-------------------------+               +-------------------------------+                         |
|                  │                                            │                                         |
|                  └──────────────────────┬─────────────────────┘                                         |
|                                         v                                                               |
|                        +─────────────────────────────────+                                              |
|                        |      CameraService Engine       |                                              |
|                        | (cv2.VideoCapture, Frame Pacing,|                                              |
|                        |   WebSocket Streamer, Rewind)   |                                              |
|                        +─────────────────────────────────+                                              |
|                                         │ Raw BGR Frame (640x480 @ 15 FPS)                              |
|                                         v                                                               |
|                        +─────────────────────────────────+                                              |
|                        |    Pre-Processing & Balancing   |                                              |
|                        |  - Grayscale Conversion         |                                              |
|                        |  - CLAHE Lighting Normalization |                                              |
|                        +─────────────────────────────────+                                              |
|                                         │ Balanced Grayscale Frame                                      |
|                                         v                                                               |
|                        +─────────────────────────────────+                                              |
|                        |          FaceDetector           |                                              |
|                        |  - Frontal Haar Cascade         |                                              |
|                        |  - Profile Cascade (Left/Right) |                                              |
|                        |  - Non-Maximum Suppression (NMS)|                                              |
|                        +─────────────────────────────────+                                              |
|                                         │ Bounding Boxes: [{"bbox": (x,y,w,h), "score": 1.0}, ...]      |
|                                         v                                                               |
|                        +─────────────────────────────────+                                              |
|                        |          FaceTracker            |                                              |
|                        |  - Centroid Spatial Association |                                              |
|                        |  - Movement Velocity & Energy   |                                              |
|                        |  - Occlusion Buffer (15 frames) |                                              |
|                        |  - Unique Track ID Persistence  |                                              |
|                        |  - Gaussian Face Privacy Blur   |                                              |
|                        +─────────────────────────────────+                                              |
|                                         │                                                               |
|                  ┌──────────────────────┴──────────────────────┐                                        |
|                  v                                             v                                        |
|   +─────────────────────────────+               +─────────────────────────────+                         |
|   |   STRUCTURED TELEMETRY      |               |     DOWNSTREAM MODULES      |                         |
|   |  - Participant Identifiers  |               |  - Activity 2.2: Attendance |                         |
|   |  - Timestamps & Durations   |               |  - Epic 4: Attention (Gaze) |                         |
|   |  - Spatial Bboxes & Velocity|               |  - Epic 5: Multimodal Fusion|                         |
|   +─────────────────────────────+               +─────────────────────────────+                         |
|                                                                                                         |
+---------------------------------------------------------------------------------------------------------+
```

---

## 3. Activity 2.1: Face Detection and Tracking Implementation

### 3.1 Face Detection (`backend/core/face_detection.py`)
Directly derived from the core reference implementation, `FaceDetector` utilizes OpenCV's built-in Haar Cascades with targeted enhancements for real classroom environments:

- **Reference Architecture:**
  ```python
  class FaceDetector:
      def __init__(self):
          haarcascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
          self.face_cascade = cv2.CascadeClassifier(haarcascade_path)
          if self.face_cascade.empty():
              print("Error: Could not load face cascade xml")

      def process_frame(self, frame):
          gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
          faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
          detections = []
          for (x, y, w, h) in faces:
              detections.append({"bbox": (int(x), int(y), int(w), int(h)), "score": 1.0})
          return detections
  ```

- **Classroom Robustness Enhancements:**
  1. **Illumination Balancing (CLAHE):** Contrast-Limited Adaptive Histogram Equalization (`clipLimit=2.0`, `tileGridSize=(8,8)`) is applied to prevent detection loss caused by projector light washouts or backlit classroom windows.
  2. **Multi-Angle Profile Support:** In addition to frontal detection, the detector integrates `haarcascade_profileface.xml` and horizontal flip processing to detect participants seated at diagonal angles or turning toward neighbors.
  3. **Non-Maximum Suppression (NMS):** Eliminates redundant, overlapping bounding boxes when both frontal and profile detectors trigger on the same face.
  4. **Enriched Positional Metadata:** Appends exact `centroid: (cx, cy)` and epoch `timestamp` to every detection record while strictly preserving the expected `{"bbox": (x, y, w, h), "score": 1.0}` structure.
  5. **Cross-Python / OpenCV 5.x Compatibility:** Automatically injects a fallback `CascadeClassifierCompat` layer on modern Python 3.14/OpenCV 5 environments where C++ bindings are altered, preventing runtime crashes.

### 3.2 Camera Ingestion Service (`backend/core/camera_service.py`)
The `CameraService` abstracts hardware video ingestion:
- **Live Webcam Capture:** Streams from device index `camera_id=0` (or external USB webcams).
- **Pre-recorded Video Playback:** Accepts local video paths (e.g. `storage/uploads/classroom_session.mp4`) with automatic end-of-file rewinding for uninterrupted test and evaluation loops.
- **WebSocket Streaming:** Contains `async def stream_websocket(self, websocket: WebSocket)` enabling high-efficiency binary JPEG streaming over web sockets.
- **Runtime Telemetry:** Exposes `get_status()` returning capture resolution, FPS, frames captured, and uptime.

### 3.3 Face Tracking & Identity Association (`backend/core/face_tracker.py`)
In real-world classroom sessions, participants must be monitored continuously without identity swapping:
- **Centroid Association:** Computes Euclidean distance matrix $D_{i,j} = \sqrt{(x_i - x_j)^2 + (y_i - y_j)^2}$ between previous tracks and incoming detections. Minimum cost pairs below `max_distance = 75.0 px` are updated.
- **Movement Velocity & Energy:** Tracks positional displacement $\vec{v} = (\frac{\Delta x}{\Delta t}, \frac{\Delta y}{\Delta t})$ and normalized movement energy $E = \min(1.0, \frac{\|\Delta \vec{x}\|}{150})$ to distinguish attentive posture from restless movement.
- **Occlusion Buffer:** When a participant sneezes, looks down at a textbook, or is briefly occluded by a peer, their track is marked as `"OCCLUDED"` and preserved for up to `max_disappeared = 15` frames (~1.0–1.5 seconds) before dereferencing. If the face reappears nearby, their identity (`track_id` / `student_id`) is seamlessly restored without fragmenting attendance records.
- **Privacy Obfuscation:** Face ROIs are subjected to a strong $31 \times 31$ Gaussian blur before video broadcast, ensuring participant privacy while preserving spatial analytics.

---

## 4. Structured Tracking Output Schema

Every processed frame generates structured telemetry matching the requirements of Activity 2.1:

```json
{
  "session_id": "SES-20261013-231454",
  "timestamp": 1791913537.896,
  "active_tracks_count": 8,
  "tracks": [
    {
      "track_id": 1,
      "student_id": "STU-101",
      "timestamp": 1791913537.896,
      "first_detected": 1791913493.507,
      "bbox": [91, 151, 56, 56],
      "centroid": [119, 179],
      "velocity": [1.2, -0.4],
      "movement_energy": 0.20,
      "presence_duration": 44.44,
      "total_frames_active": 423,
      "disappeared_frames": 0,
      "status": "ACTIVE",
      "score": 1.0,
      "attention_score": 1.0,
      "yaw": -1.9,
      "pitch": -1.4,
      "is_walkby": false
    }
  ]
}
```

---

## 5. Verification & Test Suite Summary

The Vision Module was evaluated through automated unit tests in [`tests/test_system.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/tests/test_system.py):

| Test Case | Scope | Condition Tested | Result |
| :--- | :--- | :--- | :--- |
| `test_epic2_face_detector_and_camera_service` | FaceDetector & CameraService | Cascade XML loading, frame processing, bounding box format `{"bbox": ..., "score": 1.0}`, camera start/stop | ✅ **PASSED** |
| `test_epic2_face_tracking_and_spatial_association` | FaceTracker | Spatial association across movement, persistent `track_id` consistency, occlusion buffer (0 detections for 1 frame), identity recovery | ✅ **PASSED** |
| `test_epic2_vision_api_endpoints` | API Endpoints | `/api/vision/status`, `/api/vision/tracks`, `/api/vision/detect`, and `/api/vision/milestone2_status` responses | ✅ **PASSED** |
| **Complete System Test Suite** | Full End-to-End | 16/16 tests passing across Database, Attendance, Audio, Fusion, Vision, and Privacy | ✅ **100% OK** |

### Live Endpoint Verification

```bash
# Query Vision Status
curl http://127.0.0.1:8000/api/vision/status
# -> {"status": "ACTIVE", "milestone": "EPIC 2: Vision Module Development", "activity": "Activity 2.1: Face Detection and Tracking", ...}

# Query Live Structured Tracks
curl http://127.0.0.1:8000/api/vision/tracks
# -> {"session_id": "...", "active_tracks_count": 8, "tracks": [...]}
```

---

## 6. Traceability to Subsequent Activities

1. **Activity 2.2: Presence-Based Attendance Logic:** Uses `presence_duration`, `first_detected`, and `last_detected` from structured tracks to accumulate session participation time and filter transient visitors ($\le 10\text{ s}$).
2. **Activity 4.1 & 4.2: Multimodal Fusion & Engagement Index:** Feeds participant spatial velocity, movement energy, and yaw/pitch gaze metrics into the composite engagement index calculation.
