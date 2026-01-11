"""
Liquid ASCII Art Animation - Main Entry Point

A terminal-based ASCII art animation system featuring a talking head
with smooth, liquid-like 3D rendering and lip sync capabilities.
"""

import argparse
import asyncio
import sys
from pathlib import Path

from .audio import AudioPlayer, EdgeTTSEngine, LipSyncGenerator
from .chat import ChatSession
from .config import (
    AppConfig,
    CharacterConfig,
    ChatConfig,
    EffectsConfig,
    RenderConfig,
    find_config_file,
    list_presets,
    load_config,
    load_preset,
    save_preset,
)
from .model import CharacterHead
from .model.visemes import VisemeController
from .renderer import ASCIIShader, Camera, QualityLevel, Raymarcher
from .terminal import PRESET_SCHEMES, Display, EffectsCompositor
from .tutor import TextTutor

# Effect Presets
EFFECT_PRESETS = {
    "cyberpunk": {
        "description": "Cyberpunk aesthetic with glitch and scanlines",
        "effects": {
            "glitch": True,
            "glitch_intensity": 0.15,
            "scanlines": True,
            "scanline_intensity": 0.6,
            "particles": True,
            "max_particles": 30,
        },
    },
    "matrix": {
        "description": "Matrix-style falling digital rain",
        "effects": {
            "matrix_rain": True,
            "matrix_density": 0.4,
            "scanlines": True,
            "scanline_intensity": 0.3,
            "glitch": True,
            "glitch_intensity": 0.05,
        },
    },
    "retro": {
        "description": "Retro CRT monitor simulation",
        "effects": {
            "scanlines": True,
            "scanline_intensity": 0.7,
            "depth_of_field": True,
            "dof_focus": 3.5,
            "dof_strength": 0.3,
        },
    },
    "glitchy": {
        "description": "Heavy glitch and distortion effects",
        "effects": {
            "glitch": True,
            "glitch_intensity": 0.25,
            "trails": True,
            "trail_length": 8,
            "particles": True,
            "max_particles": 40,
        },
    },
    "minimal": {
        "description": "Minimal effects - just particles",
        "effects": {
            "particles": True,
            "max_particles": 20,
        },
    },
    "showcase": {
        "description": "All effects enabled for demonstration",
        "effects": {
            "particles": True,
            "max_particles": 50,
            "trails": True,
            "trail_length": 5,
            "glitch": True,
            "glitch_intensity": 0.08,
            "scanlines": True,
            "scanline_intensity": 0.4,
            "matrix_rain": True,
            "matrix_density": 0.2,
            "depth_of_field": True,
            "dof_focus": 3.5,
            "dof_strength": 0.4,
        },
    },
}


def calculate_optimal_resolution(
    terminal_width: int,
    terminal_height: int,
    margin: int = 2,
    target_ratio: float = 2.0,
    max_width: int = 200,
    max_height: int = 100,
    min_width: int = 40,
    min_height: int = 20,
) -> tuple[int, int]:
    """
    Calculate optimal render resolution based on terminal size.

    ASCII characters are typically taller than they are wide (roughly 2:1 ratio),
    so we aim for width:height ratio of ~2:1 for proper proportions.

    Args:
        terminal_width: Terminal width in columns
        terminal_height: Terminal height in lines
        margin: Margin to leave on edges (characters)
        target_ratio: Target width:height ratio (default 2.0 for ASCII)
        max_width: Maximum render width
        max_height: Maximum render height
        min_width: Minimum render width
        min_height: Minimum render height

    Returns:
        (width, height) tuple for rendering
    """
    # Apply margins
    usable_width = max(terminal_width - margin * 2, min_width)
    usable_height = max(terminal_height - margin * 2, min_height)

    # Calculate based on height constraint (usually the limiting factor)
    # If we use full height, how much width do we need?
    width_from_height = int(usable_height * target_ratio)

    # Calculate based on width constraint
    # If we use full width, how much height do we need?
    height_from_width = int(usable_width / target_ratio)

    # Choose the limiting dimension
    if width_from_height <= usable_width:
        # Height is the limiting factor
        width = width_from_height
        height = usable_height
    else:
        # Width is the limiting factor
        width = usable_width
        height = height_from_width

    # Apply min/max constraints
    width = max(min_width, min(width, max_width))
    height = max(min_height, min(height, max_height))

    return width, height


