"""
Continuum Lab — Classical Mechanics & Calculus of Variations
TikTok 9:16 Vertical Vector Animation: La Paradoja de la Braquistócrona (Johann Bernoulli 1696)
Format: 1080x1920 @ 60 FPS, Duration: 14.5 seconds (870 frames)

Strict Safe Zones:
  - Top Safe Zone: > 160 px  (Y < 6.67)
  - Bottom Safe Zone: > 320 px (Y > -5.33)
  - Zero overlapping text, Consolas digital HUD, neon particle glow
  - Zero static freeze: Continuous kinematic, educational and visual action
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
    and real-time HUD telemetry every single frame over 4.8 seconds.
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
        lang: str = "ES",
        run_time: float = 4.8,
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
        self.lang = lang
        self.last_tick = {k: -1 for k in spheres}

        # Offset vectors for floating sphere labels while moving
        self.label_offsets = {
            "rect": np.array([0.36, 0.22, 0.0]),
            "parab": np.array([0.36, 0.08, 0.0]),
            "braq": np.array([0.36, -0.14, 0.0]),
            "circ": np.array([-0.38, -0.16, 0.0]),
        }

    def interpolate_mobject(self, alpha: float):
        # Smoothly fade out release badge early in race
        if alpha > 0.12:
            fade_alpha = max(0.0, 1.0 - (alpha - 0.12) * 6.0)
            self.go_badge.set_opacity(fade_alpha)

        # Physical time runs from 0.0 to 1.62 s
        t_sim = alpha * 1.62
        tick_id = int(t_sim * 30)  # 30 Hz digital clock refresh

        for k, track in self.sim.tracks.items():
            st = track.get_state(t_sim, use_target_time=True)
            screen_pos = self.to_screen(st.x, st.y)
            self.spheres[k].move_to(screen_pos)

            card = self.hud_cards[k]

            # Update digital clock and speedometer
            if tick_id != self.last_tick[k] or st.finished:
                self.last_tick[k] = tick_id

                timer_color = "#00FF66" if (k == "braq" and st.finished) else (WHITE if not st.finished else "#94A3B8")
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

                # Floating mini-timer over each sphere:
                if st.finished:
                    self.sphere_labels[k].set_opacity(0.0)
                else:
                    lbl_pos = screen_pos + self.label_offsets[k]
                    self.sphere_labels[k].become(
                        Text(
                            f"{st.t_elapsed:.2f}s",
                            font="Consolas",
                            font_size=9.5,
                            color=card["color"],
                            weight=BOLD,
                        ).move_to(lbl_pos)
                    )

                if k == "braq" and st.finished:
                    card["bg"].set_stroke(color="#00FF66", width=2.8)
                    win_tag = "1º LUGAR" if self.lang == "ES" else "1st PLACE"
                    card["name"].become(
                        Text(
                            win_tag,
                            font="Consolas",
                            font_size=10.5,
                            color="#00FF66",
                            weight=BOLD,
                        ).next_to(card["dot"], RIGHT, buff=0.06)
                    )
                elif k == "rect" and st.finished:
                    card["bg"].set_stroke(color="#FF0055", width=2.2)

        # Luminous particle trail for cycloid
        st_braq = self.sim.tracks["braq"].get_state(t_sim, use_target_time=True)
        if not st_braq.finished and t_sim > 0.04:
            pos = self.to_screen(st_braq.x, st_braq.y)
            spark = Dot(
                point=pos + np.array([np.random.uniform(-0.06, 0.06), np.random.uniform(-0.06, 0.06), 0.0]),
                radius=np.random.uniform(0.035, 0.06),
                color="#00F0FF",
            )
            spark.set_opacity(0.85)
            self.spark_dots.add(spark)
            if len(self.spark_dots) > 35:
                self.spark_dots.remove(self.spark_dots[0])
        elif st_braq.finished and len(self.spark_dots) > 0:
            self.spark_dots.remove(self.spark_dots[0])


def create_brachistochrone_scene_class(lang: str = "ES"):
    """Factory creating language-specific Brachistochrone scene (14.5s duration)."""

    class BrachistochroneScene(Scene):
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
                sx = (x_phys - x_mid_phys) * scale
                sy = y_screen_offset + (y_phys - y_mid_phys) * scale
                return np.array([sx, sy, 0.0])

            # Track Visual Parameters & Names
            if lang == "ES":
                track_styles = {
                    "braq": {"name": "CICLOIDE", "color": "#00F0FF", "card_x": -3.05, "len": "10.36 m"},
                    "circ": {"name": "CÍRCULO", "color": "#A855F7", "card_x": -1.02, "len": "10.15 m"},
                    "parab": {"name": "PARÁBOLA", "color": "#EAB308", "card_x": 1.02, "len": "10.05 m"},
                    "rect": {"name": "RECTA", "color": "#FF0055", "card_x": 3.05, "len": "9.90 m"},
                }
            else:
                track_styles = {
                    "braq": {"name": "CYCLOID", "color": "#00F0FF", "card_x": -3.05, "len": "10.36 m"},
                    "circ": {"name": "CIRCLE", "color": "#A855F7", "card_x": -1.02, "len": "10.15 m"},
                    "parab": {"name": "PARABOLA", "color": "#EAB308", "card_x": 1.02, "len": "10.05 m"},
                    "rect": {"name": "STRAIGHT", "color": "#FF0055", "card_x": 3.05, "len": "9.90 m"},
                }

            # ----------------------------------------------------
            # 2. Header & Branding in Top Safe Zone (Y in [5.2, 6.4])
            # ----------------------------------------------------
            header_group = VGroup()

            tag_str = "¿LA LÍNEA RECTA ES LA MÁS RÁPIDA?" if lang == "ES" else "IS THE STRAIGHT LINE THE FASTEST?"
            tag = Text(
                tag_str,
                font="Consolas",
                font_size=15.5,
                color="#38BDF8",
                weight=BOLD,
            ).move_to(np.array([0.0, 6.25, 0.0]))

            title_str = "LA CURVA BRAQUISTÓCRONA" if lang == "ES" else "THE BRACHISTOCHRONE CURVE"
            title = Text(
                title_str,
                font="Consolas",
                font_size=21,
                color=WHITE,
                weight=BOLD,
            ).next_to(tag, DOWN, buff=0.12)

            sub_str = "Johann Bernoulli (1696) // Cálculo de Variaciones" if lang == "ES" else "Johann Bernoulli (1696) // Calculus of Variations"
            subtitle = Text(
                sub_str,
                font="Consolas",
                font_size=11.5,
                color="#F59E0B",
                weight=SEMIBOLD,
            ).next_to(title, DOWN, buff=0.10)

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
                ).move_to(np.array([cx, 4.55, 0.0]))

                dot = Dot(radius=0.06, color=style["color"]).move_to(
                    card_bg.get_corner(UL) + np.array([0.22, -0.22, 0.0])
                )

                name_lbl = Text(
                    style["name"],
                    font="Consolas",
                    font_size=11,
                    color=style["color"],
                    weight=BOLD,
                ).next_to(dot, RIGHT, buff=0.08)

                timer_lbl = Text(
                    "0.000 s",
                    font="Consolas",
                    font_size=13.5,
                    color=WHITE,
                    weight=BOLD,
                ).move_to(card_bg.get_center() + np.array([0.0, -0.04, 0.0]))

                speed_lbl = Text(
                    "0.0 m/s",
                    font="Consolas",
                    font_size=10,
                    color="#94A3B8",
                ).move_to(card_bg.get_bottom() + np.array([0.0, 0.16, 0.0]))

                card_vgroup = VGroup(card_bg, dot, name_lbl, timer_lbl, speed_lbl)
                hud_cards[key] = {
                    "group": card_vgroup,
                    "bg": card_bg,
                    "dot": dot,
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
            start_ring = Circle(radius=0.22, color="#38BDF8", stroke_width=2.5).move_to(start_pt)
            start_core = Dot(radius=0.08, color=WHITE).move_to(start_pt)
            s_label_str = "A (0, 4.0)\nINICIO" if lang == "ES" else "A (0, 4.0)\nSTART"
            start_lbl = Text(s_label_str, font="Consolas", font_size=10, color="#38BDF8", line_spacing=0.9)
            start_lbl.next_to(start_ring, UL, buff=0.12)
            start_group = VGroup(start_ring, start_core, start_lbl)

            # Finish Gate
            end_ring = Circle(radius=0.26, color="#00FF66", stroke_width=3.0).move_to(end_pt)
            end_core = Dot(radius=0.09, color=WHITE).move_to(end_pt)
            e_label_str = "B (7, -3.0)\nMETA" if lang == "ES" else "B (7, -3.0)\nFINISH"
            end_lbl = Text(e_label_str, font="Consolas", font_size=10.5, color="#00FF66", weight=BOLD, line_spacing=0.9)
            end_lbl.next_to(end_ring, RIGHT, buff=0.16)

            finish_line_seg = DashedLine(
                start=end_pt + np.array([-0.4, 0.4, 0.0]),
                end=end_pt + np.array([0.4, -0.4, 0.0]),
                color="#00FF66",
                stroke_width=2.0,
                dash_length=0.1,
            )
            end_group = VGroup(end_ring, end_core, end_lbl, finish_line_seg)

            # ----------------------------------------------------
            # 6. High-Tech Spheres & Dynamic Callouts
            # ----------------------------------------------------
            spheres = {}
            sphere_labels = {}
            sphere_group = VGroup()

            for key, style in track_styles.items():
                s_glow = Circle(radius=0.18, color=style["color"], stroke_width=2.5, fill_opacity=0.0)
                s_base = Circle(radius=0.13, color=style["color"], stroke_width=2.0, fill_color="#CBD5E1", fill_opacity=0.95)
                s_spec = Dot(radius=0.04, color=WHITE).shift(np.array([-0.04, 0.04, 0.0]))

                ball = VGroup(s_glow, s_base, s_spec).move_to(start_pt)
                spheres[key] = ball
                sphere_group.add(ball)

                lbl = Text("0.00s", font="Consolas", font_size=9.5, color=style["color"], weight=BOLD)
                lbl.move_to(start_pt + np.array([0.30, 0.15, 0.0]))
                sphere_labels[key] = lbl
                sphere_group.add(lbl)

            # Introductory Length Comparison Badge
            len_badge_rect_str = "LÍNEA RECTA: Distancia más corta (9.90 m)" if lang == "ES" else "STRAIGHT LINE: Shortest Distance (9.90 m)"
            len_badge_rect = Text(
                len_badge_rect_str,
                font="Consolas",
                font_size=11,
                color="#FF0055",
                weight=BOLD,
            ).move_to(np.array([0.0, 3.45, 0.0]))

            len_badge_braq_str = "CICLOIDE: Trayectoria más larga (10.36 m)" if lang == "ES" else "CYCLOID: Longer Trajectory (10.36 m)"
            len_badge_braq = Text(
                len_badge_braq_str,
                font="Consolas",
                font_size=11,
                color="#00F0FF",
                weight=BOLD,
            ).move_to(np.array([0.0, 3.45, 0.0]))

            # Countdown Banner
            c_ready = "3... 2... 1... ¡LIBERACIÓN!" if lang == "ES" else "3... 2... 1... RELEASE!"
            countdown_txt = Text(
                c_ready,
                font="Consolas",
                font_size=17,
                color="#FCD34D",
                weight=BOLD,
            ).move_to(np.array([0.0, 3.45, 0.0]))

            # ----------------------------------------------------
            # 7. Physical Explanation Elements (Fase 3: ¿Por qué gana?)
            # ----------------------------------------------------
            explain_group = VGroup()
            explain_bg = RoundedRectangle(
                corner_radius=0.15,
                width=8.4,
                height=2.05,
                fill_color="#0F172A",
                fill_opacity=0.95,
                stroke_color="#00F0FF",
                stroke_width=2.0,
            ).move_to(np.array([0.0, -4.30, 0.0]))

            if lang == "ES":
                exp_title = Text("¿POR QUÉ GANA LA CICLOIDE? // FÍSICA DEL DESCENSO", font="Consolas", font_size=12, color="#00F0FF", weight=BOLD)
                exp_l1 = Text("1. CAÍDA VERTICAL RÁPIDA: Convierte energía potencial en cinética de golpe.", font="Consolas", font_size=9.8, color=WHITE, weight=BOLD)
                exp_l2 = Text("2. VELOCIDAD MÁXIMA: v = √(2gh) alta durante casi todo el recorrido.", font="Consolas", font_size=9.8, color="#FCD34D", weight=BOLD)
                exp_formula = Text("T = ∫ (ds / v) = MÍNIMO GLOBAL (Johann Bernoulli, 1696)", font="Consolas", font_size=10.5, color="#38BDF8", weight=BOLD)
                exp_sub = Text("Mayor velocidad media vence por completo a la menor distancia.", font="Consolas", font_size=9.5, color="#00FF66", weight=SEMIBOLD)
            else:
                exp_title = Text("WHY DOES THE CYCLOID WIN? // PHYSICS OF DESCENT", font="Consolas", font_size=12, color="#00F0FF", weight=BOLD)
                exp_l1 = Text("1. STEEP INITIAL DROP: Rapidly trades potential for kinetic energy.", font="Consolas", font_size=9.8, color=WHITE, weight=BOLD)
                exp_l2 = Text("2. PEAK VELOCITY: v = √(2gh) is maintained across most of the path.", font="Consolas", font_size=9.8, color="#FCD34D", weight=BOLD)
                exp_formula = Text("T = ∫ (ds / v) = GLOBAL MINIMUM (Johann Bernoulli, 1696)", font="Consolas", font_size=10.5, color="#38BDF8", weight=BOLD)
                exp_sub = Text("Much higher average speed easily beats the shortest distance.", font="Consolas", font_size=9.5, color="#00FF66", weight=SEMIBOLD)

            exp_title.move_to(explain_bg.get_top() + np.array([0.0, -0.25, 0.0]))
            exp_l1.next_to(exp_title, DOWN, buff=0.08)
            exp_l2.next_to(exp_l1, DOWN, buff=0.06)
            exp_formula.next_to(exp_l2, DOWN, buff=0.08)
            exp_sub.next_to(exp_formula, DOWN, buff=0.06)
            explain_group.add(explain_bg, exp_title, exp_l1, exp_l2, exp_formula, exp_sub)

            # Steep drop indicator arrow near Point A
            steep_arrow = Arrow(
                start=start_pt + np.array([0.2, 0.0, 0.0]),
                end=start_pt + np.array([0.4, -1.3, 0.0]),
                color="#00F0FF",
                stroke_width=3.5,
                buff=0.0,
            )
            steep_lbl_str = "CAÍDA ABRUPTA\n(Aceleración máxima)" if lang == "ES" else "STEEP DROP\n(Max acceleration)"
            steep_lbl = Text(steep_lbl_str, font="Consolas", font_size=9.5, color="#00F0FF", weight=BOLD, line_spacing=0.85)
            steep_lbl.next_to(steep_arrow, RIGHT, buff=0.10)
            steep_group = VGroup(steep_arrow, steep_lbl)

            # ----------------------------------------------------
            # 8. Interactive Leaderboard Podium (Fase 4: Podio)
            # ----------------------------------------------------
            podium_group = VGroup()
            podium_bg = RoundedRectangle(
                corner_radius=0.15,
                width=8.4,
                height=2.05,
                fill_color="#0F172A",
                fill_opacity=0.98,
                stroke_color="#00FF66",
                stroke_width=2.2,
            ).move_to(np.array([0.0, -4.30, 0.0]))

            if lang == "ES":
                pod_title = Text("PODIO OFICIAL // RESULTADOS DE TIEMPO", font="Consolas", font_size=12, color="#00FF66", weight=BOLD)
                pod_r1 = Text("🥇 1º CICLOIDE  : 1.321 s  [TIEMPO MÍNIMO - MÁS RÁPIDA]", font="Consolas", font_size=9.8, color="#00F0FF", weight=BOLD)
                pod_r2 = Text("🥈 2º CÍRCULO   : 1.388 s  (+0.067 s)", font="Consolas", font_size=9.5, color="#A855F7")
                pod_r3 = Text("🥉 3º PARÁBOLA  : 1.448 s  (+0.127 s)", font="Consolas", font_size=9.5, color="#EAB308")
                pod_r4 = Text("❌ 4º RECTA     : 1.622 s  (+0.301 s - DISTANCIA MÁS CORTA)", font="Consolas", font_size=9.8, color="#FF0055", weight=BOLD)
            else:
                pod_title = Text("OFFICIAL LEADERBOARD // TIME RESULTS", font="Consolas", font_size=12, color="#00FF66", weight=BOLD)
                pod_r1 = Text("🥇 1st CYCLOID : 1.321 s  [MINIMUM TIME - FASTEST]", font="Consolas", font_size=9.8, color="#00F0FF", weight=BOLD)
                pod_r2 = Text("🥈 2nd CIRCLE  : 1.388 s  (+0.067 s)", font="Consolas", font_size=9.5, color="#A855F7")
                pod_r3 = Text("🥉 3rd PARABOLA: 1.448 s  (+0.127 s)", font="Consolas", font_size=9.5, color="#EAB308")
                pod_r4 = Text("❌ 4th STRAIGHT: 1.622 s  (+0.301 s - SHORTEST DISTANCE)", font="Consolas", font_size=9.8, color="#FF0055", weight=BOLD)

            pod_title.move_to(podium_bg.get_top() + np.array([0.0, -0.24, 0.0]))
            pod_r1.next_to(pod_title, DOWN, buff=0.08)
            pod_r2.next_to(pod_r1, DOWN, buff=0.06)
            pod_r3.next_to(pod_r2, DOWN, buff=0.06)
            pod_r4.next_to(pod_r3, DOWN, buff=0.06)
            podium_group.add(podium_bg, pod_title, pod_r1, pod_r2, pod_r3, pod_r4)

            # Final Takeaway Badge
            takeaway_str = "¡LA DISTANCIA MÁS CORTA NO ES LA MÁS RÁPIDA!" if lang == "ES" else "THE SHORTEST DISTANCE IS NOT THE FASTEST!"
            takeaway_badge = Text(
                takeaway_str,
                font="Consolas",
                font_size=13,
                color="#00FF66",
                weight=BOLD,
            ).move_to(np.array([0.0, 3.45, 0.0]))

            # ----------------------------------------------------
            # 9. ANIMATION SEQUENCE (14.50 Seconds Total)
            # ----------------------------------------------------

            # [0.0 - 0.7s] Intro: Header & HUD Telemetry Cards
            self.play(
                FadeIn(header_group, shift=DOWN * 0.3),
                FadeIn(hud_group, shift=DOWN * 0.2),
                FadeIn(start_group),
                FadeIn(end_group),
                run_time=0.7,
            )

            # [0.7 - 2.1s] Drawing Tracks & Visualizing the Intuition Trap
            # 1. Straight Line (the shortest path)
            self.play(
                Create(track_mobjects["rect"]),
                FadeIn(len_badge_rect, shift=UP * 0.1),
                run_time=0.6,
            )

            # 2. Draw Parabola, Circle, and Cycloid
            self.play(
                ReplacementTransform(len_badge_rect, len_badge_braq),
                LaggedStart(
                    Create(track_mobjects["parab"]),
                    Create(track_mobjects["circ"]),
                    Create(track_mobjects["braq"]),
                    lag_ratio=0.15,
                ),
                run_time=0.8,
            )

            # [2.1 - 2.5s] Spheres Placed at Start Gate A
            self.add(sphere_group)
            self.play(
                FadeOut(len_badge_braq),
                FadeIn(countdown_txt, scale=1.15),
                run_time=0.4,
            )

            # [2.5 - 3.0s] Countdown Release Badge
            go_str = "¡LIBERACIÓN SIMULTÁNEA!" if lang == "ES" else "SIMULTANEOUS RELEASE!"
            go_badge = Text(
                go_str,
                font="Consolas",
                font_size=17,
                color="#00FF66",
                weight=BOLD,
            ).move_to(np.array([0.0, 3.45, 0.0]))

            self.play(
                ReplacementTransform(countdown_txt, go_badge),
                run_time=0.5,
            )

            # [3.0 - 7.8s] THE 4-TRACK VECTOR GRAVITY RACE (4.8s run_time)
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
                lang=lang,
                run_time=4.8,
            )

            self.play(race_anim)
            self.remove(go_badge)

            # Ensure all spheres are at exact finish locations
            for k, track in sim.tracks.items():
                st = track.get_state(1.62, use_target_time=True)
                spheres[k].move_to(to_screen(st.x, st.y))

            # [7.8 - 8.2s] Arrival Pulse & Finish Shockwave
            arrival_pulse = Circle(radius=0.26, color="#00FF66", stroke_width=4.5).move_to(end_pt)
            self.play(
                arrival_pulse.animate.scale(2.5).set_stroke(opacity=0.0),
                FadeOut(VGroup(*sphere_labels.values())),
                run_time=0.4,
            )
            self.remove(arrival_pulse)

            # [8.2 - 11.5s] PHYSICAL EXPLANATION: WHY THE CYCLOID WINS (3.3s)
            # Dim the circle and parabola to spotlight the Recta vs Cicloide duel
            self.play(
                track_mobjects["circ"].animate.set_opacity(0.18),
                track_mobjects["parab"].animate.set_opacity(0.18),
                spheres["circ"].animate.set_opacity(0.3),
                spheres["parab"].animate.set_opacity(0.3),
                FadeIn(explain_group, shift=UP * 0.3),
                FadeIn(steep_group, shift=DOWN * 0.2),
                run_time=0.8,
            )

            # Pulse the Cycloid track to emphasize kinetic speed accumulation
            self.play(
                track_mobjects["braq"].animate.set_stroke(width=5.5),
                Wiggle(steep_group, scale_value=1.12),
                run_time=1.2,
            )

            self.play(
                track_mobjects["braq"].animate.set_stroke(width=3.8),
                run_time=1.3,
            )

            # [11.5 - 13.8s] THE LEADERBOARD PODIUM (2.3s)
            self.play(
                FadeOut(steep_group),
                ReplacementTransform(explain_group, podium_group),
                FadeIn(takeaway_badge, scale=1.1),
                run_time=0.8,
            )

            # Restore track visibilities softly and emphasize podium
            self.play(
                track_mobjects["circ"].animate.set_opacity(0.7),
                track_mobjects["parab"].animate.set_opacity(0.7),
                spheres["circ"].animate.set_opacity(1.0),
                spheres["parab"].animate.set_opacity(1.0),
                Wiggle(takeaway_badge, scale_value=1.06),
                run_time=1.5,
            )

            # [13.8 - 14.5s] Clean Outro Hold (0.7s)
            self.wait(0.7)

    return BrachistochroneScene


class BrachistochroneSceneES(create_brachistochrone_scene_class(lang="ES")):
    pass


class BrachistochroneSceneEN(create_brachistochrone_scene_class(lang="EN")):
    pass


# Backward compatibility alias
class TikTokBrachistochrone(BrachistochroneSceneES):
    pass
