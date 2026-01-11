"""Tests for color system and schemes."""

import time

import pytest

from src.terminal.colors import (
    RGB,
    ColorMode,
    ColorScheme,
    GradientColors,
    PRESET_SCHEMES,
    RainbowColors,
    reset_color,
    rgb_to_ansi_256,
    rgb_to_ansi_escape,
)


class TestRGB:
    """Tests for RGB dataclass."""

    def test_rgb_creation(self):
        """RGB can be created with values."""
        color = RGB(255, 128, 64)
        assert color.r == 255
        assert color.g == 128
        assert color.b == 64

    def test_rgb_to_tuple(self):
        """RGB can be converted to tuple."""
        color = RGB(200, 150, 100)
        assert color.to_tuple() == (200, 150, 100)

    def test_rgb_lerp_at_zero(self):
        """Lerp at t=0 returns start color."""
        start = RGB(100, 100, 100)
        end = RGB(200, 200, 200)
        result = start.lerp(end, 0.0)
        assert result.r == 100
        assert result.g == 100
        assert result.b == 100

    def test_rgb_lerp_at_one(self):
        """Lerp at t=1 returns end color."""
        start = RGB(100, 100, 100)
        end = RGB(200, 200, 200)
        result = start.lerp(end, 1.0)
        assert result.r == 200
        assert result.g == 200
        assert result.b == 200

    def test_rgb_lerp_at_half(self):
        """Lerp at t=0.5 returns midpoint."""
        start = RGB(100, 100, 100)
        end = RGB(200, 200, 200)
        result = start.lerp(end, 0.5)
        assert result.r == 150
        assert result.g == 150
        assert result.b == 150

    def test_rgb_lerp_channels_independent(self):
        """Lerp interpolates each channel independently."""
        start = RGB(0, 100, 200)
        end = RGB(200, 100, 0)
        result = start.lerp(end, 0.5)
        assert result.r == 100  # Midpoint of 0-200
        assert result.g == 100  # Stays at 100
        assert result.b == 100  # Midpoint of 200-0

    def test_rgb_str_formatting(self):
        """RGB formats to hex string."""
        color = RGB(255, 128, 64)
        assert str(color) == "#ff8040"

    def test_rgb_str_zero_padding(self):
        """RGB hex format includes zero padding."""
        color = RGB(15, 5, 0)
        assert str(color) == "#0f0500"


class TestColorMode:
    """Tests for ColorMode enum."""

    def test_all_color_modes_defined(self):
        """All expected color modes are defined."""
        assert hasattr(ColorMode, "NONE")
        assert hasattr(ColorMode, "ANSI_16")
        assert hasattr(ColorMode, "ANSI_256")
        assert hasattr(ColorMode, "TRUECOLOR")

    def test_color_mode_values(self):
        """Color modes have correct values."""
        assert ColorMode.NONE.value == "none"
        assert ColorMode.ANSI_16.value == "16"
        assert ColorMode.ANSI_256.value == "256"
        assert ColorMode.TRUECOLOR.value == "truecolor"


class TestColorScheme:
    """Tests for ColorScheme dataclass."""

    def test_color_scheme_creation(self):
        """ColorScheme can be created."""
        scheme = ColorScheme(
            name="test",
            base=RGB(200, 180, 160),
            highlight=RGB(255, 245, 230),
            shadow=RGB(80, 60, 50),
            eye_color=RGB(255, 255, 255),
            pupil_color=RGB(30, 30, 30),
            mouth_color=RGB(100, 40, 40),
        )
        assert scheme.name == "test"
        assert scheme.base.r == 200

    def test_get_surface_color_dark(self):
        """get_surface_color blends shadow to base for low intensity."""
        scheme = PRESET_SCHEMES["default"]
        color = scheme.get_surface_color(0.0)
        # At 0.0, should be shadow color
        assert color.r == scheme.shadow.r
        assert color.g == scheme.shadow.g
        assert color.b == scheme.shadow.b

    def test_get_surface_color_mid(self):
        """get_surface_color returns base at mid intensity."""
        scheme = PRESET_SCHEMES["default"]
        color = scheme.get_surface_color(0.5)
        # At 0.5, should be base color
        assert color.r == scheme.base.r
        assert color.g == scheme.base.g
        assert color.b == scheme.base.b

    def test_get_surface_color_bright(self):
        """get_surface_color blends base to highlight for high intensity."""
        scheme = PRESET_SCHEMES["default"]
        color = scheme.get_surface_color(1.0)
        # At 1.0, should be highlight color
        assert color.r == scheme.highlight.r
        assert color.g == scheme.highlight.g
        assert color.b == scheme.highlight.b

    def test_get_surface_color_quarter(self):
        """get_surface_color interpolates in shadow range."""
        scheme = PRESET_SCHEMES["default"]
        color = scheme.get_surface_color(0.25)
        # Should be between shadow and base
        assert scheme.shadow.r < color.r < scheme.base.r


