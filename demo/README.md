# Liquid ASCII Demo Scripts

Ready-made shell scripts to quickly test and demonstrate Liquid ASCII features.

## Quick Start

```bash
# 1. Check prerequisites
./demo/check_prereqs.sh

# 2. Install dependencies
./demo/install.sh

# 3. Run a demo
./demo/demo_basic.sh
```

## Available Scripts

### Setup & Installation

| Script | Description |
|--------|-------------|
| `check_prereqs.sh` | Check if Python 3.11+, terminal size, audio, and network are available |
| `install.sh` | Create virtual environment and install all dependencies |

### Demos

| Script | Description | Duration |
|--------|-------------|----------|
| `demo_basic.sh` | Single static frame with default settings | Instant |
| `demo_animated.sh` | 15 seconds of animated head with idle motion | 15s |
| `demo_characters.sh` | Gallery of all character types (default, baby, tall, wide, alien, robot) | ~30s |
| `demo_expressions.sh` | Gallery of all expressions (neutral, happy, sad, angry, surprised, thinking) | ~30s |
| `demo_all_features.sh` | Showcase all features: UTF-8, colors, emojis, edges, rainbow effects | ~30s |

## Prerequisites

- **Python 3.11+** (required)
- **Terminal**: 100x60 minimum (80x40 works but smaller)
- **ANSI colors**: Most modern terminals support this
- **Audio**: Optional, for TTS features (ALSA/PulseAudio on Linux, built-in on macOS/Windows)
- **Network**: Optional, for TTS features (Edge TTS requires internet)

## What Each Demo Shows

### Basic Demo (`demo_basic.sh`)
- Single static frame
- Default character with neutral expression
- UTF-8 unicode characters
- Edge detection enabled
- 24-bit RGB colors

**Output**: One frame rendered instantly

### Animated Demo (`demo_animated.sh`)
- Baby character with organic idle animation
- Breathing motion
- Blinking eyes
- Subtle head movements
- 30 FPS smooth animation

**Output**: 15 seconds of animation

### Characters Gallery (`demo_characters.sh`)
Shows 5 seconds of animation for each character type:

1. **default** - Standard proportions, balanced features
2. **baby** - Round face, large eyes, small features
3. **tall** - Elongated vertical proportions
4. **wide** - Wider horizontal proportions
5. **alien** - Large almond eyes, small mouth
6. **robot** - Mechanical, angular features

**Output**: ~30 seconds total (6 characters × 5s each)

### Expressions Gallery (`demo_expressions.sh`)
Shows static frame for each expression:

1. **neutral** - Calm, relaxed face
2. **happy** - Wide smile, bright eyes
3. **sad** - Downturned mouth, droopy eyes
4. **angry** - Furrowed brow, tight lips
5. **surprised** - Wide eyes, open mouth
6. **thinking** - Eyes looking up, slight smile

**Output**: ~30 seconds total (6 expressions × 5s each)

### All Features Demo (`demo_all_features.sh`)
Three demos showcasing different feature combinations:

1. **Robot + Neon + Emojis + Rainbow**
   - Emoji eyes (⚫⚪) and mouth (🔴)
   - Neon color scheme
   - Horizontal rainbow gradient

2. **Alien + Green + Wave Rainbow**
   - Alien character geometry
   - Green color scheme
   - Wave rainbow effect

3. **Baby + Radial Rainbow**
   - Round baby character
   - Radial rainbow gradient from center

**Output**: ~30 seconds total (3 demos × 10s each)

## Features Demonstrated

All demos showcase these features by default:

✅ **UTF-8 Unicode Characters** - Richer character set than ASCII (`○◌◍◎●◉⦿`)
✅ **Edge Detection** - Crisp dark outlines around features
✅ **24-bit RGB Colors** - True color terminal support
✅ **100x60 Resolution** - Balanced quality and performance
✅ **30 FPS Animation** - Smooth motion (in animated demos)

Optional features shown in specific demos:

- **Emoji Features** - Emoji characters for eyes/mouth (all features demo)
- **Rainbow Effects** - Color gradients (horizontal, wave, radial)
- **Color Schemes** - Different skin tones (default, neon, green, etc.)

## Terminal Requirements

### Minimum
- **Size**: 80×40 characters
- **Colors**: ANSI 256-color support

### Recommended
- **Size**: 100×60 characters or larger
- **Colors**: 24-bit true color support
- **Font**: Monospace with unicode support (e.g., DejaVu Sans Mono, Fira Code, JetBrains Mono)

## Troubleshooting

### "Virtual environment not found"
Run `./demo/install.sh` first to set up dependencies.

### "Python 3.11+ required"
Install Python 3.11 or newer:
- **Ubuntu/Debian**: `sudo apt install python3.11`
- **macOS**: `brew install python@3.11`
- **Windows**: Download from python.org

### Terminal too small
Maximize your terminal window or increase font size. The demos need at least 80×40 characters.

### Colors look wrong
Ensure your terminal supports 24-bit true color:
- **iTerm2** (macOS): ✅ Full support
- **Windows Terminal**: ✅ Full support
- **GNOME Terminal**: ✅ Full support (recent versions)
- **xterm**: ⚠️ May need configuration

### Audio not working (for TTS features)
The demo scripts don't use TTS, but if you want to test it:
- **Linux**: Install ALSA utils: `sudo apt-get install alsa-utils`
- **macOS**: Built-in audio should work
- **Windows**: Built-in audio should work

## Running Custom Commands

All demos activate the virtual environment automatically. To run custom commands:

```bash
# Activate venv manually
source .venv/bin/activate

# Run with custom options
python -m src.main --help
python -m src.main --character alien --scheme green --duration 30
python -m src.main --static --expression happy --emojis
python -m src.main --speak "Hello world" --character robot

# Deactivate when done
deactivate
```

## Next Steps

After running the demos, see:
- **README.md** - Full project documentation
- **INSTALL.md** - Detailed installation guide
- **src/main.py --help** - All command-line options
- **dev.sh** - Development workflow script

## Windows Support

Windows users should use PowerShell equivalents:
- Check prerequisites: See README.md for manual steps
- Install: Use `.\scripts\dev.ps1 setup`
- Run demos: Use `.\scripts\dev.ps1 run` with appropriate flags

Or run directly after activating venv:
```powershell
.\.venv\Scripts\Activate.ps1
python -m src.main --static
```
