"""
Continuum Lab - Master 3D Visual Renderer for Lorenz Strange Attractor & Butterfly Effect
Module: 02 Dinamica y Vibraciones / 07 Atractor de Lorenz y Efecto Mariposa 3D
File: src/visualization/render_lorenz.py

Renders 1080x1920 (9:16 Vertical UHD @ 60 FPS) scientific animations:
  - Deep Cosmic Void Palette (#080B12, #00F0FF, #FF007F, #FFB703, #00FF88)
  - 3D Perspective Camera with smooth periodic orbit around the Strange Attractor
  - 3,600-point Ghost Manifold + Pulsing Equilibrium Cores C_- and C_+
  - Twin Phosphorescent 3D Ribbons (Reference Orbit A vs Rounded Orbit B, Δ₀ = 10⁻⁴)
  - 60-Particle Golden Phase-Space Swarm stretching & folding on the fractal manifold
  - Live Lorenz (1963) Dual Waveform Oscilloscope (x_A(t) vs x_B(t))
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

from src.physics.lorenz_sim import (
    LorenzConfig,
    LorenzSimulation,
    LorenzTelemetry,
)


class MasterLorenz3DRenderer:
    """
    Master 9:16 60 FPS 3D Renderer & Cybernetic HUD for the Lorenz Strange Attractor.
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

        # 3. 3D Strange Attractor Hero Viewport (980x980 px)
        self.sim_x1, self.sim_y1 = 50, 395
        self.sim_x2, self.sim_y2 = 1030, 1375
        self.sim_cx = (self.sim_x1 + self.sim_x2) // 2
        self.sim_cy = (self.sim_y1 + self.sim_y2) // 2 + 35

        # 4. Live Lorenz 1963 Dual Waveform Oscilloscope Panel (x_A(t) vs x_B(t))
        self.panel_x1, self.panel_y1 = 50, 1395
        self.panel_x2, self.panel_y2 = 1030, 1600

        # 5. Bottom Debate / Callout Card
        self.cta_x1, self.cta_y1 = 50, 1615
        self.cta_x2, self.cta_y2 = 1030, 1745

        # Static cosmic dust stars in the 3D viewport
        rng = np.random.default_rng(1963)
        self.bg_stars: List[Tuple[int, int, int]] = []
        for _ in range(110):
            sx = int(rng.integers(self.sim_x1 + 12, self.sim_x2 - 12))
            sy = int(rng.integers(self.sim_y1 + 12, self.sim_y2 - 12))
            sb = int(rng.integers(45, 145))
            self.bg_stars.append((sx, sy, sb))

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
            self.font_hdr_title = ImageFont.truetype(chosen_bold, 25)
            self.font_hdr_sub = ImageFont.truetype(chosen_reg, 18)
            self.font_badge_lbl = ImageFont.truetype(chosen_bold, 14)
            self.font_badge_val = ImageFont.truetype(chosen_bold, 21)
            self.font_viewport_tag = ImageFont.truetype(chosen_bold, 16)
            self.font_panel_title = ImageFont.truetype(chosen_bold, 16)
            self.font_panel_meta = ImageFont.truetype(chosen_reg, 15)
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

    def project_3d_points(self, pts_3d: np.ndarray, t_video: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Projects 3D Lorenz coordinates (N, 3) into 2D screen coordinates (N, 2) + depth Z_cam (N,)
        using a smooth periodic 18.0s camera rotation around (0, 0, 25.5).
        """
        # Periodic camera angles for a 100% seamless 18.0s loop
        omega_cam = 2.0 * np.pi / 18.0
        yaw = -0.52 + 0.58 * np.sin(omega_cam * t_video)
        pitch = 0.22 + 0.10 * np.cos(omega_cam * t_video)

        # Center around z = 25.5
        centered = pts_3d - np.array([0.0, 0.0, 25.5], dtype=np.float64)
        x = centered[:, 0]
        y = centered[:, 1]
        z = centered[:, 2]

        # Rotate around Z-axis (yaw) so the two butterfly wings face the camera broadly
        cy, sy = np.cos(yaw), np.sin(yaw)
        x1 = x * cy - y * sy
        y1 = x * sy + y * cy
        z1 = z

        # Rotate around X-axis (pitch) for 3D depth elevation
        cp, sp = np.cos(pitch), np.sin(pitch)
        x2 = x1
        y2 = y1 * cp - z1 * sp
        z2 = y1 * sp + z1 * cp

        # Perspective factor (camera distance D = 88.0 units along y2)
        cam_dist = 88.0
        persp = cam_dist / np.maximum(25.0, cam_dist - y2)
        base_scale = 17.8

        px = self.sim_cx + x2 * base_scale * persp
        py = self.sim_cy - z2 * base_scale * persp

        screen_pts = np.column_stack([px, py]).astype(np.int32)
        return screen_pts, y2

    def draw_glowing_node(self, canvas: np.ndarray, px: int, py: int,
                          bgr_col: Tuple[int, int, int], radius: int = 8):
        if not (self.sim_x1 + 10 <= px <= self.sim_x2 - 10 and self.sim_y1 + 10 <= py <= self.sim_y2 - 10):
            return
        cv2.circle(canvas, (px, py), int(radius * 2.6), tuple(int(c * 0.22) for c in bgr_col), -1, cv2.LINE_AA)
        cv2.circle(canvas, (px, py), int(radius * 1.6), tuple(int(c * 0.55) for c in bgr_col), -1, cv2.LINE_AA)
        cv2.circle(canvas, (px, py), radius, bgr_col, -1, cv2.LINE_AA)
        cv2.circle(canvas, (px, py), max(2, radius // 2), (255, 255, 255), -1, cv2.LINE_AA)

    def draw_3d_ribbon(self, canvas: np.ndarray, trail_3d: List[Tuple[float, float, float]],
                       t_video: float, bgr_col: Tuple[int, int, int]):
        if len(trail_3d) < 2:
            return
        # Subsample every 2nd point for fast, ultra-smooth long multi-loop ribbons
        arr = np.array(trail_3d[::2], dtype=np.float64)
        if len(arr) < 2:
            return
        pts_2d, _ = self.project_3d_points(arr, t_video)
        n_pts = len(pts_2d)

        for i in range(n_pts - 1):
            p1 = (int(pts_2d[i, 0]), int(pts_2d[i, 1]))
            p2 = (int(pts_2d[i + 1, 0]), int(pts_2d[i + 1, 1]))
            if not (self.sim_x1 <= p1[0] <= self.sim_x2 and self.sim_y1 <= p1[1] <= self.sim_y2):
                continue
            alpha = (i + 1) / float(n_pts)
            intensity = 0.16 + 0.84 * (alpha ** 1.4)
            col = tuple(int(c * intensity) for c in bgr_col)
            thick = 1 if alpha < 0.35 else (2 if alpha < 0.78 else 3)
            if alpha > 0.65:
                halo_col = tuple(int(c * intensity * 0.35) for c in bgr_col)
                cv2.line(canvas, p1, p2, halo_col, thick + 4, cv2.LINE_AA)
            cv2.line(canvas, p1, p2, col, thick, cv2.LINE_AA)

    def render_frame(self, sim: LorenzSimulation, telem: LorenzTelemetry) -> np.ndarray:
        # Deep Space Cosmic Void (#080B12 -> BGR 18, 11, 8)
        canvas = np.full((self.height, self.width, 3), (18, 11, 8), dtype=np.uint8)

        # BGR Palette
        col_cyan = (255, 240, 0)     # #00F0FF Electric Cyan (Trajectory A)
        col_magenta = (127, 0, 255)  # #FF007F Kinetic Magenta (Trajectory B)
        col_amber = (3, 183, 255)    # #FFB703 Euler Amber (60-Particle Swarm)
        col_emerald = (136, 255, 0)  # #00FF88 Emerald Resonance

        # 1. Top Header Card
        self.draw_card(canvas, self.hdr_x1, self.hdr_y1, self.hdr_x2, self.hdr_y2,
                       bg_bgr=(24, 18, 12), border_bgr=(255, 240, 0))

        # 2. Telemetry Badges
        self.draw_card(canvas, self.b1_x1, self.badge_y1, self.b1_x2, self.badge_y2,
                       bg_bgr=(22, 16, 12), border_bgr=col_magenta if telem.opposite_wings else (120, 95, 45))
        self.draw_card(canvas, self.b2_x1, self.badge_y1, self.b2_x2, self.badge_y2,
                       bg_bgr=(22, 16, 12), border_bgr=(180, 60, 180))
        self.draw_card(canvas, self.b3_x1, self.badge_y1, self.b3_x2, self.badge_y2,
                       bg_bgr=(22, 16, 12), border_bgr=(50, 190, 110))

        # 3. 3D Strange Attractor Viewport
        self.draw_card(canvas, self.sim_x1, self.sim_y1, self.sim_x2, self.sim_y2,
                       bg_bgr=(14, 10, 7), border_bgr=(80, 85, 110))

        # Background stars
        for sx, sy, sb in self.bg_stars:
            canvas[sy, sx] = (sb, int(sb * 0.9), int(sb * 0.8))

        # Subtle coordinate grid inside viewport
        grid_step = 140
        for gx in range(self.sim_x1 + grid_step, self.sim_x2, grid_step):
            cv2.line(canvas, (gx, self.sim_y1), (gx, self.sim_y2), (24, 18, 14), 1, cv2.LINE_AA)
        for gy in range(self.sim_y1 + grid_step, self.sim_y2, grid_step):
            cv2.line(canvas, (self.sim_x1, gy), (self.sim_x2, gy), (24, 18, 14), 1, cv2.LINE_AA)

        # Layer 1: Project and draw 3,600-point Ghost Strange Attractor Manifold
        ghost_2d, _ = self.project_3d_points(sim.ghost_manifold, telem.t_video)
        valid_mask = (
            (ghost_2d[:, 0] > self.sim_x1 + 8) & (ghost_2d[:, 0] < self.sim_x2 - 8) &
            (ghost_2d[:, 1] > self.sim_y1 + 8) & (ghost_2d[:, 1] < self.sim_y2 - 8)
        )
        for idx in range(0, len(ghost_2d) - 1):
            if valid_mask[idx] and valid_mask[idx + 1]:
                p1 = (int(ghost_2d[idx, 0]), int(ghost_2d[idx, 1]))
                p2 = (int(ghost_2d[idx + 1, 0]), int(ghost_2d[idx + 1, 1]))
                cv2.line(canvas, p1, p2, (78, 52, 26), 1, cv2.LINE_AA)

        # Layer 2: Fixed Points C_- (Left Wing), C_+ (Right Wing), and Saddle O(0,0,0)
        fp_3d = np.vstack([sim.fixed_point_minus, sim.fixed_point_plus, sim.fixed_point_origin])
        fp_2d, _ = self.project_3d_points(fp_3d, telem.t_video)
        pulse_r = int(12 + 4 * np.sin(6.0 * telem.t_video))

        # Left Wing Center C_-
        cm_pt = (int(fp_2d[0, 0]), int(fp_2d[0, 1]))
        cv2.circle(canvas, cm_pt, pulse_r, (120, 100, 30), 1, cv2.LINE_AA)
        cv2.drawMarker(canvas, cm_pt, (200, 180, 60), cv2.MARKER_CROSS, 12, 1, cv2.LINE_AA)

        # Right Wing Center C_+
        cp_pt = (int(fp_2d[1, 0]), int(fp_2d[1, 1]))
        cv2.circle(canvas, cp_pt, pulse_r, (100, 40, 130), 1, cv2.LINE_AA)
        cv2.drawMarker(canvas, cp_pt, (200, 80, 220), cv2.MARKER_CROSS, 12, 1, cv2.LINE_AA)

        # Saddle Origin O(0,0,0)
        orig_pt = (int(fp_2d[2, 0]), int(fp_2d[2, 1]))
        if self.sim_y1 + 15 < orig_pt[1] < self.sim_y2 - 15:
            cv2.drawMarker(canvas, orig_pt, (90, 140, 180), cv2.MARKER_DIAMOND, 12, 1, cv2.LINE_AA)

        # Layer 3: Draw 60-Particle Golden Ensemble Cloud
        swarm_2d, _ = self.project_3d_points(sim.swarm_states, telem.t_video)
        for s_pt in swarm_2d:
            sx_p, sy_p = int(s_pt[0]), int(s_pt[1])
            if self.sim_x1 + 8 <= sx_p <= self.sim_x2 - 8 and self.sim_y1 + 8 <= sy_p <= self.sim_y2 - 8:
                cv2.circle(canvas, (sx_p, sy_p), 5, (15, 95, 140), -1, cv2.LINE_AA)
                cv2.circle(canvas, (sx_p, sy_p), 2, col_amber, -1, cv2.LINE_AA)

        # Layer 4: Draw Twin 3D Phosphorescent Ribbons (Cyan A and Magenta B)
        self.draw_3d_ribbon(canvas, sim.trail_a, telem.t_video, col_cyan)
        self.draw_3d_ribbon(canvas, sim.trail_b, telem.t_video, col_magenta)

        # Project current heads A and B
        heads_3d = np.array([
            [telem.traj_a.x, telem.traj_a.y, telem.traj_a.z],
            [telem.traj_b.x, telem.traj_b.y, telem.traj_b.z]
        ], dtype=np.float64)
        heads_2d, _ = self.project_3d_points(heads_3d, telem.t_video)
        pa = (int(heads_2d[0, 0]), int(heads_2d[0, 1]))
        pb = (int(heads_2d[1, 0]), int(heads_2d[1, 1]))

        # Layer 5: Dynamic Euclidean Divergence Vector Laser connecting A and B
        if telem.euclidean_divergence > 1.8:
            laser_col = (80, 210, 255) if not telem.opposite_wings else (90, 90, 255)
            cv2.line(canvas, pa, pb, laser_col, 1, cv2.LINE_AA)

        # Draw Blazing Nodes at Heads B and A
        self.draw_glowing_node(canvas, pb[0], pb[1], col_magenta, radius=8)
        self.draw_glowing_node(canvas, pa[0], pa[1], col_cyan, radius=8)

        # ---------------------------------------------------------------------
        # 4. LIVE LORENZ (1963) DUAL WAVEFORM OSCILLOSCOPE PANEL (x_A vs x_B)
        # ---------------------------------------------------------------------
        self.draw_card(canvas, self.panel_x1, self.panel_y1, self.panel_x2, self.panel_y2,
                       bg_bgr=(20, 15, 11), border_bgr=(120, 90, 55))

        osc_x1, osc_x2 = self.panel_x1 + 30, self.panel_x2 - 30
        osc_y1, osc_y2 = self.panel_y1 + 52, self.panel_y2 - 42
        osc_cy = (osc_y1 + osc_y2) // 2
        osc_w = osc_x2 - osc_x1
        osc_h_half = (osc_y2 - osc_y1) // 2

        # Oscilloscope box & zero-line (x = 0 wing boundary)
        cv2.rectangle(canvas, (osc_x1, osc_y1), (osc_x2, osc_y2), (12, 9, 7), -1)
        cv2.line(canvas, (osc_x1, osc_cy), (osc_x2, osc_cy), (55, 50, 45), 1, cv2.LINE_AA)
        cv2.rectangle(canvas, (osc_x1, osc_y1), (osc_x2, osc_y2), (55, 65, 80), 1)

        n_wave = len(sim.wave_history_a)
        if n_wave >= 2:
            pts_wa = []
            pts_wb = []
            for idx_w in range(n_wave):
                wx = int(osc_x1 + (idx_w / float(max(1, sim.max_wave_len - 1))) * (osc_w - 10))
                wy_a = int(np.clip(osc_cy - (sim.wave_history_a[idx_w] / 22.0) * osc_h_half, osc_y1 + 3, osc_y2 - 3))
                wy_b = int(np.clip(osc_cy - (sim.wave_history_b[idx_w] / 22.0) * osc_h_half, osc_y1 + 3, osc_y2 - 3))
                pts_wa.append((wx, wy_a))
                pts_wb.append((wx, wy_b))

            for idx_w in range(n_wave - 1):
                cv2.line(canvas, pts_wb[idx_w], pts_wb[idx_w + 1], col_magenta, 2, cv2.LINE_AA)
                cv2.line(canvas, pts_wa[idx_w], pts_wa[idx_w + 1], col_cyan, 2, cv2.LINE_AA)

            cv2.circle(canvas, pts_wb[-1], 4, col_magenta, -1, cv2.LINE_AA)
            cv2.circle(canvas, pts_wa[-1], 4, col_cyan, -1, cv2.LINE_AA)

        # ---------------------------------------------------------------------
        # 5. BOTTOM DEBATE / CALLOUT CARD
        # ---------------------------------------------------------------------
        self.draw_card(canvas, self.cta_x1, self.cta_y1, self.cta_x2, self.cta_y2,
                       bg_bgr=(24, 18, 12), border_bgr=(0, 220, 255))

        # ---------------------------------------------------------------------
        # 6. PIL TYPOGRAPHY (STRICT BOUNDING BOX ISOLATION, ZERO OVERLAP)
        # ---------------------------------------------------------------------
        pil_img = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)

        wing_str_a = "C₊" if telem.traj_a.wing > 0 else "C₋"
        wing_str_b = "C₊" if telem.traj_b.wing > 0 else "C₋"

        if self.lang == "ES":
            h_title = "ATRACTOR DE LORENZ 3D // EFECTO MARIPOSA (1963)"
            h_sub = "dx/dt = σ(y-x)  |  dy/dt = x(ρ-z)-y  |  dz/dt = xy - βz"
            b1_lbl = "DIVERGENCIA |Δr(t)|"
            b1_val = f"{telem.euclidean_divergence:06.3f} u"
            b2_lbl = "EXP. LYAPUNOV λ₁"
            b2_val = f"+{telem.lyapunov_max:.4f} s⁻¹"
            b3_lbl = "DIM. FRACTAL D_KY"
            b3_val = f"{telem.kaplan_yorke_dim:.4f} (2D-3D)"
            vp_top_l = f"PARÁMETROS: σ=10, ρ=28, β=8/3  |  CONTRACCIÓN LIOUVILLE: div(F) = {telem.liouville_divergence:.2f} s⁻¹"
            vp_bot_l = f"ÓRBITA A (CIAN): ALA {wing_str_a}   |   ÓRBITA B (Δ₀=10⁻⁴ MAGENTA): ALA {wing_str_b}   |   ENJAMBRE: 60 PTOS"
            panel_title = f"OSCILOSCOPIO DE LORENZ x(t) // {telem.regime_es.upper()}"
            panel_meta = f"DISPERSIÓN ENJAMBRE σ_r: {telem.swarm_spread:05.2f} u   |   VOLUMEN DE FASES V(t) → 0 (VARIEDAD EXTRAÑA)"
            cta_title = "En 1963, redondear 0.506127 a 0.506 cambió la historia de la ciencia:"
            cta_desc = "Cero azar, 100% leyes deterministas, pero un error de 10⁻⁴ separa los dos\nmundos hacia alas opuestas. ¿Por qué el volumen es 0 si nunca se cruzan?"
        else:
            h_title = "3D LORENZ ATTRACTOR // BUTTERFLY EFFECT (1963)"
            h_sub = "dx/dt = σ(y-x)  |  dy/dt = x(ρ-z)-y  |  dz/dt = xy - βz"
            b1_lbl = "DIVERGENCE |Δr(t)|"
            b1_val = f"{telem.euclidean_divergence:06.3f} u"
            b2_lbl = "LYAPUNOV EXP λ₁"
            b2_val = f"+{telem.lyapunov_max:.4f} s⁻¹"
            b3_lbl = "FRACTAL DIM D_KY"
            b3_val = f"{telem.kaplan_yorke_dim:.4f} (2D-3D)"
            vp_top_l = f"PARAMETERS: σ=10, ρ=28, β=8/3  |  LIOUVILLE CONTRACTION: div(F) = {telem.liouville_divergence:.2f} s⁻¹"
            vp_bot_l = f"ORBIT A (CYAN): WING {wing_str_a}   |   ORBIT B (Δ₀=10⁻⁴ MAGENTA): WING {wing_str_b}   |   SWARM: 60 PTS"
            panel_title = f"LORENZ WAVEFORM x(t) // {telem.regime_en.upper()}"
            panel_meta = f"ENSEMBLE SPREAD σ_r: {telem.swarm_spread:05.2f} u   |   PHASE VOLUME V(t) → 0 (STRANGE MANIFOLD)"
            cta_title = "In 1963, rounding 0.506127 to 0.506 changed science forever:"
            cta_desc = "Zero randomness, 100% deterministic laws—yet a 10⁻⁴ shift flings the two\nworlds onto opposite wings. Why does volume shrink to 0 without crossing?"

        # Header Text
        draw.text((self.hdr_x1 + 24, self.hdr_y1 + 22), h_title, font=self.font_hdr_title, fill=(0, 240, 255))
        draw.text((self.hdr_x1 + 24, self.hdr_y1 + 66), h_sub, font=self.font_hdr_sub, fill=(240, 245, 255))

        # Badges Text
        draw.text((self.b1_x1 + 18, self.badge_y1 + 15), b1_lbl, font=self.font_badge_lbl, fill=(165, 185, 205))
        b1_color = (255, 80, 160) if telem.opposite_wings else (0, 240, 255)
        draw.text((self.b1_x1 + 18, self.badge_y1 + 38), b1_val, font=self.font_badge_val, fill=b1_color)

        draw.text((self.b2_x1 + 18, self.badge_y1 + 15), b2_lbl, font=self.font_badge_lbl, fill=(165, 185, 205))
        draw.text((self.b2_x1 + 18, self.badge_y1 + 38), b2_val, font=self.font_badge_val, fill=(245, 110, 245))

        draw.text((self.b3_x1 + 18, self.badge_y1 + 15), b3_lbl, font=self.font_badge_lbl, fill=(165, 185, 205))
        draw.text((self.b3_x1 + 18, self.badge_y1 + 38), b3_val, font=self.font_badge_val, fill=(90, 255, 165))

        # Viewport Top & Bottom HUD Strips (Strictly pinned to top/bottom margins of 3D box)
        draw.text((self.sim_x1 + 22, self.sim_y1 + 16), vp_top_l, font=self.font_panel_meta, fill=(180, 210, 235))
        draw.text((self.sim_x1 + 22, self.sim_y2 - 34), vp_bot_l, font=self.font_panel_meta, fill=(255, 215, 90))

        # Fixed point subtle tags
        if self.sim_x1 + 40 < cm_pt[0] < self.sim_x2 - 60 and self.sim_y1 + 55 < cm_pt[1] < self.sim_y2 - 55:
            draw.text((cm_pt[0] - 28, cm_pt[1] - 28), "C₋", font=self.font_viewport_tag, fill=(0, 240, 255))
        if self.sim_x1 + 40 < cp_pt[0] < self.sim_x2 - 60 and self.sim_y1 + 55 < cp_pt[1] < self.sim_y2 - 55:
            draw.text((cp_pt[0] + 14, cp_pt[1] - 28), "C₊", font=self.font_viewport_tag, fill=(255, 90, 190))

        # Oscilloscope Panel Text
        draw.text((self.panel_x1 + 24, self.panel_y1 + 16), panel_title, font=self.font_panel_title, fill=(0, 240, 255))
        draw.text((self.panel_x1 + 24, self.panel_y2 - 30), panel_meta, font=self.font_panel_meta, fill=(175, 190, 210))

        # Bottom Callout Card Text
        draw.text((self.cta_x1 + 24, self.cta_y1 + 16), cta_title, font=self.font_cta_title, fill=(255, 215, 0))
        draw.text((self.cta_x1 + 24, self.cta_y1 + 48), cta_desc, font=self.font_cta_desc, fill=(240, 245, 255))

        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def enhance_hero_image(bgr_frame: np.ndarray, output_path: str):
    """
    Applies image-enhancer crispness & micro-contrast optimization for high-retention social covers.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    pil_img = Image.fromarray(cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB))
    sharpened = pil_img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=125, threshold=2))
    sharpened.save(output_path, format="PNG", optimize=True)


