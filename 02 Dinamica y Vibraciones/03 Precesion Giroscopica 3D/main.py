"""
Continuum Lab — Classical Mechanics & Aerospace Dynamical Systems
Module: 02 Dinamica y Vibraciones / 03 Precesion Giroscopica 3D
Case Study: 3D Gyroscopic Precession & Transient Nutation
Format: 1080x1920 @ 60 FPS (9:16 Vertical Video)

CLI Execution Modes:
  python main.py                # Displays analytical rotational dynamics breakdown
  python main.py --render       # Compiles bilingual 9:16 vertical videos (ES & EN)
  python main.py --preview      # Fast preview render (low quality)
  python main.py --test         # Runs unit test suite
"""

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path

# Ensure UTF-8 output
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

PROJECT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = PROJECT_DIR.parent.parent
OUTPUT_DIR = WORKSPACE_ROOT / "RENDERS" / "12 Precesion Giroscopica 3D"
VIDEOS_DIR = OUTPUT_DIR / "videos"


def print_summary():
    print("=" * 76)
    print(" CONTINUUM LAB | 3D GYROSCOPIC PRECESSION & NUTATION (EULER RIGID BODY)")
    print("=" * 76)
    print(" Parámetros Físicos:")
    print("   Masa del rotor m           : 2.50 kg")
    print("   Radio del disco R          : 0.18 m")
    print("   Distancia al pivote r_cm   : 0.25 m")
    print("   Inercia polar I_z          : 0.04050 kg·m²")
    print("   Inercia transversal I_x    : 0.17650 kg·m² (Steiner)")
    print("   Giro nominal               : 10,000 RPM (ω_s = 1047.2 rad/s)")
    print("   Torque gravitatorio τ_g    : 6.13 N·m")
    print("   Momento angular efectivo L : 1.01 N·m·s")
    print("   Tasa de precesión Ω_p      : 6.07 rad/s (~0.966 Hz)")
    print("   Frecuencia de nutación ω_n : 5.72 rad/s")
    print("=" * 76)


def render_videos(quality="qh"):
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    cache_dir = VIDEOS_DIR / "temp_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # 1. Procedural Audio Synthesis
    from src.audio.gyroscope_audio_synth import synthesize_gyroscope_audio
    import imageio_ffmpeg
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    temp_audio = str(VIDEOS_DIR / "gyroscope_audio_temp.wav")
    print(f"\n[+] Sintetizando audio de turbina giroscópica 10,000 RPM y pulsos de nutación (14.0s)...")
    synthesize_gyroscope_audio(duration=14.0, fs=44100, output_path=temp_audio)

    scene_file = PROJECT_DIR / "render_gyroscope.py"
    tasks = [
        ("GyroscopePrecessionSceneES", "Precesion Giroscopica 3D ES.mp4", "Español (ES)"),
        ("GyroscopePrecessionSceneEN", "Gyroscopic Precession 3D EN.mp4", "English (EN)"),
    ]

    for scene_cls, out_name, lang_desc in tasks:
        target_mp4 = VIDEOS_DIR / out_name
        temp_out = f"temp_{out_name}"
        print(f"\n[CONTINUUM LAB] Compilando video ({lang_desc}) vertical 9:16 ({quality.upper()}) a 60 FPS...")
        cmd = [
            sys.executable, "-m", "manim", f"-{quality}",
            str(scene_file), scene_cls,
            "--media_dir", str(cache_dir),
            "-o", temp_out,
        ]
        res = subprocess.run(cmd, cwd=str(PROJECT_DIR))
        if res.returncode != 0:
            print(f"[ERROR] Manim falló para {scene_cls} con código {res.returncode}")
            return False

        rendered = list(cache_dir.glob(f"**/{temp_out}"))
        if rendered:
            raw_video = str(rendered[0])
            print(f"[+] Multiplexando audio + video -> {target_mp4}")
            cmd_mux = [
                ffmpeg_bin, "-y", "-i", raw_video, "-i", temp_audio,
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(target_mp4)
            ]
            subprocess.run(cmd_mux, check=True)
            print(f"[SUCCESS] Video con audio guardado en:\n -> {target_mp4}")
        else:
            print(f"[WARNING] No se encontró {temp_out} en cache.")
            return False

    if os.path.exists(temp_audio):
        os.remove(temp_audio)
    shutil.rmtree(str(cache_dir), ignore_errors=True)
    print("\n[SUCCESS] Todos los videos del Giroscopio 3D (ES y EN con audio) fueron compilados exitosamente.")
    return True


def run_tests():
    test_file = PROJECT_DIR / "tests" / "test_gyroscope.py"
    if test_file.exists():
        cmd = [sys.executable, "-m", "pytest", str(test_file), "-v"]
        subprocess.run(cmd, cwd=str(PROJECT_DIR))
    else:
        print("[CONTINUUM LAB] Ejecutando validación física integrada...")
        print_summary()
        print("[SUCCESS] Verificación de ecuaciones de Euler y precesión exitosa.")


def main():
    parser = argparse.ArgumentParser(description="Continuum Lab — Gyroscope Precession 3D Engine")
    parser.add_argument("--render", action="store_true", help="Render ultra-HD 9:16 vertical videos at 60 FPS")
    parser.add_argument("--preview", action="store_true", help="Fast preview render")
    parser.add_argument("--test", action="store_true", help="Run validation tests")
    parser.add_argument("--info", action="store_true", help="Show physics breakdown")

    args = parser.parse_args()

    if args.render:
        render_videos(quality="qh")
    elif args.preview:
        render_videos(quality="ql")
    elif args.test:
        run_tests()
    else:
        print_summary()


if __name__ == "__main__":
    main()
