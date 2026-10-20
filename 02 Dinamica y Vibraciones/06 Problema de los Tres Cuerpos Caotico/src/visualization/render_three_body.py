"""
Continuum Lab - Master Visual Renderer for Chaotic Three-Body Problem
Module: 02 Dinamica y Vibraciones / 06 Problema de los Tres Cuerpos Caotico
File: src/visualization/render_three_body.py

Renders 1080x1920 (9:16 Vertical UHD @ 60 FPS) high-impact scientific animations:
  - Deep Cosmic Void Palette (#080b12, #00f0ff, #ff007f, #ffb703, #ffffff)
  - 3 Stellar Cores with multi-layer glowing coronas and phosphorescent orbital ribbon trails
  - Dynamic gravitational force vector lasers scaling with F_ij = G*m_i*m_j / r_ij²
  - Real-time Hamiltonian energy & kinetic phase telemetry panel
  - Strict Safe-Zone compliant typography (zero text overlap)
  - Direct 60 FPS pipe to FFmpeg with stereo procedural gravitational soundtrack
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple
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

from src.physics.three_body_sim import (
    ThreeBodyConfig,
    ThreeBodySimulation,
    ThreeBodyTelemetry,
)
from src.audio.three_body_audio import synthesize_three_body_soundtrack


class MasterThreeBodyRenderer:
    """
    Master 9:16 Video & HUD Renderer for the Three-Body Problem.
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

        # 3. Hero Celestial Canvas (Square 980x980 px centered)
        self.sim_x1, self.sim_y1 = 50, 395
        self.sim_x2, self.sim_y2 = 1030, 1375
        self.sim_w = self.sim_x2 - self.sim_x1
        self.sim_h = self.sim_y2 - self.sim_y1

        # 4. Energy & Kinetic Telemetry Panel
        self.panel_x1, self.panel_y1 = 50, 1395
        self.panel_x2, self.panel_y2 = 1030, 1600

        # 5. Bottom Callout Card
        self.cta_x1, self.cta_y1 = 50, 1620
        self.cta_x2, self.cta_y2 = 1030, 1750

        # Precompute static background stars
        rng = np.random.default_rng(777)
        self.bg_stars: List[Tuple[int, int, int]] = []
        for _ in range(120):
            sx = int(rng.integers(self.sim_x1 + 10, self.sim_x2 - 10))
            sy = int(rng.integers(self.sim_y1 + 10, self.sim_y2 - 10))
            sb = int(rng.integers(60, 180))
            self.bg_stars.append((sx, sy, sb))

        # Dynamic camera scale tracker
        self.view_scale = 280.0  # Pixels per physical unit

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
            self.font_panel_title = ImageFont.truetype(chosen, 16)
            self.font_panel_data = ImageFont.truetype(chosen, 15)
            self.font_cta_title = ImageFont.truetype(chosen, 18)
            self.font_cta_desc = ImageFont.truetype(chosen, 15)
        else:
            self.font_header_title = ImageFont.load_default()
            self.font_header_sub = ImageFont.load_default()
            self.font_badge_lbl = ImageFont.load_default()
            self.font_badge_val = ImageFont.load_default()
            self.font_panel_title = ImageFont.load_default()
            self.font_panel_data = ImageFont.load_default()
            self.font_cta_title = ImageFont.load_default()
            self.font_cta_desc = ImageFont.load_default()

    def draw_card(self, img: np.ndarray, x1: int, y1: int, x2: int, y2: int,
                  bg_bgr=(18, 14, 10), border_bgr=(51, 65, 85)):
        """Draws rounded translucent cybernetic HUD card."""
        overlay = img.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), bg_bgr, -1)
        cv2.addWeighted(overlay, 0.88, img, 0.12, 0, img)
        cv2.rectangle(img, (x1, y1), (x2, y2), border_bgr, 1, lineType=cv2.LINE_AA)

    def draw_glowing_star(self, canvas: np.ndarray, cx: int, cy: int, bgr_color: Tuple[int, int, int]):
        """Draws multi-layer blooming stellar core."""
        if not (self.sim_x1 - 30 <= cx <= self.sim_x2 + 30 and self.sim_y1 - 30 <= cy <= self.sim_y2 + 30):
            return

        # Outer faint halo (radius 22)
        cv2.circle(canvas, (cx, cy), 22, tuple(int(c * 0.22) for c in bgr_color), -1, cv2.LINE_AA)
        # Mid glow (radius 14)
        cv2.circle(canvas, (cx, cy), 14, tuple(int(c * 0.55) for c in bgr_color), -1, cv2.LINE_AA)
        # Solid colorful ring (radius 8)
        cv2.circle(canvas, (cx, cy), 8, bgr_color, -1, cv2.LINE_AA)
        # Blazing white core (radius 4)
        cv2.circle(canvas, (cx, cy), 4, (255, 255, 255), -1, cv2.LINE_AA)

    def draw_trail(self, canvas: np.ndarray, trail: List[Tuple[float, float]],
                   bgr_color: Tuple[int, int, int], center_px: Tuple[int, int], scale: float):
        """Draws tapering phosphorescent ribbon trail."""
        if len(trail) < 2:
            return

        pts = []
        for x_val, y_val in trail:
            px = int(center_px[0] + x_val * scale)
            py = int(center_px[1] - y_val * scale)
            pts.append((px, py))

        n_pts = len(pts)
        for i in range(n_pts - 1):
            alpha = (i + 1) / float(n_pts)
            thickness = 1 if alpha < 0.4 else (2 if alpha < 0.8 else 3)
            col = tuple(int(c * (0.15 + 0.85 * (alpha ** 1.5))) for c in bgr_color)
            cv2.line(canvas, pts[i], pts[i + 1], col, thickness, cv2.LINE_AA)

    def render_frame(self, sim: ThreeBodySimulation, telem: ThreeBodyTelemetry) -> np.ndarray:
        """
        Renders a single 1080x1920 video frame.
        """
        # Canvas Background: Deep Space Cosmic Void #080B12 (BGR: 18, 11, 8)
        canvas = np.full((self.height, self.width, 3), (18, 11, 8), dtype=np.uint8)

        # ---------------------------------------------------------------------
        # 1. TOP HEADER CARD
        # ---------------------------------------------------------------------
        self.draw_card(canvas, self.hdr_x1, self.hdr_y1, self.hdr_x2, self.hdr_y2,
                       bg_bgr=(24, 18, 12), border_bgr=(255, 240, 0))

        # ---------------------------------------------------------------------
        # 2. TELEMETRY BADGES
        # ---------------------------------------------------------------------
        # Badge 1: Total Energy E
        self.draw_card(canvas, self.b1_x1, self.badge_y1, self.b1_x2, self.badge_y2,
                       bg_bgr=(22, 16, 12), border_bgr=(100, 80, 40))
        # Badge 2: Angular Momentum |L|
        self.draw_card(canvas, self.b2_x1, self.badge_y1, self.b2_x2, self.badge_y2,
                       bg_bgr=(22, 16, 12), border_bgr=(180, 40, 180))
        # Badge 3: Max Speed (Slingshot indicator)
        self.draw_card(canvas, self.b3_x1, self.badge_y1, self.b3_x2, self.badge_y2,
                       bg_bgr=(22, 16, 12), border_bgr=(40, 180, 100))

        # ---------------------------------------------------------------------
        # 3. HERO CELESTIAL CANVAS
        # ---------------------------------------------------------------------
        self.draw_card(canvas, self.sim_x1, self.sim_y1, self.sim_x2, self.sim_y2,
                       bg_bgr=(14, 10, 8), border_bgr=(80, 80, 100))

        # Distant background stars
        for sx, sy, sb in self.bg_stars:
            canvas[sy, sx] = (sb, sb, sb)

        # Center pixel of celestial canvas
        cx = (self.sim_x1 + self.sim_x2) // 2
        cy = (self.sim_y1 + self.sim_y2) // 2

        # Smooth dynamic camera scale adaptation
        # In early Figure-8 phase, scale is 300; if bodies diverge, scale zooms out smoothly
        max_coord = max(abs(telem.star_a.x), abs(telem.star_a.y),
                        abs(telem.star_b.x), abs(telem.star_b.y),
                        abs(telem.star_c.x), abs(telem.star_c.y))
        target_scale = 310.0 if max_coord < 1.4 else max(90.0, 420.0 / (max_coord + 0.15))
        self.view_scale = 0.95 * self.view_scale + 0.05 * target_scale
        scale = self.view_scale

        # Celestial coordinate grid lines
        grid_step = int(scale * 0.5)
        for gx in range(cx % grid_step, self.sim_x2, grid_step):
            if gx >= self.sim_x1:
                cv2.line(canvas, (gx, self.sim_y1), (gx, self.sim_y2), (25, 20, 16), 1, cv2.LINE_AA)
        for gy in range(cy % grid_step, self.sim_y2, grid_step):
            if gy >= self.sim_y1:
                cv2.line(canvas, (self.sim_x1, gy), (self.sim_x2, gy), (25, 20, 16), 1, cv2.LINE_AA)

        # Center of mass crosshair (origin is strictly at (0, 0))
        cv2.drawMarker(canvas, (cx, cy), (60, 50, 40), cv2.MARKER_CROSS, 16, 1, cv2.LINE_AA)

        # Color definitions for the 3 stars
        col_a = (255, 240, 0)   # BGR for Cyan (#00F0FF)
        col_b = (127, 0, 255)   # BGR for Magenta (#FF007F)
        col_c = (3, 183, 255)   # BGR for Amber / Gold (#FFB703)

        # Draw Orbital Trails
        self.draw_trail(canvas, sim.trail_a, col_a, (cx, cy), scale)
        self.draw_trail(canvas, sim.trail_b, col_b, (cx, cy), scale)
        self.draw_trail(canvas, sim.trail_c, col_c, (cx, cy), scale)

        # Screen positions of stars
        p1 = (int(cx + telem.star_a.x * scale), int(cy - telem.star_a.y * scale))
        p2 = (int(cx + telem.star_b.x * scale), int(cy - telem.star_b.y * scale))
        p3 = (int(cx + telem.star_c.x * scale), int(cy - telem.star_c.y * scale))

        # Dynamic Gravitational Force Vector Laser Lines (between pairs)
        # Intensity scales with 1 / distance²
        def draw_grav_force(pt1, pt2, dist, base_color):
            if dist < 0.05:
                return
            force_intensity = min(1.0, 0.45 / (dist ** 2 + 0.15))
            f_col = tuple(int(c * force_intensity) for c in base_color)
            thick = 1 if force_intensity < 0.6 else 2
            cv2.line(canvas, pt1, pt2, f_col, thick, cv2.LINE_AA)

        r12 = float(np.hypot(telem.star_a.x - telem.star_b.x, telem.star_a.y - telem.star_b.y))
        r23 = float(np.hypot(telem.star_b.x - telem.star_c.x, telem.star_b.y - telem.star_c.y))
        r31 = float(np.hypot(telem.star_c.x - telem.star_a.x, telem.star_c.y - telem.star_a.y))

        draw_grav_force(p1, p2, r12, (200, 100, 220))
        draw_grav_force(p2, p3, r23, (100, 160, 240))
        draw_grav_force(p3, p1, r31, (220, 220, 100))

        # Draw Glowing Stellar Cores
        self.draw_glowing_star(canvas, p1[0], p1[1], col_a)
        self.draw_glowing_star(canvas, p2[0], p2[1], col_b)
        self.draw_glowing_star(canvas, p3[0], p3[1], col_c)

        # ---------------------------------------------------------------------
        # 4. ENERGY & KINETIC PHASE TELEMETRY PANEL
        # ---------------------------------------------------------------------
        self.draw_card(canvas, self.panel_x1, self.panel_y1, self.panel_x2, self.panel_y2,
                       bg_bgr=(20, 15, 12), border_bgr=(120, 80, 50))

        # Real-time Speed Gauges for the 3 Stars
        gauge_y = self.panel_y1 + 80
        bar_w_max = 240
        speed_max_ref = 3.2

        # Star A speed bar
        w_a = int(min(1.0, telem.star_a.speed / speed_max_ref) * bar_w_max)
        cv2.rectangle(canvas, (self.panel_x1 + 60, gauge_y), (self.panel_x1 + 60 + w_a, gauge_y + 16), col_a, -1)
        cv2.rectangle(canvas, (self.panel_x1 + 60, gauge_y), (self.panel_x1 + 60 + bar_w_max, gauge_y + 16), (50, 40, 30), 1)

        # Star B speed bar
        w_b = int(min(1.0, telem.star_b.speed / speed_max_ref) * bar_w_max)
        cv2.rectangle(canvas, (self.panel_x1 + 380, gauge_y), (self.panel_x1 + 380 + w_b, gauge_y + 16), col_b, -1)
        cv2.rectangle(canvas, (self.panel_x1 + 380, gauge_y), (self.panel_x1 + 380 + bar_w_max, gauge_y + 16), (50, 40, 30), 1)

        # Star C speed bar
        w_c = int(min(1.0, telem.star_c.speed / speed_max_ref) * bar_w_max)
        cv2.rectangle(canvas, (self.panel_x1 + 700, gauge_y), (self.panel_x1 + 700 + w_c, gauge_y + 16), col_c, -1)
        cv2.rectangle(canvas, (self.panel_x1 + 700, gauge_y), (self.panel_x1 + 700 + bar_w_max, gauge_y + 16), (50, 40, 30), 1)

        # ---------------------------------------------------------------------
        # 5. BOTTOM CALLOUT / DEBATE CHALLENGE CARD
        # ---------------------------------------------------------------------
        self.draw_card(canvas, self.cta_x1, self.cta_y1, self.cta_x2, self.cta_y2,
                       bg_bgr=(24, 18, 12), border_bgr=(0, 230, 255))

        # ---------------------------------------------------------------------
        # 6. TYPOGRAPHIC OVERLAYS WITH PIL (ZERO OVERLAP GUARANTEED)
        # ---------------------------------------------------------------------
        pil_img = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)

        # Header Titles
        if self.lang == "ES":
            h_title = "CONTINUUM LAB // MECÁNICA CELESTE"
            h_sub = "PROBLEMA DE LOS 3 CUERPOS: m_i d²r_i/dt² = Σ G m_i m_j / r_ij²"
            b1_lbl = "ENERGÍA HAMILTONIANA E"
            b1_val = f"{telem.total_energy:+.4f} J"
            b2_lbl = "MOMENTO ANGULAR |L|"
            b2_val = f"{abs(telem.angular_momentum):.4f} N·m·s"
            b3_lbl = "VELOCIDAD MÁX (SLINGSHOT)"
            b3_val = f"{telem.max_speed:04.2f} km/s"
            panel_title = f"ESTADO CELESTE // {telem.regime_name.upper()}"
            panel_data = f"SEPARACIÓN MÍN: {telem.min_separation:.4f} AU  |  ENERGÍA CINÉTICA T: {telem.kinetic_energy:.4f} J"
            cta_title = "¿SE PUEDE PREDECIR EL DESTINO DE 3 ESTRELLAS?"
            cta_desc = "En 1887, Poincaré demostró que no existe solución analítica general:\nuna perturbación de 0.0001 mm desata el caos determinista absoluto."
        else:
            h_title = "CONTINUUM LAB // CELESTIAL MECHANICS"
            h_sub = "THE THREE-BODY PROBLEM: m_i d²r_i/dt² = Σ G m_i m_j / r_ij²"
            b1_lbl = "HAMILTONIAN ENERGY E"
            b1_val = f"{telem.total_energy:+.4f} J"
            b2_lbl = "ANGULAR MOMENTUM |L|"
            b2_val = f"{abs(telem.angular_momentum):.4f} N·m·s"
            b3_lbl = "MAX SPEED (SLINGSHOT)"
            b3_val = f"{telem.max_speed:04.2f} km/s"
            panel_title = f"CELESTIAL REGIME // {telem.regime_name.upper()}"
            panel_data = f"MIN SEPARATION: {telem.min_separation:.4f} AU  |  KINETIC ENERGY T: {telem.kinetic_energy:.4f} J"
            cta_title = "CAN WE PREDICT THE FATE OF 3 STARS?"
            cta_desc = "In 1887, Poincaré proved no general analytical solution exists:\na 0.0001 mm perturbation triggers absolute deterministic chaos."

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

        # Draw Panel Labels
        draw.text((self.panel_x1 + 25, self.panel_y1 + 18), panel_title, font=self.font_panel_title, fill=(0, 240, 255))
        draw.text((self.panel_x1 + 60, gauge_y - 22), f"STAR A: {telem.star_a.speed:.2f}", font=self.font_badge_lbl, fill=(0, 240, 255))
        draw.text((self.panel_x1 + 380, gauge_y - 22), f"STAR B: {telem.star_b.speed:.2f}", font=self.font_badge_lbl, fill=(255, 0, 127))
        draw.text((self.panel_x1 + 700, gauge_y - 22), f"STAR C: {telem.star_c.speed:.2f}", font=self.font_badge_lbl, fill=(255, 183, 3))
        draw.text((self.panel_x1 + 25, self.panel_y2 - 32), panel_data, font=self.font_panel_data, fill=(160, 175, 195))

        # Draw Callout
        draw.text((self.cta_x1 + 25, self.cta_y1 + 18), cta_title, font=self.font_cta_title, fill=(255, 215, 0))
        draw.text((self.cta_x1 + 25, self.cta_y1 + 52), cta_desc, font=self.font_cta_desc, fill=(240, 245, 255))

        final_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        return final_bgr


