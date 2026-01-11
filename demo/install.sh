#!/usr/bin/env bash
#
# Install Dependencies for Liquid ASCII
# ======================================
# Sets up virtual environment and installs all dependencies
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/.venv"

echo -e "${BLUE}Installing Liquid ASCII Dependencies${NC}"
echo "====================================="
echo ""

# Check prerequisites first
if [ -f "$SCRIPT_DIR/check_prereqs.sh" ]; then
    echo "Running prerequisite checks..."
    bash "$SCRIPT_DIR/check_prereqs.sh" || {
        echo ""
        echo -e "${RED}Prerequisites not met. Please fix issues above and try again.${NC}"
        exit 1
    }
    echo ""
fi

cd "$PROJECT_DIR"

# Check if uv is available
if command -v uv >/dev/null 2>&1; then
    echo -e "${GREEN}Using uv for fast installation${NC}"
    USE_UV=true
else
    echo -e "${YELLOW}Using pip for installation (uv not found)${NC}"
    USE_UV=false
fi

# Create or use existing virtual environment
echo ""
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at: $VENV_DIR"
    echo "Using existing environment..."
else
    echo "Creating virtual environment..."
    if [ "$USE_UV" = true ]; then
        uv venv "$VENV_DIR"
    else
        python3 -m venv "$VENV_DIR"
    fi
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    echo -e "${GREEN}✓${NC} Virtual environment activated"
else
    echo -e "${RED}✗${NC} Failed to activate virtual environment"
    echo "Activation script not found: $VENV_DIR/bin/activate"
    exit 1
fi

# Verify activation
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}✗${NC} Virtual environment activation failed"
    exit 1
fi

# Upgrade pip
echo ""
echo "Upgrading pip..."
python -m pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "Installing dependencies..."
if [ "$USE_UV" = true ]; then
    uv pip install -r "$SCRIPT_DIR/requirements.txt"
    # Install package in editable mode
    if [ -f "$PROJECT_DIR/pyproject.toml" ]; then
        uv pip install -e "$PROJECT_DIR"
    fi
else
    pip install -r "$SCRIPT_DIR/requirements.txt"
    # Install package in editable mode
    if [ -f "$PROJECT_DIR/pyproject.toml" ]; then
        pip install -e "$PROJECT_DIR"
    fi
fi

echo ""
echo -e "${GREEN}✓ Installation complete!${NC}"
echo ""
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Run basic demo: ./demo/demo_basic.sh"
echo "  2. Run animated demo: ./demo/demo_animated.sh"
echo "  3. See all demos: ls ./demo/demo_*.sh"
echo ""
echo "Or activate the environment manually:"
echo "  source .venv/bin/activate"
echo "  python -m src.main --help"
echo ""
