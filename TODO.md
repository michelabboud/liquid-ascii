# 📋 Liquid ASCII - Project Roadmap & TODO

This document outlines planned features, improvements, and long-term goals for the Liquid ASCII project.

---

## Current Version (0.1.0)

### ✅ Completed Features

- [x] Core raymarching renderer
- [x] SDF primitives (sphere, ellipsoid, box, torus, capsule, cylinder)
- [x] Smooth boolean operations (union, subtraction, intersection)
- [x] 3D head model with eyes and mouth
- [x] Animation system with easing functions
- [x] Viseme-based lip synchronization
- [x] Edge TTS integration (322 voices, 47 English)
- [x] Audio playback with timing
- [x] Terminal display with blessed
- [x] Color schemes (10 presets)
- [x] Rainbow color effects (5 modes)
- [x] Markdown tutoring feature
- [x] Character presets (6 types: default, round, tall, wide, robot, cute)
- [x] CLI interface with comprehensive options
- [x] Example scripts
- [x] Complete documentation (CLAUDE.md, ANIMATION_GUIDE.md, QUICKSTART.md, etc.)
- [x] Development automation (dev.sh, dev.ps1)
- [x] WSL audio support (fix scripts and documentation)
- [x] uv package manager integration
- [x] .gitignore for project hygiene

---

## 🎯 Quick Wins (High Impact, Low-Medium Effort)

These features provide immediate value and can be implemented relatively quickly.

### 1. 🎮 Interactive Controls
**Priority: HIGH** | **Effort: Medium** | **Impact: High** | **Version: 0.2.0**

Add keyboard controls during playback for real-time interaction.

**Features:**
- [ ] Arrow keys to move/rotate the head
  - `Up/Down`: Tilt head forward/backward (X rotation)
  - `Left/Right`: Turn head left/right (Y rotation)
  - `Q/E`: Lean head left/right (Z rotation)
- [ ] Number keys (1-9) to change expressions
  - `1`: Neutral, `2`: Happy, `3`: Sad, `4`: Angry
  - `5`: Surprised, `6`: Confused, `7`: Tired, `8`: Wink
- [ ] Control keys
  - `Space`: Toggle pause/resume animation
  - `C`: Cycle through color schemes
  - `R`: Toggle rainbow modes (horizontal → vertical → radial → etc.)
  - `V`: Cycle through voices (in speak mode)
  - `+/-`: Adjust FPS up/down
  - `H`: Toggle help overlay
  - `ESC` or `Q`: Quit
- [ ] Display keybindings help on screen (bottom status bar)
- [ ] Mouse support (optional) for dragging head orientation