class TestPresetSchemes:
    """Tests for predefined color schemes."""

    def test_all_presets_exist(self):
        """All expected presets are defined."""
        expected = [
            "default",
            "pale",
            "dark",
            "robot",
            "alien",
            "ghost",
            "sunset",
            "ocean",
            "neon",
            "monochrome",
        ]
        for name in expected:
            assert name in PRESET_SCHEMES

    def test_default_scheme_complete(self):
        """Default scheme has all required colors."""
        scheme = PRESET_SCHEMES["default"]
        assert scheme.name == "default"
        assert isinstance(scheme.base, RGB)
        assert isinstance(scheme.highlight, RGB)
        assert isinstance(scheme.shadow, RGB)
        assert isinstance(scheme.eye_color, RGB)
        assert isinstance(scheme.pupil_color, RGB)
        assert isinstance(scheme.mouth_color, RGB)

    def test_all_schemes_complete(self):
        """All presets have required attributes."""
        for name, scheme in PRESET_SCHEMES.items():
            assert scheme.name == name
            assert isinstance(scheme.base, RGB)
            assert isinstance(scheme.highlight, RGB)
            assert isinstance(scheme.shadow, RGB)
            assert isinstance(scheme.eye_color, RGB)
            assert isinstance(scheme.pupil_color, RGB)
            assert isinstance(scheme.mouth_color, RGB)

    def test_neon_scheme_vibrant(self):
        """Neon scheme has high saturation colors."""
        scheme = PRESET_SCHEMES["neon"]
        # Neon colors should have high values in at least one channel
        assert max(scheme.base.r, scheme.base.g, scheme.base.b) >= 200

    def test_dark_scheme_low_values(self):
        """Dark scheme has darker colors."""
        scheme = PRESET_SCHEMES["dark"]
        default = PRESET_SCHEMES["default"]
        # Dark scheme base should be darker than default
        assert scheme.base.r < default.base.r
        assert scheme.base.g < default.base.g
        assert scheme.base.b < default.base.b


