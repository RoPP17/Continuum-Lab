"""
Continuum Lab — Mathematical Physics & Complex Geometry
Vectorized Manim TikTok 9:16 Animation: Euler's Identity 3D Complex Helix & Canonical Projections.

Visual Architecture & Enhancements:
  - Perfect Viewport Centering:
      The 3D coordinate system and curves are centered at (0, 0.48, 0)
      spanning symmetrically horizontally from -3.1 to +3.1.
      All camera orientations (3D, XY, XZ, YZ) keep the curve dead-center.
  - Flawless LaTeX compilation of all signs, accents, and symbols using MathTex.
  - Extended Climax Duration:
      The Euler's Identity banner ("La fórmula más hermosa de todas las matemáticas")
      remains on screen for >8.5 seconds with a majestic ambient 3D orbit.
  - 3D Coordinate Space:
      X-axis: Parameter / Angle theta (0 <= theta <= 3*pi)
      Y-axis: Real Component Re(e^{i theta}) = cos(theta)
      Z-axis: Imaginary Component Im(e^{i theta}) = sin(theta)
  - Simultaneous 3D & 2D Drawing in the same zone:
      * 3D Helix: r(theta) = (theta, cos(theta), sin(theta)) in glowing neon magenta/violet.
      * XY Projection (Floor): (theta, cos(theta), 0) in electric cyan -> Pure Cosine Wave.
      * XZ Projection (Wall): (theta, 0, sin(theta)) in golden amber -> Pure Sine Wave.
      * Orthogonal drop-lines dynamically connecting the 3D tip to both projections.
  - Individual 2D Visualizations via Camera Orthogonal Projections:
      1. XY View (Top, phi=0, theta=-90 deg): Helix collapses into 2D Cosine wave.
      2. XZ View (Side, phi=90 deg, theta=-90 deg): Helix collapses into 2D Sine wave.
      3. YZ View (Axial, phi=90 deg, theta=0 deg): Helix collapses into Complex Unit Circle.
  - Climax:
      Euler's Identity at theta = pi: e^{i*pi} = -1 ==> e^{i*pi} + 1 = 0.
  - Safe zones: Top HUD card at y = 5.4 (>220 px margin), Bottom card at y = -4.3 (>340 px margin).
  - Bilingual delivery: Spanish (ES) and English (EN).
"""

from manim import *
import numpy as np
import os
import subprocess
import sys
from pathlib import Path
import imageio_ffmpeg

# Add project root for module imports
project_dir = Path(__file__).resolve().parent.parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.math.euler_math import EulerHelixAnalysis
from src.audio.euler_music_synth import synthesize_euler_background_music

# Exact TikTok 9:16 Canvas Configuration
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#07070b"  # Deep Cyber Void


