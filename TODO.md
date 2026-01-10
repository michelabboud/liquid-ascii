# TODO

Project roadmap and planned features for Liquid ASCII Art Animation.

## Current Version (0.1.0)

### Completed
- [x] Core raymarching renderer
- [x] SDF primitives (sphere, ellipsoid, box, torus, capsule, cylinder)
- [x] Smooth boolean operations (union, subtraction, intersection)
- [x] 3D head model with eyes and mouth
- [x] Animation system with easing functions
- [x] Viseme-based lip synchronization
- [x] Edge TTS integration
- [x] Audio playback with timing
- [x] Terminal display with blessed
- [x] Color schemes (10 presets)
- [x] Rainbow color effects (5 modes)
- [x] Markdown tutoring feature
- [x] Character presets (6 types)
- [x] CLI interface
- [x] Example scripts
- [x] Documentation

## Short-term (v0.2.0)

### Rendering
- [ ] Performance optimization with NumPy vectorization
- [ ] Adaptive resolution based on terminal size
- [ ] Z-buffer for complex scenes
- [ ] Shadow casting
- [ ] Ambient occlusion approximation

### Animation
- [ ] Expression presets (happy, sad, surprised, angry)
- [ ] Eyebrow animation
- [ ] Head tracking/following
- [ ] Gesture animations
- [ ] Transition effects between expressions

### Lip Sync
- [ ] Rhubarb Lip Sync integration
- [ ] Real-time phoneme detection
- [ ] Emotion-aware speech (happy voice = smile)
- [ ] Support for multiple languages

### Audio
- [ ] Offline TTS options (Piper, pyttsx3)
- [ ] Audio recording/playback from files
- [ ] Background music support
- [ ] Sound effects library

### Display
- [ ] More color schemes
- [ ] User-defined color schemes (JSON config)
- [ ] Block character support (▓░▒█)
- [ ] Unicode character sets
- [ ] Split-screen mode (head + text)

## Medium-term (v0.3.0)

### Features
- [ ] Interactive mode (keyboard control)
- [ ] Multi-character scenes
- [ ] Scene scripting (JSON/YAML)
- [ ] Recording and export (GIF, MP4)
- [ ] Remote streaming (WebSocket)
- [ ] REST API for remote control

### Characters
- [ ] Additional character models
- [ ] Custom character builder
- [ ] Import from 3D models (OBJ simplified)
- [ ] Animal characters
- [ ] Robot characters

### Integration
- [ ] Plugin system
- [ ] LLM integration (ChatGPT, Claude)
- [ ] Voice recognition for conversations
- [ ] Subtitle generation
- [ ] Translation support

## Long-term (v1.0.0)

### Advanced Rendering
- [ ] Real-time ray tracing (GPU)
- [ ] Particle effects
- [ ] Fluid simulation (ASCII fluid)
- [ ] Environment backgrounds
- [ ] Dynamic lighting

### Platform
- [ ] Web version (WASM/Canvas)
- [ ] Mobile support (Termux)
- [ ] Electron desktop app
- [ ] Docker container
- [ ] Cloud deployment

### AI Integration
- [ ] Emotion detection from text
- [ ] Contextual expressions
- [ ] Memory/personality persistence
- [ ] Multi-turn conversations
- [ ] Knowledge base integration

## Ideas Backlog

- Real-time face tracking from webcam
- VTuber-style avatar control
- Accessibility mode (screen reader)
- Braille output support
- Game integration (NPCs)
- Educational content creator
- Storytelling engine
- Music visualization mode
- Clock/status display mode
- System monitoring with personality

## Technical Debt

- [ ] Comprehensive test suite
- [ ] CI/CD pipeline
- [ ] Performance benchmarks
- [ ] Memory profiling
- [ ] Cross-platform testing
- [ ] Documentation generator

## Known Issues

1. Performance drops at high resolution (>100x50)
2. Audio sync may drift on long speeches
3. Some terminals don't support all colors
4. Windows console may need configuration

## Contributing

Want to help? Check [CONTRIBUTING.md](CONTRIBUTING.md) and pick a task!

Priority issues are marked with `help wanted` label on GitHub.
