#!/usr/bin/env bash
#
# Basic Static Demo
# =================
# Shows a single static frame with default settings
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/.venv"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${BLUE}Liquid ASCII - Basic Static Demo${NC}"
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

echo -e "${GREEN}Rendering static frame with default character...${NC}"
echo ""

python -m src.main --static

echo ""
echo "================================="
echo "Demo complete!"
echo ""
echo "Try other demos:"
echo "  ./demo/demo_animated.sh       - Animated demo"
echo "  ./demo/demo_characters.sh     - Different characters"
echo "  ./demo/demo_all_features.sh   - All features"
