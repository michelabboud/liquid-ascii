# Installation Guide

This guide covers installation of Liquid ASCII Art Animation on various platforms.

## Prerequisites

- **Python 3.11 or higher** (3.12, 3.13, 3.14 supported)
- **pip** (Python package installer)
- **Terminal with ANSI support** (most modern terminals)
- **Internet connection** (required for TTS)

### Optional

- **ffmpeg** - For MP3 to WAV conversion
- **Rhubarb Lip Sync** - For advanced phoneme detection

## Quick Install

```bash
# Clone repository
git clone https://github.com/yourusername/liquid-ascii.git
cd liquid-ascii

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m src.main --static
```

## Platform-Specific Instructions

### Linux (Ubuntu/Debian)

```bash
# Install Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Install audio dependencies
sudo apt install portaudio19-dev python3-pyaudio

# Clone and setup
git clone https://github.com/yourusername/liquid-ascii.git
cd liquid-ascii

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install
pip install -r requirements.txt
```

### macOS

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Install PortAudio for audio
brew install portaudio

# Clone and setup
git clone https://github.com/yourusername/liquid-ascii.git
cd liquid-ascii

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install
pip install -r requirements.txt
```

### Windows

```powershell
# Install Python from python.org (3.11+)
# Ensure "Add to PATH" is checked during installation

# Clone repository
git clone https://github.com/yourusername/liquid-ascii.git
cd liquid-ascii

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Windows (WSL)

Follow the Linux instructions within your WSL distribution.

## Development Installation

For development with testing tools:

```bash
# Clone
git clone https://github.com/yourusername/liquid-ascii.git
cd liquid-ascii

# Create venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: .\venv\Scripts\activate  # Windows

# Install with dev dependencies
pip install -e ".[dev]"
```

## Dependencies

### Required

| Package | Version | Purpose |
|---------|---------|---------|
| blessed | >=1.25.0 | Terminal handling |
| numpy | >=2.0.0 | Mathematical operations |
| edge-tts | >=7.2.0 | Text-to-speech |
| sounddevice | >=0.5.3 | Audio playback |
| scipy | >=1.11.0 | Audio file handling |

### Optional

| Package | Purpose |
|---------|---------|
| soundfile | Enhanced audio format support |
| pytest | Running tests |
| pytest-asyncio | Async test support |

## Verifying Installation

### Check Static Render

```bash
python -m src.main --static
```

You should see an ASCII head rendered in your terminal.

### Check Animation

```bash
python -m src.main --fps 15
```

You should see an animated head with blinking eyes.

### Check TTS

```bash
python -m src.main --list-voices
```

You should see a list of available TTS voices.

### Check Speaking

```bash
python -m src.main --speak "Hello world"
```

You should hear speech with synchronized lip movement.

## Troubleshooting

### "No module named 'blessed'"

```bash
pip install blessed
```

### "No module named 'sounddevice'"

```bash
pip install sounddevice
```

On Linux, you may also need:
```bash
sudo apt install portaudio19-dev
```

### "PortAudio library not found"

**Linux:**
```bash
sudo apt install portaudio19-dev
```

**macOS:**
```bash
brew install portaudio
```

**Windows:**
PortAudio should be bundled with sounddevice.

### "edge-tts requires internet"

Edge TTS uses Microsoft's online service. Ensure you have an internet connection.

### "Terminal doesn't support colors"

Try setting:
```bash
export TERM=xterm-256color
```

Or run without colors:
```bash
python -m src.main --scheme monochrome
```

### Audio Issues

If audio doesn't play:
1. Check system audio settings
2. Try: `python -c "import sounddevice; print(sounddevice.query_devices())"`
3. Set audio device: `export SDL_AUDIODRIVER=pulseaudio` (Linux)

### Performance Issues

For slow rendering:
```bash
# Reduce FPS
python -m src.main --fps 10

# Use smaller terminal
resize -s 30 60  # Linux
```

## Uninstalling

```bash
# If installed in venv
deactivate
rm -rf venv

# If installed globally
pip uninstall liquid-ascii blessed numpy edge-tts sounddevice scipy
```

## Next Steps

After installation:
1. Try the [Quick Start](README.md#quick-start)
2. Run the [Examples](examples/)
3. Read the [Architecture](ARCHITECTURE.md)
