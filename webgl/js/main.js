/**
 * Main WebGL Renderer
 *
 * Sets up WebGL context, loads shaders, and manages the render loop
 * for GPU-accelerated raymarched character rendering.
 */

import { loadShaderProgram, getUniformLocations, getAttributeLocations } from './shader-loader.js';
import { getCharacterGeometry } from './characters.js';
import { AnimationController, AnimationPresets } from './animations.js';

/**
 * Lighting presets matching src/renderer/shading.py
 */
const LIGHTING_PRESETS = {
    default: { ambient: 0.10, diffuse: 0.70, specular: 0.20, specularPower: 16.0 },
    dramatic: { ambient: 0.05, diffuse: 0.85, specular: 0.60, specularPower: 32.0 },
    soft: { ambient: 0.20, diffuse: 0.60, specular: 0.10, specularPower: 8.0 },
    metallic: { ambient: 0.08, diffuse: 0.50, specular: 0.90, specularPower: 64.0 },
    flat: { ambient: 0.50, diffuse: 0.40, specular: 0.05, specularPower: 4.0 },
    noir: { ambient: 0.02, diffuse: 0.90, specular: 0.80, specularPower: 48.0 },
    cartoon: { ambient: 0.30, diffuse: 0.60, specular: 0.10, specularPower: 8.0 },
    subsurface: { ambient: 0.15, diffuse: 0.75, specular: 0.15, specularPower: 12.0 },
};

/**
 * Main renderer class
 */
class LiquidASCIIRenderer {
    constructor(canvas) {
        this.canvas = canvas;
        this.gl = null;
        this.program = null;
        this.uniforms = {};
        this.attributes = {};
        this.vao = null;
        this.quadBuffer = null;

        // Animation state
        this.time = 0;
        this.lastFrameTime = 0;
        this.frameCount = 0;
        this.fps = 0;

        // Camera state
        this.cameraDistance = 3.5;
        this.cameraFOV = 45.0;
        this.autoRotate = true;
        this.rotationSpeed = 0.5;
        this.cameraAngle = 0;

        // Character state
        this.currentCharacter = 'default';
        this.characterGeometry = getCharacterGeometry('default');

        // Lighting state
        this.lighting = { ...LIGHTING_PRESETS.default };

        // Cel-shading state
        this.celShading = false;
        this.celBands = 3;

        // Animation controller
        this.animationController = new AnimationController();
        this.animationsEnabled = true;
    }

    /**
     * Initialize WebGL context and resources
     */
    async init() {
        console.log('Initializing WebGL renderer...');

        // Get WebGL2 context
        this.gl = this.canvas.getContext('webgl2', {
            alpha: false,
            antialias: true,
            depth: false,
            premultipliedAlpha: false,
        });

        if (!this.gl) {
            throw new Error('WebGL 2 not supported');
        }

        const gl = this.gl;

        console.log('WebGL 2 context created');
        console.log('Renderer:', gl.getParameter(gl.RENDERER));
        console.log('Vendor:', gl.getParameter(gl.VENDOR));

        // Load and compile shaders
        this.program = await loadShaderProgram(
            gl,
            'shaders/vertex.glsl',
            'shaders/fragment.glsl'
        );

        // Get attribute and uniform locations
        this.attributes = getAttributeLocations(gl, this.program, ['a_position']);

        this.uniforms = getUniformLocations(gl, this.program, [
            // Time
            'u_time',
            // Resolution
            'u_resolution',
            // Camera
            'u_camera_pos',
            'u_camera_target',
            'u_camera_fov',
            // Character geometry
            'u_head_radii',
            'u_eye_socket_radius',
            'u_eyeball_radius',
            'u_eye_separation',
            'u_eye_height',
            'u_eye_depth',
            'u_pupil_radius',
            'u_mouth_y',
            'u_mouth_openness',
            'u_mouth_width',
            'u_nose_length',
            'u_eye_socket_smooth',
            'u_eyeball_smooth',
            'u_mouth_smooth',
            'u_nose_smooth',
            // Lighting
            'u_light_dir',
            'u_ambient',
            'u_diffuse',
            'u_specular',
            'u_specular_power',
            // Cel-shading
            'u_cel_shading',
            'u_cel_bands',
        ]);

        // Create fullscreen quad
        this.createQuad();

        console.log('WebGL initialization complete!');
    }

