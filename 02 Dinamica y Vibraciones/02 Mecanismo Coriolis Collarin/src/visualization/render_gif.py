"""
Continuum Lab — Classical Mechanics & Dynamical Systems
Division: 02 Dinamica y Vibraciones / 02 Mecanismo Coriolis Collarin
Module: render_gif.py

Cinematic Slow-Motion & Dynamic Zoom GIF Generator.
Smoothly zooms into the collar during the critical Coriolis reversal zone,
slows down time for high-detail vector inspection, and returns to wide view.
Header text is placed completely outside axes coordinates to prevent any overlap.
"""

import sys
from pathlib import Path
from collections import deque
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.physics.coriolis_kinematics import CoriolisMechanismParams, CoriolisKinematicsSolver


def generate_hypnotic_gif(output_path: Path = None, n_frames: int = 150, fps: int = 30):
    if output_path is None:
        workspace_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        output_dir = workspace_root / "RENDERS" / "Coriolis_Mechanism"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "coriolis_hypnotic_loop.gif"

    params = CoriolisMechanismParams(L1=1.0, d=1.55, omega1=2.5, arm_extension=1.75)
    solver = CoriolisKinematicsSolver(params)

    # 1. GENERACIÓN DE TIEMPO CON WARPING CINEMÁTICO (SLOW-MOTION NO LINEAL)
    # Mayor densidad de cuadros (cámara lenta) en torno a theta1 = 270° (1.5 * pi)
    theta_dense = np.linspace(0, 2 * np.pi, 3000)
    w_bell = np.exp(-((theta_dense - 1.5 * np.pi) ** 2) / (2 * (0.42 ** 2)))
    # dt/dtheta = 1.0 + 3.8 * w_bell (ralentización hasta ~4.8x)
    dt_dtheta = 1.0 + 3.8 * w_bell
    cum_t = np.cumsum(dt_dtheta)
    cum_t = (cum_t - cum_t[0]) / (cum_t[-1] - cum_t[0])

    frame_norm_times = np.linspace(0, 1, n_frames, endpoint=False)
    frame_thetas = np.interp(frame_norm_times, cum_t, theta_dense)
    states = [solver.solve(th) for th in frame_thetas]

    # Precalcular trayectoria completa del stylus para la estela base
    full_cycle_stylus = np.array([
        solver.solve(th).r_O2 + solver.solve(th).u_r2 * (solver.solve(th).r2 * params.arm_extension * 0.95)
        for th in np.linspace(0, 2 * np.pi, 200)
    ])

    # 2. CONFIGURACIÓN DE FIGURA MATPLOTLIB (TÍTULO COMPLETAMENTE SEPARADO DEL CANVAS)
    plt.style.use("dark_background")
    fig = plt.figure(figsize=(8.5, 9.2), dpi=100, facecolor="#07090e")

    # Margen explícito: los ejes ocupan de y=0.07 a y=0.86. El texto va de 0.88 a 0.98.
    ax = fig.add_axes([0.06, 0.08, 0.88, 0.77], facecolor="#07090e")
    ax.set_aspect("equal")
    ax.axis("off")

    # ENCABEZADO Y TÍTULO FUERA DE LOS EJES (IMPOSIBLE QUE EL MECANISMO LOS SOLAPE)
    fig.text(
        0.5, 0.95,
        "CONTINUUM LAB • ACELERACIÓN DE CORIOLIS EN MECANISMO DE COLLARÍN",
        color="#00f0ff", fontsize=11, fontweight="bold", ha="center", fontfamily="sans-serif"
    )
    fig.text(
        0.5, 0.915,
        r"$\vec{a}_{\mathrm{cor}} = 2\,\vec{\omega}_2 \times \vec{v}_{\mathrm{rel}} \quad (\perp \text{barra ranurada}) \quad \bullet \quad \text{Zoom Cinemático \& Cámara Lenta}$",
        color="#8b949e", fontsize=9, ha="center"
    )

    # Retícula ingenieril circular tenue centrada en O1
    for r in [0.5, 1.0, 1.5, 2.0, 2.5]:
        circle = plt.Circle((0, 0), r, color="#00f0ff", fill=False, lw=0.5, alpha=0.08, ls=":")
        ax.add_patch(circle)

    # Estela base completa estática muy tenue
    ax.plot(full_cycle_stylus[:, 0], full_cycle_stylus[:, 1], color="#a855f7", lw=0.9, alpha=0.20, ls="--")

    # ELEMENTOS GRÁFICOS DINÁMICOS
    # 1. Estela dinámica fosforescente del stylus
    trail_line, = ax.plot([], [], color="#a855f7", lw=2.4, alpha=0.9)
    trail_glow, = ax.plot([], [], color="#00f0ff", lw=1.2, alpha=0.7)

    # 2. Rieles de la barra ranurada (Barra 2)
    rail_left, = ax.plot([], [], color="#58a6ff", lw=2.6, alpha=0.85)
    rail_right, = ax.plot([], [], color="#58a6ff", lw=2.6, alpha=0.85)
    slot_core, = ax.plot([], [], color="#ffffff", lw=0.8, alpha=0.35, ls=":")

    # 3. Manivela O1-A (Barra 1)
    crank_line, = ax.plot([], [], color="#ffffff", lw=3.8)
    crank_core, = ax.plot([], [], color="#00f0ff", lw=1.6)

    # 4. Pivotes fijos O1 y O2
    ax.scatter([0], [0], color="#00f0ff", s=70, zorder=6, edgecolors="#ffffff", lw=1.5)
    ax.scatter([0], [-params.d], color="#58a6ff", s=70, zorder=6, edgecolors="#ffffff", lw=1.5)
    ax.text(0.12, -0.05, "$O_1$", color="#8b949e", fontsize=10, fontweight="bold")
    ax.text(0.12, -params.d - 0.05, "$O_2$", color="#8b949e", fontsize=10, fontweight="bold")

    # 5. Collarín deslizante articulado en A
    collar_patch = plt.Polygon(np.zeros((4, 2)), closed=True, color="#ffd700", ec="#ffffff", lw=1.5, zorder=7)
    ax.add_patch(collar_patch)
    collar_pin = ax.scatter([], [], color="#00f0ff", s=35, zorder=8)

    # 6. Vectores dinámicos con escala adaptativa
    q_cor = ax.quiver([0], [0], [0], [0], color="#00f0ff", angles="xy", scale_units="xy", scale=1.0, width=0.013, zorder=9)
    q_vrel = ax.quiver([0], [0], [0], [0], color="#39ff14", angles="xy", scale_units="xy", scale=1.0, width=0.011, zorder=9)
    q_cent = ax.quiver([0], [0], [0], [0], color="#ffb800", angles="xy", scale_units="xy", scale=1.0, width=0.009, zorder=9)
    q_euler = ax.quiver([0], [0], [0], [0], color="#ff007f", angles="xy", scale_units="xy", scale=1.0, width=0.009, zorder=9)

    # 7. Telemetría flotante en la esquina inferior
    hud_badge = ax.text(0.02, 0.94, "", transform=ax.transAxes, color="#ffd700", fontsize=9, fontweight="bold", fontfamily="sans-serif")
    hud_cor = ax.text(0.02, 0.08, "", transform=ax.transAxes, color="#00f0ff", fontsize=9.5, fontfamily="monospace", fontweight="bold")
    hud_vrel = ax.text(0.02, 0.04, "", transform=ax.transAxes, color="#39ff14", fontsize=9.0, fontfamily="monospace")
    hud_acc = ax.text(0.02, 0.00, "", transform=ax.transAxes, color="#e6edf3", fontsize=8.5, fontfamily="monospace")

    trail_history = deque(maxlen=40)

    # Parámetros de cámara amplia vs zoom
    wide_center = np.array([0.0, -0.75])
    wide_half_w = 2.45

    def init():
        return (
            trail_line, trail_glow, rail_left, rail_right, slot_core,
            crank_line, crank_core, collar_patch, collar_pin,
            q_cor, q_vrel, q_cent, q_euler, hud_badge, hud_cor, hud_vrel, hud_acc
        )

    def update(frame_idx):
        s = states[frame_idx]
        th = s.theta1

        # 1. CÁLCULO DE ZOOM Y ENFOQUE EN EL COLLARÍN
        # Campana suave alrededor de 1.5 * pi (270°)
        dist_crit = abs(th - 1.5 * np.pi)
        w_zoom = float(np.exp(-(dist_crit ** 2) / (2 * (0.38 ** 2))))

        # Factor de aumento de 1.0x hasta 2.5x
        zoom_factor = 1.0 + 1.50 * w_zoom
        # Centro interpolado entre la vista general y la posición exacta del collarín A
        cam_center = (1.0 - w_zoom) * wide_center + w_zoom * s.r_A
        cur_half_w = wide_half_w / zoom_factor
        cur_half_h = cur_half_w

        ax.set_xlim(cam_center[0] - cur_half_w, cam_center[0] + cur_half_w)
        ax.set_ylim(cam_center[1] - cur_half_h, cam_center[1] + cur_half_h)

        # Indicador de estado de cámara
        if w_zoom > 0.15:
            hud_badge.set_text(f"ZOOM CINEMÁTICO {zoom_factor:.1f}x  |  CÁMARA LENTA {1.0/(1.0+3.8*w_zoom):.2f}x")
        else:
            hud_badge.set_text("VISTA CINEMÁTICA GLOBAL")

        # 2. ACTUALIZACIÓN DE ESTELA
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

        # 5. COLLARÍN ORIENTADO CON BARRA 2
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

        # 6. VECTORES DINÁMICOS CON VISUALIZACIÓN DETALLADA DURANTE EL ZOOM
        # Escala visual de vectores (se expande levemente durante el zoom para ver detalle)
        vec_scale = 0.075 / (1.0 + 0.3 * w_zoom)

        # Coriolis: 2 * (omega2 x v_rel)
        v_cor = s.a_coriolis_vec * vec_scale
        q_cor.set_offsets([s.r_A])
        q_cor.set_UVC([v_cor[0]], [v_cor[1]])

        # Velocidad relativa de deslizamiento
        v_rel = s.v_rel_vec * (vec_scale * 1.5)
        q_vrel.set_offsets([s.r_A])
        q_vrel.set_UVC([v_rel[0]], [v_rel[1]])

        # Componentes adicionales (centrípeta y Euler) visibles durante el zoom
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

        # 7. TELEMETRÍA EN TIEMPO REAL
        hud_cor.set_text(f"a_cor = {s.a_coriolis_mag:+6.2f} m/s² (Coriolis)")
        hud_vrel.set_text(f"v_rel = {s.v_rel:+6.2f} m/s | ω₂ = {s.omega2:+5.2f} rad/s")
        if w_zoom > 0.15:
            hud_acc.set_text(f"a_cent = {-s.omega2**2*s.r2:+5.2f} m/s² | a_euler = {s.alpha2*s.r2:+5.2f} m/s²")
        else:
            hud_acc.set_text(f"r₂ = {s.r2:.2f} m | θ₁ = {np.degrees(th):.0f}°")

        return (
            trail_line, trail_glow, rail_left, rail_right, slot_core,
            crank_line, crank_core, collar_patch, collar_pin,
            q_cor, q_vrel, q_cent, q_euler, hud_badge, hud_cor, hud_vrel, hud_acc
        )

    anim = animation.FuncAnimation(
        fig, update, frames=n_frames, init_func=init, blit=False, interval=1000 // fps
    )

    print(f"[CONTINUUM LAB] Rendering hypnotic looping GIF with slow-motion and dynamic zoom ({n_frames} frames @ {fps} FPS)...")
    anim.save(str(output_path), writer="pillow", fps=fps)
    plt.close()
    print(f"[SUCCESS] Hypnotic animation GIF ready at: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_hypnotic_gif()
