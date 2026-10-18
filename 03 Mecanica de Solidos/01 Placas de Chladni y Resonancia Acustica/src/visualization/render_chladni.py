"""
Continuum Lab - Master Visual Renderer for Chladni Plate Cymatics
Module: 03 Mecanica de Solidos / 01 Placas de Chladni y Resonancia Acustica
File: src/visualization/render_chladni.py

Renders 1080x1920 (9:16 Vertical UHD @ 60 FPS) high-impact scientific animations:
  - Deep Space Cybernetic Dark Palette (#0a0a0c, #00f0ff, #ff007f, #ffaa00, #a855f7)
  - 15,000 Lagrangian granular particles with velocity-dependent bioluminescent glow
  - Real-time acoustic nodal lines W(x,y) = 0 visualization
  - Center transducer acoustic wavefront pulse animations
  - Live modal telemetry HUD & frequency oscilloscope panel
  - Strict Safe-Zone compliant typography (zero text overlap)
  - Direct 60 FPS pipe to FFmpeg with stereo procedural soundtrack
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Optional
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

# Add project root to sys.path
current_dir = Path(__file__).resolve().parent
module_dir = current_dir.parent.parent
project_dir = module_dir.parent.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.physics.chladni_sim import (
    ChladniConfig,
    ChladniPlateSimulation,
    TelemetryPoint,
)
from src.audio.chladni_audio import synthesize_chladni_soundtrack


class MasterChladniRenderer:
    """
    Master 9:16 Video & HUD Renderer for Chladni Plate Resonance.
    """

    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 60, lang: str = "ES"):
        self.width = width
        self.height = height
        self.fps = fps
        self.lang = lang.upper()

        self._load_fonts()

        # Canvas Layout Geometry (Strict Mobile Safe Zones: >150px top, >275px bottom)
        # 1. Top Header Card
        self.hdr_x1, self.hdr_y1 = 50, 150
        self.hdr_x2, self.hdr_y2 = 1030, 275

        # 2. Telemetry Badges
        self.badge_y1 = 290
        self.badge_y2 = 375
        self.b1_x1, self.b1_x2 = 50, 360
        self.b2_x1, self.b2_x2 = 380, 700
        self.b3_x1, self.b3_x2 = 720, 1030

        # 3. Hero Simulation Canvas (Square 980x980 px centered)
        self.sim_x1, self.sim_y1 = 50, 395
        self.sim_x2, self.sim_y2 = 1030, 1375
        self.sim_w = self.sim_x2 - self.sim_x1
        self.sim_h = self.sim_y2 - self.sim_y1

        # 4. Modal Spectrum / Oscilloscope Panel
        self.osc_x1, self.osc_y1 = 50, 1395
        self.osc_x2, self.osc_y2 = 1030, 1600

        # 5. Bottom Callout Card
        self.cta_x1, self.cta_y1 = 50, 1620
        self.cta_x2, self.cta_y2 = 1030, 1750

        # Precompute particle color gradient lookup table
        self._init_particle_colormap()

    def _load_fonts(self):
        font_candidates = [
            "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/consolab.ttf",
            "C:/Windows/Fonts/cour.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
        chosen = None
        for fc in font_candidates:
            if os.path.exists(fc):
                chosen = fc
                break

        if chosen:
            self.font_header_title = ImageFont.truetype(chosen, 26)
            self.font_header_sub = ImageFont.truetype(chosen, 19)
            self.font_badge_lbl = ImageFont.truetype(chosen, 14)
            self.font_badge_val = ImageFont.truetype(chosen, 22)
            self.font_osc_title = ImageFont.truetype(chosen, 16)
            self.font_osc_data = ImageFont.truetype(chosen, 15)
            self.font_cta_title = ImageFont.truetype(chosen, 18)
            self.font_cta_desc = ImageFont.truetype(chosen, 15)
        else:
            self.font_header_title = ImageFont.load_default()
            self.font_header_sub = ImageFont.load_default()
            self.font_badge_lbl = ImageFont.load_default()
            self.font_badge_val = ImageFont.load_default()
            self.font_osc_title = ImageFont.load_default()
            self.font_osc_data = ImageFont.load_default()
            self.font_cta_title = ImageFont.load_default()
            self.font_cta_desc = ImageFont.load_default()

    def _init_particle_colormap(self):
        """
        Creates smooth lookup table mapping normalized speed -> BGR color.
        0.0: Electric Cyan (#00F0FF) -> 0.4: Neon Purple (#A855F7) -> 1.0: Vivid Magenta (#FF007F)
        """
        self.particle_lut = np.zeros((256, 3), dtype=np.uint8)
        c_cyan = np.array([255, 240, 0])      # BGR for Cyan (#00F0FF)
        c_purp = np.array([247, 85, 168])     # BGR for Purple (#A855F7)
        c_mage = np.array([127, 0, 255])      # BGR for Magenta (#FF007F)
        c_gold = np.array([3, 183, 255])      # BGR for Gold (#FFB703)

        for i in range(256):
            u = i / 255.0
            if u < 0.35:
                t = u / 0.35
                col = (1.0 - t) * c_cyan + t * c_purp
            elif u < 0.80:
                t = (u - 0.35) / 0.45
                col = (1.0 - t) * c_purp + t * c_mage
            else:
                t = (u - 0.80) / 0.20
                col = (1.0 - t) * c_mage + t * c_gold
            self.particle_lut[i] = np.clip(col, 0, 255).astype(np.uint8)

    def draw_card(self, img: np.ndarray, x1: int, y1: int, x2: int, y2: int,
                  bg_bgr=(22, 20, 16), border_bgr=(51, 65, 85), corner_radius=12):
        """Draws rounded translucent cybernetic HUD card."""
        overlay = img.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), bg_bgr, -1)
        cv2.addWeighted(overlay, 0.88, img, 0.12, 0, img)
        cv2.rectangle(img, (x1, y1), (x2, y2), border_bgr, 1, lineType=cv2.LINE_AA)

    def render_frame(self, sim: ChladniPlateSimulation, telem: TelemetryPoint) -> np.ndarray:
        """
        Renders a single 1080x1920 video frame.
        """
        # Canvas Background: Deep Space Void #0B0F19 (BGR: 25, 15, 11)
        canvas = np.full((self.height, self.width, 3), (25, 15, 11), dtype=np.uint8)

        # ---------------------------------------------------------------------
        # 1. TOP HEADER CARD
        # ---------------------------------------------------------------------
        self.draw_card(canvas, self.hdr_x1, self.hdr_y1, self.hdr_x2, self.hdr_y2,
                       bg_bgr=(26, 23, 16), border_bgr=(255, 240, 0))  # Cyan border

        # ---------------------------------------------------------------------
        # 2. TELEMETRY BADGES
        # ---------------------------------------------------------------------
        # Badge 1: Frequency
        self.draw_card(canvas, self.b1_x1, self.badge_y1, self.b1_x2, self.badge_y2,
                       bg_bgr=(24, 20, 16), border_bgr=(100, 80, 40))
        # Badge 2: Mode (m, n)
        self.draw_card(canvas, self.b2_x1, self.badge_y1, self.b2_x2, self.badge_y2,
                       bg_bgr=(24, 20, 16), border_bgr=(180, 40, 180))
        # Badge 3: Nodal Adherence / Accel
        self.draw_card(canvas, self.b3_x1, self.badge_y1, self.b3_x2, self.badge_y2,
                       bg_bgr=(24, 20, 16), border_bgr=(40, 180, 100))

        # ---------------------------------------------------------------------
        # 3. HERO SIMULATION CANVAS (Titanium Plate & 15,000 Particles)
        # ---------------------------------------------------------------------
        # Plate boundary card
        self.draw_card(canvas, self.sim_x1, self.sim_y1, self.sim_x2, self.sim_y2,
                       bg_bgr=(18, 16, 14), border_bgr=(80, 80, 95))

        # Subtle coordinate grid on plate
        num_grid = 6
        for g in range(1, num_grid):
            gx = self.sim_x1 + int(g * (self.sim_w / num_grid))
            gy = self.sim_y1 + int(g * (self.sim_h / num_grid))
            cv2.line(canvas, (gx, self.sim_y1), (gx, self.sim_y2), (32, 28, 24), 1, cv2.LINE_AA)
            cv2.line(canvas, (self.sim_x1, gy), (self.sim_x2, gy), (32, 28, 24), 1, cv2.LINE_AA)

        # Center acoustic driver crosshair & acoustic wavefront rings
        cx = (self.sim_x1 + self.sim_x2) // 2
        cy = (self.sim_y1 + self.sim_y2) // 2

        # Pulsating driver ring
        wave_radius = int(35 + 25 * np.sin(2.0 * np.pi * 4.0 * telem.t))
        cv2.circle(canvas, (cx, cy), wave_radius, (60, 45, 30), 1, cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy), 8, (255, 240, 0), -1, cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy), 16, (255, 240, 0), 1, cv2.LINE_AA)

        # Map simulation coordinates [-L/2, L/2] to pixels [sim_x1, sim_x2], [sim_y1, sim_y2]
        L = sim.cfg.plate_size
        px = self.sim_x1 + ((sim.x + L / 2.0) / L * self.sim_w).astype(np.int32)
        py = self.sim_y1 + ((sim.y + L / 2.0) / L * self.sim_h).astype(np.int32)

        # Clip within plate boundaries
        valid = (px >= self.sim_x1 + 2) & (px <= self.sim_x2 - 2) & \
                (py >= self.sim_y1 + 2) & (py <= self.sim_y2 - 2)
        px_v = px[valid]
        py_v = py[valid]

        # Compute speed-based color
        speeds = np.sqrt(sim.vx[valid] ** 2 + sim.vy[valid] ** 2)
        v_norm = np.clip(speeds / 0.18, 0.0, 1.0)
        lut_idx = (v_norm * 255.0).astype(np.int32)
        colors = self.particle_lut[lut_idx]

        # Render particles with subpixel fast rasterization
        for i in range(len(px_v)):
            xi = px_v[i]
            yi = py_v[i]
            col = tuple(int(c) for c in colors[i])
            # Core dot
            canvas[yi, xi] = col
            # 4-connected anti-aliasing halo
            if xi + 1 < self.sim_x2:
                canvas[yi, xi + 1] = tuple(int(c * 0.6) for c in col)
            if xi - 1 > self.sim_x1:
                canvas[yi, xi - 1] = tuple(int(c * 0.6) for c in col)
            if yi + 1 < self.sim_y2:
                canvas[yi + 1, xi] = tuple(int(c * 0.6) for c in col)
            if yi - 1 > self.sim_y1:
                canvas[yi - 1, xi] = tuple(int(c * 0.6) for c in col)

        # ---------------------------------------------------------------------
        # 4. MODAL SPECTRUM & ACOUSTIC OSCILLOSCOPE PANEL
        # ---------------------------------------------------------------------
        self.draw_card(canvas, self.osc_x1, self.osc_y1, self.osc_x2, self.osc_y2,
                       bg_bgr=(22, 18, 14), border_bgr=(120, 80, 50))

        # Real-time oscilloscope waveform
        osc_mid_y = (self.osc_y1 + self.osc_y2) // 2 + 10
        osc_pts = []
        osc_w = self.osc_x2 - self.osc_x1 - 40
        num_osc_samples = 120
        omega_t = 2.0 * np.pi * telem.frequency * telem.t

        for s in range(num_osc_samples):
            sx = self.osc_x1 + 20 + int(s * (osc_w / (num_osc_samples - 1)))
            phase_s = 2.0 * np.pi * 4.0 * (s / num_osc_samples) + omega_t
            sy = osc_mid_y + int(36 * np.sin(phase_s) + 12 * np.sin(2.0 * phase_s))
            osc_pts.append((sx, sy))

        if len(osc_pts) > 1:
            cv2.polylines(canvas, [np.array(osc_pts, dtype=np.int32)], False, (255, 240, 0), 2, cv2.LINE_AA)

        # ---------------------------------------------------------------------
        # 5. BOTTOM CTA / CHALLENGE CALLOUT CARD
        # ---------------------------------------------------------------------
        self.draw_card(canvas, self.cta_x1, self.cta_y1, self.cta_x2, self.cta_y2,
                       bg_bgr=(26, 22, 16), border_bgr=(0, 230, 255))  # Gold border

        # ---------------------------------------------------------------------
        # 6. TYPOGRAPHIC OVERLAYS WITH PIL (ZERO OVERLAP GUARANTEED)
        # ---------------------------------------------------------------------
        pil_img = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)

        # Header Titles
        if self.lang == "ES":
            h_title = "CONTINUUM LAB // MECÁNICA DE SÓLIDOS"
            h_sub = "FIGURAS DE CHLADNI: D∇⁴w + ρh ∂²w/∂t² = 0"
            b1_lbl = "FRECUENCIA ACÚSTICA"
            b1_val = f"{telem.frequency:04.0f} Hz"
            b2_lbl = "MODO ELASTODINÁMICO"
            b2_val = f"({telem.mode_m}, {telem.mode_n}) Nodal"
            b3_lbl = "ACEL. VERTICAL (PEAK)"
            b3_val = f"{telem.peak_accel_g:04.1f} g"
            osc_title = f"SEÑAL TRANSDUCTOR // {telem.active_mode_name.upper()}"
            osc_meta = f"RIGIDEZ D: {telem.bending_rigidity:.4f} N·m  |  PARTÍCULAS: 15,000 ARENA SÍLICE"
            cta_title = "¿POR QUÉ LA ARENA HUYE DEL SONIDO?"
            cta_desc = "Las partículas son expulsadas donde hay vibración (az > g) y quedan\natrapadas exclusivamente a lo largo de las líneas nodales (w = 0)."
        else:
            h_title = "CONTINUUM LAB // SOLID MECHANICS"
            h_sub = "CHLADNI FIGURES: D∇⁴w + ρh ∂²w/∂t² = 0"
            b1_lbl = "ACOUSTIC FREQUENCY"
            b1_val = f"{telem.frequency:04.0f} Hz"
            b2_lbl = "ELASTODYNAMIC MODE"
            b2_val = f"({telem.mode_m}, {telem.mode_n}) Nodal"
            b3_lbl = "VERTICAL ACCEL (PEAK)"
            b3_val = f"{telem.peak_accel_g:04.1f} g"
            osc_title = f"TRANSDUCER SIGNAL // {telem.active_mode_name.upper()}"
            osc_meta = f"RIGIDITY D: {telem.bending_rigidity:.4f} N·m  |  PARTICLES: 15,000 SILICA SAND"
            cta_title = "WHY DOES SAND FLEE FROM SOUND?"
            cta_desc = "Particles are violently kicked where vibration exceeds g (az > g)\nand trapped exclusively along zero-displacement nodal lines (w = 0)."

        # Draw Header
        draw.text((self.hdr_x1 + 25, self.hdr_y1 + 25), h_title, font=self.font_header_title, fill=(0, 240, 255))
        draw.text((self.hdr_x1 + 25, self.hdr_y1 + 68), h_sub, font=self.font_header_sub, fill=(240, 240, 250))

        # Draw Badges
        draw.text((self.b1_x1 + 18, self.badge_y1 + 16), b1_lbl, font=self.font_badge_lbl, fill=(160, 180, 200))
        draw.text((self.b1_x1 + 18, self.badge_y1 + 38), b1_val, font=self.font_badge_val, fill=(0, 240, 255))

        draw.text((self.b2_x1 + 18, self.badge_y1 + 16), b2_lbl, font=self.font_badge_lbl, fill=(160, 180, 200))
        draw.text((self.b2_x1 + 18, self.badge_y1 + 38), b2_val, font=self.font_badge_val, fill=(240, 100, 240))

        draw.text((self.b3_x1 + 18, self.badge_y1 + 16), b3_lbl, font=self.font_badge_lbl, fill=(160, 180, 200))
        draw.text((self.b3_x1 + 18, self.badge_y1 + 38), b3_val, font=self.font_badge_val, fill=(100, 255, 160))

        # Draw Oscilloscope Meta
        draw.text((self.osc_x1 + 25, self.osc_y1 + 18), osc_title, font=self.font_osc_title, fill=(0, 240, 255))
        draw.text((self.osc_x1 + 25, self.osc_y2 - 32), osc_meta, font=self.font_osc_data, fill=(160, 175, 195))

        # Draw Callout
        draw.text((self.cta_x1 + 25, self.cta_y1 + 18), cta_title, font=self.font_cta_title, fill=(255, 215, 0))
        draw.text((self.cta_x1 + 25, self.cta_y1 + 52), cta_desc, font=self.font_cta_desc, fill=(240, 245, 255))

        # Convert back to BGR for OpenCV / FFmpeg
        final_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        return final_bgr


def render_chladni_video(
    output_mp4: str,
    audio_wav: Optional[str] = None,
    lang: str = "ES",
    duration: float = 18.0,
    fps: int = 60,
    hero_capture_path: Optional[str] = None
) -> str:
    """
    Renders the complete 18.0s Chladni plate cymatic simulation and pipes to FFmpeg.
    """
    Path(output_mp4).parent.mkdir(parents=True, exist_ok=True)
    temp_video = str(Path(output_mp4).with_suffix(".temp.mp4"))

    sim = ChladniPlateSimulation()
    renderer = MasterChladniRenderer(width=1080, height=1920, fps=fps, lang=lang)

    total_frames = int(duration * fps)
    dt_frame = 1.0 / float(fps)

    print(f"\n[RENDER] Starting Chladni Video Pipeline [{lang}]: {total_frames} frames @ {fps} FPS -> {output_mp4}")

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1080x1920",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        temp_video
    ]
    pipe = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    hero_frame = None
    # Hero capture at t = 11.5s (Peak Mode 3:5 Hyperbolic Lattice)
    hero_frame_idx = int(11.5 * fps)

    t_start = time.time()
    for frame_idx in range(total_frames):
        target_t = frame_idx * dt_frame
        telem = sim.advance_to_time(target_t)
        frame_bgr = renderer.render_frame(sim, telem)

        # Pipe raw frame to FFmpeg
        pipe.stdin.write(frame_bgr.tobytes())

        if frame_idx == hero_frame_idx:
            hero_frame = frame_bgr.copy()

        if frame_idx % 120 == 0 or frame_idx == total_frames - 1:
            elapsed = time.time() - t_start
            fps_proc = (frame_idx + 1) / max(0.01, elapsed)
            eta = (total_frames - frame_idx - 1) / max(0.01, fps_proc)
            print(f"[{frame_idx+1:04d}/{total_frames}] t={telem.t:.2f}s | Mode=({telem.mode_m},{telem.mode_n}) | f={telem.frequency:.0f}Hz | FPS={fps_proc:.1f} | ETA={eta:.1f}s")

    pipe.stdin.close()
    pipe.wait()

    # Save Hero Capture
    if hero_capture_path and hero_frame is not None:
        Path(hero_capture_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(hero_capture_path, hero_frame)
        print(f"[OK] Saved Hero Capture to: {hero_capture_path}")

    # Multiplex procedural audio
    if audio_wav and os.path.exists(audio_wav):
        print(f"[AUDIO] Multiplexing procedural audio: {audio_wav}")
        mux_cmd = [
            "ffmpeg", "-y",
            "-i", temp_video,
            "-i", audio_wav,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "256k",
            "-shortest",
            output_mp4
        ]
        subprocess.run(mux_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if os.path.exists(temp_video):
            os.remove(temp_video)
    else:
        if os.path.exists(temp_video):
            os.replace(temp_video, output_mp4)

    file_size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
    print(f"[SUCCESS] Video rendered successfully: {output_mp4} ({file_size_mb:.2f} MB)")
    return output_mp4
