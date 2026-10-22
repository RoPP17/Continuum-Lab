"""
Continuum Lab - Master 9:16 Visual Renderer for Magnus Effect & Flettner Rotor
Module: 01 Mecanica de Fluidos / 05 Efecto Magnus y Rotor Flettner
File: src/visualization/render_magnus.py

Renders 1080x1920 (9:16 Vertical UHD @ 60 FPS) scientific animations:
  - Deep Cosmic Void & Aerodynamic Fluid Palette (#080B12, #00F0FF, #FF007F, #FFB703, #00FF88)
  - 2,400 velocity-coded particle tracers with speed-gradient trails
  - Rotating Flettner Rotor cylinder with dynamic radial spokes and boundary layer slip
  - Real-time stagnation point tracking (Dual surface points -> Critical merge -> Detached saddle point)
  - Upward aerodynamic lift vector L' and drag vector D' (Kutta-Joukowski theorem)
  - Live dynamic surface pressure distribution C_p(theta) polar/Cartesian oscilloscope
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
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Add project root to sys.path
current_dir = Path(__file__).resolve().parent
module_dir = current_dir.parent.parent
project_dir = module_dir.parent.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.physics.magnus_sim import (
    MagnusConfig,
    MagnusSimulation,
    MagnusTelemetry,
)


class MasterMagnusRenderer:
    """
    Master 9:16 60 FPS Visual Renderer & Cybernetic HUD for the Magnus Effect & Flettner Rotor.
    """

    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 60, lang: str = "ES"):
        self.width = width
        self.height = height
        self.fps = fps
        self.lang = lang.upper()

        self._load_fonts()

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
        self.sim_cx = (self.sim_x1 + self.sim_x2) // 2
        self.sim_cy = (self.sim_y1 + self.sim_y2) // 2 + 10

        # Physical scaling: 120 pixels per meter (R = 1.0 m -> 120 px)
        self.scale = 120.0

        # 4. Live Surface Pressure Cp(theta) Oscilloscope Panel
        self.panel_x1, self.panel_y1 = 50, 1395
        self.panel_x2, self.panel_y2 = 1030, 1600

        # 5. Bottom Callout Card
        self.cta_x1, self.cta_y1 = 50, 1615
        self.cta_x2, self.cta_y2 = 1030, 1745

        # Cylinder rotation phase accumulator
        self.rot_angle = 0.0

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
            self.font_hdr_title = ImageFont.truetype(chosen_bold, 24)
            self.font_hdr_sub = ImageFont.truetype(chosen_reg, 17)
            self.font_badge_lbl = ImageFont.truetype(chosen_bold, 14)
            self.font_badge_val = ImageFont.truetype(chosen_bold, 21)
            self.font_viewport_tag = ImageFont.truetype(chosen_bold, 16)
            self.font_panel_title = ImageFont.truetype(chosen_bold, 16)
            self.font_panel_meta = ImageFont.truetype(chosen_reg, 14)
            self.font_cta_title = ImageFont.truetype(chosen_bold, 18)
            self.font_cta_desc = ImageFont.truetype(chosen_reg, 15)
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

    def draw_card(self, img: np.ndarray, x1: int, y1: int, x2: int, y2: int,
                  bg_bgr=(18, 14, 10), border_bgr=(60, 75, 95)):
        overlay = img.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), bg_bgr, -1)
        cv2.addWeighted(overlay, 0.88, img, 0.12, 0, img)
        cv2.rectangle(img, (x1, y1), (x2, y2), border_bgr, 1, lineType=cv2.LINE_AA)

    def phys_to_screen(self, x: float, y: float) -> Tuple[int, int]:
        """Converts physical meters to viewport pixel coordinates."""
        px = int(self.sim_cx + x * self.scale)
        py = int(self.sim_cy - y * self.scale)  # Y inverted in image coords
        return px, py

    def render_frame(self, sim: MagnusSimulation, telem: MagnusTelemetry) -> np.ndarray:
        # Base Canvas (Deep space / aerodynamic dark canvas: #080B12 -> BGR: 18, 11, 8)
        img = np.full((self.height, self.width, 3), (18, 11, 8), dtype=np.uint8)

        # 1. Subtle background grid in fluid viewport
        cx, cy = self.sim_cx, self.sim_cy
        x1, y1, x2, y2 = self.sim_x1, self.sim_y1, self.sim_x2, self.sim_y2

        grid_spacing = int(self.scale)  # 1 meter grid
        for gx in range(cx % grid_spacing, self.width, grid_spacing):
            if x1 <= gx <= x2:
                cv2.line(img, (gx, y1), (gx, y2), (28, 22, 16), 1)
        for gy in range(cy % grid_spacing, self.height, grid_spacing):
            if y1 <= gy <= y2:
                cv2.line(img, (x1, gy), (x2, gy), (28, 22, 16), 1)

        # 2. Draw Suction & Overpressure Pressure Glow (Bernoulli Field)
        # Compute dynamic radius and intensity of suction zone on top
        R_px = int(sim.cfg.radius * self.scale)
        alpha = telem.spin_ratio_alpha

        if alpha > 0.05:
            # Low-pressure suction halo on top (Cyan #00F0FF -> BGR: 255, 240, 0)
            suction_cy = cy - int(R_px * 0.85)
            suction_rad = int(R_px * (1.2 + 0.3 * min(3.0, alpha)))
            overlay_s = img.copy()
            cv2.circle(overlay_s, (cx, suction_cy), suction_rad, (240, 200, 0), -1)
            cv2.GaussianBlur(overlay_s, (99, 99), 0, dst=overlay_s)
            alpha_suction = min(0.35, 0.08 + 0.07 * alpha)
            cv2.addWeighted(overlay_s, alpha_suction, img, 1.0 - alpha_suction, 0, img)

            # High-pressure stagnation halo on bottom (Hot Amber/Crimson -> BGR: 20, 80, 255)
            stag_cy = cy + int(R_px * 0.95)
            stag_rad = int(R_px * (0.9 + 0.2 * min(2.5, alpha)))
            overlay_p = img.copy()
            cv2.circle(overlay_p, (cx, stag_cy), stag_rad, (20, 80, 255), -1)
            cv2.GaussianBlur(overlay_p, (85, 85), 0, dst=overlay_p)
            alpha_stag = min(0.28, 0.06 + 0.06 * alpha)
            cv2.addWeighted(overlay_p, alpha_stag, img, 1.0 - alpha_stag, 0, img)

        # 3. Draw 2,400 Velocity-Coded Particle Tracers
        pxs = (cx + sim.particles_x * self.scale).astype(np.int32)
        pys = (cy - sim.particles_y * self.scale).astype(np.int32)
        ux, uy = sim.velocity_field(sim.particles_x, sim.particles_y, alpha)
        speeds = np.sqrt(ux**2 + uy**2)
        u_norm = speeds / sim.cfg.u_inf  # Relative to U_inf

        # Clip particles strictly within viewport
        valid_mask = (pxs >= x1 + 2) & (pxs <= x2 - 2) & (pys >= y1 + 2) & (pys <= y2 - 2)
        valid_indices = np.where(valid_mask)[0]

        # Draw particle trails and heads
        trail_scale = 0.016 * self.scale
        for idx in valid_indices:
            px, py = pxs[idx], pys[idx]
            un = u_norm[idx]

            # Color mapping by velocity:
            # Slow (< 0.8): Deep blue / cyan
            # Medium (0.8 - 1.4): Pure Electric Cyan
            # Fast (1.4 - 2.2): Emerald to Gold
            # Extreme (> 2.2): Hot Neon Magenta
            if un < 0.75:
                color = (210, 110, 40)      # BGR Deep Steel Blue
                rad = 1
            elif un < 1.35:
                color = (255, 235, 20)      # Electric Cyan
                rad = 2
            elif un < 2.10:
                color = (40, 215, 255)      # Bright Gold/Yellow
                rad = 2
            else:
                color = (130, 20, 255)      # Hot Neon Magenta
                rad = 3

            # Draw streak vector backwards
            tail_x = int(px - ux[idx] * trail_scale)
            tail_y = int(py + uy[idx] * trail_scale)
            if x1 <= tail_x <= x2 and y1 <= tail_y <= y2:
                cv2.line(img, (tail_x, tail_y), (px, py), color, 1, lineType=cv2.LINE_AA)
            cv2.circle(img, (px, py), rad, color, -1, lineType=cv2.LINE_AA)

        # 4. Draw Rotating Cylinder (Flettner Rotor)
        # Update rotation angle based on omega
        omega = alpha * sim.cfg.u_inf / sim.cfg.radius
        self.rot_angle += (omega / self.fps)

        # Cylinder Body Shadow / Depth
        cv2.circle(img, (cx, cy), R_px + 3, (40, 50, 65), 2, lineType=cv2.LINE_AA)
        cv2.circle(img, (cx, cy), R_px, (32, 26, 20), -1, lineType=cv2.LINE_AA)

        # Rotating mechanical spokes (4 spokes)
        for i in range(4):
            spoke_ang = self.rot_angle + i * (np.pi / 2.0)
            sx = int(cx + (R_px - 8) * np.cos(spoke_ang))
            sy = int(cy + (R_px - 8) * np.sin(spoke_ang))
            cv2.line(img, (cx, cy), (sx, sy), (70, 85, 110), 2, lineType=cv2.LINE_AA)

        # Central mechanical hub
        cv2.circle(img, (cx, cy), int(R_px * 0.28), (48, 40, 32), -1, lineType=cv2.LINE_AA)
        cv2.circle(img, (cx, cy), int(R_px * 0.28), (0, 240, 255), 2, lineType=cv2.LINE_AA)
        cv2.circle(img, (cx, cy), 4, (255, 255, 255), -1, lineType=cv2.LINE_AA)

        # Cylinder outer metallic rim with cyan glow
        cv2.circle(img, (cx, cy), R_px, (0, 240, 255), 3, lineType=cv2.LINE_AA)

        # Clockwise rotation indicator arrow on top/side of cylinder
        if alpha > 0.1:
            arrow_r = int(R_px * 0.62)
            cv2.ellipse(img, (cx, cy), (arrow_r, arrow_r), 0, -40, 160, (0, 215, 255), 2, lineType=cv2.LINE_AA)
            tip_x = int(cx + arrow_r * np.cos(np.radians(160)))
            tip_y = int(cy + arrow_r * np.sin(np.radians(160)))
            cv2.circle(img, (tip_x, tip_y), 4, (0, 215, 255), -1, lineType=cv2.LINE_AA)

        # 5. Draw Stagnation Points & Bifurcation Visuals
        stag_pts = telem.stag_points
        if telem.stagnation_state == "SURFACE_DUAL":
            for idx_s, pt in enumerate(stag_pts):
                spx, spy = self.phys_to_screen(pt[0], pt[1])
                # Pulsing crosshairs
                pulse = int(5 * np.sin(time.time() * 6.0))
                cv2.circle(img, (spx, spy), 8 + abs(pulse), (0, 70, 255), 2, lineType=cv2.LINE_AA)
                cv2.circle(img, (spx, spy), 3, (0, 255, 255), -1, lineType=cv2.LINE_AA)
                cv2.line(img, (spx - 14, spy), (spx + 14, spy), (0, 70, 255), 1, lineType=cv2.LINE_AA)
                cv2.line(img, (spx, spy - 14), (spx, spy + 14), (0, 70, 255), 1, lineType=cv2.LINE_AA)
                label_s = f"S{idx_s+1}"
                cv2.putText(img, label_s, (spx + 10, spy + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)

        elif telem.stagnation_state == "CRITICAL_MERGE":
            spx, spy = self.phys_to_screen(stag_pts[0][0], stag_pts[0][1])
            cv2.circle(img, (spx, spy), 14, (0, 0, 255), 3, lineType=cv2.LINE_AA)
            cv2.circle(img, (spx, spy), 5, (255, 255, 255), -1, lineType=cv2.LINE_AA)
            cv2.line(img, (spx - 22, spy), (spx + 22, spy), (0, 0, 255), 2, lineType=cv2.LINE_AA)
            cv2.line(img, (spx, spy - 22), (spx, spy + 22), (0, 0, 255), 2, lineType=cv2.LINE_AA)
            tag_text = "BIFURCACION CRITICA alpha=2.0" if self.lang == "ES" else "CRITICAL BIFURCATION alpha=2.0"
            cv2.putText(img, tag_text, (spx - 110, spy + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 160, 255), 1, cv2.LINE_AA)

        elif telem.stagnation_state == "DETACHED_SADDLE":
            spx, spy = self.phys_to_screen(stag_pts[0][0], stag_pts[0][1])
            # Draw detached saddle point crosshair
            cv2.circle(img, (spx, spy), 12, (255, 0, 180), 2, lineType=cv2.LINE_AA)
            cv2.circle(img, (spx, spy), 4, (255, 255, 255), -1, lineType=cv2.LINE_AA)
            cv2.line(img, (spx - 18, spy), (spx + 18, spy), (255, 0, 180), 2, lineType=cv2.LINE_AA)
            cv2.line(img, (spx, spy - 18), (spx, spy + 18), (255, 0, 180), 2, lineType=cv2.LINE_AA)
            # Trapped circulating boundary circle
            r_s_px = int(np.sqrt((spx - cx)**2 + (spy - cy)**2))
            cv2.circle(img, (cx, cy), r_s_px, (255, 0, 180), 1, lineType=cv2.LINE_AA)
            tag_text = "SILLA DESPRENDIDA (VORTEX CLOAK)" if self.lang == "ES" else "DETACHED SADDLE (VORTEX CLOAK)"
            cv2.putText(img, tag_text, (spx - 120, spy + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (255, 0, 220), 1, cv2.LINE_AA)

        # 6. Draw Aerodynamic Vector Arrows (Lift L' and Drag D')
        if telem.lift_real_kn_m > 0.05:
            # Lift vector arrow (straight UP from center)
            lift_len_px = int(min(320, telem.lift_real_kn_m * 65.0))
            arrow_tip_y = cy - lift_len_px
            cv2.arrowedLine(img, (cx, cy), (cx, arrow_tip_y), (0, 240, 255), 5, tipLength=0.15, line_type=cv2.LINE_AA)
            # Lift label
            lbl_l = f"L' = {telem.lift_real_kn_m:.1f} kN/m"
            cv2.putText(img, lbl_l, (cx + 15, arrow_tip_y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (0, 240, 255), 2, cv2.LINE_AA)

            # Drag vector arrow (pointing right)
            drag_len_px = int(min(140, telem.c_d_real * 35.0))
            arrow_drag_x = cx + drag_len_px
            cv2.arrowedLine(img, (cx, cy), (arrow_drag_x, cy), (20, 80, 255), 3, tipLength=0.25, line_type=cv2.LINE_AA)
            lbl_d = f"D' = {telem.c_d_real:.2f}"
            cv2.putText(img, lbl_d, (arrow_drag_x + 8, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (20, 80, 255), 1, cv2.LINE_AA)

        # Free stream wind arrow indicator (top left of viewport)
        cv2.arrowedLine(img, (x1 + 30, y1 + 50), (x1 + 110, y1 + 50), (255, 255, 255), 2, tipLength=0.25, line_type=cv2.LINE_AA)
        cv2.putText(img, f"U_inf = {sim.cfg.u_inf:.0f} m/s", (x1 + 30, y1 + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        # Viewport Cybernetic Boundary
        cv2.rectangle(img, (x1, y1), (x2, y2), (70, 85, 110), 1, lineType=cv2.LINE_AA)

        # Viewport corner brackets
        bracket_len = 16
        for bx, by, dx, dy in [(x1, y1, 1, 1), (x2, y1, -1, 1), (x1, y2, 1, -1), (x2, y2, -1, -1)]:
            cv2.line(img, (bx, by), (bx + dx * bracket_len, by), (0, 240, 255), 2)
            cv2.line(img, (bx, by), (bx, by + dy * bracket_len), (0, 240, 255), 2)

        # 7. Draw HUD Cards (Header, Badges, Oscilloscope, CTA)
        self.draw_card(img, self.hdr_x1, self.hdr_y1, self.hdr_x2, self.hdr_y2, bg_bgr=(14, 11, 8), border_bgr=(50, 65, 85))
        self.draw_card(img, self.b1_x1, self.badge_y1, self.b1_x2, self.badge_y2, bg_bgr=(16, 12, 9), border_bgr=(45, 60, 80))
        self.draw_card(img, self.b2_x1, self.badge_y1, self.b2_x2, self.badge_y2, bg_bgr=(16, 12, 9), border_bgr=(45, 60, 80))
        self.draw_card(img, self.b3_x1, self.badge_y1, self.b3_x2, self.badge_y2, bg_bgr=(16, 12, 9), border_bgr=(45, 60, 80))
        self.draw_card(img, self.panel_x1, self.panel_y1, self.panel_x2, self.panel_y2, bg_bgr=(14, 11, 8), border_bgr=(50, 65, 85))
        self.draw_card(img, self.cta_x1, self.cta_y1, self.cta_x2, self.cta_y2, bg_bgr=(16, 12, 9), border_bgr=(50, 65, 85))

        # 8. Render Live Surface Pressure Cp(theta) Curve in Panel
        px1, py1, px2, py2 = self.panel_x1, self.panel_y1, self.panel_x2, self.panel_y2
        graph_x1 = px1 + 80
        graph_x2 = px2 - 40
        graph_y_mid = py1 + 115
        graph_h = 75

        # Horizontal zero axis line (Cp = 0)
        cv2.line(img, (graph_x1, graph_y_mid), (graph_x2, graph_y_mid), (60, 75, 95), 1)
        cv2.putText(img, "Cp=0", (px1 + 25, graph_y_mid + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (140, 160, 185), 1, cv2.LINE_AA)
        cv2.putText(img, "Suction", (px1 + 15, graph_y_mid - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 240, 255), 1, cv2.LINE_AA)
        cv2.putText(img, "Pressure", (px1 + 12, graph_y_mid + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (20, 80, 255), 1, cv2.LINE_AA)

        # Plot Cp(theta) curve from theta = 0 to 360 deg
        n_pts = 180
        thetas = np.linspace(0.0, 2.0 * np.pi, n_pts)
        cp_vals = sim.surface_pressure_cp(thetas, alpha)
        # Normalize Cp: Cp = +1 (stagnation) -> graph_y_mid + 20, Cp = -12 (deep suction) -> py1 + 45
        min_cp_display = -12.0
        max_cp_display = 1.5

        pts_curve = []
        for i, th in enumerate(thetas):
            gx = int(graph_x1 + (i / (n_pts - 1)) * (graph_x2 - graph_x1))
            val = cp_vals[i]
            norm_val = np.clip((val - min_cp_display) / (max_cp_display - min_cp_display), 0.0, 1.0)
            gy = int((py1 + 45) + (1.0 - norm_val) * (py2 - py1 - 65))
            pts_curve.append((gx, gy))

        for i in range(len(pts_curve) - 1):
            cv2.line(img, pts_curve[i], pts_curve[i + 1], (0, 240, 255), 2, lineType=cv2.LINE_AA)

        # 9. Draw Crisp PIL Typography
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)

        # Header Text
        if self.lang == "ES":
            hdr_sub = "CONTINUUM LAB // MECÁNICA DE FLUIDOS Y AERODINÁMICA"
            hdr_title = "EFECTO MAGNUS Y ROTOR FLETTNER: L' = ρ∞·U∞·Γ"
            b1_lbl = "PARÁMETRO DE GIRO"
            b2_lbl = "SUSTENTACIÓN L'"
            b3_lbl = "ESTADO ESTANCAMIENTO"
            panel_title = "OSCILOSCOPIO DE PRESIÓN SUPERFICIAL CP(θ) [-12.0 a +1.0]"
            cta_title = "¿VELAS O CILINDROS GIRATORIOS EN ALTA MAR?"
            cta_desc = "Un rotor Flettner genera hasta 10 veces más sustentación que un ala de avión.\n¿Por qué no todos los buques de carga cruzan el océano con esta tecnología?"
        else:
            hdr_sub = "CONTINUUM LAB // FLUID MECHANICS & AERODYNAMICS"
            hdr_title = "MAGNUS EFFECT & FLETTNER ROTOR: L' = ρ∞·U∞·Γ"
            b1_lbl = "SPIN RATIO α"
            b2_lbl = "AERODYNAMIC LIFT L'"
            b3_lbl = "STAGNATION STATE"
            panel_title = "SURFACE PRESSURE CP(θ) OSCILLOSCOPE [-12.0 to +1.0]"
            cta_title = "CAN SPINNING TOWERS REPLACE SAILS AT SEA?"
            cta_desc = "A Flettner rotor generates up to 10x more aerodynamic lift than an aircraft wing.\nWhy doesn't every commercial cargo ship cross the oceans using this physics?"

        draw.text((self.hdr_x1 + 24, self.hdr_y1 + 16), hdr_sub, font=self.font_hdr_sub, fill=(0, 240, 255))
        draw.text((self.hdr_x1 + 24, self.hdr_y1 + 54), hdr_title, font=self.font_hdr_title, fill=(255, 255, 255))

        # Badge 1: Spin Ratio alpha & RPM
        draw.text((self.b1_x1 + 18, self.badge_y1 + 12), b1_lbl, font=self.font_badge_lbl, fill=(0, 240, 255))
        b1_val_str = f"α = {telem.spin_ratio_alpha:.2f} | {telem.omega_rpm:.0f} RPM"
        draw.text((self.b1_x1 + 18, self.badge_y1 + 40), b1_val_str, font=self.font_badge_val, fill=(255, 255, 255))

        # Badge 2: Lift L' & CL Real
        draw.text((self.b2_x1 + 18, self.badge_y1 + 12), b2_lbl, font=self.font_badge_lbl, fill=(0, 255, 136))
        b2_val_str = f"{telem.lift_real_kn_m:.1f} kN/m (CL={telem.c_l_real:.1f})"
        draw.text((self.b2_x1 + 18, self.badge_y1 + 40), b2_val_str, font=self.font_badge_val, fill=(255, 255, 255))

        # Badge 3: Stagnation State
        draw.text((self.b3_x1 + 18, self.badge_y1 + 12), b3_lbl, font=self.font_badge_lbl, fill=(255, 183, 3))
        if telem.stagnation_state == "SURFACE_DUAL":
            b3_val_str = "DUAL SURFACE"
            b3_color = (0, 240, 255)
        elif telem.stagnation_state == "CRITICAL_MERGE":
            b3_val_str = "CRITICAL α=2.0"
            b3_color = (255, 100, 100)
        else:
            b3_val_str = "DETACHED SADDLE"
            b3_color = (255, 0, 180)
        draw.text((self.b3_x1 + 18, self.badge_y1 + 40), b3_val_str, font=self.font_badge_val, fill=b3_color)

        # Oscilloscope Title & Meta
        draw.text((self.panel_x1 + 24, self.panel_y1 + 12), panel_title, font=self.font_panel_title, fill=(0, 240, 255))
        meta_str = f"Max Suction Cp = {telem.max_suction_cp:.1f} | Ship Thrust Power = {telem.thrust_power_kw:.0f} kW (4 Rotors)"
        draw.text((self.panel_x1 + 480, self.panel_y1 + 14), meta_str, font=self.font_panel_meta, fill=(200, 220, 245))

        # Bottom Callout Card Text
        draw.text((self.cta_x1 + 24, self.cta_y1 + 16), cta_title, font=self.font_cta_title, fill=(255, 215, 0))
        draw.text((self.cta_x1 + 24, self.cta_y1 + 52), cta_desc, font=self.font_cta_desc, fill=(240, 245, 255))

        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def enhance_hero_image(bgr_frame: np.ndarray, output_path: str):
    """
    Applies image-enhancer crispness & micro-contrast optimization for high-retention social covers.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    pil_img = Image.fromarray(cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB))
    sharpened = pil_img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=125, threshold=2))
    sharpened.save(output_path, format="PNG", optimize=True)


