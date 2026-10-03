"""
Continuum Lab — Classical Mechanics & Nonlinear Dynamics
Scene: Kapitza's Inverted Pendulum Paradox (Ultra-HD 1080x1920 60 FPS, 9:16 Vertical)
Division: 02 Dinamica y Vibraciones / 03 Pendulo Invertido Kapitza

Rigorously implements:
1. Exact nonlinear dynamics integrated via Scipy solve_ivp
2. Landau-Kapitza effective potential well visualization with rolling bead
3. Real-time telemetry HUD formatted with Consolas monospace typography
4. Strict mobile safe zones (Top > 160 px, Bottom > 320 px)
5. Three dramatic phases:
   - Phase 1 (0-4s): High-frequency stabilization (55 Hz)
   - Phase 2 (4-8s): 35° lateral perturbation & self-recovery
   - Phase 3 (8-15s): Sudden shutdown & violent gravitational collapse
"""

import sys
from pathlib import Path
import numpy as np
from manim import *

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


def set_vgroup_opacity(vgroup: VGroup, opacity: float):
    """Sets opacity recursively across all submobjects."""
    vgroup.set_opacity(opacity)
    for sub in vgroup.submobjects:
        sub.set_opacity(opacity)
        if isinstance(sub, VGroup):
            set_vgroup_opacity(sub, opacity)


