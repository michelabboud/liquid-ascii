#!/usr/bin/env bash
#
# Animated Demo
# =============
# Shows 15 seconds of animated head with idle motion
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/.venv"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Liquid ASCII - Animated Demo${NC}"
echo "============================="
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

echo -e "${GREEN}Starting animated demo (15 seconds at 30 FPS)${NC}"
echo ""
echo -e "${YELLOW}Features:${NC}"
echo "  • UTF-8 unicode characters (default ON)"
echo "  • Edge detection for crisp outlines (default ON)"
echo "  • 24-bit RGB colors"
echo "  • Organic idle animation (breathing, blinking)"
echo "  • 100x60 resolution"
echo ""
echo "Press Ctrl+C to stop early"
echo ""
sleep 2

python -m src.main --character baby --duration 15 --fps 30

echo ""
echo "============================="
echo "Demo complete!"
echo ""
echo "Try other demos:"
echo "  ./demo/demo_characters.sh     - Different characters"
echo "  ./demo/demo_all_features.sh   - All features + effects"