class TestRainbowColors:
    """Tests for RainbowColors class."""

    def test_rainbow_initialization(self):
        """RainbowColors initializes with defaults."""
        rainbow = RainbowColors()
        assert rainbow.speed == 1.0
        assert rainbow.saturation == 1.0
        assert rainbow.brightness == 1.0
        assert rainbow.mode == "horizontal"

    def test_rainbow_custom_params(self):
        """RainbowColors accepts custom parameters."""
        rainbow = RainbowColors(
            speed=2.0, saturation=0.8, brightness=0.9, mode="vertical"
        )
        assert rainbow.speed == 2.0
        assert rainbow.saturation == 0.8
        assert rainbow.brightness == 0.9
        assert rainbow.mode == "vertical"

    def test_get_color_returns_rgb(self):
        """get_color returns RGB object."""
        rainbow = RainbowColors()
        color = rainbow.get_color(0.5, 0.5, t=0.0)
        assert isinstance(color, RGB)

    def test_get_color_horizontal_varies(self):
        """Horizontal mode varies color with x position."""
        rainbow = RainbowColors(mode="horizontal")
        color1 = rainbow.get_color(0.25, 0.5, t=0.0)
        color2 = rainbow.get_color(0.75, 0.5, t=0.0)
        # Colors should differ based on x position (avoid wrap at 1.0)
        assert color1.to_tuple() != color2.to_tuple()

    def test_get_color_vertical_varies(self):
        """Vertical mode varies color with y position."""
        rainbow = RainbowColors(mode="vertical")
        color1 = rainbow.get_color(0.5, 0.25, t=0.0)
        color2 = rainbow.get_color(0.5, 0.75, t=0.0)
        # Colors should differ based on y position (avoid wrap at 1.0)
        assert color1.to_tuple() != color2.to_tuple()

    def test_get_color_radial_varies(self):
        """Radial mode varies color with distance from center."""
        rainbow = RainbowColors(mode="radial")
        center = rainbow.get_color(0.5, 0.5, t=0.0)
        edge = rainbow.get_color(1.0, 1.0, t=0.0)
        # Colors should differ based on distance
        assert center.to_tuple() != edge.to_tuple()

    def test_get_color_diagonal_mode(self):
        """Diagonal mode works."""
        rainbow = RainbowColors(mode="diagonal")
        color = rainbow.get_color(0.5, 0.5, t=0.0)
        assert isinstance(color, RGB)

    def test_get_color_wave_mode(self):
        """Wave mode works."""
        rainbow = RainbowColors(mode="wave")
        color = rainbow.get_color(0.5, 0.5, t=0.0)
        assert isinstance(color, RGB)

    def test_get_color_time_mode(self):
        """Time mode works."""
        rainbow = RainbowColors(mode="time")
        color = rainbow.get_color(0.5, 0.5, t=0.0)
        assert isinstance(color, RGB)

    def test_get_color_for_char(self):
        """get_color_for_char returns RGB."""
        rainbow = RainbowColors()
        color = rainbow.get_color_for_char(10, 20, 80, 40)
        assert isinstance(color, RGB)

    def test_get_color_for_char_intensity(self):
        """get_color_for_char modulates by intensity."""
        rainbow = RainbowColors()
        bright = rainbow.get_color_for_char(10, 20, 80, 40, intensity=1.0)
        dim = rainbow.get_color_for_char(10, 20, 80, 40, intensity=0.5)
        # Dim should have lower values
        assert dim.r <= bright.r
        assert dim.g <= bright.g
        assert dim.b <= bright.b

    def test_hsv_to_rgb_red(self):
        """HSV to RGB for red (h=0)."""
        rainbow = RainbowColors()
        color = rainbow._hsv_to_rgb(0.0, 1.0, 1.0)
        # Should be pure red
        assert color.r == 255
        assert color.g == 0
        assert color.b == 0

    def test_hsv_to_rgb_green(self):
        """HSV to RGB for green (h=0.33)."""
        rainbow = RainbowColors()
        color = rainbow._hsv_to_rgb(1 / 3, 1.0, 1.0)
        # Should be pure green
        assert color.r == 0
        assert color.g == 255
        assert color.b == 0

    def test_hsv_to_rgb_blue(self):
        """HSV to RGB for blue (h=0.67)."""
        rainbow = RainbowColors()
        color = rainbow._hsv_to_rgb(2 / 3, 1.0, 1.0)
        # Should be pure blue
        assert color.r == 0
        assert color.g == 0
        assert color.b == 255

    def test_hsv_to_rgb_grayscale(self):
        """HSV with s=0 returns grayscale."""
        rainbow = RainbowColors()
        color = rainbow._hsv_to_rgb(0.5, 0.0, 0.5)
        # Should be gray (all channels equal)
        assert color.r == color.g == color.b


