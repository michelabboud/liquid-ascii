"""
Lighting Presets Showcase

Demonstrates all 8 lighting presets and how they affect visual appearance.
Shows dramatic, soft, metallic, and other lighting styles.
"""

import time
from src.model import CharacterHead
from src.renderer import ASCIIShader, Camera, Raymarcher, LIGHTING_PRESETS
from src.renderer.quality import QualityLevel
from src.terminal import Display


def main():
    """Cycle through all lighting presets."""
    presets = [
        "default",
        "dramatic",
        "soft",
        "metallic",
        "flat",
        "noir",
        "cartoon",
        "subsurface",
    ]

    display = Display(target_fps=15)
    terminal_width, terminal_height = display.get_size()

    # Calculate optimal resolution
    width = min(80, terminal_width - 2)
    height = min(40, terminal_height - 8)

    camera = Camera(position=(0, 0, -3.5), target=(0, 0, 0))

    display.clear()
    display.hide_cursor()

    try:
        print("Lighting Presets Showcase")
        print("=" * 50)
        print("Demonstrating 8 different lighting styles")
        print("Press Ctrl+C to exit\n")
        time.sleep(2)

        # Show each preset
        for preset_name in presets:
            display.clear()

            # Get preset description
            preset_info = LIGHTING_PRESETS[preset_name]
            description = preset_info["description"]

            # Create shader with preset
            shader = ASCIIShader(lighting_preset=preset_name)

            raymarcher = Raymarcher(
                width=width,
                height=height,
                camera=camera,
                shader=shader,
                quality=QualityLevel.MEDIUM,
            )

            # Create character
            head = CharacterHead(character_name="default")
            sdf = head.get_sdf()

            # Render
            frame = raymarcher.render_frame(sdf)

            # Display with info
            print(f"Lighting Preset: {preset_name.upper()}")
            print(f"Description: {description}")
            print(f"Ambient: {preset_info['ambient']:.2f} | "
                  f"Diffuse: {preset_info['diffuse']:.2f} | "
                  f"Specular: {preset_info['specular']:.2f}")
            print("=" * 50)
            print(frame)
            print("\nPress Ctrl+C to exit")

            time.sleep(4)

        # Compare dramatic vs soft
        print("\n\nComparison: Dramatic vs Soft")
        print("=" * 50)
        time.sleep(1)

        for _ in range(2):
            for preset_name in ["dramatic", "soft"]:
                display.clear()

                shader = ASCIIShader(lighting_preset=preset_name)
                raymarcher = Raymarcher(
                    width=width,
                    height=height,
                    camera=camera,
                    shader=shader,
                    quality=QualityLevel.MEDIUM,
                )

                head = CharacterHead(character_name="default")
                sdf = head.get_sdf()
                frame = raymarcher.render_frame(sdf)

                print(f"Lighting: {preset_name.upper()}")
                print("=" * 50)
                print(frame)
                print(f"\n{LIGHTING_PRESETS[preset_name]['description']}")

                time.sleep(3)

        # Show with different characters
        print("\n\nLighting with Different Characters")
        print("=" * 50)
        time.sleep(1)

        characters = ["robot", "alien", "baby"]
        for char_name in characters:
            display.clear()

            shader = ASCIIShader(lighting_preset="dramatic")
            raymarcher = Raymarcher(
                width=width,
                height=height,
                camera=camera,
                shader=shader,
                quality=QualityLevel.MEDIUM,
            )

            head = CharacterHead(character_name=char_name)
            sdf = head.get_sdf()
            frame = raymarcher.render_frame(sdf)

            print(f"Character: {char_name.upper()} | Lighting: DRAMATIC")
            print("=" * 50)
            print(frame)

            time.sleep(3)

        print("\n\nLighting showcase complete!")

    except KeyboardInterrupt:
        print("\n\nShowcase interrupted by user")
    finally:
        display.show_cursor()


if __name__ == "__main__":
    main()
