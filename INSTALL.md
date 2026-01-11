# Installation Guide

This guide covers installation of Liquid ASCII Art Animation on various platforms using **uv**, the fast Python package installer.

## Prerequisites

- **Python 3.11 or higher** (3.12, 3.13, 3.14 supported)
- **Terminal with ANSI support** (most modern terminals)
- **Internet connection** (required for TTS and uv installation)

### Optional

- **ffmpeg** - For MP3 to WAV conversion
- **Rhubarb Lip Sync** - For advanced phoneme detection

## Recommended: Quick Setup with uv (All Platforms)

The easiest way to get started is using our automated setup scripts that handle everything:

### Linux / macOS / WSL

```bash
# Clone repository
git clone https://github.com/yourusername/liquid-ascii.git
cd liquid-ascii

# Run automated setup (installs uv, creates venv, installs dependencies)
./dev.sh setup

# Run demo
./dev.sh run

# See all options
./dev.sh help
```

### Windows (PowerShell)

```powershell
# Clone repository
git clone https://github.com/yourusername/liquid-ascii.git
cd liquid-ascii

# Run automated setup (installs uv, creates venv, installs dependencies)
.\scripts\dev.ps1 setup

# Run demo
.\scripts\dev.ps1 run

# See all options
.\scripts\dev.ps1 help
```

### What the Setup Does

The `dev.sh` and `dev.ps1` scripts automatically:

1. ✓ Install **uv** if not present
2. ✓ Create a Python virtual environment (`.venv`)
3. ✓ Install all dependencies using uv (10-100x faster than pip)
4. ✓ Install the package in editable mode

**That's it!** You're ready to develop.

## Development Script Commands

The development scripts provide a complete workflow:

```bash
# Setup and installation
./dev.sh setup              # Full setup (first time)
./dev.sh install            # Install dependencies only
./dev.sh update             # Update all dependencies

# Running the application
./dev.sh run                # Run demo mode
./dev.sh run --speak "Hi"   # Speak text with lip sync
./dev.sh run --tutor file   # Read file aloud
./dev.sh start              # Run in background
./dev.sh stop               # Stop background process
./dev.sh restart            # Restart background process

# Development and testing
./dev.sh test               # Run all tests
./dev.sh test tests/test_sdf.py  # Run specific test
./dev.sh status             # Check environment status
./dev.sh logs               # View recent logs
./dev.sh logs -f            # Follow logs live

# Maintenance
./dev.sh clean              # Remove venv and caches
./dev.sh shell              # Activate venv in current shell
./dev.sh help               # Show full help
```

**Windows users**: Replace `./dev.sh` with `.\scripts\dev.ps1`

## Manual Installation (Alternative)

If you prefer manual installation or want more control:

### Step 1: Install uv

**Linux / macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**Alternative - Using pip:**
```bash
pip install uv
```

### Step 2: Clone Repository

```bash
git clone https://github.com/yourusername/liquid-ascii.git
cd liquid-ascii
```

### Step 3: Create Virtual Environment

```bash
# Using uv (recommended - very fast)
uv venv

# Or using standard Python
python -m venv .venv
```

### Step 4: Activate Virtual Environment

**Linux / macOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 5: Install Dependencies

```bash
# Using uv (recommended - 10-100x faster)
uv pip install -r requirements.txt
uv pip install -e .

# Or using standard pip
pip install -r requirements.txt
pip install -e .
```

### Step 6: Verify Installation

```bash
python -m src.main --static
```

You should see an ASCII head rendered in your terminal.

## Platform-Specific Audio Dependencies

### Linux (Ubuntu/Debian)

If you encounter audio issues, install PortAudio:

```bash
sudo apt update
sudo apt install portaudio19-dev python3-dev
```

### macOS

If you encounter audio issues, install PortAudio:

```bash
brew install portaudio
```

### Windows

PortAudio is typically bundled with sounddevice. If you have issues:

1. Ensure you have the latest Visual C++ Redistributable
2. Try installing sounddevice separately: `uv pip install sounddevice --upgrade`

### WSL (Windows Subsystem for Linux)

**⚠️ AUDIO WARNING:** WSL doesn't have native audio support!

**Easiest solution:** Just use Windows PowerShell instead:
```powershell
.\scripts\dev.ps1 setup
.\scripts\dev.ps1 run --speak "Audio works!"
```

**To enable audio in WSL**, see the comprehensive guide:
- **Quick fix:** [docs/WSL_AUDIO_FIX.md](docs/WSL_AUDIO_FIX.md)
- **Automated:** Run `./scripts/fix_wsl_audio.sh` in WSL
- **Windows setup:** Run `.\scripts\setup_windows_audio_for_wsl.ps1` in PowerShell

**For development without audio:**
```bash
# WSL works great for development/testing
./dev.sh setup
./dev.sh test
./dev.sh run --static  # Visual only, no audio
```

## Development Installation

For development with testing and additional tools:

