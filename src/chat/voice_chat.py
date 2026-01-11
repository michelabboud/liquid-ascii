"""
Voice-enabled chat integration.

Combines LLM chat with TTS and lip sync for fully conversational AI.
"""

import os
import re
import tempfile
from collections.abc import AsyncIterator
from dataclasses import dataclass
from queue import Queue


@dataclass
class SpeechChunk:
    """A chunk of text ready to be synthesized."""

    text: str
    audio_file: str | None = None
    word_timings: list | None = None


class SentenceChunker:
    """
    Buffers streaming tokens and yields complete sentences.

    Handles sentence boundary detection for real-time TTS.
    """

    def __init__(self):
        """Initialize sentence chunker."""
        self.buffer = []
        # Sentence boundaries (. ! ? followed by space or end)
        self.sentence_pattern = re.compile(r"([.!?]+)(\s+|$)")
        # Abbreviations that shouldn't end sentences
        self.abbreviations = {
            "mr.",
            "mrs.",
            "ms.",
            "dr.",
            "prof.",
            "sr.",
            "jr.",
            "etc.",
            "e.g.",
            "i.e.",
            "vs.",
            "ph.d.",
        }

    def add_token(self, token: str) -> str | None:
        """
        Add a token to the buffer.

        Args:
            token: Text token from LLM

        Returns:
            Complete sentence if boundary detected, None otherwise
        """
        self.buffer.append(token)
        current_text = "".join(self.buffer)

        # Check for sentence boundary
        match = self.sentence_pattern.search(current_text)
        if match:
            # Check if it's an abbreviation
            end_pos = match.end()
            prefix = current_text[:end_pos].strip().lower()

            # If it ends with a known abbreviation, don't split
            is_abbreviation = any(prefix.endswith(abbr) for abbr in self.abbreviations)

            if not is_abbreviation:
                # Found a real sentence boundary
                sentence = current_text[:end_pos].strip()
                # Keep remainder in buffer
                remainder = current_text[end_pos:]
                self.buffer = [remainder] if remainder else []
                return sentence

        return None

    def flush(self) -> str | None:
        """
        Get remaining buffer content.

        Returns:
            Remaining text in buffer
        """
        if self.buffer:
            text = "".join(self.buffer).strip()
            self.buffer = []
            return text if text else None
        return None


class VoiceChatController:
    """
    Controller for voice-enabled chat sessions.

    Manages streaming LLM responses, TTS synthesis, and audio playback.
    """

    def __init__(self, tts_engine, voice: str | None = None):
        """
        Initialize voice chat controller.

        Args:
            tts_engine: EdgeTTSEngine instance
            voice: TTS voice name (optional)
        """
        self.tts_engine = tts_engine
        self.voice = voice
        self.speech_queue: Queue[SpeechChunk] = Queue()
        self.temp_files = []  # Track temp files for cleanup

    async def process_streaming_response(
        self, response_stream: AsyncIterator[str]
    ) -> AsyncIterator[tuple[str, SpeechChunk | None]]:
        """
        Process streaming LLM response with sentence-level TTS.

        Args:
            response_stream: Async iterator of response tokens

        Yields:
            Tuples of (token, speech_chunk)
            - token: text token for display
            - speech_chunk: SpeechChunk when sentence is complete, None otherwise
        """
        chunker = SentenceChunker()

        async for token in response_stream:
            # Yield token for immediate display
            yield token, None

            # Check if we have a complete sentence
            sentence = chunker.add_token(token)
            if sentence:
                # Synthesize sentence
                speech_chunk = await self._synthesize_sentence(sentence)
                yield "", speech_chunk

        # Flush any remaining text
        remaining = chunker.flush()
        if remaining:
            speech_chunk = await self._synthesize_sentence(remaining)
            yield "", speech_chunk

    async def _synthesize_sentence(self, text: str) -> SpeechChunk:
        """
        Synthesize a sentence to audio.

        Args:
            text: Sentence text to synthesize

        Returns:
            SpeechChunk with audio file and timing data
        """
        # Create temporary file for audio
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        temp_file.close()
        self.temp_files.append(temp_file.name)

        # Synthesize with TTS
        result = await self.tts_engine.synthesize(text, temp_file.name)

        chunk = SpeechChunk(text=text, audio_file=temp_file.name, word_timings=result.word_timings)

        return chunk

    def cleanup(self):
        """Clean up temporary audio files."""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception:
                pass
        self.temp_files.clear()


async def stream_with_voice(
    chat_session,
    user_message: str,
    voice_controller: VoiceChatController,
) -> AsyncIterator[tuple[str, str, SpeechChunk | None]]:
    """
    Stream chat response with voice synthesis.

    Args:
        chat_session: ChatSession instance
        user_message: User's input message
        voice_controller: VoiceChatController instance

    Yields:
        Tuples of (token, expression, speech_chunk)
    """
    # Get streaming response from chat
    response_stream = chat_session.send_message_stream(user_message)

    # Create a new async generator that extracts tokens
    async def token_stream():
        async for token, _expression in response_stream:
            yield token

    # Process with voice
    async for token, speech_chunk in voice_controller.process_streaming_response(token_stream()):
        # Get current expression from chat session
        expression = chat_session.get_current_expression()
        yield token, expression, speech_chunk


def chunk_text_for_tts(text: str, max_length: int = 200) -> list[str]:
    """
    Split text into chunks suitable for TTS.

    Splits on sentence boundaries, keeping chunks under max_length.

    Args:
        text: Text to split
        max_length: Maximum chunk length

    Returns:
        List of text chunks
    """
    # Split on sentence boundaries
    sentences = re.split(r"([.!?]+\s+)", text)

    chunks = []
    current_chunk = ""

    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""

        sentence_with_punct = sentence + punctuation

        # If adding this sentence exceeds max_length, start new chunk
        if current_chunk and len(current_chunk) + len(sentence_with_punct) > max_length:
            chunks.append(current_chunk.strip())
            current_chunk = sentence_with_punct
        else:
            current_chunk += sentence_with_punct

    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
