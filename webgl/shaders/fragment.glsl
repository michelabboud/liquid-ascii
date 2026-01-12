#version 300 es
precision highp float;

// Fragment shader for SDF raymarching
// Renders 3D scenes using sphere tracing

in vec2 v_uv;
out vec4 fragColor;

// ===== Uniforms =====

// Camera
uniform vec3 u_camera_pos;
uniform vec3 u_camera_target;
uniform float u_camera_fov;

// Resolution
uniform vec2 u_resolution;

// Time
uniform float u_time;

// Character parameters
uniform vec3 u_head_radii;
uniform float u_eye_socket_radius;
uniform float u_eyeball_radius;
uniform float u_pupil_radius;
uniform float u_eye_separation;
uniform float u_eye_height;
uniform float u_eye_depth;
uniform float u_mouth_y;
uniform float u_mouth_openness;
uniform float u_mouth_width;
uniform float u_nose_length;

// Lighting
uniform vec3 u_light_dir;
uniform float u_ambient;
uniform float u_diffuse;
uniform float u_specular;
uniform float u_specular_power;

// Cel-shading
uniform bool u_cel_shading;
uniform int u_cel_bands;

// Smoothness parameters
uniform float u_eye_socket_smooth;
uniform float u_eyeball_smooth;
uniform float u_mouth_smooth;
uniform float u_nose_smooth;

// ===== Constants =====

const int MAX_STEPS = 50;
const float MAX_DISTANCE = 100.0;
const float EPSILON = 0.001;

// ===== SDF Functions =====
// (Inlined from sdf.glsl for performance)

float sdf_sphere(vec3 p, vec3 center, float radius) {
    return length(p - center) - radius;
}

float sdf_ellipsoid(vec3 p, vec3 center, vec3 radii) {
    vec3 safe_radii = max(radii, vec3(1e-10));
    vec3 q = (p - center) / safe_radii;

    float k0 = length(q);
    if (k0 < 1e-10) return -min(min(safe_radii.x, safe_radii.y), safe_radii.z);

    float k1 = length(q / safe_radii);
    if (k1 < 1e-10) return -min(min(safe_radii.x, safe_radii.y), safe_radii.z);

    return k0 * (k0 - 1.0) / k1;
}

float sdf_smooth_union(float d1, float d2, float k) {
    float h = clamp(0.5 + 0.5 * (d2 - d1) / k, 0.0, 1.0);
    return mix(d2, d1, h) - k * h * (1.0 - h);
}

float sdf_smooth_subtraction(float d1, float d2, float k) {
    float h = clamp(0.5 - 0.5 * (d2 + d1) / k, 0.0, 1.0);
    return mix(d2, -d1, h) + k * h * (1.0 - h);
}

// ===== Scene SDF =====

float scene_sdf(vec3 p) {
    // Main head (ellipsoid)
    float head = sdf_ellipsoid(p, vec3(0.0), u_head_radii);

    // Eye sockets (subtract from head)
    float eye_offset_x = u_eye_separation / 2.0;
    vec3 eye_pos_l = vec3(-eye_offset_x, u_eye_height, u_eye_depth);
    vec3 eye_pos_r = vec3(eye_offset_x, u_eye_height, u_eye_depth);

    float eye_socket_l = sdf_sphere(p, eye_pos_l, u_eye_socket_radius);
    float eye_socket_r = sdf_sphere(p, eye_pos_r, u_eye_socket_radius);

    head = sdf_smooth_subtraction(eye_socket_l, head, u_eye_socket_smooth);
    head = sdf_smooth_subtraction(eye_socket_r, head, u_eye_socket_smooth);

    // Eyeballs (add to head)
    vec3 eyeball_pos_l = eye_pos_l + vec3(0.0, 0.0, 0.1);
    vec3 eyeball_pos_r = eye_pos_r + vec3(0.0, 0.0, 0.1);

    float eyeball_l = sdf_sphere(p, eyeball_pos_l, u_eyeball_radius);
    float eyeball_r = sdf_sphere(p, eyeball_pos_r, u_eyeball_radius);

    head = sdf_smooth_union(eyeball_l, head, u_eyeball_smooth);
    head = sdf_smooth_union(eyeball_r, head, u_eyeball_smooth);

    // Mouth (subtract from head)
    vec3 mouth_center = vec3(0.0, u_mouth_y, 0.9);
    vec3 mouth_size = vec3(u_mouth_width * 0.25, u_mouth_openness * 0.08, 0.05);

    // Simple mouth as ellipsoid for now
    float mouth = sdf_ellipsoid(p, mouth_center, mouth_size);
    head = sdf_smooth_subtraction(mouth, head, u_mouth_smooth);

    // Nose (add to head)
    if (u_nose_length > 0.01) {
        vec3 nose_center = vec3(0.0, 0.0, 0.8 + u_nose_length * 0.5);
        vec3 nose_size = vec3(0.12, 0.12, u_nose_length * 0.5);
        float nose = sdf_ellipsoid(p, nose_center, nose_size);
        head = sdf_smooth_union(nose, head, u_nose_smooth);
    }

    return head;
}

