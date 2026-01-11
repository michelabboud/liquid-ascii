"""
Camera system for 3D to 2D projection.

Handles view transformation and ray generation for raymarching.
"""


import numpy as np

from .sdf import Vec3, _to_array, normalize


class Camera:
    """
    Perspective camera for raymarching.

    Generates rays from a viewpoint through a virtual screen.
    """

    def __init__(
        self,
        position: Vec3 = (0, 0, -3),
        target: Vec3 = (0, 0, 0),
        up: Vec3 = (0, 1, 0),
        fov: float = 60.0,
        aspect_ratio: float = 2.0,  # Terminal chars are ~2x taller than wide
    ):
        """
        Initialize camera.

        Args:
            position: Camera position in world space
            target: Point the camera is looking at
            up: Up direction vector
            fov: Field of view in degrees
            aspect_ratio: Width/height ratio (accounting for terminal char shape)
        """
        self.position = _to_array(position)
        self.target = _to_array(target)
        self.up = _to_array(up)
        self.fov = fov
        self.aspect_ratio = aspect_ratio

        self._update_basis()

    def _update_basis(self):
        """Compute camera basis vectors."""
        # Forward direction (camera looks along -Z in camera space)
        self.forward = normalize(self.target - self.position)

        # Right vector (perpendicular to forward and up)
        self.right = normalize(np.cross(self.forward, self.up))

        # Recompute up to ensure orthogonality
        self.true_up = np.cross(self.right, self.forward)

        # FOV in radians
        self.fov_rad = np.radians(self.fov)
        self.tan_half_fov = np.tan(self.fov_rad / 2)

    def set_position(self, position: Vec3):
        """Update camera position."""
        self.position = _to_array(position)
        self._update_basis()

    def set_target(self, target: Vec3):
        """Update camera target."""
        self.target = _to_array(target)
        self._update_basis()

    def orbit(self, angle_x: float, angle_y: float, radius: float = None):
        """
        Orbit camera around target.

        Args:
            angle_x: Horizontal angle (radians)
            angle_y: Vertical angle (radians)
            radius: Distance from target (None = keep current)
        """
        if radius is None:
            radius = np.linalg.norm(self.position - self.target)

        # Clamp vertical angle to avoid gimbal lock
        angle_y = np.clip(angle_y, -np.pi / 2 + 0.01, np.pi / 2 - 0.01)

        # Spherical to Cartesian
        x = radius * np.cos(angle_y) * np.sin(angle_x)
        y = radius * np.sin(angle_y)
        z = radius * np.cos(angle_y) * np.cos(angle_x)

        self.position = self.target + np.array([x, y, z])
        self._update_basis()

    def get_ray(self, u: float, v: float) -> tuple[np.ndarray, np.ndarray]:
        """
        Generate a ray for normalized screen coordinates.

        Args:
            u: Horizontal coordinate (-1 to 1, left to right)
            v: Vertical coordinate (-1 to 1, bottom to top)

        Returns:
            (origin, direction) tuple
        """
        # Scale by FOV and aspect ratio
        x = u * self.tan_half_fov * self.aspect_ratio
        y = v * self.tan_half_fov

        # Compute ray direction in world space
        direction = normalize(
            self.forward + x * self.right + y * self.true_up
        )

        return self.position.copy(), direction

    def get_rays_batch(self, width: int, height: int) -> tuple[np.ndarray, np.ndarray]:
        """
        Generate rays for all pixels in a grid.

        Args:
            width: Screen width in characters
            height: Screen height in characters

        Returns:
            (origins, directions) arrays of shape (height, width, 3)
        """
        # Create normalized coordinate grids
        u = np.linspace(-1, 1, width)
        v = np.linspace(1, -1, height)  # Flip v for screen coordinates
        uu, vv = np.meshgrid(u, v)

        # Scale by FOV and aspect ratio
        xx = uu * self.tan_half_fov * self.aspect_ratio
        yy = vv * self.tan_half_fov

        # Build direction vectors
        directions = np.zeros((height, width, 3))
        directions[:, :, 0] = self.forward[0] + xx * self.right[0] + yy * self.true_up[0]
        directions[:, :, 1] = self.forward[1] + xx * self.right[1] + yy * self.true_up[1]
        directions[:, :, 2] = self.forward[2] + xx * self.right[2] + yy * self.true_up[2]

        # Normalize directions
        lengths = np.sqrt(np.sum(directions ** 2, axis=2, keepdims=True))
        directions = directions / lengths

        # Origins are all the same (camera position)
        origins = np.broadcast_to(self.position, (height, width, 3)).copy()

        return origins, directions


def project_point(
    point: Vec3,
    camera_pos: Vec3 = (0, 0, -3),
    k1: float = 30,
    k2: float = 5
) -> tuple[float, float]:
    """
    Simple perspective projection (donut.c style).

    Args:
        point: 3D point to project
        camera_pos: Camera position
        k1: Field of view scale
        k2: Viewer distance factor

    Returns:
        (x', y') screen coordinates
    """
    point = _to_array(point)
    camera_pos = _to_array(camera_pos)

    # Relative position
    p = point - camera_pos
    z = p[2] if p[2] != 0 else 0.001

    # Perspective division
    ooz = 1 / (k2 + z)  # "one over z"
    xp = k1 * p[0] * ooz
    yp = k1 * p[1] * ooz

    return xp, yp
