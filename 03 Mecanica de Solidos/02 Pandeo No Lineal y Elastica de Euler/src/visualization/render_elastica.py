"""
Módulo de Visualización: Genera capturas científicas de alta resolución y 
diagramas de fase/bifurcación para la Elástica de Euler con estética Continuum-Lab.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.collections import LineCollection
import numpy as np

from ..physics.euler_elastica_sim import EulerElastica


def render_elastica_hero_poster(output_path: str):
    """
    Renderiza un póster científico de 3 paneles en alta resolución (1920x1080 o 1080x1920)
    mostrando:
    1. Geometría deformada no lineal para múltiples niveles de carga P/P_cr con mapa de curvatura.
    2. Diagrama de Bifurcación Supercrítica (Pitchfork) P/P_cr vs Flecha y Acortamiento.
    3. Retrato de Fase en el plano canónico (theta, dtheta/ds) demostrando el isomorfismo con el péndulo.
    """
    elastica = EulerElastica(L=1.0, E=210e9, b=0.02, h=0.003)

    # Configuración de estilo Cyber / Deep Continuum
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 9), dpi=150)
    fig.patch.set_facecolor('#0B0F19')

    gs = gridspec.GridSpec(2, 2, width_ratios=[1.3, 1.0], height_ratios=[1.0, 1.0], 
                           wspace=0.25, hspace=0.32, left=0.07, right=0.95, top=0.90, bottom=0.08)

    # -------------------------------------------------------------
    # Panel 1: Perfiles Deformados de la Elástica (Grande a la izquierda)
    # -------------------------------------------------------------
    ax1 = fig.add_subplot(gs[:, 0])
    ax1.set_facecolor('#111827')

    angles_deg = [10.0, 30.0, 50.0, 70.0, 85.0]
    colors = plt.cm.plasma(np.linspace(0.2, 0.95, len(angles_deg)))

    for idx, a_deg in enumerate(angles_deg):
        sol = elastica.solve_exact(np.radians(a_deg), num_points=250)
        p_ratio = sol["P_ratio"]
        x = sol["x"]
        y = sol["y"]
        c_val = colors[idx]

        # Línea de la viga
        ax1.plot(x, y, color=c_val, lw=3.0, 
                 label=f"α = {a_deg:.0f}° | P/P_cr = {p_ratio:.3f}")
        # Puntos extremos (apoyos articulados)
        ax1.scatter([x[0], x[-1]], [y[0], y[-1]], color='#00F0FF', s=45, zorder=5)

    # Estado no deformado de referencia
    ax1.plot([0, 1.0], [0, 0], color='#4B5563', lw=1.5, ls='--', label='P ≤ P_cr (No deformado)')

    ax1.set_title("FAMILIA DE CONFIGURACIONES DE EQUILIBRIO NO LINEAL", 
                  fontsize=12, fontweight='bold', color='#00F0FF', pad=12)
    ax1.set_xlabel("Coordenada Horizontal x / L", fontsize=10, color='#9CA3AF')
    ax1.set_ylabel("Deflexión Lateral y / L", fontsize=10, color='#9CA3AF')
    ax1.grid(True, color='#1F2937', linestyle=':', linewidth=0.8)
    ax1.legend(loc='upper right', facecolor='#1F2937', edgecolor='#374151', fontsize=9)
    ax1.set_aspect('equal')
    ax1.set_xlim(-0.05, 1.05)
    ax1.set_ylim(-0.05, 0.55)

    # -------------------------------------------------------------
    # Panel 2: Diagrama de Bifurcación Supercrítica (Pitchfork)
    # -------------------------------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor('#111827')

    bifurc = elastica.compute_bifurcation_curve(num_alphas=120)
    p_r = bifurc["P_ratio"]
    dy_r = bifurc["delta_y_ratio"]
    dx_r = bifurc["delta_x_ratio"]

    # Rama recta estable (P < P_cr) e inestable (P > P_cr)
    p_pre = np.linspace(0.5, 1.0, 50)
    ax2.plot(p_pre, np.zeros_like(p_pre), color='#00FF88', lw=2.5, label='Equilibrio Recto Estable')
    p_post_unstable = np.linspace(1.0, 1.35, 50)
    ax2.plot(p_post_unstable, np.zeros_like(p_post_unstable), color='#EF4444', lw=1.5, ls=':', label='Rama Inestable (Recta)')

    # Ramas pandeadas simétricas (+delta_y y -delta_y)
    ax2.plot(p_r, dy_r, color='#00F0FF', lw=2.5, label='Rama Pandeada (+)')
    ax2.plot(p_r, -dy_r, color='#00F0FF', lw=2.5, ls='--', label='Rama Pandeada (-)')

    ax2.axvline(1.0, color='#F59E0B', ls='--', lw=1.2, label='Carga Crítica P_cr')
    ax2.scatter([1.0], [0.0], color='#F59E0B', s=70, zorder=6)

    ax2.set_title("DIAGRAMA DE BIFURCACIÓN TRIDENTE (PITCHFORK)", 
                  fontsize=11, fontweight='bold', color='#00F0FF', pad=10)
    ax2.set_xlabel("Relación de Carga P / P_cr", fontsize=9, color='#9CA3AF')
    ax2.set_ylabel("Flecha Lateral Máxima δy / L", fontsize=9, color='#9CA3AF')
    ax2.grid(True, color='#1F2937', linestyle=':', linewidth=0.8)
    ax2.legend(loc='lower right', facecolor='#1F2937', edgecolor='#374151', fontsize=8)
    ax2.set_xlim(0.6, 1.4)
    ax2.set_ylim(-0.6, 0.6)

    # -------------------------------------------------------------
    # Panel 3: Retrato de Fase y Curvatura Canónica
    # -------------------------------------------------------------
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor('#111827')

    for idx, a_deg in enumerate([15.0, 40.0, 65.0, 85.0]):
        sol = elastica.solve_exact(np.radians(a_deg), num_points=200)
        theta = np.degrees(sol["theta"])
        dtheta_ds = sol["kappa"]
        ax3.plot(theta, dtheta_ds, color=colors[idx], lw=2.2, 
                 label=f"α = {a_deg:.0f}°")
        ax3.plot(-theta, -dtheta_ds, color=colors[idx], lw=2.2, ls='--')

    ax3.set_title("ESPACIO DE FASE: CURVATURA vs ÁNGULO TANGENCIAL", 
                  fontsize=11, fontweight='bold', color='#00F0FF', pad=10)
    ax3.set_xlabel("Ángulo Tangente θ (°)", fontsize=9, color='#9CA3AF')
    ax3.set_ylabel("Curvatura κ = dθ/ds (m⁻¹)", fontsize=9, color='#9CA3AF')
    ax3.grid(True, color='#1F2937', linestyle=':', linewidth=0.8)
    ax3.legend(loc='upper right', facecolor='#1F2937', edgecolor='#374151', fontsize=8)

    # Título General y Membrete
    fig.suptitle("CONTINUUM LAB // 03 MECÁNICA DE SÓLIDOS: ELÁSTICA DE EULER NO LINEAL", 
                 fontsize=14, fontweight='heavy', color='#F3F4F6', y=0.96)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=200, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close()
    return output_path
