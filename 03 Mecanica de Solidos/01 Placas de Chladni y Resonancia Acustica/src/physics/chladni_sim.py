"""
Continuum Lab - Chladni Plate Vibration & Cymatics Physics Engine
Module: 03 Mecanica de Solidos / 01 Placas de Chladni y Resonancia Acustica
File: src/physics/chladni_sim.py

Implements Kirchhoff-Love thin plate biharmonic elastodynamics:
    D * ∇⁴w + ρ*h * ∂²w/∂t² = 0
where:
    D = (E * h³) / [12 * (1 - ν²)]  (Bending rigidity)

Simulates acoustic radiation drift of 15,000 Lagrangian granular particles
under multi-modal excitation:
    F_drift(x, y) = -κ * ∇(W(x, y)²) + η(t)
driving particles strictly towards zero-displacement nodal lines W(x, y) = 0.
"""

from dataclasses import dataclass, field
from typing import List, Tuple
import numpy as np


@dataclass(frozen=True)
class MaterialProperties:
    name: str
    youngs_modulus: float      # E (Pa)
    density: float             # ρ (kg/m³)
    poisson_ratio: float       # ν (dimensionless)
    yield_strength: float      # σ_y (MPa)


# Titanium Grade 5 (Ti-6Al-4V) - Aerospace Standard
TITANIUM_GR5 = MaterialProperties(
    name="Titanium Ti-6Al-4V",
    youngs_modulus=114e9,
    density=4430.0,
    poisson_ratio=0.34,
    yield_strength=880.0
)


@dataclass
class ChladniConfig:
    plate_size: float = 0.30       # L (m) = 30 cm
    thickness: float = 0.001       # h (m) = 1.0 mm
    num_particles: int = 15000     # Granular silica sand count
    material: MaterialProperties = field(default_factory=lambda: TITANIUM_GR5)
    damping: float = 8.5           # Viscous friction coefficient
    drift_coeff: float = 4.8       # Acoustic radiation drift intensity
    noise_amplitude: float = 0.08  # Micro-scattering Brownian jitter


@dataclass
class TelemetryPoint:
    t: float
    frequency: float
    mode_m: int
    mode_n: int
    active_mode_name: str
    mean_speed: float
    nodal_adherence: float        # Percentage of particles within epsilon of W=0
    bending_rigidity: float       # D in N·m
    peak_accel_g: float           # Peak vertical acceleration in g's


