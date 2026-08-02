"""
agents/voice_agent.py
~~~~~~~~~~~~~~~~~~~~~
Voice Agent: Specializes in STT, TTS, language auto-detection, and emotion adaptation.
"""

from typing import Dict, Any
from agents.base_agent import BaseAgent
from core.event_bus import event_bus, EventMessage


class VoiceAgent(BaseAgent):
    """Voice Agent for neural TTS synthesis, STT transcription, and language detection."""

    def __init__(self):
        super().__init__(
            agent_id="voice_agent",
            role="Voice & Audio Conversational Engineer",
            capabilities=["stt", "tts", "language_detection", "emotion_adaptation"],
        )
        event_bus.subscribe("AGENT_OS_VOICE", self.handle_event)

    def handle_event(self, event: EventMessage):
        task_id = event.payload.get("task_id", event.correlation_id)
        if self.is_cancelled(task_id):
            return

        text = event.payload.get("text", "")
        detected_lang = self.detect_language(text)

        res = {
            "text": text,
            "detected_language": detected_lang,
            "voice": (
                "hi-IN-MadhurNeural" if detected_lang in ["hi", "hinglish"] else "en-US-GuyNeural"
            ),
            "tone": "UP Prayagraj conversational & friendly",
            "audio_format": "mp3",
        }

        self.send_message(
            "AGENT_OS_RESULT",
            {"task_id": task_id, "agent_id": self.agent_id, "status": "SUCCESS", "result": res},
            correlation_id=event.correlation_id,
        )

    def detect_language(self, text: str) -> str:
        text_lower = text.lower()
        hindi_keywords = ["namaste", "bhai", "kya", "kaise", "batao", "boss", "shukriya"]
        if any(kw in text_lower for kw in hindi_keywords):
            return "hinglish"
        return "en"


# Global Singleton Instance
voice_agent_os = VoiceAgent()
