#!/usr/bin/env python3
"""
Talking Head Demo

Full demonstration with:
- Text-to-speech synthesis
- Lip sync animation
- Audio playback

Requires: edge-tts, sounddevice, scipy
"""

import sys
import asyncio
import os

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from src.renderer import Raymarcher, Camera, ASCIIShader
from src.model import Head
from src.model.visemes import VisemeController
from src.audio import EdgeTTSEngine, AudioPlayer, LipSyncGenerator


async def main():
    # Text to speak
    text = """
    Hello! I am your ASCII talking head assistant.
    I can speak any text you give me, with realistic lip synchronization.
    This is made possible through text to speech and viseme animation.
    Isn't that amazing?
    """

    print("Talking Head Demo")
    print("=" * 40)
    print(f"Text: {text.strip()[:50]}...")
    print()

    # Setup renderer
    camera = Camera(position=(0, 0, -3.5), target=(0, 0, 0))
    shader = ASCIIShader(ramp="standard")
    raymarcher = Raymarcher(
        width=80,
        height=35,
        camera=camera,
        shader=shader,
        max_steps=50,
    )

    # Create animated head
    head = Head(enable_idle_animation=True)

    # Initialize TTS
    print("Synthesizing speech...")
    tts = EdgeTTSEngine(voice="en-US-AriaNeural")

    try:
        result, word_timings = await tts.synthesize_with_timestamps(text)
        print(f"Audio generated: {result.duration:.1f}s")

        # Generate lip sync
        lipsync = LipSyncGenerator()
        viseme_controller = VisemeController()
        cues = lipsync.generate_from_word_timings(word_timings)
        viseme_controller.load_cues(cues)
        print(f"Generated {len(cues)} viseme cues")

        # Setup audio player
        player = AudioPlayer()
        player.load_file(result.audio_path)

        print("\nStarting playback...")
        print("Press Ctrl+C to stop\n")

        # Start playback
        player.play()

        target_fps = 15
        frame_time = 1.0 / target_fps

        while player.is_playing():
            frame_start = asyncio.get_event_loop().time()

            # Get current playback position
            t = player.get_position()

            # Update lip sync
            dt = frame_time
            shape = viseme_controller.update(t, dt)
            head.set_mouth(shape.mouth_openness, shape.mouth_width, shape.lip_pucker)

            # Update head animation (idle movement, blinking)
            head.update(dt)

            # Render
            sdf = head.get_sdf()
            frame = raymarcher.render_frame(sdf)

            # Display
            os.system('clear' if os.name == 'posix' else 'cls')
            print(frame)
            print(f"\nTime: {t:.1f}s / {result.duration:.1f}s | Mouth: {shape.mouth_openness:.2f}")

            # Frame timing
            elapsed = asyncio.get_event_loop().time() - frame_start
            if elapsed < frame_time:
                await asyncio.sleep(frame_time - elapsed)

        print("\nPlayback complete!")

    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        player.stop()
        tts.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
