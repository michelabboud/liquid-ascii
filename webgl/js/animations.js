/**
 * Animation System for Liquid ASCII
 *
 * Provides idle animations (breathing, blinking, head movement) and
 * easing functions for smooth motion.
 */

/**
 * Easing functions for smooth animation
 */
export const Easing = {
    /**
     * Linear easing (no easing)
     */
    linear: (t) => t,

    /**
     * Ease in (slow start)
     */
    easeIn: (t) => t * t,

    /**
     * Ease out (slow end)
     */
    easeOut: (t) => t * (2 - t),

    /**
     * Ease in-out (slow start and end)
     */
    easeInOut: (t) => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,

    /**
     * Smooth step (hermite interpolation)
     */
    smoothStep: (t) => t * t * (3 - 2 * t),

    /**
     * Smoother step (improved hermite)
     */
    smootherStep: (t) => t * t * t * (t * (6 * t - 15) + 10),
};

/**
 * Animation controller for idle movements
 */
export class AnimationController {
    constructor() {
        // Animation state
        this.time = 0;
        this.enabled = true;

        // Breathing animation
        this.breathingSpeed = 0.3;  // Cycles per second
        this.breathingAmount = 0.05;  // Amplitude

        // Blinking animation
        this.blinkInterval = 3.0;  // Seconds between blinks
        this.blinkDuration = 0.15;  // Seconds per blink
        this.lastBlink = 0;
        this.blinkState = 0;  // 0-1

        // Head movement (subtle sway)
        this.headSwaySpeed = 0.2;
        this.headSwayAmount = 0.03;

        // Mouth movement (idle)
        this.mouthIdleSpeed = 0.5;
        this.mouthIdleAmount = 0.02;
    }

    /**
     * Update animation state
     * @param {number} deltaTime - Time since last update in seconds
     */
    update(deltaTime) {
        if (!this.enabled) {
            return;
        }

        this.time += deltaTime;

        // Update blink state
        const timeSinceBlink = this.time - this.lastBlink;

        if (timeSinceBlink > this.blinkInterval) {
            // Start new blink
            this.lastBlink = this.time;
            this.blinkState = 0;
        }

        if (timeSinceBlink < this.blinkDuration) {
            // During blink
            const blinkProgress = timeSinceBlink / this.blinkDuration;
            // Blink goes: open -> closed -> open
            if (blinkProgress < 0.5) {
                // Closing
                this.blinkState = Easing.smoothStep(blinkProgress * 2);
            } else {
                // Opening
                this.blinkState = 1 - Easing.smoothStep((blinkProgress - 0.5) * 2);
            }
        } else {
            this.blinkState = 0;
        }
    }

    /**
     * Get current breathing offset
     * @returns {number} Vertical offset for breathing (-1 to 1)
     */
    getBreathingOffset() {
        if (!this.enabled) return 0;
        return Math.sin(this.time * this.breathingSpeed * Math.PI * 2) * this.breathingAmount;
    }

    /**
     * Get current blink amount
     * @returns {number} Blink amount (0 = open, 1 = closed)
     */
    getBlinkAmount() {
        if (!this.enabled) return 0;
        return this.blinkState;
    }

    /**
     * Get head tilt angles
     * @returns {{x: number, y: number, z: number}} Rotation angles in radians
     */
    getHeadTilt() {
        if (!this.enabled) {
            return { x: 0, y: 0, z: 0 };
        }

        // Subtle head sway
        const swayX = Math.sin(this.time * this.headSwaySpeed * Math.PI) * this.headSwayAmount;
        const swayY = Math.cos(this.time * this.headSwaySpeed * Math.PI * 1.3) * this.headSwayAmount;
        const swayZ = Math.sin(this.time * this.headSwaySpeed * Math.PI * 0.7) * this.headSwayAmount * 0.5;

        return {
            x: swayX,
            y: swayY,
            z: swayZ
        };
    }

