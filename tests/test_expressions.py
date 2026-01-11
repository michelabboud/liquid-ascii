"""Tests for expression system."""

import time

import pytest

from src.model.expressions import (
    EXPRESSIONS,
    Expression,
    ExpressionManager,
    ease_in_out,
    lerp,
)


class TestLerpFunction:
    """Tests for linear interpolation."""

    def test_lerp_at_zero(self):
        """Lerp at t=0 should return start value."""
        assert lerp(10.0, 20.0, 0.0) == 10.0

    def test_lerp_at_one(self):
        """Lerp at t=1 should return end value."""
        assert lerp(10.0, 20.0, 1.0) == 20.0

    def test_lerp_at_half(self):
        """Lerp at t=0.5 should return midpoint."""
        assert lerp(10.0, 20.0, 0.5) == 15.0

    def test_lerp_negative_range(self):
        """Lerp should work with negative values."""
        assert lerp(-10.0, 10.0, 0.5) == 0.0


class TestEasingFunction:
    """Tests for easing function."""

    def test_ease_in_out_at_zero(self):
        """Ease in out at t=0 should return 0."""
        assert ease_in_out(0.0) == 0.0

    def test_ease_in_out_at_one(self):
        """Ease in out at t=1 should return 1."""
        assert ease_in_out(1.0) == 1.0

    def test_ease_in_out_at_half(self):
        """Ease in out at t=0.5 should return 0.5."""
        assert ease_in_out(0.5) == 0.5

    def test_ease_in_out_smooth(self):
        """Ease in out should be smooth (derivative continuous)."""
        # Check that values progress smoothly
        values = [ease_in_out(t / 10) for t in range(11)]
        # Should be monotonically increasing
        for i in range(len(values) - 1):
            assert values[i] <= values[i + 1]

    def test_ease_in_out_clamps(self):
        """Ease in out should clamp values outside [0,1]."""
        assert ease_in_out(-0.5) == 0.0
        assert ease_in_out(1.5) == 1.0


class TestExpressionDataclass:
    """Tests for Expression dataclass."""

    def test_expression_creation(self):
        """Expression can be created with all parameters."""
        expr = Expression(
            name="test",
            eyebrow_raise=0.5,
            eyebrow_asymmetry=0.2,
            smile_amount=0.8,
            mouth_width_mod=0.1,
            mouth_openness=0.3,
            lip_pucker=0.0,
            blink_amount=0.0,
            eye_asymmetry=0.0,
            eye_squint=0.1,
            eye_look_x=0.2,
            eye_look_y=-0.1,
            head_tilt=(0.1, 0.0, 0.0),
            intensity=1.0,
            duration=0.5,
        )
        assert expr.name == "test"
        assert expr.eyebrow_raise == 0.5
        assert expr.smile_amount == 0.8

    def test_expression_defaults(self):
        """Expression has sensible defaults."""
        expr = Expression(name="minimal")
        assert expr.eyebrow_raise == 0.0
        assert expr.smile_amount == 0.0
        assert expr.blink_amount == 0.0
        assert expr.head_tilt == (0.0, 0.0, 0.0)
        assert expr.intensity == 1.0


class TestExpressionPresets:
    """Tests for predefined expression library."""

    def test_all_presets_exist(self):
        """All expected presets are defined."""
        expected_presets = [
            "neutral",
            "happy",
            "sad",
            "angry",
            "surprised",
            "confused",
            "tired",
            "wink",
            "thinking",
            "excited",
            "skeptical",
        ]
        for preset in expected_presets:
            assert preset in EXPRESSIONS, f"Missing preset: {preset}"

    def test_neutral_expression(self):
        """Neutral expression has zero values."""
        neutral = EXPRESSIONS["neutral"]
        assert neutral.eyebrow_raise == 0.0
        assert neutral.smile_amount == 0.0
        assert neutral.blink_amount == 0.0

    def test_happy_expression(self):
        """Happy expression has positive smile."""
        happy = EXPRESSIONS["happy"]
        assert happy.smile_amount > 0.5
        assert happy.eyebrow_raise > 0.0

    def test_sad_expression(self):
        """Sad expression has negative smile."""
        sad = EXPRESSIONS["sad"]
        assert sad.smile_amount < 0.0
        assert sad.eyebrow_raise < 0.0

    def test_angry_expression(self):
        """Angry expression has furrowed brows."""
        angry = EXPRESSIONS["angry"]
        assert angry.eyebrow_raise < -0.5

    def test_surprised_expression(self):
        """Surprised expression has raised brows and open mouth."""
        surprised = EXPRESSIONS["surprised"]
        assert surprised.eyebrow_raise > 0.5
        assert surprised.mouth_openness > 0.3

    def test_wink_expression(self):
        """Wink has asymmetric eye closure."""
        wink = EXPRESSIONS["wink"]
        assert abs(wink.eye_asymmetry) > 0.5

    def test_all_presets_valid_ranges(self):
        """All preset values are in valid ranges."""
        for name, expr in EXPRESSIONS.items():
            # Most parameters should be in [-1, 1] range
            assert -1.5 <= expr.eyebrow_raise <= 1.5, f"{name}: eyebrow_raise out of range"
            assert -1.5 <= expr.smile_amount <= 1.5, f"{name}: smile_amount out of range"
            assert 0.0 <= expr.blink_amount <= 1.0, f"{name}: blink_amount out of range"
            assert 0.0 <= expr.mouth_openness <= 1.0, f"{name}: mouth_openness out of range"
            assert 0.0 <= expr.intensity <= 2.0, f"{name}: intensity out of range"


