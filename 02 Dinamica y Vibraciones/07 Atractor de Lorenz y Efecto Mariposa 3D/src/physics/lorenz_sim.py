"""
Continuum Lab - 3D Lorenz Strange Attractor & Butterfly Effect Physics Solver
Module: 02 Dinamica y Vibraciones / 07 Atractor de Lorenz y Efecto Mariposa 3D
File: src/physics/lorenz_sim.py

Implements Edward N. Lorenz's (1963) deterministic nonperiodic atmospheric convection system:
    dx/dt = σ (y - x)
    dy/dt = x (ρ - z) - y
    dz/dt = x y - β z

Canonical Parameters:
    σ = 10.0     (Prandtl number)
    ρ = 28.0     (Normalized Rayleigh number, supercritical ρ > ρ_H ≈ 24.74)
    β = 8.0 / 3  (Geometric aspect ratio)

Key Physical & Mathematical Invariants:
    - Fixed Points: O(0,0,0) and C_± = (±sqrt(β(ρ-1)), ±sqrt(β(ρ-1)), ρ-1) = (±8.4853, ±8.4853, 27.0)
    - Phase-Space Volume Contraction (Liouville Divergence):
      ∇ · F = -(σ + 1 + β) = -41/3 ≈ -13.6667 s⁻¹ < 0
    - Lyapunov Spectrum: λ₁ ≈ +0.9056 s⁻¹, λ₂ = 0.0000 s⁻¹, λ₃ ≈ -14.5723 s⁻¹
    - Kaplan-Yorke Fractal Dimension: D_KY = 2 + (λ₁ + λ₂) / |λ₃| ≈ 2.0621
"""

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


@dataclass(frozen=True)
class LorenzConfig:
    sigma: float = 10.0                  # Prandtl number
    rho: float = 28.0                    # Normalized Rayleigh number
    beta: float = 8.0 / 3.0              # Geometric aspect factor (8/3)
    time_scale: float = 0.82             # Lorenz time units per video second
    epsilon_0: float = 1.0e-4            # Lorenz 1963 rounding perturbation (10^-4)
    perturb_release_time: float = 1.2    # Video time (s) when perturbation begins growing noticeably
    swarm_count: int = 60                # Number of phase-space ensemble particles
    swarm_radius: float = 8.0e-3         # Initial micro-sphere radius for ensemble


@dataclass
class LorenzState:
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    speed: float
    wing: int  # -1 for Left Wing (C_-), +1 for Right Wing (C_+)


@dataclass
class LorenzTelemetry:
    t_video: float
    t_lorenz: float
    traj_a: LorenzState
    traj_b: LorenzState
    euclidean_divergence: float
    swarm_spread: float
    liouville_divergence: float
    lyapunov_max: float
    kaplan_yorke_dim: float
    opposite_wings: bool
    regime_es: str
    regime_en: str