def create_head_renderer(
    width: int = 80,
    height: int = 40,
    character: str = "default",
    quality: str = "high",
    ramp: str = "standard",
) -> tuple:
    """
    Create a head model with renderer.

    Args:
        width: Render width in characters
        height: Render height in characters
        character: Character preset name
        quality: Quality level (low/medium/high/ultra/auto)
        ramp: ASCII ramp style (standard, unicode, stars, faces, etc.)

    Returns:
        (head, raymarcher) tuple
    """
    head = CharacterHead(character_name=character)
    camera = Camera(position=(0, 0, -3.5), target=(0, 0, 0))
    shader = ASCIIShader(ramp=ramp)

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


def setup_effects_from_args(args, width: int, height: int):
    """
    Create and configure EffectsCompositor from CLI arguments.

    Args:
        args: Parsed command-line arguments
        width: Display width in characters
        height: Display height in characters

    Returns:
        Configured EffectsCompositor or None if no effects enabled
    """
    # Apply preset first if specified
    effect_config = {}
    if args.effect_preset:
        if args.effect_preset in EFFECT_PRESETS:
            effect_config = EFFECT_PRESETS[args.effect_preset]["effects"].copy()

    # Override with individual flags (individual flags take precedence)
    if args.particles:
        effect_config["particles"] = True
        effect_config["max_particles"] = args.max_particles

    if args.trails:
        effect_config["trails"] = True
        effect_config["trail_length"] = args.trail_length

    if args.glitch:
        effect_config["glitch"] = True
        effect_config["glitch_intensity"] = args.glitch_intensity

    if args.scanlines:
        effect_config["scanlines"] = True
        effect_config["scanline_intensity"] = args.scanline_intensity

    if args.matrix_rain:
        effect_config["matrix_rain"] = True
        effect_config["matrix_density"] = args.matrix_density

    if args.depth_of_field:
        effect_config["depth_of_field"] = True
        effect_config["dof_focus"] = args.dof_focus
        effect_config["dof_strength"] = args.dof_strength

    # If no effects enabled, return None
    if not effect_config:
        return None

    # Create compositor and configure effects
    compositor = EffectsCompositor(width, height)

    if effect_config.get("particles"):
        compositor.enable_particles(max_particles=effect_config.get("max_particles", 50))

    if effect_config.get("trails"):
        compositor.enable_trails(length=effect_config.get("trail_length", 5))

    if effect_config.get("glitch"):
        compositor.enable_glitch(intensity=effect_config.get("glitch_intensity", 0.1))

    if effect_config.get("scanlines"):
        compositor.enable_scanlines(intensity=effect_config.get("scanline_intensity", 0.5))

    if effect_config.get("matrix_rain"):
        compositor.enable_matrix_rain(density=effect_config.get("matrix_density", 0.3))

    if effect_config.get("depth_of_field"):
        compositor.enable_depth_of_field(
            focus=effect_config.get("dof_focus", 3.5),
            strength=effect_config.get("dof_strength", 0.5),
        )

    return compositor


