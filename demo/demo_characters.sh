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

# Array of characters to demo (updated with Phase 1 extreme variations)
CHARACTERS=("default" "robot" "alien" "baby" "cyclops" "monster" "fish" "square")

for char in "${CHARACTERS[@]}"; do
    echo -e "${GREEN}Character: ${char}${NC}"
    echo ""

    case $char in
        default)
            echo "Standard proportions, balanced features"
            ;;
        robot)
            echo "Cube-like head, hard mechanical edges, wide-set eyes"
            ;;
        alien)
            echo "2x head height, 3x eye size, very high features"
            ;;
        baby)
            echo "Perfect sphere head, gigantic eyes (kawaii!)"
            ;;
        cyclops)
            echo "ONE GIANT centered eye - instantly recognizable!"
            ;;
        monster)
            echo "Wide squat head with huge gaping mouth"
            ;;
        fish)
            echo "Deep head, eyes on sides, wide O-mouth"
            ;;
        square)
            echo "Angular box head with hard edges"
            ;;
    esac

    echo ""
    sleep 1

    # Show animated version with dramatic lighting for better visibility
    python -m src.main --character "$char" --duration 4 --fps 15 --lighting dramatic

    echo ""
    echo "----------------------------------"
    echo ""
    sleep 1
done

echo "=================================="
echo "Characters gallery complete!"
echo ""
echo "All available characters:"
echo "  • default  - Standard proportions"
echo "  • robot    - Cube-like, mechanical (NEW!)"
echo "  • alien    - 2x height, huge eyes (UPDATED!)"
echo "  • baby     - Perfect sphere, giant eyes (UPDATED!)"
echo "  • cyclops  - ONE GIANT eye (NEW!)"
echo "  • monster  - Wide with huge mouth (NEW!)"
echo "  • fish     - Eyes on sides (NEW!)"
echo "  • square   - Angular box head (NEW!)"
echo "  • round    - Spherical head"
echo "  • tall     - Elongated vertical"
echo "  • wide     - Wider horizontal"
echo "  • cute     - Large eyes, rounded"
echo "  • skull    - Hollow eye sockets"
echo "  • elder    - Thin face, prominent nose"
echo ""
echo "Try them with: python -m src.main --character <name>"
echo "Add --wireframe for pure edge rendering!"
echo "Add --lighting <preset> for different moods!"
echo "Add --cel-shading for comic book style!"
