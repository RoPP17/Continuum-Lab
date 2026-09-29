"""
Continuum Lab — Visual Asset Generator
Module: 01 Mecanica de Fluidos / 02 Singularidad Navier Stokes Blowup
Generates High-Resolution Hero Previews & Animated GIF for documentation and social media.

Deliverables:
  - navier_stokes_blowup_hero.png (3D/2D Streamlines + Annular Pulses + Pressure Depth)
  - core_annulus_cross_section.png (r-z meridional section showing 3 radial zones)
  - reynolds_stress_cancellation.png (Target annular stress vs pulse flux cone representation)
  - navier_stokes_blowup_preview.gif (Animated multi-frame physical singularity contraction)
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from pathlib import Path
import os
import sys

# Add project root to sys.path
project_dir = Path(__file__).resolve().parent.parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from src.physics.navier_stokes_blowup import NavierStokesBlowupSimulation, BlowupParameters

# Configure Continuum Lab Cybernetic Theme
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#1e293b'
plt.rcParams['axes.linewidth'] = 1.0


def generate_hero_composite(output_dir: Path):
    """
    Generates navier_stokes_blowup_hero.png:
    Rich 3-panel scientific hero visualization illustrating the finite-time blowup structure.
    """
    sim = NavierStokesBlowupSimulation()
    fig = plt.figure(figsize=(16, 9), facecolor="#0a0a0c")

    # Colors
    c_bg = "#0a0a0c"
    c_card = "#0d1117"
    c_cyan = "#00f0ff"
    c_magenta = "#ff007f"
    c_amber = "#ffaa00"
    c_emerald = "#39ff14"
    c_text = "#e6edf3"
    c_muted = "#8b949e"

    # -------------------------------------------------------------------------
    # Panel 1 (Left): 3D Streamline Vortex Eye & Needle Contraction
    # -------------------------------------------------------------------------
    ax1 = fig.add_subplot(1, 3, 1, projection='3d', facecolor=c_bg)
    ax1.set_facecolor(c_bg)

    # Generate helical vortex streamlines spiraling into the origin
    num_streamlines = 14
    for i in range(num_streamlines):
        theta_0 = i * (2.0 * np.pi / num_streamlines)
        s_param = np.linspace(0.05, 1.8, 200)
        # Inward contraction r ~ s^(0.7), z ~ s^(0.6) * sign
        z_sign = 1 if i % 2 == 0 else -1
        r_line = 0.85 * (s_param**0.8) + 0.02
        z_line = z_sign * (1.1 * s_param**0.9 + 0.05)
        # Accelerating angle theta
        theta_line = theta_0 + 8.5 / (s_param**0.5)

        x_line = r_line * np.cos(theta_line)
        y_line = r_line * np.sin(theta_line)

        # Color gradient: Cyan near core, Deep Purple/Blue at exterior
        colors_line = plt.cm.cool(np.linspace(0.1, 0.95, len(s_param)))
        for seg in range(len(s_param) - 1):
            ax1.plot(
                x_line[seg:seg+2], y_line[seg:seg+2], z_line[seg:seg+2],
                color=colors_line[seg], lw=1.2 + 1.2 * (1.0 - s_param[seg] / 1.8), alpha=0.85
            )

    # Add Annular Wave Pulse Rings
    for ring_z in [-0.4, 0.0, 0.4]:
        phi_ring = np.linspace(0, 2*np.pi, 100)
        r_pulse = 0.55
        x_ring = r_pulse * np.cos(phi_ring)
        y_ring = r_pulse * np.sin(phi_ring)
        z_ring = np.full_like(phi_ring, ring_z)
        # Modulated wave pulse
        wave_mod = 0.06 * np.cos(8 * phi_ring)
        ax1.plot(x_ring + wave_mod, y_ring + wave_mod, z_ring, color=c_magenta, lw=2.2, alpha=0.9, ls="--")

    # Center needle core
    z_needle = np.linspace(-1.2, 1.2, 50)
    ax1.plot(np.zeros_like(z_needle), np.zeros_like(z_needle), z_needle, color=c_emerald, lw=3.0, alpha=0.95)

    ax1.set_title("VORTEX SPIRAL & SLENDER CORE", color=c_cyan, fontsize=12, fontweight='bold', pad=15)
    ax1.set_axis_off()
    ax1.view_init(elev=24, azim=48)

    # -------------------------------------------------------------------------
    # Panel 2 (Center): Meridional r-z Section & 3 Radial Zones
    # -------------------------------------------------------------------------
    ax2 = fig.add_subplot(1, 3, 2, facecolor=c_card)
    r_grid = np.linspace(0.001, 1.4, 120)
    z_grid = np.linspace(-1.0, 1.0, 120)
    R, Z = np.meshgrid(r_grid, z_grid)

    t_eval = 0.94
    tau_eval = sim.get_tau(t_eval)
    q_eval = sim.solve_concentration_scale_q(Z, tau_eval)
    X_grid = (R**2) / (2.0 * q_eval)
    scale_v = q_eval**(-sim.params.A)
    E_grid = sim.azimuthal_profile_E(X_grid, Z / (q_eval**sim.params.D))
    u_theta_grid = scale_v * E_grid

    # Background contour of azimuthal swirl speed
    im = ax2.contourf(R, Z, u_theta_grid, levels=30, cmap="inferno", alpha=0.88)
    cbar = plt.colorbar(im, ax=ax2, orientation='horizontal', pad=0.12, fraction=0.045)
    cbar.ax.tick_params(labelsize=8, colors=c_text)
    cbar.set_label("Swirl Speed |u_theta| (m/s)", color=c_text, fontsize=9)

    # Zone dividers
    # Inner core edge X = Xa (0.5)
    r_core_edge = np.sqrt(2.0 * q_eval * sim.params.X_a)[:, 60]
    ax2.axvline(x=np.mean(r_core_edge), color=c_cyan, lw=1.8, ls=":", label="Core Edge (X_a = 0.5)")
    # Annulus outer edge X = Xb (2.8)
    r_ann_edge = np.sqrt(2.0 * q_eval * sim.params.X_b)[:, 60]
    ax2.axvline(x=np.mean(r_ann_edge), color=c_magenta, lw=1.8, ls=":", label="Exterior Edge (X_b = 2.8)")

    # Flow arrows (u_r, u_z)
    skip = 8
    R_sub = R[::skip, ::skip]
    Z_sub = Z[::skip, ::skip]
    X_sub = X_grid[::skip, ::skip]
    q_sub = q_eval[::skip, ::skip]
    eta_sub = Z_sub / (q_sub**sim.params.D)
    U_sub = sim.axial_profile_U(X_sub, eta_sub)
    u_z_sub = (q_sub**(-sim.params.A)) * U_sub
    u_r_sub = sim.radial_profile_V0(R_sub, X_sub, eta_sub, q_sub)

    ax2.quiver(R_sub, Z_sub, u_r_sub, u_z_sub, color="#ffffff", alpha=0.75, width=0.0035, scale=45)

    ax2.set_title("MERIDIONAL (r, z) FLOW & ZONES", color=c_cyan, fontsize=12, fontweight='bold', pad=12)
    ax2.set_xlabel("Radius r (m)", color=c_text, fontsize=9)
    ax2.set_ylabel("Axial Height z (m)", color=c_text, fontsize=9)
    ax2.tick_params(colors=c_muted, labelsize=8)
    ax2.legend(loc="upper right", facecolor=c_card, edgecolor=c_muted, labelcolor=c_text, fontsize=8)

    # -------------------------------------------------------------------------
    # Panel 3 (Right): Divergence vs Finite Energy Proof
    # -------------------------------------------------------------------------
    ax3 = fig.add_subplot(1, 3, 3, facecolor=c_card)
    t_span = np.linspace(0.0, 0.9995, 200)
    m_list = [sim.compute_global_metrics(t) for t in t_span]

    tau_arr = np.array([m["tau"] for m in m_list])
    u_max_arr = np.array([m["u_max"] for m in m_list])
    e_tot_arr = np.array([m["energy_total"] for m in m_list])
    e_core_arr = np.array([m["energy_core"] for m in m_list])
    lr_arr = np.array([m["l_r"] for m in m_list])

    # Left y-axis: Velocity (Log scale)
    color_u = c_amber
    ax3.set_xlabel("Time t (s) -> Singular Time T* = 1.0", color=c_text, fontsize=9)
    ax3.set_ylabel("Peak Velocity ||u||_inf (m/s)", color=color_u, fontsize=9, fontweight='bold')
    line1 = ax3.semilogy(t_span, u_max_arr, color=color_u, lw=2.4, label="Max Velocity ||u|| -> Inf")
    ax3.tick_params(axis='y', labelcolor=color_u, colors=c_muted, labelsize=8)
    ax3.tick_params(axis='x', colors=c_muted, labelsize=8)
    ax3.grid(True, color="#1e293b", alpha=0.6, ls="--")

    # Right y-axis: Energy (Linear scale)
    ax3_twin = ax3.twinx()
    color_e = c_emerald
    ax3_twin.set_ylabel("Kinetic Energy E(t) (Joules)", color=color_e, fontsize=9, fontweight='bold')
    line2 = ax3_twin.plot(t_span, e_tot_arr, color=color_e, lw=2.4, label="Total Energy (Bounded!)")
    line3 = ax3_twin.plot(t_span, e_core_arr, color=c_cyan, lw=1.8, ls="--", label="Core Energy -> 0")
    ax3_twin.tick_params(axis='y', labelcolor=color_e, colors=c_muted, labelsize=8)
    ax3_twin.set_ylim(0, 3.5)

    # Combined legend
    lines = line1 + line2 + line3
    labels = [l.get_label() for l in lines]
    ax3.legend(lines, labels, loc="center left", facecolor=c_card, edgecolor=c_muted, labelcolor=c_text, fontsize=8)
    ax3.set_title("BLOWUP VS ENERGY BOUNDEDNESS", color=c_cyan, fontsize=12, fontweight='bold', pad=12)

    plt.tight_layout()
    hero_path = output_dir / "navier_stokes_blowup_hero.png"
    plt.savefig(hero_path, dpi=300, facecolor=c_bg, edgecolor='none')
    plt.close()
    print(f"[CONTINUUM LAB] High-Res Hero Preview created: {hero_path}")


def generate_reynolds_stress_diagram(output_dir: Path):
    """
    Generates reynolds_stress_cancellation.png:
    Visualizes the target stress cone and positive wave covariance representation.
    """
    fig, ax = plt.subplots(figsize=(10, 6), facecolor="#0a0a0c")
    ax.set_facecolor("#0d1117")

    c_cyan = "#00f0ff"
    c_magenta = "#ff007f"
    c_amber = "#ffaa00"
    c_text = "#e6edf3"
    c_muted = "#8b949e"

    sim = NavierStokesBlowupSimulation()
    r = np.linspace(0.01, 1.2, 100)
    theta = np.zeros_like(r)
    z = np.zeros_like(r)
    t = 0.95

    stress = sim.evaluate_annular_stress_and_pulses(r, theta, z, t)
    T_theta = stress["T_r_theta"]
    T_z = stress["T_r_z"]
    A_w = stress["A_wave"]

    ax.plot(r, T_theta, color=c_magenta, lw=2.5, label=r"Azimuthal Stress Flux $T_{r\theta} = \langle w_r w_\theta \rangle$")
    ax.plot(r, np.abs(T_z) * 10, color=c_amber, lw=2.0, ls="-.", label=r"Axial Stress Flux $|T_{rz}| \times 10 = |\langle w_r w_z \rangle| \times 10$")
    ax.plot(r, A_w, color=c_cyan, lw=2.0, ls="--", label=r"Oscillatory Pulse Amplitude $A_{wave} \sim q^{-1/2 - h/2}$")

    # Shaded Annular Support
    Xa = sim.params.X_a
    Xb = sim.params.X_b
    q = sim.get_tau(t)
    ra = np.sqrt(2.0 * q * Xa)
    rb = np.sqrt(2.0 * q * Xb)

    ax.axvspan(ra, rb, color=c_magenta, alpha=0.15, label=r"Annular Shear Layer $[X_a, X_b]$")
    ax.axvline(ra, color=c_cyan, ls=":", lw=1.5)
    ax.axvline(rb, color=c_magenta, ls=":", lw=1.5)

    ax.set_title("ANNULAR REYNOLDS STRESS FLUX CANCELLATION", color=c_cyan, fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Radius r (m)", color=c_text, fontsize=10)
    ax.set_ylabel("Stress Divergence & Flux Amplitude (Pa)", color=c_text, fontsize=10)
    ax.tick_params(colors=c_muted, labelsize=9)
    ax.grid(True, color="#1e293b", alpha=0.6, ls="--")
    ax.legend(facecolor="#0d1117", edgecolor=c_muted, labelcolor=c_text, fontsize=9)

    plt.tight_layout()
    stress_path = output_dir / "reynolds_stress_cancellation.png"
    plt.savefig(stress_path, dpi=300, facecolor="#0a0a0c", edgecolor='none')
    plt.close()
    print(f"[CONTINUUM LAB] Reynolds Stress Diagram created: {stress_path}")


def generate_animated_preview_gif(output_dir: Path):
    """
    Generates navier_stokes_blowup_preview.gif:
    24-frame looping preview showing progressive core collapse, accelerating swirl, and pulse rings.
    """
    from PIL import Image
    import io

    sim = NavierStokesBlowupSimulation()
    frames = []
    num_frames = 24
    times = np.linspace(0.1, 0.985, num_frames)

    for idx, t in enumerate(times):
        fig, ax = plt.subplots(figsize=(6, 6), facecolor="#0a0a0c")
        ax.set_facecolor("#0a0a0c")

        tau = sim.get_tau(t)
        q = tau
        lr = np.sqrt(tau)

        # Plot rotating particles at radius r and angle theta
        num_p = 250
        r_p = np.random.uniform(0.01, 1.2, num_p)
        theta_p = np.random.uniform(0, 2*np.pi, num_p)
        # Spin angle advances faster for smaller radii: omega ~ r^(-1) * tau^(-0.5)
        d_theta = (1.5 / (r_p + 0.05)) * (tau**(-0.5)) * (idx * 0.04)
        theta_current = theta_p + d_theta

        x_p = r_p * np.cos(theta_current)
        y_p = r_p * np.sin(theta_current)

        # Color based on radius (Cyan in core, Magenta in annulus, Blue outside)
        X_p = (r_p**2) / (2.0 * q)
        colors = []
        for x_val in X_p:
            if x_val < 0.5:
                colors.append("#00f0ff")  # Core
            elif x_val <= 2.8:
                colors.append("#ff007f")  # Annulus
            else:
                colors.append("#38bdf8")  # Exterior

        sizes = 12.0 / (r_p + 0.1)
        ax.scatter(x_p, y_p, c=colors, s=sizes, alpha=0.75, edgecolors='none')

        # Draw Annulus Rings
        phi_circle = np.linspace(0, 2*np.pi, 100)
        ra = np.sqrt(2.0 * q * sim.params.X_a)
        rb = np.sqrt(2.0 * q * sim.params.X_b)
        ax.plot(ra * np.cos(phi_circle), ra * np.sin(phi_circle), color="#00f0ff", lw=1.2, ls=":")
        ax.plot(rb * np.cos(phi_circle), rb * np.sin(phi_circle), color="#ff007f", lw=1.2, ls=":")

        # Center Singularity Core
        ax.scatter([0], [0], color="#ffffff", s=60, zorder=5)

        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-1.1, 1.1)
        ax.set_title(f"t = {t:.3f} s | ||u||_max = {sim.compute_global_metrics(t)['u_max']:.1f} m/s",
                     color="#00f0ff", fontsize=10, fontweight='bold', pad=10)
        ax.set_axis_off()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, facecolor="#0a0a0c")
        buf.seek(0)
        frames.append(Image.open(buf))
        plt.close()

    gif_path = output_dir / "navier_stokes_blowup_preview.gif"
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=75,
        loop=0
    )
    print(f"[CONTINUUM LAB] Animated GIF preview created: {gif_path}")


def generate_all_visuals():
    workspace_root = project_dir.parent.parent
    capturas_dir = workspace_root / "RENDERS" / "5 Singularidad Navier Stokes" / "extra" / "capturas"
    capturas_dir.mkdir(parents=True, exist_ok=True)

    print("=================================================================")
    print("[CONTINUUM LAB] Generating Scientific Visual Assets...")
    print("=================================================================")
    generate_hero_composite(capturas_dir)
    generate_reynolds_stress_diagram(capturas_dir)
    generate_animated_preview_gif(capturas_dir)
    print("=================================================================")
    print("[CONTINUUM LAB] All visual assets generated successfully!")
    print("=================================================================")


if __name__ == "__main__":
    generate_all_visuals()
