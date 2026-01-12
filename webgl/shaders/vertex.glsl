#version 300 es

// Simple vertex shader for fullscreen quad
// Passes UV coordinates to fragment shader

in vec2 a_position;
out vec2 v_uv;

void main() {
    // Pass UV coordinates (0 to 1)
    v_uv = a_position * 0.5 + 0.5;

    // Output position in clip space
    gl_Position = vec4(a_position, 0.0, 1.0);
}
