"""
Facial expression system for animated heads.

Provides predefined expression presets with smooth transitions between states.
"""

from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional
import time


@dataclass
class Expression:
    """
    Defines a facial expression state.

    All parameters range from -1.0 to 1.0 unless otherwise specified.
    """
    name: str

    # Eyebrow control
    eyebrow_raise: float = 0.0  # -1 = furrowed, 0 = neutral, +1 = raised
    eyebrow_asymmetry: float = 0.0  # -1 = left raised, +1 = right raised

    # Smile/mouth control
    smile_amount: float = 0.0  # -1 = frown, 0 = neutral, +1 = smile
    mouth_width_mod: float = 0.0  # -1 = narrow, 0 = normal, +1 = wide
    mouth_openness: float = 0.05  # 0 = closed, 1 = wide open
    lip_pucker: float = 0.0  # 0 = normal, 1 = puckered

    # Eye control
    blink_amount: float = 0.0  # 0 = open, 1 = closed
    eye_asymmetry: float = 0.0  # For winking: -1 = left closed, +1 = right closed
    eye_squint: float = 0.0  # 0 = normal, 1 = squinting
    eye_look_x: float = 0.0  # -1 = left, 0 = center, +1 = right
    eye_look_y: float = 0.0  # -1 = down, 0 = center, +1 = up

    # Head orientation
    head_tilt: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # (nod, turn, lean)

    # Meta information
    intensity: float = 1.0  # Multiplier for expression strength
    duration: float = 0.5  # Default transition duration in seconds


