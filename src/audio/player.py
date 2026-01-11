"""
Audio playback with precise timing for lip sync.

Uses sounddevice for cross-platform audio playback with
accurate position tracking.
"""

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class PlaybackState:
    """Current state of audio playback."""
    is_playing: bool = False
    is_paused: bool = False
    position: float = 0.0  # Current position in seconds
    duration: float = 0.0  # Total duration in seconds


class AudioPlayer:
    """
    Audio player with timing support for lip sync.

    Uses sounddevice for low-latency playback and accurate
    position tracking.
    """

    def __init__(self):
        """Initialize the audio player."""
        self._audio_data: np.ndarray | None = None
        self._sample_rate: int = 44100
        self._state = PlaybackState()
        self._position_lock = threading.Lock()
        self._stream = None
        self._frame_index = 0
        self._on_complete: Callable | None = None

    def load_file(self, file_path: Path) -> float:
        """
        Load an audio file for playback.

        Args:
            file_path: Path to audio file (MP3, WAV, etc.)

        Returns:
            Duration of the audio in seconds
        """
        file_path = Path(file_path)

        if file_path.suffix.lower() == ".mp3":
            self._audio_data, self._sample_rate = self._load_mp3(file_path)
        elif file_path.suffix.lower() == ".wav":
            self._audio_data, self._sample_rate = self._load_wav(file_path)
        else:
            # Try scipy for other formats
            self._audio_data, self._sample_rate = self._load_scipy(file_path)

        # Convert to float32 if needed
        if self._audio_data.dtype != np.float32:
            if np.issubdtype(self._audio_data.dtype, np.integer):
                max_val = np.iinfo(self._audio_data.dtype).max
                self._audio_data = self._audio_data.astype(np.float32) / max_val
            else:
                self._audio_data = self._audio_data.astype(np.float32)

        # Ensure 2D array (samples, channels)
        if len(self._audio_data.shape) == 1:
            self._audio_data = self._audio_data.reshape(-1, 1)

        self._state.duration = len(self._audio_data) / self._sample_rate
        self._frame_index = 0

        return self._state.duration

    def _load_mp3(self, file_path: Path) -> tuple:
        """Load MP3 file using scipy/soundfile."""
        try:
            # Try soundfile first (handles many formats)
            import soundfile as sf
            data, sr = sf.read(str(file_path))
            return data, sr
        except Exception:
            pass

        # Fallback: use scipy with ffmpeg if available
        try:
            import subprocess
            import tempfile

            from scipy.io import wavfile

            # Convert to WAV using ffmpeg
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name

            subprocess.run(
                ["ffmpeg", "-y", "-i", str(file_path), "-ar", "44100", tmp_path],
                capture_output=True,
                check=True,
            )

            sr, data = wavfile.read(tmp_path)
            Path(tmp_path).unlink()
            return data.astype(np.float32) / 32768.0, sr

        except Exception as e:
            raise RuntimeError(f"Could not load MP3 file: {e}. Install soundfile or ffmpeg.") from e

    def _load_wav(self, file_path: Path) -> tuple:
        """Load WAV file."""
        from scipy.io import wavfile
        sr, data = wavfile.read(str(file_path))
        return data, sr

    def _load_scipy(self, file_path: Path) -> tuple:
        """Load audio using soundfile."""
        import soundfile as sf
        data, sr = sf.read(str(file_path))
        return data, sr

    def _audio_callback(self, outdata, frames, time_info, status):
        """Callback for sounddevice stream."""
        if self._audio_data is None:
            outdata.fill(0)
            return

        with self._position_lock:
            if self._state.is_paused:
                outdata.fill(0)
                return

            start = self._frame_index
            end = start + frames

            if start >= len(self._audio_data):
                # End of audio
                outdata.fill(0)
                self._state.is_playing = False
                if self._on_complete:
                    # Schedule callback on separate thread to avoid blocking
                    threading.Thread(target=self._on_complete).start()
                return

            # Get audio chunk
            chunk = self._audio_data[start:end]

            # Pad if needed (end of file)
            if len(chunk) < frames:
                padding = np.zeros((frames - len(chunk), outdata.shape[1]), dtype=np.float32)
                chunk = np.vstack([chunk, padding])
                self._state.is_playing = False
                if self._on_complete:
                    threading.Thread(target=self._on_complete).start()

            # Handle channel mismatch
            if chunk.shape[1] != outdata.shape[1]:
                if chunk.shape[1] == 1 and outdata.shape[1] == 2:
                    chunk = np.column_stack([chunk, chunk])
                elif chunk.shape[1] == 2 and outdata.shape[1] == 1:
                    chunk = chunk.mean(axis=1, keepdims=True)

            outdata[:] = chunk
            self._frame_index = end
            self._state.position = self._frame_index / self._sample_rate

    def play(self, on_complete: Callable | None = None):
        """
        Start audio playback.

        Args:
            on_complete: Callback when playback finishes
        """
        if self._audio_data is None:
            raise RuntimeError("No audio loaded. Call load_file() first.")

        import sounddevice as sd

        self._on_complete = on_complete
        self._state.is_playing = True
        self._state.is_paused = False

        channels = self._audio_data.shape[1] if len(self._audio_data.shape) > 1 else 1

        self._stream = sd.OutputStream(
            samplerate=self._sample_rate,
            channels=channels,
            callback=self._audio_callback,
            dtype=np.float32,
        )
        self._stream.start()

    def pause(self):
        """Pause playback."""
        self._state.is_paused = True

    def resume(self):
        """Resume paused playback."""
        self._state.is_paused = False

    def stop(self):
        """Stop playback and reset position."""
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self._position_lock:
            self._state.is_playing = False
            self._state.is_paused = False
            self._frame_index = 0
            self._state.position = 0.0

    def seek(self, position: float):
        """
        Seek to a position in the audio.

        Args:
            position: Position in seconds
        """
        with self._position_lock:
            self._frame_index = int(position * self._sample_rate)
            self._frame_index = max(0, min(self._frame_index, len(self._audio_data) - 1))
            self._state.position = self._frame_index / self._sample_rate

    def get_position(self) -> float:
        """Get current playback position in seconds."""
        with self._position_lock:
            return self._state.position

    def get_duration(self) -> float:
        """Get total audio duration in seconds."""
        return self._state.duration

    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return self._state.is_playing and not self._state.is_paused

    def get_state(self) -> PlaybackState:
        """Get full playback state."""
        with self._position_lock:
            return PlaybackState(
                is_playing=self._state.is_playing,
                is_paused=self._state.is_paused,
                position=self._state.position,
                duration=self._state.duration,
            )

    def wait_until_done(self):
        """Block until playback is complete."""
        while self._state.is_playing:
            time.sleep(0.05)

    def __del__(self):
        """Cleanup on deletion."""
        self.stop()


