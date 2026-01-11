# Stages 13-14: Effect CLI Flags & Configuration System

This document covers Stages 13 and 14 of the Liquid ASCII development roadmap, focusing on command-line effect controls and a comprehensive configuration management system.

## Table of Contents

- [Stage 13: Effect CLI Flags](#stage-13-effect-cli-flags)
- [Stage 14: Configuration System](#stage-14-configuration-system)

---

## Stage 13: Effect CLI Flags

**Status**: ✅ Complete

Command-line interface for controlling visual effects individually or through presets.

### Overview

Stage 13 provides granular control over visual effects through CLI flags, allowing users to customize their experience without editing code or configuration files. Individual effect toggles and intensity controls make it easy to experiment with different visual styles.

### Features

#### Individual Effect Controls

All visual effects from Stage 8 are now controllable via CLI flags:

- **Particles**: Floating particle system
- **Motion Trails**: Smooth motion blur effect
- **Glitch**: Digital distortion effects
- **Scanlines**: CRT monitor simulation
- **Matrix Rain**: Matrix-style falling characters
- **Depth of Field**: Focus blur effect

#### Effect Presets

Six built-in effect combinations optimized for different aesthetics:

| Preset | Description | Effects |
|--------|-------------|---------|
| `cyberpunk` | Cyberpunk aesthetic | Glitch (15%), scanlines (60%), particles (30) |
| `matrix` | Matrix-style digital rain | Matrix rain (40%), scanlines (30%), light glitch (5%) |
| `retro` | Retro CRT monitor | Scanlines (70%), depth-of-field blur |
| `glitchy` | Heavy distortion | Glitch (25%), trails (8 frames), particles (40) |
| `minimal` | Subtle enhancement | Particles only (20) |
| `showcase` | All effects enabled | All effects with balanced intensities |

### Usage

#### Quick Start

```bash
# Enable single effect
./dev.sh run --particles

# Multiple effects
./dev.sh run --particles --scanlines --glitch

# Adjust intensity
./dev.sh run --glitch --glitch-intensity 0.3

# Use preset
./dev.sh run --effect-preset cyberpunk

# Combine preset with overrides
./dev.sh run --effect-preset matrix --matrix-density 0.6
```

#### Effect CLI Flags

**Particle System**:
```bash
--particles                    # Enable particles
--max-particles N              # Max particle count (default: 50)
```

**Motion Trails**:
```bash
--trails                       # Enable motion trails
--trail-length N               # Trail length in frames (default: 5)
```

**Glitch Effect**:
```bash
--glitch                       # Enable glitch
--glitch-intensity F           # Intensity 0-1 (default: 0.1)
```

**Scanlines**:
```bash
--scanlines                    # Enable scanlines
--scanline-intensity F         # Intensity 0-1 (default: 0.5)
```

**Matrix Rain**:
```bash
--matrix-rain                  # Enable matrix rain
--matrix-density F             # Density 0-1 (default: 0.3)
```

**Depth of Field**:
```bash
--depth-of-field               # Enable DOF blur
--dof-focus F                  # Focus distance (default: 3.5)
--dof-strength F               # Blur strength 0-1 (default: 0.5)
```

**Presets**:
```bash
--effect-preset NAME           # Load effect preset
--list-effect-presets          # List available presets
```

### Examples

#### Cyberpunk Robot

```bash
./dev.sh run \
  --character robot \
  --scheme neon \
  --effect-preset cyberpunk \
  --interactive
```

#### Matrix Style

```bash
./dev.sh run \
  --character default \
  --scheme monochrome \
  --effect-preset matrix \
  --rainbow time
```

#### Custom Heavy Glitch

```bash
./dev.sh run \
  --glitch \
  --glitch-intensity 0.4 \
  --trails \
  --trail-length 10 \
  --scanlines
```

#### Performance Mode (WSL/Low-End)

```bash
./dev.sh run \
  --quality low \
  --fps 10 \
  --particles \
  --max-particles 15
```

### Implementation Details

#### Architecture

```
CLI Args → setup_effects_from_args() → EffectsCompositor → run_demo_mode()
                                            ↓
                                  Render pipeline integration
```

1. **setup_effects_from_args()**: Converts CLI arguments to compositor configuration
2. **Effect Preset Loading**: Applies preset first, then individual flags override
3. **Compositor Integration**: Effects applied to each rendered frame
4. **Update Loop**: Effects update with delta time for animations

#### Priority System

Configuration sources are applied in this order (later overrides earlier):

1. Effect preset defaults
2. Preset configuration (if `--effect-preset` specified)
3. Individual CLI flags (highest priority)

Example:
```bash
# Preset sets glitch_intensity to 0.05
# Flag overrides it to 0.2
./dev.sh run --effect-preset matrix --glitch-intensity 0.2
```

#### File Structure

```
src/
├── main.py
│   ├── EFFECT_PRESETS dict         # Preset definitions
│   ├── setup_effects_from_args()   # Compositor configuration
│   └── run_demo_mode()             # Effect integration
└── terminal/
    └── effects.py                   # EffectsCompositor class
```

### Performance Considerations

- Effects add computational overhead
- Particles: ~5-10% FPS impact (depends on max_particles)
- Trails: ~10-15% FPS impact (depends on trail_length)
- Glitch: ~5% FPS impact
- Scanlines: ~3-5% FPS impact
- Matrix Rain: ~15-20% FPS impact (depends on density)
- Depth of Field: ~20-25% FPS impact

**Recommendations**:
- WSL/slower systems: Use `--quality low` with minimal effects
- Medium hardware: `--quality medium` with 2-3 effects
- High-end: All effects with `--quality high` or `--effect-preset showcase`

---

## Stage 14: Configuration System

**Status**: ✅ Complete

Comprehensive configuration management with YAML/JSON support, file auto-discovery, and preset system.

### Overview

Stage 14 provides a robust configuration system that eliminates the need for repetitive CLI arguments. Save your favorite configurations as presets, create project-specific settings, or use system-wide defaults.

### Features

#### File-Based Configuration

- **YAML Support**: Human-readable config files with PyYAML
- **JSON Support**: Standard JSON format
- **Auto-Discovery**: Searches multiple locations automatically
- **Priority System**: CLI args override config files

#### Configuration Presets

- **Save Current Settings**: Capture CLI args as reusable preset
- **Load Presets**: Apply saved configurations by name
- **Preset Library**: Store multiple configurations
- **Shareable**: JSON format for easy sharing

#### Multi-Location Resolution

Configuration files are searched in this order:

1. **Explicit path**: `--config path/to/config.yaml`
2. **Current directory**: `./.liquid-ascii.yaml`
3. **Home directory**: `~/.liquid-ascii.yaml`
4. **System directory**: `/etc/liquid-ascii/liquid-ascii.yaml` (Linux only)

### Usage

#### Quick Start

```bash
# Use auto-discovered config
./dev.sh run

# Load explicit config
./dev.sh run --config my-config.yaml

# Load saved preset
./dev.sh run --preset cyberpunk-robot

# Save current settings as preset
./dev.sh run --character robot --particles --save-preset my-preset

# List available presets
./dev.sh run --list-presets
```

#### Configuration File Format

**YAML Example** (`.liquid-ascii.yaml`):

```yaml
# Rendering configuration
render:
  quality: high
  fps: 15.0
  color_scheme: neon
  rainbow_mode: null

# Character configuration
character:
  character: robot
  expression: neutral
  voice: null

# Visual effects configuration
effects:
  particles: true
  max_particles: 30
  glitch: true
  glitch_intensity: 0.15
  scanlines: true
  scanline_intensity: 0.6

# Chat mode configuration
chat:
  llm_backend: ollama
  llm_model: null
  enable_voice: false
```

**JSON Example** (`.liquid-ascii.json`):

```json
{
  "render": {
    "quality": "high",
    "fps": 15.0,
    "color_scheme": "neon",
    "rainbow_mode": null
  },
  "character": {
    "character": "robot",
    "expression": "neutral",
    "voice": null
  },
  "effects": {
    "particles": true,
    "max_particles": 30,
    "glitch": true,
    "glitch_intensity": 0.15
  },
  "chat": {
    "llm_backend": "ollama",
    "llm_model": null,
    "enable_voice": false
  }
}
```

### Configuration Schema

#### AppConfig (Top-Level)

```python
AppConfig:
  render: RenderConfig
  character: CharacterConfig
  effects: EffectsConfig
  chat: ChatConfig
```

#### RenderConfig

```python
RenderConfig:
  quality: str              # low, medium, high, ultra, auto
  fps: float                # Target frames per second
  color_scheme: str         # Color scheme name
  rainbow_mode: str | None  # Rainbow effect mode
```

#### CharacterConfig

```python
CharacterConfig:
  character: str            # Character preset name
  expression: str | None    # Initial expression
  voice: str | None         # TTS voice name
```

#### EffectsConfig

```python
EffectsConfig:
  particles: bool
  max_particles: int
  trails: bool
  trail_length: int
  glitch: bool
  glitch_intensity: float
  scanlines: bool
  scanline_intensity: float
  matrix_rain: bool
  matrix_density: float
  depth_of_field: bool
  dof_focus: float
  dof_strength: float
```

#### ChatConfig

```python
ChatConfig:
  llm_backend: str          # ollama or openai
  llm_model: str | None     # Model name
  enable_voice: bool        # Voice-enabled chat
```

### Preset Management

#### Saving Presets

Presets capture current CLI arguments and save them for reuse.

```bash
# Save with all current settings
./dev.sh run \
  --character robot \
  --scheme neon \
  --particles \
  --scanlines \
  --chat-voice \
  --save-preset robot-assistant

# Preset saved to: ~/.config/liquid-ascii/presets/robot-assistant.json
```

#### Loading Presets

```bash
# Load by name
./dev.sh run --preset robot-assistant

# Override preset values with CLI args
./dev.sh run --preset robot-assistant --scheme ocean

# Combine with additional flags
./dev.sh run --preset robot-assistant --glitch --interactive
```

#### Listing Presets

```bash
./dev.sh run --list-presets
```

Output:
```
Available configuration presets:
======================================================================
  robot-assistant - Custom preset: robot-assistant
  perf-mode       - Custom preset: perf-mode
  showcase        - Custom preset: showcase

Usage: ./dev.sh run --preset <preset-name>
```

#### Preset Storage

Presets are stored as JSON files in:
```
~/.config/liquid-ascii/presets/
  ├── robot-assistant.json
  ├── perf-mode.json
  └── showcase.json
```

Preset file format:
```json
{
  "name": "robot-assistant",
  "description": "Custom preset: robot-assistant",
  "config": {
    "render": { ... },
    "character": { ... },
    "effects": { ... },
    "chat": { ... }
  }
}
```

### Priority System

Configuration sources are applied in this order (later overrides earlier):

1. **Default values**: Built-in application defaults
2. **Config file**: Auto-discovered or explicit `--config`
3. **Preset**: Loaded with `--preset`
4. **CLI arguments**: Individual flags (highest priority)

**Example**:
```bash
# config.yaml sets character=robot, scheme=neon
# preset sets character=alien
# CLI sets scheme=ocean
./dev.sh run --config config.yaml --preset mypreset --scheme ocean

# Result: character=alien (from preset), scheme=ocean (from CLI)
```

### Examples

#### Project-Specific Configuration

Create `.liquid-ascii.yaml` in your project directory:

```yaml
render:
  quality: medium
  fps: 12.0
  color_scheme: monochrome

effects:
  scanlines: true
  scanline_intensity: 0.7

# This config will be auto-loaded when running from this directory
```

Then simply run:
```bash
./dev.sh run
```

#### Personal Default Configuration

Create `~/.liquid-ascii.yaml` for your preferred settings:

```yaml
render:
  quality: high
  fps: 15.0

character:
  character: default
  expression: happy

effects:
  particles: true
  max_particles: 25

# Used as default for all projects unless overridden
```

#### System-Wide Configuration (Linux)

Admin can create `/etc/liquid-ascii/liquid-ascii.yaml`:

```yaml
# System-wide defaults for all users
render:
  quality: low  # Optimize for thin clients
  fps: 10.0

effects:
  particles: false
  trails: false
```

#### Performance Preset for WSL

```bash
# Create optimized preset for WSL
./dev.sh run \
  --quality low \
  --fps 10 \
  --particles \
  --max-particles 10 \
  --save-preset wsl-perf

# Use it later
./dev.sh run --preset wsl-perf
```

#### Development vs Production Configs

**dev-config.yaml**:
```yaml
render:
  quality: low
  fps: 30.0  # Fast iteration
effects:
  scanlines: true
```

**prod-config.yaml**:
```yaml
render:
  quality: ultra
  fps: 15.0  # Polished output
effects:
  particles: true
  scanlines: true
  glitch: true
```

Usage:
```bash
# Development
./dev.sh run --config dev-config.yaml

# Production
./dev.sh run --config prod-config.yaml
```

### Implementation Details

#### Module Structure

```
src/config/
├── __init__.py          # Public API exports
├── schema.py            # Configuration dataclasses
├── loader.py            # YAML/JSON file loading
└── presets.py           # Preset management
```

#### Configuration Loading Flow

```
1. Parse CLI args
   ↓
2. Check for --config flag
   ↓ (if not specified)
3. Auto-discover config file (cwd → home → system)
   ↓
4. Load config file (if found)
   ↓
5. Check for --preset flag
   ↓
6. Load preset (overrides config file)
   ↓
7. Merge CLI args (overrides everything)
   ↓
8. Use final merged configuration
```

#### Dependency Management

**Core** (always available):
- JSON support: Built-in Python `json` module

**Optional** (for YAML support):
- PyYAML: `pip install pyyaml`

If PyYAML is not installed, YAML config files will fail with a helpful error message, but JSON configs will still work.

### API Reference

#### Configuration Loading

```python
from src.config import load_config, find_config_file

# Auto-discover and load config
config_path = find_config_file()
if config_path:
    config = load_config(config_path)

# Load explicit path
config = load_config(Path("./my-config.yaml"))
```

#### Preset Management

```python
from src.config import save_preset, load_preset, list_presets

# Save current config
config = AppConfig(...)
save_preset("my-preset", config, description="My custom config")

# Load preset
config = load_preset("my-preset")

# List all presets
presets = list_presets()
for preset in presets:
    print(f"{preset['name']}: {preset['description']}")
```

#### Configuration Merging

```python
# Config files support merging
base_config = load_config(Path("base.yaml"))
override_config = load_config(Path("override.yaml"))

# Merge (override takes priority)
final_config = base_config.merge(override_config)
```

### Troubleshooting

#### YAML Not Supported

**Error**: `YAML support requires PyYAML: pip install pyyaml`

**Solution**:
```bash
pip install pyyaml
# or
./dev.sh install
```

Alternative: Use JSON format instead (no extra dependencies).

#### Config File Not Found

**Error**: `Config file not found: ./my-config.yaml`

**Solution**:
- Check file path and spelling
- Verify file has correct extension (.yaml, .yml, or .json)
- Use absolute path: `--config /full/path/to/config.yaml`

#### Preset Not Found

**Error**: `Preset not found: my-preset`

**Solution**:
```bash
# List available presets
./dev.sh run --list-presets

# Check preset directory
ls ~/.config/liquid-ascii/presets/
```

#### Invalid Configuration

**Error**: `Config file must contain a YAML/JSON object`

**Solution**:
- Verify YAML/JSON syntax is valid
- Use example file as reference: `.liquid-ascii.example.yaml`
- Test with online validator (yamllint.com, jsonlint.com)

### Migration Guide

#### From CLI Args to Config File

**Before** (CLI only):
```bash
./dev.sh run --character robot --scheme neon --particles --scanlines --fps 20
```

**After** (config file):

Create `.liquid-ascii.yaml`:
```yaml
render:
  fps: 20.0
  color_scheme: neon

character:
  character: robot

effects:
  particles: true
  scanlines: true
```

Then:
```bash
./dev.sh run  # Auto-loads config
```

#### From Config File to Preset

**Before** (carrying config file):
```bash
./dev.sh run --config my-settings.yaml
```

**After** (using preset):
```bash
# One-time: Convert to preset
./dev.sh run --config my-settings.yaml --save-preset my-settings

# Then use preset anywhere
./dev.sh run --preset my-settings
```

---

## Credits

**Stages 13-14 implemented by Michel Abboud** with AI assistance (Claude/Anthropic)

Inspired by:
- Modern CLI tool best practices (ripgrep, fzf, exa)
- XDG Base Directory Specification
- Configuration management patterns from Docker, Kubernetes

---

## See Also

- [README.md](../README.md) - Project overview
- [QUICKSTART.md](../QUICKSTART.md) - Quick reference
- [FEATURES.md](./FEATURES.md) - Stages 5-8 features
- [STAGES-9-11.md](./STAGES-9-11.md) - Voice personality, distribution, chat mode
