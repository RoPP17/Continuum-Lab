"""
Continuum Lab — Fluid Mechanics & Nonlinear PDEs
Module: 01 Mecanica de Fluidos / 02 Singularidad Navier Stokes Blowup
Vectorized Manim 9:16 (1080x1920 @ 60 FPS) Video Production Engine

Features:
  - Exact 18.0s retention timeline (1080 frames at 60 FPS).
  - Safe zones: Top HUD at y = 5.4 (>220 px free), Bottom HUD at y = -4.3 (>340 px free).
  - Zero project branding or titles in frame (100% pure physics & telemetry).
  - Live animated telemetry: tau(t) -> 0, ||u||_max -> Inf, E_total = Bounded.
  - Active swirling streamlines spiraling into the origin from frame 0 (no static pop-in).
  - Annular wave pulse packets (sigma = +/-1) glowing and generating Reynolds stress cancellation.
  - Slender needle filament forming at the center with vertical jetting.
  - Bilingual delivery (ES and EN).
  - Multi-layer procedural hydro-acoustic stereo audio multiplexing.
"""

from manim import *
import numpy as np
import os
import subprocess
import sys
from pathlib import Path
import imageio_ffmpeg

# Add project root to sys.path
project_dir = Path(__file__).resolve().parent.parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.physics.navier_stokes_blowup import NavierStokesBlowupSimulation, BlowupParameters
from src.audio.blowup_audio_synth import synthesize_blowup_audio

# Exact TikTok 9:16 Canvas Configuration
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#0a0a0c"  # Deep Cybernetic Void


