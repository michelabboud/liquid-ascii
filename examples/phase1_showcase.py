"""
Phase 1 Complete Showcase

Demonstrates ALL Phase 1 features:
- Wireframe/edge rendering
- 8 lighting presets
- Cel-shading with band control
- Extreme character variations

This is a comprehensive demonstration of character differentiation.
"""

import time
from src.model import CharacterHead
from src.renderer import ASCIIShader, Camera, Raymarcher, LIGHTING_PRESETS
from src.renderer.quality import QualityLevel
from src.terminal import Display


def main():
    """Comprehensive Phase 1 feature showcase."""
    display = Display(target_fps=15)
    terminal_width, terminal_height = display.get_size()

    # Calculate optimal resolution
    width = min(80, terminal_width - 2)
    height = min(40, terminal_height - 10)

    camera = Camera(position=(0, 0, -3.5), target=(0, 0, 0))

    display.clear()
    display.hide_cursor()

    try:
        # Title
        print("=" * 60)
        print("PHASE 1 COMPLETE SHOWCASE")
        print("Character Differentiation Features")
        print("=" * 60)
        print()
        print("Features demonstrated:")
        print("  ✓ Wireframe/edge rendering")
        print("  ✓ 8 dramatic lighting presets")
        print("  ✓ Cel-shading/toon style")
        print("  ✓ Extreme character variations")
        print()
        print("Press Ctrl+C to exit")
        print("=" * 60)
        time.sleep(4)

        # === WIREFRAME DEMONSTRATION ===
        print("\n\n1. WIREFRAME RENDERING")
        print("=" * 60)
        print("Pure edge rendering for clear character outlines")
        time.sleep(2)

        characters = ["robot", "alien", "cyclops"]
        for char_name in characters:
            display.clear()

            shader = ASCIIShader()
            raymarcher = Raymarcher(
                width=width, height=height, camera=camera, shader=shader,
                quality=QualityLevel.MEDIUM,
            )

            head = CharacterHead(character_name=char_name)
            sdf = head.get_sdf()
            frame = raymarcher.render_frame_wireframe(sdf, edge_char="#")

            print(f"Wireframe: {char_name.upper()}")
            print("=" * 60)
            print(frame)

            time.sleep(2)

        # === LIGHTING PRESETS DEMONSTRATION ===
        print("\n\n2. LIGHTING PRESETS")
        print("=" * 60)
        print("8 different lighting styles for varied moods")
        time.sleep(2)

        presets = ["default", "dramatic", "metallic", "noir"]
        head = CharacterHead(character_name="default")

        for preset_name in presets:
            display.clear()

            shader = ASCIIShader(lighting_preset=preset_name)
            raymarcher = Raymarcher(
                width=width, height=height, camera=camera, shader=shader,
                quality=QualityLevel.MEDIUM,
            )

            sdf = head.get_sdf()
            frame = raymarcher.render_frame(sdf)

            print(f"Lighting: {preset_name.upper()}")
            print(f"{LIGHTING_PRESETS[preset_name]['description']}")
            print("=" * 60)
            print(frame)

            time.sleep(2)

        # === CEL-SHADING DEMONSTRATION ===
        print("\n\n3. CEL-SHADING / TOON STYLE")
        print("=" * 60)
        print("Posterized lighting for comic book aesthetic")
        time.sleep(2)

        # Show progression
        settings = [
            (False, None, "Continuous (no cel-shading)"),
            (True, 3, "3 bands (classic cel-shading)"),
            (True, 2, "2 bands (stark contrast)"),
        ]

        for cel_shading, cel_bands, desc in settings:
            display.clear()

            shader = ASCIIShader(
                cel_shading=cel_shading,
                cel_bands=cel_bands if cel_bands else 3
            )
            raymarcher = Raymarcher(
                width=width, height=height, camera=camera, shader=shader,
                quality=QualityLevel.MEDIUM,
            )

            sdf = head.get_sdf()
            frame = raymarcher.render_frame(sdf)

            print(f"Shading: {desc}")
            print("=" * 60)
            print(frame)

            time.sleep(2)

        # === CHARACTER VARIATIONS DEMONSTRATION ===
        print("\n\n4. EXTREME CHARACTER VARIATIONS")
        print("=" * 60)
        print("Unique, instantly recognizable character designs")
        time.sleep(2)

        extreme_chars = [
            ("robot", "Cube-like with hard edges"),
            ("alien", "2x height, 3x eye size"),
            ("baby", "Perfect sphere, huge eyes"),
            ("cyclops", "ONE GIANT centered eye"),
            ("monster", "Wide with huge mouth"),
            ("fish", "Eyes on sides, deep head"),
        ]

        shader = ASCIIShader(lighting_preset="dramatic")
        raymarcher = Raymarcher(
            width=width, height=height, camera=camera, shader=shader,
            quality=QualityLevel.MEDIUM,
        )

        for char_name, desc in extreme_chars:
            display.clear()

            head = CharacterHead(character_name=char_name)
            sdf = head.get_sdf()
            frame = raymarcher.render_frame(sdf)

            print(f"Character: {char_name.upper()}")
            print(f"Features: {desc}")
            print("=" * 60)
            print(frame)

            time.sleep(2)

        # === COMBINATION DEMONSTRATION ===
        print("\n\n5. FEATURE COMBINATIONS")
        print("=" * 60)
        print("Combining multiple Phase 1 features")
        time.sleep(2)

        combinations = [
            ("robot", "dramatic", True, 3, "Robot + Dramatic + Cel-shading"),
            ("alien", "noir", False, 3, "Alien + Noir lighting"),
            ("baby", "soft", True, 2, "Baby + Soft + 2-band cel-shading"),
        ]

        for char_name, lighting, cel, bands, desc in combinations:
            display.clear()

            shader = ASCIIShader(
                lighting_preset=lighting,
                cel_shading=cel,
                cel_bands=bands
            )
            raymarcher = Raymarcher(
                width=width, height=height, camera=camera, shader=shader,
                quality=QualityLevel.MEDIUM,
            )

            head = CharacterHead(character_name=char_name)
            sdf = head.get_sdf()
            frame = raymarcher.render_frame(sdf)

            print(f"Combination: {desc}")
            print("=" * 60)
            print(frame)

            time.sleep(3)

        # === FINALE ===
        display.clear()
        print("\n\n" + "=" * 60)
        print("PHASE 1 SHOWCASE COMPLETE!")
        print("=" * 60)
        print()
        print("Summary:")
        print("  ✓ Wireframe mode creates clear silhouettes")
        print("  ✓ 8 lighting presets provide varied moods")
        print("  ✓ Cel-shading adds comic book style")
        print("  ✓ 15+ character variations, all unique")
        print()
        print("Result: Characters are now INSTANTLY RECOGNIZABLE!")
        print()
        print("Next: Phase 2 - GPU Acceleration (30-60 FPS)")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\nShowcase interrupted by user")
    finally:
        display.show_cursor()


if __name__ == "__main__":
    main()
