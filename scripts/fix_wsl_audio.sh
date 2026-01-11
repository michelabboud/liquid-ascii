#!/usr/bin/env bash
#
# Fix Audio in WSL
# Configures WSL to use Windows PulseAudio server

set -e

echo "🔊 WSL Audio Fix Script"
echo "======================="
echo ""

# Check if we're in WSL
if ! grep -qi microsoft /proc/version; then
    echo "❌ This script is only for WSL (Windows Subsystem for Linux)"
    echo "   You appear to be running native Linux."
    exit 1
fi

echo "✓ Running in WSL"
echo ""

# Get Windows host IP
HOST_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
echo "Windows Host IP: $HOST_IP"
echo ""

# Check if PulseAudio packages are installed
echo "📦 Checking PulseAudio installation..."
if ! command -v pulseaudio &> /dev/null; then
    echo "Installing PulseAudio..."
    sudo apt update
    sudo apt install -y pulseaudio pulseaudio-utils alsa-utils
else
    echo "✓ PulseAudio already installed"
fi
echo ""

# Configure environment variables
echo "⚙️  Configuring environment..."

# Check if already configured
if grep -q "PULSE_SERVER" ~/.bashrc; then
    echo "✓ Already configured in ~/.bashrc"
else
    echo "Adding configuration to ~/.bashrc..."
    cat >> ~/.bashrc << 'EOF'

# WSL Audio Configuration (added by fix_wsl_audio.sh)
export HOST_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
export PULSE_SERVER=tcp:$HOST_IP
EOF
    echo "✓ Configuration added"
fi

# Source the configuration
export HOST_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
export PULSE_SERVER=tcp:$HOST_IP

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ WSL Configuration Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 NEXT STEPS - Do this in WINDOWS (not WSL):"
echo ""
echo "1. Install PulseAudio on Windows:"
echo "   PowerShell> winget install --id=PulseAudio.PulseAudio -e"
echo ""
echo "   Or download manually from:"
echo "   https://www.freedesktop.org/wiki/Software/PulseAudio/Ports/Windows/Support/"
echo ""
echo "2. Configure PulseAudio (create C:\\PulseAudio\\etc\\pulse\\default.pa):"
echo "   load-module module-native-protocol-tcp auth-ip-acl=127.0.0.1;172.16.0.0/12"
echo "   load-module module-esound-protocol-tcp auth-ip-acl=127.0.0.0/8"
echo "   load-module module-waveout sink_name=output source_name=input"
echo ""
echo "3. Start PulseAudio on Windows:"
echo "   PowerShell> cd C:\\PulseAudio\\bin"
echo "   PowerShell> .\\pulseaudio.exe"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🧪 TESTING:"
echo ""
echo "After completing the Windows steps, restart your WSL terminal and test:"
echo ""
echo "  # Test audio system"
echo "  speaker-test -c 2 -t wav -D pulse"
echo ""
echo "  # Test Liquid ASCII"
echo "  ./dev.sh run --speak \"Testing audio\""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "❓ TROUBLESHOOTING:"
echo ""
echo "If audio still doesn't work:"
echo ""
echo "  1. Ensure PulseAudio is running on Windows (check Task Manager)"
echo "  2. Check Windows Firewall allows PulseAudio"
echo "  3. Verify HOST_IP is correct: echo \$HOST_IP"
echo "  4. Try: export PULSE_SERVER=tcp:\$HOST_IP:4713"
echo ""
echo "ALTERNATIVE: Just use Windows PowerShell directly!"
echo "  cd <project-dir>"
echo "  .\\scripts\\dev.ps1 run --speak \"This works!\""
echo ""
