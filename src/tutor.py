"""
Text and Markdown tutoring module.

Enables the talking head to read and explain text content,
markdown files, and provide tutoring-style narration.
"""

import asyncio
import re
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TutorSegment:
    """A segment of text to be spoken with optional metadata."""

    text: str
    segment_type: str  # "heading", "paragraph", "code", "list_item", "emphasis"
    pause_after: float = 0.5  # Pause duration after segment
    voice_style: str = "normal"  # "normal", "emphasis", "question", "code"


class MarkdownParser:
    """
    Parse markdown into speakable segments.
    """

    def parse(self, content: str) -> list[TutorSegment]:
        """
        Parse markdown content into segments.

        Args:
            content: Markdown text

        Returns:
            List of TutorSegment objects
        """
        segments = []
        lines = content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            # Headings
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                text = line.lstrip("#").strip()
                # Remove markdown links from headings
                text = self._clean_markdown(text)
                segments.append(
                    TutorSegment(
                        text=text,
                        segment_type="heading",
                        pause_after=1.0 if level <= 2 else 0.7,
                        voice_style="emphasis",
                    )
                )

            # Code blocks
            elif line.startswith("```"):
                code_lines = []
                lang = line[3:].strip()
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1

                if code_lines:
                    code_text = "\n".join(code_lines)
                    # Summarize code rather than reading it verbatim
                    summary = self._summarize_code(code_text, lang)
                    segments.append(
                        TutorSegment(
                            text=summary,
                            segment_type="code",
                            pause_after=0.8,
                            voice_style="code",
                        )
                    )

            # Lists
            elif line.startswith(("-", "*", "+")) or re.match(r"^\d+\.", line):
                text = re.sub(r"^[-*+]|\d+\.\s*", "", line).strip()
                text = self._clean_markdown(text)
                segments.append(
                    TutorSegment(
                        text=text,
                        segment_type="list_item",
                        pause_after=0.4,
                    )
                )

            # Blockquotes
            elif line.startswith(">"):
                text = line.lstrip(">").strip()
                text = self._clean_markdown(text)
                segments.append(
                    TutorSegment(
                        text=f"Quote: {text}",
                        segment_type="emphasis",
                        pause_after=0.6,
                        voice_style="emphasis",
                    )
                )

            # Regular paragraphs
            else:
                # Collect multi-line paragraphs
                para_lines = [line]
                i += 1
                while i < len(lines) and lines[i].strip() and not self._is_special_line(lines[i]):
                    para_lines.append(lines[i].strip())
                    i += 1
                i -= 1  # Back up one since we'll increment at end of loop

                text = " ".join(para_lines)
                text = self._clean_markdown(text)

                if text:
                    segments.append(
                        TutorSegment(
                            text=text,
                            segment_type="paragraph",
                            pause_after=0.5,
                        )
                    )

            i += 1

        return segments

    def _is_special_line(self, line: str) -> bool:
        """Check if line starts a special block."""
        line = line.strip()
        return (
            line.startswith("#")
            or line.startswith("```")
            or line.startswith("-")
            or line.startswith("*")
            or line.startswith("+")
            or line.startswith(">")
            or bool(re.match(r"^\d+\.", line))
        )

    def _clean_markdown(self, text: str) -> str:
        """Remove markdown formatting from text."""
        # Remove links but keep text: [text](url) -> text
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

        # Remove bold/italic
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        text = re.sub(r"__([^_]+)__", r"\1", text)
        text = re.sub(r"_([^_]+)_", r"\1", text)

        # Remove inline code
        text = re.sub(r"`([^`]+)`", r"\1", text)

        # Remove images
        text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def _summarize_code(self, code: str, lang: str = "") -> str:
        """Create a spoken summary of code."""
        lines = [line for line in code.split("\n") if line.strip()]

        if not lines:
            return "Empty code block."

        # Count different elements
        num_lines = len(lines)

        if lang:
            intro = f"Here's some {lang} code with {num_lines} lines."
        else:
            intro = f"Here's a code block with {num_lines} lines."

        # Try to identify what the code does
        if "def " in code:
            funcs = re.findall(r"def\s+(\w+)", code)
            if funcs:
                intro += f" It defines functions: {', '.join(funcs[:3])}."
        elif "class " in code:
            classes = re.findall(r"class\s+(\w+)", code)
            if classes:
                intro += f" It defines classes: {', '.join(classes[:3])}."
        elif "import " in code or "from " in code:
            intro += " It includes some imports."

        return intro


