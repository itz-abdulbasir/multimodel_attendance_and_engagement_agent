# 🎙️ EPIC 3: Audio Module Development
## Activity 3.1: Audio Signal Extraction & Waveform Segmentation

> **Document Version:** 1.0.0  
> **Milestone Status:** Implemented, Integrated & Validated (100% Passed)  
> **Target Subsystem:** Audio Signal Extractor, Waveform Normalizer, Window Segmenter & Multimodal Frame Synchronizer  
> **Source Files:** [`backend/core/audio_analysis.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/audio_analysis.py), [`backend/audio/audio_analyzer.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/audio/audio_analyzer.py), [`backend/api/server.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/api/server.py), [`streamlit_app.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/streamlit_app.py)

---

## 1. Executive Summary & Objective

In multimodal classroom intelligence systems, auditory cues provide vital telemetry regarding classroom engagement, teacher-student dialogue, collaborative peer problem-solving, and quiet study intervals. 

However, classroom audio ingestion presents major engineering and ethical challenges:
1. **Multi-Source Ingestion Variability:** Audio can arrive from live classroom microphones (16-bit PCM bytes via Web Audio API or hardware mics) or recorded classroom session video files (`.mp4`, `.avi`, `.mkv`, `.mov`) with disparate sample rates (8 kHz, 22.05 kHz, 44.1 kHz, 48 kHz) and multi-channel configurations (stereo, 5.1 surround).
2. **Temporal Alignment with Video:** Computer vision tracks participants frame-by-frame (e.g., at 15 FPS), while audio arrives as a high-frequency continuous stream (e.g., 16,000 samples/sec). Without precise fixed-duration window segmentation, fusing visual attention and audio dynamics into unified epochs is impossible.
3. **Strict Privacy Preservation (Zero Verbal Eavesdropping):** Storing or transcribing student speech violates privacy regulations (FERPA, GDPR). Ingestion must focus strictly on digital waveform dynamics, Root-Mean-Square (RMS) amplitude, noise decibels, and speech-to-silence ratios without converting speech to text.

**Activity 3.1: Audio Signal Extraction** solves these challenges by:
- Ingesting raw audio from microphone streams or recorded video files.
- Converting raw audio signals into normalized digital waveforms ($[-1.0, 1.0]$ float32).
- Standardizing channels to single-channel mono and normalizing sampling rates to $16{,}000\text{ Hz}$.
- Segmenting continuous waveforms into fixed-duration windows (default $1.0\text{ s}$) aligned with video frame indices.
- Storing processed audio data in structured formats (JSON / CSV), including high-resolution timestamps, RMS energy, and amplitude metrics to enable synchronized multimodal analysis.

---

## 2. Technical Architecture: Audio Signal Pipeline

```
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                    NEUROCLASS AUDIO EXTRACTION PIPELINE                                 |
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
|                                                                                                         |
|     +-------------------------+               +-------------------------------+                         |
|     |     LIVE MICROPHONE     |               |   RECORDED CLASSROOM VIDEO    |                         |
|     |  (Web Audio / 16-bit    |   --- OR ---  |  (.mp4, .avi, .mkv session)   |                         |
|     |   PCM streaming bytes)  |               |  (Librosa / SoundFile/FFmpeg) |                         |
|     +-------------------------+               +-------------------------------+                         |
|                  │                                            │                                         |
|                  └──────────────────────┬─────────────────────┘                                         |
|                                         v                                                               |
|                        +─────────────────────────────────+                                              |
|                        |   Raw Audio Ingestion & Decode  |                                              |
|                        |  - 16-bit PCM: y / 32768.0      |                                              |
|                        |  - Byte buffer -> float32 array |                                              |
|                        +─────────────────────────────────+                                              |
|                                         │ Raw Digital Samples                                           |
|                                         v                                                               |
|                        +─────────────────────────────────+                                              |
|                        |     Channel Standardization     |                                              |
|                        |  Stereo / 5.1 -> Mono 1-Channel |                                              |
|                        |      y_mono = mean(y, axis=ch)  |                                              |
|                        +─────────────────────────────────+                                              |
|                                         │ Single-Channel Waveform                                       |
|                                         v                                                               |
|                        +─────────────────────────────────+                                              |
|                        |    Sampling Rate Normalization  |                                              |
|                        |   Target Rate = 16,000 Hz       |                                              |
|                        |   Librosa / Sinc Resampling     |                                              |
|                        +─────────────────────────────────+                                              |
|                                         │ Normalized 16 kHz Mono Digital Waveform                       |
|                                         v                                                               |
|                        +─────────────────────────────────+                                              |
|                        | Fixed-Duration Window Segmenter |                                              |
|                        | Window = 1.0s (16,000 samples)  |                                              |
|                        | Non-overlapping sequential slice|                                              |
|                        +─────────────────────────────────+                                              |
|                                         │                                                               |
|                  ┌──────────────────────┴──────────────────────┐                                        |
|                  v                                             v                                        |
|   +─────────────────────────────+               +─────────────────────────────+                         |
|   |   Acoustic & Amplitude      |               |     Video Frame Alignment   |                         |
|   |   Metric Calculation        |               |  Video FPS = 15.0           |                         |
|   |  - RMS Energy & Peak Amp    |               |  Start: floor(t_start * 15) |                         |
|   |  - Noise Level (dB / SPL)   |               |  End:   floor(t_end * 15)-1 |                         |
|   |  - Speech vs Silence Ratio  |               |  Epoch: [Frame 0 to 14]     |                         |
|   |  - Pedagogical Rhythm State |               +─────────────────────────────+                         |
|   +─────────────────────────────+                              │                                        |
|                  │                                             │                                        |
|                  └──────────────────────┬──────────────────────┘                                        |
|                                         v                                                               |
|                        +─────────────────────────────────+                                              |
|                        |    Structured Data Storage      |                                              |
|                        |  - AudioSegment Dataclass       |                                              |
|                        |  - Structured JSON Time-Series  |                                              |
|                        |  - CSV Multimodal Export Audit  |                                              |
|                        |  - Synchronized Fusion Vector   |                                              |
|                        +─────────────────────────────────+                                              |
|                                                                                                         |
+─────────────────────────────────────────────────────────────────────────────────────────────────────────+
```

