#!/usr/bin/env python3
"""
Rainbow Colors Demo

Demonstrates the rainbow color effects on the animated head.
Shows different color modes: horizontal, vertical, radial, wave.
"""

import os
import sys
import time

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from src.model import Head
from src.renderer import ASCIIShader, Camera, Raymarcher
from src.terminal.colors import RainbowColors, reset_color, rgb_to_ansi_escape


def render_with_rainbow(frame: str, rainbow: RainbowColors, width: int, height: int) -> str:
    """Apply rainbow colors to a frame."""
    lines = frame.split("\n")
    output_lines = []

    for row, line in enumerate(lines):
        colored_line = ""
        for col, char in enumerate(line):
            if char.strip():
                color = rainbow.get_color_for_char(col, row, width, len(lines))
                colored_line += rgb_to_ansi_escape(color.r, color.g, color.b)
                colored_line += char
                colored_line += reset_color()
            else:
                colored_line += char
        output_lines.append(colored_line)

    return "\n".join(output_lines)


def main():
    # Setup renderer
    camera = Camera(position=(0, 0, -3.5), target=(0, 0, 0))
    shader = ASCIIShader(ramp="standard")

    width, height = 80, 35
    raymarcher = Raymarcher(
        width=width,
        height=height,
        camera=camera,
        shader=shader,
        max_steps=50,
    )

    # Create animated head
    head = Head(enable_idle_animation=True)

    # Rainbow modes to cycle through
    modes = ["horizontal", "vertical", "radial", "diagonal", "wave"]
    current_mode = 0
    rainbow = RainbowColors(speed=1.0, mode=modes[current_mode])

    mode_switch_time = 5.0  # Switch mode every 5 seconds
    mode_timer = 0.0

    print("Rainbow Demo")
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

            # Switch rainbow mode periodically
            mode_timer += dt
            if mode_timer >= mode_switch_time:
                mode_timer = 0.0
                current_mode = (current_mode + 1) % len(modes)
                rainbow = RainbowColors(speed=1.0, mode=modes[current_mode])

            # Update head animation
            head.update(dt)

            # Render base frame
            sdf = head.get_sdf()
            frame = raymarcher.render_frame(sdf)

            # Apply rainbow colors
            colored_frame = render_with_rainbow(frame, rainbow, width, height)

            # Display
            os.system("clear" if os.name == "posix" else "cls")
            print(colored_frame)
            print(
                f"\nRainbow mode: {modes[current_mode]} | Switch in: {mode_switch_time - mode_timer:.1f}s"
            )

            # Maintain frame rate
            elapsed = time.time() - current_time
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)

    except KeyboardInterrupt:
        print(reset_color() + "\nExiting...")


if __name__ == "__main__":
    main()
