"""
Tests for wireframe/edge rendering mode.
"""

import numpy as np
import pytest

from src.model import CharacterHead
from src.renderer import ASCIIShader, Camera, Raymarcher
from src.renderer.quality import QualityLevel


class TestWireframeRendering:
    """Test wireframe/edge rendering functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.head = CharacterHead(character_name="default")
        self.camera = Camera(position=(0, 0, -3.5), target=(0, 0, 0))
        self.shader = ASCIIShader()
        self.raymarcher = Raymarcher(
            width=40,
            height=20,
            camera=self.camera,
            shader=self.shader,
            quality=QualityLevel.LOW,  # Fast tests
        )

    def test_wireframe_render_returns_string(self):
        """Wireframe render should return a string."""
        sdf = self.head.get_sdf()
        frame = self.raymarcher.render_frame_wireframe(sdf)

        assert isinstance(frame, str)
        assert len(frame) > 0

    def test_wireframe_has_correct_dimensions(self):
        """Wireframe output should have correct dimensions."""
        sdf = self.head.get_sdf()
        frame = self.raymarcher.render_frame_wireframe(sdf)

        lines = frame.split("\n")
        assert len(lines) == 20  # Height

        # Check width (all lines should be same length)
        widths = [len(line) for line in lines]
        assert all(w == 40 for w in widths)  # Width

    def test_wireframe_custom_edge_char(self):
        """Wireframe should use custom edge character."""
        sdf = self.head.get_sdf()
        edge_char = "*"
        frame = self.raymarcher.render_frame_wireframe(sdf, edge_char=edge_char)

        # Should contain the edge character
        assert edge_char in frame

    def test_wireframe_background_char(self):
        """Wireframe should use custom background character."""
        sdf = self.head.get_sdf()
        background = "."
        frame = self.raymarcher.render_frame_wireframe(sdf, background=background)

        # Should contain background character
        assert background in frame

    def test_edge_detection_thresholds(self):
        """Test different edge detection thresholds."""
        sdf = self.head.get_sdf()

        # Lower threshold = more edges
        frame_sensitive = self.raymarcher.render_frame_wireframe(
            sdf, normal_threshold=1.0, edge_char="#"
        )

        # Higher threshold = fewer edges (but shouldn't error)
        frame_less_sensitive = self.raymarcher.render_frame_wireframe(
            sdf, normal_threshold=0.1, edge_char="#"
        )

        # Both should be valid strings
        assert isinstance(frame_sensitive, str)
        assert isinstance(frame_less_sensitive, str)

    def test_edge_thickness_control(self):
        """Test edge thickness variations."""
        sdf = self.head.get_sdf()

        # Thickness 1 (normal)
        frame_thin = self.raymarcher.render_frame_wireframe(
            sdf, edge_thickness=1, edge_char="#"
        )

        # Thickness 2 (thicker)
        frame_thick = self.raymarcher.render_frame_wireframe(
            sdf, edge_thickness=2, edge_char="#"
        )

        # Thicker version should have more edge characters
        thin_edge_count = frame_thin.count("#")
        thick_edge_count = frame_thick.count("#")

        assert thick_edge_count >= thin_edge_count

    def test_thicken_edges_method(self):
        """Test the _thicken_edges method."""
        # Create a small test mask
        edge_mask = np.zeros((10, 10), dtype=bool)
        edge_mask[5, 5] = True  # Single edge pixel

        # Thicken by 1 (no change)
        thickened_1 = self.raymarcher._thicken_edges(edge_mask, 1)
        assert np.sum(thickened_1) == 1  # Still 1 pixel

        # Thicken by 2 (should expand)
        thickened_2 = self.raymarcher._thicken_edges(edge_mask, 2)
        assert np.sum(thickened_2) > 1  # More pixels

        # Thicken by 3 (should expand more)
        thickened_3 = self.raymarcher._thicken_edges(edge_mask, 3)
        assert np.sum(thickened_3) > np.sum(thickened_2)

    def test_detect_edges_method(self):
        """Test the _detect_edges method."""
        # Create simple test data
        hit_mask = np.ones((10, 10), dtype=bool)
        hit_points = np.random.rand(10, 10, 3)
        normals = np.random.rand(10, 10, 3)

        # Normalize normals
        norms = np.linalg.norm(normals, axis=-1, keepdims=True)
        normals = normals / np.maximum(norms, 1e-10)

        # Detect edges
        edge_mask = self.raymarcher._detect_edges(
            hit_mask, normals, hit_points
        )

        # Should return a boolean mask of correct shape
        assert edge_mask.shape == (10, 10)
        assert edge_mask.dtype == bool

    def test_wireframe_with_different_characters(self):
        """Test wireframe rendering with different character presets."""
        characters = ["default", "robot", "alien", "baby", "cyclops"]

        for char_name in characters:
            head = CharacterHead(character_name=char_name)
            sdf = head.get_sdf()
            frame = self.raymarcher.render_frame_wireframe(sdf)

            # Should render without errors
            assert isinstance(frame, str)
            assert len(frame) > 0

    def test_wireframe_no_crash_on_empty_scene(self):
        """Wireframe should handle scenes with no geometry gracefully."""
        # Create an SDF that returns high distance everywhere (no geometry)
        def empty_sdf(p):
            return 1000.0

        frame = self.raymarcher.render_frame_wireframe(empty_sdf)

        # Should return string with background characters
        assert isinstance(frame, str)
        lines = frame.split("\n")
        assert len(lines) == 20


class TestEdgeDetection:
    """Test edge detection algorithms."""

    def test_edge_at_geometry_boundary(self):
        """Edges should be detected at geometry boundaries."""
        # Create a mask with a clear boundary
        hit_mask = np.zeros((10, 10), dtype=bool)
        hit_mask[3:7, 3:7] = True  # Square in center

        hit_points = np.zeros((10, 10, 3))
        normals = np.zeros((10, 10, 3))
        normals[:, :, 2] = 1.0  # All normals pointing forward

        raymarcher = Raymarcher(
            width=10,
            height=10,
            camera=Camera(position=(0, 0, -3.5), target=(0, 0, 0)),
            shader=ASCIIShader(),
            quality=QualityLevel.LOW,
        )

        edge_mask = raymarcher._detect_edges(hit_mask, normals, hit_points)

        # Edges should exist at the boundary
        assert np.any(edge_mask)

        # Interior pixels should mostly not be edges
        interior_edges = edge_mask[4:6, 4:6]
        assert not np.all(interior_edges)

    def test_edge_at_normal_discontinuity(self):
        """Edges should be detected at sharp normal changes."""
        hit_mask = np.ones((10, 10), dtype=bool)
        hit_points = np.zeros((10, 10, 3))
        normals = np.zeros((10, 10, 3))

        # Left half: normals pointing up
        normals[:, :5, 1] = 1.0

        # Right half: normals pointing down
        normals[:, 5:, 1] = -1.0

        raymarcher = Raymarcher(
            width=10,
            height=10,
            camera=Camera(position=(0, 0, -3.5), target=(0, 0, 0)),
            shader=ASCIIShader(),
            quality=QualityLevel.LOW,
        )

        edge_mask = raymarcher._detect_edges(
            hit_mask, normals, hit_points, normal_threshold=0.5
        )

        # Should detect edges at the discontinuity (x=5)
        assert np.any(edge_mask[:, 4:6])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
