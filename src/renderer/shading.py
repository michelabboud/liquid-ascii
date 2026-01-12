"""
ASCII shading system for converting luminance values to characters.

Maps lighting calculations to appropriate ASCII characters to create
the illusion of 3D surfaces in text.
"""

import numpy as np

from .sdf import Vec3, _to_array, normalize

# Various ASCII luminance ramps (dark to bright)
RAMPS = {
    "standard": " .,:;i1tfLCG08@",
    "extended": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "simple": " .:-=+*#%@",
    "blocks": " ░▒▓█",
    "dots": " ⠁⠂⠃⠄⠅⠆⠇⡀⡁⡂⡃⡄⡅⡆⡇",
    "minimal": " .-+*#",
    "dense": " .:-=+*#%@█",
    # UTF-8 Enhanced ramps
    "unicode": " ·∘○◌◍◎●◉⦿",
    "stars": " ․·∗∘✦✧✨✪✫✬✭✮✯✰★",
    "diamonds": " ·◆◇◈◊⬥⬦⬧⬨",
    "circles": " ○◌◍◎◐◑◒◓◔◕◖◗●",
    "squares": " ▫▪▯▮▭▬◼◾◼️⬛",
    "geometric": " ▹▸▷▶◀◁◂◃◄►",
    "box": " ░▒▓█▇▆▅▄▃▂▁",
    "smooth": " ░▒▓█▓▒░",
    # Emoji-based ramps (for fun!)
    "faces": " 😐😶😑🙂😊😃😄😁",
    "hearts": " 🖤🤎💜💙💚💛🧡❤️",
    "food": " 🥚🥔🍞🧀🍰🍪🍩🍫",
    "nature": " 🌑🌘🌗🌖🌕🌝✨💫",
    "weather": " ⛅🌤️🌥️☁️🌫️🌪️⚡🔥",
}

# Lighting presets for different visual styles
LIGHTING_PRESETS = {
    "default": {
        "ambient": 0.1,
        "diffuse": 0.7,
        "specular": 0.2,
        "specular_power": 16.0,
        "description": "Balanced lighting with moderate contrast",
    },
    "dramatic": {
        "ambient": 0.05,  # Very dark shadows
        "diffuse": 0.85,  # Strong directional light
        "specular": 0.6,  # Bright highlights
        "specular_power": 32.0,  # Sharp highlights
        "description": "High contrast with deep shadows and bright highlights",
    },
    "soft": {
        "ambient": 0.3,  # Bright ambient (fills in shadows)
        "diffuse": 0.6,  # Moderate directional
        "specular": 0.1,  # Subtle highlights
        "specular_power": 8.0,  # Soft, wide highlights
        "description": "Gentle lighting with soft shadows",
    },
    "metallic": {
        "ambient": 0.08,  # Dark ambient
        "diffuse": 0.5,  # Moderate diffuse
        "specular": 0.9,  # Very bright specular
        "specular_power": 64.0,  # Very sharp highlights (metallic sheen)
        "description": "Metallic look with sharp, bright reflections",
    },
    "flat": {
        "ambient": 0.8,  # Very bright ambient
        "diffuse": 0.2,  # Minimal directional
        "specular": 0.0,  # No highlights
        "specular_power": 1.0,
        "description": "Flat lighting with minimal shading",
    },
    "noir": {
        "ambient": 0.02,  # Almost black shadows
        "diffuse": 0.95,  # Very strong directional
        "specular": 0.3,  # Moderate highlights
        "specular_power": 24.0,  # Sharp highlights
        "description": "Film noir style with stark contrast",
    },
    "cartoon": {
        "ambient": 0.2,  # Moderate ambient
        "diffuse": 0.8,  # Strong diffuse
        "specular": 0.4,  # Noticeable highlights
        "specular_power": 12.0,  # Medium sharpness
        "description": "Cartoon-style lighting with clear separation",
    },
    "subsurface": {
        "ambient": 0.15,  # Moderate ambient
        "diffuse": 0.75,  # Strong diffuse
        "specular": 0.15,  # Subtle specular
        "specular_power": 10.0,  # Soft specular
        "description": "Soft, organic lighting (skin-like)",
    },
}


