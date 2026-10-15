"""
Continuum Lab — Classical Mechanics & Mechanical Engineering Architecture
Module: 02 Dinamica y Vibraciones / 05 Mecanismo Peaucellier Lipkin
File: peaucellier_scene.py
Target Format: 1080x1920 (9:16 Vertical UHD @ 60 FPS)

Strict Safe-Zone & Typographic Rules Enforced:
  - Top Safe Zone: > 160 px (Y < 6.4 in Manim 16.0 frame)
  - Bottom Safe Zone: > 320 px (Y > -4.8 in Manim 16.0 frame)
  - Right Margin: > 130 px (X < +3.2 in Manim 9.0 frame)
  - Zero Text Overlap & Zero Text Out-of-Bounds
"""

import numpy as np
from pathlib import Path
from manim import *

# -----------------------------------------------------------------------------
# 1. RENDER & SAFE ZONES CONFIGURATION
# -----------------------------------------------------------------------------
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#0B0F19"


def create_peaucellier_scene_class(lang: str = "ES"):
    class LocalizedPeaucellierScene(Scene):
        def construct(self):
            # 1. Physical / Geometric Parameters
            x_O1 = -2.00
            y_O1 = 0.0
            O1_pos = np.array([x_O1, y_O1, 0.0])
            r_crank = 0.85
            O2_pos = np.array([x_O1 + r_crank, y_O1, 0.0])
            
            R_arm = 2.80
            l_rhombus = 1.60
            k_inv = R_arm**2 - l_rhombus**2  # 5.2800
            x_exact_line = x_O1 + (k_inv / (2.0 * r_crank))  # -2.00 + 3.10588 = 1.1059
            
            # 2. Mathematical Reference Grid & Inversion Guides
            # Vertical straight line rail
            rail_line = DashedLine(
                start=np.array([x_exact_line, -3.0, 0.0]),
                end=np.array([x_exact_line, 3.0, 0.0]),
                dash_length=0.12,
                dashed_ratio=0.5,
                color="#334155",
                stroke_width=2.0
            )
            
            # Crank circle guide (passing through O1)
            crank_circle = Circle(
                radius=r_crank,
                color="#1E293B",
                stroke_width=1.8
            ).move_to(O2_pos)
            
            # Ground anchors for O1 and O2
            def make_ground_symbol(pos, label_text, label_dir=LEFT):
                g_pivot = Dot(pos, radius=0.09, color="#94A3B8")
                g_ring = Circle(radius=0.15, color="#64748B", stroke_width=1.5).move_to(pos)
                lbl = Text(label_text, font="Consolas", font_size=17, weight=BOLD, color="#94A3B8")
                lbl.next_to(pos, label_dir, buff=0.14)
                return Group(g_pivot, g_ring, lbl)
                
            ground_O1 = make_ground_symbol(O1_pos, "O₁", LEFT)
            ground_O2 = make_ground_symbol(O2_pos, "O₂", DOWN)
            
            self.add(rail_line, crank_circle, ground_O1, ground_O2)
            
            # 3. Dynamic Linkage Elements (Lines & Joint Dots)
            # Long arms: O1-A and O1-B (Cyan)
            bar_O1_A = Line(O1_pos, O1_pos, color="#00F0FF", stroke_width=4.5)
            bar_O1_B = Line(O1_pos, O1_pos, color="#00F0FF", stroke_width=4.5)
            
            # Crank: O2-P (Amber)
            bar_O2_P = Line(O2_pos, O2_pos, color="#F59E0B", stroke_width=5.0)
            
            # Rhombus: A-P, B-P, A-P', B-P' (Electric Emerald)
            bar_A_P  = Line(O1_pos, O1_pos, color="#00FFA3", stroke_width=4.0)
            bar_B_P  = Line(O1_pos, O1_pos, color="#00FFA3", stroke_width=4.0)
            bar_A_Pp = Line(O1_pos, O1_pos, color="#00FFA3", stroke_width=4.0)
            bar_B_Pp = Line(O1_pos, O1_pos, color="#00FFA3", stroke_width=4.0)
            
            # Joints
            dot_P  = Dot(radius=0.10, color="#FFE600")
            dot_Pp = Dot(radius=0.12, color="#FF0055")
            dot_A  = Dot(radius=0.09, color="#00F0FF")
            dot_B  = Dot(radius=0.09, color="#00F0FF")
            
            # Joint text tags
            tag_P  = Text("P", font="Consolas", font_size=16, weight=BOLD, color="#FFE600")
            tag_Pp = Text("P'", font="Consolas", font_size=18, weight=BOLD, color="#FF0055")
            tag_A  = Text("A", font="Consolas", font_size=15, weight=BOLD, color="#00F0FF")
            tag_B  = Text("B", font="Consolas", font_size=15, weight=BOLD, color="#00F0FF")
            
            # Dynamic Laser Tracer Path (Ruby Crimson)
            tracer_path = VMobject(color="#FF0055", stroke_width=4.0, stroke_opacity=0.95)
            tracer_glow = VMobject(color="#FF0055", stroke_width=9.0, stroke_opacity=0.35)
            tracer_points = []
            
            self.add(
                bar_O1_A, bar_O1_B, bar_O2_P,
                bar_A_P, bar_B_P, bar_A_Pp, bar_B_Pp,
                dot_P, dot_Pp, dot_A, dot_B,
                tag_P, tag_Pp, tag_A, tag_B,
                tracer_glow, tracer_path
            )
            
            # 4. Telemetry HUD Cards (Strictly within Safe Zones)
            hud_card, hud_readouts = self._build_hud_card(lang=lang)
            callout_card = self._build_callout_card(lang=lang)
            
            self.add(hud_card, callout_card)
            
            # 5. Kinematic Solver Function
            def compute_positions(theta):
                P = O2_pos[:2] + r_crank * np.array([np.cos(theta), np.sin(theta)])
                v_OP = P - O1_pos[:2]
                dist_OP = max(1e-6, np.linalg.norm(v_OP))
                phi = np.arctan2(v_OP[1], v_OP[0])
                u_ray = np.array([np.cos(phi), np.sin(phi)])
                n_perp = np.array([-np.sin(phi), np.cos(phi)])
                
                dist_OPp = k_inv / dist_OP
                Pp = O1_pos[:2] + dist_OPp * u_ray
                
                dist_OM = 0.5 * (dist_OP + dist_OPp)
                M = O1_pos[:2] + dist_OM * u_ray
                
                half_d = 0.5 * abs(dist_OPp - dist_OP)
                h_AM = np.sqrt(max(0.0, l_rhombus**2 - half_d**2))
                A = M + h_AM * n_perp
                B = M - h_AM * n_perp
                
                return P, Pp, A, B, phi, dist_OP, dist_OPp
                
            # 6. Animation Time Trackers
            theta_tracker = ValueTracker(0.0)
            
            # Updater
            def linkage_updater(dt=0):
                th = theta_tracker.get_value()
                P, Pp, A, B, phi, d_OP, d_OPp = compute_positions(th)
                
                P_3d  = np.array([P[0], P[1], 0.0])
                Pp_3d = np.array([Pp[0], Pp[1], 0.0])
                A_3d  = np.array([A[0], A[1], 0.0])
                B_3d  = np.array([B[0], B[1], 0.0])
                
                # Bars
                bar_O1_A.set_points_as_corners([O1_pos, A_3d])
                bar_O1_B.set_points_as_corners([O1_pos, B_3d])
                bar_O2_P.set_points_as_corners([O2_pos, P_3d])
                
                bar_A_P.set_points_as_corners([A_3d, P_3d])
                bar_B_P.set_points_as_corners([B_3d, P_3d])
                bar_A_Pp.set_points_as_corners([A_3d, Pp_3d])
                bar_B_Pp.set_points_as_corners([B_3d, Pp_3d])
                
                # Dots
                dot_P.move_to(P_3d)
                dot_Pp.move_to(Pp_3d)
                dot_A.move_to(A_3d)
                dot_B.move_to(B_3d)
                
                # Tags
                tag_P.move_to(P_3d + LEFT * 0.24)
                tag_Pp.move_to(Pp_3d + RIGHT * 0.28)
                tag_A.move_to(A_3d + UP * 0.24)
                tag_B.move_to(B_3d + DOWN * 0.24)
                
                # Tracer
                tracer_points.append(Pp_3d.copy())
                if len(tracer_points) > 550:
                    tracer_points.pop(0)
                if len(tracer_points) > 1:
                    tracer_path.set_points_as_corners(tracer_points)
                    tracer_glow.set_points_as_corners(tracer_points)
                    
                # Update live HUD readouts
                err_val = abs(Pp[0] - x_exact_line)
                hud_readouts["err"].become(
                    Text(
                        f"ε = {err_val:.8f} mm",
                        font="Consolas", font_size=17, weight=BOLD, color="#00FFA3"
                    )
                    .move_to(hud_readouts["err"].get_center())
                    .align_to(hud_readouts["err"], LEFT)
                )
                hud_readouts["pos"].become(
                    Text(
                        f"X = {Pp[0]:.4f} | Y = {Pp[1]:+.2f}",
                        font="Consolas", font_size=17, weight=BOLD, color="#FFE600"
                    )
                    .move_to(hud_readouts["pos"].get_center())
                    .align_to(hud_readouts["pos"], LEFT)
                )

            self.add_updater(linkage_updater)
            
            # 7. Cinematic Choreography (14.0 seconds total)
            # Phase 1: Mechanism Initialization & Geometry Scan (0.0s -> 2.0s)
            self.wait(1.5)
            
            # Phase 2: First Full Upward Stroke (2.0s -> 5.5s)
            self.play(
                theta_tracker.animate.set_value(np.radians(50.0)),
                run_time=3.5,
                rate_func=linear
            )
            
            # Phase 3: Continuous Harmonic Oscillation across Line (5.5s -> 12.5s)
            self.play(
                theta_tracker.animate.set_value(-np.radians(50.0)),
                run_time=3.5,
                rate_func=linear
            )
            self.play(
                theta_tracker.animate.set_value(np.radians(50.0)),
                run_time=3.5,
                rate_func=linear
            )
            
            # Phase 4: Centerline Return & Final Lock (12.5s -> 14.0s)
            self.play(
                theta_tracker.animate.set_value(0.0),
                run_time=1.5,
                rate_func=linear
            )
            self.wait(0.5)

        def _build_hud_card(self, lang="ES"):
            card_w = 7.10
            card_h = 2.45
            pos_x = -0.40  # Safe right margin: right edge at +3.15 (162 px clear)
            pos_y = 5.20   # Safe top margin: top edge at +6.425 (189 px clear)
            
            bg = RoundedRectangle(
                corner_radius=0.16, width=card_w, height=card_h,
                fill_color="#10172A", fill_opacity=0.94, stroke_color="#00F0FF", stroke_width=2.0
            ).move_to([pos_x, pos_y, 0])
            
            title_str = "CONTINUUM LAB // CINEMÁTICA EXACTA (1864)" if lang == "ES" else "CONTINUUM LAB // EXACT KINEMATICS (1864)"
            title = Text(title_str, font="Consolas", font_size=19, weight=BOLD, color="#00F0FF")
            title.next_to(bg.get_top(), DOWN, buff=0.18)
            
            sep = Line(
                start=[-card_w / 2.0 + 0.35, 0, 0],
                end=[card_w / 2.0 - 0.35, 0, 0],
                stroke_color="#1E293B", stroke_width=1.5
            ).next_to(title, DOWN, buff=0.12)
            sep.align_to(bg, LEFT).shift(RIGHT * 0.35)
            
            # Rows
            row1_lbl = "INVERSIÓN GEOM : " if lang == "ES" else "GEOMETRIC INV  : "
            row1 = VGroup(
                Text(row1_lbl, font="Consolas", font_size=17, color="#94A3B8"),
                Text("OP · OP' = R² - l² = 5.28", font="Consolas", font_size=17, weight=BOLD, color="#00F0FF")
            ).arrange(RIGHT, buff=0.10)
            
            row2_lbl = "ERROR LINEAL   : " if lang == "ES" else "LINEAR ERROR   : "
            err_val = Text("ε = 0.00000000 mm", font="Consolas", font_size=17, weight=BOLD, color="#00FFA3")
            row2 = VGroup(
                Text(row2_lbl, font="Consolas", font_size=17, color="#94A3B8"),
                err_val
            ).arrange(RIGHT, buff=0.10)
            
            row3_lbl = "TRAZADOR P'    : " if lang == "ES" else "TRACER P'      : "
            pos_val = Text("X = 1.1059 | Y = +0.00", font="Consolas", font_size=17, weight=BOLD, color="#FFE600")
            row3 = VGroup(
                Text(row3_lbl, font="Consolas", font_size=17, color="#94A3B8"),
                pos_val
            ).arrange(RIGHT, buff=0.10)
            
            rows = VGroup(row1, row2, row3).arrange(DOWN, aligned_edge=LEFT, buff=0.10)
            rows.next_to(sep, DOWN, buff=0.12)
            rows.align_to(sep, LEFT)
            
            card_group = Group(bg, title, sep, rows)
            readouts = {"err": err_val, "pos": pos_val}
            return card_group, readouts

        def _build_callout_card(self, lang="ES"):
            card_w = 7.10
            card_h = 1.65
            pos_x = -0.40  # Safe right margin
            pos_y = -3.95  # Bottom edge at -4.775 (>380 px clear from bottom)
            
            bg = RoundedRectangle(
                corner_radius=0.16, width=card_w, height=card_h,
                fill_color="#10172A", fill_opacity=0.94, stroke_color="#FF0055", stroke_width=2.0
            ).move_to([pos_x, pos_y, 0])
            
            if lang == "ES":
                q_title = Text(
                    "¿POR QUÉ NO SE DESVÍA NI 1 MICRA?",
                    font="Consolas", font_size=19, weight=BOLD, color="#FFE600"
                ).next_to(bg.get_top(), DOWN, buff=0.18)
                
                q_line1 = Text(
                    "La inversión matemática pura (OP · OP' = cte)",
                    font="Consolas", font_size=16, color="#F1F5F9"
                )
                q_line2 = Text(
                    "transforma giros en una recta euclidiana perfecta.",
                    font="Consolas", font_size=16, color="#00FFA3"
                )
            else:
                q_title = Text(
                    "WHY DOESN'T IT DEVIATE BY 1 MICRON?",
                    font="Consolas", font_size=19, weight=BOLD, color="#FFE600"
                ).next_to(bg.get_top(), DOWN, buff=0.18)
                
                q_line1 = Text(
                    "Pure mathematical inversion (OP · OP' = const)",
                    font="Consolas", font_size=16, color="#F1F5F9"
                )
                q_line2 = Text(
                    "maps circular rotation into an absolute straight line.",
                    font="Consolas", font_size=16, color="#00FFA3"
                )
                
            q_lines = VGroup(q_line1, q_line2).arrange(DOWN, buff=0.08)
            q_lines.next_to(q_title, DOWN, buff=0.12)
            
            return Group(bg, q_title, q_lines)

    return LocalizedPeaucellierScene


class PeaucellierSceneES(create_peaucellier_scene_class(lang="ES")):
    pass


class PeaucellierSceneEN(create_peaucellier_scene_class(lang="EN")):
    pass


if __name__ == "__main__":
    import subprocess
    cmd = ["manim", "-pqh", __file__, "PeaucellierSceneES"]
    subprocess.run(cmd)
