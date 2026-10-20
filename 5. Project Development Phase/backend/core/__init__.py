"""
NeuroClass Core Module
EPIC 2: Vision Module Development
- Activity 2.1: Face Detection and Tracking (FaceDetector, CameraService, FaceTracker, VisionModulePipeline)
- Activity 2.2: Presence-Based Attendance Logic (FaceRecognizer, PresenceAttendanceEngine, PresenceRecord)

EPIC 3: Audio Module Development
- Activity 3.1: Audio Signal Extraction (AudioAnalyzer, AudioSegment, AudioExtractionResult, standardize_audio_waveform, segment_audio_waveform)
- Activity 3.2: Noise & Speech Activity Analysis (NoiseAndSpeechActivityAnalyzer, SegmentAcousticFeatures)
"""

from backend.core.face_detection import FaceDetector
from backend.core.camera_service import CameraService
from backend.core.face_tracker import FaceTracker, ParticipantTrack
from backend.core.vision_pipeline import VisionModulePipeline
from backend.core.face_recognition import FaceRecognizer
from backend.core.presence_attendance import PresenceAttendanceEngine, PresenceRecord
from backend.core.audio_analysis import (
    AudioAnalyzer,
    AudioSegment,
    AudioExtractionResult,
    standardize_audio_waveform,
    segment_audio_waveform,
    NoiseAndSpeechActivityAnalyzer,
    SegmentAcousticFeatures
)
from backend.core.llm_insights import InsightGenerator
from backend.core.ai_suggestions import AISuggestionEngine
from backend.core.engagement_scoring import (
    EngagementScoringEngine,
    ScoringThresholdConfig,
    TemporalEngagementProfile,
    EngagementSegmentScore,
    FactorAttribution,
    PeakPeriod,
    DisengagementPhase,
    AttentionFluctuationMetrics,
    EngagementLevel,
    ClassroomPreset,
    ScoringRules
)

from backend.core.recommendations_engine import RecommendationsEngine, RecommendationItem
from backend.core.teacher_profiles import TeacherProfileService
from backend.core.analytics_service import AnalyticsService, PersonMetric, FocusZonePeriod

__all__ = [
    "FaceDetector",
    "FaceRecognizer",
    "CameraService",
    "FaceTracker",
    "ParticipantTrack",
    "VisionModulePipeline",
    "PresenceAttendanceEngine",
    "PresenceRecord",
    "AudioAnalyzer",
    "AudioSegment",
    "AudioExtractionResult",
    "standardize_audio_waveform",
    "segment_audio_waveform",
    "NoiseAndSpeechActivityAnalyzer",
    "SegmentAcousticFeatures",
    "InsightGenerator",
    "AISuggestionEngine",
    "EngagementScoringEngine",
    "ScoringThresholdConfig",
    "TemporalEngagementProfile",
    "EngagementSegmentScore",
    "FactorAttribution",
    "PeakPeriod",
    "DisengagementPhase",
    "AttentionFluctuationMetrics",
    "EngagementLevel",
    "ClassroomPreset",
    "ScoringRules",
    "RecommendationsEngine",
    "RecommendationItem",
    "TeacherProfileService",
    "AnalyticsService",
    "PersonMetric",
    "FocusZonePeriod"
]


