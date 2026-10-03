"""
Continuum Lab — Fluid Mechanics & Aerodynamics
Module: 01 Mecanica de Fluidos / 03 Desprendimiento Capa Limite y Stall Aerodinamico
Vectorized Manim 9:16 (1080x1920 @ 60 FPS) Video Production Engine — High Kinetic Dynamics

Key Improvements:
  - 100% kinetic from frame 0: fast-flowing continuous particle tracers and traveling streamlines.
  - Dynamic aerodynamic force vectors attached to quarter-chord:
      * Lift Force L(t) (Cyan): surges to peak then visibly collapses by 74% at stall.
      * Drag Force D(t) (Magenta): explodes 14x-18x as flow separates into turbulent wake.
  - Adverse pressure gradient arrows (dp/dx > 0) pushing backwards along the suction surface.
  - Real-time Pohlhausen boundary layer velocity vectors showing positive shear -> zero shear -> reverse flow.
  - Separation vortex eddies actively spinning and advecting downstream.
  - Structural stall buffet flutter shaking the airframe at deep stall.
  - Exact 18.0s timeline, zero branding in frame, bilingual delivery, aero-acoustic audio.
"""

from manim import *
import numpy as np
import os
import subprocess
import sys
from pathlib import Path
import imageio_ffmpeg

# Add project root to sys.path
project_dir = Path(__file__).resolve().parent.parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.physics.aerodynamic_stall import AerodynamicStallSimulation, AirfoilParameters
from src.audio.stall_audio_synth import synthesize_stall_audio

# TikTok / Reels / Shorts 9:16 Canvas Configuration
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#0a0a0c"  # Deep Cybernetic Void


