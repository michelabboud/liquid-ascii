"""Tests for animation system."""

import sys

import pytest

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from src.model.animation import (
    AnimationController,
    blink_pattern,
    ease_in,
    ease_in_out,
    ease_out,
    lerp,
    organic_noise,
    smootherstep,
    smoothstep,
)


class TestEasingFunctions:
    """Test easing/interpolation functions."""

    def test_smoothstep_bounds(self):
        """Smoothstep should return 0 at t=0 and 1 at t=1."""
        assert smoothstep(0) == 0
        assert smoothstep(1) == 1

    def test_smoothstep_middle(self):
        """Smoothstep at t=0.5 should return 0.5."""
        assert smoothstep(0.5) == 0.5

    def test_smoothstep_clamp(self):
        """Smoothstep should clamp values outside [0,1]."""
        assert smoothstep(-1) == 0
        assert smoothstep(2) == 1

    def test_smootherstep_bounds(self):
        """Smootherstep should return 0 at t=0 and 1 at t=1."""
        assert smootherstep(0) == 0
        assert smootherstep(1) == 1

    def test_lerp(self):
        """Linear interpolation test."""
        assert lerp(0, 10, 0) == 0
        assert lerp(0, 10, 1) == 10
        assert lerp(0, 10, 0.5) == 5

    def test_ease_in(self):
        """Ease in starts slow."""
        # At t=0.5, ease_in should be less than 0.5
        assert ease_in(0.5) < 0.5

    def test_ease_out(self):
        """Ease out ends slow."""
        # At t=0.5, ease_out should be greater than 0.5
        assert ease_out(0.5) > 0.5

    def test_ease_in_out_symmetric(self):
        """Ease in-out should be symmetric around 0.5."""
        assert ease_in_out(0) == 0
        assert ease_in_out(1) == 1
        assert ease_in_out(0.5) == pytest.approx(0.5, abs=0.01)


class TestOrganicNoise:
    """Test organic noise generation."""

    def test_noise_returns_tuple(self):
        """Organic noise should return 3D offset."""
        result = organic_noise(0)
        assert len(result) == 3

    def test_noise_varies(self):
        """Noise should vary over time."""
        noise0 = organic_noise(0)
        noise1 = organic_noise(1)
        # At least one component should differ
        assert any(abs(a - b) > 0.001 for a, b in zip(noise0, noise1))

    def test_noise_bounded(self):
        """Noise should be small values."""
        for t in range(100):
            noise = organic_noise(t * 0.1)
            for component in noise:
                assert abs(component) < 0.1


class TestBlinkPattern:
    """Test blink animation pattern."""

    def test_blink_mostly_open(self):
        """Eyes should be open most of the time."""
        open_count = 0
        total = 100
        for i in range(total):
            t = i * 0.05  # 5 seconds of samples
            if blink_pattern(t) < 0.1:
                open_count += 1
        # Should be open at least 80% of time
        assert open_count / total > 0.8

    def test_blink_does_close(self):
        """Eyes should blink (close) sometimes."""
        found_blink = False
        for i in range(100):
            t = i * 0.05
            if blink_pattern(t) > 0.5:
                found_blink = True
                break
        assert found_blink


class TestAnimationController:
    """Test animation controller."""

    def test_set_value(self):
        """Setting a value should work."""
        controller = AnimationController()
        controller.set_value("test", 1.0)
        assert controller.get_value("test") == 1.0

    def test_get_default(self):
        """Getting unset value should return default."""
        controller = AnimationController()
        assert controller.get_value("unset", 5.0) == 5.0

    def test_animate_to(self):
        """Animation should interpolate over time."""
        controller = AnimationController()
        controller.set_value("x", 0.0)
        controller.animate_to("x", 1.0, duration=0.1)

        # Should be animating
        assert controller.is_animating("x")

    def test_update(self):
        """Update should return all values."""
        controller = AnimationController()
        controller.set_value("a", 1.0)
        controller.set_value("b", 2.0)

        values = controller.update()
        assert "a" in values
        assert "b" in values


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