    /**
     * Create fullscreen quad geometry
     */
    createQuad() {
        const gl = this.gl;

        // Fullscreen triangle strip (2 triangles = 4 vertices)
        const positions = new Float32Array([
            -1.0, -1.0,  // Bottom-left
             1.0, -1.0,  // Bottom-right
            -1.0,  1.0,  // Top-left
             1.0,  1.0,  // Top-right
        ]);

        // Create and bind VAO
        this.vao = gl.createVertexArray();
        gl.bindVertexArray(this.vao);

        // Create and populate position buffer
        this.quadBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, this.quadBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);

        // Set up position attribute
        gl.enableVertexAttribArray(this.attributes.a_position);
        gl.vertexAttribPointer(
            this.attributes.a_position,
            2,          // 2 components per vertex (x, y)
            gl.FLOAT,   // data type
            false,      // don't normalize
            0,          // stride
            0           // offset
        );

        // Unbind
        gl.bindVertexArray(null);
        gl.bindBuffer(gl.ARRAY_BUFFER, null);
    }

    /**
     * Update character geometry
     * @param {string} characterName - Character preset name
     */
    setCharacter(characterName) {
        this.currentCharacter = characterName;
        this.characterGeometry = getCharacterGeometry(characterName);
    }

    /**
     * Update lighting preset
     * @param {string} presetName - Lighting preset name
     */
    setLightingPreset(presetName) {
        const preset = LIGHTING_PRESETS[presetName];
        if (preset) {
            this.lighting = { ...preset };
        }
    }

    /**
     * Update all shader uniforms
     */
    updateUniforms() {
        const gl = this.gl;
        const u = this.uniforms;
        const geom = this.characterGeometry;

        // Time
        if (u.u_time) gl.uniform1f(u.u_time, this.time);

        // Resolution
        if (u.u_resolution) {
            gl.uniform2f(u.u_resolution, this.canvas.width, this.canvas.height);
        }

        // Camera
        if (this.autoRotate) {
            this.cameraAngle = this.time * this.rotationSpeed * 0.3;
        }

        const camX = Math.sin(this.cameraAngle) * this.cameraDistance;
        const camZ = Math.cos(this.cameraAngle) * this.cameraDistance;

        // Apply breathing animation to camera Y
        const breathingOffset = this.animationsEnabled ? this.animationController.getBreathingOffset() : 0;
        const camY = 0.3 + breathingOffset;

        if (u.u_camera_pos) gl.uniform3f(u.u_camera_pos, camX, camY, camZ);
        if (u.u_camera_target) gl.uniform3f(u.u_camera_target, 0.0, 0.0, 0.0);
        if (u.u_camera_fov) gl.uniform1f(u.u_camera_fov, this.cameraFOV * Math.PI / 180.0);

        // Character geometry
        if (u.u_head_radii) gl.uniform3fv(u.u_head_radii, geom.head_radii);
        if (u.u_eye_socket_radius) gl.uniform1f(u.u_eye_socket_radius, geom.eye_socket_radius);
        if (u.u_eyeball_radius) gl.uniform1f(u.u_eyeball_radius, geom.eyeball_radius);
        if (u.u_eye_separation) gl.uniform1f(u.u_eye_separation, geom.eye_separation);
        if (u.u_eye_height) gl.uniform1f(u.u_eye_height, geom.eye_height);
        if (u.u_eye_depth) gl.uniform1f(u.u_eye_depth, geom.eye_depth);
        if (u.u_pupil_radius) gl.uniform1f(u.u_pupil_radius, geom.pupil_radius);
        // Apply idle mouth animation
        const idleMouthMovement = this.animationsEnabled ? this.animationController.getMouthIdleMovement() : 0;
        const mouthOpenness = geom.mouth_openness + idleMouthMovement;

        if (u.u_mouth_y) gl.uniform1f(u.u_mouth_y, geom.mouth_y);
        if (u.u_mouth_openness) gl.uniform1f(u.u_mouth_openness, mouthOpenness);
        if (u.u_mouth_width) gl.uniform1f(u.u_mouth_width, geom.mouth_width);
        if (u.u_nose_length) gl.uniform1f(u.u_nose_length, geom.nose_length);
        if (u.u_eye_socket_smooth) gl.uniform1f(u.u_eye_socket_smooth, geom.eye_socket_smooth);
        if (u.u_eyeball_smooth) gl.uniform1f(u.u_eyeball_smooth, geom.eyeball_smooth);
        if (u.u_mouth_smooth) gl.uniform1f(u.u_mouth_smooth, geom.mouth_smooth);
        if (u.u_nose_smooth) gl.uniform1f(u.u_nose_smooth, geom.nose_smooth);

        // Lighting (light from top-left-front)
        if (u.u_light_dir) gl.uniform3f(u.u_light_dir, -0.5, 0.8, 1.0);
        if (u.u_ambient) gl.uniform1f(u.u_ambient, this.lighting.ambient);
        if (u.u_diffuse) gl.uniform1f(u.u_diffuse, this.lighting.diffuse);
        if (u.u_specular) gl.uniform1f(u.u_specular, this.lighting.specular);
        if (u.u_specular_power) gl.uniform1f(u.u_specular_power, this.lighting.specularPower);

        // Cel-shading
        if (u.u_cel_shading) gl.uniform1i(u.u_cel_shading, this.celShading ? 1 : 0);
        if (u.u_cel_bands) gl.uniform1i(u.u_cel_bands, this.celBands);
    }

    /**
     * Render a single frame
     */
    render(currentTime) {
        const gl = this.gl;

        // Calculate delta time
        const deltaTime = currentTime - this.lastFrameTime;
        this.lastFrameTime = currentTime;
        this.time = currentTime * 0.001; // Convert to seconds

        // Update FPS counter
        this.frameCount++;
        if (this.frameCount % 30 === 0) {
            this.fps = Math.round(1000 / deltaTime);
        }

        // Update animations
        if (this.animationsEnabled) {
            this.animationController.update(deltaTime / 1000); // Convert ms to seconds
        }

        // Clear canvas
        gl.clearColor(0.0, 0.0, 0.0, 1.0);
        gl.clear(gl.COLOR_BUFFER_BIT);

        // Use shader program
        gl.useProgram(this.program);

        // Update uniforms
        this.updateUniforms();

        // Bind VAO and draw
        gl.bindVertexArray(this.vao);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        gl.bindVertexArray(null);
    }

    /**
     * Handle canvas resize
     */
    resize() {
        const displayWidth = this.canvas.clientWidth;
        const displayHeight = this.canvas.clientHeight;

        if (this.canvas.width !== displayWidth || this.canvas.height !== displayHeight) {
            this.canvas.width = displayWidth;
            this.canvas.height = displayHeight;
            this.gl.viewport(0, 0, displayWidth, displayHeight);
        }
    }

    /**
     * Get current FPS
     */
    getFPS() {
        return this.fps;
    }
}

