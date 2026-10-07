from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import uuid
import traceback
import sys
import subprocess
import re
import time
import threading

from core.ai import ai_service
from core.voice import voice_service

router = APIRouter(prefix="/chat", tags=["Chat"])


# ============================================================
# APP LAUNCHER WHITELIST
# ============================================================
APP_WHITELIST = {
    "chrome":         "start chrome",
    "google":         "start chrome",
    "edge":           "start msedge",
    "microsoft edge": "start msedge",
    "notepad":        "start notepad",
    "calculator":     "start calc",
    "calc":           "start calc",
    "explorer":       "start explorer",
    "file explorer":  "start explorer",
    "task manager":   "start taskmgr",
    "taskmgr":        "start taskmgr",
    "settings":       "start ms-settings:",
    "camera":         "start microsoft.windows.camera:",
    "war thunder":    "start steam://rungameid/236390",
    "steam":          "start steam:",
    "word":           "start winword",
    "excel":          "start excel",
    "vs code":        "start code",
    "vscode":         "start code",
}


# ============================================================
# LAUNCH APP
# ============================================================
def launch_app(app_key: str) -> tuple[bool, str]:
    """Launch app. Returns (success, message)."""
    command = APP_WHITELIST.get(app_key)
    if not command:
        return False, f"'{app_key}' is not in the whitelist, Sir."

    try:
        print(f"[LAUNCHER] Launching: {app_key} → {command}")
        if sys.platform == "win32":
            subprocess.Popen(command, shell=True)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-a", app_key])
        else:
            subprocess.Popen(command, shell=True)
        return True, f"Opening {app_key.title()}, Sir."
    except Exception as e:
        print(f"[LAUNCHER] Error: {e}")
        return False, f"Failed to open {app_key}: {e}"


# ============================================================
# TYPE TEXT (pyautogui)
# ============================================================
def type_text(text: str, delay_after_open: float = 1.5):
    """
    Types text into the currently focused window using pyautogui.
    Must be called AFTER the target app is open and focused.
    """
    try:
        import pyautogui
        pyautogui.FAILSAFE = False
        time.sleep(delay_after_open)

        clean = text.replace("\r\n", "\n").replace("\r", "\n")

        print(f"[TYPIST] Typing {len(clean)} chars...")
        pyautogui.typewrite(clean, interval=0.02)
        print(f"[TYPIST] Done typing")
        return True, "Typed successfully"
    except Exception as e:
        print(f"[TYPIST] Error: {e}")
        return False, f"Typing failed: {e}"


def type_text_async(text: str, delay_after_open: float = 1.5):
    """Fire-and-forget typing on a background thread."""
    t = threading.Thread(
        target=type_text,
        args=(text, delay_after_open),
        daemon=True,
    )
    t.start()
    return t


# ============================================================
# COMMAND PARSER
# ============================================================
def parse_command(text: str) -> Optional[dict]:
    """
    Parse user message for commands.
    Returns dict with keys:
        - type: 'launch' | 'launch_and_type' | 'launch_and_generate'
        - app: app name
        - content: text to type (literal)
        - content_prompt: prompt to send to LLM to GENERATE content
    Returns None if not a command.
    """
    lower = text.lower().strip().rstrip(".!?")

    # --- Strip wake-word (including misheard variants) ---
    lower = re.sub(
        r"^(hey\s+)?(jarvis|davis|jervis|jarvus|charvis|javis)\s+",
        "", lower
    )

    # --- Expanded generate-prompts list ---
    generated_prompts = [
        # Self-description
        "passage about yourself", "passage about you",
        "paragraph about yourself", "something about yourself",
        "something about yours", "something about you",
        "introduce yourself", "your introduction",
        "about yourself", "about yours", "about you",
        # Verbs that imply generation
        "explain about yourself", "explain yourself",
        "describe yourself", "tell me about yourself",
        "what model you use", "what model do you use",
        "explain your", "describe your",
        # Creative content
        "a poem", "a story", "a joke", "a python program",
        "a program", "a letter", "an essay",
        # Generic
        "something",
    ]

    # ----------------------------------------------------------
    # Pattern 1: "open X and type/write Y" or "open X then ..."
    # ----------------------------------------------------------
    m = re.match(
        r"^(?:open|launch|start|run)\s+(.+?)\s+(?:and|then)\s+"
        r"(?:type|write|say|explain|describe|tell\s+me|what)\s+"
        r"(?:this\s+)?(?:in\s+it\s+)?(?:that\s+)?(.+)$",
        lower, re.IGNORECASE,
    )
    if m:
        app_part = m.group(1).strip()
        content_part = m.group(2).strip()

        app_key = None
        for key in APP_WHITELIST.keys():
            if key in app_part or app_part in key:
                app_key = key
                break

        if app_key:
            is_generate = any(p in content_part for p in generated_prompts)
            if is_generate:
                return {
                    "type": "launch_and_generate",
                    "app": app_key,
                    "content_prompt": content_part,
                }
            else:
                return {
                    "type": "launch_and_type",
                    "app": app_key,
                    "content": m.group(2).strip(),
                }

    # ----------------------------------------------------------
    # Pattern 2: "type X in Y" / "type X into Y"
    # ----------------------------------------------------------
    m = re.match(
        r"^(?:type|write)\s+(.+?)\s+(?:in|into|on)\s+(.+)$",
        lower, re.IGNORECASE,
    )
    if m:
        content_part = m.group(1).strip()
        app_part = m.group(2).strip()

        app_key = None
        for key in APP_WHITELIST.keys():
            if key in app_part or app_part in key:
                app_key = key
                break

        if app_key:
            is_generate = any(p in content_part for p in generated_prompts)
            if is_generate:
                return {
                    "type": "launch_and_generate",
                    "app": app_key,
                    "content_prompt": content_part,
                }
            else:
                return {
                    "type": "launch_and_type",
                    "app": app_key,
                    "content": m.group(1).strip(),
                }

    # ----------------------------------------------------------
    # Pattern 3: simple "open X"
    # ----------------------------------------------------------
    m = re.match(r"^(?:open|launch|start|run)\s+(.+)$", lower, re.IGNORECASE)
    if m:
        app_part = m.group(1).strip().rstrip(".!")
        app_part = app_part.replace(" app", "").replace(" application", "")

        for key in APP_WHITELIST.keys():
            if key in app_part or app_part in key:
                return {"type": "launch", "app": key}

    return None


