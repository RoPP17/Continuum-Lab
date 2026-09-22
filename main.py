"""
Continuum Lab — Senior Computational Physics & Visual Engineering Architecture
Entry Point: Lattice Boltzmann D2Q9 Vortex Shedding Engine
Author: Roberto Andrés Pepe Sánchez (@RoPP17) & Continuum Lab Agent

Execution Modes:
  python main.py                     # Real-time 60 FPS CUDA interactive window
  python main.py --mode render       # 16:9 Widescreen Presentation Render (MP4)
  python main.py --mode render --format 9:16  # 9:16 Vertical Video for YouTube Shorts
  python main.py --benchmark         # Runs physics benchmark and exports dynamic Excel model
"""

import argparse
import sys
import os

from src.physics.lbm_d2q9 import LBMConfig
from src.simulation.engine import SimulationEngine
from src.physics.export_benchmarks import export_lbm_benchmark_excel


def parse_args():
    parser = argparse.ArgumentParser(
        description="Continuum Lab — LBM D2Q9 Vortex Shedding Simulation & Video Engine"
    )
    parser.add_argument(
        "--mode",
        choices=["interactive", "render"],
        default="interactive",
        help="Execution mode: interactive (real-time window) or render (video file export)"
    )
    parser.add_argument(
        "--format",
        choices=["16:9", "9:16"],
        default="16:9",
        help="Video aspect ratio: 16:9 (1920x1080) or 9:16 (1080x1920 for Shorts)"
    )
    parser.add_argument(
        "--reynolds",
        type=float,
        default=150.0,
        help="Reynolds number based on cylinder diameter (Re = U_inf * D / nu)"
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=360,
        help="Number of video frames to render in export mode"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=60,
        help="Frames per second for video export"
    )
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="Force CPU vectorized solver instead of Taichi GPU CUDA"
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Execute simulation benchmark and export dynamic openpyxl model (.xlsx)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print("===============================================================================")
    print("                 CONTINUUM LAB // COMPUTATIONAL PHYSICS & VISUALS")
    print("                      Director: Roberto Andrés Pepe Sánchez")
    print("===============================================================================")

    config = LBMConfig(
        nx=480,
        ny=192,
        reynolds=args.reynolds,
        u_inf=0.08,
        obstacle_radius=16.0
    )

    use_gpu = not args.cpu
    engine = SimulationEngine(config=config, use_gpu=use_gpu)

    if args.benchmark:
        print("[CONTINUUM LAB] Running benchmark time-series acquisition (500 steps)...")
        time_series = []
        for step_idx in range(500):
            telem = engine.step()
            time_series.append({
                "step": telem["step"],
                "time": step_idx * 0.01,
                "cd": telem["cd"],
                "cl": telem["cl"]
            })
            if (step_idx + 1) % 100 == 0:
                print(f"  Step {step_idx + 1}/500: Cd={telem['cd']:.3f}, Cl={telem['cl']:+.3f}")

        xlsx_path = os.path.join("assets", "benchmarks", "LBM_Karman_Shedding_Benchmark.xlsx")
        out = export_lbm_benchmark_excel(
            file_path=xlsx_path,
            time_series=time_series,
            reynolds=config.reynolds,
            mach=config.mach_number,
            diameter=config.diameter,
            nu=config.kinematic_viscosity
        )
        print(f"[CONTINUUM LAB] Dynamic Excel Benchmark saved to: {out}")
        return

    if args.mode == "render":
        output_file = os.path.join(
            "assets",
            "renders",
            f"lbm_karman_re{int(args.reynolds)}_{args.format.replace(':', 'x')}.mp4"
        )
        engine.export_video(
            output_path=output_file,
            num_frames=args.frames,
            sub_steps_per_frame=4,
            fps=args.fps,
            format_mode=args.format
        )
    else:
        # Interactive mode
        engine.run_interactive()


if __name__ == "__main__":
    main()
