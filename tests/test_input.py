"""Tests for interactive input handling."""

from unittest.mock import Mock, patch

import pytest

from src.terminal.input import (
    InputCommand,
    InputEvent,
    InteractiveController,
    InteractiveInputHandler,
)


class TestInputCommand:
    """Tests for InputCommand enum."""

    def test_all_commands_defined(self):
        """All expected commands are defined."""
        expected_commands = [
            "QUIT",
            "PAUSE",
            "HELP",
            "TILT_UP",
            "TILT_DOWN",
            "TURN_LEFT",
            "TURN_RIGHT",
            "LEAN_LEFT",
            "LEAN_RIGHT",
            "EXPRESSION_1",
            "EXPRESSION_2",
            "EXPRESSION_3",
            "EXPRESSION_4",
            "EXPRESSION_5",
            "EXPRESSION_6",
            "EXPRESSION_7",
            "EXPRESSION_8",
            "EXPRESSION_9",
            "CYCLE_COLOR_SCHEME",
            "CYCLE_RAINBOW",
            "FPS_INCREASE",
            "FPS_DECREASE",
        ]
        for cmd in expected_commands:
            assert hasattr(InputCommand, cmd)


class TestInputEvent:
    """Tests for InputEvent dataclass."""

    def test_input_event_creation(self):
        """InputEvent can be created."""
        event = InputEvent(command=InputCommand.QUIT, value=None)
        assert event.command == InputCommand.QUIT
        assert event.value is None

    def test_input_event_with_value(self):
        """InputEvent can have value."""
        event = InputEvent(command=InputCommand.FPS_INCREASE, value=2.0)
        assert event.value == 2.0


class TestInteractiveInputHandler:
    """Tests for InteractiveInputHandler."""

    def test_handler_initialization(self):
        """Handler initializes with default state."""
        with patch("src.terminal.input.Terminal"):
            handler = InteractiveInputHandler()
            assert handler._enabled
            assert not handler._show_help

    def test_handler_with_custom_terminal(self):
        """Handler can use custom terminal."""
        mock_term = Mock()
        handler = InteractiveInputHandler(term=mock_term)
        assert handler.term == mock_term

    def test_key_map_completeness(self):
        """Key map includes all expected keys."""
        with patch("src.terminal.input.Terminal"):
            handler = InteractiveInputHandler()

            # Check critical keys are mapped
            assert "q" in handler._key_map or "Q" in handler._key_map
            assert " " in handler._key_map  # Space
            assert "KEY_UP" in handler._key_map
            assert "KEY_DOWN" in handler._key_map
            assert "KEY_LEFT" in handler._key_map
            assert "KEY_RIGHT" in handler._key_map
            assert "1" in handler._key_map
            assert "+" in handler._key_map
            assert "-" in handler._key_map

    def test_expression_names(self):
        """Expression names list is complete."""
        with patch("src.terminal.input.Terminal"):
            handler = InteractiveInputHandler()
            assert len(handler._expression_names) == 9
            assert "neutral" in handler._expression_names
            assert "happy" in handler._expression_names

    def test_get_expression_name(self):
        """Can get expression name from command."""
        with patch("src.terminal.input.Terminal"):
            handler = InteractiveInputHandler()

            assert handler.get_expression_name(InputCommand.EXPRESSION_1) == "neutral"
            assert handler.get_expression_name(InputCommand.EXPRESSION_2) == "happy"
            assert handler.get_expression_name(InputCommand.EXPRESSION_9) == "thinking"
            assert handler.get_expression_name(InputCommand.QUIT) is None

    def test_get_help_text(self):
        """Help text is available."""
        with patch("src.terminal.input.Terminal"):
            handler = InteractiveInputHandler()
            help_text = handler.get_help_text()

            assert "INTERACTIVE CONTROLS HELP" in help_text
            assert "ARROW KEYS" in help_text
            assert "1-9" in help_text
            assert "ESC" in help_text

    def test_toggle_help(self):
        """Help can be toggled."""
        with patch("src.terminal.input.Terminal"):
            handler = InteractiveInputHandler()

            assert not handler.is_help_visible()
            handler.toggle_help()
            assert handler.is_help_visible()
            handler.toggle_help()
            assert not handler.is_help_visible()

    def test_enable_disable(self):
        """Handler can be enabled/disabled."""
        with patch("src.terminal.input.Terminal"):
            handler = InteractiveInputHandler()

            assert handler.is_enabled()
            handler.disable()
            assert not handler.is_enabled()
            handler.enable()
            assert handler.is_enabled()

    def test_poll_input_when_disabled(self):
        """Polling when disabled returns None."""
        with patch("src.terminal.input.Terminal") as mock_term_class:
            mock_term = Mock()
            mock_term_class.return_value = mock_term
            handler = InteractiveInputHandler()
            handler.disable()

            result = handler.poll_input()
            assert result is None

    def test_poll_input_no_key(self):
        """Polling with no key pressed returns None."""
        with patch("src.terminal.input.Terminal") as mock_term_class:
            mock_term = Mock()
            mock_term.inkey.return_value = ""
            mock_term_class.return_value = mock_term
            handler = InteractiveInputHandler()

            result = handler.poll_input(timeout=0.0)
            assert result is None

    def test_poll_input_escape_key(self):
        """ESC key triggers QUIT command."""
        with patch("src.terminal.input.Terminal") as mock_term_class:
            mock_term = Mock()
            mock_key = Mock()
            mock_key.code = 27  # ESC key code
            mock_key.__str__ = lambda self: "\x1b"
            mock_term.KEY_ESCAPE = 27
            mock_term.inkey.return_value = mock_key
            mock_term_class.return_value = mock_term
            handler = InteractiveInputHandler()

            result = handler.poll_input()
            assert result is not None
            assert result.command == InputCommand.QUIT

    def test_poll_input_number_key(self):
        """Number keys trigger expression commands."""
        with patch("src.terminal.input.Terminal") as mock_term_class:
            mock_term = Mock()
            mock_key = Mock()
            mock_key.is_sequence = False
            mock_key.__str__ = lambda self: "2"
            mock_term.inkey.return_value = mock_key
            mock_term_class.return_value = mock_term
            handler = InteractiveInputHandler()

            result = handler.poll_input()
            assert result is not None
            assert result.command == InputCommand.EXPRESSION_2

    def test_poll_input_arrow_key(self):
        """Arrow keys trigger movement commands."""
        with patch("src.terminal.input.Terminal") as mock_term_class:
            mock_term = Mock()
            mock_key = Mock()
            mock_key.is_sequence = True
            mock_key.name = "KEY_UP"
            mock_term.inkey.return_value = mock_key
            mock_term_class.return_value = mock_term
            handler = InteractiveInputHandler()

            result = handler.poll_input()
            assert result is not None
            assert result.command == InputCommand.TILT_UP


