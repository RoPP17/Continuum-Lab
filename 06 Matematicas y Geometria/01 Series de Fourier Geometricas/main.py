"""
Continuum Lab — Mathematical Physics & Fourier Geometry
Module: 06 Matematicas y Geometria / 01 Series de Fourier Geometricas
Case Study: Complex Fourier Series Approximation of Canonical 2D Shapes (Circle, Star, Octagon)

Execution Modes:
  python main.py                # Displays mathematical harmonic analysis
  python main.py --render       # Renders bilingual TikTok 9:16 videos with lo-fi background music
  python main.py --benchmark    # Exports dynamic Excel model (.xlsx)
"""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
project_dir = Path(__file__).resolve().parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.math.fourier_shapes import ShapeFourierSeries
from src.math.export_fourier_excel import export_fourier_benchmark_excel


def parse_args():
    parser = argparse.ArgumentParser(description="Continuum Lab — Geometric Fourier Series Engine")
    parser.add_argument("--render", action="store_true", help="Render bilingual 9:16 TikTok videos with background music")
    parser.add_argument("--benchmark", action="store_true", help="Generate dynamic openpyxl model (.xlsx)")
    return parser.parse_args()


def main():
    args = parse_args()
    print("===============================================================================")
    print("                 CONTINUUM LAB // MATHEMATICS & GEOMETRY")
    print("                 Module: 06 Series de Fourier Geometricas")
    print("===============================================================================")

    workspace_root = project_dir.parent.parent
    renders_dir = workspace_root / "RENDERS" / "3 Series de Fourier Geometricas"

    if args.benchmark:
        bench_path = str(renders_dir / "extra" / "benchmarks" / "Fourier_Harmonics_Geometric_Benchmark.xlsx")
        export_fourier_benchmark_excel(bench_path)
        print(f"[CONTINUUM LAB] Dynamic Excel benchmark updated: {bench_path}")
        return

    if args.render:
        from src.visualization.render_fourier_shapes_video import render_all
        render_all()
        return

    # Default: terminal mathematical summary
    print("\n--- HARMONIC DECOMPOSITION ANALYSIS ---")
    for s_name in ["circle", "star", "octagon"]:
        f_series = ShapeFourierSeries(s_name)
        print(f"\n[Shape: {s_name.upper()}]")
        print(f"  Formula: {f_series.get_latex_formula('ES')}")
        print("  Harmonics (n, amplitude, phase):")
        for freq, amp, phase in f_series.harmonics:
            print(f"    n = {freq:3d} | |c_n| = {amp:.5f} | phase = {phase:.3f} rad")


if __name__ == "__main__":
    main()