def render_lorenz_video(
    output_mp4: str,
    audio_wav: Optional[str] = None,
    lang: str = "ES",
    duration: float = 18.0,
    fps: int = 60,
    hero_capture_path: Optional[str] = None
) -> str:
    """
    Renders the complete 18.0s 3D Lorenz Strange Attractor simulation @ 60 FPS and multiplexes stereo audio.
    """
    Path(output_mp4).parent.mkdir(parents=True, exist_ok=True)
    temp_video = str(Path(output_mp4).with_suffix(".temp.mp4"))

    sim = LorenzSimulation()
    renderer = MasterLorenz3DRenderer(width=1080, height=1920, fps=fps, lang=lang)

    total_frames = int(duration * fps)
    dt_frame = 1.0 / float(fps)

    print(f"\n[RENDER] Starting 3D Lorenz Strange Attractor Pipeline [{lang}]: {total_frames} frames @ {fps} FPS -> {output_mp4}")

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
    # Capture hero cover at t = 9.0s when A and B are on opposite wings with full multi-loop ribbons and oscilloscope split
    hero_frame_idx = int(9.0 * fps)

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
                f"|dr|={telem.euclidean_divergence:.3f} | opp_wings={telem.opposite_wings} | "
                f"FPS={fps_proc:.1f} | ETA={eta:.1f}s"
            )

    pipe.stdin.close()
    pipe.wait()

    if hero_capture_path and hero_frame is not None:
        enhance_hero_image(hero_frame, hero_capture_path)
        print(f"[OK] Enhanced Hero Cover saved to: {hero_capture_path}")

    if audio_wav and os.path.exists(audio_wav):
        print(f"[AUDIO] Multiplexing binaural stereo Lorenz soundtrack: {audio_wav}")
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
