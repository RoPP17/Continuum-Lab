"""
Continuum Lab - Magnus Effect & Flettner Rotor Simulation Engine
Module: 01 Mecanica de Fluidos / 05 Efecto Magnus y Rotor Flettner
File: src/physics/magnus_sim.py

Implements mathematically rigorous potential flow with circulation around a spinning cylinder,
analytical Kutta-Joukowski lift, stagnation point bifurcation (surface -> detached saddle),
Bernoulli pressure field C_p, and Runge-Kutta 4th order particle advection.
"""

from dataclasses import dataclass
from typing import Tuple, List, Optional
import numpy as np


@dataclass
class MagnusConfig:
    """Configuration parameters for the Magnus & Flettner simulation."""
    radius: float = 1.0                # Cylinder radius R [m]
    u_inf: float = 10.0                # Free stream velocity U_inf [m/s]
    rho_air: float = 1.225             # Air density [kg/m^3]
    nu_air: float = 1.5e-5             # Kinematic viscosity [m^2/s]
    cylinder_length: float = 10.0      # Cylinder span L [m]
    n_particles: int = 2400            # Particle tracers count
    domain_x: Tuple[float, float] = (-4.0, 4.0)
    domain_y: Tuple[float, float] = (-3.5, 3.5)


@dataclass
class MagnusTelemetry:
    """Real-time physical telemetry for HUD rendering."""
    t_video: float
    spin_ratio_alpha: float            # alpha = omega * R / U_inf
    omega_rpm: float                   # Cylinder rotational speed [RPM]
    circulation_gamma: float           # Circulation Gamma [m^2/s]
    lift_ideal_kn_m: float             # Kutta-Joukowski ideal lift [kN/m]
    lift_real_kn_m: float              # Viscous experimental lift [kN/m]
    c_l_ideal: float                   # Ideal lift coefficient C_L
    c_l_real: float                    # Real lift coefficient C_L
    c_d_real: float                    # Real drag coefficient C_D
    efficiency_l_d: float              # Aerodynamic efficiency L/D
    stagnation_state: str              # "SURFACE_DUAL", "CRITICAL_MERGE", "DETACHED_SADDLE"
    stag_points: List[Tuple[float, float]] # List of (x, y) coordinates of stagnation points
    max_suction_cp: float              # Minimum (most negative) Cp on top
    max_pressure_cp: float             # Maximum Cp on bottom
    thrust_power_kw: float             # Propulsive thrust power for Flettner ship [kW]


