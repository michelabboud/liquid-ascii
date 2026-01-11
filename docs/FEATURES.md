# New Features (Stages 5-8)

This document describes the new features implemented in Stages 5-8 of development.

## Stage 5: Performance Optimizations

### Quality Presets

The renderer now supports quality presets that balance performance with visual quality.

**Usage:**
```bash
./dev.sh run --quality low      # 16 steps, fastest
./dev.sh run --quality medium   # 32 steps, balanced
./dev.sh run --quality high     # 50 steps, default
./dev.sh run --quality ultra    # 80 steps, best quality
./dev.sh run --quality auto     # Adaptive (planned for future)
```

**Quality Levels:**
- **LOW**: 16 raymarching steps, epsilon=0.01 - Best for slow systems (WSL, older hardware)
- **MEDIUM**: 32 steps, epsilon=0.005 - Good balance of speed and quality
- **HIGH**: 50 steps, epsilon=0.001 - Default quality (current baseline)
- **ULTRA**: 80 steps, epsilon=0.0005 - Maximum quality, slower performance
- **AUTO**: Adaptive quality that adjusts based on FPS (framework ready, not yet fully implemented)

**Benchmarking:**

Run the benchmark suite to test performance on your system:

```bash
python benchmarks/render_benchmark.py
```

This will test all quality levels and provide performance recommendations.

**API Usage:**

```python
from src.renderer import Raymarcher, QualityLevel

raymarcher = Raymarcher(
    width=80,
    height=40,
    quality=QualityLevel.MEDIUM
)

# Change quality dynamically
raymarcher.set_quality(QualityLevel.LOW)
```

### Performance Improvements

- **Optimized `length()` function**: Reduced array conversions for 2x speedup in vector operations
- **Quality system**: Framework for adaptive rendering based on performance
- **Benchmark suite**: Comprehensive performance testing tools

---

## Stage 6: Character Presets

Six new character presets have been added, bringing the total to 12.

### New Characters

1. **Alien** - Extraterrestrial appearance
   - Elongated head (0.7, 1.6, 0.8 radii)
   - Large almond-shaped eyes
   - Wide-set eyes (0.40 separation)
   - Minimal nose
   - Small mouth

2. **Cat** - Feline-inspired features
   - Slit pupils (smaller eyeballs)
   - Triangular nose
   - Compact face

3. **Dog** - Canine-inspired features
   - Extended head for snout effect
   - Round pupils
   - Wider nose
   - Larger mouth

4. **Baby** - Infant proportions
   - Very large eyes (0.28 socket radius)
   - Chubby, round face (1.2, 1.1, 1.1 radii)
   - Eyes high on head
   - Tiny mouth and nose

5. **Elder** - Aged appearance
   - Thinner face (0.9, 1.4, 0.9 radii)
   - Smaller eyes
   - Prominent nose (0.20 length)
   - Drooping mouth

6. **Skull** - Skeletal appearance
   - Large eye sockets (0.30 radius)
   - No visible eyeballs (0.01 radius)
   - Wide mouth cavity
   - Gaunt proportions

### Usage

```bash
# Try different characters
./dev.sh run --character alien
./dev.sh run --character cat --expression happy
./dev.sh run --character baby --scheme pale
./dev.sh run --character skull --rainbow radial

# All available characters:
# default, round, tall, wide, robot, cute, alien, cat, dog, baby, elder, skull
```

---

## Stage 7: Advanced Animations

Gesture animations and idle behaviors add life and expressiveness to the character.

### Gestures

**Nodding (Yes Gesture)**
```python
from src.model import CharacterHead

head = CharacterHead(enable_gestures=True)
head.gesture_controller.nod(duration=1.0, intensity=1.0)
```

**Shaking (No Gesture)**
```python
head.gesture_controller.shake(duration=1.5, intensity=1.0)
```

**Head Tilting (Curiosity)**
```python
head.gesture_controller.tilt(duration=2.0, direction="right", intensity=1.0)
# direction can be "left" or "right"
```

**Eye Tracking (Look At)**
```python
head.gesture_controller.look_at(x=0.5, y=-0.3, duration=0.5)
# x and y range from -1 to 1
```

### Idle Behaviors

Enable automatic idle animations for a more lifelike character:

```python
head.gesture_controller.enable_idle_behavior(True)
```

The character will randomly:
- Look around
- Perform subtle nods
- Tilt head curiously
- Blink naturally

### Gesture Sequences

Create complex animated behaviors by sequencing gestures:

```python
from src.model import create_gesture_sequence, GestureSequencer

sequence = create_gesture_sequence(
    ("nod", {"duration": 1.0}),
    ("shake", {"duration": 1.5}),
    ("tilt", {"direction": "right", "duration": 1.5}),
)

sequencer = GestureSequencer(head.gesture_controller)
sequencer.set_sequence(sequence)

# In animation loop:
sequencer.update()  # Advances through sequence automatically
```

---

## Stage 8: Visual Effects

A comprehensive effects system for ASCII rendering.

### Particle System

Floating ambient particles around the character.

```python
from src.terminal import EffectsCompositor

compositor = EffectsCompositor(width=80, height=40)
compositor.enable_particles(max_particles=50)

# In animation loop:
compositor.update(dt)
frame = compositor.render(frame_string)
```