---

## 3. Mathematical & Algorithmic Formulation

### 3.1 Digital Waveform Conversion
Raw microphone data arriving as 16-bit linear Pulse-Code Modulation (PCM) integer bytes is normalized into continuous 32-bit floating-point waveforms bounded in $[-1.0, 1.0]$:

$$y[n] = \frac{x_{\text{int16}}[n]}{32768.0}$$

### 3.2 Channel Standardization (Stereo to Mono)
Multi-channel audio signals (such as stereo video tracks $x \in \mathbb{R}^{N \times C}$) are averaged across all channel axes to guarantee omnidirectional, unbiased sound pressure representation:

$$y_{\text{mono}}[n] = \frac{1}{C} \sum_{c=1}^{C} x[n, c]$$

### 3.3 Sampling Rate Normalization
To prevent aliasing, spectral distortion, or dimension mismatch across heterogeneous recording equipment, signals are resampled to the universal target rate $f_s = 16{,}000\text{ Hz}$ using high-order Kaiser-windowed sinc interpolation:

$$y_{\text{resampled}}[m] = \sum_{n} y[n] \cdot \text{sinc}\left(\frac{m \cdot f_{s,\text{orig}}}{f_{s,\text{target}}} - n\right)$$

### 3.4 Fixed-Duration Window Segmentation
The continuous digital waveform is partitioned into fixed temporal windows of duration $T_{\text{window}} = 1.0\text{ s}$ ($L = 16{,}000\text{ samples}$):

$$W_k = \{ y[n] \mid k \cdot L \le n < (k+1) \cdot L \}, \quad k \in \{0, 1, \dots, K-1\}$$

### 3.5 Windowed Amplitude & Decibel Calculations
For each window $W_k$ of length $L$:
1. **Root-Mean-Square (RMS) Energy:**
   $$\text{RMS}_k = \sqrt{\frac{1}{L} \sum_{i=1}^L y_k[i]^2}$$

2. **Decibels Full Scale ($\text{dB}_{\text{FS}}$):**
   $$\text{dB}_{\text{FS}, k} = 20 \log_{10}\left(\max(\text{RMS}_k, 10^{-5})\right)$$

3. **Calibrated Sound Pressure Level (dB SPL):**
   $$\text{SPL}_k = \min\left(95.0, \max\left(30.0, 94.0 + \text{dB}_{\text{FS}, k}\right)\right)$$

4. **Speech-to-Silence Ratio ($R_{\text{speech}}$):**
   Evaluated over short sub-frames ($N_f = 512$ samples, $\sim 32\text{ ms}$):
   $$R_{\text{speech}, k} = \frac{1}{M} \sum_{m=1}^M \mathbb{I}\left(\text{RMS}_{k, m} > \theta_{\text{energy}}\right)$$
   $$R_{\text{silence}, k} = 1.0 - R_{\text{speech}, k}$$