def create_stall_scene(lang: str = "ES"):
    """
    Factory creating localized Manim scene class (ES or EN) with high kinetic dynamism.
    """
    class AerodynamicStallScene(Scene):
        def construct(self):
            sim = AerodynamicStallSimulation()
            alpha_tracker = ValueTracker(4.0)
            time_tracker = ValueTracker(0.0)

            # -----------------------------------------------------------------
            # 1. Top Telemetry Card (Safe Zone: y in [4.38, 6.82], leaves >140 px top)
            # -----------------------------------------------------------------
            top_box = RoundedRectangle(
                corner_radius=0.14,
                width=7.8,
                height=2.45,
                color="#00f0ff",
                stroke_width=1.5,
                fill_color="#0d1117",
                fill_opacity=0.96
            ).move_to(UP * 5.60)

            eq_top_1 = MathTex(
                r"\left.\frac{\partial u}{\partial y}\right|_{\mathrm{wall}} = 0 \quad \Big| \quad C_L = 2\pi\alpha \quad (\text{Thin Airfoil Theory})",
                font_size=17,
                color="#ffffff"
            ).move_to(UP * 6.32)

            rule_top_1 = Line(LEFT * 3.5, RIGHT * 3.5, color="#1f2937", stroke_width=0.9).move_to(UP * 5.92)

            if lang == "ES":
                sub_top = MathTex(
                    r"\frac{\partial p}{\partial x} > 0 \quad (\text{Gradiente Adverso}) \implies \tau_w \to 0 \quad [\text{Desprendimiento}]",
                    font_size=16,
                    color="#00f0ff"
                ).move_to(UP * 5.52)
            else:
                sub_top = MathTex(
                    r"\frac{\partial p}{\partial x} > 0 \quad (\text{Adverse Gradient}) \implies \tau_w \to 0 \quad [\text{Boundary Separation}]",
                    font_size=16,
                    color="#00f0ff"
                ).move_to(UP * 5.52)

            rule_top_2 = Line(LEFT * 3.5, RIGHT * 3.5, color="#1f2937", stroke_width=0.9).move_to(UP * 5.12)

            def get_live_str():
                a = alpha_tracker.get_value()
                cl = sim.lift_coefficient(a)
                cd = sim.drag_coefficient(a)
                x_sep = sim.separation_point(a)
                if lang == "ES":
                    state_str = "ADHERIDO (CRUCERO)" if a <= 8.0 else ("SEPARACIÓN INCIPIENTE" if a <= 15.5 else "¡STALL CRASH! (-74%)")
                    return (
                        f"α = {a:4.1f}°   "
                        f"C_L = {cl:4.2f}   "
                        f"C_D = {cd:4.3f}   "
                        f"x_sep/c = {x_sep:4.2f}   "
                        f"[{state_str}]"
                    )
                else:
                    state_str = "ATTACHED (CRUISE)" if a <= 8.0 else ("SEPARATION ONSET" if a <= 15.5 else "STALL CRASH! (-74%)")
                    return (
                        f"α = {a:4.1f}°   "
                        f"C_L = {cl:4.2f}   "
                        f"C_D = {cd:4.3f}   "
                        f"x_sep/c = {x_sep:4.2f}   "
                        f"[{state_str}]"
                    )

            live_text = always_redraw(lambda: Text(
                get_live_str(),
                font="Segoe UI",
                font_size=12,
                color="#39ff14" if alpha_tracker.get_value() <= 12.0 else ("#ffaa00" if alpha_tracker.get_value() <= 15.5 else "#ff0055")
            ).move_to(UP * 4.72))

            top_group = VGroup(top_box, eq_top_1, rule_top_1, sub_top, rule_top_2, live_text)
            self.add(top_group)

            # -----------------------------------------------------------------
            # 2. Bottom Challenge Card (Safe Zone: y in [-6.4, -4.8], leaves >300 px bot)
            # -----------------------------------------------------------------
            bottom_box = RoundedRectangle(
                corner_radius=0.14,
                width=7.8,
                height=1.65,
                color="#ffaa00",
                stroke_width=1.3,
                fill_color="#0d1117",
                fill_opacity=0.96
            ).move_to(DOWN * 5.60)

            if lang == "ES":
                cta_title = Text(
                    "RETO COMUNITARIO",
                    font="Segoe UI",
                    weight=BOLD,
                    font_size=14,
                    color="#ffaa00"
                ).move_to(DOWN * 5.08)

                cta_body = Text(
                    "¿Pueden los generadores de vórtices o la succión activa retrasar el stall?\n¡Comenta tu solución técnica abajo! 👇",
                    font="Segoe UI",
                    font_size=13,
                    color="#e6edf3"
                ).move_to(DOWN * 5.75)
            else:
                cta_title = Text(
                    "COMMUNITY CHALLENGE",
                    font="Segoe UI",
                    weight=BOLD,
                    font_size=14,
                    color="#ffaa00"
                ).move_to(DOWN * 5.08)

                cta_body = Text(
                    "Can vortex generators or active suction delay boundary layer separation?\nDrop your engineering solution below! 👇",
                    font="Segoe UI",
                    font_size=13,
                    color="#e6edf3"
                ).move_to(DOWN * 5.75)

            bottom_group = VGroup(bottom_box, cta_title, cta_body)
            self.add(bottom_group)

            # -----------------------------------------------------------------
            # 3. Central Physical Airfoil & Aerodynamic Flow Viewport
            # -----------------------------------------------------------------
            chord_scale = 3.6
            x_pts, y_pts = sim.get_airfoil_polygon(n_points=140)
            base_points = [
                np.array([(xp - 0.25) * chord_scale, yp * chord_scale, 0.0])
                for xp, yp in zip(x_pts, y_pts)
            ]

            # Quarter-chord aerodynamic center reference point in screen coords
            qc_center = np.array([0.0, 0.70, 0.0])

            def get_current_airfoil_and_vectors():
                a = alpha_tracker.get_value()
                t = time_tracker.get_value()

                # Structural stall buffeting vibration at deep stall
                if a > 15.5:
                    buffet_amp = 0.70 * ((a - 15.5) / 3.0)
                    buffet_osc = buffet_amp * np.sin(2.0 * np.pi * 28.0 * t) * np.cos(2.0 * np.pi * 11.0 * t)
                    eff_alpha = a + buffet_osc
                else:
                    eff_alpha = a

                rad = np.radians(-eff_alpha)
                cos_a, sin_a = np.cos(rad), np.sin(rad)

                # Rotate around quarter chord (0.0, 0.70)
                rot_pts = []
                for pt in base_points:
                    xr = pt[0] * cos_a - pt[1] * sin_a + qc_center[0]
                    yr = pt[0] * sin_a + pt[1] * cos_a + qc_center[1]
                    rot_pts.append(np.array([xr, yr, 0.0]))

                airfoil_poly = Polygon(
                    *rot_pts,
                    stroke_color="#00f0ff" if a <= 15.5 else "#ff0055",
                    stroke_width=2.6,
                    fill_color="#12161f",
                    fill_opacity=0.98
                )

                # Quarter-chord aerodynamic center marker
                pivot_dot = Dot(point=qc_center, radius=0.07, color="#39ff14")

                # Chord reference line
                te_pt = np.array([0.75 * chord_scale * cos_a + qc_center[0], 0.75 * chord_scale * sin_a + qc_center[1], 0.0])
                le_pt = np.array([-0.25 * chord_scale * cos_a + qc_center[0], -0.25 * chord_scale * sin_a + qc_center[1], 0.0])
                chord_line = DashedLine(le_pt, te_pt, color="#4a5568", stroke_width=1.0)

                # Dynamic Aerodynamic Force Vectors attached at quarter chord
                cl = sim.lift_coefficient(a)
                cd = sim.drag_coefficient(a)

                # Lift vector: perpendicular to freestream (UP * cl * 1.5)
                lift_vec_len = max(cl * 1.45, 0.20)
                lift_end = qc_center + UP * lift_vec_len
                lift_arrow = Arrow(
                    start=qc_center, end=lift_end,
                    buff=0, color="#00f0ff" if a <= 15.5 else "#ff0055",
                    stroke_width=4.0, max_tip_length_to_length_ratio=0.22
                )
                lift_tag = Text(
                    f"LIFT C_L = {cl:.2f}",
                    font="Segoe UI", weight=BOLD, font_size=10,
                    color="#00f0ff" if a <= 15.5 else "#ff0055"
                ).next_to(lift_end, UP, buff=0.10)

                # Drag vector: parallel to freestream (RIGHT * cd * 7.5)
                drag_vec_len = max(cd * 7.2, 0.18)
                drag_end = qc_center + RIGHT * drag_vec_len
                drag_arrow = Arrow(
                    start=qc_center, end=drag_end,
                    buff=0, color="#ff007f",
                    stroke_width=3.5, max_tip_length_to_length_ratio=0.25
                )
                drag_tag = Text(
                    f"DRAG C_D = {cd:.3f}",
                    font="Segoe UI", weight=BOLD, font_size=10,
                    color="#ff007f"
                ).next_to(drag_end, RIGHT, buff=0.10)

                # Adverse pressure gradient arrows along upper surface
                adv_arrows = VGroup()
                if a > 8.0:
                    prog_adv = (a - 8.0) / 10.5
                    for xc_frac in [0.45, 0.65, 0.85]:
                        # Surface point
                        x_local = (xc_frac - 0.25) * chord_scale
                        y_local = sim.naca_thickness(np.array([xc_frac]))[0] * chord_scale
                        xr_s = x_local * cos_a - y_local * sin_a + qc_center[0]
                        yr_s = x_local * sin_a + y_local * cos_a + qc_center[1] + 0.08
                        # Arrow pointing backwards (against flow)
                        adv_arr = Arrow(
                            start=np.array([xr_s + 0.35 * prog_adv, yr_s, 0.0]),
                            end=np.array([xr_s, yr_s, 0.0]),
                            buff=0, color="#ffaa00" if a <= 15.5 else "#ff0055",
                            stroke_width=2.0, max_tip_length_to_length_ratio=0.35
                        )
                        adv_arrows.add(adv_arr)

                return VGroup(airfoil_poly, chord_line, pivot_dot, lift_arrow, lift_tag, drag_arrow, drag_tag, adv_arrows)

            airfoil_group = always_redraw(get_current_airfoil_and_vectors)
            self.add(airfoil_group)

            # -----------------------------------------------------------------
            # 4. Continuous Flowing Streamlines & Advecting Particle Tracers
            # -----------------------------------------------------------------
            num_streamlines = 11
            y_inlets = np.linspace(-1.3, 2.7, num_streamlines)

            def get_streamlines():
                a = alpha_tracker.get_value()
                t = time_tracker.get_value()
                x_sep = sim.separation_point(a)

                stream_vgroup = VGroup()

                for yi in y_inlets:
                    pts = []
                    is_suction = (yi >= 0.5)

                    for x_pos in np.linspace(-4.2, 4.2, 55):
                        y_pos = yi

                        # Airfoil deflection
                        if -1.4 <= x_pos <= 2.8:
                            if is_suction:
                                # Suction side
                                arc_peak = 0.85 * np.exp(-((x_pos + 0.2) ** 2) / 1.5)
                                if a <= 10.0:
                                    y_pos += arc_peak * 0.45
                                else:
                                    # Boundary layer separation
                                    sep_lift = 1.45 * ((a - 10.0) / 8.5) * np.exp(-((x_pos - 0.7) ** 2) / 2.8)
                                    y_pos += arc_peak * 0.45 + sep_lift
                            else:
                                # Pressure side deflection
                                y_pos -= 0.35 * np.exp(-((x_pos + 0.2) ** 2) / 1.8) * np.sin(np.radians(a))

                        # Traveling wave / wake turbulence (Continuous motion from frame 0!)
                        flow_speed = 3.8
                        wave_phase = 2.0 * np.pi * (flow_speed * t - x_pos * 0.6)
                        if is_suction and a > 12.0 and x_pos > 0.4:
                            wake_turb = 0.20 * ((a - 12.0) / 6.5) * np.sin(wave_phase)
                            y_pos += wake_turb
                        else:
                            # Subtle traveling wave even in clean flow
                            y_pos += 0.025 * np.sin(wave_phase)

                        pts.append(np.array([x_pos, y_pos, 0.0]))

                    if is_suction and a > 15.0 and yi < 1.6:
                        s_color = "#ff007f" if a > 16.0 else "#ffaa00"
                        s_width = 1.8
                    else:
                        s_color = "#00f0ff"
                        s_width = 1.3

                    stream_line = VMobject(stroke_color=s_color, stroke_width=s_width, stroke_opacity=0.65)
                    stream_line.set_points_smoothly(pts)
                    stream_vgroup.add(stream_line)

                # Recirculation vortices inside separated wake
                if a > 13.0:
                    vortex_prog = (a - 13.0) / 5.5
                    for v_idx, (vx, vy, v_rad, v_speed) in enumerate([
                        (0.65, 1.35, 0.40, 4.5),
                        (1.55, 1.60, 0.50, -3.8),
                        (2.45, 1.45, 0.55, 3.2)
                    ]):
                        v_phase = 2.0 * np.pi * v_speed * t
                        v_arc = Arc(
                            radius=v_rad * vortex_prog,
                            start_angle=v_phase,
                            angle=1.6 * np.pi,
                            color="#ff0055" if v_idx == 0 else "#ffaa00",
                            stroke_width=2.0,
                            stroke_opacity=0.85 * vortex_prog
                        ).move_to(np.array([vx, vy, 0.0]))
                        stream_vgroup.add(v_arc)

                return stream_vgroup

            streamlines_group = always_redraw(get_streamlines)
            self.add(streamlines_group)

            # -----------------------------------------------------------------
            # 5. Advecting Particle Tracers (Dynamic Kinetic Stream)
            # 48 particles streaming continuously from frame 0
            # -----------------------------------------------------------------
            num_particles = 48
            particle_offsets = np.linspace(0.0, 8.4, num_particles)
            particle_lanes = np.array([y_inlets[i % len(y_inlets)] for i in range(num_particles)])

            def get_particles():
                t = time_tracker.get_value()
                a = alpha_tracker.get_value()
                v_flow = 4.2  # Units per second

                dots_vgroup = VGroup()
                for i in range(num_particles):
                    # Compute cyclic x position
                    raw_x = (t * v_flow + particle_offsets[i]) % 8.4 - 4.2
                    yi = particle_lanes[i]
                    is_suction = (yi >= 0.5)

                    # Compute y position matching streamline
                    y_pos = yi
                    if -1.4 <= raw_x <= 2.8:
                        if is_suction:
                            arc_peak = 0.85 * np.exp(-((raw_x + 0.2) ** 2) / 1.5)
                            if a <= 10.0:
                                y_pos += arc_peak * 0.45
                            else:
                                sep_lift = 1.45 * ((a - 10.0) / 8.5) * np.exp(-((raw_x - 0.7) ** 2) / 2.8)
                                y_pos += arc_peak * 0.45 + sep_lift
                        else:
                            y_pos -= 0.35 * np.exp(-((raw_x + 0.2) ** 2) / 1.8) * np.sin(np.radians(a))

                    # In separated wake: particles swirl backwards if trapped!
                    if is_suction and a > 14.5 and (0.3 < raw_x < 2.0) and (yi < 1.3):
                        # Reverse recirculating trajectory
                        swirl_rad = 0.35
                        swirl_ang = 2.0 * np.pi * 3.5 * t + i * 0.8
                        raw_x = 1.1 + swirl_rad * np.cos(swirl_ang)
                        y_pos = 1.35 + swirl_rad * np.sin(swirl_ang)
                        p_color = "#d600ff"
                    else:
                        p_color = "#39ff14" if is_suction and a <= 12.0 else ("#00f0ff" if not is_suction else "#ffaa00")

                    dot = Dot(
                        point=np.array([raw_x, y_pos, 0.0]),
                        radius=0.045,
                        color=p_color
                    )
                    dots_vgroup.add(dot)

                return dots_vgroup

            particles_group = always_redraw(get_particles)
            self.add(particles_group)

            # -----------------------------------------------------------------
            # 6. Mini Pohlhausen Boundary Layer Inset Card (Bottom-Left)
            # Safe zone: Center around x = -2.20, y = -2.35
            # -----------------------------------------------------------------
            inset_box = RoundedRectangle(
                corner_radius=0.10,
                width=3.90,
                height=2.30,
                color="#39ff14",
                stroke_width=1.2,
                fill_color="#0d1117",
                fill_opacity=0.94
            ).move_to(np.array([-2.20, -2.35, 0.0]))

            if lang == "ES":
                inset_title = Text("PERFIL CAPA LÍMITE u(y)", font="Segoe UI", weight=BOLD, font_size=10, color="#39ff14").move_to(np.array([-2.20, -1.40, 0.0]))
            else:
                inset_title = Text("BOUNDARY LAYER PROFILE u(y)", font="Segoe UI", weight=BOLD, font_size=10, color="#39ff14").move_to(np.array([-2.20, -1.40, 0.0]))

            # Inset axes
            axis_x = Line(np.array([-3.7, -3.1, 0.0]), np.array([-0.7, -3.1, 0.0]), color="#4a5568", stroke_width=1.0)
            axis_y = Line(np.array([-2.5, -3.1, 0.0]), np.array([-2.5, -1.6, 0.0]), color="#ffffff", stroke_width=1.2)  # u = 0 wall

            def get_inset_profile():
                a = alpha_tracker.get_value()
                # Compute Pohlhausen lambda
                if a <= 4.0:
                    lam = 1.0
                elif a < 18.5:
                    lam = 1.0 - 16.0 * ((a - 4.0) / 14.5)
                else:
                    lam = -15.0

                eta_pts = np.linspace(0.0, 1.0, 25)
                u_profile = sim.pohlhausen_velocity_profile(eta_pts, lam)

                pts = [
                    np.array([-2.5 + u_val * 1.5, -3.1 + eta_val * 1.4, 0.0])
                    for u_val, eta_val in zip(u_profile, eta_pts)
                ]

                p_curve = VMobject(
                    stroke_color="#39ff14" if lam > -6.0 else ("#ffaa00" if lam > -12.0 else "#ff0055"),
                    stroke_width=2.5
                )
                p_curve.set_points_smoothly(pts)

                # Discrete velocity vectors showing boundary layer flow
                arrows_vg = VGroup()
                for eta_sample in [0.2, 0.4, 0.6, 0.8]:
                    u_s = sim.pohlhausen_velocity_profile(np.array([eta_sample]), lam)[0]
                    y_s = -3.1 + eta_sample * 1.4
                    if abs(u_s) > 0.04:
                        arr = Arrow(
                            start=np.array([-2.5, y_s, 0.0]),
                            end=np.array([-2.5 + u_s * 1.5, y_s, 0.0]),
                            buff=0,
                            color="#39ff14" if u_s > 0 else "#d600ff",
                            stroke_width=1.8,
                            max_tip_length_to_length_ratio=0.30
                        )
                        arrows_vg.add(arr)

                # Wall shear gradient indicator
                wall_slope_str = f"(∂u/∂y)|w = {max(2.0 + lam/6.0, -1.0):.2f}"
                wall_label = Text(
                    wall_slope_str,
                    font="Segoe UI",
                    font_size=9,
                    color="#ff0055" if lam <= -12.0 else "#00f0ff"
                ).move_to(np.array([-2.20, -3.32, 0.0]))

                # Backflow label if separated
                if lam <= -12.0:
                    bf_label = Text(
                        "FLUJO INVERSO" if lang == "ES" else "REVERSE FLOW",
                        font="Segoe UI", weight=BOLD, font_size=8, color="#d600ff"
                    ).move_to(np.array([-3.10, -2.80, 0.0]))
                    return VGroup(p_curve, arrows_vg, wall_label, bf_label)
                else:
                    return VGroup(p_curve, arrows_vg, wall_label)

            profile_group = always_redraw(get_inset_profile)
            self.add(VGroup(inset_box, inset_title, axis_x, axis_y, profile_group))

            # -----------------------------------------------------------------
            # 7. Polar Gauge Mini Inset Card (Bottom-Right)
            # Safe zone: Center around x = 2.20, y = -2.35
            # -----------------------------------------------------------------
            polar_box = RoundedRectangle(
                corner_radius=0.10,
                width=3.90,
                height=2.30,
                color="#00f0ff",
                stroke_width=1.2,
                fill_color="#0d1117",
                fill_opacity=0.94
            ).move_to(np.array([2.20, -2.35, 0.0]))

            if lang == "ES":
                polar_title = Text("TELEMETRÍA AERODINÁMICA", font="Segoe UI", weight=BOLD, font_size=10, color="#00f0ff").move_to(np.array([2.20, -1.40, 0.0]))
            else:
                polar_title = Text("AERODYNAMIC TELEMETRY", font="Segoe UI", weight=BOLD, font_size=10, color="#00f0ff").move_to(np.array([2.20, -1.40, 0.0]))

            def get_polar_readout():
                a = alpha_tracker.get_value()
                cl = sim.lift_coefficient(a)
                cd = sim.drag_coefficient(a)
                ld = cl / max(cd, 1e-4)

                cl_bar_w = min(cl / 1.6 * 2.6, 2.6)
                cd_bar_w = min(cd / 0.3 * 2.6, 2.6)

                bar_cl_bg = Rectangle(width=2.6, height=0.18, color="#1f2937", fill_color="#1f2937", fill_opacity=1.0).move_to(np.array([2.20, -1.85, 0.0]))
                bar_cl = Rectangle(
                    width=max(cl_bar_w, 0.05), height=0.18,
                    color="#00f0ff" if a <= 15.5 else "#ff0055",
                    fill_color="#00f0ff" if a <= 15.5 else "#ff0055",
                    fill_opacity=1.0
                ).align_to(bar_cl_bg, LEFT)

                bar_cd_bg = Rectangle(width=2.6, height=0.18, color="#1f2937", fill_color="#1f2937", fill_opacity=1.0).move_to(np.array([2.20, -2.45, 0.0]))
                bar_cd = Rectangle(
                    width=max(cd_bar_w, 0.05), height=0.18,
                    color="#ffaa00" if a <= 12.0 else "#ff007f",
                    fill_color="#ffaa00" if a <= 12.0 else "#ff007f",
                    fill_opacity=1.0
                ).align_to(bar_cd_bg, LEFT)

                lbl_cl = Text(f"Lift C_L: {cl:.2f}", font="Segoe UI", font_size=9, color="#ffffff").next_to(bar_cl_bg, UP, buff=0.06).align_to(bar_cl_bg, LEFT)
                lbl_cd = Text(f"Drag C_D: {cd:.3f}", font="Segoe UI", font_size=9, color="#ffffff").next_to(bar_cd_bg, UP, buff=0.06).align_to(bar_cd_bg, LEFT)

                eff_text = Text(f"L/D Efficiency: {ld:.1f}", font="Segoe UI", font_size=9, color="#39ff14" if ld > 10 else "#ff0055").move_to(np.array([2.20, -3.10, 0.0]))

                return VGroup(bar_cl_bg, bar_cl, lbl_cl, bar_cd_bg, bar_cd, lbl_cd, eff_text)

            polar_group = always_redraw(get_polar_readout)
            self.add(VGroup(polar_box, polar_title, polar_group))

            # -----------------------------------------------------------------
            # 8. Exact 18.0-Second Retention Timeline Execution
            # -----------------------------------------------------------------
            # 0.0s - 2.5s: Kinetic Hook (Laminar cruise flow at alpha = 4.0 deg)
            # Particles rush by, streamlines wave, vectors are fully active!
            self.play(
                time_tracker.animate.set_value(2.5),
                run_time=2.5,
                rate_func=linear
            )

            # 2.5s - 13.5s: Dynamic wing pitching to alpha = 18.5 deg & Deep Stall Crash
            self.play(
                alpha_tracker.animate.set_value(18.5),
                time_tracker.animate.set_value(13.5),
                run_time=11.0,
                rate_func=smooth
            )

            # 13.5s - 18.0s: Deep Stall Plateau, Violent Stall Buffet & Debate Callout
            self.play(
                time_tracker.animate.set_value(18.0),
                run_time=4.5,
                rate_func=linear
            )

    return AerodynamicStallScene


