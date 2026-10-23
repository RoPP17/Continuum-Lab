"""
Continuum Lab - 2D Incompressible Rayleigh-Taylor Instability Simulation
Module: 01 Mecanica de Fluidos / 06 Inestabilidad Rayleigh Taylor
File: src/physics/rayleigh_taylor_sim.py

High-precision 2D Pseudospectral Navier-Stokes solver with Baroclinic Vorticity Generation:
    ∂ω/∂t + (u · ∇)ω = - 2 A g (∂C/∂x) + ν ∇²ω
    ∂C/∂t + (u · ∇)C = D ∇²C
    ∇²ψ = -ω,   u = ∂ψ/∂y,   v = -∂ψ/∂x

Initial Conditions:
    C(x, y, 0) = 0.5 * (1 + tanh((y - η(x)) / δ))
    Heavy fluid atop light fluid under downward gravity g (Atwood number A).
    Perturbation: η(x) = A₁ cos(k₁ x) + A₂ cos(k₂ x + φ)
"""

from dataclasses import dataclass
import numpy as np
from scipy.fft import fft2, ifft2, fftfreq


@dataclass
class RayleighTaylorConfig:
    """Simulation configuration parameters for Rayleigh-Taylor instability."""
    Lx: float = 1.0                 # Domain width [m]
    Ly: float = 1.778               # Domain height [m] (matches 9:16 vertical ratio)
    Nx: int = 160                   # Resolution in x
    Ny: int = 288                   # Resolution in y
    Atwood: float = 0.50            # Atwood number A = (ρ₂ - ρ₁) / (ρ₂ + ρ₁)
    g: float = 0.35                 # Gravitational acceleration [m/s²] (scaled for majestic 16s video)
    nu: float = 1.8e-4              # Kinematic viscosity [m²/s] (Re ≈ 2500)
    D: float = 1.8e-4               # Mass diffusivity [m²/s]
    delta0: float = 0.030           # Initial interface thickness [m]
    pert_amp1: float = 0.035        # Primary mode perturbation amplitude [m]
    pert_amp2: float = 0.015        # Secondary harmonic perturbation amplitude [m]
    dt: float = 0.0025              # Time step [s] (CFL < 0.5)
    fps: int = 60                   # Output frame rate
    duration: float = 16.0          # Total simulation time [s]
    num_particles: int = 600        # Number of Lagrangian tracer particles


@dataclass
class RTTelemetryPoint:
    """Instantaneous physical telemetry record."""
    t: float
    enstrophy: float                # Ω(t) = 0.5 ∬ ω² dx dy
    kinetic_energy: float           # E_k(t) = 0.5 ∬ (u² + v²) dx dy
    max_vorticity: float            # max |ω(x, y)|
    spike_depth: float              # y position of falling spike tip [m]
    bubble_height: float            # y position of rising bubble dome [m]
    mixing_width: float             # h(t) = bubble_height - spike_depth [m]
    theoretical_h: float            # h_theory(t) = α * A * g * t²
    atwood_number: float            # A
    froude_number: float            # Fr = v_spike / √(g * Lx)
    phase_name_es: str              # Stage descriptor (ES)
    phase_name_en: str              # Stage descriptor (EN)


