/*
 * OpenCL Raymarching Kernel for ASCII Art Rendering
 *
 * GPU-accelerated raymarching with SDF evaluation for terminal output.
 * Compatible with AMD, Intel, and NVIDIA GPUs via OpenCL 1.2+
 */

/* ===== SDF Primitives ===== */

float sdf_sphere(float3 p, float3 center, float radius) {
    return length(p - center) - radius;
}

float sdf_ellipsoid(float3 p, float3 center, float3 radii) {
    float3 safe_radii = fmax(radii, (float3)(1e-10f, 1e-10f, 1e-10f));
    float3 q = (p - center) / safe_radii;

    float k0 = length(q);
    if (k0 < 1e-10f) return -fmin(fmin(safe_radii.x, safe_radii.y), safe_radii.z);

    float k1 = length(q / safe_radii);
    if (k1 < 1e-10f) return -fmin(fmin(safe_radii.x, safe_radii.y), safe_radii.z);

    return k0 * (k0 - 1.0f) / k1;
}

/* ===== Smooth Boolean Operations ===== */

float sdf_smooth_union(float d1, float d2, float k) {
    float h = clamp(0.5f + 0.5f * (d2 - d1) / k, 0.0f, 1.0f);
    return mix(d2, d1, h) - k * h * (1.0f - h);
}

float sdf_smooth_subtraction(float d1, float d2, float k) {
    float h = clamp(0.5f - 0.5f * (d2 + d1) / k, 0.0f, 1.0f);
    return mix(d2, -d1, h) + k * h * (1.0f - h);
}

/* ===== Scene SDF ===== */

float scene_sdf(
    float3 p,
    float3 head_radii,
    float eye_socket_radius,
    float eyeball_radius,
    float eye_separation,
    float eye_height,
    float eye_depth,
    float pupil_radius,
    float mouth_y,
    float mouth_openness,
    float mouth_width,
    float nose_length,
    float eye_socket_smooth,
    float eyeball_smooth,
    float mouth_smooth,
    float nose_smooth
) {
    // Main head (ellipsoid)
    float head = sdf_ellipsoid(p, (float3)(0.0f, 0.0f, 0.0f), head_radii);

    // Eye sockets (subtract from head)
    float eye_offset_x = eye_separation / 2.0f;
    float3 eye_pos_l = (float3)(-eye_offset_x, eye_height, eye_depth);
    float3 eye_pos_r = (float3)(eye_offset_x, eye_height, eye_depth);

    float eye_socket_l = sdf_sphere(p, eye_pos_l, eye_socket_radius);
    float eye_socket_r = sdf_sphere(p, eye_pos_r, eye_socket_radius);
    float eye_sockets = fmin(eye_socket_l, eye_socket_r);

    head = sdf_smooth_subtraction(eye_sockets, head, eye_socket_smooth);

    // Eyeballs (add to head)
    float eyeball_l = sdf_sphere(p, eye_pos_l, eyeball_radius);
    float eyeball_r = sdf_sphere(p, eye_pos_r, eyeball_radius);
    float eyeballs = fmin(eyeball_l, eyeball_r);

    head = sdf_smooth_union(head, eyeballs, eyeball_smooth);

    // Mouth (subtract from head)
    float mouth_height = mouth_openness;
    float3 mouth_radii = (float3)(mouth_width, mouth_height, 0.15f);
    float3 mouth_pos = (float3)(0.0f, mouth_y, 0.9f);
    float mouth = sdf_ellipsoid(p, mouth_pos, mouth_radii);

    head = sdf_smooth_subtraction(mouth, head, mouth_smooth);

    // Nose (add to head)
    float3 nose_pos = (float3)(0.0f, 0.0f, 1.0f);
    float3 nose_radii = (float3)(0.12f, 0.15f, nose_length);
    float nose = sdf_ellipsoid(p, nose_pos, nose_radii);

    head = sdf_smooth_union(head, nose, nose_smooth);

    return head;
}

/* ===== Normal Computation ===== */

