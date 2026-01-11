"""Tests for head model, geometry, and state."""

import time

import numpy as np
import pytest

from src.model.head import (
    CharacterHead,
    Head,
    HeadGeometry,
    HeadState,
    create_simple_head_sdf,
)


class TestHeadState:
    """Tests for HeadState dataclass."""

    def test_head_state_creation(self):
        """HeadState can be created with defaults."""
        state = HeadState()
        assert state.mouth_openness == 0.05
        assert state.mouth_width == 0.5
        assert state.lip_pucker == 0.0
        assert state.blink_amount == 0.0
        assert state.eye_look_x == 0.0
        assert state.eye_look_y == 0.0

    def test_head_state_custom_values(self):
        """HeadState accepts custom values."""
        state = HeadState(
            mouth_openness=0.8,
            mouth_width=0.7,
            blink_amount=0.5,
            eye_look_x=-0.3,
            eye_look_y=0.4,
            head_tilt_x=0.1,
            head_tilt_y=-0.2,
            head_tilt_z=0.15,
        )
        assert state.mouth_openness == 0.8
        assert state.blink_amount == 0.5
        assert state.head_tilt_x == 0.1
        assert state.head_tilt_y == -0.2

    def test_head_state_idle_offset(self):
        """HeadState stores idle animation offset."""
        state = HeadState(idle_offset=(0.01, -0.02, 0.03))
        assert state.idle_offset == (0.01, -0.02, 0.03)


class TestHeadGeometry:
    """Tests for HeadGeometry dataclass."""

    def test_head_geometry_defaults(self):
        """HeadGeometry has sensible defaults."""
        geom = HeadGeometry()
        assert geom.head_radii == (1.0, 1.3, 1.0)
        assert geom.eye_socket_radius == 0.18
        assert geom.eyeball_radius == 0.12
        assert geom.eye_separation == 0.35
        assert geom.mouth_y == -0.35

    def test_head_geometry_custom(self):
        """HeadGeometry accepts custom values."""
        geom = HeadGeometry(
            head_radii=(1.5, 1.5, 1.2),
            eye_socket_radius=0.25,
            eyeball_radius=0.15,
            eye_separation=0.40,
            mouth_y=-0.40,
        )
        assert geom.head_radii == (1.5, 1.5, 1.2)
        assert geom.eye_socket_radius == 0.25
        assert geom.mouth_y == -0.40

    def test_head_geometry_smoothing_factors(self):
        """HeadGeometry includes SDF smoothing factors."""
        geom = HeadGeometry()
        assert geom.eye_socket_smooth == 0.1
        assert geom.eyeball_smooth == 0.05
        assert geom.mouth_smooth == 0.12
        assert geom.nose_smooth == 0.08


class TestHeadInitialization:
    """Tests for Head class initialization."""

    def test_head_default_initialization(self):
        """Head initializes with defaults."""
        head = Head()
        assert isinstance(head.geometry, HeadGeometry)
        assert isinstance(head.state, HeadState)
        assert head.enable_idle_animation is True
        assert head.enable_expressions is True
        assert head.enable_gestures is False
        assert head.expression_manager is not None
        assert head.gesture_controller is None

    def test_head_custom_geometry(self):
        """Head accepts custom geometry."""
        custom_geom = HeadGeometry(head_radii=(2.0, 2.0, 2.0))
        head = Head(geometry=custom_geom)
        assert head.geometry.head_radii == (2.0, 2.0, 2.0)

    def test_head_disable_idle_animation(self):
        """Head can disable idle animation."""
        head = Head(enable_idle_animation=False)
        assert head.enable_idle_animation is False

    def test_head_disable_expressions(self):
        """Head can disable expressions."""
        head = Head(enable_expressions=False)
        assert head.enable_expressions is False
        assert head.expression_manager is None

    def test_head_enable_gestures(self):
        """Head can enable gestures."""
        head = Head(enable_gestures=True)
        assert head.enable_gestures is True
        assert head.gesture_controller is not None


