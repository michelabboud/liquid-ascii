"""
PyOpenCL GPU-accelerated renderer for terminal ASCII output.

Provides 10-30x performance improvement over CPU raymarching by
offloading the entire rendering pipeline to the GPU using OpenCL.

Compatible with AMD, Intel, and NVIDIA GPUs.
"""

__version__ = "1.0.0"
