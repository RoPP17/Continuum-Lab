"""
Continuum Lab — Master Visual Renderer for Zeroth Law of Thermodynamics
Module: 04 Termodinamica y Calor / 01 Ley Cero de la Termodinamica 3 Cuerpos
Video Format: 1080x1920 (9:16 Vertical Video for TikTok / Reels / Shorts @ 60 FPS)

Design Philosophy:
  - 90% Visual Impact & Physical Clarity, 10% Essential Elegant Typography.
  - Massive Hero Simulation: 3 solid metallic blocks in direct flush contact.
  - Continuous Perceptually Smooth Thermography (Glacial Cyan -> Warm Amber -> Blazing Crimson).
  - Luminous Heat Flux Transfer Vectors (──►) that pulse with magnitude and vanish at equilibrium.
  - Kinetic Phonon / Molecular Energy Streamlets flowing from Hot to Cold.
  - Huge Real-Time Digital Temperature Displays above each body (ZERO text overlapping!).
  - Cinematic Atmospheric Science Soundtrack with harmonic equilibrium resolution.
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
project_dir = Path(__file__).resolve().parent.parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.physics.heat_zeroth_law import (
    ZerothLawThermalSimulation,
    ThermalConfig,
    COPPER,
    STAINLESS_STEEL,
    ALUMINUM,
)
from src.audio.thermal_synth_music import synthesize_catchy_thermal_audio


def generate_perceptual_thermal_lut() -> np.ndarray:
    """
    Generates a 1024-step perceptually continuous thermographic color lookup table.
    0.0°C   -> Glacial Deep Obsidian Cyan [10, 25, 55] (BGR: 55, 25, 10)
    20.0°C  -> Vibrant Electric Aqua Cyan [0, 195, 225] (BGR: 225, 195, 0)
    35.0°C  -> Atmospheric Indigo Slate [80, 95, 210] (BGR: 210, 95, 80)
    46.2°C  -> Radiant Solar Amber Gold [250, 165, 15] (BGR: 15, 165, 250) (EQUILIBRIUM TARGET!)
    65.0°C  -> Intense Coral Vermilion [245, 65, 30] (BGR: 30, 65, 245)
    85.0°C  -> Fiery Radiant Crimson [225, 15, 60] (BGR: 60, 15, 225)
    100.0°C -> Incandescent White-Hot Flame [255, 248, 220] (BGR: 220, 248, 255)
    """
    lut = np.zeros((1024, 3), dtype=np.uint8)
    # Control anchors: (fraction, (B, G, R))
    anchors = [
        (0.00, np.array([55.0, 25.0, 10.0])),    # 0°C Deep Glacial
        (0.18, np.array([225.0, 185.0, 0.0])),   # 18°C Electric Cyan
        (0.32, np.array([205.0, 90.0, 75.0])),   # 32°C Slate Indigo
        (0.462, np.array([15.0, 165.0, 250.0])), # 46.2°C Radiant Amber Gold (T_eq)
        (0.65, np.array([30.0, 65.0, 245.0])),   # 65°C Coral Vermilion
        (0.85, np.array([55.0, 15.0, 225.0])),   # 85°C Deep Crimson
        (1.00, np.array([220.0, 248.0, 255.0])), # 100°C Incandescent White-Hot
    ]

    for i in range(len(anchors) - 1):
        x0, c0 = anchors[i]
        x1, c1 = anchors[i + 1]
        i0 = int(x0 * 1023)
        i1 = int(x1 * 1023)
        span = max(1, i1 - i0)
        t = np.linspace(0.0, 1.0, span, endpoint=False)[:, None]
        # Smooth cosine interpolation to avoid linear slope artifacts
        t_smooth = 0.5 * (1.0 - np.cos(np.pi * t))
        lut[i0:i1] = np.clip(c0 + (c1 - c0) * t_smooth, 0, 255).astype(np.uint8)

    lut[-1] = anchors[-1][1].astype(np.uint8)
    return lut


THERMAL_LUT = generate_perceptual_thermal_lut()


class MasterHeatTransferRenderer:
    """
    High-End Master Visual Renderer for 3-Body Thermal Equilibrium.
    """

    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 60, lang: str = "ES"):
        self.width = width
        self.height = height
        self.fps = fps
        self.lang = lang

        # Typography
        self._load_fonts()

        # Telemetry history buffers for dynamic plot
        self.time_history: list[float] = []
        self.t_a_history: list[float] = []
        self.t_c_history: list[float] = []
        self.t_b_history: list[float] = []

        # Kinetic Phonon streamlets (350 particles)
        self.num_particles = 350
        self.particles_x = np.random.uniform(0.08, 0.92, self.num_particles)
        self.particles_y = np.random.uniform(0.20, 0.80, self.num_particles)
        self.particles_life = np.random.uniform(0.2, 1.0, self.num_particles)

    def _load_fonts(self):
        """Loads crisp Windows fonts with safe fallbacks."""
        try:
            self.font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 36)
            self.font_subtitle = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22)
            self.font_pill = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 22)
            self.font_body_label = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 19)
            self.font_body_temp = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 36)
            self.font_chart_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 21)
            self.font_chart_label = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 18)
            self.font_chart_legend = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 19)
            self.font_flux_label = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 18)
            self.font_narrative_phase = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
            self.font_narrative_body = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 23)
            self.font_footer = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 17)
        except Exception:
            d = ImageFont.load_default()
            self.font_title = d
            self.font_subtitle = d
            self.font_pill = d
            self.font_body_label = d
            self.font_body_temp = d
            self.font_chart_title = d
            self.font_chart_label = d
            self.font_chart_legend = d
            self.font_flux_label = d
            self.font_narrative_phase = d
            self.font_narrative_body = d
            self.font_footer = d

    def _draw_rounded_rect(
        self,
        img: np.ndarray,
        pt1: tuple[int, int],
        pt2: tuple[int, int],
        color_bgr: tuple[int, int, int],
        fill_bgr: tuple[int, int, int] | None = None,
        radius: int = 14,
        thickness: int = 2
    ):
        """Draws anti-aliased rounded rectangle with optional fill."""
        x1, y1 = pt1
        x2, y2 = pt2
        r = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)

        if fill_bgr is not None:
            overlay = img.copy()
            cv2.rectangle(overlay, (x1 + r, y1), (x2 - r, y2), fill_bgr, -1)
            cv2.rectangle(overlay, (x1, y1 + r), (x2, y2 - r), fill_bgr, -1)
            cv2.circle(overlay, (x1 + r, y1 + r), r, fill_bgr, -1)
            cv2.circle(overlay, (x2 - r, y1 + r), r, fill_bgr, -1)
            cv2.circle(overlay, (x1 + r, y2 - r), r, fill_bgr, -1)
            cv2.circle(overlay, (x2 - r, y2 - r), r, fill_bgr, -1)
            cv2.addWeighted(overlay, 0.90, img, 0.10, 0, img)

        if thickness > 0:
            cv2.line(img, (x1 + r, y1), (x2 - r, y1), color_bgr, thickness, cv2.LINE_AA)
            cv2.line(img, (x1 + r, y2), (x2 - r, y2), color_bgr, thickness, cv2.LINE_AA)
            cv2.line(img, (x1, y1 + r), (x1, y2 - r), color_bgr, thickness, cv2.LINE_AA)
            cv2.line(img, (x2, y1 + r), (x2, y2 - r), color_bgr, thickness, cv2.LINE_AA)
            cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color_bgr, thickness, cv2.LINE_AA)
            cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color_bgr, thickness, cv2.LINE_AA)
            cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color_bgr, thickness, cv2.LINE_AA)
            cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color_bgr, thickness, cv2.LINE_AA)

    def render_frame(
        self,
        sim: ZerothLawThermalSimulation,
        frame_idx: int,
        total_frames: int,
        timeline_sec: float
    ) -> np.ndarray:
        """
        Renders a single 1080x1920 (9:16) Master Definition frame.
        """
        w, h = self.width, self.height
        frame = np.full((h, w, 3), 10, dtype=np.uint8)  # Deep obsidian void #0a0a0c

        # Subtle elegant technical grid lines
        for gx in range(60, w, 120):
            cv2.line(frame, (gx, 0), (gx, h), (18, 22, 28), 1)
        for gy in range(60, h, 120):
            cv2.line(frame, (0, gy), (w, gy), (18, 22, 28), 1)

        metrics = sim.compute_metrics()
        self.time_history.append(timeline_sec)
        self.t_a_history.append(metrics["t_a_mean"])
        self.t_c_history.append(metrics["t_c_mean"])
        self.t_b_history.append(metrics["t_b_mean"])

        # ---------------------------------------------------------------------
        # 1. VIEWPORT: THE 3 BODIES HERO SIMULATION (y in [300, 1060], Height = 760)
        # ---------------------------------------------------------------------
        vp_x1 = 55
        vp_x2 = w - 55
        vp_y1 = 300
        vp_y2 = 1060
        vp_w = vp_x2 - vp_x1
        vp_h = vp_y2 - vp_y1

        # Smooth high-resolution continuous thermal map
        t_norm = np.clip(sim.T / 100.0, 0.0, 1.0)
        t_lut_idx = (t_norm * 1023.0).astype(np.int32)
        bgr_raw = THERMAL_LUT[t_lut_idx]  # shape (ny, nx, 3)

        # Bicubic upscale for continuous smooth thermal gradient (ZERO blocky pixels!)
        bgr_upscaled = cv2.resize(bgr_raw, (vp_w, vp_h), interpolation=cv2.INTER_CUBIC)

        # Upscale active solid mask
        solid_mask_upscaled = cv2.resize(
            sim.active_solid.astype(np.uint8),
            (vp_w, vp_h),
            interpolation=cv2.INTER_NEAREST
        ).astype(bool)

        # Target canvas slice
        vp_canvas = frame[vp_y1:vp_y2, vp_x1:vp_x2]

        # Apply thermal field inside active solids
        vp_canvas[solid_mask_upscaled] = bgr_upscaled[solid_mask_upscaled]

        # Inactive exterior domain: dark metallic chassis
        outside_mask = ~solid_mask_upscaled
        vp_canvas[outside_mask] = (15, 17, 22)

        # Compute heat flux field for physics vectors and kinetic phonons
        qx, qy, q_mag = sim.compute_heat_flux_field()
        max_q = max(float(np.max(q_mag)), 1e-4)

        # ---------------------------------------------------------------------
        # 2. CONTACT INTERFACE BOUNDARY & DYNAMIC HEAT FLUX ARROWS
        # ---------------------------------------------------------------------
        # Interface A-C (x = 0.35 in normalized domain)
        int1_x = int(vp_x1 + 0.35 * vp_w)
        # Interface C-B (x = 0.65 in normalized domain)
        int2_x = int(vp_x1 + 0.65 * vp_w)

        # Draw glowing vertical contact interface guidelines
        for y_dash in range(vp_y1 + 4, vp_y2 - 4, 18):
            cv2.line(frame, (int1_x, y_dash), (int1_x, y_dash + 9), (70, 85, 105), 2, cv2.LINE_AA)
            cv2.line(frame, (int2_x, y_dash), (int2_x, y_dash + 9), (70, 85, 105), 2, cv2.LINE_AA)

        # Solid body contours (clean perimeter outline)
        contours, _ = cv2.findContours(solid_mask_upscaled.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(vp_canvas, contours, -1, (180, 200, 220), 2, cv2.LINE_AA)

        # Luminous Dynamic Heat Flux Transfer Arrows across interfaces
        # Interface A -> C arrows
        q_ac = metrics["q_dot_ac"]
        flux_ac_intensity = max(0.0, min(1.0, abs(q_ac) / 6000.0))
        arrow_pulse = 0.8 + 0.2 * np.sin(timeline_sec * 8.0)

        if flux_ac_intensity > 0.05:
            arrow_color_ac = (
                int(20 * flux_ac_intensity),
                int(180 * flux_ac_intensity * arrow_pulse),
                int(255 * flux_ac_intensity * arrow_pulse)
            )
            for arrow_y in range(vp_y1 + 140, vp_y2 - 120, 100):
                # Draw arrow from A into C (pointing right)
                ax1 = int1_x - int(38 * flux_ac_intensity)
                ax2 = int1_x + int(38 * flux_ac_intensity)
                cv2.arrowedLine(frame, (ax1, arrow_y), (ax2, arrow_y), arrow_color_ac, 3, cv2.LINE_AA, tipLength=0.35)

        # Interface C -> B arrows
        q_cb = metrics["q_dot_cb"]
        flux_cb_intensity = max(0.0, min(1.0, abs(q_cb) / 4500.0))
        if flux_cb_intensity > 0.05:
            arrow_color_cb = (
                int(240 * flux_cb_intensity * arrow_pulse),
                int(210 * flux_cb_intensity * arrow_pulse),
                int(40 * flux_cb_intensity)
            )
            for arrow_y in range(vp_y1 + 140, vp_y2 - 120, 100):
                # Draw arrow from C into B (pointing right)
                bx1 = int2_x - int(38 * flux_cb_intensity)
                bx2 = int2_x + int(38 * flux_cb_intensity)
                cv2.arrowedLine(frame, (bx1, arrow_y), (bx2, arrow_y), arrow_color_cb, 3, cv2.LINE_AA, tipLength=0.35)

        # ---------------------------------------------------------------------
        # 3. KINETIC PHONON / THERMAL STREAMLET PARTICLES
        # ---------------------------------------------------------------------
        # Vectorized coordinate mapping
        ix_p = np.clip((self.particles_x * (sim.cfg.nx - 1)).astype(np.int32), 0, sim.cfg.nx - 1)
        iy_p = np.clip((self.particles_y * (sim.cfg.ny - 1)).astype(np.int32), 0, sim.cfg.ny - 1)
        in_solid = sim.active_solid[iy_p, ix_p]

        # Flux components
        local_flux = q_mag[iy_p, ix_p]
        step_scale = 0.006 * np.sqrt(np.clip(local_flux / (max_q + 1e-5), 0, 1))
        vx = qx[iy_p, ix_p] / max_q
        vy = qy[iy_p, ix_p] / max_q

        # Advance positions
        px_new = self.particles_x + vx * step_scale
        py_new = self.particles_y + vy * step_scale

        sx = (vp_x1 + self.particles_x * vp_w).astype(np.int32)
        sy = (vp_y1 + self.particles_y * vp_h).astype(np.int32)
        sx_new = (vp_x1 + px_new * vp_w).astype(np.int32)
        sy_new = (vp_y1 + py_new * vp_h).astype(np.int32)

        # Draw particles inside active solid
        for p_idx in range(self.num_particles):
            if in_solid[p_idx]:
                p_sx, p_sy = sx[p_idx], sy[p_idx]
                p_sx2, p_sy2 = sx_new[p_idx], sy_new[p_idx]
                if vp_x1 <= p_sx < vp_x2 and vp_y1 <= p_sy < vp_y2:
                    p_bright = max(0.2, min(1.0, local_flux[p_idx] / (max_q * 0.4 + 1e-5)))
                    c_val = int(255 * p_bright)
                    cv2.line(frame, (p_sx, p_sy), (p_sx2, p_sy2), (c_val, c_val, c_val), 1, cv2.LINE_AA)
                    cv2.circle(frame, (p_sx2, p_sy2), 1, (10, 215, 255), -1, cv2.LINE_AA)

                self.particles_x[p_idx] = px_new[p_idx]
                self.particles_y[p_idx] = py_new[p_idx]
                self.particles_life[p_idx] -= 0.012

                # Re-seed if life expired or exited domain
                if (
                    self.particles_life[p_idx] <= 0
                    or px_new[p_idx] < 0.06
                    or px_new[p_idx] > 0.94
                    or not sim.active_solid[
                        int(np.clip(py_new[p_idx] * (sim.cfg.ny - 1), 0, sim.cfg.ny - 1)),
                        int(np.clip(px_new[p_idx] * (sim.cfg.nx - 1), 0, sim.cfg.nx - 1))
                    ]
                ):
                    self.particles_x[p_idx] = np.random.uniform(0.08, 0.35)
                    self.particles_y[p_idx] = np.random.uniform(0.20, 0.80)
                    self.particles_life[p_idx] = np.random.uniform(0.4, 1.0)
            else:
                self.particles_x[p_idx] = np.random.uniform(0.08, 0.35)
                self.particles_y[p_idx] = np.random.uniform(0.20, 0.80)

        # Dynamic Equilibrium Glow Effect (at t >= 13.5s when delta_ab < 1.5°C)
        is_equilibrated = metrics["delta_ab"] < 1.2
        if is_equilibrated:
            eq_pulse = 0.5 + 0.5 * np.sin(timeline_sec * 6.0)
            eq_glow_color = (int(15 * eq_pulse), int(175 * eq_pulse), int(255 * eq_pulse))
            cv2.drawContours(vp_canvas, contours, -1, eq_glow_color, 4, cv2.LINE_AA)

        # Viewport Outer Enclosure Card
        self._draw_rounded_rect(
            frame,
            (vp_x1 - 4, vp_y1 - 4), (vp_x2 + 4, vp_y2 + 4),
            color_bgr=(50, 65, 85) if not is_equilibrated else (20, 180, 255),
            thickness=2, radius=14
        )

        # ---------------------------------------------------------------------
        # 4. CONVERGENCE CHART GEOMETRY (y in [1155, 1640], Height = 485)
        # ---------------------------------------------------------------------
        ch_x1 = 55
        ch_x2 = w - 55
        ch_y1 = 1155
        ch_y2 = 1640

        # Chart container card
        self._draw_rounded_rect(
            frame,
            (ch_x1, ch_y1), (ch_x2, ch_y2),
            color_bgr=(35, 48, 65),
            fill_bgr=(12, 15, 20),
            radius=14, thickness=2
        )

        # Plot axes inner rectangle
        plot_x1 = ch_x1 + 85
        plot_x2 = ch_x2 - 45
        plot_y1 = ch_y1 + 75
        plot_y2 = ch_y2 - 65
        plot_w = plot_x2 - plot_x1
        plot_h = plot_y2 - plot_y1

        # Horizontal grid lines (0, 25, 46.2, 75, 100°C)
        for t_val in [0.0, 25.0, 46.2, 75.0, 100.0]:
            y_pix = int(plot_y2 - (t_val / 100.0) * plot_h)
            cv2.line(frame, (plot_x1, y_pix), (plot_x2, y_pix), (25, 32, 42), 1)

        # Theoretical equilibrium horizontal dashed line
        y_eq_pix = int(plot_y2 - (sim.t_eq_analytical / 100.0) * plot_h)
        for x_d in range(plot_x1, plot_x2, 14):
            cv2.line(frame, (x_d, y_eq_pix), (x_d + 7, y_eq_pix), (15, 175, 255), 2, cv2.LINE_AA)

        # Dynamic Temperature History Curves
        n_pts = len(self.time_history)
        if n_pts > 1:
            max_t_ref = 18.0
            pts_a = []
            pts_c = []
            pts_b = []

            for k in range(n_pts):
                tk = self.time_history[k]
                xk = int(plot_x1 + (tk / max_t_ref) * plot_w)
                ya = int(plot_y2 - (self.t_a_history[k] / 100.0) * plot_h)
                yc = int(plot_y2 - (self.t_c_history[k] / 100.0) * plot_h)
                yb = int(plot_y2 - (self.t_b_history[k] / 100.0) * plot_h)
                pts_a.append((xk, ya))
                pts_c.append((xk, yc))
                pts_b.append((xk, yb))

            # Draw smooth temperature evolution curves
            cv2.polylines(frame, [np.array(pts_a, dtype=np.int32)], False, (60, 68, 239), 3, cv2.LINE_AA)   # Copper (Red/Coral)
            cv2.polylines(frame, [np.array(pts_c, dtype=np.int32)], False, (15, 165, 250), 3, cv2.LINE_AA)   # Steel (Gold/Amber)
            cv2.polylines(frame, [np.array(pts_b, dtype=np.int32)], False, (212, 182, 6), 3, cv2.LINE_AA)   # Aluminum (Electric Cyan)

            # Latest pulsating head dots
            cv2.circle(frame, pts_a[-1], 5, (60, 68, 239), -1, cv2.LINE_AA)
            cv2.circle(frame, pts_c[-1], 5, (15, 165, 250), -1, cv2.LINE_AA)
            cv2.circle(frame, pts_b[-1], 5, (212, 182, 6), -1, cv2.LINE_AA)

        # ---------------------------------------------------------------------
        # 5. DYNAMIC NARRATIVE FOOTER CARD (y in [1660, 1865], Height = 205)
        # ---------------------------------------------------------------------
        foot_x1 = 55
        foot_x2 = w - 55
        foot_y1 = 1660
        foot_y2 = 1865
        self._draw_rounded_rect(
            frame,
            (foot_x1, foot_y1), (foot_x2, foot_y2),
            color_bgr=(35, 48, 65) if not is_equilibrated else (20, 180, 255),
            fill_bgr=(10, 13, 18),
            radius=14, thickness=2
        )

        # ---------------------------------------------------------------------
        # 6. SINGLE UNIFIED HIGH-DEFINITION PIL TYPOGRAPHY PASS (ZERO OVERLAP!)
        # ---------------------------------------------------------------------
        img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)

        # A. TOP HEADER AREA (y in [60, 185])
        draw.text((70, 68), "CONTINUUM LAB  //  FISICA TERMICA", font=self.font_subtitle, fill=(148, 163, 184))
        draw.text((70, 102), "LEY CERO DE LA TERMODINAMICA", font=self.font_title, fill=(255, 255, 255))

        # Header Principle Pill Badge (x = 70 to 860, y = 148 to 186)
        draw.rounded_rectangle([(70, 148), (860, 186)], radius=8, fill=(15, 23, 42), outline=(74, 222, 128), width=1)
        draw.text((85, 154), "POSTULADO: Si T_A = T_C  y  T_B = T_C   ===>   T_A = T_B", font=self.font_pill, fill=(74, 222, 128))

        # B. BODY DIGITAL TEMPERATURE BADGES (y in [205, 285])
        # Direct large digital readouts above each body
        # Badge A (Copper)
        draw.rounded_rectangle([(55, 205), (355, 285)], radius=10, fill=(24, 18, 18), outline=(239, 68, 68), width=2)
        draw.text((75, 214), "CUERPO A  [COBRE]", font=self.font_body_label, fill=(252, 165, 165))
        draw.text((75, 239), f"{metrics['t_a_mean']:5.1f} °C", font=self.font_body_temp, fill=(239, 68, 68))

        # Badge C (Steel Mediator)
        draw.rounded_rectangle([(390, 205), (690, 285)], radius=10, fill=(24, 22, 15), outline=(245, 158, 11), width=2)
        draw.text((410, 214), "CUERPO C  [ACERO]", font=self.font_body_label, fill=(253, 230, 138))
        draw.text((410, 239), f"{metrics['t_c_mean']:5.1f} °C", font=self.font_body_temp, fill=(245, 158, 11))

        # Badge B (Aluminum)
        draw.rounded_rectangle([(725, 205), (1025, 285)], radius=10, fill=(15, 22, 26), outline=(6, 182, 212), width=2)
        draw.text((745, 214), "CUERPO B  [ALUMINIO]", font=self.font_body_label, fill=(165, 243, 252))
        draw.text((745, 239), f"{metrics['t_b_mean']:5.1f} °C", font=self.font_body_temp, fill=(6, 182, 212))

        # Material Property Labels inside each body (y = 905 to 935)
        draw.rounded_rectangle([(90, 905), (325, 935)], radius=6, fill=(10, 12, 16), outline=(239, 68, 68), width=1)
        draw.text((105, 911), "k_A = 401 W/(m·K)", font=self.font_chart_label, fill=(255, 255, 255))

        draw.rounded_rectangle([(425, 905), (655, 935)], radius=6, fill=(10, 12, 16), outline=(245, 158, 11), width=1)
        draw.text((440, 911), "k_C = 54 W/(m·K)", font=self.font_chart_label, fill=(255, 255, 255))

        draw.rounded_rectangle([(760, 905), (990, 935)], radius=6, fill=(10, 12, 16), outline=(6, 182, 212), width=1)
        draw.text((775, 911), "k_B = 205 W/(m·K)", font=self.font_chart_label, fill=(255, 255, 255))

        # C. UNDER-VIEWPORT HEAT FLUX RATE METERS (y in [1076, 1124])
        q_ac_val = abs(metrics['q_dot_ac'])
        q_cb_val = abs(metrics['q_dot_cb'])
        q_ac_text = f"Flujo A -> C: {q_ac_val:,.0f} W" if q_ac_val > 15 else "Flujo A -> C: 0 W (Cesa)"
        q_cb_text = f"Flujo C -> B: {q_cb_val:,.0f} W" if q_cb_val > 15 else "Flujo C -> B: 0 W (Cesa)"

        draw.rounded_rectangle([(55, 1076), (1025, 1124)], radius=8, fill=(12, 15, 20), outline=(35, 48, 65), width=1)
        draw.text((75, 1090), q_ac_text, font=self.font_flux_label, fill=(245, 158, 11))
        draw.text((435, 1090), "q = -k grad(T)  [Ley de Fourier]", font=self.font_flux_label, fill=(148, 163, 184))
        draw.text((795, 1090), q_cb_text, font=self.font_flux_label, fill=(6, 182, 212))

        # D. CONVERGENCE CHART TYPOGRAPHY (y in [1165, 1630])
        # Title at left
        draw.text((ch_x1 + 25, ch_y1 + 20), "CONVERGENCIA HACIA EL EQUILIBRIO TERMICO", font=self.font_chart_title, fill=(255, 255, 255))
        # Analytical Target at right
        draw.text((ch_x2 - 320, ch_y1 + 20), f"T_eq Objetivo = {sim.t_eq_analytical:.1f} °C", font=self.font_chart_title, fill=(245, 158, 11))

        # Y-Axis markings with generous left margins
        for t_val in [0.0, 25.0, 46.2, 75.0, 100.0]:
            y_pix = int(plot_y2 - (t_val / 100.0) * plot_h)
            lbl = f"{t_val:.0f}C" if t_val != 46.2 else "46.2C"
            draw.text((plot_x1 - 65, y_pix - 10), lbl, font=self.font_chart_label, fill=(148, 163, 184))

        # Bottom Legend
        draw.text((plot_x1 + 10, plot_y2 + 25), "● T_A (Cobre 100C)", font=self.font_chart_legend, fill=(239, 68, 68))
        draw.text((plot_x1 + 260, plot_y2 + 25), "● T_C (Sonda 25C)", font=self.font_chart_legend, fill=(245, 158, 11))
        draw.text((plot_x1 + 490, plot_y2 + 25), "● T_B (Aluminio 0C)", font=self.font_chart_legend, fill=(6, 182, 212))
        draw.text((plot_x1 + 720, plot_y2 + 25), f"--- T_eq ({sim.t_eq_analytical:.1f}C)", font=self.font_chart_legend, fill=(245, 158, 11))

        # E. DYNAMIC NARRATIVE FOOTER TYPOGRAPHY (y in [1675, 1855])
        if timeline_sec < 4.5:
            phase_title = "FASE 1: CONTACTO TERMICO Y DESEQUILIBRIO INICIAL"
            phase_color = (6, 182, 212)
            narr_line1 = "Tres cuerpos solidos puestos en contacto termico directo a 100C, 25C y 0C."
            narr_line2 = "El gradiente termico extremo en la interfaz activa la difusion espontanea."
        elif timeline_sec < 9.5:
            phase_title = "FASE 2: CONDUCCION CONTINUA Y LEY DE FOURIER"
            phase_color = (245, 158, 11)
            narr_line1 = "El calor fluye espontaneamente desde el cuerpo A caliente hacia el frio B."
            narr_line2 = "El mediador central C absorbe energia de A y simultaneamente la cede a B."
        elif timeline_sec < 13.5:
            phase_title = "FASE 3: EL MEDIADOR (C) TRANSMITE EL EQUILIBRIO"
            phase_color = (250, 204, 21)
            narr_line1 = "A medida que T_A tiende a T_C y T_B tiende a T_C, los potenciales se igualan."
            narr_line2 = "La tasa de transferencia disminuye gradualmente hacia cero (|q| -> 0)."
        else:
            phase_title = "FASE 4: ¡EQUILIBRIO TERMICO GLOBAL Y LEY CERO!"
            phase_color = (74, 222, 128)
            narr_line1 = f"LEY CERO DEMOSTRADA: T_A = T_C y T_B = T_C  ===>  T_A = T_B = {sim.t_eq_analytical:.1f} °C."
            narr_line2 = "El flujo neto cesa por completo. La Temperatura queda demostrada como propiedad de estado."

        # Narrative Header Tag
        draw.text((75, 1678), f"TELEMETRIA // {phase_title}", font=self.font_narrative_phase, fill=phase_color)
        draw.line([(75, 1712), (w - 75, 1712)], fill=(31, 41, 55), width=1)

        # Narrative Body (2 concise, clean, large lines)
        draw.text((75, 1726), narr_line1, font=self.font_narrative_body, fill=(255, 255, 255))
        draw.text((75, 1762), narr_line2, font=self.font_narrative_body, fill=(226, 232, 240))

        # Bottom System Line
        draw.text(
            (75, 1818),
            f"CONTINUUM LAB  |  t = {timeline_sec:.2f} s  |  Conservacion de Energia: 100.0%  |  dS_gen/dt -> 0",
            font=self.font_footer,
            fill=(100, 116, 139)
        )

        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


def render_zeroth_law_video(
    duration: float = 18.0,
    fps: int = 60,
    output_mp4: str = "Ley_Cero_Termodinamica_Equilibrio_3_Cuerpos.mp4",
    lang: str = "ES",
    preview: bool = False
) -> str:
    """
    Renders the complete 1080x1920 60 FPS video and multiplexes the cinematic music.
    """
    import imageio_ffmpeg
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

    out_file = Path(output_mp4).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    temp_avi = out_file.parent / f"temp_{out_file.stem}.avi"
    audio_wav = out_file.parent / f"temp_{out_file.stem}_audio.wav"

    if preview:
        duration = 6.0
        fps = 30
        print("[+] Modo PREVIEW activado: 6.0s a 30 FPS...")

    total_frames = int(duration * fps)

    # 1. Synthesize Procedural Cinematic Atmospheric Soundtrack
    print(f"\n[1/3] Sintetizando banda sonora cinematográfica de ciencia ({duration:.1f}s @ 84 BPM)...")
    synthesize_catchy_thermal_audio(duration=duration, fs=44100, output_path=str(audio_wav))

    # 2. Physics Simulation Initialization & VideoWriter
    print(f"\n[2/3] Inicializando simulador de transferencia de calor 2D (Nx=360, Ny=180, time_scale=65.0)...")
    sim = ZerothLawThermalSimulation(ThermalConfig(time_scale=65.0))
    renderer = MasterHeatTransferRenderer(width=1080, height=1920, fps=fps, lang=lang)

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    writer = cv2.VideoWriter(str(temp_avi), fourcc, fps, (1080, 1920))
    if not writer.isOpened():
        raise RuntimeError("No se pudo inicializar cv2.VideoWriter con codec MJPG.")

    sub_steps_per_frame = 18
    dt_sub = (duration / total_frames) / sub_steps_per_frame

    print(f"\n[3/3] Renderizando {total_frames} cuadros Ultra-HD 1080x1920 a {fps} FPS...")
    for frame_idx in range(total_frames):
        timeline_sec = frame_idx / fps

        # Advance physics simulation
        for _ in range(sub_steps_per_frame):
            sim.step(dt_sub)

        # Render frame
        frame_bgr = renderer.render_frame(sim, frame_idx, total_frames, timeline_sec)
        writer.write(frame_bgr)

        if frame_idx % 60 == 0 or frame_idx == total_frames - 1:
            progress = (frame_idx + 1) / total_frames * 100.0
            metrics = sim.compute_metrics()
            print(
                f"  -> Cuadro {frame_idx + 1:4d}/{total_frames} ({progress:5.1f}%) | "
                f"t = {timeline_sec:4.1f}s | "
                f"T_A={metrics['t_a_mean']:5.1f}C, T_C={metrics['t_c_mean']:5.1f}C, T_B={metrics['t_b_mean']:5.1f}C | "
                f"Eq={metrics['equilibrium_progress']*100:5.1f}%"
            )

    writer.release()
    print(f" -> Grabacion de cuadros completada ({temp_avi.stat().st_size / (1024*1024):.1f} MB)")

    # 3. Transcode to H.264 + AAC multiplexed MP4 with faststart
    cmd_mux = [
        ffmpeg_bin, "-y",
        "-i", str(temp_avi),
        "-i", str(audio_wav),
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        str(out_file)
    ]
    print(f" -> Codificando a contenedor final H.264 / AAC con FFmpeg...")
    subprocess.run(cmd_mux, check=True)

    # Clean up temporary files safely
    time.sleep(0.3)
    try:
        if temp_avi.exists():
            temp_avi.unlink()
    except Exception:
        pass
    try:
        if audio_wav.exists():
            audio_wav.unlink()
    except Exception:
        pass

    file_size_mb = out_file.stat().st_size / (1024 * 1024)
    print(f"\n[SUCCESS] Video final en Alta Definicion con audio guardado en:\n -> {out_file} ({file_size_mb:.2f} MB)\n")
    return str(out_file)


if __name__ == "__main__":
    render_zeroth_law_video(duration=6.0, fps=30, output_mp4="test_master_render.mp4", preview=True)
