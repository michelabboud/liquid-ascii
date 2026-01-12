# Liquid ASCII - Development Roadmap & TODO

## Current Status

**Performance**: 2 FPS → **Target**: 30 FPS (15x speedup required)
**Current Resolution**: 80×40 characters (~170K SDF evaluations/frame)
**Primary Bottleneck**: Pure Python raymarching loop

## Project Goals

1. **Performance**: Achieve 30+ FPS using GPU acceleration
2. **Visual Distinction**: Make characters immediately recognizable
3. **Multi-Platform**: Support terminal, browser, and desktop
4. **Public Release**: Work on AMD, Intel, NVIDIA GPUs (not CUDA-only)

---

## Phase 1: Character Differentiation (Weeks 1-2) ✅ COMPLETED

**Goal**: Make characters visually distinct at current 2 FPS

### ✅ Completed Tasks

1. **Wireframe/Edge Rendering Mode**
   - Pure edge rendering with `render_frame_wireframe()`
   - CLI: `--wireframe`, `--edge-char`, `--edge-threshold`, `--edge-thickness`
   - Edge thickness control with dilation algorithm
   - Integrated into all modes (demo, speak, tutor, chat)

2. **Extreme Character Geometry Variations**
   - Robot: Cube proportions, hard edges, wide-set eyes (mechanical)
   - Alien: 2x head height, 3x eye size, very high features
   - Baby: Perfect sphere, gigantic eyes, high features (kawaii)
   - Monster: Wide squat, huge mouth, bulbous nose
   - Cyclops: ONE GIANT centered eye
   - Fish: Deep head, eyes on sides, wide O-mouth
   - Square: Angular box with hard edges

3. **Dramatic Lighting Presets** (8 styles)
   - `default`: Balanced (ambient 0.1, diffuse 0.7, specular 0.2)
   - `dramatic`: High contrast, deep shadows, bright highlights
   - `soft`: Gentle with filled shadows
   - `metallic`: Sharp reflections (specular 0.9, power 64)
   - `flat`: Minimal shading
   - `noir`: Film noir stark contrast
   - `cartoon`: Clear light/dark separation
   - `subsurface`: Soft organic (skin-like)
   - CLI: `--lighting <preset>`, `--list-lighting`

4. **Cel-Shading/Toon Style**
   - Posterizes lighting to discrete bands (comic book look)
   - CLI: `--cel-shading`, `--cel-bands <2-8>`
   - Works with all lighting presets

**Deliverable**: ✅ Characters now have unique silhouettes and visual styles!

---

## Phase 2: GPU Acceleration (Weeks 3-9)

**Goal**: 30-60 FPS with GPU acceleration

### Option 2A: WebGL Browser Version (Weeks 3-6) ⭐ PRIMARY TARGET

**Why**: Universal (AMD/Intel/NVIDIA), no installation, 60+ FPS on all devices

#### Week 3-4: WebGL Setup

- [ ] Create HTML/WebGL project structure
  - [ ] `webgl/` directory with `index.html`, `shaders/`, `js/`
  - [ ] Set up build system (optional: webpack/vite)
  - [ ] Create WebGL 2.0 context
  - [ ] Initialize fullscreen quad for raymarching

- [ ] Port basic SDF functions to GLSL
  - [ ] `sdf_sphere()` - distance to sphere
  - [ ] `sdf_ellipsoid()` - distance to ellipsoid
  - [ ] `sdf_box()` - distance to box
  - [ ] Smooth boolean operations:
    - `smoothUnion(d1, d2, k)` - blend two shapes
    - `smoothSubtraction(d1, d2, k)` - carve out
    - `smoothIntersection(d1, d2, k)` - overlap
  - [ ] Test with simple sphere render

- [ ] Implement fragment shader raymarcher
  - [ ] Ray generation from UV coordinates
  - [ ] Camera system (position, target, FOV)
  - [ ] Sphere tracing loop (50 max steps)
  - [ ] Hit detection (distance < epsilon)
  - [ ] Early exit optimization

#### Week 5-6: WebGL Feature Complete

- [ ] Full head composition in GLSL
  - [ ] Translate `CharacterHead.evaluate_sdf()` to GLSL
  - [ ] All character presets as uniform parameters:
    - Default, robot, alien, baby, monster, cyclops, fish, square
  - [ ] Smooth SDF composition matching Python version

