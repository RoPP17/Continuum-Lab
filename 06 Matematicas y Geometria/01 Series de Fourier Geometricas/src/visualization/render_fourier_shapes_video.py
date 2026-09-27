"""
Continuum Lab — Mathematical Physics & Fourier Geometry
Vectorized Manim TikTok 9:16 Animation:
Simultaneous Temporal Development of Fourier Series along the +X Cartesian Axis.

Visual Architecture:
  - 3 Parallel Horizontal Tracks stacked vertically (Circle, 5P Star, Octagon).
  - All three develop SIMULTANEOUSLY along the positive X-axis over time t in [0, 4pi].
  - In each track:
      1. Left Card: Geometric icon + Shape Title + Explicit Fourier series function y(t).
      2. Center-Left: Rotating Epicycle Phasor generator showing instantaneous harmonic state.
      3. Right: Cartesian Coordinate Plane (X -> +X Time, Y -> Amplitude) with:
         - Time ticks (pi, 2pi, 3pi, 4pi).
         - Real-time wave drawing along +X.
         - Horizontal dashed projection line connecting rotating phasor tip directly to advancing wave head!
  - Safe zones: Top HUD at y = 5.25 (>220 px margin), Bottom HUD at y = -4.95 (>320 px margin).
  - Audio: Gentle, catchy lo-fi science music synthesized at 112 BPM.
  - Bilingual delivery: Spanish (ES) and English (EN).
"""

from manim import *
import numpy as np
import os
import subprocess
import sys
from pathlib import Path
import imageio_ffmpeg

# Add project root for module imports
project_dir = Path(__file__).resolve().parent.parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.math.fourier_shapes import ShapeFourierSeries
from src.audio.fourier_music_synth import synthesize_fourier_background_music

# Exact TikTok 9:16 Canvas Configuration
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#080a0f"  # Deep Cosmic Void


