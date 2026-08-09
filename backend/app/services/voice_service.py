import os
import io
import requests
from typing import Optional


class VoiceService:
    @staticmethod
    def generate_tts_audio(text: str, voice: str = "alloy") -> bytes:
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY environment variable missing.")

        clean_text = (
            text.replace("*", "")
            .replace("#", "")
            .replace("`", "")
            .replace("\n", " ")
            [:1000]
        )

        res = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "tts-1",
                "input": clean_text,
                "voice": voice or "alloy",
            },
            timeout=15,
        )

        if res.status_code == 200:
            return res.content
        else:
            raise RuntimeError(f"OpenAI TTS API error {res.status_code}: {res.text}")
