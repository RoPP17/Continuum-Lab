"""
Continuum Lab - Scientific 16:9 Poster Generator for Supersonic Shock Diamonds
Module: 01 Mecanica de Fluidos / 09 Diamantes de Choque y Discos de Mach
File: src/visualization/render_shock_diamonds_poster.py

Generates a publication-grade 1920x1080 scientific poster:
  - High-resolution Schlieren jet contour visualization
  - Mathematical equations (Prandtl-Meyer, Oblique Shocks, Rankine-Hugoniot, Mach Disks)
  - Color palette: Deep Space Navy, Aerodynamic Cyan (#00F0FF), Solar Gold (#FFE600)
"""

import os
import math
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

from src.physics.shock_diamonds_sim import ShockDiamondsSim


def render_shock_diamonds_poster(output_path: str, width: int = 1920, height: int = 1080) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sim = ShockDiamondsSim()
    st = sim.get_dynamic_state(8.0)  # Nominal mid-cycle peak state

    img = np.zeros((height, width, 3), dtype=np.uint8)

    # 1. Background gradient (Dark Navy Void)
    y_idx = np.linspace(0, 1, height)
    b_col = (18 + 14 * y_idx).astype(np.uint8)
    g_col = (7 + 7 * y_idx).astype(np.uint8)
    r_col = (3 + 2 * y_idx).astype(np.uint8)
    img[:, :, 0] = b_col[:, None]
    img[:, :, 1] = g_col[:, None]
    img[:, :, 2] = r_col[:, None]

    # Grid lines
    for x in range(0, width, 80):
        cv2.line(img, (x, 0), (x, height), (35, 45, 55), 1, cv2.LINE_AA)
    for y in range(0, height, 80):
        cv2.line(img, (0, y), (width, y), (35, 45, 55), 1, cv2.LINE_AA)

    # 2. Left side: Supersonic Jet Visualizer (horizontal orientation for poster)
    jet_cx = 440
    nozzle_x = 120
    nozzle_r = 95
    jet_length = 740

    # Draw horizontal de Laval nozzle
    pts_nozzle_top = [
        (nozzle_x - 70, jet_cx - nozzle_r - 25),
        (nozzle_x, jet_cx - nozzle_r),
        (nozzle_x, jet_cx - nozzle_r + 15),
        (nozzle_x - 70, jet_cx - nozzle_r - 10),
    ]
    pts_nozzle_bot = [
        (nozzle_x - 70, jet_cx + nozzle_r + 25),
        (nozzle_x, jet_cx + nozzle_r),
        (nozzle_x, jet_cx + nozzle_r - 15),
        (nozzle_x - 70, jet_cx + nozzle_r + 10),
    ]
    cv2.fillPoly(img, [np.array(pts_nozzle_top, dtype=np.int32)], (70, 80, 95))
    cv2.fillPoly(img, [np.array(pts_nozzle_bot, dtype=np.int32)], (70, 80, 95))

    # Jet plume horizontal
    cell_len = 185
    for n in range(4):
        x_left = nozzle_x + n * cell_len
        x_mid = x_left + cell_len // 2
        x_right = x_left + cell_len

        r_node = int(nozzle_r * (1.0 + 0.22 * math.exp(-0.35 * n)))
        col_shock = (255 - 40 * n, 220 - 40 * n, 100)

        # Oblique shock lines
        cv2.line(img, (x_left, jet_cx), (x_mid, jet_cx - r_node), col_shock, 2, cv2.LINE_AA)
        cv2.line(img, (x_left, jet_cx), (x_mid, jet_cx + r_node), col_shock, 2, cv2.LINE_AA)
        cv2.line(img, (x_mid, jet_cx - r_node), (x_right, jet_cx), col_shock, 2, cv2.LINE_AA)
        cv2.line(img, (x_mid, jet_cx + r_node), (x_right, jet_cx), col_shock, 2, cv2.LINE_AA)

        # Normal shock Mach Disk
        disk_r = int(32 * math.exp(-0.4 * n))
        cv2.line(img, (x_mid, jet_cx - disk_r), (x_mid, jet_cx + disk_r), (255, 255, 255), 4, cv2.LINE_AA)

        # Bloom
        flare = np.zeros_like(img)
        cv2.circle(flare, (x_mid, jet_cx), disk_r * 2, (30, 160, 255), -1)
        cv2.circle(flare, (x_mid, jet_cx), int(disk_r * 0.9), (255, 255, 255), -1)
        flare = cv2.GaussianBlur(flare, (35, 35), 0)
        cv2.add(img, flare, dst=img)

    # 3. PIL Overlay for Scientific Typography
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(pil_img, "RGBA")

    def try_font(path, size, fallback=None):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
        return fallback or ImageFont.load_default()

    f_title = try_font("C:/Windows/Fonts/segoeuib.ttf", 36)
    f_sub = try_font("C:/Windows/Fonts/segoeui.ttf", 20)
    f_sec = try_font("C:/Windows/Fonts/segoeuib.ttf", 22)
    f_body = try_font("C:/Windows/Fonts/segoeui.ttf", 16)
    f_eq = try_font("C:/Windows/Fonts/consolab.ttf", 17)
    f_badge = try_font("C:/Windows/Fonts/consolab.ttf", 13)

    # Header
    draw.text((80, 50), "CONTINUUM LAB // FLUID DYNAMICS RESEARCH", fill=(0, 240, 255), font=f_badge)
    draw.text((80, 80), "SUPERSONIC SHOCK DIAMONDS & MACH DISKS", fill=(255, 255, 255), font=f_title)
    draw.text((80, 135), "Compressible Aerodynamics, Method of Characteristics, Oblique Shocks & Extreme Incandescent Reignition", fill=(180, 200, 220), font=f_sub)

    # Right Content Cards (X: 980 to 1840)
    card_x1, card_x2 = 960, 1840

    # Card 1: Prandtl-Meyer Theory
    draw.rounded_rectangle([card_x1, 190, card_x2, 430], radius=12, fill=(11, 19, 43, 220), outline=(0, 240, 255), width=2)
    draw.text((card_x1 + 25, 210), "1. PRANDTL-MEYER EXPANSION & BOUNDARY REFLECTION", fill=(0, 240, 255), font=f_sec)
    eq1 = "nu(M) = sqrt((gamma+1)/(gamma-1)) * atan(...) - atan(sqrt(M^2 - 1))"
    draw.text((card_x1 + 25, 250), eq1, fill=(255, 220, 100), font=f_eq)
    txt1 = (
        "When an underexpanded jet leaves a rocket nozzle (p_exit > p_ambient), an expansion fan forms at the lip.\n"
        "The constant-pressure atmospheric boundary reflects the expansion waves as converging compression waves,\n"
        "which coalesce into oblique shock waves directed toward the jet axis of symmetry."
    )
    draw.text((card_x1 + 25, 285), txt1, fill=(220, 230, 240), font=f_body)
    draw.text((card_x1 + 25, 385), f"• Exit Mach: M_e = {st['M_exit']:.2f}  |  NPR: {st['NPR']:.1f}  |  Prandtl-Pack: L_d = {st['L_diamond']:.2f} m", fill=(255, 180, 50), font=f_badge)

    # Card 2: Oblique Shock & Mach Reflection (Mach Disk)
    draw.rounded_rectangle([card_x1, 460, card_x2, 720], radius=12, fill=(11, 19, 43, 220), outline=(255, 180, 0), width=2)
    draw.text((card_x1 + 25, 480), "2. RANKINE-HUGONIOT JUMP & MACH DISK FORMATION", fill=(255, 180, 0), font=f_sec)
    eq2 = "tan(theta) = 2*cot(beta) * (M1^2*sin^2(beta) - 1) / (M1^2*(gamma + cos(2*beta)) + 2)"
    draw.text((card_x1 + 25, 520), eq2, fill=(255, 220, 100), font=f_eq)
    txt2 = (
        "When the incident oblique shock angle beta exceeds the maximum deflection limit theta_max (von Neumann criterion),\n"
        "regular shock reflection is physically impossible. A normal shock disk (Mach Disk) appears at the axis!\n"
        "The normal shock abruptly decelerates the core flow to subsonic (M < 1.0), spiking static temperature past 2,850 K\n"
        "and reigniting unburnt propellant radicals into an incandescent glowing fireball."
    )
    draw.text((card_x1 + 25, 555), txt2, fill=(220, 230, 240), font=f_body)
    draw.text((card_x1 + 25, 675), f"• Core Temp: T_core = {int(st['T_mach_disk_core']):,} K  |  Shock Angle: beta = {st['beta_deg']:.1f}°  |  Mach Disk: R = {st['mach_disk_radius']*100:.1f} cm", fill=(255, 80, 80), font=f_badge)

    # Card 3: Engineering Benchmark & Open Science
    draw.rounded_rectangle([card_x1, 750, card_x2, 980], radius=12, fill=(11, 19, 43, 220), outline=(0, 240, 255), width=2)
    draw.text((card_x1 + 25, 770), "3. CONTINUUM LAB VERIFICATION & REPRODUCIBILITY", fill=(0, 240, 255), font=f_sec)
    txt3 = (
        "• Suite: 01 Mecánica de Fluidos / 09 Diamantes de Choque y Discos de Mach (Issue #25)\n"
        "• Formats: 1080x1920 UHD @ 60 FPS (9:16 Vertical Master) + 44.1 kHz Procedural Stereo Audio\n"
        "• Dynamic Excel Model: Supersonic_Shock_Diamonds_Mach_Disk_Benchmark.xlsx\n"
        "• Full Open Source Suite: github.com/RoPP17/Continuum-Lab"
    )
    draw.text((card_x1 + 25, 810), txt3, fill=(220, 230, 240), font=f_body)

    # Bottom status bar
    draw.text((80, 1010), "VALIDATED BY CONTINUUM LAB COMPRESSIBLE FLUID DYNAMICS ENGINE • 100% OPEN SOURCE", fill=(120, 140, 165), font=f_badge)

    final_rgb = np.array(pil_img)
    final_bgr = cv2.cvtColor(final_rgb, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, final_bgr)
    print(f"[OK] Scientific poster generated: {output_path}")
    return output_path


if __name__ == "__main__":
    test_poster = r"C:\Users\andre\OneDrive\Desktop\Continuum Lab\RENDERS\25 Diamantes de Choque y Discos de Mach Aerodinamicos\extra\capturas\shock_diamonds_poster.png"
    render_shock_diamonds_poster(test_poster)