class ASCIIShader:
    """
    Converts 3D lighting information to ASCII characters.
    """

    def __init__(
        self,
        ramp: str = "standard",
        custom_ramp: str | None = None,
        light_direction: Vec3 = (0.5, 0.8, -0.6),
        ambient: float = 0.1,
        diffuse: float = 0.7,
        specular: float = 0.2,
        specular_power: float = 16.0,
        lighting_preset: str | None = None,
    ):
        """
        Initialize the shader.

        Args:
            ramp: Name of predefined luminance ramp
            custom_ramp: Custom character ramp (overrides ramp param)
            light_direction: Direction TO the light source
            ambient: Ambient light intensity (0-1)
            diffuse: Diffuse light intensity (0-1)
            specular: Specular highlight intensity (0-1)
            specular_power: Specular exponent (higher = sharper highlights)
            lighting_preset: Name of lighting preset (overrides ambient/diffuse/specular)
        """
        if custom_ramp:
            self.ramp = custom_ramp
        elif ramp in RAMPS:
            self.ramp = RAMPS[ramp]
        else:
            self.ramp = RAMPS["standard"]

        self.light_dir = normalize(_to_array(light_direction))

        # Apply lighting preset if specified (overrides individual parameters)
        if lighting_preset and lighting_preset in LIGHTING_PRESETS:
            preset = LIGHTING_PRESETS[lighting_preset]
            self.ambient = preset["ambient"]
            self.diffuse = preset["diffuse"]
            self.specular = preset["specular"]
            self.specular_power = preset["specular_power"]
        else:
            self.ambient = ambient
            self.diffuse = diffuse
            self.specular = specular
            self.specular_power = specular_power

    def set_light_direction(self, direction: Vec3):
        """Update light direction."""
        self.light_dir = normalize(_to_array(direction))

    def apply_lighting_preset(self, preset_name: str):
        """
        Apply a lighting preset.

        Args:
            preset_name: Name of the preset from LIGHTING_PRESETS

        Raises:
            ValueError: If preset_name is not found
        """
        if preset_name not in LIGHTING_PRESETS:
            available = ", ".join(LIGHTING_PRESETS.keys())
            raise ValueError(f"Unknown lighting preset '{preset_name}'. Available: {available}")

        preset = LIGHTING_PRESETS[preset_name]
        self.ambient = preset["ambient"]
        self.diffuse = preset["diffuse"]
        self.specular = preset["specular"]
        self.specular_power = preset["specular_power"]

    def compute_lighting(self, normal: Vec3, view_dir: Vec3 | None = None) -> float:
        """
        Compute lighting intensity at a surface point.

        Uses Phong reflection model (ambient + diffuse + specular).

        Args:
            normal: Surface normal (should be normalized)
            view_dir: Direction from surface to camera (for specular)

        Returns:
            Lighting intensity (0-1)
        """
        normal = _to_array(normal)

        # Ambient component
        intensity = self.ambient

        # Diffuse component (Lambert)
        n_dot_l = np.dot(normal, self.light_dir)
        if n_dot_l > 0:
            intensity += self.diffuse * n_dot_l

            # Specular component (Blinn-Phong)
            if view_dir is not None and self.specular > 0:
                view_dir = normalize(_to_array(view_dir))
                # Half vector between light and view
                half_vec = normalize(self.light_dir + view_dir)
                n_dot_h = max(0, np.dot(normal, half_vec))
                intensity += self.specular * (n_dot_h**self.specular_power)

        return min(max(intensity, 0.0), 1.0)

    def compute_lighting_batch(
        self, normals: np.ndarray, view_dirs: np.ndarray | None = None
    ) -> np.ndarray:
        """
        Vectorized lighting computation for all pixels.

        Args:
            normals: Array of normals, shape (..., 3)
            view_dirs: Array of view directions, shape (..., 3)

        Returns:
            Array of intensities, shape (...)
        """
        # Ambient
        intensity = np.full(normals.shape[:-1], self.ambient)

        # Diffuse
        n_dot_l = np.sum(normals * self.light_dir, axis=-1)
        diffuse_mask = n_dot_l > 0
        intensity = np.where(diffuse_mask, intensity + self.diffuse * n_dot_l, intensity)

        # Specular
        if view_dirs is not None and self.specular > 0:
            # Normalize view directions
            view_lens = np.sqrt(np.sum(view_dirs**2, axis=-1, keepdims=True))
            view_dirs_norm = view_dirs / np.maximum(view_lens, 1e-10)

            # Half vectors
            half_vecs = self.light_dir + view_dirs_norm
            half_lens = np.sqrt(np.sum(half_vecs**2, axis=-1, keepdims=True))
            half_vecs = half_vecs / np.maximum(half_lens, 1e-10)

            n_dot_h = np.maximum(0, np.sum(normals * half_vecs, axis=-1))
            spec_contrib = self.specular * (n_dot_h**self.specular_power)
            intensity = np.where(diffuse_mask, intensity + spec_contrib, intensity)

        return np.clip(intensity, 0.0, 1.0)

    def intensity_to_char(self, intensity: float) -> str:
        """
        Map a lighting intensity to an ASCII character.

        Args:
            intensity: Lighting value (0-1)

        Returns:
            ASCII character
        """
        idx = int(intensity * (len(self.ramp) - 1))
        idx = min(max(idx, 0), len(self.ramp) - 1)
        return self.ramp[idx]

    def intensity_to_char_batch(self, intensities: np.ndarray) -> np.ndarray:
        """
        Vectorized intensity to character mapping.

        Args:
            intensities: Array of intensity values (0-1)

        Returns:
            Array of character indices into self.ramp
        """
        indices = (intensities * (len(self.ramp) - 1)).astype(int)
        return np.clip(indices, 0, len(self.ramp) - 1)

    def render_char(self, indices: np.ndarray) -> str:
        """
        Convert character indices to string output.

        Args:
            indices: 2D array of indices into ramp

        Returns:
            Multi-line string of ASCII art
        """
        lines = []
        for row in indices:
            line = "".join(self.ramp[i] for i in row)
            lines.append(line)
        return "\n".join(lines)