# ============================================================
# REQUEST MODELS
# ============================================================
class Attachment(BaseModel):
    name: str
    mime: str
    content: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    speak: bool = True
    attachment: Optional[Attachment] = None


# ============================================================
# GENERATE CONTENT (for launch_and_generate)
# ============================================================
def generate_content_for_typing(user_prompt: str) -> str:
    """Ask the LLM to generate content that we'll type into an app."""
    system = (
        "You are JARVIS. The user asked you to write something into a text editor. "
        "Generate ONLY the text to be typed. No markdown, no quotes, no explanation. "
        "Just the raw text content. Keep it concise and directly usable."
    )
    try:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ]
        response = ai_service.chat_sync(messages)
        return response.strip()
    except Exception as e:
        print(f"[GEN] Error: {e}")
        return f"JARVIS here. I am your personal AI assistant. (Generation failed: {e})"


# ============================================================
# CHAT ENDPOINT
# ============================================================
@router.post("/stream")
async def chat_stream(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    # Parse for commands FIRST
    command = parse_command(req.message)

    # Build user text (for LLM path)
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

        # ============================================================
        # CASE 1: Simple launch
        # ============================================================
        if command and command["type"] == "launch":
            success, msg = launch_app(command["app"])
            print(f"[CHAT] Launch: {command['app']} → {success}")

            yield f"data: {json.dumps({'type': 'delta', 'content': msg})}\n\n"

            if req.speak:
                try:
                    audio_bytes = voice_service.speak(msg)
                    if audio_bytes:
                        yield f"data: {json.dumps({'type': 'voice', 'audio': list(audio_bytes)})}\n\n"
                except Exception as e:
                    print(f"[VOICE] Error: {e}")

            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return

        # ============================================================
        # CASE 2: Launch + type literal text
        # ============================================================
        if command and command["type"] == "launch_and_type":
            app = command["app"]
            content = command["content"]

            success, msg = launch_app(app)
            if success:
                type_text_async(content, delay_after_open=2.0)
                response_text = (
                    f"Opening {app.title()} and typing your message, Sir. "
                    f"That's {len(content)} characters."
                )
            else:
                response_text = f"Failed to open {app}. {msg}"

            print(f"[CHAT] Launch+Type: {app} → {success}")

            yield f"data: {json.dumps({'type': 'delta', 'content': response_text})}\n\n"

            if req.speak:
                try:
                    audio_bytes = voice_service.speak(response_text)
                    if audio_bytes:
                        yield f"data: {json.dumps({'type': 'voice', 'audio': list(audio_bytes)})}\n\n"
                except Exception as e:
                    print(f"[VOICE] Error: {e}")

            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return

        # ============================================================
        # CASE 3: Launch + generate content + type
        # ============================================================
        if command and command["type"] == "launch_and_generate":
            app = command["app"]
            prompt = command["content_prompt"]

            yield f"data: {json.dumps({'type': 'delta', 'content': 'Composing that for you, Sir...'})}\n\n"

            # Generate content via LLM
            generated = generate_content_for_typing(prompt)
            print(f"[CHAT] Generated {len(generated)} chars for typing")

            # Launch + type in background
            success, msg = launch_app(app)
            if success:
                type_text_async(generated, delay_after_open=2.0)
                response_text = (
                    f"Opening {app.title()} and typing the passage now, Sir. "
                    f"{len(generated)} characters on the way."
                )
            else:
                response_text = f"Failed to open {app}. {msg}"

            yield f"data: {json.dumps({'type': 'delta', 'content': response_text})}\n\n"

            if req.speak:
                try:
                    audio_bytes = voice_service.speak(response_text)
                    if audio_bytes:
                        yield f"data: {json.dumps({'type': 'voice', 'audio': list(audio_bytes)})}\n\n"
                except Exception as e:
                    print(f"[VOICE] Error: {e}")

            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return

        # ============================================================
        # CASE 4: Normal LLM chat
        # ============================================================
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
                    audio_bytes = voice_service.speak(full_response)
                    if audio_bytes:
                        yield f"data: {json.dumps({'type': 'voice', 'audio': list(audio_bytes)})}\n\n"
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