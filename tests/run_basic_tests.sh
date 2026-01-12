#!/usr/bin/env bash
#
# Basic tests for Phase 2B, 2C, and 3
# Runs without pytest - just validates files and structure
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "======================================"
echo "Basic Tests for Phases 2B, 2C, 3"
echo "======================================"
echo

PASS=0
FAIL=0

pass() {
    echo "✓ $1"
    ((PASS++))
}

fail() {
    echo "✗ $1"
    ((FAIL++))
}

# ===== Phase 2B: PyOpenCL Tests =====
echo "Phase 2B: PyOpenCL GPU Renderer"
echo "--------------------------------"

# Check OpenCL files exist
if [ -f "$PROJECT_DIR/src/renderer/opencl/__init__.py" ]; then
    pass "opencl/__init__.py exists"
else
    fail "opencl/__init__.py missing"
fi

if [ -f "$PROJECT_DIR/src/renderer/opencl/cl_renderer.py" ]; then
    pass "cl_renderer.py exists"
else
    fail "cl_renderer.py missing"
fi

if [ -f "$PROJECT_DIR/src/renderer/opencl/raymarching.cl" ]; then
    pass "raymarching.cl exists"
else
    fail "raymarching.cl missing"
fi

if [ -f "$PROJECT_DIR/tests/test_opencl_renderer.py" ]; then
    pass "test_opencl_renderer.py exists"
else
    fail "test_opencl_renderer.py missing"
fi

# Check OpenCL kernel has required functions
if grep -q "scene_sdf" "$PROJECT_DIR/src/renderer/opencl/raymarching.cl"; then
    pass "OpenCL kernel has scene_sdf"
else
    fail "OpenCL kernel missing scene_sdf"
fi

if grep -q "raymarch" "$PROJECT_DIR/src/renderer/opencl/raymarching.cl"; then
    pass "OpenCL kernel has raymarch"
else
    fail "OpenCL kernel missing raymarch"
fi

if grep -q "compute_normal" "$PROJECT_DIR/src/renderer/opencl/raymarching.cl"; then
    pass "OpenCL kernel has compute_normal"
else
    fail "OpenCL kernel missing compute_normal"
fi

# Check Python integration
if grep -q "class OpenCLRenderer" "$PROJECT_DIR/src/renderer/opencl/cl_renderer.py"; then
    pass "OpenCLRenderer class defined"
else
    fail "OpenCLRenderer class missing"
fi

# Check CLI integration
if grep -q "\-\-opencl" "$PROJECT_DIR/src/main.py"; then
    pass "CLI has --opencl flag"
else
    fail "CLI missing --opencl flag"
fi

echo

# ===== Phase 2C: ModernGL Tests =====
echo "Phase 2C: ModernGL Desktop Renderer"
echo "------------------------------------"

# Check ModernGL files exist
if [ -f "$PROJECT_DIR/demo/demo_moderngl.py" ]; then
    pass "demo_moderngl.py exists"
else
    fail "demo_moderngl.py missing"
fi

if [ -x "$PROJECT_DIR/demo/demo_moderngl.py" ]; then
    pass "demo_moderngl.py is executable"
else
    fail "demo_moderngl.py not executable"
fi

if [ -f "$PROJECT_DIR/tests/test_moderngl_demo.py" ]; then
    pass "test_moderngl_demo.py exists"
else
    fail "test_moderngl_demo.py missing"
fi

# Check ModernGL demo structure
if grep -q "class LiquidASCIIWindow" "$PROJECT_DIR/demo/demo_moderngl.py"; then
    pass "LiquidASCIIWindow class defined"
else
    fail "LiquidASCIIWindow class missing"
fi

if grep -q "moderngl" "$PROJECT_DIR/demo/demo_moderngl.py"; then
    pass "ModernGL import present"
else
    fail "ModernGL import missing"
fi

# Check shader reuse
if grep -q "webgl.*shader" "$PROJECT_DIR/demo/demo_moderngl.py"; then
    pass "ModernGL reuses WebGL shaders"
else
    fail "ModernGL not reusing WebGL shaders"
fi

echo

# ===== Phase 3: Animation System Tests =====
echo "Phase 3: WebGL Animation System"
echo "--------------------------------"

# Check animation files exist
if [ -f "$PROJECT_DIR/webgl/js/animations.js" ]; then
    pass "animations.js exists"
else
    fail "animations.js missing"
fi

if [ -f "$PROJECT_DIR/tests/test_webgl_animations.py" ]; then
    pass "test_webgl_animations.py exists"
else
    fail "test_webgl_animations.py missing"
fi

# Check animation system components
if grep -q "export class AnimationController" "$PROJECT_DIR/webgl/js/animations.js"; then
    pass "AnimationController class exported"
else
    fail "AnimationController class missing"
fi

if grep -q "getBreathingOffset" "$PROJECT_DIR/webgl/js/animations.js"; then
    pass "Breathing animation implemented"
else
    fail "Breathing animation missing"
fi

if grep -q "getBlinkAmount" "$PROJECT_DIR/webgl/js/animations.js"; then
    pass "Blinking animation implemented"
else
    fail "Blinking animation missing"
fi

if grep -q "export const Easing" "$PROJECT_DIR/webgl/js/animations.js"; then
    pass "Easing functions exported"
else
    fail "Easing functions missing"
fi

if grep -q "AnimationPresets" "$PROJECT_DIR/webgl/js/animations.js"; then
    pass "Animation presets defined"
else
    fail "Animation presets missing"
fi

# Check main.js integration
if grep -q "from './animations.js'" "$PROJECT_DIR/webgl/js/main.js"; then
    pass "Animations imported in main.js"
else
    fail "Animations not imported in main.js"
fi

if grep -q "animationController.update" "$PROJECT_DIR/webgl/js/main.js"; then
    pass "Animation controller updated in render loop"
else
    fail "Animation controller not updated"
fi

# Check HTML UI
if grep -q 'id="idleAnimations"' "$PROJECT_DIR/webgl/index.html"; then
    pass "Idle animations toggle in HTML"
else
    fail "Idle animations toggle missing from HTML"
fi

echo
echo "======================================"
echo "Test Summary"
echo "======================================"
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo

if [ $FAIL -eq 0 ]; then
    echo "✓ All basic tests passed!"
    exit 0
else
    echo "✗ Some tests failed"
    exit 1
fi
