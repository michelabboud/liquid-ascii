"""
Liquid ASCII Art Animation - Main Entry Point

A terminal-based ASCII art animation system featuring a talking head
with smooth, liquid-like 3D rendering and lip sync capabilities.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

from .renderer import Raymarcher, Camera, ASCIIShader, QualityLevel, AdaptiveQualityController
from .model import Head, CharacterHead, AnimationController
from .model.visemes import VisemeController
from .terminal import Display, ColorMode, RainbowColors, PRESET_SCHEMES
from .audio import EdgeTTSEngine, AudioPlayer, LipSyncGenerator
from .tutor import TextTutor
from .chat import ChatSession, list_available_backends


def create_head_renderer(
    width: int = 80,
    height: int = 40,
    character: str = "default",
    quality: str = "high",
) -> tuple:
    """
    Create a head model with renderer.

    Args:
        width: Render width in characters
        height: Render height in characters
        character: Character preset name
        quality: Quality level (low/medium/high/ultra/auto)

    Returns:
        (head, raymarcher) tuple
    """
    head = CharacterHead(character_name=character)
    camera = Camera(position=(0, 0, -3.5), target=(0, 0, 0))
    shader = ASCIIShader(ramp="standard")

    # Convert quality string to enum
    quality_level = QualityLevel(quality)

    raymarcher = Raymarcher(
        width=width,
        height=height,
        camera=camera,
        shader=shader,
        quality=quality_level,
    )
    return head, raymarcher


def run_demo_mode(
    character: str = "default",
    color_scheme: str = "default",
    rainbow_mode: Optional[str] = None,
    fps: float = 15.0,
    expression: Optional[str] = None,
    interactive: bool = False,
    quality: str = "high",
):
    """
    Run the demo animation (idle head with blinking).

    Args:
        character: Character preset name
        color_scheme: Color scheme name
        rainbow_mode: Rainbow mode name
        fps: Target frames per second
        expression: Initial expression
        interactive: Enable keyboard controls
        quality: Quality level (low/medium/high/ultra/auto)
    """
    from .terminal import InteractiveInputHandler, InteractiveController, InputCommand, PRESET_SCHEMES

    display = Display(target_fps=fps)
    width, height = display.get_size()

    # Limit size for performance
    width = min(width, 100)
    height = min(height, 50)

    head, raymarcher = create_head_renderer(width, height, character, quality)

    # Set initial expression if specified
    if expression:
        head.set_expression(expression)

    if rainbow_mode:
        display.set_rainbow(mode=rainbow_mode)
    else:
        display.set_color_scheme(color_scheme)

    # Interactive controls
    input_handler = None
    controller = None
    color_schemes = list(PRESET_SCHEMES.keys())
    rainbow_modes = ["horizontal", "vertical", "radial", "diagonal", "wave", "time"]
    current_scheme_idx = color_schemes.index(color_scheme) if color_scheme in color_schemes else 0
    current_rainbow_idx = rainbow_modes.index(rainbow_mode) if rainbow_mode in rainbow_modes else 0
    current_fps = fps

    if interactive:
        input_handler = InteractiveInputHandler(display.term)
        controller = InteractiveController(input_handler)

    def update(dt: float) -> str:
        nonlocal current_scheme_idx, current_rainbow_idx, current_fps, rainbow_mode

        # Process interactive input
        if interactive and controller:
            if not controller.process_input():
                return None  # Signal quit

            # Check for expression changes
            event = input_handler.poll_input(timeout=0.0)
            if event:
                # Expression commands
                expr_name = input_handler.get_expression_name(event.command)
                if expr_name:
                    head.set_expression(expr_name)

                # Color scheme cycling
                elif event.command == InputCommand.CYCLE_COLOR_SCHEME:
                    current_scheme_idx = (current_scheme_idx + 1) % len(color_schemes)
                    new_scheme = color_schemes[current_scheme_idx]
                    display.set_color_scheme(new_scheme)
                    rainbow_mode = None

                # Rainbow mode cycling
                elif event.command == InputCommand.CYCLE_RAINBOW:
                    current_rainbow_idx = (current_rainbow_idx + 1) % len(rainbow_modes)
                    rainbow_mode = rainbow_modes[current_rainbow_idx]
                    display.set_rainbow(mode=rainbow_mode)

                # FPS adjustment
                elif event.command == InputCommand.FPS_INCREASE:
                    current_fps = min(60.0, current_fps + 2.0)
                    display.target_fps = current_fps

                elif event.command == InputCommand.FPS_DECREASE:
                    current_fps = max(5.0, current_fps - 2.0)
                    display.target_fps = current_fps

            # Apply head tilt from controller
            tilt_x, tilt_y, tilt_z = controller.get_head_tilt()
            head.set_head_tilt(tilt_x, tilt_y, tilt_z)

            # Skip update if paused
            if controller.is_paused():
                sdf = head.get_sdf()
                frame = raymarcher.render_frame(sdf)
                # Show pause indicator
                if input_handler.is_help_visible():
                    return input_handler.get_help_text()
                return frame + "\n[PAUSED] Press SPACE to resume, H for help"

        # Normal update
        head.update(dt)
        sdf = head.get_sdf()
        frame = raymarcher.render_frame(sdf)

        # Overlay help if visible
        if interactive and input_handler and input_handler.is_help_visible():
            return input_handler.get_help_text()

        return frame

    expr_info = f" with expression '{expression}'" if expression else ""
    interactive_info = " (interactive mode)" if interactive else ""
    print(f"Starting demo mode with character '{character}'{expr_info}{interactive_info}...")
    if interactive:
        print("Press 'H' for help, ESC or 'Q' to quit")
    else:
        print("Press 'q' to quit")

    display.run_loop(update, show_fps=True)


async def run_speak_mode(
    text: str,
    character: str = "default",
    color_scheme: str = "default",
    voice: Optional[str] = None,
    expression: Optional[str] = None,
    quality: str = "high",
):
    """
    Run speaking mode - head speaks given text.

    Args:
        text: Text to speak
        character: Character preset
        color_scheme: Color scheme
        voice: Voice to use (None = use character's default voice)
        expression: Initial expression
        quality: Rendering quality
    """
    from .audio.tts import run_async

    display = Display(target_fps=15.0)
    width, height = display.get_size()
    width = min(width, 100)
    height = min(height, 50)

    head, raymarcher = create_head_renderer(width, height, character, quality)

    # Set initial expression if specified
    if expression:
        head.set_expression(expression)

    display.set_color_scheme(color_scheme)

    # Use character's default voice if not specified
    if voice is None:
        voice = head.default_voice
        print(f"Using default voice for {character}: {voice}")

    # Initialize TTS
    tts = EdgeTTSEngine(voice=voice)
    player = AudioPlayer()
    lipsync = LipSyncGenerator()

    print(f"Synthesizing speech...")
    result, word_timings = await tts.synthesize_with_timestamps(text)
    print(f"Audio duration: {result.duration:.1f}s")

    # Generate lip sync
    viseme_controller = VisemeController()
    cues = lipsync.generate_from_word_timings(word_timings)
    viseme_controller.load_cues(cues)

    # Load and play audio
    player.load_file(result.audio_path)

    display.clear()
    display.hide_cursor()

    try:
        player.play()

        while player.is_playing():
            dt = display.wait_for_frame()
            t = player.get_position()

            # Update visemes
            shape = viseme_controller.update(t, dt)
            head.set_mouth(shape.mouth_openness, shape.mouth_width, shape.lip_pucker)

            # Update head animation
            head.update(dt)

            # Render
            sdf = head.get_sdf()
            frame = raymarcher.render_frame(sdf)

            status = f"Speaking... {t:.1f}s / {result.duration:.1f}s"
            display.render_frame(frame, status_text=status)

    finally:
        display.show_cursor()
        player.stop()
        tts.cleanup()


async def run_tutor_mode(
    file_path: str,
    character: str = "default",
    color_scheme: str = "default",
    voice: Optional[str] = None,
    expression: Optional[str] = None,
    quality: str = "high",
):
    """
    Run tutor mode - read and explain a text/markdown file.

    Args:
        file_path: Path to file to read
        character: Character preset
        color_scheme: Color scheme
        voice: Voice to use (None = use character's default voice)
        expression: Initial expression
        quality: Rendering quality
    """
    display = Display(target_fps=15.0)
    width, height = display.get_size()
    width = min(width, 100)
    height = min(height, 50)

    head, raymarcher = create_head_renderer(width, height, character, quality)

    # Set initial expression if specified
    if expression:
        head.set_expression(expression)

    display.set_color_scheme(color_scheme)

    # Use character's default voice if not specified
    if voice is None:
        voice = head.default_voice
        print(f"Using default voice for {character}: {voice}")

    # Load content
    tutor = TextTutor()
    segments = tutor.load_file(Path(file_path))

    print(f"Loaded {len(segments)} segments from {file_path}")
    print(f"Estimated duration: {tutor.get_estimated_duration():.0f}s")
    print("Starting in 2 seconds...")
    await asyncio.sleep(2)

    # Initialize TTS and audio
    tts = EdgeTTSEngine(voice=voice)
    player = AudioPlayer()
    lipsync = LipSyncGenerator()
    viseme_controller = VisemeController()

    display.clear()
    display.hide_cursor()

    try:
        for idx, segment in enumerate(segments):
            progress_current, progress_total = idx + 1, len(segments)

            # Synthesize segment
            result, word_timings = await tts.synthesize_with_timestamps(segment.text)

            # Generate lip sync
            cues = lipsync.generate_from_word_timings(word_timings)
            viseme_controller.load_cues(cues)
            viseme_controller.reset()

            # Play segment
            player.load_file(result.audio_path)
            player.play()

            while player.is_playing():
                dt = display.wait_for_frame()
                t = player.get_position()

                # Update animation
                shape = viseme_controller.update(t, dt)
                head.set_mouth(shape.mouth_openness, shape.mouth_width, shape.lip_pucker)
                head.update(dt)

                # Render
                sdf = head.get_sdf()
                frame = raymarcher.render_frame(sdf)

                # Truncate current text for status
                text_preview = segment.text[:40] + "..." if len(segment.text) > 40 else segment.text
                status = f"[{progress_current}/{progress_total}] {text_preview}"
                display.render_frame(frame, status_text=status)

            player.stop()

            # Pause between segments
            if segment.pause_after > 0:
                await asyncio.sleep(segment.pause_after)

        print("\nTutoring complete!")

    finally:
        display.show_cursor()
        player.stop()
        tts.cleanup()


def run_static_mode(
    character: str = "default",
    expression: Optional[str] = None,
    quality: str = "high",
):
    """
    Render a single static frame (no animation).
    """
    head, raymarcher = create_head_renderer(80, 40, character, quality)

    # Set initial expression if specified
    if expression:
        head.set_expression(expression)
        # Let expression transition complete for static render
        import time
        time.sleep(0.1)
        head.update(0.1)

    sdf = head.get_sdf()
    frame = raymarcher.render_frame(sdf)
    print(frame)


async def run_chat_mode(
    character: str = "default",
    color_scheme: str = "default",
    fps: float = 15.0,
    quality: str = "high",
    llm_backend: str = "ollama",
    llm_model: Optional[str] = None,
):
    """
    Run interactive chat mode with LLM.

    Args:
        character: Character preset name
        color_scheme: Color scheme name
        fps: Target frames per second
        quality: Quality level
        llm_backend: LLM backend type
        llm_model: LLM model name (optional)
    """
    from .chat import ChatSession

    print(f"Initializing chat mode with {character} character...")
    print(f"LLM Backend: {llm_backend}")

    # Set up backend kwargs
    backend_kwargs = {}
    if llm_model:
        backend_kwargs["model"] = llm_model

    # Create chat session
    try:
        chat_session = ChatSession(
            character_name=character,
            backend_type=llm_backend,
            backend_kwargs=backend_kwargs,
        )
    except Exception as e:
        print(f"Error initializing chat session: {e}")
        print()
        print("Troubleshooting:")
        if llm_backend == "ollama":
            print("  - Is Ollama installed and running?")
            print("  - Try: ollama serve")
            print("  - Download a model: ollama pull llama3.2")
        elif llm_backend == "openai":
            print("  - Is OPENAI_API_KEY environment variable set?")
            print("  - export OPENAI_API_KEY='your-key-here'")
        return

    # Create display and head
    display = Display(target_fps=fps)
    width, height = display.get_size()

    # Reserve bottom lines for chat UI
    chat_ui_lines = 5
    render_height = min(height - chat_ui_lines, 50)
    render_width = min(width, 100)

    head, raymarcher = create_head_renderer(render_width, render_height, character, quality)
    head.set_expression("neutral")
    display.set_color_scheme(color_scheme)

    print()
    print("=" * 70)
    print("CHAT MODE - Interactive Conversation")
    print("=" * 70)
    print(f"Character: {character}")
    print(f"Personality: {chat_session.bot.personality.description}")
    print()
    print("Controls:")
    print("  - Type your message and press Enter")
    print("  - Type 'quit' or 'exit' to end")
    print("  - Type 'clear' to clear conversation history")
    print("=" * 70)
    print()

    # Store conversation display
    conversation_log = []

    def render_frame_with_chat():
        """Render head with chat UI overlay."""
        # Update head animation
        head.update(1.0 / fps)

        # Render head
        sdf = head.get_sdf()
        frame = raymarcher.render_frame(sdf)

        # Add chat UI at bottom
        lines = frame.split("\n")

        # Add separator
        lines.append("-" * render_width)

        # Add recent conversation (last few messages)
        recent_messages = conversation_log[-3:]
        for msg in recent_messages:
            # Truncate long messages
            if len(msg) > render_width:
                msg = msg[: render_width - 3] + "..."
            lines.append(msg)

        # Pad to full height
        while len(lines) < render_height + chat_ui_lines:
            lines.append("")

        return "\n".join(lines)

    # Chat loop
    running = True
    while running:
        try:
            # Show initial frame
            frame = render_frame_with_chat()
            display.clear()
            print(frame)

            # Get user input
            print("\nYou: ", end="", flush=True)
            user_input = input().strip()

            if not user_input:
                continue

            # Check for commands
            if user_input.lower() in ["quit", "exit"]:
                print("Goodbye!")
                break

            if user_input.lower() == "clear":
                chat_session.clear()
                conversation_log.clear()
                print("Conversation cleared.")
                continue

            # Add user message to log
            conversation_log.append(f"You: {user_input}")

            # Show "thinking" while processing
            head.set_expression("thinking")
            frame = render_frame_with_chat()
            display.clear()
            print(frame)
            print("\nYou:", user_input)
            print(f"{character.capitalize()}: ", end="", flush=True)

            # Get response from LLM (streaming)
            response_text = []
            try:
                async for token, expression in chat_session.send_message_stream(user_input):
                    response_text.append(token)
                    print(token, end="", flush=True)

                    # Update expression dynamically
                    if expression != head.current_expression_name:
                        head.set_expression(expression)

                print()  # New line after response

                # Add assistant message to log
                full_response = "".join(response_text)
                conversation_log.append(f"{character.capitalize()}: {full_response}")

            except Exception as e:
                print(f"\nError getting response: {e}")
                conversation_log.append(f"{character.capitalize()}: [Error: {e}]")

            # Brief pause to show final expression
            await asyncio.sleep(0.5)

        except KeyboardInterrupt:
            print("\n\nChat interrupted.")
            running = False
        except EOFError:
            print("\n\nChat ended.")
            running = False

    display.cleanup()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Liquid ASCII - Terminal-based 3D animated talking head",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  liquid-ascii                          # Run demo mode
  liquid-ascii --speak "Hello world!"   # Speak text
  liquid-ascii --tutor README.md        # Tutor mode with a file
  liquid-ascii --character robot        # Use robot character
  liquid-ascii --rainbow horizontal     # Rainbow colors
  liquid-ascii --scheme neon            # Use neon color scheme

Characters: default, round, tall, wide, robot, cute, alien, cat, dog, baby, elder, skull
Color schemes: default, pale, dark, robot, alien, ghost, sunset, ocean, neon, monochrome
Rainbow modes: horizontal, vertical, radial, diagonal, wave, time
        """
    )

    parser.add_argument(
        "--speak", "-s",
        type=str,
        help="Text to speak"
    )
    parser.add_argument(
        "--tutor", "-t",
        type=str,
        help="Path to text/markdown file to read aloud"
    )
    parser.add_argument(
        "--character", "-c",
        type=str,
        default="default",
        help="Character preset (default, round, tall, wide, robot, cute, alien, cat, dog, baby, elder, skull)"
    )
    parser.add_argument(
        "--expression", "-e",
        type=str,
        help="Facial expression (neutral, happy, sad, angry, surprised, confused, tired, wink, thinking, excited, skeptical)"
    )
    parser.add_argument(
        "--scheme",
        type=str,
        default="default",
        help="Color scheme name"
    )
    parser.add_argument(
        "--rainbow", "-r",
        type=str,
        help="Rainbow mode (horizontal, vertical, radial, diagonal, wave)"
    )
    parser.add_argument(
        "--voice", "-v",
        type=str,
        default=None,
        help="TTS voice name (default: auto-select based on character)"
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=15.0,
        help="Target FPS (default: 15)"
    )
    parser.add_argument(
        "--quality", "-q",
        type=str,
        choices=["low", "medium", "high", "ultra", "auto"],
        default="high",
        help="Rendering quality (low=16 steps, medium=32, high=50, ultra=80, auto=adaptive) (default: high)"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Enable interactive keyboard controls (arrow keys, expressions, etc.)"
    )
    parser.add_argument(
        "--static",
        action="store_true",
        help="Render single static frame"
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List available TTS voices"
    )
    parser.add_argument(
        "--list-schemes",
        action="store_true",
        help="List available color schemes"
    )
    parser.add_argument(
        "--list-expressions",
        action="store_true",
        help="List available facial expressions"
    )
    parser.add_argument(
        "--list-character-voices",
        action="store_true",
        help="List character-to-voice mappings"
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Enable interactive chat mode with LLM"
    )
    parser.add_argument(
        "--llm-backend",
        type=str,
        choices=["ollama", "openai"],
        default="ollama",
        help="LLM backend to use (default: ollama)"
    )
    parser.add_argument(
        "--llm-model",
        type=str,
        default=None,
        help="LLM model name (default: llama3.2:latest for ollama, gpt-4o-mini for openai)"
    )
    parser.add_argument(
        "--list-llm-backends",
        action="store_true",
        help="List available LLM backends"
    )

    args = parser.parse_args()

    # Handle info commands
    if args.list_schemes:
        print("Available color schemes:")
        for name in PRESET_SCHEMES:
            print(f"  - {name}")
        return

    if args.list_voices:
        async def list_voices():
            tts = EdgeTTSEngine()
            voices = await tts.list_voices()
            print(f"Available voices ({len(voices)}):")
            for v in voices[:30]:
                print(f"  {v.short_name}: {v.name} ({v.gender}, {v.locale})")
            if len(voices) > 30:
                print(f"  ... and {len(voices) - 30} more")
            tts.cleanup()

        asyncio.run(list_voices())
        return

    if args.list_expressions:
        from .model import EXPRESSIONS
        print("Available facial expressions:")
        for name, expr in EXPRESSIONS.items():
            print(f"  - {name:12} (duration: {expr.duration:.1f}s)")
        return

    if args.list_character_voices:
        from .model import CharacterHead
        print("Character-to-Voice Mappings:")
        print("=" * 70)
        voices = CharacterHead.get_all_character_voices()
        for char, voice in voices.items():
            print(f"  {char:12} → {voice}")
        print()
        print("Note: Voices are auto-selected unless you specify --voice")
        print("      To override: ./dev.sh run --speak 'text' --character cat --voice en-US-GuyNeural")
        return

    if args.list_llm_backends:
        from .chat import list_available_backends
        print("Checking available LLM backends...")
        print()
        available = list_available_backends()
        if available:
            print(f"Available backends: {', '.join(available)}")
            print()
            for backend in available:
                if backend == "ollama":
                    print("  [ollama]")
                    print("    - Local LLM inference")
                    print("    - Install: https://ollama.ai")
                    print("    - Default model: llama3.2:latest")
                elif backend == "openai":
                    print("  [openai]")
                    print("    - OpenAI API")
                    print("    - Requires: OPENAI_API_KEY environment variable")
                    print("    - Default model: gpt-4o-mini")
        else:
            print("No LLM backends available.")
            print()
            print("To use chat mode, you need either:")
            print("  1. Ollama: Install from https://ollama.ai")
            print("  2. OpenAI: Set OPENAI_API_KEY environment variable")
        return

    # Handle modes
    if args.static:
        run_static_mode(
            args.character,
            expression=args.expression,
            quality=args.quality,
        )
    elif args.chat:
        asyncio.run(run_chat_mode(
            character=args.character,
            color_scheme=args.scheme,
            fps=args.fps,
            quality=args.quality,
            llm_backend=args.llm_backend,
            llm_model=args.llm_model,
        ))
    elif args.speak:
        asyncio.run(run_speak_mode(
            args.speak,
            character=args.character,
            color_scheme=args.scheme,
            voice=args.voice,
            expression=args.expression,
            quality=args.quality,
        ))
    elif args.tutor:
        asyncio.run(run_tutor_mode(
            args.tutor,
            character=args.character,
            color_scheme=args.scheme,
            voice=args.voice,
            expression=args.expression,
            quality=args.quality,
        ))
    else:
        run_demo_mode(
            character=args.character,
            color_scheme=args.scheme,
            rainbow_mode=args.rainbow,
            fps=args.fps,
            expression=args.expression,
            interactive=args.interactive,
            quality=args.quality,
        )


if __name__ == "__main__":
    main()
