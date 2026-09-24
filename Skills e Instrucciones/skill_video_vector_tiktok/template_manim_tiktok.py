"""
Continuum Lab — Vectorized Mathematical TikTok Animation Template
Generates pure vector 9:16 vertical animations (1080x1920 @ 60 FPS) using Manim.
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
    Renders an exact vector streamline flow past a cylinder with floating LaTeX HUD.
    Zero text overlap, strict safe zones.
    """

    def construct(self):
        # 1. Top HUD Header (Safe from TikTok search bar: y in [5.5, 6.8])
        hud_box = RoundedRectangle(
            corner_radius=0.15,
            width=7.8,
            height=2.2,
            color="#00f0ff",
            stroke_width=2,
            fill_color="#0d1117",
            fill_opacity=0.95
        ).move_to(UP * 5.6)

        title = Text("CONTINUUM LAB // VECTOR FIELD", font="Segoe UI", font_size=28, color=WHITE).move_to(hud_box.get_top() + DOWN * 0.35)
        subtitle = Text("2D INCOMPRESSIBLE FLOW PAST CYLINDER", font="Segoe UI", font_size=18, color="#8b949e").next_to(title, DOWN, buff=0.15)
        rule = Line(LEFT * 3.4, RIGHT * 3.4, color="#1f2937", stroke_width=1.5).next_to(subtitle, DOWN, buff=0.15)

        eq_text = MathTex(r"\nabla \cdot \mathbf{u} = 0 \quad \text{and} \quad Re = \frac{U_\infty D}{\nu} = 150", font_size=24, color="#00f0ff").next_to(rule, DOWN, buff=0.2)

        hud_group = VGroup(hud_box, title, subtitle, rule, eq_text)

        # 2. Solid Cylinder Obstacle at origin
        cylinder = Circle(radius=0.9, color="#00f0ff", stroke_width=4, fill_color="#12161f", fill_opacity=1.0).move_to(ORIGIN)

        # 3. Vector Field Function (Ideal Flow Past Cylinder with Circulation)
        # Potential flow: u_r = U_inf*(1 - a^2/r^2)*cos(theta), u_theta = -U_inf*(1 + a^2/r^2)*sin(theta)
        def flow_vector(pos):
            x, y = pos[0], pos[1]
            r_sq = x**2 + y**2
            a_sq = 0.9**2
            if r_sq < a_sq:
                return np.array([0.0, 0.0, 0.0])
            u_inf = 1.8
            # Cartesian potential flow velocity
            vx = u_inf * (1.0 - a_sq * (x**2 - y**2) / (r_sq**2))
            vy = u_inf * (-2.0 * a_sq * x * y / (r_sq**2))
            return np.array([vx, vy, 0.0])

        # 4. Pure Vector StreamLines
        streamlines = StreamLines(
            flow_vector,
            x_range=[-4.2, 4.2, 0.3],
            y_range=[-3.8, 3.8, 0.3],
            stroke_width=2.5,
            color=["#00f0ff", "#ffaa00", "#ff007f"],
            max_anchors_per_line=30
        )

        # 5. Bottom Telemetry Card (Safe from caption/music: y in [-4.5, -6.2])
        bottom_box = RoundedRectangle(
            corner_radius=0.15,
            width=7.8,
            height=1.8,
            color="#ff007f",
            stroke_width=1.5,
            fill_color="#0d1117",
            fill_opacity=0.95
        ).move_to(DOWN * 5.6)

        telem_title = Text("HYDRODYNAMIC FORCE METRICS", font="Segoe UI", font_size=20, color=WHITE).move_to(bottom_box.get_top() + DOWN * 0.3)
        telem_content = MathTex(r"C_D = 1.34 \pm 0.08 \quad \big| \quad St = 0.183 \quad \big| \quad Ma < 0.15", font_size=24, color="#39ff14").next_to(telem_title, DOWN, buff=0.25)
        bottom_group = VGroup(bottom_box, telem_title, telem_content)

        # 6. Animation Sequence
        self.play(FadeIn(hud_group), FadeIn(bottom_group), run_time=1.0)
        self.play(DrawBorderThenFill(cylinder), run_time=1.0)
        self.add(streamlines)
        streamlines.start_animation(warm_up=True, flow_speed=1.5)
        self.wait(4.0)
