#!/usr/bin/env python3
"""
Basic Head Rendering Example

Renders a static 3D head using raymarching and SDF.
This is the simplest example showing the core rendering pipeline.
"""

import sys
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from src.renderer import Raymarcher, Camera, ASCIIShader
from src.model.head import create_simple_head_sdf


def main():
    # Create renderer with standard settings
    camera = Camera(position=(0, 0, -3.5), target=(0, 0, 0))
    shader = ASCIIShader(ramp="standard")
    raymarcher = Raymarcher(
        width=80,
        height=40,
        camera=camera,
        shader=shader,
        max_steps=50,
    )

    # Create a simple static head SDF
    head_sdf = create_simple_head_sdf(
        mouth_openness=0.3,  # Slightly open mouth
        blink=0.0,          # Eyes open
        time=0.0,           # No animation offset
    )

    # Render frame
    frame = raymarcher.render_frame(head_sdf)
    print(frame)
    print("\n[Static head render complete]")


if __name__ == "__main__":
    main()
