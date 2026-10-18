"""
Continuum Lab - 2D Incompressible Navier-Stokes Kelvin-Helmholtz Simulation
Module: 01 Mecanica de Fluidos / 04 Inestabilidad Kelvin Helmholtz
File: src/physics/kelvin_helmholtz_sim.py

Rock-solid, fully de-aliased 2D Pseudospectral Navier-Stokes solver:
    ∂ω/∂t + (u · ∇)ω = ν ∇²ω
    ∇²ψ = -ω,   u = ∂ψ/∂y,   v = -∂ψ/∂x

Initial Conditions:
    u(x, y, 0) = U₀ tanh(y / δ₀)
    ω(x, y, 0) = - (U₀ / δ₀) sech²(y / δ₀)
    Perturbation: v'(x, y, 0) = ∑ A_m sin(k_m x + φ_m) exp(-y² / σ²)
"""

from dataclasses import dataclass
import numpy as np
from scipy.fft import fft2, ifft2, fftfreq


@dataclass
class KelvinHelmholtzConfig:
    """Simulation configuration parameters for Kelvin-Helmholtz instability."""
    Lx: float = 2.0                 # Domain length in x [m]
    Ly: float = 1.0                 # Domain height in y [m]
    Nx: int = 256                   # Power-of-2 resolution in x
    Ny: int = 128                   # Power-of-2 resolution in y
    U0: float = 1.0                 # Half-velocity difference (ΔU = 2*U0) [m/s]
    delta0: float = 0.045           # Initial shear layer thickness [m]
    nu: float = 8.0e-5              # Kinematic viscosity [m²/s] (Re ≈ 2500)
    rho: float = 1.0                # Fluid density [kg/m³]
    g: float = 9.81                 # Gravitational acceleration [m/s²]
    drho: float = 0.005             # Small density contrast for Richardson number Ri < 0.25
    pert_amp1: float = 0.045        # Primary mode perturbation amplitude (2 billows)
    pert_amp2: float = 0.015        # Subharmonic mode perturbation amplitude (pairing)
    dt: float = 0.005               # Integration time step [s] (CFL ≈ 0.6)
    fps: int = 60                   # Output video frame rate
    duration: float = 14.0          # Simulation duration [s]
    num_particles: int = 400        # Number of Lagrangian passive tracers


@dataclass
class TelemetryPoint:
    """Instantaneous physical telemetry record."""
    t: float
    enstrophy: float                # Ω(t) = 0.5 ∬ ω² dx dy
    kinetic_energy: float           # E_k(t) = 0.5 ∬ (u² + v²) dx dy
    max_vorticity: float            # max |ω(x,y)|
    total_circulation: float        # Γ = ∬ ω dx dy
    momentum_thickness: float       # θ(t) = ∫ (1/4 - (U_mean/2U0)²) dy
    richardson_number: float        # Ri = (g / ρ) * (dρ/dy) / (du/dy)²
    phase_name_es: str              # Phase descriptor (ES)
    phase_name_en: str              # Phase descriptor (EN)


