"""
3D Head model composed from SDF primitives.

Creates a talking head using smooth SDF operations for liquid-like
morphing between expressions and mouth shapes.
"""

import math
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

import numpy as np

from ..renderer.sdf import (
    Vec3,
    _to_array,
    sdf_ellipsoid,
    sdf_smooth_subtraction,
    sdf_smooth_union,
    sdf_sphere,
)
from .animation import blink_pattern, breathing_motion, organic_noise
from .expressions import Expression, ExpressionManager


class FacialFeature(Enum):
    """Types of facial features for color coding."""

    SKIN = "skin"
    EYE = "eye"
    PUPIL = "pupil"
    MOUTH = "mouth"


@dataclass
class HeadState:
    """
    Current state of the animated head.
    """

    # Mouth animation
    mouth_openness: float = 0.05
    mouth_width: float = 0.5
    lip_pucker: float = 0.0

    # Eye animation
    blink_amount: float = 0.0  # 0 = open, 1 = closed
    eye_look_x: float = 0.0  # -1 = left, 1 = right
    eye_look_y: float = 0.0  # -1 = down, 1 = up

    # Expression modifiers
    eyebrow_raise: float = 0.0  # -1 = frown, 1 = raised
    smile_amount: float = 0.0  # 0 = neutral, 1 = smiling

    # Head orientation
    head_tilt_x: float = 0.0  # nod
    head_tilt_y: float = 0.0  # turn
    head_tilt_z: float = 0.0  # lean

    # Organic movement offset
    idle_offset: tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass
class HeadGeometry:
    """
    Geometric parameters for head shape.
    """

    # Main head
    head_radii: tuple[float, float, float] = (1.0, 1.3, 1.0)

    # Eyes
    eye_socket_radius: float = 0.18
    eyeball_radius: float = 0.12
    eye_separation: float = 0.35
    eye_height: float = 0.25
    eye_depth: float = 0.85
    pupil_radius: float = 0.06

    # Mouth
    mouth_y: float = -0.35
    mouth_depth: float = 0.9
    mouth_width_base: float = 0.25
    mouth_height_base: float = 0.08

    # Nose
    nose_length: float = 0.15
    nose_width: float = 0.12
    nose_height: float = 0.0

    # Smoothing factors for liquid blending
    eye_socket_smooth: float = 0.1
    eyeball_smooth: float = 0.05
    mouth_smooth: float = 0.12
    nose_smooth: float = 0.08


