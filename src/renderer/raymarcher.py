"""
Raymarching renderer for SDF-based 3D graphics.

This is the core rendering engine that casts rays through the scene
and evaluates signed distance functions to find surfaces.
"""

from collections.abc import Callable

import numpy as np

from .camera import Camera
from .quality import QualityLevel, get_quality_preset
from .sdf import compute_normal
from .shading import ASCIIShader

# Type alias for SDF functions
SDFFunc = Callable[[np.ndarray], float]


class Raymarcher:
    """
    Raymarching renderer for ASCII output.

    Casts rays through a scene defined by signed distance functions,
    computing lighting and converting to ASCII characters.
    """

    def __init__(
        self,
        width: int = 80,
        height: int = 40,
        camera: Camera | None = None,
        shader: ASCIIShader | None = None,
        max_steps: int = 64,
        max_distance: float = 100.0,
        epsilon: float = 0.001,
        quality: QualityLevel | None = None,
    ):
        """
        Initialize the raymarcher.

        Args:
            width: Output width in characters
            height: Output height in characters
            camera: Camera for view/projection (default: standard perspective)
            shader: ASCII shader for rendering (default: standard shader)
            max_steps: Maximum raymarching iterations
            max_distance: Maximum ray travel distance
            epsilon: Surface hit threshold
            quality: Quality preset (overrides max_steps, epsilon if provided)
        """
        self.width = width
        self.height = height
        self.camera = camera or Camera()
        self.shader = shader or ASCIIShader()

        # Apply quality preset if provided
        if quality is not None:
            preset = get_quality_preset(quality)
            self.max_steps = preset.max_steps
            self.max_distance = preset.max_distance
            self.epsilon = preset.epsilon
            self._quality_preset = preset
        else:
            self.max_steps = max_steps
            self.max_distance = max_distance
            self.epsilon = epsilon
            self._quality_preset = None

        # Pre-allocate buffers
        self._hit_buffer = np.zeros((height, width), dtype=bool)
        self._distance_buffer = np.zeros((height, width))
        self._normal_buffer = np.zeros((height, width, 3))

    def resize(self, width: int, height: int):
        """Resize the render output."""
        self.width = width
        self.height = height
        self._hit_buffer = np.zeros((height, width), dtype=bool)
        self._distance_buffer = np.zeros((height, width))
        self._normal_buffer = np.zeros((height, width, 3))

    def set_quality(self, quality: QualityLevel):
        """
        Update quality settings dynamically.

        Args:
            quality: New quality level
        """
        preset = get_quality_preset(quality)
        self.max_steps = preset.max_steps
        self.max_distance = preset.max_distance
        self.epsilon = preset.epsilon
        self._quality_preset = preset

    def raymarch_single(
        self,
        origin: np.ndarray,
        direction: np.ndarray,
        sdf: SDFFunc
    ) -> tuple[float | None, np.ndarray | None]:
        """
        March a single ray through the scene.

        Args:
            origin: Ray origin
            direction: Ray direction (normalized)
            sdf: Signed distance function

        Returns:
            (distance, hit_point) or (None, None) if no hit
        """
        t = 0.0

        for _ in range(self.max_steps):
            point = origin + t * direction
            dist = sdf(tuple(point))

            if dist < self.epsilon:
                return t, point

            t += dist

            if t > self.max_distance:
                break

        return None, None

    def render_frame(self, sdf: SDFFunc, background: str = " ") -> str:
        """
        Render a complete frame to ASCII.

        Args:
            sdf: Signed distance function defining the scene
            background: Character for empty space

        Returns:
            Multi-line ASCII string
        """
        # Generate all rays
        origins, directions = self.camera.get_rays_batch(self.width, self.height)

        # Reset buffers
        self._hit_buffer.fill(False)
        self._distance_buffer.fill(self.max_distance)
        self._normal_buffer.fill(0)

        # Raymarch each pixel
        for y in range(self.height):
            for x in range(self.width):
                origin = origins[y, x]
                direction = directions[y, x]

                t, hit_point = self.raymarch_single(origin, direction, sdf)

                if hit_point is not None:
                    self._hit_buffer[y, x] = True
                    self._distance_buffer[y, x] = t
                    self._normal_buffer[y, x] = compute_normal(hit_point, sdf)

        # Compute lighting
        view_dirs = -directions  # View direction is opposite of ray direction
        intensities = self.shader.compute_lighting_batch(
            self._normal_buffer,
            view_dirs
        )

        # Convert to characters
        char_indices = self.shader.intensity_to_char_batch(intensities)

        # Build output
        lines = []
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if self._hit_buffer[y, x]:
                    row += self.shader.ramp[char_indices[y, x]]
                else:
                    row += background
            lines.append(row)

        return "\n".join(lines)

    def render_frame_fast(self, sdf: SDFFunc, background: str = " ") -> str:
        """
        Faster rendering using numpy vectorization where possible.

        Still requires per-pixel raymarching but optimizes lighting.

        Args:
            sdf: Signed distance function
            background: Background character

        Returns:
            Multi-line ASCII string
        """
        # Generate rays
        origins, directions = self.camera.get_rays_batch(self.width, self.height)

        # Arrays to store results
        hit_mask = np.zeros((self.height, self.width), dtype=bool)
        hit_points = np.zeros((self.height, self.width, 3))
        hit_distances = np.full((self.height, self.width), self.max_distance)

        # Raymarch each pixel (this is the bottleneck)
        for y in range(self.height):
            for x in range(self.width):
                t = 0.0
                origin = origins[y, x]
                direction = directions[y, x]

                for _ in range(self.max_steps):
                    point = origin + t * direction
                    dist = sdf(tuple(point))

                    if dist < self.epsilon:
                        hit_mask[y, x] = True
                        hit_points[y, x] = point
                        hit_distances[y, x] = t
                        break

                    t += dist
                    if t > self.max_distance:
                        break

        # Compute normals only for hit pixels
        normals = np.zeros((self.height, self.width, 3))
        eps = 0.001

        hit_indices = np.where(hit_mask)
        for y, x in zip(hit_indices[0], hit_indices[1]):
            p = hit_points[y, x]
            normals[y, x] = compute_normal(p, sdf, eps)

        # Vectorized lighting
        view_dirs = -directions
        intensities = self.shader.compute_lighting_batch(normals, view_dirs)

        # Apply hit mask
        intensities = np.where(hit_mask, intensities, 0)

        # Convert to characters
        char_indices = self.shader.intensity_to_char_batch(intensities)

        # Build output string
        ramp = self.shader.ramp
        bg_ord = ord(background)

        # Create output array
        output = np.full((self.height, self.width), bg_ord, dtype=np.int32)
        for i, char in enumerate(ramp):
            mask = (char_indices == i) & hit_mask
            output[mask] = ord(char)

        # Convert to string
        lines = []
        for row in output:
            lines.append("".join(chr(c) for c in row))

        return "\n".join(lines)


class AdaptiveRaymarcher(Raymarcher):
    """
    Raymarcher with adaptive quality based on distance and importance.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.relaxation_factor = 1.5  # Speed up distant rays

    def raymarch_single(
        self,
        origin: np.ndarray,
        direction: np.ndarray,
        sdf: SDFFunc
    ) -> tuple[float | None, np.ndarray | None]:
        """
        Adaptive raymarching with over-relaxation for speed.
        """
        t = 0.0
        prev_dist = float('inf')

        for i in range(self.max_steps):
            point = origin + t * direction
            dist = sdf(tuple(point))

            # Over-relaxation: step further when safe
            if dist > prev_dist * 0.5 and i > 0:
                step = dist * self.relaxation_factor
            else:
                step = dist

            if dist < self.epsilon:
                # Back up slightly for accuracy
                t -= step * 0.5
                point = origin + t * direction
                return t, point

            t += step
            prev_dist = dist

            if t > self.max_distance:
                break

        return None, None
