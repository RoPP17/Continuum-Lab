"""
Continuum Lab - Master 9:16 UHD 60 FPS Visual Video Renderer for Nonlinear Euler Elastica
Module: 03 Mecanica de Solidos / 02 Pandeo No Lineal y Elastica de Euler
File: src/visualization/render_elastica_video.py

Renders 1080x1920 (9:16 Vertical UHD @ 60 FPS) cinematic animations:
  - Deep Cosmic Void & Neon Cybernetic Palette (#030611, #00F0FF, #FF0055, #FFB703, #00FF88)
  - Full-Bleed 1080x1920 layout without cramped dashboard boxes
  - Exact Jacobi elliptic large deflection kinematics (s, x(s), y(s), theta(s), kappa(s))
  - Multi-pass neon bloom & curvature moment distribution combs (M = EI * kappa)
  - Floating Real-time Supercritical Pitchfork Bifurcation Mini-Radar
  - Real-time Glassmorphic Telemetry HUD: P/P_cr, alpha, Delta_x/L, sigma_max
  - Dynamic kinetic typography hooks & narrative subtitles (ES & EN)
  - 16.0s seamless infinite loop architecture
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple, Dict
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

from src.physics.euler_elastica_sim import EulerElastica


class MasterEulerElasticaVideoRenderer:
    """
    Master 9:16 60 FPS Cinematic Video Renderer for Nonlinear Euler Elastica.
    """

    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 60, lang: str = "ES"):
        self.width = width
        self.height = height
        self.fps = fps
        self.lang = lang.upper()

        self.elastica = EulerElastica(L=1.0, E=210e9, b=0.02, h=0.003)
        self._load_fonts()
        self._precompute_bifurcation()

        # Geometry coordinates for vertical column setup
        # Bottom anchor fixed at (540, 1530)
        self.bot_x = 540
        self.bot_y = 1530
        # Straight top position at (540, 670) -> column length = 860 px (scaled for safe screen bounds)
        self.top_x_init = 540
        self.top_y_init = 670
        self.col_pixel_len = 860.0

        # Background particles
        rng = np.random.default_rng(2026)
        self.particles = []
        for _ in range(90):
            px = float(rng.uniform(40, self.width - 40))
            py = float(rng.uniform(60, self.height - 60))
            spd = float(rng.uniform(0.4, 1.8))
            sz = int(rng.integers(1, 4))
            alpha = float(rng.uniform(0.15, 0.65))
            self.particles.append([px, py, spd, sz, alpha])

    def _load_fonts(self):
        def try_font(path, size, fallback=None):
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    pass
            return fallback or ImageFont.load_default()

        # High-impact typography
        self.f_hero_hook = try_font("C:/Windows/Fonts/segoeuib.ttf", 30, try_font("C:/Windows/Fonts/arialbd.ttf", 30))
        self.f_sub_hook = try_font("C:/Windows/Fonts/segoeui.ttf", 21, try_font("C:/Windows/Fonts/arial.ttf", 21))
        self.f_brand_title = try_font("C:/Windows/Fonts/segoeuib.ttf", 22)
        self.f_brand_sub = try_font("C:/Windows/Fonts/consolab.ttf", 15)
        self.f_card_hdr = try_font("C:/Windows/Fonts/segoeuib.ttf", 16)
        self.f_card_meta = try_font("C:/Windows/Fonts/consolab.ttf", 14)
        self.f_hud_lbl = try_font("C:/Windows/Fonts/segoeuib.ttf", 14)
        self.f_hud_val = try_font("C:/Windows/Fonts/consolab.ttf", 20)
        self.f_badge_tag = try_font("C:/Windows/Fonts/consolab.ttf", 13)

    def _precompute_bifurcation(self):
        """Precomputes smooth supercritical pitchfork branches for mini-radar card."""
        alphas = np.linspace(0.01, np.radians(85.0), 90)
        self.bif_p = []
        self.bif_dy = []
        for a in alphas:
            sol = self.elastica.solve_exact(a, num_points=60)
            self.bif_p.append(sol["P_ratio"])
            self.bif_dy.append(sol["delta_y_max"] / self.elastica.L)
        self.bif_p = np.array(self.bif_p)
        self.bif_dy = np.array(self.bif_dy)

    def _draw_glowing_line(self, img_bgr: np.ndarray, pts: np.ndarray, color_bgr: Tuple[int, int, int], 
                           thickness: int = 3, halo_thickness: int = 14, halo_alpha: float = 0.35):
        """Draws a line with smooth multi-layer neon bloom."""
        overlay = img_bgr.copy()
        pts_int = pts.astype(np.int32)
        # Outer diffuse glow
        cv2.polylines(overlay, [pts_int], isClosed=False, color=color_bgr, thickness=halo_thickness, lineType=cv2.LINE_AA)
        cv2.addWeighted(overlay, halo_alpha, img_bgr, 1.0 - halo_alpha, 0, img_bgr)

        # Mid glow
        mid_thick = max(1, thickness + 4)
        cv2.polylines(img_bgr, [pts_int], isClosed=False, color=color_bgr, thickness=mid_thick, lineType=cv2.LINE_AA)
        # Core laser spine (white hot)
        cv2.polylines(img_bgr, [pts_int], isClosed=False, color=(255, 255, 255), thickness=max(1, thickness - 1), lineType=cv2.LINE_AA)

    def render_frame(self, t: float, frame_idx: int) -> np.ndarray:
        """
        Renders a single 1080x1920 frame at time t (seconds).
        """
        # Canvas initialization with subtle vertical gradient
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        # Deep cosmic void gradient: (B=14, G=6, R=3) to (B=26, G=12, R=7)
        grad = np.linspace(0, 1, self.height)[:, None]
        frame[:, :, 0] = (14 + grad * 14).astype(np.uint8)
        frame[:, :, 1] = (6 + grad * 7).astype(np.uint8)
        frame[:, :, 2] = (3 + grad * 5).astype(np.uint8)

        # Subtle ambient grid lines (alpha-blended)
        grid_overlay = frame.copy()
        for gy in range(0, self.height, 120):
            cv2.line(grid_overlay, (0, gy), (self.width, gy), (40, 24, 15), 1, cv2.LINE_AA)
        for gx in range(0, self.width, 120):
            cv2.line(grid_overlay, (gx, 0), (gx, self.height), (40, 24, 15), 1, cv2.LINE_AA)
        cv2.addWeighted(grid_overlay, 0.28, frame, 0.72, 0, frame)

        # Ambient floating dust particles
        for p in self.particles:
            p[1] -= p[2]
            if p[1] < 50:
                p[1] = self.height - 50
            b_val = int(255 * p[4])
            g_val = int(240 * p[4])
            r_val = int(120 * p[4])
            cv2.circle(frame, (int(p[0]), int(p[1])), p[3], (b_val, g_val, r_val), -1, cv2.LINE_AA)

        # -------------------------------------------------------------
        # Physical Kinematics Schedule (16.0s duration)
        # -------------------------------------------------------------
        # Phase 1: 0.0 - 2.5s -> Compression building (P/P_cr: 0.20 -> 1.00, alpha = 0)
        # Phase 2: 2.5 - 7.5s -> Supercritical Buckling (alpha: 0 -> +82.0 deg, P/P_cr -> 1.52)
        # Phase 3: 7.5 - 9.5s -> Large deflection breathing hold (alpha ~ 82 deg)
        # Phase 4: 9.5 - 12.5s -> Symmetry reversal to negative branch (alpha: +82 -> -55 deg)
        # Phase 5: 12.5 - 16.0s -> Reversible elastic return to straight neutral state
        if t < 2.5:
            # Pre-critical
            tau = t / 2.5
            p_ratio = 0.20 + 0.80 * (tau ** 1.6)
            alpha_deg = 0.0
            sign_branch = 1.0
        elif t < 7.5:
            # Buckling ramp up
            tau = (t - 2.5) / 5.0
            # Smooth quintic ease
            w = 6 * (tau**5) - 15 * (tau**4) + 10 * (tau**3)
            alpha_deg = 82.0 * w
            p_ratio = self.elastica.load_ratio_from_alpha(np.radians(alpha_deg))
            sign_branch = 1.0
        elif t < 9.5:
            # Peak hold with subtle breathing
            tau = (t - 7.5) / 2.0
            breath = np.sin(2.0 * np.pi * 1.5 * tau) * 2.2
            alpha_deg = 82.0 + breath
            p_ratio = self.elastica.load_ratio_from_alpha(np.radians(alpha_deg))
            sign_branch = 1.0
        elif t < 12.5:
            # Symmetry reversal through 0 to negative branch
            tau = (t - 9.5) / 3.0
            # Transition from +82 to -55 deg
            # Cosine curve
            w = 0.5 * (1.0 - np.cos(np.pi * tau))
            alpha_deg = 82.0 - 137.0 * w  # 82 - 137 = -55
            sign_branch = 1.0 if alpha_deg >= 0 else -1.0
            p_ratio = self.elastica.load_ratio_from_alpha(np.radians(abs(alpha_deg)))
        else:
            # Return smoothly to straight (tau from 0 to 1)
            tau = (t - 12.5) / 3.5
            # Smoothstep to 0
            w = 1.0 - (6 * (tau**5) - 15 * (tau**4) + 10 * (tau**3))
            alpha_deg = -55.0 * w
            sign_branch = -1.0 if alpha_deg < 0 else 1.0
            p_ratio = 1.0 + (self.elastica.load_ratio_from_alpha(np.radians(55.0)) - 1.0) * w
            if abs(alpha_deg) < 0.2:
                p_ratio = 0.20 + 0.80 * (1.0 - tau)

        alpha_rad = np.radians(abs(alpha_deg))

        # Solve exact elastica profile
        if abs(alpha_rad) < 1e-4:
            s_arr = np.linspace(0, 1.0, 200)
            x_norm = s_arr
            y_norm = np.zeros_like(s_arr)
            kappa_arr = np.zeros_like(s_arr)
            delta_x_val = 0.0
            delta_y_val = 0.0
            sigma_max_mpa = (p_ratio * self.elastica.P_cr / self.elastica.A) / 1e6
        else:
            sol = self.elastica.solve_exact(alpha_rad, num_points=200)
            x_norm = sol["x"] / self.elastica.L  # 0 to 1-delta_x
            y_norm = sol["y"] / self.elastica.L  # lateral bow
            kappa_arr = sol["kappa"]
            delta_x_val = sol["delta_x"] / self.elastica.L
            delta_y_val = sol["delta_y_max"] / self.elastica.L
            sigma_max_mpa = sol["sigma_max_MPa"]

        # Map to vertical column coordinates on canvas
        # Bottom anchor fixed at (bot_x, bot_y) = (540, 1580)
        # When s=0, column is at bottom anchor
        # When s=L, column top is at y_top = bot_y - (1 - delta_x) * col_pixel_len
        y_top_current = self.bot_y - (1.0 - delta_x_val) * self.col_pixel_len

        # Column coordinates:
        # Beam arc goes from bottom (y=bot_y) up to top (y=y_top_current)
        # Vertical coord: y_px(s) = bot_y - x_norm(s) * col_pixel_len
        # Horizontal lateral deflection: x_px(s) = bot_x + sign_branch * y_norm(s) * col_pixel_len
        beam_y = self.bot_y - x_norm * self.col_pixel_len
        beam_x = self.bot_x + sign_branch * y_norm * self.col_pixel_len
        beam_pts = np.column_stack((beam_x, beam_y))

        # -------------------------------------------------------------
        # Draw Mechanical Fixtures & Actuator
        # -------------------------------------------------------------
        # 1. Bottom Pinned Anchor (540, 1580)
        tri_pts = np.array([
            [self.bot_x, self.bot_y],
            [self.bot_x - 36, self.bot_y + 44],
            [self.bot_x + 36, self.bot_y + 44]
        ], np.int32)
        cv2.fillPoly(frame, [tri_pts], (35, 22, 14), cv2.LINE_AA)
        cv2.polylines(frame, [tri_pts], True, (0, 240, 255), 2, cv2.LINE_AA)
        # Bearing pin circle
        cv2.circle(frame, (self.bot_x, self.bot_y), 9, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(frame, (self.bot_x, self.bot_y), 14, (0, 240, 255), 2, cv2.LINE_AA)
        # Foundation base plate & hatch marks
        cv2.line(frame, (self.bot_x - 60, self.bot_y + 44), (self.bot_x + 60, self.bot_y + 44), (0, 240, 255), 3, cv2.LINE_AA)
        for hx in range(self.bot_x - 50, self.bot_x + 50, 16):
            cv2.line(frame, (hx, self.bot_y + 45), (hx - 12, self.bot_y + 60), (100, 70, 50), 2, cv2.LINE_AA)

        # 2. Top Hydraulic Actuator & Piston Head
        top_y_int = int(y_top_current)
        piston_w = 90
        piston_h = 28
        # Piston block
        cv2.rectangle(frame, (self.bot_x - piston_w // 2, top_y_int - piston_h),
                      (self.bot_x + piston_w // 2, top_y_int), (30, 20, 14), -1)
        cv2.rectangle(frame, (self.bot_x - piston_w // 2, top_y_int - piston_h),
                      (self.bot_x + piston_w // 2, top_y_int), (0, 240, 255), 2, cv2.LINE_AA)
        # Hydraulic piston rod extending upwards (originating below upper HUD panels)
        cv2.rectangle(frame, (self.bot_x - 16, 480), (self.bot_x + 16, top_y_int - piston_h), (50, 35, 25), -1)
        cv2.rectangle(frame, (self.bot_x - 16, 480), (self.bot_x + 16, top_y_int - piston_h), (0, 240, 255), 2, cv2.LINE_AA)
        # Top pin bearing
        cv2.circle(frame, (self.bot_x, top_y_int), 8, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(frame, (self.bot_x, top_y_int), 13, (0, 240, 255), 2, cv2.LINE_AA)

        # Dynamic Compressive Force Arrows pointing DOWN onto the piston
        arrow_len = int(35 + 45 * min(p_ratio, 1.8))
        arr_y1 = top_y_int - piston_h - 15 - arrow_len
        arr_y2 = top_y_int - piston_h - 15
        arr_color = (0, 160, 255) if p_ratio < 1.0 else (0, 80, 255) if p_ratio < 1.3 else (85, 0, 255)
        # Draw central force arrow
        cv2.arrowedLine(frame, (self.bot_x, arr_y1), (self.bot_x, arr_y2), arr_color, 4, cv2.LINE_AA, tipLength=0.35)
        # Side auxiliary force arrows
        cv2.arrowedLine(frame, (self.bot_x - 30, arr_y1 + 10), (self.bot_x - 30, arr_y2), arr_color, 2, cv2.LINE_AA, tipLength=0.35)
        cv2.arrowedLine(frame, (self.bot_x + 30, arr_y1 + 10), (self.bot_x + 30, arr_y2), arr_color, 2, cv2.LINE_AA, tipLength=0.35)

        # -------------------------------------------------------------
        # Curvature Moment Distribution Combs (M = E * I * kappa)
        # -------------------------------------------------------------
        if abs(alpha_rad) > 0.05:
            comb_overlay = frame.copy()
            # Sample every 6 points
            for i in range(5, len(beam_pts) - 5, 6):
                pt = beam_pts[i]
                # Tangent vector
                t_vec = beam_pts[i + 1] - beam_pts[i - 1]
                t_norm = np.linalg.norm(t_vec)
                if t_norm > 1e-6:
                    t_unit = t_vec / t_norm
                    # Normal vector pointing to center of curvature (inward)
                    n_unit = np.array([-t_unit[1], t_unit[0]]) * sign_branch
                    kap = abs(kappa_arr[i])
                    comb_len = min(kap * 14.0, 48.0)
                    comb_end = pt - n_unit * comb_len
                    # Color based on curvature intensity: Electric Magenta to Gold
                    cv2.line(comb_overlay, (int(pt[0]), int(pt[1])), (int(comb_end[0]), int(comb_end[1])),
                             (255, 0, 180), 1, cv2.LINE_AA)
                    cv2.circle(comb_overlay, (int(comb_end[0]), int(comb_end[1])), 2, (0, 240, 255), -1, cv2.LINE_AA)
            cv2.addWeighted(comb_overlay, 0.45, frame, 0.55, 0, frame)

        # -------------------------------------------------------------
        # Draw the Glowing Nonlinear Elastica Beam
        # -------------------------------------------------------------
        # Dynamic color gradient along the beam based on curvature kappa
        # Straight state: Cyan -> Amber as load increases
        if abs(alpha_rad) < 1e-3:
            straight_color = (
                int(255 * (1.0 - 0.7 * min(p_ratio, 1.0))),  # B
                int(240 * (1.0 - 0.3 * min(p_ratio, 1.0))),  # G
                int(0 + 255 * min(p_ratio, 1.0))             # R
            )
            self._draw_glowing_line(frame, beam_pts, straight_color, thickness=5, halo_thickness=22, halo_alpha=0.45)
        else:
            # Segmented multi-color drawing for curvature heat-map
            n_segs = len(beam_pts) - 1
            max_k = max(np.max(kappa_arr), 1e-5)
            for i in range(n_segs):
                # Normalized local curvature (0 at ends, 1 at mid-span)
                k_local = (abs(kappa_arr[i]) + abs(kappa_arr[i + 1])) / (2.0 * max_k)
                # Color transition: BGR
                # k=0: Electric Cyan (255, 240, 0)
                # k=0.5: Vivid Violet (220, 0, 150)
                # k=1.0: Neon Magenta/Amber (0, 50, 255) to (0, 200, 255)
                b_c = int(255 * (1.0 - k_local * 0.85))
                g_c = int(240 * (1.0 - k_local * 0.70))
                r_c = int(255 * (k_local ** 0.8))
                seg_color = (b_c, g_c, r_c)
                pt1 = (int(beam_pts[i][0]), int(beam_pts[i][1]))
                pt2 = (int(beam_pts[i + 1][0]), int(beam_pts[i + 1][1]))
                # Layered drawing for segment
                cv2.line(frame, pt1, pt2, seg_color, 6, cv2.LINE_AA)
                cv2.line(frame, pt1, pt2, (255, 255, 255), 2, cv2.LINE_AA)

        # -------------------------------------------------------------
        # PIL High-Precision Glassmorphism HUD Overlay
        # -------------------------------------------------------------
        img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil, "RGBA")

        # 1. Top Header Branding Capsule (y = 80 to 168, balanced margins x = 75 to 1005)
        self._draw_glass_panel(draw, 75, 80, self.width - 75, 168, border_color=(0, 240, 255, 200))
        brand_en = "CONTINUUM LAB // ADVANCED SOLID MECHANICS"
        brand_es = "CONTINUUM LAB // MECÁNICA DE SÓLIDOS AVANZADA"
        hdr_txt = brand_es if self.lang == "ES" else brand_en
        title_txt = "PANDEO NO LINEAL & ELÁSTICA DE EULER (1744)" if self.lang == "ES" else "NONLINEAR EULER ELASTICA & PITCHFORK BIFURCATION"
        w_hdr = draw.textlength(hdr_txt, font=self.f_card_meta)
        w_title = draw.textlength(title_txt, font=self.f_brand_title)
        draw.text((int((self.width - w_hdr) / 2), 95), hdr_txt, font=self.f_card_meta, fill=(0, 240, 255, 255))
        draw.text((int((self.width - w_title) / 2), 120), title_txt, font=self.f_brand_title, fill=(255, 255, 255, 255))

        # 2. Pitchfork Bifurcation Mini-Radar Card (Upper Left: x = 75 to 455, y = 195 to 455)
        self._draw_glass_panel(draw, 75, 195, 455, 455, border_color=(0, 240, 255, 180))
        radar_title = "DIAGRAMA DE BIFURCACIÓN" if self.lang == "ES" else "PITCHFORK BIFURCATION"
        draw.text((95, 210), radar_title, font=self.f_card_hdr, fill=(0, 240, 255, 255))
        draw.text((95, 232), "Bifurcación Supercrítica Tridente", font=self.f_card_meta, fill=(160, 180, 200, 230))

        # Coordinate axes of mini radar:
        # P/P_cr from 0.5 to 1.6 mapped to x in [100, 430]
        # delta_y/L from -0.45 to +0.45 mapped to y in [425, 275]
        rx0, rx1 = 100, 430
        ry_mid = 350
        ry_min, ry_max = 275, 425

        # Draw axis lines
        draw.line([(rx0, ry_mid), (rx1, ry_mid)], fill=(80, 100, 120, 180), width=1)
        # Vertical line at P/P_cr = 1.0
        p_crit_x = rx0 + int((1.0 - 0.5) / (1.6 - 0.5) * (rx1 - rx0))
        draw.line([(p_crit_x, ry_min), (p_crit_x, ry_max)], fill=(255, 183, 3, 140), width=1)
        draw.text((p_crit_x - 14, ry_max + 4), "P_cr", font=self.f_badge_tag, fill=(255, 183, 3, 230))

        # Stable line P < P_cr
        draw.line([(rx0, ry_mid), (p_crit_x, ry_mid)], fill=(0, 255, 136, 230), width=2)
        # Unstable line P > P_cr (dashed simulation)
        for dx_s in range(p_crit_x, rx1, 8):
            draw.line([(dx_s, ry_mid), (min(dx_s + 4, rx1), ry_mid)], fill=(255, 50, 50, 180), width=1)

        # Plot precomputed pitchfork branches
        pos_pts = []
        neg_pts = []
        for bp, bdy in zip(self.bif_p, self.bif_dy):
            if bp <= 1.6:
                bx = rx0 + (bp - 0.5) / (1.6 - 0.5) * (rx1 - rx0)
                by_pos = ry_mid - (bdy / 0.45) * (ry_mid - ry_min)
                by_neg = ry_mid + (bdy / 0.45) * (ry_mid - ry_min)
                pos_pts.append((bx, by_pos))
                neg_pts.append((bx, by_neg))

        if len(pos_pts) > 1:
            draw.line(pos_pts, fill=(0, 240, 255, 230), width=2)
            draw.line(neg_pts, fill=(255, 0, 128, 230), width=2)

        # Draw Current State Point on the Pitchfork Radar
        cur_p_x = rx0 + np.clip((p_ratio - 0.5) / (1.6 - 0.5), 0.0, 1.0) * (rx1 - rx0)
        cur_dy_y = ry_mid - (sign_branch * delta_y_val / 0.45) * (ry_mid - ry_min)
        cur_dy_y = np.clip(cur_dy_y, ry_min - 5, ry_max + 5)
        # Pulsing circle halo around current point
        pulse_r = int(5 + 3 * np.sin(t * 8.0))
        draw.ellipse([cur_p_x - pulse_r, cur_dy_y - pulse_r, cur_p_x + pulse_r, cur_dy_y + pulse_r],
                     outline=(255, 255, 255, 240), width=2)
        draw.ellipse([cur_p_x - 3, cur_dy_y - 3, cur_p_x + 3, cur_dy_y + 3], fill=(0, 240, 255, 255))

        # 3. Telemetry Glass HUD (Upper Right: x = 625 to 1005, y = 195 to 455)
        self._draw_glass_panel(draw, 625, 195, 1005, 455, border_color=(0, 240, 255, 180))
        draw.text((650, 210), "TELEMETRÍA ANALÍTICA" if self.lang == "ES" else "ANALYTICAL TELEMETRY",
                  font=self.f_card_hdr, fill=(0, 240, 255, 255))

        # Dynamic Status Badge
        if p_ratio < 1.0:
            status_txt = "[ESTABLE // PRE-PANDEO]" if self.lang == "ES" else "[STABLE // PRE-BUCKLING]"
            status_color = (0, 255, 136, 255)
        elif abs(p_ratio - 1.0) < 0.05:
            status_txt = "[BIFURCACIÓN CRÍTICA]" if self.lang == "ES" else "[CRITICAL BIFURCATION]"
            status_color = (255, 183, 3, 255)
        else:
            status_txt = "[REGIMEN NO LINEAL]" if self.lang == "ES" else "[POST-BUCKLING REGIME]"
            status_color = (255, 0, 85, 255)
        draw.text((650, 233), status_txt, font=self.f_badge_tag, fill=status_color)

        # 4 Telemetry Rows
        hud_rows = [
            ("CARGA P / P_cr:" if self.lang == "ES" else "LOAD P / P_cr:", f"{p_ratio:.3f}"),
            ("ROTACIÓN α:" if self.lang == "ES" else "END ROTATION α:", f"{alpha_deg:+.1f}°"),
            ("ACORTAMIENTO Δx:" if self.lang == "ES" else "AXIAL SINK Δx:", f"{delta_x_val * 100:.1f}%"),
            ("TENSIÓN MÁX σ:" if self.lang == "ES" else "MAX STRESS σ:", f"{sigma_max_mpa:.0f} MPa")
        ]
        hud_y_start = 265
        for idx, (lbl, val) in enumerate(hud_rows):
            row_y = hud_y_start + idx * 42
            draw.text((650, row_y), lbl, font=self.f_hud_lbl, fill=(180, 200, 220, 240))
            draw.text((840, row_y - 3), val, font=self.f_hud_val, fill=(255, 255, 255, 255))

        # -------------------------------------------------------------
        # Dynamic Kinetic Typography Subtitles (Lower Safe Zone: y = 1645 to 1805)
        # -------------------------------------------------------------
        hook_box_y1 = 1645
        hook_box_y2 = 1805
        self._draw_glass_panel(draw, 75, hook_box_y1, self.width - 75, hook_box_y2, border_color=(255, 0, 85, 200))

        if t < 2.5:
            # Phase 1: The Hook
            if self.lang == "ES":
                main_hook = "¿POR QUÉ EL ACERO NO SE DOBLA...?"
                sub_hook = "La barra soporta compresión axial pura sin arquearse hasta cruzar P_cr"
            else:
                main_hook = "WHY DOES STEEL REFUSE TO BEND...?"
                sub_hook = "Pure axial compression maintains equilibrium until crossing P_cr"
            glow_c = (0, 240, 255, 255)
        elif t < 5.0:
            # Phase 2: Bifurcation snap
            if self.lang == "ES":
                main_hook = "¡P = P_cr: BIFURCACIÓN TRIDENTE!"
                sub_hook = "Ruptura espontánea de simetría: el estado recto se vuelve inestable"
            else:
                main_hook = "P = P_cr: PITCHFORK BIFURCATION SNAP!"
                sub_hook = "Spontaneous symmetry breaking: straight equilibrium turns unstable"
            glow_c = (255, 183, 3, 255)
        elif t < 9.5:
            # Phase 3: Exact Jacobi Large Deflection
            if self.lang == "ES":
                main_hook = "SOLUCIÓN EXACTA DE JACOBI (α → 82°)"
                sub_hook = "Grandes deflexiones gobernadas por Integrales Elípticas Completas K(k)"
            else:
                main_hook = "EXACT JACOBI ELLIPTIC REGIME (α → 82°)"
                sub_hook = "Large deflections governed by Complete Elliptic Integrals K(k)"
            glow_c = (255, 0, 85, 255)
        elif t < 13.0:
            # Phase 4: Symmetry Choice
            if self.lang == "ES":
                main_hook = "¿HACIA DÓNDE DECIDE DOBLARSE LA FÍSICA?"
                sub_hook = "Simetría Z_2 perfecta: dos ramas post-críticas idénticas en energía"
            else:
                main_hook = "WHICH BRANCH DOES NATURE CHOOSE?"
                sub_hook = "Perfect Z_2 pitchfork symmetry: dual post-critical energy minima"
            glow_c = (0, 240, 255, 255)
        else:
            # Phase 5: Reversible Equilibrium & Loop
            if self.lang == "ES":
                main_hook = "EQUILIBRIO ELÁSTICO 100% REVERSIBLE"
                sub_hook = "Sin deformación plástica // Continuum Lab (Monorepo Open Source)"
            else:
                main_hook = "100% REVERSIBLE ELASTIC EQUILIBRIUM"
                sub_hook = "Zero plastic deformation // Continuum Lab Open-Source Engineering"
            glow_c = (0, 255, 136, 255)

        w_main = draw.textlength(main_hook, font=self.f_hero_hook)
        w_sub = draw.textlength(sub_hook, font=self.f_sub_hook)
        draw.text((int((self.width - w_main) / 2), hook_box_y1 + 25), main_hook, font=self.f_hero_hook, fill=glow_c)
        draw.text((int((self.width - w_sub) / 2), hook_box_y1 + 82), sub_hook, font=self.f_sub_hook, fill=(220, 230, 240, 245))

        # Bottom safe zone tag (Watermark)
        draw.text((self.width // 2 - 120, self.height - 75), "github.com/RoPP17/Continuum-Lab",
                  font=self.f_badge_tag, fill=(120, 140, 160, 180))

        # Convert back to OpenCV BGR
        final_frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        return final_frame

    def _draw_glass_panel(self, draw: ImageDraw.ImageDraw, x1: int, y1: int, x2: int, y2: int, 
                          bg_fill: Tuple[int, int, int, int] = (10, 16, 28, 200),
                          border_color: Tuple[int, int, int, int] = (0, 240, 255, 180),
                          corner_radius: int = 16):
        """Draws a sleek rounded glassmorphic card with glowing border."""
        draw.rounded_rectangle([x1, y1, x2, y2], radius=corner_radius, fill=bg_fill, outline=border_color, width=2)


def render_elastica_video(output_mp4: str, audio_wav: Optional[str] = None, 
                          duration: float = 16.0, fps: int = 60, lang: str = "ES",
                          hero_capture_path: Optional[str] = None) -> str:
    """
    Renders the complete 9:16 vertical video at 60 FPS using an FFmpeg pipeline.
    """
    renderer = MasterEulerElasticaVideoRenderer(width=1080, height=1920, fps=fps, lang=lang)
    total_frames = int(duration * fps)
    temp_video = output_mp4.replace(".mp4", "_temp.mp4")

    os.makedirs(os.path.dirname(output_mp4), exist_ok=True)

    # Launch FFmpeg stdin pipe
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

    print(f"[{lang}] Launching FFmpeg render pipeline for {total_frames} frames (1080x1920 @ {fps} FPS)...")
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    hero_frame_idx = int(7.5 * fps)  # Peak deflection frame
    hero_bgr = None
    t0 = time.time()

    for i in range(total_frames):
        t_sec = i / fps
        frame_bgr = renderer.render_frame(t_sec, i)
        proc.stdin.write(frame_bgr.tobytes())

        if i == hero_frame_idx or hero_bgr is None:
            hero_bgr = frame_bgr.copy()

        if i % 120 == 0 or i == total_frames - 1:
            elapsed = time.time() - t0
            cur_fps = (i + 1) / max(0.001, elapsed)
            percent = (i + 1) / total_frames * 100.0
            print(f"[{lang}] Frame {i + 1}/{total_frames} ({percent:.1f}%) — {cur_fps:.1f} fps")
            sys.stdout.flush()

    proc.stdin.close()
    proc.wait()

    # Save hero thumbnail capture
    if hero_capture_path and hero_bgr is not None:
        os.makedirs(os.path.dirname(hero_capture_path), exist_ok=True)
        cv2.imwrite(hero_capture_path, hero_bgr)
        print(f"[{lang}] Hero thumbnail saved: {hero_capture_path}")

    # Mux audio
    if audio_wav and os.path.exists(audio_wav):
        print(f"[{lang}] Muxing cinematic 44.1 kHz stereo audio into final MP4...")
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
            print(f"[!] Warning: Audio muxing error: {res.stderr.decode('utf-8', errors='ignore')}")
            if os.path.exists(output_mp4):
                os.remove(output_mp4)
            os.rename(temp_video, output_mp4)
    else:
        if os.path.exists(temp_video):
            if os.path.exists(output_mp4):
                os.remove(output_mp4)
            os.rename(temp_video, output_mp4)

    print(f"[{lang}] Successfully rendered: {output_mp4}")
    return output_mp4


if __name__ == "__main__":
    test_out = "output/test_elastica_render.mp4"
    render_elastica_video(test_out, lang="ES")
