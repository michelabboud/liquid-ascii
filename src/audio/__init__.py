"""Audio package - TTS, lip sync, and playback"""

from .lipsync import LipSyncGenerator, estimate_speech_duration
from .player import AudioPlayer
from .tts import EdgeTTSEngine, TTSEngine

__all__ = [
    "TTSEngine",
    "EdgeTTSEngine",
    "AudioPlayer",
    "LipSyncGenerator",
    "estimate_speech_duration",
]
