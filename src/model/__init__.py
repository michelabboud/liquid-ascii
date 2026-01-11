"""Model package - head composition, visemes, and animation"""

from .animation import (
    smoothstep,
    lerp,
    ease_in_out,
    ease_in,
    ease_out,
    organic_noise,
    blink_pattern,
    AnimationController,
)
from .visemes import Viseme, VisemeController, VISEME_SHAPES
from .head import Head, HeadState, CharacterHead, HeadGeometry
from .expressions import Expression, ExpressionManager, EXPRESSIONS

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
]
