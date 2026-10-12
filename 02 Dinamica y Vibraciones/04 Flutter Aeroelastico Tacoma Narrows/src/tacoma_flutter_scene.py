"""
Continuum Lab — Classical Mechanics & Aeroelastic Dynamics
Scene: Tacoma Narrows Bridge Torsional Aeroelastic Flutter (Ultra-HD 1080x1920 60 FPS, 9:16 Vertical)
Division: 02 Dinamica y Vibraciones / 04 Flutter Aeroelastico Tacoma Narrows

Rigorous Aeroelastic Simulation & Scientific Visualization:
1. Exact coupled 2-DOF flutter dynamics precomputed via Scipy solve_ivp (RK45)
2. Scanlan unsteady aerodynamics with negative aerodynamic damping A2* > 0 (zeta_aero = -0.042)
3. 2.5D Transversal Isometric View of the H-girder bridge deck and suspension system
4. Dynamic fluid field with streamlines and alternating von Kármán / Lamb-Oseen vortices
   (Cyan for clockwise omega_z < 0, Magenta for counter-clockwise omega_z > 0)
5. Dynamic aerodynamic force vectors (Lift L and Moment M) showing 90-degree energy injection phase
6. Suspender cables with asymmetric slackening and plastic yielding (T > T_yield)
7. Real-time telemetry HUD formatted with Consolas monospace typography
8. Strict mobile safe zones (Top > 160 px, Bottom > 320 px)
9. Three dramatic phases:
   - Phase 1 (0.0s - 4.0s): Moderate wind U = 25 km/h, vertical bending, alpha ~ 0
   - Phase 2 (4.0s - 8.5s): Flutter bifurcation ramp U = 68 km/h, lock-in resonance
   - Phase 3 (8.5s - 15.0s): DRAMA: Violent torsional collapse limit cycle (alpha = +/- 38.4 deg)
"""

import sys
from pathlib import Path
import numpy as np
from manim import *

# Pre-configure Manim settings for 1080x1920 9:16 vertical resolution
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#060A13"

# Ensure project modules are importable
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.physics import (
    TacomaConfig,
    TacomaSolution,
    solve_tacoma_dynamics,
)


