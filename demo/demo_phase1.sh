#!/bin/bash

# Phase 1 Features Demo Script
# Demonstrates all character differentiation features

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "Phase 1 Features Demo"
echo "Character Differentiation"
echo "========================================"
echo ""

# Check if running
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

cd "$PROJECT_ROOT"

echo "This demo showcases Phase 1 features:"
echo "  ✓ Wireframe/edge rendering"
echo "  ✓ Dramatic lighting presets"
echo "  ✓ Cel-shading/toon style"
echo "  ✓ Extreme character variations"
echo ""
echo "Press Enter to continue..."
read

# === Wireframe Demo ===
echo ""
echo "1. WIREFRAME RENDERING"
echo "------------------------"
echo "Showing characters in wireframe mode for clear silhouettes"
sleep 2

for char in "robot" "alien" "cyclops"; do
    echo ""
    echo "Character: $char (wireframe)"
    python3 -m src.main --character "$char" --wireframe --duration 3 || true
done

# === Lighting Presets Demo ===
echo ""
echo "2. LIGHTING PRESETS"
echo "-------------------"
echo "8 different lighting styles"
sleep 2

echo ""
echo "To see all lighting presets:"
python3 -m src.main --list-lighting

echo ""
echo "Press Enter to demo lighting presets..."
read

for preset in "dramatic" "metallic" "noir"; do
    echo ""
    echo "Lighting: $preset"
    python3 -m src.main --lighting "$preset" --duration 3 || true
done

# === Cel-Shading Demo ===
echo ""
echo "3. CEL-SHADING"
echo "--------------"
echo "Comic book / anime style posterized lighting"
sleep 2

echo ""
echo "2 bands (stark contrast):"
python3 -m src.main --cel-shading --cel-bands 2 --duration 3 || true

echo ""
echo "3 bands (classic cel-shading):"
python3 -m src.main --cel-shading --cel-bands 3 --duration 3 || true

# === Character Variations Demo ===
echo ""
echo "4. CHARACTER VARIATIONS"
echo "-----------------------"
echo "Extreme geometry for instant recognition"
sleep 2

for char in "robot" "alien" "baby" "cyclops" "monster"; do
    echo ""
    echo "Character: $char"
    python3 -m src.main --character "$char" --lighting dramatic --duration 2 || true
done

# === Combinations ===
echo ""
echo "5. FEATURE COMBINATIONS"
echo "-----------------------"
echo "Mixing wireframe, lighting, and cel-shading"
sleep 2

echo ""
echo "Robot + Wireframe:"
python3 -m src.main --character robot --wireframe --duration 2 || true

echo ""
echo "Alien + Dramatic + Cel-shading:"
python3 -m src.main --character alien --lighting dramatic --cel-shading --cel-bands 3 --duration 2 || true

echo ""
echo "Baby + Soft + Cel-shading:"
python3 -m src.main --character baby --lighting soft --cel-shading --cel-bands 2 --duration 2 || true

echo ""
echo "========================================"
echo "Phase 1 Demo Complete!"
echo "========================================"
echo ""
echo "Characters are now instantly recognizable!"
echo "Next: Phase 2 - GPU Acceleration"
echo ""
