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


class DzhanibekovScene(ThreeDScene):
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
        # Vector L in space is along +Y: strictly conserved in microgravity
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
        # Safe Zones: Top > 160 px, Bottom > 320 px, Right Margin > 130 px
        # =====================================================================
        # --- Top HUD Telemetry Card (Consolas, Aerospace Console Aesthetic) ---
        top_card_bg = RoundedRectangle(
            corner_radius=0.14,
            width=7.8,
            height=2.3,
            color="#00F0FF",
            stroke_width=1.5,
            stroke_opacity=0.85,
            fill_color="#0D1117",
            fill_opacity=0.95
        ).move_to(UP * 5.5)

        title_txt = Text(
            "CONTINUUM LAB // TEOREMA DE LA RAQUETA DE TENIS",
            font="Consolas",
            font_size=17,
            weight=BOLD,
            color="#00F0FF"
        ).move_to(top_card_bg.get_top() + DOWN * 0.32)

        div_line = Line(
            start=top_card_bg.get_left() + RIGHT * 0.35,
            end=top_card_bg.get_right() + LEFT * 0.35,
            color="#1E293B",
            stroke_width=1.2
        ).move_to(top_card_bg.get_top() + DOWN * 0.58)

        # Monospaced parameter lines
        col1_txt = Text(
            "INERCIA       : I1=1.0 < I2=2.4 < I3=4.2 kg·m²\n"
            "EJE INTERMEDIO: ESTADO HIPERBÓLICO INESTABLE",
            font="Consolas",
            font_size=13.5,
            line_spacing=1.3,
            color="#E2E8F0"
        ).next_to(div_line, DOWN, buff=0.15).align_to(div_line, LEFT)

        col2_txt = Text(
            "TORQUE EXTERNO: tau = 0.00 N·m (MICROGRAVEDAD)\n"
            "CONSERVACIÓN  : |L| = 28.80 N·m·s  |  E_rot = 172.8 J",
            font="Consolas",
            font_size=13.5,
            line_spacing=1.3,
            color="#38BDF8"
        ).next_to(col1_txt, DOWN, buff=0.12).align_to(div_line, LEFT)

        # Dynamic State Banners (Pre-created to eliminate LaTeX overhead)
        banner_pos = top_card_bg.get_bottom() + UP * 0.32
        b_p1 = Text("[●] FASE 1: GIRO CUASI-ESTABLE EN EJE INTERMEDIO", font="Consolas", font_size=13, weight=BOLD, color="#00F0FF").move_to(banner_pos)
        b_p2 = Text("[▲] FASE 2: >> FLIP HOMOCLÍNICO ACROBÁTICO (180°) <<", font="Consolas", font_size=13, weight=BOLD, color="#FF0055").move_to(banner_pos)
        b_p3 = Text("[●] FASE 3: ROTACIÓN INVERTIDA (-Y) ESTABLE", font="Consolas", font_size=13, weight=BOLD, color="#FFB800").move_to(banner_pos)
        b_p4 = Text("[▲] FASE 4: >> SEGUNDO FLIP HOMOCLÍNICO (REVERSIÓN) <<", font="Consolas", font_size=13, weight=BOLD, color="#FF0055").move_to(banner_pos)
        b_p5 = Text("[●] FASE 5: CICLO DE FASE PERIÓDICO RESTABLECIDO", font="Consolas", font_size=13, weight=BOLD, color="#00F0FF").move_to(banner_pos)

        b_p2.set_opacity(0.0)
        b_p3.set_opacity(0.0)
        b_p4.set_opacity(0.0)
        b_p5.set_opacity(0.0)

        top_hud = VGroup(top_card_bg, title_txt, div_line, col1_txt, col2_txt, b_p1, b_p2, b_p3, b_p4, b_p5)
        self.add_fixed_in_frame_mobjects(top_hud)

        # --- Vector Legend Badges (Under HUD) ---
        legend_bg = RoundedRectangle(
            corner_radius=0.08,
            width=7.8,
            height=0.52,
            color="#1E293B",
            stroke_width=1.0,
            fill_color="#0D1117",
            fill_opacity=0.90
        ).move_to(UP * 3.9)

        legend_txt = Text(
            "■ L (Cian): Momento Angular [INMÓVIL]    ■ w (Carmesí): Velocidad Angular [FLIP]",
            font="Consolas",
            font_size=12.5,
            color="#CBD5E1"
        ).move_to(legend_bg)
        
        legend_group = VGroup(legend_bg, legend_txt)
        self.add_fixed_in_frame_mobjects(legend_group)

        # --- Lower Callout Card (Bottom Safe Zone > 320 px) ---
        bot_card_bg = RoundedRectangle(
            corner_radius=0.14,
            width=7.8,
            height=1.55,
            color="#38BDF8",
            stroke_width=1.3,
            stroke_opacity=0.80,
            fill_color="#0D1117",
            fill_opacity=0.95
        ).move_to(DOWN * 4.7)

        dilemma_txt = Text(
            "\"SIN CONTACTO NI FUERZA EXTERNA.\n"
            "EL CUERPO SE VOLTEA 180° POR PURA GEOMETRÍA DEL ESPACIO DE FASES.\"",
            font="Segoe UI",
            font_size=14,
            weight=BOLD,
            color="#F8FAFC",
            line_spacing=1.25
        ).move_to(bot_card_bg.get_top() + DOWN * 0.55)

        subtitle_txt = Text(
            "MECÁNICA CLÁSICA // SEPARATRIZ HOMOCLÍNICA DE POINSOT",
            font="Consolas",
            font_size=11.5,
            weight=BOLD,
            color="#00F0FF"
        ).move_to(bot_card_bg.get_bottom() + UP * 0.30)

        bot_hud = VGroup(bot_card_bg, dilemma_txt, subtitle_txt)
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
                # Rotation matrix aligning UP (0, 1, 0) to ws_dir
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

        # Attach updater to the scene
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