class Head:
    """
    Animated 3D head model using SDF composition.
    """

    def __init__(
        self,
        geometry: HeadGeometry | None = None,
        enable_idle_animation: bool = True,
        enable_expressions: bool = True,
        enable_gestures: bool = False,
    ):
        """
        Initialize the head model.

        Args:
            geometry: Head geometry parameters
            enable_idle_animation: Enable organic idle movement
            enable_expressions: Enable expression system
            enable_gestures: Enable gesture system (nodding, shaking, etc.)
        """
        self.geometry = geometry or HeadGeometry()
        self.state = HeadState()
        self.enable_idle_animation = enable_idle_animation
        self.enable_expressions = enable_expressions
        self.enable_gestures = enable_gestures
        self._time = 0.0

        # Expression system
        self.expression_manager = ExpressionManager() if enable_expressions else None

        # Gesture system
        from .gestures import GestureController

        self.gesture_controller = GestureController() if enable_gestures else None

    def update(self, dt: float):
        """
        Update head animation state.

        Args:
            dt: Time delta since last update
        """
        self._time += dt

        # Update expressions
        if self.enable_expressions and self.expression_manager:
            current_expr = self.expression_manager.update()
            self._apply_expression(current_expr)

        # Update gestures
        if self.enable_gestures and self.gesture_controller:
            tilt_x, tilt_y, tilt_z, eye_x, eye_y = self.gesture_controller.update(dt)
            # Apply gesture transformations
            self.state.head_tilt = (tilt_x, tilt_y, tilt_z)
            self.state.eye_look_x = eye_x
            self.state.eye_look_y = eye_y

        if self.enable_idle_animation:
            # Apply organic noise for lifelike movement
            self.state.idle_offset = organic_noise(self._time)

            # Auto-blink (only if not controlled by expression)
            if not (
                self.enable_expressions
                and self.expression_manager
                and self.expression_manager.is_transitioning
            ):
                self.state.blink_amount = blink_pattern(self._time)

    def set_mouth(self, openness: float, width: float = 0.5, pucker: float = 0.0):
        """Set mouth shape parameters."""
        self.state.mouth_openness = max(0.0, min(1.0, openness))
        self.state.mouth_width = max(0.0, min(1.0, width))
        self.state.lip_pucker = max(0.0, min(1.0, pucker))

    def set_blink(self, amount: float):
        """Set blink amount (overrides auto-blink)."""
        self.state.blink_amount = max(0.0, min(1.0, amount))

    def set_eye_look(self, x: float, y: float):
        """Set eye look direction."""
        self.state.eye_look_x = max(-1.0, min(1.0, x))
        self.state.eye_look_y = max(-1.0, min(1.0, y))

    def set_head_tilt(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        """Set head orientation."""
        self.state.head_tilt_x = x
        self.state.head_tilt_y = y
        self.state.head_tilt_z = z

    def set_expression(self, expression_name: str, duration: float | None = None):
        """
        Set facial expression.

        Args:
            expression_name: Name of expression (happy, sad, angry, etc.)
            duration: Transition duration in seconds (uses default if None)
        """
        if not self.enable_expressions or not self.expression_manager:
            return
        self.expression_manager.set_expression(expression_name, duration)

    def _apply_expression(self, expression: Expression):
        """
        Apply expression state to head state.

        Args:
            expression: Expression to apply
        """
        # Apply expression to state
        self.state.eyebrow_raise = expression.eyebrow_raise
        self.state.smile_amount = expression.smile_amount

        # Mouth shaping from expression
        self.state.mouth_openness = expression.mouth_openness
        self.state.lip_pucker = expression.lip_pucker

        # Eye control from expression
        if expression.blink_amount > 0:
            self.state.blink_amount = expression.blink_amount
        self.state.eye_look_x = expression.eye_look_x
        self.state.eye_look_y = expression.eye_look_y

        # Head orientation from expression
        self.state.head_tilt_x = expression.head_tilt[0]
        self.state.head_tilt_y = expression.head_tilt[1]
        self.state.head_tilt_z = expression.head_tilt[2]

    def get_current_expression(self) -> str | None:
        """Get name of current expression."""
        if self.expression_manager:
            return self.expression_manager.get_current_expression_name()
        return None

    def list_expressions(self) -> list[str]:
        """Get list of available expressions."""
        if self.expression_manager:
            return self.expression_manager.list_expressions()
        return []

    def _rotate_point(self, p: np.ndarray) -> np.ndarray:
        """Apply head rotation to a point."""
        # Simple Euler rotation for head tilt
        x, y, z = p

        # Rotate around X (nod)
        if self.state.head_tilt_x != 0:
            c, s = math.cos(self.state.head_tilt_x), math.sin(self.state.head_tilt_x)
            y, z = c * y - s * z, s * y + c * z

        # Rotate around Y (turn)
        if self.state.head_tilt_y != 0:
            c, s = math.cos(self.state.head_tilt_y), math.sin(self.state.head_tilt_y)
            x, z = c * x + s * z, -s * x + c * z

        # Rotate around Z (lean)
        if self.state.head_tilt_z != 0:
            c, s = math.cos(self.state.head_tilt_z), math.sin(self.state.head_tilt_z)
            x, y = c * x - s * y, s * x + c * y

        return np.array([x, y, z])

    def get_sdf(self) -> Callable[[Vec3], float]:
        """
        Get the SDF function for the current head state.

        Returns:
            SDF function that takes a 3D point and returns distance
        """
        g = self.geometry
        s = self.state

        # Pre-compute animated values
        mouth_height = g.mouth_height_base + s.mouth_openness * 0.25
        mouth_width = g.mouth_width_base * (0.8 + s.mouth_width * 0.4)
        mouth_pucker_effect = 1.0 - s.lip_pucker * 0.3

        eyeball_scale = 1.0 - s.blink_amount * 0.8
        eye_look_offset_x = s.eye_look_x * 0.03
        eye_look_offset_y = s.eye_look_y * 0.03

        # Breathing animation
        breath = breathing_motion(self._time)

        def head_sdf(point: Vec3) -> float:
            p = _to_array(point)

            # Apply idle offset for organic movement
            if self.enable_idle_animation:
                p = p - np.array(s.idle_offset)

            # Apply head rotation
            p = self._rotate_point(p)

            # Apply breathing (subtle vertical movement)
            p = p - np.array([0, breath, 0])

            # === Main head shape ===
            head = sdf_ellipsoid(p, (0, 0, 0), g.head_radii)

            # === Eye sockets (smooth subtraction) ===
            eye_l_pos = (-g.eye_separation, g.eye_height, g.eye_depth)
            eye_r_pos = (g.eye_separation, g.eye_height, g.eye_depth)

            eye_socket_l = sdf_sphere(p, eye_l_pos, g.eye_socket_radius)
            eye_socket_r = sdf_sphere(p, eye_r_pos, g.eye_socket_radius)

            result = sdf_smooth_subtraction(eye_socket_l, head, g.eye_socket_smooth)
            result = sdf_smooth_subtraction(eye_socket_r, result, g.eye_socket_smooth)

            # === Eyeballs (smooth union back in) ===
            # Eyeballs shrink when blinking
            actual_eyeball_radius = g.eyeball_radius * eyeball_scale

            eyeball_l_pos = (
                -g.eye_separation + eye_look_offset_x,
                g.eye_height + eye_look_offset_y,
                g.eye_depth + 0.05,
            )
            eyeball_r_pos = (
                g.eye_separation + eye_look_offset_x,
                g.eye_height + eye_look_offset_y,
                g.eye_depth + 0.05,
            )

            if eyeball_scale > 0.1:  # Only render if eye is open enough
                eyeball_l = sdf_sphere(p, eyeball_l_pos, actual_eyeball_radius)
                eyeball_r = sdf_sphere(p, eyeball_r_pos, actual_eyeball_radius)
                result = sdf_smooth_union(eyeball_l, result, g.eyeball_smooth)
                result = sdf_smooth_union(eyeball_r, result, g.eyeball_smooth)

            # === Mouth cavity (smooth subtraction) ===
            mouth_pos = (0, g.mouth_y, g.mouth_depth)
            mouth_radii = (mouth_width * mouth_pucker_effect, mouth_height, 0.15)
            mouth = sdf_ellipsoid(p, mouth_pos, mouth_radii)
            result = sdf_smooth_subtraction(mouth, result, g.mouth_smooth)

            # === Nose (subtle bump) ===
            nose_pos = (0, g.nose_height, g.head_radii[2] * 0.95)
            nose = sdf_ellipsoid(p, nose_pos, (g.nose_width, g.nose_length, 0.1))
            result = sdf_smooth_union(nose, result, g.nose_smooth)

            return result

        return head_sdf

    def get_sdf_with_pupils(self) -> Callable[[Vec3], tuple[float, bool]]:
        """
        Get SDF function that also returns whether point is on pupil.

        Returns:
            Function returning (distance, is_pupil) tuple
        """
        g = self.geometry
        s = self.state
        base_sdf = self.get_sdf()

        eye_look_offset_x = s.eye_look_x * 0.03
        eye_look_offset_y = s.eye_look_y * 0.03

        pupil_l_pos = np.array(
            [
                -g.eye_separation + eye_look_offset_x,
                g.eye_height + eye_look_offset_y,
                g.eye_depth + 0.1,
            ]
        )
        pupil_r_pos = np.array(
            [
                g.eye_separation + eye_look_offset_x,
                g.eye_height + eye_look_offset_y,
                g.eye_depth + 0.1,
            ]
        )

        def sdf_with_pupils(point: Vec3) -> tuple[float, bool]:
            p = _to_array(point)
            dist = base_sdf(point)

            # Check if point is near pupil
            if dist < 0.05:  # Near surface
                dist_to_pupil_l = np.linalg.norm(p - pupil_l_pos)
                dist_to_pupil_r = np.linalg.norm(p - pupil_r_pos)
                is_pupil = min(dist_to_pupil_l, dist_to_pupil_r) < g.pupil_radius
                return dist, is_pupil

            return dist, False

        return sdf_with_pupils

    def get_sdf_with_features(self) -> Callable[[Vec3], tuple[float, FacialFeature]]:
        """
        Get SDF function that identifies facial features for coloring.

        Returns:
            Function returning (distance, feature_type) tuple
        """
        g = self.geometry
        s = self.state
        base_sdf = self.get_sdf()

        eye_look_offset_x = s.eye_look_x * 0.03
        eye_look_offset_y = s.eye_look_y * 0.03

        # Eye positions
        eyeball_l_pos = np.array(
            [
                -g.eye_separation + eye_look_offset_x,
                g.eye_height + eye_look_offset_y,
                g.eye_depth + 0.05,
            ]
        )
        eyeball_r_pos = np.array(
            [
                g.eye_separation + eye_look_offset_x,
                g.eye_height + eye_look_offset_y,
                g.eye_depth + 0.05,
            ]
        )

        # Pupil positions
        pupil_l_pos = np.array(
            [
                -g.eye_separation + eye_look_offset_x,
                g.eye_height + eye_look_offset_y,
                g.eye_depth + 0.1,
            ]
        )
        pupil_r_pos = np.array(
            [
                g.eye_separation + eye_look_offset_x,
                g.eye_height + eye_look_offset_y,
                g.eye_depth + 0.1,
            ]
        )

        # Mouth position
        mouth_pos = np.array([0, g.mouth_y, g.mouth_depth])

        def sdf_with_features(point: Vec3) -> tuple[float, FacialFeature]:
            p = _to_array(point)
            dist = base_sdf(point)

            # Only check features near surface
            if dist < 0.05:
                # Check pupils first (most specific)
                dist_to_pupil_l = np.linalg.norm(p - pupil_l_pos)
                dist_to_pupil_r = np.linalg.norm(p - pupil_r_pos)
                if min(dist_to_pupil_l, dist_to_pupil_r) < g.pupil_radius:
                    return dist, FacialFeature.PUPIL

                # Check eyeballs
                eyeball_scale = 1.0 - s.blink_amount * 0.8
                if eyeball_scale > 0.1:
                    dist_to_eye_l = np.linalg.norm(p - eyeball_l_pos)
                    dist_to_eye_r = np.linalg.norm(p - eyeball_r_pos)
                    actual_eyeball_radius = g.eyeball_radius * eyeball_scale
                    if min(dist_to_eye_l, dist_to_eye_r) < actual_eyeball_radius + 0.05:
                        return dist, FacialFeature.EYE

                # Check mouth
                dist_to_mouth = np.linalg.norm(p - mouth_pos)
                mouth_radius = 0.35  # Approximate mouth region
                if dist_to_mouth < mouth_radius:
                    return dist, FacialFeature.MOUTH

            return dist, FacialFeature.SKIN

        return sdf_with_features


class CharacterHead(Head):
    """
    Extended head with character-specific features and presets.
    """

    def __init__(self, character_name: str = "default", **kwargs):
        """
        Initialize character head.

        Args:
            character_name: Name of character preset
            **kwargs: Passed to Head.__init__
        """
        geometry = self._get_character_geometry(character_name)
        super().__init__(geometry=geometry, **kwargs)
        self.character_name = character_name

    @property
    def default_voice(self) -> str:
        """
        Get the recommended default voice for this character.

        Returns:
            Voice name suitable for this character's personality
        """
        return self._get_character_voice(self.character_name)

    @staticmethod
    def _get_character_voice(name: str) -> str:
        """
        Get recommended voice for a character.

        Voice selections are based on character personality and appearance,
        matching vocal characteristics to visual design.

        Args:
            name: Character name

        Returns:
            Voice ID for edge-tts
        """
        voice_map = {
            # Original characters
            "default": "en-US-AriaNeural",  # Neutral, pleasant female voice
            "round": "en-AU-NatashaNeural",  # Warm, welcoming Australian voice
            "tall": "en-GB-RyanNeural",  # Deep, authoritative British voice
            "wide": "en-US-DavisNeural",  # Bold, confident male voice
            "robot": "en-US-GuyNeural",  # Deeper, more mechanical-sounding
            "cute": "en-US-JennyNeural",  # Higher-pitched, friendly voice
            # New characters (Stage 6)
            "alien": "en-US-TonyNeural",  # Serious, otherworldly tone
            "cat": "en-US-SaraNeural",  # Lighter, playful female voice
            "dog": "en-US-ChristopherNeural",  # Friendly, enthusiastic male
            "baby": "en-US-AnaNeural",  # Young-sounding, higher pitch
            "elder": "en-GB-LibbyNeural",  # Mature, experienced female voice
            "skull": "en-US-EricNeural",  # Deep, ominous male voice
        }
        return voice_map.get(name, "en-US-AriaNeural")

    @staticmethod
    def get_all_character_voices() -> dict:
        """
        Get all character-to-voice mappings.

        Returns:
            Dictionary mapping character names to default voices
        """
        return {
            "default": "en-US-AriaNeural",
            "round": "en-AU-NatashaNeural",
            "tall": "en-GB-RyanNeural",
            "wide": "en-US-DavisNeural",
            "robot": "en-US-GuyNeural",
            "cute": "en-US-JennyNeural",
            "alien": "en-US-TonyNeural",
            "cat": "en-US-SaraNeural",
            "dog": "en-US-ChristopherNeural",
            "baby": "en-US-AnaNeural",
            "elder": "en-GB-LibbyNeural",
            "skull": "en-US-EricNeural",
        }

    def _get_character_geometry(self, name: str) -> HeadGeometry:
        """Get geometry preset for a character."""
        presets = {
            "default": HeadGeometry(),
            "round": HeadGeometry(
                head_radii=(1.1, 1.1, 1.0),
                eye_separation=0.30,
                eye_height=0.20,
            ),
            "tall": HeadGeometry(
                head_radii=(0.9, 1.5, 0.9),
                eye_separation=0.30,
                eye_height=0.35,
                mouth_y=-0.45,
            ),
            "wide": HeadGeometry(
                head_radii=(1.2, 1.1, 0.9),
                eye_separation=0.45,
                eye_height=0.20,
            ),
            "robot": HeadGeometry(
                head_radii=(1.0, 1.0, 1.0),  # Perfect cube-like proportions
                eye_socket_radius=0.20,  # Rectangular "visor" eyes
                eyeball_radius=0.18,  # Glowing eyes (almost fill socket)
                eye_separation=0.50,  # Very wide-set, mechanical look
                eye_height=0.20,  # Eyes at precise mid-point
                mouth_y=-0.40,
                mouth_width_base=0.35,  # Wide speaker grille
                mouth_height_base=0.06,
                nose_length=0.02,  # Minimal nose (antenna)
                eye_socket_smooth=0.01,  # Hard edges (mechanical)
                mouth_smooth=0.01,  # Hard edges (mechanical)
                nose_smooth=0.01,
                eyeball_smooth=0.02,
            ),
            "cute": HeadGeometry(
                head_radii=(1.1, 1.0, 1.0),
                eye_socket_radius=0.25,
                eyeball_radius=0.18,
                eye_separation=0.30,
                eye_height=0.15,
                mouth_y=-0.25,
                mouth_height_base=0.05,
            ),
            # New character presets
            "alien": HeadGeometry(
                head_radii=(0.6, 2.0, 0.7),  # VERY elongated head (2x height!)
                eye_socket_radius=0.45,  # MASSIVE almond eyes (3x normal)
                eyeball_radius=0.38,  # Almost fills the socket
                pupil_radius=0.12,  # Larger pupil for more alien look
                eye_separation=0.50,  # Very wide set (side of head)
                eye_height=0.40,  # High on the head
                eye_depth=0.80,  # Slightly recessed
                mouth_y=-0.70,  # Very low, tiny mouth
                mouth_height_base=0.03,  # Tiny slit mouth
                mouth_width_base=0.15,  # Narrow
                nose_length=0.02,  # Almost no nose
                nose_width=0.06,
                eye_socket_smooth=0.18,  # Very smooth, organic
            ),
            "cat": HeadGeometry(
                head_radii=(1.0, 1.1, 1.0),
                eye_socket_radius=0.20,
                eyeball_radius=0.12,  # Slit pupils (smaller eyeballs)
                eye_separation=0.35,
                eye_height=0.20,
                mouth_y=-0.20,
                mouth_height_base=0.04,
                nose_length=0.08,  # Triangular nose
            ),
            "dog": HeadGeometry(
                head_radii=(1.1, 1.2, 1.1),  # Slightly extended
                eye_socket_radius=0.22,
                eyeball_radius=0.14,
                eye_separation=0.38,
                eye_height=0.25,
                mouth_y=-0.30,
                mouth_height_base=0.08,
                nose_length=0.15,  # Extended snout
            ),
            "baby": HeadGeometry(
                head_radii=(1.3, 1.3, 1.3),  # Perfect sphere! (baby head)
                eye_socket_radius=0.35,  # GIGANTIC eyes (kawaii!)
                eyeball_radius=0.28,  # Huge adorable eyes
                pupil_radius=0.08,  # Big pupils
                eye_separation=0.28,  # Close together (cute)
                eye_height=0.40,  # Very high on head (baby proportions)
                eye_depth=0.90,  # Protruding eyes
                mouth_y=-0.10,  # Very high mouth (baby face)
                mouth_height_base=0.03,  # Tiny O mouth
                mouth_width_base=0.12,  # Small
                nose_length=0.05,  # Button nose
                nose_width=0.10,  # Wide button nose
                eye_socket_smooth=0.15,  # Soft, baby-like
                mouth_smooth=0.15,
                nose_smooth=0.12,
            ),
            "elder": HeadGeometry(
                head_radii=(0.9, 1.4, 0.9),  # Thinner face
                eye_socket_radius=0.18,  # Smaller eyes
                eyeball_radius=0.10,
                eye_separation=0.35,
                eye_height=0.20,  # Eyes lower
                mouth_y=-0.35,  # Mouth droops
                mouth_height_base=0.06,
                nose_length=0.20,  # Prominent nose
            ),
            "skull": HeadGeometry(
                head_radii=(1.0, 1.3, 0.9),
                eye_socket_radius=0.30,  # Large eye sockets
                eyeball_radius=0.01,  # No visible eyeballs
                eye_separation=0.35,
                eye_height=0.25,
                mouth_y=-0.30,
                mouth_height_base=0.10,  # Wide mouth cavity
                nose_length=0.10,
                eye_socket_smooth=0.08,
                mouth_smooth=0.05,
            ),
            "monster": HeadGeometry(
                head_radii=(1.3, 1.0, 1.2),  # Wide, squat head
                eye_socket_radius=0.22,
                eyeball_radius=0.16,
                pupil_radius=0.04,  # Tiny pupils (creepy)
                eye_separation=0.55,  # Eyes on sides of head
                eye_height=0.15,  # Low-set eyes
                eye_depth=0.75,  # Eyes stick out
                mouth_y=-0.40,
                mouth_height_base=0.15,  # HUGE gaping maw
                mouth_width_base=0.40,  # Very wide
                nose_length=0.18,  # Large nose
                nose_width=0.18,  # Bulbous
                eye_socket_smooth=0.08,
                mouth_smooth=0.10,  # Toothy grin
            ),
            "cyclops": HeadGeometry(
                head_radii=(1.1, 1.2, 1.0),  # Normal-ish head
                eye_socket_radius=0.40,  # ONE GIANT EYE
                eyeball_radius=0.35,  # Massive single eyeball
                pupil_radius=0.10,  # Large pupil
                eye_separation=0.0,  # ZERO separation = one eye!
                eye_height=0.25,  # Centered eye
                eye_depth=0.90,  # Bulging eye
                mouth_y=-0.40,
                mouth_height_base=0.08,
                mouth_width_base=0.25,
                nose_length=0.12,  # Normal nose below eye
                nose_width=0.12,
                eye_socket_smooth=0.12,
            ),
            "fish": HeadGeometry(
                head_radii=(0.8, 1.0, 1.3),  # Deep from front-to-back
                eye_socket_radius=0.18,
                eyeball_radius=0.14,
                pupil_radius=0.06,
                eye_separation=0.60,  # Eyes on SIDES (fish)
                eye_height=0.30,  # Mid-height
                eye_depth=0.60,  # Eyes stick out to sides
                mouth_y=-0.25,
                mouth_height_base=0.12,  # Wide fish mouth
                mouth_width_base=0.40,  # Very wide "O" mouth
                nose_length=0.05,  # Minimal nose
                nose_width=0.08,
                eye_socket_smooth=0.08,
                mouth_smooth=0.18,  # Smooth fish mouth
            ),
            "square": HeadGeometry(
                head_radii=(1.0, 1.0, 1.0),  # Box head (like robot but different)
                eye_socket_radius=0.15,
                eyeball_radius=0.12,
                pupil_radius=0.04,
                eye_separation=0.40,
                eye_height=0.25,
                mouth_y=-0.35,
                mouth_height_base=0.06,
                mouth_width_base=0.30,
                nose_length=0.08,
                nose_width=0.08,
                eye_socket_smooth=0.03,  # Hard, angular edges
                mouth_smooth=0.03,
                nose_smooth=0.03,
                eyeball_smooth=0.03,
            ),
        }
        return presets.get(name, HeadGeometry())


def create_simple_head_sdf(
    mouth_openness: float = 0.0,
    blink: float = 0.0,
    time: float = 0.0,
) -> Callable[[Vec3], float]:
    """
    Create a simple head SDF without the full Head class.

    Useful for quick testing and examples.

    Args:
        mouth_openness: Mouth open amount (0-1)
        blink: Eye blink amount (0-1)
        time: Time for organic animation

    Returns:
        SDF function
    """
    # Add organic movement
    offset = organic_noise(time)

    def head_sdf(point: Vec3) -> float:
        p = _to_array(point)
        p = p - np.array(offset)

        # Main head
        head = sdf_ellipsoid(p, (0, 0, 0), (1.0, 1.3, 1.0))

        # Eye sockets
        eye_l = sdf_sphere(p, (-0.35, 0.25, 0.85), 0.18)
        eye_r = sdf_sphere(p, (0.35, 0.25, 0.85), 0.18)

        result = sdf_smooth_subtraction(eye_l, head, 0.1)
        result = sdf_smooth_subtraction(eye_r, result, 0.1)

        # Eyeballs
        eye_scale = 0.12 * (1 - blink * 0.8)
        if eye_scale > 0.02:
            eyeball_l = sdf_sphere(p, (-0.35, 0.25, 0.95), eye_scale)
            eyeball_r = sdf_sphere(p, (0.35, 0.25, 0.95), eye_scale)
            result = sdf_smooth_union(eyeball_l, result, 0.05)
            result = sdf_smooth_union(eyeball_r, result, 0.05)

        # Mouth
        mouth_height = 0.08 + mouth_openness * 0.25
        mouth = sdf_ellipsoid(p, (0, -0.35, 0.9), (0.25, mouth_height, 0.15))
        result = sdf_smooth_subtraction(mouth, result, 0.12)

        return result

    return head_sdf
