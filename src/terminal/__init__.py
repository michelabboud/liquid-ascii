"""Terminal package - display and input handling"""

from .colors import PRESET_SCHEMES, ColorScheme, RainbowColors
from .display import ColorMode, Display
from .effects import (
    DepthOfFieldEffect,
    EffectsCompositor,
    GlitchEffect,
    MatrixRainEffect,
    MotionTrail,
    ParticleSystem,
    ScanlineEffect,
)
from .input import (
    InputCommand,
    InputEvent,
    InteractiveController,
    InteractiveInputHandler,
)

__all__ = [
    "Display",
    "ColorMode",
    "ColorScheme",
    "RainbowColors",
    "PRESET_SCHEMES",
    "InputCommand",
    "InputEvent",
    "InteractiveInputHandler",
    "InteractiveController",
    "ParticleSystem",
    "MotionTrail",
    "GlitchEffect",
    "ScanlineEffect",
    "MatrixRainEffect",
    "DepthOfFieldEffect",
    "EffectsCompositor",
]
