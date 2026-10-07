from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import mimetypes

from core.config import config
from routes import chat, voice, data

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("JARVIS-HYPER Starting...")
    print(f"Voice: {config.VOICE_ID}")
    print(f"Model chain: {len(config.MODEL_CONFIGS)} tiers loaded")
    for i, mc in enumerate(config.MODEL_CONFIGS, start=1):
        print(f"  Tier {i}: {mc['model']}")
    print(f"Static dir: {STATIC_DIR}")

    # Verify the faces folder exists
    faces_dir = STATIC_DIR / "faces"
    if faces_dir.exists():
        files = list(faces_dir.iterdir())
        print(f"Faces folder: {[f.name for f in files]}")
    else:
        print(f"WARNING: {faces_dir} does not exist")

    yield
    print("JARVIS-HYPER Shutting down...")


app = FastAPI(
    title="JARVIS-HYPER API",
    description="Hyper-intelligent AI assistant with ElevenLabs voice",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# STATIC FILE ROUTES (explicit — no mounts, no shadowing)
# ============================================================
@app.get("/")
async def serve_login():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/mega")
async def serve_mega():
    return FileResponse(STATIC_DIR / "mega_index.html")


@app.get("/mega_index.html")
async def serve_mega_backup():
    return FileResponse(STATIC_DIR / "mega_index.html")


@app.get("/index.html")
async def serve_login_backup():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/static/{path:path}")
async def serve_static(path: str):
    """Serve any file under static/ — including /static/faces/moses.jpg"""
    file_path = (STATIC_DIR / path).resolve()

    # Security: prevent path traversal
    if not str(file_path).startswith(str(STATIC_DIR.resolve())):
        return Response(status_code=403, content="Forbidden")

    if not file_path.exists() or not file_path.is_file():
        print(f"[STATIC] 404: {file_path}")
        return Response(status_code=404, content=f"Not found: {path}")

    # Guess MIME type
    mime, _ = mimetypes.guess_type(str(file_path))
    if not mime:
        mime = "application/octet-stream"

    return FileResponse(file_path, media_type=mime)


# ============================================================
# API ROUTES
# ============================================================
app.include_router(chat.router, prefix="/api")
app.include_router(voice.router, prefix="/api")
app.include_router(data.router, prefix="/api")


@app.get("/api/")
async def api_root():
    return {
        "name": "JARVIS-HYPER",
        "version": "1.0.0",
        "status": "online",
        "voice": config.VOICE_ID,
        "tiers": [mc["model"] for mc in config.MODEL_CONFIGS],
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.PORT)