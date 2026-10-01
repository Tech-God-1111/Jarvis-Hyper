from elevenlabs import ElevenLabs, play
from elevenlabs.client import AsyncElevenLabs
import asyncio
from typing import Optional
from .config import config


class VoiceService:
    def __init__(self):
        self.client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
        self.async_client = None
        self.voice_id = config.VOICE_ID
        self.model = config.VOICE_MODEL

    async def init_async(self):
        """Initialize async client"""
        if not self.async_client:
            self.async_client = AsyncElevenLabs(api_key=config.ELEVENLABS_API_KEY)
        return self.async_client

    def speak(self, text: str, rate: float = 1.0) -> bytes:
        """Convert text to speech and return audio bytes"""
        try:
            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model,
                voice_settings={
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "speed": rate,
                }
            )
            return b"".join(audio)
        except Exception as e:
            print(f"Voice error: {e}")
            return None

    async def speak_async(self, text: str, rate: float = 1.0) -> Optional[bytes]:
        """Async version of speak"""
        try:
            client = await self.init_async()
            audio = await client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model,
                voice_settings={
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "speed": rate,
                }
            )
            return b"".join([chunk async for chunk in audio])
        except Exception as e:
            print(f"Voice error: {e}")
            return None

    def play_audio(self, audio_bytes: bytes):
        """Play audio bytes"""
        try:
            play(audio_bytes)
        except Exception as e:
            print(f"Play error: {e}")


voice_service = VoiceService()