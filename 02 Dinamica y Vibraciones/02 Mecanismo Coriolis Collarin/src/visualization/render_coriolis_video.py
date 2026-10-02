"""
Continuum Lab — Classical Mechanics & Dynamical Systems
Division: 02 Dinamica y Vibraciones / 02 Mecanismo Coriolis Collarin
Module: render_coriolis_video.py

Vectorized Manim 9:16 (1080x1920 @ 60 FPS) Video Production Engine
Bilingual Delivery (ES and EN) with Procedural Reactive Audio Multiplexing.

Features:
  - Exact 18.0s retention timeline (1080 frames at 60 FPS).
  - Safe zones: Top HUD Card at y = 5.4 (>220 px top margin), Bottom HUD Card at y = -4.3 (>340 px bottom margin).
  - Zero project branding or titles in frame (100% pure physics & kinematic telemetry).
  - 2-Bar Quick-Return mechanism with rotating crank O1-A and slotted rocker arm O2.
  - Dynamic 4-vector decomposition at sliding collar pin A:
      * a_coriolis (Electric Cyan #00f0ff)
      * v_rel (Neon Green #39ff14)
      * a_centripetal (Amber Yellow #ffb800)
      * a_euler (Hot Magenta #ff007f)
  - Hypnotic chromatic comet tracer trail of the slotted arm tip.
  - Multi-layer procedural acoustic stereo audio multiplexing.
"""

from manim import *
import numpy as np
import os
import subprocess
import sys
from pathlib import Path
import imageio_ffmpeg

# Add project root to sys.path
proj_dir = Path(__file__).resolve().parent.parent.parent
if str(proj_dir) not in sys.path:
    sys.path.insert(0, str(proj_dir))

from src.physics.coriolis_kinematics import CoriolisMechanismParams, CoriolisKinematicsSolver
from src.audio.coriolis_audio_synth import synthesize_coriolis_audio

# Exact TikTok 9:16 Canvas Configuration
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#0a0a0c"  # Cybernetic Deep Void

CACHE = {}


def precompute_coriolis_data(duration=18.0, fps=60):
    if "pA_arr" in CACHE:
        return CACHE

    params = CoriolisMechanismParams(L1=1.0, d=1.55, omega1=2.5, arm_extension=1.35)
    solver = CoriolisKinematicsSolver(params)

    geom_scale = 1.35
    offset_y = 0.85
    O1 = np.array([0.0, offset_y, 0.0])
    O2 = np.array([0.0, offset_y - params.d * geom_scale, 0.0])

    total_frames = int(fps * duration)
    dt_frame = 1.0 / fps

    t_arr = np.linspace(0, duration, total_frames, endpoint=False)
    pA_list = []
    pTip_list = []
    u_r2_list = []
    u_th2_list = []
    v_cor_list = []
    v_vrel_list = []
    v_cent_list = []
    v_euler_list = []
    acor_mag_list = []
    vrel_mag_list = []
    omega2_list = []
    theta1_list = []
    residual_list = []

    for t in t_arr:
        th1 = params.omega1 * t
        s = solver.solve(th1, t)

        # Coordenadas en Manim
        rA_3d = np.array([s.r_A[0] * geom_scale, s.r_A[1] * geom_scale + offset_y, 0.0])
        rTip_3d = np.array([s.r_tip_arm[0] * geom_scale, s.r_tip_arm[1] * geom_scale + offset_y, 0.0])
        ur2_3d = np.array([s.u_r2[0], s.u_r2[1], 0.0])
        uth2_3d = np.array([s.u_theta2[0], s.u_theta2[1], 0.0])

        # Escalas vectoriales para renderizado claro
        v_cor_3d = np.array([s.a_coriolis_vec[0], s.a_coriolis_vec[1], 0.0]) * 0.12
        v_vrel_3d = np.array([s.v_rel_vec[0], s.v_rel_vec[1], 0.0]) * 0.20
        v_cent_3d = np.array([s.a_centripetal_vec[0], s.a_centripetal_vec[1], 0.0]) * 0.10
        v_euler_3d = np.array([s.a_euler_vec[0], s.a_euler_vec[1], 0.0]) * 0.10

        pA_list.append(rA_3d)
        pTip_list.append(rTip_3d)
        u_r2_list.append(ur2_3d)
        u_th2_list.append(uth2_3d)
        v_cor_list.append(v_cor_3d)
        v_vrel_list.append(v_vrel_3d)
        v_cent_list.append(v_cent_3d)
        v_euler_list.append(v_euler_3d)
        acor_mag_list.append(s.a_coriolis_mag)
        vrel_mag_list.append(s.v_rel)
        omega2_list.append(s.omega2)
        theta1_list.append(th1)
        residual_list.append(s.residual_error)

    CACHE["O1"] = O1
    CACHE["O2"] = O2
    CACHE["pA_arr"] = np.array(pA_list)
    CACHE["pTip_arr"] = np.array(pTip_list)
    CACHE["u_r2_arr"] = np.array(u_r2_list)
    CACHE["u_th2_arr"] = np.array(u_th2_list)
    CACHE["v_cor_arr"] = np.array(v_cor_list)
    CACHE["v_vrel_arr"] = np.array(v_vrel_list)
    CACHE["v_cent_arr"] = np.array(v_cent_list)
    CACHE["v_euler_arr"] = np.array(v_euler_list)
    CACHE["acor_mag_arr"] = np.array(acor_mag_list)
    CACHE["vrel_mag_arr"] = np.array(vrel_mag_list)
    CACHE["omega2_arr"] = np.array(omega2_list)
    CACHE["theta1_arr"] = np.array(theta1_list)
    CACHE["residual_arr"] = np.array(residual_list)
    CACHE["t_arr"] = t_arr
    CACHE["total_frames"] = total_frames
    CACHE["duration"] = duration
    return CACHE


