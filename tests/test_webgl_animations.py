"""
Tests for WebGL animation system.
"""

import pytest
from pathlib import Path


def test_animations_js_exists():
    """Test that animations.js file exists."""
    animations_path = Path(__file__).parent.parent / "webgl" / "js" / "animations.js"
    assert animations_path.exists()
    assert animations_path.is_file()


def test_animations_js_exports():
    """Test that animations.js contains expected exports."""
    animations_path = Path(__file__).parent.parent / "webgl" / "js" / "animations.js"

    with open(animations_path) as f:
        content = f.read()

    # Check for main exports
    assert "export class AnimationController" in content
    assert "export const Easing" in content
    assert "export class OrganicNoise" in content
    assert "export const AnimationPresets" in content


def test_animation_controller_methods():
    """Test that AnimationController has required methods."""
    animations_path = Path(__file__).parent.parent / "webgl" / "js" / "animations.js"

    with open(animations_path) as f:
        content = f.read()

    # Check for essential methods
    assert "update(deltaTime)" in content
    assert "getBreathingOffset()" in content
    assert "getBlinkAmount()" in content
    assert "getHeadTilt()" in content
    assert "getMouthIdleMovement()" in content
    assert "setEnabled(enabled)" in content
    assert "reset()" in content
    assert "triggerBlink()" in content


def test_animation_presets():
    """Test that animation presets are defined."""
    animations_path = Path(__file__).parent.parent / "webgl" / "js" / "animations.js"

    with open(animations_path) as f:
        content = f.read()

    # Check for presets
    assert "default:" in content
    assert "energetic:" in content
    assert "calm:" in content
    assert "sleeping:" in content
    assert "none:" in content


def test_easing_functions():
    """Test that easing functions are defined."""
    animations_path = Path(__file__).parent.parent / "webgl" / "js" / "animations.js"

    with open(animations_path) as f:
        content = f.read()

    # Check for easing functions
    assert "linear:" in content
    assert "easeIn:" in content
    assert "easeOut:" in content
    assert "easeInOut:" in content
    assert "smoothStep:" in content
    assert "smootherStep:" in content


def test_main_js_imports_animations():
    """Test that main.js imports animation system."""
    main_path = Path(__file__).parent.parent / "webgl" / "js" / "main.js"

    with open(main_path) as f:
        content = f.read()

    # Check for animation import
    assert "from './animations.js'" in content
    assert "AnimationController" in content
    assert "AnimationPresets" in content


def test_html_has_animation_controls():
    """Test that index.html has animation control elements."""
    html_path = Path(__file__).parent.parent / "webgl" / "index.html"

    with open(html_path) as f:
        content = f.read()

    # Check for idle animations checkbox
    assert 'id="idleAnimations"' in content
    assert "Idle Animations" in content or "idle animations" in content.lower()


def test_main_js_integrates_animations():
    """Test that main.js integrates animation system."""
    main_path = Path(__file__).parent.parent / "webgl" / "js" / "main.js"

    with open(main_path) as f:
        content = f.read()

    # Check for animation controller usage
    assert "this.animationController = new AnimationController()" in content
    assert "this.animationsEnabled" in content
    assert "animationController.update" in content
    assert "getBreathingOffset()" in content
    assert "getMouthIdleMovement()" in content
