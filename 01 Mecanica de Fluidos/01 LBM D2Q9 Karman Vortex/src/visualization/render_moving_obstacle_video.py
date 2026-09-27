"""
Continuum Lab — Vortex-Induced Vibration (VIV) & von Kármán Vortex Street Engine
Renders 1080x1920 (9:16 TikTok) Vectorized Animation with Physical Clarity.

Improvements:
  - Frame 0 starts immediately with fully developed flowing streamlines (no abrupt pop-ins).
  - Eliminates floating confusing balls; shows true fluid streamlines curling into alternating wake vortices.
  - Explains cylinder fluctuation physically via dynamic Lift Force arrow F_L(t) (Vortex-Induced Vibration).
  - Bottom card shifted up to y = -4.3 to leave >340 px safe zone for TikTok description/UI.
  - Top card positioned at y = 5.4 leaving >220 px safe zone for search bar.
  - Friendly, soothing hydrodynamic audio with clear flowing water, gentle whooshes, and warm ambient chords.
  - Bilingual delivery (ES and EN). Zero project titles or branding in video frame.
"""

from manim import *
import numpy as np
import os
import subprocess
import sys
from pathlib import Path
import imageio_ffmpeg

# Add project directory to sys.path
project_dir = Path(__file__).resolve().parent.parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.audio.fluid_audio_synth import synthesize_fluid_audio

# Exact TikTok 9:16 Canvas Configuration
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#0a0a0c"  # Cybernetic Deep Void


