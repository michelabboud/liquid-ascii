"""
Interactive keyboard input handler for real-time control.

Provides non-blocking keyboard input with command processing for
interactive control during animation playback.
"""

from dataclasses import dataclass
from enum import Enum, auto

from blessed import Terminal


class InputCommand(Enum):
    """Commands that can be triggered by keyboard input."""
    # Navigation
    QUIT = auto()
    PAUSE = auto()
    HELP = auto()

    # Head movement
    TILT_UP = auto()
    TILT_DOWN = auto()
    TURN_LEFT = auto()
    TURN_RIGHT = auto()
    LEAN_LEFT = auto()
    LEAN_RIGHT = auto()

    # Expressions (1-9)
    EXPRESSION_1 = auto()  # Neutral
    EXPRESSION_2 = auto()  # Happy
    EXPRESSION_3 = auto()  # Sad
    EXPRESSION_4 = auto()  # Angry
    EXPRESSION_5 = auto()  # Surprised
    EXPRESSION_6 = auto()  # Confused
    EXPRESSION_7 = auto()  # Tired
    EXPRESSION_8 = auto()  # Wink
    EXPRESSION_9 = auto()  # Thinking

    # Visual controls
    CYCLE_COLOR_SCHEME = auto()
    CYCLE_RAINBOW = auto()

    # Performance
    FPS_INCREASE = auto()
    FPS_DECREASE = auto()


@dataclass
class InputEvent:
    """Represents a processed input event."""
    command: InputCommand
    value: float | None = None  # For analog controls like FPS adjustment


class InteractiveInputHandler:
    """
    Non-blocking keyboard input handler for interactive control.

    Uses blessed terminal for cross-platform keyboard handling.
    """

    def __init__(self, term: Terminal | None = None):
        """
        Initialize input handler.

        Args:
            term: Blessed Terminal instance (creates new if None)
        """
        self.term = term or Terminal()
        self._enabled = True
        self._show_help = False

        # Key mapping
        self._key_map: dict[str, InputCommand] = {
            # Quit
            'q': InputCommand.QUIT,
            'Q': InputCommand.QUIT,

            # Pause/Help
            ' ': InputCommand.PAUSE,
            'h': InputCommand.HELP,
            'H': InputCommand.HELP,
            '?': InputCommand.HELP,

            # Arrow keys for head movement
            'KEY_UP': InputCommand.TILT_UP,
            'KEY_DOWN': InputCommand.TILT_DOWN,
            'KEY_LEFT': InputCommand.TURN_LEFT,
            'KEY_RIGHT': InputCommand.TURN_RIGHT,

            # Q/E for lean
            'e': InputCommand.LEAN_RIGHT,
            'E': InputCommand.LEAN_RIGHT,

            # Number keys for expressions
            '1': InputCommand.EXPRESSION_1,
            '2': InputCommand.EXPRESSION_2,
            '3': InputCommand.EXPRESSION_3,
            '4': InputCommand.EXPRESSION_4,
            '5': InputCommand.EXPRESSION_5,
            '6': InputCommand.EXPRESSION_6,
            '7': InputCommand.EXPRESSION_7,
            '8': InputCommand.EXPRESSION_8,
            '9': InputCommand.EXPRESSION_9,

            # Visual controls
            'c': InputCommand.CYCLE_COLOR_SCHEME,
            'C': InputCommand.CYCLE_COLOR_SCHEME,
            'r': InputCommand.CYCLE_RAINBOW,
            'R': InputCommand.CYCLE_RAINBOW,

            # FPS adjustment
            '+': InputCommand.FPS_INCREASE,
            '=': InputCommand.FPS_INCREASE,  # + without shift
            '-': InputCommand.FPS_DECREASE,
            '_': InputCommand.FPS_DECREASE,
        }

        # Expression mapping (for display)
        self._expression_names = [
            "neutral", "happy", "sad", "angry", "surprised",
            "confused", "tired", "wink", "thinking"
        ]

    def poll_input(self, timeout: float = 0.0) -> InputEvent | None:
        """
        Poll for keyboard input (non-blocking).

        Args:
            timeout: Maximum time to wait for input in seconds (0 = immediate)

        Returns:
            InputEvent if key pressed, None otherwise
        """
        if not self._enabled:
            return None

        # Get key with timeout (in seconds)
        key = self.term.inkey(timeout=timeout)

        if not key:
            return None

        # Special handling for 'q' as lean left
        if key.lower() == 'q' and key == 'q':
            # Check if user meant lean left or quit
            # For now, lean left requires lowercase 'q', quit is uppercase or ESC
            return InputEvent(InputCommand.LEAN_LEFT)

        # Check for ESC key (quit)
        if key.code == self.term.KEY_ESCAPE or key == '\x1b':
            return InputEvent(InputCommand.QUIT)

        # Map key to command
        key_str = key.name if key.is_sequence else str(key)
        command = self._key_map.get(key_str)

        if command:
            return InputEvent(command)

        return None

    def get_help_text(self) -> str:
        """Get help text showing all available controls."""
        return """
╔════════════════════════════════════════════════════════════╗
║              INTERACTIVE CONTROLS HELP                      ║
╠════════════════════════════════════════════════════════════╣
║  ESC, Q       Quit                                         ║
║  SPACE        Pause/Resume                                 ║
║  H, ?         Toggle this help                             ║
╠════════════════════════════════════════════════════════════╣
║  ARROW KEYS   Move head (↑↓ tilt, ←→ turn)                ║
║  q / e        Lean left / right                            ║
╠════════════════════════════════════════════════════════════╣
║  1-9          Change expression:                           ║
║               1=Neutral  2=Happy    3=Sad                  ║
║               4=Angry    5=Surprised 6=Confused            ║
║               7=Tired    8=Wink     9=Thinking             ║
╠════════════════════════════════════════════════════════════╣
║  C            Cycle color schemes                          ║
║  R            Cycle rainbow modes                          ║
║  +/-          Increase/Decrease FPS                        ║
╚════════════════════════════════════════════════════════════╝
""".strip()

    def toggle_help(self):
        """Toggle help display."""
        self._show_help = not self._show_help

    def is_help_visible(self) -> bool:
        """Check if help is currently visible."""
        return self._show_help

    def enable(self):
        """Enable input handling."""
        self._enabled = True

    def disable(self):
        """Disable input handling."""
        self._enabled = False

    def is_enabled(self) -> bool:
        """Check if input handling is enabled."""
        return self._enabled

    def get_expression_name(self, command: InputCommand) -> str | None:
        """
        Get expression name for an expression command.

        Args:
            command: Input command

        Returns:
            Expression name or None
        """
        if command == InputCommand.EXPRESSION_1:
            return self._expression_names[0]
        elif command == InputCommand.EXPRESSION_2:
            return self._expression_names[1]
        elif command == InputCommand.EXPRESSION_3:
            return self._expression_names[2]
        elif command == InputCommand.EXPRESSION_4:
            return self._expression_names[3]
        elif command == InputCommand.EXPRESSION_5:
            return self._expression_names[4]
        elif command == InputCommand.EXPRESSION_6:
            return self._expression_names[5]
        elif command == InputCommand.EXPRESSION_7:
            return self._expression_names[6]
        elif command == InputCommand.EXPRESSION_8:
            return self._expression_names[7]
        elif command == InputCommand.EXPRESSION_9:
            return self._expression_names[8]
        return None