# Predefined expression library
EXPRESSIONS: Dict[str, Expression] = {
    "neutral": Expression(
        name="neutral",
        eyebrow_raise=0.0,
        smile_amount=0.0,
        mouth_openness=0.05,
        blink_amount=0.0,
    ),

    "happy": Expression(
        name="happy",
        eyebrow_raise=0.3,
        smile_amount=0.8,
        mouth_width_mod=0.3,
        mouth_openness=0.15,
        eye_squint=0.2,
        duration=0.7,
    ),

    "sad": Expression(
        name="sad",
        eyebrow_raise=-0.5,
        smile_amount=-0.3,
        mouth_width_mod=-0.2,
        mouth_openness=0.02,
        eye_look_y=-0.2,
        head_tilt=(0.1, 0.0, 0.0),  # Slight head droop
        duration=1.0,
    ),

    "angry": Expression(
        name="angry",
        eyebrow_raise=-0.8,
        smile_amount=-0.2,
        mouth_width_mod=-0.2,
        mouth_openness=0.1,
        eye_squint=0.3,
        head_tilt=(-0.1, 0.0, 0.0),  # Slight lean forward
        duration=0.5,
    ),

    "surprised": Expression(
        name="surprised",
        eyebrow_raise=0.8,
        smile_amount=0.0,
        mouth_width_mod=0.2,
        mouth_openness=0.6,
        eye_squint=-0.2,  # Eyes wide
        head_tilt=(-0.15, 0.0, 0.0),  # Head back slightly
        duration=0.3,
    ),

    "confused": Expression(
        name="confused",
        eyebrow_raise=0.3,
        eyebrow_asymmetry=-0.5,  # One eyebrow raised
        smile_amount=-0.1,
        mouth_width_mod=-0.1,
        mouth_openness=0.03,
        eye_look_x=-0.3,
        eye_look_y=0.2,
        head_tilt=(0.0, 0.0, 0.2),  # Head tilt
        duration=0.8,
    ),

    "tired": Expression(
        name="tired",
        eyebrow_raise=-0.3,
        smile_amount=-0.2,
        mouth_openness=0.1,
        blink_amount=0.5,  # Half-closed eyes
        eye_look_y=-0.3,
        head_tilt=(0.2, 0.0, 0.0),  # Head drooping forward
        duration=1.2,
    ),

    "wink": Expression(
        name="wink",
        eyebrow_raise=0.1,
        smile_amount=0.4,
        mouth_width_mod=0.1,
        blink_amount=0.0,
        eye_asymmetry=1.0,  # Right eye closed
        duration=0.4,
    ),

    "thinking": Expression(
        name="thinking",
        eyebrow_raise=0.2,
        eyebrow_asymmetry=-0.3,
        smile_amount=0.0,
        mouth_width_mod=-0.1,
        mouth_openness=0.02,
        lip_pucker=0.2,
        eye_look_x=-0.4,
        eye_look_y=0.5,  # Looking up and left
        head_tilt=(0.0, -0.15, 0.15),  # Head tilted
        duration=0.8,
    ),

    "excited": Expression(
        name="excited",
        eyebrow_raise=0.6,
        smile_amount=1.0,
        mouth_width_mod=0.4,
        mouth_openness=0.4,
        eye_squint=0.1,
        head_tilt=(-0.1, 0.0, 0.0),
        duration=0.5,
    ),

    "skeptical": Expression(
        name="skeptical",
        eyebrow_raise=0.5,
        eyebrow_asymmetry=0.6,  # One eyebrow very raised
        smile_amount=-0.2,
        mouth_width_mod=-0.2,
        eye_look_x=0.3,
        head_tilt=(0.0, 0.15, -0.15),
        duration=0.7,
    ),
}


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b."""
    return a + (b - a) * t


def ease_in_out(t: float) -> float:
    """Smooth easing function (smoothstep)."""
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


class ExpressionManager:
    """
    Manages expression transitions and blending.
    """

    def __init__(self):
        """Initialize expression manager."""
        self.current_expression: Expression = EXPRESSIONS["neutral"]
        self.target_expression: Optional[Expression] = None
        self.transition_start_time: float = 0.0
        self.transition_duration: float = 0.5
        self.is_transitioning: bool = False

    def set_expression(self, expression_name: str, duration: Optional[float] = None):
        """
        Transition to a new expression.

        Args:
            expression_name: Name of target expression
            duration: Transition duration in seconds (uses expression default if None)
        """
        if expression_name not in EXPRESSIONS:
            raise ValueError(f"Unknown expression: {expression_name}. Available: {list(EXPRESSIONS.keys())}")

        self.target_expression = EXPRESSIONS[expression_name]
        self.transition_start_time = time.time()
        self.transition_duration = duration if duration is not None else self.target_expression.duration
        self.is_transitioning = True

    def set_custom_expression(self, expression: Expression, duration: float = 0.5):
        """
        Transition to a custom expression.

        Args:
            expression: Custom Expression object
            duration: Transition duration in seconds
        """
        self.target_expression = expression
        self.transition_start_time = time.time()
        self.transition_duration = duration
        self.is_transitioning = True

    def update(self) -> Expression:
        """
        Update expression state and return current interpolated expression.

        Returns:
            Current expression state (interpolated if transitioning)
        """
        if not self.is_transitioning or self.target_expression is None:
            return self.current_expression

        # Calculate transition progress
        elapsed = time.time() - self.transition_start_time
        t = elapsed / self.transition_duration

        if t >= 1.0:
            # Transition complete
            self.current_expression = self.target_expression
            self.target_expression = None
            self.is_transitioning = False
            return self.current_expression

        # Apply easing
        t = ease_in_out(t)

        # Interpolate between current and target
        return self._blend_expressions(self.current_expression, self.target_expression, t)

    def _blend_expressions(self, expr_a: Expression, expr_b: Expression, t: float) -> Expression:
        """
        Blend two expressions with interpolation factor t.

        Args:
            expr_a: Start expression
            expr_b: Target expression
            t: Interpolation factor (0-1)

        Returns:
            Blended expression
        """
        return Expression(
            name=f"{expr_a.name}->{expr_b.name}",
            eyebrow_raise=lerp(expr_a.eyebrow_raise, expr_b.eyebrow_raise, t),
            eyebrow_asymmetry=lerp(expr_a.eyebrow_asymmetry, expr_b.eyebrow_asymmetry, t),
            smile_amount=lerp(expr_a.smile_amount, expr_b.smile_amount, t),
            mouth_width_mod=lerp(expr_a.mouth_width_mod, expr_b.mouth_width_mod, t),
            mouth_openness=lerp(expr_a.mouth_openness, expr_b.mouth_openness, t),
            lip_pucker=lerp(expr_a.lip_pucker, expr_b.lip_pucker, t),
            blink_amount=lerp(expr_a.blink_amount, expr_b.blink_amount, t),
            eye_asymmetry=lerp(expr_a.eye_asymmetry, expr_b.eye_asymmetry, t),
            eye_squint=lerp(expr_a.eye_squint, expr_b.eye_squint, t),
            eye_look_x=lerp(expr_a.eye_look_x, expr_b.eye_look_x, t),
            eye_look_y=lerp(expr_a.eye_look_y, expr_b.eye_look_y, t),
            head_tilt=(
                lerp(expr_a.head_tilt[0], expr_b.head_tilt[0], t),
                lerp(expr_a.head_tilt[1], expr_b.head_tilt[1], t),
                lerp(expr_a.head_tilt[2], expr_b.head_tilt[2], t),
            ),
            intensity=lerp(expr_a.intensity, expr_b.intensity, t),
        )

    def get_current_expression_name(self) -> str:
        """Get the name of the current expression."""
        return self.current_expression.name

    def list_expressions(self) -> list[str]:
        """Get list of available expression names."""
        return list(EXPRESSIONS.keys())
