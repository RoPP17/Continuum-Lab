"""
Continuum Lab - Master 9:16 UHD 60 FPS Visual Video Renderer for Supersonic Shock Diamonds
Module: 01 Mecanica de Fluidos / 09 Diamantes de Choque y Discos de Mach
File: src/visualization/render_shock_diamonds_video.py

Renders 1080x1920 (9:16 Vertical UHD @ 60 FPS) cinematic animations:
  - Deep Aerospace Void (#030712 / #050B1A) with telemetry grid
  - Detailed de Laval Rocket Nozzle Bell with glowing combustion throat
  - 2D Supersonic Jet Plume with Schlieren refractive density gradients
  - Multi-stage Incandescent Shock Diamond Bloom (Prandtl-Meyer fans + Oblique Shocks)
  - Blinding Mach Disk normal shock hotspots with radical reignition (T > 2,850 K)
  - 1000+ Supersonic Lagrangian velocity streak tracer particles
  - Dual Glassmorphic Cyber HUD cards (Chamber Telemetry & Shock Dynamics)
  - Mobile safe-zone compliant kinetic typography in Spanish (ES) and English (EN)
  - 16.0s seamless infinite loop architecture
"""

import os
import sys
import time
import math
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
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

from src.physics.shock_diamonds_sim import ShockDiamondsSim