def create_moving_fluid_scene(lang: str = "ES"):
    """
    Factory creating the TikTok scene class localized to Spanish or English.
    """
    class MovingFluidScene(Scene):
        def construct(self):
            # ----------------------------------------------------
            # 1. Top HUD Card (Pure Physics - Safe Zone: y in [4.6, 6.2])
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

            eq_navier = MathTex(
                r"\nabla \cdot \mathbf{u} = 0 \quad \big| \quad \frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u}\cdot\nabla)\mathbf{u} = -\nabla p + \nu \nabla^2\mathbf{u}",
                font_size=20,
                color="#ffffff"
            ).move_to(top_box.get_top() + DOWN * 0.42)

            rule_top = Line(LEFT * 3.4, RIGHT * 3.4, color="#1f2937", stroke_width=1.0).next_to(eq_navier, DOWN, buff=0.16)

            if lang == "ES":
                sub_text = MathTex(
                    r"Re = \frac{U_\infty D}{\nu} = 150 \quad \implies \quad \text{Interacci\'on Fluido-Estructura (FSI)}",
                    font_size=19,
                    color="#00f0ff"
                )
            else:
                sub_text = MathTex(
                    r"Re = \frac{U_\infty D}{\nu} = 150 \quad \implies \quad \text{Fluid-Structure Interaction (FSI)}",
                    font_size=19,
                    color="#00f0ff"
                )
            sub_text.next_to(rule_top, DOWN, buff=0.16)
            top_group = VGroup(top_box, eq_navier, rule_top, sub_text)

            # ----------------------------------------------------
            # 2. Bottom Telemetry Card (Safe Zone: y in [-5.15, -3.45])
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
                    r"\text{VIBRACI\'ON INDUCIDA POR V\'ORTICES (VIV)}",
                    font_size=19,
                    color="#ffffff"
                )
                metrics_text = MathTex(
                    r"St = \frac{f_s D}{U_\infty} = 0.183 \quad \big| \quad F_L(t) = \pm \text{Sustentaci\'on Alternada}",
                    font_size=18,
                    color="#39ff14"
                )
                callout_text = MathTex(
                    r"\text{La presi\'on asim\'etrica de los remolinos hace oscilar al cilindro}",
                    font_size=17,
                    color="#ffaa00"
                )
            else:
                telem_header = MathTex(
                    r"\text{VORTEX-INDUCED VIBRATION (VIV)}",
                    font_size=19,
                    color="#ffffff"
                )
                metrics_text = MathTex(
                    r"St = \frac{f_s D}{U_\infty} = 0.183 \quad \big| \quad F_L(t) = \pm \text{Alternating Lift Force}",
                    font_size=18,
                    color="#39ff14"
                )
                callout_text = MathTex(
                    r"\text{Asymmetric vortex low-pressure wakes drive cylinder oscillation}",
                    font_size=17,
                    color="#ffaa00"
                )

            telem_header.move_to(bottom_box.get_top() + DOWN * 0.35)
            rule_bottom = Line(LEFT * 3.4, RIGHT * 3.4, color="#1f2937", stroke_width=1.0).next_to(telem_header, DOWN, buff=0.14)
            metrics_text.next_to(rule_bottom, DOWN, buff=0.16)
            callout_text.next_to(metrics_text, DOWN, buff=0.14)

            bottom_group = VGroup(bottom_box, telem_header, rule_bottom, metrics_text, callout_text)

            # ----------------------------------------------------
            # 3. Kinematics of the Oscillating Cylinder (VIV)
            # ----------------------------------------------------
            t_val = ValueTracker(0.0)
            R_obs = 0.65
            omega_shed = 2.2  # Shedding angular frequency

            def get_obs_pos(t):
                # Harmonic transverse oscillation in response to vortex shedding
                xc = -1.2 + 0.25 * np.cos(omega_shed * t)
                yc = 0.6 + 0.95 * np.sin(omega_shed * t)
                return np.array([xc, yc, 0.0])

            def get_lift_force(t):
                # Lift force points in phase with cylinder acceleration / vortex pressure
                f_lift = 1.1 * np.cos(omega_shed * t)
                return np.array([0.0, f_lift, 0.0])

            # Cylinder body & glowing outer border
            obs_core = Circle(
                radius=R_obs,
                color="#00f0ff",
                stroke_width=3.2,
                fill_color="#12161f",
                fill_opacity=1.0
            )
            obs_inner_ring = Circle(radius=0.22, color="#00f0ff", stroke_width=1.5)
            obs_center_dot = Dot(radius=0.06, color=WHITE)
            obs_glow = Circle(radius=R_obs + 0.10, color="#00f0ff", stroke_width=1.2, stroke_opacity=0.4)

            # Dynamic Lift Force vector arrow F_L(t)
            lift_arrow = Arrow(
                start=np.array([0, 0, 0]),
                end=np.array([0, 1, 0]),
                buff=0,
                color="#39ff14",
                stroke_width=3.5,
                max_tip_length_to_length_ratio=0.28
            )

            # Lift Force label (F_L)
            fl_label = MathTex(r"\mathbf{F}_L", font_size=20, color="#39ff14")

            # Cylinder physical tag
            cyl_tag = Text("Cylinder" if lang == "EN" else "Cilindro", font_size=14, color="#94a3b8")

            def update_cylinder(mob):
                t = t_val.get_value()
                p = get_obs_pos(t)
                fl = get_lift_force(t)

                obs_core.move_to(p)
                obs_inner_ring.move_to(p)
                obs_center_dot.move_to(p)
                obs_glow.move_to(p)

                # Lift arrow
                if abs(fl[1]) > 0.1:
                    lift_arrow.put_start_and_end_on(p, p + fl * 0.85)
                    lift_arrow.set_opacity(1.0)
                    fl_label.next_to(p + fl * 0.85, RIGHT if fl[1] > 0 else LEFT, buff=0.1)
                    fl_label.set_opacity(1.0)
                else:
                    lift_arrow.set_opacity(0.0)
                    fl_label.set_opacity(0.0)

                cyl_tag.move_to(p + LEFT * (R_obs + 0.65))

            obs_core.add_updater(update_cylinder)

            # ----------------------------------------------------
            # 4. Continuous Flowing Streamlines & Vortex Sheets
            # ----------------------------------------------------
            y_base_positions = np.linspace(-2.8, 3.8, 24)
            streamlines_group = VGroup()
            for _ in y_base_positions:
                line = VMobject(stroke_width=2.2)
                streamlines_group.add(line)

            def update_streamlines(group):
                t = t_val.get_value()
                obs_p = get_obs_pos(t)
                xc, yc = obs_p[0], obs_p[1]
                x_pts = np.linspace(-4.2, 4.2, 85)

                for idx, y0 in enumerate(y_base_positions):
                    pts = []
                    # Upper or lower shear layer distinction
                    is_upper = (y0 >= yc)

                    for x in x_pts:
                        dx = x - xc
                        dy = y0 - yc
                        r2 = dx*dx + dy*dy

                        # Cylinder potential deflection
                        defl_y = 0.0
                        if r2 > 1e-4:
                            factor = (R_obs**2) / (r2 + 0.10)
                            defl_y = dy * factor

                        # Downstream von Kármán vortex rolling waves (x > xc)
                        if dx > 0.1:
                            k_wake = 1.7
                            # Exponential decay away from wake centerline
                            envelope = np.exp(-(dy**2) / 2.0) * min(1.0, dx * 0.8)
                            # Phase alternation creates the intertwining vortex street
                            phase_shift = 0.0 if is_upper else np.pi
                            wake_wave = 0.62 * np.sin(k_wake * dx - omega_shed * t + phase_shift) * envelope
                            defl_y += wake_wave

                        y_curr = y0 + defl_y
                        pts.append([x, y_curr, 0.0])

                    group[idx].set_points_smoothly(pts)

                    # Elegant chromatic gradient for shear layers
                    dist = abs(y0 - yc)
                    if dist < 0.45:
                        # Near cylinder surface: high-shear separation
                        group[idx].set_color("#fbbf24")  # Radiant amber
                    elif is_upper:
                        # Upper vortex street ribbon
                        group[idx].set_color("#00f0ff")  # Electric cyan
                    else:
                        # Lower vortex street ribbon
                        group[idx].set_color("#f43f5e")  # Electric rose/magenta

            streamlines_group.add_updater(update_streamlines)

            # ----------------------------------------------------
            # 5. Physical Wake Annotations (Vorticity Sheets)
            # ----------------------------------------------------
            vort_label_top = MathTex(
                r"\omega_z < 0 \quad (\text{Giro Horario})" if lang == "ES" else r"\omega_z < 0 \quad (\text{Clockwise Vortex})",
                font_size=15,
                color="#00f0ff"
            )
            vort_label_bot = MathTex(
                r"\omega_z > 0 \quad (\text{Antihorario})" if lang == "ES" else r"\omega_z > 0 \quad (\text{Counter-Clockwise})",
                font_size=15,
                color="#f43f5e"
            )

            def update_annotations(mob):
                t = t_val.get_value()
                obs_p = get_obs_pos(t)
                yc = obs_p[1]
                vort_label_top.move_to(np.array([1.8, yc + 1.4, 0.0]))
                vort_label_bot.move_to(np.array([1.8, yc - 1.4, 0.0]))

            vort_label_top.add_updater(update_annotations)

            # ----------------------------------------------------
            # 6. Scene Assembly & Playback (Continuous from Frame 0)
            # ----------------------------------------------------
            # Add all elements directly to start with complete active state
            self.add(top_group)
            self.add(bottom_group)
            self.add(obs_glow, obs_core, obs_inner_ring, obs_center_dot)
            self.add(lift_arrow, fl_label, cyl_tag)
            self.add(streamlines_group)
            self.add(vort_label_top, vort_label_bot)

            # Run smooth continuous animation for 18.0 seconds
            self.play(
                t_val.animate.set_value(18.0),
                run_time=18.0,
                rate_func=linear
            )
            self.wait(0.5)

    return MovingFluidScene


