"""
Signed Distance Function (SDF) primitives and operations.

Based on Inigo Quilez's SDF functions: https://iquilezles.org/articles/distfunctions/
These functions form the building blocks for 3D shape composition.
"""

import numpy as np
from typing import Union, Tuple

# Type aliases for clarity
Vec3 = Union[np.ndarray, Tuple[float, float, float]]


def _to_array(v: Vec3) -> np.ndarray:
    """Convert to numpy array if needed."""
    if isinstance(v, np.ndarray):
        return v
    return np.array(v, dtype=np.float64)


def length(v: Vec3) -> float:
    """
    Compute the length (magnitude) of a vector.

    Optimized to avoid unnecessary array conversions.
    """
    if isinstance(v, np.ndarray):
        # Fast path for numpy arrays
        return float(np.sqrt(np.sum(v * v)))
    # Fast path for tuples - avoid array conversion
    x, y, z = v
    return float((x * x + y * y + z * z) ** 0.5)


def length_vec(v: np.ndarray) -> np.ndarray:
    """Vectorized length for arrays of points."""
    return np.sqrt(np.sum(v * v, axis=-1))


def normalize(v: Vec3) -> np.ndarray:
    """Normalize a vector to unit length."""
    v = _to_array(v)
    l = length(v)
    if l < 1e-10:
        return np.zeros_like(v)
    return v / l


# =============================================================================
# SDF Primitives
# =============================================================================


def sdf_sphere(p: Vec3, center: Vec3 = (0, 0, 0), radius: float = 1.0) -> float:
    """
    Signed distance to a sphere.

    Args:
        p: Point to evaluate
        center: Center of the sphere
        radius: Radius of the sphere

    Returns:
        Signed distance (negative inside, positive outside)
    """
    p = _to_array(p)
    center = _to_array(center)
    return length(p - center) - radius


def sdf_sphere_vec(p: np.ndarray, center: Vec3 = (0, 0, 0), radius: float = 1.0) -> np.ndarray:
    """Vectorized sphere SDF for batch evaluation."""
    center = _to_array(center)
    return length_vec(p - center) - radius


def sdf_ellipsoid(p: Vec3, center: Vec3 = (0, 0, 0), radii: Vec3 = (1, 1, 1)) -> float:
    """
    Signed distance to an ellipsoid.

    This is an approximation that works well for reasonable aspect ratios.

    Args:
        p: Point to evaluate
        center: Center of the ellipsoid
        radii: Semi-axes (rx, ry, rz)

    Returns:
        Approximate signed distance
    """
    p = _to_array(p)
    center = _to_array(center)
    radii = _to_array(radii)

    # Avoid division by zero
    radii = np.maximum(radii, 1e-10)

    # Transform to unit sphere space
    q = (p - center) / radii

    k0 = length(q)
    if k0 < 1e-10:
        return -min(radii)

    k1 = length(q / radii)
    if k1 < 1e-10:
        return -min(radii)

    return k0 * (k0 - 1.0) / k1


def sdf_ellipsoid_vec(p: np.ndarray, center: Vec3 = (0, 0, 0), radii: Vec3 = (1, 1, 1)) -> np.ndarray:
    """Vectorized ellipsoid SDF for batch evaluation."""
    center = _to_array(center)
    radii = _to_array(radii)
    radii = np.maximum(radii, 1e-10)

    q = (p - center) / radii
    k0 = length_vec(q)
    k1 = length_vec(q / radii)

    # Handle edge cases
    k0 = np.maximum(k0, 1e-10)
    k1 = np.maximum(k1, 1e-10)

    return k0 * (k0 - 1.0) / k1


def sdf_box(p: Vec3, center: Vec3 = (0, 0, 0), size: Vec3 = (1, 1, 1)) -> float:
    """
    Signed distance to a box (axis-aligned).

    Args:
        p: Point to evaluate
        center: Center of the box
        size: Half-extents of the box (half width, height, depth)

    Returns:
        Signed distance
    """
    p = _to_array(p)
    center = _to_array(center)
    size = _to_array(size)

    q = np.abs(p - center) - size
    return length(np.maximum(q, 0.0)) + min(max(q[0], max(q[1], q[2])), 0.0)


def sdf_torus(p: Vec3, center: Vec3 = (0, 0, 0), R: float = 1.0, r: float = 0.3) -> float:
    """
    Signed distance to a torus (donut shape).

    Args:
        p: Point to evaluate
        center: Center of the torus
        R: Major radius (distance from center to tube center)
        r: Minor radius (tube thickness)

    Returns:
        Signed distance
    """
    p = _to_array(p)
    center = _to_array(center)
    p = p - center

    # Project to XZ plane, compute distance to ring
    q = np.array([np.sqrt(p[0]**2 + p[2]**2) - R, p[1]])
    return length(q) - r


def sdf_capsule(p: Vec3, a: Vec3 = (0, -0.5, 0), b: Vec3 = (0, 0.5, 0), r: float = 0.2) -> float:
    """
    Signed distance to a capsule (line segment with radius).

    Args:
        p: Point to evaluate
        a: Start point of capsule line
        b: End point of capsule line
        r: Capsule radius

    Returns:
        Signed distance
    """
    p = _to_array(p)
    a = _to_array(a)
    b = _to_array(b)

    pa = p - a
    ba = b - a
    h = np.clip(np.dot(pa, ba) / np.dot(ba, ba), 0.0, 1.0)
    return length(pa - ba * h) - r


