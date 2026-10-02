"""
Continuum Lab — Classical Mechanics & Dynamical Systems
Division: 02 Dinamica y Vibraciones / 02 Mecanismo Coriolis Collarin
Module: generate_plots.py

High-Resolution Diagnostic & Analytical Kinematics Plotter (Publication Grade 300 DPI).
Exports multi-panel figures for cyclic Coriolis dynamics, phase portraits, and vector breakdowns.
"""

import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from src.physics.coriolis_kinematics import CoriolisMechanismParams, CoriolisKinematicsSolver
from src.physics.harmonic_motion import HarmonicCoriolisAnalyzer


def render_kinematic_diagnostics(output_path: Path = None):
    """Generates a comprehensive 6-panel analytical diagnostic figure."""
    if output_path is None:
        workspace_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        output_dir = workspace_root / "RENDERS" / "Coriolis_Mechanism"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "Coriolis_Kinematics_Diagnostic_300DPI.png"

    # Solver y generador de ciclo
    params = CoriolisMechanismParams(L1=1.0, d=1.55, omega1=2.5, arm_extension=1.7)
    solver = CoriolisKinematicsSolver(params)
    analyzer = HarmonicCoriolisAnalyzer(solver)
    data = analyzer.compute_cyclic_harmonics(n_points=1200)

    states = solver.generate_cycle(1200)
    theta1_deg = np.array([s.theta1 * 180.0 / np.pi for s in states])
    time_sec = np.array([s.time for s in states])

    # Variables
    a_cor = np.array([s.a_coriolis_mag for s in states])
    v_rel = np.array([s.v_rel for s in states])
    omega2 = np.array([s.omega2 for s in states])
    alpha2 = np.array([s.alpha2 for s in states])
    r2 = np.array([s.r2 for s in states])
    a_rel = np.array([s.a_rel for s in states])
    a_cent = np.array([-s.omega2**2 * s.r2 for s in states])
    a_euler = np.array([s.alpha2 * s.r2 for s in states])

    # Configuración estética oscura Continuum Lab
    plt.style.use("dark_background")
    fig = plt.figure(figsize=(16, 11), dpi=300, facecolor="#07090e")
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.38, wspace=0.25)

    c_cyan = "#00f0ff"
    c_magenta = "#ff007f"
    c_lime = "#39ff14"
    c_amber = "#ffb800"
    c_purple = "#a855f7"
    c_grid = "rgba(255,255,255,0.08)"

    # Panel 1: Aceleración de Coriolis vs Ángulo de Manivela
    ax1 = fig.add_subplot(gs[0, 0], facecolor="#0d1117")
    ax1.plot(theta1_deg, a_cor, color=c_cyan, lw=2.2, label=r"$a_{cor} = 2\,\omega_2\,\dot{r}_2$")
    ax1.axhline(0, color="gray", lw=0.8, ls="--", alpha=0.5)
    ax1.set_title("1. Aceleración de Coriolis Instantánea en Función de $\\theta_1$", color="#e6edf3", fontsize=11, fontweight="bold")
    ax1.set_xlabel(r"Ángulo de Manivela $\theta_1$ [grados]", color="#8b949e", fontsize=9)
    ax1.set_ylabel(r"$a_{cor}$ [$\mathrm{m/s^2}$]", color="#8b949e", fontsize=9)
    ax1.grid(True, color="#21262d", ls=":", alpha=0.8)
    ax1.legend(loc="upper right", framealpha=0.4, fontsize=9)

    # Panel 2: Descomposición de la Velocidad Relativa y Rotacional
    ax2 = fig.add_subplot(gs[0, 1], facecolor="#0d1117")
    ax2.plot(theta1_deg, v_rel, color=c_lime, lw=2.0, label=r"Deslizamiento $\dot{r}_2$ ($v_{rel}$)")
    ax2.plot(theta1_deg, omega2, color=c_amber, lw=2.0, label=r"Velocidad Angular $\omega_2$ [rad/s]")
    ax2.axhline(0, color="gray", lw=0.8, ls="--", alpha=0.5)
    ax2.set_title(r"2. Velocidades Acopladas: Deslizamiento $\dot{r}_2$ vs Rotación $\omega_2$", color="#e6edf3", fontsize=11, fontweight="bold")
    ax2.set_xlabel(r"Ángulo $\theta_1$ [grados]", color="#8b949e", fontsize=9)
    ax2.set_ylabel(r"Magnitud [m/s, rad/s]", color="#8b949e", fontsize=9)
    ax2.grid(True, color="#21262d", ls=":", alpha=0.8)
    ax2.legend(loc="upper right", framealpha=0.4, fontsize=9)

    # Panel 3: Descomposición de los 4 Términos de Aceleración en Marco Móvil
    ax3 = fig.add_subplot(gs[1, 0], facecolor="#0d1117")
    ax3.plot(theta1_deg, a_cor, color=c_cyan, lw=2.0, label=r"Coriolis ($2\omega_2 \dot{r}_2$)")
    ax3.plot(theta1_deg, a_cent, color=c_amber, lw=1.8, ls="--", label=r"Centrípeta ($-\omega_2^2 r_2$)")
    ax3.plot(theta1_deg, a_euler, color=c_magenta, lw=1.8, ls="-.", label=r"Euler / Tangencial ($\alpha_2 r_2$)")
    ax3.plot(theta1_deg, a_rel, color=c_lime, lw=1.5, ls=":", label=r"Relativa ($\ddot{r}_2$)")
    ax3.set_title("3. Balance de Aceleraciones en el Marco Móvil de la Barra 2", color="#e6edf3", fontsize=11, fontweight="bold")
    ax3.set_xlabel(r"Ángulo $\theta_1$ [grados]", color="#8b949e", fontsize=9)
    ax3.set_ylabel(r"Aceleración [$\mathrm{m/s^2}$]", color="#8b949e", fontsize=9)
    ax3.grid(True, color="#21262d", ls=":", alpha=0.8)
    ax3.legend(loc="lower right", framealpha=0.4, fontsize=8)

    # Panel 4: Plano de Fase Hipnótico (v_rel vs omega_2) - Ciclo Límite
    ax4 = fig.add_subplot(gs[1, 1], facecolor="#0d1117")
    ax4.plot(v_rel, omega2, color=c_cyan, lw=2.2)
    ax4.scatter([v_rel[0]], [omega2[0]], color=c_magenta, s=60, zorder=5, label=r"Inicio $\theta_1=0$")
    ax4.set_title(r"4. Retrato de Fase Cíclico: $\dot{r}_2$ vs $\omega_2$ (Órbita Estable)", color="#e6edf3", fontsize=11, fontweight="bold")
    ax4.set_xlabel(r"Velocidad de Deslizamiento $\dot{r}_2$ [m/s]", color="#8b949e", fontsize=9)
    ax4.set_ylabel(r"Velocidad Angular $\omega_2$ [rad/s]", color="#8b949e", fontsize=9)
    ax4.grid(True, color="#21262d", ls=":", alpha=0.8)
    ax4.legend(loc="upper right", framealpha=0.4, fontsize=9)

    # Panel 5: Hodógrafo Vectorial de Aceleración de Coriolis (Espacio Cartesiano)
    ax5 = fig.add_subplot(gs[2, 0], facecolor="#0d1117")
    ax5.plot(data["hodograph_x"], data["hodograph_y"], color=c_magenta, lw=2.2)
    ax5.axhline(0, color="gray", lw=0.6, ls="--", alpha=0.4)
    ax5.axvline(0, color="gray", lw=0.6, ls="--", alpha=0.4)
    ax5.set_title(r"5. Hodógrafo Vectorial $\vec{a}_{cor}$ en el Plano Cartesiano", color="#e6edf3", fontsize=11, fontweight="bold")
    ax5.set_xlabel(r"$a_{cor,x}$ [$\mathrm{m/s^2}$]", color="#8b949e", fontsize=9)
    ax5.set_ylabel(r"$a_{cor,y}$ [$\mathrm{m/s^2}$]", color="#8b949e", fontsize=9)
    ax5.grid(True, color="#21262d", ls=":", alpha=0.8)
    ax5.set_aspect("equal", "datalim")

    # Panel 6: Espectro Armónico Fourier de la Aceleración de Coriolis
    ax6 = fig.add_subplot(gs[2, 1], facecolor="#0d1117")
    orders = [h["harmonic_order"] for h in data["dominant_harmonics"]]
    amps = [h["amplitude"] for h in data["dominant_harmonics"]]
    ax6.bar(orders, amps, color=c_purple, width=0.5, edgecolor=c_cyan, alpha=0.85)
    ax6.set_title("6. Espectro Armónico Dominante de Coriolis (Transformada FFT)", color="#e6edf3", fontsize=11, fontweight="bold")
    ax6.set_xlabel("Orden Armónico (Múltiplo de $\\omega_1$)", color="#8b949e", fontsize=9)
    ax6.set_ylabel("Amplitud Espectral [$\\mathrm{m/s^2}$]", color="#8b949e", fontsize=9)
    ax6.grid(True, color="#21262d", ls=":", alpha=0.8)

    # Título General y Meta-datos
    fig.suptitle(
        "CONTINUUM LAB • ANÁLISIS CINEMÁTICO RIGUROSO — ACELERACIÓN DE CORIOLIS\n"
        r"Sistema Mecánico de 2 Barras con Collarín Deslizante ($L_1=1.00\,\mathrm{m},\,d=1.55\,\mathrm{m},\,\omega_1=2.50\,\mathrm{rad/s}$)",
        color="#00f0ff",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )

    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"[SUCCESS] High-resolution diagnostic plot saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    render_kinematic_diagnostics()
