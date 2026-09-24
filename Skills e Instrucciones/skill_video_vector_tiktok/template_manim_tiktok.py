"""
Continuum Lab — Vectorized Mathematical TikTok Animation Engine
Video 1: von Kármán Vortex Shedding & Streamline Field
Duration: ~18 seconds (1080x1920 @ 60 FPS)
Strict Rules: Zero project titles, zero overlapping text, full safe zones.
"""

from manim import *
import numpy as np

# Exact TikTok 9:16 Canvas Configuration
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#0a0a0c"  # Cybernetic Deep Void


class TikTokVectorFluid(Scene):
    """
    Renders pure vector streamline flow past a cylinder undergoing von Kármán vortex shedding.
    Curious physical callouts, pulsating limit cycle, zero project titles.
    """

    def construct(self):
        # ----------------------------------------------------
        # 1. Top HUD Card (Pure Physics & Telemetry - No Project Titles)
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

        eq_continuity = MathTex(
            r"\nabla \cdot \mathbf{u} = 0 \quad \big| \quad \frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u}\cdot\nabla)\mathbf{u} = -\nabla p + \nu \nabla^2\mathbf{u}",
            font_size=21,
            color="#ffffff"
        ).move_to(top_box.get_top() + DOWN * 0.45)

        rule = Line(LEFT * 3.4, RIGHT * 3.4, color="#1f2937", stroke_width=1.0).next_to(eq_continuity, DOWN, buff=0.18)

        re_text = MathTex(
            r"Re = \frac{U_\infty D}{\nu} = 150 \quad \implies \quad \text{Bifurcaci\'on de Hopf Supercr\'itica}",
            font_size=20,
            color="#00f0ff"
        ).next_to(rule, DOWN, buff=0.18)

        top_group = VGroup(top_box, eq_continuity, rule, re_text)

        # ----------------------------------------------------
        # 2. Solid Cylinder Obstacle at (x = -1.2, y = 0.4)
        # Shifted slightly left to leave space for wake downstream
        # ----------------------------------------------------
        obs_center = np.array([-1.2, 0.4, 0.0])
        cylinder = Circle(
            radius=0.75,
            color="#00f0ff",
            stroke_width=3.5,
            fill_color="#12161f",
            fill_opacity=1.0
        ).move_to(obs_center)

        # ----------------------------------------------------
        # 3. Vector Streamlines Field with Periodic Shedding
        # ----------------------------------------------------
        # Time tracker for dynamic vortex shedding oscillation
        t_tracker = ValueTracker(0.0)

        def flow_vector(pos):
            x = pos[0] - obs_center[0]
            y = pos[1] - obs_center[1]
            r_sq = x**2 + y**2
            a_sq = 0.75**2

            if r_sq < a_sq:
                return np.array([0.0, 0.0, 0.0])

            u_inf = 1.6
            # Base potential flow velocity
            vx = u_inf * (1.0 - a_sq * (x**2 - y**2) / (r_sq**2))
            vy = u_inf * (-2.0 * a_sq * x * y / (r_sq**2))

            # Shedding vortex perturbations in the wake (x > 0.5)
            t = t_tracker.get_value()
            if x > 0.4:
                omega_shed = 2.4  # Shedding angular frequency
                wave_k = 1.8
                decay = np.exp(-((y)**2) / 1.8)
                # Alternating Karman vortex perturbation
                vort_pert_y = 0.9 * np.sin(wave_k * x - omega_shed * t) * decay
                vort_pert_x = 0.4 * np.cos(wave_k * x - omega_shed * t) * decay * (y / 1.0)
                vx += vort_pert_x
                vy += vort_pert_y

            return np.array([vx, vy, 0.0])

        streamlines = StreamLines(
            flow_vector,
            x_range=[-4.2, 4.2, 0.3],
            y_range=[-3.2, 4.0, 0.3],
            stroke_width=2.4,
            color=["#00f0ff", "#ffaa00", "#ff007f"],
            max_anchors_per_line=30
        )

        # ----------------------------------------------------
        # 4. Bottom Telemetry Card: Aerodynamic Forces & Phase Orbit
        # Safe from TikTok bottom overlay: y in [-4.6, -6.6]
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
            r"\text{TELEMETR\'IA DIN\'AMICA (MOMENTUM EXCHANGE)}",
            font_size=20,
            color="#ffffff"
        ).move_to(bottom_box.get_top() + DOWN * 0.38)

        rule_bottom = Line(LEFT * 3.4, RIGHT * 3.4, color="#1f2937", stroke_width=1.0).next_to(telem_header, DOWN, buff=0.15)

        metrics_text = MathTex(
            r"C_D = 1.34 \pm 0.08 \quad \big| \quad C_L(t) = \pm 0.62 \quad \big| \quad St = \frac{f_s D}{U_\infty} = 0.183",
            font_size=20,
            color="#39ff14"
        ).next_to(rule_bottom, DOWN, buff=0.20)

        freq_callout = MathTex(
            r"\text{Frecuencia de oscilaci\'on del arrastre: } f_{C_D} = 2\,f_{C_L} \implies \text{Ciclo L\'imite}",
            font_size=18,
            color="#ffaa00"
        ).next_to(metrics_text, DOWN, buff=0.16)

        bottom_group = VGroup(bottom_box, telem_header, rule_bottom, metrics_text, freq_callout)

        # ----------------------------------------------------
        # 5. Animation Sequence (Total Duration: 16.5 seconds)
        # ----------------------------------------------------
        self.play(FadeIn(top_group), FadeIn(bottom_group), run_time=1.2)
        self.play(DrawBorderThenFill(cylinder), run_time=1.0)

        # Start dynamic streamlines
        self.add(streamlines)
        streamlines.start_animation(warm_up=True, flow_speed=1.4)

        # Animate time tracker to trigger oscillating vortex wake for 14 seconds
        self.play(
            t_tracker.animate.set_value(14.0),
            run_time=14.0,
            rate_func=linear
        )
        self.wait(0.5)
