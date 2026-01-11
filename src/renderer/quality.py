"""
Quality presets for rendering performance optimization.

This module provides quality presets that control rendering parameters
to balance visual quality with performance.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class QualityLevel(Enum):
    """Quality level presets for rendering."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"
    AUTO = "auto"  # Adaptive quality based on FPS


@dataclass
class QualityPreset:
    """
    Quality preset configuration.

    Controls rendering parameters to balance quality and performance.
    """

    name: str
    max_steps: int  # Maximum raymarching steps
    epsilon: float  # Hit detection threshold
    max_distance: float  # Maximum ray distance
    normal_delta: float  # Delta for normal computation
    description: str

    def __str__(self) -> str:
        """Return human-readable description."""
        return (
            f"{self.name}: max_steps={self.max_steps}, "
            f"epsilon={self.epsilon}, quality={self.description}"
        )


# Predefined quality presets
QUALITY_PRESETS = {
    QualityLevel.LOW: QualityPreset(
        name="Low",
        max_steps=16,
        epsilon=0.01,  # Looser hit detection
        max_distance=20.0,
        normal_delta=0.01,
        description="Fastest performance, reduced visual quality (16 steps)",
    ),
    QualityLevel.MEDIUM: QualityPreset(
        name="Medium",
        max_steps=32,
        epsilon=0.005,
        max_distance=20.0,
        normal_delta=0.005,
        description="Balanced performance and quality (32 steps)",
    ),
    QualityLevel.HIGH: QualityPreset(
        name="High",
        max_steps=50,  # Current default
        epsilon=0.001,
        max_distance=20.0,
        normal_delta=0.001,
        description="High quality, slower performance (50 steps)",
    ),
    QualityLevel.ULTRA: QualityPreset(
        name="Ultra",
        max_steps=80,
        epsilon=0.0005,
        max_distance=20.0,
        normal_delta=0.0005,
        description="Maximum quality, slowest performance (80 steps)",
    ),
}


class AdaptiveQualityController:
    """
    Adaptive quality controller that adjusts quality based on FPS.

    Automatically reduces quality when FPS drops below target,
    and increases quality when performance improves.
    """

    def __init__(
        self,
        target_fps: float = 15.0,
        initial_quality: QualityLevel = QualityLevel.HIGH,
    ):
        """
        Initialize adaptive quality controller.

        Args:
            target_fps: Target frames per second
            initial_quality: Starting quality level
        """
        self.target_fps = target_fps
        self.current_quality = initial_quality
        self.fps_history: list[float] = []
        self.history_size = 10  # Number of frames to average

        # Thresholds for quality adjustment
        self.downgrade_threshold = 0.7  # Drop quality at 70% of target FPS
        self.upgrade_threshold = 1.1  # Increase quality at 110% of target FPS

    def update(self, current_fps: float) -> Optional[QualityLevel]:
        """
        Update quality based on current FPS.

        Args:
            current_fps: Current frames per second

        Returns:
            New quality level if changed, None otherwise
        """
        self.fps_history.append(current_fps)
        if len(self.fps_history) > self.history_size:
            self.fps_history.pop(0)

        # Need enough history to make decisions
        if len(self.fps_history) < self.history_size:
            return None

        avg_fps = sum(self.fps_history) / len(self.fps_history)
        fps_ratio = avg_fps / self.target_fps

        # Determine if we should change quality
        old_quality = self.current_quality

        if fps_ratio < self.downgrade_threshold:
            # Performance is poor, reduce quality
            if self.current_quality == QualityLevel.ULTRA:
                self.current_quality = QualityLevel.HIGH
            elif self.current_quality == QualityLevel.HIGH:
                self.current_quality = QualityLevel.MEDIUM
            elif self.current_quality == QualityLevel.MEDIUM:
                self.current_quality = QualityLevel.LOW
            # Already at LOW, can't go lower

        elif fps_ratio > self.upgrade_threshold:
            # Performance is good, increase quality
            if self.current_quality == QualityLevel.LOW:
                self.current_quality = QualityLevel.MEDIUM
            elif self.current_quality == QualityLevel.MEDIUM:
                self.current_quality = QualityLevel.HIGH
            elif self.current_quality == QualityLevel.HIGH:
                self.current_quality = QualityLevel.ULTRA
            # Already at ULTRA, can't go higher

        # Clear history when quality changes to avoid oscillation
        if old_quality != self.current_quality:
            self.fps_history.clear()
            return self.current_quality

        return None

    def get_current_preset(self) -> QualityPreset:
        """Get the current quality preset."""
        return QUALITY_PRESETS[self.current_quality]


def get_quality_preset(quality: QualityLevel) -> QualityPreset:
    """
    Get quality preset for a given quality level.

    Args:
        quality: Quality level enum value

    Returns:
        Quality preset configuration
    """
    if quality == QualityLevel.AUTO:
        # Default to HIGH for auto mode (will be adjusted dynamically)
        return QUALITY_PRESETS[QualityLevel.HIGH]
    return QUALITY_PRESETS[quality]