class TestInteractiveController:
    """Tests for InteractiveController."""

    def test_controller_initialization(self):
        """Controller initializes with default state."""
        with patch("src.terminal.input.Terminal"):
            handler = InteractiveInputHandler()
            controller = InteractiveController(handler)

            assert not controller.paused
            assert not controller.should_quit
            assert controller.head_tilt_x == 0.0
            assert controller.head_tilt_y == 0.0
            assert controller.head_tilt_z == 0.0

    def test_get_head_tilt(self):
        """Can get head tilt values."""
        with patch("src.terminal.input.Terminal"):
            handler = InteractiveInputHandler()
            controller = InteractiveController(handler)

            tilt = controller.get_head_tilt()
            assert tilt == (0.0, 0.0, 0.0)

    def test_reset_head_tilt(self):
        """Can reset head tilt to neutral."""
        with patch("src.terminal.input.Terminal"):
            handler = InteractiveInputHandler()
            controller = InteractiveController(handler)

            controller.head_tilt_x = 0.5
            controller.head_tilt_y = -0.3
            controller.head_tilt_z = 0.2

            controller.reset_head_tilt()

            assert controller.head_tilt_x == 0.0
            assert controller.head_tilt_y == 0.0
            assert controller.head_tilt_z == 0.0

    def test_is_paused(self):
        """Can check pause state."""
        with patch("src.terminal.input.Terminal"):
            handler = InteractiveInputHandler()
            controller = InteractiveController(handler)

            assert not controller.is_paused()
            controller.paused = True
            assert controller.is_paused()

    def test_process_input_no_event(self):
        """Processing with no event continues."""
        with patch("src.terminal.input.Terminal") as mock_term_class:
            mock_term = Mock()
            mock_term.inkey.return_value = ""
            mock_term_class.return_value = mock_term
            handler = InteractiveInputHandler()
            controller = InteractiveController(handler)

            result = controller.process_input()
            assert result is True
            assert not controller.should_quit

    def test_process_input_quit_command(self):
        """QUIT command sets should_quit."""
        with patch("src.terminal.input.Terminal") as mock_term_class:
            mock_term = Mock()
            mock_key = Mock()
            mock_key.code = 27
            mock_key.__str__ = lambda self: "\x1b"
            mock_term.KEY_ESCAPE = 27
            mock_term.inkey.return_value = mock_key
            mock_term_class.return_value = mock_term
            handler = InteractiveInputHandler()
            controller = InteractiveController(handler)

            result = controller.process_input()
            assert result is False
            assert controller.should_quit

    def test_process_input_pause_command(self):
        """PAUSE command toggles pause state."""
        with patch("src.terminal.input.Terminal") as mock_term_class:
            mock_term = Mock()
            mock_key = Mock()
            mock_key.is_sequence = False
            mock_key.__str__ = lambda self: " "
            mock_term.inkey.return_value = mock_key
            mock_term_class.return_value = mock_term
            handler = InteractiveInputHandler()
            controller = InteractiveController(handler)

            assert not controller.paused
            controller.process_input()
            assert controller.paused
            controller.process_input()
            assert not controller.paused

    def test_process_input_help_command(self):
        """HELP command toggles help display."""
        with patch("src.terminal.input.Terminal") as mock_term_class:
            mock_term = Mock()
            mock_key = Mock()
            mock_key.is_sequence = False
            mock_key.__str__ = lambda self: "h"
            mock_term.inkey.return_value = mock_key
            mock_term_class.return_value = mock_term
            handler = InteractiveInputHandler()
            controller = InteractiveController(handler)

            assert not handler.is_help_visible()
            controller.process_input()
            assert handler.is_help_visible()

    def test_process_input_tilt_up(self):
        """TILT_UP adjusts head tilt."""
        with patch("src.terminal.input.Terminal") as mock_term_class:
            mock_term = Mock()
            mock_key = Mock()
            mock_key.is_sequence = True
            mock_key.name = "KEY_UP"
            mock_term.inkey.return_value = mock_key
            mock_term_class.return_value = mock_term
            handler = InteractiveInputHandler()
            controller = InteractiveController(handler)

            initial_tilt = controller.head_tilt_x
            controller.process_input()
            # Tilt up should decrease X (negative is up)
            assert controller.head_tilt_x < initial_tilt

    def test_process_input_tilt_down(self):
        """TILT_DOWN adjusts head tilt."""
        with patch("src.terminal.input.Terminal") as mock_term_class:
            mock_term = Mock()
            mock_key = Mock()
            mock_key.is_sequence = True
            mock_key.name = "KEY_DOWN"
            mock_term.inkey.return_value = mock_key
            mock_term_class.return_value = mock_term
            handler = InteractiveInputHandler()
            controller = InteractiveController(handler)

            initial_tilt = controller.head_tilt_x
            controller.process_input()
            # Tilt down should increase X
            assert controller.head_tilt_x > initial_tilt

    def test_head_tilt_respects_max(self):
        """Head tilt doesn't exceed max_tilt."""
        with patch("src.terminal.input.Terminal") as mock_term_class:
            mock_term = Mock()
            mock_key = Mock()
            mock_key.is_sequence = True
            mock_key.name = "KEY_UP"
            mock_term.inkey.return_value = mock_key
            mock_term_class.return_value = mock_term
            handler = InteractiveInputHandler()
            controller = InteractiveController(handler)

            # Press up many times
            for _ in range(20):
                controller.process_input()

            # Should be clamped to max_tilt
            assert controller.head_tilt_x >= -controller.max_tilt
            assert controller.head_tilt_x <= controller.max_tilt

    def test_turn_left(self):
        """TURN_LEFT adjusts Y tilt."""
        with patch("src.terminal.input.Terminal") as mock_term_class:
            mock_term = Mock()
            mock_key = Mock()
            mock_key.is_sequence = True
            mock_key.name = "KEY_LEFT"
            mock_term.inkey.return_value = mock_key
            mock_term_class.return_value = mock_term
            handler = InteractiveInputHandler()
            controller = InteractiveController(handler)

            controller.process_input()
            assert controller.head_tilt_y < 0.0

    def test_turn_right(self):
        """TURN_RIGHT adjusts Y tilt."""
        with patch("src.terminal.input.Terminal") as mock_term_class:
            mock_term = Mock()
            mock_key = Mock()
            mock_key.is_sequence = True
            mock_key.name = "KEY_RIGHT"
            mock_term.inkey.return_value = mock_key
            mock_term_class.return_value = mock_term
            handler = InteractiveInputHandler()
            controller = InteractiveController(handler)

            controller.process_input()
            assert controller.head_tilt_y > 0.0

    def test_lean_commands(self):
        """LEAN_LEFT and LEAN_RIGHT adjust Z tilt."""
        with patch("src.terminal.input.Terminal"):
            handler = InteractiveInputHandler()
            controller = InteractiveController(handler)

            # Simulate lean left
            with patch.object(handler, "poll_input") as mock_poll:
                mock_poll.return_value = InputEvent(InputCommand.LEAN_LEFT)
                controller.process_input()
                assert controller.head_tilt_z < 0.0

            controller.reset_head_tilt()

            # Simulate lean right
            with patch.object(handler, "poll_input") as mock_poll:
                mock_poll.return_value = InputEvent(InputCommand.LEAN_RIGHT)
                controller.process_input()
                assert controller.head_tilt_z > 0.0
