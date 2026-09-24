"""
Continuum Lab — Physics Engine
Lattice Boltzmann Method (LBM) — 2D 9-Velocity Model (D2Q9-BGK)
Division: Fluid Dynamics & Non-Equilibrium Kinetics

Governing Physics:
  - Incompressible Navier-Stokes approximation via Bhatnagar-Gross-Krook (BGK) relaxation.
  - Dimensionless scaling: Re = (U_inf * D) / nu, Ma = U_inf / c_s < 0.3 (incompressible regime).
  - Hydrodynamic Force Telemetry: Momentum Exchange Method (MEM) for lift (C_L) and drag (C_D).
  - High-performance backends: Vectorized NumPy (CPU) & Taichi CUDA (NVIDIA RTX 5070).
"""

from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np

# Exact D2Q9 Discrete Velocity Lattice Constants
# Index convention:
#   0: (0, 0)
#   1: (1, 0),  2: (0, 1),  3: (-1, 0), 4: (0, -1)   [orthogonal, weight 1/9]
#   5: (1, 1),  6: (-1, 1), 7: (-1, -1), 8: (1, -1)  [diagonal,   weight 1/36]

LATTICE_C = np.array([
    [0, 0],    # 0
    [1, 0],    # 1
    [0, 1],    # 2
    [-1, 0],   # 3
    [0, -1],   # 4
    [1, 1],    # 5
    [-1, 1],   # 6
    [-1, -1],  # 7
    [1, -1]    # 8
], dtype=np.int32)

LATTICE_WEIGHTS = np.array([
    4.0 / 9.0,   # 0
    1.0 / 9.0,   # 1
    1.0 / 9.0,   # 2
    1.0 / 9.0,   # 3
    1.0 / 9.0,   # 4
    1.0 / 36.0,  # 5
    1.0 / 36.0,  # 6
    1.0 / 36.0,  # 7
    1.0 / 36.0   # 8
], dtype=np.float64)

# Inverse direction mapping for bounce-back: c[OPPOSITE[i]] = -c[i]
OPPOSITE = np.array([0, 3, 4, 1, 2, 7, 8, 5, 6], dtype=np.int32)
CS_SQ = 1.0 / 3.0  # Speed of sound squared in lattice units


@dataclass
class LBMConfig:
    """Configuration parameters for the D2Q9 Lattice Boltzmann simulation."""
    nx: int = 400            # Lattice nodes in x (streamwise)
    ny: int = 160            # Lattice nodes in y (crossflow)
    reynolds: float = 150.0  # Reynolds number Re = (u_inf * diameter) / nu
    u_inf: float = 0.08      # Free-stream velocity (lattice units, keep Ma = u_inf/cs < 0.15)
    obstacle_radius: float = 14.0  # Characteristic obstacle radius (D = 28)
    obstacle_x: Optional[float] = None
    obstacle_y: Optional[float] = None

    @property
    def diameter(self) -> float:
        return 2.0 * self.obstacle_radius

    @property
    def mach_number(self) -> float:
        return self.u_inf / np.sqrt(CS_SQ)

    @property
    def kinematic_viscosity(self) -> float:
        """nu = (u_inf * D) / Re"""
        return (self.u_inf * self.diameter) / self.reynolds

    @property
    def tau(self) -> float:
        """BGK relaxation time tau = 3 * nu + 0.5"""
        return 3.0 * self.kinematic_viscosity + 0.5

    @property
    def omega(self) -> float:
        """Relaxation frequency omega = 1 / tau"""
        return 1.0 / self.tau

    def validate(self) -> None:
        """Enforces numerical stability and incompressibility criteria."""
        if self.tau <= 0.505:
            raise ValueError(
                f"Relaxation time tau={self.tau:.4f} is too close to 0.5 (numerical instability). "
                f"Increase resolution (nx, ny, diameter) or decrease Reynolds number."
            )
        if self.mach_number >= 0.3:
            raise ValueError(
                f"Mach number Ma={self.mach_number:.3f} >= 0.3 violates incompressibility limit. "
                f"Lower u_inf to prevent compressibility errors."
            )


