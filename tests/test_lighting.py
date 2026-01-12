"""
Tests for lighting presets and lighting calculations.
"""

import numpy as np
import pytest

from src.renderer import ASCIIShader, LIGHTING_PRESETS


class TestLightingPresets:
    """Test lighting preset system."""

    def test_all_presets_exist(self):
        """All documented lighting presets should exist."""
        expected_presets = [
            "default",
            "dramatic",
            "soft",
            "metallic",
            "flat",
            "noir",
            "cartoon",
            "subsurface",
        ]

        for preset in expected_presets:
            assert preset in LIGHTING_PRESETS
            assert "ambient" in LIGHTING_PRESETS[preset]
            assert "diffuse" in LIGHTING_PRESETS[preset]
            assert "specular" in LIGHTING_PRESETS[preset]
            assert "specular_power" in LIGHTING_PRESETS[preset]
            assert "description" in LIGHTING_PRESETS[preset]

    def test_preset_values_in_valid_range(self):
        """Lighting preset values should be in valid ranges."""
        for name, preset in LIGHTING_PRESETS.items():
            # Ambient, diffuse, specular should be 0-1
            assert 0.0 <= preset["ambient"] <= 1.0, f"{name} ambient out of range"
            assert 0.0 <= preset["diffuse"] <= 1.0, f"{name} diffuse out of range"
            assert 0.0 <= preset["specular"] <= 1.0, f"{name} specular out of range"

            # Specular power should be positive
            assert preset["specular_power"] > 0, f"{name} specular_power invalid"

            # Description should be non-empty
            assert len(preset["description"]) > 0, f"{name} has no description"

    def test_shader_applies_preset_at_init(self):
        """Shader should apply preset during initialization."""
        shader = ASCIIShader(lighting_preset="dramatic")

        dramatic = LIGHTING_PRESETS["dramatic"]
        assert shader.ambient == dramatic["ambient"]
        assert shader.diffuse == dramatic["diffuse"]
        assert shader.specular == dramatic["specular"]
        assert shader.specular_power == dramatic["specular_power"]

    def test_shader_preset_overrides_individual_params(self):
        """Lighting preset should override individual parameters."""
        # If both preset and individual params provided, preset wins
        shader = ASCIIShader(
            ambient=0.5,  # These should be ignored
            diffuse=0.5,
            specular=0.5,
            lighting_preset="noir",  # This should win
        )

        noir = LIGHTING_PRESETS["noir"]
        assert shader.ambient == noir["ambient"]
        assert shader.diffuse == noir["diffuse"]
        assert shader.specular == noir["specular"]

    def test_apply_lighting_preset_method(self):
        """apply_lighting_preset() should change shader lighting."""
        shader = ASCIIShader(lighting_preset="default")

        # Apply dramatic preset
        shader.apply_lighting_preset("dramatic")

        dramatic = LIGHTING_PRESETS["dramatic"]
        assert shader.ambient == dramatic["ambient"]
        assert shader.diffuse == dramatic["diffuse"]
        assert shader.specular == dramatic["specular"]
        assert shader.specular_power == dramatic["specular_power"]

    def test_apply_invalid_preset_raises_error(self):
        """Applying invalid preset should raise ValueError."""
        shader = ASCIIShader()

        with pytest.raises(ValueError, match="Unknown lighting preset"):
            shader.apply_lighting_preset("nonexistent_preset")

    def test_dramatic_vs_soft_contrast(self):
        """Dramatic should have more contrast than soft."""
        dramatic = LIGHTING_PRESETS["dramatic"]
        soft = LIGHTING_PRESETS["soft"]

        # Dramatic has lower ambient (darker shadows)
        assert dramatic["ambient"] < soft["ambient"]

        # Dramatic has higher specular (brighter highlights)
        assert dramatic["specular"] > soft["specular"]

    def test_metallic_has_sharp_specular(self):
        """Metallic preset should have sharp, bright specularity."""
        metallic = LIGHTING_PRESETS["metallic"]

        # High specular intensity
        assert metallic["specular"] >= 0.8

        # Sharp specular (high power)
        assert metallic["specular_power"] >= 50

    def test_flat_has_minimal_shading(self):
        """Flat preset should have minimal directional shading."""
        flat = LIGHTING_PRESETS["flat"]

        # High ambient (fills in shadows)
        assert flat["ambient"] >= 0.7

        # Low or no specular
        assert flat["specular"] <= 0.1


