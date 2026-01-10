"""Renderer package - raymarching and SDF-based 3D rendering"""

from .sdf import (
    sdf_sphere,
    sdf_ellipsoid,
    sdf_box,
    sdf_torus,
    sdf_smooth_union,
    sdf_smooth_subtraction,
    sdf_smooth_intersection,
    sdf_union,
    sdf_subtraction,
    sdf_intersection,
)
from .raymarcher import Raymarcher
from .shading import ASCIIShader
from .camera import Camera

__all__ = [
    "sdf_sphere",
    "sdf_ellipsoid",
    "sdf_box",
    "sdf_torus",
    "sdf_smooth_union",
    "sdf_smooth_subtraction",
    "sdf_smooth_intersection",
    "sdf_union",
    "sdf_subtraction",
    "sdf_intersection",
    "Raymarcher",
    "ASCIIShader",
    "Camera",
]
