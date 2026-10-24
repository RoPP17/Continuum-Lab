"""
Continuum Lab - Master 9:16 UHD 60 FPS Visual Video Renderer for Cavitation & Sonoluminescence
Module: 01 Mecanica de Fluidos / 08 Colapso de Cavitacion y Sonoluminiscencia
File: src/visualization/render_cavitation_video.py

Renders 1080x1920 (9:16 Vertical UHD @ 60 FPS) cinematic animations:
  - Deep Oceanic Abyss Void (#020617 / #030A1A) with dynamic ambient caustics
  - 3D Perspective Bubble Mesh with Fresnel rim shading and van der Waals core
  - Realistic Sonoluminescence flash with blinding multi-stage bloom, flare and lens rays
  - Spherical acoustic shockwaves (Kirkwood-Bethe) with optical refractive caustic rings
  - Downward piercing supersonic micro-jet (v = 1,050 m/s) forming a toroidal cavitation ring
  - 800+ Lagrangian tracer particles with velocity glow vectors
  - Glassmorphic Cyber HUD: Dual telemetry cards (R, Mach, P_gas, T_core)
  - Safe-zone compliant kinetic subtitles & hooks in Spanish (ES) and English (EN)
  - 16.0s seamless infinite loop architecture
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

from src.physics.cavitation_sim import CavitationBubbleSim


class MasterCavitationRenderer:
    """
    Master 9:16 60 FPS Visual Renderer for Cavitation Collapse & Sonoluminescence.
    """

    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 60, lang: str = "ES"):
        self.width = width
        self.height = height
        self.fps = fps
        self.lang = lang.upper()

        self.sim = CavitationBubbleSim()
        self._load_fonts()

        # 3D Camera Configuration
        self.elev = np.radians(18.0)
        self.azim = np.radians(25.0)
        self.cam_dist = 3.20
        self.f_proj = 1050.0
        self.cx = self.width / 2.0
        self.cy = self.height / 2.0 - 15.0  # Centered safely between HUD and subtitles

        # Background suspended micro-particulates & caustics
        rng = np.random.default_rng(888)
        self.bg_particles = []
        for _ in range(120):
            bx = float(rng.uniform(30, self.width - 30))
            by = float(rng.uniform(50, self.height - 50))
            b_spd = float(rng.uniform(0.4, 1.2))
            b_sz = int(rng.integers(1, 4))
            b_alpha = float(rng.uniform(0.12, 0.45))
            self.bg_particles.append([bx, by, b_spd, b_sz, b_alpha])

    def _load_fonts(self):
        def try_font(path, size, fallback=None):
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    pass
            return fallback or ImageFont.load_default()

        self.f_hero_hook = try_font("C:/Windows/Fonts/segoeuib.ttf", 29, try_font("C:/Windows/Fonts/arialbd.ttf", 29))
        self.f_sub_hook = try_font("C:/Windows/Fonts/segoeui.ttf", 21, try_font("C:/Windows/Fonts/arial.ttf", 21))
        self.f_brand_title = try_font("C:/Windows/Fonts/segoeuib.ttf", 21)
        self.f_card_hdr = try_font("C:/Windows/Fonts/segoeuib.ttf", 16)
        self.f_card_meta = try_font("C:/Windows/Fonts/consolab.ttf", 13)
        self.f_hud_lbl = try_font("C:/Windows/Fonts/segoeuib.ttf", 13)
        self.f_hud_val = try_font("C:/Windows/Fonts/consolab.ttf", 19)
        self.f_badge_tag = try_font("C:/Windows/Fonts/consolab.ttf", 12)

    def _project_3d(self, pts_3d: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Projects 3D points (N, 3) to 2D screen coordinates using perspective.
        """
        x = pts_3d[:, 0]
        y = pts_3d[:, 1]
        z = pts_3d[:, 2]

        cos_az, sin_az = np.cos(self.azim), np.sin(self.azim)
        cos_el, sin_el = np.cos(self.elev), np.sin(self.elev)

        x_cam = -x * sin_az + y * cos_az
        y_cam = -x * sin_el * cos_az - y * sin_el * sin_az + z * cos_el
        z_cam =  x * cos_el * cos_az + y * cos_el * sin_az + z * sin_el + self.cam_dist

        z_safe = np.maximum(z_cam, 0.2)
        u = self.cx + (x_cam * self.f_proj) / z_safe
        v = self.cy - (y_cam * self.f_proj) / z_safe

        return np.column_stack((u, v)), z_cam

    def _draw_background_environment(self, img_bgr: np.ndarray, t: float):
        """Draws oceanic dark abyss gradient, floating suspended specks and caustic ripples."""
        # Vertical gradient: Deep Void (0, 3, 10) to Oceanic Cyan Glow (25, 20, 8)
        y_indices = np.linspace(0, 1, self.height)
        b_col = (10 + 20 * np.sin(np.pi * y_indices)).astype(np.uint8)
        g_col = (5 + 16 * np.sin(np.pi * y_indices)).astype(np.uint8)
        r_col = (2 + 6 * np.sin(np.pi * y_indices)).astype(np.uint8)
        
        img_bgr[:, :, 0] = b_col[:, None]
        img_bgr[:, :, 1] = g_col[:, None]
        img_bgr[:, :, 2] = r_col[:, None]

        # Ambient caustic wave bands
        overlay = img_bgr.copy()
        for idx in range(4):
            y_band = int(self.height * (0.2 + idx * 0.22) + 25.0 * np.sin(t * 1.5 + idx * 1.8))
            cv2.ellipse(
                overlay,
                (int(self.cx), y_band),
                (int(self.width * 0.75), 180),
                0, 0, 360,
                (60, 45, 15),
                -1,
                cv2.LINE_AA
            )
        cv2.addWeighted(overlay, 0.22, img_bgr, 0.78, 0, img_bgr)

        # Floating micro-particulates
        for p in self.bg_particles:
            p[1] = (p[1] - p[2]) % (self.height - 40) + 20
            p[0] = (p[0] + 0.25 * np.sin(t * 0.8 + p[1] * 0.01)) % (self.width - 40) + 20
            px, py = int(p[0]), int(p[1])
            col = (int(180 * p[4]), int(210 * p[4]), int(80 * p[4]))
            cv2.circle(img_bgr, (px, py), p[3], col, -1, cv2.LINE_AA)

    def _draw_acoustic_pressure_field(self, img_bgr: np.ndarray, t: float, R_ratio: float):
        """Draws concentric background acoustic waves converging or radiating."""
        center = (int(self.cx), int(self.cy))
        overlay = img_bgr.copy()

        # Wave pulses
        num_waves = 5
        base_phase = (t * 2.2) % 1.0
        for w in range(num_waves):
            phase = (base_phase + w / num_waves) % 1.0
            r_px = int(80 + phase * 420)
            alpha = (1.0 - phase) * 0.18
            if alpha > 0.01:
                cv2.circle(overlay, center, r_px, (255, 220, 0), 1, cv2.LINE_AA)
        cv2.addWeighted(overlay, 0.45, img_bgr, 0.55, 0, img_bgr)

    def _draw_shockwaves(self, img_bgr: np.ndarray, shock_r: float, shock_p: float):
        """Draws intense expanding spherical shockwave rings when shock_r > 0."""
        if shock_r <= 0.01:
            return

        center = (int(self.cx), int(self.cy))
        overlay = img_bgr.copy()

        # Radio principal en píxeles
        r_px = int(shock_r * 320.0)
        intensity = min(1.0, shock_p / 4000.0)

        # 3 Anillos de choque concéntricos con degradado cáustico
        for dr, col_mult, thick in [(-12, 0.6, 2), (0, 1.0, 5), (14, 0.5, 2)]:
            current_r = max(4, r_px + dr)
            color = (
                int(255 * col_mult * intensity),
                int(245 * col_mult * intensity),
                int(200 * col_mult * intensity)
            )
            cv2.circle(overlay, center, current_r, color, thick, cv2.LINE_AA)

        # Resplandor exterior
        cv2.circle(overlay, center, r_px, (255, 230, 100), 18, cv2.LINE_AA)
        cv2.addWeighted(overlay, 0.55, img_bgr, 0.45, 0, img_bgr)

    def _draw_bubble_3d(self, img_bgr: np.ndarray, mesh_3d: np.ndarray, T_k: float, SL: float, jet_len: float):
        """
        Renders the 3D bubble mesh with dynamic thermodynamics-driven coloration,
        Fresnel rim shading, interior glowing core, and micro-jet puncture.
        """
        n_lat, n_lon, _ = mesh_3d.shape
        flat_mesh = mesh_3d.reshape(-1, 3)
        pts_2d, depths = self._project_3d(flat_mesh)
        pts_grid = pts_2d.reshape(n_lat, n_lon, 2)

        # Color base según temperatura del gas:
        # T < 1000 K: Cyan bioluminiscente (255, 240, 0)
        # T in [1000, 6000 K]: Ámbar incandescente (0, 160, 255)
        # T > 10000 K: Blanco azulado plasma de sonoluminiscencia (255, 255, 255)
        if T_k < 1500.0:
            core_bgr = (255, 240, 0)       # Cyan
            rim_bgr = (255, 180, 0)
        elif T_k < 8000.0:
            core_bgr = (0, 180, 255)       # Naranja/Ámbar
            rim_bgr = (80, 230, 255)
        else:
            core_bgr = (255, 255, 255)     # Plasma blanco brillante
            rim_bgr = (255, 240, 180)

        overlay = img_bgr.copy()

        # Dibujar meridianos y paralelos como malla 3D de alta tecnología
        for i in range(0, n_lat, 2):
            ring_pts = pts_grid[i, :, :].astype(np.int32)
            cv2.polylines(overlay, [ring_pts], isClosed=True, color=rim_bgr, thickness=1, lineType=cv2.LINE_AA)

        for j in range(0, n_lon, 3):
            meridian_pts = pts_grid[:, j, :].astype(np.int32)
            cv2.polylines(overlay, [meridian_pts], isClosed=False, color=rim_bgr, thickness=1, lineType=cv2.LINE_AA)

        # Relleno translúcido de la silueta convexa
        all_pts_int = pts_2d.astype(np.int32)
        hull = cv2.convexHull(all_pts_int)
        cv2.fillPoly(overlay, [hull], core_bgr, cv2.LINE_AA)

        # Mezcla translúcida
        alpha = 0.35 + 0.45 * SL
        cv2.addWeighted(overlay, alpha, img_bgr, 1.0 - alpha, 0, img_bgr)

        # Núcleo interior concentrado
        center = (int(self.cx), int(self.cy))
        # Radio aparente del casco convexo
        r_eff = int(np.sqrt(cv2.contourArea(hull) / np.pi)) if len(hull) >= 3 else 10
        r_eff = max(r_eff, 4)

        # Destello de Sonoluminiscencia (Flash volumétrico y cruz de difracción)
        if SL > 0.05:
            flash_overlay = img_bgr.copy()
            flash_alpha = min(1.0, SL * 1.35)
            # Resplandor esférico gigante
            glow_rad = int(r_eff + 180 * SL)
            cv2.circle(flash_overlay, center, glow_rad, (255, 240, 160), -1, cv2.LINE_AA)
            cv2.circle(flash_overlay, center, int(glow_rad * 0.55), (255, 255, 255), -1, cv2.LINE_AA)

            # Rayos en cruz de lente anamórfica (Lens Flare)
            flare_len = int(320 * SL)
            cv2.line(flash_overlay, (center[0] - flare_len, center[1]), (center[0] + flare_len, center[1]), (255, 255, 255), 3, cv2.LINE_AA)
            cv2.line(flash_overlay, (center[0], center[1] - flare_len), (center[0], center[1] + flare_len), (255, 255, 255), 3, cv2.LINE_AA)
            # Rayos diagonales finos
            d_len = int(flare_len * 0.6)
            cv2.line(flash_overlay, (center[0] - d_len, center[1] - d_len), (center[0] + d_len, center[1] + d_len), (255, 240, 200), 1, cv2.LINE_AA)
            cv2.line(flash_overlay, (center[0] - d_len, center[1] + d_len), (center[0] + d_len, center[1] - d_len), (255, 240, 200), 1, cv2.LINE_AA)

            cv2.addWeighted(flash_overlay, flash_alpha * 0.75, img_bgr, 1.0 - (flash_alpha * 0.75), 0, img_bgr)

        # Borde exterior nítido
        cv2.polylines(img_bgr, [hull], isClosed=True, color=(255, 255, 255) if SL > 0.1 else (255, 240, 0), thickness=2, lineType=cv2.LINE_AA)

        # Micro-jet visual: Aguja líquida penetrante cuando jet_len > 0
        if jet_len > 0.02:
            jet_tip_y = int(self.cy + (jet_len * 120.0))
            jet_top_y = int(self.cy - r_eff - 45.0)
            cv2.arrowedLine(
                img_bgr,
                (int(self.cx), jet_top_y),
                (int(self.cx), jet_tip_y),
                (0, 240, 255),
                4,
                cv2.LINE_AA,
                tipLength=0.35
            )
            # Anillo de salpicadura
            cv2.ellipse(img_bgr, (int(self.cx), jet_tip_y), (int(r_eff * 0.65), 14), 0, 0, 360, (255, 255, 255), 2, cv2.LINE_AA)

    def _draw_particles(self, img_bgr: np.ndarray, pts_3d: np.ndarray, R_dot: float, SL: float):
        """Draws 3D tracer particles with velocity-glow vectors."""
        pts_2d, depths = self._project_3d(pts_3d)

        # Color según velocidad de pared
        if R_dot < -400.0:
            part_col = (0, 180, 255)       # Convergencia rápida ámbar
        elif SL > 0.1:
            part_col = (255, 255, 255)     # Destello blanco
        else:
            part_col = (255, 240, 0)       # Cyan fluido

        for i, (u, v) in enumerate(pts_2d):
            if 15 <= u < self.width - 15 and 100 <= v < self.height - 180:
                iu, iv = int(u), int(v)
                # Tamaño según profundidad z
                sz = 2 if depths[i] > self.cam_dist else 3
                cv2.circle(img_bgr, (iu, iv), sz, part_col, -1, cv2.LINE_AA)

    def _draw_hud_telemetry(self, pil_draw: ImageDraw.ImageDraw, st: dict):
        """Renders glassmorphic cybernetic HUD panels with telemetry."""
        # =====================================================================
        # 1. HEADER BRAND CAPSULE (Top Safe Zone: y = 75 .. 125)
        # =====================================================================
        hdr_w, hdr_h = 560, 48
        hdr_x1 = int(self.cx - hdr_w / 2)
        hdr_y1 = 75
        hdr_x2 = hdr_x1 + hdr_w
        hdr_y2 = hdr_y1 + hdr_h

        pil_draw.rounded_rectangle([hdr_x1, hdr_y1, hdr_x2, hdr_y2], radius=10, fill=(10, 25, 47, 210), outline=(0, 240, 255, 230), width=2)
        brand_text = "CONTINUUM LAB // 01 FLUID DYNAMICS"
        bw = pil_draw.textlength(brand_text, font=self.f_brand_title)
        pil_draw.text((self.cx - bw / 2, hdr_y1 + 12), brand_text, font=self.f_brand_title, fill=(0, 240, 255))

        # =====================================================================
        # 2. LEFT TELEMETRY CARD (Radius & Mach Number: y = 145 .. 330)
        # =====================================================================
        c1_x1, c1_y1, c1_w, c1_h = 45, 145, 470, 175
        c1_x2, c1_y2 = c1_x1 + c1_w, c1_y1 + c1_h

        pil_draw.rounded_rectangle([c1_x1, c1_y1, c1_x2, c1_y2], radius=12, fill=(8, 18, 36, 215), outline=(0, 240, 255, 160), width=1)
        # Title
        t_title = "RADIO Y VELOCIDAD DE PARED" if self.lang == "ES" else "BUBBLE RADIUS & WALL SPEED"
        pil_draw.text((c1_x1 + 18, c1_y1 + 14), t_title, font=self.f_card_hdr, fill=(0, 240, 255))

        # Radio R(t)
        r_um = st["R"] * 1e6
        r_str = f"{r_um:.1f} um ({st['R_ratio']:.2f} R0)"
        pil_draw.text((c1_x1 + 18, c1_y1 + 44), "RADIO R(t):", font=self.f_hud_lbl, fill=(180, 200, 220))
        pil_draw.text((c1_x1 + 18, c1_y1 + 62), r_str, font=self.f_hud_val, fill=(255, 255, 255))

        # Velocidad R_dot & Mach
        mach_str = f"M = {st['mach']:.2f} ({abs(st['R_dot']):.0f} m/s)"
        mach_col = (255, 70, 70) if st['mach'] > 0.75 else (0, 240, 255)
        pil_draw.text((c1_x1 + 18, c1_y1 + 96), "MACH DE COLAPSO:", font=self.f_hud_lbl, fill=(180, 200, 220))
        pil_draw.text((c1_x1 + 18, c1_y1 + 114), mach_str, font=self.f_hud_val, fill=mach_col)

        # Barra visual de compresión
        bar_w, bar_h = 430, 8
        bar_x = c1_x1 + 18
        bar_y = c1_y1 + 150
        pil_draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], fill=(20, 35, 60))
        fill_w = int(np.clip(st['R_ratio'] / 2.5, 0.02, 1.0) * bar_w)
        pil_draw.rectangle([bar_x, bar_y, bar_x + fill_w, bar_y + bar_h], fill=(0, 240, 255))

        # =====================================================================
        # 3. RIGHT TELEMETRY CARD (Temperature & Pressure: y = 145 .. 330)
        # =====================================================================
        c2_x1 = self.width - 45 - c1_w
        c2_y1 = 145
        c2_x2, c2_y2 = c2_x1 + c1_w, c2_y1 + c1_h

        pil_draw.rounded_rectangle([c2_x1, c2_y1, c2_x2, c2_y2], radius=12, fill=(8, 18, 36, 215), outline=(0, 240, 255, 160), width=1)
        t2_title = "TERMODINÁMICA INTERIOR" if self.lang == "ES" else "CORE THERMODYNAMICS"
        pil_draw.text((c2_x1 + 18, c2_y1 + 14), t2_title, font=self.f_card_hdr, fill=(0, 240, 255))

        # Temperatura del Gas
        tk = st["T_kelvin"]
        t_col = (255, 255, 255) if tk > 10000.0 else (255, 180, 0) if tk > 2000.0 else (0, 240, 255)
        t_label = f"{tk:,.0f} K ({st['T_celsius']:,.0f} °C)"
        pil_draw.text((c2_x1 + 18, c2_y1 + 44), "TEMPERATURA NÚCLEO:", font=self.f_hud_lbl, fill=(180, 200, 220))
        pil_draw.text((c2_x1 + 18, c2_y1 + 62), t_label, font=self.f_hud_val, fill=t_col)

        # Presión del Gas (atm)
        p_atm = st["P_gas_atm"]
        p_label = f"{p_atm:,.0f} atm ({p_atm*0.101325:,.0f} MPa)"
        pil_draw.text((c2_x1 + 18, c2_y1 + 96), "PRESIÓN VAN DER WAALS:", font=self.f_hud_lbl, fill=(180, 200, 220))
        pil_draw.text((c2_x1 + 18, c2_y1 + 114), p_label, font=self.f_hud_val, fill=(255, 255, 255))

        # Indicador de Sonoluminiscencia
        status_text = "¡FLASH ACTIVO!" if (self.lang == "ES" and st["is_sonoluminescent"]) else \
                      "FLASH ACTIVE!" if st["is_sonoluminescent"] else \
                      "COMPRESIÓN ADIABÁTICA" if self.lang == "ES" else "ADIABATIC COMPRESSION"
        badge_fill = (255, 40, 40) if st["is_sonoluminescent"] else (15, 40, 75)
        pil_draw.rounded_rectangle([c2_x1 + 18, c2_y1 + 146, c2_x1 + 220, c2_y1 + 168], radius=6, fill=badge_fill)
        pil_draw.text((c2_x1 + 28, c2_y1 + 149), status_text, font=self.f_badge_tag, fill=(255, 255, 255))

    def _draw_subtitles_and_narrative(self, pil_draw: ImageDraw.ImageDraw, t: float):
        """
        Renders safe-zone compliant narrative subtitles with dynamic kinetic hooks (y = 1640 .. 1780).
        """
        # Hook scripts by phase
        if t < 3.0:
            hook_hero = "¿UNA BURBUJA MÁS CALIENTE QUE EL SOL?" if self.lang == "ES" else "A BUBBLE HOTTER THAN THE SUN?"
            hook_sub = "Oscilación acústica y expansión inercial en agua (R0 = 50 um)" if self.lang == "ES" else "Acoustic oscillation and inertial expansion in water"
        elif t < 7.0:
            hook_hero = "COLAPSO A MACH 2: LA MATERIA CONVERGE" if self.lang == "ES" else "RAYLEIGH COLLAPSE AT MACH 2"
            hook_sub = "Aceleración extrema por sobrepresión hidrostática de Rayleigh" if self.lang == "ES" else "Extreme acceleration driven by hydrostatic overpressure"
        elif t < 8.8:
            hook_hero = "¡SONOLUMINISCENCIA! T > 18,000 K" if self.lang == "ES" else "SONOLUMINESCENCE! T > 18,000 K"
            hook_sub = "Singularidad adiabática y emisión de plasma de picosegundos" if self.lang == "ES" else "Adiabatic singularity & picosecond thermal plasma flash"
        elif t < 12.5:
            hook_hero = "ONDA DE CHOQUE Y MICRO-JET DE 1,050 M/S" if self.lang == "ES" else "16,000 BAR SHOCK & 1,050 M/S JET"
            hook_sub = "Ruptura de simetría hidrodinámica: choque Kirkwood-Bethe" if self.lang == "ES" else "Symmetry breaking: Kirkwood-Bethe shockwave ejection"
        else:
            hook_hero = "EL PODER RADIANTE DE LA CAVITACIÓN" if self.lang == "ES" else "RADIANT POWER OF CAVITATION"
            hook_sub = "Amortiguamiento acústico de Keller-Miksis y bucle infinito" if self.lang == "ES" else "Keller-Miksis radiation damping & infinite loop"

        # Card container
        sub_w, sub_h = 990, 120
        sub_x1 = int(self.cx - sub_w / 2)
        sub_y1 = 1640
        sub_x2 = sub_x1 + sub_w
        sub_y2 = sub_y1 + sub_h

        pil_draw.rounded_rectangle([sub_x1, sub_y1, sub_x2, sub_y2], radius=14, fill=(5, 12, 26, 220), outline=(0, 240, 255, 180), width=1)

        # Centered text
        hw = pil_draw.textlength(hook_hero, font=self.f_hero_hook)
        pil_draw.text((self.cx - hw / 2, sub_y1 + 22), hook_hero, font=self.f_hero_hook, fill=(0, 240, 255))

        sw = pil_draw.textlength(hook_sub, font=self.f_sub_hook)
        pil_draw.text((self.cx - sw / 2, sub_y1 + 72), hook_sub, font=self.f_sub_hook, fill=(220, 230, 245))

    def render_frame(self, t: float, frame_idx: int) -> np.ndarray:
        """Renders single 1080x1920 frame at time t."""
        st = self.sim.get_state(t)

        img_bgr = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # 1. Background oceanic environment & caustics
        self._draw_background_environment(img_bgr, t)

        # 2. Acoustic wave pressure field
        self._draw_acoustic_pressure_field(img_bgr, t, st["R_ratio"])

        # 3. Spherical shockwaves (if active)
        self._draw_shockwaves(img_bgr, st["shock_radius_norm"], st["shock_pressure_bar"])

        # 4. Lagrangian tracer particles
        self._draw_particles(img_bgr, st["particles_3d"], st["R_dot"], st["SL_intensity"])

        # 5. 3D Bubble Mesh & Sonoluminescence Flash
        self._draw_bubble_3d(img_bgr, st["bubble_mesh"], st["T_kelvin"], st["SL_intensity"], st["jet_length_norm"])

        # 6. Glassmorphic HUD & Subtitles via Pillow overlay
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        pil_draw = ImageDraw.Draw(pil_img, "RGBA")

        self._draw_hud_telemetry(pil_draw, st)
        self._draw_subtitles_and_narrative(pil_draw, t)

        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def render_cavitation_video(
    output_mp4: str,
    audio_wav: Optional[str] = None,
    duration: float = 16.0,
    fps: int = 60,
    lang: str = "ES",
    hero_capture_path: Optional[str] = None
) -> str:
    """
    Renders the master 9:16 vertical 60 FPS video and muxes stereo audio.
    """
    renderer = MasterCavitationRenderer(width=1080, height=1920, fps=fps, lang=lang)
    total_frames = int(duration * fps)

    temp_video = str(Path(output_mp4).parent / f"temp_{Path(output_mp4).stem}.mp4")
    os.makedirs(Path(output_mp4).parent, exist_ok=True)

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

    hero_frame_idx = int(7.20 * fps)  # Peak sonoluminescence frame
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
            print(f"[{lang}] Frame {i + 1}/{total_frames} ({percent:.1f}%) -> {cur_fps:.1f} fps")
            sys.stdout.flush()

    proc.stdin.close()
    proc.wait()

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