class InteractiveController:
    """
    Controller that processes input events and updates application state.
    """

    def __init__(self, input_handler: InteractiveInputHandler):
        """
        Initialize controller.

        Args:
            input_handler: Input handler instance
        """
        self.input_handler = input_handler
        self.paused = False
        self.should_quit = False

        # Head orientation state
        self.head_tilt_x = 0.0
        self.head_tilt_y = 0.0
        self.head_tilt_z = 0.0

        # Tilt increments
        self.tilt_speed = 0.1
        self.max_tilt = 0.5

    def process_input(self) -> bool:
        """
        Process pending input events.

        Returns:
            True if should continue, False if should quit
        """
        event = self.input_handler.poll_input(timeout=0.001)

        if not event:
            return not self.should_quit

        # Process command
        if event.command == InputCommand.QUIT:
            self.should_quit = True
            return False

        elif event.command == InputCommand.PAUSE:
            self.paused = not self.paused

        elif event.command == InputCommand.HELP:
            self.input_handler.toggle_help()

        # Head movement
        elif event.command == InputCommand.TILT_UP:
            self.head_tilt_x = max(-self.max_tilt, self.head_tilt_x - self.tilt_speed)

        elif event.command == InputCommand.TILT_DOWN:
            self.head_tilt_x = min(self.max_tilt, self.head_tilt_x + self.tilt_speed)

        elif event.command == InputCommand.TURN_LEFT:
            self.head_tilt_y = max(-self.max_tilt, self.head_tilt_y - self.tilt_speed)

        elif event.command == InputCommand.TURN_RIGHT:
            self.head_tilt_y = min(self.max_tilt, self.head_tilt_y + self.tilt_speed)

        elif event.command == InputCommand.LEAN_LEFT:
            self.head_tilt_z = max(-self.max_tilt, self.head_tilt_z - self.tilt_speed)

        elif event.command == InputCommand.LEAN_RIGHT:
            self.head_tilt_z = min(self.max_tilt, self.head_tilt_z + self.tilt_speed)

        return True

    def get_head_tilt(self) -> tuple[float, float, float]:
        """Get current head tilt values."""
        return (self.head_tilt_x, self.head_tilt_y, self.head_tilt_z)

    def reset_head_tilt(self):
        """Reset head to neutral position."""
        self.head_tilt_x = 0.0
        self.head_tilt_y = 0.0
        self.head_tilt_z = 0.0

    def is_paused(self) -> bool:
        """Check if currently paused."""
        return self.paused
