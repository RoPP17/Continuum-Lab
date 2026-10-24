"""
Continuum Lab - Master 9:16 UHD 60 FPS Visual Video Renderer for Vortex Rings Collision
Module: 01 Mecanica de Fluidos / 07 Colision de Anillos de Vortice
File: src/visualization/render_vortex_collision.py

Renders 1080x1920 (9:16 Vertical UHD @ 60 FPS) cinematic animations:
  - Deep Cosmic Hydrodynamic Void (#03050E) & Saturated Cyberpunk Palette
  - 3D Perspective projection (26 deg elevation tilt) showing full vertical-to-radial kinematics
  - Dual colliding vortex filaments with multi-layer neon bloom & Widnall wave modulation
  - 1200+ Lagrangian tracer particles with velocity-glow trails
  - Radial starburst of 12 secondary toroidal vortex rings upon topological reconnection
  - Floating Glassmorphic HUD: Widnall spectrum radar & live enstrophy telemetry
  - Dynamic kinetic typography hooks & safe-zone compliant narrative subtitles (ES & EN)
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

from src.physics.vortex_collision_sim import VortexRingsCollisionSim


class MasterVortexCollisionRenderer:
    """
    Master 9:16 60 FPS 3D Perspective Visual Renderer for Colliding Vortex Rings.
    """

    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 60, lang: str = "ES"):
        self.width = width
        self.height = height
        self.fps = fps
        self.lang = lang.upper()

        self.sim = VortexRingsCollisionSim()
        self._load_fonts()

        # 3D Camera Configuration
        # Tilt angle: 24 deg elevation, 32 deg azimuth
        self.elev = np.radians(24.0)
        self.azim = np.radians(32.0)
        self.cam_dist = 3.30
        self.f_proj = 1050.0
        self.cx = self.width / 2.0
        self.cy = self.height / 2.0 + 20.0  # Centered safely between upper HUD and lower subtitles

        # Background floating hydrodynamic micro-particles
        rng = np.random.default_rng(777)
        self.bg_stars = []
        for _ in range(110):
            bx = float(rng.uniform(30, self.width - 30))
            by = float(rng.uniform(50, self.height - 50))
            b_spd = float(rng.uniform(0.3, 1.4))
            b_sz = int(rng.integers(1, 4))
            b_alpha = float(rng.uniform(0.12, 0.55))
            self.bg_stars.append([bx, by, b_spd, b_sz, b_alpha])

        # Particle trail buffer (storing previous 2 frames of 2D screen positions)
        self.trail_history: List[np.ndarray] = []

    def _load_fonts(self):
        def try_font(path, size, fallback=None):
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    pass
            return fallback or ImageFont.load_default()

        self.f_hero_hook = try_font("C:/Windows/Fonts/segoeuib.ttf", 30, try_font("C:/Windows/Fonts/arialbd.ttf", 30))
        self.f_sub_hook = try_font("C:/Windows/Fonts/segoeui.ttf", 21, try_font("C:/Windows/Fonts/arial.ttf", 21))
        self.f_brand_title = try_font("C:/Windows/Fonts/segoeuib.ttf", 22)
        self.f_card_hdr = try_font("C:/Windows/Fonts/segoeuib.ttf", 16)
        self.f_card_meta = try_font("C:/Windows/Fonts/consolab.ttf", 14)
        self.f_hud_lbl = try_font("C:/Windows/Fonts/segoeuib.ttf", 14)
        self.f_hud_val = try_font("C:/Windows/Fonts/consolab.ttf", 20)
        self.f_badge_tag = try_font("C:/Windows/Fonts/consolab.ttf", 13)

    def _project_3d(self, pts_3d: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Projects 3D points (N, 3) to 2D screen coordinates (N, 2) using perspective.
        Returns: (screen_pts_2d, depth_z_cam)
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

    def _draw_glowing_ring(self, img_bgr: np.ndarray, pts_2d: np.ndarray, color_bgr: Tuple[int, int, int], 
                           thickness: int = 4, halo_thickness: int = 18, alpha: float = 0.38):
        """Draws closed 3D projected curve with multi-layer neon bloom."""
        overlay = img_bgr.copy()
        pts_int = pts_2d.astype(np.int32)
        # Outer bloom
        cv2.polylines(overlay, [pts_int], isClosed=True, color=color_bgr, thickness=halo_thickness, lineType=cv2.LINE_AA)
        cv2.addWeighted(overlay, alpha, img_bgr, 1.0 - alpha, 0, img_bgr)
        # Mid core
        cv2.polylines(img_bgr, [pts_int], isClosed=True, color=color_bgr, thickness=max(2, thickness + 3), lineType=cv2.LINE_AA)
        # White laser spine
        cv2.polylines(img_bgr, [pts_int], isClosed=True, color=(255, 255, 255), thickness=max(1, thickness - 1), lineType=cv2.LINE_AA)

    def render_frame(self, t: float, frame_idx: int) -> np.ndarray:
        """Renders single 1080x1920 frame at time t."""
        st = self.sim.get_state(t)

        # 1. Background with cosmic hydrodynamic gradient
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        grad = np.linspace(0, 1, self.height)[:, None]
        frame[:, :, 0] = (14 + grad * 12).astype(np.uint8)
        frame[:, :, 1] = (6 + grad * 6).astype(np.uint8)
        frame[:, :, 2] = (3 + grad * 5).astype(np.uint8)

        # Ambient perspective grid on collision plane z = 0
        grid_overlay = frame.copy()
        for r_ring in [0.3, 0.6, 0.9, 1.2]:
            th_grid = np.linspace(0, 2 * np.pi, 90)
            gx = r_ring * np.cos(th_grid)
            gy = r_ring * np.sin(th_grid)
            gz = np.zeros_like(th_grid)
            g_pts, _ = self._project_3d(np.column_stack((gx, gy, gz)))
            cv2.polylines(grid_overlay, [g_pts.astype(np.int32)], True, (35, 25, 18), 1, cv2.LINE_AA)
        cv2.addWeighted(grid_overlay, 0.35, frame, 0.65, 0, frame)

        # Floating ambient dust
        for s in self.bg_stars:
            s[1] -= s[2]
            if s[1] < 40:
                s[1] = self.height - 40
            cv2.circle(frame, (int(s[0]), int(s[1])), s[3],
                       (int(240 * s[4]), int(200 * s[4]), int(100 * s[4])), -1, cv2.LINE_AA)

        # 2. 3D Projections of Primary Vortex Rings
        ring1_2d, depth1 = self._project_3d(st["ring1"])
        ring2_2d, depth2 = self._project_3d(st["ring2"])

        # Determine color modulation based on approach & strain
        # Upper ring: Electric Cyan (255, 240, 0)
        # Lower ring: Neon Magenta (220, 0, 255)
        # Collision interface blend: Solar Flare Gold (0, 180, 255)
        blend_factor = float(np.clip(st["R_ratio"] / 2.8, 0.0, 1.0))

        c_upper = (
            int(255 * (1.0 - 0.7 * blend_factor)),  # B
            int(240 * (1.0 - 0.2 * blend_factor)),  # G
            int(0 + 255 * blend_factor)             # R
        )
        c_lower = (
            int(220 * (1.0 - 0.6 * blend_factor)),  # B
            int(0 + 160 * blend_factor),            # G
            int(255)                                # R
        )

        # Sort rendering order by depth (far to near)
        mean_d1 = np.mean(depth1)
        mean_d2 = np.mean(depth2)
        if mean_d1 > mean_d2:
            self._draw_glowing_ring(frame, ring1_2d, c_upper, thickness=4, halo_thickness=20, alpha=0.40)
            self._draw_glowing_ring(frame, ring2_2d, c_lower, thickness=4, halo_thickness=20, alpha=0.40)
        else:
            self._draw_glowing_ring(frame, ring2_2d, c_lower, thickness=4, halo_thickness=20, alpha=0.40)
            self._draw_glowing_ring(frame, ring1_2d, c_upper, thickness=4, halo_thickness=20, alpha=0.40)

        # 3. Secondary Reconnected Baby Rings (Crown m = 12)
        if st["is_reconnected"] and len(st["sec_rings"]) > 0:
            for k, sring_3d in enumerate(st["sec_rings"]):
                sring_2d, sdepth = self._project_3d(sring_3d)
                # Alternate colors between neon cyan and radiant magenta
                c_sec = (255, 240, 0) if k % 2 == 0 else (220, 0, 255)
                self._draw_glowing_ring(frame, sring_2d, c_sec, thickness=3, halo_thickness=14, alpha=0.35)

        # 4. Lagrangian Tracer Particles with Velocity Bloom
        p_2d, p_depth = self._project_3d(st["particles_3d"])
        speeds = st["particles_speed"]
        max_v = max(np.percentile(speeds, 95), 1.0)

        # Save to trail history buffer
        self.trail_history.append(p_2d.copy())
        if len(self.trail_history) > 3:
            self.trail_history.pop(0)

        # Draw motion trails
        if len(self.trail_history) >= 2:
            trail_overlay = frame.copy()
            p_prev = self.trail_history[0]
            for i in range(0, len(p_2d), 2):  # Every 2nd particle
                pt1 = (int(p_prev[i, 0]), int(p_prev[i, 1]))
                pt2 = (int(p_2d[i, 0]), int(p_2d[i, 1]))
                if 0 <= pt2[0] < self.width and 0 <= pt2[1] < self.height:
                    v_norm = np.clip(speeds[i] / max_v, 0.0, 1.0)
                    t_color = (int(255 * (1.0 - v_norm)), int(220 * (1.0 - 0.5 * v_norm)), int(255 * v_norm))
                    cv2.line(trail_overlay, pt1, pt2, t_color, 1, cv2.LINE_AA)
            cv2.addWeighted(trail_overlay, 0.45, frame, 0.55, 0, frame)

        # Draw particle points
        for i in range(len(p_2d)):
            u_p, v_p = int(p_2d[i, 0]), int(p_2d[i, 1])
            if 0 <= u_p < self.width and 0 <= v_p < self.height:
                v_norm = np.clip(speeds[i] / max_v, 0.0, 1.0)
                # Color gradient: Cyan -> Magenta -> Amber
                b_val = int(255 * (1.0 - v_norm * 0.9))
                g_val = int(240 * (1.0 - v_norm * 0.7))
                r_val = int(255 * (v_norm ** 0.8))
                cv2.circle(frame, (u_p, v_p), 2, (b_val, g_val, r_val), -1, cv2.LINE_AA)

        # -------------------------------------------------------------
        # PIL High-Precision Glassmorphism HUD Overlay
        # -------------------------------------------------------------
        img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil, "RGBA")

        # 1. Top Header Branding Capsule (y = 80 to 168, balanced margins x = 75 to 1005)
        self._draw_glass_panel(draw, 75, 80, self.width - 75, 168, border_color=(0, 240, 255, 200))
        brand_en = "CONTINUUM LAB // ADVANCED VORTICITY DYNAMICS"
        brand_es = "CONTINUUM LAB // DINÁMICA DE VORTICIDAD AVANZADA"
        hdr_txt = brand_es if self.lang == "ES" else brand_en
        title_txt = "COLISIÓN DE ANILLOS DE VÓRTICE & RECONEXIÓN (m = 12)" if self.lang == "ES" else "VORTEX RING COLLISION & RECONNECTION CASCADE"
        w_hdr = draw.textlength(hdr_txt, font=self.f_card_meta)
        w_title = draw.textlength(title_txt, font=self.f_brand_title)
        draw.text((int((self.width - w_hdr) / 2), 95), hdr_txt, font=self.f_card_meta, fill=(0, 240, 255, 255))
        draw.text((int((self.width - w_title) / 2), 120), title_txt, font=self.f_brand_title, fill=(255, 255, 255, 255))

        # 2. Widnall Spectrum Mini-Radar Card (Upper Left: x = 75 to 455, y = 195 to 455)
        self._draw_glass_panel(draw, 75, 195, 455, 455, border_color=(0, 240, 255, 180))
        radar_title = "INESTABILIDAD DE WIDNALL" if self.lang == "ES" else "WIDNALL INSTABILITY"
        draw.text((95, 210), radar_title, font=self.f_card_hdr, fill=(0, 240, 255, 255))
        draw.text((95, 232), "Espectro Azimutal de Deformación", font=self.f_card_meta, fill=(160, 180, 200, 230))

        # Draw bar chart of azimuthal modes m in [4, 16]
        rx0, rx1 = 100, 430
        ry_base = 415
        modes = list(range(4, 17))
        bar_w = (rx1 - rx0) // len(modes)

        # Amplitude peaks at m = 12
        for idx_m, m_val in enumerate(modes):
            bx = rx0 + idx_m * bar_w + 3
            # Gaussian peak around m = 12
            dist_12 = abs(m_val - 12)
            rel_amp = np.exp(-(dist_12**2) / 3.5) * (st["amp_widnall"] / (st["a"] * 1.5))
            b_height = int(rel_amp * 135)
            b_color = (255, 183, 3, 240) if m_val == 12 else (0, 240, 255, 160)
            draw.rectangle([bx, ry_base - b_height, bx + bar_w - 6, ry_base], fill=b_color)
            if m_val in [6, 8, 10, 12, 14, 16]:
                draw.text((bx, ry_base + 6), str(m_val), font=self.f_badge_tag, fill=(140, 160, 180, 220))

        draw.text((rx0, ry_base + 22), "Modo dominante: m = 12 (Bifurcación)", font=self.f_badge_tag, fill=(255, 183, 3, 240))

        # 3. Telemetry Glass HUD (Upper Right: x = 625 to 1005, y = 195 to 455)
        self._draw_glass_panel(draw, 625, 195, 1005, 455, border_color=(0, 240, 255, 180))
        draw.text((650, 210), "TELEMETRÍA DE VORTICIDAD" if self.lang == "ES" else "VORTICITY TELEMETRY",
                  font=self.f_card_hdr, fill=(0, 240, 255, 255))

        # Status badge
        if not st["is_reconnected"]:
            status_txt = "[APROXIMACIÓN & ESTIRAMIENTO]" if self.lang == "ES" else "[APPROACH & STRAIN]"
            status_color = (0, 255, 136, 255)
        elif t < 9.0:
            status_txt = "[¡RECONEXIÓN TOPOLÓGICA!]" if self.lang == "ES" else "[TOPOLOGICAL RECONNECTION!]"
            status_color = (255, 183, 3, 255)
        else:
            status_txt = "[CASCADA CORONA m=12]" if self.lang == "ES" else "[SECONDARY CROWN CASCADE]"
            status_color = (255, 0, 85, 255)
        draw.text((650, 233), status_txt, font=self.f_badge_tag, fill=status_color)

        hud_rows = [
            ("CIRCULACIÓN Γ₀:" if self.lang == "ES" else "CIRCULATION Γ₀:", f"{self.sim.Gamma0:.2f} m²/s"),
            ("EXPANSIÓN R / R₀:" if self.lang == "ES" else "EXPANSION R / R₀:", f"{st['R_ratio']:.2f}x"),
            ("DISTANCIA z_sep:" if self.lang == "ES" else "SEPARATION z_sep:", f"{2.0 * st['z'] * 100:.1f} cm"),
            ("VORTICIDAD ω_max:" if self.lang == "ES" else "PEAK VORTICITY ω:", f"{st['omega_max']:.0f} s⁻¹")
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

        if t < 2.8:
            if self.lang == "ES":
                main_hook = "¿QUÉ PASA AL CHOCAR DOS VÓRTICES?"
                sub_hook = "Dos anillos coaxiales de signo opuesto aceleran hacia el plano central"
            else:
                main_hook = "WHAT HAPPENS WHEN TWO VORTEX RINGS COLLIDE?"
                sub_hook = "Coaxial counter-rotating rings accelerate toward the collision plane"
            glow_c = (0, 240, 255, 255)
        elif t < 5.8:
            if self.lang == "ES":
                main_hook = "APLANAMIENTO RADIAL Y ESTIRAMIENTO DE NÚCLEO"
                sub_hook = "La inducción mutua expande el radio R y concentra la enstrofia pico"
            else:
                main_hook = "RADIAL FLATTENING & VORTEX STRETCHING"
                sub_hook = "Mutual induction drives violent radial expansion and enstrophy surge"
            glow_c = (255, 183, 3, 255)
        elif t < 9.0:
            if self.lang == "ES":
                main_hook = "¡INESTABILIDAD DE WIDNALL (m = 12)!"
                sub_hook = "Ruptura del núcleo: el esfuerzo cortante ondula los filamentos en 3D"
            else:
                main_hook = "WIDNALL INSTABILITY BREAKS THE CORES (m = 12)"
                sub_hook = "Azimuthal shear waves buckle the vortex tubes into sinusoidal loops"
            glow_c = (255, 0, 85, 255)
        elif t < 12.8:
            if self.lang == "ES":
                main_hook = "¡RECONEXIÓN: 12 ANILLOS SECUNDARIOS!"
                sub_hook = "Aniquilación viscosa y salto topológico: una corona radial se dispara"
            else:
                main_hook = "TOPOLOGICAL RECONNECTION: 12 SECONDARY RINGS!"
                sub_hook = "Viscous annihilation triggers topology jump into a radial starburst"
            glow_c = (0, 240, 255, 255)
        else:
            if self.lang == "ES":
                main_hook = "CASCADA INFINITA DE NAVIER-STOKES"
                sub_hook = "Conservación de masa y circulación // Continuum Lab Monorepo"
            else:
                main_hook = "INFINITE NAVIER-STOKES CASCADE"
                sub_hook = "Mass and circulation conservation // Continuum Lab Open-Source"
            glow_c = (0, 255, 136, 255)

        w_main = draw.textlength(main_hook, font=self.f_hero_hook)
        w_sub = draw.textlength(sub_hook, font=self.f_sub_hook)
        draw.text((int((self.width - w_main) / 2), hook_box_y1 + 25), main_hook, font=self.f_hero_hook, fill=glow_c)
        draw.text((int((self.width - w_sub) / 2), hook_box_y1 + 82), sub_hook, font=self.f_sub_hook, fill=(220, 230, 240, 245))

        draw.text((self.width // 2 - 120, self.height - 75), "github.com/RoPP17/Continuum-Lab",
                  font=self.f_badge_tag, fill=(120, 140, 160, 180))

        final_frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        return final_frame

    def _draw_glass_panel(self, draw: ImageDraw.ImageDraw, x1: int, y1: int, x2: int, y2: int, 
                          bg_fill: Tuple[int, int, int, int] = (10, 16, 28, 205),
                          border_color: Tuple[int, int, int, int] = (0, 240, 255, 180),
                          corner_radius: int = 16):
        draw.rounded_rectangle([x1, y1, x2, y2], radius=corner_radius, fill=bg_fill, outline=border_color, width=2)


def render_vortex_collision_video(output_mp4: str, audio_wav: Optional[str] = None, 
                                  duration: float = 16.0, fps: int = 60, lang: str = "ES",
                                  hero_capture_path: Optional[str] = None) -> str:
    """
    Renders the complete 9:16 vertical video at 60 FPS using an FFmpeg pipeline.
    """
    renderer = MasterVortexCollisionRenderer(width=1080, height=1920, fps=fps, lang=lang)
    total_frames = int(duration * fps)
    temp_video = output_mp4.replace(".mp4", "_temp.mp4")

    os.makedirs(os.path.dirname(output_mp4), exist_ok=True)

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

    hero_frame_idx = int(7.0 * fps)  # Peak crown reconnection frame
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
    render_vortex_collision_video("output/test_vortex.mp4", lang="ES")
