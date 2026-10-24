"""
Continuum Lab - Scientific 16:9 Hero Poster Generator
Module: 01 Mecanica de Fluidos / 07 Colision de Anillos de Vortice
File: src/visualization/render_vortex_poster.py

Renders a 3-panel high-resolution scientific poster:
  1. 3D Vortex Filaments & Secondary Crown Reconnection (m = 12)
  2. Kinematic Trajectory: Axial Distance z(t), Expansion R(t), and Core Thinning a(t)
  3. Widnall Instability Modal Spectrum & Enstrophy Amplification
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D

from ..physics.vortex_collision_sim import VortexRingsCollisionSim


def render_vortex_hero_poster(output_path: str):
    sim = VortexRingsCollisionSim()
    st = sim.get_state(6.8)  # Peak crown formation

    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 9), dpi=150)
    fig.patch.set_facecolor('#070A14')

    gs = gridspec.GridSpec(2, 2, width_ratios=[1.3, 1.0], height_ratios=[1.0, 1.0],
                           wspace=0.25, hspace=0.32, left=0.06, right=0.96, top=0.90, bottom=0.08)

    # Panel 1: 3D Reconnection Crown & Streamlines (Left)
    ax1 = fig.add_subplot(gs[:, 0], projection='3d')
    ax1.set_facecolor('#0B0F1C')

    # Primary rings
    r1 = st["ring1"]
    r2 = st["ring2"]
    ax1.plot(r1[:, 0], r1[:, 1], r1[:, 2], color='#00F0FF', lw=2.8, label='Anillo Superior (+Γ₀)')
    ax1.plot(r2[:, 0], r2[:, 1], r2[:, 2], color='#FF007F', lw=2.8, label='Anillo Inferior (-Γ₀)')

    # Secondary rings
    for k, sring in enumerate(st["sec_rings"]):
        c_val = '#FFB703' if k % 2 == 0 else '#00FF88'
        lbl = 'Corona Secundaria (m = 12)' if k == 0 else None
        ax1.plot(sring[:, 0], sring[:, 1], sring[:, 2], color=c_val, lw=2.2, label=lbl)

    # Tracer particles
    pts = st["particles_3d"]
    speeds = st["particles_speed"]
    norm_spd = np.clip(speeds / np.percentile(speeds, 95), 0, 1)
    ax1.scatter(pts[::2, 0], pts[::2, 1], pts[::2, 2], c=norm_spd[::2], cmap='cool', s=2.5, alpha=0.55)

    ax1.set_title("TOPOLOGÍA 3D DE RECONEXIÓN Y CORONA DE VÓRTICES", fontsize=11, fontweight='bold', color='#00F0FF', pad=10)
    ax1.set_xlabel("X (m)", fontsize=9, color='#9CA3AF')
    ax1.set_ylabel("Y (m)", fontsize=9, color='#9CA3AF')
    ax1.set_zlabel("Z (m)", fontsize=9, color='#9CA3AF')
    ax1.view_init(elev=28, azim=35)
    ax1.legend(loc='upper right', facecolor='#111827', edgecolor='#374151', fontsize=8)

    # Panel 2: Kinematic Evolution (Upper Right)
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor('#0E1424')

    t_arr = sim.t_traj
    ax2.plot(t_arr, sim.z_traj, color='#00F0FF', lw=2.2, label='Posición Axial z(t)')
    ax2.plot(t_arr, sim.R_traj, color='#FFB703', lw=2.2, label='Radio Anillo R(t)')
    ax2.plot(t_arr, sim.a_traj, color='#FF007F', lw=1.8, ls='--', label='Radio Núcleo a(t)')
    ax2.axvline(sim.t_reconnect, color='#00FF88', ls=':', lw=1.5, label='Reconexión t_rec')

    ax2.set_title("EVOLUCIÓN CINEMÁTICA Y ESTIRAMIENTO DE NÚCLEO", fontsize=10, fontweight='bold', color='#00F0FF', pad=8)
    ax2.set_xlabel("Tiempo t (s)", fontsize=9, color='#9CA3AF')
    ax2.set_ylabel("Escala de Longitud (m)", fontsize=9, color='#9CA3AF')
    ax2.grid(True, color='#1F2937', linestyle=':', linewidth=0.8)
    ax2.legend(loc='center right', facecolor='#111827', edgecolor='#374151', fontsize=8)

    # Panel 3: Widnall Instability Amplitude & Enstrophy Growth (Lower Right)
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor('#0E1424')

    omega_arr = sim.Gamma0 / (np.pi * np.maximum(sim.a_traj, 1e-4)**2)
    ax3_twin = ax3.twinx()

    l1 = ax3.plot(t_arr, sim.amp_traj * 1e3, color='#00FF88', lw=2.2, label='Amplitud Widnall (mm)')
    l2 = ax3_twin.plot(t_arr, omega_arr, color='#FF007F', lw=2.0, ls='-', label='Vorticidad Máx ω (s⁻¹)')

    ax3.set_title("CRECIMIENTO DE ONDAS DE WIDNALL & ENSTROFIA PICO", fontsize=10, fontweight='bold', color='#00F0FF', pad=8)
    ax3.set_xlabel("Tiempo t (s)", fontsize=9, color='#9CA3AF')
    ax3.set_ylabel("Amplitud de Onda (mm)", fontsize=9, color='#00FF88')
    ax3_twin.set_ylabel("Vorticidad Pico ω (s⁻¹)", fontsize=9, color='#FF007F')
    ax3.grid(True, color='#1F2937', linestyle=':', linewidth=0.8)

    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax3.legend(lines, labels, loc='upper left', facecolor='#111827', edgecolor='#374151', fontsize=8)

    # Main Title
    fig.suptitle("CONTINUUM LAB // 01 MECÁNICA DE FLUIDOS: COLISIÓN DE ANILLOS DE VÓRTICE",
                 fontsize=14, fontweight='heavy', color='#F3F4F6', y=0.96)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=200, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    print(f"[+] Hero poster rendered: {output_path}")
    return output_path