def sdf_cylinder(p: Vec3, center: Vec3 = (0, 0, 0), height: float = 1.0, radius: float = 0.5) -> float:
    """
    Signed distance to a vertical cylinder.

    Args:
        p: Point to evaluate
        center: Center of the cylinder
        height: Half-height of the cylinder
        radius: Radius of the cylinder

    Returns:
        Signed distance
    """
    p = _to_array(p)
    center = _to_array(center)
    p = p - center

    d = np.array([np.sqrt(p[0]**2 + p[2]**2) - radius, abs(p[1]) - height])
    return min(max(d[0], d[1]), 0.0) + length(np.maximum(d, 0.0))


# =============================================================================
# SDF Boolean Operations (Sharp)
# =============================================================================


def sdf_union(d1: float, d2: float) -> float:
    """Union of two SDFs (sharp blend)."""
    return min(d1, d2)


def sdf_subtraction(d1: float, d2: float) -> float:
    """Subtraction of d1 from d2 (sharp carve)."""
    return max(-d1, d2)


def sdf_intersection(d1: float, d2: float) -> float:
    """Intersection of two SDFs (sharp)."""
    return max(d1, d2)


# =============================================================================
# SDF Smooth Boolean Operations (KEY for liquid effect!)
# =============================================================================


def sdf_smooth_union(d1: float, d2: float, k: float = 0.1) -> float:
    """
    Smooth union of two SDFs - creates liquid-like blending.

    Args:
        d1: First SDF value
        d2: Second SDF value
        k: Smoothing factor (larger = more blending)

    Returns:
        Smoothly blended SDF value
    """
    if k < 1e-10:
        return min(d1, d2)
    h = max(k - abs(d1 - d2), 0.0) / k
    return min(d1, d2) - h * h * k * 0.25


def sdf_smooth_union_vec(d1: np.ndarray, d2: np.ndarray, k: float = 0.1) -> np.ndarray:
    """Vectorized smooth union."""
    if k < 1e-10:
        return np.minimum(d1, d2)
    h = np.maximum(k - np.abs(d1 - d2), 0.0) / k
    return np.minimum(d1, d2) - h * h * k * 0.25


def sdf_smooth_subtraction(d1: float, d2: float, k: float = 0.1) -> float:
    """
    Smooth subtraction of d1 from d2 - creates smooth cavities.

    Args:
        d1: SDF to subtract
        d2: SDF to subtract from
        k: Smoothing factor

    Returns:
        Smoothly carved SDF value
    """
    if k < 1e-10:
        return max(-d1, d2)
    h = max(k - abs(-d1 - d2), 0.0) / k
    return max(-d1, d2) + h * h * k * 0.25


def sdf_smooth_subtraction_vec(d1: np.ndarray, d2: np.ndarray, k: float = 0.1) -> np.ndarray:
    """Vectorized smooth subtraction."""
    if k < 1e-10:
        return np.maximum(-d1, d2)
    h = np.maximum(k - np.abs(-d1 - d2), 0.0) / k
    return np.maximum(-d1, d2) + h * h * k * 0.25


def sdf_smooth_intersection(d1: float, d2: float, k: float = 0.1) -> float:
    """
    Smooth intersection of two SDFs.

    Args:
        d1: First SDF value
        d2: Second SDF value
        k: Smoothing factor

    Returns:
        Smoothly intersected SDF value
    """
    if k < 1e-10:
        return max(d1, d2)
    h = max(k - abs(d1 - d2), 0.0) / k
    return max(d1, d2) + h * h * k * 0.25


# =============================================================================
# SDF Transformations
# =============================================================================


def sdf_translate(p: Vec3, offset: Vec3) -> np.ndarray:
    """Translate point (use with SDF evaluation)."""
    return _to_array(p) - _to_array(offset)


def sdf_scale(p: Vec3, scale: float) -> np.ndarray:
    """Scale point (remember to scale result by same factor)."""
    return _to_array(p) / scale


def sdf_rotate_y(p: Vec3, angle: float) -> np.ndarray:
    """Rotate point around Y axis."""
    p = _to_array(p)
    c, s = np.cos(angle), np.sin(angle)
    return np.array([
        c * p[0] + s * p[2],
        p[1],
        -s * p[0] + c * p[2]
    ])


def sdf_rotate_x(p: Vec3, angle: float) -> np.ndarray:
    """Rotate point around X axis."""
    p = _to_array(p)
    c, s = np.cos(angle), np.sin(angle)
    return np.array([
        p[0],
        c * p[1] - s * p[2],
        s * p[1] + c * p[2]
    ])


def sdf_rotate_z(p: Vec3, angle: float) -> np.ndarray:
    """Rotate point around Z axis."""
    p = _to_array(p)
    c, s = np.cos(angle), np.sin(angle)
    return np.array([
        c * p[0] - s * p[1],
        s * p[0] + c * p[1],
        p[2]
    ])


# =============================================================================
# Gradient / Normal Calculation
# =============================================================================


def compute_normal(p: Vec3, sdf_func, eps: float = 0.001) -> np.ndarray:
    """
    Compute surface normal at a point using gradient of SDF.

    Args:
        p: Point on or near surface
        sdf_func: SDF function that takes a point
        eps: Small offset for finite differences

    Returns:
        Normalized surface normal vector
    """
    p = _to_array(p)

    # Central differences for better accuracy
    normal = np.array([
        sdf_func((p[0] + eps, p[1], p[2])) - sdf_func((p[0] - eps, p[1], p[2])),
        sdf_func((p[0], p[1] + eps, p[2])) - sdf_func((p[0], p[1] - eps, p[2])),
        sdf_func((p[0], p[1], p[2] + eps)) - sdf_func((p[0], p[1], p[2] - eps))
    ])

    return normalize(normal)
