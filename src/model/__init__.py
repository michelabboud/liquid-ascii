"""Model package - head composition, visemes, and animation"""

from .animation import (
    AnimationController,
    blink_pattern,
    ease_in,
    ease_in_out,
    ease_out,
    lerp,
    organic_noise,
    smoothstep,
)
from .expressions import EXPRESSIONS, Expression, ExpressionManager
from .gestures import (
    GestureController,
    GestureSequencer,
    GestureState,
    create_gesture_sequence,
)
from .head import CharacterHead, Head, HeadGeometry, HeadState
from .visemes import VISEME_SHAPES, Viseme, VisemeController

__all__ = [
    "smoothstep",
    "lerp",
    "ease_in_out",
    "ease_in",
    "ease_out",
    "organic_noise",
    "blink_pattern",
    "AnimationController",
    "Viseme",
    "VisemeController",
    "VISEME_SHAPES",
    "Head",
    "HeadState",
    "CharacterHead",
    "HeadGeometry",
    "Expression",
    "ExpressionManager",
    "EXPRESSIONS",
    "GestureController",
    "GestureSequencer",
    "GestureState",
    "create_gesture_sequence",
]
