import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")


class Config:
    # Three separate keys + three separate models
    MODEL_CONFIGS = [
        {
            "key": os.getenv("NVIDIA_API_KEY_1"),
            "model": os.getenv("MODEL_1", "nvidia/nemotron-3-ultra-550b-a55b"),
        },
        {
            "key": os.getenv("NVIDIA_API_KEY_2"),
            "model": os.getenv("MODEL_2", "nvidia/nemotron-3-super-120b-a12b"),
        },
        {
            "key": os.getenv("NVIDIA_API_KEY_3"),
            "model": os.getenv("MODEL_3", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"),
        },
    ]

    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    PORT = int(os.getenv("PORT", 8000))

    VOICE_ID = os.getenv("VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
    VOICE_MODEL = os.getenv("VOICE_MODEL", "eleven_turbo_v2_5")
    WAKE_WORD = os.getenv("WAKE_WORD", "jarvis")

    SYSTEM_PROMPT = (
        "You are JARVIS — Just A Rather Very Intelligent System — the personal AI assistant "
        "originally engineered by Tony Stark. You speak with calm, dry British wit, immaculate "
        "precision, and unflappable composure. You address the user as 'Sir' or 'Boss' "
        "interchangeably. Keep responses SHORT and PUNCHY for voice output."
    )


config = Config()