def create_blowup_scene(lang: str = "ES"):
    """
    Factory creating localized Manim scene class (ES or EN).
    """
    class NavierStokesBlowupScene(Scene):
        def construct(self):
            sim = NavierStokesBlowupSimulation()
            t_tracker = ValueTracker(0.0)

            # -----------------------------------------------------------------
            # 1. Unified Top HUD Card (Safe Zone: y in [4.38, 6.82], leaves >140 px top)
            # Three-Row Layout with zero overlap guaranteed:
            #   Row 1 (y = 6.30): Navier-Stokes PDE in R^3
            #   Row 2 (y = 5.50): Millennium Asymptotic Bounds (Divergence vs Bounded Energy)
            #   Row 3 (y = 4.70): Live Cybernetic Telemetry Readout
            # -----------------------------------------------------------------
            top_box = RoundedRectangle(
                corner_radius=0.14,
                width=7.8,
                height=2.45,
                color="#00f0ff",
                stroke_width=1.5,
                fill_color="#0d1117",
                fill_opacity=0.96
            ).move_to(UP * 5.60)

            eq_navier = MathTex(
                r"\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u}\cdot\nabla)\mathbf{u} - \nu \Delta\mathbf{u} + \nabla p = \mathbf{f}, \quad \nabla\cdot\mathbf{u} = 0",
                font_size=18,
                color="#ffffff"
            ).move_to(UP * 6.30)

            rule_top_1 = Line(LEFT * 3.5, RIGHT * 3.5, color="#1f2937", stroke_width=0.9).move_to(UP * 5.90)

            sub_top = MathTex(
                r"\sup_{0 \le t < 1} \|\mathbf{u}(t)\|_{L^2} < \infty \quad \big| \quad \lim_{t \to 1^-} \|\mathbf{u}(t)\|_{L^\infty} = +\infty",
                font_size=16,
                color="#00f0ff"
            ).move_to(UP * 5.50)

            rule_top_2 = Line(LEFT * 3.5, RIGHT * 3.5, color="#1f2937", stroke_width=0.9).move_to(UP * 5.10)

            if lang == "ES":
                live_text = always_redraw(lambda: Text(
                    f"τ = {max(1.0 - t_tracker.get_value()/21.0*0.992, 0.008):.3f}    "
                    f"||u||_max = {sim.compute_global_metrics(min(t_tracker.get_value()/21.0*0.992, 0.992))['u_max']:.1f} m/s    "
                    f"E_tot = {sim.compute_global_metrics(min(t_tracker.get_value()/21.0*0.992, 0.992))['energy_total']:.2f} J (Acotada)",
                    font="Segoe UI",
                    font_size=14,
                    color="#39ff14"
                ).move_to(UP * 4.70))
            else:
                live_text = always_redraw(lambda: Text(
                    f"τ = {max(1.0 - t_tracker.get_value()/21.0*0.992, 0.008):.3f}    "
                    f"||u||_max = {sim.compute_global_metrics(min(t_tracker.get_value()/21.0*0.992, 0.992))['u_max']:.1f} m/s    "
                    f"E_tot = {sim.compute_global_metrics(min(t_tracker.get_value()/21.0*0.992, 0.992))['energy_total']:.2f} J (Bounded)",
                    font="Segoe UI",
                    font_size=14,
                    color="#39ff14"
                ).move_to(UP * 4.70))

            top_group = VGroup(top_box, eq_navier, rule_top_1, sub_top, rule_top_2, live_text)
            self.add(top_group)

            # -----------------------------------------------------------------
            # 2. Bottom Telemetry Card (Safe Zone: y in [-5.6, -3.8], leaves >280 px bot)
            # -----------------------------------------------------------------
            bottom_box = RoundedRectangle(
                corner_radius=0.14,
                width=7.8,
                height=1.80,
                color="#ff007f",
                stroke_width=1.5,
                fill_color="#0d1117",
                fill_opacity=0.96
            ).move_to(DOWN * 4.70)

            if lang == "ES":
                telem_header = MathTex(
                    r"\text{CANCELACI\'ON DE RESIDUO POR PULSOS ONDULATORIOS}",
                    font_size=16,
                    color="#ffffff"
                ).move_to(DOWN * 4.25)

                metrics_text = MathTex(
                    r"T_{r\theta} = \langle w_r w_\theta \rangle \quad \big| \quad \ell_r \sim \tau^{1/2} \ll \ell_z \sim \tau^{1/2-h}",
                    font_size=15,
                    color="#39ff14"
                ).move_to(DOWN * 4.68)

                callout_text = MathTex(
                    r"\text{\textquestiondown Podr\'ia la viscosidad evitar el blowup si la fuerza es nula } (f=0)\text{?}",
                    font_size=14,
                    color="#ffaa00"
                ).move_to(DOWN * 5.12)
            else:
                telem_header = MathTex(
                    r"\text{WAVE PULSE RESIDUAL STRESS CANCELLATION}",
                    font_size=16,
                    color="#ffffff"
                ).move_to(DOWN * 4.25)

                metrics_text = MathTex(
                    r"T_{r\theta} = \langle w_r w_\theta \rangle \quad \big| \quad \ell_r \sim \tau^{1/2} \ll \ell_z \sim \tau^{1/2-h}",
                    font_size=15,
                    color="#39ff14"
                ).move_to(DOWN * 4.68)

                callout_text = MathTex(
                    r"\text{Could viscosity prevent blowup if external forcing is zero } (f=0)\text{?}",
                    font_size=14,
                    color="#ffaa00"
                ).move_to(DOWN * 5.12)

            bottom_group = VGroup(bottom_box, telem_header, metrics_text, callout_text)
            self.add(bottom_group)

            # -----------------------------------------------------------------
            # 3. Central Fluid Vortex Canvas (Center at y = 0.05)
            # -----------------------------------------------------------------
            v_center = np.array([0.0, 0.05, 0.0])

            # Coordinate Grid / Range Circles
            grid_circles = VGroup()
            for r_circ in [0.70, 1.40, 2.10, 2.80]:
                c_ring = Circle(radius=r_circ, color="#1e293b", stroke_width=0.8, stroke_opacity=0.6).move_to(v_center)
                grid_circles.add(c_ring)
            self.add(grid_circles)

            # Contracting Annulus Boundary Rings
            annulus_rings = always_redraw(lambda: self.get_annulus_rings(t_tracker.get_value(), v_center, sim))
            self.add(annulus_rings)

            # Central Core Glow & Needle Filament
            core_needle = always_redraw(lambda: self.get_needle_filament(t_tracker.get_value(), v_center, sim))
            self.add(core_needle)

            # Swirling Streamlines (12 Streamlines spiraling inward)
            streamlines_group = always_redraw(lambda: self.get_dynamic_streamlines(t_tracker.get_value(), v_center, sim))
            self.add(streamlines_group)

            # Annular Oscillatory Wave Pulses (Wavepackets canceling residual)
            pulses_group = always_redraw(lambda: self.get_wave_pulses(t_tracker.get_value(), v_center, sim))
            self.add(pulses_group)

            # Rotating Fluid Tracer Particles with Dynamic Streamline Streaks (75 particles)
            particles_group = always_redraw(lambda: self.get_tracer_particles(t_tracker.get_value(), v_center, sim))
            self.add(particles_group)

            # -----------------------------------------------------------------
            # 5. Continuous 21.0s Physical Execution (+3s requested extension)
            # -----------------------------------------------------------------
            self.play(
                t_tracker.animate.set_value(21.0),
                run_time=21.0,
                rate_func=linear
            )
            self.wait(0.2)

        def get_annulus_rings(self, t: float, center: np.ndarray, sim: NavierStokesBlowupSimulation):
            prog = min(t / 21.0, 0.995)
            # Physical contraction: tau shrinks from 1.0 to 0.008
            tau = max(1.0 - prog * 0.992, 0.008)
            q = tau

            # Scaled visual radii (bounded to fit canvas)
            r_scale = 1.85
            ra_vis = np.sqrt(2.0 * q * sim.params.X_a) * r_scale + 0.15
            rb_vis = np.sqrt(2.0 * q * sim.params.X_b) * r_scale + 0.35

            ring_a = Circle(radius=ra_vis, color="#00f0ff", stroke_width=1.5, stroke_opacity=0.85).move_to(center)
            ring_b = Circle(radius=rb_vis, color="#ff007f", stroke_width=1.5, stroke_opacity=0.85).move_to(center)

            # Subtle shaded annular region
            annulus_fill = Annulus(
                inner_radius=ra_vis,
                outer_radius=rb_vis,
                color="#ff007f",
                fill_opacity=0.08,
                stroke_width=0
            ).move_to(center)

            return VGroup(annulus_fill, ring_a, ring_b)

        def get_needle_filament(self, t: float, center: np.ndarray, sim: NavierStokesBlowupSimulation):
            prog = min(t / 21.0, 0.995)
            tau = max(1.0 - prog * 0.992, 0.008)
            lr = np.sqrt(tau)
            lz = tau**(0.5 - sim.params.h)

            # Central glowing core dot
            core_radius = max(0.08 * np.sqrt(tau), 0.025)
            dot_core = Dot(point=center, radius=core_radius, color="#ffffff")
            halo_core = Dot(point=center, radius=core_radius * 2.8, color="#00f0ff", fill_opacity=0.45)

            # Slender needle vertical indicator
            needle_height = max(1.2 * (lz / lr) * 0.25, 0.4)
            needle_height = min(needle_height, 2.4)
            needle_line = Line(
                center + DOWN * (needle_height / 2.0),
                center + UP * (needle_height / 2.0),
                color="#39ff14",
                stroke_width=2.5,
                stroke_opacity=0.9
            )

            # Upward and downward axial outflow arrows (u_z jets)
            arrow_up = Arrow(
                start=center + UP * 0.15,
                end=center + UP * (needle_height / 2.0 + 0.35),
                color="#39ff14",
                stroke_width=2.0,
                max_tip_length_to_length_ratio=0.25
            )
            arrow_down = Arrow(
                start=center + DOWN * 0.15,
                end=center + DOWN * (needle_height / 2.0 + 0.35),
                color="#39ff14",
                stroke_width=2.0,
                max_tip_length_to_length_ratio=0.25
            )

            return VGroup(halo_core, dot_core, needle_line, arrow_up, arrow_down)

        def get_dynamic_streamlines(self, t: float, center: np.ndarray, sim: NavierStokesBlowupSimulation):
            prog = min(t / 21.0, 0.995)
            tau = max(1.0 - prog * 0.992, 0.008)

            streamlines = VGroup()
            num_lines = 12
            # Spin angle advances dynamically
            spin_offset = 2.8 * t + 1.2 * (prog**2.2) * 21.0

            for i in range(num_lines):
                theta_0 = i * (2.0 * np.pi / num_lines) + spin_offset * 0.25
                # Spiral curve from r = 3.2 inward to r = 0.18
                s_vals = np.linspace(0.18, 3.2, 35)
                # Hyperbolic logarithmic spiral: theta(s) = theta_0 + alpha / s^(0.7)
                theta_s = theta_0 + (1.8 / (s_vals**0.65)) * (tau**(-0.25))

                x_pts = s_vals * np.cos(theta_s)
                y_pts = s_vals * np.sin(theta_s)

                points = [center + np.array([x_pts[k], y_pts[k], 0.0]) for k in range(len(s_vals))]
                curve = VMobject()
                curve.set_points_smoothly(points)

                # Color: Cyan at inner end, Deep Azure at outer end
                curve.set_color_by_gradient("#00f0ff", "#38bdf8", "#1e40af")
                curve.set_stroke(width=1.4, opacity=0.75)
                streamlines.add(curve)

            return streamlines

        def get_wave_pulses(self, t: float, center: np.ndarray, sim: NavierStokesBlowupSimulation):
            """
            Draws the annular wave pulse packets (sigma = +1 and sigma = -1)
            representing the Reynolds stress cancellation <w_r * w_theta> and <w_r * w_z>.
            """
            prog = min(t / 21.0, 0.995)
            tau = max(1.0 - prog * 0.992, 0.008)
            q = tau

            r_scale = 1.85
            ra_vis = np.sqrt(2.0 * q * sim.params.X_a) * r_scale + 0.15
            rb_vis = np.sqrt(2.0 * q * sim.params.X_b) * r_scale + 0.35
            r_mid = 0.5 * (ra_vis + rb_vis)

            pulses = VGroup()
            num_wave_nodes = 8
            # Wave moves with high frequency phase
            phase_wave = 14.0 * t

            for k in range(num_wave_nodes):
                phi = k * (2.0 * np.pi / num_wave_nodes) + phase_wave * 0.08
                # Radial oscillation (w_r)
                dr = 0.12 * np.sin(4.0 * phi - phase_wave)
                pos = center + np.array([(r_mid + dr) * np.cos(phi), (r_mid + dr) * np.sin(phi), 0.0])

                # Tangential shear arrow (w_theta)
                tangent_dir = np.array([-np.sin(phi), np.cos(phi), 0.0])
                arrow_w = Arrow(
                    start=pos,
                    end=pos + tangent_dir * (0.22 * np.cos(4.0 * phi - phase_wave)),
                    color="#ff007f",
                    stroke_width=1.8,
                    max_tip_length_to_length_ratio=0.3
                )
                pulses.add(arrow_w)

            return pulses

        def get_tracer_particles(self, t: float, center: np.ndarray, sim: NavierStokesBlowupSimulation):
            """
            Rotating Fluid Tracer Particles with Dynamic Velocity Comet Streaks.
            Slightly enlarged and accented with trailing velocity vectors to make
            the swirling fluid kinematics and inward spiral advection clearly evident.
            """
            prog = min(t / 21.0, 0.995)
            tau = max(1.0 - prog * 0.992, 0.008)

            particles = VGroup()
            num_p = 75
            for idx in range(num_p):
                # Fixed deterministic radial anchor
                r_seed = ((idx * 37) % 100) / 100.0
                theta_base = ((idx * 83) % 100) / 100.0 * 2.0 * np.pi
                r_base = 0.22 + 2.85 * r_seed

                # Continuous inward spiral drift with respawn
                drift = 0.38 * (t / 21.0) + 0.18 * (prog**2.0)
                r_curr = ((r_base - 0.22 - drift) % 2.85) + 0.22

                # Dynamic swirling angular velocity omega_p(r, tau)
                omega_p = (2.2 / (r_curr**0.95)) * (tau**(-0.38))
                theta_curr = theta_base + omega_p * t

                pos = center + np.array([r_curr * np.cos(theta_curr), r_curr * np.sin(theta_curr), 0.0])

                # Tangent velocity streak / comet trail (reveals fluid velocity & direction clearly)
                dt_trail = 0.075
                theta_tail = theta_curr - omega_p * dt_trail
                r_tail = min(r_curr + 0.035 * dt_trail, 3.1)
                pos_tail = center + np.array([r_tail * np.cos(theta_tail), r_tail * np.sin(theta_tail), 0.0])

                # Layered fluid colors: Cyan in core, Neon Magenta/Green in annulus, Sky Blue in outer flow
                if r_curr < 0.8:
                    p_col = "#00f0ff"
                elif r_curr < 1.9:
                    p_col = "#ff007f" if idx % 2 == 0 else "#39ff14"
                else:
                    p_col = "#38bdf8"

                # Velocity trail line + glowing particle head
                tail_line = Line(pos_tail, pos, color=p_col, stroke_width=2.6, stroke_opacity=0.75)
                dot_glow = Dot(point=pos, radius=0.060, color=p_col, fill_opacity=0.90)
                dot_core = Dot(point=pos, radius=0.030, color="#ffffff", fill_opacity=1.0)
                particles.add(tail_line, dot_glow, dot_core)

            return particles



    return NavierStokesBlowupScene


