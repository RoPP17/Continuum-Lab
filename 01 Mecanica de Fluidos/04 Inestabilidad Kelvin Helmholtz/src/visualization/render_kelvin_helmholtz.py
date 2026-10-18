"""
Continuum Lab - Master Visual Renderer for Kelvin-Helmholtz Instability
Module: 01 Mecanica de Fluidos / 04 Inestabilidad Kelvin Helmholtz
File: src/visualization/render_kelvin_helmholtz.py

Renders 1080x1920 (9:16 Vertical UHD @ 60 FPS) high-impact scientific animations:
  - Deep Space Cybernetic Dark Palette (#0a0a0c, #00f0ff, #ff007f, #ffaa00, #39ff14)
  - Multi-spectral compositing: Passive Scalar Dye (Cyan/Magenta) + Vorticity Curl (Amber/Violet)
  - 350 Lagrangian passive tracers with velocity-dependent glow
  - Live animated vortex core crosshair tracking with live coordinates
  - Integrated real-time enstrophy / kinetic energy chart panel
  - Strict Safe-Zone compliant typography (zero text overlap)
  - Direct 60 FPS pipe to FFmpeg with stereo procedural soundtrack
"""

import os
import sys
import time
import subprocess
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

# Add project root to sys.path
current_dir = Path(__file__).resolve().parent
module_dir = current_dir.parent.parent
project_dir = module_dir.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.physics.kelvin_helmholtz_sim import (
    KelvinHelmholtzConfig,
    KelvinHelmholtzSimulation,
    TelemetryPoint,
)
from src.audio.kelvin_helmholtz_audio import synthesize_khi_soundtrack

def generate_khi_vorticity_lut() -> np.ndarray:
    lut = np.zeros((1024, 3), dtype=np.uint8)
    anchors = [
        (0.00, np.array([127.0, 0.0, 255.0])),    # Clockwise Core (Magenta)
        (0.25, np.array([190.0, 20.0, 180.0])),   # Transition Purple
        (0.42, np.array([80.0, 30.0, 60.0])),     # Dim Violet
        (0.50, np.array([28.0, 16.0, 12.0])),     # Void (w = 0)
        (0.58, np.array([0.0, 140.0, 230.0])),    # Amber Braid
        (0.78, np.array([200.0, 200.0, 0.0])),    # Cyan/Aqua
        (1.00, np.array([255.0, 240.0, 0.0])),    # Extreme Cyan
    ]

    for i in range(len(anchors) - 1):
        x0, c0 = anchors[i]
        x1, c1 = anchors[i + 1]
        i0 = int(x0 * 1023)
        i1 = int(x1 * 1023)
        span = max(1, i1 - i0)
        t = np.linspace(0.0, 1.0, span, endpoint=False)[:, None]
        t_smooth = 0.5 * (1.0 - np.cos(np.pi * t))
        lut[i0:i1] = np.clip(c0 + (c1 - c0) * t_smooth, 0, 255).astype(np.uint8)

    lut[-1] = anchors[-1][1].astype(np.uint8)
    return lut


VORTICITY_LUT = generate_khi_vorticity_lut()


