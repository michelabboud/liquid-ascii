"""Audio package - TTS, lip sync, and playback"""

from .tts import TTSEngine, EdgeTTSEngine
from .player import AudioPlayer
from .lipsync import LipSyncGenerator, estimate_speech_duration

__all__ = [
    "TTSEngine",
    "EdgeTTSEngine",
    "AudioPlayer",
    "LipSyncGenerator",
    "estimate_speech_duration",
]
