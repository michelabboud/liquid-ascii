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
- **Text-to-Speech Integration** - Uses Microsoft Edge TTS for high-quality speech
- **Markdown Tutoring** - Read and explain text/markdown files aloud
- **Color Support** - Rainbow effects and custom color schemes
- **Cross-Platform** - Works on Linux, macOS, and Windows

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

See [QUICKSTART.md](QUICKSTART.md) for more examples and the full command reference.

## Installation

**Quick Start** (Recommended - uses [uv](https://github.com/astral-sh/uv) for 10-100x faster installs):

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

### With Colors

```bash
# Rainbow effect
./dev.sh run --rainbow horizontal

# Color scheme
./dev.sh run --scheme neon

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
--speak, -s TEXT      Text to speak
--tutor, -t FILE      Path to text/markdown file to read aloud
--character, -c NAME  Character preset (default, round, tall, wide, robot, cute)
--scheme NAME         Color scheme (default, pale, dark, robot, alien, ghost, sunset, ocean, neon, monochrome)
--rainbow, -r MODE    Rainbow mode (horizontal, vertical, radial, diagonal, wave)
--voice, -v NAME      TTS voice name (default: en-US-AriaNeural)
--fps NUMBER          Target FPS (default: 15)
--static              Render single static frame
--list-voices         List available TTS voices
--list-schemes        List available color schemes
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
│   │   └── camera.py
│   ├── model/          # Head model and animation
│   │   ├── head.py     # 3D head composition
│   │   ├── visemes.py  # Mouth shapes for lip sync
│   │   └── animation.py
│   ├── audio/          # TTS and audio playback
│   │   ├── tts.py      # Edge TTS integration
│   │   ├── player.py   # Audio playback
│   │   └── lipsync.py  # Viseme generation
│   ├── terminal/       # Display and colors
│   │   ├── display.py
│   │   └── colors.py
│   ├── tutor.py        # Markdown parsing and tutoring
│   └── main.py         # Entry point
├── examples/
└── docs/
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

## Dependencies

- **blessed** - Terminal handling
- **numpy** - Mathematical operations
- **edge-tts** - Text-to-speech
- **sounddevice** - Audio playback
- **scipy** - Audio file handling

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
