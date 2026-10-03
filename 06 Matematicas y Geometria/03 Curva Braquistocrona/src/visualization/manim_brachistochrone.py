"""
Continuum Lab — Classical Mechanics & Calculus of Variations
TikTok 9:16 Vertical Vector Animation: La Paradoja de la Braquistócrona (Johann Bernoulli 1696)
Format: 1080x1920 @ 60 FPS, Duration: 12.0 seconds (720 frames)

Strict Safe Zones:
  - Top Safe Zone: > 160 px  (Y < 6.67)
  - Bottom Safe Zone: > 320 px (Y > -5.33)
  - Zero overlapping text, Consolas digital HUD, neon particle glow
"""

from manim import *
import numpy as np
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.physics.brachistochrone_models import BrachistochroneSimulator

# ----------------------------------------------------
# Exact 9:16 Vertical Canvas Configuration
# ----------------------------------------------------
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#0B0F19"  # Deep Space Cybernetic Navy


class BrachistochroneRaceAnimation(Animation):
    """
    Deterministic vector animation interpolator for the 4-track race.
    Guarantees exact physical positions, individual floating chronometers,
    and real-time HUD telemetry every single frame.
    """

    def __init__(
        self,
        scene,
        sim: BrachistochroneSimulator,
        spheres: dict,
        sphere_labels: dict,
        hud_cards: dict,
        spark_dots: VGroup,
        go_badge: Mobject,
        to_screen_func,
        run_time: float = 3.7,
        **kwargs,
    ):
        self.go_badge = go_badge
        combined = VGroup(
            *spheres.values(),
            *sphere_labels.values(),
            *[c["group"] for c in hud_cards.values()],
            spark_dots,
            go_badge,
        )
        super().__init__(combined, run_time=run_time, rate_func=linear, **kwargs)
        self.scene = scene
        self.sim = sim
        self.spheres = spheres
        self.sphere_labels = sphere_labels
        self.hud_cards = hud_cards
        self.spark_dots = spark_dots
        self.to_screen = to_screen_func
        self.last_tick = {k: -1 for k in spheres}

        # Offset vectors for floating sphere labels to guarantee zero collision
        self.label_offsets = {
            "rect": np.array([0.36, 0.22, 0.0]),
            "parab": np.array([0.36, 0.08, 0.0]),
            "braq": np.array([0.36, -0.14, 0.0]),
            "circ": np.array([-0.38, -0.16, 0.0]),
        }

    def interpolate_mobject(self, alpha: float):
        # Smoothly fade out "LIBERACION SIMULTANEA" badge early in race
        if alpha > 0.15:
            fade_alpha = max(0.0, 1.0 - (alpha - 0.15) * 5.0)
            self.go_badge.set_opacity(fade_alpha)

        # Physical time runs from 0.0 to 1.62 s
        t_sim = alpha * 1.62
        tick_id = int(t_sim * 25)  # 25 Hz digital clock refresh

        for k, track in self.sim.tracks.items():
            st = track.get_state(t_sim, use_target_time=True)
            screen_pos = self.to_screen(st.x, st.y)
            self.spheres[k].move_to(screen_pos)

            card = self.hud_cards[k]

            # Update digital clock and speedometer
            if tick_id != self.last_tick[k] or st.finished:
                self.last_tick[k] = tick_id

                timer_color = "#00FF66" if st.finished else WHITE
                card["timer"].become(
                    Text(
                        f"{st.t_elapsed:.3f} s",
                        font="Consolas",
                        font_size=13.5,
                        color=timer_color,
                        weight=BOLD,
                    ).move_to(card["bg"].get_center() + np.array([0.0, -0.04, 0.0]))
                )

                speed_color = "#38BDF8" if not st.finished else "#64748B"
                card["speed"].become(
                    Text(
                        f"v: {st.speed:.1f} m/s",
                        font="Consolas",
                        font_size=10,
                        color=speed_color,
                    ).move_to(card["bg"].get_bottom() + np.array([0.0, 0.16, 0.0]))
                )

                # Floating mini-timer over each sphere
                lbl_pos = screen_pos + self.label_offsets[k]
                if st.finished:
                    rank_str = "1º" if k == "braq" else ("2º" if k == "circ" else ("3º" if k == "parab" else "4º"))
                    lbl_text = f"{rank_str} {st.t_elapsed:.2f}s"
                    lbl_col = "#00FF66" if k == "braq" else card["color"]
                else:
                    lbl_text = f"{st.t_elapsed:.2f}s"
                    lbl_col = card["color"]

                self.sphere_labels[k].become(
                    Text(
                        lbl_text,
                        font="Consolas",
                        font_size=9.5,
                        color=lbl_col,
                        weight=BOLD,
                    ).move_to(lbl_pos)
                )

                if k == "braq" and st.finished:
                    card["bg"].set_stroke(color="#00FF66", width=2.5)

        # Luminous particle trail for cycloid
        st_braq = self.sim.tracks["braq"].get_state(t_sim, use_target_time=True)
        if not st_braq.finished and t_sim > 0.05:
            pos = self.to_screen(st_braq.x, st_braq.y)
            spark = Dot(
                point=pos + np.array([np.random.uniform(-0.05, 0.05), np.random.uniform(-0.05, 0.05), 0.0]),
                radius=np.random.uniform(0.03, 0.055),
                color="#00F0FF",
            )
            spark.set_opacity(0.85)
            self.spark_dots.add(spark)
            if len(self.spark_dots) > 30:
                self.spark_dots.remove(self.spark_dots[0])
        elif st_braq.finished and len(self.spark_dots) > 0:
            self.spark_dots.remove(self.spark_dots[0])


