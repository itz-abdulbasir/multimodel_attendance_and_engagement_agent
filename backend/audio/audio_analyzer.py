"""
Multimodal Attendance & Engagement Agent - Audio Dynamics & Speech Rhythm
Epic 5: Tasks 9 & 10 (TASK-09, TASK-10) - Acoustic VAD & Classroom Interaction Pattern Detector
"""

import time
import math
import random
from typing import Dict, Any, List, Optional

import numpy as np

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

# Re-export core AudioAnalyzer for seamless unified access across modules (Activity 3.1 & 3.2)
from backend.core.audio_analysis import (
    AudioAnalyzer,
    AudioSegment,
    AudioExtractionResult,
    standardize_audio_waveform,
    segment_audio_waveform,
    NoiseAndSpeechActivityAnalyzer,
    SegmentAcousticFeatures
)

class AudioSignalAnalyzer:
    """
    Processes classroom acoustic signals completely offline and privacy-preservingly.
    Computes energy levels, Voice Activity Detection (VAD), and interaction rhythms
    WITHOUT recording or transcribing private verbal speech.
    Integrates Activity 3.2 Noise & Speech Activity Analysis capabilities.
    """

    def __init__(self, energy_threshold: float = 0.035, monologue_limit_sec: float = 720.0,
                 silence_limit_sec: float = 360.0, sample_rate: int = 16000):
        self.energy_threshold = energy_threshold
        self.monologue_limit_sec = monologue_limit_sec
        self.silence_limit_sec = silence_limit_sec
        self.sample_rate = sample_rate
        
        # State tracking
        self.current_state = "INSTRUCTOR_MONOLOGUE"
        self.state_start_time = time.time()
        self.last_speech_time = time.time()
        self.consecutive_monologue_sec = 0.0
        self.consecutive_silence_sec = 0.0
        self.speaker_turns_count = 0
        self.recent_energy_history: List[float] = []
        self.spl_history: List[float] = []

        # Activity 3.2 Analyzer Engine
        self.noise_speech_analyzer = NoiseAndSpeechActivityAnalyzer(
            sample_rate=sample_rate,
            silence_threshold_rms=0.015,
            speech_threshold_rms=energy_threshold
        )

    def update_simulation_acoustics(self, session_elapsed: float) -> Dict[str, Any]:
        """
        Synthesizes realistic classroom acoustic dynamics aligned with lecture phases:
        - 0 to 4 min: Introduction & greeting (Discussion / QA)
        - 4 to 20 min: Core Concept lecture (Instructor Monologue)
        - 20 to 28 min: Interactive Check & Student Q&A (High interaction, alternating speech)
        - 28 to 36 min: Group peer problem solving (Collaborative Buzz)
        - 36 to 45 min: Individual quiet coding / study (Low energy / Silence)
        """
        cycle = (int(session_elapsed) % 600) / 60.0 # 10 minute looping demo cycle
        
        if cycle < 1.5:
            # Welcome & Q&A
            target_state = "QA_INTERACTION"
            base_energy = random.uniform(0.045, 0.085)
            vad_active = True
        elif cycle < 5.0:
            # Monologue lecture
            target_state = "INSTRUCTOR_MONOLOGUE"
            base_energy = random.uniform(0.038, 0.065)
            vad_active = True
        elif cycle < 7.0:
            # Interactive student Q&A
            target_state = "QA_INTERACTION"
            base_energy = random.uniform(0.055, 0.095)
            vad_active = True
        elif cycle < 8.5:
            # Collaborative buzz
            target_state = "COLLABORATIVE_BUZZ"
            base_energy = random.uniform(0.070, 0.120)
            vad_active = True
        else:
            # Silent study
            target_state = "SILENT_STUDY"
            base_energy = random.uniform(0.005, 0.025)
            vad_active = False

        return self.process_acoustic_metrics(base_energy, vad_active, target_state)

    def process_acoustic_metrics(self, energy_rms: float, vad_active: bool,
                                 rhythm_hint: Optional[str] = None) -> Dict[str, Any]:
        """Processes acoustic frame energy and updates session speech rhythm state."""
        now = time.time()
        
        # Buffer energy
        self.recent_energy_history.append(energy_rms)
        if len(self.recent_energy_history) > 60:
            self.recent_energy_history.pop(0)

        # Transition logic
        new_state = rhythm_hint or self.current_state
        if new_state != self.current_state:
            self.current_state = new_state
            self.state_start_time = now
            self.speaker_turns_count += 1

        state_duration = now - self.state_start_time

        if self.current_state == "INSTRUCTOR_MONOLOGUE":
            self.consecutive_monologue_sec = state_duration
            self.consecutive_silence_sec = 0.0
        elif self.current_state == "SILENT_STUDY" or not vad_active:
            self.consecutive_silence_sec = state_duration
            self.consecutive_monologue_sec = 0.0
        else:
            self.consecutive_monologue_sec = 0.0
            self.consecutive_silence_sec = 0.0

        # Acoustic interaction density score [0.0 - 1.0]
        if self.current_state == "QA_INTERACTION":
            interaction_density = 0.90
        elif self.current_state == "COLLABORATIVE_BUZZ":
            interaction_density = 0.80
        elif self.current_state == "INSTRUCTOR_MONOLOGUE":
            interaction_density = 0.35
        else: # SILENT_STUDY
            interaction_density = 0.15

        # Activity 3.2 Acoustic Metrics
        db_fs = float(20.0 * math.log10(max(energy_rms, 1e-5)))
        spl_db = float(max(30.0, min(95.0, 94.0 + db_fs)))
        self.spl_history.append(spl_db)
        if len(self.spl_history) > 60:
            self.spl_history.pop(0)

        if spl_db < 48.0:
            ambient_noise_level = "QUIET"
        elif spl_db < 62.0:
            ambient_noise_level = "MODERATE"
        elif spl_db < 74.0:
            ambient_noise_level = "ELEVATED"
        else:
            ambient_noise_level = "LOUD_DISRUPTIVE"

        if not vad_active and energy_rms < 0.018:
            speech_state = "SILENCE"
        elif not vad_active and energy_rms >= 0.018:
            speech_state = "BACKGROUND_NOISE"
        else:
            speech_state = "ACTIVE_SPEECH"

        elapsed_min = max(0.1, state_duration / 60.0)
        participation_frequency = float(self.speaker_turns_count / elapsed_min)

        return {
            "energy_rms": round(energy_rms, 4),
            "vad_active": vad_active,
            "rhythm_state": self.current_state,
            "state_duration_sec": round(state_duration, 1),
            "consecutive_monologue_sec": round(self.consecutive_monologue_sec, 1),
            "consecutive_silence_sec": round(self.consecutive_silence_sec, 1),
            "interaction_density": interaction_density,
            "speaker_turns": self.speaker_turns_count,
            # Activity 3.2 Acoustic Fields
            "activity_id": "Activity 3.2",
            "noise_level_db": round(db_fs, 2),
            "noise_level_spl": round(spl_db, 1),
            "ambient_noise_level": ambient_noise_level,
            "speech_state": speech_state,
            "speech_ratio": 0.85 if vad_active else 0.10,
            "participation_frequency": round(participation_frequency, 1)
        }

    def compute_segment_features(self, waveform: np.ndarray,
                                 segment_index: int = 0,
                                 timestamp: Optional[float] = None) -> SegmentAcousticFeatures:
        """Activity 3.2: Forwarding to core NoiseAndSpeechActivityAnalyzer."""
        return self.noise_speech_analyzer.compute_segment_features(
            waveform=waveform,
            segment_index=segment_index,
            timestamp=timestamp
        )

    def get_noise_level_trend(self) -> Dict[str, Any]:
        """Activity 3.2: Computes ambient noise level trends and direction."""
        return self.noise_speech_analyzer.get_noise_level_trend()

    def aggregate_session_context(self) -> Dict[str, Any]:
        """Activity 3.2: Aggregates session-level audio context metrics over time."""
        return self.noise_speech_analyzer.aggregate_session_context()

    def format_for_multimodal_fusion(self) -> Dict[str, Any]:
        """Activity 3.2: Formats audio telemetry for MultimodalFusionEngine."""
        return self.noise_speech_analyzer.format_for_multimodal_fusion()

    def analyze_audio_file(self, filepath: str) -> Dict[str, Any]:
        """
        Extracts acoustic features from an audio file using librosa, soundfile, or wave.
        Computes RMS energy, dB SPL, and Voice Activity without verbal speech-to-text recording.
        """
        # Try librosa if available
        if LIBROSA_AVAILABLE:
            try:
                import librosa
                y, sr = librosa.load(filepath, sr=None, duration=60.0)
                if len(y) > 0:
                    rms_val = float(librosa.feature.rms(y=y).mean())
                    duration = float(librosa.get_duration(y=y, sr=sr))
                    db_fs = float(20.0 * math.log10(max(rms_val, 1e-5)))
                    spl_db = float(max(30.0, min(95.0, 94.0 + db_fs)))
                    return {
                        "rms": round(rms_val, 4),
                        "duration_sec": round(duration, 2),
                        "samplerate": sr,
                        "engine": "librosa",
                        "vad_active": rms_val > self.energy_threshold,
                        "noise_level_spl": round(spl_db, 1),
                        "speech_state": "ACTIVE_SPEECH" if rms_val > self.energy_threshold else "SILENCE"
                    }
            except Exception:
                pass

        # Try soundfile
        try:
            import soundfile as sf
            data, samplerate = sf.read(filepath)
            if len(data.shape) > 1:
                data = data.mean(axis=1)
            rms = float(math.sqrt((data ** 2).mean())) if len(data) > 0 else 0.0
            duration = len(data) / samplerate if samplerate else 0.0
            db_fs = float(20.0 * math.log10(max(rms, 1e-5)))
            spl_db = float(max(30.0, min(95.0, 94.0 + db_fs)))
            return {
                "rms": round(rms, 4),
                "duration_sec": round(duration, 2),
                "samplerate": samplerate,
                "engine": "soundfile",
                "vad_active": rms > self.energy_threshold,
                "noise_level_spl": round(spl_db, 1),
                "speech_state": "ACTIVE_SPEECH" if rms > self.energy_threshold else "SILENCE"
            }
        except Exception:
            pass

        # Standard library wave fallback
        import wave, struct
        try:
            with wave.open(filepath, 'rb') as wf:
                n_frames = wf.getnframes()
                rate = wf.getframerate()
                frames = wf.readframes(min(n_frames, 48000))
                samples = struct.unpack(f"{len(frames)//2}h", frames) if len(frames) >= 2 else []
                rms = math.sqrt(sum(s**2 for s in samples) / max(len(samples), 1)) / 32768.0 if samples else 0.0
                db_fs = float(20.0 * math.log10(max(rms, 1e-5)))
                spl_db = float(max(30.0, min(95.0, 94.0 + db_fs)))
                return {
                    "rms": round(rms, 4),
                    "duration_sec": round(n_frames / rate, 2) if rate else 0.0,
                    "samplerate": rate,
                    "engine": "wave_fallback",
                    "vad_active": rms > self.energy_threshold,
                    "noise_level_spl": round(spl_db, 1),
                    "speech_state": "ACTIVE_SPEECH" if rms > self.energy_threshold else "SILENCE"
                }
        except Exception:
            return {
                "rms": 0.0,
                "duration_sec": 0.0,
                "samplerate": 16000,
                "engine": "none",
                "vad_active": False,
                "noise_level_spl": 30.0,
                "speech_state": "SILENCE"
            }

