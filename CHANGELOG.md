# Changelog

All notable changes to Liquid ASCII Art Animation will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and core implementation
- Raymarching renderer with SDF primitives
- Smooth boolean operations for liquid effects
- 3D head model with composable features
- Animation system with easing functions
- Viseme-based lip synchronization
- Edge TTS integration for text-to-speech
- Audio playback with timing synchronization
- Terminal display with blessed library
- Color support with multiple schemes
- Rainbow color effects (horizontal, vertical, radial, diagonal, wave)
- Markdown tutoring feature for reading files aloud
- Multiple character presets (default, round, tall, wide, robot, cute)
- Command-line interface with comprehensive options
- Example scripts for various use cases

### Technical Details
- Python 3.11+ support
- Modular package architecture
- Cross-platform compatibility (Linux, macOS, Windows)
- ~15 FPS target for smooth animation
- Configurable render resolution

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