class TestHeadStateSetters:
    """Tests for Head state setter methods."""

    def test_set_mouth(self):
        """set_mouth updates mouth parameters."""
        head = Head()
        head.set_mouth(openness=0.8, width=0.7, pucker=0.3)
        assert head.state.mouth_openness == 0.8
        assert head.state.mouth_width == 0.7
        assert head.state.lip_pucker == 0.3

    def test_set_mouth_clamping(self):
        """set_mouth clamps values to valid range."""
        head = Head()
        head.set_mouth(openness=1.5, width=-0.2, pucker=2.0)
        assert head.state.mouth_openness == 1.0  # Clamped to max
        assert head.state.mouth_width == 0.0  # Clamped to min
        assert head.state.lip_pucker == 1.0  # Clamped to max

    def test_set_blink(self):
        """set_blink updates blink amount."""
        head = Head()
        head.set_blink(0.6)
        assert head.state.blink_amount == 0.6

    def test_set_blink_clamping(self):
        """set_blink clamps to [0, 1]."""
        head = Head()
        head.set_blink(1.5)
        assert head.state.blink_amount == 1.0
        head.set_blink(-0.5)
        assert head.state.blink_amount == 0.0

    def test_set_eye_look(self):
        """set_eye_look updates eye direction."""
        head = Head()
        head.set_eye_look(0.5, -0.3)
        assert head.state.eye_look_x == 0.5
        assert head.state.eye_look_y == -0.3

    def test_set_eye_look_clamping(self):
        """set_eye_look clamps to [-1, 1]."""
        head = Head()
        head.set_eye_look(2.0, -1.5)
        assert head.state.eye_look_x == 1.0
        assert head.state.eye_look_y == -1.0

    def test_set_head_tilt(self):
        """set_head_tilt updates head orientation."""
        head = Head()
        head.set_head_tilt(x=0.2, y=-0.1, z=0.15)
        assert head.state.head_tilt_x == 0.2
        assert head.state.head_tilt_y == -0.1
        assert head.state.head_tilt_z == 0.15


class TestHeadExpressions:
    """Tests for Head expression system integration."""

    def test_set_expression(self):
        """set_expression triggers expression transition."""
        head = Head(enable_expressions=True)
        head.set_expression("happy")
        assert head.expression_manager.target_expression.name == "happy"
        assert head.expression_manager.is_transitioning

    def test_set_expression_with_duration(self):
        """set_expression accepts custom duration."""
        head = Head(enable_expressions=True)
        head.set_expression("sad", duration=2.0)
        assert head.expression_manager.transition_duration == 2.0

    def test_set_expression_when_disabled(self):
        """set_expression does nothing when expressions disabled."""
        head = Head(enable_expressions=False)
        head.set_expression("happy")  # Should not raise error

    def test_get_current_expression(self):
        """get_current_expression returns current expression name."""
        head = Head(enable_expressions=True)
        assert head.get_current_expression() == "neutral"

        head.set_expression("happy", duration=0.05)
        time.sleep(0.1)
        head.update(0.1)
        assert head.get_current_expression() == "happy"

    def test_get_current_expression_when_disabled(self):
        """get_current_expression returns None when disabled."""
        head = Head(enable_expressions=False)
        assert head.get_current_expression() is None

    def test_list_expressions(self):
        """list_expressions returns available expressions."""
        head = Head(enable_expressions=True)
        expressions = head.list_expressions()
        assert "neutral" in expressions
        assert "happy" in expressions
        assert "sad" in expressions
        assert len(expressions) >= 9

    def test_list_expressions_when_disabled(self):
        """list_expressions returns empty list when disabled."""
        head = Head(enable_expressions=False)
        assert head.list_expressions() == []


