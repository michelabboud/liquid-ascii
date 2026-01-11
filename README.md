# Liquid ASCII Art Animation

A terminal-based ASCII art animation system featuring a "talking head" character with smooth, liquid-like 3D rendering and lip-sync capabilities.

```
          @@@@@@@@@@@@
       @@@@@@@@@@@@@@@@@@@
     @@@@@@@@@@@@@@@@@@@@@@@@
    @@@@@@   @@@@@@@@   @@@@@@
   @@@@@@ @@ @@@@@@@@ @@ @@@@@@
   @@@@@@    @@@@@@@@    @@@@@@
   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @@@@@@@@@@@@@@@@@@@@@@@@@@@
     @@@@@@@@@        @@@@@@@@@
       @@@@@@@@@@@@@@@@@@@@@
          @@@@@@@@@@@@@@
```

## Features

- **3D ASCII Rendering** - Raymarching with signed distance functions (SDF)
- **Liquid Smooth Transitions** - Metaball-style smooth unions for organic morphing
- **Talking Head Animation** - Viseme-based lip synchronization
- **Text-to-Speech Integration** - Uses Microsoft Edge TTS with character-matched voices
- **Interactive Chat Mode** - Conversation with LLM-powered character personalities (Ollama/OpenAI)
- **Voice-Enabled Chat** - AI speaks its responses aloud with perfect lip synchronization
- **12 Character Presets** - Unique appearances and personalities (robot, alien, cat, dog, baby, elder, skull, etc.)
- **Visual Effects** - Particles, motion trails, glitch effects, scanlines, matrix rain
- **Effect CLI Controls** - Individual effect toggles and intensity parameters with built-in presets
- **Configuration System** - YAML/JSON config files with auto-discovery and preset management
- **Performance Optimization** - Quality presets for different hardware capabilities
- **Ready-Made Demo Scripts** - Shell scripts for easy testing (check prereqs, install, run demos)
- **Edge Detection** - Crisp feature boundaries for clear facial recognition (enabled by default)
- **Markdown Tutoring** - Read and explain text/markdown files aloud
- **Color Support** - Rainbow effects and custom color schemes
- **Cross-Platform** - Works on Linux, macOS, and Windows
- **Multiple Distribution Methods** - PyPI package, Docker containers, or from source

## Requirements

- Python 3.11+
- Terminal with ANSI color support
- Internet connection (for TTS)

## Quick Start

**TL;DR** - Get started in 30 seconds:

```bash
git clone https://github.com/yourusername/liquid-ascii.git
cd liquid-ascii
./dev.sh setup    # One command installs everything!
./dev.sh run      # Try it!
```

**Or use ready-made demo scripts:**

```bash
./demo/check_prereqs.sh   # Check system requirements
./demo/install.sh         # Install dependencies
./demo/demo_basic.sh      # Run basic demo
./demo/demo_animated.sh   # Run animated demo
```

See [demo/README.md](demo/README.md) for all available demos and [QUICKSTART.md](QUICKSTART.md) for full command reference.

## Installation

### Option 1: Install from PyPI (Easiest)

```bash
pip install liquid-ascii
liquid-ascii --help
```

### Option 2: Docker (No Setup Required)

```bash
# Run demo
docker run -it --rm ghcr.io/YOURORG/liquid-ascii:latest

# Speak mode
docker run -it --rm ghcr.io/YOURORG/liquid-ascii:latest --speak "Hello!"

# Or use docker-compose
docker-compose --profile demo up
```

### Option 3: From Source (Recommended for Development)