def create_fourier_wave_scene(lang: str = "ES"):
    class FourierWaveScene(Scene):
        def construct(self):
            # ----------------------------------------------------
            # 1. Top HUD Card (Safe Zone: y in [4.6, 5.9])
            # Leaves >240 px margin from top edge
            # ----------------------------------------------------
            top_box = RoundedRectangle(
                corner_radius=0.14,
                width=8.0,
                height=1.35,
                color="#00f0ff",
                stroke_width=1.4,
                fill_color="#0d1117",
                fill_opacity=0.95
            ).move_to(UP * 5.25)

            eq_top = MathTex(
                r"z(t) = \sum_{n=-\infty}^{\infty} c_n \, e^{i n \omega_0 t} \quad \longleftrightarrow \quad y(t) = \sum_{n=1}^{\infty} b_n \sin(n \omega_0 t)",
                font_size=18,
                color="#ffffff"
            )
            sub_top = MathTex(
                r"\mathbf{DESARROLLO\ TEMPORAL\ DE\ SERIES\ DE\ FOURIER\ (+X)}" if lang == "ES"
                else r"\mathbf{TEMPORAL\ EVOLUTION\ OF\ FOURIER\ SERIES\ (+X)}",
                font_size=15,
                color="#00f0ff"
            )

            eq_top.move_to(top_box.get_top() + DOWN * 0.38)
            sub_top.next_to(eq_top, DOWN, buff=0.16)
            top_group = VGroup(top_box, eq_top, sub_top)

            # ----------------------------------------------------
            # 2. Bottom Summary Card (Safe Zone: y in [-5.5, -4.4])
            # Leaves >310 px margin from bottom edge for TikTok UI
            # ----------------------------------------------------
            bottom_box = RoundedRectangle(
                corner_radius=0.14,
                width=8.0,
                height=1.15,
                color="#ec4899",
                stroke_width=1.3,
                fill_color="#0d1117",
                fill_opacity=0.95
            ).move_to(DOWN * 4.95)

            if lang == "ES":
                telem_header = MathTex(
                    r"\mathbf{SIMILITUD\ ESPECTRAL\ EN\ EL\ TIEMPO\ (+X)}",
                    font_size=16,
                    color="#ffffff"
                )
                desc_text = MathTex(
                    r"\text{Las tres formas modulan el mismo fasor fundamental } e^{i t} \text{ a lo largo del tiempo}",
                    font_size=14,
                    color="#39ff14"
                )
            else:
                telem_header = MathTex(
                    r"\mathbf{SPECTRAL\ SIMILARITY\ OVER\ TIME\ (+X)}",
                    font_size=16,
                    color="#ffffff"
                )
                desc_text = MathTex(
                    r"\text{All three shapes modulate the same fundamental phasor } e^{i t} \text{ over time}",
                    font_size=14,
                    color="#39ff14"
                )

            telem_header.move_to(bottom_box.get_top() + DOWN * 0.32)
            desc_text.next_to(telem_header, DOWN, buff=0.16)
            bottom_group = VGroup(bottom_box, telem_header, desc_text)

            # ----------------------------------------------------
            # 3. Geometry & Track Architecture (3 Simultaneous Rows)
            # ----------------------------------------------------
            y_rows = [2.85, 0.00, -2.85]
            
            # Physical scales
            r_phasor = 0.48    # Base phasor radius
            x_phasor = -0.75   # Phasor center X
            x_origin = 0.20    # Cartesian axis origin X
            x_end = 3.85       # Cartesian axis arrow tip X
            L_draw = 3.25      # Length of drawing domain (t = 4pi at x_origin + L_draw = 3.45)

            # ====================================================
            # BUILD TRACK 1: CÍRCULO (y = 2.85)
            # ====================================================
            y1 = y_rows[0]
            # Card 1 (Left)
            c1_box = RoundedRectangle(
                corner_radius=0.12, width=2.65, height=2.15,
                color="#00f0ff", stroke_width=1.2, fill_color="#090d16", fill_opacity=0.90
            ).move_to(np.array([-2.70, y1, 0]))

            icon_c1 = Circle(radius=0.22, color="#00f0ff", stroke_width=2.2, fill_color="#00f0ff", fill_opacity=0.15).move_to(np.array([-3.55, y1 + 0.55, 0]))
            title_c1 = Text("1. CÍRCULO" if lang == "ES" else "1. CIRCLE", font_size=13, color="#00f0ff", weight=BOLD).move_to(np.array([-2.55, y1 + 0.55, 0]))
            eq1_c1 = MathTex(r"y(t) = \sin(\omega_0 t)", font_size=14, color=WHITE).move_to(np.array([-2.70, y1 + 0.12, 0]))
            eq2_c1 = MathTex(r"z(t) = e^{i \omega_0 t} \quad (N = 1)", font_size=12, color="#94a3b8").move_to(np.array([-2.70, y1 - 0.28, 0]))
            note_c1 = MathTex(r"\text{Arm\'onico Fundamental Puro}" if lang == "ES" else r"\text{Pure Fundamental Harmonic}", font_size=10, color="#38bdf8").move_to(np.array([-2.70, y1 - 0.65, 0]))
            card1 = VGroup(c1_box, icon_c1, title_c1, eq1_c1, eq2_c1, note_c1)

            # Phasor 1 (Circle generator)
            guide_c1 = Circle(radius=r_phasor, color="#1e293b", stroke_width=1.0, stroke_opacity=0.5).move_to(np.array([x_phasor, y1, 0]))
            contour_c1 = Circle(radius=r_phasor, color="#00f0ff", stroke_width=1.2, stroke_opacity=0.35).move_to(np.array([x_phasor, y1, 0]))
            arm1_c1 = Line(np.array([x_phasor, y1, 0]), np.array([x_phasor + r_phasor, y1, 0]), color="#00f0ff", stroke_width=2.4)
            dot_c1 = Dot(np.array([x_phasor + r_phasor, y1, 0]), radius=0.045, color=WHITE)

            # Cartesian Plane 1
            axis_x1 = Arrow(np.array([x_origin, y1, 0]), np.array([x_end, y1, 0]), buff=0, color="#475569", stroke_width=1.4, max_tip_length_to_length_ratio=0.06)
            axis_y1 = Arrow(np.array([x_origin, y1 - 0.80, 0]), np.array([x_origin, y1 + 0.85, 0]), buff=0, color="#475569", stroke_width=1.4, max_tip_length_to_length_ratio=0.06)
            lbl_x1 = MathTex(r"t \ (\text{Tiempo})" if lang == "ES" else r"t \ (\text{Time})", font_size=10, color="#94a3b8").next_to(axis_x1, UP, buff=0.08).align_to(axis_x1, RIGHT)
            lbl_y1 = MathTex(r"y(t)", font_size=10, color="#94a3b8").next_to(axis_y1, RIGHT, buff=0.06).align_to(axis_y1, UP)
            base_line1 = DashedLine(np.array([x_origin, y1, 0]), np.array([x_end - 0.1, y1, 0]), stroke_width=0.6, color="#1e293b")

            # Ticks at pi, 2pi, 3pi, 4pi
            ticks_g1 = VGroup()
            for k, lbl in [(1, r"\pi"), (2, r"2\pi"), (3, r"3\pi"), (4, r"4\pi")]:
                x_tk = x_origin + (k / 4.0) * L_draw
                tk_line = Line(np.array([x_tk, y1 + 0.04, 0]), np.array([x_tk, y1 - 0.04, 0]), color="#64748b", stroke_width=1.0)
                tk_lbl = MathTex(lbl, font_size=9, color="#64748b").next_to(tk_line, DOWN, buff=0.14)
                ticks_g1.add(tk_line, tk_lbl)

            cartesian1 = VGroup(base_line1, axis_x1, axis_y1, lbl_x1, lbl_y1, ticks_g1)

            # Wave Trail 1 & Cursor
            trail1 = VMobject(stroke_width=2.5, color="#00f0ff", fill_opacity=0.0)
            trail1.set_points_as_corners([np.array([x_origin, y1, 0]), np.array([x_origin + 0.001, y1, 0])])
            cursor1 = Dot(np.array([x_origin, y1, 0]), radius=0.065, color=WHITE)
            halo1 = Circle(radius=0.12, color="#00f0ff", stroke_width=1.4)
            proj_line1 = DashedLine(np.array([x_phasor + r_phasor, y1, 0]), np.array([x_origin, y1, 0]), dash_length=0.08, dashed_ratio=0.5, color="#38bdf8", stroke_width=1.2)

            # ====================================================
            # BUILD TRACK 2: ESTRELLA 5P (y = 0.00)
            # ====================================================
            y2 = y_rows[1]
            c2_box = RoundedRectangle(
                corner_radius=0.12, width=2.65, height=2.15,
                color="#fbbf24", stroke_width=1.2, fill_color="#141109", fill_opacity=0.90
            ).move_to(np.array([-2.70, y2, 0]))

            # Star Icon
            ang_s = np.linspace(np.pi/2, np.pi/2 + 2*np.pi, 10, endpoint=False)
            rad_s = np.array([0.24, 0.11] * 5)
            pts_s = [np.array([-3.55 + r * np.cos(a), y2 + 0.55 + r * np.sin(a), 0]) for r, a in zip(rad_s, ang_s)]
            pts_s.append(pts_s[0])
            icon_c2 = VMobject(stroke_width=2.0, color="#fbbf24", fill_color="#fbbf24", fill_opacity=0.15)
            icon_c2.set_points_as_corners(pts_s)

            title_c2 = Text("2. ESTRELLA 5P" if lang == "ES" else "2. 5-POINT STAR", font_size=13, color="#fbbf24", weight=BOLD).move_to(np.array([-2.55, y2 + 0.55, 0]))
            eq1_c2 = MathTex(r"y(t) \approx \sin(t) - \frac{1}{4}\sin(4t)", font_size=13, color=WHITE).move_to(np.array([-2.70, y2 + 0.12, 0]))
            eq2_c2 = MathTex(r"D_5 \implies n \in \{1, -4, 6, \dots\}", font_size=11, color="#94a3b8").move_to(np.array([-2.70, y2 - 0.28, 0]))
            note_c2 = MathTex(r"\text{Arm\'onico }-4t\text{ genera 5 C\'uspides}" if lang == "ES" else r"\text{Retrograde }-4t\text{ forms 5 Cusps}", font_size=10, color="#fbbf24").move_to(np.array([-2.70, y2 - 0.65, 0]))
            card2 = VGroup(c2_box, icon_c2, title_c2, eq1_c2, eq2_c2, note_c2)

            # Phasor 2 (Two-arm epicycles: n = 1, n = -4, n = 6)
            r_s1 = 0.80 * r_phasor
            r_s2 = 0.25 * r_s1
            r_s3 = 0.08 * r_s1
            guide_s1 = Circle(radius=r_s1, color="#1e293b", stroke_width=0.8, stroke_opacity=0.5).move_to(np.array([x_phasor, y2, 0]))
            guide_s2 = Circle(radius=r_s2, color="#1e293b", stroke_width=0.8, stroke_opacity=0.5)

            # Star reference contour lightly in background
            t_samples = np.linspace(0, 2*np.pi, 120)
            star_bg_pts = [np.array([x_phasor + r_s1*np.cos(th) + r_s2*np.cos(-4*th) + r_s3*np.cos(6*th), y2 + r_s1*np.sin(th) + r_s2*np.sin(-4*th) + r_s3*np.sin(6*th), 0]) for th in t_samples]
            star_bg_pts.append(star_bg_pts[0])
            contour_c2 = VMobject(stroke_width=1.2, color="#fbbf24", stroke_opacity=0.35)
            contour_c2.set_points_as_corners(star_bg_pts)

            arm1_c2 = Line(np.array([x_phasor, y2, 0]), np.array([x_phasor + r_s1, y2, 0]), color="#fbbf24", stroke_width=2.2)
            arm2_c2 = Line(np.array([x_phasor + r_s1, y2, 0]), np.array([x_phasor + r_s1 + r_s2, y2, 0]), color="#f59e0b", stroke_width=1.8)
            dot_c2 = Dot(np.array([x_phasor + r_s1 + r_s2, y2, 0]), radius=0.045, color=WHITE)

            # Cartesian Plane 2
            axis_x2 = Arrow(np.array([x_origin, y2, 0]), np.array([x_end, y2, 0]), buff=0, color="#475569", stroke_width=1.4, max_tip_length_to_length_ratio=0.06)
            axis_y2 = Arrow(np.array([x_origin, y2 - 0.80, 0]), np.array([x_origin, y2 + 0.85, 0]), buff=0, color="#475569", stroke_width=1.4, max_tip_length_to_length_ratio=0.06)
            lbl_x2 = MathTex(r"t \ (\text{Tiempo})" if lang == "ES" else r"t \ (\text{Time})", font_size=10, color="#94a3b8").next_to(axis_x2, UP, buff=0.08).align_to(axis_x2, RIGHT)
            lbl_y2 = MathTex(r"y(t)", font_size=10, color="#94a3b8").next_to(axis_y2, RIGHT, buff=0.06).align_to(axis_y2, UP)
            base_line2 = DashedLine(np.array([x_origin, y2, 0]), np.array([x_end - 0.1, y2, 0]), stroke_width=0.6, color="#1e293b")

            ticks_g2 = VGroup()
            for k, lbl in [(1, r"\pi"), (2, r"2\pi"), (3, r"3\pi"), (4, r"4\pi")]:
                x_tk = x_origin + (k / 4.0) * L_draw
                tk_line = Line(np.array([x_tk, y2 + 0.04, 0]), np.array([x_tk, y2 - 0.04, 0]), color="#64748b", stroke_width=1.0)
                tk_lbl = MathTex(lbl, font_size=9, color="#64748b").next_to(tk_line, DOWN, buff=0.14)
                ticks_g2.add(tk_line, tk_lbl)

            cartesian2 = VGroup(base_line2, axis_x2, axis_y2, lbl_x2, lbl_y2, ticks_g2)

            trail2 = VMobject(stroke_width=2.5, fill_opacity=0.0)
            trail2.set_points_as_corners([np.array([x_origin, y2, 0]), np.array([x_origin + 0.001, y2, 0])])
            trail2.set_color_by_gradient("#fbbf24", "#f59e0b", "#ef4444")
            cursor2 = Dot(np.array([x_origin, y2, 0]), radius=0.065, color=WHITE)
            halo2 = Circle(radius=0.12, color="#fbbf24", stroke_width=1.4)
            proj_line2 = DashedLine(np.array([x_phasor + r_s1 + r_s2, y2, 0]), np.array([x_origin, y2, 0]), dash_length=0.08, dashed_ratio=0.5, color="#fbbf24", stroke_width=1.2)

            # ====================================================
            # BUILD TRACK 3: OCTÓGONO (y = -2.85)
            # ====================================================
            y3 = y_rows[2]
            c3_box = RoundedRectangle(
                corner_radius=0.12, width=2.65, height=2.15,
                color="#f43f5e", stroke_width=1.2, fill_color="#14090d", fill_opacity=0.90
            ).move_to(np.array([-2.70, y3, 0]))

            # Octagon Icon
            ang_o = np.linspace(np.pi/8, np.pi/8 + 2*np.pi, 8, endpoint=False)
            pts_o = [np.array([-3.55 + 0.22 * np.cos(a), y3 + 0.55 + 0.22 * np.sin(a), 0]) for a in ang_o]
            pts_o.append(pts_o[0])
            icon_c3 = VMobject(stroke_width=2.0, color="#f43f5e", fill_color="#f43f5e", fill_opacity=0.15)
            icon_c3.set_points_as_corners(pts_o)

            title_c3 = Text("3. OCTÓGONO" if lang == "ES" else "3. OCTAGON", font_size=13, color="#f43f5e", weight=BOLD).move_to(np.array([-2.55, y3 + 0.55, 0]))
            eq1_c3 = MathTex(r"y(t) \approx \sin(t) - \frac{1}{49}\sin(7t)", font_size=13, color=WHITE).move_to(np.array([-2.70, y3 + 0.12, 0]))
            eq2_c3 = MathTex(r"D_8 \implies n \in \{1, -7, 9, \dots\}", font_size=11, color="#94a3b8").move_to(np.array([-2.70, y3 - 0.28, 0]))
            note_c3 = MathTex(r"\text{Simetr\'ia } D_8 \text{ aplana las caras}" if lang == "ES" else r"\text{Dihedral } D_8 \text{ flattens facets}", font_size=10, color="#f43f5e").move_to(np.array([-2.70, y3 - 0.65, 0]))
            card3 = VGroup(c3_box, icon_c3, title_c3, eq1_c3, eq2_c3, note_c3)

            # Phasor 3 (Two-arm epicycles: n = 1, n = -7, n = 9)
            r_o1 = 0.95 * r_phasor
            r_o2 = 0.08 * r_o1
            r_o3 = 0.04 * r_o1
            guide_o1 = Circle(radius=r_o1, color="#1e293b", stroke_width=0.8, stroke_opacity=0.5).move_to(np.array([x_phasor, y3, 0]))
            guide_o2 = Circle(radius=r_o2, color="#1e293b", stroke_width=0.8, stroke_opacity=0.5)

            # Octagon reference contour lightly in background
            oct_bg_pts = [np.array([x_phasor + r_o1*np.cos(th) + r_o2*np.cos(-7*th) + r_o3*np.cos(9*th), y3 + r_o1*np.sin(th) + r_o2*np.sin(-7*th) + r_o3*np.sin(9*th), 0]) for th in t_samples]
            oct_bg_pts.append(oct_bg_pts[0])
            contour_c3 = VMobject(stroke_width=1.2, color="#f43f5e", stroke_opacity=0.35)
            contour_c3.set_points_as_corners(oct_bg_pts)

            arm1_c3 = Line(np.array([x_phasor, y3, 0]), np.array([x_phasor + r_o1, y3, 0]), color="#f43f5e", stroke_width=2.2)
            arm2_c3 = Line(np.array([x_phasor + r_o1, y3, 0]), np.array([x_phasor + r_o1 + r_o2, y3, 0]), color="#ec4899", stroke_width=1.8)
            dot_c3 = Dot(np.array([x_phasor + r_o1 + r_o2, y3, 0]), radius=0.045, color=WHITE)

            # Cartesian Plane 3
            axis_x3 = Arrow(np.array([x_origin, y3, 0]), np.array([x_end, y3, 0]), buff=0, color="#475569", stroke_width=1.4, max_tip_length_to_length_ratio=0.06)
            axis_y3 = Arrow(np.array([x_origin, y3 - 0.80, 0]), np.array([x_origin, y3 + 0.85, 0]), buff=0, color="#475569", stroke_width=1.4, max_tip_length_to_length_ratio=0.06)
            lbl_x3 = MathTex(r"t \ (\text{Tiempo})" if lang == "ES" else r"t \ (\text{Time})", font_size=10, color="#94a3b8").next_to(axis_x3, UP, buff=0.08).align_to(axis_x3, RIGHT)
            lbl_y3 = MathTex(r"y(t)", font_size=10, color="#94a3b8").next_to(axis_y3, RIGHT, buff=0.06).align_to(axis_y3, UP)
            base_line3 = DashedLine(np.array([x_origin, y3, 0]), np.array([x_end - 0.1, y3, 0]), stroke_width=0.6, color="#1e293b")

            ticks_g3 = VGroup()
            for k, lbl in [(1, r"\pi"), (2, r"2\pi"), (3, r"3\pi"), (4, r"4\pi")]:
                x_tk = x_origin + (k / 4.0) * L_draw
                tk_line = Line(np.array([x_tk, y3 + 0.04, 0]), np.array([x_tk, y3 - 0.04, 0]), color="#64748b", stroke_width=1.0)
                tk_lbl = MathTex(lbl, font_size=9, color="#64748b").next_to(tk_line, DOWN, buff=0.14)
                ticks_g3.add(tk_line, tk_lbl)

            cartesian3 = VGroup(base_line3, axis_x3, axis_y3, lbl_x3, lbl_y3, ticks_g3)

            trail3 = VMobject(stroke_width=2.5, fill_opacity=0.0)
            trail3.set_points_as_corners([np.array([x_origin, y3, 0]), np.array([x_origin + 0.001, y3, 0])])
            trail3.set_color_by_gradient("#f43f5e", "#ec4899", "#a855f7")
            cursor3 = Dot(np.array([x_origin, y3, 0]), radius=0.065, color=WHITE)
            halo3 = Circle(radius=0.12, color="#f43f5e", stroke_width=1.4)
            proj_line3 = DashedLine(np.array([x_phasor + r_o1 + r_o2, y3, 0]), np.array([x_origin, y3, 0]), dash_length=0.08, dashed_ratio=0.5, color="#f43f5e", stroke_width=1.2)

            # ----------------------------------------------------
            # 4. Assembly of Scene Graph
            # ----------------------------------------------------
            self.add(top_group)
            self.add(bottom_group)

            # Add Track 1
            self.add(card1, contour_c1, guide_c1, arm1_c1, dot_c1)
            self.add(cartesian1, trail1, proj_line1, cursor1, halo1)

            # Add Track 2
            self.add(card2, contour_c2, guide_s1, guide_s2, arm1_c2, arm2_c2, dot_c2)
            self.add(cartesian2, trail2, proj_line2, cursor2, halo2)

            # Add Track 3
            self.add(card3, contour_c3, guide_o1, guide_o2, arm1_c3, arm2_c3, dot_c3)
            self.add(cartesian3, trail3, proj_line3, cursor3, halo3)

            # ----------------------------------------------------
            # 5. Continuous Real-Time Animation Updater (Analytical Curves)
            # ----------------------------------------------------
            t_tracker = ValueTracker(0.0)

            # Total duration of active drawing = 20.0 seconds
            T_draw = 20.0
            T_max_angle = 4.0 * np.pi  # 2 complete wavelengths

            def update_three_tracks(mob):
                t_raw = t_tracker.get_value()
                # Phase angle from 0 to 4*pi
                theta = max((t_raw / T_draw) * T_max_angle, 0.002)

                # Number of sample points proportional to progress
                n_pts = max(int(theta * 32), 4)
                t_arr = np.linspace(0, theta, n_pts)
                x_arr = x_origin + (t_arr / T_max_angle) * L_draw

                # ================= Track 1: Círculo =================
                p_c_orig = np.array([x_phasor, y1, 0])
                tip1 = p_c_orig + np.array([r_phasor * np.cos(theta), r_phasor * np.sin(theta), 0])
                arm1_c1.put_start_and_end_on(p_c_orig, tip1)
                dot_c1.move_to(tip1)

                pts1 = [np.array([x, y1 + r_phasor * np.sin(t), 0]) for x, t in zip(x_arr, t_arr)]
                trail1.set_points_smoothly(pts1)
                trail1.set_fill(opacity=0.0)

                w1_pos = pts1[-1]
                cursor1.move_to(w1_pos)
                halo1.move_to(w1_pos)
                proj_line1.put_start_and_end_on(tip1, w1_pos)

                # ================= Track 2: Estrella =================
                p_s_orig = np.array([x_phasor, y2, 0])
                tip2_base = p_s_orig + np.array([r_s1 * np.cos(theta), r_s1 * np.sin(theta), 0])
                tip2 = tip2_base + np.array([r_s2 * np.cos(-4 * theta), r_s2 * np.sin(-4 * theta), 0]) + np.array([r_s3 * np.cos(6 * theta), r_s3 * np.sin(6 * theta), 0])

                arm1_c2.put_start_and_end_on(p_s_orig, tip2_base)
                arm2_c2.put_start_and_end_on(tip2_base, tip2)
                guide_s2.move_to(tip2_base)
                dot_c2.move_to(tip2)

                pts2 = [np.array([x, y2 + r_s1 * np.sin(t) + r_s2 * np.sin(-4 * t) + r_s3 * np.sin(6 * t), 0]) for x, t in zip(x_arr, t_arr)]
                trail2.set_points_smoothly(pts2)
                trail2.set_color_by_gradient("#fbbf24", "#f59e0b", "#ef4444")
                trail2.set_fill(opacity=0.0)

                w2_pos = pts2[-1]
                cursor2.move_to(w2_pos)
                halo2.move_to(w2_pos)
                proj_line2.put_start_and_end_on(tip2, w2_pos)

                # ================= Track 3: Octógono =================
                p_o_orig = np.array([x_phasor, y3, 0])
                tip3_base = p_o_orig + np.array([r_o1 * np.cos(theta), r_o1 * np.sin(theta), 0])
                tip3 = tip3_base + np.array([r_o2 * np.cos(-7 * theta), r_o2 * np.sin(-7 * theta), 0]) + np.array([r_o3 * np.cos(9 * theta), r_o3 * np.sin(9 * theta), 0])

                arm1_c3.put_start_and_end_on(p_o_orig, tip3_base)
                arm2_c3.put_start_and_end_on(tip3_base, tip3)
                guide_o2.move_to(tip3_base)
                dot_c3.move_to(tip3)

                pts3 = [np.array([x, y3 + r_o1 * np.sin(t) + r_o2 * np.sin(-7 * t) + r_o3 * np.sin(9 * t), 0]) for x, t in zip(x_arr, t_arr)]
                trail3.set_points_smoothly(pts3)
                trail3.set_color_by_gradient("#f43f5e", "#ec4899", "#a855f7")
                trail3.set_fill(opacity=0.0)

                w3_pos = pts3[-1]
                cursor3.move_to(w3_pos)
                halo3.move_to(w3_pos)
                proj_line3.put_start_and_end_on(tip3, w3_pos)

            # Bind updater to master object
            arm1_c1.add_updater(update_three_tracks)

            # Run smooth continuous animation for 20.0 seconds
            self.play(
                t_tracker.animate.set_value(20.0),
                run_time=20.0,
                rate_func=linear
            )

            # Hold final state for 2.0 seconds so viewers can admire the full waveforms
            self.wait(2.0)

    return FourierWaveScene