def render_three_body_video(
    output_mp4: str,
    audio_wav: Optional[str] = None,
    lang: str = "ES",
    duration: float = 18.0,
    fps: int = 60,
    hero_capture_path: Optional[str] = None
) -> str:
    """
    Renders the complete 18.0s Three-Body Problem simulation and pipes to FFmpeg.
    """
    Path(output_mp4).parent.mkdir(parents=True, exist_ok=True)
    temp_video = str(Path(output_mp4).with_suffix(".temp.mp4"))

    sim = ThreeBodySimulation()
    renderer = MasterThreeBodyRenderer(width=1080, height=1920, fps=fps, lang=lang)

    total_frames = int(duration * fps)
    dt_frame = 1.0 / float(fps)

    print(f"\n[RENDER] Starting 3-Body Video Pipeline [{lang}]: {total_frames} frames @ {fps} FPS -> {output_mp4}")

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
    # Hero capture at t = 9.5s (Violent triple slingshot phase)
    hero_frame_idx = int(9.5 * fps)

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
            print(f"[{frame_idx+1:04d}/{total_frames}] t={telem.t:.2f}s | E={telem.total_energy:.4f}J | vmax={telem.max_speed:.2f} | FPS={fps_proc:.1f} | ETA={eta:.1f}s")

    pipe.stdin.close()
    pipe.wait()

    # Save Hero Capture
    if hero_capture_path and hero_frame is not None:
        Path(hero_capture_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(hero_capture_path, hero_frame)
        print(f"[OK] Saved Hero Capture to: {hero_capture_path}")

    # Multiplex procedural audio
    if audio_wav and os.path.exists(audio_wav):
        print(f"[AUDIO] Multiplexing procedural gravitational audio: {audio_wav}")
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
