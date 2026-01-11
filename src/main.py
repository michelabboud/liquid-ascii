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

from .renderer import Raymarcher, Camera, ASCIIShader
from .model import Head, CharacterHead, AnimationController
from .model.visemes import VisemeController
from .terminal import Display, ColorMode, RainbowColors, PRESET_SCHEMES
from .audio import EdgeTTSEngine, AudioPlayer, LipSyncGenerator
from .tutor import TextTutor


def create_head_renderer(
    width: int = 80,
    height: int = 40,
    character: str = "default",
) -> tuple:
    """
    Create a head model with renderer.

    Returns:
        (head, raymarcher) tuple
    """
    head = CharacterHead(character_name=character)
    camera = Camera(position=(0, 0, -3.5), target=(0, 0, 0))
    shader = ASCIIShader(ramp="standard")
    raymarcher = Raymarcher(
        width=width,
        height=height,
        camera=camera,
        shader=shader,
        max_steps=50,
    )
    return head, raymarcher


def run_demo_mode(
    character: str = "default",
    color_scheme: str = "default",
    rainbow_mode: Optional[str] = None,
    fps: float = 15.0,
    expression: Optional[str] = None,
):
    """
    Run the demo animation (idle head with blinking).
    """
    display = Display(target_fps=fps)
    width, height = display.get_size()

    # Limit size for performance
    width = min(width, 100)
    height = min(height, 50)

    head, raymarcher = create_head_renderer(width, height, character)

    # Set initial expression if specified
    if expression:
        head.set_expression(expression)

    if rainbow_mode:
        display.set_rainbow(mode=rainbow_mode)
    else:
        display.set_color_scheme(color_scheme)

    def update(dt: float) -> str:
        head.update(dt)
        sdf = head.get_sdf()
        return raymarcher.render_frame(sdf)

    expr_info = f" with expression '{expression}'" if expression else ""
    print(f"Starting demo mode with character '{character}'{expr_info}...")
    print("Press 'q' to quit")

    display.run_loop(update, show_fps=True)


async def run_speak_mode(
    text: str,
    character: str = "default",
    color_scheme: str = "default",
    voice: str = "en-US-AriaNeural",
    expression: Optional[str] = None,
):
    """
    Run speaking mode - head speaks given text.
    """
    from .audio.tts import run_async

    display = Display(target_fps=15.0)
    width, height = display.get_size()
    width = min(width, 100)
    height = min(height, 50)

    head, raymarcher = create_head_renderer(width, height, character)

    # Set initial expression if specified
    if expression:
        head.set_expression(expression)

    display.set_color_scheme(color_scheme)

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
    voice: str = "en-US-AriaNeural",
    expression: Optional[str] = None,
):
    """
    Run tutor mode - read and explain a text/markdown file.
    """
    display = Display(target_fps=15.0)
    width, height = display.get_size()
    width = min(width, 100)
    height = min(height, 50)

    head, raymarcher = create_head_renderer(width, height, character)

    # Set initial expression if specified
    if expression:
        head.set_expression(expression)

    display.set_color_scheme(color_scheme)

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


def run_static_mode(character: str = "default", expression: Optional[str] = None):
    """
    Render a single static frame (no animation).
    """
    head, raymarcher = create_head_renderer(80, 40, character)

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

Characters: default, round, tall, wide, robot, cute
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
        help="Character preset (default, round, tall, wide, robot, cute)"
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
        default="en-US-AriaNeural",
        help="TTS voice name"
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=15.0,
        help="Target FPS (default: 15)"
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

    # Handle modes
    if args.static:
        run_static_mode(args.character, expression=args.expression)
    elif args.speak:
        asyncio.run(run_speak_mode(
            args.speak,
            character=args.character,
            color_scheme=args.scheme,
            voice=args.voice,
            expression=args.expression,
        ))
    elif args.tutor:
        asyncio.run(run_tutor_mode(
            args.tutor,
            character=args.character,
            color_scheme=args.scheme,
            voice=args.voice,
            expression=args.expression,
        ))
    else:
        run_demo_mode(
            character=args.character,
            color_scheme=args.scheme,
            rainbow_mode=args.rainbow,
            fps=args.fps,
            expression=args.expression,
        )


if __name__ == "__main__":
    main()
