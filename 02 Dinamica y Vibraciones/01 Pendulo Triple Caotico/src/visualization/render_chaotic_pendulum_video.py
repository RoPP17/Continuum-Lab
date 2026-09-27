"""
Continuum Lab — Classical Mechanics & Dynamical Systems
Vectorized Manim TikTok 9:16 Animation: Chaotic Triple Pendulum Trajectory
Elevated Aesthetics, Safe Zones, and Friendly Musical Pentatonic Audio.

Improvements:
  - Elevated visual design: high-tech polar grid, dual-layer glowing rods, mechanical pivot bearings.
  - Hypnotic multi-tone chromatic gradient comet trail for bob 3.
  - Safe zones: top card at y = 5.4 (>220 px top margin), bottom card at y = -4.3 (>340 px bottom margin).
  - Friendly musical pentatonic chimes & warm celestial pad synchronized to chaotic velocity.
  - Dual bilingual delivery (ES and EN). Zero project titles or branding in video frame.
"""

from manim import *
import numpy as np
import os
import subprocess
import sys
from pathlib import Path
import imageio_ffmpeg

# Add project root for robust imports
project_dir = Path(__file__).resolve().parent.parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.physics.triple_pendulum import TriplePendulumSimulator, TriplePendulumParams
from src.audio.pendulum_audio_synth import synthesize_pendulum_audio

# Exact TikTok 9:16 Canvas Configuration
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#0a0a0c"  # Cybernetic Deep Void

CACHE = {}


def precompute_pendulum_data(duration=18.0, fps=60):
    if "p3_arr" in CACHE:
        return CACHE

    # Scaled pendulum rod lengths for perfectly framed 9:16 swing
    params = TriplePendulumParams(l1=1.05, l2=0.88, l3=0.72, m1=1.2, m2=1.0, m3=0.8)
    sim = TriplePendulumSimulator(params)
    init_angles = (np.radians(130.0), np.radians(100.0), np.radians(70.0))
    sim.set_initial_state(init_angles)

    total_frames = int(fps * duration)
    dt_frame = 1.0 / fps
    sub_steps = 10
    dt_sub = dt_frame / sub_steps
    pivot = np.array([0.0, 1.4, 0.0])  # Elevated pivot for optimal framing

    p1_list, p2_list, p3_list = [], [], []
    v3_list, t_list = [], []

    prev_p3 = None
    for f_idx in range(total_frames):
        for _ in range(sub_steps):
            sim.step_rk4(dt_sub)
        pos1, pos2, pos3 = sim.get_cartesian_positions()
        curr_p1 = pivot + np.array([pos1[0], pos1[1], 0.0])
        curr_p2 = pivot + np.array([pos2[0], pos2[1], 0.0])
        curr_p3 = pivot + np.array([pos3[0], pos3[1], 0.0])

        p1_list.append(curr_p1)
        p2_list.append(curr_p2)
        p3_list.append(curr_p3)
        t_list.append(f_idx * dt_frame)

        if prev_p3 is not None:
            v_inst = np.linalg.norm(curr_p3 - prev_p3) / dt_frame
        else:
            v_inst = 0.0
        v3_list.append(v_inst)
        prev_p3 = curr_p3

    CACHE["p1_arr"] = np.array(p1_list)
    CACHE["p2_arr"] = np.array(p2_list)
    CACHE["p3_arr"] = np.array(p3_list)
    CACHE["v3_arr"] = np.array(v3_list)
    CACHE["t_arr"] = np.array(t_list)
    CACHE["total_frames"] = total_frames
    CACHE["duration"] = duration
    CACHE["pivot"] = pivot
    return CACHE


