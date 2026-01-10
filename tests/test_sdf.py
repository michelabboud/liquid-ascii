"""Tests for SDF primitives and operations."""

import pytest
import numpy as np
import sys
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from src.renderer.sdf import (
    sdf_sphere,
    sdf_ellipsoid,
    sdf_box,
    sdf_smooth_union,
    sdf_smooth_subtraction,
    length,
    normalize,
    compute_normal,
)


class TestSDFPrimitives:
    """Test SDF primitive functions."""

    def test_sphere_center(self):
        """Point at center should have negative distance."""
        dist = sdf_sphere((0, 0, 0), (0, 0, 0), 1.0)
        assert dist == -1.0

    def test_sphere_surface(self):
        """Point on surface should have zero distance."""
        dist = sdf_sphere((1, 0, 0), (0, 0, 0), 1.0)
        assert abs(dist) < 0.001

    def test_sphere_outside(self):
        """Point outside should have positive distance."""
        dist = sdf_sphere((2, 0, 0), (0, 0, 0), 1.0)
        assert dist == pytest.approx(1.0, abs=0.001)

    def test_ellipsoid_center(self):
        """Ellipsoid center should be inside."""
        dist = sdf_ellipsoid((0, 0, 0), (0, 0, 0), (1, 2, 1))
        assert dist < 0

    def test_box_center(self):
        """Box center should be inside."""
        dist = sdf_box((0, 0, 0), (0, 0, 0), (1, 1, 1))
        assert dist < 0

    def test_box_surface(self):
        """Point on box surface should have ~zero distance."""
        dist = sdf_box((1, 0, 0), (0, 0, 0), (1, 1, 1))
        assert abs(dist) < 0.001


class TestSDFOperations:
    """Test SDF boolean operations."""

    def test_smooth_union_identical(self):
        """Smooth union of identical SDFs."""
        result = sdf_smooth_union(0.5, 0.5, 0.1)
        # Should be less than either input due to blending
        assert result < 0.5

    def test_smooth_union_far_apart(self):
        """Smooth union of distant SDFs should be like hard union."""
        result = sdf_smooth_union(0.1, 10.0, 0.1)
        assert result == pytest.approx(0.1, abs=0.01)

    def test_smooth_subtraction(self):
        """Smooth subtraction should carve out volume."""
        # Subtracting a sphere from a larger sphere
        outer = 1.0  # Distance to outer sphere surface
        inner = 0.5  # Distance to inner sphere surface
        result = sdf_smooth_subtraction(inner, outer, 0.1)
        # Should be positive (outside the carved volume)
        assert result > 0


class TestVectorOps:
    """Test vector operations."""

    def test_length(self):
        """Test vector length calculation."""
        assert length((3, 4, 0)) == 5.0
        assert length((1, 0, 0)) == 1.0
        assert length((0, 0, 0)) == 0.0

    def test_normalize(self):
        """Test vector normalization."""
        n = normalize((3, 4, 0))
        assert length(n) == pytest.approx(1.0, abs=0.0001)
        assert n[0] == pytest.approx(0.6, abs=0.0001)
        assert n[1] == pytest.approx(0.8, abs=0.0001)

    def test_normalize_zero(self):
        """Normalizing zero vector should return zero."""
        n = normalize((0, 0, 0))
        assert np.allclose(n, [0, 0, 0])


class TestNormalComputation:
    """Test surface normal computation."""

    def test_sphere_normal_x(self):
        """Normal on +X side of sphere should point +X."""
        def sphere_sdf(p):
            return sdf_sphere(p, (0, 0, 0), 1.0)

        normal = compute_normal((1, 0, 0), sphere_sdf)
        assert normal[0] == pytest.approx(1.0, abs=0.01)
        assert abs(normal[1]) < 0.01
        assert abs(normal[2]) < 0.01

    def test_sphere_normal_y(self):
        """Normal on +Y side of sphere should point +Y."""
        def sphere_sdf(p):
            return sdf_sphere(p, (0, 0, 0), 1.0)

        normal = compute_normal((0, 1, 0), sphere_sdf)
        assert abs(normal[0]) < 0.01
        assert normal[1] == pytest.approx(1.0, abs=0.01)
        assert abs(normal[2]) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