class MagnusSimulation:
    """
    Simulation of potential flow with circulation + 4th-order particle advection.
    """

    def __init__(self, config: Optional[MagnusConfig] = None):
        self.cfg = config or MagnusConfig()
        self.t = 0.0

        # Pre-seed particle swarm
        self.rng = np.random.default_rng(2026)
        self.particles_x = self.rng.uniform(self.cfg.domain_x[0], self.cfg.domain_x[1], self.cfg.n_particles)
        self.particles_y = self.rng.uniform(self.cfg.domain_y[0], self.cfg.domain_y[1], self.cfg.n_particles)
        
        # Ensure initial particles are outside cylinder
        mask_inside = (self.particles_x**2 + self.particles_y**2) <= (self.cfg.radius * 1.05)**2
        while np.any(mask_inside):
            self.particles_x[mask_inside] = self.rng.uniform(self.cfg.domain_x[0], self.cfg.domain_x[1], np.sum(mask_inside))
            self.particles_y[mask_inside] = self.rng.uniform(self.cfg.domain_y[0], self.cfg.domain_y[1], np.sum(mask_inside))
            mask_inside = (self.particles_x**2 + self.particles_y**2) <= (self.cfg.radius * 1.05)**2

        self.particles_age = self.rng.uniform(0.0, 1.0, self.cfg.n_particles)

    def get_alpha_at_time(self, t: float) -> float:
        """
        Calculates time-dependent spin ratio alpha(t) for narrative video progression.
        - t in [0.0, 3.0): alpha = 0.0 (Pure unspun potential flow)
        - t in [3.0, 8.0): alpha ramps from 0.0 to 1.6 (Spin initiation, lift grows)
        - t in [8.0, 12.0): alpha ramps from 1.6 to 2.4 (Crossing critical bifurcation alpha=2)
        - t in [12.0, 18.0]: alpha ramps from 2.4 to 3.6 (Supercritical detached vortex & Flettner power)
        """
        if t <= 3.0:
            return 0.0
        elif t <= 8.0:
            tau = (t - 3.0) / 5.0
            s = 3.0 * tau**2 - 2.0 * tau**3  # Smoothstep
            return 0.0 + 1.6 * s
        elif t <= 12.0:
            tau = (t - 8.0) / 4.0
            s = 3.0 * tau**2 - 2.0 * tau**3
            return 1.6 + (2.4 - 1.6) * s
        else:
            tau = min(1.0, (t - 12.0) / 6.0)
            s = 3.0 * tau**2 - 2.0 * tau**3
            return 2.4 + (3.6 - 2.4) * s

    def velocity_field(self, x: np.ndarray, y: np.ndarray, alpha: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculates 2D velocity vector field (u_x, u_y) in Cartesian coordinates.
        Uses complex potential w(z) = U_inf*(z + R^2/z) - i*Gamma/(2*pi)*ln(z/R).
        """
        r2 = x**2 + y**2
        r = np.sqrt(np.maximum(r2, 1e-12))
        theta = np.arctan2(y, x)

        R = self.cfg.radius
        U = self.cfg.u_inf
        # Circulation Gamma = 2*pi*R*U*alpha (clockwise, so flow accelerates on top)
        gamma = 2.0 * np.pi * R * U * alpha

        # External flow (r >= R)
        # u_r = U * (1 - R^2/r^2) * cos(theta)
        # u_theta = -U * (1 + R^2/r^2) * sin(theta) - gamma / (2*pi*r)
        inv_r2 = R**2 / np.maximum(r2, 1e-12)
        u_r = U * (1.0 - inv_r2) * np.cos(theta)
        u_theta = -U * (1.0 + inv_r2) * np.sin(theta) - (gamma / (2.0 * np.pi * r))

        # Convert polar to Cartesian
        cos_t = np.cos(theta)
        sin_t = np.sin(theta)
        ux = u_r * cos_t - u_theta * sin_t
        uy = u_r * sin_t + u_theta * cos_t

        # Inside cylinder (rigid body rotation with boundary match)
        mask_inside = r < R
        if np.any(mask_inside):
            # omega = alpha * U / R
            omega = alpha * U / R
            # Clockwise rotation: u_x = omega * y, u_y = -omega * x
            ux = np.where(mask_inside, omega * y, ux)
            uy = np.where(mask_inside, -omega * x, uy)

        return ux, uy

    def surface_pressure_cp(self, theta: np.ndarray, alpha: float) -> np.ndarray:
        """
        Surface pressure coefficient C_p(theta) on the cylinder wall (r = R).
        C_p = 1 - (u_theta / U_inf)^2 = 1 - (-2*sin(theta) - alpha)^2
        """
        u_surf = -2.0 * np.sin(theta) - alpha
        return 1.0 - u_surf**2

    def compute_stagnation_points(self, alpha: float) -> Tuple[str, List[Tuple[float, float]]]:
        """
        Calculates exact analytical coordinates of stagnation points.
        - If alpha < 2.0: Two surface stagnation points at sin(theta_s) = -alpha/2
        - If alpha == 2.0: Merged critical stagnation point at theta = -pi/2
        - If alpha > 2.0: Detached saddle stagnation point at theta = -pi/2, r_s = R*(alpha + sqrt(alpha^2 - 4))/2
        """
        R = self.cfg.radius
        if alpha < 1.99:
            val = np.clip(alpha / 2.0, 0.0, 0.999999)
            phi = np.arcsin(val)
            # Two solutions in bottom half: theta_1 = -phi, theta_2 = -pi + phi
            th1 = -phi
            th2 = -np.pi + phi
            p1 = (R * np.cos(th1), R * np.sin(th1))
            p2 = (R * np.cos(th2), R * np.sin(th2))
            return "SURFACE_DUAL", [p1, p2]
        elif alpha <= 2.05:
            # Merging / critical at bottom pole
            th_crit = -np.pi / 2.0
            p_crit = (0.0, -R)
            return "CRITICAL_MERGE", [p_crit]
        else:
            # Detached saddle point
            r_s = R * (alpha + np.sqrt(alpha**2 - 4.0)) / 2.0
            p_saddle = (0.0, -r_s)
            return "DETACHED_SADDLE", [p_saddle]

    def step_particles(self, dt: float, alpha: float):
        """
        Advects tracer particles using 4th-order Runge-Kutta (RK4) integration.
        """
        # RK4 step
        x = self.particles_x
        y = self.particles_y

        k1_x, k1_y = self.velocity_field(x, y, alpha)
        k2_x, k2_y = self.velocity_field(x + 0.5 * dt * k1_x, y + 0.5 * dt * k1_y, alpha)
        k3_x, k3_y = self.velocity_field(x + 0.5 * dt * k2_x, y + 0.5 * dt * k2_y, alpha)
        k4_x, k4_y = self.velocity_field(x + dt * k3_x, y + dt * k3_y, alpha)

        self.particles_x += (dt / 6.0) * (k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x)
        self.particles_y += (dt / 6.0) * (k1_y + 2.0 * k2_y + 2.0 * k3_y + k4_y)
        self.particles_age += dt

        # Recycle particles that exit domain or penetrate inside cylinder
        xmin, xmax = self.cfg.domain_x
        ymin, ymax = self.cfg.domain_y
        R = self.cfg.radius

        mask_out = (
            (self.particles_x > xmax) |
            (self.particles_x < xmin) |
            (self.particles_y > ymax) |
            (self.particles_y < ymin) |
            (self.particles_x**2 + self.particles_y**2 < (R * 1.02)**2)
        )

        n_reseed = int(np.sum(mask_out))
        if n_reseed > 0:
            self.particles_x[mask_out] = self.rng.uniform(xmin, xmin + 0.5, n_reseed)
            self.particles_y[mask_out] = self.rng.uniform(ymin * 0.9, ymax * 0.9, n_reseed)
            self.particles_age[mask_out] = 0.0

    def get_telemetry(self, t: float) -> MagnusTelemetry:
        """Computes all HUD telemetry and physical metrics at time t."""
        alpha = self.get_alpha_at_time(t)
        R = self.cfg.radius
        U = self.cfg.u_inf
        rho = self.cfg.rho_air
        L = self.cfg.cylinder_length

        omega = alpha * U / R  # rad/s
        omega_rpm = omega * (60.0 / (2.0 * np.pi))
        gamma = 2.0 * np.pi * R * U * alpha

        # Kutta-Joukowski Lift per unit span: L' = rho * U * Gamma
        lift_ideal_nm = rho * U * gamma
        lift_ideal_kn_m = lift_ideal_nm / 1000.0
        c_l_ideal = 2.0 * np.pi * alpha

        # Real viscous lift and drag (Prandtl-Thom experimental curve for Flettner rotors)
        c_l_real = float((2.0 * np.pi * alpha) / (1.0 + 0.16 * (alpha**1.32)))
        c_d_real = float(0.48 + 0.32 * (alpha**1.22))
        efficiency_l_d = float(c_l_real / max(0.01, c_d_real))
        lift_real_kn_m = 0.5 * rho * (U**2) * (2.0 * R) * c_l_real / 1000.0

        # Flettner cargo ship thrust power: 4 rotors of 30m x 5m at 12 m/s
        # P = Thrust * V_ship (e.g. ship cruising at 15 knots ~ 7.7 m/s)
        total_lift_flettner_n = 4.0 * (0.5 * rho * (U**2) * (5.0 * 30.0) * c_l_real)
        thrust_power_kw = (total_lift_flettner_n * 7.7) / 1000.0

        # Stagnation state and coordinates
        stag_state, stag_pts = self.compute_stagnation_points(alpha)

        # Extreme surface pressures
        theta_grid = np.linspace(0, 2.0 * np.pi, 360)
        cp_grid = self.surface_pressure_cp(theta_grid, alpha)
        max_suction = float(np.min(cp_grid))  # Minimum Cp is highest suction
        max_pressure = float(np.max(cp_grid))

        return MagnusTelemetry(
            t_video=t,
            spin_ratio_alpha=float(alpha),
            omega_rpm=float(omega_rpm),
            circulation_gamma=float(gamma),
            lift_ideal_kn_m=float(lift_ideal_kn_m),
            lift_real_kn_m=float(lift_real_kn_m),
            c_l_ideal=float(c_l_ideal),
            c_l_real=float(c_l_real),
            c_d_real=float(c_d_real),
            efficiency_l_d=float(efficiency_l_d),
            stagnation_state=stag_state,
            stag_points=stag_pts,
            max_suction_cp=max_suction,
            max_pressure_cp=max_pressure,
            thrust_power_kw=float(thrust_power_kw),
        )

    def advance_to_time(self, target_t: float) -> MagnusTelemetry:
        """Advances physics simulation to target timestamp using substepping."""
        dt_target = target_t - self.t
        if dt_target > 0:
            n_substeps = max(1, int(np.ceil(dt_target / 0.005)))
            sub_dt = dt_target / n_substeps
            for _ in range(n_substeps):
                curr_alpha = self.get_alpha_at_time(self.t)
                self.step_particles(sub_dt, curr_alpha)
                self.t += sub_dt
        self.t = target_t
        return self.get_telemetry(self.t)
