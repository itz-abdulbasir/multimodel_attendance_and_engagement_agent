"""
Multimodal Attendance & Engagement Agent - AI Suggestion Engine
Epic 4: AI Implementation - Activity 4.2: Multimodal Signal Fusion
Reference: backend/core/ai_suggestions.py (AISuggestionEngine)
"""

import os
import json
import time
from typing import Dict, List, Any, Optional

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class AISuggestionEngine:
    """
    AI Suggestion Engine for Multimodal Signal Fusion (Epic 4: Activity 4.2).
    Generates actionable teaching interventions and pedagogical suggestions based on
    fused visual indicators (presence, movement, inactivity) and audio indicators (noise, speech).
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model
        self.client: Optional[Any] = None

        if self.api_key and GROQ_AVAILABLE:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"[AISuggestionEngine] Warning: Could not initialize Groq client: {e}")
                self.client = None

    def build_prompt(self, session_data: dict) -> str:
        """Constructs prompt correlating visual indicators with audio dynamics."""
        # Visual indicators
        presence_sec = session_data.get("presence_duration_seconds", 300.0)
        movement_pattern = session_data.get("movement_pattern", "MODERATE_FOCUSED")
        motion_energy = session_data.get("average_motion_energy", 0.05)
        inactivity_sec = session_data.get("inactivity_seconds", 0.0)
        v_attention = session_data.get("average_visual_attention", 0.75) * 100.0 if session_data.get("average_visual_attention", 0.75) <= 1.0 else session_data.get("average_visual_attention", 75.0)

        # Audio indicators
        noise_spl = session_data.get("noise_level_spl", 55.0)
        ambient_noise = session_data.get("ambient_noise_level", "MODERATE")
        speech_state = session_data.get("signal_classification", "ACTIVE_SPEECH")
        rhythm = session_data.get("rhythm_state", "INSTRUCTOR_MONOLOGUE")
        part_freq = session_data.get("participation_frequency", 1.0)
        ei = session_data.get("engagement_index", 75.0)

        prompt = (
            f"Classroom Multimodal Fusion Indicators:\n"
            f"[Visual Modality]\n"
            f"- Visual Focus / Board Gaze: {v_attention:.1f}%\n"
            f"- Cumulative Presence Duration: {presence_sec:.0f}s\n"
            f"- Movement Pattern & Posture: {movement_pattern} (Motion Energy: {motion_energy:.3f})\n"
            f"- Prolonged Inactivity Period: {inactivity_sec:.1f}s\n\n"
            f"[Audio Modality]\n"
            f"- Ambient Noise Level: {noise_spl:.1f} dB SPL ({ambient_noise})\n"
            f"- Speech Activity State: {speech_state} (Rhythm: {rhythm})\n"
            f"- Student Participation Frequency: {part_freq:.1f} turns/min\n\n"
            f"[Composite Telemetry]\n"
            f"- Fused Engagement Index: {ei:.1f}%\n\n"
            f"Provide 2-3 specific, actionable teaching suggestions for the instructor. "
            f"Format each suggestion as:\n"
            f"- TITLE: <short title>\n"
            f"  ACTION: <specific pedagogical adjustment>\n"
            f"  RATIONALE: <why based on visual-audio fusion>"
        )
        return prompt

    def generate_suggestions(self, session_data: dict) -> List[Dict[str, Any]]:
        """
        Generates teaching suggestions from synchronized multimodal session data.
        Matches reference signature: generate_suggestions(self, session_data: dict)
        """
        prompt = self.build_prompt(session_data)

        try:
            if not self.client:
                return self._fallback_suggestions(session_data)

            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert AI teaching assistant."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=200
            )

            response = completion.choices[0].message.content
            return self._parse_response(response)

        except Exception as e:
            print(f"AI Suggestion Error: {e}")
            return self._fallback_suggestions(session_data)

    def _parse_response(self, response: str) -> List[Dict[str, Any]]:
        """Parses LLM textual completion into structured suggestion items."""
        suggestions = []
        current = {}

        for raw_line in response.split("\n"):
            line = raw_line.strip()
            if not line:
                continue

            if "TITLE:" in line.upper():
                if current and "title" in current:
                    suggestions.append(current)
                    current = {}
                title_idx = line.upper().find("TITLE:") + len("TITLE:")
                current["title"] = line[title_idx:].strip().strip("- ")
                current["timestamp"] = time.time()
                current["model"] = self.model
            elif "ACTION:" in line.upper() and current:
                act_idx = line.upper().find("ACTION:") + len("ACTION:")
                current["action"] = line[act_idx:].strip()
            elif "RATIONALE:" in line.upper() and current:
                rat_idx = line.upper().find("RATIONALE:") + len("RATIONALE:")
                current["rationale"] = line[rat_idx:].strip()

        if current and "title" in current:
            suggestions.append(current)

        # Fallback if structure parsing produced empty list
        if not suggestions:
            clean_text = response.strip().replace("\n\n", "\n")
            suggestions.append({
                "title": "Instructional Flow Recommendation",
                "action": clean_text[:140] if len(clean_text) > 140 else clean_text,
                "rationale": "Generated via Groq LLaMA-3 based on fused classroom dynamics.",
                "model": self.model,
                "timestamp": time.time()
            })

        return suggestions

    def _fallback_suggestions(self, session_data: dict) -> List[Dict[str, Any]]:
        """
        Deterministic, interpretable pedagogical suggestion generator when offline.
        Uses exact correlation between visual attention and audio interaction.
        """
        now = time.time()
        suggestions = []

        v_att = session_data.get("average_visual_attention", 0.75)
        if v_att <= 1.0:
            v_att *= 100.0
        motion = session_data.get("average_motion_energy", 0.05)
        inactivity_sec = session_data.get("inactivity_seconds", 0.0)
        noise_spl = session_data.get("noise_level_spl", 55.0)
        ambient = session_data.get("ambient_noise_level", "MODERATE")
        rhythm = session_data.get("rhythm_state", "INSTRUCTOR_MONOLOGUE")
        part_freq = session_data.get("participation_frequency", 1.0)
        ei = session_data.get("engagement_index", 75.0)

        # Suggestion 1: Acoustic disruption vs. Visual focus
        if ambient == "LOUD_DISRUPTIVE" or noise_spl >= 75.0:
            suggestions.append({
                "title": "Room Acoustic Reset",
                "action": "Pause lecture briefly to address room cross-talk and regain acoustic focus.",
                "rationale": f"High ambient noise ({noise_spl:.1f} dB SPL) is competing with student visual concentration ({v_att:.1f}%).",
                "model": "offline_rule_reasoner",
                "timestamp": now
            })
        elif rhythm == "QA_INTERACTION" and part_freq < 0.8:
            suggestions.append({
                "title": "Interactive Scaffolding Check",
                "action": "Pose a targeted concept question to a specific group or initiate a 60-second peer Think-Pair-Share.",
                "rationale": f"Q&A session active with high visual attention ({v_att:.1f}%) but low verbal turn-taking ({part_freq:.1f} turns/min).",
                "model": "offline_rule_reasoner",
                "timestamp": now
            })
        elif v_att < 55.0 and noise_spl < 52.0:
            suggestions.append({
                "title": "Visual Re-Engagement Reset",
                "action": "Switch presentation medium, show a live code demonstration, or ask an open-ended application question.",
                "rationale": f"Classroom is quiet ({noise_spl:.1f} dB SPL) but visual focus is wandering ({v_att:.1f}% focus).",
                "model": "offline_rule_reasoner",
                "timestamp": now
            })
        elif inactivity_sec >= 90.0 and motion < 0.02:
            suggestions.append({
                "title": "Physical Alertness Boost",
                "action": "Conduct a 30-second stand-up stretch or quick thumbs-up polling exercise.",
                "rationale": f"Prolonged physical dormancy detected ({inactivity_sec:.0f}s with motion < 0.02).",
                "model": "offline_rule_reasoner",
                "timestamp": now
            })
        elif motion > 0.40 and v_att < 60.0:
            suggestions.append({
                "title": "Pacing Adjustment for Restlessness",
                "action": "Transition to an active problem-solving segment to channel physical energy into the lesson.",
                "rationale": f"Elevated physical restlessness (motion: {motion:.2f}) combined with declining visual attention.",
                "model": "offline_rule_reasoner",
                "timestamp": now
            })
        else:
            suggestions.append({
                "title": "Instructional Flow Maintenance",
                "action": "Continue current instructional progression; learners are displaying harmonious visual and acoustic balance.",
                "rationale": f"High multimodal engagement index ({ei:.1f}%) with balanced visual attention ({v_att:.1f}%) and acoustic resonance.",
                "model": "offline_rule_reasoner",
                "timestamp": now
            })

        return suggestions
