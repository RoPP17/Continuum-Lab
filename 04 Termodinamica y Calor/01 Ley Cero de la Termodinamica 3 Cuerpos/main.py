"""
Continuum Lab — Thermal Physics & Heat Conduction Engine
Module: 04 Termodinamica y Calor / 01 Ley Cero de la Termodinamica 3 Cuerpos
Case Study: Zeroth Law of Thermodynamics & Multi-Material Heat Diffusion
Format: 1080x1920 @ 60 FPS (9:16 Vertical Video for TikTok/Reels/Shorts)

Execution Modes:
  python main.py                # Displays analytical physical breakdown & equilibrium proof
  python main.py --render       # Renders 1080x1920 @ 60 FPS vertical video with catchy synth music
  python main.py --preview      # Fast preview render (6.0s @ 30 FPS)
  python main.py --benchmark    # Exports dynamic formula-driven Excel model (.xlsx)
  python main.py --visuals      # Generates 1080x1920 hero cover PNGs and animated GIF preview
  python main.py --test         # Runs unit test suite
  python main.py --all          # Runs benchmark, visuals, and video rendering pipeline
"""

import sys
import argparse
import subprocess
from pathlib import Path

# UTF-8 stdout configuration for Windows console
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

PROJECT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = PROJECT_DIR.parent.parent
RENDERS_DIR = WORKSPACE_ROOT / "RENDERS" / "14 Ley Cero Termodinamica 3 Cuerpos"
VIDEOS_DIR = RENDERS_DIR / "videos"
COVER_DIR = RENDERS_DIR / "cover"
BENCH_DIR = RENDERS_DIR / "benchmarks"

# Add project root to sys.path
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from src.physics.heat_zeroth_law import (
    ZerothLawThermalSimulation,
    ThermalConfig,
    COPPER,
    STAINLESS_STEEL,
    ALUMINUM,
)
from src.physics.export_benchmarks import create_zeroth_law_benchmark_workbook
from src.visualization.generate_hero_previews import generate_all_visuals
from src.visualization.render_zeroth_law_video import render_zeroth_law_video


