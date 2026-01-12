#!/usr/bin/env bash
#
# Launch script for WebGL GPU renderer
# Starts a local HTTP server and provides testing information
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-8000}"

echo "======================================"
echo "Liquid ASCII - WebGL GPU Renderer"
echo "======================================"
echo

# Check if port is available
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port $PORT is already in use"
    echo "   Trying to stop existing server..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Verify files exist
echo "✓ Checking files..."
REQUIRED_FILES=(
    "index.html"
    "js/main.js"
    "js/shader-loader.js"
    "js/characters.js"
    "shaders/vertex.glsl"
    "shaders/fragment.glsl"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$SCRIPT_DIR/$file" ]; then
        echo "❌ Missing file: $file"
        exit 1
    fi
done

echo "✓ All required files present"

# Check JavaScript syntax if node is available
if command -v node &> /dev/null; then
    echo "✓ Checking JavaScript syntax..."
    node --check "$SCRIPT_DIR/js/main.js" || exit 1
    node --check "$SCRIPT_DIR/js/shader-loader.js" || exit 1
    node --check "$SCRIPT_DIR/js/characters.js" || exit 1
    echo "✓ JavaScript syntax valid"
fi

echo
echo "Starting HTTP server on port $PORT..."
echo

# Start server from webgl directory
(python3 -m http.server $PORT 2>&1 | sed 's/^/  [server] /') &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Check if server is running
if ! ps -p $SERVER_PID > /dev/null; then
    echo "❌ Failed to start server"
    exit 1
fi

echo "✓ Server started (PID: $SERVER_PID)"
echo

# Get local IP for LAN access
LOCAL_IP=$(hostname -I | awk '{print $1}' || echo "localhost")

echo "======================================"
echo "🚀 WebGL Renderer is Ready!"
echo "======================================"
echo
echo "Open in your browser:"
echo "  • Local:    http://localhost:$PORT/"
echo "  • LAN:      http://$LOCAL_IP:$PORT/"
echo
echo "Quick Tests:"
echo "  • All characters:  http://localhost:$PORT/#characters"
echo "  • Lighting demo:   http://localhost:$PORT/#lighting"
echo "  • Cel-shading:     http://localhost:$PORT/#cel"
echo
echo "Features to Test:"
echo "  ✓ Switch characters (dropdown)"
echo "  ✓ Adjust camera (distance, FOV)"
echo "  ✓ Change lighting (8 presets)"
echo "  ✓ Enable cel-shading (2-8 bands)"
echo "  ✓ Auto-rotation toggle"
echo "  ✓ Check FPS counter (target: 60+)"
echo
echo "Press Ctrl+C to stop the server"
echo "======================================"
echo

# Handle shutdown
trap "echo; echo 'Stopping server...'; kill $SERVER_PID 2>/dev/null; exit 0" INT TERM

# Keep script running
wait $SERVER_PID
