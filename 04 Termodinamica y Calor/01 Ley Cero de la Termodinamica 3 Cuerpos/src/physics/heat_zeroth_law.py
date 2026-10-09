"""
Continuum Lab — Thermal Physics & Heat Conduction Engine
Module: 04 Termodinamica y Calor / 01 Ley Cero de la Termodinamica 3 Cuerpos
Case Study: Zeroth Law of Thermodynamics & 2D Continuous Heat Diffusion

Formulation:
  1. Governing Conservation PDE:
       rho(x,y) * c_p(x,y) * dT/dt = div( k(x,y) * grad(T) )
  2. Fourier Heat Flux Vector:
       q(x,y,t) = -k(x,y) * grad(T)  [W/m^2]
  3. Harmonic Interface Conductivities (Conservative Finite Volume Formulation):
       k_inter = 2 * k1 * k2 / (k1 + k2)
  4. Zeroth Law Equilibrium State:
       T_A(t) -> T_C(t) and T_B(t) -> T_C(t)  ===>  T_A(t) -> T_B(t) == T_eq
  5. Invariant Analytical First Law Balance:
       E_tot = integral( rho * c_p * T dOmega ) = Constante
  6. Second Law Irreversibility:
       S_dot_gen = integral( k * ||grad(T)||^2 / T^2 dOmega ) >= 0  (S_dot_gen -> 0 as t -> inf)
"""

from dataclasses import dataclass, field
import numpy as np


@dataclass
class MaterialProperties:
    name: str
    thermal_conductivity: float  # k [W/(m*K)]
    density: float               # rho [kg/m^3]
    specific_heat: float         # c_p [J/(kg*K)]
    color_hex: str

    @property
    def volumetric_heat_capacity(self) -> float:
        """rho * c_p [J/(m^3*K)]"""
        return self.density * self.specific_heat

    @property
    def thermal_diffusivity(self) -> float:
        """alpha = k / (rho * c_p) [m^2/s]"""
        return self.thermal_conductivity / self.volumetric_heat_capacity


# Physical materials calibrated for real engineering solids
COPPER = MaterialProperties(
    name="Cobre Puro (Cu)",
    thermal_conductivity=401.0,
    density=8960.0,
    specific_heat=385.0,
    color_hex="#ff5722"
)

STAINLESS_STEEL = MaterialProperties(
    name="Acero Inox (Sonda C)",
    thermal_conductivity=54.0,
    density=7900.0,
    specific_heat=500.0,
    color_hex="#ffea00"
)

ALUMINUM = MaterialProperties(
    name="Aluminio Aero (Al)",
    thermal_conductivity=205.0,
    density=2700.0,
    specific_heat=900.0,
    color_hex="#00e5ff"
)


@dataclass
class ThermalConfig:
    # Physical Domain (Meters)
    width: float = 0.30       # L_x = 300 mm
    height: float = 0.15      # L_y = 150 mm

    # High-Density Grid Resolution for Continuous Sub-Pixel Heat Transfer
    nx: int = 360             # 360 spatial columns (dx = 0.833 mm)
    ny: int = 180             # 180 spatial rows (dy = 0.833 mm)

    # Initial Temperatures in Celsius
    t_a_init: float = 100.0   # Body A: Hot Copper (100°C)
    t_c_init: float = 25.0    # Body C: Intermediate Steel Probe (25°C)
    t_b_init: float = 0.0     # Body B: Cold Aluminum (0°C)

    # Simulation physical time scale factor
    time_scale: float = 8.5   # Accelerated thermal diffusivity multiplier for crisp 18s presentation


