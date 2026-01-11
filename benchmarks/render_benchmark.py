#!/usr/bin/env python3
"""
Rendering performance benchmark suite.

Measures frame render times across different quality levels.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model import CharacterHead
from src.renderer import ASCIIShader, Camera, QualityLevel, Raymarcher


def benchmark_quality_level(quality: QualityLevel, num_frames: int = 10) -> dict:
    """
    Benchmark a specific quality level.

    Args:
        quality: Quality level to test
        num_frames: Number of frames to render

    Returns:
        Dict with benchmark results
    """
    print(f"\nBenchmarking {quality.value} quality...")

    # Create renderer
    head = CharacterHead()
    camera = Camera(position=(0, 0, -3.5), target=(0, 0, 0))
    shader = ASCIIShader(ramp="standard")
    raymarcher = Raymarcher(
        width=80,
        height=40,
        camera=camera,
        shader=shader,
        quality=quality,
    )

    # Warm up
    sdf = head.get_sdf()
    raymarcher.render_frame(sdf)

    # Benchmark
    times = []
    for i in range(num_frames):
        head.update(0.033)  # Simulate 30 FPS updates
        sdf = head.get_sdf()

        start = time.perf_counter()
        _ = raymarcher.render_frame(sdf)
        end = time.perf_counter()

        elapsed = end - start
        times.append(elapsed)

        print(f"  Frame {i+1}/{num_frames}: {elapsed*1000:.1f}ms", end="\r")

    print()  # New line after progress

    # Calculate statistics
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    avg_fps = 1.0 / avg_time if avg_time > 0 else 0

    return {
        "quality": quality.value,
        "avg_time_ms": avg_time * 1000,
        "min_time_ms": min_time * 1000,
        "max_time_ms": max_time * 1000,
        "avg_fps": avg_fps,
        "max_steps": raymarcher.max_steps,
        "epsilon": raymarcher.epsilon,
    }


def run_benchmark_suite():
    """Run complete benchmark suite across all quality levels."""
    print("=" * 60)
    print("Liquid ASCII Rendering Benchmark")
    print("=" * 60)
    print("Resolution: 80x40 characters")
    print("Frames per quality level: 10")
    print()

    qualities = [
        QualityLevel.LOW,
        QualityLevel.MEDIUM,
        QualityLevel.HIGH,
        QualityLevel.ULTRA,
    ]

    results = []
    for quality in qualities:
        result = benchmark_quality_level(quality, num_frames=10)
        results.append(result)

    # Print summary table
    print("\n" + "=" * 60)
    print("Benchmark Results")
    print("=" * 60)
    print(
        f"{'Quality':<10} {'Steps':<8} {'Avg Time':<12} {'Min Time':<12} "
        f"{'Max Time':<12} {'Avg FPS':<10}"
    )
    print("-" * 60)

    for r in results:
        print(
            f"{r['quality']:<10} {r['max_steps']:<8} "
            f"{r['avg_time_ms']:>10.1f}ms "
            f"{r['min_time_ms']:>10.1f}ms "
            f"{r['max_time_ms']:>10.1f}ms "
            f"{r['avg_fps']:>9.1f}"
        )

    # Calculate speedup relative to HIGH (default)
    high_result = next(r for r in results if r["quality"] == "high")
    high_time = high_result["avg_time_ms"]

    print("\n" + "=" * 60)
    print("Performance Comparison (relative to HIGH quality)")
    print("=" * 60)

    for r in results:
        speedup = high_time / r["avg_time_ms"]
        print(
            f"{r['quality']:<10} {speedup:>5.2f}x "
            f"({r['avg_time_ms']/high_time*100:>5.1f}% time)"
        )

    # Recommendations
    print("\n" + "=" * 60)
    print("Recommendations")
    print("=" * 60)

    low_fps = results[0]["avg_fps"]  # LOW quality
    medium_fps = results[1]["avg_fps"]  # MEDIUM quality
    high_fps = results[2]["avg_fps"]  # HIGH quality

    if high_fps >= 15:
        print("✓ HIGH quality achieves target 15 FPS - recommended for most users")
    elif medium_fps >= 15:
        print("⚠ Use MEDIUM quality to achieve target 15 FPS")
    elif low_fps >= 15:
        print("⚠ Use LOW quality to achieve target 15 FPS")
    else:
        print("⚠ Performance is below target even at LOW quality")
        print("  Consider reducing resolution or using --quality auto for adaptive quality")

    print()


if __name__ == "__main__":
    run_benchmark_suite()