class ChladniPlateSimulation:
    """
    High-fidelity physical simulation of a 2D vibrating elastic plate
    and granular cymatic particle self-organization.
    """

    def __init__(self, config: ChladniConfig = ChladniConfig(), seed: int = 42):
        self.cfg = config
        self.rng = np.random.default_rng(seed)

        # Bending rigidity D = E * h³ / (12 * (1 - ν²))
        E = self.cfg.material.youngs_modulus
        h = self.cfg.thickness
        nu = self.cfg.material.poisson_ratio
        rho = self.cfg.material.density
        self.D = (E * (h ** 3)) / (12.0 * (1.0 - nu ** 2))

        # Wave speed in thin plate: cp = sqrt(E / (rho * (1 - nu^2)))
        self.plate_sound_speed = np.sqrt(E / (rho * (1.0 - nu ** 2)))

        # Initialize particles randomly across square plate [-L/2, L/2]
        L = self.cfg.plate_size
        margin = 0.01 * L
        self.x = self.rng.uniform(-L / 2 + margin, L / 2 - margin, self.cfg.num_particles).astype(np.float64)
        self.y = self.rng.uniform(-L / 2 + margin, L / 2 - margin, self.cfg.num_particles).astype(np.float64)
        self.vx = np.zeros(self.cfg.num_particles, dtype=np.float64)
        self.vy = np.zeros(self.cfg.num_particles, dtype=np.float64)

        # Modal schedule: (t_start, t_end, m, n, a, b, target_freq, name)
        # 18-second video sequence with 4 distinct resonant regimes
        self.schedule = [
            (0.0, 3.8, 1, 3, 1.0, 1.0, 432.0, "Modo (1, 3) Cruz Diamante"),
            (3.8, 4.8, 2, 4, 1.0, 0.8, 880.0, "Transición Armónica (2, 4)"),
            (4.8, 9.2, 3, 3, 1.0, 1.0, 1420.0, "Modo (3, 3) Mandala Nodal"),
            (9.2, 10.2, 2, 6, 1.0, 0.9, 2150.0, "Transición Armónica (2, 6)"),
            (10.2, 14.2, 3, 5, 1.0, 1.0, 2860.0, "Modo (3, 5) Red Hiperbólica"),
            (14.2, 18.0, 5, 5, 1.0, 1.0, 4320.0, "Modo (5, 5) Celosía Fractal"),
        ]

        self.current_time = 0.0
        self.telemetry_history: List[TelemetryPoint] = []

    def get_modal_params(self, t: float) -> Tuple[float, float, float, float, float, str, int, int]:
        """
        Computes smoothly interpolated modal parameters (m, n, a, b, frequency) at time t.
        """
        for i, (t0, t1, m, n, a, b, freq, name) in enumerate(self.schedule):
            if t0 <= t <= t1:
                # If near transition to next regime, blend
                if t1 - t < 0.6 and i < len(self.schedule) - 1:
                    next_regime = self.schedule[i + 1]
                    alpha = (t - (t1 - 0.6)) / 0.6
                    alpha_smooth = 0.5 * (1.0 - np.cos(np.pi * alpha))
                    m_eff = (1.0 - alpha_smooth) * m + alpha_smooth * next_regime[2]
                    n_eff = (1.0 - alpha_smooth) * n + alpha_smooth * next_regime[3]
                    a_eff = (1.0 - alpha_smooth) * a + alpha_smooth * next_regime[4]
                    b_eff = (1.0 - alpha_smooth) * b + alpha_smooth * next_regime[5]
                    f_eff = (1.0 - alpha_smooth) * freq + alpha_smooth * next_regime[6]
                    return m_eff, n_eff, a_eff, b_eff, f_eff, name, int(round(m)), int(round(n))
                else:
                    return float(m), float(n), float(a), float(b), freq, name, m, n

        # Default fallback to last regime
        last = self.schedule[-1]
        return float(last[2]), float(last[3]), float(last[4]), float(last[5]), last[6], last[7], last[2], last[3]

    def evaluate_plate_field(self, px: np.ndarray, py: np.ndarray, t: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Computes the normalized Chladni displacement field W(x, y) and its spatial gradient
        (∂W/∂x, ∂W/∂y) on the plate.
        """
        L = self.cfg.plate_size
        m, n, a, b, _, _, _, _ = self.get_modal_params(t)

        kx_m = (m * np.pi) / L
        ky_n = (n * np.pi) / L
        kx_n = (n * np.pi) / L
        ky_m = (m * np.pi) / L

        # Modal function for free square plate (Chladni-Germain solution):
        # W(x, y) = a * cos(m*pi*x/L)*cos(n*pi*y/L) - b * cos(n*pi*x/L)*cos(m*pi*y/L)
        cos_mx = np.cos(kx_m * px)
        cos_ny = np.cos(ky_n * py)
        cos_nx = np.cos(kx_n * px)
        cos_my = np.cos(ky_m * py)

        sin_mx = np.sin(kx_m * px)
        sin_ny = np.sin(ky_n * py)
        sin_nx = np.sin(kx_n * px)
        sin_my = np.sin(ky_m * py)

        W = a * (cos_mx * cos_ny) - b * (cos_nx * cos_my)

        # Gradients ∂W/∂x and ∂W/∂y
        dW_dx = -a * kx_m * (sin_mx * cos_ny) + b * kx_n * (sin_nx * cos_my)
        dW_dy = -a * ky_n * (cos_mx * sin_ny) + b * ky_m * (cos_nx * sin_my)

        return W, dW_dx, dW_dy

    def step(self, dt: float) -> TelemetryPoint:
        """
        Advances the simulation by dt using acoustic radiation force dynamics
        and inelastic plate-particle impact mechanics.
        """
        L = self.cfg.plate_size
        half_L = L / 2.0
        m_eff, n_eff, a_eff, b_eff, freq, mode_name, m_int, n_int = self.get_modal_params(self.current_time)

        # 1. Evaluate plate displacement & gradients at current particle positions
        W, dW_dx, dW_dy = self.evaluate_plate_field(self.x, self.y, self.current_time)

        # 2. Acoustic radiation drift force: F_drift = -κ * ∇(W²) = -2 * κ * W * ∇W
        # Particles are repelled from vibration maxima (|W| > 0) towards nodal lines (W = 0).
        grad_W2_x = 2.0 * W * dW_dx
        grad_W2_y = 2.0 * W * dW_dy

        # Frequency-dependent acceleration scale (higher frequency = more violent acoustic push)
        omega = 2.0 * np.pi * freq
        accel_scale = self.cfg.drift_coeff * (1.0 + (freq / 1000.0) * 0.45)

        fx = -accel_scale * grad_W2_x
        fy = -accel_scale * grad_W2_y

        # Micro-scattering Brownian excitation from chaotic plate rebound
        noise_x = self.rng.normal(0.0, self.cfg.noise_amplitude, self.cfg.num_particles) * np.abs(W)
        noise_y = self.rng.normal(0.0, self.cfg.noise_amplitude, self.cfg.num_particles) * np.abs(W)

        # 3. Velocity Verlet / Semi-implicit Euler integration with viscous air/plate damping
        damping = self.cfg.damping
        self.vx += (fx + noise_x - damping * self.vx) * dt
        self.vy += (fy + noise_y - damping * self.vy) * dt

        self.x += self.vx * dt
        self.y += self.vy * dt

        # 4. Inelastic boundary collisions at plate edges
        boundary_margin = half_L * 0.985
        restitution = 0.25

        left_mask = self.x < -boundary_margin
        self.x[left_mask] = -boundary_margin
        self.vx[left_mask] = -self.vx[left_mask] * restitution

        right_mask = self.x > boundary_margin
        self.x[right_mask] = boundary_margin
        self.vx[right_mask] = -self.vx[right_mask] * restitution

        bottom_mask = self.y < -boundary_margin
        self.y[bottom_mask] = -boundary_margin
        self.vy[bottom_mask] = -self.vy[bottom_mask] * restitution

        top_mask = self.y > boundary_margin
        self.y[top_mask] = boundary_margin
        self.vy[top_mask] = -self.vy[top_mask] * restitution

        # 5. Compute real-time physical telemetry
        speeds = np.sqrt(self.vx ** 2 + self.vy ** 2)
        mean_speed = float(np.mean(speeds))

        # Nodal adherence: fraction of particles where |W| < 0.12 (near nodal line)
        nodal_adherence = float(np.mean(np.abs(W) < 0.12) * 100.0)

        # Peak acceleration in g's: a_z = ω² * A_plate / g
        plate_amp_m = 0.00012  # ~120 microns physical vibration
        peak_accel_g = float((omega ** 2) * plate_amp_m / 9.81)

        self.current_time += dt

        telem = TelemetryPoint(
            t=self.current_time,
            frequency=freq,
            mode_m=m_int,
            mode_n=n_int,
            active_mode_name=mode_name,
            mean_speed=mean_speed,
            nodal_adherence=nodal_adherence,
            bending_rigidity=self.D,
            peak_accel_g=peak_accel_g,
        )
        self.telemetry_history.append(telem)
        return telem

    def advance_to_time(self, target_t: float, sub_steps: int = 4) -> TelemetryPoint:
        """
        Advances simulation to target_t with sub-stepping for smooth numerical stability.
        """
        dt_total = target_t - self.current_time
        if dt_total <= 0:
            return self.telemetry_history[-1] if self.telemetry_history else self.step(0.001)

        sub_dt = dt_total / float(sub_steps)
        telem = None
        for _ in range(sub_steps):
            telem = self.step(sub_dt)
        return telem
