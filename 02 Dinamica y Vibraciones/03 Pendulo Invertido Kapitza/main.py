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
    res_flags = ["-r", "1080,1920", "--fps", "60"] if quality == "qh" else ["-r", "720,1280", "--fps", "30"]
    renders_dir = ROOT_DIR.parent.parent / "RENDERS" / "11 Pendulo Invertido Kapitza" / "videos"
    renders_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = renders_dir / "temp_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # 1. Procedural Audio Synthesis (Melody + Physical SFX)
    from src.audio.kapitza_audio_synth import synthesize_kapitza_audio
    import imageio_ffmpeg
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    temp_audio = str(renders_dir / "kapitza_audio_temp.wav")
    print(f"\n[+] Sintetizando audio procedural con melodía cinemática y SFX mecánicos (15.0s)...")
    synthesize_kapitza_audio(duration=15.0, fs=44100, output_path=temp_audio)

    tasks = [
        ("KapitzaPendulumSceneES", "Pendulo Invertido Kapitza ES.mp4", "Español (ES)"),
        ("KapitzaPendulumSceneEN", "Kapitza Inverted Pendulum EN.mp4", "English (EN)"),
    ]

    for scene_cls, out_name, lang_desc in tasks:
        target_mp4 = renders_dir / out_name
        temp_out = f"temp_{out_name}"
        print(f"\n[+] Renderizando simulación ({lang_desc}, {quality_names.get(quality, quality)})...")
        cmd = [
            sys.executable, "-m", "manim",
            *res_flags,
            "src/kapitza_scene.py", scene_cls,
            "--media_dir", str(cache_dir),
            "-o", temp_out,
        ]
        res = subprocess.run(cmd, cwd=str(ROOT_DIR))
        if res.returncode != 0:
            print(f"[-] Error: Manim falló para {scene_cls} con código {res.returncode}")
            return False

        rendered = list(cache_dir.glob(f"**/{temp_out}"))
        if not rendered:
            rendered = list(cache_dir.glob(f"**/*{temp_out}*"))
        if rendered:
            raw_video = str(rendered[0])
            print(f"[+] Multiplexando audio + video -> {target_mp4}")
            cmd_mux = [
                ffmpeg_bin, "-y", "-i", raw_video, "-i", temp_audio,
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(target_mp4)
            ]
            subprocess.run(cmd_mux, check=True)
            print(f"[✔] Video con audio guardado en: {target_mp4}")
        else:
            print(f"[-] Advertencia: No se encontró {temp_out} en cache.")
            return False

    import shutil
    import os
    if os.path.exists(temp_audio):
        os.remove(temp_audio)
    shutil.rmtree(str(cache_dir), ignore_errors=True)
    print("\n[✔] Todos los videos del Péndulo de Kapitza (ES y EN con audio) fueron compilados exitosamente.")
    return True


def generate_snapshots():
    print("\n[+] Generando snapshots de alta resolución 1080x1920 para las 3 fases y covers...")
    output_base = ROOT_DIR.parent.parent / "RENDERS" / "11 Pendulo Invertido Kapitza"
    cover_dir = output_base / "cover"
    capturas_dir = output_base / "extra" / "capturas"
    cover_dir.mkdir(parents=True, exist_ok=True)
    capturas_dir.mkdir(parents=True, exist_ok=True)

    cache_dir = output_base / "temp_snap_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    snapshots = [
        ("KapitzaPhase1Snapshot", "fase1_estabilidad_kapitza.png", cover_dir / "cover_kapitza_es_1080x1920.png"),
        ("KapitzaPhase1SnapshotEN", "fase1_stability_kapitza_en.png", cover_dir / "cover_kapitza_en_1080x1920.png"),
        ("KapitzaPhase2Snapshot", "fase2_perturbacion_kapitza.png", None),
        ("KapitzaPhase3Snapshot", "fase3_colapso_kapitza.png", None),
    ]

    import shutil
    for snap_cls, out_png, cover_dest in snapshots:
        print(f"  -> Renderizando {snap_cls} (1080x1920)...")
        cmd = [
            sys.executable, "-m", "manim",
            "-s", "-r", "1080,1920", "--fps", "60",
            "src/kapitza_scene.py", snap_cls,
            "--media_dir", str(cache_dir),
            "-o", out_png
        ]
        res = subprocess.run(cmd, cwd=str(ROOT_DIR))
        if res.returncode != 0:
            print(f"[-] Error renderizando snapshot {snap_cls}")
            return False

        found = list(cache_dir.glob(f"**/{out_png}"))
        if not found:
            found = list(cache_dir.glob(f"**/*{out_png}*"))
        if found:
            src_file = found[0]
            # Copy to extra/capturas
            target_cap = capturas_dir / out_png
            shutil.copy2(src_file, target_cap)
            print(f"     [✔] Captura guardada en: {target_cap.name}")
            if cover_dest:
                shutil.copy2(src_file, cover_dest)
                print(f"     [✔] Cover maestro guardado en: {cover_dest.name}")

    shutil.rmtree(str(cache_dir), ignore_errors=True)
    print("\n[✔] Todos los snapshots y covers 1080x1920 fueron generados exitosamente.")
    return True


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
