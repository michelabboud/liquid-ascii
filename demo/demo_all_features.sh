#!/usr/bin/env bash
#
# All Features Demo
# =================
# Shows all features: UTF-8, colors, emojis, edges, rainbow effects
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/.venv"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}Liquid ASCII - All Features Demo${NC}"
echo "================================="
echo ""

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Run ./demo/install.sh first."
    exit 1
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# Run demo
cd "$PROJECT_DIR"

echo -e "${GREEN}Demo 1: Robot with Neon Colors + Emojis + Rainbow${NC}"
echo ""
echo -e "${YELLOW}Features:${NC}"
echo "  • Emoji eyes and mouth (⚫⚪🔴)"
echo "  • Neon color scheme"
echo "  • Horizontal rainbow gradient"
echo "  • Edge detection"
echo "  • 30 FPS animation"
echo ""
sleep 2

python -m src.main --character robot --scheme neon --emojis --rainbow horizontal --duration 10 --fps 30

echo ""
echo "================================="
echo ""
echo -e "${GREEN}Demo 2: Alien with Green Skin + Wave Rainbow${NC}"
echo ""
echo -e "${YELLOW}Features:${NC}"
echo "  • Alien character geometry"
echo "  • Green color scheme"
echo "  • Wave rainbow effect"
echo "  • UTF-8 unicode characters"
echo "  • Edge detection"
echo ""
sleep 2

python -m src.main --character alien --scheme green --rainbow wave --duration 10 --fps 30

echo ""
echo "================================="
echo ""
echo -e "${GREEN}Demo 3: Baby with Radial Rainbow${NC}"
echo ""
echo -e "${YELLOW}Features:${NC}"
echo "  • Baby character (round proportions)"
echo "  • Radial rainbow gradient"
echo "  • All default features enabled"
echo ""
sleep 2

python -m src.main --character baby --rainbow radial --duration 10 --fps 30

echo ""
echo "================================="
echo "All features demo complete!"
echo ""
echo -e "${MAGENTA}Features Demonstrated:${NC}"
echo "  ✓ UTF-8 unicode characters"
echo "  ✓ 24-bit RGB colors"
echo "  ✓ Emoji facial features"
echo "  ✓ Edge detection"
echo "  ✓ Rainbow effects (horizontal, wave, radial)"
echo "  ✓ Multiple character types"
echo "  ✓ Color schemes"
echo "  ✓ 30 FPS smooth animation"
