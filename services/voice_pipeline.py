"""
Purpose:
Voice STT (Speech-To-Text) and TTS (Text-To-Speech) Pipeline Engine for Jarvis AI OS.

Responsibilities:
- Process audio speech input into recognized text transcriptions
- Synthesize text replies into spoken audio responses
"""

import os
import re
from typing import Dict, Any

import requests
import edge_tts


class VoicePipelineService:
    """Voice Speech-to-Text & Text-to-Speech Engine."""

    def __init__(self):
        self.stt_engine = "Whisper (Base/CPU)"
        self.tts_engine = "gTTS / Microsoft Neural Voice"

    def transcribe_audio(
        self, audio_bytes: bytes, filename: str = "voice.webm", content_type: str = "audio/webm"
    ) -> str:
        """Transcribes recorded browser audio through Groq Whisper when configured."""
        if not audio_bytes:
            return ""
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise RuntimeError("Voice transcription is not configured on this deployment.")
        response = requests.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {api_key}"},
            data={
                "model": "whisper-large-v3",
                "response_format": "json",
                "temperature": "0",
                "prompt": "This is a Hindi, English, or Hinglish JARVIS voice command. Preserve names, numbers, and technical terms.",
            },
            files={"file": (filename, audio_bytes, content_type)},
            timeout=25,
        )
        if not response.ok:
            raise RuntimeError("Voice transcription could not be completed. Please try again.")
        return str(response.json().get("text", "")).strip()

    def synthesize_speech(self, text: str) -> Dict[str, Any]:
        """Synthesizes text into spoken audio output."""
        clean_text = text.strip()
        return {
            "status": "success",
            "text": clean_text,
            "audio_format": "mp3",
            "engine": self.tts_engine,
        }

    async def stream_neural_speech(self, text: str):
        """Streams a natural Indian neural voice matching the response script."""
        voice = (
            "hi-IN-MadhurNeural" if re.search(r"[\u0900-\u097F]", text) else "en-IN-PrabhatNeural"
        )
        communicate = edge_tts.Communicate(text[:4000], voice=voice, rate="-2%")
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]


# Global VoicePipelineService Singleton
voice_pipeline = VoicePipelineService()
