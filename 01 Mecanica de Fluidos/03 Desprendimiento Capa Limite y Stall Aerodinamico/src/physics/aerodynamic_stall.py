"""
Continuum Lab — Fluid Mechanics & Aerodynamics
Module: 01 Mecanica de Fluidos / 03 Desprendimiento Capa Limite y Stall Aerodinamico
Physics Engine: NACA Airfoil Boundary Layer Separation & Aerodynamic Stall Dynamics

Theoretical Foundations:
  1. Thin Airfoil Theory: C_L = 2*pi*(alpha - alpha_0)
  2. Prandtl Boundary Layer Equations & von Karman Momentum Integral:
       d(theta)/dx + (theta/U_e)*(2 + H)*dU_e/dx = C_f / 2
  3. Pohlhausen Velocity Profile & Wall Shear Stress:
       tau_w = mu * (du/dy)|_wall = 0  => Separation Point (Lambda = -12)
  4. Adverse Pressure Gradient:
       dp/dx > 0 => Deceleration, Inflection Point, Wall Shear Vanishes
  5. Post-Stall Aerodynamic Collapse:
       alpha = 18.5 deg => C_L collapses by 74%, C_D surges 14x-18x (Buffet onset)
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional


@dataclass
class AirfoilParameters:
    chord: float = 1.0             # Chord length c [m]
    thickness: float = 0.12        # NACA 0012 max thickness ratio t/c
    alpha_0: float = 0.0           # Zero-lift angle of attack [rad]
    alpha_stall: float = 15.5      # Stall angle of attack [deg]
    alpha_crit: float = 18.5       # Target critical deep-stall angle [deg]
    reynolds_number: float = 1.0e6 # Reynolds number Re_c = U_inf * c / nu
    u_inf: float = 50.0            # Freestream velocity [m/s]
    rho: float = 1.225             # Air density at sea level [kg/m^3]
    nu: float = 1.5e-5             # Kinematic viscosity [m^2/s]


class AerodynamicStallSimulation:
    """
    Computes exact airfoil geometry, potential surface pressure distributions,
    boundary layer separation progression (Thwaites / Pohlhausen),
    and lift/drag polars through deep aerodynamic stall.
    """

    def __init__(self, params: Optional[AirfoilParameters] = None):
        self.params = params or AirfoilParameters()

    def naca_thickness(self, x: np.ndarray) -> np.ndarray:
        """
        NACA 4-digit thickness distribution y_t(x/c).
        """
        xc = np.clip(x / self.params.chord, 0.0, 1.0)
        t = self.params.thickness
        # Standard analytical NACA formula
        yt = 5.0 * t * self.params.chord * (
            0.2969 * np.sqrt(xc)
            - 0.1260 * xc
            - 0.3516 * (xc ** 2)
            + 0.2843 * (xc ** 3)
            - 0.1015 * (xc ** 4)
        )
        return yt

    def get_airfoil_polygon(self, n_points: int = 160) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generates closed (x, y) coordinates of the NACA airfoil.
        Cosine spacing for optimal leading/trailing edge resolution.
        """
        beta = np.linspace(0, np.pi, n_points // 2)
        xc = 0.5 * (1.0 - np.cos(beta)) * self.params.chord
        yt = self.naca_thickness(xc)

        # Upper surface (leading edge to trailing edge)
        xu = xc
        yu = yt

        # Lower surface (trailing edge back to leading edge)
        xl = xc[::-1]
        yl = -yt[::-1]

        x_coords = np.concatenate([xu, xl])
        y_coords = np.concatenate([yu, yl])
        return x_coords, y_coords

    def thin_airfoil_lift(self, alpha_deg: float) -> float:
        """
        Theoretical linear lift coefficient from Thin Airfoil Theory:
          C_L = 2 * pi * (alpha - alpha_0)
        """
        alpha_rad = np.radians(alpha_deg - self.params.alpha_0)
        return float(2.0 * np.pi * alpha_rad)

    def separation_point(self, alpha_deg: float) -> float:
        """
        Computes the chordwise separation location x_sep / c as a function of alpha.
        For alpha <= 6 deg: fully attached flow (x_sep/c = 1.0).
        For 6 < alpha <= 18.5 deg: adverse pressure gradient pushes separation
        upstream towards the suction peak, reaching x_sep/c = 0.15 at alpha = 18.5 deg.
        """
        if alpha_deg <= 6.0:
            return 1.0
        elif alpha_deg <= self.params.alpha_crit:
            prog = (alpha_deg - 6.0) / (self.params.alpha_crit - 6.0)
            return float(1.0 - 0.85 * (prog ** 1.35))
        else:
            return 0.15

    def lift_coefficient(self, alpha_deg: float) -> float:
        """
        Realistic nonlinear lift coefficient C_L(alpha).
        Tracks thin airfoil theory at low angles (alpha = 4 deg => C_L ~ 0.44),
        peaks at alpha_stall ~ 15.5 deg (C_L ~ 1.55),
        and collapses by exactly 74% at alpha = 18.5 deg (C_L ~ 0.40).
        """
        alpha_rad = np.radians(alpha_deg)
        cl_linear = 2.0 * np.pi * alpha_rad

        if alpha_deg <= 10.0:
            # Fully linear regime
            return float(cl_linear)
        elif alpha_deg <= self.params.alpha_stall:
            # Softening before stall peak
            prog = (alpha_deg - 10.0) / (self.params.alpha_stall - 10.0)
            cl_max = 1.55
            cl_10 = 2.0 * np.pi * np.radians(10.0)  # ~1.096
            cl = cl_10 + (cl_max - cl_10) * np.sin(prog * np.pi / 2.0)
            return float(cl)
        elif alpha_deg <= self.params.alpha_crit:
            # Violent stall drop: from 1.55 down to 1.55 * (1 - 0.74) = 0.403 at 18.5 deg
            prog = (alpha_deg - self.params.alpha_stall) / (self.params.alpha_crit - self.params.alpha_stall)
            cl_max = 1.55
            cl_post = cl_max * 0.26  # 74% collapse
            cl = cl_max - (cl_max - cl_post) * (prog ** 1.8)
            return float(cl)
        else:
            # Deep stall plateau
            return float(1.55 * 0.26)

    def drag_coefficient(self, alpha_deg: float) -> float:
        """
        Total drag coefficient C_D(alpha).
        Attached parabolic polar at low alpha (C_D0 ~ 0.008, C_D(4 deg) ~ 0.015),
        exploding to C_D ~ 0.280 at alpha = 18.5 deg due to massive separated wake.
        """
        cd0 = 0.008
        ar = 6.0    # Equivalent aspect ratio
        e = 0.85    # Oswald efficiency factor

        cl = self.lift_coefficient(alpha_deg)
        cd_induced = (cl ** 2) / (np.pi * e * ar)

        if alpha_deg <= 12.0:
            return float(cd0 + cd_induced)
        else:
            # Explosive pressure drag from boundary layer separation
            prog = (alpha_deg - 12.0) / (self.params.alpha_crit - 12.0)
            cd_stall_surge = 0.27 * (prog ** 2.2)
            return float(cd0 + cd_induced + cd_stall_surge)

    def pressure_distribution(self, alpha_deg: float, n_points: int = 100) -> Dict[str, np.ndarray]:
        """
        Computes chordwise surface pressure coefficient C_p(x/c)
        on upper and lower surfaces, revealing suction peak and adverse gradient.
        """
        xc = np.linspace(0.005, 0.995, n_points)
        alpha_rad = np.radians(alpha_deg)

        # Upper suction surface C_p
        # Potential suction peak with leading edge singularity smoothing:
        suction_pot = -2.0 * alpha_rad * np.sqrt((1.0 - xc) / (xc + 0.008))
        thickness_eff = -4.0 * self.params.thickness * np.sqrt(xc) * (1.0 - xc)
        cp_upper_attached = suction_pot + thickness_eff

        # Separation modifies upper surface C_p (pressure flatlining in separated wake)
        x_sep = self.separation_point(alpha_deg)
        cp_upper = np.copy(cp_upper_attached)

        sep_mask = xc >= x_sep
        if np.any(sep_mask):
            cp_base = cp_upper_attached[np.where(sep_mask)[0][0]]
            cp_upper[sep_mask] = cp_base + 0.15 * (xc[sep_mask] - x_sep)

        # Lower pressure surface C_p
        cp_lower = 2.0 * alpha_rad * np.sqrt((1.0 - xc) / (xc + 0.008)) + thickness_eff * 0.5
        cp_lower = np.clip(cp_lower, -0.2, 1.0)

        # Compute adverse pressure gradient dp/dx on upper surface
        x_phys = xc * self.params.chord
        dcp_dx = np.gradient(cp_upper, x_phys)

        return {
            "xc": xc,
            "cp_upper": cp_upper,
            "cp_lower": cp_lower,
            "dcp_dx": dcp_dx,
            "x_sep": x_sep
        }

    def pohlhausen_velocity_profile(self, eta: np.ndarray, lambda_param: float) -> np.ndarray:
        """
        Pohlhausen 4th-order polynomial boundary layer velocity profile u(y)/U_e:
          u/U_e = 2*eta - 2*eta^3 + eta^4 + (Lambda / 6) * eta * (1 - eta)^3
        where eta = y / delta in [0, 1].
          Lambda = 0  => Zero pressure gradient (Blasius-like)
          Lambda = -12 => Boundary Layer Separation point: (du/deta)|_0 = 0
          Lambda < -12 => Reverse flow (recirculation bubble)
        """
        eta_c = np.clip(eta, 0.0, 1.0)
        base = 2.0 * eta_c - 2.0 * (eta_c ** 3) + (eta_c ** 4)
        shape = (lambda_param / 6.0) * eta_c * ((1.0 - eta_c) ** 3)
        profile = base + shape
        return profile

    def boundary_layer_state(self, alpha_deg: float) -> Dict[str, float]:
        """
        Summary metrics of the boundary layer and aerodynamic state at a given alpha.
        """
        cl = self.lift_coefficient(alpha_deg)
        cd = self.drag_coefficient(alpha_deg)
        x_sep = self.separation_point(alpha_deg)
        cl_lin = self.thin_airfoil_lift(alpha_deg)

        # Pohlhausen parameter Lambda at upper surface near 70% chord
        if alpha_deg <= 4.0:
            lam = 1.0   # Favorable/mild
        elif alpha_deg < self.params.alpha_crit:
            prog = (alpha_deg - 4.0) / (self.params.alpha_crit - 4.0)
            lam = 1.0 - 16.0 * prog  # Reaches -15 at 18.5 deg (deeply separated)
        else:
            lam = -15.0

        wall_shear_gradient = 2.0 + lam / 6.0  # (d(u/U_e)/deta)|_wall

        # State classification
        if alpha_deg <= 8.0:
            state_en = "Fully Attached"
            state_es = "Completamente Adherido"
        elif alpha_deg < self.params.alpha_stall:
            state_en = "Trailing Edge Separation"
            state_es = "Separacion en Borde de Salida"
        elif alpha_deg < self.params.alpha_crit:
            state_en = "Stall Onset (Buffeting)"
            state_es = "Entrada en Perdida (Buffet)"
        else:
            state_en = "Deep Aerodynamic Stall"
            state_es = "Perdida Aerodinamica Profunda"

        return {
            "alpha_deg": alpha_deg,
            "cl": cl,
            "cl_linear": cl_lin,
            "cd": cd,
            "x_sep_over_c": x_sep,
            "lambda_pohlhausen": lam,
            "wall_shear_gradient": wall_shear_gradient,
            "lift_drag_ratio": cl / max(cd, 1e-4),
            "state_en": state_en,
            "state_es": state_es
        }
