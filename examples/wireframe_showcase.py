"""
Wireframe/Edge Rendering Showcase

Demonstrates the wireframe rendering mode with all character variations.
Shows how edge detection creates clear character silhouettes.
"""

import time
from src.model import CharacterHead
from src.renderer import ASCIIShader, Camera, Raymarcher
from src.renderer.quality import QualityLevel
from src.terminal import Display


def main():
    """Show all characters in wireframe mode."""
    characters = [
        "default",
        "robot",
        "alien",
        "baby",
        "monster",
        "cyclops",
        "fish",
        "square",
    ]

    display = Display(target_fps=15)
    terminal_width, terminal_height = display.get_size()

    # Calculate optimal resolution
    width = min(80, terminal_width - 2)
    height = min(40, terminal_height - 5)

    camera = Camera(position=(0, 0, -3.5), target=(0, 0, 0))
    shader = ASCIIShader()
    raymarcher = Raymarcher(
        width=width,
        height=height,
        camera=camera,
        shader=shader,
        quality=QualityLevel.MEDIUM,
    )

    display.clear()
    display.hide_cursor()

    try:
        print("Wireframe/Edge Rendering Showcase")
        print("=" * 50)
        print("Showing pure edge rendering for clear silhouettes")
        print("Press Ctrl+C to exit\n")
        time.sleep(2)

        for char_name in characters:
            display.clear()

            # Create character
            head = CharacterHead(character_name=char_name)
            sdf = head.get_sdf()

            # Render in wireframe mode
            frame = raymarcher.render_frame_wireframe(
                sdf,
                edge_char="#",
                edge_threshold=0.5,
                edge_thickness=1,
            )

            # Display
            status = f"Character: {char_name.upper()} | Wireframe Mode | Press Ctrl+C to exit"
            print(frame)
            print("\n" + status)

            time.sleep(3)

        # Show edge thickness variations
        print("\n\nEdge Thickness Variations")
        print("=" * 50)
        time.sleep(1)

        head = CharacterHead(character_name="default")
        sdf = head.get_sdf()

        for thickness in [1, 2, 3]:
            display.clear()

            frame = raymarcher.render_frame_wireframe(
                sdf,
                edge_char="#",
                edge_threshold=0.5,
                edge_thickness=thickness,
            )

            status = f"Edge Thickness: {thickness} | Press Ctrl+C to exit"
            print(frame)
            print("\n" + status)

            time.sleep(2)

        # Show edge characters
        print("\n\nDifferent Edge Characters")
        print("=" * 50)
        time.sleep(1)

        edge_chars = ["#", "*", "@", "█", "▓"]

        for edge_char in edge_chars:
            display.clear()

            frame = raymarcher.render_frame_wireframe(
                sdf,
                edge_char=edge_char,
                edge_threshold=0.5,
                edge_thickness=1,
            )

            status = f"Edge Character: '{edge_char}' | Press Ctrl+C to exit"
            print(frame)
            print("\n" + status)

            time.sleep(2)

        print("\n\nWireframe showcase complete!")

    except KeyboardInterrupt:
        print("\n\nShowcase interrupted by user")
    finally:
        display.show_cursor()


if __name__ == "__main__":
    main()
