"""
Color schemes and effects for ASCII rendering.

Supports rainbow effects, custom color schemes, and terminal color modes.
"""

import math
import time
from dataclasses import dataclass
from enum import Enum


@dataclass
class RGB:
    """RGB color value."""

    r: int
    g: int
    b: int

    def to_tuple(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b)

    def lerp(self, other: "RGB", t: float) -> "RGB":
        """Interpolate between two colors."""
        return RGB(
            r=int(self.r + (other.r - self.r) * t),
            g=int(self.g + (other.g - self.g) * t),
            b=int(self.b + (other.b - self.b) * t),
        )

    def __str__(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"


class ColorMode(Enum):
    """Terminal color modes."""

    NONE = "none"  # No colors
    ANSI_16 = "16"  # Basic 16 ANSI colors
    ANSI_256 = "256"  # 256 color palette
    TRUECOLOR = "truecolor"  # 24-bit RGB


@dataclass
class ColorScheme:
    """
    Color scheme for ASCII rendering.
    """

    name: str
    base: RGB  # Main surface color
    highlight: RGB  # Bright areas
    shadow: RGB  # Dark areas
    eye_color: RGB  # Eyeball color
    pupil_color: RGB  # Pupil color
    mouth_color: RGB  # Inside mouth
    background: RGB | None = None

    def get_surface_color(self, intensity: float) -> RGB:
        """Get color for a surface point based on lighting intensity."""
        if intensity < 0.5:
            t = intensity * 2
            return self.shadow.lerp(self.base, t)
        else:
            t = (intensity - 0.5) * 2
            return self.base.lerp(self.highlight, t)


# Preset color schemes
PRESET_SCHEMES: dict[str, ColorScheme] = {
    "default": ColorScheme(
        name="default",
        base=RGB(200, 180, 160),
        highlight=RGB(255, 245, 230),
        shadow=RGB(80, 60, 50),
        eye_color=RGB(255, 255, 255),
        pupil_color=RGB(30, 30, 30),
        mouth_color=RGB(100, 40, 40),
    ),
    "pale": ColorScheme(
        name="pale",
        base=RGB(240, 220, 200),
        highlight=RGB(255, 255, 250),
        shadow=RGB(150, 130, 110),
        eye_color=RGB(255, 255, 255),
        pupil_color=RGB(50, 80, 120),
        mouth_color=RGB(180, 100, 100),
    ),
    "dark": ColorScheme(
        name="dark",
        base=RGB(80, 60, 50),
        highlight=RGB(150, 130, 110),
        shadow=RGB(30, 20, 15),
        eye_color=RGB(200, 200, 200),
        pupil_color=RGB(20, 20, 20),
        mouth_color=RGB(50, 20, 20),
    ),
    "robot": ColorScheme(
        name="robot",
        base=RGB(100, 120, 140),
        highlight=RGB(180, 200, 220),
        shadow=RGB(40, 50, 60),
        eye_color=RGB(0, 200, 255),
        pupil_color=RGB(0, 100, 150),
        mouth_color=RGB(20, 40, 60),
    ),
    "alien": ColorScheme(
        name="alien",
        base=RGB(100, 180, 100),
        highlight=RGB(150, 255, 150),
        shadow=RGB(30, 80, 30),
        eye_color=RGB(0, 0, 0),
        pupil_color=RGB(255, 100, 0),
        mouth_color=RGB(50, 100, 50),
    ),
    "ghost": ColorScheme(
        name="ghost",
        base=RGB(200, 200, 220),
        highlight=RGB(255, 255, 255),
        shadow=RGB(100, 100, 140),
        eye_color=RGB(0, 0, 0),
        pupil_color=RGB(150, 0, 0),
        mouth_color=RGB(80, 80, 100),
    ),
    "sunset": ColorScheme(
        name="sunset",
        base=RGB(255, 150, 100),
        highlight=RGB(255, 220, 180),
        shadow=RGB(150, 50, 50),
        eye_color=RGB(255, 255, 200),
        pupil_color=RGB(80, 40, 20),
        mouth_color=RGB(180, 60, 60),
    ),
    "ocean": ColorScheme(
        name="ocean",
        base=RGB(80, 150, 180),
        highlight=RGB(150, 220, 255),
        shadow=RGB(30, 70, 100),
        eye_color=RGB(200, 255, 255),
        pupil_color=RGB(20, 50, 80),
        mouth_color=RGB(40, 80, 100),
    ),
    "neon": ColorScheme(
        name="neon",
        base=RGB(255, 0, 255),
        highlight=RGB(255, 150, 255),
        shadow=RGB(100, 0, 100),
        eye_color=RGB(0, 255, 255),
        pupil_color=RGB(255, 255, 0),
        mouth_color=RGB(150, 0, 150),
    ),
    "monochrome": ColorScheme(
        name="monochrome",
        base=RGB(180, 180, 180),
        highlight=RGB(255, 255, 255),
        shadow=RGB(60, 60, 60),
        eye_color=RGB(255, 255, 255),
        pupil_color=RGB(0, 0, 0),
        mouth_color=RGB(80, 80, 80),
    ),
}


class RainbowColors:
    """
    Rainbow color effects for dynamic coloring.
    """

    def __init__(
        self,
        speed: float = 1.0,
        saturation: float = 1.0,
        brightness: float = 1.0,
        mode: str = "horizontal",  # horizontal, vertical, radial, time
    ):
        """
        Initialize rainbow color generator.

        Args:
            speed: Animation speed multiplier
            saturation: Color saturation (0-1)
            brightness: Color brightness (0-1)
            mode: How colors are distributed
        """
        self.speed = speed
        self.saturation = saturation
        self.brightness = brightness
        self.mode = mode
        self._start_time = time.time()

    def get_color(
        self,
        x: float = 0.0,
        y: float = 0.0,
        t: float | None = None,
    ) -> RGB:
        """
        Get rainbow color for a position.

        Args:
            x: Normalized x position (0-1)
            y: Normalized y position (0-1)
            t: Time value (auto if None)

        Returns:
            RGB color
        """
        if t is None:
            t = (time.time() - self._start_time) * self.speed

        # Calculate hue based on mode
        if self.mode == "horizontal":
            hue = (x + t * 0.1) % 1.0
        elif self.mode == "vertical":
            hue = (y + t * 0.1) % 1.0
        elif self.mode == "radial":
            dist = math.sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2)
            hue = (dist * 2 + t * 0.1) % 1.0
        elif self.mode == "diagonal":
            hue = ((x + y) * 0.5 + t * 0.1) % 1.0
        elif self.mode == "wave":
            hue = (x + math.sin(y * 6.28 + t) * 0.2 + t * 0.1) % 1.0
        else:  # time-only
            hue = (t * 0.1) % 1.0

        return self._hsv_to_rgb(hue, self.saturation, self.brightness)

    def get_color_for_char(
        self,
        col: int,
        row: int,
        width: int,
        height: int,
        intensity: float = 1.0,
    ) -> RGB:
        """
        Get color for a character position.

        Args:
            col: Column position
            row: Row position
            width: Total width
            height: Total height
            intensity: Lighting intensity to modulate brightness

        Returns:
            RGB color
        """
        x = col / max(width - 1, 1)
        y = row / max(height - 1, 1)

        color = self.get_color(x, y)

        # Modulate by intensity
        return RGB(
            r=int(color.r * intensity),
            g=int(color.g * intensity),
            b=int(color.b * intensity),
        )

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> RGB:
        """Convert HSV to RGB."""
        if s == 0:
            val = int(v * 255)
            return RGB(val, val, val)

        h = h * 6
        i = int(h)
        f = h - i
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))

        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q

        return RGB(int(r * 255), int(g * 255), int(b * 255))


