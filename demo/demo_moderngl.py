#!/usr/bin/env python3
"""
ModernGL Desktop GPU Renderer Demo

Native OpenGL desktop window with 60+ FPS GPU-accelerated rendering.
Reuses WebGL shaders for maximum code sharing.
"""

import sys
import time
from pathlib import Path

try:
    import moderngl
    import moderngl_window as mglw
    from moderngl_window import geometry
    MODERNGL_AVAILABLE = True
except ImportError:
    MODERNGL_AVAILABLE = False
    print("ModernGL not installed. Install with:")
    print("  pip install moderngl moderngl-window")
    sys.exit(1)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model.head import CharacterHead, HeadGeometry


class LiquidASCIIWindow(mglw.WindowConfig):
    """
    ModernGL window for GPU-accelerated 3D head rendering.
    """

    gl_version = (3, 3)
    title = "Liquid ASCII - ModernGL Desktop Renderer"
    window_size = (1280, 720)
    aspect_ratio = 16 / 9
    resizable = True
    vsync = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Character state
        self.character_name = "default"
        self.head = CharacterHead(character_name=self.character_name)
        self.geom = self.head.geometry

        # Camera state
        self.camera_distance = 3.5
        self.camera_angle = 0.0
        self.camera_fov = 45.0
        self.auto_rotate = True
        self.rotation_speed = 0.5

        # Lighting state
        self.ambient = 0.1
        self.diffuse = 0.7
        self.specular = 0.2
        self.specular_power = 16.0

        # Cel-shading
        self.cel_shading = False
        self.cel_bands = 3

        # Load shaders (reuse WebGL shaders)
        self.load_shaders()

        # Create fullscreen quad
        self.quad = geometry.quad_fs()

        # FPS tracking
        self.fps_time = time.time()
        self.fps_frames = 0
        self.fps = 0

    def load_shaders(self):
        """Load vertex and fragment shaders."""
        # Load from WebGL shader files
        webgl_dir = Path(__file__).parent.parent / "webgl" / "shaders"

        vertex_path = webgl_dir / "vertex.glsl"
        fragment_path = webgl_dir / "fragment.glsl"

        if not vertex_path.exists() or not fragment_path.exists():
            print(f"Error: WebGL shaders not found at {webgl_dir}")
            sys.exit(1)

        with open(vertex_path) as f:
            vertex_source = f.read()

        with open(fragment_path) as f:
            fragment_source = f.read()

        # Create shader program
        self.program = self.ctx.program(
            vertex_shader=vertex_source,
            fragment_shader=fragment_source
        )

    def render(self, time_val: float, frametime: float):
        """Render frame."""
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)

        # Update camera
        if self.auto_rotate:
            self.camera_angle = time_val * self.rotation_speed * 0.3

        cam_x = self.camera_distance * 0.0  # Fixed for now
        cam_y = 0.3
        cam_z = self.camera_distance

        # Set uniforms
        self.program['u_time'].value = time_val
        self.program['u_resolution'].value = self.window_size

        # Camera
        self.program['u_camera_pos'].value = (cam_x, cam_y, cam_z)
        self.program['u_camera_target'].value = (0.0, 0.0, 0.0)
        self.program['u_camera_fov'].value = self.camera_fov * 3.14159 / 180.0

        # Character geometry
        self.program['u_head_radii'].value = self.geom.head_radii
        self.program['u_eye_socket_radius'].value = self.geom.eye_socket_radius
        self.program['u_eyeball_radius'].value = self.geom.eyeball_radius
        self.program['u_eye_separation'].value = self.geom.eye_separation
        self.program['u_eye_height'].value = self.geom.eye_height
        self.program['u_eye_depth'].value = self.geom.eye_depth
        self.program['u_pupil_radius'].value = self.geom.pupil_radius
        self.program['u_mouth_y'].value = self.geom.mouth_y
        self.program['u_mouth_openness'].value = self.head.state.mouth_openness
        self.program['u_mouth_width'].value = self.geom.mouth_width_base
        self.program['u_nose_length'].value = self.geom.nose_length
        self.program['u_eye_socket_smooth'].value = self.geom.eye_socket_smooth
        self.program['u_eyeball_smooth'].value = self.geom.eyeball_smooth
        self.program['u_mouth_smooth'].value = self.geom.mouth_smooth
        self.program['u_nose_smooth'].value = self.geom.nose_smooth

        # Lighting
        self.program['u_light_dir'].value = (-0.5, 0.8, 1.0)
        self.program['u_ambient'].value = self.ambient
        self.program['u_diffuse'].value = self.diffuse
        self.program['u_specular'].value = self.specular
        self.program['u_specular_power'].value = self.specular_power

        # Cel-shading
        self.program['u_cel_shading'].value = 1 if self.cel_shading else 0
        self.program['u_cel_bands'].value = self.cel_bands

        # Render fullscreen quad
        self.quad.render(self.program)

        # Update FPS
        self.fps_frames += 1
        if time_val - self.fps_time >= 1.0:
            self.fps = self.fps_frames
            self.fps_frames = 0
            self.fps_time = time_val
            self.wnd.title = f"Liquid ASCII - ModernGL ({self.fps} FPS) - {self.character_name}"

    def key_event(self, key, action, modifiers):
        """Handle keyboard input."""
        if action == self.wnd.keys.ACTION_PRESS:
            # Character switching (1-9)
            if key == self.wnd.keys.NUMBER_1:
                self.switch_character("default")
            elif key == self.wnd.keys.NUMBER_2:
                self.switch_character("robot")
            elif key == self.wnd.keys.NUMBER_3:
                self.switch_character("alien")
            elif key == self.wnd.keys.NUMBER_4:
                self.switch_character("cyclops")
            elif key == self.wnd.keys.NUMBER_5:
                self.switch_character("monster")
            elif key == self.wnd.keys.NUMBER_6:
                self.switch_character("baby")
            elif key == self.wnd.keys.NUMBER_7:
                self.switch_character("fish")
            elif key == self.wnd.keys.NUMBER_8:
                self.switch_character("square")

            # Cel-shading toggle (C)
            elif key == self.wnd.keys.C:
                self.cel_shading = not self.cel_shading
                print(f"Cel-shading: {'ON' if self.cel_shading else 'OFF'}")

            # Auto-rotate toggle (SPACE)
            elif key == self.wnd.keys.SPACE:
                self.auto_rotate = not self.auto_rotate
                print(f"Auto-rotate: {'ON' if self.auto_rotate else 'OFF'}")

    def switch_character(self, name: str):
        """Switch to a different character."""
        self.character_name = name
        self.head = CharacterHead(character_name=name)
        self.geom = self.head.geometry
        print(f"Switched to character: {name}")


def main():
    """Run ModernGL demo."""
    print("=" * 70)
    print("Liquid ASCII - ModernGL Desktop Renderer")
    print("=" * 70)
    print()
    print("Controls:")
    print("  1-8: Switch characters")
    print("  C: Toggle cel-shading")
    print("  SPACE: Toggle auto-rotation")
    print("  ESC: Exit")
    print()
    print("Starting...")
    print()

    # Run window
    mglw.run_window_config(LiquidASCIIWindow)


if __name__ == "__main__":
    main()
