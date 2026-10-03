"""
Continuum Lab — Visual Production Engine
Module: 01 Mecanica de Fluidos / 03 Desprendimiento Capa Limite y Stall Aerodinamico
High-Resolution Diagnostic Previews & Animated GIF Generator

Generates:
  - aerodynamic_stall_hero.png (300 DPI Comprehensive 4-panel diagnostic poster)
  - stall_9_16_hero.png (1080x1920 Vertical Hero Preview for social cover)
  - boundary_layer_velocity_profiles.png (Boundary layer velocity profiles & wall shear)
  - boundary_layer_separation_preview.gif (Animated streamline detachment loop)
"""

import os
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch, Rectangle
from matplotlib.animation import FuncAnimation, PillowWriter

from src.physics.aerodynamic_stall import AerodynamicStallSimulation, AirfoilParameters


def setup_dark_style():
    plt.style.use("dark_background")
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"],
        "axes.edgecolor": "#1f2937",
        "axes.facecolor": "#0d1117",
        "figure.facecolor": "#0a0a0c",
        "grid.color": "#1f2937",
        "grid.linestyle": ":",
        "grid.alpha": 0.6,
        "text.color": "#e6edf3",
        "axes.labelcolor": "#8b949e",
        "xtick.color": "#8b949e",
        "ytick.color": "#8b949e",
    })