```bash
# Using dev script (recommended)
./dev.sh setup

# Or manually with uv
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

This installs additional packages:
- pytest - Testing framework
- pytest-asyncio - Async test support

## Dependencies

### Required

| Package | Version | Purpose | Installation |
|---------|---------|---------|-------------|
| blessed | >=1.25.0 | Terminal handling | Auto-installed |
| numpy | >=2.0.0 | Mathematical operations | Auto-installed |
| edge-tts | >=7.2.0 | Text-to-speech | Auto-installed |
| sounddevice | >=0.5.3 | Audio playback | Auto-installed |
| scipy | >=1.11.0 | Audio file handling | Auto-installed |

### Optional

| Package | Purpose | Installation |
|---------|---------|-------------|
| pytest | Running tests | `uv pip install pytest` |
| pytest-asyncio | Async test support | `uv pip install pytest-asyncio` |

## Verifying Installation

### Check Static Render

```bash
./dev.sh run --static
# or: python -m src.main --static
```

You should see an ASCII head rendered in your terminal.

### Check Animation

```bash
./dev.sh run --fps 15
# or: python -m src.main --fps 15
```

You should see an animated head with blinking eyes.

### Check TTS Voices

```bash
./dev.sh run --list-voices
# or: python -m src.main --list-voices
```

You should see a list of available TTS voices.

### Check Speaking

```bash
./dev.sh run --speak "Hello world"
# or: python -m src.main --speak "Hello world"
```

You should hear speech with synchronized lip movement.

### Check Environment Status

```bash
./dev.sh status
```

Shows installation status of all components.

## Troubleshooting

### uv Installation Issues

**"uv command not found" after installation:**

The uv installer adds to your PATH. Restart your terminal or run:

**Linux/macOS:**
```bash
export PATH="$HOME/.cargo/bin:$PATH"
```

**Windows:**
Close and reopen PowerShell/Terminal.

### Virtual Environment Issues

**"No module named 'blessed'" or similar:**

```bash
# Ensure venv is activated
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\Activate.ps1  # Windows

# Reinstall dependencies
uv pip install -r requirements.txt
```

**"Virtual environment not found":**

```bash
./dev.sh setup  # Recreate everything
```

### Audio Issues

**"PortAudio library not found":**

**Linux:**
```bash
sudo apt install portaudio19-dev python3-dev
uv pip install sounddevice --force-reinstall
```

**macOS:**
```bash
brew install portaudio
uv pip install sounddevice --force-reinstall
```

**No audio output:**

1. Check system audio settings
2. Test audio devices: `python -c "import sounddevice; print(sounddevice.query_devices())"`
3. Try different device: `python -m src.main --speak "test" --device-id 0`

### TTS Issues

**"edge-tts requires internet":**

Edge TTS uses Microsoft's online service. Ensure you have an active internet connection.

**"Connection timeout":**

Try again. If persistent, Microsoft's service may be temporarily unavailable.

### Terminal Display Issues

**"Terminal doesn't support colors":**

```bash
export TERM=xterm-256color
./dev.sh run
```

Or run without colors:
```bash
./dev.sh run --scheme monochrome
```

**"Display looks garbled":**

1. Ensure terminal is at least 80x40 characters
2. Try a different terminal (iTerm2, Windows Terminal, gnome-terminal)
3. Check terminal font supports ASCII characters

### Performance Issues

**Slow rendering:**

```bash
# Reduce FPS
./dev.sh run --fps 10

# Use smaller terminal window
# Resize terminal to 80x30 or smaller
```

**Slow installation:**

Using uv should be 10-100x faster than pip. If still slow:
1. Check internet connection
2. Try: `uv pip install -r requirements.txt --no-cache`

### Permission Issues

**Linux/macOS - "Permission denied" on dev.sh:**

```bash
chmod +x dev.sh
./dev.sh setup
```

**Windows - "Execution policy" error:**

```powershell
# Run PowerShell as Administrator, then:
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then run the script normally:
.\scripts\dev.ps1 setup
```

## Updating

To update to the latest version:

```bash
# Pull latest code
git pull

# Update dependencies
./dev.sh update

# Or manually
uv pip install --upgrade -r requirements.txt
```

## Uninstalling

```bash
# Quick cleanup
./dev.sh clean

# Remove everything
cd ..
rm -rf liquid-ascii

# Uninstall uv (optional)
# Linux/macOS:
rm -rf ~/.cargo/bin/uv
# Windows: Run uv's uninstaller or remove from Programs
```

## Next Steps

After installation:

1. ✓ Run `./dev.sh run` to see the demo
2. ✓ Try different characters: `./dev.sh run --character robot`
3. ✓ Try speaking: `./dev.sh run --speak "Hello, I am Liquid ASCII"`
4. ✓ Read the [README](README.md) for usage examples
5. ✓ Check [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
6. ✓ Run tests: `./dev.sh test`

## Getting Help

- Check `./dev.sh status` to diagnose issues
- View logs: `./dev.sh logs`
- Read [CONTRIBUTING.md](CONTRIBUTING.md) for development setup
- Open an issue on GitHub with details from `./dev.sh status`

---

**Why uv?**

uv is written in Rust and is 10-100x faster than pip, with better dependency resolution. It's actively developed by the creators of Ruff and is becoming the standard for modern Python development.

Learn more: https://github.com/astral-sh/uv
