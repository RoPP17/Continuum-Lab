"""
Continuum Lab — Visual Engineering & Hero Cover Generator
Module: 04 Termodinamica y Calor / 01 Ley Cero de la Termodinamica 3 Cuerpos
Generates 1080x1920 High-Res Cover PNGs (ES & EN) and Animated GIF Previews.
"""

import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

project_dir = Path(__file__).resolve().parent.parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.physics.heat_zeroth_law import ZerothLawThermalSimulation, ThermalConfig
from src.visualization.render_zeroth_law_video import MasterHeatTransferRenderer


def generate_all_visuals(output_dir: Path | None = None):
    """
    Generates high-definition hero cover images (1080x1920) and animated preview GIF.
    """
    workspace_root = project_dir.parent.parent
    if output_dir is None:
        renders_base = workspace_root / "RENDERS" / "14 Ley Cero Termodinamica 3 Cuerpos"
    else:
        renders_base = output_dir

    cover_dir = renders_base / "cover"
    cover_dir.mkdir(parents=True, exist_ok=True)

    print("\n[+] Generando portadas de alta definición y vista previa GIF...")

    # 1. Generate Keyframe at peak thermal flux (t ~ 3.5s)
    sim = ZerothLawThermalSimulation()
    renderer = MasterHeatTransferRenderer(width=1080, height=1920, fps=60, lang="ES")

    # Step simulation recording history to populate convergence curves
    dt_step = 3.5 / 120.0
    for k in range(120):
        sim.step(dt_step)
        frame_es = renderer.render_frame(sim, frame_idx=k, total_frames=1080, timeline_sec=(k + 1) * dt_step)

    cover_es_path = cover_dir / "cover_ley_cero_es_1080x1920.png"
    cv2.imwrite(str(cover_es_path), frame_es)
    print(f"  -> Portada en Espanol guardada: {cover_es_path}")

    # Generate English Cover
    renderer_en = MasterHeatTransferRenderer(width=1080, height=1920, fps=60, lang="EN")
    renderer_en.time_history = list(renderer.time_history)
    renderer_en.t_a_history = list(renderer.t_a_history)
    renderer_en.t_c_history = list(renderer.t_c_history)
    renderer_en.t_b_history = list(renderer.t_b_history)
    frame_en = renderer_en.render_frame(sim, frame_idx=120, total_frames=1080, timeline_sec=3.5)
    cover_en_path = cover_dir / "cover_zeroth_law_en_1080x1920.png"
    cv2.imwrite(str(cover_en_path), frame_en)
    print(f"  -> Portada en Ingles guardada: {cover_en_path}")

    # 2. Generate Animated GIF Preview (scaled to 480x854 for fast web loading in README)
    gif_path = cover_dir / "preview_ley_cero_termodinamica.gif"
    print(f"  -> Generando GIF animado liviano: {gif_path}...")

    sim_gif = ZerothLawThermalSimulation()
    renderer_gif = MasterHeatTransferRenderer(width=1080, height=1920, fps=30, lang="ES")
    frames_gif = []

    # Sample 36 frames spanning the entire equilibration timeline
    total_steps = 36
    for k in range(total_steps):
        for _ in range(22):
            sim_gif.step(0.02)
        frame_bgr = renderer_gif.render_frame(sim_gif, frame_idx=k*30, total_frames=1080, timeline_sec=k*0.5)
        # Downscale to 480x854 for optimized GIF size
        frame_small = cv2.resize(frame_bgr, (480, 854), interpolation=cv2.INTER_AREA)
        frame_rgb = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)
        frames_gif.append(Image.fromarray(frame_rgb))

    if frames_gif:
        frames_gif[0].save(
            str(gif_path),
            save_all=True,
            append_images=frames_gif[1:],
            duration=90,  # ~11 FPS
            loop=0,
            optimize=True
        )
        print(f"  -> [SUCCESS] GIF animado guardado en: {gif_path}")


if __name__ == "__main__":
    generate_all_visuals()
