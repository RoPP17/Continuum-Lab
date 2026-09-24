"""
Continuum Lab — Classical Mechanics & Dynamical Systems
Vectorized Manim TikTok 9:16 Animation: Chaotic Triple Pendulum Trajectory
Duration: 20 seconds (1080x1920 @ 60 FPS)
Strict Rules: Zero project titles, zero overlapping text, full safe zones.
"""

from manim import *
import numpy as np
import sys
from pathlib import Path

# Add project root for imports
current_dir = Path(__file__).resolve().parent.parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from src.physics.triple_pendulum import TriplePendulumSimulator, TriplePendulumParams

# Exact TikTok 9:16 Canvas Configuration
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#0a0a0c"  # Cybernetic Deep Void


class TikTokTriplePendulum(Scene):
    """
    Renders pure vector chaotic triple pendulum with live glowing trajectory tracing.
    """

    def construct(self):
        # ----------------------------------------------------
        # 1. Physics Precomputation (RK4 High Precision)
        # ----------------------------------------------------
        # Rod lengths scaled for 9:16 screen viewing
        params = TriplePendulumParams(l1=1.1, l2=0.95, l3=0.8, m1=1.2, m2=1.0, m3=0.8)
        sim = TriplePendulumSimulator(params)

        # High energy chaotic release: [130 deg, 100 deg, 70 deg]
        init_angles = (np.radians(130.0), np.radians(100.0), np.radians(70.0))
        sim.set_initial_state(init_angles)

        fps = 60
        total_seconds = 18.0
        total_frames = int(fps * total_seconds)
        dt_frame = 1.0 / fps
        sub_steps = 10  # 10 internal RK4 steps per visual frame
        dt_sub = dt_frame / sub_steps

        pivot = np.array([0.0, 1.8, 0.0])  # Pivot shifted to upper-middle

        # Precompute trajectories
        p1_list = []
        p2_list = []
        p3_list = []
        energy_list = []

        for _ in range(total_frames):
            for _ in range(sub_steps):
                sim.step_rk4(dt_sub)
            pos1, pos2, pos3 = sim.get_cartesian_positions()
            p1_list.append(pivot + np.array([pos1[0], pos1[1], 0.0]))
            p2_list.append(pivot + np.array([pos2[0], pos2[1], 0.0]))
            p3_list.append(pivot + np.array([pos3[0], pos3[1], 0.0]))
            energy_list.append(sim.total_energy())

        p1_arr = np.array(p1_list)
        p2_arr = np.array(p2_list)
        p3_arr = np.array(p3_list)

        # ----------------------------------------------------
        # 2. Top HUD Card (Pure Physics - Strictly NO Project Titles)
        # Safe from TikTok search bar: y in [5.4, 6.8]
        # ----------------------------------------------------
        top_box = RoundedRectangle(
            corner_radius=0.15,
            width=7.8,
            height=1.8,
            color="#00f0ff",
            stroke_width=1.5,
            fill_color="#0d1117",
            fill_opacity=0.95
        ).move_to(UP * 5.8)

        eq_lagrange = MathTex(
            r"\mathcal{L} = T - V \quad \big| \quad \frac{d}{dt}\left(\frac{\partial \mathcal{L}}{\partial \dot{\theta}_k}\right) - \frac{\partial \mathcal{L}}{\partial \theta_k} = 0",
            font_size=21,
            color="#ffffff"
        ).move_to(top_box.get_top() + DOWN * 0.45)

        rule_top = Line(LEFT * 3.4, RIGHT * 3.4, color="#1f2937", stroke_width=1.0).next_to(eq_lagrange, DOWN, buff=0.18)

        caos_text = MathTex(
            r"\text{Sistemas Din\'amicos No Lineales } \implies \text{Caos Determinista } (\lambda > 0)",
            font_size=19,
            color="#00f0ff"
        ).next_to(rule_top, DOWN, buff=0.18)

        top_group = VGroup(top_box, eq_lagrange, rule_top, caos_text)

        # ----------------------------------------------------
        # 3. Bottom Telemetry Card (Hamiltonian Conservation)
        # Safe from TikTok caption/audio: y in [-4.6, -6.6]
        # ----------------------------------------------------
        bottom_box = RoundedRectangle(
            corner_radius=0.15,
            width=7.8,
            height=2.0,
            color="#ff007f",
            stroke_width=1.5,
            fill_color="#0d1117",
            fill_opacity=0.95
        ).move_to(DOWN * 5.6)

        telem_header = MathTex(
            r"\text{CONSERVACI\'ON DE ENERG\'IA HAMILTONIANA}",
            font_size=20,
            color="#ffffff"
        ).move_to(bottom_box.get_top() + DOWN * 0.38)

        rule_bottom = Line(LEFT * 3.4, RIGHT * 3.4, color="#1f2937", stroke_width=1.0).next_to(telem_header, DOWN, buff=0.15)

        energy_text = MathTex(
            r"E = T + V = \text{const} \quad \big| \quad \frac{\Delta E}{E_0} < 10^{-5} \quad \big| \quad 3 \text{ Grados de Libertad}",
            font_size=19,
            color="#39ff14"
        ).next_to(rule_bottom, DOWN, buff=0.20)

        chaos_desc = MathTex(
            r"\text{Trayectoria Fractal del Extremo } (x_3, y_3) \text{ en el Espacio Real}",
            font_size=18,
            color="#ffaa00"
        ).next_to(energy_text, DOWN, buff=0.16)

        bottom_group = VGroup(bottom_box, telem_header, rule_bottom, energy_text, chaos_desc)

        # ----------------------------------------------------
        # 4. Pendulum Visual Elements
        # ----------------------------------------------------
        pivot_dot = Dot(point=pivot, radius=0.10, color=WHITE)
        pivot_ring = Circle(radius=0.18, color="#00f0ff", stroke_width=2).move_to(pivot)

        # Dynamic Rods
        rod1 = Line(pivot, p1_arr[0], color="#00f0ff", stroke_width=4.0)
        rod2 = Line(p1_arr[0], p2_arr[0], color="#ffaa00", stroke_width=3.5)
        rod3 = Line(p2_arr[0], p3_arr[0], color="#ff007f", stroke_width=3.0)

        # Dynamic Bobs
        bob1 = Dot(p1_arr[0], radius=0.14, color="#00f0ff")
        bob2 = Dot(p2_arr[0], radius=0.13, color="#ffaa00")
        bob3 = Dot(p3_arr[0], radius=0.12, color="#ffffff")
        bob3_glow = Circle(radius=0.22, color="#ff007f", stroke_width=2.5).move_to(p3_arr[0])

        # Trajectory Trail of Bob 3 (Persistent luminous vector curve)
        trail = VMobject(stroke_width=2.2)
        trail.set_points_as_corners([p3_arr[0], p3_arr[0] + np.array([0.001, 0, 0])])
        trail.set_color_by_gradient("#00f0ff", "#39ff14", "#ffaa00", "#ff007f")

        # ----------------------------------------------------
        # 5. Updaters for 60 FPS Synchronization
        # ----------------------------------------------------
        frame_idx = ValueTracker(0)

        def update_pendulum(mob):
            idx = int(frame_idx.get_value())
            if idx >= total_frames:
                idx = total_frames - 1
            pos1 = p1_arr[idx]
            pos2 = p2_arr[idx]
            pos3 = p3_arr[idx]

            rod1.put_start_and_end_on(pivot, pos1)
            rod2.put_start_and_end_on(pos1, pos2)
            rod3.put_start_and_end_on(pos2, pos3)

            bob1.move_to(pos1)
            bob2.move_to(pos2)
            bob3.move_to(pos3)
            bob3_glow.move_to(pos3)

        def update_trail(mob):
            idx = int(frame_idx.get_value())
            if idx > 1:
                idx_end = min(idx + 1, total_frames)
                # Keep last 500 points for a magnificent trailing comet or all points
                mob.set_points_smoothly(p3_arr[:idx_end])
                mob.set_color_by_gradient("#00f0ff", "#39ff14", "#ffaa00", "#ff007f")

        # Initial Appearance
        self.play(FadeIn(top_group), FadeIn(bottom_group), run_time=1.0)
        self.play(
            FadeIn(pivot_dot), FadeIn(pivot_ring),
            Create(rod1), Create(rod2), Create(rod3),
            FadeIn(bob1), FadeIn(bob2), FadeIn(bob3), FadeIn(bob3_glow),
            run_time=1.0
        )

        # Attach updaters
        rod1.add_updater(update_pendulum)
        trail.add_updater(update_trail)
        self.add(trail)

        # Play Chaotic Swing for 18 seconds (total scene duration: 20 seconds)
        self.play(
            frame_idx.animate.set_value(total_frames - 1),
            run_time=total_seconds,
            rate_func=linear
        )
        self.wait(0.5)
