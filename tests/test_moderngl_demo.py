"""
Tests for ModernGL desktop renderer demo.
"""

import pytest
from pathlib import Path

# Check if ModernGL is available
try:
    import moderngl
    import moderngl_window
    MODERNGL_AVAILABLE = True
except ImportError:
    MODERNGL_AVAILABLE = False


@pytest.mark.skipif(not MODERNGL_AVAILABLE, reason="ModernGL not installed")
def test_moderngl_demo_exists():
    """Test that ModernGL demo script exists."""
    demo_path = Path(__file__).parent.parent / "demo" / "demo_moderngl.py"
    assert demo_path.exists()
    assert demo_path.is_file()


@pytest.mark.skipif(not MODERNGL_AVAILABLE, reason="ModernGL not installed")
def test_moderngl_import():
    """Test that ModernGL can be imported."""
    assert moderngl is not None
    assert moderngl_window is not None


@pytest.mark.skipif(not MODERNGL_AVAILABLE, reason="ModernGL not installed")
def test_webgl_shaders_exist():
    """Test that WebGL shaders exist for ModernGL to use."""
    webgl_dir = Path(__file__).parent.parent / "webgl" / "shaders"

    vertex_shader = webgl_dir / "vertex.glsl"
    fragment_shader = webgl_dir / "fragment.glsl"

    assert vertex_shader.exists(), "vertex.glsl not found"
    assert fragment_shader.exists(), "fragment.glsl not found"

    # Check shaders have content
    with open(vertex_shader) as f:
        content = f.read()
        assert len(content) > 0
        assert "#version 300 es" in content

    with open(fragment_shader) as f:
        content = f.read()
        assert len(content) > 0
        assert "#version 300 es" in content
        assert "scene_sdf" in content
        assert "raymarch" in content
