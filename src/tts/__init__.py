"""Text-to-Speech module."""

from .google_tts import GoogleTTS
from .voice_manager import VoiceManager

__all__ = ["GoogleTTS", "VoiceManager"]