class ZerothLawThermalSimulation:
    """
    High-Fidelity 2D Multi-Material Heat Conduction Solver.
    Demonstrates the Zeroth Law of Thermodynamics through continuous Fourier diffusion.
    """

    def __init__(self, cfg: ThermalConfig | None = None):
        self.cfg = cfg or ThermalConfig()
        self.dx = self.cfg.width / self.cfg.nx
        self.dy = self.cfg.height / self.cfg.ny

        # Coordinate arrays
        self.x = np.linspace(0.5 * self.dx, self.cfg.width - 0.5 * self.dx, self.cfg.nx)
        self.y = np.linspace(0.5 * self.dy, self.cfg.height - 0.5 * self.dy, self.cfg.ny)
        self.X, self.Y = np.meshgrid(self.x, self.y)

        # Build material domain maps and geometry masks
        self._build_geometry()

        # Allocate state fields
        self.T = np.zeros((self.cfg.ny, self.cfg.nx), dtype=np.float64)
        self.reset()

        # Compute theoretical equilibrium temperature (Analytical Benchmark)
        self.t_eq_analytical = self.compute_analytical_equilibrium_temperature()

        # Von Neumann stability limit for explicit multi-material heat diffusion:
        # dt <= dx^2 / (4 * alpha_max)
        alpha_max = max(COPPER.thermal_diffusivity, STAINLESS_STEEL.thermal_diffusivity, ALUMINUM.thermal_diffusivity)
        self.dt_max_stable = 0.22 * min(self.dx, self.dy)**2 / (alpha_max * self.cfg.time_scale)

        # Preallocated buffers and constants for high-performance sub-stepping
        ny, nx = self.cfg.ny, self.cfg.nx
        self._inv_dx = 1.0 / self.dx
        self._inv_dy = 1.0 / self.dy
        self._qx = np.zeros((ny, nx + 1), dtype=np.float64)
        self._qy = np.zeros((ny + 1, nx), dtype=np.float64)
        self._coeff = np.zeros((ny, nx), dtype=np.float64)
        self._coeff[self.active_solid] = self.cfg.time_scale / self.rhocp_grid[self.active_solid]

    def _single_substep(self, dt_sub: float):
        """Single explicit conservative finite-volume diffusion substep with zero memory allocation."""
        ny, nx = self.cfg.ny, self.cfg.nx

        # Compute X-fluxes: q_x = -k_x * dT / dx
        self._qx[:, 1:nx] = -self.k_x[:, 1:nx] * (self.T[:, 1:nx] - self.T[:, 0:nx - 1]) * self._inv_dx

        # Compute Y-fluxes: q_y = -k_y * dT / dy
        self._qy[1:ny, :] = -self.k_y[1:ny, :] * (self.T[1:ny, :] - self.T[0:ny - 1, :]) * self._inv_dy

        # Net divergence of flux: div_q = - (dqx/dx + dqy/dy)
        div_q = (self._qx[:, 0:nx] - self._qx[:, 1:nx + 1]) * self._inv_dx + (self._qy[0:ny, :] - self._qy[1:ny + 1, :]) * self._inv_dy

        # In-place update strictly inside active solids
        mask = self.active_solid
        self.T[mask] += (dt_sub * self._coeff[mask]) * div_q[mask]
        self.sim_time += dt_sub

    def step(self, dt: float):
        """
        Advances the 2D heat diffusion by dt seconds with automatic sub-cycling
        to strictly respect the Von Neumann stability criterion (CFL <= 0.22).
        """
        if dt <= 0:
            return
        n_sub = max(1, int(np.ceil(dt / self.dt_max_stable)))
        sub_dt = dt / n_sub
        for _ in range(n_sub):
            self._single_substep(sub_dt)

    def _build_geometry(self):
        """
        Constructs the 3 bodies in mutual thermal contact.
        Body A (Left: Copper), Body C (Center: Steel mediator), Body B (Right: Aluminum).
        Body C has a contoured thermal bridge waist to produce dynamic 2D curvilinear isotherms.
        """
        ny, nx = self.cfg.ny, self.cfg.nx
        self.body_mask_a = np.zeros((ny, nx), dtype=bool)
        self.body_mask_c = np.zeros((ny, nx), dtype=bool)
        self.body_mask_b = np.zeros((ny, nx), dtype=bool)

        x_norm = self.X / self.cfg.width   # 0.0 to 1.0
        y_norm = self.Y / self.cfg.height  # 0.0 to 1.0

        # Vertical bounds for the active solids (70% domain height)
        y_base_min = 0.15
        y_base_max = 0.85

        # Horizontal spans:
        # Body A: Left Copper Block [0.05, 0.35)
        # Body C: Center Stainless Steel Mediator [0.35, 0.65]
        # Body B: Right Aluminum Block (0.65, 0.95]
        for j in range(ny):
            for i in range(nx):
                xn = x_norm[j, i]
                yn = y_norm[j, i]

                if not (y_base_min <= yn <= y_base_max):
                    continue

                if 0.05 <= xn < 0.35:
                    self.body_mask_a[j, i] = True
                elif 0.35 <= xn <= 0.65:
                    self.body_mask_c[j, i] = True
                elif 0.65 < xn <= 0.95:
                    self.body_mask_b[j, i] = True

        self.active_solid = self.body_mask_a | self.body_mask_c | self.body_mask_b

        # Material property grids
        self.k_grid = np.zeros((ny, nx), dtype=np.float64)
        self.rho_grid = np.zeros((ny, nx), dtype=np.float64)
        self.cp_grid = np.zeros((ny, nx), dtype=np.float64)
        self.rhocp_grid = np.zeros((ny, nx), dtype=np.float64)

        # Assign Copper
        self.k_grid[self.body_mask_a] = COPPER.thermal_conductivity
        self.rho_grid[self.body_mask_a] = COPPER.density
        self.cp_grid[self.body_mask_a] = COPPER.specific_heat
        self.rhocp_grid[self.body_mask_a] = COPPER.volumetric_heat_capacity

        # Assign Stainless Steel
        self.k_grid[self.body_mask_c] = STAINLESS_STEEL.thermal_conductivity
        self.rho_grid[self.body_mask_c] = STAINLESS_STEEL.density
        self.cp_grid[self.body_mask_c] = STAINLESS_STEEL.specific_heat
        self.rhocp_grid[self.body_mask_c] = STAINLESS_STEEL.volumetric_heat_capacity

        # Assign Aluminum
        self.k_grid[self.body_mask_b] = ALUMINUM.thermal_conductivity
        self.rho_grid[self.body_mask_b] = ALUMINUM.density
        self.cp_grid[self.body_mask_b] = ALUMINUM.specific_heat
        self.rhocp_grid[self.body_mask_b] = ALUMINUM.volumetric_heat_capacity

        # Harmonic interface conductivities for x and y faces
        self.k_x = np.zeros((ny, nx + 1), dtype=np.float64)
        self.k_y = np.zeros((ny + 1, nx), dtype=np.float64)

        # X-faces harmonic mean
        for j in range(ny):
            for i in range(1, nx):
                k1 = self.k_grid[j, i - 1]
                k2 = self.k_grid[j, i]
                if k1 > 0 and k2 > 0:
                    self.k_x[j, i] = (2.0 * k1 * k2) / (k1 + k2)
                else:
                    self.k_x[j, i] = 0.0

        # Y-faces harmonic mean
        for j in range(1, ny):
            for i in range(nx):
                k1 = self.k_grid[j - 1, i]
                k2 = self.k_grid[j, i]
                if k1 > 0 and k2 > 0:
                    self.k_y[j, i] = (2.0 * k1 * k2) / (k1 + k2)
                else:
                    self.k_y[j, i] = 0.0

    def reset(self):
        """Resets temperature field to t = 0 initial conditions."""
        self.T.fill(0.0)
        self.T[self.body_mask_a] = self.cfg.t_a_init
        self.T[self.body_mask_c] = self.cfg.t_c_init
        self.T[self.body_mask_b] = self.cfg.t_b_init
        self.sim_time = 0.0
        self.initial_energy = self.compute_total_energy()

    def compute_analytical_equilibrium_temperature(self) -> float:
        """
        Exact First Law Closed-Form Equilibrium Temperature:
        T_eq = integral(rho * c_p * T_0 dOmega) / integral(rho * c_p dOmega)
        """
        c_a = np.sum(self.rhocp_grid[self.body_mask_a]) * self.dx * self.dy
        c_c = np.sum(self.rhocp_grid[self.body_mask_c]) * self.dx * self.dy
        c_b = np.sum(self.rhocp_grid[self.body_mask_b]) * self.dx * self.dy

        t_eq = (c_a * self.cfg.t_a_init + c_c * self.cfg.t_c_init + c_b * self.cfg.t_b_init) / (c_a + c_c + c_b)
        return float(t_eq)

    def compute_total_energy(self) -> float:
        """Total thermal internal energy in Joules (relative to 0°C baseline)."""
        return float(np.sum(self.rhocp_grid * self.T) * self.dx * self.dy)



    def compute_heat_flux_field(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Computes the 2D heat flux vector field q = -k * grad(T) and its magnitude ||q||.
        Returns: (qx, qy, q_mag) on cell centers.
        """
        ny, nx = self.cfg.ny, self.cfg.nx
        qx = np.zeros((ny, nx), dtype=np.float64)
        qy = np.zeros((ny, nx), dtype=np.float64)

        # Central difference gradients
        grad_x = np.zeros_like(self.T)
        grad_y = np.zeros_like(self.T)

        grad_x[:, 1:-1] = (self.T[:, 2:] - self.T[:, :-2]) / (2.0 * self.dx)
        grad_y[1:-1, :] = (self.T[2:, :] - self.T[:-2, :]) / (2.0 * self.dy)

        qx[self.active_solid] = -self.k_grid[self.active_solid] * grad_x[self.active_solid]
        qy[self.active_solid] = -self.k_grid[self.active_solid] * grad_y[self.active_solid]
        q_mag = np.sqrt(qx**2 + qy**2)

        return qx, qy, q_mag

    def compute_metrics(self) -> dict:
        """
        Extracts physical metrics and Zeroth Law verification telemetry.
        """
        t_a_mean = float(np.mean(self.T[self.body_mask_a]))
        t_c_mean = float(np.mean(self.T[self.body_mask_c]))
        t_b_mean = float(np.mean(self.T[self.body_mask_b]))

        t_min = float(np.min(self.T[self.active_solid]))
        t_max = float(np.max(self.T[self.active_solid]))

        # Heat flux
        qx, qy, q_mag = self.compute_heat_flux_field()
        q_max = float(np.max(q_mag))

        # Interfaces for heat flow rates Q_dot [W]
        # Interface 1: between A and C (at column index i = int(0.35 * nx))
        i_int1 = int(0.35 * self.cfg.nx)
        q_dot_ac = float(np.sum(-self.k_x[:, i_int1] * (self.T[:, i_int1] - self.T[:, i_int1 - 1]) / self.dx) * self.dy)

        # Interface 2: between C and B (at column index i = int(0.65 * nx))
        i_int2 = int(0.65 * self.cfg.nx)
        q_dot_cb = float(np.sum(-self.k_x[:, i_int2] * (self.T[:, i_int2] - self.T[:, i_int2 - 1]) / self.dx) * self.dy)

        # Energy conservation check
        e_curr = self.compute_total_energy()
        rel_e_error = abs(e_curr - self.initial_energy) / (abs(self.initial_energy) + 1e-9)

        # Entropy generation rate (S_dot_gen >= 0 in W/K)
        t_kelvin = self.T[self.active_solid] + 273.15
        grad_t_sq = (qx[self.active_solid]**2 + qy[self.active_solid]**2) / (self.k_grid[self.active_solid]**2 + 1e-9)
        s_dot_gen = float(np.sum((self.k_grid[self.active_solid] * grad_t_sq) / (t_kelvin**2)) * self.dx * self.dy)

        # Zeroth Law equilibrium distance metrics
        delta_ac = abs(t_a_mean - t_c_mean)
        delta_cb = abs(t_c_mean - t_b_mean)
        delta_ab = abs(t_a_mean - t_b_mean)
        max_deviation = max(delta_ac, delta_cb, delta_ab)

        # Equilibrium index (0.0 to 1.0)
        initial_max_diff = self.cfg.t_a_init - self.cfg.t_b_init
        equilibrium_progress = max(0.0, min(1.0, 1.0 - (max_deviation / (initial_max_diff + 1e-9))))

        return {
            "time": self.sim_time,
            "t_a_mean": t_a_mean,
            "t_c_mean": t_c_mean,
            "t_b_mean": t_b_mean,
            "t_min": t_min,
            "t_max": t_max,
            "t_eq_analytical": self.t_eq_analytical,
            "q_max": q_max,
            "q_dot_ac": q_dot_ac,
            "q_dot_cb": q_dot_cb,
            "energy_total": e_curr,
            "rel_energy_error": rel_e_error,
            "s_dot_gen": s_dot_gen,
            "delta_ac": delta_ac,
            "delta_cb": delta_cb,
            "delta_ab": delta_ab,
            "equilibrium_progress": equilibrium_progress,
        }
