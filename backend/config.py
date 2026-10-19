"""
Multimodal Attendance & Engagement Agent - Configuration Management
Epic 1: Task 1 (TASK-01) - Modular Architecture & Offline Config
"""

import os
import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class SystemConfig:
    # System & Runtime
    app_name: str = "Multimodal Attendance & Engagement Agent"
    version: str = "1.0.0"
    host: str = "127.0.0.1"
    port: int = 8000
    offline_mode: bool = True  # Strict offline operation
    debug: bool = False
    
    # Video Ingestion & Processing
    video_source: str = "simulated"  # "simulated", "webcam", or "file"
    video_path: Optional[str] = None # Path to pre-recorded classroom video file
    webcam_index: int = 0
    target_fps: int = 15
    frame_width: int = 640
    frame_height: int = 480
    
    # Privacy Protocol
    privacy_blur_enabled: bool = True  # Anonymize faces in live feed
    blur_kernel_size: int = 31
    store_raw_frames: bool = False     # Never store identifiable raw frames
    hash_salt: str = "privacy_salt_offline_classroom_2026"
    
    # Attendance Tracking & Sustained Presence Thresholds (Epic 3)
    session_duration_minutes: int = 45
    min_sustained_seconds: int = 30    # Minimum presence before candidate attendance (demo: 30s; prod: 300s)
    sustained_presence_ratio: float = 0.65  # Must be present 65% of the observed window
    walkby_threshold_seconds: int = 15 # Detections under this are classified as transient walk-bys
    late_threshold_minutes: int = 10   # After 10 minutes marked as Late
    
    # Visual Attention & Behavior (Epic 4)
    yaw_attention_threshold: float = 25.0    # Degrees from center
    pitch_attention_threshold: float = 20.0  # Degrees from center
    inactivity_dormant_seconds: int = 120    # Flag static posture
    restless_motion_threshold: float = 0.45  # High-frequency jitter threshold
    
    # Audio Signal Dynamics (Epic 5)
    audio_sample_rate: int = 16000
    vad_energy_threshold: float = 0.035
    monologue_alert_minutes: float = 12.0    # Instructor continuous speech without student interaction
    silence_alert_minutes: float = 6.0       # Complete classroom silence warning
    
    # Multimodal Fusion Weights (Epic 6)
    weight_visual_attention: float = 0.50
    weight_motion_balance: float = 0.20
    weight_acoustic_interaction: float = 0.30
    drop_alert_percentage: float = 25.0      # Drop of 25% triggers pacing review
    
    # Pedagogical Agent Cooldowns (Epic 7)
    suggestion_cooldown_seconds: int = 45   # Avoid alert fatigue
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def load_from_file(cls, path: str = "config.json") -> "SystemConfig":
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return cls(**data)
            except Exception as e:
                print(f"[Config] Error loading {path}: {e}, using default config.")
        return cls()

    def save_to_file(self, path: str = "config.json") -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

# Global default config instance
CONFIG = SystemConfig()
