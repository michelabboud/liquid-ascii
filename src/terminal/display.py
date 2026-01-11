"""
Terminal display module for ASCII rendering.

Uses blessed library for cross-platform terminal handling with
support for colors, screen buffering, and keyboard input.
"""

import sys
import time
from collections.abc import Callable

from .colors import (
    PRESET_SCHEMES,
    RGB,
    ColorMode,
    ColorScheme,
    RainbowColors,
    reset_color,
    rgb_to_ansi_escape,
)


class Display:
    """
    Terminal display manager for ASCII animation.

    Handles screen output, colors, and refresh rate.
    """

    def __init__(
        self,
        width: int | None = None,
        height: int | None = None,
        target_fps: float = 30.0,
        color_mode: ColorMode = ColorMode.TRUECOLOR,
        color_scheme: ColorScheme | None = None,
        rainbow: RainbowColors | None = None,
    ):
        """
        Initialize the display.

        Args:
            width: Display width (auto-detect if None)
            height: Display height (auto-detect if None)
            target_fps: Target frame rate
            color_mode: Terminal color mode
            color_scheme: Static color scheme (mutually exclusive with rainbow)
            rainbow: Rainbow color generator
        """
        self._term = None
        self._width = width
        self._height = height
        self.target_fps = target_fps
        self.color_mode = color_mode
        self.color_scheme = color_scheme or PRESET_SCHEMES["default"]
        self.rainbow = rainbow

        self._frame_time = 1.0 / target_fps
        self._last_frame_time = 0.0
        self._frame_count = 0
        self._fps_history: list[float] = []

    def _init_terminal(self):
        """Initialize blessed terminal."""
        if self._term is None:
            from blessed import Terminal
            self._term = Terminal()

    @property
    def term(self):
        """Get the blessed Terminal instance."""
        if self._term is None:
            self._init_terminal()
        return self._term

    @property
    def width(self) -> int:
        """Get display width."""
        if self._width:
            return self._width
        self._init_terminal()
        return self._term.width

    @property
    def height(self) -> int:
        """Get display height (minus status line)."""
        if self._height:
            return self._height
        self._init_terminal()
        return self._term.height - 2  # Leave room for status

    def get_size(self) -> tuple:
        """Get (width, height) tuple."""
        return (self.width, self.height)

    def clear(self):
        """Clear the terminal screen."""
        self._init_terminal()
        print(self._term.home + self._term.clear)

    def hide_cursor(self):
        """Hide the terminal cursor."""
        self._init_terminal()
        print(self._term.hide_cursor, end="")

    def show_cursor(self):
        """Show the terminal cursor."""
        self._init_terminal()
        print(self._term.normal_cursor, end="")

    def move_to(self, x: int, y: int):
        """Move cursor to position."""
        self._init_terminal()
        print(self._term.move_xy(x, y), end="")

    def render_frame(
        self,
        frame: str,
        intensities: list[list[float]] | None = None,
        status_text: str | None = None,
    ):
        """
        Render a frame to the terminal.

        Args:
            frame: Multi-line ASCII string
            intensities: Optional 2D array of lighting values for coloring
            status_text: Optional status line text
        """
        self._init_terminal()

        lines = frame.split("\n")

        # Build output with colors
        output = self._term.home

        for row, line in enumerate(lines):
            colored_line = ""

            for col, char in enumerate(line):
                if self.color_mode != ColorMode.NONE and char.strip():
                    # Get color
                    color = self._get_color(col, row, len(line), len(lines), intensities)
                    colored_line += rgb_to_ansi_escape(color.r, color.g, color.b, self.color_mode)
                    colored_line += char
                    colored_line += reset_color()
                else:
                    colored_line += char

            output += colored_line + self._term.clear_eol + "\n"

        # Status line
        if status_text:
            output += self._term.move_xy(0, self._term.height - 1)
            output += status_text[:self._term.width]
            output += self._term.clear_eol

        print(output, end="", flush=True)

    def _get_color(
        self,
        col: int,
        row: int,
        width: int,
        height: int,
        intensities: list[list[float]] | None = None,
    ) -> RGB:
        """Get color for a character position."""
        intensity = 1.0
        if intensities and row < len(intensities) and col < len(intensities[row]):
            intensity = intensities[row][col]

        if self.rainbow:
            return self.rainbow.get_color_for_char(col, row, width, height, intensity)
        else:
            return self.color_scheme.get_surface_color(intensity)

    def wait_for_frame(self) -> float:
        """
        Wait to maintain target FPS.

        Returns:
            Actual delta time since last frame
        """
        current_time = time.time()

        if self._last_frame_time > 0:
            elapsed = current_time - self._last_frame_time
            sleep_time = self._frame_time - elapsed

            if sleep_time > 0:
                time.sleep(sleep_time)
                current_time = time.time()

        dt = current_time - self._last_frame_time if self._last_frame_time > 0 else self._frame_time
        self._last_frame_time = current_time
        self._frame_count += 1

        # Track FPS
        if dt > 0:
            self._fps_history.append(1.0 / dt)
            if len(self._fps_history) > 30:
                self._fps_history.pop(0)

        return dt

    def get_fps(self) -> float:
        """Get average FPS over recent frames."""
        if not self._fps_history:
            return 0.0
        return sum(self._fps_history) / len(self._fps_history)

    def run_loop(
        self,
        update_fn: Callable[[float], str],
        on_key: Callable[[str], bool] | None = None,
        show_fps: bool = True,
    ):
        """
        Run the main animation loop.

        Args:
            update_fn: Function called each frame, receives dt, returns frame string
            on_key: Optional key handler, returns False to quit
            show_fps: Show FPS in status line
        """
        self._init_terminal()

        self.clear()
        self.hide_cursor()

        try:
            with self._term.cbreak():
                running = True

                while running:
                    # Check for input
                    key = self._term.inkey(timeout=0)
                    if key:
                        if key.name == "KEY_ESCAPE" or key == "q":
                            running = False
                        elif on_key:
                            running = on_key(str(key))

                    # Update and render
                    dt = self.wait_for_frame()
                    frame = update_fn(dt)

                    status = None
                    if show_fps:
                        status = f"FPS: {self.get_fps():.1f} | Press 'q' to quit"

                    self.render_frame(frame, status_text=status)

        finally:
            self.show_cursor()
            print()

    def set_color_scheme(self, scheme_name: str):
        """Set color scheme by name."""
        if scheme_name in PRESET_SCHEMES:
            self.color_scheme = PRESET_SCHEMES[scheme_name]
            self.rainbow = None

    def set_rainbow(self, mode: str = "horizontal", speed: float = 1.0):
        """Enable rainbow coloring."""
        self.rainbow = RainbowColors(speed=speed, mode=mode)

    def disable_colors(self):
        """Disable colors."""
        self.color_mode = ColorMode.NONE


