"""
JARVIS-HYPER — Configuration
3-tier Nemotron failover + voice + system settings.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")


# ============================================================
# NVIDIA BASE URL
# ============================================================
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"


# ============================================================
# SYSTEM PROMPT
# ============================================================
SYSTEM_PROMPT = (
    "You are JARVIS — Just A Rather Very Intelligent System — the personal AI assistant "
    "originally engineered by Tony Stark. You speak with calm, dry British wit, immaculate "
    "precision, and unflappable composure. You address the user as 'Sir' or 'Boss' "
    "interchangeably. Keep responses SHORT and PUNCHY for voice output."
)


# ============================================================
# 3-TIER MODEL CONFIGS
# ============================================================
MODEL_CONFIGS = [
    {
        "tier": 1,
        "api_key": os.getenv("NVIDIA_API_KEY_1"),
        "model": os.getenv("MODEL_1", "nvidia/nemotron-3-ultra-550b-a55b"),
        "enable_thinking": True,
        "max_tokens": 4096,
    },
    {
        "tier": 2,
        "api_key": os.getenv("NVIDIA_API_KEY_2"),
        "model": os.getenv("MODEL_2", "nvidia/nemotron-3-super-120b-a12b"),
        "enable_thinking": False,
        "max_tokens": 4096,
    },
    {
        "tier": 3,
        "api_key": os.getenv("NVIDIA_API_KEY_3"),
        "model": os.getenv("MODEL_3", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"),
        "enable_thinking": True,
        "max_tokens": 4096,
    },
]


# ============================================================
# VOICE (ElevenLabs)
# ============================================================
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
VOICE_MODEL = os.getenv("VOICE_MODEL", "eleven_turbo_v2_5")
WAKE_WORD = os.getenv("WAKE_WORD", "jarvis")


# ============================================================
# SERVER
# ============================================================
PORT = int(os.getenv("PORT", 8000))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")


# ============================================================
# CONFIG CLASS (backward compatibility)
# ============================================================
class Config:
    MODEL_CONFIGS = MODEL_CONFIGS
    NVIDIA_BASE_URL = NVIDIA_BASE_URL
    SYSTEM_PROMPT = SYSTEM_PROMPT
    ELEVENLABS_API_KEY = ELEVENLABS_API_KEY
    VOICE_ID = VOICE_ID
    VOICE_MODEL = VOICE_MODEL
    WAKE_WORD = WAKE_WORD
    PORT = PORT
    CORS_ORIGINS = CORS_ORIGINS


config = Config()