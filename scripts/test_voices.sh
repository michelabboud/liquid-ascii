#!/usr/bin/env bash
#
# Test Different English TTS Voices
# Quick demo to hear different voice styles

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "🎤 Testing English TTS Voices"
echo "=============================="
echo ""

# Test phrases
PHRASE="Hello! I am an ASCII talking head assistant."

# Array of voices to test (name, description)
declare -a voices=(
    "en-US-AriaNeural:US Female (default)"
    "en-US-GuyNeural:US Male (news anchor)"
    "en-US-JennyNeural:US Female (warm)"
    "en-GB-RyanNeural:UK Male (British)"
    "en-GB-SoniaNeural:UK Female (British)"
    "en-AU-NatashaNeural:Australian Female"
    "en-IN-NeerjaNeural:Indian Female"
)

echo "Testing ${#voices[@]} different English voices..."
echo ""

for voice_info in "${voices[@]}"; do
    IFS=':' read -r voice desc <<< "$voice_info"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎙️  $desc"
    echo "   Voice: $voice"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Run with this voice
    ./dev.sh run --speak "$PHRASE" --voice "$voice" --fps 20

    echo ""
    echo "Press Enter to continue to next voice (or Ctrl+C to exit)..."
    read -r
    echo ""
done

echo "✅ Voice test complete!"
echo ""
echo "To use a specific voice:"
echo "  ./dev.sh run --speak \"Your text\" --voice VOICE_NAME"
echo ""
echo "List all voices:"
echo "  ./dev.sh voices"