class FourierWaveSceneES(create_fourier_wave_scene("ES")):
    pass


class FourierWaveSceneEN(create_fourier_wave_scene("EN")):
    pass


def render_all():
    base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    renders_dir = base_dir / "RENDERS" / "3 Series de Fourier Geometricas"
    videos_dir = renders_dir / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)

    # 1. Synthesize Catchy Lo-Fi Science Background Music (23.5 seconds)
    temp_audio_path = str(videos_dir / "fourier_music_bg.wav")
    print("[CONTINUUM LAB] Synthesizing gentle lo-fi background music...")
    synthesize_fourier_background_music(duration=23.5, fs=44100, output_path=temp_audio_path)

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    this_script = str(Path(__file__).resolve())

    # 2. Render Spanish Version
    print("\n=======================================================")
    print("[CONTINUUM LAB] Rendering Spanish Cartesian Wave Video (ES)...")
    print("=======================================================")
    cmd_manim_es = [
        "manim", "-qh", "--media_dir", str(videos_dir / "temp_media"),
        this_script, "FourierWaveSceneES"
    ]
    subprocess.run(cmd_manim_es, check=True)

    raw_es = list((videos_dir / "temp_media").rglob("FourierWaveSceneES.mp4"))[0]
    out_es = str(videos_dir / "Series de Fourier Geometricas ES.mp4")

    print(f"[CONTINUUM LAB] Multiplexing ES Audio + Video -> {out_es}")
    cmd_mux_es = [
        ffmpeg_bin, "-y", "-i", str(raw_es), "-i", temp_audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_es
    ]
    subprocess.run(cmd_mux_es, check=True)

    # 3. Render English Version
    print("\n=======================================================")
    print("[CONTINUUM LAB] Rendering English Cartesian Wave Video (EN)...")
    print("=======================================================")
    cmd_manim_en = [
        "manim", "-qh", "--media_dir", str(videos_dir / "temp_media"),
        this_script, "FourierWaveSceneEN"
    ]
    subprocess.run(cmd_manim_en, check=True)

    raw_en = list((videos_dir / "temp_media").rglob("FourierWaveSceneEN.mp4"))[0]
    out_en = str(videos_dir / "Geometric Fourier Series EN.mp4")

    print(f"[CONTINUUM LAB] Multiplexing EN Audio + Video -> {out_en}")
    cmd_mux_en = [
        ffmpeg_bin, "-y", "-i", str(raw_en), "-i", temp_audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_en
    ]
    subprocess.run(cmd_mux_en, check=True)

    # 4. Extract HD hero thumbnail (at 18.0s when waves are fully developed along +X)
    out_png = str(renders_dir / "extra" / "capturas" / "fourier_shapes_hero.png")
    cmd_snap = [ffmpeg_bin, "-y", "-ss", "00:00:18.00", "-i", out_es, "-vframes", "1", out_png]
    subprocess.run(cmd_snap, check=True)
    print(f"[CONTINUUM LAB] Updated hero capture -> {out_png}")

    # Cleanup temp media
    import shutil
    if os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)
    shutil.rmtree(str(videos_dir / "temp_media"), ignore_errors=True)

    print("\n=======================================================")
    print("[CONTINUUM LAB] ALL 3-TRACK CARTESIAN FOURIER VIDEOS DELIVERED SUCCESSFULLY!")
    print(f"  - Spanish: {out_es}")
    print(f"  - English: {out_en}")
    print(f"  - Capture: {out_png}")
    print("=======================================================")


if __name__ == "__main__":
    render_all()
