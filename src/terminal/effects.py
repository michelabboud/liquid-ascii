"""
Visual effects for ASCII rendering.

Provides particle systems, motion trails, glitch effects, scanlines, and more.
"""

import random
import time
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class Particle:
    """A single particle in the particle system."""

    x: float
    y: float
    vx: float  # Velocity x
    vy: float  # Velocity y
    char: str
    life: float  # Time to live
    age: float = 0.0


class ParticleSystem:
    """
    ASCII particle system for floating characters.

    Creates ambient particles that float around the render area.
    """

    def __init__(
        self,
        width: int,
        height: int,
        max_particles: int = 50,
        chars: str = ".:*+#",
    ):
        """
        Initialize particle system.

        Args:
            width: Render width
            height: Render height
            max_particles: Maximum number of particles
            chars: Characters to use for particles
        """
        self.width = width
        self.height = height
        self.max_particles = max_particles
        self.chars = chars
        self.particles: List[Particle] = []
        self.spawn_rate = 2.0  # Particles per second
        self.last_spawn = time.time()

    def update(self, dt: float):
        """Update all particles."""
        # Update existing particles
        for particle in self.particles[:]:
            particle.age += dt
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt

            # Remove dead particles
            if particle.age >= particle.life:
                self.particles.remove(particle)

        # Spawn new particles
        current_time = time.time()
        if (
            len(self.particles) < self.max_particles
            and current_time - self.last_spawn > 1.0 / self.spawn_rate
        ):
            self._spawn_particle()
            self.last_spawn = current_time

    def _spawn_particle(self):
        """Spawn a new particle."""
        particle = Particle(
            x=random.uniform(0, self.width),
            y=random.uniform(0, self.height),
            vx=random.uniform(-5, 5),
            vy=random.uniform(-10, -5),  # Float upward
            char=random.choice(self.chars),
            life=random.uniform(3.0, 6.0),
        )
        self.particles.append(particle)

    def render(self, frame: List[List[str]]) -> List[List[str]]:
        """
        Render particles onto frame.

        Args:
            frame: 2D list of characters (mutable)

        Returns:
            Modified frame
        """
        for particle in self.particles:
            x = int(particle.x)
            y = int(particle.y)

            # Check bounds
            if 0 <= y < len(frame) and 0 <= x < len(frame[0]):
                # Only draw if background (don't overwrite content)
                if frame[y][x] == " ":
                    # Fade based on age
                    alpha = 1.0 - (particle.age / particle.life)
                    if alpha > 0.3:  # Only draw if not too faded
                        frame[y][x] = particle.char

        return frame


class MotionTrail:
    """
    Motion trail effect.

    Leaves trailing characters behind moving objects.
    """

    def __init__(self, trail_length: int = 5):
        """
        Initialize motion trail.

        Args:
            trail_length: Number of trail frames to keep
        """
        self.trail_length = trail_length
        self.history: List[List[List[str]]] = []

    def add_frame(self, frame: List[List[str]]):
        """Add frame to history."""
        # Deep copy frame
        frame_copy = [row[:] for row in frame]
        self.history.append(frame_copy)

        # Keep only recent frames
        if len(self.history) > self.trail_length:
            self.history.pop(0)

    def render(self, frame: List[List[str]]) -> List[List[str]]:
        """
        Render trail effect.

        Args:
            frame: Current frame

        Returns:
            Frame with trail effect
        """
        if not self.history:
            return frame

        # Blend previous frames with decreasing opacity
        for i, old_frame in enumerate(self.history[:-1]):  # Skip most recent
            opacity = (i + 1) / len(self.history)

            for y in range(len(frame)):
                for x in range(len(frame[0])):
                    # If current frame is empty but old frame has content
                    if frame[y][x] == " " and old_frame[y][x] != " ":
                        # Show faded trail character
                        if opacity > 0.3:
                            # Use lighter characters for fade effect
                            trail_char = self._fade_char(old_frame[y][x], opacity)
                            frame[y][x] = trail_char

        return frame

    def _fade_char(self, char: str, opacity: float) -> str:
        """Convert character to faded version."""
        fade_map = {
            "@": "#",
            "#": "*",
            "*": "+",
            "+": ":",
            ":": ".",
            "%": "#",
            "O": "o",
            "o": ".",
        }
        # Fade based on opacity
        if opacity < 0.5:
            return fade_map.get(char, ".")
        return char