class KelvinHelmholtzSimulation:
    """
    Rock-solid 2D Pseudospectral Navier-Stokes solver with 2/3 de-aliasing
    for stable Kelvin-Helmholtz roll-up and cat's-eye vortex pairing.
    """

    def __init__(self, config: KelvinHelmholtzConfig | None = None):
        self.cfg = config or KelvinHelmholtzConfig()

        # Spatial grid
        self.dx = self.cfg.Lx / self.cfg.Nx
        self.dy = self.cfg.Ly / self.cfg.Ny
        self.x = np.linspace(0, self.cfg.Lx, self.cfg.Nx, endpoint=False)
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
        self.psi = np.zeros((self.cfg.Ny, self.cfg.Nx), dtype=np.float64)
        self.u = np.zeros((self.cfg.Ny, self.cfg.Nx), dtype=np.float64)
        self.v = np.zeros((self.cfg.Ny, self.cfg.Nx), dtype=np.float64)

        # Time tracking
        self.t = 0.0
        self.step_count = 0
        self.telemetry_history: list[TelemetryPoint] = []

        # Lagrangian passive tracer particles
        np.random.seed(42)
        px = np.random.uniform(0.0, self.cfg.Lx, self.cfg.num_particles)
        py = np.random.normal(0.0, self.cfg.delta0 * 1.0, self.cfg.num_particles)
        py = np.clip(py, -self.cfg.Ly * 0.45, self.cfg.Ly * 0.45)
        self.particle_pos = np.column_stack((px, py))
        self.particle_orig_layer = np.where(py >= 0.0, 1.0, -1.0)

        self.reset()

    def reset(self):
        """Initializes the base hyperbolic tangent shear layer with perturbations."""
        self.t = 0.0
        self.step_count = 0
        self.telemetry_history.clear()

        # Base shear vorticity: ω0(y) = - (U0 / delta0) * sech²(y / delta0)
        omega_base = -(self.cfg.U0 / self.cfg.delta0) / (np.cosh(self.Y / self.cfg.delta0) ** 2)

        # Perturbation modes:
        k1 = 4.0 * np.pi / self.cfg.Lx
        k2 = 2.0 * np.pi / self.cfg.Lx
        envelope = np.exp(-(self.Y / (1.8 * self.cfg.delta0)) ** 2)

        dv_dx = (
            self.cfg.pert_amp1 * k1 * np.cos(k1 * self.X) +
            self.cfg.pert_amp2 * k2 * np.cos(k2 * self.X + 0.4)
        ) * envelope

        self.omega = omega_base + dv_dx

        # Solve for initial velocity and streamfunction
        self._invert_poisson()

        # Record initial telemetry
        self._record_telemetry()

    def _invert_poisson(self):
        """Solves ∇²ψ = -ω and computes (u, v) in spectral space."""
        omega_hat = fft2(self.omega) * self.dealias_mask
        omega_hat[0, 0] = 0.0

        psi_hat = omega_hat * self.inv_K_sq
        u_hat = 1j * self.KY * psi_hat
        v_hat = -1j * self.KX * psi_hat

        self.psi = np.real(ifft2(psi_hat))
        self.u = np.real(ifft2(u_hat))
        self.v = np.real(ifft2(v_hat))

    def _rhs(self, omega_field: np.ndarray) -> np.ndarray:
        """
        Conservative flux formulation with 2/3 de-aliasing:
        dω/dt = - [ ∂(uω)/∂x + ∂(vω)/∂y ] + ν ∇²ω
        """
        omega_hat = fft2(omega_field) * self.dealias_mask
        omega_hat[0, 0] = 0.0

        psi_hat = omega_hat * self.inv_K_sq
        u = np.real(ifft2(1j * self.KY * psi_hat))
        v = np.real(ifft2(-1j * self.KX * psi_hat))
        om = np.real(ifft2(omega_hat))

        flux_x = u * om
        flux_y = v * om

        flux_x_hat = fft2(flux_x) * self.dealias_mask
        flux_y_hat = fft2(flux_y) * self.dealias_mask

        div_flux_hat = 1j * self.KX * flux_x_hat + 1j * self.KY * flux_y_hat
        diff_hat = -self.cfg.nu * self.K_sq * omega_hat

        domega_hat = -div_flux_hat + diff_hat
        domega_hat *= self.dealias_mask

        return np.real(ifft2(domega_hat))

    def step(self):
        """Advances simulation by dt using 4th-order Runge-Kutta (RK4)."""
        dt = self.cfg.dt

        k1 = self._rhs(self.omega)
        k2 = self._rhs(self.omega + 0.5 * dt * k1)
        k3 = self._rhs(self.omega + 0.5 * dt * k2)
        k4 = self._rhs(self.omega + dt * k3)

        self.omega += (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

        # Invert Poisson for updated velocities
        self._invert_poisson()

        # Advect particles
        self._advect_particles(dt)

        self.t += dt
        self.step_count += 1

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

    def _advect_particles(self, dt: float):
        """Advects Lagrangian passive tracers using RK2."""
        u1, v1 = self._interpolate_velocity(self.particle_pos)
        pos_half = self.particle_pos.copy()
        pos_half[:, 0] = np.mod(pos_half[:, 0] + 0.5 * dt * u1, self.cfg.Lx)
        pos_half[:, 1] = np.clip(pos_half[:, 1] + 0.5 * dt * v1, -self.cfg.Ly * 0.48, self.cfg.Ly * 0.48)

        u2, v2 = self._interpolate_velocity(pos_half)
        self.particle_pos[:, 0] = np.mod(self.particle_pos[:, 0] + dt * u2, self.cfg.Lx)
        self.particle_pos[:, 1] = np.clip(self.particle_pos[:, 1] + dt * v2, -self.cfg.Ly * 0.48, self.cfg.Ly * 0.48)

    def get_phase_name(self) -> tuple[str, str]:
        """Returns the scientific phase name in ES and EN based on current time."""
        t_norm = self.t / self.cfg.duration
        if t_norm < 0.22:
            return (
                "FASE 1: CIZALLADURA LAMINAR Y PERTURBACIÓN LINEAL",
                "PHASE 1: LAMINAR SHEAR & LINEAR PERTURBATION"
            )
        elif t_norm < 0.52:
            return (
                "FASE 2: CRECIMIENTO EXPONENCIAL Y ONDULACIÓN DE INTERFAZ",
                "PHASE 2: EXPONENTIAL GROWTH & INTERFACE WAVINESS"
            )
        elif t_norm < 0.80:
            return (
                "FASE 3: ENROLLAMIENTO CAT'S-EYE Y SATURACIÓN NO LINEAL",
                "PHASE 3: CAT'S-EYE VORTEX ROLL-UP & NON-LINEAR SATURATION"
            )
        else:
            return (
                "FASE 4: ESTIRAMIENTO DE FILAMENTOS Y PAIRING DE VÓRTICES",
                "PHASE 4: FILAMENT BRAID STRETCHING & VORTEX PAIRING"
            )

    def _record_telemetry(self) -> TelemetryPoint:
        """Calculates instantaneous integral physical invariants and metrics."""
        enstrophy = 0.5 * np.sum(self.omega**2) * self.dx * self.dy
        ke = 0.5 * np.sum(self.u**2 + self.v**2) * self.dx * self.dy
        max_vort = float(np.max(np.abs(self.omega)))
        circulation = float(np.sum(self.omega) * self.dx * self.dy)

        u_mean_y = np.mean(self.u, axis=1)
        momentum_thickness = float(np.sum(0.25 - (u_mean_y / (2.0 * self.cfg.U0))**2) * self.dy)

        du_dy_max = max(1e-3, self.cfg.U0 / self.cfg.delta0)
        drho_dy = self.cfg.drho / (2.0 * self.cfg.delta0)
        richardson = float((self.cfg.g / self.cfg.rho) * drho_dy / (du_dy_max**2))

        phase_es, phase_en = self.get_phase_name()

        pt = TelemetryPoint(
            t=self.t,
            enstrophy=float(enstrophy),
            kinetic_energy=float(ke),
            max_vorticity=max_vort,
            total_circulation=circulation,
            momentum_thickness=momentum_thickness,
            richardson_number=richardson,
            phase_name_es=phase_es,
            phase_name_en=phase_en,
        )
        self.telemetry_history.append(pt)
        return pt

    def advance_to_time(self, target_t: float) -> TelemetryPoint:
        """Steps simulation forward until target_t is reached, recording telemetry."""
        while self.t < target_t - 1e-6:
            self.step()
        return self._record_telemetry()
