#!/usr/bin/env bash
#
# Test WSL Audio Setup
# Run this after completing Windows PulseAudio setup

set -e

echo ""
echo "🧪 WSL Audio Setup Test"
echo "======================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Track overall success
ALL_PASSED=true

# Test 1: Check environment variables
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 1: Environment Variables"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -z "$HOST_IP" ]; then
    export HOST_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
fi

if [ -z "$PULSE_SERVER" ]; then
    export PULSE_SERVER=tcp:$HOST_IP
fi

echo "HOST_IP: $HOST_IP"
echo "PULSE_SERVER: $PULSE_SERVER"

if [ -n "$PULSE_SERVER" ]; then
    echo -e "${GREEN}✓ Environment variables are set${NC}"
else
    echo -e "${RED}✗ Environment variables not set${NC}"
    ALL_PASSED=false
fi
echo ""

# Test 2: Check PulseAudio client
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 2: PulseAudio Client Tools"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v pactl &> /dev/null; then
    echo -e "${GREEN}✓ PulseAudio tools installed${NC}"
else
    echo -e "${RED}✗ PulseAudio tools not found${NC}"
    echo "Run: sudo apt install pulseaudio-utils"
    ALL_PASSED=false
fi
echo ""

# Test 3: Check PortAudio library
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 3: PortAudio Library"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ldconfig -p | grep libportaudio &> /dev/null; then
    echo -e "${GREEN}✓ PortAudio library found${NC}"
else
    echo -e "${RED}✗ PortAudio library not found${NC}"
    echo "Run: sudo apt install portaudio19-dev"
    ALL_PASSED=false
fi
echo ""

# Test 4: Test PulseAudio connection
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 4: PulseAudio Server Connection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing connection to Windows PulseAudio..."

if timeout 5 pactl info &> /dev/null; then
    echo -e "${GREEN}✓ Connected to PulseAudio server${NC}"
    echo ""
    echo "Server info:"
    pactl info | grep -E "(Server Name|Server Version|Default Sink)"
else
    echo -e "${RED}✗ Cannot connect to PulseAudio server${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "  1. Check if PulseAudio is running on Windows:"
    echo "     PowerShell> Get-Process pulseaudio"
    echo ""
    echo "  2. If not running, start it:"
    echo "     PowerShell> cd C:\\PulseAudio\\bin"
    echo "     PowerShell> .\\pulseaudio.exe"
    echo ""
    echo "  3. Check Windows Firewall allows PulseAudio"
    echo ""
    echo "  4. Verify configuration file exists:"
    echo "     C:\\PulseAudio\\etc\\pulse\\default.pa"
    echo ""
    ALL_PASSED=false
fi
echo ""

# Test 5: Check Python audio modules
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 5: Python Audio Modules"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if python -c "import sounddevice" 2>/dev/null; then
    echo -e "${GREEN}✓ sounddevice module imported${NC}"

    # Try to list devices
    if python -c "import sounddevice; sounddevice.query_devices()" 2>/dev/null; then
        echo -e "${GREEN}✓ Audio devices accessible${NC}"
        echo ""
        echo "Available devices:"
        python -c "import sounddevice; print(sounddevice.query_devices())"
    else
        echo -e "${YELLOW}⚠ sounddevice imports but cannot access devices${NC}"
        echo "This might still work depending on the error."
    fi
else
    echo -e "${RED}✗ sounddevice module not found${NC}"
    echo "Run: ./dev.sh update"
    ALL_PASSED=false
fi
echo ""

# Test 6: Final audio test
if [ "$ALL_PASSED" = true ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Test 6: Real Audio Test"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Testing with Liquid ASCII..."
    echo ""

    if ./dev.sh run --speak "Audio test successful!" 2>&1; then
        echo ""
        echo -e "${GREEN}✓ Audio test passed!${NC}"
        echo ""
        echo "🎉 SUCCESS! WSL audio is working!"
        echo ""
        echo "You can now use:"
        echo "  ./dev.sh run --speak \"Your text\""
        echo "  ./dev.sh voices"
        echo ""
    else
        echo ""
        echo -e "${YELLOW}⚠ Audio test had issues${NC}"
        echo "But the basic setup looks correct."
        echo ""
        echo "Try these troubleshooting steps:"
        echo "  1. Restart WSL terminal"
        echo "  2. Check PulseAudio on Windows is running"
        echo "  3. See: cat docs/WSL_AUDIO_FIX.md"
        echo ""
    fi
else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Summary"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Complete the Windows setup first:"
    echo "  cat WINDOWS_SETUP_INSTRUCTIONS.txt"
    echo ""
    echo "Or see the full guide:"
    echo "  cat docs/WSL_AUDIO_FIX.md"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