class GlitchEffect:
    """
    Digital glitch/distortion effect.

    Randomly corrupts parts of the display.
    """

    def __init__(self, intensity: float = 0.1):
        """
        Initialize glitch effect.

        Args:
            intensity: Glitch intensity (0-1)
        """
        self.intensity = intensity
        self.glitch_chars = "!@#$%^&*<>?/\\|"

    def render(self, frame: List[List[str]]) -> List[List[str]]:
        """Apply glitch effect to frame."""
        if random.random() > self.intensity:
            return frame  # No glitch this frame

        # Random glitch type
        glitch_type = random.choice(["horizontal", "vertical", "random", "invert"])

        if glitch_type == "horizontal":
            # Horizontal line corruption
            y = random.randint(0, len(frame) - 1)
            offset = random.randint(-5, 5)
            if offset != 0:
                frame[y] = frame[y][offset:] + frame[y][:offset]

        elif glitch_type == "vertical":
            # Vertical column shift
            x = random.randint(0, len(frame[0]) - 1)
            for y in range(len(frame)):
                if random.random() < 0.3:
                    frame[y][x] = random.choice(self.glitch_chars)

        elif glitch_type == "random":
            # Random character corruption
            for _ in range(random.randint(5, 20)):
                y = random.randint(0, len(frame) - 1)
                x = random.randint(0, len(frame[0]) - 1)
                frame[y][x] = random.choice(self.glitch_chars)

        elif glitch_type == "invert":
            # Invert a region
            y1 = random.randint(0, len(frame) - 5)
            y2 = min(y1 + random.randint(3, 8), len(frame))
            for y in range(y1, y2):
                frame[y] = list(reversed(frame[y]))

        return frame


class ScanlineEffect:
    """
    CRT monitor scanline effect.

    Simulates horizontal scanlines of old CRT displays.
    """

    def __init__(self, intensity: float = 0.5, speed: float = 1.0):
        """
        Initialize scanline effect.

        Args:
            intensity: Scanline visibility (0-1)
            speed: Scanline scroll speed
        """
        self.intensity = intensity
        self.speed = speed
        self.offset = 0.0

    def update(self, dt: float):
        """Update scanline position."""
        self.offset += self.speed * dt

    def render(self, frame: List[List[str]]) -> List[List[str]]:
        """Apply scanline effect."""
        for y in range(len(frame)):
            # Calculate scanline intensity for this row
            phase = (y + int(self.offset)) % 3
            if phase == 0 and random.random() < self.intensity:
                # Darken this scanline
                for x in range(len(frame[0])):
                    if frame[y][x] != " ":
                        # Dim the character (use lighter version)
                        frame[y][x] = self._dim_char(frame[y][x])

        return frame

    def _dim_char(self, char: str) -> str:
        """Convert character to dimmer version."""
        dim_map = {
            "@": "%",
            "#": "+",
            "%": ":",
            "*": ".",
            "+": ".",
            "O": "o",
            "G": "C",
            "C": "c",
        }
        return dim_map.get(char, char)


class MatrixRainEffect:
    """
    Matrix-style digital rain background effect.

    Falling characters in the background.
    """

    def __init__(self, width: int, height: int, density: float = 0.3):
        """
        Initialize matrix rain.

        Args:
            width: Display width
            height: Display height
            density: Rain density (0-1)
        """
        self.width = width
        self.height = height
        self.density = density
        self.columns: List[Optional[int]] = [None] * width  # Y position per column
        self.chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def update(self, dt: float):
        """Update rain positions."""
        for x in range(self.width):
            if self.columns[x] is None:
                # Maybe start new rain in this column
                if random.random() < self.density * dt:
                    self.columns[x] = 0
            else:
                # Advance rain
                self.columns[x] += int(30 * dt)  # Fall speed
                if self.columns[x] >= self.height:
                    self.columns[x] = None

    def render(self, frame: List[List[str]]) -> List[List[str]]:
        """Render matrix rain."""
        for x in range(min(self.width, len(frame[0]))):
            y_pos = self.columns[x]
            if y_pos is not None and 0 <= y_pos < self.height:
                # Only draw in background (don't overwrite content)
                if frame[y_pos][x] == " ":
                    frame[y_pos][x] = random.choice(self.chars)

                # Draw fading trail above
                for i in range(1, min(5, y_pos + 1)):
                    y_trail = y_pos - i
                    if 0 <= y_trail < self.height and frame[y_trail][x] == " ":
                        if random.random() < 0.5:  # Sparse trail
                            frame[y_trail][x] = "."

        return frame


