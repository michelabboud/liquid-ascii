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
FeatureSDFFunc = Callable[[np.ndarray], tuple[float, any]]  # Returns (distance, feature)


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
        self, origin: np.ndarray, direction: np.ndarray, sdf: SDFFunc
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
        intensities = self.shader.compute_lighting_batch(self._normal_buffer, view_dirs)

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

    def _detect_edges(
        self,
        hit_mask: np.ndarray,
        normals: np.ndarray,
        hit_points: np.ndarray,
        normal_threshold: float = 0.5,
        depth_threshold: float = 0.1,
    ) -> np.ndarray:
        """
        Detect edges using normal discontinuities and depth changes.

        Args:
            hit_mask: Boolean mask of pixels that hit geometry
            normals: Surface normals at each pixel
            hit_points: 3D hit points for depth comparison
            normal_threshold: Normal angle difference threshold (0-2, higher = more sensitive)
            depth_threshold: Depth discontinuity threshold

        Returns:
            Boolean mask indicating edge pixels
        """
        edge_mask = np.zeros_like(hit_mask, dtype=bool)
        h, w = hit_mask.shape

        for y in range(1, h - 1):
            for x in range(1, w - 1):
                if not hit_mask[y, x]:
                    continue

                is_edge = False
                current_normal = normals[y, x]
                current_point = hit_points[y, x]

                # Check 4-neighbors (up, down, left, right)
                neighbors = [
                    (y - 1, x),  # up
                    (y + 1, x),  # down
                    (y, x - 1),  # left
                    (y, x + 1),  # right
                ]

                for ny, nx in neighbors:
                    # Edge at geometry boundary (hit vs no-hit)
                    if not hit_mask[ny, nx]:
                        is_edge = True
                        break

                    # Edge at normal discontinuity
                    neighbor_normal = normals[ny, nx]
                    dot_product = np.dot(current_normal, neighbor_normal)
                    if dot_product < (1.0 - normal_threshold):
                        is_edge = True
                        break

                    # Edge at depth discontinuity
                    neighbor_point = hit_points[ny, nx]
                    depth_diff = np.abs(np.linalg.norm(current_point - neighbor_point))
                    if depth_diff > depth_threshold:
                        is_edge = True
                        break

                edge_mask[y, x] = is_edge

        return edge_mask

    def render_frame_with_features(
        self,
        sdf_with_features: FeatureSDFFunc,
        color_scheme,
        background: str = " ",
        use_emojis: bool = False,
        use_edges: bool = True,
        edge_boost: float = 0.8,
    ) -> str:
        """
        Render frame with feature-specific coloring (eyes, mouth, skin).

        Args:
            sdf_with_features: SDF function that returns (distance, feature_type)
            color_scheme: ColorScheme with eye_color, pupil_color, mouth_color
            background: Background character
            use_emojis: Use emoji characters for facial features
            use_edges: Enable edge detection for sharper feature boundaries
            edge_boost: How much to boost edge intensity (0-1, higher = darker edges)

        Returns:
            Multi-line ASCII string with ANSI color codes
        """
        from ..terminal.colors import rgb_to_ansi_escape, reset_color
        from ..model.head import FacialFeature

        # Emoji feature characters
        EMOJI_CHARS = {
            FacialFeature.PUPIL: "⚫",  # Black circle
            FacialFeature.EYE: "⚪",    # White circle
            FacialFeature.MOUTH: "🔴", # Red circle
        }

        # Generate rays
        origins, directions = self.camera.get_rays_batch(self.width, self.height)

        # Buffers
        hit_mask = np.zeros((self.height, self.width), dtype=bool)
        hit_points = np.zeros((self.height, self.width, 3))
        features = np.zeros((self.height, self.width), dtype=object)
        normals = np.zeros((self.height, self.width, 3))

        # Raymarch each pixel
        for y in range(self.height):
            for x in range(self.width):
                t = 0.0
                origin = origins[y, x]
                direction = directions[y, x]

                for _ in range(self.max_steps):
                    point = origin + t * direction
                    dist, feature = sdf_with_features(tuple(point))

                    if dist < self.epsilon:
                        hit_mask[y, x] = True
                        hit_points[y, x] = point
                        features[y, x] = feature
                        # Compute normal using just distance
                        normals[y, x] = self._compute_normal_for_feature(point, sdf_with_features)
                        break

                    t += dist
                    if t > self.max_distance:
                        break

        # Compute lighting
        view_dirs = -directions
        intensities = self.shader.compute_lighting_batch(normals, view_dirs)
        char_indices = self.shader.intensity_to_char_batch(intensities)

        # Apply edge detection to boost contrast at feature boundaries
        if use_edges:
            edge_mask = self._detect_edges(hit_mask, normals, hit_points)
            # Boost character indices at edges (push toward darker characters)
            ramp_size = len(self.shader.ramp)
            for y in range(self.height):
                for x in range(self.width):
                    if edge_mask[y, x]:
                        # Boost toward max index (darkest character)
                        boosted = char_indices[y, x] + edge_boost * (ramp_size - 1 - char_indices[y, x])
                        char_indices[y, x] = int(min(boosted, ramp_size - 1))
                        # Also darken the intensity for edge coloring
                        intensities[y, x] = max(0, intensities[y, x] - edge_boost * 0.3)

        # Build colored output
        lines = []
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if hit_mask[y, x]:
                    feature = features[y, x]
                    intensity = intensities[y, x]

                    # Select character (emoji or ASCII)
                    if use_emojis and feature in EMOJI_CHARS:
                        char = EMOJI_CHARS[feature]
                    else:
                        char = self.shader.ramp[char_indices[y, x]]

                    # Select color based on feature
                    if feature == FacialFeature.PUPIL:
                        color = color_scheme.pupil_color
                    elif feature == FacialFeature.EYE:
                        color = color_scheme.eye_color
                    elif feature == FacialFeature.MOUTH:
                        color = color_scheme.mouth_color
                    else:  # SKIN
                        color = color_scheme.get_surface_color(intensity)

                    # Apply color
                    color_code = rgb_to_ansi_escape(color.r, color.g, color.b)
                    row += f"{color_code}{char}{reset_color()}"
                else:
                    row += background

            lines.append(row)

        return "\n".join(lines)

    def _compute_normal_for_feature(self, point: np.ndarray, sdf_with_features: FeatureSDFFunc) -> np.ndarray:
        """Compute normal using feature SDF (extract just distance)."""
        eps = 0.001
        px, _ = sdf_with_features(tuple(point + np.array([eps, 0, 0])))
        nx, _ = sdf_with_features(tuple(point - np.array([eps, 0, 0])))
        py, _ = sdf_with_features(tuple(point + np.array([0, eps, 0])))
        ny, _ = sdf_with_features(tuple(point - np.array([0, eps, 0])))
        pz, _ = sdf_with_features(tuple(point + np.array([0, 0, eps])))
        nz, _ = sdf_with_features(tuple(point - np.array([0, 0, eps])))

        normal = np.array([(px - nx), (py - ny), (pz - nz)])
        norm = np.linalg.norm(normal)
        if norm > 0:
            return normal / norm
        return np.array([0, 1, 0])


class AdaptiveRaymarcher(Raymarcher):
    """
    Raymarcher with adaptive quality based on distance and importance.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.relaxation_factor = 1.5  # Speed up distant rays

    def raymarch_single(
        self, origin: np.ndarray, direction: np.ndarray, sdf: SDFFunc
    ) -> tuple[float | None, np.ndarray | None]:
        """
        Adaptive raymarching with over-relaxation for speed.
        """
        t = 0.0
        prev_dist = float("inf")

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