class TestLightingCalculations:
    """Test lighting computation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.shader = ASCIIShader()

    def test_compute_lighting_returns_float(self):
        """compute_lighting should return a float."""
        normal = np.array([0, 0, 1])  # Forward-facing normal
        intensity = self.shader.compute_lighting(normal)

        assert isinstance(intensity, (float, np.floating))

    def test_lighting_clamped_to_0_1(self):
        """Lighting intensity should be clamped to [0, 1]."""
        # Test various normals
        normals = [
            [0, 0, 1],  # Forward
            [0, 0, -1],  # Backward
            [1, 0, 0],  # Right
            [0, 1, 0],  # Up
        ]

        for normal in normals:
            intensity = self.shader.compute_lighting(np.array(normal))
            assert 0.0 <= intensity <= 1.0

    def test_lighting_with_view_direction(self):
        """Lighting with view direction should include specular."""
        normal = np.array([0, 0, 1])
        view_dir = np.array([0, 0, -1])  # Looking toward surface

        # With view direction (includes specular)
        intensity_with_spec = self.shader.compute_lighting(normal, view_dir)

        # Without view direction (no specular)
        intensity_no_spec = self.shader.compute_lighting(normal, None)

        # Should be different if specular > 0
        if self.shader.specular > 0:
            assert intensity_with_spec != intensity_no_spec

    def test_facing_light_brighter_than_away(self):
        """Surface facing light should be brighter than facing away."""
        # Normal pointing toward light
        normal_toward = np.array([0.5, 0.8, -0.6])  # Matching default light dir
        normal_toward = normal_toward / np.linalg.norm(normal_toward)

        # Normal pointing away from light
        normal_away = -normal_toward

        intensity_toward = self.shader.compute_lighting(normal_toward)
        intensity_away = self.shader.compute_lighting(normal_away)

        # Facing light should be brighter
        assert intensity_toward > intensity_away

    def test_compute_lighting_batch_shape(self):
        """Batch lighting should preserve shape."""
        # Create batch of normals
        normals = np.random.rand(10, 20, 3)
        normals = normals / np.linalg.norm(normals, axis=-1, keepdims=True)

        intensities = self.shader.compute_lighting_batch(normals)

        # Should return array of correct shape
        assert intensities.shape == (10, 20)
        assert np.all((intensities >= 0) & (intensities <= 1))

    def test_batch_and_single_lighting_match(self):
        """Batch and single lighting should give same results."""
        normals = np.random.rand(5, 5, 3)
        normals = normals / np.linalg.norm(normals, axis=-1, keepdims=True)

        # Batch computation
        intensities_batch = self.shader.compute_lighting_batch(normals)

        # Single computations
        intensities_single = np.zeros((5, 5))
        for y in range(5):
            for x in range(5):
                intensities_single[y, x] = self.shader.compute_lighting(normals[y, x])

        # Should be approximately equal
        np.testing.assert_allclose(intensities_batch, intensities_single, rtol=1e-5)

    def test_lighting_with_zero_normal_no_crash(self):
        """Zero normal should not crash lighting calculation."""
        zero_normal = np.array([0, 0, 0])

        # Should not raise exception
        intensity = self.shader.compute_lighting(zero_normal)

        # Should return valid intensity
        assert 0.0 <= intensity <= 1.0

    def test_different_presets_give_different_results(self):
        """Different presets should produce different lighting."""
        normal = np.array([0, 0, 1])
        view_dir = np.array([0, 0, -1])

        results = {}
        for preset_name in ["default", "dramatic", "soft", "metallic"]:
            shader = ASCIIShader(lighting_preset=preset_name)
            results[preset_name] = shader.compute_lighting(normal, view_dir)

        # All results should be different
        values = list(results.values())
        assert len(set(values)) == len(values), "Presets should produce different lighting"


class TestLightDirection:
    """Test light direction changes."""

    def test_set_light_direction(self):
        """Should be able to update light direction."""
        shader = ASCIIShader()

        new_direction = (1, 0, 0)  # Light from right
        shader.set_light_direction(new_direction)

        # Direction should be normalized
        assert np.allclose(np.linalg.norm(shader.light_dir), 1.0)

    def test_light_from_different_directions(self):
        """Lighting should change based on light direction."""
        normal = np.array([0, 0, 1])  # Forward-facing

        shader = ASCIIShader()

        # Light from front
        shader.set_light_direction((0, 0, -1))
        intensity_front = shader.compute_lighting(normal)

        # Light from side
        shader.set_light_direction((1, 0, 0))
        intensity_side = shader.compute_lighting(normal)

        # Should be different
        assert intensity_front != intensity_side


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