class TestHeadUpdate:
    """Tests for Head update method."""

    def test_update_increments_time(self):
        """update() increments internal time."""
        head = Head()
        initial_time = head._time
        head.update(0.1)
        assert head._time == initial_time + 0.1

    def test_update_with_expressions(self):
        """update() processes expression transitions."""
        head = Head(enable_expressions=True)
        head.set_expression("happy", duration=0.05)
        head.update(0.1)
        # Expression should be applied to state
        assert head.state.smile_amount > 0.0

    def test_update_with_idle_animation(self):
        """update() applies idle animation."""
        head = Head(enable_idle_animation=True)
        head.update(0.1)
        # Idle offset should be set
        assert head.state.idle_offset != (0.0, 0.0, 0.0)

    def test_update_without_idle_animation(self):
        """update() skips idle animation when disabled."""
        head = Head(enable_idle_animation=False)
        head.update(0.1)
        # Idle offset should remain default
        assert head.state.idle_offset == (0.0, 0.0, 0.0)


class TestHeadRotation:
    """Tests for head rotation math."""

    def test_rotate_point_identity(self):
        """Rotation with zero tilt returns original point."""
        head = Head()
        p = np.array([1.0, 2.0, 3.0])
        result = head._rotate_point(p)
        np.testing.assert_array_almost_equal(result, p)

    def test_rotate_point_x_axis(self):
        """Rotation around X axis (nod)."""
        head = Head()
        head.set_head_tilt(x=np.pi / 2)  # 90 degree nod
        p = np.array([0.0, 1.0, 0.0])
        result = head._rotate_point(p)
        # Y should rotate to Z
        np.testing.assert_array_almost_equal(result, [0.0, 0.0, 1.0], decimal=5)

    def test_rotate_point_y_axis(self):
        """Rotation around Y axis (turn)."""
        head = Head()
        head.set_head_tilt(y=np.pi / 2)  # 90 degree turn
        p = np.array([1.0, 0.0, 0.0])
        result = head._rotate_point(p)
        # X should rotate to -Z
        np.testing.assert_array_almost_equal(result, [0.0, 0.0, -1.0], decimal=5)

    def test_rotate_point_z_axis(self):
        """Rotation around Z axis (lean)."""
        head = Head()
        head.set_head_tilt(z=np.pi / 2)  # 90 degree lean
        p = np.array([1.0, 0.0, 0.0])
        result = head._rotate_point(p)
        # X should rotate to Y
        np.testing.assert_array_almost_equal(result, [0.0, 1.0, 0.0], decimal=5)


class TestHeadSDF:
    """Tests for Head SDF generation."""

    def test_get_sdf_returns_callable(self):
        """get_sdf() returns callable function."""
        head = Head()
        sdf = head.get_sdf()
        assert callable(sdf)

    def test_sdf_function_works(self):
        """SDF function accepts point and returns distance."""
        head = Head()
        sdf = head.get_sdf()
        # Test point far from head center
        distance = sdf((5.0, 0.0, 0.0))
        assert isinstance(distance, float)
        assert distance > 0  # Outside the head

    def test_sdf_at_origin(self):
        """SDF at origin should be negative (inside head)."""
        head = Head()
        sdf = head.get_sdf()
        distance = sdf((0.0, 0.0, 0.0))
        assert distance < 0  # Inside the head

    def test_get_sdf_with_pupils_returns_callable(self):
        """get_sdf_with_pupils() returns callable."""
        head = Head()
        sdf_pupils = head.get_sdf_with_pupils()
        assert callable(sdf_pupils)

    def test_sdf_with_pupils_returns_tuple(self):
        """SDF with pupils returns (distance, is_pupil)."""
        head = Head()
        sdf_pupils = head.get_sdf_with_pupils()
        distance, is_pupil = sdf_pupils((0.0, 0.0, 0.0))
        assert isinstance(distance, float)
        # is_pupil can be numpy bool or Python bool
        assert isinstance(is_pupil, (bool, np.bool_))


