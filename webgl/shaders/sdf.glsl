// SDF Library - Signed Distance Functions
// Based on Inigo Quilez's SDF functions
// Ported from Python implementation in src/renderer/sdf.py

// ===== Utility Functions =====

float length_vec3(vec3 v) {
    return sqrt(dot(v, v));
}

vec3 normalize_vec3(vec3 v) {
    float len = length_vec3(v);
    if (len < 1e-10) return vec3(0.0);
    return v / len;
}

// ===== SDF Primitives =====

// Sphere SDF
float sdf_sphere(vec3 p, vec3 center, float radius) {
    return length(p - center) - radius;
}

// Ellipsoid SDF
// Approximation that works well for reasonable aspect ratios
float sdf_ellipsoid(vec3 p, vec3 center, vec3 radii) {
    // Avoid division by zero
    vec3 safe_radii = max(radii, vec3(1e-10));

    // Transform to unit sphere space
    vec3 q = (p - center) / safe_radii;

    float k0 = length(q);
    if (k0 < 1e-10) return -min(min(safe_radii.x, safe_radii.y), safe_radii.z);

    float k1 = length(q / safe_radii);
    if (k1 < 1e-10) return -min(min(safe_radii.x, safe_radii.y), safe_radii.z);

    return k0 * (k0 - 1.0) / k1;
}

// Box SDF
float sdf_box(vec3 p, vec3 center, vec3 size) {
    vec3 q = abs(p - center) - size;
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0);
}

// Capsule SDF
float sdf_capsule(vec3 p, vec3 a, vec3 b, float radius) {
    vec3 pa = p - a;
    vec3 ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h) - radius;
}

// Torus SDF
float sdf_torus(vec3 p, vec3 center, float major_radius, float minor_radius) {
    vec3 q = p - center;
    vec2 t = vec2(length(q.xz) - major_radius, q.y);
    return length(t) - minor_radius;
}

// ===== Boolean Operations =====

// Union (minimum)
float sdf_union(float d1, float d2) {
    return min(d1, d2);
}

// Subtraction
float sdf_subtraction(float d1, float d2) {
    return max(-d1, d2);
}

// Intersection
float sdf_intersection(float d1, float d2) {
    return max(d1, d2);
}

// ===== Smooth Boolean Operations =====

// Smooth Union (polynomial blend)
float sdf_smooth_union(float d1, float d2, float k) {
    float h = clamp(0.5 + 0.5 * (d2 - d1) / k, 0.0, 1.0);
    return mix(d2, d1, h) - k * h * (1.0 - h);
}

// Smooth Subtraction
float sdf_smooth_subtraction(float d1, float d2, float k) {
    float h = clamp(0.5 - 0.5 * (d2 + d1) / k, 0.0, 1.0);
    return mix(d2, -d1, h) + k * h * (1.0 - h);
}

// Smooth Intersection
float sdf_smooth_intersection(float d1, float d2, float k) {
    float h = clamp(0.5 - 0.5 * (d2 - d1) / k, 0.0, 1.0);
    return mix(d2, d1, h) + k * h * (1.0 - h);
}

// ===== Normal Computation =====

// Compute surface normal using SDF gradient (central differences)
vec3 compute_normal(vec3 p, float epsilon) {
    // This will be overridden with the actual scene SDF
    // For now, just a placeholder structure
    vec2 e = vec2(epsilon, 0.0);

    // We'll need to sample the scene SDF at 6 points
    // This is done in the fragment shader where the scene SDF is defined
    return vec3(0.0, 0.0, 1.0); // Placeholder
}

// ===== Helper Functions =====

// Repeat space for infinite patterns (if needed)
vec3 repeat(vec3 p, vec3 spacing) {
    return mod(p + 0.5 * spacing, spacing) - 0.5 * spacing;
}

// Rotation matrices
mat2 rotate2D(float angle) {
    float s = sin(angle);
    float c = cos(angle);
    return mat2(c, -s, s, c);
}

vec3 rotate_x(vec3 p, float angle) {
    float s = sin(angle);
    float c = cos(angle);
    return vec3(p.x, c * p.y - s * p.z, s * p.y + c * p.z);
}

vec3 rotate_y(vec3 p, float angle) {
    float s = sin(angle);
    float c = cos(angle);
    return vec3(c * p.x + s * p.z, p.y, -s * p.x + c * p.z);
}

vec3 rotate_z(vec3 p, float angle) {
    float s = sin(angle);
    float c = cos(angle);
    return vec3(c * p.x - s * p.y, s * p.x + c * p.y, p.z);
}
