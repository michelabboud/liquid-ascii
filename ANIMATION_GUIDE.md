# 🎨 Liquid ASCII Animation Guide

Complete guide to visual effects and animation features.

---

## 🎭 Character Presets

Different head shapes with unique proportions:

### Default
```bash
./dev.sh run --character default
```
Standard proportions - balanced and neutral.

### Round
```bash
./dev.sh run --character round
```
Rounder head with closer-set eyes. Friendlier appearance.
- Head radii: (1.1, 1.1, 1.0) - more spherical
- Eye separation: 0.30 (closer together)

### Tall
```bash
./dev.sh run --character tall
```
Elongated head, eyes higher, mouth lower. Elegant look.
- Head radii: (0.9, 1.5, 0.9) - vertically stretched
- Eye height: 0.35 (higher position)
- Mouth Y: -0.45 (lower position)

### Wide
```bash
./dev.sh run --character wide
```
Wider head with far-apart eyes. Bold presence.
- Head radii: (1.2, 1.1, 0.9) - horizontally stretched
- Eye separation: 0.45 (far apart)

### Robot
```bash
./dev.sh run --character robot
```
Mechanical look with sharper features and less smoothing.
- Cubic head: (1.0, 1.0, 1.0)
- Larger eyes: 0.15 radius
- Sharp smoothing: 0.02 (more geometric)

### Cute
```bash
./dev.sh run --character cute
```
Large eyes, higher on head, small mouth. Kawaii style!
- Large eyeballs: 0.18 radius
- Eyes closer together: 0.30 separation
- Small mouth higher up: -0.25 Y position

---

## 🌈 Rainbow Modes

Dynamic color effects that change over time or space:

### Horizontal Rainbow
```bash
./dev.sh run --rainbow horizontal
```
Colors flow left-to-right across the screen.

### Vertical Rainbow
```bash
./dev.sh run --rainbow vertical
```
Colors flow top-to-bottom down the screen.

### Radial Rainbow
```bash
./dev.sh run --rainbow radial
```
Colors radiate outward from the center in concentric circles.

### Diagonal Rainbow
```bash
./dev.sh run --rainbow diagonal
```
Colors sweep diagonally across the screen.

### Wave Rainbow
```bash
./dev.sh run --rainbow wave
```
Animated wave pattern that moves through the rainbow spectrum.

### Time Rainbow
```bash
./dev.sh run --rainbow time
```
Entire screen cycles through rainbow colors over time.

---

## 🎨 Color Schemes

Preset color palettes for different moods:

### Default
```bash
./dev.sh run --scheme default
```
Classic white-on-black ASCII.

### Pale
```bash
./dev.sh run --scheme pale
```
Soft, desaturated pastel tones.

### Dark
```bash
./dev.sh run --scheme dark
```
Dark, moody colors with blue-gray tones.

### Neon
```bash
./dev.sh run --scheme neon
```
Bright, vibrant cyberpunk colors.

### Sunset
```bash
./dev.sh run --scheme sunset
```
Warm oranges, reds, and yellows.

### Ocean
```bash
./dev.sh run --scheme ocean
```
Cool blues and teals.

### Robot
```bash
./dev.sh run --scheme robot
```
Metallic grays and silver tones.

### Alien
```bash
./dev.sh run --scheme alien
```
Eerie greens and toxic colors.

### Ghost
```bash
./dev.sh run --scheme ghost
```
Pale blues and whites, ethereal.

### Monochrome
```bash
./dev.sh run --scheme monochrome
```
Pure black and white, high contrast. **Best for performance!**

---

## 🎪 Combined Effects

Mix characters, colors, and rainbows together:

### Neon Robot
```bash
./dev.sh run --character robot --scheme neon
```

### Cute with Radial Rainbow
```bash
./dev.sh run --character cute --rainbow radial
```

### Tall Ghost
```bash
./dev.sh run --character tall --scheme ghost
```

### Wide Ocean Wave
```bash
./dev.sh run --character wide --scheme ocean --rainbow wave
```

---

## 🎤 With Text-to-Speech

Add speaking to any visual style:

```bash
# Robot voice with neon colors
./dev.sh run --character robot --scheme neon --speak "I am a robot"

# Cute character with rainbow
./dev.sh run --character cute --rainbow radial --speak "Hello world!"

# Different voice
./dev.sh run --character tall --voice "en-GB-SoniaNeural" --speak "Greetings"
```

