"""
Master CLI y Pipeline de Ejecución: Continuum Lab // 03 Mecánica de Sólidos
02 Pandeo No Lineal y Elástica de Euler (Bifurcación Supercrítica de Pitchfork)
"""

import os
import sys
import argparse
from pathlib import Path

# Asegurar path de imports
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent.parent
RENDERS_DIR = PROJECT_DIR / "RENDERS" / "22 Pandeo No Lineal y Elastica de Euler"

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.physics.euler_elastica_sim import EulerElastica
from src.physics.export_excel_benchmark import generate_elastica_excel_benchmark
from src.visualization.render_elastica import render_elastica_hero_poster
from src.visualization.render_elastica_video import render_elastica_video
from src.audio.elastica_audio_cinematic import generate_cinematic_elastica_audio


def print_banner():
    print("=" * 76)
    print("   CONTINUUM LAB // 03 MECANICA DE SOLIDOS: ELASTICA DE EULER NO LINEAL")
    print("   Bifurcacion Supercritica (Pitchfork) & Solucion Analitica de Jacobi")
    print("   Vertical 9:16 UHD (1080x1920 @ 60 FPS) Master Production Pipeline")
    print("=" * 76)


def run_summary():
    elastica = EulerElastica(L=1.0, E=210e9, b=0.02, h=0.003)
    print_banner()
    print(f"[*] Parametros de la Viga:")
    print(f"    - Longitud L:              {elastica.L:.3f} m")
    print(f"    - Seccion Rectangular:     {elastica.b*1e3:.1f} x {elastica.h*1e3:.1f} mm")
    print(f"    - Rigidez a Flexion EI:    {elastica.EI:.3f} N*m^2")
    print(f"    - Carga Critica Euler P_cr:{elastica.P_cr:.3f} N\n")

    print("[*] Comportamiento en Grandes Deflexiones (Solucion Eliptica):")
    print(f"    {'Angulo alpha (deg)':<18} | {'P / P_cr':<10} | {'Carga P (N)':<12} | {'Flecha dy/L':<12} | {'Acort. dx/L':<12} | {'sigma_max (MPa)':<15}")
    print("    " + "-" * 88)

    for deg in [5.0, 15.0, 30.0, 45.0, 60.0, 75.0, 85.0]:
        sol = elastica.solve_exact(alpha_rad=deg * (3.141592653589793 / 180.0))
        print(f"    {deg:<18.1f} | {sol['P_ratio']:<10.4f} | {sol['P']:<12.2f} | {sol['delta_y_max']/elastica.L:<12.4f} | {sol['delta_x']/elastica.L:<12.4f} | {sol['sigma_max_MPa']:<15.1f}")
    print("=" * 88 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Pipeline de la Elástica de Euler No Lineal")
    parser.add_argument("--benchmark", action="store_true", help="Generar libro Excel (.xlsx)")
    parser.add_argument("--visuals", action="store_true", help="Renderizar póster científico PNG")
    parser.add_argument("--audio", action="store_true", help="Generar audio cinematográfico WAV")
    parser.add_argument("--video", action="store_true", help="Renderizar videos 9:16 60 FPS (ES & EN)")
    parser.add_argument("--lang", type=str, default="ALL", choices=["ES", "EN", "ALL"], help="Idioma de video")
    parser.add_argument("--all", action="store_true", help="Ejecutar pipeline completo")

    args = parser.parse_args()

    if not (args.benchmark or args.visuals or args.audio or args.video or args.all):
        args.all = True

    run_summary()

    # Destination directories in RENDERS and local output
    renders_video_dir = RENDERS_DIR / "videos"
    renders_capturas_dir = RENDERS_DIR / "extra" / "capturas"
    renders_audio_dir = RENDERS_DIR / "extra" / "audio"
    
    os.makedirs(renders_video_dir, exist_ok=True)
    os.makedirs(renders_capturas_dir, exist_ok=True)
    os.makedirs(renders_audio_dir, exist_ok=True)

    # 1. Benchmark Excel
    if args.benchmark or args.all:
        excel_path = RENDERS_DIR / "Euler_Elastica_Nonlinear_Benchmark.xlsx"
        generate_elastica_excel_benchmark(str(excel_path))
        print(f"[+] Benchmark Excel generado: {excel_path}")

    # 2. Hero Poster
    if args.visuals or args.all:
        poster_path = renders_capturas_dir / "euler_elastica_hero.png"
        render_elastica_hero_poster(str(poster_path))
        print(f"[+] Póster científico renderizado: {poster_path}")

    # 3. Audio Cinematográfico
    audio_path = renders_audio_dir / "euler_elastica_cinematic_audio.wav"
    if args.audio or args.video or args.all:
        generate_cinematic_elastica_audio(str(audio_path), duration=16.0)
        print(f"[+] Audio cinematográfico generado: {audio_path}")

    # 4. Master 9:16 Video Rendering
    if args.video or args.all:
        langs = ["ES", "EN"] if args.lang == "ALL" else [args.lang]

        for lang in langs:
            if lang == "ES":
                vid_name = "Pandeo No Lineal Elastica de Euler ES.mp4"
                hero_name = "euler_elastica_hero_es.png"
            else:
                vid_name = "Nonlinear Euler Elastica Buckling EN.mp4"
                hero_name = "euler_elastica_hero_en.png"

            out_vid = renders_video_dir / vid_name
            out_hero = renders_capturas_dir / hero_name

            print(f"\n---> Iniciando renderizado de video [{lang}]: {vid_name}")
            render_elastica_video(
                output_mp4=str(out_vid),
                audio_wav=str(audio_path),
                duration=16.0,
                fps=60,
                lang=lang,
                hero_capture_path=str(out_hero)
            )

    print("\n[OK] Pipeline de la Elástica de Euler completado con éxito total.\n")


if __name__ == "__main__":
    main()