float3 compute_normal(
    float3 p,
    float3 head_radii,
    float eye_socket_radius,
    float eyeball_radius,
    float eye_separation,
    float eye_height,
    float eye_depth,
    float pupil_radius,
    float mouth_y,
    float mouth_openness,
    float mouth_width,
    float nose_length,
    float eye_socket_smooth,
    float eyeball_smooth,
    float mouth_smooth,
    float nose_smooth
) {
    const float h = 0.001f;
    float3 n;

    n.x = scene_sdf((float3)(p.x + h, p.y, p.z), head_radii, eye_socket_radius, eyeball_radius,
                    eye_separation, eye_height, eye_depth, pupil_radius, mouth_y,
                    mouth_openness, mouth_width, nose_length, eye_socket_smooth,
                    eyeball_smooth, mouth_smooth, nose_smooth)
        - scene_sdf((float3)(p.x - h, p.y, p.z), head_radii, eye_socket_radius, eyeball_radius,
                    eye_separation, eye_height, eye_depth, pupil_radius, mouth_y,
                    mouth_openness, mouth_width, nose_length, eye_socket_smooth,
                    eyeball_smooth, mouth_smooth, nose_smooth);

    n.y = scene_sdf((float3)(p.x, p.y + h, p.z), head_radii, eye_socket_radius, eyeball_radius,
                    eye_separation, eye_height, eye_depth, pupil_radius, mouth_y,
                    mouth_openness, mouth_width, nose_length, eye_socket_smooth,
                    eyeball_smooth, mouth_smooth, nose_smooth)
        - scene_sdf((float3)(p.x, p.y - h, p.z), head_radii, eye_socket_radius, eyeball_radius,
                    eye_separation, eye_height, eye_depth, pupil_radius, mouth_y,
                    mouth_openness, mouth_width, nose_length, eye_socket_smooth,
                    eyeball_smooth, mouth_smooth, nose_smooth);

    n.z = scene_sdf((float3)(p.x, p.y, p.z + h), head_radii, eye_socket_radius, eyeball_radius,
                    eye_separation, eye_height, eye_depth, pupil_radius, mouth_y,
                    mouth_openness, mouth_width, nose_length, eye_socket_smooth,
                    eyeball_smooth, mouth_smooth, nose_smooth)
        - scene_sdf((float3)(p.x, p.y, p.z - h), head_radii, eye_socket_radius, eyeball_radius,
                    eye_separation, eye_height, eye_depth, pupil_radius, mouth_y,
                    mouth_openness, mouth_width, nose_length, eye_socket_smooth,
                    eyeball_smooth, mouth_smooth, nose_smooth);

    return normalize(n);
}

/* ===== Raymarching ===== */

typedef struct {
    bool hit;
    float3 position;
    float distance;
} RayHit;

RayHit raymarch(
    float3 origin,
    float3 direction,
    float3 head_radii,
    float eye_socket_radius,
    float eyeball_radius,
    float eye_separation,
    float eye_height,
    float eye_depth,
    float pupil_radius,
    float mouth_y,
    float mouth_openness,
    float mouth_width,
    float nose_length,
    float eye_socket_smooth,
    float eyeball_smooth,
    float mouth_smooth,
    float nose_smooth
) {
    const int MAX_STEPS = 50;
    const float MAX_DISTANCE = 100.0f;
    const float EPSILON = 0.001f;

    float t = 0.0f;

    for (int i = 0; i < MAX_STEPS; i++) {
        float3 p = origin + t * direction;
        float dist = scene_sdf(p, head_radii, eye_socket_radius, eyeball_radius,
                              eye_separation, eye_height, eye_depth, pupil_radius,
                              mouth_y, mouth_openness, mouth_width, nose_length,
                              eye_socket_smooth, eyeball_smooth, mouth_smooth, nose_smooth);

        if (dist < EPSILON) {
            RayHit hit;
            hit.hit = true;
            hit.position = p;
            hit.distance = t;
            return hit;
        }

        t += dist;

        if (t > MAX_DISTANCE) {
            break;
        }
    }

    RayHit miss;
    miss.hit = false;
    miss.position = (float3)(0.0f, 0.0f, 0.0f);
    miss.distance = t;
    return miss;
}

