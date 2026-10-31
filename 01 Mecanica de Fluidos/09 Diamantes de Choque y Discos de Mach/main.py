"""
Master CLI y Pipeline de Ejecución: Continuum Lab // 01 Mecánica de Fluidos
09 Diamantes de Choque y Discos de Mach (Compressible Aerodynamics & Mach Reflection)
"""

import os
import sys
import argparse
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent.parent
RENDERS_DIR = PROJECT_DIR / "RENDERS" / "25 Diamantes de Choque y Discos de Mach Aerodinamicos"

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.physics.shock_diamonds_sim import ShockDiamondsSim
from src.physics.export_excel_benchmark import generate_shock_diamonds_excel_benchmark
from src.visualization.render_shock_diamonds_poster import render_shock_diamonds_poster
from src.visualization.render_shock_diamonds_video import render_shock_diamonds_video
from src.audio.shock_diamonds_audio import generate_shock_diamonds_audio


def print_banner():
    print("=" * 85)
    print("   CONTINUUM LAB // 01 MECÁNICA DE FLUIDOS: DIAMANTES DE CHOQUE Y DISCOS DE MACH")
    print("   Compressible Gas Dynamics, Prandtl-Meyer Expansion & Extreme Reignition (T > 2,850 K)")
    print("   Vertical 9:16 UHD (1080x1920 @ 60 FPS) Master Cinematic Pipeline")
    print("=" * 85)


def run_summary():
    sim = ShockDiamondsSim()
    print_banner()
    print("[*] Parámetros Gasdinámicos y Termodinámicos Iniciales:")
    print(f"    - Presión de Cámara p_0:         {sim.p0/1e6:.2f} MPa ({sim.p0/101325.0:.1f} atm)")
    print(f"    - Temperatura de Cámara T_0:     {sim.T0:,.0f} K")
    print(f"    - Presión Atmosférica p_a:       {sim.pa/1000.0:.2f} kPa")
    print(f"    - Mach de Salida de Tobera M_e:  {sim.M_exit:.2f}")
    print(f"    - Diámetro de Salida de Tobera:  {sim.d_exit:.2f} m")
    print(f"    - Espaciado Prandtl-Pack L_d:    {sim.L_diamond_nominal:.2f} m\n")

    print("[*] Hitos Cinemáticos y Termodinámicos a lo largo del Ciclo de 16.0s:")
    print(f"    {'Tiempo t (s)':<14} | {'p0 (MPa)':<12} | {'NPR':<10} | {'pe / pa':<10} | {'L_d (m)':<10} | {'Disco Mach (cm)':<18} | {'T_core (K)':<14} | {'Estado':<20}")
    print("    " + "-" * 115)

    for t_test in [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0]:
        st = sim.get_dynamic_state(t_test)
        if st["T_mach_disk_core"] > 2750:
            state_str = "REIGNICIÓN INCANDESCENTE"
        elif st["is_mach_reflection"]:
            state_str = "DISCO DE MACH ACTIVO"
        else:
            state_str = "EXPANSIÓN REGULAR"

        print(f"    {t_test:<14.2f} | {st['p0']/1e6:<12.2f} | {st['NPR']:<10.1f} | {st['rp']:<10.2f} | {st['L_diamond']:<10.2f} | {st['mach_disk_radius']*100:<18.1f} | {st['T_mach_disk_core']:<14,.0f} | {state_str:<20}")
    print("=" * 115 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Pipeline de Diamantes de Choque y Discos de Mach")
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
        excel_path = RENDERS_DIR / "Supersonic_Shock_Diamonds_Mach_Disk_Benchmark.xlsx"
        generate_shock_diamonds_excel_benchmark(str(excel_path))

    # 2. Hero Poster 16:9
    if args.visuals or args.all:
        poster_path = renders_capturas_dir / "shock_diamonds_poster.png"
        render_shock_diamonds_poster(str(poster_path))

    # 3. Audio Cinematográfico
    audio_path = renders_audio_dir / "shock_diamonds_cinematic_audio.wav"
    if args.audio or args.video or args.all:
        generate_shock_diamonds_audio(str(audio_path), duration=16.0)

    # 4. Master 9:16 Video Rendering (ES & EN)
    if args.video or args.all:
        langs = ["ES", "EN"] if args.lang == "ALL" else [args.lang]

        for lang in langs:
            vid_name = "Diamantes Choque y Discos de Mach ES.mp4" if lang == "ES" else "Supersonic Shock Diamonds and Mach Disks EN.mp4"
            hero_name = "shock_diamonds_hero_es.png" if lang == "ES" else "shock_diamonds_hero_en.png"

            out_vid = renders_video_dir / vid_name
            out_hero = renders_capturas_dir / hero_name

            print(f"\n---> Iniciando renderizado de video cinematográfico [{lang}]: {vid_name}")
            render_shock_diamonds_video(
                output_mp4=str(out_vid),
                audio_wav=str(audio_path),
                duration=16.0,
                fps=60,
                lang=lang,
                hero_capture_path=str(out_hero)
            )

    print("\n[OK] Pipeline de Diamantes de Choque y Discos de Mach completado con éxito total.\n")


if __name__ == "__main__":
    main()