- [ ] Lighting system
  - [ ] Phong lighting model (ambient + diffuse + specular)
  - [ ] Normal computation via SDF gradient
  - [ ] All 8 lighting presets as uniform structs
  - [ ] Cel-shading posterization in shader

- [ ] ASCII rendering strategy (choose one):
  - [ ] **Option A**: Render to texture → JS converts to ASCII → `<pre>` tag
  - [ ] **Option B**: ASCII texture atlas → sample in fragment shader
  - [ ] **Option C**: Pure pixel rendering (skip ASCII conversion)

- [ ] Interactive UI
  - [ ] Character selector dropdown
  - [ ] Lighting preset buttons
  - [ ] Mouth openness slider (0-1)
  - [ ] Eye look X/Y sliders
  - [ ] Blink button
  - [ ] Expression selector
  - [ ] Color scheme picker
  - [ ] FPS counter display

- [ ] Animation system
  - [ ] Idle animation (breathing, subtle motion)
  - [ ] Blinking cycle
  - [ ] Smooth parameter interpolation

- [ ] Lip sync integration (optional)
  - [ ] Port viseme system to JavaScript
  - [ ] TTS integration (Web Speech API or external service)
  - [ ] Synchronize mouth animation with audio playback

**Deliverable**: Browser app running at 60+ FPS, works on mobile

**Deployment**: GitHub Pages at `https://yourusername.github.io/liquid-ascii/`

---

### Option 2B: PyOpenCL Terminal (Weeks 7-9) - SECONDARY TARGET

**Why**: Fast terminal version for power users, works on AMD 780M

#### Week 7: OpenCL Setup

- [ ] Add `pyopencl` dependency to `pyproject.toml`
- [ ] GPU detection and selection
  - [ ] List all OpenCL platforms/devices
  - [ ] Prefer GPU, fallback to CPU
  - [ ] CLI: `--list-gpus`, `--gpu <id>`
  - [ ] Test on AMD Radeon 780M (RDNA3, OpenCL 2.1)

- [ ] OpenCL "hello world" kernel
  - [ ] Simple vector addition test
  - [ ] Buffer creation and data transfer
  - [ ] Kernel compilation and execution
  - [ ] Verify on AMD GPU

#### Week 8: OpenCL Raymarching

- [ ] Port raymarching to OpenCL kernel
  - [ ] Each work-item processes one pixel
  - [ ] Inline SDF evaluation for performance
  - [ ] Pass geometry as kernel arguments (not function pointers)
  - [ ] Return hit distances and points

- [ ] Buffer management
  - [ ] Ray origins/directions: CPU → GPU transfer
  - [ ] Hit buffer, normal buffer: GPU → CPU transfer
  - [ ] Minimize memory copies

- [ ] Normal computation in OpenCL
  - [ ] Compute normals on GPU (6 SDF evals per hit pixel)
  - [ ] Return to CPU for shading

- [ ] Optimize for AMD RDNA3
  - [ ] Tune work-group sizes (e.g., 8×8, 16×16)
  - [ ] Local memory usage
  - [ ] Coalesced memory access

#### Week 9: Integration & Polish

- [ ] Integrate OpenCL renderer into main.py
  - [ ] New `OpenCLRaymarcher` class
  - [ ] Auto-detect GPU at runtime
  - [ ] Graceful fallback to CPU if no OpenCL

- [ ] CLI updates
  - [ ] `--renderer <cpu|opencl|auto>`
  - [ ] Display active renderer in status

- [ ] Benchmark and verify
  - [ ] Test on AMD 780M: expect 30-60 FPS
  - [ ] Compare vs CPU: expect 30-80x speedup
  - [ ] Memory usage profiling

**Deliverable**: Fast terminal version (30+ FPS with GPU, 2 FPS CPU fallback)

---

### Option 2C: ModernGL Desktop (Weeks 7-9) - ALTERNATIVE

**Why**: Native desktop app with GUI, works on AMD/Intel/NVIDIA

#### Week 7: Setup

- [ ] Add `moderngl`, `pygame` dependencies
- [ ] Create pygame window (800×600 default)
- [ ] Initialize ModernGL context (OpenGL 3.3+)
- [ ] Test compute shader compilation

#### Week 8: OpenGL Rendering