class SyncAudioPlayer:
    """
    Simple synchronous audio player for basic use cases.

    Uses sounddevice.play() for simpler playback without
    precise timing callbacks.
    """

    def __init__(self):
        """Initialize player."""
        self._start_time: float | None = None
        self._duration: float = 0.0
        self._is_playing: bool = False

    def play_file(self, file_path: Path, blocking: bool = False):
        """
        Play an audio file.

        Args:
            file_path: Path to audio file
            blocking: If True, wait until playback completes
        """
        import sounddevice as sd

        # Load audio
        try:
            import soundfile as sf
            data, sr = sf.read(str(file_path))
        except ImportError:
            from scipy.io import wavfile
            sr, data = wavfile.read(str(file_path))
            data = data.astype(np.float32) / 32768.0

        self._duration = len(data) / sr
        self._start_time = time.time()
        self._is_playing = True

        sd.play(data, sr)

        if blocking:
            sd.wait()
            self._is_playing = False

    def get_position(self) -> float:
        """Get estimated playback position."""
        if self._start_time is None:
            return 0.0
        elapsed = time.time() - self._start_time
        return min(elapsed, self._duration)

    def stop(self):
        """Stop playback."""
        import sounddevice as sd
        sd.stop()
        self._is_playing = False

    def is_playing(self) -> bool:
        """Check if playing."""
        if not self._is_playing:
            return False
        return self.get_position() < self._duration
