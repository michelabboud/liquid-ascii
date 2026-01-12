#!/usr/bin/env bash
#
# Automated test script for WebGL renderer
# Validates files, syntax, and HTTP serving
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=8123  # Use different port for testing

echo "======================================"
echo "WebGL Renderer - Automated Tests"
echo "======================================"
echo

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() {
    echo -e "${GREEN}✓${NC} $1"
}

fail() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

warn() {
    echo -e "${YELLOW}!${NC} $1"
}

# Test 1: File Structure
echo "Test 1: Checking file structure..."
REQUIRED_FILES=(
    "index.html"
    "README.md"
    "js/main.js"
    "js/shader-loader.js"
    "js/characters.js"
    "shaders/vertex.glsl"
    "shaders/fragment.glsl"
    "shaders/sdf.glsl"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        pass "Found: $file"
    else
        fail "Missing: $file"
    fi
done
echo

# Test 2: HTML Structure
echo "Test 2: Validating HTML..."
if grep -q 'type="module"' "$SCRIPT_DIR/index.html"; then
    pass "HTML uses ES6 modules"
else
    fail "HTML missing ES6 module declaration"
fi

if grep -q 'canvas.*glCanvas' "$SCRIPT_DIR/index.html"; then
    pass "Canvas element present"
else
    fail "Canvas element missing"
fi
echo

# Test 3: JavaScript Syntax
echo "Test 3: Checking JavaScript syntax..."
if command -v node &> /dev/null; then
    for jsfile in "$SCRIPT_DIR"/js/*.js; do
        if node --check "$jsfile" 2>/dev/null; then
            pass "Valid syntax: $(basename $jsfile)"
        else
            fail "Syntax error in: $(basename $jsfile)"
        fi
    done
else
    warn "Node.js not available, skipping syntax checks"
fi
echo

# Test 4: Module Dependencies
echo "Test 4: Checking module dependencies..."
if grep -q "import.*from.*shader-loader" "$SCRIPT_DIR/js/main.js"; then
    pass "main.js imports shader-loader"
else
    fail "main.js missing shader-loader import"
fi

if grep -q "import.*from.*characters" "$SCRIPT_DIR/js/main.js"; then
    pass "main.js imports characters"
else
    fail "main.js missing characters import"
fi

if grep -q "export" "$SCRIPT_DIR/js/shader-loader.js"; then
    pass "shader-loader.js exports functions"
else
    fail "shader-loader.js missing exports"
fi

if grep -q "export" "$SCRIPT_DIR/js/characters.js"; then
    pass "characters.js exports data"
else
    fail "characters.js missing exports"
fi
echo

# Test 5: GLSL Shaders
echo "Test 5: Validating GLSL shaders..."

# Check vertex shader
if grep -q "#version 300 es" "$SCRIPT_DIR/shaders/vertex.glsl"; then
    pass "Vertex shader has GLSL ES 3.0 version"
else
    fail "Vertex shader missing version declaration"
fi

if grep -q "void main()" "$SCRIPT_DIR/shaders/vertex.glsl"; then
    pass "Vertex shader has main function"
else
    fail "Vertex shader missing main function"
fi

# Check fragment shader
if grep -q "#version 300 es" "$SCRIPT_DIR/shaders/fragment.glsl"; then
    pass "Fragment shader has GLSL ES 3.0 version"
else
    fail "Fragment shader missing version declaration"
fi

if grep -q "scene_sdf" "$SCRIPT_DIR/shaders/fragment.glsl"; then
    pass "Fragment shader has scene_sdf function"
else
    fail "Fragment shader missing scene_sdf function"
fi

if grep -q "raymarch" "$SCRIPT_DIR/shaders/fragment.glsl"; then
    pass "Fragment shader has raymarch function"
else
    fail "Fragment shader missing raymarch function"
fi
echo

# Test 6: Character Presets
echo "Test 6: Validating character presets..."
CHARACTERS=("default" "robot" "alien" "baby" "cyclops" "monster" "fish" "square")
for char in "${CHARACTERS[@]}"; do
    if grep -q "\"$char\":" "$SCRIPT_DIR/js/characters.js"; then
        pass "Character preset: $char"
    else
        warn "Character preset missing: $char"
    fi
done
echo

# Test 7: Lighting Presets
echo "Test 7: Validating lighting presets..."
LIGHTS=("default" "dramatic" "soft" "metallic" "noir" "cartoon")
for light in "${LIGHTS[@]}"; do
    if grep -q "$light:" "$SCRIPT_DIR/js/main.js"; then
        pass "Lighting preset: $light"
    else
        warn "Lighting preset missing: $light"
    fi
done
echo

# Test 8: HTTP Server Test
echo "Test 8: Testing HTTP server..."

# Kill any existing test server
lsof -ti:$PORT 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 1

# Start server
python3 -m http.server $PORT > /tmp/webgl_test_server.log 2>&1 &
SERVER_PID=$!
sleep 2

# Check if server is running
if ps -p $SERVER_PID > /dev/null; then
    pass "HTTP server started (PID: $SERVER_PID)"
else
    fail "Failed to start HTTP server"
fi

# Test file accessibility
if curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/index.html | grep -q "200"; then
    pass "index.html accessible via HTTP"
else
    fail "index.html not accessible (check server working directory)"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/js/main.js | grep -q "200"; then
    pass "main.js accessible via HTTP"
else
    fail "main.js not accessible"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/shaders/fragment.glsl | grep -q "200"; then
    pass "Shaders accessible via HTTP"
else
    fail "Shaders not accessible"
fi

# Stop test server
kill $SERVER_PID 2>/dev/null || true
sleep 1
pass "HTTP server stopped"
echo

# Test 9: Content Validation
echo "Test 9: Validating content..."

# Check if main.js initializes WebGL
if grep -q "WebGL2RenderingContext" "$SCRIPT_DIR/js/main.js" || grep -q "getContext.*webgl2" "$SCRIPT_DIR/js/main.js"; then
    pass "main.js initializes WebGL 2.0"
else
    fail "main.js missing WebGL 2.0 initialization"
fi

# Check if render loop exists
if grep -q "requestAnimationFrame" "$SCRIPT_DIR/js/main.js"; then
    pass "Render loop implemented"
else
    fail "Render loop missing"
fi

# Check if uniforms are set
if grep -q "uniform" "$SCRIPT_DIR/js/main.js"; then
    pass "Uniform management present"
else
    fail "Uniform management missing"
fi
echo

# Summary
echo "======================================"
echo -e "${GREEN}All tests passed!${NC}"
echo "======================================"
echo
echo "WebGL renderer is ready for use."
echo "Run './run.sh' to start the server and open in browser."
echo