- [ ] Write GLSL compute shader for raymarching
- [ ] Set up Shader Storage Buffer Objects (SSBOs)
  - Ray origins/directions buffer
  - Hit buffer (distances, points, normals)
- [ ] Dispatch compute (80×40 work groups)
- [ ] Read back results

- [ ] ASCII conversion
  - [ ] CPU: Convert hit buffer to ASCII string
  - [ ] GPU: Compute shader for character selection (optional)

- [ ] Display in pygame
  - [ ] Render ASCII to pygame surface
  - [ ] Or: Render as texture in OpenGL

#### Week 9: Desktop UI

- [ ] Menu bar (File, Edit, View, Help)
- [ ] Control panel
  - Character selector
  - Lighting controls
  - Animation controls
  - Effects toggles

- [ ] Export features
  - [ ] Save screenshot (PNG)
  - [ ] Record to GIF
  - [ ] Record to MP4 (with ffmpeg)

**Deliverable**: Desktop app with 30-60 FPS, native look & feel

---

## Phase 3: Advanced Features (Weeks 10-13) - FUTURE

**Goal**: Polish and expand

### Rendering Enhancements

- [ ] Hybrid ASCII/pixel rendering
  - [ ] Smooth zoom transitions
  - [ ] Resolution-adaptive

- [ ] Additional visual styles
  - [ ] Hatching/cross-hatching
  - [ ] Outline-only (wireframe++)
  - [ ] Dithering patterns

### Performance

- [ ] Multi-backend auto-selection
  - WebGL → PyOpenCL → ModernGL → CPU
- [ ] Adaptive quality (maintain target FPS)
- [ ] Dynamic resolution scaling

### Export & Sharing

- [ ] Video export (MP4, GIF)
- [ ] Thumbnail generation
- [ ] Share custom characters (JSON)

### Character Editor

- [ ] Visual SDF composer
- [ ] Drag-and-drop primitives
- [ ] Real-time preview
- [ ] Save/load characters

---

## Documentation Tasks

### User Documentation

- [x] `GPU_ACCELERATION_PLAN.md` - Technical analysis ✅
- [ ] `README.md` - Update with Phase 1 features
  - [ ] Wireframe mode examples
  - [ ] Lighting presets showcase
  - [ ] Cel-shading demo
  - [ ] Character gallery

- [ ] `INSTALL.md` - GPU dependencies
  - [ ] PyOpenCL setup (AMD/Intel/NVIDIA)
  - [ ] ModernGL setup
  - [ ] Web deployment guide

- [ ] `EXAMPLES.md` - Visual showcase
  - [ ] Screenshots of each character
  - [ ] Wireframe vs shaded
  - [ ] Lighting comparisons
  - [ ] Cel-shading bands

### Developer Documentation

- [ ] `ARCHITECTURE.md` - System overview
  - [ ] Rendering pipeline diagram
  - [ ] GPU strategies
  - [ ] SDF patterns

- [ ] `CONTRIBUTING.md` - Feature guide
  - [ ] Adding characters
  - [ ] Adding lighting presets
  - [ ] Creating effects

---

## Testing Tasks

### Unit Tests

- [ ] Renderer tests
  - [ ] SDF primitives accuracy
  - [ ] Smooth operations
  - [ ] Lighting calculations
  - [ ] Cel-shading posterization

- [ ] Character tests
  - [ ] All presets load
  - [ ] Valid parameters
  - [ ] No NaN/inf

### GPU Backend Tests

- [ ] OpenCL kernel compilation
- [ ] ModernGL context creation
- [ ] WebGL shader compilation
- [ ] Fallback behavior

### Performance Benchmarks

- [ ] CPU baseline (2 FPS)
- [ ] OpenCL on AMD 780M (30-60 FPS target)
- [ ] WebGL on AMD 780M (60-120 FPS target)
- [ ] ModernGL on AMD 780M (30-60 FPS target)

---

## Deployment & Release

### Pre-Release Checklist

- [ ] All tests passing
- [ ] No warnings
- [ ] Code formatted (black)
- [ ] Type hints complete
- [ ] Docstrings complete

### Release Packages

#### Terminal Version (PyPI)

- [ ] Build for PyPI (`python -m build`)
- [ ] Upload to PyPI
- [ ] Version 0.4.0 release notes

#### Browser Version (GitHub Pages)

- [ ] Build production bundle
- [ ] Minify JavaScript/CSS
- [ ] Deploy to GitHub Pages
- [ ] Custom domain (optional)

