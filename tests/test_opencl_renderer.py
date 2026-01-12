"""
Tests for PyOpenCL GPU renderer.
"""

import pytest

# Check if PyOpenCL is available
try:
    import pyopencl as cl
    OPENCL_AVAILABLE = True
except ImportError:
    OPENCL_AVAILABLE = False


@pytest.mark.skipif(not OPENCL_AVAILABLE, reason="PyOpenCL not installed")
def test_opencl_import():
    """Test that OpenCL renderer module can be imported."""
    from src.renderer.opencl.cl_renderer import OpenCLRenderer
    assert OpenCLRenderer is not None


@pytest.mark.skipif(not OPENCL_AVAILABLE, reason="PyOpenCL not installed")
def test_list_opencl_devices():
    """Test listing OpenCL devices."""
    from src.renderer.opencl.cl_renderer import list_opencl_devices

    devices = list_opencl_devices()
    # Should return a list (may be empty if no devices)
    assert isinstance(devices, list)

    # If devices exist, check format
    if devices:
        platform_idx, device_idx, platform_name, device_name, dev_type = devices[0]
        assert isinstance(platform_idx, int)
        assert isinstance(device_idx, int)
        assert isinstance(platform_name, str)
        assert isinstance(device_name, str)
        assert isinstance(dev_type, str)


@pytest.mark.skipif(not OPENCL_AVAILABLE, reason="PyOpenCL not installed")
def test_get_best_opencl_device():
    """Test getting best OpenCL device."""
    from src.renderer.opencl.cl_renderer import get_best_opencl_device

    result = get_best_opencl_device()
    # May be None if no devices, or tuple of (platform_idx, device_idx)
    if result is not None:
        platform_idx, device_idx = result
        assert isinstance(platform_idx, int)
        assert isinstance(device_idx, int)


@pytest.mark.skipif(not OPENCL_AVAILABLE, reason="PyOpenCL not installed")
def test_opencl_renderer_creation():
    """Test OpenCL renderer can be created."""
    from src.renderer.opencl.cl_renderer import OpenCLRenderer, get_best_opencl_device
    from src.renderer import Camera, ASCIIShader

    device = get_best_opencl_device()
    if device is None:
        pytest.skip("No OpenCL devices available")

    platform_idx, device_idx = device

    camera = Camera()
    shader = ASCIIShader()

    renderer = OpenCLRenderer(
        width=40,
        height=20,
        camera=camera,
        shader=shader,
        platform_index=platform_idx,
        device_index=device_idx,
    )

    assert renderer.width == 40
    assert renderer.height == 20
    assert renderer.camera is not None
    assert renderer.shader is not None


@pytest.mark.skipif(not OPENCL_AVAILABLE, reason="PyOpenCL not installed")
def test_opencl_render_frame():
    """Test rendering a frame with OpenCL."""
    from src.renderer.opencl.cl_renderer import OpenCLRenderer, get_best_opencl_device
    from src.renderer import Camera, ASCIIShader
    from src.model import CharacterHead

    device = get_best_opencl_device()
    if device is None:
        pytest.skip("No OpenCL devices available")

    platform_idx, device_idx = device

    camera = Camera()
    shader = ASCIIShader()
    head = CharacterHead(character_name="default")

    renderer = OpenCLRenderer(
        width=40,
        height=20,
        camera=camera,
        shader=shader,
        platform_index=platform_idx,
        device_index=device_idx,
    )

    # Render a frame
    frame = renderer.render_frame(head)

    # Check output
    assert isinstance(frame, str)
    assert len(frame) > 0

    # Check dimensions (40 chars * 20 lines + 19 newlines)
    lines = frame.split('\n')
    assert len(lines) == 20
    assert all(len(line) == 40 for line in lines)


@pytest.mark.skipif(not OPENCL_AVAILABLE, reason="PyOpenCL not installed")
def test_opencl_cleanup():
    """Test OpenCL renderer cleanup."""
    from src.renderer.opencl.cl_renderer import OpenCLRenderer, get_best_opencl_device
    from src.renderer import Camera, ASCIIShader

    device = get_best_opencl_device()
    if device is None:
        pytest.skip("No OpenCL devices available")

    platform_idx, device_idx = device

    camera = Camera()
    shader = ASCIIShader()

    renderer = OpenCLRenderer(
        width=20,
        height=10,
        camera=camera,
        shader=shader,
        platform_index=platform_idx,
        device_index=device_idx,
    )

    # Cleanup should not raise errors
    renderer.cleanup()
