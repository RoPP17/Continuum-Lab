"""
Continuum Lab — Classical Mechanics & Dynamical Systems
Division: 02 Dinamica y Vibraciones / 04 Efecto Dzhanibekov 3D
Module: 3D Ultra-HD Manim Community Scene (9:16 Vertical, 1080x1920 @ 60 FPS)

Efecto Dzhanibekov / Teorema de la Raqueta de Tenis / Inestabilidad de Euler
- Exact Euler equations integrated via DOP853.
- Metallic aerospace T-handle rigid body in microgravity.
- Strict conservation of Angular Momentum (|L| = const) and Energy (T_rot = const).
- Poinsot Inertia Ellipsoid wireframe tumbling synchronously.
- Stationary space angular momentum vector (L) vs flipping angular velocity vector (w).
- Full 9:16 Safe Zones HUD with telemetry and dynamic state banners.
- Zero slow LaTeX calls in animation loop.
"""

from manim import *
import numpy as np
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.physics.euler_rigid_body import RigidBodyParams, RigidBodySimulator

# Exact 9:16 Vertical Video Configuration (1080x1920 @ 60 FPS)
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#0B0F19"  # Deep Aerospace Void


def create_dzhanibekov_scene_class(lang: str = "ES"):
    """Creates a localized 3D Manim scene for the Dzhanibekov Effect."""

    class LocalizedDzhanibekovScene(ThreeDScene):
        """
        Ultra-HD 3D Cinematic Simulation of the Dzhanibekov Effect in microgravity.
        Duration: 14.0 seconds (840 frames @ 60 FPS).
        """

        def construct(self):
            # =====================================================================
            # 1. Theoretical Physics Precomputation (DOP853 8th Order RK)
            # =====================================================================
            params = RigidBodyParams(I1=1.0, I2=2.4, I3=4.2)
            sim = RigidBodySimulator(params)

            fps = 60
            total_time = 14.0
            total_frames = int(round(total_time * fps)) + 1

            # Run simulation with optimal perturbation
            sim_data = sim.simulate(t_span=(0.0, total_time), fps=fps, method="DOP853")
            rot_matrices = sim_data["rot_matrices"]
            omega_body = sim_data["omega_body"]
            omega_space = sim_data["omega_space"]
            num_steps = len(rot_matrices)

            # =====================================================================
            # 2. Camera Setup & Spatial Environment
            # =====================================================================
            self.set_camera_orientation(phi=72 * DEGREES, theta=-45 * DEGREES, gamma=0)
            self.begin_ambient_camera_rotation(rate=0.035)

            # Spatial reference rings (subtle aerospace orbital plane)
            ref_rings = Group(*[
                ParametricFunction(
                    lambda u, r=r: np.array([r * np.cos(u), -2.6, r * np.sin(u)]),
                    t_range=[0, TAU],
                    color="#1E293B",
                    stroke_width=0.9,
                    stroke_opacity=0.35
                ) for r in [1.2, 2.2, 3.2]
            ])
            ref_axes = Group(
                Line(start=[-3.2, 0, 0], end=[3.2, 0, 0], color="#1E293B", stroke_width=0.6, stroke_opacity=0.25).shift(DOWN * 2.6),
                Line(start=[0, 0, -3.2], end=[0, 0, 3.2], color="#1E293B", stroke_width=0.6, stroke_opacity=0.25).shift(DOWN * 2.6)
            )
            self.add(ref_rings, ref_axes)

            # =====================================================================
            # 3. High-Detail Aerospace 3D T-Handle Geometry (Solid Metallic Finish)
            # =====================================================================
            # Shaft along intermediate axis (Y)
            stem = Cylinder(radius=0.10, height=2.4, direction=UP, color="#94A3B8", fill_opacity=0.90, checkerboard_colors=False)

            # Crossbar along major axis (Z)
            crossbar = Cylinder(radius=0.09, height=1.8, direction=OUT, color="#CBD5E1", fill_opacity=0.90, checkerboard_colors=False).shift(UP * 0.7)

            # Central mounting hex collar
            hex_collar = Cylinder(radius=0.22, height=0.32, direction=UP, color="#475569", fill_opacity=0.95, checkerboard_colors=False).shift(UP * 0.7)

            # Knurled rings along stem
            ring1 = Cylinder(radius=0.13, height=0.06, direction=UP, color="#64748B", fill_opacity=0.95, checkerboard_colors=False).shift(DOWN * 0.4)
            ring2 = Cylinder(radius=0.13, height=0.06, direction=UP, color="#64748B", fill_opacity=0.95, checkerboard_colors=False).shift(DOWN * 0.8)
            bottom_cap = Sphere(radius=0.14, color="#D97706", fill_opacity=0.95, checkerboard_colors=False).shift(DOWN * 1.2)

            # Asymmetric Wingtips (Gold vs Cyan) to make the 180 deg flip vividly clear
            tip_gold = Sphere(radius=0.18, color="#FFB800", fill_opacity=0.95, checkerboard_colors=False).shift(UP * 0.7 + OUT * 0.9)
            tip_cyan = Sphere(radius=0.18, color="#00F0FF", fill_opacity=0.95, checkerboard_colors=False).shift(UP * 0.7 + IN * 0.9)

            t_handle = Group(stem, crossbar, hex_collar, ring1, ring2, bottom_cap, tip_gold, tip_cyan)
            t_handle_orig_pts = {sm: sm.points.copy() for sm in t_handle.get_family() if len(sm.points) > 0}
            self.add(t_handle)

            # =====================================================================
            # 4. Poinsot Inertia Ellipsoid Wireframe
            # Semi-axes: I1*x^2 + I2*y^2 + I3*z^2 = 2T -> a > b > c
            # =====================================================================
            scale_ell = 1.35
            a_ell = scale_ell * np.sqrt(2.4 / 1.0)  # ~2.09
            b_ell = scale_ell * 1.0                 # ~1.35
            c_ell = scale_ell * np.sqrt(2.4 / 4.2)  # ~1.02

            meridian_xy = ParametricFunction(
                lambda u: np.array([a_ell * np.cos(u), b_ell * np.sin(u), 0.0]),
                t_range=[0, TAU],
                color="#38BDF8",
                stroke_width=1.2,
                stroke_opacity=0.40
            )
            meridian_yz = ParametricFunction(
                lambda u: np.array([0.0, b_ell * np.sin(u), c_ell * np.cos(u)]),
                t_range=[0, TAU],
                color="#38BDF8",
                stroke_width=1.2,
                stroke_opacity=0.40
            )
            meridian_xz = ParametricFunction(
                lambda u: np.array([a_ell * np.cos(u), 0.0, c_ell * np.sin(u)]),
                t_range=[0, TAU],
                color="#38BDF8",
                stroke_width=1.2,
                stroke_opacity=0.40
            )
            lat_top = ParametricFunction(
                lambda u: np.array([a_ell * 0.714 * np.cos(u), b_ell * 0.70, c_ell * 0.714 * np.sin(u)]),
                t_range=[0, TAU],
                color="#0284C7",
                stroke_width=1.0,
                stroke_opacity=0.30
            )
            lat_bot = ParametricFunction(
                lambda u: np.array([a_ell * 0.714 * np.cos(u), -b_ell * 0.70, c_ell * 0.714 * np.sin(u)]),
                t_range=[0, TAU],
                color="#0284C7",
                stroke_width=1.0,
                stroke_opacity=0.30
            )

            poinsot_ellipsoid = Group(meridian_xy, meridian_yz, meridian_xz, lat_top, lat_bot)
            ellipsoid_orig_pts = {sm: sm.points.copy() for sm in poinsot_ellipsoid.get_family() if len(sm.points) > 0}
            self.add(poinsot_ellipsoid)

            # =====================================================================
            # 5. Angular Momentum Vector L (STRICTLY IMMOBILE in Space)
            # =====================================================================
            l_len = 3.0
            l_line = Line3D(start=ORIGIN, end=UP * l_len, color="#00F0FF", thickness=0.035)
            l_cone = Cone(base_radius=0.10, height=0.30, direction=UP, color="#00F0FF", fill_opacity=0.95, checkerboard_colors=False).shift(UP * l_len)
            l_group = Group(l_line, l_cone)
            self.add(l_group)

            # Vector w (Angular Velocity) in space
            w_len = 2.8
            w_line = Line3D(start=ORIGIN, end=UP * w_len, color="#FF0055", thickness=0.035)
            w_cone = Cone(base_radius=0.10, height=0.30, direction=UP, color="#FF0055", fill_opacity=0.95, checkerboard_colors=False).shift(UP * w_len)
            w_group = Group(w_line, w_cone)
            w_orig_pts = {sm: sm.points.copy() for sm in w_group.get_family() if len(sm.points) > 0}
            self.add(w_group)

            # =====================================================================
            # 6. Dynamic Tip Trail (Golden Wingtip Acrobatic Flip Path)
            # =====================================================================
            tip_trail = VMobject(color="#FFB800", stroke_width=2.2, stroke_opacity=0.65)
            self.add(tip_trail)
            tip_trail_pts = []

            # =====================================================================
            # 7. Safe Zones 2D HUD Overlay (Fixed in Frame)
            # Strict Anti-Microtext Rule: font_size >= 18 pt on all elements
            # =====================================================================
            top_card_bg = RoundedRectangle(
                corner_radius=0.16,
                width=8.0,
                height=2.85,
                color="#00F0FF",
                stroke_width=1.6,
                stroke_opacity=0.90,
                fill_color="#0D1117",
                fill_opacity=0.96
            ).move_to(UP * 5.15)

            title_str = "¿EL VOLTEO PROHIBIDO EN EL ESPACIO?" if lang == "ES" else "THE FORBIDDEN FLIP IN SPACE?"
            title_txt = Text(
                title_str,
                font="Consolas",
                font_size=24,
                weight=BOLD,
                color="#00F0FF"
            ).move_to(top_card_bg.get_top() + DOWN * 0.36)

            div_line = Line(
                start=top_card_bg.get_left() + RIGHT * 0.40,
                end=top_card_bg.get_right() + LEFT * 0.40,
                color="#1E293B",
                stroke_width=1.5
            ).move_to(top_card_bg.get_top() + DOWN * 0.70)

            # High-legibility telemetry lines (18 pt)
            if lang == "ES":
                row1_str = "INERCIA  : I1 < I2 < I3 (SADDLE INESTABLE)"
                row2_str = "TORQUE   : tau = 0.00 N·m (MICROGRAVEDAD)"
                row3_str = "ENERGIA  : E = 172.8 J  |  |L| = 28.8 N·m·s"
            else:
                row1_str = "INERTIA  : I1 < I2 < I3 (SADDLE UNSTABLE)"
                row2_str = "TORQUE   : tau = 0.00 N·m (ZERO GRAVITY)"
                row3_str = "ENERGY   : E = 172.8 J  |  |L| = 28.8 N·m·s"

            row1_txt = Text(row1_str, font="Consolas", font_size=18, color="#00F0FF").next_to(div_line, DOWN, buff=0.14).align_to(div_line, LEFT)
            row2_txt = Text(row2_str, font="Consolas", font_size=18, color="#E2E8F0").next_to(row1_txt, DOWN, buff=0.10).align_to(div_line, LEFT)
            row3_txt = Text(row3_str, font="Consolas", font_size=18, color="#38BDF8").next_to(row2_txt, DOWN, buff=0.10).align_to(div_line, LEFT)

            # Dynamic State Banners (18 pt Bold, Positioned with safe clearance)
            banner_pos = top_card_bg.get_bottom() + UP * 0.35
            if lang == "ES":
                b_p1 = Text("● FASE 1: GIRO EJE INTERMEDIO", font="Consolas", font_size=18, weight=BOLD, color="#00F0FF").move_to(banner_pos)
                b_p2 = Text("▲ FASE 2: >> FLIP ACROBATICO 180° <<", font="Consolas", font_size=18, weight=BOLD, color="#FF0055").move_to(banner_pos)
                b_p3 = Text("● FASE 3: ROTACION INVERTIDA (-Y)", font="Consolas", font_size=18, weight=BOLD, color="#FFB800").move_to(banner_pos)
                b_p4 = Text("▲ FASE 4: >> SEGUNDO FLIP (REVERSION) <<", font="Consolas", font_size=18, weight=BOLD, color="#FF0055").move_to(banner_pos)
                b_p5 = Text("● FASE 5: ORBITA HOMOCLINICA CERRADA", font="Consolas", font_size=18, weight=BOLD, color="#00F0FF").move_to(banner_pos)
            else:
                b_p1 = Text("● PHASE 1: INTERMEDIATE AXIS SPIN", font="Consolas", font_size=18, weight=BOLD, color="#00F0FF").move_to(banner_pos)
                b_p2 = Text("▲ PHASE 2: >> 180° HOMOCLINIC FLIP <<", font="Consolas", font_size=18, weight=BOLD, color="#FF0055").move_to(banner_pos)
                b_p3 = Text("● PHASE 3: INVERTED (-Y) ROTATION", font="Consolas", font_size=18, weight=BOLD, color="#FFB800").move_to(banner_pos)
                b_p4 = Text("▲ PHASE 4: >> 180° REVERSION FLIP <<", font="Consolas", font_size=18, weight=BOLD, color="#FF0055").move_to(banner_pos)
                b_p5 = Text("● PHASE 5: CLOSED HOMOCLINIC ORBIT", font="Consolas", font_size=18, weight=BOLD, color="#00F0FF").move_to(banner_pos)

            b_p2.set_opacity(0.0)
            b_p3.set_opacity(0.0)
            b_p4.set_opacity(0.0)
            b_p5.set_opacity(0.0)

            top_hud = VGroup(top_card_bg, title_txt, div_line, row1_txt, row2_txt, row3_txt, b_p1, b_p2, b_p3, b_p4, b_p5)
            self.add_fixed_in_frame_mobjects(top_hud)

            # --- Vector Legend Badges (Under Top HUD) ---
            legend_bg = RoundedRectangle(
                corner_radius=0.10,
                width=8.0,
                height=0.62,
                color="#1E293B",
                stroke_width=1.2,
                fill_color="#0D1117",
                fill_opacity=0.92
            ).move_to(UP * 3.30)

            leg_str = (
                "■ L (Cian): Inmóvil   ■ w (Rojo): Volteo"
                if lang == "ES" else
                "■ L (Cyan): Stationary   ■ w (Red): Tumbling"
            )
            legend_txt = Text(
                leg_str,
                font="Consolas",
                font_size=18,
                weight=BOLD,
                color="#CBD5E1"
            ).move_to(legend_bg)

            legend_group = VGroup(legend_bg, legend_txt)
            self.add_fixed_in_frame_mobjects(legend_group)

            # --- Lower Callout Card (Bottom Safe Zone > 320 px) ---
            bot_card_bg = RoundedRectangle(
                corner_radius=0.16,
                width=8.0,
                height=1.85,
                color="#38BDF8",
                stroke_width=1.6,
                stroke_opacity=0.88,
                fill_color="#0D1117",
                fill_opacity=0.96
            ).move_to(DOWN * 4.30)

            if lang == "ES":
                call_title_str = "SIN FUERZA NI TORQUE EXTERNO"
                call_body_str = "Se voltea 180° por pura geometría de fases."
                subtitle_str = "ECUACIONES DE EULER // SEPARATRIZ POINSOT"
            else:
                call_title_str = "NO EXTERNAL FORCE OR TORQUE"
                call_body_str = "Flips 180° purely from phase-space geometry."
                subtitle_str = "EULER EQUATIONS // POINSOT SEPARATRIX"

            call_title_txt = Text(
                call_title_str,
                font="Consolas",
                font_size=20,
                weight=BOLD,
                color="#FFE600"
            ).move_to(bot_card_bg.get_top() + DOWN * 0.40)

            call_body_txt = Text(
                call_body_str,
                font="Consolas",
                font_size=18,
                color="#F8FAFC"
            ).next_to(call_title_txt, DOWN, buff=0.15)

            subtitle_txt = Text(
                subtitle_str,
                font="Consolas",
                font_size=18,
                weight=BOLD,
                color="#00F0FF"
            ).next_to(call_body_txt, DOWN, buff=0.15)

            bot_hud = VGroup(bot_card_bg, call_title_txt, call_body_txt, subtitle_txt)
            self.add_fixed_in_frame_mobjects(bot_hud)

            # =====================================================================
            # 8. High-Performance Frame Updater
            # =====================================================================
            time_tracker = ValueTracker(0.0)

            def update_frame(dt):
                t = time_tracker.get_value()
                k = int(round(t * fps))
                k = min(max(k, 0), num_steps - 1)

                R = rot_matrices[k]

                # 1. Rotate 3D T-handle
                for sm, base_pts in t_handle_orig_pts.items():
                    sm.points = base_pts @ R.T

                # 2. Rotate Poinsot Ellipsoid
                for sm, base_pts in ellipsoid_orig_pts.items():
                    sm.points = base_pts @ R.T

                # 3. Update Vector w (Angular velocity direction in space)
                ws = omega_space[k]
                ws_norm = np.linalg.norm(ws)
                if ws_norm > 1e-4:
                    ws_dir = ws / ws_norm
                    v_init = np.array([0.0, 1.0, 0.0])
                    v_axis = np.cross(v_init, ws_dir)
                    axis_norm = np.linalg.norm(v_axis)
                    if axis_norm < 1e-8:
                        R_align = np.eye(3) if np.dot(v_init, ws_dir) > 0 else -np.eye(3)
                    else:
                        v_axis = v_axis / axis_norm
                        ang = np.arccos(np.clip(np.dot(v_init, ws_dir), -1.0, 1.0))
                        K = np.array([
                            [0.0, -v_axis[2], v_axis[1]],
                            [v_axis[2], 0.0, -v_axis[0]],
                            [-v_axis[1], v_axis[0], 0.0]
                        ])
                        R_align = np.eye(3) + np.sin(ang) * K + (1.0 - np.cos(ang)) * (K @ K)

                    for sm, pts in w_orig_pts.items():
                        sm.points = pts @ R_align.T

                # 4. Update Tip Trail
                gold_tip_body = np.array([0.0, 0.7, 0.9])
                gold_tip_space = R @ gold_tip_body
                tip_trail_pts.append(gold_tip_space)
                if len(tip_trail_pts) > 150:
                    tip_trail_pts.pop(0)
                if len(tip_trail_pts) >= 2:
                    tip_trail.set_points_as_corners(tip_trail_pts)

                # 5. Dynamic State Banners (Zero LaTeX Overhead)
                b_p1.set_opacity(1.0 if t < 3.5 else 0.0)
                b_p2.set_opacity(1.0 if 3.5 <= t < 5.0 else 0.0)
                b_p3.set_opacity(1.0 if 5.0 <= t < 8.5 else 0.0)
                b_p4.set_opacity(1.0 if 8.5 <= t < 10.0 else 0.0)
                b_p5.set_opacity(1.0 if t >= 10.0 else 0.0)

            t_handle.add_updater(lambda m, dt: update_frame(dt))

            # =====================================================================
            # 9. Play 14.0 Seconds Animation
            # =====================================================================
            self.play(
                time_tracker.animate.set_value(total_time),
                run_time=total_time,
                rate_func=linear
            )
            t_handle.clear_updaters()
            self.wait(0.2)

    return LocalizedDzhanibekovScene


class DzhanibekovSceneES(create_dzhanibekov_scene_class(lang="ES")):
    pass


class DzhanibekovSceneEN(create_dzhanibekov_scene_class(lang="EN")):
    pass


# Backward compatibility
class DzhanibekovScene(DzhanibekovSceneES):
    pass