def generate_horizontal_hero(output_path: str, sim: AerodynamicStallSimulation):
    """
    Generates a 300 DPI master 4-panel scientific diagnostic chart.
    """
    setup_dark_style()
    fig = plt.figure(figsize=(18, 10), dpi=300)
    fig.suptitle(
        "CONTINUUM LAB // AERODYNAMIC STALL & BOUNDARY LAYER SEPARATION DYNAMICS\n"
        r"NACA 0012 Airfoil | $\partial p / \partial x > 0$ Adverse Gradient | $(\partial u / \partial y)_{\mathrm{wall}} = 0$ | $C_L$ 74% Collapse",
        fontsize=15, fontweight="bold", color="#00f0ff", y=0.97
    )

    gs = fig.add_gridspec(2, 2, hspace=0.32, wspace=0.22, left=0.07, right=0.96, top=0.88, bottom=0.08)

    # -------------------------------------------------------------------------
    # Panel 1: Physical Flow Field & Boundary Layer Detachment (Top Left)
    # -------------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_title("1. Massive Boundary Layer Separation at Deep Stall (α = 18.5°)", fontsize=11, fontweight="bold", color="#ffffff", pad=10)

    # Airfoil at alpha = 18.5 deg
    x_coords, y_coords = sim.get_airfoil_polygon(n_points=240)
    alpha_rad = np.radians(18.5)
    # Rotate airfoil around quarter-chord (0.25, 0)
    xc, yc = 0.25, 0.0
    xr = (x_coords - xc) * np.cos(-alpha_rad) - (y_coords - yc) * np.sin(-alpha_rad) + xc
    yr = (x_coords - xc) * np.sin(-alpha_rad) + (y_coords - yc) * np.cos(-alpha_rad) + yc

    ax1.fill(xr, yr, color="#161b22", edgecolor="#00f0ff", linewidth=2.0, zorder=5)

    # Draw Streamlines
    nx, ny = 120, 80
    x_grid = np.linspace(-0.5, 1.8, nx)
    y_grid = np.linspace(-0.8, 1.0, ny)
    X, Y = np.meshgrid(x_grid, y_grid)

    # Vectorized flow model: free stream + deflected flow + massive separated recirculation zone
    U_field = np.ones_like(X) * 50.0
    V_field = np.zeros_like(Y)

    # Recirculating vortex in wake above suction side
    x_core, y_core = 0.65, 0.35
    dx = X - x_core
    dy = Y - y_core
    r2 = dx**2 + dy**2 + 0.05
    # Clockwise recirculation
    U_vortex = -35.0 * (dy / r2) * np.exp(-r2 / 0.35)
    V_vortex = 35.0 * (dx / r2) * np.exp(-r2 / 0.35)

    # Deflection under the wing
    under_mask = (X >= -0.2) & (X <= 1.2) & (Y < yr.min() + 0.1) & (Y > -0.5)
    V_field[under_mask] -= 12.0

    U_tot = U_field + U_vortex
    V_tot = V_field + V_vortex
    speed = np.sqrt(U_tot**2 + V_tot**2)

    strm = ax1.streamplot(
        X, Y, U_tot, V_tot, color=speed, cmap="cool",
        density=1.4, linewidth=1.1, arrowsize=1.0, zorder=3
    )

    # Separation point marker
    x_sep = sim.separation_point(18.5)
    # find location on upper rotated surface near x_sep
    idx_sep = np.argmin(np.abs(x_coords[:len(x_coords)//2] - x_sep))
    ax1.plot(xr[idx_sep], yr[idx_sep], "o", color="#ff0055", markersize=9, zorder=8)
    ax1.annotate(
        r"Separation Point $x_{\mathrm{sep}} \approx 0.15c$" "\n" r"$[\partial u / \partial y]_{\mathrm{wall}} = 0$",
        xy=(xr[idx_sep], yr[idx_sep]), xytext=(xr[idx_sep] - 0.45, yr[idx_sep] + 0.40),
        arrowprops=dict(arrowstyle="->", color="#ff0055", lw=1.5),
        fontsize=9, color="#ff0055", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#1a0b16", edgecolor="#ff0055", alpha=0.9)
    )

    # Recirculation zone label
    ax1.text(0.70, 0.45, "Turbulent Separated\nRecirculation Bubble", color="#ffaa00", fontsize=9, fontweight="bold", ha="center")

    ax1.set_xlim(-0.4, 1.6)
    ax1.set_ylim(-0.6, 0.9)
    ax1.set_aspect("equal")
    ax1.set_xlabel("Chord Normalized x / c", fontsize=9)
    ax1.set_ylabel("y / c", fontsize=9)
    ax1.grid(True)

    # -------------------------------------------------------------------------
    # Panel 2: Pressure Distribution & Adverse Gradient (Top Right)
    # -------------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_title("2. Surface Pressure Distribution $C_p(x/c)$: Suction Peak vs Separation", fontsize=11, fontweight="bold", color="#ffffff", pad=10)

    cp_4 = sim.pressure_distribution(4.0)
    cp_18 = sim.pressure_distribution(18.5)

    # In aerodynamics, Cp is conventionally plotted inverted (-Cp upwards)
    ax2.plot(cp_4["xc"], cp_4["cp_upper"], label=r"Upper Surface ($\alpha = 4.0^\circ$ Attached)", color="#00f0ff", lw=2.2)
    ax2.plot(cp_4["xc"], cp_4["cp_lower"], label=r"Lower Surface ($\alpha = 4.0^\circ$)", color="#00f0ff", lw=1.5, linestyle="--")

    ax2.plot(cp_18["xc"], cp_18["cp_upper"], label=r"Upper Surface ($\alpha = 18.5^\circ$ Stalled)", color="#ff0055", lw=2.4)
    ax2.plot(cp_18["xc"], cp_18["cp_lower"], label=r"Lower Surface ($\alpha = 18.5^\circ$)", color="#ff0055", lw=1.5, linestyle="--")

    # Fill area showing adverse pressure gradient
    ax2.fill_between(cp_18["xc"], cp_18["cp_upper"], cp_4["cp_upper"], where=(cp_18["cp_upper"] > cp_4["cp_upper"]),
                     color="#ff0055", alpha=0.18, label="Lift Deficit (Suction Collapse)")

    ax2.annotate(
        r"Adverse Pressure Gradient" "\n" r"$\partial p / \partial x > 0 \Rightarrow \tau_w \to 0$",
        xy=(0.45, -0.6), xytext=(0.50, -1.8),
        arrowprops=dict(arrowstyle="->", color="#ffaa00", lw=1.5),
        fontsize=9, color="#ffaa00", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#1b170d", edgecolor="#ffaa00", alpha=0.9)
    )

    ax2.invert_yaxis()
    ax2.set_xlabel("Chord Normalized x / c", fontsize=9)
    ax2.set_ylabel(r"Pressure Coefficient $C_p$", fontsize=9)
    ax2.legend(loc="lower right", fontsize=8, facecolor="#0d1117", edgecolor="#1f2937")
    ax2.grid(True)

    # -------------------------------------------------------------------------
    # Panel 3: Boundary Layer Velocity Profiles (Pohlhausen) (Bottom Left)
    # -------------------------------------------------------------------------
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_title(r"3. Boundary Layer Profiles: $\left.\frac{\partial u}{\partial y}\right|_{\mathrm{wall}} = 0$ Separation Criterion", fontsize=11, fontweight="bold", color="#ffffff", pad=10)

    eta = np.linspace(0.0, 1.0, 100)
    p_attached = sim.pohlhausen_velocity_profile(eta, lambda_param=+2.0)
    p_zero = sim.pohlhausen_velocity_profile(eta, lambda_param=0.0)
    p_favorable = sim.pohlhausen_velocity_profile(eta, lambda_param=-6.0)
    p_sep = sim.pohlhausen_velocity_profile(eta, lambda_param=-12.0)
    p_reverse = sim.pohlhausen_velocity_profile(eta, lambda_param=-15.0)

    ax3.plot(p_attached, eta, label=r"Favorable $\Lambda = +2.0$ (Accelerating)", color="#39ff14", lw=1.8)
    ax3.plot(p_zero, eta, label=r"Blasius Flat Plate $\Lambda = 0.0$", color="#8b949e", lw=1.5, linestyle=":")
    ax3.plot(p_favorable, eta, label=r"Mild Adverse $\Lambda = -6.0$ (Decelerating)", color="#ffaa00", lw=1.8)
    ax3.plot(p_sep, eta, label=r"SEPARATION POINT $\Lambda = -12.0$ [$\tau_w = 0$]", color="#ff0055", lw=2.5)
    ax3.plot(p_reverse, eta, label=r"Detached Reverse Flow $\Lambda = -15.0$ [Backflow]", color="#d600ff", lw=2.2, linestyle="--")

    ax3.axvline(0.0, color="#ffffff", linestyle="-", lw=1.0, alpha=0.7)
    # Highlight backflow area
    ax3.fill_betweenx(eta[:25], p_reverse[:25], 0.0, color="#d600ff", alpha=0.35, label="Recirculation Backflow")

    ax3.annotate(
        r"Zero Wall Shear: $\left.\frac{\partial u}{\partial y}\right|_{y=0} = 0$",
        xy=(0.0, 0.0), xytext=(0.20, 0.12),
        arrowprops=dict(arrowstyle="->", color="#ff0055", lw=1.5),
        fontsize=9, color="#ff0055", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#1a0b16", edgecolor="#ff0055", alpha=0.9)
    )

    ax3.set_xlabel(r"Normalized Streamwise Velocity $u / U_e$", fontsize=9)
    ax3.set_ylabel(r"Wall-Normal Distance $\eta = y / \delta$", fontsize=9)
    ax3.set_xlim(-0.25, 1.15)
    ax3.set_ylim(0.0, 1.05)
    ax3.legend(loc="upper left", fontsize=8, facecolor="#0d1117", edgecolor="#1f2937")
    ax3.grid(True)

    # -------------------------------------------------------------------------
    # Panel 4: Aerodynamic Polars & 74% Collapse (Bottom Right)
    # -------------------------------------------------------------------------
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_title("4. Aerodynamic Lift & Drag Polar: The 74% Collapse & Drag Explosion", fontsize=11, fontweight="bold", color="#ffffff", pad=10)

    alphas = np.linspace(-2.0, 22.0, 120)
    cl_vals = [sim.lift_coefficient(a) for a in alphas]
    cl_lin = [sim.thin_airfoil_lift(a) for a in alphas]
    cd_vals = [sim.drag_coefficient(a) for a in alphas]

    line_cl, = ax4.plot(alphas, cl_vals, label=r"Actual Lift $C_L(\alpha)$", color="#00f0ff", lw=2.6)
    line_lin, = ax4.plot(alphas, cl_lin, label=r"Thin Airfoil Theory $C_L = 2\pi\alpha$", color="#8b949e", lw=1.5, linestyle="--")

    # Critical annotations
    cl_4 = sim.lift_coefficient(4.0)
    cl_stall = sim.lift_coefficient(15.5)
    cl_18 = sim.lift_coefficient(18.5)

    ax4.plot(4.0, cl_4, "o", color="#39ff14", markersize=8, zorder=6)
    ax4.text(4.0 + 0.5, cl_4 - 0.08, r"$\alpha = 4^\circ \rightarrow C_L = 0.44$", color="#39ff14", fontsize=8, fontweight="bold")

    ax4.plot(15.5, cl_stall, "o", color="#ffaa00", markersize=8, zorder=6)
    ax4.text(15.5 - 4.5, cl_stall + 0.06, r"Stall Peak $C_{L,\max} = 1.55$", color="#ffaa00", fontsize=8, fontweight="bold")

    ax4.plot(18.5, cl_18, "o", color="#ff0055", markersize=9, zorder=6)
    ax4.annotate(
        r"$\mathbf{-74\%}$ Lift Crash!" "\n" r"$C_L = 0.40$ at $18.5^\circ$",
        xy=(18.5, cl_18), xytext=(12.0, 0.45),
        arrowprops=dict(arrowstyle="->", color="#ff0055", lw=2.0),
        fontsize=9, color="#ff0055", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#1a0b16", edgecolor="#ff0055", alpha=0.95)
    )

    ax4.set_xlabel("Angle of Attack α [degrees]", fontsize=9)
    ax4.set_ylabel(r"Lift Coefficient $C_L$", color="#00f0ff", fontsize=9)
    ax4.tick_params(axis="y", labelcolor="#00f0ff")
    ax4.set_ylim(-0.3, 1.9)
    ax4.set_xlim(-2.0, 22.0)
    ax4.grid(True)

    # Secondary axis for Drag Coefficient C_D
    ax4_drag = ax4.twinx()
    line_cd, = ax4_drag.plot(alphas, cd_vals, label=r"Drag Coefficient $C_D(\alpha)$", color="#ff007f", lw=2.2, linestyle="-.")
    ax4_drag.set_ylabel(r"Drag Coefficient $C_D$", color="#ff007f", fontsize=9)
    ax4_drag.tick_params(axis="y", labelcolor="#ff007f")
    ax4_drag.set_ylim(0.0, 0.35)

    # Combined legend
    lines = [line_cl, line_lin, line_cd]
    labels = [l.get_label() for l in lines]
    ax4.legend(lines, labels, loc="upper left", fontsize=8, facecolor="#0d1117", edgecolor="#1f2937")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[CONTINUUM LAB] Horizontal Hero Preview created: {output_path}")


def generate_vertical_hero(output_path: str, sim: AerodynamicStallSimulation):
    """
    Generates a 1080x1920 (9:16) poster hero preview.
    """
    setup_dark_style()
    fig, ax = plt.subplots(figsize=(6.075, 10.8), dpi=177.778)  # Exactly 1080 x 1920 px
    fig.patch.set_facecolor("#0a0a0c")
    ax.set_facecolor("#0a0a0c")

    # Remove standard ticks for clean cybernetic presentation
    ax.set_xlim(-0.6, 1.8)
    ax.set_ylim(-1.6, 2.4)
    ax.axis("off")

    # Header Card
    hdr = Rectangle((-0.52, 1.55), 2.24, 0.72, facecolor="#0d1117", edgecolor="#00f0ff", linewidth=1.5, zorder=10)
    ax.add_patch(hdr)
    ax.text(0.60, 2.05, r"$\left.\frac{\partial u}{\partial y}\right|_{\mathrm{wall}} = 0 \quad | \quad C_L = 2\pi\alpha$",
            color="#ffffff", fontsize=11, fontweight="bold", ha="center", va="center", zorder=11)
    ax.text(0.60, 1.75, r"$\frac{\partial p}{\partial x} > 0 \Rightarrow \mathrm{ADVERSE\ GRADIENT\ \rightarrow\ STALL}$",
            color="#00f0ff", fontsize=9, ha="center", va="center", zorder=11)

    # Airfoil at 18.5 deg
    x_coords, y_coords = sim.get_airfoil_polygon(n_points=260)
    alpha_rad = np.radians(18.5)
    xc, yc = 0.25, 0.2
    xr = (x_coords - xc) * np.cos(-alpha_rad) - (y_coords - yc) * np.sin(-alpha_rad) + xc
    yr = (x_coords - xc) * np.sin(-alpha_rad) + (y_coords - yc) * np.cos(-alpha_rad) + yc

    ax.fill(xr, yr, color="#161b22", edgecolor="#00f0ff", linewidth=2.4, zorder=6)

    # Detached streamlines
    nx, ny = 90, 90
    xg = np.linspace(-0.5, 1.7, nx)
    yg = np.linspace(-0.6, 1.2, ny)
    X, Y = np.meshgrid(xg, yg)

    U = np.ones_like(X) * 45.0
    V = np.zeros_like(Y)
    dx = X - 0.65
    dy = Y - 0.50
    r2 = dx**2 + dy**2 + 0.04
    U += -38.0 * (dy / r2) * np.exp(-r2 / 0.30)
    V += 38.0 * (dx / r2) * np.exp(-r2 / 0.30)

    speed = np.sqrt(U**2 + V**2)
    ax.streamplot(X, Y, U, V, color=speed, cmap="cool", density=1.3, linewidth=1.2, arrowsize=1.1, zorder=3)

    # Separation Point
    x_sep = sim.separation_point(18.5)
    idx_sep = np.argmin(np.abs(x_coords[:len(x_coords)//2] - x_sep))
    ax.plot(xr[idx_sep], yr[idx_sep], "o", color="#ff0055", markersize=10, zorder=8)
    ax.text(xr[idx_sep] - 0.05, yr[idx_sep] + 0.28, "SEPARATION POINT\nWall Shear = 0",
            color="#ff0055", fontsize=8, fontweight="bold", ha="right",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#1a0b16", edgecolor="#ff0055"))

    # Telemetry Badge
    tele_box = Rectangle((-0.52, -0.65), 2.24, 0.58, facecolor="#0d1117", edgecolor="#39ff14", linewidth=1.2, zorder=10)
    ax.add_patch(tele_box)
    ax.text(0.60, -0.22, "TELEMETRY READOUT (α = 18.5°)", color="#39ff14", fontsize=9, fontweight="bold", ha="center", zorder=11)
    ax.text(0.60, -0.50, "C_L: 0.403 (-74%)    C_D: 0.280 (+1750%)    x_sep/c: 0.15",
            color="#ffffff", fontsize=8, ha="center", zorder=11)

    # Bottom Community Card
    cta_box = Rectangle((-0.52, -1.45), 2.24, 0.65, facecolor="#0d1117", edgecolor="#ffaa00", linewidth=1.2, zorder=10)
    ax.add_patch(cta_box)
    ax.text(0.60, -1.02, "COMMUNITY CHALLENGE", color="#ffaa00", fontsize=9, fontweight="bold", ha="center", zorder=11)
    ax.text(0.60, -1.30, "Can vortex generators or active suction delay stall?\nDrop your engineering solution below! 👇",
            color="#e6edf3", fontsize=7.5, ha="center", zorder=11)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=177.778, facecolor="#0a0a0c")
    plt.close()
    print(f"[CONTINUUM LAB] 9:16 Hero Preview created: {output_path}")


def generate_animated_preview_gif(output_path: str, sim: AerodynamicStallSimulation):
    """
    Generates an animated GIF preview loop of the pitching wing and boundary layer separation.
    """
    setup_dark_style()
    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
    fig.patch.set_facecolor("#0a0a0c")
    ax.set_facecolor("#0d1117")

    alphas_deg = np.concatenate([
        np.linspace(4.0, 18.5, 24),
        np.linspace(18.5, 4.0, 18)
    ])

    x_coords, y_coords = sim.get_airfoil_polygon(n_points=180)

    def update(frame_idx):
        ax.clear()
        ax.set_facecolor("#0d1117")
        a_deg = alphas_deg[frame_idx]
        a_rad = np.radians(a_deg)

        # Rotate airfoil
        xc, yc = 0.25, 0.0
        xr = (x_coords - xc) * np.cos(-a_rad) - (y_coords - yc) * np.sin(-a_rad) + xc
        yr = (x_coords - xc) * np.sin(-a_rad) + (y_coords - yc) * np.cos(-a_rad) + yc

        ax.fill(xr, yr, color="#161b22", edgecolor="#00f0ff", linewidth=2.0, zorder=5)

        # Separation indicator
        x_sep = sim.separation_point(a_deg)
        cl = sim.lift_coefficient(a_deg)
        cd = sim.drag_coefficient(a_deg)

        idx_sep = np.argmin(np.abs(x_coords[:len(x_coords)//2] - x_sep))
        sep_color = "#39ff14" if a_deg <= 8.0 else ("#ffaa00" if a_deg <= 15.0 else "#ff0055")
        ax.plot(xr[idx_sep], yr[idx_sep], "o", color=sep_color, markersize=8, zorder=8)

        # Detached streamline sketch
        if a_deg > 10.0:
            sep_x = xr[idx_sep]
            sep_y = yr[idx_sep]
            wake_x = np.linspace(sep_x, 1.4, 30)
            wake_y = sep_y + 0.45 * ((wake_x - sep_x) ** 0.8) * ((a_deg - 10.0) / 8.5)
            ax.plot(wake_x, wake_y, "--", color="#ff0055", lw=1.8, alpha=0.85)

        ax.set_title(f"α = {a_deg:.1f}° | C_L = {cl:.2f} | C_D = {cd:.3f} | x_sep/c = {x_sep:.2f}",
                     fontsize=9, color="#00f0ff", pad=8)
        ax.set_xlim(-0.3, 1.5)
        ax.set_ylim(-0.5, 0.7)
        ax.set_aspect("equal")
        ax.grid(True)

    anim = FuncAnimation(fig, update, frames=len(alphas_deg), interval=80)
    writer = PillowWriter(fps=15)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    anim.save(output_path, writer=writer)
    plt.close()
    print(f"[CONTINUUM LAB] Animated GIF preview created: {output_path}")


def generate_boundary_layer_profiles_diagram(output_path: str, sim: AerodynamicStallSimulation):
    """
    Dedicated high-resolution diagram focusing on Prandtl Boundary Layer Theory and the separation point.
    """
    setup_dark_style()
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    fig.patch.set_facecolor("#0a0a0c")
    ax.set_facecolor("#0d1117")

    eta = np.linspace(0.0, 1.0, 120)
    p_attached = sim.pohlhausen_velocity_profile(eta, lambda_param=+2.0)
    p_zero = sim.pohlhausen_velocity_profile(eta, lambda_param=0.0)
    p_adverse = sim.pohlhausen_velocity_profile(eta, lambda_param=-6.0)
    p_sep = sim.pohlhausen_velocity_profile(eta, lambda_param=-12.0)
    p_rev = sim.pohlhausen_velocity_profile(eta, lambda_param=-15.0)

    ax.plot(p_attached, eta, label=r"$\Lambda = +2.0$ (Favorable Gradient, Accelerating)", color="#39ff14", lw=2.2)
    ax.plot(p_zero, eta, label=r"$\Lambda = 0.0$ (Blasius Flat Plate, $\partial p/\partial x = 0$)", color="#8b949e", lw=1.8, linestyle=":")
    ax.plot(p_adverse, eta, label=r"$\Lambda = -6.0$ (Adverse Gradient, Decelerating)", color="#ffaa00", lw=2.0)
    ax.plot(p_sep, eta, label=r"$\Lambda = -12.0$ [SEPARATION: $(\partial u/\partial y)_{\mathrm{wall}} = 0$]", color="#ff0055", lw=3.0)
    ax.plot(p_rev, eta, label=r"$\Lambda = -15.0$ [REVERSE FLOW: Backflow Recirculation]", color="#d600ff", lw=2.4, linestyle="--")

    ax.axvline(0.0, color="#ffffff", linestyle="-", lw=1.2, alpha=0.7)
    ax.fill_betweenx(eta[:30], p_rev[:30], 0.0, color="#d600ff", alpha=0.30, label="Reverse Flow Zone")

    ax.annotate(
        r"$\mathbf{Zero\ Wall\ Shear\ (\tau_w = 0):}$" "\n"
        r"$\left.\frac{\partial u}{\partial y}\right|_{y=0} = 0 \quad (\Lambda = -12)$",
        xy=(0.0, 0.0), xytext=(0.25, 0.15),
        arrowprops=dict(arrowstyle="->", color="#ff0055", lw=2.0),
        fontsize=10, color="#ff0055", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#1a0b16", edgecolor="#ff0055", alpha=0.95)
    )

    ax.set_title(
        "CONTINUUM LAB // PRANDTL-POHLHAUSEN BOUNDARY LAYER DYNAMICS\n"
        r"Momentum Balance at the Wall: $\left.\nu \frac{\partial^2 u}{\partial y^2}\right|_{\mathrm{wall}} = \frac{1}{\rho}\frac{\partial p}{\partial x}$",
        fontsize=12, fontweight="bold", color="#00f0ff", pad=12
    )
    ax.set_xlabel(r"Dimensionless Streamwise Velocity $u / U_e$", fontsize=10)
    ax.set_ylabel(r"Dimensionless Distance from Wall $\eta = y / \delta$", fontsize=10)
    ax.set_xlim(-0.25, 1.15)
    ax.set_ylim(0.0, 1.05)
    ax.legend(loc="upper left", fontsize=9, facecolor="#0d1117", edgecolor="#1f2937")
    ax.grid(True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[CONTINUUM LAB] Boundary Layer Velocity Profiles Diagram created: {output_path}")


def generate_all_visuals():
    sim = AerodynamicStallSimulation()
    workspace_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    renders_dir = workspace_root / "RENDERS" / "7 Desprendimiento Capa Limite y Stall Aerodinamico" / "extra" / "capturas"

    hero_h = str(renders_dir / "aerodynamic_stall_hero.png")
    hero_v = str(renders_dir / "stall_9_16_hero.png")
    profiles_diag = str(renders_dir / "boundary_layer_velocity_profiles.png")
    gif_preview = str(renders_dir / "boundary_layer_separation_preview.gif")

    generate_horizontal_hero(hero_h, sim)
    generate_vertical_hero(hero_v, sim)
    generate_boundary_layer_profiles_diagram(profiles_diag, sim)
    generate_animated_preview_gif(gif_preview, sim)


if __name__ == "__main__":
    generate_all_visuals()