def create_euler_3d_scene(lang: str = "ES"):
    class EulerIdentity3DScene(ThreeDScene):
        def construct(self):
            # Target center of viewport between top card (y=5.4) and bottom card (y=-4.3)
            center_v = UP * 0.48

            # ----------------------------------------------------
            # 1. Top HUD Card (Fixed in Screen Frame)
            # Safe zone: y in [4.6, 6.2], leaves >220 px top margin
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

            eq_euler = MathTex(
                r"e^{i\theta} = \cos(\theta) + i\sin(\theta) \quad \Big| \quad e^{i\pi} + 1 = 0",
                font_size=20,
                color="#ffffff"
            ).move_to(top_box.get_top() + DOWN * 0.42)

            rule_top = Line(LEFT * 3.4, RIGHT * 3.4, color="#1f2937", stroke_width=1.0).next_to(eq_euler, DOWN, buff=0.16)

            if lang == "ES":
                sub_top = MathTex(
                    r"\text{ESPACIO COMPLEJO 3D // ESPIRAL Y PROYECCIONES CAN\'ONICAS}",
                    font_size=17,
                    color="#00f0ff"
                )
            else:
                sub_top = MathTex(
                    r"\text{3D COMPLEX SPACE // HELIX AND CANONICAL PROJECTIONS}",
                    font_size=17,
                    color="#00f0ff"
                )
            sub_top.next_to(rule_top, DOWN, buff=0.16)
            top_group = VGroup(top_box, eq_euler, rule_top, sub_top)
            self.add_fixed_in_frame_mobjects(top_group)

            # ----------------------------------------------------
            # 2. Bottom Telemetry Card (Fixed in Screen Frame)
            # Safe zone: y in [-5.15, -3.45], leaves >340 px bottom margin
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
                    r"\text{DESCOMPOSICI\'ON ORTOGONAL DE LA ONDA COMPLEJA}",
                    font_size=18,
                    color="#ffffff"
                )
            else:
                telem_header = MathTex(
                    r"\text{ORTHOGONAL DECOMPOSITION OF THE COMPLEX WAVE}",
                    font_size=18,
                    color="#ffffff"
                )
            telem_header.move_to(bottom_box.get_top() + DOWN * 0.38)

            rule_bot = Line(LEFT * 3.4, RIGHT * 3.4, color="#1f2937", stroke_width=1.0).next_to(telem_header, DOWN, buff=0.14)

            # Telemetry readout using MathTex for 100% vector precision & proper symbols
            if lang == "ES":
                mode_text = MathTex(
                    r"\text{MODO: PERSPECTIVA 3D -- ESPIRAL HELICOIDAL COMPLEJA}",
                    font_size=14,
                    color="#ff007f"
                )
                legend_text = MathTex(
                    r"\text{Espiral 3D: } e^{i\theta} \quad|\quad \text{Plano XY: } \cos(\theta) \quad|\quad \text{Plano XZ: } \sin(\theta)",
                    font_size=14,
                    color="#94a3b8"
                )
            else:
                mode_text = MathTex(
                    r"\text{MODE: 3D PERSPECTIVE -- COMPLEX HELICAL SPIRAL}",
                    font_size=14,
                    color="#ff007f"
                )
                legend_text = MathTex(
                    r"\text{3D Helix: } e^{i\theta} \quad|\quad \text{XY Plane: } \cos(\theta) \quad|\quad \text{XZ Plane: } \sin(\theta)",
                    font_size=14,
                    color="#94a3b8"
                )

            mode_text.next_to(rule_bot, DOWN, buff=0.14)
            legend_text.next_to(mode_text, DOWN, buff=0.14)

            bottom_group = VGroup(bottom_box, telem_header, rule_bot, mode_text, legend_text)
            self.add_fixed_in_frame_mobjects(bottom_group)

            # ----------------------------------------------------
            # 3. Centered 3D Coordinate System Setup
            # ----------------------------------------------------
            # Set initial camera orientation focused directly on center_v
            self.set_camera_orientation(phi=68 * DEGREES, theta=-42 * DEGREES, frame_center=center_v)

            # Axes parameters:
            # x: theta in [0, 3*pi] (~9.42 rad)
            # y: Re in [-1.6, 1.6]
            # z: Im in [-1.6, 1.6]
            axes = ThreeDAxes(
                x_range=[0, 3.0 * np.pi, np.pi],
                y_range=[-1.6, 1.6, 1.0],
                z_range=[-1.6, 1.6, 1.0],
                x_length=6.2,
                y_length=2.6,
                z_length=2.6,
                axis_config={"color": "#475569", "stroke_width": 1.8},
            )
            # Calculate midpoint of curve (at theta = 1.5*pi) and shift axes so that
            # mid_point lands EXACTLY at center_v (dead center horizontally and vertically)
            mid_point = axes.c2p(1.5 * np.pi, 0, 0)
            axes.shift(-mid_point + center_v)

            # Labels for axes
            if lang == "ES":
                lbl_x = MathTex(r"\theta \text{ (\'Angulo)}", font_size=16, color="#ffffff")
                lbl_y = MathTex(r"\text{Re}(e^{i\theta})", font_size=16, color="#00f0ff")
                lbl_z = MathTex(r"\text{Im}(e^{i\theta})", font_size=16, color="#ffb703")
            else:
                lbl_x = MathTex(r"\theta \text{ (Angle)}", font_size=16, color="#ffffff")
                lbl_y = MathTex(r"\text{Re}(e^{i\theta})", font_size=16, color="#00f0ff")
                lbl_z = MathTex(r"\text{Im}(e^{i\theta})", font_size=16, color="#ffb703")

            lbl_x.next_to(axes.c2p(3.0 * np.pi, 0, 0), RIGHT * 0.4 + UP * 0.2, buff=0.1)
            lbl_y.next_to(axes.c2p(0, 1.6, 0), UP * 0.25 + LEFT * 0.15, buff=0.1)
            lbl_z.next_to(axes.c2p(0, 0, 1.6), OUT * 0.2 + UP * 0.25, buff=0.1)

            # ----------------------------------------------------
            # 4. Perfectly Centered Coordinate Projection Sheets
            # ----------------------------------------------------
            # XY Plane (Floor / Real plane): z = 0, spanning from theta=0 to 3*pi
            p_xy_c00 = axes.c2p(0, -1.5, 0)
            p_xy_c10 = axes.c2p(3.0 * np.pi, -1.5, 0)
            p_xy_c11 = axes.c2p(3.0 * np.pi, 1.5, 0)
            p_xy_c01 = axes.c2p(0, 1.5, 0)

            xy_floor = Polygon(
                p_xy_c00, p_xy_c10, p_xy_c11, p_xy_c01,
                fill_color="#00f0ff",
                fill_opacity=0.08,
                stroke_color="#00f0ff",
                stroke_width=0.8,
                stroke_opacity=0.35
            )

            # XZ Plane (Wall / Imaginary plane): y = 0, spanning from theta=0 to 3*pi
            p_xz_c00 = axes.c2p(0, 0, -1.5)
            p_xz_c10 = axes.c2p(3.0 * np.pi, 0, -1.5)
            p_xz_c11 = axes.c2p(3.0 * np.pi, 0, 1.5)
            p_xz_c01 = axes.c2p(0, 0, 1.5)

            xz_wall = Polygon(
                p_xz_c00, p_xz_c10, p_xz_c11, p_xz_c01,
                fill_color="#ffb703",
                fill_opacity=0.08,
                stroke_color="#ffb703",
                stroke_width=0.8,
                stroke_opacity=0.35
            )

            # Intro animation: build axes and reference projection sheets
            self.play(
                Create(axes),
                FadeIn(xy_floor),
                FadeIn(xz_wall),
                Write(lbl_x),
                Write(lbl_y),
                Write(lbl_z),
                run_time=2.0
            )
            self.wait(0.5)

            # ----------------------------------------------------
            # 5. Dynamic 3D Helix & Simultaneous Projections Drawing
            # ----------------------------------------------------
            theta_tracker = ValueTracker(0.001)

            # Dynamic 3D Helix Curve
            helix_curve = always_redraw(
                lambda: ParametricFunction(
                    lambda t: axes.c2p(t, np.cos(t), np.sin(t)),
                    t_range=[0.0, max(0.001, theta_tracker.get_value())],
                    color="#ff007f",
                    stroke_width=4.5
                ).set_shade_in_3d(True)
            )

            # Dynamic XY Projection (Cosine Wave on the Floor)
            proj_xy_curve = always_redraw(
                lambda: ParametricFunction(
                    lambda t: axes.c2p(t, np.cos(t), 0.0),
                    t_range=[0.0, max(0.001, theta_tracker.get_value())],
                    color="#00f0ff",
                    stroke_width=3.6
                )
            )

            # Dynamic XZ Projection (Sine Wave on the Wall)
            proj_xz_curve = always_redraw(
                lambda: ParametricFunction(
                    lambda t: axes.c2p(t, 0.0, np.sin(t)),
                    t_range=[0.0, max(0.001, theta_tracker.get_value())],
                    color="#ffb703",
                    stroke_width=3.6
                )
            )

            # Rotating 3D Phasor line from central axis (t, 0, 0) to helix tip (t, cos t, sin t)
            phasor_line = always_redraw(
                lambda: Line(
                    axes.c2p(theta_tracker.get_value(), 0, 0),
                    axes.c2p(theta_tracker.get_value(), np.cos(theta_tracker.get_value()), np.sin(theta_tracker.get_value())),
                    color="#ffffff",
                    stroke_width=2.5
                )
            )

            # Helix Tip Dot in 3D
            helix_tip = always_redraw(
                lambda: Dot3D(
                    point=axes.c2p(theta_tracker.get_value(), np.cos(theta_tracker.get_value()), np.sin(theta_tracker.get_value())),
                    radius=0.08,
                    color="#ffffff"
                )
            )

            # Drop line to XY projection (Floor)
            drop_to_xy = always_redraw(
                lambda: DashedLine(
                    axes.c2p(theta_tracker.get_value(), np.cos(theta_tracker.get_value()), np.sin(theta_tracker.get_value())),
                    axes.c2p(theta_tracker.get_value(), np.cos(theta_tracker.get_value()), 0),
                    color="#00f0ff",
                    stroke_width=1.8,
                    dash_length=0.08
                )
            )

            # Drop line to XZ projection (Wall)
            drop_to_xz = always_redraw(
                lambda: DashedLine(
                    axes.c2p(theta_tracker.get_value(), np.cos(theta_tracker.get_value()), np.sin(theta_tracker.get_value())),
                    axes.c2p(theta_tracker.get_value(), 0, np.sin(theta_tracker.get_value())),
                    color="#ffb703",
                    stroke_width=1.8,
                    dash_length=0.08
                )
            )

            # Add dynamic elements to scene
            self.add(
                helix_curve, proj_xy_curve, proj_xz_curve,
                phasor_line, helix_tip, drop_to_xy, drop_to_xz
            )

            # Draw the spiral across 3 full cycles (0 to 3*pi)
            self.play(
                theta_tracker.animate.set_value(3.0 * np.pi),
                run_time=6.5,
                rate_func=linear
            )
            self.wait(0.8)

            # Replace dynamic curves with static versions for optimal rendering during camera moves
            static_helix = ParametricFunction(
                lambda t: axes.c2p(t, np.cos(t), np.sin(t)),
                t_range=[0.0, 3.0 * np.pi],
                color="#ff007f",
                stroke_width=4.5
            ).set_shade_in_3d(True)

            static_proj_xy = ParametricFunction(
                lambda t: axes.c2p(t, np.cos(t), 0.0),
                t_range=[0.0, 3.0 * np.pi],
                color="#00f0ff",
                stroke_width=3.6
            )

            static_proj_xz = ParametricFunction(
                lambda t: axes.c2p(t, 0.0, np.sin(t)),
                t_range=[0.0, 3.0 * np.pi],
                color="#ffb703",
                stroke_width=3.6
            )

            self.remove(helix_curve, proj_xy_curve, proj_xz_curve, drop_to_xy, drop_to_xz, phasor_line, helix_tip)
            self.add(static_helix, static_proj_xy, static_proj_xz)

            # ----------------------------------------------------
            # 6. Act 3: Individual 2D Visualizations via Camera Rotations
            # ----------------------------------------------------
            # VIEW 1: XY Plane (Cosine Wave) - Perfectly Centered
            # Camera aligns looking down the Z axis (phi=0, theta=-90 deg)
            if lang == "ES":
                new_mode_xy = MathTex(
                    r"\text{VISTA 2D: PLANO REAL XY } \longrightarrow \cos(\theta)",
                    font_size=15,
                    color="#00f0ff"
                ).move_to(mode_text.get_center())
            else:
                new_mode_xy = MathTex(
                    r"\text{2D VIEW: REAL XY PLANE } \longrightarrow \cos(\theta)",
                    font_size=15,
                    color="#00f0ff"
                ).move_to(mode_text.get_center())

            self.play(
                Transform(mode_text, new_mode_xy),
                run_time=0.6
            )

            self.move_camera(
                phi=0.0 * DEGREES,
                theta=-90.0 * DEGREES,
                frame_center=center_v,
                run_time=2.2
            )
            self.wait(1.8)

            # VIEW 2: XZ Plane (Sine Wave) - Perfectly Centered
            # Camera aligns looking along Y axis (phi=90 deg, theta=-90 deg)
            if lang == "ES":
                new_mode_xz = MathTex(
                    r"\text{VISTA 2D: PLANO IMAGINARIO XZ } \longrightarrow \sin(\theta)",
                    font_size=15,
                    color="#ffb703"
                ).move_to(mode_text.get_center())
            else:
                new_mode_xz = MathTex(
                    r"\text{2D VIEW: IMAGINARY XZ PLANE } \longrightarrow \sin(\theta)",
                    font_size=15,
                    color="#ffb703"
                ).move_to(mode_text.get_center())

            self.play(
                Transform(mode_text, new_mode_xz),
                run_time=0.6
            )

            self.move_camera(
                phi=90.0 * DEGREES,
                theta=-90.0 * DEGREES,
                frame_center=center_v,
                run_time=2.2
            )
            self.wait(1.8)

            # VIEW 3: YZ Complex Plane (Unit Circle) - Perfectly Centered
            # Camera looks straight down X axis (phi=90 deg, theta=0 deg)
            if lang == "ES":
                new_mode_yz = MathTex(
                    r"\text{VISTA 2D: PLANO COMPLEJO } \mathbb{C} \longrightarrow |z| = 1",
                    font_size=15,
                    color="#a855f7"
                ).move_to(mode_text.get_center())
            else:
                new_mode_yz = MathTex(
                    r"\text{2D VIEW: COMPLEX PLANE } \mathbb{C} \longrightarrow |z| = 1",
                    font_size=15,
                    color="#a855f7"
                ).move_to(mode_text.get_center())

            self.play(
                Transform(mode_text, new_mode_yz),
                run_time=0.6
            )

            self.move_camera(
                phi=90.0 * DEGREES,
                theta=0.0 * DEGREES,
                frame_center=center_v,
                run_time=2.0
            )
            self.wait(1.6)

            # ----------------------------------------------------
            # 7. Act 4: Return to 3D Orbit & Euler's Identity at theta = pi
            # EXTENDED SCENE: >8.5 SECONDS WITH MAJESTIC 3D ORBIT
            # ----------------------------------------------------
            if lang == "ES":
                new_mode_euler = MathTex(
                    r"\text{CL\'IMAX: IDENTIDAD DE EULER EN } \theta = \pi",
                    font_size=15,
                    color="#ffd700"
                ).move_to(mode_text.get_center())
            else:
                new_mode_euler = MathTex(
                    r"\text{CLIMAX: EULER\'S IDENTITY AT } \theta = \pi",
                    font_size=15,
                    color="#ffd700"
                ).move_to(mode_text.get_center())

            self.play(
                Transform(mode_text, new_mode_euler),
                run_time=0.6
            )

            self.move_camera(
                phi=65.0 * DEGREES,
                theta=-45.0 * DEGREES,
                frame_center=center_v,
                run_time=2.2
            )

            # Landmark Point at theta = pi
            # r(pi) = (pi, cos(pi), sin(pi)) = (pi, -1, 0)
            pt_euler_3d = axes.c2p(np.pi, -1.0, 0.0)

            euler_marker = Dot3D(point=pt_euler_3d, radius=0.15, color="#ffd700")
            euler_ring = Circle(radius=0.38, color="#ffd700", stroke_width=2.8).move_to(pt_euler_3d)

            # Golden Callout Banner in 3D Viewport Space (Clean, Centered, Perfectly Formatted)
            if lang == "ES":
                euler_formula = MathTex(
                    r"\mathbf{e^{i\pi} + 1 = 0}",
                    font_size=28,
                    color="#ffd700"
                )
                euler_title = MathTex(
                    r"\text{La f\'ormula m\'as hermosa de todas las matem\'aticas}",
                    font_size=15,
                    color="#ffffff"
                )
                euler_sub = MathTex(
                    r"\text{Uniendo las 5 constantes cardinales: } e, \, i, \, \pi, \, 1, \, 0",
                    font_size=13,
                    color="#00f0ff"
                )
            else:
                euler_formula = MathTex(
                    r"\mathbf{e^{i\pi} + 1 = 0}",
                    font_size=28,
                    color="#ffd700"
                )
                euler_title = MathTex(
                    r"\text{The Most Beautiful Equation in All of Mathematics}",
                    font_size=15,
                    color="#ffffff"
                )
                euler_sub = MathTex(
                    r"\text{Uniting the 5 fundamental constants: } e, \, i, \, \pi, \, 1, \, 0",
                    font_size=13,
                    color="#00f0ff"
                )

            euler_callout_box = RoundedRectangle(
                corner_radius=0.14,
                width=7.4,
                height=1.55,
                color="#ffd700",
                fill_color="#0b0f19",
                fill_opacity=0.94,
                stroke_width=1.6
            )
            euler_formula.move_to(euler_callout_box.get_top() + DOWN * 0.40)
            euler_title.next_to(euler_formula, DOWN, buff=0.12)
            euler_sub.next_to(euler_title, DOWN, buff=0.10)
            euler_banner_group = VGroup(euler_callout_box, euler_formula, euler_title, euler_sub).move_to(UP * 3.1)

            self.add_fixed_in_frame_mobjects(euler_banner_group)

            self.play(
                FadeIn(euler_marker),
                Create(euler_ring),
                FadeIn(euler_banner_group, shift=DOWN * 0.2),
                run_time=1.5
            )

            # EXTENDED AMBIENT ROTATION: 8.5 seconds of smooth 3D contemplation
            self.begin_ambient_camera_rotation(rate=0.12)
            self.wait(8.5)
            self.stop_ambient_camera_rotation()

            # Final fade out
            self.play(
                FadeOut(top_group),
                FadeOut(bottom_group),
                FadeOut(euler_banner_group),
                FadeOut(axes),
                FadeOut(static_helix),
                FadeOut(static_proj_xy),
                FadeOut(static_proj_xz),
                FadeOut(xy_floor),
                FadeOut(xz_wall),
                FadeOut(lbl_x),
                FadeOut(lbl_y),
                FadeOut(lbl_z),
                FadeOut(euler_marker),
                FadeOut(euler_ring),
                run_time=1.5
            )
            self.wait(0.5)

    return EulerIdentity3DScene


