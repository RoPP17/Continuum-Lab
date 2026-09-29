"""
Continuum Lab — Fluid Mechanics & Nonlinear PDEs
Module: 01 Mecanica de Fluidos / 02 Singularidad Navier Stokes Blowup
Case Study: Finite-Time Singularity for 3D Incompressible Navier-Stokes Equations (OpenAI Breakthrough)

Execution Modes:
  python main.py                # Displays analytical physical summary & asymptotic metrics
  python main.py --render       # Renders bilingual 9:16 TikTok 60 FPS videos with hydro-acoustic audio
  python main.py --benchmark    # Exports dynamic Excel model (.xlsx)
  python main.py --visuals      # Generates high-res PNG diagrams & animated GIF preview
  python main.py --all          # Runs all benchmark, visual, and video generation steps
"""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
project_dir = Path(__file__).resolve().parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.physics.navier_stokes_blowup import NavierStokesBlowupSimulation, BlowupParameters
from src.physics.export_benchmarks import create_singularity_benchmark_workbook
from src.visualization.generate_hero_previews import generate_all_visuals


def parse_args():
    parser = argparse.ArgumentParser(description="Continuum Lab — Navier-Stokes Blowup Engine")
    parser.add_argument("--render", action="store_true", help="Render bilingual 9:16 60 FPS TikTok videos with audio")
    parser.add_argument("--benchmark", action="store_true", help="Generate dynamic openpyxl model (.xlsx)")
    parser.add_argument("--visuals", action="store_true", help="Generate high-resolution PNGs and animated GIF")
    parser.add_argument("--all", action="store_true", help="Execute benchmark, visuals, and video rendering")
    return parser.parse_args()


def main():
    args = parse_args()
    print("===============================================================================")
    print("                 CONTINUUM LAB // FLUID MECHANICS & NONLINEAR PDES")
    print("         Case Study: 02 Singularidad de Navier-Stokes en Tiempo Finito")
    print("         Paper: OpenAI (2024/2025) — Millennium Problem Alternative (C)")
    print("===============================================================================")

    workspace_root = project_dir.parent.parent
    renders_dir = workspace_root / "RENDERS" / "5 Singularidad Navier Stokes"

    if args.benchmark or args.all:
        bench_path = str(renders_dir / "extra" / "benchmarks" / "Navier_Stokes_Singularity_Benchmark.xlsx")
        create_singularity_benchmark_workbook(bench_path)
        print(f"[CONTINUUM LAB] Dynamic Excel benchmark updated: {bench_path}")

    if args.visuals or args.all:
        generate_all_visuals()

    if args.render or args.all:
        from src.visualization.render_blowup_video import render_all
        render_all()
        return

    if not (args.benchmark or args.visuals or args.render or args.all):
        # Default: Terminal scientific and asymptotic summary
        sim = NavierStokesBlowupSimulation()
        print("\n--- 1. SCALING EXPONENTS & MILLENNIUM PROBLEM FORMULATION ---")
        print(f"  Kinematic Viscosity nu:    {sim.params.nu:.4f}")
        print(f"  Scaling Exponent h:        {sim.params.h:.4f}  (Constraint: 0 < h < 1/100)")
        print(f"  Velocity Exponent A:       {sim.params.A:.4f}  (A = 1/2 + h)")
        print(f"  Axial Scale Exponent D:    {sim.params.D:.4f}  (D = 1/2 - h)")
        print(f"  Exponent Sum A + D:        {sim.params.A + sim.params.D:.4f}  (Exact Incompressibility)")

        print("\n--- 2. TIME HORIZON ASYMPTOTICS (t -> T* = 1.0 s) ---")
        print(f"{'Time t':<10} | {'tau':<10} | {'||u||_inf (m/s)':<16} | {'E_tot (J)':<12} | {'l_r (m)':<10} | {'l_z (m)':<10} | {'l_r/l_z':<10}")
        print("-" * 88)
        for t_val in [0.0, 0.5, 0.9, 0.99, 0.999, 0.9999]:
            m = sim.compute_global_metrics(t_val)
            print(f"{t_val:<10.4f} | {m['tau']:<10.1e} | {m['u_max']:<16.2e} | {m['energy_total']:<12.4f} | {m['l_r']:<10.4f} | {m['l_z']:<10.4f} | {m['slenderness']:<10.4f}")

        print("\n--- 3. KEY MATHEMATICAL BREAKTHROUGHS OF THE CONSTRUCTION ---")
        print("  1. Divergent Peak Velocity: ||u(t)||_inf ~ tau^(-1/2 - h) -> +Inf (Finite-time blowup)")
        print("  2. Uniformly Bounded Energy: sup_t ||u(t)||_L2 < Inf (Core energy shrinks as tau^(1/2 - 3h) -> 0)")
        print("  3. Needle Core Formation: l_r / l_z ~ tau^h -> 0 (Anisotropic radial contraction)")
        print("  4. Reynolds Stress Cancellation: Two wave pulse families (sigma = +/-1) in the annulus")
        print("     provide <w_r w_theta> and <w_r w_z> that exactly cancel the singular momentum residual!")

        print("\n[CONTINUUM LAB] Use --benchmark, --visuals, or --render to generate all assets.")


if __name__ == "__main__":
    main()
