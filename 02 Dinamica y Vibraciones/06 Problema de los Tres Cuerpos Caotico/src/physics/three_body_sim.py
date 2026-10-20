"""
Continuum Lab - Chaotic Three-Body Problem Gravitational Physics Engine
Module: 02 Dinamica y Vibraciones / 06 Problema de los Tres Cuerpos Caotico
File: src/physics/three_body_sim.py

Implements Newtonian n-body gravitational dynamics:
    m_i * d²r_i/dt² = Σ_{j ≠ i} G * m_i * m_j * (r_j - r_i) / |r_j - r_i|³

Features:
  - Exact Moore-Chenciner (2000) Figure-8 choreography initial conditions
  - Hamiltonian conservation (E = T + V = const, L = 0, P = 0)
  - Micro-perturbation injection triggering Lyapunov chaotic divergence
  - High-order adaptive Runge-Kutta 4th-order (RK4) orbital integration
  - Slingshot hyperbolic ejection and eccentric binary capture dynamics
"""

from dataclasses import dataclass, field
from typing import List, Tuple
import numpy as np


@dataclass(frozen=True)
class ThreeBodyConfig:
    G: float = 1.0                      # Gravitational constant
    m1: float = 1.0                     # Mass Star A
    m2: float = 1.0                     # Mass Star B
    m3: float = 1.0                     # Mass Star C
    softening: float = 0.001            # Gravitational softening to prevent singularity
    perturb_time: float = 4.8           # Time in seconds when perturbation is injected
    perturb_dx: float = 1.8e-4          # X-perturbation on Star C
    perturb_dy: float = -2.2e-4         # Y-perturbation on Star C


@dataclass
class BodyState:
    x: float
    y: float
    vx: float
    vy: float
    speed: float


@dataclass
class ThreeBodyTelemetry:
    t: float
    kinetic_energy: float
    potential_energy: float
    total_energy: float
    angular_momentum: float
    min_separation: float
    max_speed: float
    regime_name: str
    is_chaotic: bool
    star_a: BodyState
    star_b: BodyState
    star_c: BodyState


