"""
Continuum Lab — Classical Mechanics & Dynamical Systems
Division: 02 Dinamica y Vibraciones / 02 Mecanismo Coriolis Collarin
Module: pygame_app.py

Desktop 60 FPS Native Visualizer with Phosphorescent Kinetic Trails,
Vector Bloom Overlays, and Real-Time Keyboard Interactivity.
"""

import sys
import math
from pathlib import Path
from collections import deque
from typing import Tuple
import numpy as np
import pygame

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.physics.coriolis_kinematics import (
    CoriolisMechanismParams,
    KinematicState,
    CoriolisKinematicsSolver,
)


class PygameCoriolisVisualizer:
    def __init__(self, width: int = 1280, height: int = 720):
        pygame.init()
        pygame.display.set_caption("Continuum Lab — Mecanismo con Aceleración de Coriolis (2 Barras + Collarín)")
        self.screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.width = width
        self.height = height

        # Superficie de estela / persistencia luminosa con canal alfa
        self.trail_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        self.trail_surf.fill((0, 0, 0, 0))

        # Tipografía
        self.font_title = pygame.font.SysKeyFont(["JetBrains Mono", "Segoe UI", "Consolas"], 18, bold=True)
        self.font_hud = pygame.font.SysKeyFont(["JetBrains Mono", "Segoe UI", "Consolas"], 13)
        self.font_small = pygame.font.SysKeyFont(["JetBrains Mono", "Segoe UI", "Consolas"], 11)

        # Paleta de colores (Cyberpunk Dark Obsidian)
        self.c_bg = (7, 9, 14)
        self.c_cyan = (0, 240, 255)
        self.c_magenta = (255, 0, 127)
        self.c_lime = (57, 255, 20)
        self.c_amber = (255, 184, 0)
        self.c_purple = (168, 85, 247)
        self.c_white = (255, 255, 255)
        self.c_dim = (139, 148, 158)
        self.c_rail = (88, 166, 255)

        # Parámetros físicos
        self.params = CoriolisMechanismParams(
            L1=1.0,
            d=1.55,
            omega1=2.2,
            arm_extension=1.75
        )
        self.solver = CoriolisKinematicsSolver(self.params)

        # Estado de visualización
        self.theta1 = 0.0
        self.time = 0.0
        self.is_running = True
        self.time_scale = 1.0
        self.base_ppm = 100.0
        self.pixels_per_meter = 100.0
        self.vector_scale = 20.0

        # Posicionamiento de cámara (centro del mecanismo con espacio superior)
        self.base_cam_x = width // 2 - 80
        self.base_cam_y = height // 2 + 100
        self.cam_x = self.base_cam_x
        self.cam_y = self.base_cam_y

        # Modo Zoom Cinemático & Slow-Motion
        self.cinematic_zoom_enabled = True
        self.current_zoom_weight = 0.0

        # Buffers de estela
        self.stylus_trail = deque(maxlen=600)
        self.coriolis_trail = deque(maxlen=400)

        # Toggles de capas
        self.show_coriolis = True
        self.show_vrel = True
        self.show_centripetal = False
        self.show_all_acc = False
        self.show_grid = True

    def world_to_screen(self, x: float, y: float) -> Tuple[int, int]:
        sx = int(self.cam_x + x * self.pixels_per_meter)
        sy = int(self.cam_y - y * self.pixels_per_meter)
        return sx, sy

    def clear_trails(self):
        self.stylus_trail.clear()
        self.coriolis_trail.clear()
        self.trail_surf.fill((0, 0, 0, 0))

    def set_preset(self, preset_name: str):
        self.clear_trails()
        if preset_name == "harmonic":
            self.params.L1 = 1.0
            self.params.d = 1.55
            self.params.omega1 = 2.2
            self.params.arm_extension = 1.7
        elif preset_name == "whitworth":
            self.params.L1 = 1.4
            self.params.d = 0.85  # d < L1 -> Rotación completa
            self.params.omega1 = 2.0
            self.params.arm_extension = 1.4
        elif preset_name == "resonant":
            self.params.L1 = 1.0
            self.params.d = 1.15
            self.params.omega1 = 1.8
            self.params.arm_extension = 1.8
        elif preset_name == "spirograph":
            self.params.L1 = 1.1
            self.params.d = 1.75
            self.params.omega1 = 3.2
            self.params.arm_extension = 2.3

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.w, event.h
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.RESIZABLE)
                self.trail_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                self.cam_x = self.width // 2 - 80
                self.cam_y = self.height // 2 + 50
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.is_running = not self.is_running
                elif event.key == pygame.K_UP:
                    self.params.omega1 = min(6.0, self.params.omega1 + 0.2)
                elif event.key == pygame.K_DOWN:
                    self.params.omega1 = max(0.2, self.params.omega1 - 0.2)
                elif event.key == pygame.K_RIGHT:
                    self.params.d = min(3.0, self.params.d + 0.05)
                    self.clear_trails()
                elif event.key == pygame.K_LEFT:
                    self.params.d = max(0.4, self.params.d - 0.05)
                    self.clear_trails()
                elif event.key == pygame.K_c:
                    self.show_coriolis = not self.show_coriolis
                elif event.key == pygame.K_v:
                    self.show_vrel = not self.show_vrel
                elif event.key == pygame.K_a:
                    self.show_all_acc = not self.show_all_acc
                elif event.key == pygame.K_t:
                    self.clear_trails()
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                elif event.key == pygame.K_1:
                    self.set_preset("harmonic")
                elif event.key == pygame.K_2:
                    self.set_preset("whitworth")
                elif event.key == pygame.K_3:
                    self.set_preset("resonant")
                elif event.key == pygame.K_4:
                    self.set_preset("spirograph")
                elif event.key == pygame.K_s:
                    self.save_screenshot()
                elif event.key == pygame.K_z:
                    self.cinematic_zoom_enabled = not self.cinematic_zoom_enabled
                    if not self.cinematic_zoom_enabled:
                        self.pixels_per_meter = self.base_ppm
                        self.cam_x = self.base_cam_x
                        self.cam_y = self.base_cam_y

        # Zoom con rueda del ratón
        return True

    def save_screenshot(self):
        output_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "RENDERS" / "Coriolis_Mechanism"
        output_dir.mkdir(parents=True, exist_ok=True)
        img_path = output_dir / f"coriolis_sim_{int(self.time*1000)}.png"
        pygame.image.save(self.screen, str(img_path))
        print(f"[SCREENSHOT SAVED] -> {img_path}")

    def draw_arrow(self, origin: Tuple[int, int], vec: np.ndarray, color: Tuple[int, int, int], label: str):
        length = math.hypot(vec[0], vec[1])
        if length < 2.0:
            return

        dest_x = int(origin[0] + vec[0])
        dest_y = int(origin[1] - vec[1])

        pygame.draw.line(self.screen, color, origin, (dest_x, dest_y), 3)

        angle = math.atan2(-(dest_y - origin[1]), dest_x - origin[0])
        arrow_size = 10
        p1 = (
            int(dest_x - arrow_size * math.cos(angle - math.pi / 6)),
            int(dest_y + arrow_size * math.sin(angle - math.pi / 6)),
        )
        p2 = (
            int(dest_x - arrow_size * math.cos(angle + math.pi / 6)),
            int(dest_y + arrow_size * math.sin(angle + math.pi / 6)),
        )
        pygame.draw.polygon(self.screen, color, [(dest_x, dest_y), p1, p2])

        lbl = self.font_small.render(label, True, color)
        self.screen.blit(lbl, (dest_x + 6, dest_y - 8))

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0
            if not self.handle_input():
                break

            # 1. CÁLCULO DE ZOOM Y SLOW-MOTION CINEMÁTICO
            w_zoom = 0.0
            if self.cinematic_zoom_enabled:
                dist_crit = abs(self.theta1 - 1.5 * math.pi)
                if dist_crit > math.pi:
                    dist_crit = 2.0 * math.pi - dist_crit
                w_zoom = math.exp(-(dist_crit**2) / (2.0 * (0.36**2)))
            self.current_zoom_weight = w_zoom

            slow_factor = 1.0 + 3.6 * w_zoom
            effective_dt = dt / slow_factor

            if self.is_running:
                self.theta1 += self.params.omega1 * effective_dt * self.time_scale
                self.time += effective_dt * self.time_scale
                if self.theta1 > 2.0 * math.pi:
                    self.theta1 -= 2.0 * math.pi

            state = self.solver.solve(self.theta1, self.time)

            # 2. INTERPOLACIÓN DE CÁMARA
            if self.cinematic_zoom_enabled:
                target_scale = self.base_ppm * (1.0 + 1.45 * w_zoom)
                target_cam_x = self.base_cam_x - state.r_A[0] * self.pixels_per_meter * (w_zoom * 0.85)
                target_cam_y = self.base_cam_y + (state.r_A[1] * self.pixels_per_meter + 30 - self.base_cam_y) * (w_zoom * 0.85)

                self.pixels_per_meter += (target_scale - self.pixels_per_meter) * 0.12
                self.cam_x += (target_cam_x - self.cam_x) * 0.12
                self.cam_y += (target_cam_y - self.cam_y) * 0.12

            # Fondo
            self.screen.fill(self.c_bg)

            # Retícula de ingeniería
            if self.show_grid:
                self.draw_grid()

            # Extremo de stylus para trazo hipnótico
            stylus_pos = state.r_O2 + state.u_r2 * (state.r2 * self.params.arm_extension * 0.95)
            self.stylus_trail.append((stylus_pos[0], stylus_pos[1], abs(state.a_coriolis_mag)))

            # Traza de la punta del vector Coriolis (hodógrafo)
            tip_cor_x = state.r_A[0] + (state.a_coriolis_vec[0] / self.pixels_per_meter) * self.vector_scale
            tip_cor_y = state.r_A[1] + (state.a_coriolis_vec[1] / self.pixels_per_meter) * self.vector_scale
            self.coriolis_trail.append((tip_cor_x, tip_cor_y))

            # Dibujar estelas hipnóticas
            self.draw_trails()

            # Dibujar mecanismo
            self.draw_mechanism(state)

            # Dibujar vectores dinámicos
            self.draw_vectors(state)

            # Dibujar HUD lateral
            self.draw_hud(state)

            pygame.display.flip()

        pygame.quit()

    def draw_grid(self):
        grid_step = int(self.pixels_per_meter * 0.5)
        for x in range(self.cam_x % grid_step, self.width, grid_step):
            pygame.draw.line(self.screen, (16, 22, 34), (x, 0), (x, self.height), 1)
        for y in range(self.cam_y % grid_step, self.height, grid_step):
            pygame.draw.line(self.screen, (16, 22, 34), (0, y), (self.width, y), 1)

        # Ejes
        pygame.draw.line(self.screen, (32, 42, 60), (self.cam_x, 0), (self.cam_x, self.height), 1)
        pygame.draw.line(self.screen, (32, 42, 60), (0, self.cam_y), (self.width, self.cam_y), 1)

    def draw_trails(self):
        # 1. Traza hipnótica del Stylus
        if len(self.stylus_trail) > 2:
            n = len(self.stylus_trail)
            pts = list(self.stylus_trail)
            for i in range(1, n):
                p1 = self.world_to_screen(pts[i - 1][0], pts[i - 1][1])
                p2 = self.world_to_screen(pts[i][0], pts[i][1])
                intensity = int((i / n) * 230) + 25
                color = (min(255, 120 + int(pts[i][2] * 20)), 50, 255)
                pygame.draw.line(self.screen, color, p1, p2, 2)

        # 2. Traza hodógrafo de Coriolis
        if self.show_coriolis and len(self.coriolis_trail) > 2:
            n = len(self.coriolis_trail)
            pts = list(self.coriolis_trail)
            for i in range(1, n):
                p1 = self.world_to_screen(pts[i - 1][0], pts[i - 1][1])
                p2 = self.world_to_screen(pts[i][0], pts[i][1])
                pygame.draw.line(self.screen, (255, 0, 127), p1, p2, 1)

    def draw_mechanism(self, state: KinematicState):
        pO1 = self.world_to_screen(self.params.x_O1, self.params.y_O1)
        pO2 = self.world_to_screen(self.params.x_O2, self.params.y_O2)
        pA = self.world_to_screen(state.r_A[0], state.r_A[1])
        pTip = self.world_to_screen(state.r_tip_arm[0], state.r_tip_arm[1])

        # 1. Barra 2: Guía ranurada (Slotted Arm)
        # Rieles paralelos
        dx = pTip[0] - pO2[0]
        dy = pTip[1] - pO2[1]
        length = math.hypot(dx, dy)
        if length > 0:
            nx = -dy / length
            ny = dx / length
            offset = 8
            # Riel 1
            pygame.draw.line(self.screen, self.c_rail, 
                             (pO2[0] + nx * offset, pO2[1] + ny * offset),
                             (pTip[0] + nx * offset, pTip[1] + ny * offset), 3)
            # Riel 2
            pygame.draw.line(self.screen, self.c_rail, 
                             (pO2[0] - nx * offset, pO2[1] - ny * offset),
                             (pTip[0] - nx * offset, pTip[1] - ny * offset), 3)

        # 2. Barra 1: Manivela O1-A
        pygame.draw.line(self.screen, self.c_white, pO1, pA, 5)
        pygame.draw.line(self.screen, self.c_cyan, pO1, pA, 2)

        # 3. Collarín deslizante en punto A
        # Bloque orientado con theta2
        c_w, c_h = 24, 16
        cos2, sin2 = state.u_r2[0], state.u_r2[1]
        corners = [
            (-c_w / 2, -c_h / 2),
            (c_w / 2, -c_h / 2),
            (c_w / 2, c_h / 2),
            (-c_w / 2, c_h / 2),
        ]
        poly_pts = []
        for cx, cy in corners:
            rx = cx * cos2 - cy * sin2
            ry = cx * sin2 + cy * cos2
            poly_pts.append((pA[0] + rx, pA[1] - ry))

        pygame.draw.polygon(self.screen, (218, 165, 32), poly_pts)
        pygame.draw.polygon(self.screen, (255, 235, 150), poly_pts, 2)
        pygame.draw.circle(self.screen, self.c_cyan, pA, 4)

        # 4. Pivotes fijos O1 y O2
        for p, label in [(pO1, "O1"), (pO2, "O2")]:
            pygame.draw.circle(self.screen, (25, 33, 48), p, 9)
            pygame.draw.circle(self.screen, self.c_cyan, p, 9, 2)
            pygame.draw.circle(self.screen, self.c_white, p, 3)
            lbl = self.font_small.render(label, True, self.c_dim)
            self.screen.blit(lbl, (p[0] + 12, p[1] - 8))

    def draw_vectors(self, state: KinematicState):
        pA = self.world_to_screen(state.r_A[0], state.r_A[1])

        # 1. Vector Coriolis: 2 * (omega2 x v_rel)
        if self.show_coriolis:
            vec_screen = np.array([
                state.a_coriolis_vec[0] * self.vector_scale,
                state.a_coriolis_vec[1] * self.vector_scale
            ])
            self.draw_arrow(pA, vec_screen, self.c_cyan, f"a_cor = {state.a_coriolis_mag:+.2f} m/s²")

        # 2. Velocidad relativa v_rel
        if self.show_vrel:
            vec_screen = np.array([
                state.v_rel_vec[0] * (self.vector_scale * 1.5),
                state.v_rel_vec[1] * (self.vector_scale * 1.5)
            ])
            self.draw_arrow(pA, vec_screen, self.c_lime, f"v_rel = {state.v_rel:+.2f} m/s")

        # 3. Aceleración centrípeta
        is_zoomed = self.current_zoom_weight > 0.12
        if self.show_centripetal or self.show_all_acc or is_zoomed:
            vec_screen = np.array([
                state.a_centripetal_vec[0] * self.vector_scale,
                state.a_centripetal_vec[1] * self.vector_scale
            ])
            cent_val = -state.omega2**2 * state.r2
            self.draw_arrow(pA, vec_screen, self.c_amber, f"a_n = {cent_val:+.2f} m/s²")

        # 4. Aceleración de Euler y Relativa
        if self.show_all_acc or is_zoomed:
            vec_euler = np.array([
                state.a_euler_vec[0] * self.vector_scale,
                state.a_euler_vec[1] * self.vector_scale
            ])
            euler_val = state.alpha2 * state.r2
            self.draw_arrow(pA, vec_euler, self.c_magenta, f"a_euler = {euler_val:+.2f} m/s²")

        if self.show_all_acc:
            vec_arel = np.array([
                state.a_rel_vec[0] * self.vector_scale,
                state.a_rel_vec[1] * self.vector_scale
            ])
            self.draw_arrow(pA, vec_arel, (200, 200, 200), f"a_rel = {state.a_rel:+.2f} m/s²")

    def draw_hud(self, state: KinematicState):
        hud_w = 340
        hud_rect = pygame.Rect(self.width - hud_w - 16, 16, hud_w, self.height - 32)
        hud_surf = pygame.Surface((hud_rect.width, hud_rect.height), pygame.SRCALPHA)
        hud_surf.fill((13, 17, 26, 220))
        pygame.draw.rect(hud_surf, (255, 255, 255, 25), (0, 0, hud_rect.width, hud_rect.height), 1, border_radius=10)

        self.screen.blit(hud_surf, hud_rect.topleft)

        x0 = hud_rect.x + 18
        y0 = hud_rect.y + 18

        # Título
        title = self.font_title.render("TELEMETRÍA CORIOLIS", True, self.c_cyan)
        self.screen.blit(title, (x0, y0))
        y0 += 28

        regime_str = "Oscilante (d > L1)" if self.params.is_oscillating else "Rotación Continua (Whitworth)"
        sub = self.font_small.render(f"Régimen: {regime_str}", True, self.c_dim)
        self.screen.blit(sub, (x0, y0))
        y0 += 24

        pygame.draw.line(self.screen, (255, 255, 255, 30), (x0, y0), (x0 + hud_w - 36, y0), 1)
        y0 += 14

        # Variables clave
        readouts = [
            ("Aceleración Coriolis (a_cor):", f"{state.a_coriolis_mag:+.3f} m/s²", self.c_cyan),
            ("Velocidad Deslizamiento (v_rel):", f"{state.v_rel:+.3f} m/s", self.c_lime),
            ("Velocidad Angular Barra 2 (ω₂):", f"{state.omega2:+.3f} rad/s", self.c_white),
            ("Aceleración Angular Barra 2 (α₂):", f"{state.alpha2:+.3f} rad/s²", self.c_magenta),
            ("Distancia Radial (r₂):", f"{state.r2:.3f} m", self.c_amber),
            ("Aceleración Relativa (a_rel):", f"{state.a_rel:+.3f} m/s²", self.c_dim),
            ("Error Reconstrucción Vectorial:", f"{state.residual_error:.1e} m/s²", (50, 255, 120)),
        ]

        for lbl, val, col in readouts:
            lbl_rend = self.font_small.render(lbl, True, self.c_dim)
            val_rend = self.font_hud.render(val, True, col)
            self.screen.blit(lbl_rend, (x0, y0))
            y0 += 16
            self.screen.blit(val_rend, (x0, y0))
            y0 += 22

        pygame.draw.line(self.screen, (255, 255, 255, 30), (x0, y0), (x0 + hud_w - 36, y0), 1)
        y0 += 16

        # Instrucciones de teclado
        controls_title = self.font_small.render("CONTROLES DE TECLADO:", True, self.c_amber)
        self.screen.blit(controls_title, (x0, y0))
        y0 += 18

        keys_info = [
            ("[ESPACIO]", "Pausar / Reanudar"),
            ("[↑ / ↓]", f"Velocidad ω₁ ({self.params.omega1:.1f} rad/s)"),
            ("[← / →]", f"Separación d ({self.params.d:.2f} m)"),
            ("[1, 2, 3, 4]", "Presets (Harmónico, Whitworth...)"),
            ("[C / V / A]", "Toggle Vectores (Coriolis, v_rel, Todos)"),
            ("[Z]", f"Zoom Cinemático Auto ({'ON' if self.cinematic_zoom_enabled else 'OFF'})"),
            ("[T / G]", "Limpiar Estelas / Toggle Cuadrícula"),
            ("[S]", "Guardar Captura en RENDERS/"),
        ]

        for key, desc in keys_info:
            txt = self.font_small.render(f"{key:<12} {desc}", True, (180, 190, 205))
            self.screen.blit(txt, (x0, y0))
            y0 += 18


def launch_pygame_app():
    app = PygameCoriolisVisualizer()
    app.run()


if __name__ == "__main__":
    launch_pygame_app()