**Available voices:**
```bash
./dev.sh voices  # List all 47 English voices
```

---

## ⚡ Performance Optimization

### Adjust FPS
```bash
# Lower FPS for smoother performance
./dev.sh run --fps 8

# Very low for weak systems
./dev.sh run --fps 5
```

### Use Smaller Terminal
Simply make your terminal window smaller - fewer pixels = faster rendering!

### Best Performance Settings
```bash
# Monochrome, low FPS, simple character
./dev.sh run --scheme monochrome --fps 8 --character default
```

### Single Frame (No Animation)
```bash
# Just render one frame
./dev.sh run --static --character robot
```

---

## 🧪 Technical Details

### How Characters Work

Characters are defined by `HeadGeometry` parameters:

- **head_radii**: (x, y, z) ellipsoid dimensions
- **eye_separation**: Distance between eyes
- **eye_height**: Vertical position of eyes
- **eye_socket_radius**: Size of eye sockets
- **eyeball_radius**: Size of eyeballs
- **mouth_y**: Vertical position of mouth
- **smoothing factors**: Control liquid blending effect

See: `src/model/head.py:320` for all preset definitions.

### How Rainbow Modes Work

Rainbow effects use position or time to map colors:

- **Horizontal**: `color = f(x_position)`
- **Vertical**: `color = f(y_position)`
- **Radial**: `color = f(distance_from_center)`
- **Wave**: `color = f(x, y, time)` with sine waves
- **Time**: `color = f(time)` - whole screen cycles

See: `src/terminal/color.py` for rainbow implementations.

### SDF Smoothing

The "liquid" look comes from smooth boolean operations:

```python
# Sharp union (geometric)
result = min(shape1, shape2)

# Smooth union (liquid)
result = sdf_smooth_union(shape1, shape2, smoothness=0.1)
```

Higher smoothness = more liquid blending.
Lower smoothness = sharper, more geometric.

See: `src/renderer/sdf.py` for SDF operations.

---

## 🎬 Example Showcase

Try these for impressive demos:

### 1. Neon Robot Dance
```bash
./dev.sh run --character robot --scheme neon --rainbow wave
```

### 2. Cute Kawaii Rainbow
```bash
./dev.sh run --character cute --rainbow radial
```

### 3. Ghost Story
```bash
./dev.sh run --character tall --scheme ghost --speak "I am the ghost of ASCII past"
```

### 4. Ocean Waves
```bash
./dev.sh run --character round --scheme ocean --rainbow wave
```

### 5. Sunset Speech
```bash
./dev.sh run --character default --scheme sunset --speak "The sun sets beautifully in ASCII"
```

---

## 📋 Quick Command Reference

```bash
# Basic demo
./dev.sh run

# Character options
--character [default|round|tall|wide|robot|cute]

# Color scheme options
--scheme [default|pale|dark|neon|sunset|ocean|robot|alien|ghost|monochrome]

# Rainbow mode options
--rainbow [horizontal|vertical|radial|diagonal|wave|time]

# Performance options
--fps [number]        # Target frames per second (default: 15)
--static              # Render single frame only

# TTS options
--speak "text"        # Speak text with lip sync
--voice "voice-name"  # Choose voice (default: en-US-AriaNeural)

# List options
--list-voices         # Show all TTS voices
--list-schemes        # Show all color schemes
```

---

## 💡 Tips

1. **For demos**: Use rainbow effects and expressive characters
2. **For performance**: Use monochrome, low FPS, small terminal
3. **For coding**: Keep terminal reasonable size (80x40)
4. **For presentations**: Robot + neon is impressive!
5. **For fun**: Cute + radial rainbow is adorable

---

## 🐛 Troubleshooting

### Animation is slow
- Lower FPS: `--fps 8`
- Smaller terminal window
- Use monochrome: `--scheme monochrome`
- Try native Windows instead of WSL

### Colors not showing
- Check terminal supports color (most do)
- Try different color scheme
- Verify terminal is not in monochrome mode

### Character looks wrong
- Make terminal window bigger (minimum 60x30 recommended)
- Check terminal font (monospace required)
- Try `--static` to see single frame

---

🎉 **Have fun creating liquid ASCII art!**
