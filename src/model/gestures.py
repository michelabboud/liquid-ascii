"""
Gesture animations for the character head.

Provides high-level gestures like nodding, shaking, tilting, and idle behaviors.
"""

import math
import time
from dataclasses import dataclass

from .animation import ease_in_out, ease_out


@dataclass
class GestureState:
    """State of an ongoing gesture animation."""

    name: str
    start_time: float
    duration: float
    params: dict

    def get_progress(self) -> float:
        """Get progress from 0 to 1."""
        elapsed = time.time() - self.start_time
        return min(elapsed / self.duration, 1.0)

    def is_complete(self) -> bool:
        """Check if gesture is complete."""
        return self.get_progress() >= 1.0


class GestureController:
    """
    Controller for gesture animations.

    Manages high-level gestures like nodding, shaking, and complex behaviors.
    """

    def __init__(self):
        """Initialize gesture controller."""
        self.current_gesture: GestureState | None = None
        self.idle_behavior_enabled = False
        self.idle_time = 0.0
        self.next_idle_action = 5.0  # Time until next idle behavior

    def nod(self, duration: float = 1.0, intensity: float = 1.0):
        """
        Start a nodding gesture (yes).

        Args:
            duration: Duration in seconds
            intensity: Gesture intensity (0-1)
        """
        self.current_gesture = GestureState(
            name="nod",
            start_time=time.time(),
            duration=duration,
            params={"intensity": intensity},
        )

    def shake(self, duration: float = 1.5, intensity: float = 1.0):
        """
        Start a shaking gesture (no).

        Args:
            duration: Duration in seconds
            intensity: Gesture intensity (0-1)
        """
        self.current_gesture = GestureState(
            name="shake",
            start_time=time.time(),
            duration=duration,
            params={"intensity": intensity},
        )

    def tilt(self, duration: float = 2.0, direction: str = "right", intensity: float = 1.0):
        """
        Start a head tilt gesture (curiosity/confusion).

        Args:
            duration: Duration in seconds
            direction: Tilt direction ("left" or "right")
            intensity: Gesture intensity (0-1)
        """
        self.current_gesture = GestureState(
            name="tilt",
            start_time=time.time(),
            duration=duration,
            params={"direction": direction, "intensity": intensity},
        )

    def look_at(self, x: float, y: float, duration: float = 0.5):
        """
        Look at a specific point (eye tracking).

        Args:
            x: Horizontal position (-1 to 1)
            y: Vertical position (-1 to 1)
            duration: Transition duration
        """
        self.current_gesture = GestureState(
            name="look_at",
            start_time=time.time(),
            duration=duration,
            params={"target_x": x, "target_y": y},
        )

    def stop_gesture(self):
        """Stop current gesture."""
        self.current_gesture = None

    def enable_idle_behavior(self, enabled: bool = True):
        """Enable or disable idle behaviors."""
        self.idle_behavior_enabled = enabled
        if enabled:
            self.idle_time = 0.0
            self.next_idle_action = 5.0 + (time.time() % 5.0)

    def update(self, dt: float) -> tuple[float, float, float, float, float]:
        """
        Update gesture state and return head transformations.

        Args:
            dt: Delta time in seconds

        Returns:
            Tuple of (tilt_x, tilt_y, tilt_z, eye_look_x, eye_look_y)
        """
        tilt_x = 0.0
        tilt_y = 0.0
        tilt_z = 0.0
        eye_look_x = 0.0
        eye_look_y = 0.0

        # Update active gesture
        if self.current_gesture:
            if self.current_gesture.is_complete():
                self.current_gesture = None
            else:
                progress = self.current_gesture.get_progress()
                tilt_x, tilt_y, tilt_z, eye_look_x, eye_look_y = self._evaluate_gesture(
                    self.current_gesture, progress
                )

        # Update idle behaviors
        if self.idle_behavior_enabled and not self.current_gesture:
            self.idle_time += dt
            if self.idle_time >= self.next_idle_action:
                self._trigger_idle_action()

        return tilt_x, tilt_y, tilt_z, eye_look_x, eye_look_y

    def _evaluate_gesture(
        self, gesture: GestureState, progress: float
    ) -> tuple[float, float, float, float, float]:
        """
        Evaluate gesture at given progress.

        Returns:
            Tuple of (tilt_x, tilt_y, tilt_z, eye_look_x, eye_look_y)
        """
        if gesture.name == "nod":
            return self._evaluate_nod(gesture, progress)
        elif gesture.name == "shake":
            return self._evaluate_shake(gesture, progress)
        elif gesture.name == "tilt":
            return self._evaluate_tilt(gesture, progress)
        elif gesture.name == "look_at":
            return self._evaluate_look_at(gesture, progress)
        else:
            return 0.0, 0.0, 0.0, 0.0, 0.0

    def _evaluate_nod(
        self, gesture: GestureState, progress: float
    ) -> tuple[float, float, float, float, float]:
        """Evaluate nodding gesture."""
        intensity = gesture.params["intensity"]

        # Nodding motion: down -> up -> neutral
        # Uses a sine wave for smooth motion
        angle = progress * math.pi * 2  # One complete cycle
        tilt_x = math.sin(angle) * 0.3 * intensity

        # Eyes follow the nod slightly
        eye_y = tilt_x * 0.5

        return tilt_x, 0.0, 0.0, 0.0, eye_y

    def _evaluate_shake(
        self, gesture: GestureState, progress: float
    ) -> tuple[float, float, float, float, float]:
        """Evaluate shaking gesture."""
        intensity = gesture.params["intensity"]

        # Shaking motion: left -> right -> left -> neutral
        # Uses sine wave with multiple cycles
        angle = progress * math.pi * 4  # Two complete cycles
        tilt_y = math.sin(angle) * 0.3 * intensity * (1.0 - progress)  # Decay over time

        # Eyes follow the shake
        eye_x = tilt_y * 0.8

        return 0.0, tilt_y, 0.0, eye_x, 0.0

    def _evaluate_tilt(
        self, gesture: GestureState, progress: float
    ) -> tuple[float, float, float, float, float]:
        """Evaluate head tilt gesture."""
        intensity = gesture.params["intensity"]
        direction = gesture.params["direction"]

        # Tilt motion: 0 -> max -> hold -> return
        if progress < 0.3:
            # Tilt in
            t = progress / 0.3
            t = ease_in_out(t)
            tilt_z = t * 0.4 * intensity
        elif progress < 0.7:
            # Hold
            tilt_z = 0.4 * intensity
        else:
            # Return
            t = (progress - 0.7) / 0.3
            t = ease_in_out(t)
            tilt_z = (1.0 - t) * 0.4 * intensity

        # Apply direction
        if direction == "left":
            tilt_z = -tilt_z

        return 0.0, 0.0, tilt_z, 0.0, 0.0

    def _evaluate_look_at(
        self, gesture: GestureState, progress: float
    ) -> tuple[float, float, float, float, float]:
        """Evaluate look-at gesture (eye tracking)."""
        target_x = gesture.params["target_x"]
        target_y = gesture.params["target_y"]

        # Smooth transition with ease-out
        t = ease_out(progress)

        eye_look_x = target_x * t
        eye_look_y = target_y * t

        return 0.0, 0.0, 0.0, eye_look_x, eye_look_y

    def _trigger_idle_action(self):
        """Trigger a random idle action."""
        import random

        # Reset idle timer
        self.idle_time = 0.0
        self.next_idle_action = random.uniform(5.0, 15.0)

        # Choose random idle behavior
        actions = [
            ("look_around", 0.4),
            ("blink_twice", 0.3),
            ("slight_nod", 0.2),
            ("tilt_curiosity", 0.1),
        ]

        # Weighted random choice
        total_weight = sum(w for _, w in actions)
        r = random.random() * total_weight
        cumulative = 0.0

        for action, weight in actions:
            cumulative += weight
            if r <= cumulative:
                self._execute_idle_action(action)
                break

    def _execute_idle_action(self, action: str):
        """Execute a specific idle action."""
        import random

        if action == "look_around":
            # Look in a random direction
            x = random.uniform(-0.4, 0.4)
            y = random.uniform(-0.3, 0.3)
            self.look_at(x, y, duration=0.8)

        elif action == "slight_nod":
            # Subtle nod
            self.nod(duration=0.8, intensity=0.5)

        elif action == "tilt_curiosity":
            # Brief tilt
            direction = random.choice(["left", "right"])
            self.tilt(duration=1.5, direction=direction, intensity=0.6)

        # blink_twice would be handled by the blink system


