"""
Continuum Lab — Classical Mechanics & Nonlinear Dynamical Systems
Entry Point: Deterministic Chaos & Lyapunov Divergence in Double Pendulum Swarm
Dual Render Edition: Spanish (ES) and English (EN)
Division: 02 Dinamica y Vibraciones / 03 Enjambre Doble Pendulo Caotico
"""

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
    print("\n[CONTINUUM LAB] 1/4 Verificando física hamiltoniana con pytest...")
    cmd = [sys.executable, "-m", "pytest", str(test_file), "-v"]
    res = subprocess.run(cmd, cwd=str(current_dir))
    if res.returncode != 0:
        print("[ERROR] Los tests físicos no pasaron. Abortando renderizado.")
        return False
    print("[SUCCESS] Verificación física completada y aprobada (100%).")
    return True


def export_benchmark():
    """Genera el modelo dinámico en Excel con fórmulas vivas."""
    print("\n[CONTINUUM LAB] 2/4 Generando modelo analítico y benchmark en Excel (.xlsx)...")
    local_xlsx = current_dir / "benchmarks" / "Doble_Pendulo_Conservacion_Energia.xlsx"
    render_xlsx = OUTPUT_DIR / "Doble_Pendulo_Conservacion_Energia.xlsx"

    generate_swarm_benchmark_xlsx(local_xlsx)
    shutil.copy2(str(local_xlsx), str(render_xlsx))
    print(f"[SUCCESS] Benchmark exportado a:")
    print(f"  -> {local_xlsx}")
    print(f"  -> {render_xlsx}")


def render_scene(scene_name: str, target_video_name: str, target_cover_name: str, lang_label: str):
    """Compila una versión de la animación vectorial 9:16 (1080x1920 @ 60 FPS) con Manim."""
    video_dir = OUTPUT_DIR / "videos"
    cover_dir = OUTPUT_DIR / "cover"
    video_dir.mkdir(parents=True, exist_ok=True)
    cover_dir.mkdir(parents=True, exist_ok=True)

    cache_dir = current_dir / f"manim_cache_{scene_name}"
    scene_file = current_dir / "src" / "visualization" / "manim_swarm_scene.py"
    target_mp4 = video_dir / target_video_name
    target_cover = cover_dir / target_cover_name

    print(f"\n[CONTINUUM LAB] Compilando video ({lang_label}) 1080x1920 @ 60 FPS...")
    cmd_video = [
        sys.executable,
        "-m",
        "manim",
        "-qh",
        str(scene_file),
        scene_name,
        "--media_dir",
        str(cache_dir),
        "-o",
        target_video_name,
    ]

    t0 = time.time()
    res = subprocess.run(cmd_video, cwd=str(current_dir))
    elapsed = time.time() - t0

    if res.returncode != 0:
        print(f"[ERROR] Manim falló para {scene_name} con código {res.returncode}")
        return False

    # Mover video compilado
    rendered_files = list(cache_dir.glob(f"**/{target_video_name}"))
    if rendered_files:
        shutil.move(str(rendered_files[0]), str(target_mp4))
        print(f"[SUCCESS] Video ({lang_label}) listo en {elapsed:.1f} s: {target_mp4}")
    else:
        print(f"[WARNING] No se encontró el video {target_video_name} en la caché.")

    # Generar Portada Estática en Alta Resolución
    print(f"[CONTINUUM LAB] Generando portada ({lang_label}) en resolución nativa...")
    cmd_cover = [
        sys.executable,
        "-m",
        "manim",
        "-s",
        "-qh",
        str(scene_file),
        scene_name,
        "--media_dir",
        str(cache_dir),
    ]
    subprocess.run(cmd_cover, cwd=str(current_dir), capture_output=True)
    cover_files = list(cache_dir.glob("**/*.png"))
    if cover_files:
        shutil.move(str(cover_files[0]), str(target_cover))
        print(f"[SUCCESS] Portada ({lang_label}) guardada en: {target_cover}")

    # Limpiar caché
    shutil.rmtree(str(cache_dir), ignore_errors=True)
    return True


def main():
    print("=" * 75)
    print("CONTINUUM LAB // SIMULADOR DE CAOS DETERMINISTA Y SENSIBILIDAD EXTREMA")
    print("Enjambre de 50 Dobles Péndulos Planos Superpuestos (DOP853 Runge-Kutta)")
    print("Edición Dual: Español (ES) & Inglés (EN)")
    print("=" * 75)

    if not run_unit_tests():
        sys.exit(1)

    export_benchmark()

    # 1. Render Español
    render_scene(
        scene_name="SwarmDoublePendulumSceneES",
        target_video_name="doble_pendulo_enjambre_caos_es_1080x1920.mp4",
        target_cover_name="cover_enjambre_caotico_es_1080x1920.png",
        lang_label="Español",
    )

    # 2. Render Inglés
    render_scene(
        scene_name="SwarmDoublePendulumSceneEN",
        target_video_name="double_pendulum_swarm_chaos_en_1080x1920.mp4",
        target_cover_name="cover_swarm_chaos_en_1080x1920.png",
        lang_label="English",
    )

    # Mantener alias doble_pendulo_enjambre_caos_1080x1920.mp4 apuntando a la versión en español
    default_mp4 = OUTPUT_DIR / "videos" / "doble_pendulo_enjambre_caos_1080x1920.mp4"
    es_mp4 = OUTPUT_DIR / "videos" / "doble_pendulo_enjambre_caos_es_1080x1920.mp4"
    if es_mp4.exists():
        shutil.copy2(str(es_mp4), str(default_mp4))

    default_cover = OUTPUT_DIR / "cover" / "cover_enjambre_caotico_1080x1920.png"
    es_cover = OUTPUT_DIR / "cover" / "cover_enjambre_caotico_es_1080x1920.png"
    if es_cover.exists():
        shutil.copy2(str(es_cover), str(default_cover))

    print("\n" + "=" * 75)
    print("PROCESO DUAL COMPLETADO EXITOSAMENTE (ES & EN)")
    print("=" * 75)


if __name__ == "__main__":
    main()
