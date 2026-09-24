"""
Continuum Lab — Classical Mechanics & Dynamical Systems
Entry Point: Chaotic Triple Pendulum Trajectory Simulation
Division: 02 Dinamica y Vibraciones / 01 Pendulo Triple Caotico
"""

import os
import sys
import subprocess
from pathlib import Path

current_dir = Path(__file__).resolve().parent
WORKSPACE_ROOT = current_dir.parent.parent
OUTPUT_DIR = WORKSPACE_ROOT / "RENDERS" / "2 Pendulo Triple Trayectoria Caotica"


def render_video():
    """Compiles the 9:16 vertical vector video using Manim."""
    video_dir = OUTPUT_DIR / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = video_dir / "manim_cache"

    scene_file = current_dir / "src" / "visualization" / "manim_triple_pendulum.py"
    target_mp4 = video_dir / "pendulo_triple_caos_1080x1920.mp4"

    cmd = [
        sys.executable, "-m", "manim", "-qh",
        str(scene_file), "TikTokTriplePendulum",
        "--media_dir", str(cache_dir),
        "-o", "pendulo_triple_caos_1080x1920.mp4"
    ]

    print(f"[CONTINUUM LAB] Compiling 20s vector TikTok video (1080x1920 @ 60 FPS)...")
    res = subprocess.run(cmd, cwd=str(current_dir))
    if res.returncode != 0:
        print(f"[ERROR] Manim failed with code {res.returncode}")
        return False

    # Move from cache to final video folder
    rendered_file = list(cache_dir.glob("**/pendulo_triple_caos_1080x1920.mp4"))
    if rendered_file:
        import shutil
        shutil.move(str(rendered_file[0]), str(target_mp4))
        shutil.rmtree(str(cache_dir), ignore_errors=True)
        print(f"[SUCCESS] Video ready at: {target_mp4}")
        return True
    return False


def export_benchmark_data():
    """Simulates 10,000 steps and saves energy conservation benchmark to openpyxl model."""
    from src.physics.triple_pendulum import TriplePendulumSimulator, TriplePendulumParams
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    bench_dir = OUTPUT_DIR / "benchmarks"
    bench_dir.mkdir(parents=True, exist_ok=True)
    xlsx_file = bench_dir / "Pendulo_Triple_Conservacion_Energia.xlsx"

    sim = TriplePendulumSimulator()
    sim.set_initial_state((2.268, 1.745, 1.221))  # [130, 100, 70 deg]

    wb = Workbook()
    ws = wb.active
    ws.title = "Energy_Dynamics"
    ws.views.sheetView[0].showGridLines = True

    # Styling
    hdr_fill = PatternFill(start_color="0D1117", end_color="0D1117", fill_type="solid")
    hdr_font = Font(name="Segoe UI", size=11, bold=True, color="00F0FF")
    reg_font = Font(name="Segoe UI", size=10, color="E6EDF3")
    accent_fill = PatternFill(start_color="161B22", end_color="161B22", fill_type="solid")

    headers = ["Step", "Time_sec", "Theta1_rad", "Theta2_rad", "Theta3_rad", "Total_Energy_J", "Abs_Energy_Deviation"]
    for c_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=c_idx, value=h)
        cell.fill = hdr_fill
        cell.font = hdr_font
        cell.alignment = Alignment(horizontal="center")

    dt = 0.002
    for i in range(1, 1001):
        sim.step_rk4(dt)
        r = i + 1
        ws.cell(row=r, column=1, value=i).number_format = "#,##0"
        ws.cell(row=r, column=2, value=sim.time).number_format = "0.000"
        ws.cell(row=r, column=3, value=sim.state[0]).number_format = "0.0000"
        ws.cell(row=r, column=4, value=sim.state[1]).number_format = "0.0000"
        ws.cell(row=r, column=5, value=sim.state[2]).number_format = "0.0000"
        ws.cell(row=r, column=6, value=sim.total_energy()).number_format = "0.00000"
        ws.cell(row=r, column=7, value=f"=ABS(F{r}-$F$2)").number_format = "0.000000"

        for col in range(1, 8):
            cell = ws.cell(row=r, column=col)
            cell.font = reg_font
            if i % 2 == 0:
                cell.fill = accent_fill

    wb.save(str(xlsx_file))
    print(f"[SUCCESS] Dynamic benchmark saved to: {xlsx_file}")


if __name__ == "__main__":
    export_benchmark_data()
    render_video()