    /**
     * Get idle mouth movement
     * @returns {number} Mouth openness adjustment
     */
    getMouthIdleMovement() {
        if (!this.enabled) return 0;

        // Subtle mouth movement (breathing)
        const movement = Math.sin(this.time * this.mouthIdleSpeed * Math.PI) * this.mouthIdleAmount;
        return Math.max(0, movement);  // Only open, not close
    }

    /**
     * Enable/disable animations
     * @param {boolean} enabled
     */
    setEnabled(enabled) {
        this.enabled = enabled;
    }

    /**
     * Reset animation state
     */
    reset() {
        this.time = 0;
        this.lastBlink = 0;
        this.blinkState = 0;
    }

    /**
     * Trigger immediate blink
     */
    triggerBlink() {
        this.lastBlink = this.time;
        this.blinkState = 0;
    }

    /**
     * Set breathing parameters
     * @param {number} speed - Breathing speed (cycles per second)
     * @param {number} amount - Breathing amplitude
     */
    setBreathingParams(speed, amount) {
        this.breathingSpeed = speed;
        this.breathingAmount = amount;
    }

    /**
     * Set blink parameters
     * @param {number} interval - Time between blinks (seconds)
     * @param {number} duration - Blink duration (seconds)
     */
    setBlinkParams(interval, duration) {
        this.blinkInterval = interval;
        this.blinkDuration = duration;
    }
}

/**
 * Noise-based organic motion (Perlin-like)
 * Simplified 1D noise for smooth random motion
 */
export class OrganicNoise {
    constructor(seed = 0) {
        this.seed = seed;
        this.octaves = 3;
        this.persistence = 0.5;
    }

    /**
     * Get noise value at time
     * @param {number} t - Time value
     * @returns {number} Noise value (-1 to 1)
     */
    noise(t) {
        let total = 0;
        let frequency = 1;
        let amplitude = 1;
        let maxValue = 0;

        for (let i = 0; i < this.octaves; i++) {
            total += this.simpleNoise(t * frequency + this.seed) * amplitude;
            maxValue += amplitude;
            amplitude *= this.persistence;
            frequency *= 2;
        }

        return total / maxValue;
    }

    /**
     * Simple pseudo-random noise
     * @param {number} x - Input value
     * @returns {number} Noise value (-1 to 1)
     */
    simpleNoise(x) {
        const i = Math.floor(x);
        const f = x - i;

        // Hash function
        const hash = (n) => {
            n = Math.sin(n) * 43758.5453123;
            return n - Math.floor(n);
        };

        const a = hash(i);
        const b = hash(i + 1);

        // Smooth interpolation
        const t = Easing.smootherStep(f);
        return (a * (1 - t) + b * t) * 2 - 1;
    }
}

/**
 * Animation preset configurations
 */
export const AnimationPresets = {
    default: {
        breathingSpeed: 0.3,
        breathingAmount: 0.05,
        blinkInterval: 3.0,
        blinkDuration: 0.15,
        headSwaySpeed: 0.2,
        headSwayAmount: 0.03,
    },

    energetic: {
        breathingSpeed: 0.5,
        breathingAmount: 0.08,
        blinkInterval: 2.0,
        blinkDuration: 0.12,
        headSwaySpeed: 0.35,
        headSwayAmount: 0.05,
    },

    calm: {
        breathingSpeed: 0.2,
        breathingAmount: 0.03,
        blinkInterval: 4.5,
        blinkDuration: 0.18,
        headSwaySpeed: 0.1,
        headSwayAmount: 0.02,
    },

    sleeping: {
        breathingSpeed: 0.15,
        breathingAmount: 0.06,
        blinkInterval: 0.3,  // Very frequent "blinks" = eyes closed
        blinkDuration: 5.0,  // Long duration = sleeping
        headSwaySpeed: 0.05,
        headSwayAmount: 0.01,
    },

    none: {
        breathingSpeed: 0,
        breathingAmount: 0,
        blinkInterval: 9999,
        blinkDuration: 0,
        headSwaySpeed: 0,
        headSwayAmount: 0,
    },
};