class DepthOfFieldEffect:
    """
    Depth-of-field blur effect.

    Blurs characters based on distance from focus point.
    """

    def __init__(self, focus_distance: float = 3.5, blur_strength: float = 0.5):
        """
        Initialize depth-of-field effect.

        Args:
            focus_distance: Distance of focus plane
            blur_strength: Blur intensity (0-1)
        """
        self.focus_distance = focus_distance
        self.blur_strength = blur_strength

    def render(
        self, frame: List[List[str]], depth_buffer: Optional[List[List[float]]] = None
    ) -> List[List[str]]:
        """
        Apply depth-of-field blur.

        Args:
            frame: Frame to render
            depth_buffer: Optional depth information per pixel

        Returns:
            Blurred frame
        """
        if depth_buffer is None:
            # Without depth buffer, apply simple center-focused blur
            return self._simple_blur(frame)

        # Blur based on depth
        for y in range(len(frame)):
            for x in range(len(frame[0])):
                depth = depth_buffer[y][x]
                distance_from_focus = abs(depth - self.focus_distance)

                # Blur if far from focus
                if distance_from_focus > 0.5:
                    blur_amount = min(distance_from_focus * self.blur_strength, 1.0)
                    if random.random() < blur_amount:
                        frame[y][x] = self._blur_char(frame[y][x])

        return frame

    def _simple_blur(self, frame: List[List[str]]) -> List[List[str]]:
        """Simple radial blur from center."""
        cy = len(frame) // 2
        cx = len(frame[0]) // 2

        for y in range(len(frame)):
            for x in range(len(frame[0])):
                # Distance from center
                dx = x - cx
                dy = y - cy
                dist = math.sqrt(dx * dx + dy * dy) / max(cx, cy)

                # Blur edges
                if dist > 0.6:
                    blur_amount = (dist - 0.6) * self.blur_strength
                    if random.random() < blur_amount:
                        frame[y][x] = self._blur_char(frame[y][x])

        return frame

    def _blur_char(self, char: str) -> str:
        """Convert character to blurred version."""
        blur_map = {
            "@": "#",
            "#": "+",
            "%": ":",
            "*": ".",
            "+": ":",
            ":": ".",
            "G": "C",
            "C": ":",
            "O": "o",
            "o": ".",
        }
        return blur_map.get(char, ".")


class EffectsCompositor:
    """
    Compositor for combining multiple visual effects.

    Manages and applies effects in proper order.
    """

    def __init__(self, width: int, height: int):
        """
        Initialize effects compositor.

        Args:
            width: Render width
            height: Render height
        """
        self.width = width
        self.height = height

        # Available effects
        self.particles: Optional[ParticleSystem] = None
        self.trail: Optional[MotionTrail] = None
        self.glitch: Optional[GlitchEffect] = None
        self.scanlines: Optional[ScanlineEffect] = None
        self.matrix_rain: Optional[MatrixRainEffect] = None
        self.dof: Optional[DepthOfFieldEffect] = None

    def enable_particles(self, max_particles: int = 50):
        """Enable particle system."""
        self.particles = ParticleSystem(self.width, self.height, max_particles)

    def enable_trails(self, length: int = 5):
        """Enable motion trails."""
        self.trail = MotionTrail(length)

    def enable_glitch(self, intensity: float = 0.1):
        """Enable glitch effect."""
        self.glitch = GlitchEffect(intensity)

    def enable_scanlines(self, intensity: float = 0.5):
        """Enable scanline effect."""
        self.scanlines = ScanlineEffect(intensity)

    def enable_matrix_rain(self, density: float = 0.3):
        """Enable matrix rain background."""
        self.matrix_rain = MatrixRainEffect(self.width, self.height, density)

    def enable_depth_of_field(self, focus: float = 3.5, strength: float = 0.5):
        """Enable depth-of-field blur."""
        self.dof = DepthOfFieldEffect(focus, strength)

    def update(self, dt: float):
        """Update all effects."""
        if self.particles:
            self.particles.update(dt)
        if self.scanlines:
            self.scanlines.update(dt)
        if self.matrix_rain:
            self.matrix_rain.update(dt)

    def render(self, frame_str: str, depth_buffer: Optional[List[List[float]]] = None) -> str:
        """
        Apply all enabled effects to frame.

        Args:
            frame_str: Frame as string (newline-separated)
            depth_buffer: Optional depth information

        Returns:
            Processed frame string
        """
        # Convert string to 2D list
        lines = frame_str.split("\n")
        frame = [list(line) for line in lines]

        # Ensure all rows have same length
        max_len = max(len(row) for row in frame)
        for row in frame:
            while len(row) < max_len:
                row.append(" ")

        # Apply effects in order
        if self.matrix_rain:
            frame = self.matrix_rain.render(frame)

        if self.particles:
            frame = self.particles.render(frame)

        if self.trail:
            frame = self.trail.render(frame)

        if self.scanlines:
            frame = self.scanlines.render(frame)

        if self.dof:
            frame = self.dof.render(frame, depth_buffer)

        if self.glitch:
            frame = self.glitch.render(frame)

        # Add current frame to trail history
        if self.trail:
            self.trail.add_frame(frame)

        # Convert back to string
        return "\n".join("".join(row) for row in frame)