/**
 * UI Controller
 */
class UIController {
    constructor(renderer) {
        this.renderer = renderer;
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Character selection
        document.getElementById('character').addEventListener('change', (e) => {
            this.renderer.setCharacter(e.target.value);
        });

        // Camera controls
        this.setupSlider('cameraDistance', (val) => {
            this.renderer.cameraDistance = val;
        });

        this.setupSlider('cameraFOV', (val) => {
            this.renderer.cameraFOV = val;
        });

        // Lighting preset
        document.getElementById('lighting').addEventListener('change', (e) => {
            this.renderer.setLightingPreset(e.target.value);
            this.updateLightingSliders();
        });

        // Lighting controls
        this.setupSlider('ambient', (val) => {
            this.renderer.lighting.ambient = val;
        });

        this.setupSlider('diffuse', (val) => {
            this.renderer.lighting.diffuse = val;
        });

        this.setupSlider('specular', (val) => {
            this.renderer.lighting.specular = val;
        });

        this.setupSlider('specularPower', (val) => {
            this.renderer.lighting.specularPower = val;
        });

        // Cel-shading
        document.getElementById('celShading').addEventListener('change', (e) => {
            this.renderer.celShading = e.target.checked;
        });

        this.setupSlider('celBands', (val) => {
            this.renderer.celBands = Math.round(val);
        });

        // Animation controls
        document.getElementById('idleAnimations').addEventListener('change', (e) => {
            this.renderer.animationsEnabled = e.target.checked;
            this.renderer.animationController.setEnabled(e.target.checked);
        });

        document.getElementById('autoRotate').addEventListener('change', (e) => {
            this.renderer.autoRotate = e.target.checked;
        });

        this.setupSlider('rotationSpeed', (val) => {
            this.renderer.rotationSpeed = val;
        });

        // Reset button
        document.getElementById('resetButton').addEventListener('click', () => {
            this.resetAll();
        });
    }

