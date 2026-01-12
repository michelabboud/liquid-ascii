# Liquid ASCII - WebGL GPU Renderer

**Phase 2A: GPU-Accelerated Browser Version**

This is the WebGL 2.0 implementation of Liquid ASCII, providing GPU-accelerated raymarching for high-performance 3D character rendering directly in the browser.

## Features

- **GPU Acceleration**: Runs entirely on the GPU using WebGL 2.0 shaders
- **Cross-Platform**: Works on all modern browsers (Chrome, Firefox, Safari, Edge)
- **Universal GPU Support**: Compatible with AMD, Intel, and NVIDIA GPUs
- **60+ FPS Target**: Smooth real-time rendering at high frame rates
- **All Character Presets**: Full support for all 15+ character variations (robot, alien, baby, cyclops, monster, etc.)
- **Lighting Presets**: 8 dramatic lighting styles (default, dramatic, soft, metallic, noir, cartoon, etc.)
- **Cel-Shading**: Configurable toon-style rendering with 2-8 bands
- **Interactive Controls**: Real-time adjustment of all parameters
- **Auto-Rotation**: Animated camera for automatic character showcase

## Quick Start

### Running Locally

Since this uses ES6 modules, you need to serve the files through a local web server (browsers block module loading from `file://` URLs).

**Option 1: Python (Recommended)**

```bash
# From the webgl/ directory
python3 -m http.server 8000

# Then open: http://localhost:8000
```

**Option 2: Node.js**

```bash
# Install http-server globally (once)
npm install -g http-server

# From the webgl/ directory
http-server -p 8000

# Then open: http://localhost:8000
```

**Option 3: PHP**

```bash
# From the webgl/ directory
php -S localhost:8000

# Then open: http://localhost:8000
```

**Option 4: VS Code Live Server Extension**

1. Install "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

### Browser Requirements

- **WebGL 2.0 Support Required**
- Chrome 56+ (2017)
- Firefox 51+ (2017)
- Safari 15+ (2021)
- Edge 79+ (2020)

To check WebGL 2.0 support, visit: https://get.webgl.org/webgl2/

## Project Structure

```
webgl/
├── index.html              # Main HTML interface
├── shaders/
│   ├── vertex.glsl        # Vertex shader (fullscreen quad)
│   ├── fragment.glsl      # Fragment shader (raymarching + lighting)
│   └── sdf.glsl           # SDF primitive functions (standalone)
├── js/
│   ├── main.js            # WebGL renderer and main loop
│   ├── shader-loader.js   # Shader compilation utilities
│   └── characters.js      # Character geometry presets
└── README.md              # This file
```

## Architecture

### Rendering Pipeline

1. **Vertex Shader** (`vertex.glsl`): Generates fullscreen quad covering the entire canvas
2. **Fragment Shader** (`fragment.glsl`): Runs for every pixel, performs raymarching
3. **Raymarching Loop**: Each pixel casts a ray into the 3D scene
4. **SDF Evaluation**: Ray steps forward using signed distance field (sphere tracing)
5. **Surface Hit**: When ray hits surface, compute normal and lighting
6. **Phong Lighting**: Calculate ambient, diffuse, and specular components
7. **Cel-Shading** (optional): Posterize lighting to discrete bands
8. **Output**: Final pixel color

### Performance

- **GPU Parallelism**: All pixels rendered simultaneously on GPU
- **Optimized Raymarching**: 50 max steps per ray, early termination
- **Efficient SDF Composition**: Smooth boolean operations with configurable blend radius
- **Real-Time Updates**: Camera, lighting, and geometry changes applied instantly

**Expected Performance:**
- Desktop (AMD 780M / Intel Arc / RTX): **60-120 FPS** @ 800x600
- Laptop (Integrated GPU): **30-60 FPS** @ 800x600
- Mobile (Modern): **20-40 FPS** @ 640x480

## Controls

### Character Panel
- **Preset**: Choose from 15+ character variations
  - `default`, `round`, `tall`, `wide`, `cute`
  - `robot`, `alien`, `baby`, `cyclops`, `monster`
  - `fish`, `square`, `cat`, `dog`, `elder`, `skull`

### Camera Panel
- **Distance**: Camera distance from character (2.0 - 8.0)
- **FOV**: Field of view angle (20° - 90°)

