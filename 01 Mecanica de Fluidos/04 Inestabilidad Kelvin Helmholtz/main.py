"""
Continuum Lab - Kelvin-Helmholtz Instability Master CLI & Pipeline
Module: 01 Mecanica de Fluidos / 04 Inestabilidad Kelvin Helmholtz
File: main.py

Usage:
    python main.py --all
    python main.py --render-es
    python main.py --render-en
    python main.py --audio
    python main.py --excel
    python main.py --hero
"""

import os
import sys
import argparse
from pathlib import Path

# Add module to sys.path
module_dir = Path(__file__).resolve().parent
project_dir = module_dir.parent.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.audio.kelvin_helmholtz_audio import synthesize_khi_soundtrack
from src.physics.export_excel_benchmark import create_kelvin_helmholtz_excel_benchmark
from src.visualization.render_kelvin_helmholtz import render_khi_video


def run_pipeline(
    render_es: bool = True,
    render_en: bool = True,
    audio: bool = True,
    excel: bool = True,
    hero: bool = True
):
    renders_base = project_dir / "RENDERS" / "16 Inestabilidad Kelvin Helmholtz"
    videos_dir = renders_base / "videos"
    capturas_dir = renders_base / "extra" / "capturas"
    benchmarks_dir = renders_base / "benchmarks"
    cover_dir = renders_base / "cover"

    for d in [videos_dir, capturas_dir, benchmarks_dir, cover_dir]:
        d.mkdir(parents=True, exist_ok=True)

    audio_wav = str(videos_dir / "khi_audio.wav")
    excel_path = str(benchmarks_dir / "Inestabilidad_Kelvin_Helmholtz_Benchmark.xlsx")
    video_es = str(videos_dir / "Inestabilidad Kelvin Helmholtz ES.mp4")
    video_en = str(videos_dir / "Kelvin Helmholtz Instability EN.mp4")
    hero_es = str(capturas_dir / "kelvin_helmholtz_hero.png")
    hero_en = str(capturas_dir / "kelvin_helmholtz_hero_en.png")
    cover_es = str(cover_dir / "cover_kelvin_helmholtz_es_1080x1920.png")
    cover_en = str(cover_dir / "cover_kelvin_helmholtz_en_1080x1920.png")

    print("\n" + "=" * 70)
    print("CONTINUUM LAB // KELVIN-HELMHOLTZ MASTER EXECUTION PIPELINE")
    print("=" * 70)

    # 1. Synthesize Audio
    if audio or not os.path.exists(audio_wav):
        print("\n[1/4] Synthesizing 44.1 kHz procedural hydrodynamic soundtrack...")
        synthesize_khi_soundtrack(audio_wav, duration=14.0)
        print(f"[OK] Audio ready: {audio_wav}")

    # 2. Dynamic Excel Benchmark
    if excel:
        print("\n[2/4] Generating dynamic Excel benchmark model (.xlsx)...")
        create_kelvin_helmholtz_excel_benchmark(excel_path)
        print(f"[OK] Excel benchmark ready: {excel_path}")

    # 3. Render Spanish Master Video
    if render_es:
        print("\n[3/4] Rendering Spanish Master Video (1080x1920 @ 60 FPS)...")
        render_khi_video(
            output_mp4=video_es,
            audio_wav=audio_wav,
            lang="ES",
            duration=14.0,
            fps=60,
            hero_capture_path=hero_es
        )
        # Also copy hero to cover directory
        if os.path.exists(hero_es):
            import shutil
            shutil.copy2(hero_es, cover_es)

    # 4. Render English Master Video
    if render_en:
        print("\n[4/4] Rendering English Master Video (1080x1920 @ 60 FPS)...")
        render_khi_video(
            output_mp4=video_en,
            audio_wav=audio_wav,
            lang="EN",
            duration=14.0,
            fps=60,
            hero_capture_path=hero_en
        )
        if os.path.exists(hero_en):
            import shutil
            shutil.copy2(hero_en, cover_en)

    print("\n" + "=" * 70)
    print("KELVIN-HELMHOLTZ SIMULATION SUITE COMPLETED SUCCESSFULLY!")
    print(f"Videos:    {video_es}")
    print(f"           {video_en}")
    print(f"Excel:     {excel_path}")
    print(f"Covers:    {hero_es}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kelvin-Helmholtz Instability Simulation Pipeline")
    parser.add_argument("--all", action="store_true", help="Execute complete pipeline (audio, excel, videos, covers)")
    parser.add_argument("--render-es", action="store_true", help="Render Spanish video")
    parser.add_argument("--render-en", action="store_true", help="Render English video")
    parser.add_argument("--audio", action="store_true", help="Synthesize procedural audio")
    parser.add_argument("--excel", action="store_true", help="Generate Excel benchmark")
    parser.add_argument("--hero", action="store_true", help="Generate hero covers")
    args = parser.parse_args()

    if args.all or not any([args.render_es, args.render_en, args.audio, args.excel, args.hero]):
        run_pipeline(render_es=True, render_en=True, audio=True, excel=True, hero=True)
    else:
        run_pipeline(
            render_es=args.render_es,
            render_en=args.render_en,
            audio=args.audio,
            excel=args.excel,
            hero=args.hero
        )
