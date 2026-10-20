"""
Multimodal Attendance & Engagement Agent - LLM Classroom Insights Generator
Epic 4: AI Implementation - Activity 4.1: Multimodal Agent Implementation
Reference: backend/core/llm_insights.py (InsightGenerator)
"""

import os
import json
import time
from typing import Dict, Any, Optional

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class InsightGenerator:
    """
    LLM-Powered Classroom Insight Generator.
    Uses Groq Cloud (llama-3.3-70b-versatile) with robust offline fallback
    to synthesize contextual, interpretable, and actionable educational insights from session data.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model
        self.client: Optional[Any] = None
        
        if self.api_key and GROQ_AVAILABLE:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"[InsightGenerator] Warning: Could not initialize Groq client: {e}")
                self.client = None

    def build_prompt(self, session_data: Dict[str, Any]) -> str:
        """Constructs an interpretable prompt from multimodal session metrics."""
        ei = session_data.get("engagement_index", 75.0)
        v_att = session_data.get("visual_attention_score", 0.75) * 100.0 if session_data.get("visual_attention_score", 0.75) <= 1.0 else session_data.get("visual_attention_score", 75.0)
        motion = session_data.get("motion_balance_score", 0.90)
        rhythm = session_data.get("rhythm_state", "INSTRUCTOR_MONOLOGUE")
        spl_db = session_data.get("noise_level_spl", 55.0)
        ambient = session_data.get("ambient_noise_level", "MODERATE")
        turn_freq = session_data.get("participation_frequency", 1.0)
        speech_state = session_data.get("signal_classification", "ACTIVE_SPEECH")
        trend = session_data.get("trend", "STABLE")
        active_count = session_data.get("active_participants", 0)

        prompt = (
            f"Classroom Session Telemetry:\n"
            f"- Composite Engagement Index: {ei:.1f}% ({trend})\n"
            f"- Visual Focus Ratio: {v_att:.1f}%\n"
            f"- Motion Balance: {motion:.2f}\n"
            f"- Classroom Acoustic Rhythm: {rhythm}\n"
            f"- Ambient Sound Pressure: {spl_db:.1f} dB SPL ({ambient})\n"
            f"- Speech Activity State: {speech_state}\n"
            f"- Student Turn-Taking Frequency: {turn_freq:.1f} turns/min\n"
            f"- Active Attendees Detected: {active_count}\n\n"
            f"Please respond in the following exact format:\n"
            f"INSIGHT: <one sentence summarizing class engagement state>\n"
            f"RECOMMENDATION: <one actionable pedagogical suggestion for the instructor>"
        )
        return prompt

    def generate_classroom_insight(self, session_data: dict) -> dict:
        """
        Generates contextual classroom insight and teaching recommendations from session data.
        Integrates Groq API with robust rule-based offline fallback.
        """
        prompt = self.build_prompt(session_data)
        # Compute dynamic, context-aware baseline from session telemetry
        insight, recommendation = self._generate_offline_insight(session_data)
        used_offline = True
        raw_response = ""

        if self.client:
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert educational AI assistant. "
                                "Provide brief, professional, and actionable insights for "
                                "classroom engagement and pedagogical optimization."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=self.model,
                    temperature=0.5,
                    max_tokens=150,
                )

                response_text = chat_completion.choices[0].message.content
                raw_response = response_text

                # Parse LLM Response
                lines = response_text.strip().split("\n")
                parsed_insight = None
                parsed_rec = None
                for line in lines:
                    line_clean = line.strip()
                    if line_clean.upper().startswith("INSIGHT:"):
                        parsed_insight = line_clean[len("INSIGHT:"):].strip()
                    elif line_clean.upper().startswith("RECOMMENDATION:"):
                        parsed_rec = line_clean[len("RECOMMENDATION:"):].strip()

                if parsed_insight:
                    insight = parsed_insight
                elif len(lines) > 0 and lines[0]:
                    insight = lines[0].replace("INSIGHT:", "").strip()

                if parsed_rec:
                    recommendation = parsed_rec
                elif len(lines) > 1 and lines[1]:
                    recommendation = lines[1].replace("RECOMMENDATION:", "").strip()

                used_offline = False

            except Exception as e:
                # Fallback to local deterministic reasoning if API fails
                print(f"[InsightGenerator] Groq API call failed ({e}), using offline reasoning.")
                insight, recommendation = self._generate_offline_insight(session_data)
                raw_response = f"Fallback error: {str(e)}"
        else:
            insight, recommendation = self._generate_offline_insight(session_data)
            raw_response = "Offline rule-based intelligence"

        return {
            "status": "success",
            "insight": insight,
            "recommendation": recommendation,
            "model": self.model if not used_offline else "offline_rule_reasoner",
            "is_offline": used_offline,
            "timestamp": time.time(),
            "raw_response": raw_response
        }

    def _generate_offline_insight(self, session_data: dict) -> tuple[str, str]:
        """Deterministic, interpretable pedagogical reasoning engine when offline."""
        ei = session_data.get("engagement_index", 75.0)
        v_att = session_data.get("visual_attention_score", 0.75)
        if v_att <= 1.0:
            v_att *= 100.0
        spl_db = session_data.get("noise_level_spl", 55.0)
        ambient = session_data.get("ambient_noise_level", "MODERATE")
        rhythm = session_data.get("rhythm_state", "INSTRUCTOR_MONOLOGUE")
        turn_freq = session_data.get("participation_frequency", 1.0)
        trend = session_data.get("trend", "STABLE")
        drop_alert = session_data.get("attention_drop_alert", False)

        if drop_alert or (trend == "DROPPING" and ei < 55.0):
            insight = "Collective attention drop detected with declining visual focus."
            recommendation = "Pause the presentation and initiate a 60-second interactive comprehension poll."
        elif ambient == "LOUD_DISRUPTIVE" or spl_db >= 75.0:
            insight = f"Elevated ambient room noise ({spl_db:.1f} dB SPL) is creating acoustic distraction."
            recommendation = "Briefly pause lecturing to address room cross-talk and regain acoustic focus."
        elif rhythm == "QA_INTERACTION" and turn_freq < 0.8:
            insight = "Active Q&A session identified but student verbal turn-taking frequency is low."
            recommendation = "Pose an open-ended question to specific peer clusters to spark participation."
        elif v_att < 55.0 and spl_db < 50.0:
            insight = "Classroom is quiet but visual gaze has significantly wandered from the board."
            recommendation = "Re-engage learners with a relatable real-world example or live visual demonstration."
        elif ei >= 80.0 and (rhythm == "QA_INTERACTION" or turn_freq >= 1.5):
            insight = "High multimodal engagement observed with vibrant question-and-answer dialogue."
            recommendation = "Maintain current momentum and transition into an advanced conceptual challenge."
        else:
            insight = "Classroom status is stable with balanced visual focus and instructional rhythm."
            recommendation = "Maintain current instructional pace and monitor upcoming transition intervals."

        return insight, recommendation
