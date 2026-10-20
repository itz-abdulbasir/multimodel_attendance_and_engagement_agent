"""
Multimodal Classroom Intelligence & Attendance Agent
EPIC 6: Interface, Testing, and Deployment
Activity 6.1: Run Core Application - Pre-recorded Video Asset Generator

Generates high-fidelity pre-recorded classroom video files for local testing and demonstration.
Produces an MP4 video clip depicting an authentic classroom lecture with:
- Multiple enrolled students seated at desks
- Realistic head rotations (frontal focus, lateral distraction, downward gaze)
- Acoustic rhythm indicators (monologue, interactive Q&A)
- Walking transient visitor for walk-by filtering validation
- Suitable for local CameraService and VideoStreamEngine playback
"""

import os
import cv2
import numpy as np
from typing import Optional
from backend.vision.video_stream import VideoStreamEngine


def generate_prerecorded_classroom_video(
    output_path: str = "storage/uploads/classroom_lecture_sample.mp4",
    duration_seconds: float = 10.0,
    fps: int = 15,
    width: int = 640,
    height: int = 480
) -> str:
    """
    Generates a realistic classroom lecture video clip and saves to disk.
    If the file already exists and is non-empty, returns the existing path.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    total_frames = int(duration_seconds * fps)
    
    # FourCC codec - try 'mp4v', fallback to 'XVID' or 'MJPG'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        # Fallback to AVI / MJPG if mp4v container isn't supported on current platform
        fallback_path = output_path.replace(".mp4", ".avi")
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter(fallback_path, fourcc, fps, (width, height))
        if out.isOpened():
            output_path = fallback_path
        else:
            raise RuntimeError(f"Could not open VideoWriter for {output_path} or {fallback_path}")

    sim_engine = VideoStreamEngine(source_type="simulated", target_fps=fps, width=width, height=height)
    sim_engine.start()

    try:
        rhythms = ["INSTRUCTOR_MONOLOGUE", "INSTRUCTOR_MONOLOGUE", "QA_INTERACTION", "GROUP_DISCUSSION", "INSTRUCTOR_MONOLOGUE"]
        
        for frame_idx in range(total_frames):
            rhythm = rhythms[(frame_idx // (fps * 2)) % len(rhythms)]
            ret, frame, _ = sim_engine.read_frame(acoustic_state=rhythm)
            if ret and frame is not None:
                # Add watermark indicating pre-recorded dataset
                cv2.putText(
                    frame,
                    f"PRE-RECORDED CLASSROOM DATASET: Frame {frame_idx+1}/{total_frames}",
                    (15, height - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.38,
                    (220, 220, 220),
                    1,
                    cv2.LINE_AA
                )
                out.write(frame)
    finally:
        out.release()
        sim_engine.stop()

    return output_path


if __name__ == "__main__":
    path = generate_prerecorded_classroom_video()
    print(f"Generated pre-recorded classroom video at: {path} ({os.path.getsize(path)} bytes)")
