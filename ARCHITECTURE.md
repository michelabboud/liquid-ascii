# Architecture

This document describes the technical architecture of Liquid ASCII Art Animation.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                            │
│                     (Terminal / CLI)                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                       Main Controller                            │
│                        (src/main.py)                             │
└─────┬─────────────┬─────────────┬─────────────┬─────────────────┘
      │             │             │             │
      ▼             ▼             ▼             ▼
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│Renderer │   │  Model  │   │  Audio  │   │Terminal │
│ Package │   │ Package │   │ Package │   │ Package │
└─────────┘   └─────────┘   └─────────┘   └─────────┘
```

## Package Structure

### Renderer Package (`src/renderer/`)

Handles 3D-to-ASCII conversion using raymarching and signed distance functions.

```
renderer/
├── sdf.py          # SDF primitives and boolean operations
├── raymarcher.py   # Ray marching algorithm
├── shading.py      # Lighting and ASCII character mapping
└── camera.py       # View projection and ray generation
```

**Key Concepts:**

1. **SDF Primitives** - Mathematical functions that return the distance from a point to a surface
2. **Smooth Operations** - Blend SDFs together for liquid-like morphing
3. **Raymarching** - Step along rays until hitting surfaces
4. **ASCII Shading** - Map lighting intensity to characters

### Model Package (`src/model/`)

Defines the 3D head model and animation system.

```
model/
├── head.py         # Head SDF composition
├── visemes.py      # Mouth shapes for speech
└── animation.py    # Easing functions and controllers
```

**Head Composition:**

```
Head SDF = Ellipsoid (main head)
         - Smooth Subtract: Eye sockets
         + Smooth Union: Eyeballs
         - Smooth Subtract: Mouth cavity
         + Smooth Union: Nose
```

### Audio Package (`src/audio/`)

Text-to-speech and audio playback with lip sync.

```
audio/
├── tts.py          # Edge TTS integration
├── player.py       # Audio playback with timing
└── lipsync.py      # Viseme generation from speech
```

**Lip Sync Pipeline:**

```
Text → TTS Engine → Audio + Word Timings → Viseme Cues → Animation
```

### Terminal Package (`src/terminal/`)

Display and color management.

```
terminal/
├── display.py      # Blessed terminal handling
└── colors.py       # Color schemes and rainbow effects
```

## Data Flow

### Rendering Pipeline

```
1. Scene Definition (Head SDF)
       │
       ▼
2. Ray Generation (Camera)
       │
       ▼
3. Raymarching Loop
   ┌──────────────────┐
   │ For each pixel:  │
   │   Cast ray       │
   │   March forward  │
   │   Check SDF dist │
   │   If hit: shade  │
   └──────────────────┘
       │
       ▼
4. Surface Normal Calculation
       │
       ▼
5. Lighting Computation (Phong)
       │
       ▼
6. ASCII Character Selection
       │
       ▼
7. Color Application (optional)
       │
       ▼
8. Terminal Output
```

### Animation Pipeline

```
1. Time Update (dt)
       │
       ├──▶ Idle Animation (organic noise, blinking)
       │
       ├──▶ Lip Sync (viseme interpolation)
       │
       └──▶ User Input (expressions)
       │
       ▼
2. Head State Update
   - mouth_openness
   - blink_amount
   - eye_look
   - head_tilt
       │
       ▼
3. SDF Regeneration
       │
       ▼
4. Frame Render
```

### Speech Pipeline

```
1. Text Input
       │
       ▼
2. TTS Synthesis (Edge TTS)
   → Audio file
   → Word timestamps
       │
       ▼
3. Lip Sync Generation
   → Viseme cues with timing
       │
       ▼
4. Synchronized Playback
   ┌────────────────────────┐
   │ Audio Thread           │
   │   └──▶ Current position│
   │                        │
   │ Animation Loop         │
   │   Query position       │
   │   Get viseme for time  │
   │   Update mouth shape   │
   │   Render frame         │
   └────────────────────────┘
```

## Key Algorithms

### Signed Distance Functions

The SDF returns the shortest distance from point `p` to a surface:
- Positive = outside
- Negative = inside
- Zero = on surface

**Smooth Union (liquid blending):**

```python
def sdf_smooth_union(d1, d2, k):
    h = max(k - abs(d1 - d2), 0.0) / k
    return min(d1, d2) - h * h * k * 0.25
```

The parameter `k` controls blend radius.

### Raymarching

```python
def raymarch(origin, direction, sdf, max_steps=64):
    t = 0.0
    for _ in range(max_steps):
        point = origin + t * direction
        dist = sdf(point)
        if dist < 0.001:  # Hit surface
            return t, point
        t += dist  # Safe step (sphere tracing)
        if t > 100:
            break
    return None, None
```

### Viseme Interpolation

Smooth transitions between mouth shapes:

```python
def interpolate_viseme(current, target, t):
    # Hermite interpolation for smooth movement
    t_smooth = t * t * (3 - 2 * t)
    return lerp(current, target, t_smooth)
```

## Performance Considerations

### Rendering Optimization

1. **Limited Resolution** - Default 80x40 characters
2. **Reduced Ray Steps** - Max 50 iterations
3. **Early Ray Termination** - Stop when hit or too far
4. **Frame Rate Control** - Target 15-30 FPS

### Memory Usage

- Frame buffer: ~3KB per frame
- Audio buffers: ~1MB during playback
- SDF evaluation: O(1) per point

## Extension Points

### Adding New Characters

1. Create geometry in `model/head.py`
2. Add preset in `CharacterHead._get_character_geometry()`

### Adding New Color Schemes

1. Define RGB values in `terminal/colors.py`
2. Add to `PRESET_SCHEMES` dictionary

### Adding TTS Backends

1. Implement `TTSEngine` interface in `audio/tts.py`
2. Override `synthesize()` and `list_voices()`

## Dependencies Graph

```
numpy ──────┬──▶ renderer/sdf.py
            └──▶ audio/player.py

blessed ────────▶ terminal/display.py

edge-tts ───────▶ audio/tts.py

sounddevice ────▶ audio/player.py

scipy ──────────▶ audio/player.py (WAV loading)
```
