"""
Animation utilities for smooth, organic movement.

Provides easing functions, interpolation, and organic noise
for creating fluid, lifelike animations.
"""

import math
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple


def smoothstep(t: float) -> float:
    """
    Hermite interpolation - smooth acceleration/deceleration.

    Args:
        t: Input value (0-1)

    Returns:
        Smoothly interpolated value
    """
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def smootherstep(t: float) -> float:
    """
    Ken Perlin's improved smoothstep with zero second derivative at endpoints.

    Args:
        t: Input value (0-1)

    Returns:
        Very smooth interpolated value
    """
    t = max(0.0, min(1.0, t))
    return t * t * t * (t * (t * 6 - 15) + 10)


def lerp(a: float, b: float, t: float) -> float:
    """
    Linear interpolation with optional smoothing.

    Args:
        a: Start value
        b: End value
        t: Interpolation factor (0-1)

    Returns:
        Interpolated value
    """
    return a + (b - a) * t


def ease_in(t: float, power: float = 2.0) -> float:
    """Ease in (slow start)."""
    return t ** power


def ease_out(t: float, power: float = 2.0) -> float:
    """Ease out (slow end)."""
    return 1 - (1 - t) ** power


def ease_in_out(t: float, power: float = 2.0) -> float:
    """Ease in and out (slow start and end)."""
    if t < 0.5:
        return (2 ** (power - 1)) * (t ** power)
    else:
        return 1 - ((-2 * t + 2) ** power) / 2


def bounce_out(t: float) -> float:
    """Bouncy easing."""
    n1, d1 = 7.5625, 2.75

    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375


def elastic_out(t: float) -> float:
    """Elastic/springy easing."""
    c4 = (2 * math.pi) / 3

    if t <= 0:
        return 0
    if t >= 1:
        return 1

    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def organic_noise(t: float) -> Tuple[float, float, float]:
    """
    Generate organic noise for subtle idle movement.

    Combines multiple sine waves at different frequencies
    to create natural-looking micro-movements.

    Args:
        t: Time value

    Returns:
        (x, y, z) displacement tuple
    """
    return (
        math.sin(t * 0.5) * 0.015 + math.sin(t * 1.3) * 0.008 + math.sin(t * 2.7) * 0.003,
        math.sin(t * 0.7 + 0.5) * 0.012 + math.sin(t * 1.9 + 1.2) * 0.005,
        math.sin(t * 0.4 + 1.0) * 0.010 + math.sin(t * 1.1 + 0.8) * 0.004,
    )


def breathing_motion(t: float, rate: float = 0.2) -> float:
    """
    Subtle breathing motion.

    Args:
        t: Time value
        rate: Breathing rate (cycles per second)

    Returns:
        Breathing offset value
    """
    cycle = t * rate * 2 * math.pi
    # Asymmetric: slower inhale, faster exhale
    return (math.sin(cycle) + 0.3 * math.sin(2 * cycle)) * 0.02


def blink_pattern(t: float, interval: float = 4.0, duration: float = 0.15) -> float:
    """
    Natural blink animation.

    Generates periodic blinks with natural timing.

    Args:
        t: Time value
        interval: Average seconds between blinks
        duration: Blink duration in seconds

    Returns:
        Blink amount (0 = open, 1 = closed)
    """
    # Add some variation to timing
    variation = math.sin(t * 0.3) * 0.5
    effective_interval = interval + variation

    cycle = t % effective_interval

    # Blink occurs at end of cycle
    blink_start = effective_interval - duration

    if cycle < blink_start:
        return 0.0

    # Progress through blink (0 to 1 to 0)
    blink_progress = (cycle - blink_start) / duration

    # Quick close, slightly slower open
    if blink_progress < 0.4:
        return smoothstep(blink_progress / 0.4)
    else:
        return 1.0 - smoothstep((blink_progress - 0.4) / 0.6)


def double_blink_pattern(t: float, interval: float = 5.0) -> float:
    """
    Occasional double-blink for more natural look.

    Args:
        t: Time value
        interval: Seconds between blink sequences

    Returns:
        Blink amount (0 = open, 1 = closed)
    """
    cycle = t % interval

    # Single blink at 0.8 into cycle
    if 0.8 <= cycle < 0.95:
        return smoothstep((cycle - 0.8) / 0.075) * (1 - smoothstep((cycle - 0.875) / 0.075))

    # Occasional double blink (every ~3 cycles)
    if int(t / interval) % 3 == 0:
        if 1.0 <= cycle < 1.15:
            return smoothstep((cycle - 1.0) / 0.075) * (1 - smoothstep((cycle - 1.075) / 0.075))

    return 0.0


@dataclass
class AnimationTarget:
    """A single animated value target."""
    start_value: float
    end_value: float
    start_time: float
    duration: float
    easing: Callable[[float], float] = smoothstep

    def get_value(self, current_time: float) -> float:
        """Get the current interpolated value."""
        if current_time < self.start_time:
            return self.start_value
        if current_time >= self.start_time + self.duration:
            return self.end_value

        t = (current_time - self.start_time) / self.duration
        eased_t = self.easing(t)
        return lerp(self.start_value, self.end_value, eased_t)

    def is_complete(self, current_time: float) -> bool:
        """Check if animation has completed."""
        return current_time >= self.start_time + self.duration


@dataclass
class AnimationController:
    """
    Manages multiple animated values with smooth transitions.
    """
    values: Dict[str, float] = field(default_factory=dict)
    targets: Dict[str, AnimationTarget] = field(default_factory=dict)
    _start_time: float = field(default_factory=time.time)

    def set_value(self, name: str, value: float):
        """Set a value immediately without animation."""
        self.values[name] = value
        if name in self.targets:
            del self.targets[name]

    def get_value(self, name: str, default: float = 0.0) -> float:
        """Get current value (with animation applied)."""
        return self.values.get(name, default)

    def animate_to(
        self,
        name: str,
        target_value: float,
        duration: float = 0.2,
        easing: Callable[[float], float] = smoothstep,
    ):
        """
        Animate a value to a target.

        Args:
            name: Value name
            target_value: Target value
            duration: Animation duration in seconds
            easing: Easing function
        """
        current_value = self.values.get(name, 0.0)
        current_time = time.time() - self._start_time

        self.targets[name] = AnimationTarget(
            start_value=current_value,
            end_value=target_value,
            start_time=current_time,
            duration=duration,
            easing=easing,
        )

    def update(self) -> Dict[str, float]:
        """
        Update all animated values.

        Returns:
            Dict of all current values
        """
        current_time = time.time() - self._start_time
        completed = []

        for name, target in self.targets.items():
            self.values[name] = target.get_value(current_time)
            if target.is_complete(current_time):
                completed.append(name)

        for name in completed:
            del self.targets[name]

        return self.values

    def is_animating(self, name: Optional[str] = None) -> bool:
        """Check if a value (or any value) is currently animating."""
        if name is not None:
            return name in self.targets
        return len(self.targets) > 0

    def get_elapsed_time(self) -> float:
        """Get time since controller was created."""
        return time.time() - self._start_time
