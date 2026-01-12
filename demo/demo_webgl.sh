#!/usr/bin/env bash
#
# WebGL Demo Script
# Quick demonstration of GPU-accelerated rendering
#

set -e

WEBGL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../webgl" && pwd)"

echo "======================================"
echo "Liquid ASCII - WebGL GPU Demo"
echo "======================================"
echo
echo "This demo launches the GPU-accelerated"
echo "WebGL version in your browser."
echo
echo "Performance: 60+ FPS (vs 2-5 FPS terminal)"
echo "Platform: Any GPU (AMD/Intel/NVIDIA)"
echo
echo "======================================"
echo

# Check if webgl directory exists
if [ ! -d "$WEBGL_DIR" ]; then
    echo "❌ WebGL directory not found: $WEBGL_DIR"
    exit 1
fi

# Check required files
if [ ! -f "$WEBGL_DIR/index.html" ]; then
    echo "❌ index.html not found"
    exit 1
fi

if [ ! -f "$WEBGL_DIR/run.sh" ]; then
    echo "❌ run.sh not found"
    exit 1
fi

echo "✓ WebGL files found"
echo

# Check if browser is available
if command -v xdg-open &> /dev/null; then
    OPEN_CMD="xdg-open"
elif command -v open &> /dev/null; then
    OPEN_CMD="open"
elif command -v start &> /dev/null; then
    OPEN_CMD="start"
else
    OPEN_CMD=""
fi

# Start server
echo "Starting HTTP server..."
(cd "$WEBGL_DIR" && "$WEBGL_DIR/run.sh") &
SERVER_PID=$!

# Wait for server
sleep 3

# Open browser if possible
if [ -n "$OPEN_CMD" ]; then
    echo
    echo "Opening browser..."
    $OPEN_CMD "http://localhost:8000" &
    sleep 2
fi

echo
echo "======================================"
echo "WebGL Renderer Running!"
echo "======================================"
echo
echo "If browser didn't open automatically,"
echo "visit: http://localhost:8000"
echo
echo "Features to Try:"
echo "  • Switch characters (robot, alien, cyclops)"
echo "  • Adjust camera distance and FOV"
echo "  • Change lighting (dramatic, metallic, noir)"
echo "  • Enable cel-shading (2-8 bands)"
echo "  • Toggle auto-rotation"
echo "  • Monitor FPS counter (target: 60+)"
echo
echo "Press Ctrl+C to stop"
echo "======================================"

# Wait for interrupt
trap "echo; echo 'Stopping server...'; kill $SERVER_PID 2>/dev/null; exit 0" INT TERM
wait $SERVER_PID
