"""
Offline TTS Engine using pyttsx3 (system voices)

Lightweight alternative to edge-tts that works offline.
Uses system TTS: SAPI5 (Windows), NSSpeech (macOS), espeak (Linux)
"""

import asyncio
import tempfile
from pathlib import Path

try:
    import pyttsx3

    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False


class OfflineTTSEngine:
    """
    Offline text-to-speech using system voices (pyttsx3).

    Pros:
    - No internet required
    - Very lightweight (~50KB)
    - Fast synthesis

    Cons:
    - Lower quality (robotic sound)
    - Limited voices
    - No word timing data for perfect lip sync
    """

    def __init__(self):
        if not PYTTSX3_AVAILABLE:
            raise ImportError("pyttsx3 not installed. Install with: uv pip install pyttsx3")

        self.engine = pyttsx3.init()

    def list_voices(self) -> list[dict[str, str]]:
        """List available system voices."""
        voices = self.engine.getProperty("voices")
        return [
            {
                "name": voice.name,
                "id": voice.id,
                "languages": voice.languages if hasattr(voice, "languages") else [],
            }
            for voice in voices
        ]

    def set_voice(self, voice_id: str | None = None):
        """Set voice by ID or use default."""
        if voice_id:
            self.engine.setProperty("voice", voice_id)

    def set_rate(self, rate: int = 150):
        """Set speech rate (words per minute). Default: 150."""
        self.engine.setProperty("rate", rate)

    def set_volume(self, volume: float = 1.0):
        """Set volume (0.0 to 1.0). Default: 1.0."""
        self.engine.setProperty("volume", volume)

    async def synthesize(
        self, text: str, voice: str | None = None, rate: int = 150, output_dir: Path | None = None
    ) -> dict:
        """
        Synthesize text to speech and save as audio file.

        Args:
            text: Text to synthesize
            voice: Voice ID (optional)
            rate: Speech rate in words per minute
            output_dir: Directory to save audio (default: temp)

        Returns:
            Dict with 'audio_path' and 'duration' (word_timings not available)
        """
        if output_dir is None:
            output_dir = Path(tempfile.gettempdir())

        audio_file = output_dir / f"tts_offline_{hash(text)}.wav"

        # Set voice and rate
        if voice:
            self.set_voice(voice)
        self.set_rate(rate)

        # Synthesize to file (blocking - run in executor)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: self._synthesize_sync(text, str(audio_file)))

        # Estimate duration (rough estimate based on text length and rate)
        word_count = len(text.split())
        duration = (word_count / rate) * 60  # Convert WPM to seconds

        return {
            "audio_path": str(audio_file),
            "duration": duration,
            "word_timings": [],  # Not available with pyttsx3
        }

    def _synthesize_sync(self, text: str, output_file: str):
        """Synchronous synthesis (called from executor)."""
        self.engine.save_to_file(text, output_file)
        self.engine.runAndWait()


# Example usage
if __name__ == "__main__":

    async def demo():
        if not PYTTSX3_AVAILABLE:
            print("Install pyttsx3: uv pip install pyttsx3")
            return

        engine = OfflineTTSEngine()

        # List voices
        print("Available voices:")
        for voice in engine.list_voices():
            print(f"  - {voice['name']} ({voice['id']})")

        # Synthesize
        print("\nSynthesizing...")
        result = await engine.synthesize("Hello! I am speaking using offline text to speech.")
        print(f"Audio saved to: {result['audio_path']}")
        print(f"Duration: {result['duration']:.2f}s")

    asyncio.run(demo())
