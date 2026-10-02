"""
Classical Mechanics & Dynamical Systems
Division: 02 Dinamica y Vibraciones / 02 Mecanismo Coriolis Collarin
Module: render_video.py

High-Definition 60 FPS MP4 Video Generator (1080p, H.264/yuv420p).
No branding / No project name.
Pure kinematic visualization:
- Dynamic slow-motion and cinematic zoom into the collar during peak Coriolis inversion.
- Detailed decomposition of all 4 acceleration components in the rotating frame.
- Real-time oscilloscope wave and phase portrait (v_rel vs omega2).
"""

import sys
import math
from pathlib import Path
from collections import deque
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.physics.coriolis_kinematics import CoriolisMechanismParams, CoriolisKinematicsSolver


def render_hypnotic_video(
    output_path: Path = None,
    fps: int = 60,
    total_seconds: float = 12.0
):
    if output_path is None:
        workspace_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        output_dir = workspace_root / "RENDERS" / "Coriolis_Mechanism"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "mecanismo_coriolis_60fps.mp4"

    # Parámetros físicos rigurosos
    params = CoriolisMechanismParams(L1=1.0, d=1.55, omega1=2.5, arm_extension=1.75)
    solver = CoriolisKinematicsSolver(params)

    total_frames = int(total_seconds * fps)

    # 1. PERFIL TEMPORAL: 2 CICLOS COMPLETOS CON SLOW-MOTION EN EL SEGUNDO CICLO
    # Ciclo 1 (0 -> 2pi): Vista global normal (frames 0 -> total_frames // 2)
    # Ciclo 2 (2pi -> 4pi): Slow-motion & Zoom cinematográfico en la zona crítica (frames total_frames // 2 -> total_frames)

    half_frames = total_frames // 2

    # Ciclo 1: tiempo lineal uniforme
    th_cycle1 = np.linspace(0, 2.0 * np.pi, half_frames, endpoint=False)

    # Ciclo 2: tiempo no lineal con alta densidad de cuadros en theta1 = 270° (cámara lenta)
    th_dense = np.linspace(2.0 * np.pi, 4.0 * np.pi, 3000)
    th_rel = th_dense - 2.0 * np.pi
    dist_crit = abs(th_rel - 1.5 * np.pi)
    w_bell = np.exp(-(dist_crit ** 2) / (2.0 * (0.38 ** 2)))
    dt_dtheta = 1.0 + 4.2 * w_bell # Ralentización hasta ~5.2x
    cum_t = np.cumsum(dt_dtheta)
    cum_t = (cum_t - cum_t[0]) / (cum_t[-1] - cum_t[0])

    t_norm = np.linspace(0, 1, total_frames - half_frames, endpoint=False)
    th_cycle2 = np.interp(t_norm, cum_t, th_dense)

    all_thetas = np.concatenate([th_cycle1, th_cycle2])
    states = [solver.solve(th % (2.0 * np.pi)) for th in all_thetas]

    # Precalcular trayectoria completa del stylus para la estela base tenue
    base_stylus = np.array([
        solver.solve(th).r_O2 + solver.solve(th).u_r2 * (solver.solve(th).r2 * params.arm_extension * 0.95)
        for th in np.linspace(0, 2 * np.pi, 300)
    ])

    # 2. CONFIGURACIÓN DE LA FIGURA (1920x1080 @ 60 FPS, ESTÉTICA OBSIDIANA MINIMALISTA)
    plt.style.use("dark_background")
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor="#07090e")
    gs = gridspec.GridSpec(2, 2, width_ratios=[1.35, 0.65], height_ratios=[1, 1],
                           left=0.04, right=0.96, bottom=0.06, top=0.94, wspace=0.14, hspace=0.18)

    # Eje Principal (Mecanismo y Visualización Vectorial)
    ax_main = fig.add_subplot(gs[:, 0], facecolor="#07090e")
    ax_main.set_aspect("equal")
    ax_main.axis("off")

    # Eje Superior Derecho: Osciloscopio a_cor(t) en tiempo real
    ax_scope = fig.add_subplot(gs[0, 1], facecolor="#0d1117")
    ax_scope.set_title(r"Aceleración de Coriolis Instantánea: $a_{\mathrm{cor}} = 2\,\omega_2\,\dot{r}_2$",
                       color="#00f0ff", fontsize=11, fontweight="bold", pad=8)
    ax_scope.set_ylabel(r"$a_{\mathrm{cor}}$ [$\mathrm{m/s^2}$]", color="#8b949e", fontsize=10)
    ax_scope.set_ylim(-12, 12)
    ax_scope.set_xlim(0, 120)
    ax_scope.grid(True, color="#21262d", ls=":", alpha=0.8)
    ax_scope.tick_params(colors="#8b949e", labelsize=9)
    ax_scope.axhline(0, color="gray", lw=0.8, ls="--", alpha=0.4)

    # Eje Inferior Derecho: Plano de Fase (Ciclo Límite: v_rel vs omega2)
    ax_phase = fig.add_subplot(gs[1, 1], facecolor="#0d1117")
    ax_phase.set_title(r"Plano de Fase: Deslizamiento $\dot{r}_2$ vs Rotación $\omega_2$",
                       color="#39ff14", fontsize=11, fontweight="bold", pad=8)
    ax_phase.set_xlabel(r"Velocidad de Deslizamiento $\dot{r}_2$ ($v_{\mathrm{rel}}$) [m/s]", color="#8b949e", fontsize=10)
    ax_phase.set_ylabel(r"Velocidad Angular $\omega_2$ [rad/s]", color="#8b949e", fontsize=10)
    ax_phase.grid(True, color="#21262d", ls=":", alpha=0.8)
    ax_phase.tick_params(colors="#8b949e", labelsize=9)

    # Curva estática completa del ciclo límite en el plano de fase
    cycle_vrel = [solver.solve(th).v_rel for th in np.linspace(0, 2*np.pi, 200)]
    cycle_w2 = [solver.solve(th).omega2 for th in np.linspace(0, 2*np.pi, 200)]
    ax_phase.plot(cycle_vrel, cycle_w2, color="#00f0ff", alpha=0.35, lw=1.5, ls="--")
    phase_bead, = ax_phase.plot([], [], marker="o", color="#ff007f", markersize=8, zorder=5)

    # Retícula ingenieril en el eje principal
    for r in [0.5, 1.0, 1.5, 2.0, 2.5]:
        circle = plt.Circle((0, 0), r, color="#00f0ff", fill=False, lw=0.6, alpha=0.08, ls=":")
        ax_main.add_patch(circle)

    # Estela base tenue completa
    ax_main.plot(base_stylus[:, 0], base_stylus[:, 1], color="#a855f7", lw=1.0, alpha=0.18, ls="--")

    # ELEMENTOS DINÁMICOS DEL MECANISMO
    # 1. Estela persistente fosforescente del stylus
    trail_line, = ax_main.plot([], [], color="#a855f7", lw=2.8, alpha=0.9)
    trail_glow, = ax_main.plot([], [], color="#00f0ff", lw=1.2, alpha=0.7)

    # 2. Rieles de la barra ranurada (Barra 2)
    rail_left, = ax_main.plot([], [], color="#58a6ff", lw=3.2, alpha=0.85)
    rail_right, = ax_main.plot([], [], color="#58a6ff", lw=3.2, alpha=0.85)
    slot_core, = ax_main.plot([], [], color="#ffffff", lw=1.0, alpha=0.35, ls=":")

    # 3. Manivela impulsora O1-A (Barra 1)
    crank_line, = ax_main.plot([], [], color="#ffffff", lw=4.5)
    crank_core, = ax_main.plot([], [], color="#00f0ff", lw=2.0)

    # 4. Pivotes fijos O1 y O2
    ax_main.scatter([0], [0], color="#00f0ff", s=80, zorder=6, edgecolors="#ffffff", lw=1.8)
    ax_main.scatter([0], [-params.d], color="#58a6ff", s=80, zorder=6, edgecolors="#ffffff", lw=1.8)
    ax_main.text(0.12, -0.06, "$O_1$", color="#8b949e", fontsize=11, fontweight="bold")
    ax_main.text(0.12, -params.d - 0.06, "$O_2$", color="#8b949e", fontsize=11, fontweight="bold")

    # 5. Collarín deslizante articulado en A
    collar_patch = plt.Polygon(np.zeros((4, 2)), closed=True, color="#ffd700", ec="#ffffff", lw=1.8, zorder=7)
    ax_main.add_patch(collar_patch)
    collar_pin = ax_main.scatter([], [], color="#00f0ff", s=45, zorder=8)

    # 6. Flechas vectoriales
    q_cor = ax_main.quiver([0], [0], [0], [0], color="#00f0ff", angles="xy", scale_units="xy", scale=1.0, width=0.012, zorder=9)
    q_vrel = ax_main.quiver([0], [0], [0], [0], color="#39ff14", angles="xy", scale_units="xy", scale=1.0, width=0.010, zorder=9)
    q_cent = ax_main.quiver([0], [0], [0], [0], color="#ffb800", angles="xy", scale_units="xy", scale=1.0, width=0.009, zorder=9)
    q_euler = ax_main.quiver([0], [0], [0], [0], color="#ff007f", angles="xy", scale_units="xy", scale=1.0, width=0.009, zorder=9)

    # 7. Textos dinámicos en pantalla (Sin nombre de proyecto)
    hud_state_badge = ax_main.text(0.04, 0.94, "", transform=ax_main.transAxes, color="#ffd700", fontsize=11, fontweight="bold")
    hud_cor = ax_main.text(0.04, 0.08, "", transform=ax_main.transAxes, color="#00f0ff", fontsize=11, fontfamily="monospace", fontweight="bold")
    hud_vrel = ax_main.text(0.04, 0.04, "", transform=ax_main.transAxes, color="#39ff14", fontsize=10.5, fontfamily="monospace")
    hud_components = ax_main.text(0.04, 0.00, "", transform=ax_main.transAxes, color="#e6edf3", fontsize=9.5, fontfamily="monospace")

    # Línea del osciloscopio
    scope_history = deque(maxlen=120)
    scope_line, = ax_scope.plot([], [], color="#00f0ff", lw=2.2)
    scope_dot, = ax_scope.plot([], [], marker="o", color="#ffffff", markersize=6)

    trail_history = deque(maxlen=65)

    wide_center = np.array([0.0, -0.75])
    wide_half_w = 2.45

    def update(frame_idx):
        s = states[frame_idx]
        th_val = all_thetas[frame_idx]

        # Comprobar si estamos en el segundo ciclo (zona de zoom cinemático)
        is_second_cycle = frame_idx >= half_frames
        w_zoom = 0.0
        if is_second_cycle:
            th_rel = (th_val - 2.0 * np.pi)
            dist_c = abs(th_rel - 1.5 * np.pi)
            w_zoom = float(np.exp(-(dist_c ** 2) / (2.0 * (0.36 ** 2))))

        # 1. CÁMARA DINÁMICA & ZOOM EN EL COLLARÍN
        zoom_factor = 1.0 + 1.65 * w_zoom
        cam_center = (1.0 - w_zoom) * wide_center + w_zoom * s.r_A
        cur_half_w = wide_half_w / zoom_factor
        cur_half_h = cur_half_w

        ax_main.set_xlim(cam_center[0] - cur_half_w, cam_center[0] + cur_half_w)
        ax_main.set_ylim(cam_center[1] - cur_half_h, cam_center[1] + cur_half_h)

        if w_zoom > 0.15:
            hud_state_badge.set_text(f"ZOOM CINEMÁTICO {zoom_factor:.1f}x  |  CÁMARA LENTA {1.0/(1.0+4.2*w_zoom):.2f}x")
        else:
            hud_state_badge.set_text("VISTA CINEMÁTICA GLOBAL")

        # 2. ESTELA DEL STYLUS
        stylus_pt = s.r_O2 + s.u_r2 * (s.r2 * params.arm_extension * 0.95)
        trail_history.append(stylus_pt)
        trail_arr = np.array(trail_history)

        trail_line.set_data(trail_arr[:, 0], trail_arr[:, 1])
        trail_glow.set_data(trail_arr[:, 0], trail_arr[:, 1])

        # 3. MANIVELA O1 -> A
        crank_line.set_data([0, s.r_A[0]], [0, s.r_A[1]])
        crank_core.set_data([0, s.r_A[0]], [0, s.r_A[1]])

        # 4. RIELES BARRA 2
        pO2 = s.r_O2
        pTip = s.r_tip_arm
        dx = pTip[0] - pO2[0]
        dy = pTip[1] - pO2[1]
        length = np.hypot(dx, dy)
        nx = -dy / length * 0.08
        ny = dx / length * 0.08

        rail_left.set_data([pO2[0] + nx, pTip[0] + nx], [pO2[1] + ny, pTip[1] + ny])
        rail_right.set_data([pO2[0] - nx, pTip[0] - nx], [pO2[1] - ny, pTip[1] - ny])
        slot_core.set_data([pO2[0], pTip[0]], [pO2[1], pTip[1]])

        # 5. COLLARÍN
        w_c, h_c = 0.22, 0.15
        cos2, sin2 = s.u_r2[0], s.u_r2[1]
        corners_local = np.array([
            [-w_c/2, -h_c/2],
            [w_c/2, -h_c/2],
            [w_c/2, h_c/2],
            [-w_c/2, h_c/2]
        ])
        rot_mat = np.array([[cos2, -sin2], [sin2, cos2]])
        corners_world = (corners_local @ rot_mat.T) + s.r_A
        collar_patch.set_xy(corners_world)
        collar_pin.set_offsets([s.r_A])

        # 6. VECTORES DINÁMICOS
        vec_scale = 0.075 / (1.0 + 0.3 * w_zoom)

        # Coriolis
        v_cor = s.a_coriolis_vec * vec_scale
        q_cor.set_offsets([s.r_A])
        q_cor.set_UVC([v_cor[0]], [v_cor[1]])

        # Deslizamiento
        v_rel = s.v_rel_vec * (vec_scale * 1.5)
        q_vrel.set_offsets([s.r_A])
        q_vrel.set_UVC([v_rel[0]], [v_rel[1]])

        # Componentes adicionales durante zoom
        if w_zoom > 0.10:
            v_cent = s.a_centripetal_vec * (vec_scale * 0.7)
            q_cent.set_offsets([s.r_A])
            q_cent.set_UVC([v_cent[0]], [v_cent[1]])

            v_euler = s.a_euler_vec * (vec_scale * 0.7)
            q_euler.set_offsets([s.r_A])
            q_euler.set_UVC([v_euler[0]], [v_euler[1]])
        else:
            q_cent.set_UVC([0], [0])
            q_euler.set_UVC([0], [0])

        # HUD en vivo
        hud_cor.set_text(f"a_cor = {s.a_coriolis_mag:+6.2f} m/s² (Coriolis)")
        hud_vrel.set_text(f"v_rel = {s.v_rel:+6.2f} m/s | ω₂ = {s.omega2:+5.2f} rad/s")
        if w_zoom > 0.12:
            hud_components.set_text(f"a_cent = {-s.omega2**2*s.r2:+5.2f} m/s² | a_euler = {s.alpha2*s.r2:+5.2f} m/s²")
        else:
            hud_components.set_text(f"r₂ = {s.r2:.2f} m | θ₁ = {np.degrees(s.theta1):.0f}°")

        # 7. ACTUALIZACIÓN DE OSCILOSCOPIO
        scope_history.append(s.a_coriolis_mag)
        scope_arr = np.array(scope_history)
        xs = np.arange(len(scope_arr))
        scope_line.set_data(xs, scope_arr)
        if len(scope_arr) > 0:
            scope_dot.set_data([xs[-1]], [scope_arr[-1]])

        # 8. ACTUALIZACIÓN DEL PLANO DE FASE
        phase_bead.set_data([s.v_rel], [s.omega2])

        return (
            trail_line, trail_glow, rail_left, rail_right, slot_core,
            crank_line, crank_core, collar_patch, collar_pin,
            q_cor, q_vrel, q_cent, q_euler,
            hud_state_badge, hud_cor, hud_vrel, hud_components,
            scope_line, scope_dot, phase_bead
        )

    print(f"[VIDEO COMPILER] Rendering {total_frames} frames @ {fps} FPS (1080p MP4 / H.264)...")
    writer = animation.FFMpegWriter(
        fps=fps,
        codec="libx264",
        bitrate=8000,
        extra_args=["-pix_fmt", "yuv420p", "-crf", "18"]
    )

    anim = animation.FuncAnimation(fig, update, frames=total_frames, blit=False)
    anim.save(str(output_path), writer=writer)
    plt.close()
    print(f"[SUCCESS] High-definition MP4 video saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    render_hypnotic_video()
