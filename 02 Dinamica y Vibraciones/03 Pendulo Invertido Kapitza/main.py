"""
Continuum Lab - Dinamica y Vibraciones
03 Pendulo Invertido de Kapitza
CLI Runner y Suite de Generacion
"""

import sys
import argparse
import subprocess
from pathlib import Path

# Configurar stdout para evitar errores de codificación en consolas de Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Añadir directorio raíz al sys.path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from src.physics import KapitzaConfig, solve_kapitza_dynamics, compute_effective_potential


def print_banner():
    banner = r"""
  ╔════════════════════════════════════════════════════════════════════╗
  ║                 CONTINUUM LAB • DINÁMICA AVANZADA                 ║
  ║             SIMULACIÓN VECTORIAL: PÉNDULO DE KAPITZA               ║
  ║         Estabilización Asintótica por Excitación Rápida            ║
  ╚════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def show_physics_info():
    config = KapitzaConfig()
    omega = 2.0 * 3.141592653589793 * config.f
    kapitza_lhs = (config.a * omega) ** 2
    kapitza_rhs = 2.0 * config.g * config.L
    ratio = kapitza_lhs / kapitza_rhs
    f_crit = (1.0 / (2.0 * 3.141592653589793)) * (2.0 * config.g * config.L) ** 0.5 / config.a
    basin_rad = (1.0 / ratio)
    import math
    basin_deg = math.degrees(math.acos(-basin_rad))

    print("=" * 68)
    print(" PARÁMETROS FÍSICOS Y DINÁMICA NO LINEAL DE KAPITZA-BOGOLIUBOV")
    print("=" * 68)
    print(f" Masa del péndulo (m)          : {config.m:.2f} kg")
    print(f" Longitud efectiva (L)         : {config.L:.2f} m")
    print(f" Aceleración gravitatoria (g)  : {config.g:.2f} m/s²")
    print(f" Coeficiente amortiguamiento (b): {config.b:.2f} s⁻¹")
    print("-" * 68)
    print(f" Amplitud vibración soporte (a): {config.a * 100:.1f} cm ({config.a:.4f} m)")
    print(f" Frecuencia excitación (f)     : {config.f:.1f} Hz (ω = {omega:.2f} rad/s)")
    print(f" Aceleración máxima soporte    : a·ω² = {config.a * omega**2:.2f} m/s² ({config.a * omega**2 / config.g:.1f} g)")
    print("-" * 68)
    print(f" Condición de Estabilidad      : (a·ω)² > 2·g·L")
    print(f"   Lado Izquierdo (a·ω)²       : {kapitza_lhs:.3f} m²/s²")
    print(f"   Lado Derecho 2·g·L          : {kapitza_rhs:.3f} m²/s²")
    print(f"   Ratio de Seguridad R        : {ratio:.2f}x (¡Estricto Superávit!)")
    print(f"   Frecuencia Crítica f_crit   : {f_crit:.2f} Hz (Operando al {config.f / f_crit * 100:.1f}%)")
    half_basin = 180.0 - basin_deg
    print(f" Cuenca de Atracción Angular   : θ ∈ [{180.0 - half_basin:.1f}°, {180.0 + half_basin:.1f}°] (Semiancho: ±{half_basin:.1f}°)")
    print("=" * 68)


def run_tests():
    print("\n[+] Ejecutando suite de pruebas automatizadas con pytest...")
    res = subprocess.run([sys.executable, "-m", "pytest", "-v", "tests/test_kapitza.py"])
    return res.returncode == 0


def render_scene(quality="qh"):
    quality_names = {"qh": "1080p60 Ultra-HD", "ql": "720p30 Preview"}
    print(f"\n[+] Renderizando simulación vectorial Manim ({quality_names.get(quality, quality)})...")
    cmd = [sys.executable, "-m", "manim", f"-{quality}", "src/kapitza_scene.py", "KapitzaPendulumScene"]
    res = subprocess.run(cmd)
    return res.returncode == 0


def generate_snapshots():
    print("\n[+] Generando snapshots de alta resolución para las 3 fases...")
    snapshots = [
        "KapitzaPhase1Snapshot",
        "KapitzaPhase2Snapshot",
        "KapitzaPhase3Snapshot",
    ]
    all_ok = True
    for snap in snapshots:
        print(f"  -> Renderizando {snap}...")
        cmd = [sys.executable, "-m", "manim", "-s", "-qh", "src/kapitza_scene.py", snap]
        res = subprocess.run(cmd)
        if res.returncode != 0:
            all_ok = False
    return all_ok


def main():
    print_banner()
    parser = argparse.ArgumentParser(description="Continuum Lab - Simulación de Péndulo Invertido de Kapitza")
    parser.add_argument("--info", action="store_true", help="Muestra parámetros físicos y verificación analítica")
    parser.add_argument("--test", action="store_true", help="Ejecuta la suite de pruebas unitarias pytest")
    parser.add_argument("--render", action="store_true", help="Renderiza el video maestro 1080p60 Ultra-HD")
    parser.add_argument("--render-preview", action="store_true", help="Renderiza preview rápida 720p30")
    parser.add_argument("--snapshots", action="store_true", help="Genera capturas PNG de las 3 fases")
    parser.add_argument("--all", action="store_true", help="Ejecuta pruebas, genera snapshots y renderiza video maestro")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        show_physics_info()
        print("\nUso rápido:")
        print("  python main.py --test            -> Ejecutar pruebas físicas")
        print("  python main.py --snapshots       -> Generar capturas de las 3 fases")
        print("  python main.py --render-preview  -> Renderizar video 720p30")
        print("  python main.py --render          -> Renderizar video 1080p60 maestro")
        print("  python main.py --all             -> Pipeline completo")
        return

    if args.info:
        show_physics_info()

    if args.test or args.all:
        if not run_tests():
            print("[-] Error: Fallaron las pruebas unitarias.")
            sys.exit(1)

    if args.snapshots or args.all:
        if not generate_snapshots():
            print("[-] Error generando snapshots.")
            sys.exit(1)

    if args.render_preview:
        if not render_scene("ql"):
            print("[-] Error renderizando preview 720p30.")
            sys.exit(1)

    if args.render or args.all:
        if not render_scene("qh"):
            print("[-] Error renderizando video maestro 1080p60.")
            sys.exit(1)

    print("\n[✔] Proceso completado exitosamente en Continuum Lab.")


if __name__ == "__main__":
    main()