class MasterShockDiamondsRenderer:
    """
    Master 9:16 60 FPS Visual Renderer for Supersonic Shock Diamonds & Mach Disks.
    """

    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 60, lang: str = "ES"):
        self.width = width
        self.height = height
        self.fps = fps
        self.lang = lang.upper()

        self.sim = ShockDiamondsSim()
        self._load_fonts()

        # Jet Geometry on Canvas
        self.cx = self.width / 2.0
        self.nozzle_y = 380.0       # Top nozzle exit position
        self.jet_length = 980.0     # Pixels down the canvas
        self.r_exit_px = 110.0      # Nominal exit radius in pixels

        # Pre-seed Lagrangian tracer particles
        rng = np.random.default_rng(2026)
        self.n_particles = 900
        self.p_y = rng.uniform(self.nozzle_y, self.nozzle_y + self.jet_length, self.n_particles)
        self.p_eta = rng.uniform(-0.95, 0.95, self.n_particles)
        self.p_spd = rng.uniform(18.0, 36.0, self.n_particles)
        self.p_sz = rng.choice([1, 2, 3], size=self.n_particles, p=[0.6, 0.3, 0.1])
        self.p_alpha = rng.uniform(0.3, 0.95, self.n_particles)

        # Background starry/grid telemetry particles
        self.bg_dots = []
        for _ in range(80):
            bx = float(rng.uniform(30, self.width - 30))
            by = float(rng.uniform(50, self.height - 50))
            self.bg_dots.append((bx, by, float(rng.uniform(0.1, 0.4))))

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
        self.f_brand_title = try_font("C:/Windows/Fonts/segoeuib.ttf", 20)
        self.f_card_hdr = try_font("C:/Windows/Fonts/segoeuib.ttf", 15)
        self.f_card_meta = try_font("C:/Windows/Fonts/consolab.ttf", 13)
        self.f_hud_lbl = try_font("C:/Windows/Fonts/segoeuib.ttf", 12)
        self.f_hud_val = try_font("C:/Windows/Fonts/consolab.ttf", 18)
        self.f_badge_tag = try_font("C:/Windows/Fonts/consolab.ttf", 12)

    def _draw_background_environment(self, img_bgr: np.ndarray, t: float):
        """Draws deep space aerospace gradient and subtle telemetry grid."""
        y_indices = np.linspace(0, 1, self.height)
        # Deep space dark slate: RGB(3, 7, 18) to (5, 14, 32)
        b_col = (18 + 14 * y_indices).astype(np.uint8)
        g_col = (7 + 7 * y_indices).astype(np.uint8)
        r_col = (3 + 2 * y_indices).astype(np.uint8)

        img_bgr[:, :, 0] = b_col[:, None]
        img_bgr[:, :, 1] = g_col[:, None]
        img_bgr[:, :, 2] = r_col[:, None]

        # Subtle engineering grid lines
        grid_alpha = 0.08
        for gx in range(60, self.width, 120):
            cv2.line(img_bgr, (gx, 0), (gx, self.height), (40, 50, 60), 1, cv2.LINE_AA)
        for gy in range(80, self.height, 120):
            cv2.line(img_bgr, (0, gy), (self.width, gy), (40, 50, 60), 1, cv2.LINE_AA)

        # Starry dust
        for bx, by, a in self.bg_dots:
            val = int(255 * a)
            cv2.circle(img_bgr, (int(bx), int(by)), 1, (val, val, val), -1)

    def _draw_rocket_nozzle(self, img_bgr: np.ndarray, st: Dict[str, Any]):
        """Renders the de Laval rocket nozzle bell at the top of the canvas."""
        cx = self.cx
        y_exit = self.nozzle_y
        y_throat = y_exit - 170.0
        r_throat = 42.0
        r_exit = self.r_exit_px

        # Outer bell contours (left and right)
        pts_left = [
            (int(cx - r_throat - 35), int(y_throat - 60)),
            (int(cx - r_throat), int(y_throat)),
            (int(cx - r_throat - 20), int(y_throat + 60)),
            (int(cx - r_exit - 12), int(y_exit)),
            (int(cx - r_exit), int(y_exit)),
            (int(cx - r_throat + 10), int(y_throat + 50)),
            (int(cx - r_throat), int(y_throat)),
            (int(cx - r_throat - 35), int(y_throat - 60)),
        ]
        pts_right = [
            (int(cx + r_throat + 35), int(y_throat - 60)),
            (int(cx + r_throat), int(y_throat)),
            (int(cx + r_throat + 20), int(y_throat + 60)),
            (int(cx + r_exit + 12), int(y_exit)),
            (int(cx + r_exit), int(y_exit)),
            (int(cx + r_throat - 10), int(y_throat + 50)),
            (int(cx + r_throat), int(y_throat)),
            (int(cx + r_throat + 35), int(y_throat - 60)),
        ]

        # Draw nozzle walls with metallic gradient
        cv2.fillPoly(img_bgr, [np.array(pts_left, dtype=np.int32)], (60, 65, 75))
        cv2.fillPoly(img_bgr, [np.array(pts_right, dtype=np.int32)], (60, 65, 75))
        cv2.polylines(img_bgr, [np.array(pts_left, dtype=np.int32)], True, (130, 140, 155), 2, cv2.LINE_AA)
        cv2.polylines(img_bgr, [np.array(pts_right, dtype=np.int32)], True, (130, 140, 155), 2, cv2.LINE_AA)

        # Regenerative cooling channels lines
        for offset in [10, 22, 34]:
            cv2.line(img_bgr, (int(cx - r_exit + offset), int(y_exit - 10)), (int(cx - r_throat + offset // 2), int(y_throat + 30)), (90, 100, 115), 1, cv2.LINE_AA)
            cv2.line(img_bgr, (int(cx + r_exit - offset), int(y_exit - 10)), (int(cx + r_throat - offset // 2), int(y_throat + 30)), (90, 100, 115), 1, cv2.LINE_AA)

        # Glowing combustion chamber throat (super hot orange-yellow core)
        throat_glow = np.zeros_like(img_bgr)
        cv2.ellipse(throat_glow, (int(cx), int(y_throat)), (int(r_throat * 1.5), 35), 0, 0, 360, (50, 180, 255), -1)
        cv2.ellipse(throat_glow, (int(cx), int(y_throat)), (int(r_throat * 0.8), 20), 0, 0, 360, (200, 240, 255), -1)
        throat_glow = cv2.GaussianBlur(throat_glow, (31, 31), 0)
        cv2.add(img_bgr, throat_glow, dst=img_bgr)

        # Nozzle Exit Lip Ring
        cv2.ellipse(img_bgr, (int(cx), int(y_exit)), (int(r_exit), 14), 0, 0, 360, (180, 195, 215), 3, cv2.LINE_AA)

    def _draw_supersonic_jet_plume(self, img_bgr: np.ndarray, t: float, st: Dict[str, Any]):
        """Renders the supersonic jet plume, shock diamonds, expansion fans, and Mach disks."""
        cx = self.cx
        y_exit = self.nozzle_y
        r_exit = self.r_exit_px
        rp = st["rp"]

        # Number of diamond cells
        n_cells = 4
        # Pixel length of diamond cells
        cell_len_px = 220.0 * math.sqrt(max(0.6, rp / 4.0))

        # Dynamic overlay for additive blending (blooms and glow)
        glow_layer = np.zeros_like(img_bgr)

        # 1. Jet Plume Base Core Gradient (Blue/Cyan supersonic stream)
        # Compute jet boundary envelope R_jet(y) down the canvas
        y_pts = np.linspace(y_exit, y_exit + self.jet_length, 120)
        left_poly = []
        right_poly = []

        for y in y_pts:
            dy = y - y_exit
            # Expansion ratio breathing
            expansion = (rp - 1.0) * 0.22 * math.exp(-0.0018 * dy) * math.sin(2.0 * math.pi * dy / cell_len_px - math.pi / 2.0)
            r_cur = r_exit * (1.0 + expansion) + 0.08 * dy  # Turbulent shear expansion
            left_poly.append((int(cx - r_cur), int(y)))
            right_poly.append((int(cx + r_cur), int(y)))

        # Plume polygon
        full_plume = left_poly + right_poly[::-1]
        plume_mask = np.zeros(img_bgr.shape[:2], dtype=np.uint8)
        cv2.fillPoly(plume_mask, [np.array(full_plume, dtype=np.int32)], 255)

        # Fill plume with aerodynamic supersonic gradient: Cyan/Deep Blue (#00F0FF -> #0A2540)
        for i, y in enumerate(y_pts[:-1]):
            y1 = int(y)
            y2 = int(y_pts[i + 1])
            if y2 > y1:
                prog = i / len(y_pts)
                # Color transitions from bright cyan at nozzle to deep sapphire down the jet
                b = int(220 * (1.0 - 0.6 * prog))
                g = int(180 * (1.0 - 0.75 * prog))
                r = int(50 * (1.0 - 0.8 * prog))
                cv2.rectangle(glow_layer, (0, y1), (self.width, y2), (b, g, r), -1)

        # Mask glow layer to the plume boundary
        glow_layer = cv2.bitwise_and(glow_layer, glow_layer, mask=plume_mask)
        glow_layer = cv2.GaussianBlur(glow_layer, (45, 45), 0)
        cv2.addWeighted(img_bgr, 1.0, glow_layer, 0.45, 0, dst=img_bgr)

        # 2. Draw Prandtl-Meyer Expansion Fans at Nozzle Lips
        # Expanding rays from left and right nozzle lips
        for sign in [-1, 1]:
            lip_x = int(cx + sign * r_exit)
            lip_y = int(y_exit)
            for angle_deg in np.linspace(15, 45, 7):
                rad = math.radians(angle_deg)
                dx = int(sign * 180 * math.sin(rad))
                dy = int(180 * math.cos(rad))
                cv2.line(img_bgr, (lip_x, lip_y), (lip_x + dx, lip_y + dy), (255, 230, 100), 1, cv2.LINE_AA)

        # 3. Draw Shock Diamond Cells (Criss-crossing oblique shock lines)
        shock_layer = np.zeros_like(img_bgr)
        for n in range(n_cells):
            y_top = y_exit + n * cell_len_px
            y_mid = y_top + cell_len_px * 0.50
            y_bot = y_top + cell_len_px

            if y_bot > y_exit + self.jet_length + 50:
                continue

            r_node = r_exit * (1.0 + 0.25 * math.exp(-0.4 * n))

            # Diamond vertices
            p_top = (int(cx), int(y_top))
            p_left = (int(cx - r_node), int(y_mid))
            p_right = (int(cx + r_node), int(y_mid))
            p_bot = (int(cx), int(y_bot))

            cell_intensity = math.exp(-0.40 * n)
            col_shock = (
                int(255 * cell_intensity),
                int(220 * cell_intensity),
                int(120 * cell_intensity)
            )

            # Oblique shock rays
            cv2.line(shock_layer, p_top, p_left, col_shock, 2, cv2.LINE_AA)
            cv2.line(shock_layer, p_top, p_right, col_shock, 2, cv2.LINE_AA)
            cv2.line(shock_layer, p_left, p_bot, col_shock, 2, cv2.LINE_AA)
            cv2.line(shock_layer, p_right, p_bot, col_shock, 2, cv2.LINE_AA)

            # Central Mach Reflection: The Normal Shock Disk!
            # Form a horizontal glowing incandescent disk at y_mid
            disk_r = int(st["mach_disk_radius"] * 250.0 * (1.0 - 0.25 * n))
            disk_r = max(8, min(disk_r, 48))
            y_disk = int(y_mid)

            # Horizontal normal shock line
            cv2.line(shock_layer, (int(cx - disk_r), y_disk), (int(cx + disk_r), y_disk), (255, 255, 255), 4, cv2.LINE_AA)

            # Incandescent Radicals Reignition Bloom (Golden-Orange-White Fire)
            flare = np.zeros_like(img_bgr)
            cv2.circle(flare, (int(cx), y_disk), int(disk_r * 2.2), (40, 160, 255), -1)  # Orange aura
            cv2.circle(flare, (int(cx), y_disk), int(disk_r * 1.3), (120, 230, 255), -1) # Yellow core
            cv2.circle(flare, (int(cx), y_disk), int(disk_r * 0.7), (255, 255, 255), -1) # White hot singularity
            flare = cv2.GaussianBlur(flare, (35, 35), 0)
            cv2.add(shock_layer, flare, dst=shock_layer)

            # Shock diamond annotation on first cell
            if n == 0:
                cv2.putText(
                    shock_layer,
                    f"Mach Disk [M < 1.0, T > {int(st['T_mach_disk_core']):,} K]",
                    (int(cx + disk_r + 25), y_disk + 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.48,
                    (200, 240, 255),
                    1,
                    cv2.LINE_AA
                )
                cv2.line(shock_layer, (int(cx + disk_r + 5), y_disk), (int(cx + disk_r + 20), y_disk), (200, 240, 255), 1, cv2.LINE_AA)

        # Merge shock layer with bloom
        cv2.add(img_bgr, shock_layer, dst=img_bgr)

    def _update_and_draw_particles(self, img_bgr: np.ndarray, dt: float, st: Dict[str, Any]):
        """Animates 900+ supersonic Lagrangian tracer particles streaming down the plume."""
        cx = self.cx
        y_exit = self.nozzle_y
        r_exit = self.r_exit_px
        cell_len_px = 220.0 * math.sqrt(max(0.6, st["rp"] / 4.0))

        # Update particle positions
        self.p_y += self.p_spd
        # Reset particles that exit the bottom
        reset_mask = self.p_y > (y_exit + self.jet_length)
        self.p_y[reset_mask] = y_exit + np.random.uniform(0.0, 15.0, np.sum(reset_mask))

        # Render particles with velocity streaks
        for i in range(self.n_particles):
            y = self.p_y[i]
            dy = y - y_exit
            expansion = (st["rp"] - 1.0) * 0.22 * math.exp(-0.0018 * dy) * math.sin(2.0 * math.pi * dy / cell_len_px - math.pi / 2.0)
            r_cur = r_exit * (1.0 + expansion) + 0.08 * dy

            x = cx + self.p_eta[i] * r_cur
            streak_len = self.p_spd[i] * 0.95
            y_tail = y - streak_len

            # Particle color: hot white near axis, bright cyan in supersonic stream
            dist_center = abs(self.p_eta[i])
            if dist_center < 0.25:
                col = (255, 255, 255)
            elif dist_center < 0.65:
                col = (255, 230, 100)
            else:
                col = (220, 150, 40)

            alpha = self.p_alpha[i]
            # Draw streak
            cv2.line(img_bgr, (int(x), int(y_tail)), (int(x), int(y)), col, self.p_sz[i], cv2.LINE_AA)

    def _draw_hud_cards(self, pil_draw: ImageDraw.ImageDraw, st: Dict[str, Any]):
        """Renders dual glassmorphic cyber HUD telemetry cards."""
        # Top branding header (Safe Zone Y: 140 - 220)
        brand_text = "CONTINUUM LAB // FLUID DYNAMICS"
        pil_draw.text((self.cx, 150), brand_text, fill=(0, 240, 255), font=self.f_brand_title, anchor="mt")

        module_tag = "01 MECÁNICA DE FLUIDOS • ENTREGA #25: DIAMANTES DE CHOQUE & DISCO DE MACH" if self.lang == "ES" else "01 FLUID MECHANICS • ISSUE #25: SHOCK DIAMONDS & MACH DISKS"
        pil_draw.text((self.cx, 185), module_tag, fill=(180, 200, 220), font=self.f_card_meta, anchor="mt")

        # Telemetry Card Left: Rocket Chamber & Flow Properties (X: 50 to 450, Y: 230 to 350)
        card_l_x1, card_l_y1, card_l_x2, card_l_y2 = 50, 225, 470, 350
        pil_draw.rounded_rectangle([card_l_x1, card_l_y1, card_l_x2, card_l_y2], radius=12, fill=(11, 19, 43, 210), outline=(0, 240, 255), width=2)
        pil_draw.text((card_l_x1 + 18, card_l_y1 + 12), "CHAMBER TELEMETRY" if self.lang == "EN" else "TELEMETRÍA DE CÁMARA", fill=(0, 240, 255), font=self.f_card_hdr)
        pil_draw.text((card_l_x1 + 18, card_l_y1 + 38), f"p0: {st['p0']/1e6:.2f} MPa  |  T0: {int(st['T0']):,} K", fill=(255, 255, 255), font=self.f_card_meta)
        pil_draw.text((card_l_x1 + 18, card_l_y1 + 64), f"NPR (p0/pa): {st['NPR']:.1f}  |  Exit Mach: {st['M_exit']:.2f}", fill=(200, 230, 255), font=self.f_hud_val)
        pil_draw.text((card_l_x1 + 18, card_l_y1 + 96), f"pe / pa: {st['rp']:.2f} [Underexpanded Jet]", fill=(255, 200, 80), font=self.f_card_meta)

        # Telemetry Card Right: Shock Wave Dynamics & Mach Disk (X: 610 to 1030, Y: 230 to 350)
        card_r_x1, card_r_y1, card_r_x2, card_r_y2 = 610, 225, 1030, 350
        pil_draw.rounded_rectangle([card_r_x1, card_r_y1, card_r_x2, card_r_y2], radius=12, fill=(11, 19, 43, 210), outline=(255, 180, 0), width=2)
        pil_draw.text((card_r_x1 + 18, card_r_y1 + 12), "SHOCK DYNAMICS" if self.lang == "EN" else "DINÁMICA DE CHOQUE", fill=(255, 200, 0), font=self.f_card_hdr)
        pil_draw.text((card_r_x1 + 18, card_r_y1 + 38), f"Diamond Spacing L_d: {st['L_diamond']:.2f} m", fill=(255, 255, 255), font=self.f_card_meta)
        pil_draw.text((card_r_x1 + 18, card_r_y1 + 64), f"Shock Angle beta: {st['beta_deg']:.1f}° | Defl: {st['theta_deg']:.1f}°", fill=(255, 220, 150), font=self.f_hud_val)
        pil_draw.text((card_r_x1 + 18, card_r_y1 + 96), f"Mach Disk Core T: {int(st['T_mach_disk_core']):,} K [Plasma Flash]", fill=(255, 80, 80), font=self.f_card_meta)

    def _draw_subtitles_and_hooks(self, pil_draw: ImageDraw.ImageDraw, t: float):
        """Draws kinetic subtitles and viral hook in the mobile safe zone."""
        # Top Hook (Y: 70 - 130)
        if self.lang == "ES":
            hook_line1 = "¿POR QUÉ EL ESCAPE DE UN COHETE"
            hook_line2 = "FORMA DIAMANTES DE FUEGO INCANDESCENTES?"
        else:
            hook_line1 = "WHY ROCKET EXHAUSTS FORM"
            hook_line2 = "GLOWING INCANDESCENT SHOCK DIAMONDS"

        pil_draw.text((self.cx, 75), hook_line1, fill=(255, 255, 255), font=self.f_hero_hook, anchor="mt")
        pil_draw.text((self.cx, 112), hook_line2, fill=(0, 240, 255), font=self.f_hero_hook, anchor="mt")

        # Lower Educational Explanations (Y: 1480 - 1720, Safe from TikTok/Reels UI)
        if t < 4.0:
            if self.lang == "ES":
                sub1 = "La tobera de Laval expande el gas de combustión a régimen supersónico (Mach > 2.4)."
                sub2 = "Al salir al aire libre, la presión del chorro supera con creces la presión atmosférica (pe > pa)."
            else:
                sub1 = "The de Laval nozzle accelerates combustion gas to supersonic speeds (Mach > 2.4)."
                sub2 = "At the exit, the jet core pressure drastically exceeds atmospheric pressure (pe > pa)."
        elif t < 8.5:
            if self.lang == "ES":
                sub1 = "El chorro subexpandido genera abanicos de expansión de Prandtl-Meyer en el labio."
                sub2 = "La frontera a presión constante refleja las ondas como ondas de choque oblicuas convergentes."
            else:
                sub1 = "The underexpanded jet triggers Prandtl-Meyer expansion fans at the nozzle lip."
                sub2 = "The constant-pressure boundary reflects these waves as converging oblique shocks."
        elif t < 12.5:
            if self.lang == "ES":
                sub1 = "Al colisionar en el eje, el choque regular es imposible: ¡se forma el DISCO DE MACH!"
                sub2 = "El choque normal frena el flujo a subsónico, disparando la temperatura por encima de 2,850 K."
            else:
                sub1 = "Crossing at the axis exceeds regular reflection limits: a normal MACH DISK forms!"
                sub2 = "The normal shock drops flow to subsonic, spiking temperature past 2,850 K."
        else:
            if self.lang == "ES":
                sub1 = "El flujo se re-expande en una cadena periódica de diamantes hasta disiparse por mezcla turbulenta."
                sub2 = "¡Un espectáculo gobernado al 100% por las leyes exactas de Navier-Stokes y Euler!"
            else:
                sub1 = "The flow periodically re-expands forming a diamond chain before viscous mixing decay."
                sub2 = "An iconic aerospace spectacle governed 100% by compressible Navier-Stokes & Euler!"

        # Subtitle glass card (Y: 1540 to 1690)
        box_y1, box_y2 = 1530, 1690
        pil_draw.rounded_rectangle([70, box_y1, self.width - 70, box_y2], radius=14, fill=(11, 19, 43, 220), outline=(0, 240, 255), width=2)
        pil_draw.text((self.cx, box_y1 + 25), sub1, fill=(255, 255, 255), font=self.f_sub_hook, anchor="mt")
        pil_draw.text((self.cx, box_y1 + 80), sub2, fill=(255, 215, 0), font=self.f_sub_hook, anchor="mt")

        # Bottom Safe Zone watermark (Y: 1730 - 1760)
        pil_draw.text((self.cx, 1740), "CONTINUUM LAB • @continuumlab_ • OPEN SCIENCE", fill=(120, 140, 165), font=self.f_card_meta, anchor="mt")

    def render_frame(self, t: float) -> np.ndarray:
        """Renders a single master 1080x1920 frame at time t."""
        st = self.sim.get_dynamic_state(t)
        frame_bgr = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # 1. Background
        self._draw_background_environment(frame_bgr, t)

        # 2. Supersonic Plume & Shock Diamonds
        self._draw_supersonic_jet_plume(frame_bgr, t, st)

        # 3. Lagrangian Particles
        self._update_and_draw_particles(frame_bgr, 1.0 / self.fps, st)

        # 4. Rocket Nozzle Hardware
        self._draw_rocket_nozzle(frame_bgr, st)

        # 5. PIL Overlay for HUD and Typography
        img_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        pil_draw = ImageDraw.Draw(pil_img, "RGBA")

        self._draw_hud_cards(pil_draw, st)
        self._draw_subtitles_and_hooks(pil_draw, t)

        final_rgb = np.array(pil_img)
        return cv2.cvtColor(final_rgb, cv2.COLOR_RGB2BGR)


def render_shock_diamonds_video(
    output_mp4: str,
    audio_wav: Optional[str] = None,
    duration: float = 16.0,
    fps: int = 60,
    lang: str = "ES",
    hero_capture_path: Optional[str] = None
) -> str:
    """
    Renders the complete 16.0s 60 FPS video and multiplexes with audio.
    """
    os.makedirs(os.path.dirname(output_mp4), exist_ok=True)
    total_frames = int(duration * fps)

    renderer = MasterShockDiamondsRenderer(width=1080, height=1920, fps=fps, lang=lang)

    temp_video = output_mp4.replace(".mp4", "_temp_raw.mp4")

    # Start FFmpeg subprocess to pipe raw video frames directly
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{renderer.width}x{renderer.height}",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        temp_video
    ]

    print(f"[*] Lanzando encoder FFmpeg para [{lang}] (Frames totales: {total_frames})...")
    pipe = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    t_start = time.time()
    for frame_idx in range(total_frames):
        t_cur = frame_idx / float(fps)
        frame_bgr = renderer.render_frame(t_cur)

        # Save hero frame at peak shock diamond illumination (t = 8.0s)
        if hero_capture_path and frame_idx == int(8.0 * fps):
            os.makedirs(os.path.dirname(hero_capture_path), exist_ok=True)
            cv2.imwrite(hero_capture_path, frame_bgr)
            print(f"[OK] Hero capture guardado: {hero_capture_path}")

        pipe.stdin.write(frame_bgr.tobytes())

        if (frame_idx + 1) % 120 == 0 or frame_idx == total_frames - 1:
            elapsed = time.time() - t_start
            fps_render = (frame_idx + 1) / max(0.1, elapsed)
            print(f"    - Renderizados {frame_idx + 1}/{total_frames} frames ({fps_render:.1f} FPS) [{lang}]")

    pipe.stdin.close()
    pipe.wait()

    # Multiplex with audio if provided
    if audio_wav and os.path.exists(audio_wav):
        print(f"[*] Multiplexando audio estéreo 44.1 kHz con FFmpeg...")
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
        subprocess.run(mux_cmd, check=True)
        if os.path.exists(temp_video):
            os.remove(temp_video)
    else:
        if os.path.exists(temp_video):
            if os.path.exists(output_mp4):
                os.remove(output_mp4)
            os.rename(temp_video, output_mp4)

    print(f"[OK] Video final masterizado con éxito: {output_mp4}")
    return output_mp4


if __name__ == "__main__":
    test_out = r"C:\Users\andre\OneDrive\Desktop\Continuum Lab\RENDERS\25 Diamantes de Choque y Discos de Mach Aerodinamicos\videos\Diamantes Choque y Discos de Mach ES.mp4"
    test_hero = r"C:\Users\andre\OneDrive\Desktop\Continuum Lab\RENDERS\25 Diamantes de Choque y Discos de Mach Aerodinamicos\extra\capturas\shock_diamonds_hero_es.png"
    render_shock_diamonds_video(test_out, hero_capture_path=test_hero, duration=2.0, fps=30, lang="ES")