class MovingStallSceneES(create_stall_scene(lang="ES")):
    pass


class MovingStallSceneEN(create_stall_scene(lang="EN")):
    pass


def render_all():
    """
    Renders both Spanish and English versions with Manim, synthesizes procedural audio,
    and multiplexes into final 9:16 Full HD 60 FPS MP4 deliverables.
    """
    workspace_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    renders_dir = workspace_root / "RENDERS" / "7 Desprendimiento Capa Limite y Stall Aerodinamico"
    videos_dir = renders_dir / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)

    # 1. Synthesize Procedural Aero-Acoustic Audio (18.0s)
    temp_audio_path = str(videos_dir / "stall_audio_temp.wav")
    print("\n=======================================================")
    print("[CONTINUUM LAB] Synthesizing Aero-Acoustic Stall Audio (18.0s)...")
    print("=======================================================")
    synthesize_stall_audio(duration=18.0, fs=44100, output_path=temp_audio_path)

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    this_script = str(Path(__file__).resolve())

    # 2. Render Spanish Version
    print("\n=======================================================")
    print("[CONTINUUM LAB] Rendering Spanish Aerodynamic Stall Simulation (ES)...")
    print("=======================================================")
    cmd_manim_es = [
        "manim", "-qh", "--media_dir", str(videos_dir / "temp_media"),
        this_script, "MovingStallSceneES"
    ]
    subprocess.run(cmd_manim_es, check=True)

    raw_es = list((videos_dir / "temp_media").rglob("MovingStallSceneES.mp4"))[0]
    out_es = str(videos_dir / "Desprendimiento Capa Limite y Stall ES.mp4")

    print(f"[CONTINUUM LAB] Multiplexing ES Audio + Video -> {out_es}")
    cmd_mux_es = [
        ffmpeg_bin, "-y", "-i", str(raw_es), "-i", temp_audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_es
    ]
    subprocess.run(cmd_mux_es, check=True)

    # 3. Render English Version
    print("\n=======================================================")
    print("[CONTINUUM LAB] Rendering English Aerodynamic Stall Simulation (EN)...")
    print("=======================================================")
    cmd_manim_en = [
        "manim", "-qh", "--media_dir", str(videos_dir / "temp_media"),
        this_script, "MovingStallSceneEN"
    ]
    subprocess.run(cmd_manim_en, check=True)

    raw_en = list((videos_dir / "temp_media").rglob("MovingStallSceneEN.mp4"))[0]
    out_en = str(videos_dir / "Aerodynamic Stall Boundary Layer Separation EN.mp4")

    print(f"[CONTINUUM LAB] Multiplexing EN Audio + Video -> {out_en}")
    cmd_mux_en = [
        ffmpeg_bin, "-y", "-i", str(raw_en), "-i", temp_audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_en
    ]
    subprocess.run(cmd_mux_en, check=True)

    # Cleanup temporary files
    import shutil
    if os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)
    shutil.rmtree(str(videos_dir / "temp_media"), ignore_errors=True)

    print("\n=======================================================")
    print("[CONTINUUM LAB] ALL AERODYNAMIC STALL VIDEOS DELIVERED!")
    print(f"  - Spanish: {out_es}")
    print(f"  - English: {out_en}")
    print("=======================================================")


if __name__ == "__main__":
    render_all()
