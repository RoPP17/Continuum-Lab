"""
Master CLI y Pipeline de Ejecución: Continuum Lab // 01 Mecánica de Fluidos
08 Colapso de Cavitación y Sonoluminiscencia (Rayleigh-Plesset, Keller-Miksis & Star-in-a-jar)
"""

import os
import sys
import argparse
from pathlib import Path

# Paths setup
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent.parent
RENDERS_DIR = PROJECT_DIR / "RENDERS" / "24 Colapso de Cavitacion y Sonoluminiscencia"

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.physics.cavitation_sim import CavitationBubbleSim
from src.physics.export_excel_benchmark import generate_cavitation_excel_benchmark
from src.visualization.render_cavitation_poster import render_cavitation_hero_poster
from src.visualization.render_cavitation_video import render_cavitation_video
from src.audio.cavitation_audio import generate_cavitation_audio


def print_banner():
    print("=" * 80)
    print("   CONTINUUM LAB // 01 MECÁNICA DE FLUIDOS: CAVITACIÓN & SONOLUMINISCENCIA")
    print("   Keller-Miksis, Bremsstrahlung Térmico (T > 18,000 K) & Micro-Jet Supersónico")
    print("   Vertical 9:16 UHD (1080x1920 @ 60 FPS) Master Cinematic Pipeline")
    print("=" * 80)


def run_summary():
    sim = CavitationBubbleSim()
    print_banner()
    print("[*] Parámetros Hidrodinámicos y Termodinámicos Iniciales:")
    print(f"    - Radio Inicial R_0:             {sim.R0*1e6:.1f} um")
    print(f"    - Núcleo duro van der Waals h:   {sim.h_vdw*1e6:.2f} um")
    print(f"    - Presión de gas de reposo p_g0: {sim.pg0/101325.0:.3f} atm ({sim.pg0:.1f} Pa)")
    print(f"    - Tiempo analítico de Rayleigh:  {sim.t_rayleigh*1e6:.2f} microsegundos")
    print(f"    - Frecuencia Minnaert f_M:       {sim.f_minnaert/1e3:.1f} kHz\n")

    print("[*] Hitos Cinemáticos y Termodinámicos:")
    print(f"    {'Tiempo t (s)':<14} | {'Radio R (um)':<14} | {'R / R0':<10} | {'Mach M':<10} | {'Temp Core (K)':<15} | {'Presión Gas (atm)':<20} | {'Estado':<20}")
    print("    " + "-" * 110)

    for t_test in [0.0, 2.0, 3.0, 5.0, 6.8, 7.20, 7.6, 9.5, 13.0, 16.0]:
        st = sim.get_state(t_test)
        if st["is_sonoluminescent"]:
            state_str = "¡SONOLUMINISCENCIA!"
        elif st["is_shock_active"]:
            state_str = "ONDA DE CHOQUE"
        elif st["mach"] > 0.5:
            state_str = "COLAPSO RÁPIDO"
        elif t_test <= 3.0:
            state_str = "EXPANSIÓN ACÚSTICA"
        else:
            state_str = "RELAJACIÓN"

        print(f"    {t_test:<14.2f} | {st['R']*1e6:<14.1f} | {st['R_ratio']:<10.2f} | {st['mach']:<10.2f} | {st['T_kelvin']:<15,.0f} | {st['P_gas_atm']:<20,.0f} | {state_str:<20}")
    print("=" * 110 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Pipeline de Colapso de Cavitación y Sonoluminiscencia")
    parser.add_argument("--benchmark", action="store_true", help="Generar libro Excel (.xlsx)")
    parser.add_argument("--visuals", action="store_true", help="Renderizar póster científico 16:9")
    parser.add_argument("--audio", action="store_true", help="Generar audio cinematográfico WAV")
    parser.add_argument("--video", action="store_true", help="Renderizar videos 9:16 60 FPS (ES & EN)")
    parser.add_argument("--lang", type=str, default="ALL", choices=["ES", "EN", "ALL"], help="Idioma de video")
    parser.add_argument("--all", action="store_true", help="Ejecutar pipeline completo")

    args = parser.parse_args()

    if not (args.benchmark or args.visuals or args.audio or args.video or args.all):
        args.all = True

    run_summary()

    renders_video_dir = RENDERS_DIR / "videos"
    renders_capturas_dir = RENDERS_DIR / "extra" / "capturas"
    renders_audio_dir = RENDERS_DIR / "extra" / "audio"

    os.makedirs(renders_video_dir, exist_ok=True)
    os.makedirs(renders_capturas_dir, exist_ok=True)
    os.makedirs(renders_audio_dir, exist_ok=True)

    # 1. Benchmark Excel
    if args.benchmark or args.all:
        excel_path = RENDERS_DIR / "Cavitation_Sonoluminescence_Benchmark.xlsx"
        generate_cavitation_excel_benchmark(str(excel_path))

    # 2. Hero Poster 16:9
    if args.visuals or args.all:
        poster_path = renders_capturas_dir / "cavitation_poster.png"
        render_cavitation_hero_poster(str(poster_path))

    # 3. Audio Cinematográfico
    audio_path = renders_audio_dir / "cavitation_cinematic_audio.wav"
    if args.audio or args.video or args.all:
        generate_cavitation_audio(str(audio_path), duration=16.0)

    # 4. Master 9:16 Video Rendering (ES & EN)
    if args.video or args.all:
        langs = ["ES", "EN"] if args.lang == "ALL" else [args.lang]

        for lang in langs:
            vid_name = "Colapso Cavitacion y Sonoluminiscencia ES.mp4" if lang == "ES" else "Cavitation Collapse and Sonoluminescence EN.mp4"
            hero_name = "cavitation_hero_es.png" if lang == "ES" else "cavitation_hero_en.png"

            out_vid = renders_video_dir / vid_name
            out_hero = renders_capturas_dir / hero_name

            print(f"\n---> Iniciando renderizado de video cinematográfico [{lang}]: {vid_name}")
            render_cavitation_video(
                output_mp4=str(out_vid),
                audio_wav=str(audio_path),
                duration=16.0,
                fps=60,
                lang=lang,
                hero_capture_path=str(out_hero)
            )

    print("\n[OK] Pipeline de Colapso de Cavitación y Sonoluminiscencia completado con éxito total.\n")


if __name__ == "__main__":
    main()
