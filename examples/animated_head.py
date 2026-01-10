#!/usr/bin/env python3
"""
Animated Head Example

Shows a head with idle animation including:
- Organic subtle movement
- Natural blinking
- Breathing motion

Press Ctrl+C to exit.
"""

import sys
import time
import os

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from src.renderer import Raymarcher, Camera, ASCIIShader
from src.model import Head


def main():
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

    print("Animated Head Demo")
    print("Press Ctrl+C to exit")
    print()
    time.sleep(1)

    target_fps = 15
    frame_time = 1.0 / target_fps
    last_time = time.time()

    try:
        while True:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            # Update head animation
            head.update(dt)

            # Get current SDF and render
            sdf = head.get_sdf()
            frame = raymarcher.render_frame(sdf)

            # Clear and draw
            os.system('clear' if os.name == 'posix' else 'cls')
            print(frame)
            print(f"\nFPS: {1/dt:.1f} | Blink: {head.state.blink_amount:.2f}")

            # Maintain frame rate
            elapsed = time.time() - current_time
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)

    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()