def run_demo_mode(
    character: str = "default",
    color_scheme: str = "default",
    rainbow_mode: str | None = None,
    fps: float = 15.0,
    expression: str | None = None,
    interactive: bool = False,
    quality: str = "high",
    compositor: EffectsCompositor | None = None,
    duration: float | None = None,
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
        compositor: Optional effects compositor for visual effects
        duration: Duration in seconds (None = run until interrupted)
    """
    from .terminal import (
        PRESET_SCHEMES,
        InputCommand,
        InteractiveController,
        InteractiveInputHandler,
    )

    display = Display(target_fps=fps)
    terminal_width, terminal_height = display.get_size()

    # Calculate optimal resolution based on terminal size
    width, height = calculate_optimal_resolution(terminal_width, terminal_height)

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
    elapsed_time = 0.0

    if interactive:
        input_handler = InteractiveInputHandler(display.term)
        controller = InteractiveController(input_handler)

    def update(dt: float) -> str:
        nonlocal current_scheme_idx, current_rainbow_idx, current_fps, rainbow_mode, elapsed_time

        # Check duration limit
        if duration is not None:
            elapsed_time += dt
            if elapsed_time >= duration:
                return None  # Signal to stop the loop

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

                # Apply effects if compositor is available
                if compositor:
                    frame = compositor.render(frame)

                # Show pause indicator
                if input_handler.is_help_visible():
                    return input_handler.get_help_text()
                return frame + "\n[PAUSED] Press SPACE to resume, H for help"

        # Normal update
        head.update(dt)
        sdf = head.get_sdf()
        frame = raymarcher.render_frame(sdf)

        # Apply effects if compositor is available
        if compositor:
            compositor.update(dt)
            frame = compositor.render(frame)

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
    voice: str | None = None,
    expression: str | None = None,
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

    display = Display(target_fps=30.0)
    terminal_width, terminal_height = display.get_size()

    # Calculate optimal resolution based on terminal size
    width, height = calculate_optimal_resolution(terminal_width, terminal_height)

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

    print("Synthesizing speech...")
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
    voice: str | None = None,
    expression: str | None = None,
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
    display = Display(target_fps=30.0)
    terminal_width, terminal_height = display.get_size()

    # Calculate optimal resolution based on terminal size
    width, height = calculate_optimal_resolution(terminal_width, terminal_height)

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
    expression: str | None = None,
    quality: str = "high",
    color_scheme_name: str = "default",
    ramp: str = "standard",
    use_emojis: bool = False,
    use_edges: bool = True,
    edge_boost: float = 0.8,
):
    """
    Render a single static frame with feature-based coloring.
    """
    from blessed import Terminal
    from .terminal.colors import PRESET_SCHEMES

    # Get terminal size and calculate optimal resolution
    term = Terminal()
    terminal_width = term.width or 80
    terminal_height = term.height or 40
    width, height = calculate_optimal_resolution(terminal_width, terminal_height)

    head, raymarcher = create_head_renderer(width, height, character, quality, ramp)
    color_scheme = PRESET_SCHEMES[color_scheme_name]

    # Set initial expression if specified
    if expression:
        head.set_expression(expression)
        # Let expression transition complete for static render
        import time

        time.sleep(0.1)
        head.update(0.1)

    # Use feature-based rendering for colored facial features
    sdf_with_features = head.get_sdf_with_features()
    frame = raymarcher.render_frame_with_features(
        sdf_with_features,
        color_scheme,
        use_emojis=use_emojis,
        use_edges=use_edges,
        edge_boost=edge_boost,
    )
    print(frame)


async def run_chat_mode(
    character: str = "default",
    color_scheme: str = "default",
    fps: float = 15.0,
    quality: str = "high",
    llm_backend: str = "ollama",
    llm_model: str | None = None,
    enable_voice: bool = False,
    voice: str | None = None,
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
        enable_voice: Enable voice output with TTS and lip sync
        voice: TTS voice name (optional, defaults to character voice)
    """
    from .chat import VoiceChatController, stream_with_voice

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
    terminal_width, terminal_height = display.get_size()

    # Reserve bottom lines for chat UI
    chat_ui_lines = 5
    available_height = terminal_height - chat_ui_lines

    # Calculate optimal resolution with reduced height for chat UI
    width, height = calculate_optimal_resolution(
        terminal_width, available_height, margin=2
    )

    head, raymarcher = create_head_renderer(width, height, character, quality)
    head.set_expression("neutral")
    display.set_color_scheme(color_scheme)

    # Set up voice if enabled
    voice_controller = None
    audio_player = None
    viseme_controller = None

    if enable_voice:
        # Use character's default voice if not specified
        if voice is None:
            voice = head.default_voice

        print(f"Voice Mode: Enabled (using {voice})")

        # Create TTS engine and voice controller
        tts_engine = EdgeTTSEngine(voice=voice)
        voice_controller = VoiceChatController(tts_engine, voice=voice)

        # Create audio player and viseme controller
        audio_player = AudioPlayer()
        viseme_controller = VisemeController()

    print()
    print("=" * 70)
    print("CHAT MODE - Interactive Conversation")
    if enable_voice:
        print("(with Voice and Lip Sync)")
    print("=" * 70)
    print(f"Character: {character}")
    print(f"Personality: {chat_session.bot.personality.description}")
    if enable_voice:
        print(f"Voice: {voice}")
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
            audio_queue = []  # Queue of audio chunks to play

            try:
                if enable_voice and voice_controller:
                    # Voice-enabled chat with TTS
                    async for token, expression, speech_chunk in stream_with_voice(
                        chat_session, user_input, voice_controller
                    ):
                        if token:
                            response_text.append(token)
                            print(token, end="", flush=True)

                        # Update expression dynamically
                        if expression != head.current_expression_name:
                            head.set_expression(expression)

                        # Queue audio chunk for playback
                        if speech_chunk and speech_chunk.audio_file:
                            audio_queue.append(speech_chunk)

                    print()  # New line after response

                    # Play all audio chunks with lip sync
                    if audio_queue and audio_player and viseme_controller:
                        for chunk in audio_queue:
                            # Load and play audio
                            audio_player.load(chunk.audio_file)
                            audio_player.play()

                            # Generate viseme cues from word timings
                            if chunk.word_timings:
                                from .audio import LipSyncGenerator

                                lipsync_gen = LipSyncGenerator()
                                viseme_cues = lipsync_gen.generate_from_words(
                                    chunk.text, chunk.word_timings
                                )
                                viseme_controller.set_cues(viseme_cues)

                                # Animate while audio plays
                                while audio_player.is_playing():
                                    # Update viseme based on playback position
                                    position = audio_player.get_position()
                                    mouth_params = viseme_controller.update(position)
                                    head.state.mouth_openness = mouth_params["openness"]
                                    head.state.mouth_width = mouth_params["width"]
                                    head.state.lip_pucker = mouth_params["pucker"]

                                    # Render frame with lip sync
                                    head.update(1.0 / fps)
                                    sdf = head.get_sdf()
                                    frame = raymarcher.render_frame(sdf)
                                    display.clear()
                                    print(frame)

                                    await asyncio.sleep(1.0 / fps)

                            audio_player.stop()

                else:
                    # Text-only chat (original behavior)
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

    # Cleanup
    display.cleanup()
    if voice_controller:
        voice_controller.cleanup()
    if audio_player:
        audio_player.cleanup()


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
        """,
    )

    parser.add_argument("--speak", "-s", type=str, help="Text to speak")
    parser.add_argument("--tutor", "-t", type=str, help="Path to text/markdown file to read aloud")
    parser.add_argument(
        "--character",
        "-c",
        type=str,
        default="default",
        help="Character preset (default, round, tall, wide, robot, cute, alien, cat, dog, baby, elder, skull)",
    )
    parser.add_argument(
        "--expression",
        "-e",
        type=str,
        help="Facial expression (neutral, happy, sad, angry, surprised, confused, tired, wink, thinking, excited, skeptical)",
    )
    parser.add_argument("--scheme", type=str, default="default", help="Color scheme name")
    parser.add_argument(
        "--ramp",
        type=str,
        default="standard",
        help="ASCII ramp style (standard, unicode, stars, circles, faces, hearts, nature, etc.)",
    )
    parser.add_argument(
        "--emojis",
        action="store_true",
        help="Use emoji characters for eyes, pupils, and mouth (⚪⚫🔴)",
    )
    parser.add_argument(
        "--no-utf8",
        action="store_true",
        help="Disable UTF-8 enhanced characters (use basic ASCII only)",
    )
    parser.add_argument(
        "--edges",
        action="store_true",
        default=True,
        help="Enable edge detection for sharper feature boundaries (default: ON)",
    )
    parser.add_argument(
        "--no-edges",
        action="store_true",
        help="Disable edge detection",
    )
    parser.add_argument(
        "--edge-intensity",
        type=float,
        default=0.8,
        help="Edge contrast boost intensity 0-1 (default: 0.8)",
    )
    parser.add_argument(
        "--rainbow",
        "-r",
        type=str,
        help="Rainbow mode (horizontal, vertical, radial, diagonal, wave)",
    )
    parser.add_argument(
        "--voice",
        "-v",
        type=str,
        default=None,
        help="TTS voice name (default: auto-select based on character)",
    )
    parser.add_argument("--fps", type=float, default=30.0, help="Target FPS (default: 30)")
    parser.add_argument(
        "--duration",
        "-d",
        type=float,
        default=None,
        help="Duration in seconds for demo mode (default: run until interrupted)",
    )
    parser.add_argument(
        "--quality",
        "-q",
        type=str,
        choices=["low", "medium", "high", "ultra", "auto"],
        default="high",
        help="Rendering quality (low=16 steps, medium=32, high=50, ultra=80, auto=adaptive) (default: high)",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Enable interactive keyboard controls (arrow keys, expressions, etc.)",
    )
    parser.add_argument("--static", action="store_true", help="Render single static frame")
    parser.add_argument("--list-voices", action="store_true", help="List available TTS voices")
    parser.add_argument("--list-schemes", action="store_true", help="List available color schemes")
    parser.add_argument(
        "--list-expressions", action="store_true", help="List available facial expressions"
    )
    parser.add_argument(
        "--list-character-voices", action="store_true", help="List character-to-voice mappings"
    )
    parser.add_argument("--chat", action="store_true", help="Enable interactive chat mode with LLM")
    parser.add_argument(
        "--llm-backend",
        type=str,
        choices=["ollama", "openai"],
        default="ollama",
        help="LLM backend to use (default: ollama)",
    )
    parser.add_argument(
        "--llm-model",
        type=str,
        default=None,
        help="LLM model name (default: llama3.2:latest for ollama, gpt-4o-mini for openai)",
    )
    parser.add_argument(
        "--chat-voice",
        action="store_true",
        help="Enable voice output in chat mode (AI speaks responses with lip sync)",
    )
    parser.add_argument(
        "--list-llm-backends", action="store_true", help="List available LLM backends"
    )

    # Visual Effects
    parser.add_argument("--particles", action="store_true", help="Enable particle system effect")
    parser.add_argument(
        "--max-particles", type=int, default=50, help="Maximum number of particles (default: 50)"
    )
    parser.add_argument("--trails", action="store_true", help="Enable motion trail effect")
    parser.add_argument(
        "--trail-length", type=int, default=5, help="Motion trail length in frames (default: 5)"
    )
    parser.add_argument("--glitch", action="store_true", help="Enable glitch/distortion effect")
    parser.add_argument(
        "--glitch-intensity",
        type=float,
        default=0.1,
        help="Glitch effect intensity 0-1 (default: 0.1)",
    )
    parser.add_argument("--scanlines", action="store_true", help="Enable CRT scanline effect")
    parser.add_argument(
        "--scanline-intensity",
        type=float,
        default=0.5,
        help="Scanline intensity 0-1 (default: 0.5)",
    )
    parser.add_argument(
        "--matrix-rain", action="store_true", help="Enable Matrix-style falling rain effect"
    )
    parser.add_argument(
        "--matrix-density", type=float, default=0.3, help="Matrix rain density 0-1 (default: 0.3)"
    )
    parser.add_argument(
        "--depth-of-field", action="store_true", help="Enable depth-of-field blur effect"
    )
    parser.add_argument(
        "--dof-focus", type=float, default=3.5, help="Depth-of-field focus distance (default: 3.5)"
    )
    parser.add_argument(
        "--dof-strength",
        type=float,
        default=0.5,
        help="Depth-of-field blur strength 0-1 (default: 0.5)",
    )
    parser.add_argument(
        "--effect-preset",
        type=str,
        choices=["cyberpunk", "matrix", "retro", "glitchy", "minimal", "showcase"],
        help="Apply preset effect combination",
    )
    parser.add_argument(
        "--list-effect-presets", action="store_true", help="List available effect presets"
    )

    # Configuration
    parser.add_argument(
        "--config", type=str, metavar="PATH", help="Load configuration from file (.yaml/.json)"
    )
    parser.add_argument(
        "--preset", type=str, metavar="NAME", help="Load configuration preset by name"
    )
    parser.add_argument(
        "--save-preset", type=str, metavar="NAME", help="Save current configuration as preset"
    )
    parser.add_argument(
        "--list-presets", action="store_true", help="List available configuration presets"
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
        print(
            "      To override: ./dev.sh run --speak 'text' --character cat --voice en-US-GuyNeural"
        )
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

    if args.list_effect_presets:
        print("Available effect presets:")
        print("=" * 70)
        for name, preset in EFFECT_PRESETS.items():
            print(f"  {name:12} - {preset['description']}")
            print(f"               Effects: {', '.join(preset['effects'].keys())}")
        print()
        print("Usage: ./dev.sh run --effect-preset <preset-name>")
        print("       ./dev.sh run --effect-preset cyberpunk")
        return

    if args.list_presets:
        print("Available configuration presets:")
        print("=" * 70)
        presets = list_presets()
        if presets:
            for preset_info in presets:
                print(f"  {preset_info['name']:12} - {preset_info['description']}")
            print()
            print("Usage: ./dev.sh run --preset <preset-name>")
            print("       ./dev.sh run --preset my-config")
        else:
            print("  No presets found.")
            print()
            print("Create a preset with: ./dev.sh run --save-preset <name>")
        return

    # Load configuration
    config = AppConfig()  # Start with defaults

    # 1. Load from config file if specified or found
    if args.config:
        config_path = Path(args.config)
        try:
            loaded_config = load_config(config_path)
            if loaded_config:
                config = config.merge(loaded_config)
                print(f"Loaded config from: {config_path}")
        except Exception as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            return
    else:
        # Auto-discover config file
        config_path = find_config_file()
        if config_path:
            try:
                loaded_config = load_config(config_path)
                if loaded_config:
                    config = config.merge(loaded_config)
                    print(f"Loaded config from: {config_path}")
            except Exception as e:
                print(f"Warning: Error loading config from {config_path}: {e}", file=sys.stderr)

    # 2. Load from preset if specified (overrides config file)
    if args.preset:
        try:
            preset_config = load_preset(args.preset)
            config = config.merge(preset_config)
            print(f"Loaded preset: {args.preset}")
        except FileNotFoundError:
            print(f"Error: Preset not found: {args.preset}", file=sys.stderr)
            return
        except Exception as e:
            print(f"Error loading preset: {e}", file=sys.stderr)
            return

    # 3. Override config with CLI arguments (CLI args have highest priority)
    # This happens implicitly - we use args values below

    # 4. Handle save preset (if requested, save and exit)
    if args.save_preset:
        # Build config from current args
        save_config = AppConfig(
            render=RenderConfig(
                quality=args.quality,
                fps=args.fps,
                color_scheme=args.scheme,
                rainbow_mode=args.rainbow,
            ),
            character=CharacterConfig(
                character=args.character,
                expression=args.expression,
                voice=args.voice,
            ),
            effects=EffectsConfig(
                particles=args.particles,
                max_particles=args.max_particles,
                trails=args.trails,
                trail_length=args.trail_length,
                glitch=args.glitch,
                glitch_intensity=args.glitch_intensity,
                scanlines=args.scanlines,
                scanline_intensity=args.scanline_intensity,
                matrix_rain=args.matrix_rain,
                matrix_density=args.matrix_density,
                depth_of_field=args.depth_of_field,
                dof_focus=args.dof_focus,
                dof_strength=args.dof_strength,
            ),
            chat=ChatConfig(
                llm_backend=args.llm_backend if hasattr(args, "llm_backend") else "ollama",
                llm_model=args.llm_model if hasattr(args, "llm_model") else None,
                enable_voice=args.chat_voice if hasattr(args, "chat_voice") else False,
            ),
        )
        try:
            save_preset(args.save_preset, save_config)
            print(f"Preset saved: {args.save_preset}")
            return
        except Exception as e:
            print(f"Error saving preset: {e}", file=sys.stderr)
            return

    # Handle modes
    if args.static:
        # UTF-8 is ON by default, can be disabled with --no-utf8
        if args.no_utf8:
            ramp = args.ramp  # Use specified ramp or default "standard"
        else:
            ramp = "unicode" if args.ramp == "standard" else args.ramp

        # Edges are ON by default, can be disabled with --no-edges
        use_edges = not args.no_edges

        run_static_mode(
            args.character,
            expression=args.expression,
            quality=args.quality,
            color_scheme_name=args.scheme,
            ramp=ramp,
            use_emojis=args.emojis,
            use_edges=use_edges,
            edge_boost=args.edge_intensity,
        )
    elif args.chat:
        asyncio.run(
            run_chat_mode(
                character=args.character,
                color_scheme=args.scheme,
                fps=args.fps,
                quality=args.quality,
                llm_backend=args.llm_backend,
                llm_model=args.llm_model,
                enable_voice=args.chat_voice,
                voice=args.voice,
            )
        )
    elif args.speak:
        asyncio.run(
            run_speak_mode(
                args.speak,
                character=args.character,
                color_scheme=args.scheme,
                voice=args.voice,
                expression=args.expression,
                quality=args.quality,
            )
        )
    elif args.tutor:
        asyncio.run(
            run_tutor_mode(
                args.tutor,
                character=args.character,
                color_scheme=args.scheme,
                voice=args.voice,
                expression=args.expression,
                quality=args.quality,
            )
        )
    else:
        # Set up effects compositor if any effects are enabled
        display_temp = Display()
        terminal_width, terminal_height = display_temp.get_size()

        # Calculate optimal resolution for effects
        width, height = calculate_optimal_resolution(terminal_width, terminal_height)
        compositor = setup_effects_from_args(args, width, height)

        run_demo_mode(
            character=args.character,
            color_scheme=args.scheme,
            rainbow_mode=args.rainbow,
            fps=args.fps,
            expression=args.expression,
            interactive=args.interactive,
            quality=args.quality,
            compositor=compositor,
            duration=args.duration,
        )


if __name__ == "__main__":
    main()