### Lighting Panel
- **Preset**: Select lighting style
  - `default`: Balanced lighting
  - `dramatic`: High contrast, strong highlights
  - `soft`: Gentle, diffused lighting
  - `metallic`: Sharp highlights, reflective
  - `flat`: Minimal shadows, even lighting
  - `noir`: High contrast, film noir style
  - `cartoon`: Bright, playful lighting
  - `subsurface`: Skin-like translucent effect
- **Ambient**: Base brightness (0.0 - 1.0)
- **Diffuse**: Surface scattering (0.0 - 1.0)
- **Specular**: Highlight intensity (0.0 - 1.0)
- **Specular Power**: Highlight sharpness (2 - 128)

### Cel-Shading Panel
- **Enable Cel-Shading**: Toggle toon-style rendering
- **Bands**: Number of discrete lighting levels (2 - 8)

### Animation Panel
- **Auto-Rotate**: Enable automatic camera rotation
- **Speed**: Rotation speed multiplier (0.0 - 2.0)

### Actions
- **Reset All**: Restore default settings

## Technical Details

### SDF Composition

The head is composed from multiple SDF primitives using smooth boolean operations:

```glsl
head = ellipsoid(head_radii)
head = smooth_subtract(head, eye_sockets, smoothness)
head = smooth_union(head, eyeballs, smoothness)
head = smooth_subtract(head, mouth_cavity, smoothness)
head = smooth_union(head, nose, smoothness)
```

The `smoothness` parameter controls the "liquid" blending effect. Higher values = more organic, fluid transitions.

### Lighting Model

Phong shading with three components:

```glsl
ambient_light = ambient_intensity
diffuse_light = diffuse_intensity * max(0, dot(normal, light_dir))
specular_light = specular_intensity * pow(max(0, dot(reflect, view)), specular_power)

final_color = ambient + diffuse + specular
```

### Cel-Shading

Posterization is applied by quantizing the lighting intensity to discrete bands:

```glsl
if (cel_shading_enabled) {
    intensity = floor(intensity * bands) / bands;
}
```

## Troubleshooting

### "WebGL 2 not supported" Error
- Update your browser to the latest version
- Check GPU drivers are up to date
- Try a different browser (Chrome has best WebGL support)
- Verify WebGL 2.0 at: https://get.webgl.org/webgl2/

### Black Screen / Nothing Renders
- Open browser console (F12) and check for errors
- Verify all shader files are being loaded (check Network tab)
- Ensure you're running from a web server (not `file://`)
- Try reducing canvas size or lowering quality settings

### Low FPS / Performance Issues
- Reduce canvas resolution in `index.html` (width/height attributes)
- Disable cel-shading (adds overhead)
- Close other GPU-intensive applications
- Check GPU temperature (may be thermal throttling)

### Controls Not Working
- Check browser console for JavaScript errors
- Verify all JS files loaded correctly
- Try hard refresh (Ctrl+Shift+R / Cmd+Shift+R)

## Development

### Modifying Shaders

Edit shader files in `shaders/`:
- Changes take effect on page reload
- Check browser console for compilation errors
- Use `console.log()` in main.js to debug uniform values

### Adding New Characters

Edit `js/characters.js`:
1. Add new preset to `CHARACTER_PRESETS` object
2. Define geometry parameters (head_radii, eye_socket_radius, etc.)
3. Add option to HTML `<select id="character">` in `index.html`

### Adding Lighting Presets

Edit `js/main.js`:
1. Add new preset to `LIGHTING_PRESETS` object
2. Define ambient, diffuse, specular, and specularPower values
3. Add option to HTML `<select id="lighting">` in `index.html`

## Comparison: WebGL vs Python Terminal

| Feature | Python Terminal | WebGL Browser |
|---------|----------------|---------------|
| FPS | 2-5 FPS | 60-120 FPS |
| GPU Usage | CPU only | Full GPU |
| Resolution | 80x40 chars | 800x600+ pixels |
| Portability | Python required | Any modern browser |
| Platform | Desktop only | Desktop + Mobile |
| Installation | pip install | Just open URL |

## Next Steps (Phase 2B/2C)

- **Phase 2B**: PyOpenCL terminal version (GPU-accelerated ASCII for AMD/Intel/NVIDIA)
- **Phase 2C**: ModernGL desktop version (Native OpenGL for maximum performance)
- **Phase 3**: Advanced features (animations, lip sync, audio in browser)

## License

Part of the Liquid ASCII Art Animation project.
See main project README for full license information.
