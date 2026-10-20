# ⏱️ EPIC 2: Vision Module Development
## Activity 2.2: Presence-Based Attendance Logic

> **Document Version:** 1.0.0  
> **Milestone Status:** Implemented, Integrated & Validated (100% Passed)  
> **Target Subsystem:** Temporal Presence Duration Accumulator & Attendance Filter  
> **Source Files:** [`backend/core/presence_attendance.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/presence_attendance.py), [`backend/core/face_recognition.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/face_recognition.py), [`backend/attendance/sustained_presence.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/attendance/sustained_presence.py)

---

## 1. Executive Summary & Objective

In traditional or naive computer vision attendance systems, a single detected face in a single video frame is often erroneously counted as attendance. In a bustling educational institution, this leads to widespread false positives:
- A student walking past the classroom door in the hallway is mistakenly recorded as present.
- A student who enters the room for 15 seconds to borrow a pen is recorded as attending the entire 60-minute lecture.
- Transient optical false detections trigger false roll-call entries.

**Activity 2.2: Presence-Based Attendance Logic** eliminates single-frame vulnerabilities by establishing continuous, timestamp-based accumulation of participant presence. Instead of instantaneous marking, attendance is confirmed **only when a participant remains visible for a minimum sustained duration** throughout the classroom session.

---

## 2. Temporal Logic & Mathematical Specification

```
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                    PRESENCE-BASED ATTENDANCE STATE MACHINE                              |
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                                                                                         |
|       [Track Ingestion from Activity 2.1]                                                               |
|                        │                                                                                |
|                        v                                                                                |
|          +───────────────────────────+                                                                  |
|          |  Is Participant Visible?  |                                                                  |
|          +───────────────────────────+                                                                  |
|                  │            │                                                                         |
|            YES   │            │   NO (Head turn, brief occlusion, or stepped out)                       |
|                  v            v                                                                         |
|       +───────────────────+   +───────────────────────────────────+                                     |
|       | Accumulate:       |   | Pause Accumulation:               |                                     |
|       | T_cum += dt       |   | Keep T_cum intact                 |                                     |
|       | Close open gap    |   | Record appearance interval gap    |                                     |
|       +───────────────────+   +───────────────────────────────────+                                     |
|                  │                             │                                                        |
|                  └──────────────┬──────────────┘                                                        |
|                                 v                                                                       |
|             +─────────────────────────────────────────+                                                 |
|             |        Temporal Rule Classification     |                                                 |
|             +─────────────────────────────────────────+                                                 |
|               │                   │                 │                                                   |
|  T_cum < T_walkby & left          │                 │  T_cum >= T_min_sustained                         |
|               │                   │                 │                                                   |
|               v                   v                 v                                                   |
|      [WALKBY_FILTERED]    [INTERMITTENT]       +─────────────────────────+                              |
|      (Excluded from       (Accumulating,       | First Arrival > Cutoff? |                              |
|       attendance logs)     not yet confirmed)  +─────────────────────────+                              |
|                                                  │                     │                                |
|                                             NO   │                YES  │                                |
|                                                  v                     v                                |
|                                             [PRESENT]                [LATE]                             |
|                                         (Confirmed Audit)       (Confirmed Late)                        |
|                                                                                                         |
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
```

### 2.1 Core Equations

1. **Cumulative Presence Duration ($T_{\text{cum}}$):**
   $$T_{\text{cum}} = \sum_{k=1}^{N} \mathbb{I}(\text{visible}_k) \cdot \Delta t_k$$
   where $\mathbb{I}(\text{visible}_k) = 1$ when the participant's spatial track is active in frame $k$, and $\Delta t_k = t_k - t_{k-1}$.

2. **Temporal Presence Ratio ($R_{\text{presence}}$):**
   $$R_{\text{presence}} = \min\left(1.0, \frac{T_{\text{cum}}}{\max(1.0, T_{\text{session\_elapsed}})}\right)$$

3. **Status Decision Rules:**
   $$\text{Status} = \begin{cases} 
   \text{WALKBY\_FILTERED} & \text{if } T_{\text{cum}} < T_{\text{walkby}} \text{ and participant departed} \\
   \text{LATE} & \text{if } T_{\text{cum}} \ge T_{\text{sustained}} \text{ and } (t_{\text{first}} - t_{\text{session\_start}}) > T_{\text{late\_cutoff}} \\
   \text{PRESENT} & \text{if } T_{\text{cum}} \ge T_{\text{sustained}} \\
   \text{INTERMITTENT} & \text{if } 0 < T_{\text{cum}} < T_{\text{sustained}} \\
   \text{ABSENT} & \text{if } T_{\text{cum}} = 0
   \end{cases}$$

---

## 3. Implemented Components

### 3.1 Biometric Face Recognition Engine (`backend/core/face_recognition.py`)
Directly implemented from your reference photo (`backend > core > face_recognition.py`):
```python
from deepface import DeepFace
import cv2
import numpy as np
import os

class FaceRecognizer:
    def __init__(self, db_path="student_db"):
        self.db_path = db_path
        if not os.path.exists(db_path):
            os.makedirs(db_path)

    def register_student(self, img_input, student_id, display_name=None):
        # Saves student reference into db_path folder
        # Computes and indexes feature embedding
        ...

    def recognize(self, frame):
        # If no DB yet, returns []
        if not os.listdir(self.db_path):
            return []
        # Uses DeepFace when installed, or edge-optimized feature vector extraction offline
        ...
```
- **Robustness:** Built with graceful fallback when running on CPU or edge offline environments without GPU acceleration, while preserving full DeepFace compatibility.

### 3.2 Presence Attendance Engine (`backend/core/presence_attendance.py`)
- **Single-Frame Protection:** Guarantees that single-frame detections are marked as `INTERMITTENT`, not `PRESENT`.
- **Intermittent Accumulation:** Accumulates broken intervals across head turns, bathroom breaks, and occlusions to ensure fair and accurate time tracking.
- **Walk-By Filtering:** Prevents passersby ($< 10\text{ seconds}$) from polluting official class rosters.
- **Tamper-Proof Audit Hashes:** Generates salted SHA-256 integrity hashes for each attendance record.

---

## 4. Structured Output Format

Structured attendance logs returned by `/api/attendance/presence_logs`:

```json
{
  "student_id": "STU-101",
  "display_name": "Emma Watson",
  "seat": "Row 1 - Left",
  "status": "PRESENT",
  "is_currently_visible": true,
  "cumulative_presence_seconds": 72.82,
  "presence_ratio": 0.932,
  "presence_percentage": 93.2,
  "first_seen": "2026-10-13T23:38:14.590679",
  "last_seen": "2026-10-13T23:39:32.464033",
  "total_detections_count": 766,
  "intervals_count": 1,
  "audit_hash": "24e681f7bebaa8dc"
}
```

---

## 5. Verification & Test Suite Results

Evaluated through automated unit tests in [`tests/test_system.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/tests/test_system.py):

| Test Case | Scope | Verified Behavior | Status |
| :--- | :--- | :--- | :--- |
| `test_epic2_activity2_2_face_recognizer` | `FaceRecognizer` | Enrollment, recognition on empty database (returns `[]`), matching against registered faces | ✅ **PASSED** |
| `test_epic2_activity2_2_presence_based_attendance_logic` | `PresenceAttendanceEngine` | Single-frame detection rejected as `INTERMITTENT`, intermittent accumulation, walk-by filter, transition to `PRESENT` upon threshold crossing | ✅ **PASSED** |
| `test_epic2_activity2_2_api_endpoints` | API Endpoints | `/api/attendance/presence_summary`, `/api/attendance/presence_logs`, `/api/attendance/registered_faces` | ✅ **PASSED** |
| **Complete System Test Suite** | Full End-to-End | **19/19 Tests Passing** (100% OK) | ✅ **PASSED** |