class TacomaFlutterSceneBase(Scene):
    """
    Ultra-HD 1080x1920 60 FPS 9:16 Vertical Manim Community Scene
    modeling the Torsional Aeroelastic Flutter of the Tacoma Narrows Bridge.
    """
    lang = "ES"

    def construct(self):
        lang = getattr(self, "lang", "ES")
        # Precompute exact physical solution decoupled from renderer
        phys_cfg = TacomaConfig()
        sol: TacomaSolution = solve_tacoma_dynamics(phys_cfg)

        # Time tracker variable (0.0 to 15.0 s)
        time_tracker = ValueTracker(0.0)

        # Helper interpolation function
        def get_frame_idx(t: float) -> int:
            idx = int(np.clip(t * phys_cfg.fps, 0, sol.n_frames - 1))
            return idx

        # -------------------------------------------------------------
        # 1. Engineering Coordinate Atmosphere
        # -------------------------------------------------------------
        grid_lines = VGroup()
        for x in np.arange(-4.0, 4.5, 1.0):
            grid_lines.add(
                Line(
                    start=[x, -7.6, 0],
                    end=[x, 7.6, 0],
                    stroke_color="#1E293B",
                    stroke_width=0.6,
                    stroke_opacity=0.25,
                )
            )
        for y in np.arange(-7.2, 7.6, 1.0):
            grid_lines.add(
                Line(
                    start=[-4.2, y, 0],
                    end=[4.2, y, 0],
                    stroke_color="#1E293B",
                    stroke_width=0.6,
                    stroke_opacity=0.25,
                )
            )
        self.add(grid_lines)

        # -------------------------------------------------------------
        # 2. Header & Branding (Safe Zone: y in [5.1, 6.45])
        # -------------------------------------------------------------
        hook_str = "¿POR QUÉ COLAPSÓ EL PUENTE TACOMA?" if lang == "ES" else "WHY DID THE TACOMA BRIDGE COLLAPSE?"
        brand_badge = Text(
            hook_str,
            font="Arial",
            weight=BOLD,
            font_size=17,
            color="#38BDF8",
        ).move_to([0.0, 6.35, 0.0])

        title_str = "ALETEO TORSIONAL (FLUTTER)" if lang == "ES" else "TORSIONAL FLUTTER"
        main_title = Text(
            title_str,
            font="Arial",
            weight=BOLD,
            font_size=21,
            color="#FFFFFF",
        ).move_to([0.0, 5.90, 0.0])

        sub_str = "Vórtices inducen torsión y resonancia inestable (1940)" if lang == "ES" else "Unsteady vortices drive unstable torsional resonance (1940)"
        case_subtitle = Text(
            sub_str,
            font="Consolas",
            font_size=10.5,
            color="#F59E0B",
        ).move_to([0.0, 5.50, 0.0])

        header_divider = Line(
            start=[-4.1, 5.25, 0],
            end=[4.1, 5.25, 0],
            stroke_color="#334155",
            stroke_width=1.2,
            stroke_opacity=0.75,
        )
        brand_badge.set_z_index(30)
        main_title.set_z_index(30)
        case_subtitle.set_z_index(30)
        header_divider.set_z_index(30)
        self.add(brand_badge, main_title, case_subtitle, header_divider)

        # -------------------------------------------------------------
        # 3. Aeroelastic Stage: Structure Constants
        # -------------------------------------------------------------
        y_deck_rest = 1.35
        b_screen = 2.45        # Half-width in screen units
        girder_h = 1.05        # Girder web height
        girder_w = 0.15        # Girder web thickness
        flange_w = 0.38        # Flange width
        flange_h = 0.06        # Flange thickness
        
        # Isometric depth vector for 2.5D transversal perspective
        v_depth = np.array([0.85, 0.52, 0.0])

        # Main Cable Arch & Saddles (Fixed tower structure)
        saddle_front_l = np.array([-b_screen, 4.40, 0.0])
        saddle_front_r = np.array([b_screen, 4.40, 0.0])
        saddle_back_l = saddle_front_l + v_depth
        saddle_back_r = saddle_front_r + v_depth

        # Rear main cable
        cable_rear = ParametricFunction(
            lambda s: np.array([s, 4.40 + 0.14 * (( (s - v_depth[0]) / b_screen) ** 2 - 1.0) + v_depth[1], 0.0]),
            t_range=[-3.0 + v_depth[0], 3.0 + v_depth[0]],
            stroke_color="#334155",
            stroke_width=2.5,
            stroke_opacity=0.6,
        )
        # Front main cable
        cable_front = ParametricFunction(
            lambda s: np.array([s, 4.40 + 0.14 * ((s / b_screen) ** 2 - 1.0), 0.0]),
            t_range=[-3.6, 3.6],
            stroke_color="#64748B",
            stroke_width=3.2,
        )

        saddle_dot_l = Dot(point=saddle_front_l, radius=0.07, color="#94A3B8")
        saddle_dot_r = Dot(point=saddle_front_r, radius=0.07, color="#94A3B8")
        saddle_lbl_l = Text("TORRE W" if lang == "ES" else "TOWER W", font="Consolas", font_size=8, color="#64748B").next_to(saddle_front_l, UP, buff=0.1)
        saddle_lbl_r = Text("TORRE E" if lang == "ES" else "TOWER E", font="Consolas", font_size=8, color="#64748B").next_to(saddle_front_r, UP, buff=0.1)

        # Baseline horizontal reference axis
        deck_ref_axis = DashedLine(
            start=[-3.2, y_deck_rest, 0],
            end=[3.2, y_deck_rest, 0],
            stroke_color="#1E293B",
            stroke_width=1.0,
            dash_length=0.14,
        )
        self.add(cable_rear, cable_front, saddle_dot_l, saddle_dot_r, saddle_lbl_l, saddle_lbl_r, deck_ref_axis)

        # -------------------------------------------------------------
        # 4. Helper Kinematics Transformation Function
        # -------------------------------------------------------------
        def get_kinematics(t_curr: float):
            idx = get_frame_idx(t_curr)
            h_m = sol.h[idx]
            alpha_rad = sol.alpha[idx]
            alpha_deg = sol.alpha_deg[idx]
            
            # Scaled vertical displacement centered in aeroelastic stage
            y_c = y_deck_rest + 0.40 * h_m
            center_front = np.array([0.0, y_c, 0.0])
            center_back = center_front + v_depth

            cos_a = np.cos(alpha_rad)
            sin_a = np.sin(alpha_rad)

            def rot_f(x_loc, y_loc):
                xr = x_loc * cos_a - y_loc * sin_a
                yr = x_loc * sin_a + y_loc * cos_a
                return np.array([xr, y_c + yr, 0.0])

            def rot_b(x_loc, y_loc):
                return rot_f(x_loc, y_loc) + v_depth

            # Exact hanger attach points on top of girder flanges
            y_att = girder_h / 2 + flange_h
            att_front_l = rot_f(-b_screen, y_att)
            att_front_r = rot_f(b_screen, y_att)
            att_back_l = rot_b(-b_screen, y_att)
            att_back_r = rot_b(b_screen, y_att)

            return {
                "idx": idx,
                "y_c": y_c,
                "center_front": center_front,
                "center_back": center_back,
                "alpha_rad": alpha_rad,
                "alpha_deg": alpha_deg,
                "cos_a": cos_a,
                "sin_a": sin_a,
                "rot_f": rot_f,
                "rot_b": rot_b,
                "att_fl": att_front_l,
                "att_fr": att_front_r,
                "att_bl": att_back_l,
                "att_br": att_back_r,
            }

        # -------------------------------------------------------------
        # 5. Dynamic Bridge Deck (2.5D Transversal Isometric View)
        # -------------------------------------------------------------
        @always_redraw
        def deck_assembly() -> VGroup:
            t_curr = time_tracker.get_value()
            k = get_kinematics(t_curr)
            rot_f = k["rot_f"]
            rot_b = k["rot_b"]
            center_front = k["center_front"]

            grp = VGroup()

            # 1. Rear H-Girder and Roadway (Darker background silhouette)
            road_half_th = 0.08
            rb1 = rot_b(-b_screen, road_half_th)
            rb2 = rot_b(b_screen, road_half_th)
            rb3 = rot_b(b_screen, -road_half_th)
            rb4 = rot_b(-b_screen, -road_half_th)
            rear_roadway = Polygon(
                rb1, rb2, rb3, rb4,
                fill_color="#131B2E", fill_opacity=1.0, stroke_color="#334155", stroke_width=1.0
            )
            grp.add(rear_roadway)

            # 2. Longitudinal Roadway Surface connecting Front and Back
            rf1 = rot_f(-b_screen, road_half_th)
            rf2 = rot_f(b_screen, road_half_th)
            deck_surface = Polygon(
                rf1, rf2, rb2, rb1,
                fill_color="#1A2234", fill_opacity=1.0, stroke_color="#334155", stroke_width=1.0
            )
            grp.add(deck_surface)

            # Longitudinal Center Stripes in Perspective
            c_f = rot_f(0.0, road_half_th)
            c_b = rot_b(0.0, road_half_th)
            center_longitudinal = DashedLine(
                start=c_f, end=c_b,
                stroke_color="#EAB308", stroke_width=1.6, dash_length=0.15, stroke_opacity=0.75
            )
            grp.add(center_longitudinal)

            # 3. Longitudinal Bottom Truss Bracing Lines
            bot_f_l = rot_f(-b_screen, -road_half_th)
            bot_f_r = rot_f(b_screen, -road_half_th)
            bot_b_l = rot_b(-b_screen, -road_half_th)
            bot_b_r = rot_b(b_screen, -road_half_th)
            edge_l = Line(bot_f_l, bot_b_l, stroke_color="#1E293B", stroke_width=1.2)
            edge_r = Line(bot_f_r, bot_b_r, stroke_color="#1E293B", stroke_width=1.2)
            grp.add(edge_l, edge_r)

            # 4. Front Roadway Cross Section (Full contrast and crisp edges)
            rf3 = rot_f(b_screen, -road_half_th)
            rf4 = rot_f(-b_screen, -road_half_th)
            front_roadway = Polygon(
                rf1, rf2, rf3, rf4,
                fill_color="#1E2538", fill_opacity=1.0, stroke_color="#64748B", stroke_width=1.8
            )
            grp.add(front_roadway)

            # Center Yellow Stripe on Front Deck Face
            front_center_stripe = DashedLine(
                start=rot_f(-b_screen * 0.85, 0.0),
                end=rot_f(b_screen * 0.85, 0.0),
                stroke_color="#EAB308",
                stroke_width=1.6,
                dash_length=0.16,
            )
            grp.add(front_center_stripe)

            # 5. H-Girders (Left = Upstream bluff plate; Right = Downstream plate)
            def make_girder(x_pos, is_front=True):
                rf = rot_f if is_front else rot_b
                g_grp = VGroup()
                # Vertical web
                w1 = rf(x_pos - girder_w/2, girder_h/2)
                w2 = rf(x_pos + girder_w/2, girder_h/2)
                w3 = rf(x_pos + girder_w/2, -girder_h/2)
                w4 = rf(x_pos - girder_w/2, -girder_h/2)
                web = Polygon(w1, w2, w3, w4, fill_color="#475569", fill_opacity=1.0, stroke_color="#94A3B8", stroke_width=1.4)
                # Top flange
                tf1 = rf(x_pos - flange_w/2, girder_h/2 + flange_h)
                tf2 = rf(x_pos + flange_w/2, girder_h/2 + flange_h)
                tf3 = rf(x_pos + flange_w/2, girder_h/2)
                tf4 = rf(x_pos - flange_w/2, girder_h/2)
                t_flange = Polygon(tf1, tf2, tf3, tf4, fill_color="#64748B", fill_opacity=1.0, stroke_color="#CBD5E1", stroke_width=1.4)
                # Bottom flange
                bf1 = rf(x_pos - flange_w/2, -girder_h/2)
                bf2 = rf(x_pos + flange_w/2, -girder_h/2)
                bf3 = rf(x_pos + flange_w/2, -girder_h/2 - flange_h)
                bf4 = rf(x_pos - flange_w/2, -girder_h/2 - flange_h)
                b_flange = Polygon(bf1, bf2, bf3, bf4, fill_color="#64748B", fill_opacity=1.0, stroke_color="#CBD5E1", stroke_width=1.4)
                # Vertical stiffener rib
                stiff = Line(rf(x_pos, girder_h/2), rf(x_pos, -girder_h/2), stroke_color="#334155", stroke_width=1.2)
                g_grp.add(web, t_flange, b_flange, stiff)
                return g_grp

            # Rear Girders
            grp.add(make_girder(-b_screen, is_front=False))
            grp.add(make_girder(b_screen, is_front=False))
            # Front Girders
            grp.add(make_girder(-b_screen, is_front=True))
            grp.add(make_girder(b_screen, is_front=True))

            # Railings on front
            rail_l = Line(rot_f(-b_screen * 0.95, road_half_th), rot_f(-b_screen * 0.95, road_half_th + 0.32), stroke_color="#94A3B8", stroke_width=1.4)
            rail_r = Line(rot_f(b_screen * 0.95, road_half_th), rot_f(b_screen * 0.95, road_half_th + 0.32), stroke_color="#94A3B8", stroke_width=1.4)
            grp.add(rail_l, rail_r)

            # Center Shear Axis / Pivot Crosshair
            pivot_ring = Circle(radius=0.11, stroke_color="#00F0FF", stroke_width=2.0, fill_color="#08101E", fill_opacity=1.0).move_to(center_front)
            cross_h = Line(center_front + [-0.14, 0, 0], center_front + [0.14, 0, 0], stroke_color="#00F0FF", stroke_width=1.2)
            cross_v = Line(center_front + [0, -0.14, 0], center_front + [0, 0.14, 0], stroke_color="#00F0FF", stroke_width=1.2)
            grp.add(pivot_ring, cross_h, cross_v)

            grp.set_z_index(20)
            return grp

        self.add(deck_assembly)

        # -------------------------------------------------------------
        # 6. Dynamic Suspender Hangers & Plastic Yielding Glow
        txt_yield_l = Text("¡CEDENCIA!" if lang == "ES" else "PLASTIC YIELD!", font="Consolas", font_size=8, color="#EF4444")
        txt_yield_r = Text("¡CEDENCIA!" if lang == "ES" else "PLASTIC YIELD!", font="Consolas", font_size=8, color="#EF4444")
        txt_slack_l = Text("DESTENSADO" if lang == "ES" else "SLACK", font="Consolas", font_size=7, color="#64748B")
        txt_slack_r = Text("DESTENSADO" if lang == "ES" else "SLACK", font="Consolas", font_size=7, color="#64748B")

        @always_redraw
        def suspender_cables() -> VGroup:
            t_curr = time_tracker.get_value()
            k = get_kinematics(t_curr)
            idx = k["idx"]

            grp = VGroup()

            # Helper for drawing a cable with its exact state
            def draw_hanger(saddle_pt, deck_pt, is_yield, is_slack, side_str):
                c_grp = VGroup()
                is_l = "L" in side_str
                if is_yield:
                    # Flashing plastic yield glow
                    glow = Line(saddle_pt, deck_pt, stroke_color="#EF4444", stroke_width=7.5, stroke_opacity=0.45)
                    core = Line(saddle_pt, deck_pt, stroke_color="#FF0055", stroke_width=4.0)
                    lbl = (txt_yield_l if is_l else txt_yield_r).copy().next_to((saddle_pt + deck_pt)/2, LEFT if is_l else RIGHT, buff=0.12)
                    c_grp.add(glow, core, lbl)
                elif is_slack:
                    # Slacked cable with slight catenary droop
                    mid = (saddle_pt + deck_pt) / 2 + np.array([-0.14 if is_l else 0.14, 0, 0])
                    cable = ParametricFunction(
                        lambda s: (1 - s)**2 * saddle_pt + 2 * (1 - s) * s * mid + s**2 * deck_pt,
                        t_range=[0, 1],
                        stroke_color="#64748B",
                        stroke_width=1.5,
                        stroke_opacity=0.40,
                    )
                    lbl = (txt_slack_l if is_l else txt_slack_r).copy().next_to(mid, LEFT if is_l else RIGHT, buff=0.10)
                    c_grp.add(cable, lbl)
                else:
                    # Normal tension
                    cable = Line(saddle_pt, deck_pt, stroke_color="#38BDF8", stroke_width=2.5)
                    c_grp.add(cable)
                return c_grp

            # Rear Cables (Slightly dimmed)
            grp.add(draw_hanger(saddle_back_l, k["att_bl"], sol.left_yield[idx], sol.left_slack[idx], "BL"))
            grp.add(draw_hanger(saddle_back_r, k["att_br"], sol.right_yield[idx], sol.right_slack[idx], "BR"))

            # Front Cables
            grp.add(draw_hanger(saddle_front_l, k["att_fl"], sol.left_yield[idx], sol.left_slack[idx], "FL"))
            grp.add(draw_hanger(saddle_front_r, k["att_fr"], sol.right_yield[idx], sol.right_slack[idx], "FR"))

            grp.set_z_index(15)
            return grp

        self.add(suspender_cables)

        # -------------------------------------------------------------
        # 7. Fluid Flow Field: Full-Width Streamlines & Dynamic Vortices
        # -------------------------------------------------------------
        legend_bg = RoundedRectangle(
            width=2.5, height=0.52, corner_radius=0.08,
            fill_color="#0A1120", fill_opacity=0.85, stroke_color="#334155", stroke_width=0.8
        ).move_to([2.7, 4.15, 0])
        dot_ccw = Dot(point=[1.7, 4.15, 0], radius=0.055, color="#FF007F")
        lbl_ccw = Text("+ω_z", font="Consolas", font_size=8, color="#FF007F").next_to(dot_ccw, RIGHT, buff=0.06)
        dot_cw = Dot(point=[2.7, 4.15, 0], radius=0.055, color="#00F0FF")
        lbl_cw = Text("-ω_z", font="Consolas", font_size=8, color="#00F0FF").next_to(dot_cw, RIGHT, buff=0.06)
        vorticity_legend_grp = VGroup(legend_bg, dot_ccw, lbl_ccw, dot_cw, lbl_cw).set_z_index(6)

        last_wind_10hz = [-1]
        cached_wind_tag = [None]

        @always_redraw
        def fluid_flow_field() -> VGroup:
            t_curr = time_tracker.get_value()
            k = get_kinematics(t_curr)
            idx = k["idx"]

            u_kmh = sol.U_kmh[idx]
            alpha_rad = sol.alpha[idx]
            phase = sol.phase_idx[idx]
            wind_speed_ratio = u_kmh / 68.0

            grp = VGroup()
            grp.set_z_index(5)

            sin_a = np.sin(alpha_rad)
            h_curr = sol.h[idx]
            y_c_val = y_deck_rest + 0.40 * h_curr

            # 3D deck envelope bounds
            deck_top = lambda x: y_c_val + x * sin_a + 0.525 + 0.06 + max(0, v_depth[1]) + 0.12
            deck_bot = lambda x: y_c_val + x * sin_a - 0.525 - 0.06 - 0.12

            def get_w(x_val):
                s_up = 1.0 / (1.0 + np.exp(-3.5 * (x_val - (-3.1))))
                s_dn = 1.0 / (1.0 + np.exp(3.5 * (x_val - 3.3)))
                return s_up * s_dn

            upper_y0 = [2.2, 2.7, 3.2, 3.7]
            lower_y0 = [0.5, 0.0, -0.5, -1.0]
            xs = np.linspace(-4.4, 4.4, 25)

            # --- UPPER STREAMLINES (Continuous across full width) ---
            for y0 in upper_y0:
                ys = []
                for x_val in xs:
                    w = get_w(x_val)
                    target_y = deck_top(x_val) + (y0 - 2.2) * 0.70 + 0.20
                    wake = 0.0
                    if x_val > b_screen:
                        age_x = x_val - b_screen
                        wake = 0.14 * np.sin(2.8 * age_x - 5.0 * t_curr) * (1.0 - np.exp(-age_x)) * wind_speed_ratio
                    y_base = y0 + wake
                    lift = max(0.0, target_y - y_base)
                    y_val = y_base + w * lift
                    ys.append(y_val)

                pts = [np.array([x_val, y_val, 0.0]) for x_val, y_val in zip(xs, ys)]
                stream_line = VMobject(
                    stroke_color="#00F0FF",
                    stroke_width=1.3,
                    stroke_opacity=0.30 + 0.40 * wind_speed_ratio,
                )
                stream_line.set_points_smoothly(pts)
                grp.add(stream_line)

                # 2 Flow direction chevrons across screen
                for c_i in range(2):
                    phase_c = (t_curr * (0.35 + 0.75 * wind_speed_ratio) + c_i * 0.5 + y0 * 0.15) % 1.0
                    c_x = -4.3 + phase_c * 8.6
                    c_y = float(np.interp(c_x, xs, ys))
                    c_y_next = float(np.interp(min(c_x + 0.06, 4.4), xs, ys))
                    ang = np.arctan2(c_y_next - c_y, 0.06)
                    c_tri = Triangle(
                        fill_color="#38BDF8", fill_opacity=0.80, stroke_width=0
                    ).scale(0.055).rotate(ang - PI/2).move_to([c_x, c_y, 0])
                    grp.add(c_tri)

            # --- LOWER STREAMLINES (Continuous across full width) ---
            for y0 in lower_y0:
                ys = []
                for x_val in xs:
                    w = get_w(x_val)
                    target_y = deck_bot(x_val) - (0.5 - y0) * 0.70 - 0.20
                    wake = 0.0
                    if x_val > b_screen:
                        age_x = x_val - b_screen
                        wake = 0.14 * np.sin(2.8 * age_x - 5.0 * t_curr + np.pi) * (1.0 - np.exp(-age_x)) * wind_speed_ratio
                    y_base = y0 + wake
                    drop = max(0.0, y_base - target_y)
                    y_val = y_base - w * drop
                    ys.append(y_val)

                pts = [np.array([x_val, y_val, 0.0]) for x_val, y_val in zip(xs, ys)]
                stream_line = VMobject(
                    stroke_color="#00F0FF",
                    stroke_width=1.3,
                    stroke_opacity=0.30 + 0.40 * wind_speed_ratio,
                )
                stream_line.set_points_smoothly(pts)
                grp.add(stream_line)

                for c_i in range(2):
                    phase_c = (t_curr * (0.35 + 0.75 * wind_speed_ratio) + c_i * 0.5 + (y0 + 2.0) * 0.15) % 1.0
                    c_x = -4.3 + phase_c * 8.6
                    c_y = float(np.interp(c_x, xs, ys))
                    c_y_next = float(np.interp(min(c_x + 0.06, 4.4), xs, ys))
                    ang = np.arctan2(c_y_next - c_y, 0.06)
                    c_tri = Triangle(
                        fill_color="#38BDF8", fill_opacity=0.80, stroke_width=0
                    ).scale(0.055).rotate(ang - PI/2).move_to([c_x, c_y, 0])
                    grp.add(c_tri)

            # Wind Speed Upstream Indicator (10 Hz throttle)
            step_10hz = idx // 6
            if step_10hz != last_wind_10hz[0] or cached_wind_tag[0] is None:
                last_wind_10hz[0] = step_10hz
                wind_lbl_str = f"VIENTO U = {u_kmh:.1f} km/h" if lang == "ES" else f"WIND U = {u_kmh:.1f} km/h"
                cached_wind_tag[0] = Text(
                    wind_lbl_str,
                    font="Consolas",
                    font_size=9,
                    color="#00F0FF",
                ).move_to([-3.1, 4.15, 0])
            grp.add(cached_wind_tag[0])

            # Alternating von Kármán Coherent Vortices in Wake (Phase 2 & 3)
            if phase >= 2:
                convect_speed = 1.10 + 0.90 * wind_speed_ratio
                for v_i in range(4):
                    t_born = t_curr - v_i * 1.30
                    if t_born < 4.0:
                        continue
                    age = t_curr - t_born
                    x_v = 2.45 + convect_speed * age
                    if x_v > 4.25:
                        continue

                    v_sign = 1 if (v_i % 2 == 0) else -1
                    y_v = (y_deck_rest + 0.75) if v_sign > 0 else (y_deck_rest - 0.75)
                    y_v += 0.22 * np.sin(x_v * 1.6)

                    v_color = "#FF007F" if v_sign > 0 else "#00F0FF"
                    core_rad = 0.20 + 0.07 * age

                    core_circle = Circle(
                        radius=core_rad,
                        stroke_color=v_color,
                        stroke_width=1.8,
                        stroke_opacity=max(0.1, 0.85 - 0.12 * age),
                        fill_color=v_color,
                        fill_opacity=max(0.04, 0.20 - 0.04 * age),
                    ).move_to([x_v, y_v, 0])

                    spin_angle = t_curr * 7.5 * v_sign
                    swirl_arc = Arc(
                        radius=core_rad * 0.75,
                        start_angle=spin_angle,
                        angle=PI * 1.3,
                        stroke_color=v_color,
                        stroke_width=1.5,
                        stroke_opacity=max(0.15, 0.90 - 0.15 * age),
                    ).move_to([x_v, y_v, 0])

                    tip_pt = [
                        x_v + core_rad * 0.75 * np.cos(spin_angle + PI * 1.3),
                        y_v + core_rad * 0.75 * np.sin(spin_angle + PI * 1.3),
                        0.0,
                    ]
                    swirl_tip = Dot(point=tip_pt, radius=0.035, color=v_color)
                    grp.add(core_circle, swirl_arc, swirl_tip)

                grp.add(vorticity_legend_grp)

            return grp

        self.add(fluid_flow_field)

        # -------------------------------------------------------------
        # 8. Dynamic Aeroelastic Vectors (Lift L, Moment M, Angle α)
        # -------------------------------------------------------------
        last_aero_10hz = [-1]
        cached_aero_lbls = [VGroup()]

        @always_redraw
        def dynamic_aero_vectors() -> VGroup:
            t_curr = time_tracker.get_value()
            k = get_kinematics(t_curr)
            idx = k["idx"]
            center_front = k["center_front"]
            alpha_deg = k["alpha_deg"]
            alpha_rad = k["alpha_rad"]

            l_val = sol.L_aero[idx]
            m_val = sol.M_aero[idx]

            grp = VGroup()

            # 1. Pitch Angle Arc & Readout
            if abs(alpha_deg) > 0.6:
                arc_rad = 1.55
                start_a = 0.0 if alpha_rad >= 0 else alpha_rad
                span_a = abs(alpha_rad)
                angle_arc = Arc(
                    radius=arc_rad,
                    start_angle=start_a,
                    angle=span_a,
                    arc_center=center_front,
                    stroke_color="#F59E0B",
                    stroke_width=2.0,
                )
                grp.add(angle_arc)

            # 2. Dynamic Aerodynamic Lift Vector L(t)
            lift_scale = 1.0 / 8.0e3
            l_len = np.clip(l_val * lift_scale, -1.6, 1.6)
            if abs(l_len) > 0.14:
                l_end = center_front + np.array([0.0, l_len, 0.0])
                l_color = "#10B981" if l_len > 0 else "#F43F5E"
                l_arrow = Arrow(
                    start=center_front,
                    end=l_end,
                    buff=0.0,
                    stroke_color=l_color,
                    stroke_width=3.2,
                    max_tip_length_to_length_ratio=0.28,
                    max_stroke_width_to_length_ratio=4.0,
                )
                grp.add(l_arrow)

            # 3. Dynamic Aerodynamic Pitching Moment Vector M(t) (90° Phase Lead)
            m_scale = 1.0 / 5.0e4
            m_norm = np.clip(m_val * m_scale, -1.0, 1.0)
            if abs(m_norm) > 0.08:
                m_rad = 0.68
                m_color = "#F59E0B"
                if m_val > 0:
                    start_th = 0.2
                    sweep_th = abs(m_norm) * PI * 0.85
                else:
                    start_th = PI - 0.2
                    sweep_th = -abs(m_norm) * PI * 0.85

                m_arc = Arc(
                    radius=m_rad,
                    start_angle=start_th,
                    angle=sweep_th,
                    arc_center=center_front,
                    stroke_color=m_color,
                    stroke_width=3.0,
                )
                end_th = start_th + sweep_th
                tip_pt = center_front + np.array([m_rad * np.cos(end_th), m_rad * np.sin(end_th), 0.0])
                tip_tangent = np.array([-np.sin(end_th), np.cos(end_th), 0.0]) * (1.0 if m_val > 0 else -1.0)
                tip_arrow = Triangle(
                    fill_color=m_color, fill_opacity=1.0, stroke_width=0
                ).scale(0.075).rotate(np.arctan2(tip_tangent[1], tip_tangent[0]) - PI/2).move_to(tip_pt)
                grp.add(m_arc, tip_arrow)

            # Text labels cached at 10 Hz
            step_10hz = idx // 6
            if step_10hz != last_aero_10hz[0] or len(cached_aero_lbls[0]) == 0:
                last_aero_10hz[0] = step_10hz
                lbl_grp = VGroup()
                if abs(alpha_deg) > 0.6:
                    lbl_x = center_front[0] + (1.55 + 0.42) * np.cos(alpha_rad / 2)
                    lbl_y = center_front[1] + (1.55 + 0.42) * np.sin(alpha_rad / 2)
                    lbl_grp.add(Text(f"α = {alpha_deg:+.1f}°", font="Consolas", font_size=11, color="#F59E0B").move_to([lbl_x, lbl_y, 0]))
                if abs(l_len) > 0.14:
                    l_end = center_front + np.array([0.0, l_len, 0.0])
                    l_color = "#10B981" if l_len > 0 else "#F43F5E"
                    lbl_grp.add(Text(f"L = {l_val/1e3:+.1f} kN/m", font="Consolas", font_size=8.5, color=l_color).next_to(l_end, UP if l_len > 0 else DOWN, buff=0.1))
                if abs(m_norm) > 0.08:
                    lbl_grp.add(Text(f"M = {m_val/1e3:+.0f} kN·m", font="Consolas", font_size=8.5, color="#F59E0B").move_to([center_front[0] - 1.25, center_front[1] + 0.42, 0]))
                cached_aero_lbls[0] = lbl_grp

            grp.add(cached_aero_lbls[0])
            grp.set_z_index(25)
            return grp

        self.add(dynamic_aero_vectors)

        # -------------------------------------------------------------
        # 9. Telemetry HUD Console (Safe Zone: y in [-4.4, -2.5])
        # -------------------------------------------------------------
        hud_box = RoundedRectangle(
            width=8.4,
            height=2.05,
            corner_radius=0.15,
            fill_color="#0A1120",
            fill_opacity=0.92,
            stroke_color="#1E293B",
            stroke_width=1.5,
        ).move_to([0.0, -3.45, 0.0])

        hud_bar_str = "TELEMETRÍA AEROELÁSTICA // CONSOLA DINÁMICA DE SCANLAN" if lang == "ES" else "AEROELASTIC TELEMETRY // SCANLAN DYNAMIC CONSOLE"
        hud_title_bar = Text(
            hud_bar_str,
            font="Consolas",
            font_size=9.5,
            color="#38BDF8",
        ).move_to([0.0, -2.60, 0.0])

        hud_divider = Line(
            start=[-4.0, -2.75, 0],
            end=[4.0, -2.75, 0],
            stroke_color="#1E293B",
            stroke_width=1.0,
        )
        hud_box.set_z_index(30)
        hud_title_bar.set_z_index(30)
        hud_divider.set_z_index(30)
        self.add(hud_box, hud_title_bar, hud_divider)

        last_hud_10hz = [-1]
        cached_hud_grp = [VGroup()]

        @always_redraw
        def hud_telemetry() -> VGroup:
            t_curr = time_tracker.get_value()
            idx = get_frame_idx(t_curr)

            step_10hz = idx // 6
            if step_10hz != last_hud_10hz[0] or len(cached_hud_grp[0]) == 0:
                last_hud_10hz[0] = step_10hz

                phase = sol.phase_idx[idx]
                u_kmh = sol.U_kmh[idx]
                a2 = sol.A2_star[idx]
                zeta_aero = sol.zeta_aero[idx]
                alpha_deg = sol.alpha_deg[idx]
                work_kj = sol.work_accum[idx] / 1e3
                is_yield = sol.left_yield[idx] or sol.right_yield[idx]

                if lang == "ES":
                    if phase == 1:
                        state_str = "ESTABLE (FLEXIÓN VERTICAL)"
                        state_col = "#10B981"
                        zeta_col = "#10B981"
                        cable_col = "#38BDF8"
                        cable_str = "T0 = 42 kN/m [NOMINAL]"
                    elif phase == 2:
                        state_str = "BIFURCACIÓN DE FLUTTER (LOCK-IN)"
                        state_col = "#F59E0B"
                        zeta_col = "#EF4444"
                        cable_col = "#F59E0B"
                        cable_str = "SOBRETENSIÓN DINÁMICA"
                    else:
                        state_str = "¡COLAPSO TORSIONAL RESONANTE!"
                        state_col = "#EF4444"
                        zeta_col = "#EF4444"
                        cable_col = "#FF0055" if is_yield else "#EF4444"
                        cable_str = "¡CEDENCIA PLÁSTICA / ROTURA!"

                    line1_label = "FENÓMENO: "
                    line2_str = f"VEL. VIENTO  : U = {u_kmh:4.1f} km/h  {'[SUPERCRÍTICA]' if u_kmh > 40 else '[MODERADO]'}"
                    line3_str = f"SCANLAN A2*  : A2* = {a2:+.3f}  {'(INYECCIÓN ENERGÍA)' if a2 > 0 else '(DISIPATIVO)'}"
                    line4_str = f"AMORTIGUAM.  : ζ_aero = {zeta_aero:+.3f}  {'[INESTABLE / BOMBA]' if zeta_aero < 0 else '[ESTABLE]'}"
                    line5_str = f"ÁNGULO TORSIÓN: α = {alpha_deg:+5.1f}°  |  W_eólico = {work_kj:5.1f} kJ/m"
                    line6_str = f"CABLES TIJERA: {cable_str}"
                else:
                    if phase == 1:
                        state_str = "STABLE (VERTICAL BENDING)"
                        state_col = "#10B981"
                        zeta_col = "#10B981"
                        cable_col = "#38BDF8"
                        cable_str = "T0 = 42 kN/m [NOMINAL]"
                    elif phase == 2:
                        state_str = "FLUTTER BIFURCATION (LOCK-IN)"
                        state_col = "#F59E0B"
                        zeta_col = "#EF4444"
                        cable_col = "#F59E0B"
                        cable_str = "DYNAMIC OVERTENSION"
                    else:
                        state_str = "RESONANT TORSIONAL COLLAPSE!"
                        state_col = "#EF4444"
                        zeta_col = "#EF4444"
                        cable_col = "#FF0055" if is_yield else "#EF4444"
                        cable_str = "PLASTIC YIELD / SNAP!"

                    line1_label = "PHENOMENON   : "
                    line2_str = f"WIND SPEED   : U = {u_kmh:4.1f} km/h  {'[SUPERCRITICAL]' if u_kmh > 40 else '[MODERATE]'}"
                    line3_str = f"SCANLAN A2*  : A2* = {a2:+.3f}  {'(ENERGY INJECTION)' if a2 > 0 else '(DISSIPATIVE)'}"
                    line4_str = f"DAMPING      : ζ_aero = {zeta_aero:+.3f}  {'[UNSTABLE / PUMP]' if zeta_aero < 0 else '[ESTABLE]'}"
                    line5_str = f"TORSION ANGLE: α = {alpha_deg:+5.1f}°  |  W_wind = {work_kj:5.1f} kJ/m"
                    line6_str = f"HANGER CABLES: {cable_str}"

                grp = VGroup()

                line1 = Text(
                    f"{line1_label}{state_str}",
                    font="Consolas",
                    font_size=9.5,
                    color=state_col,
                ).move_to([-3.9, -2.96, 0], aligned_edge=LEFT)

                line2 = Text(
                    line2_str,
                    font="Consolas",
                    font_size=9.0,
                    color="#00F0FF" if u_kmh > 40 else "#94A3B8",
                ).move_to([-3.9, -3.22, 0], aligned_edge=LEFT)

                line3 = Text(
                    line3_str,
                    font="Consolas",
                    font_size=9.0,
                    color="#EF4444" if a2 > 0 else "#94A3B8",
                ).move_to([-3.9, -3.48, 0], aligned_edge=LEFT)

                line4 = Text(
                    line4_str,
                    font="Consolas",
                    font_size=9.0,
                    color=zeta_col,
                ).move_to([-3.9, -3.74, 0], aligned_edge=LEFT)

                line5 = Text(
                    line5_str,
                    font="Consolas",
                    font_size=9.0,
                    color="#F59E0B" if abs(alpha_deg) < 25 else "#EF4444",
                ).move_to([-3.9, -4.00, 0], aligned_edge=LEFT)

                line6 = Text(
                    line6_str,
                    font="Consolas",
                    font_size=9.0,
                    color=cable_col,
                ).move_to([-3.9, -4.24, 0], aligned_edge=LEFT)

                grp.add(line1, line2, line3, line4, line5, line6)
                grp.set_z_index(30)
                cached_hud_grp[0] = grp

            return cached_hud_grp[0]

        self.add(hud_telemetry)

        # -------------------------------------------------------------
        # 10. Flashing Emergency Alarm Banner (Safe Zone: y in [-5.25, -4.55])
        # -------------------------------------------------------------
        p_text = "ESTABILIDAD AEROELÁSTICA: AMORTIGUAMIENTO POSITIVO (ζ > 0)" if lang == "ES" else "AEROELASTIC STABILITY: POSITIVE DAMPING (ζ > 0)"
        panel_p1 = RoundedRectangle(
            width=8.4, height=0.62, corner_radius=0.10,
            fill_color="#064E3B", fill_opacity=0.35, stroke_color="#10B981", stroke_width=1.0
        ).move_to([0.0, -4.85, 0.0])
        txt_p1 = Text(
            p_text,
            font="Consolas",
            font_size=8.5,
            color="#10B981",
        ).move_to([0.0, -4.85, 0.0])
        banner_p1_grp = VGroup(panel_p1, txt_p1).set_z_index(30)

        panel_p23 = RoundedRectangle(
            width=8.4, height=0.68, corner_radius=0.10,
            fill_color="#7F1D1D", fill_opacity=0.92, stroke_color="#EF4444", stroke_width=2.0
        ).move_to([0.0, -4.85, 0.0])

        t1_str = "[!] INYECCIÓN NETA DE ENERGÍA EÓLICA [!]" if lang == "ES" else "[!] NET WIND ENERGY INJECTION [!]"
        t2_str = "EL VIENTO ALIMENTA LA RESONANCIA EN LUGAR DE FRENARLA" if lang == "ES" else "THE WIND AMPLIFIES RESONANCE INSTEAD OF OPPOSING IT"

        txt_l1 = Text(
            t1_str,
            font="Consolas",
            weight=BOLD,
            font_size=9.5,
            color="#FEF08A",
        ).move_to([0.0, -4.72, 0.0])

        txt_l2 = Text(
            t2_str,
            font="Consolas",
            font_size=8.5,
            color="#FFFFFF",
        ).move_to([0.0, -4.95, 0.0])

        banner_p23_grp = VGroup(panel_p23, txt_l1, txt_l2).set_z_index(30)

        @always_redraw
        def emergency_alarm_banner() -> VGroup:
            t_curr = time_tracker.get_value()
            idx = get_frame_idx(t_curr)
            phase = sol.phase_idx[idx]

            if phase == 1:
                return banner_p1_grp
            else:
                freq = 2.5 if phase == 2 else 4.2
                blink = (np.sin(2.0 * np.pi * freq * t_curr) > 0)
                panel_p23.set_fill(color="#7F1D1D" if blink else "#450A0A", opacity=0.92)
                panel_p23.set_stroke(color="#EF4444" if blink else "#991B1B", width=2.0)
                txt_l1.set_color("#FEF08A" if blink else "#FDE047")
                txt_l2.set_color("#FFFFFF" if blink else "#FCA5A5")
                return banner_p23_grp

        self.add(emergency_alarm_banner)

        # -------------------------------------------------------------
        # 11. Orchestrated 15-Second Animation Sequence (60 FPS)
        # -------------------------------------------------------------
        self.play(
            time_tracker.animate.set_value(phys_cfg.t_total),
            run_time=phys_cfg.t_total,
            rate_func=linear,
        )
        self.wait(0.1)


class TacomaFlutterSceneES(TacomaFlutterSceneBase):
    lang = "ES"


class TacomaFlutterSceneEN(TacomaFlutterSceneBase):
    lang = "EN"


class TacomaFlutterScene(TacomaFlutterSceneES):
    pass