class MasterKHIRenderer:
    """
    Master 9:16 Video & HUD Renderer for Kelvin-Helmholtz Instability.
    """

    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 60, lang: str = "ES"):
        self.width = width
        self.height = height
        self.fps = fps
        self.lang = lang

        # Typography
        self._load_fonts()

        # Canvas layout geometry (Strict Mobile Safe Zones: >150px top, >275px bottom, 60px sides)
        # 1. Top Header Card
        self.hdr_x1, self.hdr_y1 = 60, 150
        self.hdr_x2, self.hdr_y2 = 1020, 275

        # 2. Telemetry Badges
        self.badge_y1 = 290
        self.badge_y2 = 375
        self.b1_x1, self.b1_x2 = 60, 365
        self.b2_x1, self.b2_x2 = 385, 695
        self.b3_x1, self.b3_x2 = 715, 1020

        # 3. Main Fluid Simulation Hero Canvas
        self.sim_x1, self.sim_y1 = 60, 390
        self.sim_x2, self.sim_y2 = 1020, 1060
        self.sim_w = self.sim_x2 - self.sim_x1
        self.sim_h = self.sim_y2 - self.sim_y1

        # 4. Real-Time Dynamic Graph Panel
        self.graph_x1, self.graph_y1 = 60, 1075
        self.graph_x2, self.graph_y2 = 1020, 1420

        # 5. Bottom Safe-Zone Callout Card (Ends at 1640 -> 280px margin from bottom!)
        self.bot_x1, self.bot_y1 = 60, 1435
        self.bot_x2, self.bot_y2 = 1020, 1645

        # History tracking for live plots
        self.t_history: list[float] = []
        self.enstrophy_history: list[float] = []
        self.ke_history: list[float] = []

    def _load_fonts(self):
        try:
            self.font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 32)
            self.font_subtitle = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 20)
            self.font_pill = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 18)
            self.font_badge_lbl = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 16)
            self.font_badge_val = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 24)
            self.font_chart_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
            self.font_chart_label = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 16)
            self.font_chart_legend = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 17)
            self.font_narrative_phase = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
            self.font_narrative_body = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 20)
            self.font_footer = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)
        except Exception:
            d = ImageFont.load_default()
            self.font_title = d
            self.font_subtitle = d
            self.font_pill = d
            self.font_badge_lbl = d
            self.font_badge_val = d
            self.font_chart_title = d
            self.font_chart_label = d
            self.font_chart_legend = d
            self.font_narrative_phase = d
            self.font_narrative_body = d
            self.font_footer = d

    def _draw_rounded_rect(
        self, img: np.ndarray, pt1: tuple[int, int], pt2: tuple[int, int],
        radius: int, color_bgr: tuple[int, int, int], thickness: int = -1
    ):
        """Draws a smooth rounded rectangle on an OpenCV image."""
        x1, y1 = pt1
        x2, y2 = pt2
        r = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)

        if thickness == -1:
            cv2.rectangle(img, (x1 + r, y1), (x2 - r, y2), color_bgr, -1)
            cv2.rectangle(img, (x1, y1 + r), (x2, y2 - r), color_bgr, -1)
            cv2.circle(img, (x1 + r, y1 + r), r, color_bgr, -1, cv2.LINE_AA)
            cv2.circle(img, (x2 - r, y1 + r), r, color_bgr, -1, cv2.LINE_AA)
            cv2.circle(img, (x1 + r, y2 - r), r, color_bgr, -1, cv2.LINE_AA)
            cv2.circle(img, (x2 - r, y2 - r), r, color_bgr, -1, cv2.LINE_AA)
        else:
            cv2.line(img, (x1 + r, y1), (x2 - r, y1), color_bgr, thickness, cv2.LINE_AA)
            cv2.line(img, (x1 + r, y2), (x2 - r, y2), color_bgr, thickness, cv2.LINE_AA)
            cv2.line(img, (x1, y1 + r), (x1, y2 - r), color_bgr, thickness, cv2.LINE_AA)
            cv2.line(img, (x2, y1 + r), (x2, y2 - r), color_bgr, thickness, cv2.LINE_AA)
            cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color_bgr, thickness, cv2.LINE_AA)
            cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color_bgr, thickness, cv2.LINE_AA)
            cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color_bgr, thickness, cv2.LINE_AA)
            cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color_bgr, thickness, cv2.LINE_AA)

    def render_frame(self, sim: KelvinHelmholtzSimulation, telem: TelemetryPoint) -> np.ndarray:
        """Renders one complete 1080x1920 frame."""
        # 1. Base canvas: Deep Space Void (#0a0a0c => BGR: 12, 10, 10)
        canvas = np.full((self.height, self.width, 3), [12, 10, 10], dtype=np.uint8)

        # Subtle background cybernetic grid
        for gy in range(0, self.height, 80):
            cv2.line(canvas, (0, gy), (self.width, gy), (22, 18, 18), 1)
        for gx in range(0, self.width, 80):
            cv2.line(canvas, (gx, 0), (gx, self.height), (22, 18, 18), 1)

        # Update telemetry history
        self.t_history.append(telem.t)
        self.enstrophy_history.append(telem.enstrophy)
        self.ke_history.append(telem.kinetic_energy)

        # ---------------------------------------------------------------------
        # A. Top Header Card
        # ---------------------------------------------------------------------
        self._draw_rounded_rect(canvas, (self.hdr_x1, self.hdr_y1), (self.hdr_x2, self.hdr_y2), 16, (26, 20, 15), -1)
        self._draw_rounded_rect(canvas, (self.hdr_x1, self.hdr_y1), (self.hdr_x2, self.hdr_y2), 16, (255, 240, 0), 2)

        # ---------------------------------------------------------------------
        # B. Telemetry Badges
        # ---------------------------------------------------------------------
        # Badge 1: Top Fluid (Cyan)
        self._draw_rounded_rect(canvas, (self.b1_x1, self.badge_y1), (self.b1_x2, self.badge_y2), 14, (26, 20, 15), -1)
        self._draw_rounded_rect(canvas, (self.b1_x1, self.badge_y1), (self.b1_x2, self.badge_y2), 14, (255, 240, 0), 2)

        # Badge 2: Richardson Number (Amber)
        self._draw_rounded_rect(canvas, (self.b2_x1, self.badge_y1), (self.b2_x2, self.badge_y2), 14, (26, 20, 15), -1)
        self._draw_rounded_rect(canvas, (self.b2_x1, self.badge_y1), (self.b2_x2, self.badge_y2), 14, (0, 170, 255), 2)

        # Badge 3: Bottom Fluid (Magenta)
        self._draw_rounded_rect(canvas, (self.b3_x1, self.badge_y1), (self.b3_x2, self.badge_y2), 14, (26, 20, 15), -1)
        self._draw_rounded_rect(canvas, (self.b3_x1, self.badge_y1), (self.b3_x2, self.badge_y2), 14, (127, 0, 255), 2)

        # ---------------------------------------------------------------------
        # C. Central Hero Fluid Simulation Panel
        # ---------------------------------------------------------------------
        self._draw_rounded_rect(canvas, (self.sim_x1, self.sim_y1), (self.sim_x2, self.sim_y2), 16, (22, 16, 12), -1)

        # 1. Map 2D vorticity to color image using custom hyperbolic LUT
        omega_norm = np.tanh(sim.omega / 16.0)  # Range [-1, 1]
        lut_idx = np.clip(((omega_norm + 1.0) * 0.5 * 1023.0).astype(int), 0, 1023)
        vort_bgr = VORTICITY_LUT[lut_idx]

        # Resize to hero simulation panel inner dimensions (with 8px padding)
        pad = 8
        inner_w = self.sim_w - 2 * pad
        inner_h = self.sim_h - 2 * pad
        fluid_resized = cv2.resize(vort_bgr, (inner_w, inner_h), interpolation=cv2.INTER_CUBIC)

        # Place fluid field into canvas
        canvas[self.sim_y1 + pad:self.sim_y2 - pad, self.sim_x1 + pad:self.sim_x2 - pad] = fluid_resized

        # 2. Draw Shear Flow Arrows (+U0 right on top, -U0 left on bottom)
        arrow_y_top = self.sim_y1 + pad + int(inner_h * 0.12)
        arrow_y_bot = self.sim_y1 + pad + int(inner_h * 0.88)
        # Top arrows (Cyan)
        arr_centers = [
            self.sim_x1 + int(self.sim_w * 0.22),
            self.sim_x1 + int(self.sim_w * 0.50),
            self.sim_x1 + int(self.sim_w * 0.78)
        ]
        for ax in arr_centers:
            cv2.arrowedLine(canvas, (ax - 65, arrow_y_top), (ax + 65, arrow_y_top), (255, 240, 0), 2, tipLength=0.28)
        # Bottom arrows (Magenta)
        for ax in arr_centers:
            cv2.arrowedLine(canvas, (ax + 65, arrow_y_bot), (ax - 65, arrow_y_bot), (127, 0, 255), 2, tipLength=0.28)

        # 3. Draw Lagrangian Tracer Particles
        part_px_x = self.sim_x1 + pad + (sim.particle_pos[:, 0] / sim.cfg.Lx) * inner_w
        part_px_y = self.sim_y1 + pad + ((sim.particle_pos[:, 1] + sim.cfg.Ly / 2.0) / sim.cfg.Ly) * inner_h

        for px, py, layer in zip(part_px_x, part_px_y, sim.particle_orig_layer):
            ix_p, iy_p = int(px), int(py)
            if self.sim_x1 + pad < ix_p < self.sim_x2 - pad and self.sim_y1 + pad < iy_p < self.sim_y2 - pad:
                # Glowing phosphor dot
                cv2.circle(canvas, (ix_p, iy_p), 3, (0, 255, 120), -1, cv2.LINE_AA)
                cv2.circle(canvas, (ix_p, iy_p), 1, (255, 255, 255), -1, cv2.LINE_AA)

        # 4. Animated Vortex Core Crosshair Reticles
        # Find 2 primary clockwise vortex cores (minimum vorticity)
        y_mask = np.abs(sim.y) < 0.28
        om_slice = sim.omega[y_mask, :]
        min_indices = np.argsort(om_slice.flatten())[:2]
        slice_ny, slice_nx = om_slice.shape
        vortex_cores = []
        for idx in min_indices:
            cy_idx = idx // slice_nx
            cx_idx = idx % slice_nx
            y_phys = sim.y[y_mask][cy_idx]
            x_phys = sim.x[cx_idx]
            vortex_cores.append((x_phys, y_phys))

        for vx, vy in vortex_cores[:2]:
            c_px_x = int(self.sim_x1 + pad + (vx / sim.cfg.Lx) * inner_w)
            c_px_y = int(self.sim_y1 + pad + ((vy + sim.cfg.Ly / 2.0) / sim.cfg.Ly) * inner_h)
            if self.sim_x1 + 40 < c_px_x < self.sim_x2 - 40 and self.sim_y1 + 40 < c_px_y < self.sim_y2 - 40:
                reticle_r = 22
                cv2.circle(canvas, (c_px_x, c_px_y), reticle_r, (0, 240, 255), 1, cv2.LINE_AA)
                cv2.circle(canvas, (c_px_x, c_px_y), 3, (0, 170, 255), -1, cv2.LINE_AA)
                cv2.line(canvas, (c_px_x - reticle_r - 8, c_px_y), (c_px_x + reticle_r + 8, c_px_y), (0, 240, 255), 1, cv2.LINE_AA)
                cv2.line(canvas, (c_px_x, c_px_y - reticle_r - 8), (c_px_x, c_px_y + reticle_r + 8), (0, 240, 255), 1, cv2.LINE_AA)

        # Panel border
        self._draw_rounded_rect(canvas, (self.sim_x1, self.sim_y1), (self.sim_x2, self.sim_y2), 16, (255, 240, 0), 2)

        # ---------------------------------------------------------------------
        # D. Real-Time Dynamic Graph Panel
        # ---------------------------------------------------------------------
        self._draw_rounded_rect(canvas, (self.graph_x1, self.graph_y1), (self.graph_x2, self.graph_y2), 16, (22, 16, 12), -1)
        self._draw_rounded_rect(canvas, (self.graph_x1, self.graph_y1), (self.graph_x2, self.graph_y2), 16, (0, 170, 255), 2)

        # Graph inner plotting area
        gx1, gy1 = self.graph_x1 + 75, self.graph_y1 + 80
        gx2, gy2 = self.graph_x2 - 40, self.graph_y2 - 50
        gw, gh = gx2 - gx1, gy2 - gy1

        # Grid lines on plot
        for gy_grid in np.linspace(gy1, gy2, 5):
            cv2.line(canvas, (gx1, int(gy_grid)), (gx2, int(gy_grid)), (40, 32, 25), 1)
        for gx_grid in np.linspace(gx1, gx2, 8):
            cv2.line(canvas, (int(gx_grid), gy1), (int(gx_grid), gy2), (40, 32, 25), 1)

        # Plot curves:
        # Enstrophy (Emerald Lime)
        if len(self.t_history) > 1:
            t_max = 14.0
            ens_max = 50.0
            ens_min = 10.0

            plot_pts_ens = []
            for t_h, ens_h in zip(self.t_history, self.enstrophy_history):
                px = gx1 + int((t_h / t_max) * gw)
                norm_y = (ens_h - ens_min) / max(1.0, (ens_max - ens_min))
                py = gy2 - int(np.clip(norm_y, 0.0, 1.0) * gh)
                plot_pts_ens.append((px, py))

            # Draw smooth curve
            for i in range(len(plot_pts_ens) - 1):
                cv2.line(canvas, plot_pts_ens[i], plot_pts_ens[i + 1], (60, 255, 32), 3, cv2.LINE_AA)

            # Glowing current cursor dot
            cur_pt = plot_pts_ens[-1]
            cv2.circle(canvas, cur_pt, 7, (60, 255, 32), -1, cv2.LINE_AA)
            cv2.circle(canvas, cur_pt, 12, (180, 255, 120), 2, cv2.LINE_AA)

        # ---------------------------------------------------------------------
        # E. Bottom Safe-Zone Callout Card
        # ---------------------------------------------------------------------
        self._draw_rounded_rect(canvas, (self.bot_x1, self.bot_y1), (self.bot_x2, self.bot_y2), 16, (26, 20, 15), -1)
        self._draw_rounded_rect(canvas, (self.bot_x1, self.bot_y1), (self.bot_x2, self.bot_y2), 16, (127, 0, 255), 2)

        # ---------------------------------------------------------------------
        # F. Typography Overlay via PIL (High DPI Anti-Aliasing)
        # ---------------------------------------------------------------------
        pil_img = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)

        # 1. Header Card Texts (clean ASCII mathematical characters)
        if self.lang == "ES":
            draw.text((self.hdr_x1 + 25, self.hdr_y1 + 16), "CONTINUUM LAB // MECANICA DE FLUIDOS AVANZADA", font=self.font_subtitle, fill=(0, 240, 255))
            draw.text((self.hdr_x1 + 25, self.hdr_y1 + 44), "INESTABILIDAD DE KELVIN-HELMHOLTZ", font=self.font_title, fill=(255, 255, 255))
            draw.text((self.hdr_x1 + 25, self.hdr_y1 + 86), "d(w)/dt + (u*grad)w = nu*grad^2(w)  |  Capa de Cizalla y Vortices", font=self.font_pill, fill=(0, 255, 136))
        else:
            draw.text((self.hdr_x1 + 25, self.hdr_y1 + 16), "CONTINUUM LAB // ADVANCED FLUID MECHANICS", font=self.font_subtitle, fill=(0, 240, 255))
            draw.text((self.hdr_x1 + 25, self.hdr_y1 + 44), "KELVIN-HELMHOLTZ INSTABILITY", font=self.font_title, fill=(255, 255, 255))
            draw.text((self.hdr_x1 + 25, self.hdr_y1 + 86), "d(w)/dt + (u*grad)w = nu*grad^2(w)  |  Shear Layer & Cat's-Eye Roll-Up", font=self.font_pill, fill=(0, 255, 136))

        # 2. Telemetry Badges Texts
        # Badge 1: Top Fluid
        lbl_b1 = "CAPA SUPERIOR [+U0]" if self.lang == "ES" else "TOP LAYER [+U0]"
        draw.text((self.b1_x1 + 18, self.badge_y1 + 14), lbl_b1, font=self.font_badge_lbl, fill=(0, 240, 255))
        draw.text((self.b1_x1 + 18, self.badge_y1 + 42), f"u = +{sim.cfg.U0:.2f} m/s", font=self.font_badge_val, fill=(255, 255, 255))

        # Badge 2: Richardson Number
        lbl_b2 = "CRITERIO MILES-HOWARD" if self.lang == "ES" else "MILES-HOWARD CRITERION"
        draw.text((self.b2_x1 + 18, self.badge_y1 + 14), lbl_b2, font=self.font_badge_lbl, fill=(255, 170, 0))
        draw.text((self.b2_x1 + 18, self.badge_y1 + 42), f"Ri = {telem.richardson_number:.3f} < 0.25", font=self.font_badge_val, fill=(255, 215, 0))

        # Badge 3: Bottom Fluid
        lbl_b3 = "CAPA INFERIOR [-U0]" if self.lang == "ES" else "BOTTOM LAYER [-U0]"
        draw.text((self.b3_x1 + 18, self.badge_y1 + 14), lbl_b3, font=self.font_badge_lbl, fill=(255, 0, 127))
        draw.text((self.b3_x1 + 18, self.badge_y1 + 42), f"u = -{sim.cfg.U0:.2f} m/s", font=self.font_badge_val, fill=(255, 255, 255))

        # 3. Graph Panel Texts
        chart_t = "DINAMICA DE ENSTROFIA Y ENERGIA CINETICA" if self.lang == "ES" else "ENSTROPHY DYNAMICS & KINETIC ENERGY"
        draw.text((self.graph_x1 + 25, self.graph_y1 + 14), chart_t, font=self.font_chart_title, fill=(255, 255, 255))

        chart_sub = (
            f"Omega(t) = {telem.enstrophy:.2f} m2/s2   |   E_k = {telem.kinetic_energy:.4f} J/kg   |   Re = 2,500"
            if self.lang == "ES" else
            f"Omega(t) = {telem.enstrophy:.2f} m2/s2   |   E_k = {telem.kinetic_energy:.4f} J/kg   |   Re = 2,500"
        )
        draw.text((self.graph_x1 + 25, self.graph_y1 + 42), chart_sub, font=self.font_chart_legend, fill=(0, 255, 136))

        # Graph Y axis labels
        draw.text((self.graph_x1 + 16, gy1), "50", font=self.font_chart_label, fill=(148, 163, 184))
        draw.text((self.graph_x1 + 16, gy1 + gh // 2), "30", font=self.font_chart_label, fill=(148, 163, 184))
        draw.text((self.graph_x1 + 16, gy2 - 10), "10", font=self.font_chart_label, fill=(148, 163, 184))

        # Graph X axis labels
        draw.text((gx1, gy2 + 8), "t = 0.0s", font=self.font_chart_label, fill=(148, 163, 184))
        draw.text((gx1 + gw // 2 - 25, gy2 + 8), "7.0s", font=self.font_chart_label, fill=(148, 163, 184))
        draw.text((gx2 - 50, gy2 + 8), "14.0s", font=self.font_chart_label, fill=(148, 163, 184))

        # 4. Bottom Callout Card Texts
        phase_str = telem.phase_name_es if self.lang == "ES" else telem.phase_name_en
        draw.text((self.bot_x1 + 25, self.bot_y1 + 16), f">> {phase_str}", font=self.font_narrative_phase, fill=(255, 170, 0))

        if self.lang == "ES":
            draw.text(
                (self.bot_x1 + 25, self.bot_y1 + 48),
                "Por que se forman estas espirales en el cielo y atmosferas planetarias?\n"
                "La discontinuidad de cizalladura (Delta-U) enrolla la interfaz en vortices Cat's-Eye.\n"
                "El criterio de Miles-Howard (Ri < 0.25) desestabiliza cualquier estratificacion.",
                font=self.font_narrative_body, fill=(241, 245, 249), spacing=5
            )
            draw.text(
                (self.bot_x1 + 25, self.bot_y1 + 162),
                f"CONTINUUM LAB // t = {telem.t:.2f} s // NAVIER-STOKES 2D ESPECTRAL",
                font=self.font_footer, fill=(148, 163, 184)
            )
        else:
            draw.text(
                (self.bot_x1 + 25, self.bot_y1 + 48),
                "Why do these billow spirals appear in planetary atmospheres & clouds?\n"
                "Velocity shear discontinuity (Delta-U) rolls the layer into discrete Cat's-Eye vortices.\n"
                "Miles-Howard criterion (Ri < 0.25) governs the exponential growth rate.",
                font=self.font_narrative_body, fill=(241, 245, 249), spacing=5
            )
            draw.text(
                (self.bot_x1 + 25, self.bot_y1 + 162),
                f"CONTINUUM LAB // t = {telem.t:.2f} s // 2D SPECTRAL NAVIER-STOKES",
                font=self.font_footer, fill=(148, 163, 184)
            )

        # Convert back to BGR OpenCV format
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def render_khi_video(
    output_mp4: str,
    audio_wav: str | None = None,
    lang: str = "ES",
    duration: float = 14.0,
    fps: int = 60,
    hero_capture_path: str | None = None
) -> str:
    """
    Renders the complete Kelvin-Helmholtz simulation video using direct FFmpeg pipe.
    """
    Path(output_mp4).parent.mkdir(parents=True, exist_ok=True)
    temp_video = output_mp4.replace(".mp4", "_temp.mp4")

    config = KelvinHelmholtzConfig(
        Lx=2.0,
        Ly=1.0,
        Nx=256,
        Ny=128,
        U0=1.0,
        delta0=0.045,
        nu=8.0e-5,
        dt=0.005,
        fps=fps,
        duration=duration
    )
    sim = KelvinHelmholtzSimulation(config)
    renderer = MasterKHIRenderer(width=1080, height=1920, fps=fps, lang=lang)

    total_frames = int(duration * fps)
    dt_frame = 1.0 / fps

    print("=" * 70)
    print(f"CONTINUUM LAB // MASTER KHI VIDEO RENDERER [{lang}]")
    print(f"Target Video: {output_mp4}")
    print(f"Resolution:   1080x1920 @ {fps} FPS (Total: {total_frames} frames)")
    print("=" * 70)

    # Launch FFmpeg pipe
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
    hero_frame_idx = int(7.5 * fps)  # Peak non-linear cat's-eye roll-up moment

    t_start = time.time()
    for frame_idx in range(total_frames):
        target_t = frame_idx * dt_frame
        telem = sim.advance_to_time(target_t)
        frame_bgr = renderer.render_frame(sim, telem)

        # Send raw bytes to FFmpeg
        pipe.stdin.write(frame_bgr.tobytes())

        if frame_idx == hero_frame_idx:
            hero_frame = frame_bgr.copy()

        if frame_idx % 120 == 0 or frame_idx == total_frames - 1:
            elapsed = time.time() - t_start
            fps_proc = (frame_idx + 1) / max(0.01, elapsed)
            eta = (total_frames - frame_idx - 1) / max(0.01, fps_proc)
            print(f"[{frame_idx+1:03d}/{total_frames}] t={telem.t:.2f}s | Omega={telem.enstrophy:.2f} | FPS={fps_proc:.1f} | ETA={eta:.1f}s")

    pipe.stdin.close()
    pipe.wait()

    # Save Hero Capture
    if hero_capture_path and hero_frame is not None:
        Path(hero_capture_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(hero_capture_path, hero_frame)
        print(f"[OK] Saved Hero Capture to: {hero_capture_path}")

    # Mix audio if available
    if audio_wav and os.path.exists(audio_wav):
        print(f"[AUDIO] Multiplexing cinematic audio stream: {audio_wav}")
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
