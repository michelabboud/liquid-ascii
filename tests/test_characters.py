"""
Tests for character geometry variations.
"""

import pytest

from src.model import CharacterHead


class TestCharacterPresets:
    """Test character geometry presets."""

    def test_all_character_presets_load(self):
        """All character presets should load without errors."""
        characters = [
            "default",
            "round",
            "tall",
            "wide",
            "robot",
            "cute",
            "alien",
            "cat",
            "dog",
            "baby",
            "elder",
            "skull",
            "monster",
            "cyclops",
            "fish",
            "square",
        ]

        for char_name in characters:
            head = CharacterHead(character_name=char_name)
            assert head is not None
            assert head.character_name == char_name

    def test_invalid_character_fallback(self):
        """Invalid character name should fall back to default."""
        head = CharacterHead(character_name="nonexistent")
        # Should not crash, uses default geometry
        assert head is not None

    def test_character_sdf_callable(self):
        """Each character should provide a callable SDF."""
        characters = ["default", "robot", "alien", "baby", "cyclops"]

        for char_name in characters:
            head = CharacterHead(character_name=char_name)
            sdf = head.get_sdf()

            # Should be callable
            assert callable(sdf)

            # Should return float for a point
            distance = sdf((0, 0, 0))
            assert isinstance(distance, (int, float))

    def test_characters_have_unique_geometry(self):
        """Different characters should have different geometry."""
        # Sample characters with intentionally different designs
        chars_to_test = [
            ("default", "robot"),  # Robot has cubic proportions
            ("alien", "baby"),     # Alien is tall, baby is spherical
            ("cyclops", "fish"),   # Cyclops has 1 eye, fish has side eyes
        ]

        for char1_name, char2_name in chars_to_test:
            head1 = CharacterHead(character_name=char1_name)
            head2 = CharacterHead(character_name=char2_name)

            geom1 = head1.geometry
            geom2 = head2.geometry

            # At least one geometric parameter should differ
            different = (
                geom1.head_radii != geom2.head_radii
                or geom1.eye_separation != geom2.eye_separation
                or geom1.eye_socket_radius != geom2.eye_socket_radius
                or geom1.eyeball_radius != geom2.eyeball_radius
                or geom1.mouth_y != geom2.mouth_y
            )

            assert different, f"{char1_name} and {char2_name} have identical geometry"


class TestExtremeCharacterVariations:
    """Test extreme character variations from Phase 1."""

    def test_robot_has_mechanical_features(self):
        """Robot should have cube-like proportions and hard edges."""
        robot = CharacterHead(character_name="robot")
        geom = robot.geometry

        # Perfect cube-like proportions (all radii equal)
        assert geom.head_radii[0] == geom.head_radii[1] == geom.head_radii[2]

        # Hard edges (low smoothness)
        assert geom.eye_socket_smooth <= 0.02
        assert geom.mouth_smooth <= 0.02

        # Wide-set eyes
        assert geom.eye_separation >= 0.45

    def test_alien_has_elongated_head(self):
        """Alien should have very tall head and huge eyes."""
        alien = CharacterHead(character_name="alien")
        geom = alien.geometry

        # Elongated head (y-radius much larger than x/z)
        assert geom.head_radii[1] >= 1.8  # At least 1.8x height
        assert geom.head_radii[1] > geom.head_radii[0]
        assert geom.head_radii[1] > geom.head_radii[2]

        # Massive eyes
        assert geom.eye_socket_radius >= 0.40  # At least 3x normal
        assert geom.eyeball_radius >= 0.35

        # Very low mouth
        assert geom.mouth_y <= -0.65

    def test_baby_has_spherical_head(self):
        """Baby should have perfect sphere head with huge eyes."""
        baby = CharacterHead(character_name="baby")
        geom = baby.geometry

        # Perfect sphere (all radii equal and large)
        assert geom.head_radii[0] == geom.head_radii[1] == geom.head_radii[2]
        assert geom.head_radii[0] >= 1.2

        # Gigantic eyes
        assert geom.eye_socket_radius >= 0.30
        assert geom.eyeball_radius >= 0.25

        # Eyes high on head
        assert geom.eye_height >= 0.35

        # Close-set eyes (cute)
        assert geom.eye_separation <= 0.30

    def test_cyclops_has_single_eye(self):
        """Cyclops should have zero eye separation (one eye)."""
        cyclops = CharacterHead(character_name="cyclops")
        geom = cyclops.geometry

        # Zero eye separation = single centered eye
        assert geom.eye_separation == 0.0

        # Giant eye
        assert geom.eye_socket_radius >= 0.35
        assert geom.eyeball_radius >= 0.30

    def test_monster_has_huge_mouth(self):
        """Monster should have wide squat head with huge mouth."""
        monster = CharacterHead(character_name="monster")
        geom = monster.geometry

        # Wide squat (x and z large, y smaller)
        assert geom.head_radii[0] >= 1.2
        assert geom.head_radii[2] >= 1.0
        assert geom.head_radii[1] <= 1.1

        # Huge mouth
        assert geom.mouth_height_base >= 0.12
        assert geom.mouth_width_base >= 0.35

        # Eyes on sides
        assert geom.eye_separation >= 0.50

    def test_fish_has_eyes_on_sides(self):
        """Fish should have deep head with eyes on sides."""
        fish = CharacterHead(character_name="fish")
        geom = fish.geometry

        # Deep from front-to-back (z-radius larger)
        assert geom.head_radii[2] >= 1.2

        # Eyes very far apart (on sides)
        assert geom.eye_separation >= 0.55

        # Eyes stick out to sides (low depth)
        assert geom.eye_depth <= 0.65

    def test_square_has_angular_edges(self):
        """Square should have box head with hard edges."""
        square = CharacterHead(character_name="square")
        geom = square.geometry

        # Box proportions
        assert geom.head_radii[0] == geom.head_radii[1] == geom.head_radii[2]

        # Hard angular edges (very low smoothness)
        assert geom.eye_socket_smooth <= 0.04
        assert geom.mouth_smooth <= 0.04
        assert geom.nose_smooth <= 0.04