class TestGradientColors:
    """Tests for GradientColors class."""

    def test_gradient_initialization(self):
        """GradientColors initializes with colors."""
        colors = [RGB(0, 0, 0), RGB(255, 255, 255)]
        gradient = GradientColors(colors)
        assert gradient.colors == colors
        assert gradient.direction == "vertical"

    def test_gradient_custom_direction(self):
        """GradientColors accepts custom direction."""
        colors = [RGB(0, 0, 0), RGB(255, 255, 255)]
        gradient = GradientColors(colors, direction="horizontal")
        assert gradient.direction == "horizontal"

    def test_get_color_returns_rgb(self):
        """get_color returns RGB object."""
        colors = [RGB(0, 0, 0), RGB(255, 255, 255)]
        gradient = GradientColors(colors)
        color = gradient.get_color(0.5, 0.5)
        assert isinstance(color, RGB)

    def test_get_color_vertical_start(self):
        """Vertical gradient at y=0 returns first color."""
        colors = [RGB(100, 100, 100), RGB(200, 200, 200)]
        gradient = GradientColors(colors, direction="vertical")
        color = gradient.get_color(0.5, 0.0)
        assert color.r == 100
        assert color.g == 100
        assert color.b == 100

    def test_get_color_vertical_end(self):
        """Vertical gradient at y=1 returns last color."""
        colors = [RGB(100, 100, 100), RGB(200, 200, 200)]
        gradient = GradientColors(colors, direction="vertical")
        color = gradient.get_color(0.5, 1.0)
        assert color.r == 200
        assert color.g == 200
        assert color.b == 200

    def test_get_color_vertical_midpoint(self):
        """Vertical gradient interpolates at midpoint."""
        colors = [RGB(100, 100, 100), RGB(200, 200, 200)]
        gradient = GradientColors(colors, direction="vertical")
        color = gradient.get_color(0.5, 0.5)
        # Should be midpoint
        assert color.r == 150
        assert color.g == 150
        assert color.b == 150

    def test_get_color_horizontal_varies(self):
        """Horizontal gradient varies with x."""
        colors = [RGB(0, 0, 0), RGB(255, 255, 255)]
        gradient = GradientColors(colors, direction="horizontal")
        left = gradient.get_color(0.0, 0.5)
        right = gradient.get_color(1.0, 0.5)
        assert left.r < right.r

    def test_get_color_radial_center(self):
        """Radial gradient at center returns first color."""
        colors = [RGB(100, 100, 100), RGB(200, 200, 200)]
        gradient = GradientColors(colors, direction="radial")
        color = gradient.get_color(0.5, 0.5)
        # Center should be close to first color
        assert color.r == 100

    def test_get_color_multiple_stops(self):
        """Gradient works with multiple color stops."""
        colors = [RGB(0, 0, 0), RGB(128, 128, 128), RGB(255, 255, 255)]
        gradient = GradientColors(colors)
        color = gradient.get_color(0.5, 0.5)
        # Should interpolate through middle color
        assert isinstance(color, RGB)

    def test_get_color_single_color(self):
        """Gradient with single color returns that color."""
        colors = [RGB(123, 123, 123)]
        gradient = GradientColors(colors)
        color = gradient.get_color(0.5, 0.5)
        assert color.r == 123


class TestColorUtilities:
    """Tests for color utility functions."""

    def test_rgb_to_ansi_256_black(self):
        """Black converts to ANSI code 16."""
        code = rgb_to_ansi_256(0, 0, 0)
        assert code == 16

    def test_rgb_to_ansi_256_white(self):
        """White converts to ANSI code 231."""
        code = rgb_to_ansi_256(255, 255, 255)
        assert code == 231

    def test_rgb_to_ansi_256_red(self):
        """Pure red converts correctly."""
        code = rgb_to_ansi_256(255, 0, 0)
        assert 196 <= code <= 231  # Red range in color cube

    def test_rgb_to_ansi_256_in_range(self):
        """All RGB values map to valid ANSI codes."""
        for r in [0, 128, 255]:
            for g in [0, 128, 255]:
                for b in [0, 128, 255]:
                    code = rgb_to_ansi_256(r, g, b)
                    assert 16 <= code <= 231

    def test_rgb_to_ansi_escape_truecolor(self):
        """Truecolor mode produces correct escape sequence."""
        escape = rgb_to_ansi_escape(200, 150, 100, ColorMode.TRUECOLOR)
        assert escape == "\033[38;2;200;150;100m"

    def test_rgb_to_ansi_escape_256(self):
        """256 color mode produces correct escape sequence."""
        escape = rgb_to_ansi_escape(255, 0, 0, ColorMode.ANSI_256)
        assert escape.startswith("\033[38;5;")
        assert escape.endswith("m")

    def test_rgb_to_ansi_escape_none(self):
        """None mode returns empty string."""
        escape = rgb_to_ansi_escape(200, 150, 100, ColorMode.NONE)
        assert escape == ""

    def test_rgb_to_ansi_escape_ansi16(self):
        """ANSI 16 mode returns empty string."""
        escape = rgb_to_ansi_escape(200, 150, 100, ColorMode.ANSI_16)
        assert escape == ""

    def test_reset_color(self):
        """reset_color returns ANSI reset sequence."""
        reset = reset_color()
        assert reset == "\033[0m"
