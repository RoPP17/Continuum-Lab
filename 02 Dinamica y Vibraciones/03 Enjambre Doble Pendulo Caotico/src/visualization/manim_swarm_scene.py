"""
Continuum Lab — Dinámica No Lineal y Caos Determinista
Visualización Vectorial de Ultra-Alta Definición (1080x1920 @ 60 FPS, 9:16 Vertical)
Enjambre de 50 Doble Péndulos Planos Hamiltoniano con Divergencia de Lyapunov
"""

import sys
from pathlib import Path
import numpy as np
from manim import *

# Asegurar importación de src desde la raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.physics.double_pendulum_swarm import DoublePendulumSwarmSimulator, SwarmParameters

# Configuración Estricta 9:16 Vertical para Plataformas Móviles de Alta Retención
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#0B0F19"  # Dark Cosmic Void


class SwarmDoublePendulumScene(Scene):
    """
    Simulación en Manim Community del Caos Determinista mediante un
    enjambre de 50 dobles péndulos planos con divergencia exponencial de Lyapunov.
    """

    def construct(self):
        # =========================================================================
        # 1. PRECOMPUTACIÓN FÍSICA Y VECTORIAL (DOP853 Runge-Kutta Orden 8(5,3))
        # =========================================================================
        fps = 60
        duration = 15.0  # 15 segundos exactos
        total_frames = int(fps * duration)  # 900 frames

        params = SwarmParameters(
            m1=1.0,
            m2=1.0,
            L1=1.5,
            L2=1.5,
            g=9.81,
            num_pendulums=50,
            theta1_0_deg=120.0,
            theta2_0_deg=-60.0,
            delta_theta=1.0e-6,
            duration=duration,
            fps=fps,
            rtol=1.0e-9,
            atol=1.0e-12,
        )

        sim = DoublePendulumSwarmSimulator(params)
        data = sim.run_simulation()

        # Coordenadas escaladas para encuadre en lienzo 9:16
        scale = 1.25
        pivot = np.array([0.0, 0.70, 0.0])

        x1_raw = data["x1"]  # (50, 901)
        y1_raw = data["y1"]
        x2_raw = data["x2"]
        y2_raw = data["y2"]
        swarm_span = data["swarm_span"]  # (901,)

        n_pends = params.num_pendulums
        n_pts = len(data["t"])

        # Arreglos 3D finales para render: (50, 901, 3)
        p1_coords = np.zeros((n_pends, n_pts, 3), dtype=np.float64)
        p2_coords = np.zeros((n_pends, n_pts, 3), dtype=np.float64)

        for k in range(n_pends):
            p1_coords[k, :, 0] = pivot[0] + scale * x1_raw[k]
            p1_coords[k, :, 1] = pivot[1] + scale * y1_raw[k]
            p2_coords[k, :, 0] = pivot[0] + scale * x2_raw[k]
            p2_coords[k, :, 1] = pivot[1] + scale * y2_raw[k]

        # =========================================================================
        # 2. GENERADOR DE PALETA CROMÁTICA CIBERNÉTICA Y TRANSICIÓN DE FASE
        # =========================================================================
        # Puntos clave del espectro: Cian -> Azul -> Violeta -> Magenta -> Amarillo
        stops = [
            (0.00, np.array([0x00, 0xF0, 0xFF], dtype=np.float64)),  # #00F0FF
            (0.25, np.array([0x00, 0x70, 0xF3], dtype=np.float64)),  # #0070F3
            (0.50, np.array([0x79, 0x28, 0xCA], dtype=np.float64)),  # #7928CA
            (0.75, np.array([0xFF, 0x00, 0x55], dtype=np.float64)),  # #FF0055
            (1.00, np.array([0xFF, 0xE6, 0x00], dtype=np.float64)),  # #FFE600
        ]

        def get_rainbow_rgb(u: float) -> np.ndarray:
            for idx in range(len(stops) - 1):
                u0, c0 = stops[idx]
                u1, c1 = stops[idx + 1]
                if u0 <= u <= u1:
                    frac = (u - u0) / (u1 - u0)
                    return (1.0 - frac) * c0 + frac * c1
            return stops[-1][1]

        base_cyber_rgb = np.array(
            [get_rainbow_rgb(k / (n_pends - 1)) for k in range(n_pends)]
        )  # (50, 3)
        pure_white_rgb = np.array([255.0, 255.0, 255.0])

        # Ponderación temporal de fase:
        # t in [0.0, 5.5]: w = 0.0 (Blanco metálico sólido)
        # t in [5.5, 7.5]: w in [0.0, 1.0] (Bifurcación iridiscente)
        # t in [7.5, 15.0]: w = 1.0 (Abanico cromático fluorescente)
        t_arr = data["t"]
        w_phase = np.clip((t_arr - 5.5) / 2.0, 0.0, 1.0)  # (901,)

        # Tabla de colores precalculada (50, 901)
        rgb_interpolated = (
            (1.0 - w_phase[None, :, None]) * pure_white_rgb[None, None, :]
            + w_phase[None, :, None] * base_cyber_rgb[:, None, :]
        )
        rgb_int = np.clip(np.round(rgb_interpolated), 0, 255).astype(np.uint8)

        hex_colors = [
            [
                f"#{rgb_int[k, i, 0]:02X}{rgb_int[k, i, 1]:02X}{rgb_int[k, i, 2]:02X}"
                for i in range(n_pts)
            ]
            for k in range(n_pends)
        ]

        # =========================================================================
        # 3. HUD DE TELEMETRÍA DINÁMICA (SAFE ZONE SUPERIOR: Y > 5.5)
        # =========================================================================
        top_box = RoundedRectangle(
            corner_radius=0.15,
            width=8.2,
            height=2.35,
            stroke_color="#1E293B",
            stroke_width=1.5,
            fill_color="#0D121F",
            fill_opacity=0.94,
        ).move_to(UP * 6.35)

        hud_title = Text(
            "[ CONTINUUM LAB // SISTEMAS DINÁMICOS ]",
            font="Consolas",
            font_size=12,
            weight=BOLD,
            color="#00F0FF",
        ).move_to(top_box.get_top() + DOWN * 0.28 + LEFT * 1.55)

        phase_status = Text(
            "T = 00.0s | FASE 1: ORDEN",
            font="Consolas",
            font_size=12,
            color="#E2E8F0",
        ).move_to(top_box.get_top() + DOWN * 0.28 + RIGHT * 2.30)

        divider_top = Line(
            start=top_box.get_left() + RIGHT * 0.25 + UP * 0.65,
            end=top_box.get_right() + LEFT * 0.25 + UP * 0.65,
            stroke_color="#1E293B",
            stroke_width=1.0,
        )

        # Columna Izquierda de Telemetría (Alineada estrictamente a la izquierda en X = -3.8)
        t_enjambre = Text(
            "ENJAMBRE     : 50 PÉNDULOS IDÉNTICOS",
            font="Consolas",
            font_size=10.5,
            color="#CBD5E1",
        )
        t_perturb = Text(
            "PERTURBACIÓN : Δθ = 10⁻⁶ rad (0.000057°)",
            font="Consolas",
            font_size=10.5,
            color="#94A3B8",
        )
        t_lyapunov = Text(
            "EXP. LYAPUNOV: λ ≈ 1.42 s⁻¹",
            font="Consolas",
            font_size=10.5,
            color="#00F0FF",
        )
        left_col = VGroup(t_enjambre, t_perturb, t_lyapunov).arrange(
            DOWN, aligned_edge=LEFT, buff=0.18
        )
        left_col.move_to(top_box.get_center() + DOWN * 0.22)
        left_col.align_to(top_box.get_left() + RIGHT * 0.35, LEFT)

        # Columna Derecha de Telemetría (Alineada estrictamente a la izquierda en X = +0.5)
        t_divergencia = Text(
            "DIVERGENCIA  : |ΔX(t)| ~ e^(λ·t)",
            font="Consolas",
            font_size=10.5,
            color="#FF0055",
        )
        t_determinismo = Text(
            "DETERMINISMO : 100% (CERO AZAR)",
            font="Consolas",
            font_size=10.5,
            color="#39FF14",
        )
        t_separacion = Text(
            "SEPARACIÓN   : 0.07 mm",
            font="Consolas",
            font_size=10.5,
            weight=BOLD,
            color="#FFE600",
        )
        right_col = VGroup(t_divergencia, t_determinismo, t_separacion).arrange(
            DOWN, aligned_edge=LEFT, buff=0.18
        )
        right_col.move_to(top_box.get_center() + DOWN * 0.22)
        right_col.align_to(top_box.get_center() + RIGHT * 0.45, LEFT)

        top_hud = VGroup(
            top_box,
            hud_title,
            phase_status,
            divider_top,
            left_col,
            right_col,
        )

        # =========================================================================
        # 4. CALLOUT DE RETENCIÓN MÓVIL (SAFE ZONE INFERIOR: Y < -5.5)
        # =========================================================================
        bottom_box = RoundedRectangle(
            corner_radius=0.15,
            width=8.2,
            height=2.05,
            stroke_color="#FF0055",
            stroke_width=1.5,
            fill_color="#0D121F",
            fill_opacity=0.94,
        ).move_to(DOWN * 6.40)

        c_line1 = Text(
            "SEGUNDO 0 AL 5: PARECEN UN SOLO PÉNDULO.",
            font="Consolas",
            font_size=14,
            weight=BOLD,
            color="#FFE600",
        ).move_to(bottom_box.get_top() + DOWN * 0.42)

        c_line2 = Text(
            "SEGUNDO 7: LA MARIPOSA DESTRUYE EL ORDEN.",
            font="Consolas",
            font_size=14,
            weight=BOLD,
            color="#FF0055",
        ).move_to(bottom_box.get_top() + DOWN * 0.88)

        divider_bot = Line(
            start=bottom_box.get_left() + RIGHT * 0.35 + DOWN * 0.22,
            end=bottom_box.get_right() + LEFT * 0.35 + DOWN * 0.22,
            stroke_color="#1E293B",
            stroke_width=1.0,
        )

        c_subtext = Text(
            "SISTEMA NO LINEAL DE EULER-LAGRANGE | CONSERVACIÓN HAMILTONIANA ΔE/E₀ < 10⁻⁷",
            font="Consolas",
            font_size=9.5,
            color="#64748B",
        ).move_to(bottom_box.get_top() + DOWN * 1.55)

        bottom_hud = VGroup(bottom_box, c_line1, c_line2, divider_bot, c_subtext)

        # =========================================================================
        # 5. COMPONENTES VISUALES DEL ENJAMBRE DE PÉNDULOS
        # =========================================================================
        pivot_dot = Dot(point=pivot, radius=0.08, color=WHITE)
        pivot_ring = Circle(radius=0.18, color="#00F0FF", stroke_width=2.0).move_to(pivot)
        pivot_tick_t = Line(pivot + UP * 0.15, pivot + UP * 0.25, color="#00F0FF", stroke_width=1.5)
        pivot_tick_b = Line(pivot + DOWN * 0.15, pivot + DOWN * 0.25, color="#00F0FF", stroke_width=1.5)
        pivot_tick_l = Line(pivot + LEFT * 0.15, pivot + LEFT * 0.25, color="#00F0FF", stroke_width=1.5)
        pivot_tick_r = Line(pivot + RIGHT * 0.15, pivot + RIGHT * 0.25, color="#00F0FF", stroke_width=1.5)
        pivot_group = VGroup(
            pivot_ring, pivot_dot, pivot_tick_t, pivot_tick_b, pivot_tick_l, pivot_tick_r
        )

        # Estructura del Enjambre: 50 Barras 1, 50 Barras 2, 50 Masas terminales
        rods1 = [
            Line(pivot, p1_coords[k, 0], stroke_width=2.4, color=WHITE)
            for k in range(n_pends)
        ]
        rods2 = [
            Line(p1_coords[k, 0], p2_coords[k, 0], stroke_width=1.9, color=WHITE)
            for k in range(n_pends)
        ]
        bobs2 = [
            Dot(p2_coords[k, 0], radius=0.055, color=WHITE)
            for k in range(n_pends)
        ]

        # Trazadores de Punta (Estelas luminosas con gradiente de opacidad)
        tail_len = 36  # Longitud de estela cometa (~0.60 segundos a 60 FPS)
        opacities = list(np.linspace(0.03, 0.90, tail_len))

        trails = []
        for k in range(n_pends):
            tr = VMobject(stroke_width=2.4)
            tr.set_points_as_corners([p2_coords[k, 0], p2_coords[k, 0]])
            tr.set_stroke(color=hex_colors[k][0], opacity=[0.05, 0.85])
            trails.append(tr)

        # Agregar elementos al lienzo en el orden de profundidad correcto
        self.add(*trails)
        self.add(*rods1)
        self.add(*rods2)
        self.add(*bobs2)
        self.add(pivot_group)
        self.add(top_hud)
        self.add(bottom_hud)

        # =========================================================================
        # 6. SINCRONIZADOR VECTORIAL DINÁMICO (60 FPS NATIVE CLOCK)
        # =========================================================================
        time_tracker = ValueTracker(0.0)
        last_sec_int = [-1]

        def update_swarm(dt):
            t_curr = time_tracker.get_value()
            frame_idx = int(np.clip(t_curr * fps, 0, total_frames - 1))
            t_sec = frame_idx / fps

            start_tail = max(0, frame_idx - tail_len)

            # Actualización vectorizada de los 50 péndulos
            for k in range(n_pends):
                p1 = p1_coords[k, frame_idx]
                p2 = p2_coords[k, frame_idx]
                curr_color = hex_colors[k][frame_idx]

                # Varillas y masas
                rods1[k].put_start_and_end_on(pivot, p1)
                rods2[k].put_start_and_end_on(p1, p2)
                bobs2[k].move_to(p2)

                # Color cromático dinámico
                rods1[k].set_color(curr_color)
                rods2[k].set_color(curr_color)
                bobs2[k].set_color(curr_color)

                # Estela cometa con opacidad decreciente
                pts = p2_coords[k, start_tail : frame_idx + 1]
                if len(pts) > 1:
                    trails[k].set_points_as_corners(pts)
                    cur_opacs = opacities[-len(pts) :]
                    trails[k].set_stroke(color=curr_color, opacity=cur_opacs)

            # Actualización de Telemetría Dinámica (a intervalos de 0.1s para alto rendimiento)
            sec_step = int(t_curr * 10)
            if sec_step != last_sec_int[0]:
                last_sec_int[0] = sec_step

                # Fase dinámica
                if t_sec < 5.5:
                    p_txt = f"T = {t_sec:04.1f}s | FASE 1: ORDEN"
                    p_col = "#E2E8F0"
                elif t_sec < 7.5:
                    p_txt = f"T = {t_sec:04.1f}s | FASE 2: BIFURCACIÓN"
                    p_col = "#00F0FF"
                else:
                    p_txt = f"T = {t_sec:04.1f}s | FASE 3: CAOS"
                    p_col = "#FF0055"

                phase_status.become(
                    Text(p_txt, font="Consolas", font_size=12, color=p_col).move_to(
                        top_box.get_top() + DOWN * 0.28 + RIGHT * 2.30
                    )
                )

                # Métrica de separación dinámica
                span_val = swarm_span[frame_idx]
                if span_val < 0.001:
                    sep_str = f"SEPARACIÓN   : {span_val*1000:0.2f} mm"
                elif span_val < 1.0:
                    sep_str = f"SEPARACIÓN   : {span_val*100:0.2f} cm"
                else:
                    sep_str = f"SEPARACIÓN   : {span_val:0.2f} m"

                t_separacion.become(
                    Text(
                        sep_str,
                        font="Consolas",
                        font_size=10.5,
                        weight=BOLD,
                        color="#FFE600" if span_val < 0.1 else "#FF0055",
                    ).move_to(right_col[2].get_center())
                )

        # Vincular sincronizador
        self.add_updater(update_swarm)

        # Reproducir animación durante 15.0 segundos continuos exactos
        self.play(
            time_tracker.animate.set_value(duration),
            run_time=duration,
            rate_func=linear,
        )
        self.remove_updater(update_swarm)
        self.wait(0.1)