class KapitzaPendulumScene(Scene):
    """
    Manim Community 1080x1920 60 FPS 9:16 vertical visualization
    of the Kapitza Inverted Pendulum Paradox.
    """
    initial_time: float = 0.0

    def construct(self):
        # -------------------------------------------------------------
        # 1. Canvas & Physical Engine Integration
        # -------------------------------------------------------------
        config.pixel_width = 1080
        config.pixel_height = 1920
        config.frame_width = 9.0
        config.frame_height = 16.0
        config.background_color = "#070B12"

        # Precompute exact physical solution decoupled from renderer
        phys_cfg = KapitzaConfig()
        sol: KapitzaSolution = solve_kapitza_dynamics(phys_cfg)

        time_tracker = ValueTracker(self.initial_time)

        def get_frame_idx(t: float) -> int:
            return int(np.clip(t * phys_cfg.fps, 0, sol.n_frames - 1))

        # -------------------------------------------------------------
        # 2. Engineering Technical Background & Atmosphere
        # -------------------------------------------------------------
        grid_lines = VGroup()
        for x in np.arange(-4.0, 4.5, 1.0):
            grid_lines.add(
                Line(
                    start=[x, -7.5, 0],
                    end=[x, 7.5, 0],
                    stroke_color="#1E293B",
                    stroke_width=0.6,
                    stroke_opacity=0.35,
                )
            )
        for y in np.arange(-7.0, 7.5, 1.0):
            grid_lines.add(
                Line(
                    start=[-4.2, y, 0],
                    end=[4.2, y, 0],
                    stroke_color="#1E293B",
                    stroke_width=0.6,
                    stroke_opacity=0.35,
                )
            )
        self.add(grid_lines)

        # -------------------------------------------------------------
        # 3. Header & Branding (Safe Zone: y in [5.4, 6.6])
        # -------------------------------------------------------------
        brand_badge = Text(
            "CONTINUUM LAB • DINÁMICA NO LINEAL",
            font="Consolas",
            font_size=13,
            color="#38BDF8",
        ).move_to([0.0, 6.45, 0.0])

        main_title = Text(
            "PARADOJA DE KAPITZA",
            font="Arial",
            weight=BOLD,
            font_size=28,
            color="#FFFFFF",
        ).next_to(brand_badge, DOWN, buff=0.15)

        subtitle = Text(
            "Estabilización Invertida por Alta Frecuencia",
            font="Arial",
            font_size=15,
            color="#94A3B8",
        ).next_to(main_title, DOWN, buff=0.12)

        self.add(brand_badge, main_title, subtitle)

        # -------------------------------------------------------------
        # 4. Real-time Glassmorphic Telemetry HUD (y in [3.25, 5.35])
        # -------------------------------------------------------------
        hud_bg = RoundedRectangle(
            width=8.2,
            height=2.05,
            corner_radius=0.15,
            stroke_color="#334155",
            stroke_width=1.5,
            fill_color="#0F172A",
            fill_opacity=0.90,
        ).move_to([0.0, 4.30, 0.0])

        hud_status_bar = RoundedRectangle(
            width=0.12,
            height=1.85,
            corner_radius=0.06,
            stroke_width=0,
            fill_color="#00F2FE",
            fill_opacity=1.0,
        ).move_to([-3.92, 4.30, 0.0])

        hud_divider = Line(
            start=[-3.7, 3.65, 0],
            end=[3.7, 3.65, 0],
            stroke_color="#1E293B",
            stroke_width=1.0,
        )

        self.add(hud_bg, hud_status_bar, hud_divider)

        # Pre-build HUD text groups for the three phases to guarantee 60 FPS
        # Phase 1 HUD lines
        p1_l1 = Text("CONDICIÓN KAPITZA : (a·ω)² > 2·g·L (CUMPLIDA)", font="Consolas", font_size=13, color="#00F2FE").move_to([-3.65, 5.00, 0], aligned_edge=LEFT)
        p1_l2 = Text("FRECUENCIA BASE   : f = 55.0 Hz (ALTA VELOCIDAD)", font="Consolas", font_size=13, color="#F1F5F9").move_to([-3.65, 4.65, 0], aligned_edge=LEFT)
        p1_l3 = Text("EQUILIBRIO VERTICAL: ASINTÓTICAMENTE ESTABLE", font="Consolas", font_size=13, color="#10B981").move_to([-3.65, 4.30, 0], aligned_edge=LEFT)
        p1_l4 = Text("ESTADO DINÁMICO   : POZO DE ENERGÍA EFECTIVA", font="Consolas", font_size=13, color="#F59E0B").move_to([-3.65, 3.95, 0], aligned_edge=LEFT)
        hud_p1 = VGroup(p1_l1, p1_l2, p1_l3, p1_l4)

        # Phase 2 HUD lines
        p2_l1 = Text("CONDICIÓN KAPITZA : (a·ω)² > 2·g·L (CUMPLIDA)", font="Consolas", font_size=13, color="#00F2FE").move_to([-3.65, 5.00, 0], aligned_edge=LEFT)
        p2_l2 = Text("FRECUENCIA BASE   : f = 55.0 Hz (ALTA VELOCIDAD)", font="Consolas", font_size=13, color="#F1F5F9").move_to([-3.65, 4.65, 0], aligned_edge=LEFT)
        p2_l3 = Text("EQUILIBRIO VERTICAL: ASINTÓTICAMENTE ESTABLE", font="Consolas", font_size=13, color="#10B981").move_to([-3.65, 4.30, 0], aligned_edge=LEFT)
        p2_l4 = Text("ESTADO DINÁMICO   : PERTURBACIÓN EXTERNA (Δθ = 35°)", font="Consolas", font_size=13, color="#FF0055").move_to([-3.65, 3.95, 0], aligned_edge=LEFT)
        hud_p2 = VGroup(p2_l1, p2_l2, p2_l3, p2_l4)

        # Phase 3 HUD lines
        p3_l1 = Text("CONDICIÓN KAPITZA : (a·ω)² > 2·g·L (ANULADA)", font="Consolas", font_size=13, color="#EF4444").move_to([-3.65, 5.00, 0], aligned_edge=LEFT)
        p3_l2 = Text("FRECUENCIA BASE   : f = 0.0 Hz (MOTOR APAGADO)", font="Consolas", font_size=13, color="#94A3B8").move_to([-3.65, 4.65, 0], aligned_edge=LEFT)
        p3_l3 = Text("EQUILIBRIO VERTICAL: ESTÁTICAMENTE INESTABLE", font="Consolas", font_size=13, color="#EF4444").move_to([-3.65, 4.30, 0], aligned_edge=LEFT)
        p3_l4 = Text("ESTADO DINÁMICO   : DESPLOME / CAÍDA LIBRE", font="Consolas", font_size=13, color="#F87171").move_to([-3.65, 3.95, 0], aligned_edge=LEFT)
        hud_p3 = VGroup(p3_l1, p3_l2, p3_l3, p3_l4)

        set_vgroup_opacity(hud_p1, 1.0)
        set_vgroup_opacity(hud_p2, 0.0)
        set_vgroup_opacity(hud_p3, 0.0)
        self.add(hud_p1, hud_p2, hud_p3)

        # Row 5: Dynamic Telemetry Metrics
        metrics_container = VGroup().move_to([0.0, 3.45, 0.0])
        initial_metrics = Text(
            "θ: 180.0°   |   a_base: +000 m/s²   |   Margen R: 9.74",
            font="Consolas",
            font_size=12,
            color="#94A3B8",
        ).move_to([0.0, 3.45, 0.0])
        metrics_container.add(initial_metrics)
        self.add(metrics_container)

        # -------------------------------------------------------------
        # 5. Mechanical Physical System (Central Zone: y in [-1.5, 3.1])
        # -------------------------------------------------------------
        rail_y_center = 0.85
        rail_height = 2.4
        rail_bg = RoundedRectangle(
            width=0.22,
            height=rail_height,
            corner_radius=0.08,
            fill_color="#1E293B",
            fill_opacity=0.9,
            stroke_color="#475569",
            stroke_width=1.5,
        ).move_to([0.0, rail_y_center, 0.0])

        rail_ticks = VGroup()
        for y_tick in np.linspace(rail_y_center - 1.0, rail_y_center + 1.0, 11):
            rail_ticks.add(
                Line(
                    start=[-0.18, y_tick, 0],
                    end=[0.18, y_tick, 0],
                    stroke_color="#64748B",
                    stroke_width=1.0,
                )
            )
        rail_assembly = VGroup(rail_bg, rail_ticks)
        self.add(rail_assembly)

        # Carriage assembly
        carriage_box = RoundedRectangle(
            width=1.1,
            height=0.42,
            corner_radius=0.08,
            fill_color="#334155",
            fill_opacity=1.0,
            stroke_color="#00F2FE",
            stroke_width=2.0,
        )
        bearing_pin = Circle(
            radius=0.10,
            fill_color="#F59E0B",
            fill_opacity=1.0,
            stroke_color="#FFFFFF",
            stroke_width=1.5,
        )
        carriage_assembly = VGroup(carriage_box, bearing_pin)

        vib_arrow_l = Text("↕", font="Arial", font_size=18, color="#00F2FE").next_to(carriage_box, LEFT, buff=0.1)
        vib_arrow_r = Text("↕", font="Arial", font_size=18, color="#00F2FE").next_to(carriage_box, RIGHT, buff=0.1)
        vib_indicators = VGroup(vib_arrow_l, vib_arrow_r)

        # Rod and Bob
        L_vis = 2.00
        rod_line = Line(start=[0, 0, 0], end=[0, L_vis, 0], stroke_color="#CBD5E1", stroke_width=5.0)
        rod_shine = Line(start=[0, 0, 0], end=[0, L_vis, 0], stroke_color="#FFFFFF", stroke_width=1.5)

        bob_glow = Circle(radius=0.34, fill_color="#00F2FE", fill_opacity=0.30, stroke_width=0)
        bob_body = Circle(radius=0.22, fill_color="#0284C7", fill_opacity=1.0, stroke_color="#38BDF8", stroke_width=2.5)
        bob_core = Circle(radius=0.08, fill_color="#FFFFFF", fill_opacity=1.0, stroke_width=0)
        bob_assembly = VGroup(bob_glow, bob_body, bob_core)

        ref_vertical = DashedLine(
            start=[0, rail_y_center, 0],
            end=[0, rail_y_center + L_vis + 0.25, 0],
            stroke_color="#475569",
            stroke_width=1.2,
            dash_length=0.08,
        )
        self.add(ref_vertical, carriage_assembly, vib_indicators, rod_line, rod_shine, bob_assembly)

        # External perturbation arrow (Phase 2)
        pert_arrow = Arrow(
            start=[2.2, 2.85, 0],
            end=[0.4, 2.85, 0],
            color="#FF0055",
            stroke_width=6,
            buff=0,
            max_tip_length_to_length_ratio=0.3,
        )
        pert_label = Text(
            "PERTURBACIÓN LATERAL (Δθ = 35°)",
            font="Consolas",
            font_size=13,
            weight=BOLD,
            color="#FF0055",
        ).next_to(pert_arrow, UP, buff=0.12)
        pert_group = VGroup(pert_arrow, pert_label)
        set_vgroup_opacity(pert_group, 0.0)
        self.add(pert_group)

        # Emergency Shutdown Warning Banner (Phase 3)
        shutdown_banner = RoundedRectangle(
            width=7.8,
            height=0.55,
            corner_radius=0.1,
            fill_color="#7F1D1D",
            fill_opacity=0.9,
            stroke_color="#EF4444",
            stroke_width=2.0,
        ).move_to([0.0, 1.95, 0.0])
        shutdown_text = Text(
            "⚠️ PARADA DE EMERGENCIA: MOTOR OFF (f = 0 Hz)",
            font="Consolas",
            font_size=13,
            weight=BOLD,
            color="#FEE2E2",
        ).move_to([0.0, 1.95, 0.0])
        shutdown_group = VGroup(shutdown_banner, shutdown_text)
        set_vgroup_opacity(shutdown_group, 0.0)
        self.add(shutdown_group)

        # -------------------------------------------------------------
        # 6. Lower Auxiliary Zone: Effective Potential Landscape
        #    Safe Zone: y in [-5.15, -1.80]
        # -------------------------------------------------------------
        chart_y_center = -3.45
        chart_bg = RoundedRectangle(
            width=8.2,
            height=3.30,
            corner_radius=0.18,
            fill_color="#0B132B",
            fill_opacity=0.92,
            stroke_color="#334155",
            stroke_width=1.5,
        ).move_to([0.0, chart_y_center, 0.0])

        chart_title = Text(
            "POZO DE ENERGÍA EFECTIVA DE LANDAU-KAPITZA",
            font="Consolas",
            font_size=14,
            weight=BOLD,
            color="#F59E0B",
        ).move_to([0.0, chart_y_center + 1.35, 0.0])

        chart_formula = Text(
            "V_eff(Θ) = m·g·L·(1 - cos Θ) + ¼·m·a²·ω²·sin² Θ",
            font="Consolas",
            font_size=11,
            color="#94A3B8",
        ).move_to([0.0, chart_y_center + 1.05, 0.0])

        self.add(chart_bg, chart_title, chart_formula)

        # Potential graph mapping
        x_min, x_max = -3.3, 3.3
        y_min, y_max = -4.6, -2.8
        v_scale_max = 32.0

        def theta_to_x(th: float) -> float:
            norm_th = float(th) % (2.0 * np.pi)
            if norm_th < 1e-4 and th > 1.0:
                norm_th = 2.0 * np.pi
            return x_min + (x_max - x_min) * (norm_th / (2.0 * np.pi))

        def v_to_y(v_val: float) -> float:
            norm_v = np.clip(v_val / v_scale_max, 0.0, 1.0)
            return y_min + (y_max - y_min) * norm_v

        # Chart axes
        axis_x = Line(start=[x_min, y_min, 0], end=[x_max, y_min, 0], stroke_color="#475569", stroke_width=1.5)
        axis_y = Line(start=[x_min, y_min, 0], end=[x_min, y_max, 0], stroke_color="#475569", stroke_width=1.5)
        mark_pi_line = DashedLine(
            start=[0.0, y_min, 0],
            end=[0.0, y_max, 0],
            stroke_color="#00F2FE",
            stroke_width=1.2,
            dash_length=0.06,
        )

        lbl_0 = Text("0° (Abajo)", font="Consolas", font_size=10, color="#64748B").next_to([x_min, y_min, 0], DOWN, buff=0.1)
        lbl_pi = Text("180° (Invertido)", font="Consolas", font_size=10, color="#00F2FE", weight=BOLD).next_to([0.0, y_min, 0], DOWN, buff=0.1)
        lbl_2pi = Text("360° (Abajo)", font="Consolas", font_size=10, color="#64748B").next_to([x_max, y_min, 0], DOWN, buff=0.1)

        chart_axes_group = VGroup(axis_x, axis_y, mark_pi_line, lbl_0, lbl_pi, lbl_2pi)
        self.add(chart_axes_group)

        # Dynamic Potential Curve & Fill
        theta_grid = np.linspace(0.0, 2.0 * np.pi, 80)
        potential_curve = VMobject(color="#00F2FE", stroke_width=3.0)
        potential_fill = VMobject(fill_color="#00F2FE", fill_opacity=0.12, stroke_width=0)
        self.add(potential_fill, potential_curve)

        # Rolling Bead on Potential Landscape
        bead_halo = Circle(radius=0.16, fill_color="#F59E0B", fill_opacity=0.35, stroke_width=0)
        bead_body = Circle(radius=0.09, fill_color="#FFFFFF", fill_opacity=1.0, stroke_color="#F59E0B", stroke_width=2.0)
        bead_tag = Text("Θ(t)", font="Consolas", font_size=10, color="#FDE047", weight=BOLD)
        bead_assembly = VGroup(bead_halo, bead_body, bead_tag)
        self.add(bead_assembly)

        # -------------------------------------------------------------
        # 7. Synchronous Dynamic Updaters (60 FPS Vector Graphics)
        # -------------------------------------------------------------
        state = {
            "current_phase": 1,
            "last_metrics_frame": -10,
        }

        def update_scene(dt):
            t = time_tracker.get_value()
            idx = get_frame_idx(t)

            th = sol.theta[idx]
            th_slow = sol.theta_slow[idx]
            th_deg = sol.theta_deg[idx]
            y0_val = sol.y_base[idx]
            a_base_val = sol.a_base[idx]
            w_inst = sol.omega_inst[idx]
            f_inst = sol.f_inst[idx]
            phase = sol.phase_id[idx]

            # 1. Pivot carriage position (scaled by 4.0x for high visual impact)
            y_pivot = rail_y_center + 4.0 * y0_val
            carriage_assembly.move_to([0.0, y_pivot, 0.0])

            # Stroboscopic vibration indicator
            if f_inst > 5.0:
                vib_indicators.set_opacity(0.85)
                vib_indicators[0].next_to(carriage_box, LEFT, buff=0.12)
                vib_indicators[1].next_to(carriage_box, RIGHT, buff=0.12)
                carriage_box.set_stroke(color="#00F2FE", width=2.0)
            else:
                vib_indicators.set_opacity(0.0)
                carriage_box.set_stroke(color="#EF4444", width=1.5)

            # 2. Pendulum Rod & Bob (60 FPS exact physical integration)
            bob_x = L_vis * np.sin(th)
            bob_y = y_pivot - L_vis * np.cos(th)

            rod_line.put_start_and_end_on([0.0, y_pivot, 0.0], [bob_x, bob_y, 0.0])
            rod_shine.put_start_and_end_on([0.0, y_pivot, 0.0], [bob_x, bob_y, 0.0])
            bob_assembly.move_to([bob_x, bob_y, 0.0])
            ref_vertical.put_start_and_end_on([0.0, y_pivot, 0.0], [0.0, y_pivot + L_vis + 0.25, 0.0])

            # 3. Phase-driven HUD and warning state transitions
            if phase != state["current_phase"]:
                state["current_phase"] = phase
                if phase == 1:
                    set_vgroup_opacity(hud_p1, 1.0)
                    set_vgroup_opacity(hud_p2, 0.0)
                    set_vgroup_opacity(hud_p3, 0.0)
                    hud_status_bar.set_fill(color="#00F2FE")
                    set_vgroup_opacity(shutdown_group, 0.0)
                elif phase == 2:
                    set_vgroup_opacity(hud_p1, 0.0)
                    set_vgroup_opacity(hud_p2, 1.0)
                    set_vgroup_opacity(hud_p3, 0.0)
                    hud_status_bar.set_fill(color="#FF0055")
                    set_vgroup_opacity(shutdown_group, 0.0)
                else:  # Phase 3
                    set_vgroup_opacity(hud_p1, 0.0)
                    set_vgroup_opacity(hud_p2, 0.0)
                    set_vgroup_opacity(hud_p3, 1.0)
                    hud_status_bar.set_fill(color="#EF4444")
                    set_vgroup_opacity(shutdown_group, 1.0)

            # Lateral perturbation arrow in Phase 2
            if phase == 2 and 4.0 <= t <= 4.75:
                pulse_op = float(np.clip(np.sin(np.pi * (t - 4.0) / 0.75), 0.0, 1.0))
                set_vgroup_opacity(pert_group, pulse_op)
                pert_arrow.put_start_and_end_on([bob_x + 1.8, bob_y, 0], [bob_x + 0.35, bob_y, 0])
                pert_label.next_to(pert_arrow, UP, buff=0.1)
            else:
                set_vgroup_opacity(pert_group, 0.0)

            # Update numeric readout at 10 Hz rate (every 6 frames)
            if idx - state["last_metrics_frame"] >= 6 or state["last_metrics_frame"] < 0:
                state["last_metrics_frame"] = idx
                r_ratio = ((phys_cfg.a * w_inst) ** 2) / (2.0 * phys_cfg.g * phys_cfg.L)
                metrics_str = f"θ: {th_deg%360.0:5.1f}°   |   a_base: {a_base_val:+05.0f} m/s²   |   Margen R: {r_ratio:4.2f}"
                new_m = Text(metrics_str, font="Consolas", font_size=12, color="#94A3B8").move_to([0.0, 3.45, 0.0])
                metrics_container.submobjects = [new_m]

            # 4. Update Lower Auxiliary Potential Landscape (Vector morphing)
            v_vals = compute_effective_potential(theta_grid, w_inst, phys_cfg)
            points = [
                [x_min + (x_max - x_min) * (tg / (2.0 * np.pi)), v_to_y(vg), 0.0]
                for tg, vg in zip(theta_grid, v_vals)
            ]
            potential_curve.set_points_smoothly(points)
            if phase == 3:
                potential_curve.set_color("#F59E0B")
            else:
                potential_curve.set_color("#00F2FE")

            fill_pts = points + [[x_max, y_min, 0.0], [x_min, y_min, 0.0]]
            potential_fill.set_points_as_corners(fill_pts)

            # 5. Update Rolling Bead on Potential Landscape
            v_bead = compute_effective_potential(np.array([th_slow]), w_inst, phys_cfg)[0]
            bx = theta_to_x(th_slow)
            by = v_to_y(v_bead)
            bead_halo.move_to([bx, by, 0.0])
            bead_body.move_to([bx, by, 0.0])
            bead_tag.next_to(bead_body, UP, buff=0.08)

        # Updaters
        self.add_updater(update_scene)
        update_scene(0.0)

        # Execution mode: snapshot vs full video render
        if getattr(self, "is_snapshot", False):
            self.wait(0.02)
        else:
            self.play(
                time_tracker.animate.set_value(phys_cfg.t_total),
                run_time=phys_cfg.t_total,
                rate_func=linear,
            )


class KapitzaPhase1Snapshot(KapitzaPendulumScene):
    """Renders a snapshot of Phase 1: High frequency stable upright inversion (t=2.0s)."""
    is_snapshot = True
    initial_time = 2.0


class KapitzaPhase2Snapshot(KapitzaPendulumScene):
    """Renders a snapshot of Phase 2: Lateral perturbation of 35 deg with external force arrow (t=4.25s)."""
    is_snapshot = True
    initial_time = 4.25


class KapitzaPhase3Snapshot(KapitzaPendulumScene):
    """Renders a snapshot of Phase 3: Vibration shutdown, collapsed potential, and violent plunge (t=9.2s)."""
    is_snapshot = True
    initial_time = 9.2


if __name__ == "__main__":
    import subprocess
    cmd = [
        "manim",
        "-pqh",
        str(Path(__file__).resolve()),
        "KapitzaPendulumScene",
    ]
    subprocess.run(cmd)
