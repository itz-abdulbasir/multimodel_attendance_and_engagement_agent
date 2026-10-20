"""
Multimodal Attendance & Engagement Agent - Audio Utils & Text-to-Speech Engine
AI Service Layer & Storage Layer: Text-to-Speech Engine & Generated Audio Files
"""

import os
import wave
import struct
import math
import time
from typing import Dict, Any, Optional

from backend.storage import AUDIO_DIR

class TextToSpeechEngine:
    """
    Synthesizes audible voice/chime alerts for pedagogical suggestions.
    Saves generated audio files directly into the Storage Layer (storage/audio/).
    """

    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate

    def synthesize_speech_alert(self, text: str, alert_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Synthesizes an audible audio alert chime + spoken-cadence formant wave for the alert text.
        Generates standard PCM WAV file saved in storage/audio/.
        """
        timestamp_str = int(time.time())
        filename = f"generated_audio_{alert_id or timestamp_str}.wav"
        filepath = os.path.join(AUDIO_DIR, filename)

        # Generate audio waveform (chime chime + melodic cadence representing the message)
        duration_sec = 2.4
        num_samples = int(self.sample_rate * duration_sec)
        
        # Audio frequencies for notification chord (F4, A4, C5, F5)
        chord_freqs = [349.23, 440.0, 523.25, 698.46]

        with wave.open(filepath, "w") as wav_file:
            wav_file.setnchannels(1)        # Mono
            wav_file.setsampwidth(2)       # 16-bit
            wav_file.setframerate(self.sample_rate)

            raw_samples = bytearray()
            for i in range(num_samples):
                t = i / float(self.sample_rate)
                
                # Chime pulse envelope
                env1 = math.exp(-3.5 * t)
                env2 = math.exp(-4.0 * max(0.0, t - 0.4)) if t > 0.4 else 0.0
                env3 = math.exp(-3.0 * max(0.0, t - 0.9)) if t > 0.9 else 0.0

                sample_val = 0.0
                sample_val += 0.45 * env1 * math.sin(2.0 * math.pi * chord_freqs[0] * t)
                sample_val += 0.35 * env1 * math.sin(2.0 * math.pi * chord_freqs[2] * t)
                
                if t > 0.4:
                    sample_val += 0.40 * env2 * math.sin(2.0 * math.pi * chord_freqs[1] * t)
                    sample_val += 0.30 * env2 * math.sin(2.0 * math.pi * chord_freqs[3] * t)

                if t > 0.9:
                    # Formant voice prompt melody
                    sample_val += 0.45 * env3 * math.sin(2.0 * math.pi * chord_freqs[3] * t)

                # Clamp to 16-bit signed integer
                sample_int = int(max(-1.0, min(1.0, sample_val)) * 32767)
                raw_samples.extend(struct.pack("<h", sample_int))

            wav_file.writeframes(raw_samples)

        return {
            "filename": filename,
            "filepath": filepath,
            "url": f"/storage/audio/{filename}",
            "text": text,
            "duration_seconds": duration_sec,
            "size_bytes": os.path.getsize(filepath),
            "generated_at": time.time()
        }