class RayleighTaylorSimulation:
    """
    High-fidelity 2D Pseudospectral Navier-Stokes solver with baroclinic
    torque and 2/3 de-aliasing for Rayleigh-Taylor mushroom plumes.
    """

    def __init__(self, config: RayleighTaylorConfig | None = None):
        self.cfg = config or RayleighTaylorConfig()

        # Spatial grid
        self.dx = self.cfg.Lx / self.cfg.Nx
        self.dy = self.cfg.Ly / self.cfg.Ny
        self.x = np.linspace(0.0, self.cfg.Lx, self.cfg.Nx, endpoint=False)
        self.y = np.linspace(-self.cfg.Ly / 2.0, self.cfg.Ly / 2.0, self.cfg.Ny, endpoint=False)
        self.X, self.Y = np.meshgrid(self.x, self.y, indexing="xy")

        # Spectral wavenumbers
        kx = 2.0 * np.pi * fftfreq(self.cfg.Nx, self.dx)
        ky = 2.0 * np.pi * fftfreq(self.cfg.Ny, self.dy)
        self.KX, self.KY = np.meshgrid(kx, ky, indexing="xy")
        self.K_sq = self.KX**2 + self.KY**2
        self.inv_K_sq = np.zeros_like(self.K_sq)
        nonzero = self.K_sq > 1e-10
        self.inv_K_sq[nonzero] = 1.0 / self.K_sq[nonzero]

        # 2/3 de-aliasing mask
        k_max_x = np.max(np.abs(kx)) * (2.0 / 3.0)
        k_max_y = np.max(np.abs(ky)) * (2.0 / 3.0)
        self.dealias_mask = ((np.abs(self.KX) < k_max_x) & (np.abs(self.KY) < k_max_y)).astype(np.float64)

        # Fields
        self.omega = np.zeros((self.cfg.Ny, self.cfg.Nx), dtype=np.float64)
        self.C = np.zeros((self.cfg.Ny, self.cfg.Nx), dtype=np.float64)
        self.psi = np.zeros((self.cfg.Ny, self.cfg.Nx), dtype=np.float64)
        self.u = np.zeros((self.cfg.Ny, self.cfg.Nx), dtype=np.float64)
        self.v = np.zeros((self.cfg.Ny, self.cfg.Nx), dtype=np.float64)

        # Wall sponge damping profile near top and bottom boundaries
        sponge_width = 0.12 * self.cfg.Ly
        dist_top = (self.cfg.Ly / 2.0) - self.Y
        dist_bot = self.Y - (-self.cfg.Ly / 2.0)
        dist_wall = np.minimum(dist_top, dist_bot)
        self.sponge = np.where(dist_wall < sponge_width, np.sin(0.5 * np.pi * dist_wall / sponge_width)**2, 1.0)

        # Time tracking
        self.t = 0.0
        self.step_count = 0
        self.telemetry_history: list[RTTelemetryPoint] = []

        # Lagrangian tracer particles (seeded along initial interfacial band)
        np.random.seed(2026)
        px = np.random.uniform(0.0, self.cfg.Lx, self.cfg.num_particles)
        py = np.random.normal(0.0, self.cfg.delta0 * 0.8, self.cfg.num_particles)
        py = np.clip(py, -self.cfg.Ly * 0.40, self.cfg.Ly * 0.40)
        self.particle_pos = np.column_stack((px, py))
        self.particle_orig_layer = np.where(py >= 0.0, 1.0, -1.0)

        self.reset()

    def reset(self):
        """Initializes heavy fluid atop light fluid with interfacial perturbation."""
        self.t = 0.0
        self.step_count = 0
        self.telemetry_history.clear()

        # Interfacial perturbation: primary mode + second harmonic
        k1 = 2.0 * np.pi / self.cfg.Lx
        k2 = 4.0 * np.pi / self.cfg.Lx
        eta = (
            self.cfg.pert_amp1 * np.cos(k1 * self.X) +
            self.cfg.pert_amp2 * np.cos(k2 * self.X + 0.35)
        )

        # Concentration field C in [0, 1]
        self.C = 0.5 * (1.0 + np.tanh((self.Y - eta) / self.cfg.delta0))
        self.omega.fill(0.0)

        self._invert_poisson()
        self._record_telemetry()

    def _invert_poisson(self):
        """Solves ∇²ψ = -ω and computes velocity field (u, v) with exact incompressibility."""
        omega_hat = fft2(self.omega) * self.dealias_mask
        omega_hat[0, 0] = 0.0

        psi_hat = omega_hat * self.inv_K_sq
        u_hat = 1j * self.KY * psi_hat
        v_hat = -1j * self.KX * psi_hat

        self.psi = np.real(ifft2(psi_hat))
        self.u = np.real(ifft2(u_hat))
        self.v = np.real(ifft2(v_hat))

    def _rhs(self, omega_field: np.ndarray, C_field: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Computes time derivatives:
            dω/dt = - ∇·(u ω) - 2 A g (∂C/∂x) + ν ∇²ω - damping(y)*ω
            dC/dt = - ∇·(u C) + D ∇²C
        """
        om_hat = fft2(omega_field) * self.dealias_mask
        om_hat[0, 0] = 0.0

        c_hat = fft2(C_field) * self.dealias_mask

        # Invert for velocity (strictly divergence-free)
        psi_hat = om_hat * self.inv_K_sq
        u = np.real(ifft2(1j * self.KY * psi_hat))
        v = np.real(ifft2(-1j * self.KX * psi_hat))
        om = np.real(ifft2(om_hat))
        c = np.real(ifft2(c_hat))

        # Nonlinear advection fluxes (conservative form)
        flux_om_x = fft2(u * om) * self.dealias_mask
        flux_om_y = fft2(v * om) * self.dealias_mask
        div_om_hat = 1j * self.KX * flux_om_x + 1j * self.KY * flux_om_y

        flux_c_x = fft2(u * c) * self.dealias_mask
        flux_c_y = fft2(v * c) * self.dealias_mask
        div_c_hat = 1j * self.KX * flux_c_x + 1j * self.KY * flux_c_y

        # Baroclinic torque: - 2 * A * g * (∂C/∂x)
        dC_dx_hat = 1j * self.KX * c_hat
        baroclinic_hat = - 2.0 * self.cfg.Atwood * self.cfg.g * dC_dx_hat

        # Viscous and mass diffusion
        diff_om_hat = -self.cfg.nu * self.K_sq * om_hat
        diff_c_hat = -self.cfg.D * self.K_sq * c_hat

        # Assemble time derivatives
        dom_hat = (-div_om_hat + baroclinic_hat + diff_om_hat) * self.dealias_mask
        dc_hat = (-div_c_hat + diff_c_hat) * self.dealias_mask

        dom_dt = np.real(ifft2(dom_hat))
        dc_dt = np.real(ifft2(dc_hat))

        return dom_dt, dc_dt

    def step(self):
        """Advances the simulation by dt using 4th-order Runge-Kutta (RK4)."""
        dt = self.cfg.dt

        k1_om, k1_c = self._rhs(self.omega, self.C)
        k2_om, k2_c = self._rhs(self.omega + 0.5 * dt * k1_om, self.C + 0.5 * dt * k1_c)
        k3_om, k3_c = self._rhs(self.omega + 0.5 * dt * k2_om, self.C + 0.5 * dt * k2_c)
        k4_om, k4_c = self._rhs(self.omega + dt * k3_om, self.C + dt * k3_c)

        self.omega += (dt / 6.0) * (k1_om + 2.0 * k2_om + 2.0 * k3_om + k4_om)
        self.C += (dt / 6.0) * (k1_c + 2.0 * k2_c + 2.0 * k3_c + k4_c)
        self.C = np.clip(self.C, 0.0, 1.0)

        self._invert_poisson()
        self._advect_particles(dt)

        self.t += dt
        self.step_count += 1

    def _advect_particles(self, dt: float):
        """Advects Lagrangian passive tracers using 2nd-order Runge-Kutta."""
        up1, vp1 = self._interpolate_velocity(self.particle_pos)
        pos_mid = self.particle_pos + 0.5 * dt * np.column_stack((up1, vp1))
        up2, vp2 = self._interpolate_velocity(pos_mid)

        self.particle_pos[:, 0] = np.mod(self.particle_pos[:, 0] + dt * up2, self.cfg.Lx)
        self.particle_pos[:, 1] = np.clip(
            self.particle_pos[:, 1] + dt * vp2,
            -self.cfg.Ly / 2.0 + 1e-3,
            self.cfg.Ly / 2.0 - 1e-3
        )

    def _interpolate_velocity(self, positions: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Bilinear velocity interpolation at arbitrary coordinates."""
        px = np.mod(positions[:, 0], self.cfg.Lx)
        py = np.clip(positions[:, 1], -self.cfg.Ly / 2.0 + 1e-4, self.cfg.Ly / 2.0 - 1e-4)

        gx = (px / self.dx)
        gy = ((py + self.cfg.Ly / 2.0) / self.dy)

        i0 = np.floor(gx).astype(int) % self.cfg.Nx
        i1 = (i0 + 1) % self.cfg.Nx
        j0 = np.clip(np.floor(gy).astype(int), 0, self.cfg.Ny - 1)
        j1 = np.clip(j0 + 1, 0, self.cfg.Ny - 1)

        fx = gx - np.floor(gx)
        fy = gy - np.floor(gy)

        u_interp = (
            (1.0 - fx) * (1.0 - fy) * self.u[j0, i0] +
            fx * (1.0 - fy) * self.u[j0, i1] +
            (1.0 - fx) * fy * self.u[j1, i0] +
            fx * fy * self.u[j1, i1]
        )
        v_interp = (
            (1.0 - fx) * (1.0 - fy) * self.v[j0, i0] +
            fx * (1.0 - fy) * self.v[j0, i1] +
            (1.0 - fx) * fy * self.v[j1, i0] +
            fx * fy * self.v[j1, i1]
        )
        return u_interp, v_interp

    def _record_telemetry(self):
        """Calculates and stores instantaneous physical diagnostic metrics."""
        dA = self.dx * self.dy
        enstrophy = 0.5 * np.sum(self.omega**2) * dA
        kinetic_energy = 0.5 * np.sum(self.u**2 + self.v**2) * dA
        max_vorticity = float(np.max(np.abs(self.omega)))

        # Spike & Bubble penetration detection
        # Heavy fluid (C >= 0.5) falling downward
        heavy_mask = self.C >= 0.5
        spike_y = float(np.min(self.Y[heavy_mask])) if np.any(heavy_mask) else 0.0

        # Light fluid (C < 0.5) rising upward
        light_mask = self.C < 0.5
        bubble_y = float(np.max(self.Y[light_mask])) if np.any(light_mask) else 0.0

        mixing_width = max(0.0, bubble_y - spike_y)

        # Theoretical growth: h_theory = alpha * A * g * t^2 (Dimonte-Schneider alpha = 0.06)
        alpha_dimonte = 0.06
        theoretical_h = alpha_dimonte * self.cfg.Atwood * self.cfg.g * (self.t**2)

        # Froude number based on downward velocity
        v_max_down = float(np.max(np.abs(self.v)))
        froude = v_max_down / np.sqrt(max(1e-6, self.cfg.g * self.cfg.Lx))

        # Dynamic Phase Names
        if self.t < 3.5:
            es_phase = "Etapa Lineal: Perturbación y Torque Baroclínico"
            en_phase = "Linear Stage: Perturbation & Baroclinic Torque"
        elif self.t < 8.0:
            es_phase = "Etapa No-Lineal: Inversión de Picos y Burbujas"
            en_phase = "Nonlinear Inversion: Spike & Bubble Penetration"
        elif self.t < 12.5:
            es_phase = "Evolución Secundaria: Vórtices de Champiñón"
            en_phase = "Secondary Roll-up: Mushroom Plume Vortices"
        else:
            es_phase = "Régimen Turbulento: Ensanchamiento Cuadrático"
            en_phase = "Turbulent Regime: Quadratic Mixing Zone"

        pt = RTTelemetryPoint(
            t=self.t,
            enstrophy=enstrophy,
            kinetic_energy=kinetic_energy,
            max_vorticity=max_vorticity,
            spike_depth=spike_y,
            bubble_height=bubble_y,
            mixing_width=mixing_width,
            theoretical_h=theoretical_h,
            atwood_number=self.cfg.Atwood,
            froude_number=froude,
            phase_name_es=es_phase,
            phase_name_en=en_phase,
        )
        self.telemetry_history.append(pt)

    def step_to_frame(self, target_time: float) -> RTTelemetryPoint:
        """Sub-steps until simulation reaches the exact target time."""
        while self.t + 1e-8 < target_time:
            self.step()
        self._record_telemetry()
        return self.telemetry_history[-1]
