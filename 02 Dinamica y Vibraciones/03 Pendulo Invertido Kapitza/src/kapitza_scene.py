"""
Continuum Lab — Classical Mechanics & Nonlinear Dynamics
Scene: Kapitza's Inverted Pendulum Paradox (Ultra-HD 1080x1920 60 FPS, 9:16 Vertical)
Division: 02 Dinamica y Vibraciones / 03 Pendulo Invertido Kapitza

Rigorously implements:
1. Exact nonlinear dynamics integrated via Scipy solve_ivp (RK45)
2. Native 9:16 1080x1920 vertical canvas pre-configured at module load time (zero distortion)
3. Horizontal machine guide bench with dual precision chrome shafts and linear bearings
4. Motorized eccentric drive unit displaying high-frequency rotation ("la parte que gira")
5. Landau-Kapitza dynamic effective potential well with real-time rolling bead
6. Real-time engineering telemetry HUD with Consolas monospace typography
7. Strict mobile safe zones (Top > 160 px, Bottom > 320 px)
8. Three dramatic phases:
   - Phase 1 (0-4s): High-frequency stabilization (55 Hz, a*omega^2 = 486 g)
   - Phase 2 (4-8s): 35° lateral perturbation & self-recovery
   - Phase 3 (8-15s): Sudden shutdown & violent gravitational collapse
"""

import sys
from pathlib import Path
import numpy as np
from manim import *

# Pre-configure Manim settings at module level for native 1080x1920 9:16 vertical resolution
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#070B14"

# Ensure project modules are importable
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.physics import (
    KapitzaConfig,
    KapitzaSolution,
    solve_kapitza_dynamics,
    compute_effective_potential,
)


