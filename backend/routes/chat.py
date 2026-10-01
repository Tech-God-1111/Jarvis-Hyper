from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import uuid
import traceback

from core.ai import ai_service
from core.voice import voice_service

router = APIRouter(prefix="/chat", tags=["Chat"])


class Attachment(BaseModel):
    name: str
    mime: str
    content: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    speak: bool = True
    attachment: Optional[Attachment] = None


@router.post("/stream")
async def chat_stream(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    user_text = req.message
    if req.attachment and req.attachment.content:
        file_content = req.attachment.content[:80000]
        user_text = (
            f"[ATTACHED FILE: {req.attachment.name} | {req.attachment.mime}]\n"
            f"---BEGIN FILE---\n{file_content}\n---END FILE---\n\n"
            f"USER QUESTION: {req.message}"
        )

    messages = [{"role": "user", "content": user_text}]

    async def generate():
        yield f"data: {json.dumps({'type': 'session', 'session_id': session_id})}\n\n"

        full_response = ""
        try:
            print(f"[CHAT] Received: {req.message[:80]}")

            for chunk in ai_service.chat_stream_with_failover(messages):
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta
                reasoning = getattr(delta, "reasoning_content", None)
                if reasoning:
                    continue

                if delta.content:
                    full_response += delta.content
                    yield f"data: {json.dumps({'type': 'delta', 'content': delta.content})}\n\n"

            print(f"[CHAT] Response: {full_response[:120]}")

            if req.speak and full_response.strip():
                try:
                    print(f"[VOICE] Generating voice...")
                    audio_bytes = voice_service.speak(full_response)
                    if audio_bytes:
                        yield f"data: {json.dumps({'type': 'voice', 'audio': list(audio_bytes)})}\n\n"
                        print(f"[VOICE] {len(audio_bytes)} bytes")
                except Exception as e:
                    print(f"[VOICE] Error: {e}")

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            print(f"[CHAT] EXCEPTION: {e}")
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/send")
async def chat_send(req: ChatRequest):
    messages = [{"role": "user", "content": req.message}]
    response = ai_service.chat_sync(messages)
    return {"response": response}