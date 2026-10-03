"""
Continuum Lab — Classical Mechanics & Mathematical Physics
Division: 06 Matematicas y Geometria / 03 Curva Braquistocrona
Case Study: La Paradoja de la Curva Braquistócrona (Johann Bernoulli 1696)
Format: TikTok 9:16 Vertical Video (1080x1920 @ 60 FPS)

CLI Execution Modes:
  python main.py                # Displays analytical calculus of variations breakdown
  python main.py --render       # Compiles ultra-HD 9:16 vertical video at 60 FPS
  python main.py --preview      # Fast preview render (low quality)
  python main.py --benchmark    # Generates dynamic Excel workbook (.xlsx)
  python main.py --test         # Executes pytest validation suite
"""

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path

# Add project root to sys.path
project_dir = Path(__file__).resolve().parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.physics.brachistochrone_models import BrachistochroneSimulator
from src.export.export_excel import export_brachistochrone_excel

WORKSPACE_ROOT = project_dir.parent.parent
RENDERS_DIR = WORKSPACE_ROOT / "RENDERS" / "9 Curva Braquistocrona"
VIDEO_DIR = RENDERS_DIR / "videos"
BENCH_DIR = RENDERS_DIR / "benchmarks"


def render_video(quality: str = "qh") -> bool:
    """Compiles the 9:16 vertical vector video using Manim."""
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    cache_dir = VIDEO_DIR / "manim_cache"
    scene_file = project_dir / "src" / "visualization" / "manim_brachistochrone.py"
    target_mp4 = VIDEO_DIR / "braquistocrona_tiktok_1080x1920.mp4"

    cmd = [
        sys.executable, "-m", "manim", f"-{quality}",
        str(scene_file), "TikTokBrachistochrone",
        "--media_dir", str(cache_dir),
        "-o", "braquistocrona_tiktok_1080x1920.mp4",
    ]

    print(f"\n[CONTINUUM LAB] Compilando video vectorial vertical 9:16 ({quality.upper()}) a 60 FPS...")
    print(f"Comando: {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=str(project_dir))
    if res.returncode != 0:
        print(f"[ERROR] Manim falló con código {res.returncode}")
        return False

    rendered_files = list(cache_dir.glob("**/braquistocrona_tiktok_1080x1920.mp4"))
    if rendered_files:
        shutil.move(str(rendered_files[0]), str(target_mp4))
        shutil.rmtree(str(cache_dir), ignore_errors=True)
        print(f"\n[SUCCESS] Video renderizado con éxito en:\n -> {target_mp4}")
        return True

    print("[WARNING] No se encontró el archivo generado en cache.")
    return False


def run_benchmark():
    """Generates the dynamic Excel spreadsheet model."""
    BENCH_DIR.mkdir(parents=True, exist_ok=True)
    xlsx_target = BENCH_DIR / "Braquistocrona_Benchmark_Cinematico.xlsx"
    export_brachistochrone_excel(str(xlsx_target))
    print(f"\n[CONTINUUM LAB] Modelo Excel (.xlsx) generado con éxito en:\n -> {xlsx_target}")


def run_unit_tests():
    """Runs the full pytest test suite."""
    test_path = project_dir / "tests" / "test_brachistochrone.py"
    cmd = [sys.executable, "-m", "pytest", str(test_path), "-v"]
    print(f"\n[CONTINUUM LAB] Ejecutando suite de pruebas unitarias...")
    subprocess.run(cmd, cwd=str(project_dir))


def print_theoretical_summary():
    """Outputs analytical procedure and comparison in terminal."""
    sim = BrachistochroneSimulator(g=9.81)
    summary = sim.get_summary_data()

    print("================================================================================")
    print("                 CONTINUUM LAB // CÁLCULO DE VARIACIONES                        ")
    print("           LA PARADOJA DE LA BRAQUISTÓCRONA (JOHANN BERNOULLI 1696)             ")
    print("================================================================================")
    print("Punto Inicial: A = (0.0, 4.0) m  |  Punto Final: B = (7.0, -3.0) m  |  g = 9.81 m/s²\n")
    print("Derivación Teórica de Euler-Lagrange:")
    print("  Funcional de tiempo: T[y] = integral_{x_A}^{x_B} sqrt(1 + y'^2) / sqrt(2*g*(y_0 - y)) dx")
    print("  Identidad de Beltrami: f - y'*(df/dy') = C  =>  (y_0 - y)*(1 + y'^2) = 2*r")
    print("  Solución Paramétrica (Cicloide Invertida):")
    print("    x(theta) = r * (theta - sin(theta))")
    print("    y(theta) = y_0 - r * (1 - cos(theta))\n")
    print("RESULTADOS COMPARATIVOS DE LAS 4 PISTAS:")
    print("-" * 80)
    print(f"{'Puesto':<8} {'Pista':<26} {'T. Target (s)':<15} {'T. Físico (s)':<15} {'Longitud (m)':<14}")
    print("-" * 80)
    for s in summary:
        print(f"{s['rank']}º       {s['name']:<26} {s['target_time']:<15.3f} {s['physical_time']:<15.3f} {s['arc_length']:<14.3f}")
    print("-" * 80)
    print("\nPARADOJA RESUELTA:")
    print("  - Distancia Euclidiana más corta: Pista Recta (9.899 m), pero es la MÁS LENTA (1.62 s).")
    print("  - Camino de Mínimo Tiempo: Cicloide (10.364 m), 1er Lugar (1.32 s).")
    print("  - Razón Física: La cicloide aprovecha la caída vertical abrupta inicial para transformar")
    print("    energía potencial en energía cinética de inmediato, alcanzando una velocidad media")
    print("    abrumadoramente superior que compensa con creces el trayecto adicional.\n")
    print("Comandos disponibles:")
    print("  python main.py --render     # Renderiza video 1080x1920 @ 60 FPS")
    print("  python main.py --preview    # Renderiza preview rápido")
    print("  python main.py --benchmark  # Exporta modelo Excel dinámico (.xlsx)")
    print("  python main.py --test       # Ejecuta pruebas automatizadas")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Continuum Lab — Brachistochrone Paradox Engine")
    parser.add_argument("--render", action="store_true", help="Render ultra-HD 9:16 vertical video at 60 FPS")
    parser.add_argument("--preview", action="store_true", help="Fast preview render")
    parser.add_argument("--benchmark", action="store_true", help="Export dynamic Excel model (.xlsx)")
    parser.add_argument("--test", action="store_true", help="Run pytest unit tests")

    args = parser.parse_args()

    if args.render:
        render_video(quality="qh")
    elif args.preview:
        render_video(quality="ql")
    elif args.benchmark:
        run_benchmark()
    elif args.test:
        run_unit_tests()
    else:
        print_theoretical_summary()


if __name__ == "__main__":
    main()
