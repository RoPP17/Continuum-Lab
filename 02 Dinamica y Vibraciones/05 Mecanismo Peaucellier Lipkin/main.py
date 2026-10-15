"""
Continuum Lab — Classical Mechanics & Mechanical Engineering Systems
Module: 02 Dinamica y Vibraciones / 05 Mecanismo Peaucellier Lipkin
Case Study: Peaucellier-Lipkin Exact Straight-Line Mechanism (1864)
Format: 1080x1920 @ 60 FPS (9:16 Vertical Video)

CLI Execution Modes:
  python main.py                # Displays analytical kinematic derivation
  python main.py --render       # Compiles bilingual 9:16 vertical videos (ES & EN)
  python main.py --preview      # Fast preview render (low quality)
  python main.py --test         # Runs unit test suite
  python main.py --benchmark    # Generates dynamic Excel workbook (.xlsx)
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
OUTPUT_DIR = WORKSPACE_ROOT / "RENDERS" / "15 Mecanismo de Peaucellier Lipkin"
VIDEOS_DIR = OUTPUT_DIR / "videos"
BENCHMARKS_DIR = OUTPUT_DIR / "benchmarks"


def print_summary():
    print("=" * 76)
    print(" CONTINUUM LAB | MECANISMO DE PEAUCELLIER-LIPKIN (LÍNEA RECTA EXACTA DE 1864)")
    print("=" * 76)
    print(" Fundamento Físico & Cinemático:")
    print("   Inversión Geométrica en el Plano Complejo: OP · OP' = R² - l² = k")
    print("   Eslabones móviles         : 7 barras + 6 pasadores rotatorios (Cero guías)")
    print("   Polo fijo de inversión O₁ : (-2.00, 0.00) cm")
    print("   Pivote fijo manivela O₂   : (-1.15, 0.00) cm")
    print("   Radio manivela guía r     : 0.85 cm")
    print("   Longitud brazos O₁A, O₁B  : 2.80 cm (R)")
    print("   Lado rombo APBP'          : 1.60 cm (l)")
    print("   Potencia de inversión k   : 5.2800 cm²")
    print("   Recta teórica resultante  : x = -2.00 + 5.28 / (2 * 0.85) = 1.1059 cm")
    print("   Desviación analítica      : ε = 0.000000000 mm (Error = 0.00%)")
    print("=" * 76)


def run_benchmark():
    from src.export.export_excel_benchmark import generate_benchmark
    out_file = BENCHMARKS_DIR / "Mecanismo_Peaucellier_Lipkin_Linea_Recta.xlsx"
    generate_benchmark(out_file)
    print(f"[OK] Benchmark generado en: {out_file}")


def render_videos(quality="qh"):
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    cache_dir = VIDEOS_DIR / "temp_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # 1. Procedural Audio Synthesis
    from src.audio.peaucellier_audio_synth import synthesize_peaucellier_audio
    import imageio_ffmpeg
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    temp_audio = str(VIDEOS_DIR / "peaucellier_audio_temp.wav")
    print(f"\n[+] Sintetizando audio procedural de deslizamiento mecánico y chimes (14.0s)...")
    synthesize_peaucellier_audio(duration=14.0, fs=44100, output_path=temp_audio)

    scene_file = PROJECT_DIR / "src" / "visualization" / "peaucellier_scene.py"
    tasks = [
        ("PeaucellierSceneES", "Mecanismo Peaucellier Lipkin ES.mp4", "Español (ES)"),
        ("PeaucellierSceneEN", "Peaucellier Lipkin Mechanism EN.mp4", "English (EN)"),
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
        try:
            os.remove(temp_audio)
        except Exception:
            pass

    if cache_dir.exists():
        try:
            shutil.rmtree(cache_dir)
        except Exception:
            pass

    print("\n" + "=" * 76)
    print(" [CONTINUUM LAB] VIDEOS VECTORIALES COMPILADOS CON ÉXITO")
    print(f" Directorio de salida: {VIDEOS_DIR}")
    print("=" * 76)
    return True


def run_tests():
    test_dir = PROJECT_DIR / "tests"
    cmd = [sys.executable, "-m", "pytest", str(test_dir), "-v"]
    res = subprocess.run(cmd)
    return res.returncode == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Continuum Lab - Peaucellier-Lipkin Mechanism")
    parser.add_argument("--render", action="store_true", help="Render full HD 9:16 vertical videos (60 FPS)")
    parser.add_argument("--preview", action="store_true", help="Render fast preview (480p)")
    parser.add_argument("--test", action="store_true", help="Run verification test suite")
    parser.add_argument("--benchmark", action="store_true", help="Export dynamic Excel model")
    args = parser.parse_args()

    if args.render:
        render_videos(quality="qh")
    elif args.preview:
        render_videos(quality="ql")
    elif args.test:
        run_tests()
    elif args.benchmark:
        run_benchmark()
    else:
        print_summary()