def render_magnus_video(
    output_mp4: str,
    audio_wav: Optional[str] = None,
    lang: str = "ES",
    duration: float = 18.0,
    fps: int = 60,
    hero_capture_path: Optional[str] = None
) -> str:
    """
    Renders the complete 18.0s Magnus Effect simulation @ 60 FPS and multiplexes stereo audio.
    """
    Path(output_mp4).parent.mkdir(parents=True, exist_ok=True)
    temp_video = str(Path(output_mp4).with_suffix(".temp.mp4"))

    sim = MagnusSimulation()
    renderer = MasterMagnusRenderer(width=1080, height=1920, fps=fps, lang=lang)

    total_frames = int(duration * fps)
    dt_frame = 1.0 / float(fps)

    print(f"\n[RENDER] Starting Magnus Effect Pipeline [{lang}]: {total_frames} frames @ {fps} FPS -> {output_mp4}")

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
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        temp_video
    ]
    pipe = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    hero_frame = None
    # Capture hero cover at t = 10.0s when alpha is near critical bifurcation and streamlines warp violently
    hero_frame_idx = int(10.0 * fps)

    t_start = time.time()
    for frame_idx in range(total_frames):
        target_t = frame_idx * dt_frame
        telem = sim.advance_to_time(target_t)
        frame_bgr = renderer.render_frame(sim, telem)

        pipe.stdin.write(frame_bgr.tobytes())

        if frame_idx == hero_frame_idx:
            hero_frame = frame_bgr.copy()

        if frame_idx % 180 == 0 or frame_idx == total_frames - 1:
            elapsed = time.time() - t_start
            fps_proc = (frame_idx + 1) / max(0.01, elapsed)
            eta = (total_frames - frame_idx - 1) / max(0.01, fps_proc)
            print(
                f"[{frame_idx+1:04d}/{total_frames}] t={telem.t_video:.2f}s | "
                f"alpha={telem.spin_ratio_alpha:.2f} | L'={telem.lift_real_kn_m:.1f} kN/m | "
                f"state={telem.stagnation_state} | FPS={fps_proc:.1f} | ETA={eta:.1f}s"
            )

    pipe.stdin.close()
    pipe.wait()

    if hero_capture_path and hero_frame is not None:
        enhance_hero_image(hero_frame, hero_capture_path)
        print(f"[OK] Enhanced Hero Cover saved to: {hero_capture_path}")

    if audio_wav and os.path.exists(audio_wav):
        print(f"[AUDIO] Multiplexing procedural Magnus soundtrack: {audio_wav}")
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

    size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
    print(f"[SUCCESS] Master Video rendered: {output_mp4} ({size_mb:.2f} MB)")
    return output_mp4
