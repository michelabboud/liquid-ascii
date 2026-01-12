/**
 * Character Presets
 *
 * Geometry definitions for all character variations.
 * Ported from src/model/head.py
 */

/**
 * Default head geometry parameters
 */
const DEFAULT_GEOMETRY = {
    // Main head
    head_radii: [1.0, 1.3, 1.0],

    // Eyes
    eye_socket_radius: 0.18,
    eyeball_radius: 0.12,
    eye_separation: 0.35,
    eye_height: 0.25,
    eye_depth: 0.85,
    pupil_radius: 0.06,

    // Mouth
    mouth_y: -0.35,
    mouth_openness: 0.05,
    mouth_width: 0.25,

    // Nose
    nose_length: 0.15,

    // Smoothing factors
    eye_socket_smooth: 0.1,
    eyeball_smooth: 0.05,
    mouth_smooth: 0.12,
    nose_smooth: 0.08,
};

/**
 * Character geometry presets
 */
export const CHARACTER_PRESETS = {
    default: { ...DEFAULT_GEOMETRY },

    round: {
        ...DEFAULT_GEOMETRY,
        head_radii: [1.1, 1.1, 1.0],
        eye_separation: 0.30,
        eye_height: 0.20,
    },

    tall: {
        ...DEFAULT_GEOMETRY,
        head_radii: [0.9, 1.5, 0.9],
        eye_separation: 0.30,
        eye_height: 0.35,
        mouth_y: -0.45,
    },

    wide: {
        ...DEFAULT_GEOMETRY,
        head_radii: [1.2, 1.1, 0.9],
        eye_separation: 0.45,
        eye_height: 0.20,
    },

    robot: {
        ...DEFAULT_GEOMETRY,
        head_radii: [1.0, 1.0, 1.0],  // Perfect cube-like proportions
        eye_socket_radius: 0.20,  // Rectangular "visor" eyes
        eyeball_radius: 0.18,  // Glowing eyes (almost fill socket)
        eye_separation: 0.50,  // Very wide-set, mechanical look
        eye_height: 0.20,  // Eyes at precise mid-point
        mouth_y: -0.40,
        mouth_width: 0.35,  // Wide speaker grille
        nose_length: 0.02,  // Minimal nose (antenna)
        eye_socket_smooth: 0.01,  // Hard edges (mechanical)
        mouth_smooth: 0.01,  // Hard edges (mechanical)
        nose_smooth: 0.01,
        eyeball_smooth: 0.02,
    },

    cute: {
        ...DEFAULT_GEOMETRY,
        head_radii: [1.1, 1.0, 1.0],
        eye_socket_radius: 0.25,
        eyeball_radius: 0.18,
        eye_separation: 0.30,
        eye_height: 0.15,
        mouth_y: -0.25,
    },

    alien: {
        ...DEFAULT_GEOMETRY,
        head_radii: [0.6, 2.0, 0.7],  // VERY elongated head (2x height!)
        eye_socket_radius: 0.45,  // MASSIVE almond eyes (3x normal)
        eyeball_radius: 0.38,  // Almost fills the socket
        pupil_radius: 0.12,  // Larger pupil for more alien look
        eye_separation: 0.50,  // Very wide set (side of head)
        eye_height: 0.40,  // High on the head
        eye_depth: 0.80,  // Slightly recessed
        mouth_y: -0.70,  // Very low, tiny mouth
        mouth_width: 0.15,  // Narrow
        nose_length: 0.02,  // Almost no nose
        eye_socket_smooth: 0.18,  // Very smooth, organic
    },

    cat: {
        ...DEFAULT_GEOMETRY,
        head_radii: [1.0, 1.1, 1.0],
        eye_socket_radius: 0.20,
        eyeball_radius: 0.12,  // Slit pupils (smaller eyeballs)
        eye_separation: 0.35,
        eye_height: 0.20,
        mouth_y: -0.20,
        nose_length: 0.08,  // Triangular nose
    },

    dog: {
        ...DEFAULT_GEOMETRY,
        head_radii: [1.1, 1.2, 1.1],  // Slightly extended
        eye_socket_radius: 0.22,
        eyeball_radius: 0.14,
        eye_separation: 0.38,
        eye_height: 0.25,
        mouth_y: -0.30,
        nose_length: 0.15,  // Extended snout
    },

    baby: {
        ...DEFAULT_GEOMETRY,
        head_radii: [1.3, 1.3, 1.3],  // Perfect sphere! (baby head)
        eye_socket_radius: 0.35,  // GIGANTIC eyes (kawaii!)
        eyeball_radius: 0.28,  // Huge adorable eyes
        pupil_radius: 0.08,  // Big pupils
        eye_separation: 0.28,  // Close together (cute)
        eye_height: 0.40,  // Very high on head (baby proportions)
        eye_depth: 0.90,  // Protruding eyes
        mouth_y: -0.10,  // Very high mouth (baby face)
        mouth_width: 0.12,  // Small
        nose_length: 0.05,  // Button nose
        eye_socket_smooth: 0.15,  // Soft, baby-like
        mouth_smooth: 0.15,
        nose_smooth: 0.12,
    },

    elder: {
        ...DEFAULT_GEOMETRY,
        head_radii: [0.9, 1.4, 0.9],  // Thinner face
        eye_socket_radius: 0.18,  // Smaller eyes
        eyeball_radius: 0.10,
        eye_separation: 0.35,
        eye_height: 0.20,  // Eyes lower
        mouth_y: -0.35,  // Mouth droops
        nose_length: 0.20,  // Prominent nose
    },

    skull: {
        ...DEFAULT_GEOMETRY,
        head_radii: [1.0, 1.3, 0.9],
        eye_socket_radius: 0.30,  // Large eye sockets
        eyeball_radius: 0.01,  // No visible eyeballs
        eye_separation: 0.35,
        eye_height: 0.25,
        mouth_y: -0.30,
        nose_length: 0.10,
        eye_socket_smooth: 0.08,
        mouth_smooth: 0.05,
    },

    monster: {
        ...DEFAULT_GEOMETRY,
        head_radii: [1.3, 1.0, 1.2],  // Wide, squat head
        eye_socket_radius: 0.22,
        eyeball_radius: 0.16,
        pupil_radius: 0.04,  // Tiny pupils (creepy)
        eye_separation: 0.55,  // Eyes on sides of head
        eye_height: 0.15,  // Low-set eyes
        eye_depth: 0.75,  // Eyes stick out
        mouth_y: -0.40,
        mouth_width: 0.40,  // Very wide
        nose_length: 0.18,  // Large nose
        eye_socket_smooth: 0.08,
        mouth_smooth: 0.10,  // Toothy grin
    },

    cyclops: {
        ...DEFAULT_GEOMETRY,
        head_radii: [1.1, 1.2, 1.0],  // Normal-ish head
        eye_socket_radius: 0.40,  // ONE GIANT EYE
        eyeball_radius: 0.35,  // Massive single eyeball
        pupil_radius: 0.10,  // Large pupil
        eye_separation: 0.0,  // ZERO separation = one eye!
        eye_height: 0.25,  // Centered eye
        eye_depth: 0.90,  // Bulging eye
        mouth_y: -0.40,
        mouth_width: 0.25,
        nose_length: 0.12,  // Normal nose below eye
        eye_socket_smooth: 0.12,
    },

    fish: {
        ...DEFAULT_GEOMETRY,
        head_radii: [0.8, 1.0, 1.3],  // Deep from front-to-back
        eye_socket_radius: 0.18,
        eyeball_radius: 0.14,
        pupil_radius: 0.06,
        eye_separation: 0.60,  // Eyes on SIDES (fish)
        eye_height: 0.30,  // Mid-height
        eye_depth: 0.60,  // Eyes stick out to sides
        mouth_y: -0.25,
        mouth_width: 0.40,  // Very wide "O" mouth
        nose_length: 0.05,  // Minimal nose
        eye_socket_smooth: 0.08,
        mouth_smooth: 0.18,  // Smooth fish mouth
    },

    square: {
        ...DEFAULT_GEOMETRY,
        head_radii: [1.0, 1.0, 1.0],  // Box head
        eye_socket_radius: 0.15,
        eyeball_radius: 0.12,
        pupil_radius: 0.04,
        eye_separation: 0.40,
        eye_height: 0.25,
        mouth_y: -0.35,
        mouth_width: 0.30,
        nose_length: 0.08,
        eye_socket_smooth: 0.03,  // Hard, angular edges
        mouth_smooth: 0.03,
        nose_smooth: 0.03,
        eyeball_smooth: 0.03,
    },
};

/**
 * Get character geometry by name
 * @param {string} name - Character name
 * @returns {Object} Character geometry parameters
 */
export function getCharacterGeometry(name) {
    return CHARACTER_PRESETS[name] || CHARACTER_PRESETS.default;
}

/**
 * Get all available character names
 * @returns {string[]} Array of character names
 */
export function getCharacterNames() {
    return Object.keys(CHARACTER_PRESETS);
}
