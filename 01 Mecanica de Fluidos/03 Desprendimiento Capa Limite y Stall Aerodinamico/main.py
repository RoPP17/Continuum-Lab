"""
Continuum Lab — Fluid Mechanics & Aerodynamics
Module: 01 Mecanica de Fluidos / 03 Desprendimiento Capa Limite y Stall Aerodinamico
Case Study: Aerodynamic Stall at 18.5° & Boundary Layer Separation Dynamics

Execution Modes:
  python main.py                # Displays analytical physical summary & aerodynamic polars
  python main.py --benchmark    # Exports dynamic Excel model (.xlsx)
  python main.py --visuals      # Generates high-res PNG diagrams & animated GIF preview
  python main.py --render       # Renders bilingual 9:16 60 FPS TikTok/Shorts videos with audio
  python main.py --all          # Runs benchmark, visuals, and video rendering sequentially
"""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
project_dir = Path(__file__).resolve().parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.physics.aerodynamic_stall import AerodynamicStallSimulation, AirfoilParameters
from src.physics.export_benchmarks import create_stall_benchmark_workbook
from src.visualization.generate_hero_previews import generate_all_visuals


def parse_args():
    parser = argparse.ArgumentParser(description="Continuum Lab — Aerodynamic Stall Engine")
    parser.add_argument("--benchmark", action="store_true", help="Generate dynamic openpyxl model (.xlsx)")
    parser.add_argument("--visuals", action="store_true", help="Generate high-resolution PNGs and animated GIF")
    parser.add_argument("--render", action="store_true", help="Render bilingual 9:16 60 FPS TikTok videos with audio")
    parser.add_argument("--all", action="store_true", help="Execute benchmark, visuals, and video rendering")
    return parser.parse_args()


def main():
    args = parse_args()
    print("===============================================================================")
    print("                 CONTINUUM LAB // FLUID MECHANICS & AERODYNAMICS")
    print("       Case Study: 03 Desprendimiento de Capa Límite y Stall Aerodinámico")
    print("       Topic: Boundary Layer Separation, Adverse Gradient dp/dx > 0 & Stall Buffet")
    print("===============================================================================")

    workspace_root = project_dir.parent.parent
    renders_dir = workspace_root / "RENDERS" / "7 Desprendimiento Capa Limite y Stall Aerodinamico"

    if args.benchmark or args.all:
        bench_path = str(renders_dir / "extra" / "benchmarks" / "Aerodynamic_Stall_Boundary_Layer_Benchmark.xlsx")
        create_stall_benchmark_workbook(bench_path)
        print(f"[CONTINUUM LAB] Dynamic Excel benchmark updated: {bench_path}")

    if args.visuals or args.all:
        generate_all_visuals()

    if args.render or args.all:
        from src.visualization.render_stall_video import render_all
        render_all()
        return

    if not (args.benchmark or args.visuals or args.render or args.all):
        # Default: Terminal scientific and aerodynamic summary
        sim = AerodynamicStallSimulation()
        print("\n--- 1. AIRFOIL SPECIFICATIONS & FLOW REGIME ---")
        print(f"  Airfoil:                   NACA {int(sim.params.thickness*100):02d} (Symmetric, t/c = {sim.params.thickness:.2f})")
        print(f"  Chord Length c:            {sim.params.chord:.2f} m")
        print(f"  Freestream Speed U_inf:    {sim.params.u_inf:.1f} m/s ({sim.params.u_inf*3.6:.0f} km/h)")
        print(f"  Reynolds Number Re_c:      {sim.params.reynolds_number:.1e}")
        print(f"  Thin Airfoil Lift Slope:   2*pi rad^-1 ({2*np.pi*np.radians(1.0):.4f} deg^-1)")

        print("\n--- 2. AERODYNAMIC POLAR EVOLUTION (CRUISE TO DEEP STALL) ---")
        print(f"{'Alpha (deg)':<12} | {'C_L (Thin)':<12} | {'C_L (Real)':<12} | {'C_D':<10} | {'L/D':<8} | {'x_sep/c':<10} | {'Regime'}")
        print("-" * 88)
        for a_val in [0.0, 4.0, 8.0, 12.0, 15.5, 17.0, 18.5, 20.0]:
            st = sim.boundary_layer_state(a_val)
            print(f"{a_val:<12.1f} | {st['cl_linear']:<12.3f} | {st['cl']:<12.3f} | {st['cd']:<10.3f} | {st['lift_drag_ratio']:<8.1f} | {st['x_sep_over_c']:<10.2f} | {st['state_en']}")

        print("\n--- 3. KEY AERODYNAMIC & FLUID DYNAMIC DISCOVERIES ---")
        print("  1. Thin Airfoil Theory: C_L = 2*pi*alpha matches closely up to alpha ~ 10 deg (C_L(4 deg) = 0.44).")
        print("  2. Adverse Pressure Gradient: dp/dx > 0 on suction side decelerates the boundary layer.")
        print("  3. Wall Shear Vanishing: (du/dy)|_wall = 0 at separation point (Pohlhausen parameter Lambda = -12).")
        print("  4. The 74% Lift Crash: Pitching to alpha = 18.5 deg causes C_L to collapse from 1.55 to 0.40.")
        print("  5. Drag Explosion: Separated wake form drag surges C_D from 0.015 to 0.288 (>14x increase), triggering violent stall buffet.")

        print("\n[CONTINUUM LAB] Use --benchmark, --visuals, or --render to generate all deliverables.")


if __name__ == "__main__":
    import numpy as np
    main()