**Quick Start** (uses [uv](https://github.com/astral-sh/uv) for 10-100x faster installs):

```bash
# Clone the repository
git clone https://github.com/yourusername/liquid-ascii.git
cd liquid-ascii

# Automated setup (installs uv, creates venv, installs dependencies)
./dev.sh setup

# Windows: .\scripts\dev.ps1 setup
```

**Manual Installation** (if you prefer pip):

```bash
# Clone repository
git clone https://github.com/yourusername/liquid-ascii.git
cd liquid-ascii

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

See [INSTALL.md](INSTALL.md) for detailed installation instructions and troubleshooting.

## Quick Start

### Demo Mode (Animated Head)

```bash
./dev.sh run
# or: python -m src.main
```

### Speak Text

```bash
./dev.sh run --speak "Hello, I am your ASCII assistant!"
# or: python -m src.main --speak "Hello, I am your ASCII assistant!"
```

### Tutor Mode (Read Files)

```bash
./dev.sh run --tutor README.md
# or: python -m src.main --tutor README.md
```

### Chat Mode (Interactive Conversation)

```bash
# Requires Ollama (local) or OpenAI API key
./dev.sh run --chat --character robot

# With voice output and lip sync (NEW in v0.2.0!)
./dev.sh run --chat --chat-voice --character robot

# With specific backend
./dev.sh run --chat --llm-backend openai --character alien

# List available backends
./dev.sh run --list-llm-backends
```

### With Colors and Effects

```bash
# Rainbow effect
./dev.sh run --rainbow horizontal

# Color scheme
./dev.sh run --scheme neon

# Quality settings (for performance)
./dev.sh run --quality low  # Faster on WSL/slower systems

# or: python -m src.main --rainbow horizontal --scheme neon
```

## Usage

```bash
# Using dev script (handles venv activation automatically)
./dev.sh run [options]

# Or direct Python (requires venv activation)
python -m src.main [options]

# Or if installed globally
liquid-ascii [options]
```

### Options

```
# Modes
--speak, -s TEXT        Text to speak with lip sync
--tutor, -t FILE        Read and explain text/markdown files aloud
--chat                  Interactive chat mode with LLM
--interactive, -i       Enable keyboard controls in demo mode
--static                Render single static frame

# Character & Appearance
--character, -c NAME    Character preset (default, round, tall, wide, robot, cute,
                        alien, cat, dog, baby, elder, skull)
--expression, -e NAME   Facial expression (neutral, happy, sad, angry, surprised, etc.)
--scheme NAME           Color scheme (default, pale, dark, robot, alien, ghost,
                        sunset, ocean, neon, monochrome)
--rainbow, -r MODE      Rainbow mode (horizontal, vertical, radial, diagonal, wave, time)

# Audio & LLM
--voice, -v NAME        TTS voice (default: auto-select per character)
--llm-backend TYPE      LLM backend (ollama or openai)
--llm-model NAME        LLM model name
--chat-voice            Enable voice output in chat mode (AI speaks with lip sync)

# Performance
--quality, -q LEVEL     Quality preset (low, medium, high, ultra, auto)
--fps NUMBER            Target FPS (default: 15)

# Information
--list-voices           List available TTS voices
--list-schemes          List available color schemes
--list-expressions      List available facial expressions
--list-character-voices List character-to-voice mappings
--list-llm-backends     List available LLM backends
```

### Development Commands

```bash
./dev.sh help         # Show all available commands
./dev.sh test         # Run tests
./dev.sh status       # Check environment status
./dev.sh update       # Update dependencies
./dev.sh clean        # Clean environment
```

**Windows**: Use `.\scripts\dev.ps1` instead of `./dev.sh`

## Examples

### Ready-Made Demo Scripts

The `demo/` folder contains ready-to-run shell scripts for quick testing:

```bash
# Check system prerequisites
./demo/check_prereqs.sh

# Install dependencies automatically
./demo/install.sh

# Run demos
./demo/demo_basic.sh           # Static frame
./demo/demo_animated.sh        # 15-second animation
./demo/demo_characters.sh      # Gallery of all characters
./demo/demo_expressions.sh     # Gallery of all expressions
./demo/demo_all_features.sh    # Showcase all features
```

See [demo/README.md](demo/README.md) for detailed documentation.

### Python Example Scripts

Run the example scripts:

```bash
# Basic static render
python examples/basic_head.py

# Animated head with idle motion
python examples/animated_head.py

# Full talking demo with TTS
python examples/talking_demo.py

# Rainbow color effects
python examples/rainbow_demo.py
```

## Architecture

```
liquid-ascii/
├── src/
│   ├── renderer/       # Raymarching and SDF rendering
│   │   ├── sdf.py      # SDF primitives and operations
│   │   ├── raymarcher.py
│   │   ├── shading.py  # ASCII character mapping
│   │   ├── camera.py
│   │   └── quality.py  # Performance presets
│   ├── model/          # Head model and animation
│   │   ├── head.py     # 3D head composition & character presets
│   │   ├── visemes.py  # Mouth shapes for lip sync
│   │   ├── animation.py
│   │   └── gestures.py # Advanced gesture animations
│   ├── audio/          # TTS and audio playback
│   │   ├── tts.py      # Edge TTS integration
│   │   ├── player.py   # Audio playback
│   │   └── lipsync.py  # Viseme generation
│   ├── terminal/       # Display and UI
│   │   ├── display.py
│   │   ├── colors.py
│   │   ├── input.py    # Interactive controls
│   │   └── effects.py  # Visual effects (particles, glitch, etc.)
│   ├── chat/           # LLM-powered conversation
│   │   ├── bot.py      # Chat bot controller
│   │   ├── llm.py      # LLM backends (Ollama, OpenAI)
│   │   ├── memory.py   # Conversation history
│   │   └── personality.py  # Character personalities
│   ├── tutor.py        # Markdown parsing and tutoring
│   └── main.py         # Entry point
├── examples/
├── docs/
└── tests/
```

## How It Works

### Raymarching + SDF

The rendering uses raymarching with signed distance functions, inspired by demoscene productions and Andy Sloane's famous "donut.c".

For each terminal character:
1. Map screen position to normalized coordinates
2. Cast ray from camera through screen point
3. March along ray, evaluating SDF at each step
4. When surface is hit, compute normal and lighting
5. Map luminance to ASCII character

### Smooth Blending

The liquid effect comes from smooth boolean operations on SDFs:

```python
def sdf_smooth_union(d1, d2, k=0.1):
    h = max(k - abs(d1 - d2), 0.0) / k
    return min(d1, d2) - h * h * k * 0.25
```

### Lip Sync

1. Text is synthesized to audio using Edge TTS
2. Word timestamps are extracted during synthesis
3. Words are mapped to visemes (mouth shapes)
4. Animation interpolates smoothly between visemes

### Chat Mode

1. User input is sent to LLM (Ollama or OpenAI)
2. LLM generates response based on character personality
3. Sentiment analysis determines appropriate expression
4. Character expression updates dynamically during streaming
5. Conversation context maintained in memory

## Dependencies

**Core:**
- **blessed** - Terminal handling
- **numpy** - Mathematical operations
- **edge-tts** - Text-to-speech
- **sounddevice** - Audio playback
- **scipy** - Audio file handling

**Chat Mode:**
- **aiohttp** - Async HTTP for LLM APIs
- **requests** - Availability checks
- **Ollama** (optional) - Local LLM inference
- **OpenAI API key** (optional) - Cloud LLM access

## Documentation

Comprehensive guides for all features:

- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference for all commands
- **[INSTALL.md](INSTALL.md)** - Detailed installation instructions
- **[FEATURES.md](docs/FEATURES.md)** - Stages 5-8 features (performance, characters, animations, effects)
- **[STAGES-9-11.md](docs/STAGES-9-11.md)** - Stages 9-12 features (voice personality, distribution, chat mode, voice-chat)
- **[STAGES-13-14.md](docs/STAGES-13-14.md)** - Stages 13-14 features (effect CLI flags, configuration system)
- **[BUILD.md](BUILD.md)** - Building, packaging, and distribution guide
- **[TODO.md](TODO.md)** - Development roadmap and future features
- **[CLAUDE.md](CLAUDE.md)** - Developer guidance for Claude Code

## Credits

**Created by Michel Abboud** with AI assistance (Claude/Anthropic)

This project was developed with full transparency regarding AI collaboration. The architecture, algorithms, and implementation were designed through human-AI partnership.

### References

- [Donut Math Explained](https://www.a1k0n.net/2011/07/20/donut-math.html) - Andy Sloane
- [Inigo Quilez SDF Functions](https://iquilezles.org/articles/distfunctions/)
- [Ray Marching SDFs](https://jamie-wong.com/2016/07/15/ray-marching-signed-distance-functions/)

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.
