"""Terminal package - display and input handling"""

from .display import Display, ColorMode
from .colors import ColorScheme, RainbowColors, PRESET_SCHEMES
from .input import (
    InputCommand,
    InputEvent,
    InteractiveInputHandler,
    InteractiveController,
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
]
