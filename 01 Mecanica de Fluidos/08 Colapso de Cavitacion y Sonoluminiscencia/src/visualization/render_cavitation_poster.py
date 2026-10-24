"""
Continuum Lab - Scientific 16:9 Hero Poster Generator
Module: 01 Mecanica de Fluidos / 08 Colapso de Cavitacion y Sonoluminiscencia
File: src/visualization/render_cavitation_poster.py

Renders a 3-panel high-resolution scientific poster:
  1. 3D Perspective Bubble Mesh & Surrounding Converging Flow Field
  2. Temporal Evolution: R(t)/R0, Wall Speed R_dot, and Mach Number M
  3. Extreme Thermodynamics: Internal Core Temperature T(t) & van der Waals Pressure P(t)
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D

from ..physics.cavitation_sim import CavitationBubbleSim


def render_cavitation_hero_poster(output_path: str):
    sim = CavitationBubbleSim()
    st = sim.get_state(7.20)  # Peak sonoluminescence state

    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 9), dpi=150)
    fig.patch.set_facecolor('#050A18')

    gs = gridspec.GridSpec(2, 2, width_ratios=[1.25, 1.0], height_ratios=[1.0, 1.0],
                           wspace=0.25, hspace=0.32, left=0.06, right=0.96, top=0.90, bottom=0.08)

    # -------------------------------------------------------------------------
    # Panel 1: 3D Bubble Mesh & Tracer Particles (Left)
    # -------------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[:, 0], projection='3d')
    ax1.set_facecolor('#091124')

    mesh_3d = st["bubble_mesh"]
    n_lat, n_lon, _ = mesh_3d.shape
    x_m = mesh_3d[:, :, 0]
    y_m = mesh_3d[:, :, 1]
    z_m = mesh_3d[:, :, 2]

    # Bubble wireframe/surface
    ax1.plot_wireframe(x_m, y_m, z_m, color='#00F0FF', rstride=2, cstride=3, lw=0.9, alpha=0.75, label='Burbuja de Cavitación')

    # Flash center
    ax1.scatter([0], [0], [0], color='#FFFFFF', s=120, edgecolors='#FFE600', label='Destello Sonoluminiscencia (T > 18,000 K)')

    # Particles
    pts = st["particles_3d"]
    radii = np.linalg.norm(pts, axis=1)
    ax1.scatter(pts[::2, 0], pts[::2, 1], pts[::2, 2], c=radii[::2], cmap='cyan_r' if 'cyan_r' in plt.colormaps else 'cool', s=2.5, alpha=0.45)

    ax1.set_title("GEOMETRÍA 3D DE COLAPSO Y CAMPO CONVERGENTE", fontsize=11, fontweight='bold', color='#00F0FF', pad=10)
    ax1.set_xlabel("X / R0", fontsize=9, color='#9CA3AF')
    ax1.set_ylabel("Y / R0", fontsize=9, color='#9CA3AF')
    ax1.set_zlabel("Z / R0", fontsize=9, color='#9CA3AF')
    ax1.view_init(elev=22, azim=32)
    ax1.legend(loc='upper right', facecolor='#111827', edgecolor='#374151', fontsize=8)

    # -------------------------------------------------------------------------
    # Panel 2: Kinematic Evolution R(t) & Mach (Top Right)
    # -------------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor('#091124')

    t_arr = sim.time_grid
    r_arr = sim.R_traj * 1e6
    r_ratio = sim.R_traj / sim.R0
    mach_arr = np.abs(sim.R_dot_traj) / sim.c_s

    ax2.plot(t_arr, r_ratio, color='#00F0FF', lw=2.2, label='Radio Normalizado R(t)/R0')
    ax2.axvline(7.20, color='#FFE600', ls='--', lw=1.5, label='Singularidad t = 7.20s')
    ax2.set_ylabel("R / R0", color='#00F0FF', fontsize=10)
    ax2.set_xlabel("Tiempo (s)", color='#9CA3AF', fontsize=9)
    ax2.grid(True, color='#1F2937', ls=':', alpha=0.6)

    # Twin axis for Mach
    ax2_twin = ax2.twinx()
    ax2_twin.plot(t_arr, mach_arr, color='#FF007F', lw=1.8, ls='-.', label='Número de Mach M(t)')
    ax2_twin.set_ylabel("Mach M = |v| / c_s", color='#FF007F', fontsize=10)

    ax2.set_title("DINÁMICA CINEMÁTICA: ECUACIÓN DE KELLER-MIKSIS", fontsize=10, fontweight='bold', color='#E5E7EB')

    # Combined legend
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right', facecolor='#111827', edgecolor='#374151', fontsize=8)

    # -------------------------------------------------------------------------
    # Panel 3: Temperature & van der Waals Pressure (Bottom Right)
    # -------------------------------------------------------------------------
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor('#091124')

    t_k_arr = sim.T_traj
    p_atm_arr = sim.P_gas_traj / 101325.0

    ax3.semilogy(t_arr, t_k_arr, color='#FFB703', lw=2.2, label='Temperatura Core T(t) [K]')
    ax3.axhline(5778.0, color='#E5E7EB', ls=':', lw=1.2, label='Fotosfera Solar (5,778 K)')
    ax3.set_ylabel("Temperatura [K] (Log)", color='#FFB703', fontsize=10)
    ax3.set_xlabel("Tiempo (s)", color='#9CA3AF', fontsize=9)
    ax3.grid(True, color='#1F2937', ls=':', alpha=0.6)

    # Twin axis for Pressure
    ax3_twin = ax3.twinx()
    ax3_twin.semilogy(t_arr, p_atm_arr, color='#00FF88', lw=1.8, ls='--', label='Presión Interior P_gas [atm]')
    ax3_twin.set_ylabel("Presión [atm] (Log)", color='#00FF88', fontsize=10)

    ax3.set_title("TERMODINÁMICA EXTREMA Y SONOLUMINISCENCIA", fontsize=10, fontweight='bold', color='#E5E7EB')

    lines3, labels3 = ax3.get_legend_handles_labels()
    lines4, labels4 = ax3_twin.get_legend_handles_labels()
    ax3.legend(lines3 + lines4, labels3 + labels4, loc='upper right', facecolor='#111827', edgecolor='#374151', fontsize=8)

    # Master Title
    fig.suptitle("CONTINUUM LAB // COLAPSO DE CAVITACIÓN Y DESTELLO DE SONOLUMINISCENCIA",
                 fontsize=14, fontweight='bold', color='#00F0FF', y=0.96)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[OK] Póster científico 16:9 generado con éxito: {output_path}")