class GradientColors:
    """
    Gradient color effects between multiple colors.
    """

    def __init__(self, colors: list[RGB], direction: str = "vertical"):
        """
        Initialize gradient.

        Args:
            colors: List of colors for gradient stops
            direction: Gradient direction (vertical, horizontal, radial)
        """
        self.colors = colors
        self.direction = direction

    def get_color(self, x: float, y: float) -> RGB:
        """Get color at normalized position."""
        if self.direction == "horizontal":
            t = x
        elif self.direction == "radial":
            t = math.sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2) * 2
            t = min(1.0, t)
        else:  # vertical
            t = y

        # Map t to color stops
        if len(self.colors) < 2:
            return self.colors[0] if self.colors else RGB(255, 255, 255)

        segment_length = 1.0 / (len(self.colors) - 1)
        segment_idx = min(int(t / segment_length), len(self.colors) - 2)
        segment_t = (t - segment_idx * segment_length) / segment_length

        return self.colors[segment_idx].lerp(self.colors[segment_idx + 1], segment_t)


def rgb_to_ansi_256(r: int, g: int, b: int) -> int:
    """Convert RGB to nearest ANSI 256 color code."""
    # Use the 6x6x6 color cube (codes 16-231)
    r_idx = round(r / 255 * 5)
    g_idx = round(g / 255 * 5)
    b_idx = round(b / 255 * 5)
    return 16 + 36 * r_idx + 6 * g_idx + b_idx


def rgb_to_ansi_escape(r: int, g: int, b: int, mode: ColorMode = ColorMode.TRUECOLOR) -> str:
    """Get ANSI escape sequence for a color."""
    if mode == ColorMode.TRUECOLOR:
        return f"\033[38;2;{r};{g};{b}m"
    elif mode == ColorMode.ANSI_256:
        code = rgb_to_ansi_256(r, g, b)
        return f"\033[38;5;{code}m"
    else:
        return ""


def reset_color() -> str:
    """Get ANSI reset escape sequence."""
    return "\033[0m"