#### Desktop App (GitHub Releases)

- [ ] Build executables (PyInstaller)
  - Windows .exe
  - macOS .app
  - Linux AppImage
- [ ] Create release packages

### Marketing

- [ ] Reddit (r/Python, r/programming)
- [ ] Hacker News
- [ ] Twitter/X
- [ ] YouTube demo video
- [ ] Dev.to article

---

## Priority Matrix

### P0: Critical (Now)

1. ✅ Phase 1: Character Differentiation - **COMPLETE**
2. ⏳ Phase 2A: WebGL Browser Version - **IN PROGRESS**

### P1: High

3. Phase 2B: PyOpenCL Terminal
4. Documentation updates
5. Testing suite

### P2: Medium

6. Phase 2C: ModernGL Desktop
7. Character editor
8. Video export

### P3: Low

9. Hybrid rendering
10. Advanced effects
11. Social features

---

## Success Metrics

### Performance

- ✅ Phase 1: Distinct at 2 FPS
- ⏳ Phase 2: 30+ FPS (terminal) or 60+ FPS (browser)
- ⏳ Phase 3: Consistent 60 FPS everywhere

### User Experience

- ✅ Characters immediately recognizable
- ⏳ Works on 95%+ devices
- ⏳ Graceful GPU fallback
- ⏳ Zero configuration

### Community

- ⏳ 1000+ GitHub stars
- ⏳ Hacker News front page
- ⏳ 10,000+ web demo visits

---

## Current Sprint: Week 3-4 (WebGL Setup)

### Active

- [ ] Create HTML/WebGL boilerplate
- [ ] Initialize WebGL context
- [ ] Port SDF functions to GLSL

### Next

- [ ] Fragment shader raymarcher
- [ ] Test with sphere

### Blocked

- None

---

## Hardware Context

**User GPU**: AMD Radeon 780M (RDNA3)
- OpenGL 4.6 ✅
- OpenCL 2.1 ✅
- Vulkan 1.3 ✅
- WebGL 2.0 ✅
- 12 RDNA3 compute units

**Expected Performance**:
- WebGL: 60-120 FPS at 80×40
- OpenCL: 30-60 FPS at 80×40
- CPU: 2 FPS (baseline)

---

## Design Decisions

- ✅ **WebGL First**: Widest reach, universal compatibility
- ✅ **No CUDA**: AMD GPU incompatible
- ✅ **PyOpenCL Second**: Cross-vendor (AMD/Intel/NVIDIA)
- ✅ **Progressive Enhancement**: CPU → OpenCL → WebGL

---

## Changelog

### 2026-01-12: Phase 1 Complete! 🎉

**Completed**:
- ✅ Wireframe/edge rendering
- ✅ 8 extreme character variations
- ✅ 8 dramatic lighting presets
- ✅ Cel-shading/toon style

**Stats**:
- 4 commits
- 600+ lines added
- 20+ new CLI flags
- Characters have unique silhouettes!

**Next**: Phase 2A - WebGL (Week 3-6)

---

## Resources

### Plans & Guides

- [GPU_ACCELERATION_PLAN.md](./GPU_ACCELERATION_PLAN.md) - Full technical plan
- [CLAUDE.md](./CLAUDE.md) - Project overview for AI
- [ANIMATION_GUIDE.md](./docs/ANIMATION_GUIDE.md) - Animation system

### Technical References

- [Inigo Quilez SDF Functions](https://iquilezles.org/articles/distfunctions/)
- [Ray Marching Guide (Jamie Wong)](https://jamie-wong.com/2016/07/15/ray-marching-signed-distance-functions/)
- [WebGL SDF Renderer Example](https://github.com/OscarSaharoy/SDF-Renderer)

### GPU Programming

- [PyOpenCL Docs](https://documen.tician.de/pyopencl/)
- [ModernGL Docs](https://moderngl.readthedocs.io/)
- [WebGL2 Spec](https://www.khronos.org/registry/webgl/specs/latest/2.0/)
- [GLSL Reference](https://www.khronos.org/files/opengles_shading_language.pdf)

### Tools

- **Dev**: `./dev.sh` (Linux/macOS) or `.\scripts\dev.ps1` (Windows)
- **Test**: `./dev.sh test`
- **Benchmark**: `python benchmarks/render_benchmark.py`