// ===== Normal Computation =====

vec3 compute_normal(vec3 p) {
    vec2 e = vec2(EPSILON, 0.0);

    return normalize(vec3(
        scene_sdf(p + e.xyy) - scene_sdf(p - e.xyy),
        scene_sdf(p + e.yxy) - scene_sdf(p - e.yxy),
        scene_sdf(p + e.yyx) - scene_sdf(p - e.yyx)
    ));
}

// ===== Lighting =====

float posterize_intensity(float intensity, int bands) {
    int band = int(intensity * float(bands));
    band = clamp(band, 0, bands - 1);
    return (float(band) + 0.5) / float(bands);
}

float compute_lighting(vec3 normal, vec3 view_dir) {
    // Ambient
    float intensity = u_ambient;

    // Diffuse (Lambert)
    float n_dot_l = dot(normal, u_light_dir);
    if (n_dot_l > 0.0) {
        intensity += u_diffuse * n_dot_l;

        // Specular (Blinn-Phong)
        vec3 half_vec = normalize(u_light_dir + view_dir);
        float n_dot_h = max(0.0, dot(normal, half_vec));
        intensity += u_specular * pow(n_dot_h, u_specular_power);
    }

    // Clamp
    intensity = clamp(intensity, 0.0, 1.0);

    // Apply cel-shading if enabled
    if (u_cel_shading) {
        intensity = posterize_intensity(intensity, u_cel_bands);
    }

    return intensity;
}

// ===== Raymarching =====

struct RayHit {
    bool hit;
    vec3 position;
    float distance;
};

RayHit raymarch(vec3 origin, vec3 direction) {
    float t = 0.0;

    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 p = origin + t * direction;
        float dist = scene_sdf(p);

        if (dist < EPSILON) {
            // Hit!
            return RayHit(true, p, t);
        }

        t += dist;

        if (t > MAX_DISTANCE) {
            // Too far
            break;
        }
    }

    // Miss
    return RayHit(false, vec3(0.0), t);
}

// ===== Camera =====

struct Ray {
    vec3 origin;
    vec3 direction;
};

Ray get_ray(vec2 uv) {
    // Build camera basis
    vec3 forward = normalize(u_camera_target - u_camera_pos);
    vec3 right = normalize(cross(forward, vec3(0.0, 1.0, 0.0)));
    vec3 up = cross(right, forward);

    // Field of view
    float fov_radians = radians(u_camera_fov);
    float half_height = tan(fov_radians * 0.5);
    float half_width = half_height * (u_resolution.x / u_resolution.y);

    // Convert UV to NDC (-1 to 1)
    vec2 ndc = uv * 2.0 - 1.0;

    // Calculate ray direction
    vec3 direction = normalize(
        forward
        + right * ndc.x * half_width
        + up * ndc.y * half_height
    );

    return Ray(u_camera_pos, direction);
}

// ===== Main =====

void main() {
    // Get ray for this pixel
    Ray ray = get_ray(v_uv);

    // Raymarch
    RayHit hit = raymarch(ray.origin, ray.direction);

    if (hit.hit) {
        // Compute normal
        vec3 normal = compute_normal(hit.position);

        // Compute lighting
        vec3 view_dir = -ray.direction;
        float intensity = compute_lighting(normal, view_dir);

        // Grayscale output (for now)
        vec3 color = vec3(intensity);

        fragColor = vec4(color, 1.0);
    } else {
        // Background
        fragColor = vec4(0.1, 0.1, 0.15, 1.0);
    }
}
