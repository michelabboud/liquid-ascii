"""Renderer package - raymarching and SDF-based 3D rendering"""

from .camera import Camera
from .quality import AdaptiveQualityController, QualityLevel, QualityPreset, get_quality_preset
from .raymarcher import Raymarcher
from .sdf import (
    sdf_box,
    sdf_ellipsoid,
    sdf_intersection,
    sdf_smooth_intersection,
    sdf_smooth_subtraction,
    sdf_smooth_union,
    sdf_sphere,
    sdf_subtraction,
    sdf_torus,
    sdf_union,
)
from .shading import ASCIIShader

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
    "QualityLevel",
    "QualityPreset",
    "AdaptiveQualityController",
    "get_quality_preset",
]