### 3.6 Video Frame Alignment
Given video camera pacing at frame rate $\text{FPS}_{\text{video}} = 15.0$:
$$\text{Frame}_{\text{start}, k} = \lfloor t_{\text{start}, k} \cdot \text{FPS}_{\text{video}} \rfloor$$
$$\text{Frame}_{\text{end}, k} = \max\left(\text{Frame}_{\text{start}, k}, \lfloor t_{\text{end}, k} \cdot \text{FPS}_{\text{video}} \rfloor - 1\right)$$

This direct mathematical link guarantees that Audio Window $k$ exactly matches Video Frames $[\text{Frame}_{\text{start}}, \text{Frame}_{\text{end}}]$ for multimodal fusion.

---

## 4. Implementation Details

### 4.1 Reference Class: `AudioAnalyzer`
Located in [`backend/core/audio_analysis.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/backend/core/audio_analysis.py), `AudioAnalyzer` matches the user's reference design while expanding it with robust extraction, normalization, segmentation, and export capabilities:

```python
class AudioAnalyzer:
    def __init__(self, sample_rate=16000, window_duration_sec=1.0, energy_threshold=0.035):
        self.sample_rate = sample_rate
        self.window_duration_sec = window_duration_sec
        self.window_size_samples = int(self.sample_rate * self.window_duration_sec)
        self.energy_threshold = energy_threshold

    def analyze_audio_chunk(self, audio_data):
        """
        Analyzes raw audio bytes/array:
        1. Noise level (decibels)
        2. Speech vs silence ratio
        3. Sound activity patterns

        Returns engagement metrics
        """
        try:
            # Convert bytes to float32 numpy array if needed
            if isinstance(audio_data, bytes):
                # Assuming 16-bit PCM
                y = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            else:
                y = audio_data

            if len(y) == 0:
                return None
            ...
```

### 4.2 Structured Data Container: `AudioSegment`
```python
@dataclass
class AudioSegment:
    segment_index: int
    start_time: float
    end_time: float
    duration_sec: float
    sample_rate: int
    sample_count: int
    rms_energy: float
    db_level: float
    noise_level_spl: float
    max_amplitude: float
    min_amplitude: float
    peak_to_peak: float
    zero_crossing_rate: float
    speech_ratio: float
    silence_ratio: float
    vad_active: bool
    sound_activity_pattern: str
    aligned_frame_start: int
    aligned_frame_end: int
    waveform: Optional[np.ndarray] = None
```

---

## 5. REST API Specifications

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/audio/activity_3_1/status` | Returns verification status, sampling rate normalization ($16\text{ kHz}$), mono channel standardization, window duration ($1.0\text{ s}$), and latest metrics. |
| `POST` | `/api/audio/activity_3_1/analyze_chunk` | Analyzes raw PCM bytes or float32 arrays and computes decibels, speech ratio, and activity patterns. |
| `POST` | `/api/audio/activity_3_1/extract_from_video` | Extracts audio track from recorded classroom video, standardizes rate & channels, and segments into windows. |
| `POST` | `/api/audio/activity_3_1/segment_waveform` | Segments digital waveforms into fixed-duration windows aligned with video frame indices. |
| `GET` | `/api/audio/activity_3_1/structured_segments` | Returns real-time time-series of structured fixed-duration audio window segments. |
| `GET` | `/api/audio/activity_3_1/export_csv` | Exports structured audio segments as CSV audit file for multimodal synchronization. |
| `GET` | `/api/audio/activity_3_1/export_json` | Exports structured audio segments as JSON audit file. |

---

## 6. Verification & Automated Test Coverage

The test suite in [`tests/test_system.py`](file:///c:/Users/91970/OneDrive/Music/SmartBridge/tests/test_system.py) validates all aspects of Activity 3.1:
1. `test_epic3_activity3_1_audio_analyzer_reference`: Confirms `AudioAnalyzer` processes 16-bit PCM bytes and float32 arrays, returns `None` for empty inputs, and outputs noise decibels, speech-to-silence ratio, and sound activity patterns.
2. `test_epic3_activity3_1_standardization_and_resampling`: Verifies stereo-to-mono channel standardization and 44.1 kHz to 16 kHz sample rate normalization.
3. `test_epic3_activity3_1_fixed_duration_window_segmentation`: Verifies fixed 1.0s windowing, timestamp boundaries, and exact $[0, 14]$ video frame synchronization.
4. `test_epic3_activity3_1_structured_storage_and_export`: Validates structured JSON and CSV file persistence with all amplitude metrics and headers.
5. `test_epic3_activity3_1_api_endpoints`: Verifies all Activity 3.1 FastAPI endpoints asynchronously.
