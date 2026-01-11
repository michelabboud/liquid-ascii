# Quick Start Guide - Liquid ASCII

**Get started in 30 seconds!**

## First Time Setup

```bash
# 1. Clone and enter directory
git clone https://github.com/yourusername/liquid-ascii.git
cd liquid-ascii

# 2. One-command setup (installs everything)
./dev.sh setup

# 3. Done! Try it:
./dev.sh run
```

**Windows**: Use `.\scripts\dev.ps1` instead of `./dev.sh`

**WSL Users**: ⚠️ WSL doesn't have native audio! See [WSL Audio Fix Guide](docs/WSL_AUDIO_FIX.md) or just use Windows PowerShell for audio features.

---

## Demo Scripts (Alternative Setup)

**New!** Use ready-made demo scripts without dev.sh:

```bash
# 1. Check prerequisites
./demo/check_prereqs.sh

# 2. Install dependencies
./demo/install.sh

# 3. Run demos
./demo/demo_basic.sh           # Static frame
./demo/demo_animated.sh        # 15-second animation
./demo/demo_characters.sh      # All character types
./demo/demo_expressions.sh     # All expressions
./demo/demo_all_features.sh    # Everything!
```

See [demo/README.md](demo/README.md) for full documentation.

---

## Quick Commands

```bash
# Demo mode (animated head)
./dev.sh run

# Speak text (with lip sync!)
./dev.sh run --speak "Hello, I am your ASCII assistant!"

# Read a file aloud
./dev.sh run --tutor README.md

# With visual effects
./dev.sh run --rainbow horizontal --scheme neon

# List all English voices
./dev.sh voices

# Run tests
./dev.sh test

# Check status
./dev.sh status
```

---

## English TTS Voices

**You have 47 English voices available!** No setup needed - they work immediately.

### Quick Examples

```bash
# US English (default)
./dev.sh run --speak "Hello from America" --voice en-US-AriaNeural

# British English
./dev.sh run --speak "Hello from Britain" --voice en-GB-RyanNeural

# Australian English
./dev.sh run --speak "G'day mate" --voice en-AU-NatashaNeural

# Indian English
./dev.sh run --speak "Hello from India" --voice en-IN-NeerjaNeural
```

### Recommended Voices

| Voice | Type | Description |
|-------|------|-------------|
| `en-US-AriaNeural` | US Female | Natural, clear (default) ⭐ |
| `en-US-GuyNeural` | US Male | Professional news anchor |
| `en-US-JennyNeural` | US Female | Warm and friendly |
| `en-GB-RyanNeural` | UK Male | Clear British accent |
| `en-GB-SoniaNeural` | UK Female | Professional British |
| `en-AU-NatashaNeural` | AU Female | Australian accent |

### View All Voices

```bash
# List all 47 English voices
./dev.sh voices

# Or see ALL 322 voices (100+ languages)
./dev.sh run --list-voices
```

### Test Different Voices

```bash
# Interactive voice demo
./scripts/test_voices.sh
```

---

## Common Tasks

### Speaking Text

```bash
# Simple
./dev.sh run --speak "Your text here"

# With specific voice
./dev.sh run --speak "Hello world" --voice en-US-GuyNeural

# Longer text
./dev.sh run --speak "This is a longer sentence that demonstrates the text-to-speech with animated lip synchronization."
```

### Reading Files

```bash
# Read markdown file
./dev.sh run --tutor README.md

# Read text file
./dev.sh run --tutor myfile.txt
```

### Visual Effects

```bash
# Rainbow effects
./dev.sh run --rainbow horizontal  # Left to right
./dev.sh run --rainbow vertical    # Top to bottom
./dev.sh run --rainbow radial      # Center outward
./dev.sh run --rainbow wave        # Animated wave

# Color schemes
./dev.sh run --scheme neon         # Neon colors
./dev.sh run --scheme sunset       # Warm sunset
./dev.sh run --scheme ocean        # Cool ocean
./dev.sh run --scheme robot        # Tech/robot theme

# Combine both!
./dev.sh run --speak "Colorful!" --rainbow radial --scheme neon
```

