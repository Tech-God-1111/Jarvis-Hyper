from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional

from core.voice import voice_service

router = APIRouter(prefix="/voice", tags=["Voice"])

class SpeakRequest(BaseModel):
    text: str
    rate: float = 1.0

@router.post("/speak")
async def speak(req: SpeakRequest):
    """Convert text to speech and return audio"""
    audio_bytes = voice_service.speak(req.text, req.rate)
    if not audio_bytes:
        raise HTTPException(500, "Voice generation failed")
    return Response(content=audio_bytes, media_type="audio/mpeg")

@router.post("/speak/stream")
async def speak_stream(req: SpeakRequest):
    """Stream voice response"""
    audio_bytes = voice_service.speak(req.text, req.rate)
    if not audio_bytes:
        raise HTTPException(500, "Voice generation failed")
    return Response(content=audio_bytes, media_type="audio/mpeg")