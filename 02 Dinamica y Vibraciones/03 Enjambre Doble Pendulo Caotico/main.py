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


def render_scene(scene_name: str, target_video_name: str, target_cover_name: str, lang_label: str, audio_path: str):
    """Compila una versión de la animación vectorial 9:16 (1080x1920 @ 60 FPS) con Manim y audio procedural."""
    import imageio_ffmpeg
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

    video_dir = OUTPUT_DIR / "videos"
    cover_dir = OUTPUT_DIR / "cover"
    video_dir.mkdir(parents=True, exist_ok=True)
    cover_dir.mkdir(parents=True, exist_ok=True)

    cache_dir = current_dir / f"manim_cache_{scene_name}"
    scene_file = current_dir / "src" / "visualization" / "manim_swarm_scene.py"
    target_mp4 = video_dir / target_video_name
    target_cover = cover_dir / target_cover_name

    temp_video_name = f"temp_{target_video_name}"
    print(f"\n[+] Compilando video ({lang_label}) 1080x1920 @ 60 FPS...")
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
        temp_video_name,
    ]

    t0 = time.time()
    res = subprocess.run(cmd_video, cwd=str(current_dir))
    elapsed = time.time() - t0

    if res.returncode != 0:
        print(f"[ERROR] Manim falló para {scene_name} con código {res.returncode}")
        return False

    rendered_files = list(cache_dir.glob(f"**/{temp_video_name}"))
    if rendered_files:
        print(f"[+] Multiplexando audio + video -> {target_mp4}")
        cmd_mux = [
            ffmpeg_bin, "-y", "-i", str(rendered_files[0]), "-i", audio_path,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(target_mp4)
        ]
        subprocess.run(cmd_mux, check=True)
        print(f"[SUCCESS] Video con audio listo en {elapsed:.1f} s: {target_mp4}")
    else:
        print(f"[WARNING] No se encontró el video {temp_video_name} en la caché.")

    # Generar Portada Estática en Alta Resolución
    print(f"[+] Generando portada ({lang_label}) en resolución nativa...")
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

    # 0. Sintetizar Audio Procedural Caótico (15.0s)
    video_dir = OUTPUT_DIR / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)
    audio_path = str(video_dir / "swarm_audio.wav")
    from src.audio.swarm_audio_synth import synthesize_swarm_audio
    print(f"\n[+] Sintetizando audio procedural del enjambre caótico (15.0s)...")
    synthesize_swarm_audio(duration=15.0, fs=44100, output_path=audio_path)

    # 1. Render Español
    render_scene(
        scene_name="SwarmDoublePendulumSceneES",
        target_video_name="doble_pendulo_enjambre_caos_es_1080x1920.mp4",
        target_cover_name="cover_enjambre_caotico_es_1080x1920.png",
        lang_label="Español",
        audio_path=audio_path,
    )

    # 2. Render Inglés
    render_scene(
        scene_name="SwarmDoublePendulumSceneEN",
        target_video_name="double_pendulum_swarm_chaos_en_1080x1920.mp4",
        target_cover_name="cover_swarm_chaos_en_1080x1920.png",
        lang_label="English",
        audio_path=audio_path,
    )

    # Copiar con nombres estándar limpios
    es_std = OUTPUT_DIR / "videos" / "Enjambre Doble Pendulo Caotico ES.mp4"
    en_std = OUTPUT_DIR / "videos" / "Double Pendulum Chaotic Swarm EN.mp4"
    es_src = OUTPUT_DIR / "videos" / "doble_pendulo_enjambre_caos_es_1080x1920.mp4"
    en_src = OUTPUT_DIR / "videos" / "double_pendulum_swarm_chaos_en_1080x1920.mp4"
    if es_src.exists():
        shutil.copy2(str(es_src), str(es_std))
    if en_src.exists():
        shutil.copy2(str(en_src), str(en_std))

    if Path(audio_path).exists():
        Path(audio_path).unlink()


if __name__ == "__main__":
    main()
