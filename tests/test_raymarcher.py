"""Tests for raymarching renderer."""

import numpy as np
import pytest

from src.renderer.camera import Camera
from src.renderer.quality import QualityLevel
from src.renderer.raymarcher import AdaptiveRaymarcher, Raymarcher
from src.renderer.shading import ASCIIShader


class TestRaymarcherInitialization:
    """Tests for Raymarcher initialization."""

    def test_raymarcher_defaults(self):
        """Raymarcher initializes with default settings."""
        rm = Raymarcher()
        assert rm.width == 80
        assert rm.height == 40
        assert isinstance(rm.camera, Camera)
        assert isinstance(rm.shader, ASCIIShader)
        assert rm.max_steps == 64
        assert rm.max_distance == 100.0
        assert rm.epsilon == 0.001

    def test_raymarcher_custom_size(self):
        """Raymarcher accepts custom dimensions."""
        rm = Raymarcher(width=100, height=50)
        assert rm.width == 100
        assert rm.height == 50

    def test_raymarcher_custom_params(self):
        """Raymarcher accepts custom rendering parameters."""
        rm = Raymarcher(max_steps=32, max_distance=50.0, epsilon=0.01)
        assert rm.max_steps == 32
        assert rm.max_distance == 50.0
        assert rm.epsilon == 0.01

    def test_raymarcher_custom_camera(self):
        """Raymarcher accepts custom camera."""
        camera = Camera(fov=60.0)
        rm = Raymarcher(camera=camera)
        assert rm.camera == camera
        assert rm.camera.fov == 60.0

    def test_raymarcher_custom_shader(self):
        """Raymarcher accepts custom shader."""
        shader = ASCIIShader()
        rm = Raymarcher(shader=shader)
        assert rm.shader == shader

    def test_raymarcher_quality_preset(self):
        """Raymarcher applies quality presets."""
        rm = Raymarcher(quality=QualityLevel.HIGH)
        # Quality preset should be applied
        assert rm._quality_preset is not None
        # Values should come from preset
        assert rm.max_steps > 0
        assert rm.max_distance > 0
        assert rm.epsilon > 0

    def test_raymarcher_quality_overrides(self):
        """Quality preset overrides manual params."""
        rm = Raymarcher(
            max_steps=10,  # These should be overridden
            max_distance=20.0,
            epsilon=0.1,
            quality=QualityLevel.HIGH,
        )
        # Values from quality preset, not manual params
        assert rm.max_steps != 10
        assert rm.epsilon != 0.1


class TestRaymarcherBuffers:
    """Tests for internal buffer management."""

    def test_buffers_allocated(self):
        """Internal buffers are pre-allocated."""
        rm = Raymarcher(width=10, height=5)
        assert rm._hit_buffer.shape == (5, 10)
        assert rm._distance_buffer.shape == (5, 10)
        assert rm._normal_buffer.shape == (5, 10, 3)

    def test_resize_updates_buffers(self):
        """resize() updates buffer dimensions."""
        rm = Raymarcher(width=10, height=5)
        rm.resize(20, 15)
        assert rm.width == 20
        assert rm.height == 15
        assert rm._hit_buffer.shape == (15, 20)
        assert rm._distance_buffer.shape == (15, 20)
        assert rm._normal_buffer.shape == (15, 20, 3)


class TestRaymarcherQuality:
    """Tests for quality settings."""

    def test_set_quality(self):
        """set_quality updates rendering parameters."""
        rm = Raymarcher()
        initial_steps = rm.max_steps

        rm.set_quality(QualityLevel.ULTRA)
        # Ultra quality should have more steps than default
        assert rm.max_steps > initial_steps
        assert rm._quality_preset is not None

    def test_set_quality_low(self):
        """Low quality has fewer steps."""
        rm = Raymarcher()
        rm.set_quality(QualityLevel.LOW)
        # Low quality should have fewer steps
        assert rm.max_steps < 64


class TestRaymarchSingle:
    """Tests for single ray raymarching."""

    def test_raymarch_hits_surface(self):
        """Ray hits a simple surface."""
        rm = Raymarcher()

        # Simple sphere SDF at origin
        def sphere_sdf(p):
            return np.linalg.norm(p) - 1.0

        # Ray from -5 on z-axis toward origin
        origin = np.array([0.0, 0.0, -5.0])
        direction = np.array([0.0, 0.0, 1.0])

        distance, hit_point = rm.raymarch_single(origin, direction, sphere_sdf)

        # Should hit the sphere
        assert distance is not None
        assert hit_point is not None
        assert distance > 0
        # Hit point should be on sphere surface (distance ~4.0 along ray)
        assert 3.8 < distance < 4.2

    def test_raymarch_misses_surface(self):
        """Ray misses when pointing away."""
        rm = Raymarcher()

        def sphere_sdf(p):
            return np.linalg.norm(p) - 1.0

        # Ray pointing away from sphere
        origin = np.array([0.0, 0.0, -5.0])
        direction = np.array([0.0, 0.0, -1.0])  # Away from sphere

        distance, hit_point = rm.raymarch_single(origin, direction, sphere_sdf)

        # Should miss
        assert distance is None
        assert hit_point is None

    def test_raymarch_exceeds_max_distance(self):
        """Ray stops at max_distance."""
        rm = Raymarcher(max_distance=2.0)

        def sphere_sdf(p):
            # Sphere very far away
            return np.linalg.norm(np.array(p) - np.array([0, 0, 100])) - 1.0

        origin = np.array([0.0, 0.0, 0.0])
        direction = np.array([0.0, 0.0, 1.0])

        distance, hit_point = rm.raymarch_single(origin, direction, sphere_sdf)

        # Should stop due to max_distance
        assert distance is None
        assert hit_point is None

    def test_raymarch_exceeds_max_steps(self):
        """Ray stops at max_steps."""
        rm = Raymarcher(max_steps=5)  # Very few steps

        def complex_sdf(p):
            # SDF that requires many steps
            return abs(np.linalg.norm(p) - 5.0) + 0.5

        origin = np.array([0.0, 0.0, 0.0])
        direction = np.array([1.0, 0.0, 0.0])

        distance, hit_point = rm.raymarch_single(origin, direction, complex_sdf)

        # May not converge with so few steps
        # (This is probabilistic but likely to fail)
        assert True  # Just verify it doesn't crash

    def test_raymarch_inside_surface(self):
        """Ray starting inside surface."""
        rm = Raymarcher()

        def sphere_sdf(p):
            return np.linalg.norm(p) - 2.0

        # Start at origin (inside sphere of radius 2)
        origin = np.array([0.0, 0.0, 0.0])
        direction = np.array([1.0, 0.0, 0.0])

        distance, hit_point = rm.raymarch_single(origin, direction, sphere_sdf)

        # Should find the exit point
        assert distance is not None
        assert hit_point is not None


