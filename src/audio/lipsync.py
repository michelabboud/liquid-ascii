"""
Lip sync generation from text and audio.

Generates viseme timing data for mouth animation synchronized
with speech audio.
"""

import json
import subprocess
import tempfile
from pathlib import Path

from ..model.visemes import (
    RHUBARB_TO_VISEME,
    Viseme,
    VisemeController,
    VisemeCue,
    simple_text_to_visemes,
)


def estimate_speech_duration(text: str, words_per_minute: float = 150.0) -> float:
    """
    Estimate speech duration from text.

    Args:
        text: Text to estimate
        words_per_minute: Speaking rate

    Returns:
        Estimated duration in seconds
    """
    word_count = len(text.split())
    return max(0.5, (word_count / words_per_minute) * 60)


class LipSyncGenerator:
    """
    Generates lip sync viseme data from text and/or audio.
    """

    def __init__(self, use_rhubarb: bool = True):
        """
        Initialize the lip sync generator.

        Args:
            use_rhubarb: If True, try to use Rhubarb Lip Sync for
                        accurate phoneme detection
        """
        self.use_rhubarb = use_rhubarb
        self._rhubarb_available: bool | None = None

    def _check_rhubarb(self) -> bool:
        """Check if Rhubarb Lip Sync is available."""
        if self._rhubarb_available is not None:
            return self._rhubarb_available

        try:
            result = subprocess.run(
                ["rhubarb", "--version"],
                capture_output=True,
                timeout=5,
            )
            self._rhubarb_available = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self._rhubarb_available = False

        return self._rhubarb_available

    def generate_from_audio(
        self,
        audio_path: Path,
        dialog_text: str | None = None,
    ) -> list[VisemeCue]:
        """
        Generate viseme cues from an audio file.

        Args:
            audio_path: Path to audio file (WAV preferred)
            dialog_text: Optional text hint for better recognition

        Returns:
            List of viseme timing cues
        """
        audio_path = Path(audio_path)

        if self.use_rhubarb and self._check_rhubarb():
            return self._generate_with_rhubarb(audio_path, dialog_text)
        else:
            # Fall back to simple text-based estimation
            if dialog_text:
                # Estimate duration from audio file
                duration = self._get_audio_duration(audio_path)
                return simple_text_to_visemes(dialog_text, duration)
            else:
                # Very basic fallback: alternating mouth shapes
                duration = self._get_audio_duration(audio_path)
                return self._generate_simple_pattern(duration)

    def _generate_with_rhubarb(
        self,
        audio_path: Path,
        dialog_text: str | None = None,
    ) -> list[VisemeCue]:
        """Generate visemes using Rhubarb Lip Sync."""
        # Convert to WAV if needed (Rhubarb prefers WAV)
        wav_path = audio_path
        cleanup_wav = False

        if audio_path.suffix.lower() != ".wav":
            wav_path = Path(tempfile.mktemp(suffix=".wav"))
            cleanup_wav = True
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(audio_path), "-ar", "16000", str(wav_path)],
                capture_output=True,
            )

        try:
            # Build Rhubarb command
            cmd = ["rhubarb", str(wav_path), "-f", "json"]

            # Add dialog file if provided
            dialog_file = None
            if dialog_text:
                dialog_file = Path(tempfile.mktemp(suffix=".txt"))
                dialog_file.write_text(dialog_text)
                cmd.extend(["-d", str(dialog_file)])

            # Run Rhubarb
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=60,
            )

            if dialog_file and dialog_file.exists():
                dialog_file.unlink()

            if result.returncode != 0:
                raise RuntimeError(f"Rhubarb failed: {result.stderr.decode()}")

            # Parse JSON output
            data = json.loads(result.stdout.decode())
            return self._parse_rhubarb_output(data)

        finally:
            if cleanup_wav and wav_path.exists():
                wav_path.unlink()

    def _parse_rhubarb_output(self, data: dict) -> list[VisemeCue]:
        """Parse Rhubarb JSON output to viseme cues."""
        cues = []

        for cue in data.get("mouthCues", []):
            viseme_str = cue.get("value", "X")
            viseme = RHUBARB_TO_VISEME.get(viseme_str, Viseme.X)

            cues.append(VisemeCue(
                start_time=float(cue["start"]),
                end_time=float(cue["end"]),
                viseme=viseme,
            ))

        return cues

    def _get_audio_duration(self, audio_path: Path) -> float:
        """Get duration of an audio file."""
        try:
            import soundfile as sf
            info = sf.info(str(audio_path))
            return info.duration
        except Exception:
            pass

        # Fallback: use ffprobe
        try:
            result = subprocess.run(
                [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(audio_path)
                ],
                capture_output=True,
                timeout=10,
            )
            return float(result.stdout.decode().strip())
        except Exception:
            return 5.0  # Default fallback

    def _generate_simple_pattern(self, duration: float) -> list[VisemeCue]:
        """Generate a simple alternating mouth pattern."""
        cues = []
        time = 0.0
        syllable_duration = 0.15

        viseme_cycle = [Viseme.A, Viseme.X, Viseme.E, Viseme.X, Viseme.O, Viseme.X]
        idx = 0

        while time < duration:
            cues.append(VisemeCue(
                start_time=time,
                end_time=min(time + syllable_duration, duration),
                viseme=viseme_cycle[idx % len(viseme_cycle)],
            ))
            time += syllable_duration
            idx += 1

        return cues

    def generate_from_text(
        self,
        text: str,
        duration: float | None = None,
        words_per_minute: float = 150.0,
    ) -> list[VisemeCue]:
        """
        Generate viseme cues from text without audio.

        Args:
            text: Text to generate cues for
            duration: Fixed duration (auto-estimated if None)
            words_per_minute: Speaking rate for duration estimation

        Returns:
            List of viseme cues
        """
        if duration is None:
            duration = estimate_speech_duration(text, words_per_minute)

        return simple_text_to_visemes(text, duration, words_per_minute)

    def generate_from_word_timings(
        self,
        word_timings: list[dict],
    ) -> list[VisemeCue]:
        """
        Generate viseme cues from word timing data.

        Useful with TTS engines that provide word timestamps.

        Args:
            word_timings: List of {"text", "offset", "duration"} dicts

        Returns:
            List of viseme cues
        """
        cues = []

        for word_data in word_timings:
            word = word_data["text"]
            start = word_data["offset"]
            duration = word_data["duration"]

            # Simple per-word viseme generation
            word_cues = self._word_to_visemes(word, start, duration)
            cues.extend(word_cues)

        return cues

    def _word_to_visemes(
        self,
        word: str,
        start_time: float,
        duration: float,
    ) -> list[VisemeCue]:
        """Convert a single word to viseme cues."""
        cues = []

        # Count vowels for syllable estimation
        vowels = set("aeiouAEIOU")
        syllables = sum(1 for c in word if c in vowels)
        syllables = max(1, syllables)

        time_per_syllable = duration / syllables
        current_time = start_time

        # Map first character to viseme for variety
        char_to_viseme = {
            "a": Viseme.A, "e": Viseme.E, "i": Viseme.E,
            "o": Viseme.O, "u": Viseme.O,
            "m": Viseme.B, "b": Viseme.B, "p": Viseme.B,
            "f": Viseme.F, "v": Viseme.F,
            "t": Viseme.C, "d": Viseme.C, "n": Viseme.C,
            "s": Viseme.C, "z": Viseme.C,
            "l": Viseme.H, "r": Viseme.H,
            "w": Viseme.O,
        }

        for i in range(syllables):
            # Pick viseme based on word characters
            char_idx = min(i, len(word) - 1)
            char = word[char_idx].lower()
            viseme = char_to_viseme.get(char, Viseme.A)

            cues.append(VisemeCue(
                start_time=current_time,
                end_time=current_time + time_per_syllable * 0.8,
                viseme=viseme,
            ))

            # Brief closure between syllables
            cues.append(VisemeCue(
                start_time=current_time + time_per_syllable * 0.8,
                end_time=current_time + time_per_syllable,
                viseme=Viseme.X,
            ))

            current_time += time_per_syllable

        return cues


def create_lip_sync_controller(
    text: str,
    audio_path: Path | None = None,
    word_timings: list[dict] | None = None,
    duration: float | None = None,
) -> VisemeController:
    """
    Convenience function to create a configured VisemeController.

    Args:
        text: Text being spoken
        audio_path: Optional path to audio file
        word_timings: Optional word timing data from TTS
        duration: Optional fixed duration

    Returns:
        Configured VisemeController ready for animation
    """
    generator = LipSyncGenerator()
    controller = VisemeController()

    if word_timings:
        cues = generator.generate_from_word_timings(word_timings)
    elif audio_path:
        cues = generator.generate_from_audio(audio_path, text)
    else:
        cues = generator.generate_from_text(text, duration)

    controller.load_cues(cues)
    return controller