class TextTutor:
    """
    Text tutoring system with TTS integration.

    Reads text and markdown files aloud with the animated head.
    """

    def __init__(self):
        """Initialize the tutor."""
        self._parser = MarkdownParser()
        self._segments: list[TutorSegment] = []
        self._current_segment_idx = 0

    def load_file(self, file_path: Path) -> list[TutorSegment]:
        """
        Load a text or markdown file.

        Args:
            file_path: Path to file

        Returns:
            List of parsed segments
        """
        file_path = Path(file_path)
        content = file_path.read_text(encoding="utf-8")

        if file_path.suffix.lower() in (".md", ".markdown"):
            self._segments = self._parser.parse(content)
        else:
            # Plain text: split into paragraphs
            paragraphs = content.split("\n\n")
            self._segments = [
                TutorSegment(text=p.strip(), segment_type="paragraph")
                for p in paragraphs
                if p.strip()
            ]

        self._current_segment_idx = 0
        return self._segments

    def load_text(self, text: str, is_markdown: bool = False) -> list[TutorSegment]:
        """
        Load text content directly.

        Args:
            text: Text content
            is_markdown: Whether to parse as markdown

        Returns:
            List of parsed segments
        """
        if is_markdown:
            self._segments = self._parser.parse(text)
        else:
            paragraphs = text.split("\n\n")
            self._segments = [
                TutorSegment(text=p.strip(), segment_type="paragraph")
                for p in paragraphs
                if p.strip()
            ]

        self._current_segment_idx = 0
        return self._segments

    def get_segments(self) -> list[TutorSegment]:
        """Get all loaded segments."""
        return self._segments

    def get_next_segment(self) -> TutorSegment | None:
        """Get next segment to read."""
        if self._current_segment_idx < len(self._segments):
            segment = self._segments[self._current_segment_idx]
            self._current_segment_idx += 1
            return segment
        return None

    def reset(self):
        """Reset to beginning."""
        self._current_segment_idx = 0

    def has_more(self) -> bool:
        """Check if there are more segments."""
        return self._current_segment_idx < len(self._segments)

    def segment_generator(self) -> Generator[TutorSegment, None, None]:
        """Generate segments one by one."""
        yield from self._segments

    async def speak_all(
        self,
        tts_engine,
        audio_player,
        on_segment_start=None,
        on_segment_end=None,
    ):
        """
        Speak all segments with TTS.

        Args:
            tts_engine: TTS engine instance
            audio_player: Audio player instance
            on_segment_start: Callback(segment) when starting a segment
            on_segment_end: Callback(segment) when ending a segment
        """
        for segment in self._segments:
            if on_segment_start:
                on_segment_start(segment)

            # Synthesize speech
            result = await tts_engine.synthesize(segment.text)

            # Play audio
            audio_player.load_file(result.audio_path)
            audio_player.play()
            audio_player.wait_until_done()

            if on_segment_end:
                on_segment_end(segment)

            # Pause between segments
            if segment.pause_after > 0:
                await asyncio.sleep(segment.pause_after)

    def get_progress(self) -> tuple[int, int]:
        """Get (current_index, total) progress."""
        return (self._current_segment_idx, len(self._segments))

    def get_full_text(self) -> str:
        """Get all text as a single string."""
        return " ".join(s.text for s in self._segments)

    def get_estimated_duration(self, words_per_minute: float = 150.0) -> float:
        """
        Estimate total speaking duration.

        Args:
            words_per_minute: Speaking rate

        Returns:
            Estimated duration in seconds
        """
        total_words = sum(len(s.text.split()) for s in self._segments)
        total_pauses = sum(s.pause_after for s in self._segments)
        speaking_time = (total_words / words_per_minute) * 60
        return speaking_time + total_pauses


def create_introduction_text(topic: str) -> str:
    """Create an introduction for a tutoring session."""
    return f"""
# Welcome to the Tutorial

Hello! I'm your ASCII tutor, and today we'll be learning about **{topic}**.

I'll guide you through the content step by step, explaining each concept as we go.

Feel free to follow along, and remember that you can pause at any time.

Let's get started!
"""