def create_gesture_sequence(*gestures) -> list:
    """
    Create a sequence of gestures to be played in order.

    Args:
        *gestures: Tuple of (gesture_name, params) tuples

    Returns:
        List of gesture commands

    Example:
        sequence = create_gesture_sequence(
            ("nod", {"duration": 1.0}),
            ("shake", {"duration": 1.5}),
            ("tilt", {"direction": "right"}),
        )
    """
    return list(gestures)


class GestureSequencer:
    """
    Play a sequence of gestures in order.

    Useful for complex animated behaviors.
    """

    def __init__(self, controller: GestureController):
        """
        Initialize sequencer.

        Args:
            controller: Gesture controller to use
        """
        self.controller = controller
        self.sequence: list = []
        self.current_index = 0

    def set_sequence(self, sequence: list):
        """
        Set gesture sequence.

        Args:
            sequence: List of (gesture_name, params) tuples
        """
        self.sequence = sequence
        self.current_index = 0

    def update(self):
        """Update sequencer - advance to next gesture when current completes."""
        if not self.sequence or self.current_index >= len(self.sequence):
            return

        # If no active gesture, start next one
        if not self.controller.current_gesture:
            gesture_name, params = self.sequence[self.current_index]

            # Call the appropriate gesture method
            if gesture_name == "nod":
                self.controller.nod(**params)
            elif gesture_name == "shake":
                self.controller.shake(**params)
            elif gesture_name == "tilt":
                self.controller.tilt(**params)
            elif gesture_name == "look_at":
                self.controller.look_at(**params)

            self.current_index += 1

    def is_complete(self) -> bool:
        """Check if sequence is complete."""
        return (
            self.current_index >= len(self.sequence)
            and not self.controller.current_gesture
        )

    def reset(self):
        """Reset sequence to beginning."""
        self.current_index = 0
