"""
Cel-Shading/Toon Style Showcase

Demonstrates cel-shading posterization with different band counts.
Shows how discrete lighting levels create a comic book/anime aesthetic.
"""

import time
from src.model import CharacterHead
from src.renderer import ASCIIShader, Camera, Raymarcher
from src.renderer.quality import QualityLevel
from src.terminal import Display


def main():
    """Show cel-shading with different band counts."""
    display = Display(target_fps=15)
    terminal_width, terminal_height = display.get_size()

    # Calculate optimal resolution
    width = min(80, terminal_width - 2)
    height = min(40, terminal_height - 8)

    camera = Camera(position=(0, 0, -3.5), target=(0, 0, 0))

    display.clear()
    display.hide_cursor()

    try:
        print("Cel-Shading/Toon Style Showcase")
        print("=" * 50)
        print("Demonstrating posterized lighting for comic book look")
        print("Press Ctrl+C to exit\n")
        time.sleep(2)

        # Show progression from continuous to discrete
        print("Progression: Continuous → Discrete Lighting")
        print("=" * 50)
        time.sleep(1)

        head = CharacterHead(character_name="default")
        sdf = head.get_sdf()

        # No cel-shading (continuous)
        display.clear()
        shader = ASCIIShader(cel_shading=False)
        raymarcher = Raymarcher(
            width=width, height=height, camera=camera, shader=shader,
            quality=QualityLevel.MEDIUM,
        )
        frame = raymarcher.render_frame(sdf)

        print("Continuous Shading (No Cel-Shading)")
        print("Smooth gradients, photorealistic")
        print("=" * 50)
        print(frame)
        time.sleep(4)

        # Show different band counts
        band_counts = [2, 3, 4, 6]

        for bands in band_counts:
            display.clear()

            shader = ASCIIShader(cel_shading=True, cel_bands=bands)
            raymarcher = Raymarcher(
                width=width, height=height, camera=camera, shader=shader,
                quality=QualityLevel.MEDIUM,
            )

            frame = raymarcher.render_frame(sdf)

            print(f"Cel-Shading: {bands} Bands")
            print(f"Discrete lighting levels: {bands}")
            if bands == 2:
                print("Effect: Stark light/dark separation (minimal shading)")
            elif bands == 3:
                print("Effect: Classic cel-shading (comic book style)")
            elif bands == 4:
                print("Effect: Balanced posterization")
            else:
                print("Effect: Subtle posterization (more gradual)")
            print("=" * 50)
            print(frame)
            print("\nPress Ctrl+C to exit")

            time.sleep(4)

        # Show cel-shading with different lighting presets
        print("\n\nCel-Shading + Lighting Presets")
        print("=" * 50)
        time.sleep(1)

        presets = ["dramatic", "soft", "metallic"]

        for preset_name in presets:
            display.clear()

            shader = ASCIIShader(
                lighting_preset=preset_name,
                cel_shading=True,
                cel_bands=3
            )

            raymarcher = Raymarcher(
                width=width, height=height, camera=camera, shader=shader,
                quality=QualityLevel.MEDIUM,
            )

            frame = raymarcher.render_frame(sdf)

            print(f"Preset: {preset_name.upper()} + Cel-Shading (3 bands)")
            print("=" * 50)
            print(frame)

            time.sleep(4)

        # Show cel-shading with different characters
        print("\n\nCel-Shading with Different Characters")
        print("=" * 50)
        time.sleep(1)

        characters = [
            ("robot", "Mechanical look with sharp edges"),
            ("alien", "Elongated features with banding"),
            ("baby", "Soft spherical shape, posterized"),
        ]

        for char_name, desc in characters:
            display.clear()

            shader = ASCIIShader(cel_shading=True, cel_bands=3)
            raymarcher = Raymarcher(
                width=width, height=height, camera=camera, shader=shader,
                quality=QualityLevel.MEDIUM,
            )

            head = CharacterHead(character_name=char_name)
            sdf = head.get_sdf()
            frame = raymarcher.render_frame(sdf)

            print(f"Character: {char_name.upper()}")
            print(f"{desc}")
            print("=" * 50)
            print(frame)

            time.sleep(3)

        # Comparison: 2 bands vs 6 bands
        print("\n\nComparison: 2 Bands vs 6 Bands")
        print("=" * 50)
        time.sleep(1)

        for _ in range(2):
            for bands in [2, 6]:
                display.clear()

                shader = ASCIIShader(cel_shading=True, cel_bands=bands)
                raymarcher = Raymarcher(
                    width=width, height=height, camera=camera, shader=shader,
                    quality=QualityLevel.MEDIUM,
                )

                head = CharacterHead(character_name="default")
                sdf = head.get_sdf()
                frame = raymarcher.render_frame(sdf)

                print(f"Cel-Shading: {bands} Bands")
                print("=" * 50)
                print(frame)

                time.sleep(3)

        print("\n\nCel-shading showcase complete!")

    except KeyboardInterrupt:
        print("\n\nShowcase interrupted by user")
    finally:
        display.show_cursor()


if __name__ == "__main__":
    main()
