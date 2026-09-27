"""
Continuum Lab — Mathematical Physics & Complex Geometry
Module: 06 Matematicas y Geometria / 02 Identidad de Euler 3D
Case Study: 3D Helical Representation of Euler's Formula and Orthogonal 2D Projections (Cosine & Sine Waves)

Execution Modes:
  python main.py                # Displays analytical mathematical summary & landmark evaluation
  python main.py --render       # Renders bilingual TikTok 9:16 3D videos with lo-fi soundtrack
  python main.py --benchmark    # Exports dynamic Excel model (.xlsx)
"""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
project_dir = Path(__file__).resolve().parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.math.euler_math import EulerHelixAnalysis
from src.math.export_euler_excel import export_euler_benchmark_excel


def parse_args():
    parser = argparse.ArgumentParser(description="Continuum Lab — Euler 3D Identity & Projections Engine")
    parser.add_argument("--render", action="store_true", help="Render bilingual 9:16 TikTok 3D videos with lo-fi music")
    parser.add_argument("--benchmark", action="store_true", help="Generate dynamic openpyxl model (.xlsx)")
    return parser.parse_args()


def main():
    args = parse_args()
    print("===============================================================================")
    print("                 CONTINUUM LAB // MATHEMATICS & GEOMETRY")
    print("                 Module: 02 Identidad de Euler en el Espacio 3D")
    print("===============================================================================")

    workspace_root = project_dir.parent.parent
    renders_dir = workspace_root / "RENDERS" / "4 Identidad de Euler 3D"

    if args.benchmark:
        bench_path = str(renders_dir / "extra" / "benchmarks" / "Euler_Identity_Complex_Benchmark.xlsx")
        export_euler_benchmark_excel(bench_path)
        print(f"[CONTINUUM LAB] Dynamic Excel benchmark updated: {bench_path}")
        return

    if args.render:
        from src.visualization.render_euler_3d_video import render_all
        render_all()
        return

    # Default: terminal mathematical summary
    engine = EulerHelixAnalysis()
    print("\n--- 1. CARDINAL LANDMARKS & EULER'S IDENTITY ---")
    for lm in engine.key_landmarks():
        print(f"  theta = {lm['angle_symbol']:6s} | z = {lm['complex_str']:10s} | Modulus: {lm['modulus']:.4f} | {lm['description']}")

    print("\n--- 2. DIFFERENTIAL GEOMETRY OF THE COMPLEX HELIX ---")
    diff = engine.differential_properties(1.0)
    print(f"  Helix Speed |v(t)|:       {diff['speed']:.6f}  (Exact: sqrt(2) = 1.414214)")
    print(f"  Curvature kappa:          {diff['curvature']:.6f}  (Exact: 1/2 = 0.500000)")
    print(f"  Torsion tau:              {diff['torsion']:.6f}  (Exact: 1/2 = 0.500000)")

    print("\n--- 3. TAYLOR CONVERGENCE AT theta = 1 rad ---")
    for order in [1, 3, 5, 7]:
        t_res = engine.taylor_approximation(1.0, order=order)
        print(f"  Order {order}: cos_err = {t_res['cos_error']:.2e} | sin_err = {t_res['sin_error']:.2e}")

    print("\n[CONTINUUM LAB] Use --render to compile videos or --benchmark to export Excel.")


if __name__ == "__main__":
    main()