def create_triple_pendulum_scene(lang: str = "ES"):
    class DynamicTriplePendulumScene(Scene):
        def construct(self):
            data = precompute_pendulum_data(duration=18.0, fps=60)
            p1_arr = data["p1_arr"]
            p2_arr = data["p2_arr"]
            p3_arr = data["p3_arr"]
            total_frames = data["total_frames"]
            total_seconds = data["duration"]
            pivot = data["pivot"]

            # ----------------------------------------------------
            # 1. Subtle Precision Polar Grid (Laboratory Aesthetic)
            # ----------------------------------------------------
            grid_group = VGroup()
            for r in [0.9, 1.8, 2.65]:
                grid_circle = Circle(radius=r, color="#1e293b", stroke_width=1.0, stroke_opacity=0.35).move_to(pivot)
                grid_group.add(grid_circle)
            axis_h = Line(pivot + LEFT * 2.8, pivot + RIGHT * 2.8, color="#1e293b", stroke_width=0.8, stroke_opacity=0.25)
            axis_v = Line(pivot + DOWN * 2.8, pivot + UP * 0.8, color="#1e293b", stroke_width=0.8, stroke_opacity=0.25)
            grid_group.add(axis_h, axis_v)

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

            eq_lagrange = MathTex(
                r"\mathcal{L} = T - V \quad \big| \quad \frac{d}{dt}\left(\frac{\partial \mathcal{L}}{\partial \dot{\theta}_k}\right) - \frac{\partial \mathcal{L}}{\partial \theta_k} = 0",
                font_size=20,
                color="#ffffff"
            ).move_to(top_box.get_top() + DOWN * 0.42)

            rule_top = Line(LEFT * 3.4, RIGHT * 3.4, color="#1f2937", stroke_width=1.0).next_to(eq_lagrange, DOWN, buff=0.16)

            if lang == "ES":
                sub_top = MathTex(
                    r"\text{Sistemas Din\'amicos No Lineales } \implies \text{Caos Determinista } (\lambda > 0)",
                    font_size=19,
                    color="#00f0ff"
                )
            else:
                sub_top = MathTex(
                    r"\text{Nonlinear Dynamical Systems } \implies \text{Deterministic Chaos } (\lambda > 0)",
                    font_size=19,
                    color="#00f0ff"
                )
            sub_top.next_to(rule_top, DOWN, buff=0.16)
            top_group = VGroup(top_box, eq_lagrange, rule_top, sub_top)

            # ----------------------------------------------------
            # 3. Bottom Telemetry Card (Safe Zone: y in [-5.15, -3.45])
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
                    r"\text{CONSERVACI\'ON DE ENERG\'IA HAMILTONIANA}",
                    font_size=19,
                    color="#ffffff"
                )
                energy_text = MathTex(
                    r"E = T + V = \text{const} \quad \big| \quad \frac{\Delta E}{E_0} < 10^{-5} \quad \big| \quad 3 \text{ Grados de Libertad}",
                    font_size=18,
                    color="#39ff14"
                )
                desc_text = MathTex(
                    r"\text{Trayectoria Fractal del Extremo } (x_3, y_3) \text{ en el Espacio Real}",
                    font_size=17,
                    color="#ffaa00"
                )
            else:
                telem_header = MathTex(
                    r"\text{HAMILTONIAN ENERGY CONSERVATION}",
                    font_size=19,
                    color="#ffffff"
                )
                energy_text = MathTex(
                    r"E = T + V = \text{const} \quad \big| \quad \frac{\Delta E}{E_0} < 10^{-5} \quad \big| \quad 3 \text{ Degrees of Freedom}",
                    font_size=18,
                    color="#39ff14"
                )
                desc_text = MathTex(
                    r"\text{Fractal Trajectory of Tip } (x_3, y_3) \text{ in Real Configuration Space}",
                    font_size=17,
                    color="#ffaa00"
                )

            telem_header.move_to(bottom_box.get_top() + DOWN * 0.35)
            rule_bottom = Line(LEFT * 3.4, RIGHT * 3.4, color="#1f2937", stroke_width=1.0).next_to(telem_header, DOWN, buff=0.14)
            energy_text.next_to(rule_bottom, DOWN, buff=0.16)
            desc_text.next_to(energy_text, DOWN, buff=0.14)

            bottom_group = VGroup(bottom_box, telem_header, rule_bottom, energy_text, desc_text)

            # ----------------------------------------------------
            # 4. Elevated Mechanical Pendulum Elements
            # ----------------------------------------------------
            # High-tech Pivot assembly
            pivot_glow = Circle(radius=0.28, color="#00f0ff", stroke_width=1.5, stroke_opacity=0.4).move_to(pivot)
            pivot_ring = Circle(radius=0.18, color="#00f0ff", stroke_width=2.5).move_to(pivot)
            pivot_dot = Dot(point=pivot, radius=0.08, color=WHITE)

            # Dual-layer glowing rods (outer glow + inner core)
            rod1_glow = Line(pivot, p1_arr[0], color="#00f0ff", stroke_width=6.0, stroke_opacity=0.6)
            rod1_core = Line(pivot, p1_arr[0], color=WHITE, stroke_width=2.0)

            rod2_glow = Line(p1_arr[0], p2_arr[0], color="#a855f7", stroke_width=5.5, stroke_opacity=0.6)
            rod2_core = Line(p1_arr[0], p2_arr[0], color=WHITE, stroke_width=1.8)

            rod3_glow = Line(p2_arr[0], p3_arr[0], color="#ff007f", stroke_width=5.0, stroke_opacity=0.6)
            rod3_core = Line(p2_arr[0], p3_arr[0], color=WHITE, stroke_width=1.6)

            # Dynamic Bobs with glowing halos
            bob1_halo = Circle(radius=0.20, color="#00f0ff", stroke_width=1.5, stroke_opacity=0.4).move_to(p1_arr[0])
            bob1 = Dot(p1_arr[0], radius=0.13, color="#00f0ff")

            bob2_halo = Circle(radius=0.18, color="#a855f7", stroke_width=1.5, stroke_opacity=0.4).move_to(p2_arr[0])
            bob2 = Dot(p2_arr[0], radius=0.12, color="#a855f7")

            bob3_halo = Circle(radius=0.24, color="#ff007f", stroke_width=2.0, stroke_opacity=0.7).move_to(p3_arr[0])
            bob3 = Dot(p3_arr[0], radius=0.11, color=WHITE)

            # Hypnotic Chromatic Trajectory Comet Ribbon (Bob 3)
            trail = VMobject(stroke_width=2.6)
            trail.set_points_as_corners([p3_arr[0], p3_arr[0] + np.array([0.001, 0, 0])])
            trail.set_color_by_gradient("#00f0ff", "#38bdf8", "#a855f7", "#ec4899", "#f59e0b")

            frame_idx = ValueTracker(0)

            def update_pendulum(mob):
                idx = int(frame_idx.get_value())
                if idx >= total_frames:
                    idx = total_frames - 1
                pos1 = p1_arr[idx]
                pos2 = p2_arr[idx]
                pos3 = p3_arr[idx]

                rod1_glow.put_start_and_end_on(pivot, pos1)
                rod1_core.put_start_and_end_on(pivot, pos1)

                rod2_glow.put_start_and_end_on(pos1, pos2)
                rod2_core.put_start_and_end_on(pos1, pos2)

                rod3_glow.put_start_and_end_on(pos2, pos3)
                rod3_core.put_start_and_end_on(pos2, pos3)

                bob1_halo.move_to(pos1)
                bob1.move_to(pos1)

                bob2_halo.move_to(pos2)
                bob2.move_to(pos2)

                bob3_halo.move_to(pos3)
                bob3.move_to(pos3)

            def update_trail(mob):
                idx = int(frame_idx.get_value())
                if idx > 1:
                    idx_end = min(idx + 1, total_frames)
                    mob.set_points_smoothly(p3_arr[:idx_end])
                    mob.set_color_by_gradient("#00f0ff", "#38bdf8", "#a855f7", "#ec4899", "#f59e0b")

            # ----------------------------------------------------
            # 5. Scene Assembly & Playback (Continuous from Frame 0)
            # ----------------------------------------------------
            self.add(grid_group)
            self.add(top_group)
            self.add(bottom_group)

            self.add(pivot_glow, pivot_ring, pivot_dot)
            self.add(rod1_glow, rod1_core)
            self.add(rod2_glow, rod2_core)
            self.add(rod3_glow, rod3_core)
            self.add(bob1_halo, bob1)
            self.add(bob2_halo, bob2)
            self.add(bob3_halo, bob3)

            rod1_glow.add_updater(update_pendulum)
            trail.add_updater(update_trail)
            self.add(trail)

            # Play Chaotic Trajectory for 18.0 seconds
            self.play(
                frame_idx.animate.set_value(total_frames - 1),
                run_time=total_seconds,
                rate_func=linear
            )
            self.wait(0.5)

    return DynamicTriplePendulumScene


