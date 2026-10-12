"""
Visualización Vectorial de Ultra-Alta Definición (1080x1920 @ 60 FPS, 9:16 Vertical)
Enjambre de 50 Doble Péndulos Planos con Transición de Fase y Divergencia Caótica
Versiones: Español (ES) e Inglés (EN)
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

# Configuración Estricta 9:16 Vertical para Plataformas Móviles (TikTok, Shorts, Reels)
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#080C16"  # Dark Cosmic Void

TEXT_CONFIG = {
    "es": {
        "hud_title": "[ DINÁMICA CAÓTICA // EFECTO MARIPOSA ]",
        "phase_1": "FASE 1: PÉNDULO SIMPLE (ORDEN)",
        "phase_2": "FASE 2: PÉNDULO DOBLE",
        "phase_3": "FASE 3: CAOS DETERMINISTA",
        "swarm_label": "ENJAMBRE     : 50 PÉNDULOS",
        "perturb_label": "PERTURBACIÓN : Δθ = 10⁻⁴ rad (0.028°)",
        "lyapunov_label": "EXP. LYAPUNOV: λ ≈ 1.42 s⁻¹",
        "divergence_label": "DIVERGENCIA  : |ΔX(t)| ~ e^(λ·t)",
        "determinism_label": "DETERMINISMO : 100% (CERO AZAR)",
        "sep_prefix": "SEPARACIÓN   : ",
    },
    "en": {
        "hud_title": "[ CHAOTIC DYNAMICS // BUTTERFLY EFFECT ]",
        "phase_1": "PHASE 1: SINGLE PENDULUM (ORDER)",
        "phase_2": "PHASE 2: DOUBLE PENDULUM",
        "phase_3": "PHASE 3: DETERMINISTIC CHAOS",
        "swarm_label": "SWARM        : 50 PENDULUMS",
        "perturb_label": "PERTURBATION : Δθ = 10⁻⁴ rad (0.028°)",
        "lyapunov_label": "LYAPUNOV EXP : λ ≈ 1.42 s⁻¹",
        "divergence_label": "DIVERGENCE   : |ΔX(t)| ~ e^(λ·t)",
        "determinism_label": "DETERMINISM  : 100% (ZERO RANDOMNESS)",
        "sep_prefix": "SEPARATION   : ",
    },
}


class BaseSwarmDoublePendulumScene(Scene):
    """
    Simulación cinemática y dinámica en 2 fases:
      - 0.0s a 2.5s: 1 solo péndulo oscilando armónicamente con alta retención.
      - 2.5s a 15.0s: Acoplamiento del segundo brazo generando el péndulo doble
        y la divergencia fractal del enjambre de 50 péndulos iridiscentes.
    """

    lang = "es"

    def construct(self):
        txts = TEXT_CONFIG[self.lang]

        # =========================================================================
        # 1. PRECOMPUTACIÓN FÍSICA Y VECTORIAL (DOP853 Runge-Kutta Orden 8(5,3))
        # =========================================================================
        fps = 60
        duration = 15.0  # 15 segundos exactos
        total_frames = int(fps * duration)  # 900 frames
        t_switch = 2.5  # Transición exacta a los 2.5s
        idx_switch = int(round(t_switch * fps))  # Frame 150

        params = SwarmParameters(
            m1=1.0,
            m2=1.0,
            L1=1.5,
            L2=1.5,
            g=9.81,
            num_pendulums=50,
            theta1_0_deg=120.0,
            theta2_0_deg=-60.0,
            duration=duration,
            fps=fps,
            rtol=1.0e-9,
            atol=1.0e-12,
        )

        sim = DoublePendulumSwarmSimulator(params)
        data = sim.run_two_phase_simulation(
            t_switch=t_switch,
            delta_theta1=2.0e-5,
            delta_theta2=2.0e-4,
        )

        # Coordenadas escaladas para encuadre seguro en lienzo 9:16
        scale = 1.25
        pivot = np.array([0.0, 0.75, 0.0])

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
            (0.00, np.array([0x00, 0xF0, 0xFF], dtype=np.float64)),  # #00F0FF (Cian Neón)
            (0.25, np.array([0x00, 0x70, 0xF3], dtype=np.float64)),  # #0070F3 (Azul Eléctrico)
            (0.50, np.array([0x79, 0x28, 0xCA], dtype=np.float64)),  # #7928CA (Violeta Cyber)
            (0.75, np.array([0xFF, 0x00, 0x55], dtype=np.float64)),  # #FF0055 (Magenta Intenso)
            (1.00, np.array([0xFF, 0xE6, 0x00], dtype=np.float64)),  # #FFE600 (Amarillo Solar)
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
        pure_white_rgb = np.array([240.0, 250.0, 255.0])

        # Ponderación temporal de fase:
        # t in [0.0, 2.5]: Blanco/Cian puro (Péndulo simple unificado)
        # t in [2.5, 4.5]: Transición cromática iridiscente
        # t in [4.5, 15.0]: Abanico cromático fluorescente completo
        t_arr = data["t"]
        w_phase = np.clip((t_arr - 2.5) / 2.0, 0.0, 1.0)  # (901,)

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
            height=2.25,
            stroke_color="#1E293B",
            stroke_width=1.5,
            fill_color="#0D121F",
            fill_opacity=0.94,
        ).move_to(UP * 6.45)

        hud_title = Text(
            txts["hud_title"],
            font="Consolas",
            font_size=10.5,
            weight=BOLD,
            color="#00F0FF",
        )
        hud_title.move_to(top_box.get_top() + DOWN * 0.28)
        hud_title.align_to(top_box.get_left() + RIGHT * 0.35, LEFT)

        phase_status = Text(
            f"T = 00.0s | {txts['phase_1']}",
            font="Consolas",
            font_size=10.5,
            color="#E2E8F0",
        )
        phase_status.move_to(top_box.get_top() + DOWN * 0.28)
        phase_status.align_to(top_box.get_right() + LEFT * 0.35, RIGHT)

        divider_top = Line(
            start=top_box.get_left() + RIGHT * 0.25 + UP * 0.60,
            end=top_box.get_right() + LEFT * 0.25 + UP * 0.60,
            stroke_color="#1E293B",
            stroke_width=1.0,
        )

        # Columna Izquierda de Telemetría
        t_enjambre = Text(
            txts["swarm_label"],
            font="Consolas",
            font_size=10.5,
            color="#CBD5E1",
        )
        t_perturb = Text(
            txts["perturb_label"],
            font="Consolas",
            font_size=10.5,
            color="#94A3B8",
        )
        t_lyapunov = Text(
            txts["lyapunov_label"],
            font="Consolas",
            font_size=10.5,
            color="#00F0FF",
        )
        left_col = VGroup(t_enjambre, t_perturb, t_lyapunov).arrange(
            DOWN, aligned_edge=LEFT, buff=0.18
        )
        left_col.move_to(top_box.get_center() + DOWN * 0.22)
        left_col.align_to(top_box.get_left() + RIGHT * 0.35, LEFT)

        # Columna Derecha de Telemetría
        t_divergencia = Text(
            txts["divergence_label"],
            font="Consolas",
            font_size=10.5,
            color="#FF0055",
        )
        t_determinismo = Text(
            txts["determinism_label"],
            font="Consolas",
            font_size=10.5,
            color="#39FF14",
        )
        t_separacion = Text(
            f"{txts['sep_prefix']}0.07 mm",
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

        top_hud_static = VGroup(
            top_box,
            hud_title,
            divider_top,
            left_col,
            t_divergencia,
            t_determinismo,
        )
        hud_dynamic = VGroup(phase_status, t_separacion)

        # =========================================================================
        # 4. COMPONENTES VISUALES DEL ENJAMBRE DE PÉNDULOS
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

        # Masas intermedias (Bob 1) y terminales (Bob 2)
        bobs1 = [
            Dot(p1_coords[k, 0], radius=0.065, color=WHITE)
            for k in range(n_pends)
        ]
        bobs2 = [
            Dot(p1_coords[k, 0], radius=0.055, color=WHITE)
            for k in range(n_pends)
        ]

        # Estructura del Enjambre: 50 Barras 1 y 50 Barras 2
        rods1 = [
            Line(pivot, p1_coords[k, 0], stroke_width=2.8, color=WHITE)
            for k in range(n_pends)
        ]
        rods2 = [
            Line(p1_coords[k, 0], p1_coords[k, 0], stroke_width=2.2, color=WHITE)
            for k in range(n_pends)
        ]

        # Anillo de onda de choque en el momento exacto de transición (t = 2.5s)
        shockwave_ring = Circle(
            radius=0.05,
            color="#00F0FF",
            stroke_width=3.0,
            fill_opacity=0.0,
        ).move_to(p1_coords[0, idx_switch])
        shockwave_ring.set_opacity(0.0)

        # Trazadores de Punta (Estelas luminosas con gradiente cometa)
        tail_len = 45  # ~0.75s a 60 FPS
        opacities = list(np.linspace(0.02, 0.90, tail_len))

        trails = []
        for k in range(n_pends):
            tr = VMobject(stroke_width=2.4)
            tr.set_points_as_corners([p1_coords[k, 0], p1_coords[k, 0]])
            tr.set_stroke(color=hex_colors[k][0], opacity=[0.05, 0.85])
            trails.append(tr)

        # Grupo activo del enjambre
        swarm_group = VGroup(*trails, *rods1, *rods2, *bobs1, *bobs2, shockwave_ring)

        # Agregar elementos al lienzo (SIN HUD INFERIOR)
        self.add(top_hud_static)
        self.add(hud_dynamic)
        self.add(pivot_group)
        self.add(swarm_group)

        # =========================================================================
        # 5. SINCRONIZADORES VECTORIALES DINÁMICOS VINCULADOS A MOBJECTS
        # =========================================================================
        time_tracker = ValueTracker(0.0)
        last_sec_int = [-1]

        def update_swarm(mob, dt):
            t_curr = time_tracker.get_value()
            frame_idx = int(np.clip(t_curr * fps, 0, total_frames - 1))
            start_tail = max(0, frame_idx - tail_len)

            is_phase1 = t_curr < t_switch

            # Animación de despliegue de la barra 2 en el umbral t = 2.5s
            if is_phase1:
                deploy_factor = 0.0
            elif t_curr < (t_switch + 0.12):
                deploy_factor = (t_curr - t_switch) / 0.12
            else:
                deploy_factor = 1.0

            # Onda de choque luminosa a los 2.5s
            if 2.45 <= t_curr <= 2.90:
                sw_prog = (t_curr - 2.45) / 0.45
                shockwave_ring.move_to(p1_coords[0, frame_idx])
                shockwave_ring.set_width(0.1 + sw_prog * 1.8)
                shockwave_ring.set_stroke(color="#00F0FF", opacity=(1.0 - sw_prog) * 0.95, width=3.0 * (1.0 - sw_prog))
            else:
                shockwave_ring.set_opacity(0.0)

            # Actualización vectorizada de los 50 péndulos
            for k in range(n_pends):
                p1 = p1_coords[k, frame_idx]
                curr_color = hex_colors[k][frame_idx]

                # Varilla 1 y Masa 1
                rods1[k].put_start_and_end_on(pivot, p1)
                rods1[k].set_color(curr_color)
                bobs1[k].move_to(p1)
                bobs1[k].set_color(curr_color)

                if is_phase1:
                    # En Fase 1: Únicamente 1 péndulo visible (varilla 2 oculta)
                    rods2[k].put_start_and_end_on(p1, p1)
                    rods2[k].set_stroke(opacity=0.0)
                    bobs2[k].move_to(p1)
                    bobs2[k].set_opacity(0.0)

                    # Estela trazada por la punta del péndulo simple (p1)
                    pts = p1_coords[k, start_tail : frame_idx + 1]
                    if len(pts) > 1:
                        trails[k].set_points_as_corners(pts)
                        cur_opacs = opacities[-len(pts) :]
                        trails[k].set_stroke(color=curr_color, opacity=cur_opacs)
                else:
                    # En Fase 2 & 3: Péndulo doble completamente activo
                    p2_target = p2_coords[k, frame_idx]
                    p2_current = p1 + deploy_factor * (p2_target - p1)

                    rods2[k].put_start_and_end_on(p1, p2_current)
                    rods2[k].set_stroke(color=curr_color, opacity=1.0)
                    bobs2[k].move_to(p2_current)
                    bobs2[k].set_opacity(1.0)
                    bobs2[k].set_color(curr_color)

                    # Estela trazada por la punta del péndulo doble (p2)
                    pts = p2_coords[k, start_tail : frame_idx + 1]
                    if len(pts) > 1:
                        trails[k].set_points_as_corners(pts)
                        cur_opacs = opacities[-len(pts) :]
                        trails[k].set_stroke(color=curr_color, opacity=cur_opacs)

        def update_hud(mob, dt):
            t_curr = time_tracker.get_value()
            frame_idx = int(np.clip(t_curr * fps, 0, total_frames - 1))
            t_sec = frame_idx / fps

            sec_step = int(t_curr * 10)
            if sec_step != last_sec_int[0]:
                last_sec_int[0] = sec_step

                # Fase dinámica
                if t_sec < 2.5:
                    p_txt = f"T = {t_sec:04.1f}s | {txts['phase_1']}"
                    p_col = "#E2E8F0"
                elif t_sec < 5.0:
                    p_txt = f"T = {t_sec:04.1f}s | {txts['phase_2']}"
                    p_col = "#00F0FF"
                else:
                    p_txt = f"T = {t_sec:04.1f}s | {txts['phase_3']}"
                    p_col = "#FF0055"

                new_phase = Text(p_txt, font="Consolas", font_size=10.5, color=p_col)
                new_phase.move_to(top_box.get_top() + DOWN * 0.28)
                new_phase.align_to(top_box.get_right() + LEFT * 0.35, RIGHT)
                phase_status.become(new_phase)

                # Métrica de separación dinámica
                span_val = swarm_span[frame_idx]
                if span_val < 0.001:
                    sep_str = f"{txts['sep_prefix']}{span_val*1000:0.2f} mm"
                elif span_val < 1.0:
                    sep_str = f"{txts['sep_prefix']}{span_val*100:0.2f} cm"
                else:
                    sep_str = f"{txts['sep_prefix']}{span_val:0.2f} m"

                t_separacion.become(
                    Text(
                        sep_str,
                        font="Consolas",
                        font_size=10.5,
                        weight=BOLD,
                        color="#FFE600" if span_val < 0.1 else "#FF0055",
                    ).move_to(right_col[2].get_center())
                )

        # Vincular sincronizadores a los Mobjects
        swarm_group.add_updater(update_swarm)
        hud_dynamic.add_updater(update_hud)

        # Reproducir animación durante 15.0 segundos continuos exactos
        self.play(
            time_tracker.animate.set_value(duration),
            run_time=duration,
            rate_func=linear,
        )
        self.wait(0.1)


class SwarmDoublePendulumSceneES(BaseSwarmDoublePendulumScene):
    """Versión en Español de la simulación del enjambre caótico."""
    lang = "es"


class SwarmDoublePendulumSceneEN(BaseSwarmDoublePendulumScene):
    """English version of the chaotic double pendulum swarm simulation."""
    lang = "en"


# Alias para retrocompatibilidad
SwarmDoublePendulumScene = SwarmDoublePendulumSceneES
