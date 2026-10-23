"""
Continuum Lab - Rayleigh-Taylor Instability Master CLI & Pipeline
Module: 01 Mecanica de Fluidos / 06 Inestabilidad Rayleigh Taylor
File: main.py

Usage:
    python main.py --all
    python main.py --render-es
    python main.py --render-en
    python main.py --audio
    python main.py --excel
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

module_dir = Path(__file__).resolve().parent
project_dir = module_dir.parent.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.audio.rayleigh_taylor_audio import synthesize_rayleigh_taylor_soundtrack
from src.physics.export_excel_benchmark import create_rayleigh_taylor_excel_benchmark
from src.visualization.render_rayleigh_taylor import render_rayleigh_taylor_video


def run_pipeline(
    render_es: bool = True,
    render_en: bool = True,
    audio: bool = True,
    excel: bool = True,
):
    renders_base = project_dir / "RENDERS" / "21 Inestabilidad Rayleigh Taylor y Plumas Gravitatorias"
    videos_dir = renders_base / "videos"
    capturas_dir = renders_base / "extra" / "capturas"
    extra_bench_dir = renders_base / "extra" / "benchmarks"
    benchmarks_dir = renders_base / "benchmarks"
    cover_dir = renders_base / "cover"

    for d in [videos_dir, capturas_dir, extra_bench_dir, benchmarks_dir, cover_dir]:
        d.mkdir(parents=True, exist_ok=True)

    audio_wav = str(videos_dir / "rayleigh_taylor_audio.wav")
    excel_path = str(benchmarks_dir / "Inestabilidad_Rayleigh_Taylor_Benchmark.xlsx")
    extra_excel_path = str(extra_bench_dir / "Inestabilidad_Rayleigh_Taylor_Benchmark.xlsx")
    video_es = str(videos_dir / "Inestabilidad Rayleigh Taylor ES.mp4")
    video_en = str(videos_dir / "Rayleigh Taylor Instability EN.mp4")
    hero_es = str(capturas_dir / "rayleigh_taylor_hero.png")
    hero_en = str(capturas_dir / "rayleigh_taylor_hero_en.png")
    cover_es = str(cover_dir / "cover_rayleigh_taylor_es_1080x1920.png")
    cover_en = str(cover_dir / "cover_rayleigh_taylor_en_1080x1920.png")

    print("\n" + "=" * 74)
    print("CONTINUUM LAB // RAYLEIGH-TAYLOR INSTABILITY MASTER PIPELINE (#21)")
    print("=" * 74)

    # 1. Synthesize Procedural Stereo Audio
    if audio or not os.path.exists(audio_wav):
        print("\n[1/4] Synthesizing 44.1 kHz stereo Rayleigh-Taylor soundtrack...")
        synthesize_rayleigh_taylor_soundtrack(audio_wav, duration=16.0)

    # 2. Generate Dynamic Excel Benchmark
    if excel:
        print("\n[2/4] Generating dynamic Excel benchmark model (.xlsx)...")
        create_rayleigh_taylor_excel_benchmark(excel_path)
        shutil.copy2(excel_path, extra_excel_path)

    # 3. Render Spanish Master Video
    if render_es:
        print("\n[3/4] Rendering Spanish Master Video (1080x1920 @ 60 FPS)...")
        render_rayleigh_taylor_video(
            output_mp4=video_es,
            audio_wav=audio_wav,
            lang="ES",
            duration=16.0,
            fps=60,
            hero_capture_path=hero_es
        )
        if os.path.exists(hero_es):
            shutil.copy2(hero_es, cover_es)

    # 4. Render English Master Video
    if render_en:
        print("\n[4/4] Rendering English Master Video (1080x1920 @ 60 FPS)...")
        render_rayleigh_taylor_video(
            output_mp4=video_en,
            audio_wav=audio_wav,
            lang="EN",
            duration=16.0,
            fps=60,
            hero_capture_path=hero_en
        )
        if os.path.exists(hero_en):
            shutil.copy2(hero_en, cover_en)

    print("\n" + "=" * 74)
    print("RAYLEIGH-TAYLOR INSTABILITY SUITE COMPLETED SUCCESSFULLY!")
    print(f"Videos: {video_es}")
    print(f"        {video_en}")
    print(f"Excel:  {excel_path}")
    print(f"Covers: {hero_en}")
    print("=" * 74 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rayleigh-Taylor Instability Master Pipeline")
    parser.add_argument("--all", action="store_true", help="Run full pipeline")
    parser.add_argument("--render-es", action="store_true", help="Render Spanish video")
    parser.add_argument("--render-en", action="store_true", help="Render English video")
    parser.add_argument("--audio", action="store_true", help="Synthesize audio")
    parser.add_argument("--excel", action="store_true", help="Generate Excel benchmark")
    args = parser.parse_args()

    if args.all or not any([args.render_es, args.render_en, args.audio, args.excel]):
        run_pipeline(render_es=True, render_en=True, audio=True, excel=True)
    else:
        run_pipeline(
            render_es=args.render_es,
            render_en=args.render_en,
            audio=args.audio,
            excel=args.excel
        )
