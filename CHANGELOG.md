# Changelog

All notable changes to Liquid ASCII Art Animation will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.1] - 2026-01-11

### Fixed
- **AttributeError crash** when `--duration` timer expires
  - Fixed `'NoneType' object has no attribute 'split'` error
  - `display.run_loop()` now checks for `None` before rendering
  - Demo mode exits cleanly after duration expires
- **Pip detection** in `check_prereqs.sh`
  - Now correctly detects `uv pip` in uv-created venvs
  - Shows "Available (uv pip)" when using uv
  - Falls back to `python3 -m pip` if uv not found

### Added
- **`--duration` / `-d` flag** for timed demo runs
  - Specify duration in seconds (e.g., `--duration 10`)
  - Demo mode stops automatically when time expires
  - Used by demo scripts internally

### Technical Details
- Fixed render loop to handle `None` return from update function
- Smart pip detection checks `uv pip` first, then standard pip
- Duration tracking with elapsed time counter in demo mode

## [0.3.0] - 2026-01-11

### Added - Demo System
- **Demo folder with ready-made shell scripts**
  - `check_prereqs.sh` - System requirements validation with color-coded output
  - `install.sh` - Automated dependency installation with uv/pip support
  - `demo_basic.sh` - Static frame demo
  - `demo_animated.sh` - 15-second animation demo at 30 FPS
  - `demo_characters.sh` - Gallery of all 6 character types
  - `demo_expressions.sh` - Gallery of all 6 facial expressions
  - `demo_all_features.sh` - Comprehensive feature showcase
  - `demo/requirements.txt` - Self-contained dependency list
  - `demo/README.md` - Complete documentation with troubleshooting
- **Smart venv handling** in install.sh
  - Reuses existing virtual environment instead of recreating
  - Safe to run multiple times (idempotent)
  - Verifies activation before installing requirements
  - Clear error messages and user feedback

### Added - Dynamic Resolution
- **Automatic resolution calculation** based on terminal size
  - Detects terminal width and height dynamically
  - Maintains proper 2:1 width:height aspect ratio for ASCII art
  - Applies configurable margins (default: 2 characters)
  - Respects min/max constraints (40-200 width, 20-100 height)
  - Chooses limiting dimension automatically
- **Applied to all rendering modes**:
  - Demo mode, speak mode, tutor mode, chat mode, static mode
  - Effects compositor uses dynamic resolution
  - Chat mode reserves space for UI (5 lines)

### Changed
- Resolution now adapts to terminal size instead of fixed 100×60
- Project status updated to "Alpha" (In Development)
- Demo folder is self-contained with own requirements.txt

### Technical Details
- Terminal 198×50 → Render 92×46 (2.00:1 ratio)
- Terminal 80×24 → Render 40×20 (2.00:1 ratio)
- Terminal 100×60 → Render 96×48 (2.00:1 ratio)
- ASCII characters are ~2× taller than wide, hence 2:1 ratio for proper proportions

## [0.2.0] - 2026-01-11

### Added - Major Features
- **Chat Mode** - Interactive conversation with LLM-powered characters
  - Ollama backend for local LLM inference
  - OpenAI backend for cloud LLM access
  - Streaming responses with live expression updates
  - Conversation memory and context management
  - Character-specific personalities
- **Voice-Enabled Chat** - AI speaks responses with perfect lip sync
  - `--chat-voice` flag for voice output in chat mode
  - Real-time viseme generation during speech
  - Synchronized animation with TTS
- **Edge Detection** - Crisp feature boundaries for human visibility
  - Normal discontinuity detection
  - Depth discontinuity detection
  - Geometry boundary detection
  - Adjustable intensity via `--edge-intensity` (default: 0.8)
  - Enabled by default with `--edges` / `--no-edges` toggle

### Added - Character System
- 12 character presets total (6 new):
  - `alien` - Large almond eyes, otherworldly appearance
  - `cat` - Feline features with pointed ears
  - `dog` - Canine features with floppy ears
  - `baby` - Round face, large eyes
  - `elder` - Mature features
  - `skull` - Skeletal appearance
