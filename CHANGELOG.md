# Changelog

All notable changes to Liquid ASCII Art Animation will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Demo folder with ready-made shell scripts
  - `check_prereqs.sh` - System requirements validation
  - `install.sh` - Automated dependency installation
  - `demo_basic.sh` - Static frame demo
  - `demo_animated.sh` - 15-second animation demo
  - `demo_characters.sh` - Gallery of all character types
  - `demo_expressions.sh` - Gallery of all expressions
  - `demo_all_features.sh` - Comprehensive feature showcase
  - Detailed README.md with troubleshooting guide

### Changed
- Project status updated to "Alpha" (In Development)

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