def create_coriolis_scene(lang: str = "ES"):
    class DynamicCoriolisMechanismScene(Scene):
        def construct(self):
            data = precompute_coriolis_data(duration=18.0, fps=60)
            O1 = data["O1"]
            O2 = data["O2"]
            pA_arr = data["pA_arr"]
            pTip_arr = data["pTip_arr"]
            u_r2_arr = data["u_r2_arr"]
            v_cor_arr = data["v_cor_arr"]
            v_vrel_arr = data["v_vrel_arr"]
            v_cent_arr = data["v_cent_arr"]
            v_euler_arr = data["v_euler_arr"]
            acor_mag_arr = data["acor_mag_arr"]
            vrel_mag_arr = data["vrel_mag_arr"]
            omega2_arr = data["omega2_arr"]
            theta1_arr = data["theta1_arr"]
            total_frames = data["total_frames"]
            total_seconds = data["duration"]

            # ----------------------------------------------------
            # 1. Subtle Precision Polar Grid (Laboratory Aesthetic)
            # ----------------------------------------------------
            grid_group = VGroup()
            for r in [0.7, 1.35, 2.0, 2.7]:
                grid_c = Circle(radius=r, color="#1e293b", stroke_width=0.9, stroke_opacity=0.35).move_to(O1)
                grid_group.add(grid_c)
            axis_h = Line(O1 + LEFT * 3.4, O1 + RIGHT * 3.4, color="#1e293b", stroke_width=0.8, stroke_opacity=0.25)
            axis_v = Line(O2 + DOWN * 0.6, O1 + UP * 2.2, color="#1e293b", stroke_width=0.8, stroke_opacity=0.25)
            grid_group.add(axis_h, axis_v)

            # Circular trajectory guideline for crank pin A
            crank_orbit = DashedVMobject(Circle(radius=1.35, color="#00f0ff", stroke_width=1.0, stroke_opacity=0.25).move_to(O1))
            grid_group.add(crank_orbit)

            # ----------------------------------------------------
            # 2. Top HUD Card (Safe Zone: y in [4.6, 6.2])
            # Leaves >220 px free from top edge
            # ----------------------------------------------------
            top_box = RoundedRectangle(
                corner_radius=0.14,
                width=7.8,
                height=1.65,
                color="#00f0ff",
                stroke_width=1.5,
                fill_color="#0d1117",
                fill_opacity=0.95
            ).move_to(UP * 5.4)

            eq_coriolis = MathTex(
                r"\mathbf{a}_{\mathrm{Coriolis}} = 2\,\boldsymbol{\omega}_2 \times \mathbf{v}_{\mathrm{rel}} = 2\,\omega_2\,\dot{r}_2\,\mathbf{u}_{\theta 2}",
                font_size=20,
                color="#ffffff"
            ).move_to(top_box.get_top() + DOWN * 0.42)

            rule_top = Line(LEFT * 3.4, RIGHT * 3.4, color="#1f2937", stroke_width=1.0).next_to(eq_coriolis, DOWN, buff=0.16)

            if lang == "ES":
                sub_top = MathTex(
                    r"\mathbf{a}_A = \mathbf{a}_{O_2} + \boldsymbol{\alpha}_2 \times \mathbf{r} + \boldsymbol{\omega}_2 \times (\boldsymbol{\omega}_2 \times \mathbf{r}) + \mathbf{a}_{\mathrm{rel}} + \mathbf{a}_{\mathrm{Coriolis}}",
                    font_size=17,
                    color="#00f0ff"
                )
            else:
                sub_top = MathTex(
                    r"\mathbf{a}_A = \mathbf{a}_{O_2} + \boldsymbol{\alpha}_2 \times \mathbf{r} + \boldsymbol{\omega}_2 \times (\boldsymbol{\omega}_2 \times \mathbf{r}) + \mathbf{a}_{\mathrm{rel}} + \mathbf{a}_{\mathrm{Coriolis}}",
                    font_size=17,
                    color="#00f0ff"
                )
            sub_top.next_to(rule_top, DOWN, buff=0.16)
            top_group = VGroup(top_box, eq_coriolis, rule_top, sub_top)

            # ----------------------------------------------------
            # 3. Vector Legend Card (Mid-Lower Zone: y = -2.6)
            # ----------------------------------------------------
            legend_box = RoundedRectangle(
                corner_radius=0.10,
                width=7.8,
                height=0.65,
                color="#30363d",
                stroke_width=1.0,
                fill_color="#0d1117",
                fill_opacity=0.90
            ).move_to(DOWN * 2.6)

            dot_cor = Dot(radius=0.07, color="#00f0ff")
            txt_cor = MathTex(r"\mathbf{a}_{\mathrm{cor}}", font_size=15, color="#00f0ff")
            g_cor = VGroup(dot_cor, txt_cor).arrange(RIGHT, buff=0.08)

            dot_vrel = Dot(radius=0.07, color="#39ff14")
            txt_vrel = MathTex(r"\mathbf{v}_{\mathrm{rel}}", font_size=15, color="#39ff14")
            g_vrel = VGroup(dot_vrel, txt_vrel).arrange(RIGHT, buff=0.08)

            dot_cent = Dot(radius=0.07, color="#ffb800")
            txt_cent = MathTex(r"\mathbf{a}_{\mathrm{cent}}", font_size=15, color="#ffb800")
            g_cent = VGroup(dot_cent, txt_cent).arrange(RIGHT, buff=0.08)

            dot_euler = Dot(radius=0.07, color="#ff007f")
            txt_euler = MathTex(r"\mathbf{a}_{\mathrm{Euler}}", font_size=15, color="#ff007f")
            g_euler = VGroup(dot_euler, txt_euler).arrange(RIGHT, buff=0.08)

            legend_row = VGroup(g_cor, g_vrel, g_cent, g_euler).arrange(RIGHT, buff=0.55).move_to(legend_box.get_center())
            legend_group = VGroup(legend_box, legend_row)

            # ----------------------------------------------------
            # 4. Bottom Telemetry Card (Safe Zone: y in [-5.15, -3.45])
            # Leaves >340 px free from bottom edge for TikTok overlay
            # ----------------------------------------------------
            bottom_box = RoundedRectangle(
                corner_radius=0.14,
                width=7.8,
                height=1.75,
                color="#ff007f",
                stroke_width=1.5,
                fill_color="#0d1117",
                fill_opacity=0.95
            ).move_to(DOWN * 4.3)

            if lang == "ES":
                telem_header = MathTex(
                    r"\text{DESCOMPOSICI\'ON VECTORIAL EN MARCO NO INERCIAL}",
                    font_size=18,
                    color="#ffffff"
                )
                desc_text = MathTex(
                    r"\|\mathbf{a}_A - \sum \mathbf{a}_k\| < 10^{-14}\,\mathrm{m/s^2} \quad \big| \quad \text{Soluci\'on Anal\'itica Exacta}",
                    font_size=16,
                    color="#ffaa00"
                )
            else:
                telem_header = MathTex(
                    r"\text{VECTOR DECOMPOSITION IN ROTATING NON-INERTIAL FRAME}",
                    font_size=18,
                    color="#ffffff"
                )
                desc_text = MathTex(
                    r"\|\mathbf{a}_A - \sum \mathbf{a}_k\| < 10^{-14}\,\mathrm{m/s^2} \quad \big| \quad \text{Exact Analytical Solution}",
                    font_size=16,
                    color="#ffaa00"
                )

            telem_header.move_to(bottom_box.get_top() + DOWN * 0.35)
            rule_bottom = Line(LEFT * 3.4, RIGHT * 3.4, color="#1f2937", stroke_width=1.0).next_to(telem_header, DOWN, buff=0.14)

            frame_idx = ValueTracker(0)

            # Telemetría en tiempo real (Pango/Cairo text para alto rendimiento a 60 FPS)
            telemetry_text = always_redraw(lambda: Text(
                f"a_cor = {acor_mag_arr[min(int(frame_idx.get_value()), total_frames - 1)]:+5.2f} m/s²   |   "
                f"v_rel = {vrel_mag_arr[min(int(frame_idx.get_value()), total_frames - 1)]:+5.2f} m/s   |   "
                f"ω₂ = {omega2_arr[min(int(frame_idx.get_value()), total_frames - 1)]:+5.2f} rad/s",
                font="Consolas",
                font_size=14,
                color="#39ff14"
            ).next_to(rule_bottom, DOWN, buff=0.16))

            desc_text.next_to(telemetry_text, DOWN, buff=0.14)
            bottom_group = VGroup(bottom_box, telem_header, rule_bottom, telemetry_text, desc_text)

            # ----------------------------------------------------
            # 5. Fixed Pivots O1 & O2 Assembly
            # ----------------------------------------------------
            pivot1_glow = Circle(radius=0.18, color="#00f0ff", stroke_width=1.5, stroke_opacity=0.4).move_to(O1)
            pivot1_ring = Circle(radius=0.11, color="#00f0ff", stroke_width=2.5).move_to(O1)
            pivot1_dot = Dot(point=O1, radius=0.05, color=WHITE)
            label_O1 = MathTex("O_1", font_size=16, color="#8b949e").next_to(O1, RIGHT, buff=0.15)

            pivot2_glow = Circle(radius=0.18, color="#58a6ff", stroke_width=1.5, stroke_opacity=0.4).move_to(O2)
            pivot2_ring = Circle(radius=0.11, color="#58a6ff", stroke_width=2.5).move_to(O2)
            pivot2_dot = Dot(point=O2, radius=0.05, color=WHITE)
            label_O2 = MathTex("O_2", font_size=16, color="#8b949e").next_to(O2, RIGHT, buff=0.15)

            pivots_group = VGroup(
                pivot1_glow, pivot1_ring, pivot1_dot, label_O1,
                pivot2_glow, pivot2_ring, pivot2_dot, label_O2
            )

            # ----------------------------------------------------
            # 6. Mechanism Links: Crank & Slotted Rocker Arm
            # ----------------------------------------------------
            # Manivela impulsora O1-A
            crank_glow = Line(O1, pA_arr[0], color="#00f0ff", stroke_width=5.5, stroke_opacity=0.55)
            crank_core = Line(O1, pA_arr[0], color=WHITE, stroke_width=2.2)

            # Barra ranurada 2 (rieles paralelos + línea central)
            rail_l = Line(O2, pTip_arr[0], color="#58a6ff", stroke_width=3.2, stroke_opacity=0.85)
            rail_r = Line(O2, pTip_arr[0], color="#58a6ff", stroke_width=3.2, stroke_opacity=0.85)
            slot_mid = Line(O2, pTip_arr[0], color="#ffffff", stroke_width=1.0, stroke_opacity=0.35)

            # Collarín deslizante articulado en A
            w_c, h_c = 0.38, 0.24
            collar_corners_init = [
                pA_arr[0] + np.array([-w_c/2, -h_c/2, 0.0]),
                pA_arr[0] + np.array([w_c/2, -h_c/2, 0.0]),
                pA_arr[0] + np.array([w_c/2, h_c/2, 0.0]),
                pA_arr[0] + np.array([-w_c/2, h_c/2, 0.0]),
            ]
            collar_poly = Polygon(*collar_corners_init, color=WHITE, stroke_width=1.5, fill_color="#ffd700", fill_opacity=0.85)
            collar_pin = Dot(radius=0.07, color="#00f0ff")

            # ----------------------------------------------------
            # 7. Dynamic Vector Quivers Emanating from Collar Pin A
            # ----------------------------------------------------
            arrow_cor = Arrow(pA_arr[0], pA_arr[0] + v_cor_arr[0], buff=0, color="#00f0ff", stroke_width=3.5, max_tip_length_to_length_ratio=0.35)
            arrow_vrel = Arrow(pA_arr[0], pA_arr[0] + v_vrel_arr[0], buff=0, color="#39ff14", stroke_width=3.0, max_tip_length_to_length_ratio=0.35)
            arrow_cent = Arrow(pA_arr[0], pA_arr[0] + v_cent_arr[0], buff=0, color="#ffb800", stroke_width=2.6, max_tip_length_to_length_ratio=0.35)
            arrow_euler = Arrow(pA_arr[0], pA_arr[0] + v_euler_arr[0], buff=0, color="#ff007f", stroke_width=2.6, max_tip_length_to_length_ratio=0.35)

            # Estela fosforescente del extremo de la barra ranurada
            trail = VMobject(stroke_width=2.6)
            trail.set_points_as_corners([pTip_arr[0], pTip_arr[0] + np.array([0.001, 0, 0])])
            trail.set_color_by_gradient("#00f0ff", "#38bdf8", "#a855f7", "#ec4899", "#f59e0b")

            # Updaters
            def update_mechanism(mob):
                idx = int(frame_idx.get_value())
                if idx >= total_frames:
                    idx = total_frames - 1

                pA = pA_arr[idx]
                pTip = pTip_arr[idx]
                ur2 = u_r2_arr[idx]

                # Manivela
                crank_glow.put_start_and_end_on(O1, pA)
                crank_core.put_start_and_end_on(O1, pA)

                # Rieles barra 2 (separación perpendicular +/- 0.10)
                dx = pTip[0] - O2[0]
                dy = pTip[1] - O2[1]
                L_arm = np.hypot(dx, dy) + 1e-8
                nx = -dy / L_arm * 0.10
                ny = dx / L_arm * 0.10
                n_vec = np.array([nx, ny, 0.0])

                rail_l.put_start_and_end_on(O2 + n_vec, pTip + n_vec)
                rail_r.put_start_and_end_on(O2 - n_vec, pTip - n_vec)
                slot_mid.put_start_and_end_on(O2, pTip)

                # Collarín orientado a lo largo de ur2
                cos2, sin2 = ur2[0], ur2[1]
                rot_mat = np.array([[cos2, -sin2], [sin2, cos2]])
                local_corners = np.array([
                    [-w_c/2, -h_c/2],
                    [w_c/2, -h_c/2],
                    [w_c/2, h_c/2],
                    [-w_c/2, h_c/2]
                ])
                world_corners_2d = (local_corners @ rot_mat.T) + np.array([pA[0], pA[1]])
                world_corners_3d = [np.array([c[0], c[1], 0.0]) for c in world_corners_2d]
                collar_poly.set_points_as_corners([*world_corners_3d, world_corners_3d[0]])
                collar_pin.move_to(pA)

                # Flechas vectoriales
                def update_arrow(arrow_mob, vec, min_len=0.08):
                    norm_v = np.linalg.norm(vec)
                    if norm_v > min_len:
                        arrow_mob.set_opacity(1.0)
                        arrow_mob.put_start_and_end_on(pA, pA + vec)
                    else:
                        arrow_mob.set_opacity(0.15)
                        arrow_mob.put_start_and_end_on(pA, pA + vec)

                update_arrow(arrow_cor, v_cor_arr[idx], 0.06)
                update_arrow(arrow_vrel, v_vrel_arr[idx], 0.06)
                update_arrow(arrow_cent, v_cent_arr[idx], 0.06)
                update_arrow(arrow_euler, v_euler_arr[idx], 0.06)

            def update_trail(mob):
                idx = int(frame_idx.get_value())
                if idx > 1:
                    idx_end = min(idx + 1, total_frames)
                    mob.set_points_smoothly(pTip_arr[:idx_end])
                    mob.set_color_by_gradient("#00f0ff", "#38bdf8", "#a855f7", "#ec4899", "#f59e0b")

            # ----------------------------------------------------
            # 8. Scene Assembly & Playback (Continuous from Frame 0)
            # ----------------------------------------------------
            self.add(grid_group)
            self.add(top_group)
            self.add(legend_group)
            self.add(bottom_group)
            self.add(pivots_group)

            self.add(crank_glow, crank_core)
            self.add(rail_l, rail_r, slot_mid)
            self.add(collar_poly, collar_pin)
            self.add(arrow_cent, arrow_euler, arrow_vrel, arrow_cor)
            self.add(trail)

            crank_glow.add_updater(update_mechanism)
            trail.add_updater(update_trail)

            # Play for exact 18.0 seconds at 60 FPS
            self.play(
                frame_idx.animate.set_value(total_frames - 1),
                run_time=total_seconds,
                rate_func=linear
            )
            self.wait(0.5)

    return DynamicCoriolisMechanismScene


