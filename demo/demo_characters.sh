#!/usr/bin/env bash
#
# Characters Demo
# ===============
# Shows all available character types
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

echo -e "${BLUE}Liquid ASCII - Characters Gallery${NC}"
echo "=================================="
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

# Array of characters to demo
CHARACTERS=("default" "baby" "tall" "wide" "alien" "robot")

for char in "${CHARACTERS[@]}"; do
    echo -e "${GREEN}Character: ${char}${NC}"
    echo ""

    case $char in
        default)
            echo "Standard proportions, balanced features"
            ;;
        baby)
            echo "Round face, large eyes, small features"
            ;;
        tall)
            echo "Elongated vertical proportions"
            ;;
        wide)
            echo "Wider horizontal proportions"
            ;;
        alien)
            echo "Large almond eyes, small mouth"
            ;;
        robot)
            echo "Mechanical, angular features"
            ;;
    esac

    echo ""
    sleep 1

    # Show animated version
    python -m src.main --character "$char" --duration 5 --fps 30

    echo ""
    echo "----------------------------------"
    echo ""
    sleep 1
done

echo "=================================="
echo "Characters gallery complete!"
echo ""
echo "All available characters:"
echo "  • default - Standard proportions"
echo "  • baby    - Round, cute features"
echo "  • tall    - Elongated vertical"
echo "  • wide    - Wider horizontal"
echo "  • alien   - Large eyes, otherworldly"
echo "  • robot   - Mechanical, angular"
