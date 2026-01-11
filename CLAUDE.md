# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Liquid ASCII Art Animation is a terminal-based 3D rendering system that creates animated talking heads using raymarching, signed distance functions (SDFs), and text-to-speech with lip sync. The "liquid" effect comes from smooth SDF boolean operations that blend geometry organically.

### Development Tooling

This project uses **uv** (https://github.com/astral-sh/uv) for fast Python package management. The `dev.sh` (Linux/macOS) and `scripts/dev.ps1` (Windows) scripts provide a complete development workflow that automatically handles environment setup, dependency installation, testing, and running the application.

## Development Commands

### Quick Setup (First Time)

```bash
# Automated setup with uv (recommended)
./dev.sh setup              # Installs uv, creates venv, installs dependencies

# Windows
.\scripts\dev.ps1 setup
```

This handles everything automatically. See [INSTALL.md](INSTALL.md) for details.

### Running the Application

```bash
# Using dev script (recommended)
./dev.sh run                           # Demo mode (animated idle head)
./dev.sh run --speak "Hello world"     # Speak text with lip sync
./dev.sh run --tutor README.md         # Tutor mode (read files aloud)
./dev.sh run --rainbow horizontal --scheme neon  # With visual effects

# Direct Python invocation (requires venv activation)
python -m src.main
python -m src.main --speak "Hello world"
```

### Background Execution

```bash
./dev.sh start --speak "Background"    # Run in background
./dev.sh logs -f                       # Follow logs live
./dev.sh stop                          # Stop background process
./dev.sh restart                       # Restart
```

### Testing

```bash
# Using dev script
./dev.sh test                          # Run all tests
./dev.sh test tests/test_sdf.py        # Run specific test file
./dev.sh test tests/test_sdf.py -v     # Verbose output

# Direct pytest (requires venv activation)
pytest
pytest --cov=src
pytest tests/test_sdf.py -v
```

### Dependency Management

```bash
./dev.sh install            # Install/reinstall dependencies
./dev.sh update             # Update all dependencies to latest versions
```

### Development Environment

```bash
./dev.sh status             # Check environment status (uv, venv, deps, process)
./dev.sh clean              # Remove venv and cache files
./dev.sh shell              # Instructions to activate venv manually
./dev.sh logs               # View recent logs
./dev.sh help               # Show all available commands
```

### Windows Commands

Replace `./dev.sh` with `.\scripts\dev.ps1` for all commands above.

## Architecture Overview

### Core Rendering Pipeline

The system uses **raymarching** (not rasterization) to render 3D geometry to ASCII:

1. **SDF Scene Definition** (`src/model/head.py`) - Head is composed from multiple SDF primitives using smooth boolean operations
2. **Ray Generation** (`src/renderer/camera.py`) - Each terminal character position generates a ray
3. **Raymarching Loop** (`src/renderer/raymarcher.py`) - Rays march forward, querying SDF distance at each step until surface hit
4. **Surface Normals** - Computed via SDF gradient (finite differences)
5. **Lighting** (`src/renderer/shading.py`) - Phong shading model with configurable light positions
6. **ASCII Mapping** - Luminance values mapped to ASCII characters (` .:-=+*#%@`)

### SDF Composition Pattern

The head model is built by combining SDF primitives with smooth boolean operations:

```
Head = Ellipsoid (base)
     - Smooth Subtract: Eye sockets
     + Smooth Union: Eyeballs
     - Smooth Subtract: Mouth cavity
     + Smooth Union: Nose
```

The smoothness parameter `k` in operations like `sdf_smooth_union(d1, d2, k)` controls the "liquid" blending radius. Larger `k` = more fluid transitions.

### Animation System

Two parallel animation systems:

1. **Idle Animation** (`src/model/animation.py`) - Organic noise-based movements (breathing, subtle head motion, blinking) using easing functions
2. **Lip Sync** (`src/model/visemes.py`, `src/audio/lipsync.py`) - TTS word timestamps mapped to viseme cues (mouth shapes like "AH", "EE", "OO"), interpolated with Hermite smoothing

The `HeadState` dataclass in `src/model/head.py` holds all animatable parameters (mouth_openness, blink_amount, eye_look, etc.) which modify the SDF geometry each frame.

### Audio Pipeline

```
Text → Edge TTS (synthesize) → Audio File + Word Timings
                             → Lip Sync Generator → Viseme Cues
                             → Synchronized Playback (audio thread + animation loop)
```

The audio player (`src/audio/player.py`) runs in a separate thread and provides current playback position. The main animation loop queries this position and updates the mouth shape accordingly.

## Key Files and Modules

### Renderer Package (`src/renderer/`)

- **`sdf.py`** - SDF primitives (sphere, ellipsoid, box, capsule) and boolean operations (union, subtraction, intersection). Based on Inigo Quilez's reference functions.
- **`raymarcher.py`** - Core raymarching algorithm. Uses sphere tracing: step distance = SDF(point) ensures no surface overshoot.
- **`shading.py`** - Phong lighting model and ASCII character ramps for different visual styles.
- **`camera.py`** - View projection and ray direction calculation for each screen coordinate.

### Model Package (`src/model/`)

- **`head.py`** - `CharacterHead` class composes the 3D head from SDFs. Contains character presets (default, round, tall, robot, etc.). The `evaluate_sdf()` method combines all geometry.
- **`visemes.py`** - Defines mouth shapes for phonemes (A, E, I, O, U, M, etc.) and interpolation logic.
- **`animation.py`** - Easing functions, organic motion generators, and `AnimationController` for idle animations.

### Audio Package (`src/audio/`)

- **`tts.py`** - `EdgeTTSEngine` wraps edge-tts for synthesis. Returns audio file + word timing data.
- **`lipsync.py`** - `LipSyncGenerator` converts word sequences to viseme cues with timestamps.
- **`player.py`** - `AudioPlayer` handles playback with position tracking for sync.

### Terminal Package (`src/terminal/`)

- **`display.py`** - `Display` class wraps blessed terminal. Handles frame buffer rendering and cursor management.
- **`colors.py`** - Color schemes (RGB palettes) and rainbow effect generators (horizontal, radial, wave).

## Development Patterns

### Adding New SDF Primitives

1. Add the mathematical function to `src/renderer/sdf.py` following the pattern:
   ```python
   def sdf_your_shape(p: Vec3, center: Vec3 = (0,0,0), ...) -> float:
       """Return signed distance to shape."""
       # Positive = outside, negative = inside, zero = surface
   ```
2. Export in `src/renderer/__init__.py`

### Adding Character Presets

Edit `CharacterHead._get_character_geometry()` in `src/model/head.py`. Return a `HeadGeometry` dataclass with custom dimensions and blend parameters.

### Adding Color Schemes

Add RGB tuple to `PRESET_SCHEMES` dictionary in `src/terminal/colors.py`:
```python
PRESET_SCHEMES["your_scheme"] = (255, 128, 64)  # RGB
```

### Adding Visemes

Edit `VISEME_DEFINITIONS` in `src/model/visemes.py`. Each viseme needs `mouth_openness`, `mouth_width`, and `lip_pucker` values.

## Performance Considerations

- Default resolution is 80x40 characters (~3200 ray casts per frame)
- Raymarching limited to 50 max steps to maintain real-time performance
- Target frame rate is 15 FPS (configurable with `--fps`)
- SDF evaluation is the hot path - keep operations simple and avoid expensive math in the SDF functions
- Smooth operations add overhead; reduce `k` parameter or use hard unions for better performance

## Testing Strategy

- `tests/test_sdf.py` - Unit tests for SDF primitives and operations (center points, surface points, distance accuracy)
- `tests/test_animation.py` - Tests for easing functions and motion generators
- No visual regression tests currently (ASCII output varies by terminal)

## Important Constraints

- **Python 3.11+ required** - Uses match statements and modern type hints
- **Terminal requirements** - Must support ANSI color codes and at least 80x40 characters
- **Internet connection needed** - Edge TTS requires network access for synthesis
- **Audio playback** - Requires working sounddevice backend (PortAudio)

## Code Style Notes

- Type hints used throughout for clarity
- Docstrings follow Google style (Args/Returns sections)
- SDF functions are pure mathematical operations (no side effects)
- Animation state is immutable where possible (dataclasses)
- Avoid premature optimization in SDF code - clarity over micro-optimization