class MovingFluidSceneES(create_moving_fluid_scene("ES")):
    pass


class MovingFluidSceneEN(create_moving_fluid_scene("EN")):
    pass


def render_all():
    base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    renders_dir = base_dir / "RENDERS" / "1 Vortices de von Karman"
    videos_dir = renders_dir / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)

    # 1. Synthesize Friendly Hydrodynamic Audio
    temp_audio_path = str(videos_dir / "fluid_flow_friendly.wav")
    print("[CONTINUUM LAB] Synthesizing friendly hydrodynamic audio...")
    synthesize_fluid_audio(duration=18.5, fs=44100, output_path=temp_audio_path)

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    this_script = str(Path(__file__).resolve())

    # 2. Render Spanish Version
    print("\n=======================================================")
    print("[CONTINUUM LAB] Rendering Spanish Fluid Simulation (ES)...")
    print("=======================================================")
    cmd_manim_es = [
        "manim", "-qh", "--media_dir", str(videos_dir / "temp_media"),
        this_script, "MovingFluidSceneES"
    ]
    subprocess.run(cmd_manim_es, check=True)

    raw_es = list((videos_dir / "temp_media").rglob("MovingFluidSceneES.mp4"))[0]
    out_es = str(videos_dir / "Vortices de von Karman ES.mp4")

    print(f"[CONTINUUM LAB] Multiplexing ES Audio + Video -> {out_es}")
    cmd_mux_es = [
        ffmpeg_bin, "-y", "-i", str(raw_es), "-i", temp_audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_es
    ]
    subprocess.run(cmd_mux_es, check=True)

    # 3. Render English Version
    print("\n=======================================================")
    print("[CONTINUUM LAB] Rendering English Fluid Simulation (EN)...")
    print("=======================================================")
    cmd_manim_en = [
        "manim", "-qh", "--media_dir", str(videos_dir / "temp_media"),
        this_script, "MovingFluidSceneEN"
    ]
    subprocess.run(cmd_manim_en, check=True)

    raw_en = list((videos_dir / "temp_media").rglob("MovingFluidSceneEN.mp4"))[0]
    out_en = str(videos_dir / "von Karman Vortices EN.mp4")

    print(f"[CONTINUUM LAB] Multiplexing EN Audio + Video -> {out_en}")
    cmd_mux_en = [
        ffmpeg_bin, "-y", "-i", str(raw_en), "-i", temp_audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_en
    ]
    subprocess.run(cmd_mux_en, check=True)

    # Cleanup temporary files
    import shutil
    if os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)
    shutil.rmtree(str(videos_dir / "temp_media"), ignore_errors=True)

    print("\n=======================================================")
    print("[CONTINUUM LAB] ALL FLUID VIDEOS DELIVERED SUCCESSFULLY!")
    print(f"  - Spanish: {out_es}")
    print(f"  - English: {out_en}")
    print("=======================================================")


if __name__ == "__main__":
    render_all()