class EulerIdentity3DSceneES(create_euler_3d_scene(lang="ES")):
    pass


class EulerIdentity3DSceneEN(create_euler_3d_scene(lang="EN")):
    pass


def render_all():
    """
    Renders both Spanish and English versions in high resolution (1080x1920 @ 60 FPS),
    synthesizes bespoke lo-fi science music, multiplexes audio and video,
    and extracts high-resolution hero captures into the RENDERS directory.
    """
    workspace_root = project_dir.parent.parent
    renders_dir = workspace_root / "RENDERS" / "4 Identidad de Euler 3D"
    videos_dir = renders_dir / "videos"
    captures_dir = renders_dir / "extra" / "capturas"

    os.makedirs(videos_dir, exist_ok=True)
    os.makedirs(captures_dir, exist_ok=True)

    this_script = str(Path(__file__).resolve())
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

    # 1. Synthesize Extended Soundtrack (~43 seconds to match the extended climax)
    temp_audio_path = str(videos_dir / "temp_euler_lofi.wav")
    print("\n=======================================================")
    print("[CONTINUUM LAB] Synthesizing Bespoke Ambient Lo-Fi Track (43s)...")
    print("=======================================================")
    synthesize_euler_background_music(duration=43.0, output_path=temp_audio_path)

    # 2. Render Spanish Scene
    print("\n=======================================================")
    print("[CONTINUUM LAB] Rendering Spanish 3D Euler Video (ES)...")
    print("=======================================================")
    cmd_manim_es = [
        "manim", "-qh", "--media_dir", str(videos_dir / "temp_media"),
        this_script, "EulerIdentity3DSceneES"
    ]
    subprocess.run(cmd_manim_es, check=True)

    raw_es = list((videos_dir / "temp_media").rglob("EulerIdentity3DSceneES.mp4"))[0]
    out_es = str(videos_dir / "Identidad de Euler 3D ES.mp4")

    print(f"[CONTINUUM LAB] Multiplexing ES Audio + Video -> {out_es}")
    cmd_mux_es = [
        ffmpeg_bin, "-y", "-i", str(raw_es), "-i", temp_audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_es
    ]
    subprocess.run(cmd_mux_es, check=True)

    # 3. Render English Scene
    print("\n=======================================================")
    print("[CONTINUUM LAB] Rendering English 3D Euler Video (EN)...")
    print("=======================================================")
    cmd_manim_en = [
        "manim", "-qh", "--media_dir", str(videos_dir / "temp_media"),
        this_script, "EulerIdentity3DSceneEN"
    ]
    subprocess.run(cmd_manim_en, check=True)

    raw_en = list((videos_dir / "temp_media").rglob("EulerIdentity3DSceneEN.mp4"))[0]
    out_en = str(videos_dir / "Euler Identity 3D EN.mp4")

    print(f"[CONTINUUM LAB] Multiplexing EN Audio + Video -> {out_en}")
    cmd_mux_en = [
        ffmpeg_bin, "-y", "-i", str(raw_en), "-i", temp_audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_en
    ]
    subprocess.run(cmd_mux_en, check=True)

    # 4. Extract HD hero captures
    hero_png = str(captures_dir / "euler_3d_hero.png")
    proj_cos_png = str(captures_dir / "euler_3d_projections.png")
    proj_sin_png = str(captures_dir / "euler_3d_sine.png")

    # Snapshot at 30.0s (Euler Identity Climax in 3D during ambient orbit)
    cmd_snap1 = [ffmpeg_bin, "-y", "-ss", "00:00:30.00", "-i", out_es, "-vframes", "1", hero_png]
    subprocess.run(cmd_snap1, check=True)

    # Snapshot at 12.5s (2D Cosine Projection)
    cmd_snap2 = [ffmpeg_bin, "-y", "-ss", "00:00:12.50", "-i", out_es, "-vframes", "1", proj_cos_png]
    subprocess.run(cmd_snap2, check=True)

    # Snapshot at 17.0s (2D Sine Projection)
    cmd_snap3 = [ffmpeg_bin, "-y", "-ss", "00:00:17.00", "-i", out_es, "-vframes", "1", proj_sin_png]
    subprocess.run(cmd_snap3, check=True)

    print(f"[CONTINUUM LAB] Hero capture generated: {hero_png}")
    print(f"[CONTINUUM LAB] Cosine projection capture generated: {proj_cos_png}")
    print(f"[CONTINUUM LAB] Sine projection capture generated: {proj_sin_png}")

    # Cleanup temp media
    import shutil
    if os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)
    shutil.rmtree(str(videos_dir / "temp_media"), ignore_errors=True)

    print("\n=======================================================")
    print("[CONTINUUM LAB] ALL 3D EULER DELIVERABLES RENDERED SUCCESSFULLY!")
    print(f"  - Spanish: {out_es}")
    print(f"  - English: {out_en}")
    print(f"  - Hero Image: {hero_png}")
    print(f"  - Cosine Projection: {proj_cos_png}")
    print(f"  - Sine Projection: {proj_sin_png}")
    print("=======================================================")


if __name__ == "__main__":
    render_all()
