/**
 * Shader Loading and Compilation Utilities
 */

/**
 * Load shader source from file
 * @param {string} url - Path to shader file
 * @returns {Promise<string>} Shader source code
 */
export async function loadShaderSource(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to load shader: ${url} (${response.status})`);
        }
        return await response.text();
    } catch (error) {
        console.error(`Error loading shader from ${url}:`, error);
        throw error;
    }
}

/**
 * Compile a shader
 * @param {WebGL2RenderingContext} gl - WebGL context
 * @param {number} type - Shader type (gl.VERTEX_SHADER or gl.FRAGMENT_SHADER)
 * @param {string} source - Shader source code
 * @returns {WebGLShader} Compiled shader
 */
export function compileShader(gl, type, source) {
    const shader = gl.createShader(type);
    if (!shader) {
        throw new Error('Failed to create shader');
    }

    gl.shaderSource(shader, source);
    gl.compileShader(shader);

    // Check compilation status
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        const info = gl.getShaderInfoLog(shader);
        gl.deleteShader(shader);
        throw new Error(`Shader compilation failed: ${info}`);
    }

    return shader;
}

/**
 * Link vertex and fragment shaders into a program
 * @param {WebGL2RenderingContext} gl - WebGL context
 * @param {WebGLShader} vertexShader - Compiled vertex shader
 * @param {WebGLShader} fragmentShader - Compiled fragment shader
 * @returns {WebGLProgram} Linked program
 */
export function linkProgram(gl, vertexShader, fragmentShader) {
    const program = gl.createProgram();
    if (!program) {
        throw new Error('Failed to create program');
    }

    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);

    // Check linking status
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        const info = gl.getProgramInfoLog(program);
        gl.deleteProgram(program);
        throw new Error(`Program linking failed: ${info}`);
    }

    return program;
}

/**
 * Load and compile a complete shader program
 * @param {WebGL2RenderingContext} gl - WebGL context
 * @param {string} vertexUrl - Path to vertex shader
 * @param {string} fragmentUrl - Path to fragment shader
 * @returns {Promise<WebGLProgram>} Compiled and linked program
 */
export async function loadShaderProgram(gl, vertexUrl, fragmentUrl) {
    console.log('Loading shaders...');

    // Load sources in parallel
    const [vertexSource, fragmentSource] = await Promise.all([
        loadShaderSource(vertexUrl),
        loadShaderSource(fragmentUrl)
    ]);

    console.log('Compiling shaders...');

    // Compile shaders
    const vertexShader = compileShader(gl, gl.VERTEX_SHADER, vertexSource);
    const fragmentShader = compileShader(gl, gl.FRAGMENT_SHADER, fragmentSource);

    console.log('Linking program...');

    // Link program
    const program = linkProgram(gl, vertexShader, fragmentShader);

    // Clean up - shaders can be deleted after linking
    gl.deleteShader(vertexShader);
    gl.deleteShader(fragmentShader);

    console.log('Shader program ready!');

    return program;
}

/**
 * Get all uniform locations from a program
 * @param {WebGL2RenderingContext} gl - WebGL context
 * @param {WebGLProgram} program - Shader program
 * @param {string[]} uniformNames - Array of uniform names to retrieve
 * @returns {Object} Map of uniform names to locations
 */
export function getUniformLocations(gl, program, uniformNames) {
    const locations = {};

    for (const name of uniformNames) {
        const location = gl.getUniformLocation(program, name);
        if (location === null) {
            console.warn(`Uniform '${name}' not found in shader program`);
        }
        locations[name] = location;
    }

    return locations;
}

/**
 * Get all attribute locations from a program
 * @param {WebGL2RenderingContext} gl - WebGL context
 * @param {WebGLProgram} program - Shader program
 * @param {string[]} attributeNames - Array of attribute names to retrieve
 * @returns {Object} Map of attribute names to locations
 */
export function getAttributeLocations(gl, program, attributeNames) {
    const locations = {};

    for (const name of attributeNames) {
        const location = gl.getAttribLocation(program, name);
        if (location === -1) {
            console.warn(`Attribute '${name}' not found in shader program`);
        }
        locations[name] = location;
    }

    return locations;
}