class MovingBlowupSceneES(create_blowup_scene("ES")):
    pass


class MovingBlowupSceneEN(create_blowup_scene("EN")):
    pass


def render_all():
    base_dir = project_dir.parent.parent
    renders_dir = base_dir / "RENDERS" / "5 Singularidad Navier Stokes"
    videos_dir = renders_dir / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)

    # 1. Synthesize Procedural Hydro-Acoustic Audio (21.5s)
    temp_audio_path = str(videos_dir / "navier_stokes_blowup_audio.wav")
    print("\n=======================================================")
    print("[CONTINUUM LAB] Synthesizing Hydro-Acoustic Blowup Audio (21.5s)...")
    print("=======================================================")
    synthesize_blowup_audio(duration=21.5, fs=44100, output_path=temp_audio_path)

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    this_script = str(Path(__file__).resolve())

    # 2. Render Spanish Version
    print("\n=======================================================")
    print("[CONTINUUM LAB] Rendering Spanish Navier-Stokes Simulation (ES)...")
    print("=======================================================")
    cmd_manim_es = [
        "manim", "-qh", "--media_dir", str(videos_dir / "temp_media"),
        this_script, "MovingBlowupSceneES"
    ]
    subprocess.run(cmd_manim_es, check=True)

    raw_es = list((videos_dir / "temp_media").rglob("MovingBlowupSceneES.mp4"))[0]
    out_es = str(videos_dir / "Singularidad Navier Stokes ES.mp4")

    print(f"[CONTINUUM LAB] Multiplexing ES Audio + Video -> {out_es}")
    cmd_mux_es = [
        ffmpeg_bin, "-y", "-i", str(raw_es), "-i", temp_audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out_es
    ]
    subprocess.run(cmd_mux_es, check=True)

    # 3. Render English Version
    print("\n=======================================================")
    print("[CONTINUUM LAB] Rendering English Navier-Stokes Simulation (EN)...")
    print("=======================================================")
    cmd_manim_en = [
        "manim", "-qh", "--media_dir", str(videos_dir / "temp_media"),
        this_script, "MovingBlowupSceneEN"
    ]
    subprocess.run(cmd_manim_en, check=True)

    raw_en = list((videos_dir / "temp_media").rglob("MovingBlowupSceneEN.mp4"))[0]
    out_en = str(videos_dir / "Navier Stokes Singularity EN.mp4")

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
    print("[CONTINUUM LAB] ALL NAVIER-STOKES BLOWUP VIDEOS DELIVERED!")
    print(f"  - Spanish: {out_es}")
    print(f"  - English: {out_en}")
    print("=======================================================")


if __name__ == "__main__":
    render_all()
