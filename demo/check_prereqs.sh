#!/usr/bin/env bash
#
# Check Prerequisites for Liquid ASCII
# =====================================
# Verifies that all required software is installed
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Checking Prerequisites for Liquid ASCII${NC}"
echo "========================================"
echo ""

# Track overall status
ALL_OK=true

# Check Python
echo -n "Checking Python 3.11+... "
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 11 ]; then
        echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION"
    else
        echo -e "${RED}✗${NC} Python $PYTHON_VERSION (need 3.11+)"
        ALL_OK=false
    fi
else
    echo -e "${RED}✗${NC} Not found"
    ALL_OK=false
fi

# Check uv (optional but recommended)
echo -n "Checking uv... "
if command -v uv >/dev/null 2>&1; then
    UV_VERSION=$(uv --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    echo -e "${GREEN}✓${NC} uv $UV_VERSION"
else
    echo -e "${YELLOW}⚠${NC} Not found (recommended for fast installs)"
    echo "  Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

# Check pip
echo -n "Checking pip... "
if python3 -m pip --version >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Available"
else
    echo -e "${RED}✗${NC} Not found"
    ALL_OK=false
fi

# Check terminal capabilities
echo -n "Checking terminal size... "
COLS=$(tput cols 2>/dev/null || echo 0)
LINES=$(tput lines 2>/dev/null || echo 0)
if [ "$COLS" -ge 100 ] && [ "$LINES" -ge 60 ]; then
    echo -e "${GREEN}✓${NC} ${COLS}x${LINES} (good)"
elif [ "$COLS" -ge 80 ] && [ "$LINES" -ge 40 ]; then
    echo -e "${YELLOW}⚠${NC} ${COLS}x${LINES} (minimum met, but 100x60+ recommended)"
else
    echo -e "${RED}✗${NC} ${COLS}x${LINES} (too small, need at least 80x40)"
    ALL_OK=false
fi

# Check ANSI color support
echo -n "Checking ANSI color support... "
if [ -t 1 ]; then
    echo -e "${GREEN}✓${NC} Supported"
else
    echo -e "${YELLOW}⚠${NC} May not support colors"
fi

# Check audio (optional)
echo -n "Checking audio support... "
if command -v aplay >/dev/null 2>&1 || command -v paplay >/dev/null 2>&1 || command -v afplay >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Available"
else
    echo -e "${YELLOW}⚠${NC} No audio player detected (TTS may not work)"
    echo "  Install: sudo apt-get install alsa-utils (Linux) or use macOS/Windows built-in"
fi

# Check network (for TTS)
echo -n "Checking network connectivity... "
if ping -c 1 google.com >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Connected"
else
    echo -e "${YELLOW}⚠${NC} No network (TTS requires internet)"
fi

echo ""
echo "========================================"
if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}✓ All required prerequisites met!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run: ./demo/install.sh"
    echo "  2. Run demos: ./demo/demo_basic.sh"
    exit 0
else
    echo -e "${RED}✗ Some required prerequisites are missing${NC}"
    echo ""
    echo "Please install missing components and try again."
    exit 1
fi