class TestExpressionManager:
    """Tests for ExpressionManager."""

    def test_manager_initialization(self):
        """Manager starts with neutral expression."""
        manager = ExpressionManager()
        assert manager.current_expression.name == "neutral"
        assert not manager.is_transitioning

    def test_set_expression(self):
        """Setting expression starts transition."""
        manager = ExpressionManager()
        manager.set_expression("happy")
        assert manager.target_expression.name == "happy"
        assert manager.is_transitioning

    def test_set_invalid_expression(self):
        """Setting invalid expression raises ValueError."""
        manager = ExpressionManager()
        with pytest.raises(ValueError):
            manager.set_expression("nonexistent")

    def test_set_expression_with_duration(self):
        """Can override default duration."""
        manager = ExpressionManager()
        manager.set_expression("happy", duration=2.0)
        assert manager.transition_duration == 2.0

    def test_transition_completes(self):
        """Transition completes after duration."""
        manager = ExpressionManager()
        manager.set_expression("happy", duration=0.1)

        # Immediately after setting, should be transitioning
        assert manager.is_transitioning

        # Wait for transition to complete
        time.sleep(0.15)
        result = manager.update()

        assert not manager.is_transitioning
        assert result.name == "happy"
        assert manager.current_expression.name == "happy"

    def test_transition_interpolates(self):
        """Expression interpolates during transition."""
        manager = ExpressionManager()
        neutral_smile = EXPRESSIONS["neutral"].smile_amount
        happy_smile = EXPRESSIONS["happy"].smile_amount

        manager.set_expression("happy", duration=1.0)

        # Check midpoint of transition
        time.sleep(0.5)
        result = manager.update()

        # Should be somewhere between neutral and happy
        # Not exact due to easing, but should be in range
        assert neutral_smile < result.smile_amount < happy_smile

    def test_update_when_not_transitioning(self):
        """Update returns current expression when not transitioning."""
        manager = ExpressionManager()
        result = manager.update()
        assert result.name == "neutral"
        assert result == manager.current_expression

    def test_blend_expressions(self):
        """Expression blending creates intermediate values."""
        manager = ExpressionManager()
        neutral = EXPRESSIONS["neutral"]
        happy = EXPRESSIONS["happy"]

        blended = manager._blend_expressions(neutral, happy, 0.5)

        # Blended values should be midpoint
        assert blended.smile_amount == (neutral.smile_amount + happy.smile_amount) / 2
        assert (
            blended.eyebrow_raise == (neutral.eyebrow_raise + happy.eyebrow_raise) / 2
        )

    def test_set_custom_expression(self):
        """Can set custom expression."""
        manager = ExpressionManager()
        custom = Expression(
            name="custom", smile_amount=0.5, eyebrow_raise=0.3, duration=0.5
        )
        manager.set_custom_expression(custom, duration=0.2)

        assert manager.target_expression.name == "custom"
        assert manager.transition_duration == 0.2

    def test_get_current_expression_name(self):
        """Can get current expression name."""
        manager = ExpressionManager()
        assert manager.get_current_expression_name() == "neutral"

        manager.set_expression("happy", duration=0.05)
        time.sleep(0.1)
        manager.update()

        assert manager.get_current_expression_name() == "happy"

    def test_list_expressions(self):
        """Can list all available expressions."""
        manager = ExpressionManager()
        expressions = manager.list_expressions()

        assert "neutral" in expressions
        assert "happy" in expressions
        assert "sad" in expressions
        assert len(expressions) >= 9

    def test_sequential_transitions(self):
        """Multiple sequential transitions work correctly."""
        manager = ExpressionManager()

        # Transition to happy
        manager.set_expression("happy", duration=0.05)
        time.sleep(0.1)
        manager.update()
        assert manager.get_current_expression_name() == "happy"

        # Transition to sad
        manager.set_expression("sad", duration=0.05)
        time.sleep(0.1)
        manager.update()
        assert manager.get_current_expression_name() == "sad"

    def test_transition_preserves_head_tilt(self):
        """Head tilt is interpolated during transition."""
        manager = ExpressionManager()
        neutral_tilt = EXPRESSIONS["neutral"].head_tilt
        sad_tilt = EXPRESSIONS["sad"].head_tilt

        manager.set_expression("sad", duration=0.1)
        time.sleep(0.05)
        result = manager.update()

        # Should interpolate head tilt
        assert result.head_tilt != neutral_tilt
        # Allow some tolerance for timing
        assert isinstance(result.head_tilt, tuple)
        assert len(result.head_tilt) == 3