class TestCharacterRendering:
    """Test that characters actually render."""

    def test_all_characters_render_without_errors(self):
        """All characters should render without crashing."""
        from src.renderer import ASCIIShader, Camera, Raymarcher
        from src.renderer.quality import QualityLevel

        characters = [
            "default", "robot", "alien", "baby", "monster",
            "cyclops", "fish", "square", "skull", "elder",
        ]

        camera = Camera(position=(0, 0, -3.5), target=(0, 0, 0))
        shader = ASCIIShader()
        raymarcher = Raymarcher(
            width=40,
            height=20,
            camera=camera,
            shader=shader,
            quality=QualityLevel.LOW,
        )

        for char_name in characters:
            head = CharacterHead(character_name=char_name)
            sdf = head.get_sdf()

            # Should render without errors
            frame = raymarcher.render_frame(sdf)

            assert isinstance(frame, str)
            assert len(frame) > 0

    def test_characters_produce_different_frames(self):
        """Different characters should produce visually different frames."""
        from src.renderer import ASCIIShader, Camera, Raymarcher
        from src.renderer.quality import QualityLevel

        camera = Camera(position=(0, 0, -3.5), target=(0, 0, 0))
        shader = ASCIIShader()
        raymarcher = Raymarcher(
            width=40,
            height=20,
            camera=camera,
            shader=shader,
            quality=QualityLevel.LOW,
        )

        # Render two very different characters
        head_default = CharacterHead(character_name="default")
        frame_default = raymarcher.render_frame(head_default.get_sdf())

        head_cyclops = CharacterHead(character_name="cyclops")
        frame_cyclops = raymarcher.render_frame(head_cyclops.get_sdf())

        # Frames should be different
        assert frame_default != frame_cyclops


class TestCharacterGeometryParameters:
    """Test character geometry parameter values."""

    def test_all_radii_positive(self):
        """All radii should be positive."""
        characters = ["default", "robot", "alien", "baby", "cyclops"]

        for char_name in characters:
            head = CharacterHead(character_name=char_name)
            geom = head.geometry

            assert all(r > 0 for r in geom.head_radii)
            assert geom.eye_socket_radius > 0
            assert geom.eyeball_radius > 0
            assert geom.pupil_radius > 0

    def test_eyeball_smaller_than_socket(self):
        """Eyeball should be smaller than eye socket."""
        characters = ["default", "robot", "alien", "baby", "cyclops"]

        for char_name in characters:
            head = CharacterHead(character_name=char_name)
            geom = head.geometry

            # Eyeball shouldn't be larger than socket
            # (except for protruding eyes, but even then not much larger)
            assert geom.eyeball_radius <= geom.eye_socket_radius * 1.2

    def test_pupil_smaller_than_eyeball(self):
        """Pupil should be smaller than eyeball."""
        characters = ["default", "robot", "alien", "baby", "cyclops"]

        for char_name in characters:
            head = CharacterHead(character_name=char_name)
            geom = head.geometry

            assert geom.pupil_radius < geom.eyeball_radius

    def test_smoothness_in_valid_range(self):
        """Smoothness parameters should be in valid range."""
        characters = ["default", "robot", "alien", "baby", "cyclops"]

        for char_name in characters:
            head = CharacterHead(character_name=char_name)
            geom = head.geometry

            # Smoothness should be positive
            assert geom.eye_socket_smooth >= 0
            assert geom.eyeball_smooth >= 0
            assert geom.mouth_smooth >= 0
            assert geom.nose_smooth >= 0

            # Shouldn't be too large (would cause excessive blending)
            assert geom.eye_socket_smooth <= 0.3
            assert geom.mouth_smooth <= 0.3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
