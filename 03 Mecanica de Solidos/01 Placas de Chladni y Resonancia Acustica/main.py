"""
Continuum Lab - Chladni Plate Cymatics Master CLI & Pipeline
Module: 03 Mecanica de Solidos / 01 Placas de Chladni y Resonancia Acustica
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
import shutil
import argparse
from pathlib import Path

# Add module to sys.path
module_dir = Path(__file__).resolve().parent
project_dir = module_dir.parent.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.audio.chladni_audio import synthesize_chladni_soundtrack
from src.physics.export_excel_benchmark import create_chladni_excel_benchmark
from src.visualization.render_chladni import render_chladni_video


def run_pipeline(
    render_es: bool = True,
    render_en: bool = True,
    audio: bool = True,
    excel: bool = True,
    hero: bool = True
):
    renders_base = project_dir / "RENDERS" / "17 Placas de Chladni y Resonancia Acustica"
    videos_dir = renders_base / "videos"
    capturas_dir = renders_base / "extra" / "capturas"
    benchmarks_dir = renders_base / "benchmarks"
    cover_dir = renders_base / "cover"

    for d in [videos_dir, capturas_dir, benchmarks_dir, cover_dir]:
        d.mkdir(parents=True, exist_ok=True)

    audio_wav = str(videos_dir / "chladni_audio.wav")
    excel_path = str(benchmarks_dir / "Placas_de_Chladni_Benchmark.xlsx")
    video_es = str(videos_dir / "Placas de Chladni ES.mp4")
    video_en = str(videos_dir / "Chladni Plate Cymatics EN.mp4")
    hero_es = str(capturas_dir / "chladni_hero.png")
    hero_en = str(capturas_dir / "chladni_hero_en.png")
    cover_es = str(cover_dir / "cover_chladni_es_1080x1920.png")
    cover_en = str(cover_dir / "cover_chladni_en_1080x1920.png")

    print("\n" + "=" * 70)
    print("CONTINUUM LAB // CHLADNI PLATE CYMATICS MASTER PIPELINE")
    print("=" * 70)

    # 1. Synthesize Audio
    if audio or not os.path.exists(audio_wav):
        print("\n[1/4] Synthesizing 44.1 kHz procedural acoustic soundtrack...")
        synthesize_chladni_soundtrack(audio_wav, duration=18.0)
        print(f"[OK] Audio ready: {audio_wav}")

    # 2. Dynamic Excel Benchmark
    if excel:
        print("\n[2/4] Generating dynamic Excel benchmark model (.xlsx)...")
        create_chladni_excel_benchmark(excel_path)
        print(f"[OK] Excel benchmark ready: {excel_path}")

    # 3. Render Spanish Master Video
    if render_es:
        print("\n[3/4] Rendering Spanish Master Video (1080x1920 @ 60 FPS)...")
        render_chladni_video(
            output_mp4=video_es,
            audio_wav=audio_wav,
            lang="ES",
            duration=18.0,
            fps=60,
            hero_capture_path=hero_es
        )
        if os.path.exists(hero_es):
            shutil.copy2(hero_es, cover_es)

    # 4. Render English Master Video
    if render_en:
        print("\n[4/4] Rendering English Master Video (1080x1920 @ 60 FPS)...")
        render_chladni_video(
            output_mp4=video_en,
            audio_wav=audio_wav,
            lang="EN",
            duration=18.0,
            fps=60,
            hero_capture_path=hero_en
        )
        if os.path.exists(hero_en):
            shutil.copy2(hero_en, cover_en)

    print("\n" + "=" * 70)
    print("CHLADNI CYMATICS SUITE COMPLETED SUCCESSFULLY!")
    print(f"Videos:    {video_es}")
    print(f"           {video_en}")
    print(f"Excel:     {excel_path}")
    print(f"Covers:    {hero_es}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chladni Plate Cymatics Master Pipeline")
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