### Different Characters

```bash
./dev.sh run --character default   # Standard head
./dev.sh run --character robot     # Robotic style
./dev.sh run --character round     # Rounder features
./dev.sh run --character tall      # Taller head
./dev.sh run --character wide      # Wider head
```

### Combining Options

```bash
# Everything together
./dev.sh run \
  --speak "I am a robotic rainbow head!" \
  --character robot \
  --voice en-GB-RyanNeural \
  --rainbow wave \
  --scheme neon \
  --fps 20
```

---

## Development Commands

```bash
# Setup
./dev.sh setup         # Initial setup (first time)
./dev.sh install       # Install/reinstall dependencies
./dev.sh update        # Update to latest dependencies

# Running
./dev.sh run           # Run application
./dev.sh start         # Run in background
./dev.sh stop          # Stop background process
./dev.sh restart       # Restart background process

# Testing & Status
./dev.sh test          # Run all tests
./dev.sh status        # Check environment status
./dev.sh logs          # View logs
./dev.sh logs -f       # Follow logs live

# Maintenance
./dev.sh clean         # Clean environment
./dev.sh voices        # List English voices
./dev.sh help          # Show all commands
```

---

## Troubleshooting

### "No audio output"

```bash
# Check your audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Try different device
./dev.sh run --speak "test" --device-id 0
```

### "uv command not found"

```bash
# Restart terminal or run:
export PATH="$HOME/.cargo/bin:$PATH"

# Then try again:
./dev.sh setup
```

### "Virtual environment issues"

```bash
# Clean and recreate
./dev.sh clean
./dev.sh setup
```

### "Slow rendering"

```bash
# Reduce FPS
./dev.sh run --fps 10

# Or use smaller terminal window
```

### "No audio in WSL"

**Option 1: Use Windows directly (easiest)**
```powershell
# In Windows PowerShell
.\scripts\dev.ps1 run --speak "Audio works!"
```

**Option 2: Fix WSL audio**
```bash
# Run automated fix
./scripts/fix_wsl_audio.sh

# See full guide
cat docs/WSL_AUDIO_FIX.md
```

---

## Need Help?

```bash
# Check environment status
./dev.sh status

# View recent activity logs
./dev.sh logs

# Get full help
./dev.sh help

# Or check the docs
less INSTALL.md
less docs/TTS_OPTIONS.md
```

---

## Next Steps

1. ✅ Try different voices: `./dev.sh voices`
2. ✅ Test voice styles: `./scripts/test_voices.sh`
3. ✅ Explore examples: `ls examples/`
4. ✅ Read architecture: `less ARCHITECTURE.md`
5. ✅ Run tests: `./dev.sh test`
6. ✅ Check options: `./dev.sh run --help`

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│              LIQUID ASCII QUICK REFERENCE               │
├─────────────────────────────────────────────────────────┤
│ Setup:       ./dev.sh setup                             │
│ Run:         ./dev.sh run                               │
│ Speak:       ./dev.sh run --speak "TEXT"                │
│ Voices:      ./dev.sh voices                            │
│ Test:        ./dev.sh test                              │
│ Status:      ./dev.sh status                            │
│ Help:        ./dev.sh help                              │
├─────────────────────────────────────────────────────────┤
│ Effects:                                                │
│   --rainbow horizontal|vertical|radial|wave             │
│   --scheme neon|sunset|ocean|robot|...                  │
│   --character default|robot|round|tall|wide             │
│   --voice en-US-AriaNeural (47 English voices!)         │
│   --fps NUMBER (animation speed)                        │
├─────────────────────────────────────────────────────────┤
│ Docs:        INSTALL.md, ARCHITECTURE.md                │
│ TTS Help:    docs/TTS_OPTIONS.md                        │
│ Issues:      ./dev.sh status && ./dev.sh logs           │
└─────────────────────────────────────────────────────────┘
```

**Enjoy your ASCII adventures! 🎨🎤**