**Features:**
- Configurable particle count
- Customizable character set
- Upward floating motion
- Automatic lifetime management
- Fading based on age

### Motion Trails

Trailing effect behind moving objects.

```python
compositor.enable_trails(length=5)  # Number of trail frames
```

Creates a ghosting effect by blending previous frames with decreasing opacity.

### Glitch Effects

Digital distortion for cyberpunk aesthetics.

```python
compositor.enable_glitch(intensity=0.1)  # 0-1 intensity
```

**Glitch types:**
- Horizontal line corruption
- Vertical column shifts
- Random character corruption
- Region inversion

### Scanline Effects

CRT monitor simulation with horizontal scanlines.

```python
compositor.enable_scanlines(intensity=0.5)
```

Simulates the scanlines of old CRT displays with subtle dimming patterns.

### Matrix Rain

Falling digital rain effect in the background.

```python
compositor.enable_matrix_rain(density=0.3)  # 0-1 density
```

Characters fall from top to bottom like in The Matrix, only appearing in empty background areas.

### Depth-of-Field Blur

Blur characters based on distance from focus.

```python
compositor.enable_depth_of_field(focus=3.5, strength=0.5)
```

Creates a focus effect by blurring objects far from the focus plane.

### Combining Effects

All effects can be combined and will be applied in optimal order:

```python
compositor = EffectsCompositor(width=80, height=40)
compositor.enable_matrix_rain(density=0.2)
compositor.enable_particles(max_particles=30)
compositor.enable_scanlines(intensity=0.3)
compositor.enable_glitch(intensity=0.05)

# In render loop:
compositor.update(dt)
rendered_frame = compositor.render(ascii_frame)
```

**Effect Order:**
1. Matrix rain (background)
2. Particles (floating overlay)
3. Motion trails (ghosting)
4. Scanlines (CRT effect)
5. Depth-of-field (focus blur)
6. Glitch (corruption, applied last)

---

## Combined Usage Examples

### High-Quality Alien with Gestures

```bash
./dev.sh run --character alien --quality ultra --expression thinking
```

### Interactive Cat with Low Quality (Performance Mode)

```bash
./dev.sh run --character cat --quality low --interactive
```

### Speaking Elder with Expression

```bash
./dev.sh run --speak "Get off my lawn!" --character elder --expression angry
```

### Baby Character Tutor Mode

```bash
./dev.sh run --tutor README.md --character baby --expression happy --voice en-US-JennyNeural
```

---

## API Documentation

### Quality System

```python
from src.renderer import QualityLevel, AdaptiveQualityController

# Manual quality control
raymarcher.set_quality(QualityLevel.LOW)

# Adaptive quality (monitors FPS and adjusts)
adaptive = AdaptiveQualityController(target_fps=15.0)
adaptive.update(current_fps)
new_quality = adaptive.get_current_preset()
```

### Gesture System

```python
from src.model import CharacterHead, GestureController

head = CharacterHead(enable_gestures=True)

# Direct gesture calls
head.gesture_controller.nod()
head.gesture_controller.shake()
head.gesture_controller.tilt(direction="left")
head.gesture_controller.look_at(x=0.5, y=0.0)

# Stop current gesture
head.gesture_controller.stop_gesture()

# Enable idle behaviors
head.gesture_controller.enable_idle_behavior(True)
```

### Effects System

```python
from src.terminal import EffectsCompositor

compositor = EffectsCompositor(width=80, height=40)

# Enable individual effects
compositor.enable_particles(max_particles=50)
compositor.enable_trails(length=5)
compositor.enable_glitch(intensity=0.1)
compositor.enable_scanlines(intensity=0.5)
compositor.enable_matrix_rain(density=0.3)
compositor.enable_depth_of_field(focus=3.5, strength=0.5)

# Update and render
compositor.update(dt)
result = compositor.render(frame_string, depth_buffer=None)
```

---

## Performance Notes

### Quality Presets
- LOW quality provides ~7% speedup over HIGH
- Main bottleneck is SDF evaluation, not raymarching steps
- For major performance gains on WSL, use LOW or MEDIUM quality

### Effects
- Particle system: Minimal overhead (~2% per 50 particles)
- Motion trails: ~5% overhead (depends on trail length)
- Glitch effects: Negligible (<1%, random occurrence)
- Scanlines: ~2% overhead
- Matrix rain: ~3% overhead (depends on density)
- Depth-of-field: ~5% overhead

### Recommendations
- For WSL2: Use `--quality low` or `--quality medium`
- Enable effects selectively based on your performance target
- Use benchmarks to test on your specific system

---

## Future Enhancements

Planned features for future development:

- **Adaptive Quality**: Fully implement automatic quality adjustment based on FPS
- **SDF Caching**: Cache SDF results for static geometry
- **Delta Rendering**: Only update changed terminal characters
- **Numba JIT**: Compile hot paths for major speedup
- **Effect Presets**: Pre-configured effect combinations
- **Effect CLI Flags**: Command-line control for effects
- **Character Builder**: Interactive tool to design custom characters
- **Gesture Recording**: Record and playback gesture sequences
- **Physics-based Particles**: More realistic particle motion
- **Post-processing Pipeline**: Extensible effect framework