class TestCharacterHead:
    """Tests for CharacterHead presets."""

    def test_character_head_default(self):
        """CharacterHead initializes with default character."""
        head = CharacterHead()
        assert head.character_name == "default"
        assert isinstance(head.geometry, HeadGeometry)

    def test_all_character_presets_exist(self):
        """All character presets can be instantiated."""
        characters = [
            "default",
            "round",
            "tall",
            "wide",
            "robot",
            "cute",
            "alien",
            "cat",
            "dog",
            "baby",
            "elder",
            "skull",
        ]
        for char_name in characters:
            head = CharacterHead(char_name)
            assert head.character_name == char_name
            assert isinstance(head.geometry, HeadGeometry)

    def test_character_geometry_differs(self):
        """Different characters have different geometry."""
        default = CharacterHead("default")
        tall = CharacterHead("tall")
        round_head = CharacterHead("round")

        # Tall should have taller head radii
        assert tall.geometry.head_radii[1] > default.geometry.head_radii[1]

        # Round should have more uniform radii
        assert abs(round_head.geometry.head_radii[0] - round_head.geometry.head_radii[1]) < 0.2

    def test_robot_character_less_smooth(self):
        """Robot character has sharper edges."""
        robot = CharacterHead("robot")
        default = CharacterHead("default")
        # Robot should have less smoothing
        assert robot.geometry.eye_socket_smooth < default.geometry.eye_socket_smooth
        assert robot.geometry.mouth_smooth < default.geometry.mouth_smooth

    def test_baby_character_large_eyes(self):
        """Baby character has proportionally large eyes."""
        baby = CharacterHead("baby")
        default = CharacterHead("default")
        assert baby.geometry.eye_socket_radius > default.geometry.eye_socket_radius
        assert baby.geometry.eyeball_radius > default.geometry.eyeball_radius

    def test_unknown_character_uses_default(self):
        """Unknown character name falls back to default."""
        head = CharacterHead("nonexistent")
        default = CharacterHead("default")
        assert head.geometry.head_radii == default.geometry.head_radii


class TestCharacterVoices:
    """Tests for character voice mappings."""

    def test_default_voice_property(self):
        """default_voice property returns voice string."""
        head = CharacterHead("default")
        voice = head.default_voice
        assert isinstance(voice, str)
        assert "Neural" in voice

    def test_all_characters_have_voices(self):
        """All character presets have voice assignments."""
        characters = [
            "default",
            "round",
            "tall",
            "wide",
            "robot",
            "cute",
            "alien",
            "cat",
            "dog",
            "baby",
            "elder",
            "skull",
        ]
        for char_name in characters:
            head = CharacterHead(char_name)
            voice = head.default_voice
            assert isinstance(voice, str)
            assert len(voice) > 0
            assert "Neural" in voice

    def test_get_all_character_voices(self):
        """get_all_character_voices returns complete mapping."""
        voices = CharacterHead.get_all_character_voices()
        assert isinstance(voices, dict)
        assert len(voices) == 12
        assert "default" in voices
        assert "robot" in voices
        assert "skull" in voices

    def test_character_voices_unique(self):
        """Different characters have distinct voice personalities."""
        tall_voice = CharacterHead("tall").default_voice
        cute_voice = CharacterHead("cute").default_voice
        robot_voice = CharacterHead("robot").default_voice

        # These should be different to match character personalities
        assert tall_voice != cute_voice
        assert tall_voice != robot_voice

    def test_unknown_character_voice_fallback(self):
        """Unknown character gets default voice."""
        voice = CharacterHead._get_character_voice("nonexistent")
        default_voice = CharacterHead._get_character_voice("default")
        assert voice == default_voice


class TestSimpleHeadSDF:
    """Tests for create_simple_head_sdf utility."""

    def test_create_simple_head_sdf(self):
        """create_simple_head_sdf returns callable."""
        sdf = create_simple_head_sdf()
        assert callable(sdf)

    def test_simple_head_sdf_with_params(self):
        """create_simple_head_sdf accepts parameters."""
        sdf = create_simple_head_sdf(mouth_openness=0.8, blink=0.5, time=1.0)
        assert callable(sdf)

        # Test it works
        distance = sdf((0.0, 0.0, 0.0))
        assert isinstance(distance, float)

    def test_simple_head_sdf_evaluates(self):
        """Simple head SDF returns valid distances."""
        sdf = create_simple_head_sdf()

        # Inside head
        dist_inside = sdf((0.0, 0.0, 0.0))
        assert dist_inside < 0

        # Outside head
        dist_outside = sdf((5.0, 0.0, 0.0))
        assert dist_outside > 0