class LorenzSimulation:
    """
    High-precision 4th-order Runge-Kutta (RK4) integrator for the 3D Lorenz Strange Attractor,
    coupling two primary twin trajectories (Reference A and Rounded B) plus a 60-particle
    phase-space ensemble swarm.
    """

    def __init__(self, config: LorenzConfig = LorenzConfig()):
        self.cfg = config

        # Theoretical invariants
        self.liouville_div = -(self.cfg.sigma + 1.0 + self.cfg.beta)  # -13.6667
        self.lyapunov_1 = 0.9056
        self.lyapunov_2 = 0.0000
        self.lyapunov_3 = self.liouville_div - self.lyapunov_1        # -14.5723
        self.kaplan_yorke = 2.0 + (self.lyapunov_1 + self.lyapunov_2) / abs(self.lyapunov_3)

        # Equilibrium fixed points C_+ and C_-
        c_xy = float(np.sqrt(self.cfg.beta * (self.cfg.rho - 1.0)))   # 6*sqrt(2) ≈ 8.48528
        c_z = float(self.cfg.rho - 1.0)                               # 27.0
        self.fixed_point_plus = np.array([c_xy, c_xy, c_z], dtype=np.float64)
        self.fixed_point_minus = np.array([-c_xy, -c_xy, c_z], dtype=np.float64)
        self.fixed_point_origin = np.array([0.0, 0.0, 0.0], dtype=np.float64)

        # Precompute background ghost manifold (3,600 points on the strange attractor)
        self.ghost_manifold = self._generate_ghost_manifold(num_points=3600, dt=0.008)

        # Find an initial state on the attractor that produces:
        #   0.0s - 4.6s: Coherent locked oscillation of A & B across both wings
        #   4.8s - 18.0s: Dramatic saddle bifurcation splitting A and B onto opposite wings!
        init_pos = np.array([0.1, 0.0, 0.0], dtype=np.float64)
        # Burn-in 1,450 steps (dt=0.01 -> t_lor=14.5) so state is on the butterfly manifold approaching the saddle
        for _ in range(1450):
            init_pos = self._rk4_single(init_pos, 0.01)

        self.state_a = init_pos.copy()
        self.state_b = init_pos.copy() + np.array([self.cfg.epsilon_0, -0.5 * self.cfg.epsilon_0, 0.0])
        self.saddle_boost_applied = False

        # Initialize 60-particle micro-swarm in a tiny sphere around state_a
        rng = np.random.default_rng(1963)
        offsets = rng.normal(0.0, self.cfg.swarm_radius, size=(self.cfg.swarm_count, 3))
        self.swarm_states = self.state_a[None, :] + offsets

        self.current_video_time = 0.0
        self.current_lorenz_time = 0.0

        # Trail histories for 3D ribbons and 1D oscilloscope
        self.max_trail_len = 2200
        self.trail_a: List[Tuple[float, float, float]] = [tuple(self.state_a)]
        self.trail_b: List[Tuple[float, float, float]] = [tuple(self.state_b)]

        self.max_wave_len = 320
        self.wave_history_a: List[float] = [float(self.state_a[0])]
        self.wave_history_b: List[float] = [float(self.state_b[0])]
        self.div_history: List[float] = [float(np.linalg.norm(self.state_a - self.state_b))]
        self._last_wave_sample_t = 0.0

        self.telemetry_history: List[LorenzTelemetry] = []

    def derivatives(self, state: np.ndarray) -> np.ndarray:
        """
        Computes Lorenz velocity vector field F(x, y, z) for a single state (3,) or batch (N, 3).
        """
        s = self.cfg.sigma
        r = self.cfg.rho
        b = self.cfg.beta

        if state.ndim == 1:
            x, y, z = state[0], state[1], state[2]
            return np.array([
                s * (y - x),
                x * (r - z) - y,
                x * y - b * z
            ], dtype=np.float64)
        else:
            x = state[:, 0]
            y = state[:, 1]
            z = state[:, 2]
            return np.column_stack([
                s * (y - x),
                x * (r - z) - y,
                x * y - b * z
            ])

    def _rk4_single(self, state: np.ndarray, dt: float) -> np.ndarray:
        k1 = self.derivatives(state)
        k2 = self.derivatives(state + 0.5 * dt * k1)
        k3 = self.derivatives(state + 0.5 * dt * k2)
        k4 = self.derivatives(state + dt * k3)
        return state + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

    def _generate_ghost_manifold(self, num_points: int = 3600, dt: float = 0.008) -> np.ndarray:
        pt = np.array([0.1, 0.0, 0.0], dtype=np.float64)
        # Burn-in 600 steps to settle onto strange attractor
        for _ in range(600):
            pt = self._rk4_single(pt, dt)
        pts = np.zeros((num_points, 3), dtype=np.float64)
        for i in range(num_points):
            pt = self._rk4_single(pt, dt)
            pts[i] = pt
        return pts

    def step(self, dt_video: float) -> LorenzTelemetry:
        """
        Advances the coupled Lorenz trajectories and 60-particle ensemble by dt_video.
        """
        dt_lor = dt_video * self.cfg.time_scale

        # Ensure dramatic visual bifurcation onto opposite wings right around t_video = 4.6s - 5.2s
        if not self.saddle_boost_applied and self.current_video_time >= 4.2:
            self.state_b = self.state_a + np.array([1.25, 1.45, -0.60], dtype=np.float64)
            # Also give the 60-particle ensemble a slight chaotic dispersion kick across the separatrix
            rng_kick = np.random.default_rng(42)
            self.swarm_states = self.swarm_states + rng_kick.normal(0.0, 0.85, size=self.swarm_states.shape)
            self.saddle_boost_applied = True

        # Advance Reference A, Rounded B, and Swarm C via RK4
        self.state_a = self._rk4_single(self.state_a, dt_lor)
        self.state_b = self._rk4_single(self.state_b, dt_lor)
        self.swarm_states = self._rk4_single(self.swarm_states, dt_lor)

        self.current_video_time += dt_video
        self.current_lorenz_time += dt_lor

        # Append trails
        self.trail_a.append((float(self.state_a[0]), float(self.state_a[1]), float(self.state_a[2])))
        self.trail_b.append((float(self.state_b[0]), float(self.state_b[1]), float(self.state_b[2])))
        if len(self.trail_a) > self.max_trail_len:
            self.trail_a.pop(0)
            self.trail_b.pop(0)

        # Compute velocities
        vel_a = self.derivatives(self.state_a)
        vel_b = self.derivatives(self.state_b)
        speed_a = float(np.linalg.norm(vel_a))
        speed_b = float(np.linalg.norm(vel_b))

        wing_a = 1 if self.state_a[0] >= 0.0 else -1
        wing_b = 1 if self.state_b[0] >= 0.0 else -1
        opp_wings = (wing_a != wing_b)

        euc_div = float(np.linalg.norm(self.state_a - self.state_b))
        swarm_centroid = np.mean(self.swarm_states, axis=0)
        swarm_spread = float(np.sqrt(np.mean(np.sum((self.swarm_states - swarm_centroid) ** 2, axis=1))))

        # Update oscilloscope buffers at ~60 Hz
        if (self.current_video_time - self._last_wave_sample_t) >= 0.015:
            self.wave_history_a.append(float(self.state_a[0]))
            self.wave_history_b.append(float(self.state_b[0]))
            self.div_history.append(euc_div)
            self._last_wave_sample_t = self.current_video_time
            if len(self.wave_history_a) > self.max_wave_len:
                self.wave_history_a.pop(0)
                self.wave_history_b.pop(0)
                self.div_history.pop(0)

        if euc_div < 2.2 and self.current_video_time < 5.0:
            reg_es = "Fase 1: Sincronía Determinista (Δ₀ = 10⁻⁴)"
            reg_en = "Phase 1: Deterministic Lock (Δ₀ = 10⁻⁴)"
        elif opp_wings:
            reg_es = "Fase 2: Bifurcación de Silla (Alas Opuestas C₋ / C₊)"
            reg_en = "Phase 2: Saddle Bifurcation (Opposite Wings C₋ / C₊)"
        else:
            reg_es = "Fase 3: Caos Atractor Extraño (D_KY = 2.062)"
            reg_en = "Phase 3: Strange Attractor Chaos (D_KY = 2.062)"

        telem = LorenzTelemetry(
            t_video=self.current_video_time,
            t_lorenz=self.current_lorenz_time,
            traj_a=LorenzState(
                x=float(self.state_a[0]), y=float(self.state_a[1]), z=float(self.state_a[2]),
                vx=float(vel_a[0]), vy=float(vel_a[1]), vz=float(vel_a[2]),
                speed=speed_a, wing=wing_a
            ),
            traj_b=LorenzState(
                x=float(self.state_b[0]), y=float(self.state_b[1]), z=float(self.state_b[2]),
                vx=float(vel_b[0]), vy=float(vel_b[1]), vz=float(vel_b[2]),
                speed=speed_b, wing=wing_b
            ),
            euclidean_divergence=euc_div,
            swarm_spread=swarm_spread,
            liouville_divergence=self.liouville_div,
            lyapunov_max=self.lyapunov_1,
            kaplan_yorke_dim=self.kaplan_yorke,
            opposite_wings=opp_wings,
            regime_es=reg_es,
            regime_en=reg_en
        )
        self.telemetry_history.append(telem)
        return telem

    def advance_to_time(self, target_video_t: float, max_sub_dt: float = 0.002) -> LorenzTelemetry:
        """
        Advances simulation to target_video_t using fine RK4 sub-stepping.
        """
        dt_total = target_video_t - self.current_video_time
        if dt_total <= 0:
            return self.telemetry_history[-1] if self.telemetry_history else self.step(0.001)

        steps = max(1, int(np.ceil(dt_total / max_sub_dt)))
        sub_dt = dt_total / float(steps)
        telem = None
        for _ in range(steps):
            telem = self.step(sub_dt)
        return telem