- Character-to-voice mappings for TTS personality matching
- `--list-character-voices` command to view mappings

### Added - Expression System
- 6 facial expressions:
  - `neutral` - Calm, relaxed
  - `happy` - Wide smile, bright eyes
  - `sad` - Downturned mouth, droopy eyes
  - `angry` - Furrowed brow, tight lips
  - `surprised` - Wide eyes, open mouth
  - `thinking` - Eyes up, slight smile
- Dynamic expression updates based on sentiment analysis
- `--list-expressions` command

### Added - Visual Effects
- Particle system with customizable behavior
- Motion trail effects
- Glitch effects with configurable intensity
- Scanline overlay effects
- Matrix-style rain effect
- Individual effect CLI flags:
  - `--particles` / `--particles-intensity`
  - `--trails` / `--trails-intensity`
  - `--glitch` / `--glitch-intensity`
  - `--scanlines` / `--scanlines-intensity`
  - `--matrix` / `--matrix-intensity`

### Added - Configuration System
- YAML/JSON config file support
- Auto-discovery from multiple locations:
  - `~/.config/liquid-ascii/config.yaml`
  - `./liquid-ascii.yaml`
  - Custom path via `--config`
- Preset management system
- Effect presets (minimal, subtle, moderate, dramatic, extreme)
- `--list-presets` command

### Added - Performance & Quality
- Quality presets: `low`, `medium`, `high`, `ultra`, `auto`
- Adaptive raymarching with over-relaxation
- Configurable FPS targeting (default: 15, demos use 30)
- Resolution optimization (default 100x60, was 160x80)
- WSL-specific performance optimizations

### Added - Rendering Enhancements
- UTF-8 unicode character support (enabled by default)
  - Richer character sets: `○◌◍◎●◉⦿`
  - `--no-utf8` flag to disable
- Extended ASCII ramps:
  - `unicode`, `stars`, `diamonds`, `circles`, `squares`, `geometric`, `box`, `smooth`
  - Emoji ramps: `faces`, `hearts`, `food`, `nature`, `weather`
- Emoji facial features with `--emojis` flag
  - ⚫ (pupil), ⚪ (eye), 🔴 (mouth)

### Added - Development Tools
- Comprehensive test suite (31% coverage, 183 tests)
- Development workflow script (`dev.sh`)
- GitHub Actions CI/CD pipeline
- Pylint code analysis workflow
- Dependabot integration

### Changed
- Default resolution changed from 160x80 to 100x60 for better performance
- Edge detection enabled by default
- UTF-8 unicode characters enabled by default
- Enhanced color schemes (10 total schemes)

### Fixed
- WSL audio playback issues with PulseAudio
- Terminal size detection and validation
- Color rendering in various terminal emulators
- Memory efficiency in raymarching loops

### Technical Details
- Python 3.11+ support with modern type hints
- Modular package architecture
- Cross-platform compatibility (Linux, macOS, Windows)
- 15-30 FPS animation (configurable)
- 100x60 default resolution (configurable)

## [0.1.0] - 2026-01-10

### Added
- First public release
- Core rendering pipeline
- Head model with eyes and mouth
- Basic lip sync
- TTS integration
- Terminal display
- Color schemes

---

## Version History Notes

### v0.1.0 Goals
- [x] Core SDF rendering
- [x] Animated head model
- [x] Lip sync with TTS
- [x] Color support
- [x] Documentation

### Future Roadmap (v0.2.0+)
- [ ] Additional character models
- [ ] Expression presets (happy, sad, surprised)
- [ ] Multiple language support
- [ ] Rhubarb Lip Sync integration
- [ ] Interactive mode with user input
- [ ] Recording/export functionality
- [ ] Performance optimizations (NumPy vectorization)
- [ ] WebSocket streaming for remote display
