"""
Character Variations Showcase

Demonstrates all character geometry variations with descriptions.
Shows how different proportions create instantly recognizable characters.
"""

import time
from src.model import CharacterHead
from src.renderer import ASCIIShader, Camera, Raymarcher
from src.renderer.quality import QualityLevel
from src.terminal import Display


# Character descriptions
CHARACTER_INFO = {
    "default": "Balanced proportions, standard features",
    "robot": "Cube-like head, hard edges, mechanical look, wide-set eyes",
    "alien": "2x head height, 3x eye size, very high features, elongated",
    "baby": "Perfect sphere, gigantic eyes (kawaii!), high features",
    "monster": "Wide squat head, huge gaping mouth, bulbous nose, low eyes",
    "cyclops": "ONE GIANT centered eye, large head",
    "fish": "Deep head, eyes on sides, wide O-mouth",
    "square": "Angular box head with hard edges",
    "round": "Spherical head with close-set eyes",
    "tall": "Elongated vertical proportions",
    "wide": "Broad horizontal proportions",
    "cute": "Large eyes, small mouth, rounded features",
    "skull": "Large eye sockets, minimal eyeballs, hollow look",
    "elder": "Thin face, prominent nose, smaller eyes",
}


def main():
    """Show all character variations."""
    display = Display(target_fps=15)
    terminal_width, terminal_height = display.get_size()

    # Calculate optimal resolution
    width = min(80, terminal_width - 2)
    height = min(40, terminal_height - 10)

    camera = Camera(position=(0, 0, -3.5), target=(0, 0, 0))
    shader = ASCIIShader(lighting_preset="dramatic")  # Dramatic for clear features

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
        print("Character Variations Showcase")
        print("=" * 50)
        print("Showing extreme character geometry variations")
        print("All characters have unique, recognizable silhouettes")
        print("Press Ctrl+C to exit\n")
        time.sleep(3)

        # Show each character
        for char_name, description in CHARACTER_INFO.items():
            display.clear()

            # Create character
            head = CharacterHead(character_name=char_name)
            sdf = head.get_sdf()

            # Render
            frame = raymarcher.render_frame(sdf)

            # Display
            print(f"Character: {char_name.upper()}")
            print(f"Features: {description}")
            print("=" * 50)
            print(frame)
            print("\nPress Ctrl+C to exit")

            time.sleep(4)

        # Show "extreme" variations side-by-side comparisons
        print("\n\nExtreme Variations Comparison")
        print("=" * 50)
        time.sleep(1)

        extreme_chars = [
            ("robot", "Cube-like, mechanical"),
            ("alien", "Tall with huge eyes"),
            ("baby", "Sphere with giant eyes"),
            ("cyclops", "ONE GIANT EYE"),
        ]

        for _ in range(2):
            for char_name, desc in extreme_chars:
                display.clear()

                head = CharacterHead(character_name=char_name)
                sdf = head.get_sdf()
                frame = raymarcher.render_frame(sdf)

                print(f"{char_name.upper()}: {desc}")
                print("=" * 50)
                print(frame)

                time.sleep(2)

        # Show wireframe comparisons
        print("\n\nWireframe Comparison")
        print("=" * 50)
        print("Same characters in wireframe for clear silhouettes")
        time.sleep(1)

        for char_name, desc in extreme_chars:
            display.clear()

            head = CharacterHead(character_name=char_name)
            sdf = head.get_sdf()
            frame = raymarcher.render_frame_wireframe(sdf, edge_char="#")

            print(f"{char_name.upper()} (Wireframe): {desc}")
            print("=" * 50)
            print(frame)

            time.sleep(2)

        # Animation: cycle through characters
        print("\n\nRapid Cycle Through All Characters")
        print("=" * 50)
        time.sleep(1)

        characters = list(CHARACTER_INFO.keys())
        for _ in range(2):  # Two full cycles
            for char_name in characters:
                display.clear()

                head = CharacterHead(character_name=char_name)
                sdf = head.get_sdf()
                frame = raymarcher.render_frame(sdf)

                print(f"Character: {char_name.upper()}")
                print("=" * 50)
                print(frame)

                time.sleep(0.8)  # Quick cycle

        print("\n\nCharacter showcase complete!")

    except KeyboardInterrupt:
        print("\n\nShowcase interrupted by user")
    finally:
        display.show_cursor()


if __name__ == "__main__":
    main()
