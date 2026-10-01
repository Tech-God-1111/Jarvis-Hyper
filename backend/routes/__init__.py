# Routes module for JARVIS-HYPER backend
from .chat import router as chat_router
from .voice import router as voice_router
from .data import router as data_router

__all__ = ['chat_router', 'voice_router', 'data_router']