from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import config
from routes import chat, voice, data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    print("JARVIS-HYPER Starting...")
    print(f"Voice: {config.VOICE_ID}")
    print(f"Model chain: {len(config.MODEL_CONFIGS)} tiers loaded")
    for i, mc in enumerate(config.MODEL_CONFIGS, start=1):
        print(f"  Tier {i}: {mc['model']}")
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

# Routes
app.include_router(chat.router, prefix="/api")
app.include_router(voice.router, prefix="/api")
app.include_router(data.router, prefix="/api")


@app.get("/")
async def root():
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