    setupSlider(id, callback) {
        const slider = document.getElementById(id);
        const valueDisplay = document.getElementById(id + 'Value');

        slider.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            callback(value);

            // Update display
            if (valueDisplay) {
                if (id === 'cameraFOV') {
                    valueDisplay.textContent = `${Math.round(value)}°`;
                } else if (id.includes('Power') || id === 'celBands') {
                    valueDisplay.textContent = Math.round(value).toString();
                } else {
                    valueDisplay.textContent = value.toFixed(2);
                }
            }
        });
    }

    updateLightingSliders() {
        const lighting = this.renderer.lighting;

        this.setSliderValue('ambient', lighting.ambient);
        this.setSliderValue('diffuse', lighting.diffuse);
        this.setSliderValue('specular', lighting.specular);
        this.setSliderValue('specularPower', lighting.specularPower);
    }

    setSliderValue(id, value) {
        const slider = document.getElementById(id);
        const valueDisplay = document.getElementById(id + 'Value');

        if (slider) {
            slider.value = value;
        }

        if (valueDisplay) {
            if (id === 'cameraFOV') {
                valueDisplay.textContent = `${Math.round(value)}°`;
            } else if (id.includes('Power') || id === 'celBands') {
                valueDisplay.textContent = Math.round(value).toString();
            } else {
                valueDisplay.textContent = value.toFixed(2);
            }
        }
    }

    resetAll() {
        // Reset to defaults
        document.getElementById('character').value = 'default';
        this.renderer.setCharacter('default');

        this.setSliderValue('cameraDistance', 3.5);
        this.renderer.cameraDistance = 3.5;

        this.setSliderValue('cameraFOV', 45);
        this.renderer.cameraFOV = 45;

        document.getElementById('lighting').value = 'default';
        this.renderer.setLightingPreset('default');
        this.updateLightingSliders();

        document.getElementById('celShading').checked = false;
        this.renderer.celShading = false;

        this.setSliderValue('celBands', 3);
        this.renderer.celBands = 3;

        document.getElementById('idleAnimations').checked = true;
        this.renderer.animationsEnabled = true;
        this.renderer.animationController.setEnabled(true);
        this.renderer.animationController.reset();

        document.getElementById('autoRotate').checked = true;
        this.renderer.autoRotate = true;

        this.setSliderValue('rotationSpeed', 0.5);
        this.renderer.rotationSpeed = 0.5;

        this.renderer.cameraAngle = 0;
    }
}

/**
 * Main application entry point
 */
async function main() {
    try {
        console.log('Starting Liquid ASCII WebGL Renderer...');

        // Get canvas
        const canvas = document.getElementById('glCanvas');
        if (!canvas) {
            throw new Error('Canvas element not found');
        }

        // Create renderer
        const renderer = new LiquidASCIIRenderer(canvas);

        // Initialize WebGL
        await renderer.init();

        // Set up UI controls
        const ui = new UIController(renderer);

        // FPS display
        const fpsElement = document.getElementById('fps');

        // Main render loop
        function renderLoop(currentTime) {
            // Handle resize
            renderer.resize();

            // Render frame
            renderer.render(currentTime);

            // Update FPS display
            if (fpsElement) {
                fpsElement.textContent = `FPS: ${renderer.getFPS()}`;
            }

            // Continue loop
            requestAnimationFrame(renderLoop);
        }

        // Start render loop
        requestAnimationFrame(renderLoop);

        console.log('Renderer started successfully!');

    } catch (error) {
        console.error('Failed to start renderer:', error);
        alert(`Failed to initialize WebGL renderer:\n\n${error.message}\n\nPlease check the browser console for details.`);
    }
}

// Start when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', main);
} else {
    main();
}
