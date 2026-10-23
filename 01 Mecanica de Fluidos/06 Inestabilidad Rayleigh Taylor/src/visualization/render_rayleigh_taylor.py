"""
Continuum Lab - Master 9:16 Visual Renderer for Rayleigh-Taylor Instability
Module: 01 Mecanica de Fluidos / 06 Inestabilidad Rayleigh Taylor
File: src/visualization/render_rayleigh_taylor.py

Renders 1080x1920 (9:16 Vertical UHD @ 60 FPS) scientific animations:
  - Deep Cosmic Void & Interfacial Fluid Palette (#06080F, #00F0FF, #FF007F, #FFB703, #00FF88)
  - Continuous scalar concentration field C(x,y) with custom cybernetic shader colormap
  - Baroclinic vorticity curls (counter-rotating mushroom plume spirals)
  - 600 Lagrangian tracer particles with velocity-glow trails
  - Real-time telemetry oscilloscope: Enstrophy Ω(t), Kinetic Energy E_k(t), and Dimonte quadratic mixing law h(t)
  - Strict Mobile Safe Zones & Zero Text Overlap
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

current_dir = Path(__file__).resolve().parent
module_dir = current_dir.parent.parent
project_dir = module_dir.parent.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.physics.rayleigh_taylor_sim import (
    RayleighTaylorConfig,
    RayleighTaylorSimulation,
    RTTelemetryPoint,
)


class MasterRayleighTaylorRenderer:
    """
    Master 9:16 60 FPS Visual Renderer & Cybernetic HUD for Rayleigh-Taylor Instability.
    """

    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 60, lang: str = "ES"):
        self.width = width
        self.height = height
        self.fps = fps
        self.lang = lang.upper()

        self._load_fonts()
        self._build_colormaps()

        # Strict Mobile Safe-Zone Layout (1080x1920)
        # 1. Top Header Card
        self.hdr_x1, self.hdr_y1 = 50, 150
        self.hdr_x2, self.hdr_y2 = 1030, 275

        # 2. Telemetry Badges (3 Columns)
        self.badge_y1, self.badge_y2 = 290, 375
        self.b1_x1, self.b1_x2 = 50, 360
        self.b2_x1, self.b2_x2 = 380, 700
        self.b3_x1, self.b3_x2 = 720, 1030

        # 3. Fluid Mechanics Viewport (980x980 px)
        self.sim_x1, self.sim_y1 = 50, 395
        self.sim_x2, self.sim_y2 = 1030, 1375
        self.sim_w = self.sim_x2 - self.sim_x1
        self.sim_h = self.sim_y2 - self.sim_y1

        # 4. Live Oscilloscope Panel (980x205 px)
        self.panel_x1, self.panel_y1 = 50, 1395
        self.panel_x2, self.panel_y2 = 1030, 1600

        # 5. Bottom Callout Card
        self.cta_x1, self.cta_y1 = 50, 1615
        self.cta_x2, self.cta_y2 = 1030, 1745

    def _load_fonts(self):
        font_candidates = [
            "C:/Windows/Fonts/consolab.ttf",
            "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/courbd.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
        chosen_bold = None
        for fc in font_candidates:
            if os.path.exists(fc):
                chosen_bold = fc
                break

        chosen_reg = "C:/Windows/Fonts/consola.ttf" if os.path.exists("C:/Windows/Fonts/consola.ttf") else chosen_bold

        if chosen_bold and chosen_reg:
            self.font_hdr_title = ImageFont.truetype(chosen_bold, 23)
            self.font_hdr_sub = ImageFont.truetype(chosen_reg, 16)
            self.font_badge_lbl = ImageFont.truetype(chosen_bold, 14)
            self.font_badge_val = ImageFont.truetype(chosen_bold, 21)
            self.font_viewport_tag = ImageFont.truetype(chosen_bold, 15)
            self.font_panel_title = ImageFont.truetype(chosen_bold, 16)
            self.font_panel_meta = ImageFont.truetype(chosen_reg, 13)
            self.font_cta_title = ImageFont.truetype(chosen_bold, 17)
            self.font_cta_desc = ImageFont.truetype(chosen_reg, 14)
        else:
            default_f = ImageFont.load_default()
            self.font_hdr_title = default_f
            self.font_hdr_sub = default_f
            self.font_badge_lbl = default_f
            self.font_badge_val = default_f
            self.font_viewport_tag = default_f
            self.font_panel_title = default_f
            self.font_panel_meta = default_f
            self.font_cta_title = default_f
            self.font_cta_desc = default_f

    def _build_colormaps(self):
        """Constructs an exquisite scientific colormap for concentration & vorticity."""
        # 256 steps from C=0.0 (light fluid) to C=1.0 (heavy fluid)
        # C=0.0: Deep Midnight Navy (B=25, G=14, R=8)
        # C=0.3: Luminous Electric Cyan (B=255, G=230, R=0)
        # C=0.5: Emerald Mint (B=140, G=255, R=0)
        # C=0.7: Amber Orange (B=0, G=150, R=255)
        # C=1.0: Neon Magenta/Violet (B=180, G=0, R=255)
        cmap = np.zeros((256, 1, 3), dtype=np.uint8)
        for i in range(256):
            s = i / 255.0
            if s < 0.35:
                t = s / 0.35
                b = int(25 + t * (255 - 25))
                g = int(14 + t * (210 - 14))
                r = int(8 + t * (0 - 8))
            elif s < 0.60:
                t = (s - 0.35) / 0.25
                b = int(255 + t * (80 - 255))
                g = int(210 + t * (255 - 210))
                r = int(0 + t * (80 - 0))
            elif s < 0.82:
                t = (s - 0.60) / 0.22
                b = int(80 + t * (30 - 80))
                g = int(255 + t * (120 - 255))
                r = int(80 + t * (255 - 80))
            else:
                t = (s - 0.82) / 0.18
                b = int(30 + t * (200 - 30))
                g = int(120 + t * (20 - 120))
                r = int(255 + t * (255 - 255))
            cmap[i, 0] = [b, g, r]
        self.conc_lut = cmap

    def draw_card(self, img: np.ndarray, x1: int, y1: int, x2: int, y2: int,
                  bg_bgr=(16, 12, 8), border_bgr=(65, 80, 105)):
        """Draws a semi-transparent HUD card with antialiased borders."""
        overlay = img.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), bg_bgr, -1)
        cv2.addWeighted(overlay, 0.88, img, 0.12, 0, img)
        cv2.rectangle(img, (x1, y1), (x2, y2), border_bgr, 1, lineType=cv2.LINE_AA)

    def render_frame(
        self,
        sim: RayleighTaylorSimulation,
        telemetry: RTTelemetryPoint,
        history: List[RTTelemetryPoint],
    ) -> np.ndarray:
        """Renders one master 1080x1920 frame containing HUD and physical simulation."""
        # Canvas: Deep Cosmic Void
        frame = np.full((self.height, self.width, 3), (12, 8, 5), dtype=np.uint8)

        # Subtle background grid
        for gy in range(0, self.height, 60):
            cv2.line(frame, (0, gy), (self.width, gy), (18, 14, 10), 1)
        for gx in range(0, self.width, 60):
            cv2.line(frame, (gx, 0), (gx, self.height), (18, 14, 10), 1)

        # -------------------------------------------------------------
        # 1. RENDER FLUID MECHANICS VIEWPORT
        # -------------------------------------------------------------
        self.draw_card(frame, self.sim_x1, self.sim_y1, self.sim_x2, self.sim_y2,
                       bg_bgr=(10, 7, 5), border_bgr=(80, 105, 135))

        # Map simulation concentration field C to 8-bit image
        c_uint8 = np.clip(sim.C * 255.0, 0, 255).astype(np.uint8)
        # Flip along Y because sim.Y=-Ly/2 is bottom, image y=0 is top
        c_uint8_flipped = np.flipud(c_uint8)
        c_color = cv2.applyColorMap(c_uint8_flipped, self.conc_lut)

        # Vorticity highlights: positive (counter-clockwise, cyan), negative (clockwise, orange)
        omega_flipped = np.flipud(sim.omega)
        max_om = max(1.0, float(np.percentile(np.abs(sim.omega), 98)))
        om_norm = np.clip(omega_flipped / max_om, -1.0, 1.0)

        om_pos = np.clip(om_norm, 0.0, 1.0)
        om_neg = np.clip(-om_norm, 0.0, 1.0)

        # Blend vorticity glow onto concentration field
        glow_layer = np.zeros_like(c_color, dtype=np.float32)
        glow_layer[:, :, 0] += om_pos * 180.0  # Blue
        glow_layer[:, :, 1] += om_pos * 120.0  # Green
        glow_layer[:, :, 2] += om_neg * 220.0  # Red
        glow_layer[:, :, 1] += om_neg * 100.0  # Amber

        sim_blended = np.clip(c_color.astype(np.float32) * 0.85 + glow_layer * 0.40, 0, 255).astype(np.uint8)
        sim_resized = cv2.resize(sim_blended, (self.sim_w - 4, self.sim_h - 4), interpolation=cv2.INTER_LINEAR)

        # Insert into frame inside safe borders
        frame[self.sim_y1 + 2:self.sim_y2 - 2, self.sim_x1 + 2:self.sim_x2 - 2] = sim_resized

        # Draw Lagrangian tracer particles
        px = sim.particle_pos[:, 0]
        py = sim.particle_pos[:, 1]
        # Map physical coordinates to viewport pixels
        # x in [0, Lx] -> [sim_x1 + 2, sim_x2 - 2]
        # y in [-Ly/2, Ly/2] -> [sim_y2 - 2, sim_y1 + 2]
        vp_px = (self.sim_x1 + 2 + (px / sim.cfg.Lx) * (self.sim_w - 4)).astype(int)
        vp_py = (self.sim_y2 - 2 - ((py + sim.cfg.Ly / 2.0) / sim.cfg.Ly) * (self.sim_h - 4)).astype(int)

        for p_idx in range(len(vp_px)):
            ix, iy = vp_px[p_idx], vp_py[p_idx]
            if self.sim_x1 + 3 < ix < self.sim_x2 - 3 and self.sim_y1 + 3 < iy < self.sim_y2 - 3:
                is_heavy = sim.particle_orig_layer[p_idx] > 0
                color_p = (255, 60, 220) if is_heavy else (255, 240, 40)
                cv2.circle(frame, (ix, iy), 2, color_p, -1, lineType=cv2.LINE_AA)

        # Interface midline tracker: overlay reference line at initial interface y=0
        ref_mid_y = int(self.sim_y1 + 2 + 0.5 * (self.sim_h - 4))
        cv2.line(frame, (self.sim_x1 + 4, ref_mid_y), (self.sim_x2 - 4, ref_mid_y), (60, 80, 100), 1, cv2.LINE_AA)

        # Viewport corner labels
        cv2.putText(frame, "HEAVY FLUID (rho_2) [DOWNWARD ACCELERATION]",
                    (self.sim_x1 + 16, self.sim_y1 + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (200, 160, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, "LIGHT FLUID (rho_1) [BUOYANT BUBBLE RISE]",
                    (self.sim_x1 + 16, self.sim_y2 - 16), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (255, 220, 100), 1, cv2.LINE_AA)

        # -------------------------------------------------------------
        # 2. TOP HEADER CARD
        # -------------------------------------------------------------
        self.draw_card(frame, self.hdr_x1, self.hdr_y1, self.hdr_x2, self.hdr_y2,
                       bg_bgr=(18, 14, 10), border_bgr=(70, 90, 120))

        # PIL text rendering for crisp typography
        img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)

        hdr_cat = "CONTINUUM LAB // MECÁNICA DE FLUIDOS II" if self.lang == "ES" else "CONTINUUM LAB // ADVANCED FLUID DYNAMICS"
        hdr_title = "INESTABILIDAD RAYLEIGH-TAYLOR: PLUMAS DE CAÍDA" if self.lang == "ES" else "RAYLEIGH-TAYLOR INSTABILITY: MUSHROOM PLUMES"
        hdr_sub = "TORQUE BAROCLÍNICO  ∇ρ × ∇p  //  LOUIVILLE & DIMONTE MIXING" if self.lang == "ES" else "BAROCLINIC TORQUE  ∇ρ × ∇p  //  DIMONTE TURBULENT MIXING"

        draw.text((self.hdr_x1 + 20, self.hdr_y1 + 14), hdr_cat, font=self.font_hdr_sub, fill=(0, 240, 255))
        draw.text((self.hdr_x1 + 20, self.hdr_y1 + 42), hdr_title, font=self.font_hdr_title, fill=(255, 255, 255))
        draw.text((self.hdr_x1 + 20, self.hdr_y1 + 84), hdr_sub, font=self.font_panel_meta, fill=(160, 185, 215))

        # -------------------------------------------------------------
        # 3. TELEMETRY BADGES (3 COLUMNS)
        # -------------------------------------------------------------
        # Badge 1: Atwood Number
        self.draw_card(frame, self.b1_x1, self.badge_y1, self.b1_x2, self.badge_y2,
                       bg_bgr=(18, 14, 10), border_bgr=(65, 85, 110))
        # Badge 2: Growth Rate / Vorticity
        self.draw_card(frame, self.b2_x1, self.badge_y1, self.b2_x2, self.badge_y2,
                       bg_bgr=(18, 14, 10), border_bgr=(65, 85, 110))
        # Badge 3: Mixing Zone Width
        self.draw_card(frame, self.b3_x1, self.badge_y1, self.b3_x2, self.badge_y2,
                       bg_bgr=(18, 14, 10), border_bgr=(65, 85, 110))

        # Render badge text with PIL
        b1_lbl = "NÚMERO DE ATWOOD" if self.lang == "ES" else "ATWOOD NUMBER"
        b1_val = f"A = {telemetry.atwood_number:.2f}"

        b2_lbl = "VORTICIDAD MÁXIMA" if self.lang == "ES" else "MAX VORTICITY"
        b2_val = f"|ω| = {telemetry.max_vorticity:.1f} s⁻¹"

        b3_lbl = "ANCHO DE MEZCLA" if self.lang == "ES" else "MIXING ZONE WIDTH"
        b3_val = f"h(t) = {telemetry.mixing_width:.3f} m"

        draw.text((self.b1_x1 + 16, self.badge_y1 + 12), b1_lbl, font=self.font_badge_lbl, fill=(0, 240, 255))
        draw.text((self.b1_x1 + 16, self.badge_y1 + 38), b1_val, font=self.font_badge_val, fill=(255, 255, 255))

        draw.text((self.b2_x1 + 16, self.badge_y1 + 12), b2_lbl, font=self.font_badge_lbl, fill=(255, 0, 127))
        draw.text((self.b2_x1 + 16, self.badge_y1 + 38), b2_val, font=self.font_badge_val, fill=(255, 255, 255))

        draw.text((self.b3_x1 + 16, self.badge_y1 + 12), b3_lbl, font=self.font_badge_lbl, fill=(255, 183, 3))
        draw.text((self.b3_x1 + 16, self.badge_y1 + 38), b3_val, font=self.font_badge_val, fill=(255, 255, 255))

        # -------------------------------------------------------------
        # 4. LOWER OSCILLOSCOPE PANEL
        # -------------------------------------------------------------
        self.draw_card(frame, self.panel_x1, self.panel_y1, self.panel_x2, self.panel_y2,
                       bg_bgr=(18, 14, 10), border_bgr=(70, 95, 125))

        p_title = "OSCILOSCOPIO FÍSICO // ENERGÍA CINÉTICA Y MEZCLA CUADRÁTICA" if self.lang == "ES" else "PHYSICAL OSCILLOSCOPE // KINETIC ENERGY & QUADRATIC MIXING"
        draw.text((self.panel_x1 + 20, self.panel_y1 + 10), p_title, font=self.font_panel_title, fill=(0, 240, 255))

        # Convert back to cv2 for graph plotting
        frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        # Plot telemetry curves
        plot_x1 = self.panel_x1 + 25
        plot_y1 = self.panel_y1 + 45
        plot_x2 = self.panel_x2 - 25
        plot_y2 = self.panel_y2 - 20
        plot_w = plot_x2 - plot_x1
        plot_h = plot_y2 - plot_y1

        # Background grid in oscilloscope
        cv2.rectangle(frame, (plot_x1, plot_y1), (plot_x2, plot_y2), (25, 20, 14), -1)
        for gy in np.linspace(plot_y1, plot_y2, 5):
            cv2.line(frame, (plot_x1, int(gy)), (plot_x2, int(gy)), (40, 32, 24), 1)
        for gx in np.linspace(plot_x1, plot_x2, 7):
            cv2.line(frame, (int(gx), plot_y1), (int(gx), plot_y2), (40, 32, 24), 1)

        # Plot history: h(t) and Kinetic Energy
        if len(history) > 1:
            max_t = max(1.0, history[-1].t)
            # Find max values for normalization
            max_h_hist = max(0.5, max(pt.mixing_width for pt in history))
            max_ek_hist = max(0.01, max(pt.kinetic_energy for pt in history))

            pts_h = []
            pts_ek = []
            pts_theory = []

            for pt in history:
                gx = int(plot_x1 + (pt.t / max(16.0, max_t)) * plot_w)
                # Curve 1: h(t) in Amber Gold
                gy_h = int(plot_y2 - np.clip(pt.mixing_width / max_h_hist, 0.0, 1.0) * (plot_h - 6))
                # Curve 2: E_k(t) in Neon Cyan
                gy_ek = int(plot_y2 - np.clip(pt.kinetic_energy / max_ek_hist, 0.0, 1.0) * (plot_h - 6))
                # Curve 3: Theoretical Dimonte h_theory(t) in Magenta
                gy_th = int(plot_y2 - np.clip(pt.theoretical_h / max_h_hist, 0.0, 1.0) * (plot_h - 6))

                pts_h.append((gx, gy_h))
                pts_ek.append((gx, gy_ek))
                pts_theory.append((gx, gy_th))

            # Draw lines
            for i in range(len(pts_h) - 1):
                cv2.line(frame, pts_theory[i], pts_theory[i + 1], (255, 0, 127), 1, cv2.LINE_AA)
                cv2.line(frame, pts_ek[i], pts_ek[i + 1], (255, 240, 0), 2, cv2.LINE_AA)
                cv2.line(frame, pts_h[i], pts_h[i + 1], (3, 183, 255), 2, cv2.LINE_AA)

        # Oscilloscope legends
        cv2.putText(frame, "h(t) Simulada", (plot_x1 + 10, plot_y1 + 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (3, 183, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, "E_k(t) Cinética", (plot_x1 + 130, plot_y1 + 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 240, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, "h_teorica = alpha*A*g*t^2", (plot_x1 + 250, plot_y1 + 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 0, 127), 1, cv2.LINE_AA)

        # -------------------------------------------------------------
        # 5. BOTTOM CALLOUT CARD
        # -------------------------------------------------------------
        self.draw_card(frame, self.cta_x1, self.cta_y1, self.cta_x2, self.cta_y2,
                       bg_bgr=(18, 14, 10), border_bgr=(70, 95, 125))

        img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)

        if self.lang == "ES":
            cta_title = f"FASE: {telemetry.phase_name_es.upper()}"
            cta_desc = "El torque baroclínico  -2Ag(∂C/∂x)  genera pares de vórtices que enrollan los dedos en plumas de champiñón."
        else:
            cta_title = f"STAGE: {telemetry.phase_name_en.upper()}"
            cta_desc = "Baroclinic torque  -2Ag(∂C/∂x)  injects counter-rotating vortices, rolling falling fingers into mushroom plumes."

        draw.text((self.cta_x1 + 20, self.cta_y1 + 18), cta_title, font=self.font_cta_title, fill=(0, 255, 136))
        draw.text((self.cta_x1 + 20, self.cta_y1 + 54), cta_desc, font=self.font_cta_desc, fill=(200, 220, 245))

        frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        return frame


def render_rayleigh_taylor_video(
    output_mp4: str,
    audio_wav: Optional[str] = None,
    lang: str = "ES",
    duration: float = 16.0,
    fps: int = 60,
    hero_capture_path: Optional[str] = None,
) -> str:
    """Renders the master 1080x1920 60 FPS video directly to MP4 via FFmpeg pipe."""
    cfg = RayleighTaylorConfig(duration=duration, fps=fps)
    sim = RayleighTaylorSimulation(cfg)
    renderer = MasterRayleighTaylorRenderer(fps=fps, lang=lang)

    total_frames = int(duration * fps)
    temp_video = output_mp4.replace(".mp4", "_temp.mp4")

    os.makedirs(os.path.dirname(output_mp4), exist_ok=True)

    # Launch FFmpeg pipeline
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{renderer.width}x{renderer.height}",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "17",
        temp_video
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    hero_frame_idx = int(10.5 * fps)  # 10.5s is peak mushroom plume curl!
    hero_img = None

    t0 = time.time()
    print(f"[{lang}] Rendering {total_frames} frames (1080x1920 @ {fps} FPS)...")

    for frame_idx in range(total_frames):
        target_t = frame_idx / fps
        telemetry = sim.step_to_frame(target_t)
        frame_bgr = renderer.render_frame(sim, telemetry, sim.telemetry_history)

        proc.stdin.write(frame_bgr.tobytes())

        if frame_idx == hero_frame_idx or (hero_img is None and frame_idx > 100):
            hero_img = frame_bgr.copy()

        if frame_idx % 120 == 0 or frame_idx == total_frames - 1:
            elapsed = time.time() - t0
            fps_proc = (frame_idx + 1) / max(0.001, elapsed)
            print(f"[{lang}] Frame {frame_idx + 1}/{total_frames} ({((frame_idx+1)/total_frames)*100:.1f}%) - {fps_proc:.1f} fps")
            sys.stdout.flush()

    proc.stdin.close()
    proc.wait()

    if hero_capture_path and hero_img is not None:
        os.makedirs(os.path.dirname(hero_capture_path), exist_ok=True)
        cv2.imwrite(hero_capture_path, hero_img)
        print(f"[{lang}] Hero capture saved to: {hero_capture_path}")

    # Mux audio if present
    if audio_wav and os.path.exists(audio_wav):
        print(f"[{lang}] Muxing procedural 44.1 kHz stereo audio into MP4...")
        mux_cmd = [
            "ffmpeg", "-y",
            "-i", temp_video,
            "-i", audio_wav,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_mp4
        ]
        res = subprocess.run(mux_cmd, capture_output=True)
        if res.returncode == 0:
            if os.path.exists(temp_video):
                os.remove(temp_video)
        else:
            print(f"Warning: Audio mux failed, falling back to temp video: {res.stderr.decode('utf-8', errors='ignore')}")
            if os.path.exists(output_mp4):
                os.remove(output_mp4)
            os.rename(temp_video, output_mp4)
    else:
        if os.path.exists(temp_video):
            if os.path.exists(output_mp4):
                os.remove(output_mp4)
            os.rename(temp_video, output_mp4)

    print(f"[{lang}] Video rendered successfully: {output_mp4}")
    return output_mp4
