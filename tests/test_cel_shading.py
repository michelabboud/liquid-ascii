"""
Tests for cel-shading/toon style rendering.
"""

import numpy as np
import pytest

from src.renderer import ASCIIShader


class TestCelShading:
    """Test cel-shading posterization."""

    def test_cel_shading_disabled_by_default(self):
        """Cel-shading should be disabled by default."""
        shader = ASCIIShader()
        assert shader.cel_shading is False

    def test_cel_shading_can_be_enabled(self):
        """Cel-shading can be enabled at initialization."""
        shader = ASCIIShader(cel_shading=True)
        assert shader.cel_shading is True

    def test_cel_bands_default(self):
        """Default cel bands should be 3."""
        shader = ASCIIShader(cel_shading=True)
        assert shader.cel_bands == 3

    def test_cel_bands_custom(self):
        """Custom cel bands should be respected."""
        shader = ASCIIShader(cel_shading=True, cel_bands=5)
        assert shader.cel_bands == 5

    def test_cel_bands_clamped_to_range(self):
        """Cel bands should be clamped to 2-8."""
        # Too low (should clamp to 2)
        shader_low = ASCIIShader(cel_shading=True, cel_bands=1)
        assert shader_low.cel_bands == 2

        # Too high (should clamp to 8)
        shader_high = ASCIIShader(cel_shading=True, cel_bands=20)
        assert shader_high.cel_bands == 8

        # Valid range
        shader_valid = ASCIIShader(cel_shading=True, cel_bands=4)
        assert shader_valid.cel_bands == 4

    def test_posterize_intensity_returns_quantized_value(self):
        """Posterize should return discrete values."""
        shader = ASCIIShader(cel_shading=True, cel_bands=3)

        # Test various intensities
        intensities = [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
        posterized = [shader._posterize_intensity(i) for i in intensities]

        # Should have limited unique values (3 bands)
        unique_values = set(posterized)
        assert len(unique_values) <= 3

    def test_posterize_intensity_band_centers(self):
        """Posterized values should be at band centers."""
        shader = ASCIIShader(cel_shading=True, cel_bands=3)

        # Expected band centers for 3 bands:
        # Band 0: 0.0-0.33 → center 0.167
        # Band 1: 0.33-0.67 → center 0.5
        # Band 2: 0.67-1.0 → center 0.833

        expected_centers = [
            (0 + 0.5) / 3,  # 0.167
            (1 + 0.5) / 3,  # 0.5
            (2 + 0.5) / 3,  # 0.833
        ]

        # Test values in each band
        assert abs(shader._posterize_intensity(0.1) - expected_centers[0]) < 1e-6
        assert abs(shader._posterize_intensity(0.5) - expected_centers[1]) < 1e-6
        assert abs(shader._posterize_intensity(0.9) - expected_centers[2]) < 1e-6

    def test_posterize_intensity_batch(self):
        """Batch posterization should work on arrays."""
        shader = ASCIIShader(cel_shading=True, cel_bands=3)

        intensities = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
        posterized = shader._posterize_intensity_batch(intensities)

        # Should return array of same shape
        assert posterized.shape == intensities.shape

        # Should have limited unique values
        unique_values = np.unique(posterized)
        assert len(unique_values) <= 3

    def test_posterize_batch_matches_single(self):
        """Batch posterization should match single posterization."""
        shader = ASCIIShader(cel_shading=True, cel_bands=4)

        intensities = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])

        # Batch version
        posterized_batch = shader._posterize_intensity_batch(intensities)

        # Single version
        posterized_single = np.array([
            shader._posterize_intensity(i) for i in intensities
        ])

        np.testing.assert_allclose(posterized_batch, posterized_single, rtol=1e-6)

    def test_cel_shading_reduces_lighting_continuity(self):
        """Cel-shading should create discrete lighting steps."""
        normal = np.array([0, 0, 1])
        view_dir = np.array([0, 0, -1])

        # Without cel-shading
        shader_continuous = ASCIIShader(cel_shading=False)

        # With cel-shading
        shader_cel = ASCIIShader(cel_shading=True, cel_bands=3)

        # Compute lighting for slightly different normals
        normals = [
            np.array([0, 0, 1]),
            np.array([0.1, 0, 0.995]),
            np.array([0.2, 0, 0.98]),
        ]

        # Normalize
        normals = [n / np.linalg.norm(n) for n in normals]

        # Continuous shading should have gradual changes
        continuous_results = [
            shader_continuous.compute_lighting(n, view_dir) for n in normals
        ]

        # Cel-shading might have same value for nearby normals
        cel_results = [
            shader_cel.compute_lighting(n, view_dir) for n in normals
        ]

        # Continuous should have more unique values
        assert len(set(continuous_results)) >= len(set(cel_results))

    def test_cel_shading_with_different_band_counts(self):
        """Different band counts should produce different quantization."""
        normal = np.array([0, 0, 1])

        # Create range of intensities by varying light direction
        test_normals = []
        for angle in np.linspace(0, np.pi / 2, 20):
            n = np.array([np.sin(angle), 0, np.cos(angle)])
            test_normals.append(n)

        # 2 bands
        shader_2 = ASCIIShader(cel_shading=True, cel_bands=2)
        results_2 = [shader_2.compute_lighting(n) for n in test_normals]
        unique_2 = len(set(results_2))

        # 4 bands
        shader_4 = ASCIIShader(cel_shading=True, cel_bands=4)
        results_4 = [shader_4.compute_lighting(n) for n in test_normals]
        unique_4 = len(set(results_4))

        # 8 bands
        shader_8 = ASCIIShader(cel_shading=True, cel_bands=8)
        results_8 = [shader_8.compute_lighting(n) for n in test_normals]
        unique_8 = len(set(results_8))

        # More bands = more unique values
        assert unique_2 <= unique_4 <= unique_8

    def test_cel_shading_preserves_lighting_order(self):
        """Cel-shading should preserve relative brightness order."""
        view_dir = np.array([0, 0, -1])

        shader = ASCIIShader(cel_shading=True, cel_bands=3)

        # Bright surface (facing light)
        normal_bright = np.array([0.5, 0.8, -0.6])
        normal_bright = normal_bright / np.linalg.norm(normal_bright)

        # Dark surface (facing away)
        normal_dark = -normal_bright

        # Medium surface (perpendicular)
        normal_medium = np.array([1, 0, 0])

        intensity_bright = shader.compute_lighting(normal_bright, view_dir)
        intensity_medium = shader.compute_lighting(normal_medium, view_dir)
        intensity_dark = shader.compute_lighting(normal_dark, view_dir)

        # Order should be preserved
        assert intensity_bright >= intensity_medium >= intensity_dark

    def test_cel_shading_batch_computation(self):
        """Cel-shading should work with batch lighting computation."""
        shader = ASCIIShader(cel_shading=True, cel_bands=3)

        # Create batch of normals
        normals = np.random.rand(5, 5, 3)
        normals = normals / np.linalg.norm(normals, axis=-1, keepdims=True)

        # Compute lighting (should apply cel-shading)
        intensities = shader.compute_lighting_batch(normals)

        # Should return quantized values
        unique_values = np.unique(intensities)
        assert len(unique_values) <= 3  # 3 bands

    def test_cel_shading_works_with_lighting_presets(self):
        """Cel-shading should work with all lighting presets."""
        presets = ["default", "dramatic", "soft", "metallic"]
        normal = np.array([0, 0, 1])

        for preset in presets:
            shader = ASCIIShader(
                lighting_preset=preset,
                cel_shading=True,
                cel_bands=4
            )

            # Should compute without errors
            intensity = shader.compute_lighting(normal)

            # Should return quantized value
            assert 0.0 <= intensity <= 1.0

    def test_cel_shading_values_in_valid_range(self):
        """Posterized values should always be in [0, 1]."""
        shader = ASCIIShader(cel_shading=True, cel_bands=3)

        # Test edge cases
        test_values = [0.0, 0.001, 0.5, 0.999, 1.0]
        for value in test_values:
            posterized = shader._posterize_intensity(value)
            assert 0.0 <= posterized <= 1.0

    def test_cel_shading_2_bands_simple_case(self):
        """2 bands should create simple light/dark separation."""
        shader = ASCIIShader(cel_shading=True, cel_bands=2)

        # Expected: Band 0 (dark) = 0.25, Band 1 (light) = 0.75

        # Low intensity → dark band
        dark = shader._posterize_intensity(0.2)
        assert abs(dark - 0.25) < 1e-6

        # High intensity → light band
        light = shader._posterize_intensity(0.8)
        assert abs(light - 0.75) < 1e-6


class TestCelShadingIntegration:
    """Integration tests for cel-shading with full rendering."""

    def test_cel_shading_with_character_rendering(self):
        """Cel-shading should work with full character rendering."""
        from src.model import CharacterHead
        from src.renderer import Camera, Raymarcher
        from src.renderer.quality import QualityLevel

        head = CharacterHead(character_name="default")
        camera = Camera(position=(0, 0, -3.5), target=(0, 0, 0))
        shader = ASCIIShader(cel_shading=True, cel_bands=3)

        raymarcher = Raymarcher(
            width=40,
            height=20,
            camera=camera,
            shader=shader,
            quality=QualityLevel.LOW,
        )

        sdf = head.get_sdf()

        # Should render without errors
        frame = raymarcher.render_frame(sdf)

        assert isinstance(frame, str)
        assert len(frame) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