class TikTokBrachistochrone(Scene):
    """
    Ultra-high definition vectorized Manim animation of the Brachistochrone race.
    Resolves Bernoulli's 1696 paradox comparing Cycloid, Circle, Parabola, and Straight line.
    """

    def construct(self):
        # ----------------------------------------------------
        # 1. Physics Engine Setup & Spatial Transformations
        # ----------------------------------------------------
        sim = BrachistochroneSimulator(g=9.81)

        scale = 0.84
        x_mid_phys = 3.5
        y_mid_phys = 0.5
        y_screen_offset = 0.2

        def to_screen(x_phys: float, y_phys: float) -> np.ndarray:
            """Maps physical coordinates [0, 7] x [-3, 4] to 9:16 screen space."""
            sx = (x_phys - x_mid_phys) * scale
            sy = y_screen_offset + (y_phys - y_mid_phys) * scale
            return np.array([sx, sy, 0.0])

        # Track Visual Parameters
        track_styles = {
            "braq": {"name": "CICLOIDE", "color": "#00F0FF", "card_x": -3.05},
            "circ": {"name": "CÍRCULO", "color": "#7928CA", "card_x": -1.02},
            "parab": {"name": "PARÁBOLA", "color": "#FFE600", "card_x": 1.02},
            "rect": {"name": "RECTA", "color": "#FF0055", "card_x": 3.05},
        }

        # ----------------------------------------------------
        # 2. Header & Branding in Top Safe Zone (Y in [5.2, 6.4])
        # ----------------------------------------------------
        header_group = VGroup()

        tag = Text(
            "CONTINUUM LAB // CÁLCULO DE VARIACIONES",
            font="Consolas",
            font_size=15,
            color="#38BDF8",
            weight=BOLD,
        )
        tag.move_to(np.array([0.0, 6.25, 0.0]))

        title = Text(
            "LA BRAQUISTÓCRONA",
            font="Consolas",
            font_size=23,
            color=WHITE,
            weight=BOLD,
        )
        title.next_to(tag, DOWN, buff=0.12)

        subtitle = Text(
            "EL CAMINO MÁS CORTO NO ES EL MÁS RÁPIDO",
            font="Consolas",
            font_size=13,
            color="#94A3B8",
            weight=SEMIBOLD,
        )
        subtitle.next_to(title, DOWN, buff=0.10)

        header_line = Line(
            start=np.array([-4.0, 5.25, 0.0]),
            end=np.array([4.0, 5.25, 0.0]),
            color="#1E293B",
            stroke_width=1.5,
        )

        header_group.add(tag, title, subtitle, header_line)

        # ----------------------------------------------------
        # 3. Floating Telemetry HUD Cards (Y in [3.9, 5.0])
        # ----------------------------------------------------
        hud_cards = {}
        hud_group = VGroup()

        for key, style in track_styles.items():
            cx = style["card_x"]
            card_bg = RoundedRectangle(
                corner_radius=0.12,
                width=1.88,
                height=1.05,
                fill_color="#0F172A",
                fill_opacity=0.90,
                stroke_color="#334155",
                stroke_width=1.5,
            )
            card_bg.move_to(np.array([cx, 4.55, 0.0]))

            dot = Dot(radius=0.06, color=style["color"])
            dot.move_to(card_bg.get_corner(UL) + np.array([0.22, -0.22, 0.0]))

            name_lbl = Text(
                style["name"],
                font="Consolas",
                font_size=11,
                color=style["color"],
                weight=BOLD,
            )
            name_lbl.next_to(dot, RIGHT, buff=0.08)

            timer_lbl = Text(
                "0.000 s",
                font="Consolas",
                font_size=13.5,
                color=WHITE,
                weight=BOLD,
            )
            timer_lbl.move_to(card_bg.get_center() + np.array([0.0, -0.04, 0.0]))

            speed_lbl = Text(
                "0.0 m/s",
                font="Consolas",
                font_size=10,
                color="#94A3B8",
            )
            speed_lbl.move_to(card_bg.get_bottom() + np.array([0.0, 0.16, 0.0]))

            card_vgroup = VGroup(card_bg, dot, name_lbl, timer_lbl, speed_lbl)
            hud_cards[key] = {
                "group": card_vgroup,
                "bg": card_bg,
                "timer": timer_lbl,
                "speed": speed_lbl,
                "name": name_lbl,
                "color": style["color"],
            }
            hud_group.add(card_vgroup)

        # ----------------------------------------------------
        # 4. Neon Track Curves Construction
        # ----------------------------------------------------
        track_mobjects = {}
        track_group = VGroup()

        for key, track in sim.tracks.items():
            pts_phys = track.get_trajectory_points(num_points=350)
            pts_screen = [to_screen(p[0], p[1]) for p in pts_phys]

            # Glowing base stroke
            glow_path = VMobject()
            glow_path.set_points_smoothly(pts_screen)
            glow_path.set_stroke(color=track.color, width=7.0, opacity=0.25)

            # Core sharp neon stroke
            core_path = VMobject()
            core_path.set_points_smoothly(pts_screen)
            core_path.set_stroke(color=track.color, width=3.8, opacity=0.95)

            track_combo = VGroup(glow_path, core_path)
            track_mobjects[key] = track_combo
            track_group.add(track_combo)

        # ----------------------------------------------------
        # 5. Start Line A and Finish Line B Markers
        # ----------------------------------------------------
        start_pt = to_screen(0.0, 4.0)
        end_pt = to_screen(7.0, -3.0)

        # Start Gate
        start_ring = Circle(radius=0.22, color="#38BDF8", stroke_width=2.5)
        start_ring.move_to(start_pt)
        start_core = Dot(radius=0.08, color=WHITE).move_to(start_pt)
        start_lbl = Text("A (0, 4.0)\nINICIO", font="Consolas", font_size=10, color="#38BDF8", line_spacing=0.9)
        start_lbl.next_to(start_ring, UL, buff=0.12)
        start_group = VGroup(start_ring, start_core, start_lbl)

        # Finish Gate — placed strictly with label UP-RIGHT to avoid overlapping callout card below!
        end_ring = Circle(radius=0.26, color="#00FF66", stroke_width=3.0)
        end_ring.move_to(end_pt)
        end_core = Dot(radius=0.09, color=WHITE).move_to(end_pt)
        end_lbl = Text("B (7, -3.0)\nMETA", font="Consolas", font_size=10.5, color="#00FF66", weight=BOLD, line_spacing=0.9)
        end_lbl.next_to(end_ring, UP + RIGHT, buff=0.10)

        finish_line_seg = DashedLine(
            start=end_pt + np.array([-0.5, 0.4, 0.0]),
            end=end_pt + np.array([0.5, -0.4, 0.0]),
            color="#00FF66",
            stroke_width=2.0,
            dash_length=0.1,
        )
        end_group = VGroup(end_ring, end_core, end_lbl, finish_line_seg)

        # ----------------------------------------------------
        # 6. High-Tech Metallic Spheres & Floating Mini-Timers
        # ----------------------------------------------------
        spheres = {}
        sphere_labels = {}
        sphere_group = VGroup()

        for key, style in track_styles.items():
            s_glow = Circle(radius=0.18, color=style["color"], stroke_width=2.5, fill_opacity=0.0)
            s_base = Circle(radius=0.13, color=style["color"], stroke_width=2.0, fill_color="#CBD5E1", fill_opacity=0.95)
            s_spec = Dot(radius=0.04, color=WHITE).shift(np.array([-0.04, 0.04, 0.0]))
            
            ball = VGroup(s_glow, s_base, s_spec)
            ball.move_to(start_pt)
            spheres[key] = ball
            sphere_group.add(ball)

            lbl = Text("0.00s", font="Consolas", font_size=9.5, color=style["color"], weight=BOLD)
            lbl.move_to(start_pt + np.array([0.30, 0.15, 0.0]))
            sphere_labels[key] = lbl
            sphere_group.add(lbl)

        # Countdown Banner
        countdown_txt = Text(
            "LISTOS...",
            font="Consolas",
            font_size=18,
            color="#FCD34D",
            weight=BOLD,
        )
        countdown_txt.move_to(np.array([0.0, 3.45, 0.0]))

        # ----------------------------------------------------
        # 7. Post-Race Paradox Resolution Card (Bottom Safe Zone: Y in [-5.3, -3.3])
        # ----------------------------------------------------
        callout_group = VGroup()
        callout_bg = RoundedRectangle(
            corner_radius=0.16,
            width=8.4,
            height=2.05,
            fill_color="#0F172A",
            fill_opacity=0.95,
            stroke_color="#00F0FF",
            stroke_width=2.0,
        )
        callout_bg.move_to(np.array([0.0, -4.30, 0.0]))

        c_title = Text(
            "PARADOJA RESUELTA // JOHANN BERNOULLI (1696)",
            font="Consolas",
            font_size=12.5,
            color="#00F0FF",
            weight=BOLD,
        )
        c_title.move_to(callout_bg.get_top() + np.array([0.0, -0.26, 0.0]))

        c_exp1 = Text(
            "LA CICLOIDE GASTA ENERGÍA AL PRINCIPIO PARA ACUMULAR",
            font="Consolas",
            font_size=10.5,
            color=WHITE,
            weight=BOLD,
        )
        c_exp1.next_to(c_title, DOWN, buff=0.10)

        c_exp2 = Text(
            "VELOCIDAD CINÉTICA MÁXIMA Y LLEGAR PRIMERA A LA META.",
            font="Consolas",
            font_size=10.5,
            color="#FCD34D",
            weight=BOLD,
        )
        c_exp2.next_to(c_exp1, DOWN, buff=0.06)

        # Scoreboard summary line
        c_table = Text(
            "1º CICLOIDE: 1.32s | 2º CÍRCULO: 1.39s | 3º PARÁBOLA: 1.45s | 4º RECTA: 1.62s",
            font="Consolas",
            font_size=9.5,
            color="#94A3B8",
        )
        c_table.next_to(c_exp2, DOWN, buff=0.12)

        c_sub = Text(
            "La distancia más corta (Recta) resulta ser la más lenta.",
            font="Consolas",
            font_size=10,
            color="#FF0055",
            weight=BOLD,
        )
        c_sub.next_to(c_table, DOWN, buff=0.06)

        callout_group.add(callout_bg, c_title, c_exp1, c_exp2, c_table, c_sub)

        # ----------------------------------------------------
        # 8. ANIMATION SEQUENCE (12.0 Seconds Total)
        # ----------------------------------------------------
        # [0.0 - 1.8s] Intro: Header, Tracks, and Gates draw simultaneously
        self.play(
            FadeIn(header_group, shift=DOWN * 0.3),
            FadeIn(hud_group, shift=DOWN * 0.2),
            run_time=0.8,
        )

        self.play(
            LaggedStart(
                *[Create(track_mobjects[k]) for k in ["rect", "parab", "circ", "braq"]],
                lag_ratio=0.12,
            ),
            FadeIn(start_group),
            FadeIn(end_group),
            run_time=1.0,
        )

        # [1.8 - 2.5s] Countdown & Placement
        self.add(sphere_group)
        self.play(
            FadeIn(countdown_txt, scale=1.2),
            run_time=0.3,
        )

        self.wait(0.4)
        self.remove(countdown_txt)

        go_badge = Text(
            "¡LIBERACIÓN SIMULTÁNEA!",
            font="Consolas",
            font_size=17,
            color="#00FF66",
            weight=BOLD,
        )
        go_badge.move_to(np.array([0.0, 3.45, 0.0]))
        self.add(go_badge)

        # ----------------------------------------------------
        # [2.5 - 6.2s] The Dynamic Vector Race via Custom Animation
        # ----------------------------------------------------
        spark_dots = VGroup()
        self.add(spark_dots)

        race_anim = BrachistochroneRaceAnimation(
            scene=self,
            sim=sim,
            spheres=spheres,
            sphere_labels=sphere_labels,
            hud_cards=hud_cards,
            spark_dots=spark_dots,
            go_badge=go_badge,
            to_screen_func=to_screen,
            run_time=3.7,
        )

        self.play(race_anim)
        self.remove(go_badge)

        # Ensure final arrival positions
        for k, track in sim.tracks.items():
            st = track.get_state(1.62, use_target_time=True)
            spheres[k].move_to(to_screen(st.x, st.y))

        # Green pulse shockwave on arrival + clean fadeout of mini labels
        arrival_pulse = Circle(radius=0.26, color="#00FF66", stroke_width=4.0).move_to(end_pt)
        self.play(
            arrival_pulse.animate.scale(2.2).set_stroke(opacity=0.0),
            FadeOut(VGroup(*sphere_labels.values())),
            run_time=0.6,
        )
        self.remove(arrival_pulse)

        # ----------------------------------------------------
        # [6.8 - 12.0s] Paradox Resolution & Scientific Conclusion
        # ----------------------------------------------------
        self.play(
            FadeIn(callout_group, shift=UP * 0.4),
            run_time=1.0,
        )

        # Hold final state until 12.0s
        self.wait(4.2)
