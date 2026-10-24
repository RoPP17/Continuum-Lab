"""
Master CLI y Pipeline de Ejecución: Continuum Lab // 01 Mecánica de Fluidos
07 Colisión de Anillos de Vórtice y Cascada de Reconexión (Biot-Savart & Inestabilidad de Widnall)
"""

import os
import sys
import argparse
from pathlib import Path

# Paths setup
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent.parent
RENDERS_DIR = PROJECT_DIR / "RENDERS" / "23 Colision de Anillos de Vortice y Cascada de Reconexion"

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.physics.vortex_collision_sim import VortexRingsCollisionSim
from src.physics.export_excel_benchmark import generate_vortex_excel_benchmark
from src.visualization.render_vortex_poster import render_vortex_hero_poster
from src.visualization.render_vortex_collision import render_vortex_collision_video
from src.audio.vortex_collision_audio import generate_vortex_collision_audio


def print_banner():
    print("=" * 80)
    print("   CONTINUUM LAB // 01 MECANICA DE FLUIDOS: COLISIÓN DE ANILLOS DE VÓRTICE")
    print("   Biot-Savart, Inestabilidad de Widnall (m = 12) & Reconexión Topológica")
    print("   Vertical 9:16 UHD (1080x1920 @ 60 FPS) Master Cinematic Pipeline")
    print("=" * 80)


def run_summary():
    sim = VortexRingsCollisionSim()
    print_banner()
    print("[*] Parámetros Hidrodinámicos Iniciales:")
    print(f"    - Radio Inicial del Anillo R₀:   {sim.R0:.3f} m")
    print(f"    - Radio del Núcleo a₀:           {sim.a0*1e3:.1f} mm")
    print(f"    - Circulación de Kelvin Γ₀:      {sim.Gamma0:.2f} m^2/s")
    print(f"    - Velocidad Auto-Inducida U_0:   {sim._kelvin_hicks_speed(sim.R0, sim.a0):.3f} m/s")
    print(f"    - Modo Azimutal Dominante:       m = {sim.m_mode} ondas Widnall\n")

    print("[*] Hitos Cinemáticos y Dinámica de Vorticidad:")
    print(f"    {'Tiempo t (s)':<14} | {'z_sep (cm)':<12} | {'Radio R (m)':<12} | {'Expansión R/R₀':<15} | {'Vorticidad ω (s⁻¹)':<20} | {'Estado':<20}")
    print("    " + "-" * 100)

    for t_test in [0.0, 2.0, 3.5, 5.0, 5.8, 7.5, 10.0, 13.0, 16.0]:
        st = sim.get_state(t_test)
        state_str = "RECONEXIÓN (CROWN)" if st["is_reconnected"] else "APROXIMACIÓN & STRAIN"
        print(f"    {t_test:<14.1f} | {2.0*st['z']*100:<12.1f} | {st['R']:<12.3f} | {st['R_ratio']:<15.2f} | {st['omega_max']:<20.1f} | {state_str:<20}")
    print("=" * 100 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Pipeline de Colisión de Anillos de Vórtice")
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
        excel_path = RENDERS_DIR / "Vortex_Rings_Collision_Benchmark.xlsx"
        generate_vortex_excel_benchmark(str(excel_path))

    # 2. Hero Poster 16:9
    if args.visuals or args.all:
        poster_path = renders_capturas_dir / "vortex_collision_poster.png"
        render_vortex_hero_poster(str(poster_path))

    # 3. Audio Cinematográfico
    audio_path = renders_audio_dir / "vortex_collision_cinematic_audio.wav"
    if args.audio or args.video or args.all:
        generate_vortex_collision_audio(str(audio_path), duration=16.0)

    # 4. Master 9:16 Video Rendering (ES & EN)
    if args.video or args.all:
        langs = ["ES", "EN"] if args.lang == "ALL" else [args.lang]

        for lang in langs:
            vid_name = "Colision Anillos de Vortice ES.mp4" if lang == "ES" else "Vortex Rings Collision EN.mp4"
            hero_name = "vortex_collision_hero_es.png" if lang == "ES" else "vortex_collision_hero_en.png"

            out_vid = renders_video_dir / vid_name
            out_hero = renders_capturas_dir / hero_name

            print(f"\n---> Iniciando renderizado de video cinematográfico [{lang}]: {vid_name}")
            render_vortex_collision_video(
                output_mp4=str(out_vid),
                audio_wav=str(audio_path),
                duration=16.0,
                fps=60,
                lang=lang,
                hero_capture_path=str(out_hero)
            )

    print("\n[OK] Pipeline de Colisión de Anillos de Vórtice completado con éxito total.\n")


if __name__ == "__main__":
    main()
