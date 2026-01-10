"""
Text-to-Speech engine wrapper.

Provides unified interface for TTS with support for multiple backends.
Primary support for edge-tts (Microsoft Edge online TTS).
"""

import asyncio
import tempfile
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncGenerator, List, Optional, Tuple


@dataclass
class TTSResult:
    """Result from TTS synthesis."""
    audio_path: Path
    duration: float  # Estimated duration in seconds
    text: str
    voice: str


@dataclass
class Voice:
    """Voice configuration."""
    name: str
    short_name: str
    gender: str
    locale: str


class TTSEngine(ABC):
    """Abstract base class for TTS engines."""

    @abstractmethod
    async def synthesize(self, text: str, output_path: Optional[Path] = None) -> TTSResult:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            output_path: Output file path (auto-generated if None)

        Returns:
            TTSResult with audio file path and metadata
        """
        pass

    @abstractmethod
    async def list_voices(self) -> List[Voice]:
        """List available voices."""
        pass

    @abstractmethod
    def set_voice(self, voice_name: str):
        """Set the voice to use."""
        pass


class EdgeTTSEngine(TTSEngine):
    """
    Text-to-speech using Microsoft Edge TTS.

    Uses the edge-tts library for high-quality free TTS.
    Requires internet connection.
    """

    # Popular voices for different use cases
    RECOMMENDED_VOICES = {
        "en-US-male": "en-US-GuyNeural",
        "en-US-female": "en-US-AriaNeural",
        "en-US-news": "en-US-JennyNeural",
        "en-GB-male": "en-GB-RyanNeural",
        "en-GB-female": "en-GB-SoniaNeural",
        "en-AU-female": "en-AU-NatashaNeural",
        "es-ES-female": "es-ES-ElviraNeural",
        "fr-FR-female": "fr-FR-DeniseNeural",
        "de-DE-female": "de-DE-KatjaNeural",
        "ja-JP-female": "ja-JP-NanamiNeural",
        "zh-CN-female": "zh-CN-XiaoxiaoNeural",
    }

    def __init__(
        self,
        voice: str = "en-US-AriaNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
    ):
        """
        Initialize Edge TTS engine.

        Args:
            voice: Voice name (e.g., "en-US-AriaNeural")
            rate: Speech rate adjustment (e.g., "+10%", "-20%")
            pitch: Pitch adjustment (e.g., "+5Hz", "-10Hz")
            volume: Volume adjustment (e.g., "+10%")
        """
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self.volume = volume
        self._temp_dir = tempfile.mkdtemp(prefix="liquid_ascii_tts_")

    async def synthesize(self, text: str, output_path: Optional[Path] = None) -> TTSResult:
        """Synthesize speech from text using Edge TTS."""
        import edge_tts

        if output_path is None:
            output_path = Path(self._temp_dir) / f"speech_{hash(text) & 0xFFFFFFFF}.mp3"

        communicate = edge_tts.Communicate(
            text,
            self.voice,
            rate=self.rate,
            pitch=self.pitch,
            volume=self.volume,
        )

        await communicate.save(str(output_path))

        # Estimate duration (rough: ~150 words per minute)
        word_count = len(text.split())
        duration = max(1.0, word_count / 2.5)  # ~150 WPM

        return TTSResult(
            audio_path=output_path,
            duration=duration,
            text=text,
            voice=self.voice,
        )

    async def synthesize_with_timestamps(
        self,
        text: str,
        output_path: Optional[Path] = None
    ) -> Tuple[TTSResult, List[dict]]:
        """
        Synthesize speech and get word timestamps.

        Returns:
            Tuple of (TTSResult, list of word timing dicts)
        """
        import edge_tts

        if output_path is None:
            output_path = Path(self._temp_dir) / f"speech_{hash(text) & 0xFFFFFFFF}.mp3"

        communicate = edge_tts.Communicate(
            text,
            self.voice,
            rate=self.rate,
            pitch=self.pitch,
            volume=self.volume,
        )

        word_timings = []

        with open(output_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    word_timings.append({
                        "text": chunk["text"],
                        "offset": chunk["offset"] / 10_000_000,  # Convert to seconds
                        "duration": chunk["duration"] / 10_000_000,
                    })

        # Calculate total duration from word timings
        if word_timings:
            last_word = word_timings[-1]
            duration = last_word["offset"] + last_word["duration"]
        else:
            duration = max(1.0, len(text.split()) / 2.5)

        result = TTSResult(
            audio_path=output_path,
            duration=duration,
            text=text,
            voice=self.voice,
        )

        return result, word_timings

    async def stream_audio(self, text: str) -> AsyncGenerator[bytes, None]:
        """
        Stream audio chunks as they're generated.

        Yields:
            Audio data chunks
        """
        import edge_tts

        communicate = edge_tts.Communicate(
            text,
            self.voice,
            rate=self.rate,
            pitch=self.pitch,
            volume=self.volume,
        )

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]

    async def list_voices(self) -> List[Voice]:
        """List all available Edge TTS voices."""
        import edge_tts

        voices_list = await edge_tts.list_voices()
        voices = []

        for v in voices_list:
            voices.append(Voice(
                name=v["FriendlyName"],
                short_name=v["ShortName"],
                gender=v["Gender"],
                locale=v["Locale"],
            ))

        return voices

    def set_voice(self, voice_name: str):
        """Set the voice to use."""
        self.voice = voice_name

    def set_rate(self, rate: str):
        """Set speech rate (e.g., '+10%', '-20%')."""
        self.rate = rate

    def set_pitch(self, pitch: str):
        """Set pitch (e.g., '+5Hz', '-10Hz')."""
        self.pitch = pitch

    def cleanup(self):
        """Clean up temporary files."""
        import shutil
        if os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir)

    def __del__(self):
        """Destructor to clean up temp files."""
        try:
            self.cleanup()
        except Exception:
            pass


def run_async(coro):
    """Helper to run async code synchronously."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)


class SyncEdgeTTSEngine:
    """
    Synchronous wrapper for EdgeTTSEngine.

    Convenience class for non-async code.
    """

    def __init__(self, **kwargs):
        """Initialize with same args as EdgeTTSEngine."""
        self._engine = EdgeTTSEngine(**kwargs)

    def synthesize(self, text: str, output_path: Optional[Path] = None) -> TTSResult:
        """Synthesize speech synchronously."""
        return run_async(self._engine.synthesize(text, output_path))

    def synthesize_with_timestamps(
        self,
        text: str,
        output_path: Optional[Path] = None
    ) -> Tuple[TTSResult, List[dict]]:
        """Synthesize speech with timestamps synchronously."""
        return run_async(self._engine.synthesize_with_timestamps(text, output_path))

    def list_voices(self) -> List[Voice]:
        """List voices synchronously."""
        return run_async(self._engine.list_voices())

    def set_voice(self, voice_name: str):
        """Set voice."""
        self._engine.set_voice(voice_name)

    def cleanup(self):
        """Clean up temp files."""
        self._engine.cleanup()