/* ===== Lighting ===== */

float compute_lighting(
    float3 position,
    float3 normal,
    float3 view_dir,
    float3 light_dir,
    float ambient,
    float diffuse,
    float specular,
    float specular_power,
    bool cel_shading,
    int cel_bands
) {
    // Ambient
    float intensity = ambient;

    // Diffuse
    float diff = fmax(0.0f, dot(normal, light_dir));
    intensity += diffuse * diff;

    // Specular
    float3 reflect_dir = reflect(-light_dir, normal);
    float spec = pow(fmax(0.0f, dot(reflect_dir, view_dir)), specular_power);
    intensity += specular * spec;

    // Cel-shading
    if (cel_shading && cel_bands > 1) {
        float bands_float = (float)cel_bands;
        intensity = floor(intensity * bands_float + 0.5f) / bands_float;
    }

    return clamp(intensity, 0.0f, 1.0f);
}

/* ===== Main Kernel ===== */

__kernel void render_frame(
    __global float *output,          // Output intensity buffer (width * height)
    int width,
    int height,
    float3 camera_pos,
    float3 camera_target,
    float camera_fov,
    // Character parameters
    float3 head_radii,
    float eye_socket_radius,
    float eyeball_radius,
    float eye_separation,
    float eye_height,
    float eye_depth,
    float pupil_radius,
    float mouth_y,
    float mouth_openness,
    float mouth_width,
    float nose_length,
    float eye_socket_smooth,
    float eyeball_smooth,
    float mouth_smooth,
    float nose_smooth,
    // Lighting parameters
    float3 light_dir,
    float ambient,
    float diffuse,
    float specular,
    float specular_power,
    int cel_shading,
    int cel_bands
) {
    int x = get_global_id(0);
    int y = get_global_id(1);

    if (x >= width || y >= height) {
        return;
    }

    // Calculate ray direction
    float aspect = (float)width / (float)height;
    float fov_scale = tan(camera_fov * 0.5f);

    // Normalized device coordinates
    float ndc_x = (2.0f * ((float)x + 0.5f) / (float)width - 1.0f) * aspect * fov_scale;
    float ndc_y = (1.0f - 2.0f * ((float)y + 0.5f) / (float)height) * fov_scale;

    // Camera basis vectors
    float3 forward = normalize(camera_target - camera_pos);
    float3 right = normalize(cross(forward, (float3)(0.0f, 1.0f, 0.0f)));
    float3 up = cross(right, forward);

    // Ray direction in world space
    float3 ray_dir = normalize(forward + ndc_x * right + ndc_y * up);

    // Raymarch
    RayHit hit = raymarch(
        camera_pos, ray_dir,
        head_radii, eye_socket_radius, eyeball_radius,
        eye_separation, eye_height, eye_depth, pupil_radius,
        mouth_y, mouth_openness, mouth_width, nose_length,
        eye_socket_smooth, eyeball_smooth, mouth_smooth, nose_smooth
    );

    float intensity = 0.0f;

    if (hit.hit) {
        // Compute normal
        float3 normal = compute_normal(
            hit.position,
            head_radii, eye_socket_radius, eyeball_radius,
            eye_separation, eye_height, eye_depth, pupil_radius,
            mouth_y, mouth_openness, mouth_width, nose_length,
            eye_socket_smooth, eyeball_smooth, mouth_smooth, nose_smooth
        );

        // Compute lighting
        float3 view_dir = normalize(camera_pos - hit.position);
        float3 normalized_light = normalize(light_dir);

        intensity = compute_lighting(
            hit.position, normal, view_dir, normalized_light,
            ambient, diffuse, specular, specular_power,
            cel_shading != 0, cel_bands
        );
    }

    // Write output
    int index = y * width + x;
    output[index] = intensity;
}