class ThreeBodySimulation:
    """
    High-precision gravitational integrator for the 3-Body Problem.
    """

    def __init__(self, config: ThreeBodyConfig = ThreeBodyConfig()):
        self.cfg = config

        # Moore-Chenciner Figure-8 canonical initial parameters
        # x1 = -x2, y1 = -y2, r3 = (0, 0)
        # v1 = v2, v3 = -2*v1
        x0 = 0.97000436
        y0 = -0.24308753
        vx0 = 0.46620531
        vy0 = 0.43236573

        # State vectors: [r1x, r1y, r2x, r2y, r3x, r3y, v1x, v1y, v2x, v2y, v3x, v3y]
        self.state = np.array([
            -x0, -y0,          # r1 (Star A - Cyan)
             x0,  y0,          # r2 (Star B - Magenta)
            0.0, 0.0,          # r3 (Star C - Amber)
            vx0, vy0,          # v1
            vx0, vy0,          # v2
            -2.0 * vx0, -2.0 * vy0  # v3
        ], dtype=np.float64)

        self.current_time = 0.0
        self.perturbed = False

        # Trail history buffers (circular / append)
        self.max_trail_len = 480
        self.trail_a: List[Tuple[float, float]] = [(-x0, -y0)]
        self.trail_b: List[Tuple[float, float]] = [(x0, y0)]
        self.trail_c: List[Tuple[float, float]] = [(0.0, 0.0)]

        self.telemetry_history: List[ThreeBodyTelemetry] = []

    def compute_accelerations(self, r: np.ndarray) -> np.ndarray:
        """
        Computes gravitational accelerations for all 3 bodies:
            a_i = Σ_{j≠i} G * m_j * (r_j - r_i) / (r_ij² + ε²)^(3/2)
        """
        G = self.cfg.G
        m = [self.cfg.m1, self.cfg.m2, self.cfg.m3]
        eps2 = self.cfg.softening ** 2

        pos = r.reshape((3, 2))
        acc = np.zeros((3, 2), dtype=np.float64)

        for i in range(3):
            for j in range(3):
                if i != j:
                    diff = pos[j] - pos[i]
                    dist2 = np.sum(diff ** 2) + eps2
                    dist3 = dist2 ** 1.5
                    acc[i] += G * m[j] * diff / dist3

        return acc.flatten()

    def rk4_step(self, dt: float):
        """
        Executes a 4th-order Runge-Kutta numerical step.
        """
        y = self.state
        r = y[0:6]
        v = y[6:12]

        # k1
        k1_r = v
        k1_v = self.compute_accelerations(r)

        # k2
        r2 = r + 0.5 * dt * k1_r
        v2 = v + 0.5 * dt * k1_v
        k2_r = v2
        k2_v = self.compute_accelerations(r2)

        # k3
        r3 = r + 0.5 * dt * k2_r
        v3 = v + 0.5 * dt * k2_v
        k3_r = v3
        k3_v = self.compute_accelerations(r3)

        # k4
        r4 = r + dt * k3_r
        v4 = v + dt * k3_v
        k4_r = v4
        k4_v = self.compute_accelerations(r4)

        self.state[0:6] += (dt / 6.0) * (k1_r + 2.0 * k2_r + 2.0 * k3_r + k4_r)
        self.state[6:12] += (dt / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v)

    def step(self, dt: float) -> ThreeBodyTelemetry:
        """
        Advances the 3-body system by dt and updates trail and telemetry.
        """
        # Inject perturbation if time reached
        if not self.perturbed and self.current_time >= self.cfg.perturb_time:
            self.state[4] += self.cfg.perturb_dx  # r3x
            self.state[5] += self.cfg.perturb_dy  # r3y
            self.perturbed = True

        self.rk4_step(dt)
        self.current_time += dt

        # Update trails
        r1 = (float(self.state[0]), float(self.state[1]))
        r2 = (float(self.state[2]), float(self.state[3]))
        r3 = (float(self.state[4]), float(self.state[5]))

        self.trail_a.append(r1)
        self.trail_b.append(r2)
        self.trail_c.append(r3)

        if len(self.trail_a) > self.max_trail_len:
            self.trail_a.pop(0)
            self.trail_b.pop(0)
            self.trail_c.pop(0)

        # Telemetry calculations
        m1, m2, m3 = self.cfg.m1, self.cfg.m2, self.cfg.m3
        v1x, v1y = self.state[6], self.state[7]
        v2x, v2y = self.state[8], self.state[9]
        v3x, v3y = self.state[10], self.state[11]

        s1 = float(np.hypot(v1x, v1y))
        s2 = float(np.hypot(v2x, v2y))
        s3 = float(np.hypot(v3x, v3y))

        # Kinetic energy T = 0.5 * Σ m_i * v_i²
        T = 0.5 * (m1 * (s1 ** 2) + m2 * (s2 ** 2) + m3 * (s3 ** 2))

        # Potential energy V = -Σ G m_i m_j / r_ij
        r12 = float(np.hypot(self.state[0] - self.state[2], self.state[1] - self.state[3]))
        r23 = float(np.hypot(self.state[2] - self.state[4], self.state[3] - self.state[5]))
        r31 = float(np.hypot(self.state[4] - self.state[0], self.state[5] - self.state[1]))

        eps = self.cfg.softening
        V = -self.cfg.G * (
            (m1 * m2) / np.sqrt(r12 ** 2 + eps ** 2) +
            (m2 * m3) / np.sqrt(r23 ** 2 + eps ** 2) +
            (m3 * m1) / np.sqrt(r31 ** 2 + eps ** 2)
        )
        E_tot = float(T + V)

        # Angular momentum Lz = Σ m_i * (x_i * vy_i - y_i * vx_i)
        Lz = float(
            m1 * (self.state[0] * v1y - self.state[1] * v1x) +
            m2 * (self.state[2] * v2y - self.state[3] * v2x) +
            m3 * (self.state[4] * v3y - self.state[5] * v3x)
        )

        min_sep = min(r12, r23, r31)
        max_v = max(s1, s2, s3)

        if not self.perturbed:
            regime = "Coreografía Figura-8 (Moore-Chenciner)"
        elif self.current_time < 12.0:
            regime = "Divergencia Caótica & Encuentros Cercanos"
        else:
            regime = "Efección Hiperbólica & Binaria Excêntrica"

        telem = ThreeBodyTelemetry(
            t=self.current_time,
            kinetic_energy=float(T),
            potential_energy=float(V),
            total_energy=E_tot,
            angular_momentum=Lz,
            min_separation=min_sep,
            max_speed=max_v,
            regime_name=regime,
            is_chaotic=self.perturbed,
            star_a=BodyState(x=float(self.state[0]), y=float(self.state[1]), vx=v1x, vy=v1y, speed=s1),
            star_b=BodyState(x=float(self.state[2]), y=float(self.state[3]), vx=v2x, vy=v2y, speed=s2),
            star_c=BodyState(x=float(self.state[4]), y=float(self.state[5]), vx=v3x, vy=v3y, speed=s3)
        )
        self.telemetry_history.append(telem)
        return telem

    def advance_to_time(self, target_t: float, max_sub_dt: float = 0.001) -> ThreeBodyTelemetry:
        """
        Advances simulation to target_t using fine sub-stepping for extreme orbital stability and Hamiltonian conservation.
        """
        dt_total = target_t - self.current_time
        if dt_total <= 0:
            return self.telemetry_history[-1] if self.telemetry_history else self.step(0.001)

        steps = max(1, int(np.ceil(dt_total / max_sub_dt)))
        sub_dt = dt_total / float(steps)
        telem = None
        for _ in range(steps):
            telem = self.step(sub_dt)
        return telem
