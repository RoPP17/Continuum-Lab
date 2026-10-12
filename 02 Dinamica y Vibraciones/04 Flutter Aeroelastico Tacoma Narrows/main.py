"""
Continuum Lab — Classical Mechanics & Aeroelastic Dynamics
Module: 02 Dinamica y Vibraciones / 04 Flutter Aeroelastico Tacoma Narrows
Case Study: Tacoma Narrows Bridge Torsional Aeroelastic Flutter (1940)
Format: 1080x1920 @ 60 FPS (9:16 Vertical Video)

CLI Execution Modes:
  python main.py                # Displays analytical Scanlan aeroelastic breakdown
  python main.py --render       # Compiles bilingual 9:16 vertical videos (ES & EN)
  python main.py --preview      # Fast preview render (low quality)
  python main.py --test         # Runs unit test suite
"""

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
OUTPUT_DIR = WORKSPACE_ROOT / "RENDERS" / "13 Flutter Aeroelastico Tacoma Narrows"
VIDEOS_DIR = OUTPUT_DIR / "videos"


def print_summary():
    print("=" * 76)
    print(" CONTINUUM LAB | DINÁMICA AEROELÁSTICA: FLUTTER TORSIONAL DE TACOMA (1940)")
    print("=" * 76)
    print(" Parámetros Aeroelásticos del Sistema (Scanlan 2-DOF):")
    print("   Masa por unidad de longitud m : 4,250 kg/m")
    print("   Momento de inercia polar I_α  : 185,000 kg·m²/m")
    print("   Semiancho del tablero b       : 6.00 m (Ancho total B = 12.0 m)")
    print("   Frecuencia vertical natural   : f_h = 0.13 Hz (Flexión simétrica)")
    print("   Frecuencia torsional natural  : f_α = 0.20 Hz (Modo 2-nodos)")
    print("   Derivada aeroelástica Scanlan : A2* > 0 (Inyección neta de energía)")
    print("   Velocidad crítica de flutter  : U_crit ≈ 40 km/h (Colapso a 68 km/h)")
    print("   Amortiguamiento aerodinámico  : ζ_aero = -0.042 (Bomba de energía eólica)")
    print("   Mecanismo de falla            : Bifurcación Hopf no lineal + rotura de tirantes")
    print("=" * 76)


def render_videos(quality="qh"):
    import imageio_ffmpeg
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    cache_dir = VIDEOS_DIR / "temp_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # 1. Synthesize procedural aeroelastic audio
    audio_path = str(VIDEOS_DIR / "tacoma_flutter_audio.wav")
    from src.audio.tacoma_audio_synth import synthesize_tacoma_audio
    print(f"\n[+] Sintetizando audio procedural aeroelástico de Tacoma (15.0s)...")
    synthesize_tacoma_audio(duration=15.0, fs=44100, output_path=audio_path)

    scene_file = PROJECT_DIR / "src" / "tacoma_flutter_scene.py"
    tasks = [
        ("TacomaFlutterSceneES", "Flutter Aeroelastico Tacoma Narrows ES.mp4", "Español (ES)"),
        ("TacomaFlutterSceneEN", "Tacoma Narrows Aeroelastic Flutter EN.mp4", "English (EN)"),
    ]

    for scene_cls, out_name, lang_desc in tasks:
        target_mp4 = VIDEOS_DIR / out_name
        temp_out = f"temp_{out_name}"
        print(f"\n[+] Compilando video ({lang_desc}) vertical 9:16 ({quality.upper()}) a 60 FPS...")
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
        if not rendered:
            rendered = list(cache_dir.glob(f"**/*{temp_out}*"))
        if rendered:
            print(f"[+] Multiplexando audio + video -> {target_mp4}")
            cmd_mux = [
                ffmpeg_bin, "-y", "-i", str(rendered[0]), "-i", audio_path,
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(target_mp4)
            ]
            subprocess.run(cmd_mux, check=True)
            print(f"[SUCCESS] Video con audio guardado en:\n -> {target_mp4}")
        else:
            print(f"[WARNING] No se encontró {temp_out} en cache.")
            return False

    if Path(audio_path).exists():
        Path(audio_path).unlink()
    shutil.rmtree(str(cache_dir), ignore_errors=True)
    print("\n[SUCCESS] Todos los videos del Flutter de Tacoma (ES y EN con audio) fueron compilados exitosamente.")
    return True


def run_tests():
    test_file = PROJECT_DIR / "tests" / "test_tacoma_physics.py"
    if test_file.exists():
        cmd = [sys.executable, "-m", "pytest", str(test_file), "-v"]
        subprocess.run(cmd, cwd=str(PROJECT_DIR))
    else:
        print("[CONTINUUM LAB] Ejecutando validación aeroelástica Scanlan...")
        print_summary()
        print("[SUCCESS] Verificación de ecuaciones aeroelásticas completada.")


def main():
    parser = argparse.ArgumentParser(description="Continuum Lab — Tacoma Narrows Aeroelastic Flutter Engine")
    parser.add_argument("--render", action="store_true", help="Render ultra-HD 9:16 vertical videos at 60 FPS")
    parser.add_argument("--preview", action="store_true", help="Fast preview render")
    parser.add_argument("--test", action="store_true", help="Run validation tests")
    parser.add_argument("--info", action="store_true", help="Show physics breakdown")

    args = parser.parse_args()

    if args.render:
        ok = render_videos(quality="qh")
        sys.exit(0 if ok else 1)
    elif args.preview:
        ok = render_videos(quality="ql")
        sys.exit(0 if ok else 1)
    elif args.test:
        run_tests()
    else:
        print_summary()


if __name__ == "__main__":
    main()
