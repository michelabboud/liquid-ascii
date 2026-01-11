#!/usr/bin/env bash
#
# Expressions Demo
# ================
# Shows all available facial expressions
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

echo -e "${BLUE}Liquid ASCII - Expressions Gallery${NC}"
echo "==================================="
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

# Array of expressions to demo
EXPRESSIONS=("neutral" "happy" "sad" "angry" "surprised" "thinking")

for expr in "${EXPRESSIONS[@]}"; do
    echo -e "${GREEN}Expression: ${expr}${NC}"
    echo ""

    case $expr in
        neutral)
            echo "Calm, relaxed face"
            ;;
        happy)
            echo "Wide smile, bright eyes"
            ;;
        sad)
            echo "Downturned mouth, droopy eyes"
            ;;
        angry)
            echo "Furrowed brow, tight lips"
            ;;
        surprised)
            echo "Wide eyes, open mouth"
            ;;
        thinking)
            echo "Eyes looking up, slight smile"
            ;;
    esac

    echo ""
    sleep 1

    # Show static expression
    python -m src.main --static --expression "$expr"

    echo ""
    echo "-----------------------------------"
    echo ""
    sleep 1
done

echo "==================================="
echo "Expressions gallery complete!"
echo ""
echo "All available expressions:"
echo "  • neutral    - Calm, relaxed"
echo "  • happy      - Smiling, joyful"
echo "  • sad        - Downturned, melancholy"
echo "  • angry      - Furrowed, intense"
echo "  • surprised  - Wide-eyed, amazed"
echo "  • thinking   - Contemplative"