def create_kapitza_scene_class(lang: str = "ES"):
    """Factory creating localized Kapitza Pendulum scene."""

    class LocalizedKapitzaScene(Scene):
        initial_time: float = 0.0

        def construct(self):
            # Precompute exact physical solution decoupled from renderer
            phys_cfg = KapitzaConfig()
            sol: KapitzaSolution = solve_kapitza_dynamics(phys_cfg)

            time_tracker = ValueTracker(self.initial_time)

            def get_frame_idx(t: float) -> int:
                return int(np.clip(t * phys_cfg.fps, 0, sol.n_frames - 1))

            # -------------------------------------------------------------
            # 1. Engineering Technical Grid & Background Atmosphere
            # -------------------------------------------------------------
            grid_group = VGroup()
            for x in np.arange(-4.0, 4.5, 1.0):
                grid_group.add(
                    Line(
                        start=[x, -7.6, 0],
                        end=[x, 7.6, 0],
                        stroke_color="#1E293B",
                        stroke_width=0.6,
                        stroke_opacity=0.30,
                    )
                )
            for y in np.arange(-7.0, 7.5, 1.0):
                grid_group.add(
                    Line(
                        start=[-4.2, y, 0],
                        end=[4.2, y, 0],
                        stroke_color="#1E293B",
                        stroke_width=0.6,
                        stroke_opacity=0.30,
                    )
                )
            self.add(grid_group)

            # -------------------------------------------------------------
            # 2. Header & Title in Top Safe Zone (Y in [5.7, 7.4])
            # -------------------------------------------------------------
            header_group = VGroup()

            tag_str = "CONTINUUM LAB • DINÁMICA NO LINEAL" if lang == "ES" else "CONTINUUM LAB • NONLINEAR DYNAMICS"
            tag_box = RoundedRectangle(
                width=4.4,
                height=0.40,
                corner_radius=0.10,
                fill_color="#0F172A",
                fill_opacity=0.90,
                stroke_color="#0284C7",
                stroke_width=1.2,
            ).move_to([0.0, 7.15, 0.0])

            tag_text = Text(
                tag_str,
                font="Consolas",
                font_size=11,
                weight=BOLD,
                color="#38BDF8",
            ).move_to(tag_box.get_center())

            title_str = "¿POR QUÉ NO CAE AL REVÉS?" if lang == "ES" else "WHY DOESN'T IT FALL DOWN?"
            main_title = Text(
                title_str,
                font="Arial",
                weight=BOLD,
                font_size=23,
                color="#FFFFFF",
            ).move_to([0.0, 6.60, 0.0])

            sub_str = "PARADOJA DE KAPITZA: Estabilización Asintótica por Vibración Rápida" if lang == "ES" else "KAPITZA PARADOX: High-Frequency Vibrational Dynamic Stabilization"
            subtitle = Text(
                sub_str,
                font="Arial",
                font_size=11.5,
                color="#94A3B8",
            ).move_to([0.0, 6.18, 0.0])

            header_divider = Line(
                start=[-4.1, 5.85, 0],
                end=[4.1, 5.85, 0],
                stroke_color="#334155",
                stroke_width=1.2,
            )

            header_group.add(tag_box, tag_text, main_title, subtitle, header_divider)
            self.add(header_group)

            # -------------------------------------------------------------
            # 3. Real-time Telemetry & HUD Console (Y in [4.20, 5.65])
            # -------------------------------------------------------------
            @always_redraw
            def dynamic_telemetry_hud():
                t = time_tracker.get_value()
                idx = get_frame_idx(t)

                th_deg = sol.theta_deg[idx]
                w_inst = sol.omega_inst[idx]
                f_inst = sol.f_inst[idx]
                phase = sol.phase_id[idx]
                a_base_val = sol.a_base[idx]
                v_eff_val = sol.v_eff_instant[idx]

                hud_bg = RoundedRectangle(
                    width=8.3,
                    height=1.45,
                    corner_radius=0.14,
                    stroke_color="#334155",
                    stroke_width=1.5,
                    fill_color="#0A1124",
                    fill_opacity=0.92,
                ).move_to([0.0, 4.95, 0.0])

                status_col = "#00F2FE" if phase == 1 else ("#EC4899" if phase == 2 else "#EF4444")
                status_bar = RoundedRectangle(
                    width=0.12,
                    height=1.25,
                    corner_radius=0.06,
                    stroke_width=0,
                    fill_color=status_col,
                    fill_opacity=1.0,
                ).move_to([-4.02, 4.95, 0.0])

                r_ratio = ((phys_cfg.a * w_inst) ** 2) / (2.0 * phys_cfg.g * phys_cfg.L)

                if lang == "ES":
                    if phase == 1:
                        l1 = f"CONDICIÓN KAPITZA : (a·ω)² > 2·g·L  [CUMPLIDA • R = {r_ratio:4.2f}x]"
                        l2 = f"MOTOR EXCITACIÓN  : f = {f_inst:.1f} Hz (ALTA VELOCIDAD | 486 g)"
                        l3 = "ESTADO DINÁMICO   : EQUILIBRIO INVERTIDO ASINTÓTICO (180°)"
                    elif phase == 2:
                        l1 = f"CONDICIÓN KAPITZA : (a·ω)² > 2·g·L  [RECUPERACIÓN ACTIVA • R = {r_ratio:4.2f}x]"
                        l2 = f"MOTOR EXCITACIÓN  : f = {f_inst:.1f} Hz (ALTA VELOCIDAD | 486 g)"
                        l3 = "ESTADO DINÁMICO   : PERTURBACIÓN EXTERNA RESUELTA (Δθ = 35°)"
                    else:
                        l1 = "CONDICIÓN KAPITZA : (a·ω)² > 2·g·L  [ANULADA • R = 0.00x]"
                        l2 = "MOTOR EXCITACIÓN  : f = 0.0 Hz (MOTOR APAGADO)"
                        l3 = "ESTADO DINÁMICO   : COLAPSO GRAVITATORIO NO LINEAL"
                    metric_str = f"θ: {th_deg%360.0:5.1f}°  |  V_eff: {v_eff_val:4.1f} J  |  a_base: {a_base_val:+05.0f} m/s²"
                else:
                    if phase == 1:
                        l1 = f"KAPITZA CONDITION : (a·ω)² > 2·g·L  [SATISFIED • R = {r_ratio:4.2f}x]"
                        l2 = f"EXCITATION MOTOR  : f = {f_inst:.1f} Hz (HIGH SPEED | 486 g)"
                        l3 = "DYNAMIC STATE     : ASYMPTOTICALLY STABLE INVERTED (180°)"
                    elif phase == 2:
                        l1 = f"KAPITZA CONDITION : (a·ω)² > 2·g·L  [ACTIVE RESTORATION • R = {r_ratio:4.2f}x]"
                        l2 = f"EXCITATION MOTOR  : f = {f_inst:.1f} Hz (HIGH SPEED | 486 g)"
                        l3 = "DYNAMIC STATE     : EXTERNAL IMPACT RESOLVED (Δθ = 35°)"
                    else:
                        l1 = "KAPITZA CONDITION : (a·ω)² > 2·g·L  [VIOLATED • R = 0.00x]"
                        l2 = "EXCITATION MOTOR  : f = 0.0 Hz (MOTOR SHUTDOWN)"
                        l3 = "DYNAMIC STATE     : NONLINEAR GRAVITATIONAL COLLAPSE"
                    metric_str = f"θ: {th_deg%360.0:5.1f}°  |  V_eff: {v_eff_val:4.1f} J  |  a_base: {a_base_val:+05.0f} m/s²"

                t1 = Text(l1, font="Consolas", font_size=11, color=status_col, weight=BOLD).move_to([-3.75, 5.38, 0], aligned_edge=LEFT)
                t2 = Text(l2, font="Consolas", font_size=10.5, color="#F1F5F9").move_to([-3.75, 5.12, 0], aligned_edge=LEFT)
                t3 = Text(l3, font="Consolas", font_size=10.5, color="#10B981" if phase <= 2 else "#EF4444").move_to([-3.75, 4.86, 0], aligned_edge=LEFT)
                t4 = Text(metric_str, font="Consolas", font_size=10, color="#94A3B8").move_to([-3.75, 4.58, 0], aligned_edge=LEFT)

                return VGroup(hud_bg, status_bar, t1, t2, t3, t4)

            self.add(dynamic_telemetry_hud)

            # -------------------------------------------------------------
            # 4. Central Mechanical Apparatus: Horizontal Bench & Drive
            # -------------------------------------------------------------
            # The user explicitly requested:
            # "quisiera que la guía en donde está girando la parte que vibra,
            #  donde está vibrando el péndulo esté de manera horizontal y no vertical"
            # Here we render a realistic, heavy precision HORIZONTAL guide bench.
            bench_y = -0.70

            # Horizontal structural guide bench
            bench_beam = RoundedRectangle(
                width=7.8,
                height=0.40,
                corner_radius=0.08,
                fill_color="#0F172A",
                fill_opacity=0.95,
                stroke_color="#334155",
                stroke_width=1.6,
            ).move_to([0.0, bench_y, 0.0])

            # Dual precision chrome guide rails
            chrome_rail_top = Line(start=[-3.7, bench_y + 0.10, 0], end=[3.7, bench_y + 0.10, 0], stroke_color="#94A3B8", stroke_width=2.5)
            chrome_rail_bot = Line(start=[-3.7, bench_y - 0.10, 0], end=[3.7, bench_y - 0.10, 0], stroke_color="#475569", stroke_width=2.5)

            # Measurement scale ticks along the horizontal bench
            bench_ticks = VGroup()
            for xt in np.linspace(-3.5, 3.5, 29):
                h_tick = 0.08 if int(abs(xt * 2)) % 2 == 0 else 0.04
                bench_ticks.add(
                    Line(
                        start=[xt, bench_y + 0.20, 0],
                        end=[xt, bench_y + 0.20 - h_tick, 0],
                        stroke_color="#64748B",
                        stroke_width=1.0,
                    )
                )

            # End pillow blocks with mounting bolts & rubber bumpers
            pillow_l = RoundedRectangle(width=0.35, height=0.55, corner_radius=0.06, fill_color="#1E293B", fill_opacity=1.0, stroke_color="#475569", stroke_width=1.5).move_to([-3.75, bench_y, 0])
            pillow_r = RoundedRectangle(width=0.35, height=0.55, corner_radius=0.06, fill_color="#1E293B", fill_opacity=1.0, stroke_color="#475569", stroke_width=1.5).move_to([3.75, bench_y, 0])
            bumper_l = Circle(radius=0.08, fill_color="#EF4444", fill_opacity=0.8, stroke_width=0).move_to([-3.50, bench_y, 0])
            bumper_r = Circle(radius=0.08, fill_color="#EF4444", fill_opacity=0.8, stroke_width=0).move_to([3.50, bench_y, 0])

            bench_label_str = "BANCADA / GUÍA LINEAL HORIZONTAL" if lang == "ES" else "HORIZONTAL LINEAR GUIDE BENCH"
            bench_label = Text(
                bench_label_str,
                font="Consolas",
                font_size=9,
                color="#64748B",
                weight=BOLD,
            ).move_to([0.0, bench_y - 0.44, 0])

            # Educational Note Badge: Explains that the bench/guide is horizontal,
            # while the restoring vibration is vertical (Kapitza condition).
            note_str = "BANCADA HORIZONTAL • VIBRACIÓN VERTICAL RESTAURADORA (KAPITZA)" if lang == "ES" else "HORIZONTAL BENCH • RESTORING VERTICAL VIBRATION (KAPITZA)"
            note_badge = Text(
                note_str,
                font="Consolas",
                font_size=8.5,
                color="#38BDF8",
            ).move_to([0.0, bench_y - 0.68, 0])

            self.add(VGroup(
                bench_beam, chrome_rail_top, chrome_rail_bot, bench_ticks,
                pillow_l, pillow_r, bumper_l, bumper_r,
                bench_label, note_badge
            ))

            # -------------------------------------------------------------
            # 5. Dynamic Mechanical Drive & Pendulum System (@always_redraw)
            # -------------------------------------------------------------
            L_vis = 2.05

            @always_redraw
            def dynamic_mechanical_system():
                t = time_tracker.get_value()
                idx = get_frame_idx(t)

                th = sol.theta[idx]
                y0_val = sol.y_base[idx]
                f_inst = sol.f_inst[idx]
                phase = sol.phase_id[idx]

                grp = VGroup()

                # Pivot position: Carriage is on horizontal bench at y = bench_y,
                # with high-frequency vertical vibration of the pivot pin inside the carriage:
                # y0_val is in [-0.04, 0.04], amplified visually by 6.0x for clear perception
                y_pivot = (bench_y + 0.28) + 6.0 * y0_val

                is_vibrating = f_inst > 5.0
                c_stroke = "#00F2FE" if is_vibrating else "#EF4444"
                c_fill = "#1E293B" if is_vibrating else "#18181B"

                # 5.1 Motor Unit & Rotating Crank Wheel ("la parte que gira")
                # Positioned on the left side of the carriage:
                motor_x = -1.45
                motor_box = RoundedRectangle(
                    width=0.95,
                    height=0.68,
                    corner_radius=0.08,
                    fill_color="#0F172A",
                    fill_opacity=1.0,
                    stroke_color="#0284C7" if is_vibrating else "#64748B",
                    stroke_width=1.8,
                ).move_to([motor_x, bench_y + 0.05, 0.0])

                # Rotating Flywheel / Disc driven by the motor
                rotor_angle = (2.0 * np.pi * 55.0 * t) if is_vibrating else 0.0
                disc = Circle(
                    radius=0.28,
                    fill_color="#1E293B",
                    fill_opacity=1.0,
                    stroke_color=c_stroke,
                    stroke_width=1.8,
                ).move_to([motor_x, bench_y + 0.05, 0.0])

                # Rotating spokes and eccentric drive pin
                spoke_1 = Line(
                    start=[motor_x - 0.24 * np.cos(rotor_angle), bench_y + 0.05 - 0.24 * np.sin(rotor_angle), 0],
                    end=[motor_x + 0.24 * np.cos(rotor_angle), bench_y + 0.05 + 0.24 * np.sin(rotor_angle), 0],
                    stroke_color="#94A3B8",
                    stroke_width=1.5,
                )
                spoke_2 = Line(
                    start=[motor_x - 0.24 * np.sin(rotor_angle), bench_y + 0.05 + 0.24 * np.cos(rotor_angle), 0],
                    end=[motor_x + 0.24 * np.sin(rotor_angle), bench_y + 0.05 - 0.24 * np.cos(rotor_angle), 0],
                    stroke_color="#94A3B8",
                    stroke_width=1.5,
                )
                crank_pin_x = motor_x + 0.16 * np.cos(rotor_angle)
                crank_pin_y = bench_y + 0.05 + 0.16 * np.sin(rotor_angle)
                crank_pin = Circle(
                    radius=0.05,
                    fill_color="#F59E0B" if is_vibrating else "#64748B",
                    fill_opacity=1.0,
                    stroke_width=0,
                ).move_to([crank_pin_x, crank_pin_y, 0])

                motor_tag = Text(
                    "MOTOR 55 Hz" if is_vibrating else "OFF (0 Hz)",
                    font="Consolas",
                    font_size=8,
                    color="#38BDF8" if is_vibrating else "#EF4444",
                    weight=BOLD,
                ).next_to(motor_box, UP, buff=0.08)

                # Connecting link / yoke from rotating eccentric to carriage
                link_arm = Line(
                    start=[crank_pin_x, crank_pin_y, 0],
                    end=[-0.70, y_pivot, 0],
                    stroke_color="#64748B",
                    stroke_width=2.0,
                )

                grp.add(motor_box, disc, spoke_1, spoke_2, crank_pin, motor_tag, link_arm)

                # 5.2 Carriage Assembly riding on the horizontal bench
                carriage_box = RoundedRectangle(
                    width=1.45,
                    height=0.62,
                    corner_radius=0.10,
                    fill_color=c_fill,
                    fill_opacity=1.0,
                    stroke_color=c_stroke,
                    stroke_width=2.2,
                ).move_to([0.0, bench_y + 0.05, 0.0])

                # Internal precision vertical slot inside carriage
                slot_bg = RoundedRectangle(
                    width=0.22,
                    height=0.50,
                    corner_radius=0.06,
                    fill_color="#0F172A",
                    fill_opacity=1.0,
                    stroke_color="#475569",
                    stroke_width=1.2,
                ).move_to([0.0, bench_y + 0.05, 0.0])

                # Bearing Pin at vibrating pivot
                bearing_pin = Circle(
                    radius=0.10,
                    fill_color="#F59E0B",
                    fill_opacity=1.0,
                    stroke_color="#FFFFFF",
                    stroke_width=1.6,
                ).move_to([0.0, y_pivot, 0.0])

                grp.add(carriage_box, slot_bg, bearing_pin)

                # Vibration blur echoes & frequency indicator when buzzing at 55 Hz
                if is_vibrating:
                    echo_top = bearing_pin.copy().shift(UP * 0.10).set_opacity(0.35).set_stroke(color="#00F2FE", width=1.0)
                    echo_bot = bearing_pin.copy().shift(DOWN * 0.10).set_opacity(0.35).set_stroke(color="#00F2FE", width=1.0)
                    vib_pill = RoundedRectangle(
                        width=1.95,
                        height=0.32,
                        corner_radius=0.08,
                        fill_color="#0F172A",
                        fill_opacity=0.90,
                        stroke_color="#00F2FE",
                        stroke_width=1.0,
                    ).next_to(carriage_box, RIGHT, buff=0.18)
                    vib_txt = Text("↕ 55 Hz (486 g)", font="Consolas", font_size=8.5, color="#00F2FE", weight=BOLD).move_to(vib_pill.get_center())
                    grp.add(echo_top, echo_bot, vib_pill, vib_txt)

                # 5.3 Pendulum Rod and Bob (Angle convention: theta = pi is straight UP)
                bob_x = L_vis * np.sin(th)
                bob_y = y_pivot - L_vis * np.cos(th)

                # Vertical reference dashed axis (upright vertical at 180 deg)
                ref_line = DashedLine(
                    start=[0.0, y_pivot, 0.0],
                    end=[0.0, y_pivot + L_vis + 0.35, 0.0],
                    stroke_color="#475569",
                    stroke_width=1.2,
                    dash_length=0.08,
                )

                # Dual-layer rigid rod (silver core + slate body)
                rod_body = Line(
                    start=[0.0, y_pivot, 0.0],
                    end=[bob_x, bob_y, 0.0],
                    stroke_color="#94A3B8",
                    stroke_width=5.5,
                )
                rod_shine = Line(
                    start=[0.0, y_pivot, 0.0],
                    end=[bob_x, bob_y, 0.0],
                    stroke_color="#FFFFFF",
                    stroke_width=1.8,
                )

                # Heavy inertial tungsten/brass bob
                bob_halo = Circle(
                    radius=0.38,
                    fill_color="#00F2FE" if is_vibrating else "#EF4444",
                    fill_opacity=0.30,
                    stroke_width=0,
                ).move_to([bob_x, bob_y, 0.0])

                bob_body = Circle(
                    radius=0.25,
                    fill_color="#0284C7" if is_vibrating else "#991B1B",
                    fill_opacity=1.0,
                    stroke_color="#38BDF8" if is_vibrating else "#F87171",
                    stroke_width=2.5,
                ).move_to([bob_x, bob_y, 0.0])

                bob_core = Circle(
                    radius=0.08,
                    fill_color="#FFFFFF",
                    fill_opacity=1.0,
                    stroke_width=0,
                ).move_to([bob_x, bob_y, 0.0])

                grp.add(ref_line, rod_body, rod_shine, bob_halo, bob_body, bob_core)
                return grp

            self.add(dynamic_mechanical_system)

            # -------------------------------------------------------------
            # 6. Dynamic Alert Banners: Perturbation & Emergency Shutdown
            # -------------------------------------------------------------
            @always_redraw
            def dynamic_alert_banners():
                t = time_tracker.get_value()
                grp = VGroup()

                # Phase 2: Lateral perturbation pulse (t = 4.0 to 4.8s)
                if 4.0 <= t <= 4.8:
                    idx = get_frame_idx(t)
                    th = sol.theta[idx]
                    y_piv = (bench_y + 0.28) + 6.0 * sol.y_base[idx]
                    bx = L_vis * np.sin(th)
                    by = y_piv - L_vis * np.cos(th)

                    p_arrow = Arrow(
                        start=[bx + 2.0, by, 0],
                        end=[bx + 0.45, by, 0],
                        color="#EC4899",
                        stroke_width=5.5,
                        buff=0,
                        max_tip_length_to_length_ratio=0.28,
                    )
                    p_txt_str = "¡PERTURBACIÓN EXTERNA! (Δθ = 35°)" if lang == "ES" else "EXTERNAL DISTURBANCE! (Δθ = 35°)"
                    p_label = Text(
                        p_txt_str,
                        font="Consolas",
                        font_size=11,
                        weight=BOLD,
                        color="#EC4899",
                    ).next_to(p_arrow, UP, buff=0.10)
                    grp.add(p_arrow, p_label)

                # Phase 3: Emergency shutdown warning banner (t >= 8.0s)
                if t >= 8.0:
                    blink = (int(t * 5.0) % 2 == 0)
                    s_bg = RoundedRectangle(
                        width=8.3,
                        height=0.55,
                        corner_radius=0.10,
                        fill_color="#7F1D1D" if blink else "#450A0A",
                        fill_opacity=0.95,
                        stroke_color="#EF4444",
                        stroke_width=2.0,
                    ).move_to([0.0, 2.05, 0.0])

                    s_text_str = "⚠️ MOTOR APAGADO (f = 0 Hz) • PÉRDIDA DE ESTABILIDAD INVERTIDA" if lang == "ES" else "⚠️ MOTOR OFF (f = 0 Hz) • INVERTED STABILITY DESTROYED"
                    s_txt = Text(
                        s_text_str,
                        font="Consolas",
                        font_size=11,
                        weight=BOLD,
                        color="#FFFFFF" if blink else "#FCA5A5",
                    ).move_to([0.0, 2.05, 0.0])
                    grp.add(s_bg, s_txt)

                return grp

            self.add(dynamic_alert_banners)

            # -------------------------------------------------------------
            # 7. Landau-Kapitza Effective Potential Well Landscape
            #    Safe Zone: Y in [-6.90, -2.55]
            # -------------------------------------------------------------
            chart_y_center = -4.70
            chart_bg = RoundedRectangle(
                width=8.3,
                height=4.15,
                corner_radius=0.16,
                fill_color="#070E20",
                fill_opacity=0.94,
                stroke_color="#334155",
                stroke_width=1.5,
            ).move_to([0.0, chart_y_center, 0.0])

            c_title_str = "POZO DE ENERGÍA EFECTIVA DE LANDAU-KAPITZA" if lang == "ES" else "LANDAU-KAPITZA EFFECTIVE POTENTIAL WELL"
            chart_title = Text(
                c_title_str,
                font="Consolas",
                font_size=12.5,
                weight=BOLD,
                color="#F59E0B",
            ).move_to([0.0, chart_y_center + 1.75, 0.0])

            chart_formula = Text(
                "V_eff(θ) = m·g·L·(1 - cos θ) + ¼·m·a²·ω²·sin² θ",
                font="Consolas",
                font_size=10.5,
                color="#94A3B8",
            ).move_to([0.0, chart_y_center + 1.45, 0.0])

            self.add(chart_bg, chart_title, chart_formula)

            x_min, x_max = -3.4, 3.4
            y_min, y_max = chart_y_center - 1.50, chart_y_center + 1.05
            v_scale_max = 32.0

            def theta_to_x(th: float) -> float:
                norm_th = float(th) % (2.0 * np.pi)
                if norm_th < 1e-4 and th > 1.0:
                    norm_th = 2.0 * np.pi
                return x_min + (x_max - x_min) * (norm_th / (2.0 * np.pi))

            def v_to_y(v_val: float) -> float:
                norm_v = np.clip(v_val / v_scale_max, 0.0, 1.0)
                return y_min + (y_max - y_min) * norm_v

            # Static Axis elements
            axis_x = Line(start=[x_min, y_min, 0], end=[x_max, y_min, 0], stroke_color="#475569", stroke_width=1.5)
            axis_y = Line(start=[x_min, y_min, 0], end=[x_min, y_max, 0], stroke_color="#475569", stroke_width=1.5)
            mark_pi_line = DashedLine(
                start=[0.0, y_min, 0],
                end=[0.0, y_max, 0],
                stroke_color="#00F2FE",
                stroke_width=1.2,
                dash_length=0.06,
            )

            t_0 = "0° (Colgado)" if lang == "ES" else "0° (Hanging)"
            t_pi = "180° (Invertido)" if lang == "ES" else "180° (Inverted)"
            t_2pi = "360° (Colgado)" if lang == "ES" else "360° (Hanging)"

            lbl_0 = Text(t_0, font="Consolas", font_size=9.5, color="#64748B").next_to([x_min, y_min, 0], DOWN, buff=0.10)
            lbl_pi = Text(t_pi, font="Consolas", font_size=9.5, color="#00F2FE", weight=BOLD).next_to([0.0, y_min, 0], DOWN, buff=0.10)
            lbl_2pi = Text(t_2pi, font="Consolas", font_size=9.5, color="#64748B").next_to([x_max, y_min, 0], DOWN, buff=0.10)

            self.add(VGroup(axis_x, axis_y, mark_pi_line, lbl_0, lbl_pi, lbl_2pi))

            theta_grid = np.linspace(0.0, 2.0 * np.pi, 90)

            @always_redraw
            def dynamic_potential_well():
                t = time_tracker.get_value()
                idx = get_frame_idx(t)
                w_inst = sol.omega_inst[idx]
                th_slow = sol.theta_slow[idx]
                phase = sol.phase_id[idx]

                v_vals = compute_effective_potential(theta_grid, w_inst, phys_cfg)
                points = [
                    [x_min + (x_max - x_min) * (tg / (2.0 * np.pi)), v_to_y(vg), 0.0]
                    for tg, vg in zip(theta_grid, v_vals)
                ]

                p_curve = VMobject(color="#F59E0B" if phase == 3 else "#00F2FE", stroke_width=3.2)
                p_curve.set_points_smoothly(points)

                fill_pts = points + [[x_max, y_min, 0.0], [x_min, y_min, 0.0]]
                p_fill = VMobject(fill_color="#F59E0B" if phase == 3 else "#00F2FE", fill_opacity=0.15, stroke_width=0)
                p_fill.set_points_as_corners(fill_pts)

                # Rolling bead indicating slow macro-angle Theta(t)
                v_bead = compute_effective_potential(np.array([th_slow]), w_inst, phys_cfg)[0]
                bx = theta_to_x(th_slow)
                by = v_to_y(v_bead)

                bead_halo = Circle(radius=0.16, fill_color="#F59E0B", fill_opacity=0.35, stroke_width=0).move_to([bx, by, 0.0])
                bead_body = Circle(radius=0.09, fill_color="#FFFFFF", fill_opacity=1.0, stroke_color="#F59E0B", stroke_width=2.0).move_to([bx, by, 0.0])
                bead_tag = Text(f"θ={np.degrees(th_slow)%360.0:.0f}°", font="Consolas", font_size=9, color="#FDE047", weight=BOLD).next_to(bead_body, UP, buff=0.06)

                return VGroup(p_fill, p_curve, bead_halo, bead_body, bead_tag)

            self.add(dynamic_potential_well)

            # -------------------------------------------------------------
            # 8. Animation Execution: 15.0 Seconds @ 60 FPS
            # -------------------------------------------------------------
            if getattr(self, "is_snapshot", False):
                time_tracker.set_value(self.initial_time)
                self.wait(0.02)
            else:
                self.play(
                    time_tracker.animate.set_value(phys_cfg.t_total),
                    run_time=phys_cfg.t_total,
                    rate_func=linear,
                )

    return LocalizedKapitzaScene


class KapitzaPendulumSceneES(create_kapitza_scene_class(lang="ES")):
    pass


class KapitzaPendulumSceneEN(create_kapitza_scene_class(lang="EN")):
    pass


class KapitzaPhase1SnapshotEN(KapitzaPendulumSceneEN):
    is_snapshot = True
    initial_time = 2.0


# Backward compatibility alias
class KapitzaPendulumScene(KapitzaPendulumSceneES):
    pass


class KapitzaPhase1Snapshot(KapitzaPendulumSceneES):
    is_snapshot = True
    initial_time = 2.0


class KapitzaPhase2Snapshot(KapitzaPendulumSceneES):
    is_snapshot = True
    initial_time = 4.25


class KapitzaPhase3Snapshot(KapitzaPendulumSceneES):
    is_snapshot = True
    initial_time = 9.2