class ColorASCIIShader(ASCIIShader):
    """
    Extended shader with color support for terminals with color capabilities.
    """

    def __init__(
        self,
        *args,
        base_color: tuple[int, int, int] = (200, 180, 160),  # Skin tone
        highlight_color: tuple[int, int, int] = (255, 255, 240),
        shadow_color: tuple[int, int, int] = (80, 60, 50),
        **kwargs,
    ):
        """
        Initialize color shader.

        Args:
            base_color: RGB base color for surfaces
            highlight_color: RGB color for bright highlights
            shadow_color: RGB color for shadows
            *args, **kwargs: Passed to parent ASCIIShader
        """
        super().__init__(*args, **kwargs)
        self.base_color = np.array(base_color)
        self.highlight_color = np.array(highlight_color)
        self.shadow_color = np.array(shadow_color)

    def compute_color(self, intensity: float) -> tuple[int, int, int]:
        """
        Compute RGB color based on lighting intensity.

        Args:
            intensity: Lighting value (0-1)

        Returns:
            (r, g, b) color tuple
        """
        if intensity < 0.5:
            # Interpolate shadow to base
            t = intensity * 2
            color = self.shadow_color + t * (self.base_color - self.shadow_color)
        else:
            # Interpolate base to highlight
            t = (intensity - 0.5) * 2
            color = self.base_color + t * (self.highlight_color - self.base_color)

        return tuple(int(c) for c in np.clip(color, 0, 255))

    def ansi_256_color(self, r: int, g: int, b: int) -> int:
        """Convert RGB to nearest ANSI 256 color code."""
        # Use the 6x6x6 color cube (codes 16-231)
        r_idx = int(r / 255 * 5)
        g_idx = int(g / 255 * 5)
        b_idx = int(b / 255 * 5)
        return 16 + 36 * r_idx + 6 * g_idx + b_idx

    def ansi_truecolor(self, r: int, g: int, b: int) -> str:
        """Generate ANSI escape sequence for true color."""
        return f"\033[38;2;{r};{g};{b}m"

    def render_colored_char(self, char: str, intensity: float, use_truecolor: bool = True) -> str:
        """
        Render a character with color escape codes.

        Args:
            char: Character to render
            intensity: Lighting intensity
            use_truecolor: Use 24-bit color (vs 256 color)

        Returns:
            Character with ANSI color codes
        """
        r, g, b = self.compute_color(intensity)

        if use_truecolor:
            return f"{self.ansi_truecolor(r, g, b)}{char}\033[0m"
        else:
            color_code = self.ansi_256_color(r, g, b)
            return f"\033[38;5;{color_code}m{char}\033[0m"