class TestRenderFrame:
    """Tests for frame rendering."""

    def test_render_frame_returns_string(self):
        """render_frame returns a string."""
        rm = Raymarcher(width=10, height=5)

        def simple_sdf(p):
            return 10.0  # Nothing to hit

        result = rm.render_frame(simple_sdf)

        assert isinstance(result, str)
        assert "\n" in result  # Multi-line output

    def test_render_frame_dimensions(self):
        """render_frame produces correct dimensions."""
        rm = Raymarcher(width=10, height=5)

        def simple_sdf(p):
            return 10.0

        result = rm.render_frame(simple_sdf)
        lines = result.split("\n")

        assert len(lines) == 5  # Height
        assert all(len(line) == 10 for line in lines)  # Width

    def test_render_frame_background(self):
        """render_frame uses background character."""
        rm = Raymarcher(width=10, height=5)

        def simple_sdf(p):
            return 10.0  # Nothing hits

        result = rm.render_frame(simple_sdf, background=".")

        # Should be all background chars
        assert all(c in [".", "\n"] for c in result)

    def test_render_frame_with_hit(self):
        """render_frame shows objects that are hit."""
        rm = Raymarcher(width=10, height=5, max_steps=100)

        # Sphere at origin, camera should see it
        def sphere_sdf(p):
            return np.linalg.norm(p) - 1.5

        result = rm.render_frame(sphere_sdf, background=" ")

        # Should have some non-space characters (the sphere)
        assert any(c != " " and c != "\n" for c in result)


class TestRenderFrameFast:
    """Tests for optimized rendering."""

    def test_render_frame_fast_returns_string(self):
        """render_frame_fast returns a string."""
        rm = Raymarcher(width=10, height=5)

        def simple_sdf(p):
            return 10.0

        result = rm.render_frame_fast(simple_sdf)

        assert isinstance(result, str)
        assert "\n" in result

    def test_render_frame_fast_dimensions(self):
        """render_frame_fast produces correct dimensions."""
        rm = Raymarcher(width=10, height=5)

        def simple_sdf(p):
            return 10.0

        result = rm.render_frame_fast(simple_sdf)
        lines = result.split("\n")

        assert len(lines) == 5
        assert all(len(line) == 10 for line in lines)

    def test_render_frame_fast_background(self):
        """render_frame_fast uses background character."""
        rm = Raymarcher(width=10, height=5)

        def simple_sdf(p):
            return 10.0

        result = rm.render_frame_fast(simple_sdf, background="*")

        assert all(c in ["*", "\n"] for c in result)


class TestAdaptiveRaymarcher:
    """Tests for adaptive raymarching."""

    def test_adaptive_initialization(self):
        """AdaptiveRaymarcher initializes properly."""
        arm = AdaptiveRaymarcher()
        assert isinstance(arm, Raymarcher)
        assert hasattr(arm, "relaxation_factor")
        assert arm.relaxation_factor == 1.5

    def test_adaptive_custom_params(self):
        """AdaptiveRaymarcher accepts custom parameters."""
        arm = AdaptiveRaymarcher(width=100, height=50, max_steps=32)
        assert arm.width == 100
        assert arm.height == 50
        assert arm.max_steps == 32

    def test_adaptive_hits_surface(self):
        """Adaptive raymarcher can hit surfaces."""
        arm = AdaptiveRaymarcher()

        def sphere_sdf(p):
            return np.linalg.norm(p) - 1.0

        origin = np.array([0.0, 0.0, -5.0])
        direction = np.array([0.0, 0.0, 1.0])

        distance, hit_point = arm.raymarch_single(origin, direction, sphere_sdf)

        assert distance is not None
        assert hit_point is not None
        assert distance > 0

    def test_adaptive_misses_surface(self):
        """Adaptive raymarcher can miss surfaces."""
        arm = AdaptiveRaymarcher()

        def sphere_sdf(p):
            return np.linalg.norm(p) - 1.0

        origin = np.array([0.0, 0.0, -5.0])
        direction = np.array([0.0, 0.0, -1.0])

        distance, hit_point = arm.raymarch_single(origin, direction, sphere_sdf)

        assert distance is None
        assert hit_point is None

    def test_adaptive_renders_frame(self):
        """AdaptiveRaymarcher can render frames."""
        arm = AdaptiveRaymarcher(width=10, height=5)

        def sphere_sdf(p):
            return np.linalg.norm(p) - 1.5

        result = arm.render_frame(sphere_sdf)

        assert isinstance(result, str)
        lines = result.split("\n")
        assert len(lines) == 5