**Implementation:**
- Create `src/terminal/input.py` - Non-blocking keyboard handler
- Create `src/model/expressions.py` - Expression presets (see #2)
- Modify `src/terminal/display.py` - Integrate input handling
- Modify `src/main.py` - Add `--interactive` flag
- Use `blessed` terminal for non-blocking keyboard input

**Technical Notes:**
- Non-blocking input with `term.inkey(timeout=0)`
- Input buffer to queue keypresses
- State machine for mode switching
- Thread-safe input handling

---

### 2. 😊 Expression System
**Priority: HIGH** | **Effort: Medium** | **Impact: High** | **Version: 0.2.0**

Implement predefined facial expressions with smooth transitions.

**Expression Presets:**
- [ ] **Neutral** (default)
  - Eyebrows: 0.0, Smile: 0.0, Eyes: normal
- [ ] **Happy**
  - Raised eyebrows (+0.3), wide smile (+0.8), slight eye squint
- [ ] **Sad**
  - Lowered eyebrows (-0.5), downturned mouth (-0.3), droopy eyes
- [ ] **Angry**
  - Furrowed brows (-0.8), tight mouth (width -0.2), intense stare
- [ ] **Surprised**
  - Raised eyebrows (+0.8), wide eyes (+0.3), open mouth (+0.6)
- [ ] **Confused**
  - One raised eyebrow (asymmetric), tilted head, slight frown
- [ ] **Tired**
  - Half-closed eyes (blink 0.5), slight mouth droop, head tilt forward
- [ ] **Wink**
  - One eye closed (asymmetric blink), slight smile
- [ ] **Thinking**
  - Eyes looking up-left, one raised eyebrow, pursed lips

**Features:**
- [ ] Smooth transitions between expressions (0.5-1 second)
- [ ] Easing functions for natural movement (ease-in-out)
- [ ] Expression queue/sequencing
- [ ] Random idle expressions (optional)
- [ ] Expression triggers:
  - Manual via API: `head.set_expression("happy")`
  - Automatic based on text sentiment (optional)
  - Timed expression changes

**Implementation:**
- Create `src/model/expressions.py`:
  ```python
  @dataclass
  class Expression:
      name: str
      eyebrow_raise: float
      smile_amount: float
      blink_amount: float
      eye_squint: float
      mouth_width_mod: float
      head_tilt: Tuple[float, float, float]
  ```
- Add `ExpressionManager` class
- Modify `src/model/head.py` - Add expression support
- Modify `src/main.py` - Add `--expression <name>` CLI option
- Create expression transition interpolator

---

### 3. ⚡ Performance Optimizations (WSL Focus)
**Priority: HIGH** | **Effort: Medium-High** | **Impact: High** | **Version: 0.2.0**

Make rendering faster, especially in WSL environments.

**Optimization Tasks:**

#### A. Adaptive Quality
- [ ] Auto-reduce quality if FPS drops below target
  - Monitor actual FPS vs target FPS
  - Adjust `max_steps` dynamically (64 → 48 → 32 → 16)
  - Reduce terminal resolution if needed
- [ ] Quality presets:
  - `--quality low` (max_steps=16, reduced resolution)
  - `--quality medium` (max_steps=32)
  - `--quality high` (max_steps=50, default)
  - `--quality ultra` (max_steps=80, full quality)

#### B. SDF Caching
- [ ] Cache SDF evaluation results for static geometry
- [ ] Invalidate cache only when head state changes
- [ ] Implement spatial hash for repeated ray queries
- [ ] Cache distance field slices

#### C. Rendering Optimizations
- [ ] Early ray termination when distance < epsilon (0.001)
- [ ] Skip pixels that haven't changed (delta rendering)
- [ ] Reduce raymarching steps for distant surfaces
- [ ] Implement distance-based LOD (level of detail)
- [ ] Use sphere tracing optimizations (overrelaxation)

#### D. Code Optimizations
- [ ] Profile hot paths with cProfile:
  ```bash
  python -m cProfile -o profile.stats -m src.main --fps 30
  ```
- [ ] Use NumPy vectorization where possible
- [ ] Consider Numba JIT compilation for critical loops:
  ```python
  from numba import jit
  @jit(nopython=True)
  def raymarching_kernel(...)
  ```
- [ ] Optimize SDF function composition (reduce call overhead)
- [ ] Pre-compute trigonometric values

#### E. Terminal Optimizations
- [ ] Delta rendering (only update changed characters)
- [ ] Reduce color escape sequence overhead
- [ ] Buffer management improvements
- [ ] Use `\033[H` (home) instead of clearing entire screen
- [ ] Batch terminal writes

**Benchmarking:**
- [ ] Add `--benchmark` flag for performance testing
- [ ] Create benchmark suite comparing optimizations
- [ ] Performance regression tests
- [ ] Document performance improvements

**Files to modify:**
- `src/renderer/raymarcher.py` - Core optimization target
- `src/renderer/sdf.py` - Cache and vectorize SDF operations
- `src/terminal/display.py` - Delta rendering
- Create `src/renderer/cache.py` - SDF caching system
- Create `benchmarks/render_benchmark.py`

**Target Goals:**
- 30 FPS @ 80x40 on WSL2 (currently ~8-10 FPS)
- 60 FPS @ 80x40 on native Linux
- Sub-100ms frame time @ 100x50

---

## 🎨 Animation & Visual Features

### 4. 🎭 More Character Presets
**Priority: Medium** | **Effort: Low-Medium** | **Impact: Medium** | **Version: 0.2.0**

Create additional character variations.

**New Characters:**

- [ ] **Alien** - Extraterrestrial appearance
  - Head radii: (0.7, 1.6, 0.8) - elongated
  - Eye socket radius: 0.30 - large almond eyes
  - Eye separation: 0.40 - wide set
  - Small mouth: height 0.05
  - Minimal nose
  - Color: green/gray by default

- [ ] **Cat** - Feline-inspired features
  - Pointed ears (using SDF capsules at top of head)
  - Whiskers (thin lines from cheeks)
  - Slit pupils (vertical ellipse)
  - Triangular nose
  - Small mouth with fangs (optional)

- [ ] **Dog** - Canine-inspired features
  - Floppy ears (hanging capsules)
  - Extended snout (forward ellipsoid)
  - Round pupils
  - Wider nose
  - Panting tongue option (visible in mouth)

- [ ] **Baby** - Infant proportions
  - Very large eyes (eyeball_radius: 0.20)
  - Eyes high on head (eye_height: 0.35)
  - Small nose (nose_length: 0.08)
  - Round, chubby cheeks (head_radii: 1.2, 1.1, 1.1)
  - Tiny mouth (mouth_height: 0.04)

- [ ] **Elder** - Aged appearance
  - Droopy features (eyes lower, mouth droops)
  - "Wrinkles" (texture variations in shading)
  - Smaller eyes (eyeball_radius: 0.10)
  - Prominent nose (nose_length: 0.20)
  - Thinner face (head_radii: 0.9, 1.4, 0.9)

- [ ] **Skull** - Skeletal appearance
  - No eyeballs (just sockets)
  - Large eye sockets
  - Nasal cavity (subtracted triangle)
  - Teeth (in mouth cavity)
  - Jawbone definition

**Custom Character Builder:**
- [ ] Interactive CLI to design characters
  - Adjust sliders for each parameter
  - Real-time preview
  - Save/load character definitions
- [ ] Character file format (YAML/JSON):
  ```yaml
  name: "MyCharacter"
  head_radii: [1.0, 1.3, 1.0]
  eye_separation: 0.35
  eye_height: 0.25
  # ... etc
  ```
- [ ] Command: `--character-file custom.yaml`

**Files to modify:**
- `src/model/head.py` - Add character geometry presets
- Create `docs/characters/` - Document each character
- Create `examples/character_builder.py` - Interactive builder

---

### 5. 🎬 Advanced Animations
**Priority: Medium** | **Effort: Medium-High** | **Impact: Medium** | **Version: 0.3.0**

Add more dynamic movement and life to the character.

**Head Movements:**
- [ ] **Nodding** (yes gesture)
  - Head tilt X: 0 → +0.3 → -0.1 → 0 (smooth arc)
  - Duration: 1 second
  - Trigger: `head.nod()`

- [ ] **Shaking** (no gesture)
  - Head tilt Y: 0 → -0.3 → +0.3 → -0.3 → 0
  - Duration: 1.5 seconds
  - Trigger: `head.shake()`

- [ ] **Tilting** (curiosity/confusion)
  - Head tilt Z: 0 → +0.4 (lean right)
  - Duration: 0.5 seconds
  - Hold for 2 seconds, then return

- [ ] **Bobbing** (idle motion)
  - Subtle up/down movement
  - Slow sine wave (period: 3 seconds)
  - Amplitude: 0.05 units

- [ ] **Looking around** (scanning environment)
  - Eyes dart to corners (saccadic movement)
  - Head follows eyes after delay
  - Random direction changes every 3-5 seconds

**Eye Animations:**
- [ ] **Saccadic movements** (quick jumps between fixation points)
  - Instantaneous eye position changes
  - Brief pause at each fixation
  - Random targets within ±0.5 range

- [ ] **Smooth pursuit** (following moving objects)
  - Smooth eye tracking
  - Virtual target moves across screen
  - Eyes follow with slight lag

- [ ] **Eye dart to random positions**
  - During idle, eyes occasionally glance to side
  - Return to center after 0.5 seconds

- [ ] **Vergence** (eyes converge/diverge)
  - Look at near object (eyes angle inward)
  - Look at far object (eyes parallel)

**Breathing Animation (enhance existing):**
- [ ] More pronounced chest movement (not just vertical)
- [ ] Shoulder rise/fall
- [ ] Nostril flare (subtle SDF morphing)
- [ ] Diaphragm breathing (abdomen expands)

**Idle Behaviors:**
- [ ] **Sighing**
  - Deep breath in (slow rise)
  - Quick exhale (drop + slight head tilt forward)
  - Occasional (every 30 seconds)

- [ ] **Yawning**
  - Slow mouth open (3 seconds)
  - Eyes close briefly
  - Jaw stretch
  - Quick close + blink

- [ ] **Stretching**
  - Head tilt back + to sides
  - Eyes closed during stretch
  - Return to neutral with satisfaction expression

- [ ] **Scratching head**
  - Head tilt slightly
  - Confused expression
  - (Virtual hand would be future enhancement)

- [ ] **Random blinks with variation**
  - Normal blink: 0.15 seconds
  - Slow blink: 0.4 seconds (sleepy)
  - Double blink: two quick blinks
  - Wink: one eye only

**Gesture System:**
- [ ] Predefined gesture sequences
- [ ] Gesture queue with timing
- [ ] Trigger gestures from code: `head.perform_gesture("nod")`
- [ ] Chain gestures: `head.gesture_sequence(["nod", "smile", "wink"])`
- [ ] Interrupt/blend gestures

**Files to modify:**
- `src/model/animation.py` - Extend animation functions
- `src/model/head.py` - Add gesture support
- Create `src/model/gestures.py` - Gesture library
- Create `src/model/idle_behaviors.py` - Idle animation manager

---

### 6. 🌈 Additional Visual Effects
**Priority: Low** | **Effort: Low-Medium** | **Impact: Low-Medium** | **Version: 0.3.0**

More color schemes and visual enhancements.

**New Color Schemes:**
- [ ] **Matrix** - Green-on-black (classic hacker aesthetic)
  - Bright green text on pure black
  - Phosphor glow effect

- [ ] **Cyberpunk** - Pink/cyan neon
  - Hot pink and electric cyan
  - High contrast, vibrant

- [ ] **Vaporwave** - Pink/purple aesthetic
  - Pastel pink, purple, teal gradients
  - Nostalgic 80s/90s vibe

- [ ] **Retro** - Amber or green phosphor
  - Monochrome amber (old terminals)
  - Monochrome green (classic CRT)

- [ ] **Sepia** - Old photograph
  - Brown/tan tones
  - Vintage appearance

- [ ] **High Contrast** - Accessibility
  - Pure white on pure black (or inverse)
  - Maximum readability

**Dynamic Effects:**
- [ ] **Glitch effect**
  - Random character corruption
  - Horizontal displacement
  - Color channel separation
  - Triggered occasionally or on command

- [ ] **Scanlines** - CRT monitor effect
  - Horizontal lines at regular intervals
  - Alternate brightness
  - Animated scrolling

- [ ] **Chromatic aberration**
  - R/G/B channel offset
  - Creates prismatic edge effect
  - Adjustable intensity

- [ ] **Glow/bloom effect**
  - Bright pixels "bleed" into neighbors
  - Softer appearance
  - Ethereal quality

- [ ] **Screen shake**
  - Random position jitter
  - Triggered by events (surprise expression, loud sounds)
  - Settles after duration

**Particle Effects:**
- [ ] **Sparkles** around happy expressions
  - ASCII characters: `*`, `·`, `˙`, `∗`
  - Float upward and fade
  - Spawn rate based on happiness level

- [ ] **Tears** when sad
  - Drop characters: `'`, `,`, `.`
  - Fall from eyes
  - Accumulate at bottom

- [ ] **Steam/smoke**
  - ASCII: `~`, `≈`, `∼`
  - Rise from top of head (thinking)
  - Dissipate over time

- [ ] **Thought bubbles**
  - Display text in bubble above head
  - ASCII art bubble border

**Files to create/modify:**
- `src/terminal/color.py` - Add color schemes
- Create `src/terminal/effects.py` - Visual effects system
- Create `src/terminal/particles.py` - Particle system

---

## 🎤 Audio & Speech Improvements

### 7. 🎙️ Voice Personality Matching
**Priority: Medium** | **Effort: Low** | **Impact: Medium** | **Version: 0.2.0**

Auto-select appropriate voice based on character.

**Voice Mappings:**
- [ ] **Default** → `en-US-AriaNeural` (neutral, pleasant)
- [ ] **Robot** → `en-US-GuyNeural` (deeper, more mechanical)
- [ ] **Cute** → `en-US-JennyNeural` (higher-pitched, friendly)
- [ ] **Tall** → `en-GB-RyanNeural` (deep, authoritative)
- [ ] **Wide** → `en-US-DavisNeural` (bold, confident)
- [ ] **Round** → `en-AU-NatashaNeural` (warm, welcoming)
- [ ] **Alien** → `en-US-GuyNeural` (pitch-shifted down)
- [ ] **Cat/Dog** → Higher-pitched voices
- [ ] **Baby** → `en-US-JennyNeural` (highest pitch)
- [ ] **Elder** → `en-GB-LibbyNeural` (mature voice)

**Features:**
- [ ] Add voice metadata to `CharacterHead` class
- [ ] Auto-select voice unless `--voice` explicitly provided
- [ ] Document recommended voices per character
- [ ] Voice preview: `--preview-voice <character>`

**Files to modify:**
- `src/model/head.py` - Add `default_voice` property to CharacterHead
- `src/audio/tts.py` - Voice selection logic
- `src/main.py` - Integrate auto-selection

---

### 8. 🌍 Multi-language Support
**Priority: Low** | **Effort: Medium** | **Impact: Medium** | **Version: 0.3.0**

Extend beyond English voices (edge-tts has 322 voices in 100+ languages).

**Features:**
- [ ] Add `--lang <code>` parameter
- [ ] Auto-detect text language (using `langdetect` library)
- [ ] List voices by language: `./dev.sh run --list-voices --lang ja`
- [ ] Support for major languages:
  - Japanese (ja-JP) - 12 voices
  - Spanish (es-ES, es-MX) - 40+ voices
  - French (fr-FR) - 15+ voices
  - German (de-DE) - 12+ voices
  - Chinese (zh-CN) - 30+ voices
  - Italian, Portuguese, Korean, Russian, etc.

**Implementation:**
- [ ] Language detection:
  ```python
  from langdetect import detect
  lang = detect(text)  # returns 'en', 'ja', 'es', etc.
  ```
- [ ] Filter voices by locale
- [ ] Default voice per language
- [ ] Update documentation with language examples

**Files to modify:**
- `src/audio/tts.py` - Language support
- `scripts/list_english_voices.py` → `scripts/list_voices.py` - Support all languages
- Add `langdetect` to requirements.txt

---

### 9. 🎛️ Audio Effects
**Priority: Low** | **Effort: High** | **Impact: Low** | **Version: 0.4.0**

Process audio with real-time effects.

**Effects:**
- [ ] **Echo/Reverb** - For ghost character
  - Add delayed copies of audio
  - Decay over time
  - Adjustable room size

- [ ] **Pitch Shifting** - Make voice higher/lower
  - Semitone adjustment
  - Formant preservation (optional)
  - Character-specific presets

- [ ] **Robot Vocoding** - Synthetic robot voice
  - Carrier wave modulation
  - Harmonizer
  - Bitcrusher

- [ ] **Distortion** - Angry/monster voices
  - Overdrive/clipping
  - Harmonic distortion
  - Fuzz effect

- [ ] **Filters** - EQ and tone shaping
  - Low-pass filter (remove high frequencies)
  - High-pass filter (remove low frequencies)
  - Bandpass filter
  - EQ adjustments

**Dependencies:**
```bash
uv pip install pedalboard  # Spotify's audio effects library (fast, high-quality)
# or: pydub, soundfile + scipy
```

**Implementation:**
- Create `src/audio/effects.py`:
  ```python
  from pedalboard import Reverb, Distortion, PitchShift

  class AudioEffectsProcessor:
      def apply_reverb(self, audio, room_size=0.5): ...
      def apply_pitch_shift(self, audio, semitones): ...
      def apply_robot_effect(self, audio): ...
  ```
- Modify `src/audio/player.py` - Apply effects before playback
- Add `--effect <name>` CLI option

---

## 🎮 Interactive Features

### 10. 💬 Chat Mode (Interactive Conversation)
**Priority: HIGH** | **Effort: High** | **Impact: Very High** | **Version: 0.3.0**

Transform into an interactive conversational assistant.

**Core Chat Features:**
- [ ] User types input, character responds
- [ ] Conversation history (maintain context)
- [ ] Expression changes based on conversation:
  - Greeting → Happy
  - Question → Thinking
  - Joke → Laughing
  - Problem → Concerned

**Integration Options:**

A. **Local LLM** (Privacy, no internet required)
- [ ] Ollama integration:
  ```python
  import ollama
  response = ollama.chat(model='llama2', messages=[...])
  ```
- [ ] llama.cpp Python bindings
- [ ] Support models: Llama 2/3, Mistral, Phi, etc.

B. **API-based LLM** (High quality, internet required)
- [ ] OpenAI API (GPT-4, GPT-3.5)
- [ ] Anthropic API (Claude)
- [ ] Google Gemini API
- [ ] API key management

C. **Rule-based Responses** (No AI, simple patterns)
- [ ] Pattern matching
- [ ] Keyword responses
- [ ] Scripted conversations
- [ ] FAQ system

**Additional Features:**
- [ ] **Speech-to-text input** (whisper.cpp)
  - Speak instead of typing
  - Real-time transcription
  - Multiple language support

- [ ] **Conversation Memory**
  - Remember previous messages
  - Context window management
  - Summarization for long conversations

- [ ] **Personality System**
  - Define character personality traits
  - Consistent response style
  - Character-specific knowledge

- [ ] **Multi-turn Conversations**
  - Follow-up questions
  - Topic tracking
  - Conversation flow management

**Command:**
```bash
./dev.sh run --chat                    # Default (local LLM)
./dev.sh run --chat --llm openai       # Use OpenAI API
./dev.sh run --chat --llm local        # Use Ollama
./dev.sh run --chat --personality friendly  # Set personality
```

**Files to create:**
- `src/chat/` - New module for chat functionality
- `src/chat/bot.py` - Chat bot interface
- `src/chat/llm.py` - LLM integration (Ollama, OpenAI, etc.)
- `src/chat/stt.py` - Speech-to-text (optional, using whisper)
- `src/chat/memory.py` - Conversation memory management
- `src/chat/personality.py` - Personality system

**Files to modify:**
- `src/main.py` - Add `--chat` mode

**Dependencies:**
```bash
# Optional dependencies (install as needed)
uv pip install ollama-python        # Local LLM
uv pip install openai               # OpenAI API
uv pip install anthropic            # Claude API
uv pip install faster-whisper       # Speech-to-text
```

---

### 11. 📊 Presentation Mode
**Priority: Medium** | **Effort: Medium** | **Impact: Medium** | **Version: 0.3.0**

Present markdown slides with narration.

**Features:**
- [ ] **Slide Parser**
  - Parse markdown files into slides
  - Support `---` separator for slide breaks
  - Extract speaker notes from HTML comments: `<!-- Note: ... -->`
  - Support for:
    - Headers (slide titles)
    - Lists (bullet points)
    - Code blocks (syntax highlighting)
    - Images (ASCII art)
    - Tables

- [ ] **Presentation Controls**
  - Auto-advance or manual control (arrow keys)
  - Progress indicator (slide X of Y)
  - Slide numbers
  - Timer/clock display
  - Pause/resume

- [ ] **Split Screen Layout**
  - Top half: Slide content (rendered markdown)
  - Bottom half: Animated character narrating
  - Adjustable split ratio

- [ ] **Animations**
  - Slide transitions (fade, slide in)
  - Bullet points appear one by one
  - Code blocks syntax highlighted
  - Character points to slide content

**Command:**
```bash
./dev.sh run --present slides.md              # Present slides
./dev.sh run --present slides.md --auto       # Auto-advance
./dev.sh run --present slides.md --speaker    # Show speaker notes
```

**Slide Format:**
```markdown
# Introduction to ASCII Art
Welcome to the presentation!
<!-- Note: Greet audience enthusiastically -->

---

## What is ASCII Art?
- Text-based graphics
- Uses characters to form images
- Terminal-friendly

---

## Demo Time!
Let me show you something cool...
```

**Files to create:**
- `src/presentation/` - Presentation module
- `src/presentation/parser.py` - Markdown parser
- `src/presentation/renderer.py` - Slide renderer
- `src/presentation/controller.py` - Presentation controller

---

### 12. 📹 Screen Recording
**Priority: Low** | **Effort: High** | **Impact: Medium** | **Version: 0.4.0**

Capture and export animations.

**Format Support:**
- [ ] **ASCII recording** (asciinema format)
  - Lightweight, text-based
  - Exact terminal reproduction
  - Shareable, web-playable

- [ ] **Animated GIF** export
  - Universal format
  - Easy sharing on social media
  - Configurable FPS and size

- [ ] **MP4 video** export
  - High quality
  - Audio included
  - Standard video format

- [ ] **PNG sequence** export
  - Individual frames
  - For further editing
  - Custom processing

**Recording Features:**
- [ ] Real-time recording: `--record output.cast`
- [ ] Configurable output FPS (can differ from render FPS)
- [ ] Audio capture with video
- [ ] Trim/edit capabilities
- [ ] Metadata embedding (character, settings, etc.)

**Playback:**
- [ ] Play back recordings: `--play recording.cast`
- [ ] Convert between formats: `--convert input.cast output.gif`
- [ ] Share recordings online (asciinema.org)

**Commands:**
```bash
# Record to asciinema format
./dev.sh run --speak "Hello" --record demo.cast

# Convert to GIF
./dev.sh convert demo.cast demo.gif

# Convert to MP4
./dev.sh convert demo.cast demo.mp4 --fps 30

# Play back recording
./dev.sh play demo.cast
```

**Dependencies:**
```bash
uv pip install asciinema    # ASCII recording
uv pip install pillow       # GIF/PNG export
# ffmpeg must be installed on system for video
```

**Files to create:**
- `src/recording/` - Recording module
- `src/recording/recorder.py` - Screen capture
- `src/recording/exporter.py` - Format converters
- `src/recording/player.py` - Playback

---

## 📦 Distribution & Polish

### 13. 📤 Package Distribution
**Priority: HIGH** | **Effort: Medium-High** | **Impact: Very High** | **Version: 0.2.0**

Make it easy for others to install and use.

**PyPI Publication:**
- [ ] Finalize package metadata in `pyproject.toml`:
  ```toml
  [project]
  name = "liquid-ascii"
  version = "0.2.0"
  description = "Terminal-based 3D animated talking head"
  authors = [{name = "Michel Abboud", email = "..."}]
  license = {text = "MIT"}
  keywords = ["ascii", "art", "animation", "tts", "terminal"]
  ```
- [ ] Setup PyPI account and credentials
- [ ] Build package: `uv build`
- [ ] Test on TestPyPI first
- [ ] Publish to PyPI: `uv publish`
- [ ] Semantic versioning (MAJOR.MINOR.PATCH)
- [ ] Create release workflow

**Installation becomes:**
```bash
pip install liquid-ascii
liquid-ascii --speak "Hello world!"
```

**Standalone Executables:**
- [ ] PyInstaller builds for Windows/macOS/Linux
  ```bash
  pyinstaller --onefile --name liquid-ascii src/main.py
  ```
- [ ] Single-file executables (no Python required)
- [ ] Auto-update mechanism
- [ ] Bundle dependencies

**Docker Container:**
- [ ] Create `Dockerfile`:
  ```dockerfile
  FROM python:3.11-slim
  COPY . /app
  RUN pip install -e /app
  ENTRYPOINT ["liquid-ascii"]
  ```
- [ ] Docker Compose for easy setup
- [ ] Publish to Docker Hub: `docker pull michelabboud/liquid-ascii`
- [ ] Volume mounts for configs

**Web Version (Future):**
- [ ] Explore WASM compilation (Pyodide)
- [ ] Browser-based demo at liquidascii.com
- [ ] No installation needed
- [ ] Share links to animations

**Files to create:**
- `Dockerfile`
- `docker-compose.yml`
- `.github/workflows/release.yml` - Release automation
- `scripts/build_executable.py` - PyInstaller script

**Files to modify:**
- `pyproject.toml` - Package metadata

---

### 14. ⚙️ Configuration System
**Priority: Medium** | **Effort: Medium** | **Impact: Medium** | **Version: 0.2.0**

Persistent user preferences and custom configurations.

**Config File Support:**
- [ ] YAML format: `~/.liquid-ascii.yaml` or `.liquid-ascii.yaml`
- [ ] JSON format: `~/.liquid-ascii.json` or `.liquid-ascii.json`
- [ ] Load from:
  1. Current directory (`./.liquid-ascii.yaml`)
  2. Home directory (`~/.liquid-ascii.yaml`)
  3. System config (`/etc/liquid-ascii/config.yaml`)
- [ ] Command line overrides config file

**Configuration Options:**
```yaml
# .liquid-ascii.yaml
defaults:
  character: robot
  voice: en-US-GuyNeural
  color_scheme: neon
  rainbow_mode: radial
  fps: 30
  quality: high

performance:
  max_steps: 50
  adaptive_quality: true
  cache_sdf: true

audio:
  device_id: 0
  volume: 0.8

characters:
  # Define custom characters
  my_character:
    head_radii: [1.1, 1.2, 1.0]
    eye_separation: 0.35
    # ...

presets:
  # Define presets
  presentation:
    character: tall
    scheme: sunset
    voice: en-GB-RyanNeural
    fps: 30
    quality: ultra

  demo:
    character: robot
    scheme: neon
    rainbow_mode: wave
    fps: 15
```

**Features:**
- [ ] Load config: `--config path/to/config.yaml`
- [ ] Save current settings: `--save-preset name`
- [ ] Load preset: `--preset presentation`
- [ ] List presets: `--list-presets`
- [ ] Generate example config: `--generate-config`

**Files to create:**
- `src/config/` - Configuration module
- `src/config/loader.py` - Config file parser
- `src/config/validator.py` - Config validation
- `.liquid-ascii.example.yaml` - Example config

**Files to modify:**
- `src/main.py` - Load and apply config

---

### 15. 📚 Examples & Demos
**Priority: Medium** | **Effort: Low** | **Impact: Medium** | **Version: 0.2.0**

Create showcase content and tutorials.

**Example Scripts:**
- [ ] `examples/tutorial.py` - Interactive tutorial
  - Teach users how to use the system
  - Step-by-step walkthrough
  - Interactive prompts

- [ ] `examples/showcase.py` - Feature showcase
  - Demonstrate all characters
  - Demonstrate all color schemes
  - Demonstrate all features in sequence

- [ ] `examples/story.py` - Narrative example
  - Tell a short story
  - Multiple expressions
  - Music/sound effects

- [ ] `examples/weather.py` - Weather report demo
  - Fetch weather data (API)
  - Narrate weather conditions
  - Appropriate expressions (happy for sunny, sad for rain)

- [ ] `examples/news_reader.py` - News reader demo
  - Read RSS feeds
  - Summarize news articles
  - Professional presentation

- [ ] `examples/quiz.py` - Interactive quiz
  - Ask questions
  - Evaluate answers
  - Score tracking

**Demo Gallery:**
- [ ] Create `demos/gallery.py` - Automated demo playback
- [ ] Record demos for sharing
- [ ] Performance comparison demos

**Video Demonstrations:**
- [ ] Record feature walkthrough videos
- [ ] Create tutorial videos for YouTube
- [ ] GIF demos for GitHub README
- [ ] Share on social media (Twitter, Reddit, etc.)

**Documentation Improvements:**
- [ ] More code examples in docs
- [ ] API documentation (Sphinx)
- [ ] Architecture diagrams (draw.io, mermaid)
- [ ] Contributing guide

**Files to create:**
- `examples/tutorial.py`
- `examples/showcase.py`
- `examples/story.py`
- `examples/weather.py`
- `examples/news_reader.py`
- `examples/quiz.py`
- `demos/gallery.py`
- `docs/examples/` - Example documentation

---

## 🧪 Testing & Quality

### 16. ✅ Test Coverage
**Priority: HIGH** | **Effort: High** | **Impact: High** | **Version: 0.2.0**

Comprehensive testing for reliability.

**Unit Tests:**
- [ ] **SDF operations** (`tests/test_sdf.py`)
  - Test each primitive (sphere, ellipsoid, box, etc.)
  - Test boolean operations (union, subtraction, intersection)
  - Test smooth operations with various smoothing factors
  - Edge cases (zero radius, negative distance, etc.)

- [ ] **Color calculations** (`tests/test_color.py`)
  - Test RGB/HSV conversions
  - Test color scheme generation
  - Test rainbow modes
  - Test ANSI escape sequence generation

- [ ] **Animation functions** (`tests/test_animation.py`)
  - Test easing functions
  - Test interpolation
  - Test organic noise
  - Test blink patterns

- [ ] **Head geometry** (`tests/test_head.py`)
  - Test HeadState updates
  - Test expression changes
  - Test mouth/eye animations
  - Test SDF generation

- [ ] **Viseme controller** (`tests/test_visemes.py`)
  - Test phoneme to viseme mapping
  - Test timing synchronization
  - Test viseme transitions

**Integration Tests:**
- [ ] **TTS synthesis** (`tests/integration/test_tts.py`)
  - Test text-to-speech generation
  - Test word timing extraction
  - Test multiple voices
  - Mock network calls for speed

- [ ] **Audio playback** (`tests/integration/test_audio.py`)
  - Test audio loading
  - Test playback timing
  - Test device enumeration
  - Mock audio output

- [ ] **Full rendering pipeline** (`tests/integration/test_render.py`)
  - Test end-to-end rendering
  - Test frame generation
  - Test terminal output
  - Compare against reference frames

**Visual Regression Tests:**
- [ ] Capture reference frames for each test case
- [ ] Compare rendered output pixel-by-pixel
- [ ] Detect visual changes/regressions
- [ ] Store reference images in `tests/fixtures/`

**Performance Benchmarks:**
- [ ] Raymarching speed (frames per second)
- [ ] SDF evaluation speed
- [ ] Memory usage profiling
- [ ] Startup time measurement
- [ ] Compare optimization impacts

**Coverage Goals:**
- [ ] Overall: >80% code coverage
- [ ] Critical paths: 100% coverage
- [ ] SDF/rendering: >90% coverage

**Test Commands:**
```bash
./dev.sh test                     # Run all tests
./dev.sh test tests/test_sdf.py  # Run specific test
./dev.sh test --coverage          # With coverage report
./dev.sh benchmark                # Run benchmarks
```

**Files to create:**
- `tests/test_sdf.py`
- `tests/test_color.py`
- `tests/test_animation.py`
- `tests/test_head.py`
- `tests/test_visemes.py`
- `tests/integration/test_tts.py`
- `tests/integration/test_audio.py`
- `tests/integration/test_render.py`
- `tests/visual/` - Visual regression tests
- `benchmarks/render_benchmark.py`
- `benchmarks/sdf_benchmark.py`

**Configuration:**
- Update `pytest.ini`
- Setup `coverage.py` config
- Add test requirements to `requirements-dev.txt`

---

### 17. 🚀 CI/CD Pipeline
**Priority: HIGH** | **Effort: Medium** | **Impact: High** | **Version: 0.2.0**

Automated testing and deployment.

**GitHub Actions Workflows:**

A. **Test Workflow** (`.github/workflows/test.yml`)
- [ ] Trigger on: push, pull request
- [ ] Test matrix:
  - Python versions: 3.11, 3.12, 3.13
  - Platforms: ubuntu-latest, macos-latest, windows-latest
  - WSL testing (separate job)
- [ ] Steps:
  1. Checkout code
  2. Setup Python
  3. Install uv
  4. Install dependencies
  5. Run tests with coverage
  6. Upload coverage to Codecov
  7. Generate test report

B. **Lint Workflow** (`.github/workflows/lint.yml`)
- [ ] Linting with ruff:
  ```bash
  ruff check .
  ruff format --check .
  ```
- [ ] Type checking with mypy:
  ```bash
  mypy src/
  ```
- [ ] Security scanning with bandit
- [ ] Dependency audit

C. **Release Workflow** (`.github/workflows/release.yml`)
- [ ] Trigger on: tag push (v*.*.*)
- [ ] Steps:
  1. Build package: `uv build`
  2. Run tests
  3. Publish to PyPI
  4. Create GitHub release
  5. Generate changelog
  6. Build executables (Windows, macOS, Linux)
  7. Upload artifacts
  8. Build and push Docker image

D. **Documentation Workflow** (`.github/workflows/docs.yml`)
- [ ] Build documentation with Sphinx or MkDocs
- [ ] Deploy to GitHub Pages
- [ ] API documentation generation
- [ ] Trigger on: push to main

**Additional Automation:**
- [ ] **Dependabot** - Automated dependency updates
- [ ] **Pre-commit hooks** - Local checks before commit
  ```yaml
  # .pre-commit-config.yaml
  repos:
    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v0.1.0
      hooks:
        - id: ruff
        - id: ruff-format
  ```
- [ ] **Codecov** - Coverage tracking and reports
- [ ] **Semantic Release** - Automated versioning

**Files to create:**
- `.github/workflows/test.yml`
- `.github/workflows/lint.yml`
- `.github/workflows/release.yml`
- `.github/workflows/docs.yml`
- `.github/dependabot.yml`
- `.pre-commit-config.yaml`

**Configuration Files:**
- `ruff.toml` - Ruff linter config
- `mypy.ini` - MyPy type checker config
- `pytest.ini` - Pytest config
- `.coveragerc` - Coverage config

**Example Test Workflow:**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.11', '3.12', '3.13']

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: |
          uv venv
          uv pip install -r requirements.txt
          uv pip install -e ".[dev]"

      - name: Run tests
        run: pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 📊 Priority Matrix Summary

### 🔥 Immediate Priority (v0.2.0 - Next 1-2 months)
1. ✅ .gitignore and project cleanup (DONE)
2. **Interactive Controls** (#1) - High impact demo feature
3. **Expression System** (#2) - Emotional depth
4. **Test Coverage** (#16) - Quality foundation
5. **CI/CD Pipeline** (#17) - Automation
6. **Performance Optimizations** (#3) - Critical for usability

### ⚡ High Priority (v0.2.0-0.3.0 - 2-4 months)
1. **Package Distribution** (#13) - PyPI publication
2. **Configuration System** (#14) - User customization
3. **More Characters** (#4) - Content expansion
4. **Voice Personality Matching** (#7) - Polish
5. **Examples & Demos** (#15) - Showcase features

### 🎯 Medium Priority (v0.3.0-0.4.0 - 4-6 months)
1. **Chat Mode** (#10) - Game-changing feature
2. **Presentation Mode** (#11) - Professional use case
3. **Advanced Animations** (#5) - Polish and delight
4. **Additional Visual Effects** (#6) - Eye candy

### 🌟 Long-term (v0.4.0+ - 6+ months)
1. **Screen Recording** (#12) - Content creation
2. **Audio Effects** (#9) - Nice-to-have
3. **Multi-language Support** (#8) - Global reach

---

## 📈 Success Metrics

Track these metrics to measure project success:

- **Performance**: Target 30 FPS @ 80x40 on WSL2, 60 FPS native
- **Distribution**: PyPI downloads per month (target: 1000+)
- **Engagement**: GitHub stars (target: 500+), forks (target: 50+)
- **Quality**: Test coverage >80%, CI passing
- **Adoption**: Active users/installations

---

## 💡 Ideas Backlog (Future Exploration)

Lower priority ideas for future consideration:

- Real-time face tracking from webcam (OpenCV)
- VTuber-style avatar control
- Accessibility mode (screen reader integration)
- Braille output support
- Game integration (NPCs in text-based games)
- Educational content creator (automated tutorials)
- Storytelling engine with branching narratives
- Music visualization mode (audio-reactive animations)
- Clock/status display mode (system monitor with personality)
- System monitoring with personality (CPU, memory, etc.)
- Multi-character scenes (multiple heads conversing)
- Scene scripting (JSON/YAML timeline)
- Remote streaming (WebSocket server)
- REST API for remote control
- Plugin system (extensible architecture)
- Mobile support (Termux on Android)
- Electron desktop app
- Cloud deployment (SaaS offering)

---

## 🛠️ Technical Debt

Ongoing maintenance tasks:

- [ ] Refactor raymarcher for better modularity
- [ ] Optimize import times (lazy loading)
- [ ] Reduce memory footprint
- [ ] Profile and eliminate performance hotspots
- [ ] Improve error messages and handling
- [ ] Add debug mode with verbose logging
- [ ] Cross-platform terminal compatibility testing
- [ ] Documentation generator (Sphinx/MkDocs)
- [ ] Code style consistency (ruff format)
- [ ] Type hints everywhere (100% mypy compliance)

---

## 🐛 Known Issues

Current limitations to address:

1. **Performance drops at high resolution** (>100x50)
   - Target: Optimize rendering pipeline (#3)

2. **Audio sync may drift on long speeches** (>2 minutes)
   - Target: Improve audio timing accuracy

3. **Some terminals don't support all colors**
   - Target: Better terminal capability detection

4. **Windows console may need configuration**
   - Target: Auto-configure Windows Terminal settings

5. **WSL audio requires manual setup**
   - Status: Automated scripts exist, but could be smoother

6. **No error handling for network failures** (TTS)
   - Target: Add retry logic and offline fallback

---

## 🤝 Contributing

Want to tackle one of these TODOs?

1. **Check if an issue exists** for the feature (GitHub Issues)
2. **Create an issue** if not (reference this TODO item number)
3. **Fork the repository**
4. **Create a feature branch**: `git checkout -b feature/interactive-controls`
5. **Implement the feature** with tests
6. **Submit a pull request**

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

**Priority issues** are marked with:
- `good first issue` - Easy entry points
- `help wanted` - Community contributions welcome
- `high priority` - Critical features

---

## 📝 Notes

- This TODO list is a **living document** and will evolve
- Priorities may change based on **community feedback**
- Some items may be **split into smaller tasks** for incremental progress
- **New ideas are always welcome!** Open an issue to discuss.

---

**Last Updated:** 2026-01-11
**Version:** 0.1.0 → 0.2.0 in progress
**Status:** Active development 🚀