class SimpleDisplay:
    """
    Simple display without blessed dependency.

    Uses basic ANSI escape codes for terminal control.
    Works in most terminals but with fewer features.
    """

    def __init__(self, width: int = 80, height: int = 40):
        """Initialize simple display."""
        self.width = width
        self.height = height
        self._last_frame_time = 0.0

    def clear(self):
        """Clear screen."""
        print("\033[2J\033[H", end="")

    def hide_cursor(self):
        """Hide cursor."""
        print("\033[?25l", end="")

    def show_cursor(self):
        """Show cursor."""
        print("\033[?25h", end="")

    def render_frame(self, frame: str, status_text: str | None = None):
        """Render frame with simple cursor positioning."""
        # Move to home position
        print("\033[H", end="")

        # Print frame
        print(frame)

        # Status line
        if status_text:
            print(f"\n{status_text}", end="")

        sys.stdout.flush()

    def wait_for_frame(self, target_fps: float = 30.0) -> float:
        """Wait to maintain FPS."""
        current_time = time.time()
        frame_time = 1.0 / target_fps

        if self._last_frame_time > 0:
            elapsed = current_time - self._last_frame_time
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)
                current_time = time.time()

        dt = current_time - self._last_frame_time if self._last_frame_time > 0 else frame_time
        self._last_frame_time = current_time
        return dt


def detect_terminal_color_support() -> ColorMode:
    """
    Detect terminal color support level.

    Returns:
        Best supported ColorMode
    """
    import os

    # Check COLORTERM for truecolor
    colorterm = os.environ.get("COLORTERM", "").lower()
    if colorterm in ("truecolor", "24bit"):
        return ColorMode.TRUECOLOR

    # Check TERM
    term = os.environ.get("TERM", "").lower()

    if "256color" in term or "256" in term:
        return ColorMode.ANSI_256

    if term in ("xterm", "screen", "vt100"):
        return ColorMode.ANSI_16

    # Default to 256 colors as a safe middle ground
    return ColorMode.ANSI_256