def print_summary():
    sim = ZerothLawThermalSimulation()
    t_eq = sim.compute_analytical_equilibrium_temperature()

    print("=" * 82)
    print("      CONTINUUM LAB // TERMODINÁMICA Y TRANSFERENCIA DE CALOR")
    print("      Caso de Estudio: Ley Cero de la Termodinámica (Sistema de 3 Cuerpos)")
    print("      Fundamento Teórico: Ralph H. Fowler (1935) — Transitividad Térmica")
    print("=" * 82)
    print("\n--- 1. PROPIEDADES TERMOFÍSICAS DE LOS CUERPOS EN CONTACTO ---")
    print(f"  [CUERPO A - CALIENTE] : {COPPER.name}")
    print(f"     Conductividad k_A  : {COPPER.thermal_conductivity:6.1f} W/(m·K)")
    print(f"     Densidad rho_A     : {COPPER.density:6.1f} kg/m³")
    print(f"     Calor específico   : {COPPER.specific_heat:6.1f} J/(kg·K)")
    print(f"     Cap. Volumétrica   : {COPPER.volumetric_heat_capacity:,.0f} J/(m³·K)")
    print(f"     Temperatura T_A,0  : {sim.cfg.t_a_init:6.1f} °C (373.15 K)")
    print()
    print(f"  [CUERPO C - MEDIADOR] : {STAINLESS_STEEL.name} (Sonda Termométrica)")
    print(f"     Conductividad k_C  : {STAINLESS_STEEL.thermal_conductivity:6.1f} W/(m·K)")
    print(f"     Densidad rho_C     : {STAINLESS_STEEL.density:6.1f} kg/m³")
    print(f"     Calor específico   : {STAINLESS_STEEL.specific_heat:6.1f} J/(kg·K)")
    print(f"     Cap. Volumétrica   : {STAINLESS_STEEL.volumetric_heat_capacity:,.0f} J/(m³·K)")
    print(f"     Temperatura T_C,0  : {sim.cfg.t_c_init:6.1f} °C (298.15 K)")
    print()
    print(f"  [CUERPO B - FRÍO]    : {ALUMINUM.name}")
    print(f"     Conductividad k_B  : {ALUMINUM.thermal_conductivity:6.1f} W/(m·K)")
    print(f"     Densidad rho_B     : {ALUMINUM.density:6.1f} kg/m³")
    print(f"     Calor específico   : {ALUMINUM.specific_heat:6.1f} J/(kg·K)")
    print(f"     Cap. Volumétrica   : {ALUMINUM.volumetric_heat_capacity:,.0f} J/(m³·K)")
    print(f"     Temperatura T_B,0  : {sim.cfg.t_b_init:6.1f} °C (273.15 K)")

    print("\n--- 2. EQUILIBRIO TÉRMICO ANALÍTICO Y LEYES DE LA TERMODINÁMICA ---")
    print(f"  Temperatura de Equilibrio Global T_eq : {t_eq:6.2f} °C ({t_eq + 273.15:6.2f} K)")
    print(f"  Energía Interna Total Inicial E_0     : {sim.initial_energy/1000:,.2f} kJ")
    print("  Conservación de la Energía (1ª Ley)   : dE/dt = 0 (Conservada a nivel de máquina)")
    print("  Irreversibilidad Espontánea (2ª Ley)  : S_gen_dot = integral( k*|grad(T)|²/T² ) >= 0")
    print("  Postulado Ley Cero                    : T_A = T_C  ∧  T_B = T_C  ===>  T_A = T_B == T_eq")

    print("\n--- 3. EVOLUCIÓN NUMÉRICA ASINTÓTICA HACIA EL EQUILIBRIO ---")
    print(f"{'Paso':<8} | {'T_A media':<12} | {'T_C media':<12} | {'T_B media':<12} | {'|T_A - T_B|':<12} | {'Equilibrio %':<12}")
    print("-" * 76)
    m0 = sim.compute_metrics()
    print(f"{'t = 0.0s':<8} | {m0['t_a_mean']:<12.1f} | {m0['t_c_mean']:<12.1f} | {m0['t_b_mean']:<12.1f} | {m0['delta_ab']:<12.1f} | {m0['equilibrium_progress']*100:<12.1f}")

    for step_num in [1, 2, 4, 8, 16]:
        for _ in range(70):
            sim.step(0.015)
        m = sim.compute_metrics()
        print(f"{f't = {step_num*1.1:.1f}s':<8} | {m['t_a_mean']:<12.1f} | {m['t_c_mean']:<12.1f} | {m['t_b_mean']:<12.1f} | {m['delta_ab']:<12.1f} | {m['equilibrium_progress']*100:<12.1f}")

    print("\n[CONTINUUM LAB] Usa --render para generar el video con música, o --all para todos los entregables.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Continuum Lab — Ley Cero de la Termodinamica 3 Cuerpos"
    )
    parser.add_argument("--render", action="store_true", help="Renderizar video vertical 1080x1920 60 FPS con audio")
    parser.add_argument("--preview", action="store_true", help="Renderizar vista previa rapida (6.0s a 30 FPS)")
    parser.add_argument("--benchmark", action="store_true", help="Exportar modelo analitico dinámico de Excel (.xlsx)")
    parser.add_argument("--visuals", action="store_true", help="Generar portadas en alta resolución y GIF animado")
    parser.add_argument("--test", action="store_true", help="Ejecutar suite completa de pruebas unitarias pytest")
    parser.add_argument("--all", action="store_true", help="Ejecutar benchmark, portadas, y renderizado completo")
    return parser.parse_args()


def main():
    args = parse_args()

    # Create directories
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    BENCH_DIR.mkdir(parents=True, exist_ok=True)

    if args.test:
        test_file = PROJECT_DIR / "tests" / "test_heat_zeroth_law.py"
        print(f"\n[+] Ejecutando suite de pruebas pytest: {test_file}")
        res = subprocess.run([sys.executable, "-m", "pytest", str(test_file), "-v"])
        sys.exit(res.returncode)

    if args.benchmark or args.all:
        bench_path = BENCH_DIR / "Ley_Cero_Termodinamica_Benchmark.xlsx"
        print(f"\n[+] Generando libro de benchmark dinámico Excel: {bench_path}")
        create_zeroth_law_benchmark_workbook(str(bench_path))

    if args.visuals or args.all:
        generate_all_visuals(RENDERS_DIR)

    if args.preview:
        out_prev = VIDEOS_DIR / "preview_ley_cero_6s.mp4"
        print(f"\n[+] Renderizando vista previa rápida...")
        render_zeroth_law_video(duration=6.0, fps=30, output_mp4=str(out_prev), preview=True)
        print(f"[SUCCESS] Vista previa completada: {out_prev}")
        return

    if args.render or args.all:
        out_video = VIDEOS_DIR / "Ley Cero Termodinamica Equilibrio 3 Cuerpos ES.mp4"
        print(f"\n[+] Renderizando video oficial 1080x1920 @ 60 FPS con banda sonora cinematográfica de ciencia...")
        render_zeroth_law_video(duration=18.0, fps=60, output_mp4=str(out_video), preview=False)
        print(f"[SUCCESS] Video oficial publicado en: {out_video}")
        return

    if not (args.benchmark or args.visuals or args.render or args.preview or args.test or args.all):
        print_summary()


if __name__ == "__main__":
    main()