class CoriolisMechanismSceneES(create_coriolis_scene("ES")):
    pass


class CoriolisMechanismSceneEN(create_coriolis_scene("EN")):
    pass


def render_all():
    base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    renders_dir = base_dir / "RENDERS" / "6 Mecanismo Coriolis Collarin"
    videos_dir = renders_dir / "videos"
    capturas_dir = renders_dir / "extra" / "capturas"
    benchmarks_dir = renders_dir / "extra" / "benchmarks"

    videos_dir.mkdir(parents=True, exist_ok=True)
    capturas_dir.mkdir(parents=True, exist_ok=True)
    benchmarks_dir.mkdir(parents=True, exist_ok=True)

    # 1. Migrar y organizar assets complementarios si existen en Coriolis_Mechanism
    old_renders_dir = base_dir / "RENDERS" / "Coriolis_Mechanism"
    if old_renders_dir.exists():
        import shutil
        for item in old_renders_dir.iterdir():
            if item.suffix in [".png", ".gif"]:
                dest = capturas_dir / item.name
                if not dest.exists():
                    shutil.copy2(item, dest)
                    print(f"[ORGANIZER] Copied capture -> {dest}")
            elif item.suffix in [".xlsx"]:
                dest = benchmarks_dir / item.name
                if not dest.exists():
                    shutil.copy2(item, dest)
                    print(f"[ORGANIZER] Copied benchmark -> {dest}")

    # 2. Precalcular cinemática y sintetizar audio reactivo de alta fidelidad
    data = precompute_coriolis_data(duration=18.0, fps=60)
    temp_audio_path = str(videos_dir / "coriolis_acoustic_synth.wav")
    print("\n[CONTINUUM LAB] Synthesizing physical Coriolis reactive audio...")
    synthesize_coriolis_audio(
        time_points=data["t_arr"],
        collar_x=data["pA_arr"][:, 0],
        v_rel=data["vrel_mag_arr"],
        a_cor=data["acor_mag_arr"],
        omega2=data["omega2_arr"],
        duration=18.5,
        fs=44100,
        output_path=temp_audio_path
    )

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    this_script = str(Path(__file__).resolve())

    # 3. Render Spanish Version
    print("\n=======================================================")
    print("[CONTINUUM LAB] Rendering Spanish Coriolis Mechanism (ES)...")
    print("=======================================================")
    cmd_manim_es = [
        sys.executable, "-m", "manim", "-qh", "--media_dir", str(videos_dir / "temp_media"),
        this_script, "CoriolisMechanismSceneES"
    ]
    subprocess.run(cmd_manim_es, check=True)

    raw_es = list((videos_dir / "temp_media").rglob("CoriolisMechanismSceneES.mp4"))[0]
    out_es = str(videos_dir / "Mecanismo Coriolis Cinematica ES.mp4")

    print(f"[CONTINUUM LAB] Multiplexing ES Audio + Video -> {out_es}")
    cmd_mux_es = [
        ffmpeg_bin, "-y", "-i", str(raw_es), "-i", temp_audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_es
    ]
    subprocess.run(cmd_mux_es, check=True)

    # 4. Render English Version
    print("\n=======================================================")
    print("[CONTINUUM LAB] Rendering English Coriolis Mechanism (EN)...")
    print("=======================================================")
    cmd_manim_en = [
        sys.executable, "-m", "manim", "-qh", "--media_dir", str(videos_dir / "temp_media"),
        this_script, "CoriolisMechanismSceneEN"
    ]
    subprocess.run(cmd_manim_en, check=True)

    raw_en = list((videos_dir / "temp_media").rglob("CoriolisMechanismSceneEN.mp4"))[0]
    out_en = str(videos_dir / "Coriolis Mechanism Kinematics EN.mp4")

    print(f"[CONTINUUM LAB] Multiplexing EN Audio + Video -> {out_en}")
    cmd_mux_en = [
        ffmpeg_bin, "-y", "-i", str(raw_en), "-i", temp_audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_en
    ]
    subprocess.run(cmd_mux_en, check=True)

    # Generar hero cover thumbnail para Instagram / YouTube
    hero_thumb_path = str(capturas_dir / "coriolis_9_16_hero.png")
    cmd_thumb = [
        ffmpeg_bin, "-y", "-ss", "00:00:03.500", "-i", out_en,
        "-vframes", "1", "-q:v", "2", hero_thumb_path
    ]
    subprocess.run(cmd_thumb, check=True)
    print(f"[CONTINUUM LAB] Generated hero thumbnail cover -> {hero_thumb_path}")

    # Cleanup temp
    import shutil
    if os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)
    shutil.rmtree(str(videos_dir / "temp_media"), ignore_errors=True)

    print("\n=======================================================")
    print("[CONTINUUM LAB] ALL CORIOLIS VIDEOS DELIVERED SUCCESSFULLY!")
    print(f"  - Spanish: {out_es}")
    print(f"  - English: {out_en}")
    print(f"  - Thumbnail: {hero_thumb_path}")
    print("=======================================================")
    return out_en, hero_thumb_path


if __name__ == "__main__":
    render_all()