class LBMD2Q9Solver:
    """
    Precision Vectorized D2Q9 BGK Solver with Hydrodynamic Force Telemetry.
    """

    def __init__(self, config: LBMConfig):
        self.config = config
        self.config.validate()

        self.nx = config.nx
        self.ny = config.ny
        self.u_inf = config.u_inf
        self.tau = config.tau
        self.omega = config.omega
        self.nu = config.kinematic_viscosity

        # Center obstacle position if not specified
        obs_x = config.obstacle_x if config.obstacle_x is not None else self.nx / 4.0
        obs_y = config.obstacle_y if config.obstacle_y is not None else self.ny / 2.0
        self.obstacle_center = (obs_x, obs_y)

        # Discrete populations: shape (9, nx, ny)
        self.f = np.zeros((9, self.nx, self.ny), dtype=np.float64)
        self.f_post = np.zeros((9, self.nx, self.ny), dtype=np.float64)

        # Macroscopic quantities: rho (nx, ny), u (2, nx, ny)
        self.rho = np.ones((self.nx, self.ny), dtype=np.float64)
        self.u = np.zeros((2, self.nx, self.ny), dtype=np.float64)

        # Obstacle geometry mask (True = Solid, False = Fluid)
        self.solid_mask = np.zeros((self.nx, self.ny), dtype=bool)
        self._build_circular_obstacle()

        # Telemetry history buffers
        self.drag_force: float = 0.0
        self.lift_force: float = 0.0
        self.cd: float = 0.0
        self.cl: float = 0.0
        self.time_step: int = 0

        # Initialize to uniform flow equilibrium with small perturbation to trigger Karman instability
        self.reset()

    def _build_circular_obstacle(self) -> None:
        """Constructs cylinder solid boundary mask."""
        x = np.arange(self.nx)[:, None]
        y = np.arange(self.ny)[None, :]
        cx, cy = self.obstacle_center
        r_sq = (x - cx) ** 2 + (y - cy) ** 2
        self.solid_mask = r_sq <= (self.config.obstacle_radius ** 2)

    def set_custom_mask(self, mask: np.ndarray) -> None:
        """Assigns an arbitrary solid mask (e.g. NACA airfoil or bluff square)."""
        assert mask.shape == (self.nx, self.ny), "Mask dimensions must match (nx, ny)"
        self.solid_mask = mask.astype(bool)

    def compute_equilibrium(self, rho: np.ndarray, u: np.ndarray) -> np.ndarray:
        """
        Calculates exact D2Q9 Maxwell-Boltzmann equilibrium distribution:
          f_i^eq = w_i * rho * [ 1 + 3(c_i . u) + 4.5(c_i . u)^2 - 1.5|u|^2 ]
        """
        u_sq = u[0]**2 + u[1]**2
        feq = np.empty((9, self.nx, self.ny), dtype=np.float64)

        for i in range(9):
            cx, cy = LATTICE_C[i]
            ci_dot_u = cx * u[0] + cy * u[1]
            feq[i] = LATTICE_WEIGHTS[i] * rho * (
                1.0 + 3.0 * ci_dot_u + 4.5 * (ci_dot_u ** 2) - 1.5 * u_sq
            )
        return feq

    def reset(self) -> None:
        """Initializes macroscopic fields and populations with initial vortex perturbation."""
        self.rho.fill(1.0)
        self.u[0].fill(self.u_inf)
        self.u[1].fill(0.0)

        # Introduce a micro-asymmetry in transverse velocity to break numerical symmetry
        cx, cy = self.obstacle_center
        x = np.arange(self.nx)[:, None]
        y = np.arange(self.ny)[None, :]
        dist_sq = (x - cx)**2 + (y - cy)**2
        perturbation = 0.005 * self.u_inf * np.sin(2.0 * np.pi * (y - cy) / self.config.diameter) * np.exp(-dist_sq / (2.0 * (self.config.obstacle_radius * 2.0)**2))
        self.u[1] += perturbation

        # Zero velocity inside solid
        self.u[:, self.solid_mask] = 0.0

        # Equilibrium populations
        self.f = self.compute_equilibrium(self.rho, self.u)
        self.f_post = self.f.copy()
        self.time_step = 0
        self.drag_force = 0.0
        self.lift_force = 0.0
        self.cd = 0.0
        self.cl = 0.0

    def step(self) -> None:
        """
        Executes one full LBM time cycle:
          1. Macroscopic moments calculation: rho = sum(f_i), rho*u = sum(f_i * c_i)
          2. BGK Collision: f_i^* = f_i - omega * (f_i - f_i^eq)
          3. Momentum Exchange Method (MEM) force integration on solid boundary
          4. Solid bounce-back & Boundary Conditions (Inlet/Outlet/Walls)
          5. Streaming: f_i(x + c_i, y + c_i) = f_i^*(x, y)
        """
        # 1. Macroscopic Density & Velocity Moments
        self.rho = np.sum(self.f, axis=0)
        # Compute momentum: rho * u = sum(f_i * c_i)
        self.u[0] = (
            self.f[1] - self.f[3] + self.f[5] - self.f[6] - self.f[7] + self.f[8]
        ) / self.rho
        self.u[1] = (
            self.f[2] - self.f[4] + self.f[5] + self.f[6] - self.f[7] - self.f[8]
        ) / self.rho

        # Fix solid velocity to zero
        self.u[:, self.solid_mask] = 0.0
        self.rho[self.solid_mask] = 1.0

        # 2. Collision Step (BGK)
        feq = self.compute_equilibrium(self.rho, self.u)
        self.f_post = self.f - self.omega * (self.f - feq)

        # 3. Momentum Exchange Force Computation on Immersed Solid
        self._compute_aerodynamic_forces()

        # 4. Standard Half-way Bounce-Back on Solid Nodes
        for i in range(9):
            opp = OPPOSITE[i]
            self.f_post[opp, self.solid_mask] = self.f[i, self.solid_mask]

        # 5. Streaming Step with Vectorized Roll
        for i in range(9):
            cx, cy = LATTICE_C[i]
            self.f[i] = np.roll(np.roll(self.f_post[i], cx, axis=0), cy, axis=1)

        # 6. Boundary Conditions
        self._apply_boundary_conditions()

        self.time_step += 1

    def _apply_boundary_conditions(self) -> None:
        """
        Boundary Conditions:
          - West (x=0): Dirichlet Uniform Velocity Inlet (Zou-He / Equilibrium)
          - East (x=nx-1): Convective Open Outlet (Zero-gradient extrapolation)
          - North & South (y=0, y=ny-1): Free-slip specular reflection or Periodic
        """
        # Inlet (x = 0): Re-inject uniform velocity equilibrium
        rho_inlet = 1.0 / (1.0 - self.u_inf) * (
            self.f[0, 0, :] + self.f[2, 0, :] + self.f[4, 0, :] +
            2.0 * (self.f[3, 0, :] + self.f[6, 0, :] + self.f[7, 0, :])
        )
        u_inlet = np.zeros((2, self.ny), dtype=np.float64)
        u_inlet[0] = self.u_inf
        u_inlet[1] = 0.0

        feq_inlet = self.compute_equilibrium(rho_inlet[None, :], u_inlet[:, None, :])
        self.f[:, 0, :] = feq_inlet[:, 0, :]

        # Outlet (x = nx - 1): Open boundary condition (Neumann zero-gradient)
        self.f[:, -1, :] = self.f[:, -2, :]

        # Top & Bottom Free-slip (specular bounce):
        # Bottom wall (y = 0): bounce c_2 -> c_4, c_5 -> c_8, c_6 -> c_7
        self.f[2, :, 0] = self.f[4, :, 0]
        self.f[5, :, 0] = self.f[8, :, 0]
        self.f[6, :, 0] = self.f[7, :, 0]

        # Top wall (y = ny - 1): bounce c_4 -> c_2, c_8 -> c_5, c_7 -> c_6
        self.f[4, :, -1] = self.f[2, :, -1]
        self.f[8, :, -1] = self.f[5, :, -1]
        self.f[7, :, -1] = self.f[6, :, -1]

    def _compute_aerodynamic_forces(self) -> None:
        """
        Momentum Exchange Method (MEM):
          Integrates discrete momentum transferred to the solid obstacle across all boundary links:
          F_MEM = sum_{nodes} 2 * c_i * f_i^*(x_fluid)
        """
        # Detect fluid-solid interface links
        fx_sum = 0.0
        fy_sum = 0.0

        for i in range(1, 9):
            cx, cy = LATTICE_C[i]
            # Neighbor node coordinates
            fluid_mask = ~self.solid_mask
            # Shifted solid mask to check which fluid nodes stream into solid
            solid_neighbor = np.roll(np.roll(self.solid_mask, -cx, axis=0), -cy, axis=1)
            # Interface links: fluid node that points into a solid node
            interface_nodes = fluid_mask & solid_neighbor

            if np.any(interface_nodes):
                transferred_f = self.f_post[i, interface_nodes]
                fx_sum += np.sum(2.0 * cx * transferred_f)
                fy_sum += np.sum(2.0 * cy * transferred_f)

        self.drag_force = fx_sum
        self.lift_force = fy_sum

        # Dimensionless dynamic force coefficients: C = F / (0.5 * rho * U^2 * D)
        q_inf = 0.5 * 1.0 * (self.u_inf ** 2) * self.config.diameter
        if q_inf > 1e-12:
            self.cd = self.drag_force / q_inf
            self.cl = self.lift_force / q_inf

    @property
    def vorticity(self) -> np.ndarray:
        """
        Computes the out-of-plane vorticity field:
          omega_z = (dv/dx) - (du/dy)
        via 2nd-order central finite differences.
        """
        # dv/dx
        dv_dx = np.gradient(self.u[1], axis=0)
        # du/dy
        du_dy = np.gradient(self.u[0], axis=1)
        wz = dv_dx - du_dy
        wz[self.solid_mask] = 0.0
        return wz

    @property
    def velocity_magnitude(self) -> np.ndarray:
        """Computes speed |u| = sqrt(ux^2 + uy^2)."""
        speed = np.sqrt(self.u[0]**2 + self.u[1]**2)
        speed[self.solid_mask] = 0.0
        return speed
