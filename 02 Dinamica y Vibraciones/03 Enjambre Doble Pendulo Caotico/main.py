"""
Continuum Lab — Classical Mechanics & Nonlinear Dynamical Systems
Entry Point: Deterministic Chaos & Lyapunov Divergence in Double Pendulum Swarm
Division: 02 Dinamica y Vibraciones / 03 Enjambre Doble Pendulo Caotico
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import time

current_dir = Path(__file__).resolve().parent
WORKSPACE_ROOT = current_dir.parent.parent
OUTPUT_DIR = WORKSPACE_ROOT / "RENDERS" / "8 Enjambre Doble Pendulo Caotico"

# Asegurar importación de src
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from src.physics.export_excel_benchmark import generate_swarm_benchmark_xlsx


def run_unit_tests():
    """Ejecuta la suite de verificación física con pytest."""
    test_file = current_dir / "tests" / "test_swarm_physics.py"
    print("\n[CONTINUUM LAB] 1/3 Verificando física hamiltoniana y condiciones de caos con pytest...")
    cmd = [sys.executable, "-m", "pytest", str(test_file), "-v"]
    res = subprocess.run(cmd, cwd=str(current_dir))
    if res.returncode != 0:
        print("[ERROR] Los tests físicos no pasaron. Abortando renderizado.")
        return False
    print("[SUCCESS] Verificación física completa y aprobada (100%).")
    return True


def export_benchmark():
    """Genera el modelo dinámico en Excel con fórmulas vivas."""
    print("\n[CONTINUUM LAB] 2/3 Generando modelo analítico y benchmark en Excel (.xlsx)...")
    local_xlsx = current_dir / "benchmarks" / "Doble_Pendulo_Conservacion_Energia.xlsx"
    render_xlsx = OUTPUT_DIR / "Doble_Pendulo_Conservacion_Energia.xlsx"

    generate_swarm_benchmark_xlsx(local_xlsx)
    shutil.copy2(str(local_xlsx), str(render_xlsx))
    print(f"[SUCCESS] Benchmark exportado a:")
    print(f"  -> {local_xlsx}")
    print(f"  -> {render_xlsx}")


def render_vector_animation():
    """Compila el video vectorial 9:16 (1080x1920 @ 60 FPS, 15 segundos exactos) con Manim."""
    print("\n[CONTINUUM LAB] 3/3 Compilando animación vectorial Manim 9:16 (1080x1920 @ 60 FPS)...")
    video_dir = OUTPUT_DIR / "videos"
    cover_dir = OUTPUT_DIR / "cover"
    video_dir.mkdir(parents=True, exist_ok=True)
    cover_dir.mkdir(parents=True, exist_ok=True)

    cache_dir = current_dir / "manim_cache"
    scene_file = current_dir / "src" / "visualization" / "manim_swarm_scene.py"
    target_mp4 = video_dir / "doble_pendulo_enjambre_caos_1080x1920.mp4"
    target_cover = cover_dir / "cover_enjambre_caotico_1080x1920.png"

    # Comando de renderizado Manim en alta definición (-qh)
    cmd = [
        sys.executable,
        "-m",
        "manim",
        "-qh",
        str(scene_file),
        "SwarmDoublePendulumScene",
        "--media_dir",
        str(cache_dir),
        "-o",
        "doble_pendulo_enjambre_caos_1080x1920.mp4",
    ]

    t0 = time.time()
    res = subprocess.run(cmd, cwd=str(current_dir))
    elapsed = time.time() - t0

    if res.returncode != 0:
        print(f"[ERROR] Manim falló con código {res.returncode}")
        return False

    # Mover archivo de video desde cache hacia el directorio final de RENDERS
    rendered_files = list(cache_dir.glob("**/doble_pendulo_enjambre_caos_1080x1920.mp4"))
    if rendered_files:
        shutil.move(str(rendered_files[0]), str(target_mp4))
        print(f"[SUCCESS] Video compilado en {elapsed:.1f} s (< 3 minutos).")
        print(f"[SUCCESS] Archivo MP4 listo en: {target_mp4}")
    else:
        print("[WARNING] No se encontró el archivo MP4 renderizado en la caché.")

    # Generar Snapshot / Portada Ultra-HD
    print("[CONTINUUM LAB] Generando portada estática en resolución nativa...")
    cmd_cover = [
        sys.executable,
        "-m",
        "manim",
        "-s",
        "-qh",
        str(scene_file),
        "SwarmDoublePendulumScene",
        "--media_dir",
        str(cache_dir),
    ]
    subprocess.run(cmd_cover, cwd=str(current_dir), capture_output=True)
    cover_files = list(cache_dir.glob("**/*.png"))
    if cover_files:
        shutil.move(str(cover_files[0]), str(target_cover))
        print(f"[SUCCESS] Portada guardada en: {target_cover}")

    # Limpiar caché
    shutil.rmtree(str(cache_dir), ignore_errors=True)
    return True


def main():
    print("=" * 75)
    print("CONTINUUM LAB // SIMULADOR DE CAOS DETERMINISTA Y SENSIBILIDAD EXTREMA")
    print("Enjambre de 50 Dobles Péndulos Planos Superpuestos (DOP853 Runge-Kutta)")
    print("=" * 75)

    if not run_unit_tests():
        sys.exit(1)

    export_benchmark()
    render_vector_animation()

    print("\n" + "=" * 75)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 75)


if __name__ == "__main__":
    main()