class TriplePendulumSceneES(create_triple_pendulum_scene("ES")):
    pass


class TriplePendulumSceneEN(create_triple_pendulum_scene("EN")):
    pass


def render_all():
    base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    renders_dir = base_dir / "RENDERS" / "2 Pendulo Triple Trayectoria Caotica"
    videos_dir = renders_dir / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)

    # 1. Precompute and Synthesize Friendly Musical Audio
    data = precompute_pendulum_data(duration=18.0, fps=60)
    temp_audio_path = str(videos_dir / "pendulum_musical_synth.wav")
    print("[CONTINUUM LAB] Synthesizing friendly musical chaotic audio...")
    synthesize_pendulum_audio(
        time_points=data["t_arr"],
        p3_trajectory=data["p3_arr"],
        velocities=data["v3_arr"],
        duration=18.5,
        fs=44100,
        output_path=temp_audio_path
    )

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    this_script = str(Path(__file__).resolve())

    # 2. Render Spanish Version
    print("\n=======================================================")
    print("[CONTINUUM LAB] Rendering Spanish Triple Pendulum (ES)...")
    print("=======================================================")
    cmd_manim_es = [
        "manim", "-qh", "--media_dir", str(videos_dir / "temp_media"),
        this_script, "TriplePendulumSceneES"
    ]
    subprocess.run(cmd_manim_es, check=True)

    raw_es = list((videos_dir / "temp_media").rglob("TriplePendulumSceneES.mp4"))[0]
    out_es = str(videos_dir / "Pendulo Triple Caotico ES.mp4")

    print(f"[CONTINUUM LAB] Multiplexing ES Audio + Video -> {out_es}")
    cmd_mux_es = [
        ffmpeg_bin, "-y", "-i", str(raw_es), "-i", temp_audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_es
    ]
    subprocess.run(cmd_mux_es, check=True)

    # 3. Render English Version
    print("\n=======================================================")
    print("[CONTINUUM LAB] Rendering English Triple Pendulum (EN)...")
    print("=======================================================")
    cmd_manim_en = [
        "manim", "-qh", "--media_dir", str(videos_dir / "temp_media"),
        this_script, "TriplePendulumSceneEN"
    ]
    subprocess.run(cmd_manim_en, check=True)

    raw_en = list((videos_dir / "temp_media").rglob("TriplePendulumSceneEN.mp4"))[0]
    out_en = str(videos_dir / "Chaotic Triple Pendulum EN.mp4")

    print(f"[CONTINUUM LAB] Multiplexing EN Audio + Video -> {out_en}")
    cmd_mux_en = [
        ffmpeg_bin, "-y", "-i", str(raw_en), "-i", temp_audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_en
    ]
    subprocess.run(cmd_mux_en, check=True)

    # Cleanup temp
    import shutil
    if os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)
    shutil.rmtree(str(videos_dir / "temp_media"), ignore_errors=True)

    print("\n=======================================================")
    print("[CONTINUUM LAB] ALL PENDULUM VIDEOS DELIVERED SUCCESSFULLY!")
    print(f"  - Spanish: {out_es}")
    print(f"  - English: {out_en}")
    print("=======================================================")


if __name__ == "__main__":
    render_all()
