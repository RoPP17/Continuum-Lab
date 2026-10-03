"""
Continuum Lab — Mathematical Physics & Calculus of Variations
Division: 06 Matematicas y Geometria / 03 Curva Braquistocrona
Module: Physics Models & Kinematic Solver for 4 Frictionless Gravity Tracks

Theoretical Foundation:
Euler-Lagrange Equation applied to the Brachistochrone problem (Johann Bernoulli, 1696):
    minimize T[y] = integral_{x_A}^{x_B} sqrt(1 + y'^2) / sqrt(2*g*(y_0 - y)) dx

Beltrami Identity (since integrand f(y, y') has no explicit x-dependence):
    f - y' * (df / dy') = C = const  =>  (y_0 - y) * (1 + y'^2) = 2*r
Leading to the exact inverted cycloid:
    x(theta) = r * (theta - sin(theta))
    y(theta) = y_0 - r * (1 - cos(theta))
"""

from dataclasses import dataclass
from typing import Tuple, List, Dict
import numpy as np
from scipy.optimize import root_scalar
from scipy.integrate import quad
from scipy.interpolate import PchipInterpolator


@dataclass
class TrackState:
    """Instantaneous state of a moving particle along a track."""
    x: float
    y: float
    vx: float
    vy: float
    speed: float
    arc_length: float
    t_elapsed: float
    finished: bool


class BaseTrack:
    """Base class for a parameterized gravity track between A(0, 4) and B(7, -3)."""

    def __init__(self, name: str, key: str, color: str, g: float = 9.81):
        self.name = name
        self.key = key
        self.color = color
        self.g = g
        self.x_A, self.y_A = 0.0, 4.0
        self.x_B, self.y_B = 7.0, -3.0
        self.physical_travel_time: float = 0.0
        self.target_travel_time: float = 0.0
        self.total_arc_length: float = 0.0

    def get_point_by_param(self, u: float) -> Tuple[float, float]:
        """u in [0, 1] parameterizing the geometry."""
        raise NotImplementedError

    def get_trajectory_points(self, num_points: int = 400) -> np.ndarray:
        """Returns array of shape (N, 2) with (x, y) coordinates."""
        u_vals = np.linspace(0.0, 1.0, num_points)
        pts = [self.get_point_by_param(u) for u in u_vals]
        return np.array(pts)

    def get_state(self, t: float, use_target_time: bool = True) -> TrackState:
        """Returns the kinematic state at time t."""
        raise NotImplementedError


class StraightTrack(BaseTrack):
    """
    Track 1: Euclidean Straight Line A -> B
    y(x) = 4 - x,  s = sqrt(2)*x,  a = g/sqrt(2)
    Travel time: T_rect = sqrt(28 / g)
    """

    def __init__(self, g: float = 9.81, target_time: float = 1.62):
        super().__init__(name="Pista Recta", key="rect", color="#FF0055", g=g)
        self.physical_travel_time = np.sqrt(28.0 / g)  # ~1.6894 s
        self.target_travel_time = target_time          # 1.62 s
        self.total_arc_length = 7.0 * np.sqrt(2.0)     # ~9.8995 m

    def get_point_by_param(self, u: float) -> Tuple[float, float]:
        u_clamped = np.clip(u, 0.0, 1.0)
        x = 7.0 * u_clamped
        y = 4.0 - 7.0 * u_clamped
        return (float(x), float(y))

    def get_state(self, t: float, use_target_time: bool = True) -> TrackState:
        T = self.target_travel_time if use_target_time else self.physical_travel_time
        finished = t >= T
        t_eff = min(t, T)
        tau = t_eff / T  # tau in [0, 1]

        # Normalized kinematic progression: s(t) proportional to t^2 under constant acceleration
        u = tau ** 2
        x, y = self.get_point_by_param(u)

        # Potential energy drop: h = y_A - y
        h = max(0.0, self.y_A - y)
        speed = np.sqrt(2.0 * self.g * h)
        arc_len = u * self.total_arc_length

        vx = speed / np.sqrt(2.0)
        vy = -speed / np.sqrt(2.0)

        return TrackState(
            x=x, y=y, vx=vx, vy=vy,
            speed=speed, arc_length=arc_len,
            t_elapsed=t_eff, finished=finished
        )


class CycloidTrack(BaseTrack):
    """
    Track 4 (Euler-Lagrange Brachistochrone): Inverted Cycloid
    x(theta) = r * (theta - sin(theta))
    y(theta) = 4 - r * (1 - cos(theta))
    dtheta/dt = sqrt(g / r) = constant!
    """

    def __init__(self, g: float = 9.81, target_time: float = 1.32):
        super().__init__(name="Pista Cicloide (Braquistócrona)", key="braq", color="#00F0FF", g=g)
        
        # Solve for theta_max: (theta - sin(theta)) / (1 - cos(theta)) = (7 - 0) / (4 - (-3)) = 1.0
        def f_root(theta):
            return (theta - np.sin(theta)) / (1.0 - np.cos(theta)) - 1.0

        sol = root_scalar(f_root, bracket=[0.5, np.pi])
        self.theta_max = sol.root  # ~2.412011 rad (138.2 deg)
        self.r = 7.0 / (1.0 - np.cos(self.theta_max))  # ~4.010486 m
        self.omega = np.sqrt(g / self.r)
        self.physical_travel_time = self.theta_max / self.omega  # ~1.5422 s
        self.target_travel_time = target_time                    # 1.32 s

        # Total arc length: s = integral_0^{theta_max} 2*r*sin(theta/2) dtheta = 4*r*(1 - cos(theta_max/2))
        self.total_arc_length = 4.0 * self.r * (1.0 - np.cos(self.theta_max / 2.0))  # ~10.364 m

    def get_point_by_param(self, u: float) -> Tuple[float, float]:
        u_clamped = np.clip(u, 0.0, 1.0)
        theta = u_clamped * self.theta_max
        x = self.r * (theta - np.sin(theta))
        y = 4.0 - self.r * (1.0 - np.cos(theta))
        return (float(x), float(y))

    def get_state(self, t: float, use_target_time: bool = True) -> TrackState:
        T = self.target_travel_time if use_target_time else self.physical_travel_time
        finished = t >= T
        t_eff = min(t, T)
        tau = t_eff / T

        # For the cycloid, theta is strictly linear with time!
        theta = tau * self.theta_max
        x = self.r * (theta - np.sin(theta))
        y = 4.0 - self.r * (1.0 - np.cos(theta))

        h = max(0.0, self.y_A - y)
        speed = np.sqrt(2.0 * self.g * h)
        arc_len = 4.0 * self.r * (1.0 - np.cos(theta / 2.0))

        # Velocity components from tangent vector
        if theta > 1e-6:
            dx_dtheta = self.r * (1.0 - np.cos(theta))
            dy_dtheta = -self.r * np.sin(theta)
            norm = np.sqrt(dx_dtheta**2 + dy_dtheta**2)
            vx = speed * (dx_dtheta / norm)
            vy = speed * (dy_dtheta / norm)
        else:
            vx, vy = 0.0, 0.0

        return TrackState(
            x=x, y=y, vx=vx, vy=vy,
            speed=speed, arc_length=arc_len,
            t_elapsed=t_eff, finished=finished
        )


class ParabolicTrack(BaseTrack):
    """
    Track 2: Parabola passing through A(0, 4) and B(7, -3)
    y(x) = 4 - x - a*x*(7 - x)
    """

    def __init__(self, a: float = 0.10, g: float = 9.81, target_time: float = 1.45):
        super().__init__(name="Pista Parabólica", key="parab", color="#FFE600", g=g)
        self.a = a
        self.target_travel_time = target_time

        # Precompute desingularized quadrature t(x)
        # Using x = u^2 to eliminate 1/sqrt(x) singularity at x=0
        num_grid = 300
        u_vals = np.linspace(0.0, np.sqrt(7.0), num_grid)
        x_vals = u_vals ** 2
        t_vals = np.zeros(num_grid)

        def integrand(u):
            x = u ** 2
            dydx = -1.0 - 7.0 * self.a + 2.0 * self.a * x
            drop_factor = 1.0 + self.a * (7.0 - x)
            denom = np.sqrt(2.0 * self.g * max(1e-8, drop_factor))
            return 2.0 * np.sqrt(1.0 + dydx ** 2) / denom

        for i in range(1, num_grid):
            val, _ = quad(integrand, 0.0, u_vals[i], epsrel=1e-8)
            t_vals[i] = val

        self.physical_travel_time = float(t_vals[-1])
        self.t_to_x_spline = PchipInterpolator(t_vals, x_vals)

        # Arc length computation
        def ds_du(u):
            x = u ** 2
            dydx = -1.0 - 7.0 * self.a + 2.0 * self.a * x
            return 2.0 * u * np.sqrt(1.0 + dydx ** 2)

        tot_s, _ = quad(ds_du, 0.0, np.sqrt(7.0), epsrel=1e-8)
        self.total_arc_length = float(tot_s)

    def get_point_by_param(self, u: float) -> Tuple[float, float]:
        u_clamped = np.clip(u, 0.0, 1.0)
        x = 7.0 * u_clamped
        y = 4.0 - x - self.a * x * (7.0 - x)
        return (float(x), float(y))

    def get_state(self, t: float, use_target_time: bool = True) -> TrackState:
        T = self.target_travel_time if use_target_time else self.physical_travel_time
        finished = t >= T
        t_eff = min(t, T)
        tau = t_eff / T

        t_mapped = tau * self.physical_travel_time
        x = float(self.t_to_x_spline(t_mapped))
        x = np.clip(x, 0.0, 7.0)
        y = 4.0 - x - self.a * x * (7.0 - x)

        h = max(0.0, self.y_A - y)
        speed = np.sqrt(2.0 * self.g * h)

        dydx = -1.0 - 7.0 * self.a + 2.0 * self.a * x
        norm = np.sqrt(1.0 + dydx ** 2)
        vx = speed / norm
        vy = speed * dydx / norm

        arc_len = tau * self.total_arc_length

        return TrackState(
            x=x, y=y, vx=vx, vy=vy,
            speed=speed, arc_length=arc_len,
            t_elapsed=t_eff, finished=finished
        )


class CircularTrack(BaseTrack):
    """
    Track 3: Circular Arc passing through A(0, 4) and B(7, -3)
    Center on perpendicular bisector of chord AB.
    """

    def __init__(self, h_offset: float = 6.5, g: float = 9.81, target_time: float = 1.39):
        super().__init__(name="Pista Circular (Arco)", key="circ", color="#7928CA", g=g)
        self.h = h_offset
        self.target_travel_time = target_time

        # Circle geometry
        self.xc = 3.5 + self.h / np.sqrt(2.0)
        self.yc = 0.5 + self.h / np.sqrt(2.0)
        self.R = np.sqrt(self.h ** 2 + 24.5)

        self.phi_A = np.arctan2(4.0 - self.yc, 0.0 - self.xc)
        self.phi_B = np.arctan2(-3.0 - self.yc, 7.0 - self.xc)
        self.dphi = self.phi_B - self.phi_A  # Positive angular displacement

        self.total_arc_length = float(self.R * self.dphi)

        # Precompute desingularized quadrature t(alpha) with alpha = sigma^2
        num_grid = 300
        sigma_vals = np.linspace(0.0, np.sqrt(self.dphi), num_grid)
        alpha_vals = sigma_vals ** 2
        t_vals = np.zeros(num_grid)

        def integrand(s):
            if s == 0:
                return 0.0
            a_val = s ** 2
            phi = self.phi_A + a_val
            y_val = self.yc + self.R * np.sin(phi)
            drop = max(1e-8, 4.0 - y_val)
            v = np.sqrt(2.0 * self.g * drop)
            return 2.0 * self.R * s / v

        for i in range(1, num_grid):
            val, _ = quad(integrand, 0.0, sigma_vals[i], epsrel=1e-8)
            t_vals[i] = val

        self.physical_travel_time = float(t_vals[-1])
        self.t_to_alpha_spline = PchipInterpolator(t_vals, alpha_vals)

    def get_point_by_param(self, u: float) -> Tuple[float, float]:
        u_clamped = np.clip(u, 0.0, 1.0)
        phi = self.phi_A + u_clamped * self.dphi
        x = self.xc + self.R * np.cos(phi)
        y = self.yc + self.R * np.sin(phi)
        return (float(x), float(y))

    def get_state(self, t: float, use_target_time: bool = True) -> TrackState:
        T = self.target_travel_time if use_target_time else self.physical_travel_time
        finished = t >= T
        t_eff = min(t, T)
        tau = t_eff / T

        t_mapped = tau * self.physical_travel_time
        alpha = float(self.t_to_alpha_spline(t_mapped))
        alpha = np.clip(alpha, 0.0, self.dphi)
        phi = self.phi_A + alpha

        x = float(self.xc + self.R * np.cos(phi))
        y = float(self.yc + self.R * np.sin(phi))

        h = max(0.0, self.y_A - y)
        speed = np.sqrt(2.0 * self.g * h)

        # Tangent vector for circular motion
        vx = -speed * np.sin(phi)
        vy = speed * np.cos(phi)

        arc_len = alpha * self.R

        return TrackState(
            x=x, y=y, vx=vx, vy=vy,
            speed=speed, arc_length=arc_len,
            t_elapsed=t_eff, finished=finished
        )


class BrachistochroneSimulator:
    """High-level physics manager orchestrating all 4 tracks simultaneously."""

    def __init__(self, g: float = 9.81):
        self.g = g
        self.tracks: Dict[str, BaseTrack] = {
            "braq": CycloidTrack(g=g, target_time=1.32),
            "circ": CircularTrack(g=g, target_time=1.39),
            "parab": ParabolicTrack(g=g, target_time=1.45),
            "rect": StraightTrack(g=g, target_time=1.62),
        }

    def get_all_states(self, t: float, use_target_time: bool = True) -> Dict[str, TrackState]:
        return {key: track.get_state(t, use_target_time=use_target_time) for key, track in self.tracks.items()}

    def get_summary_data(self) -> List[Dict]:
        """Returns ordered benchmark data from 1st to 4th place."""
        ordered_keys = ["braq", "circ", "parab", "rect"]
        summary = []
        for rank, key in enumerate(ordered_keys, start=1):
            track = self.tracks[key]
            final_speed = np.sqrt(2.0 * self.g * (4.0 - (-3.0)))
            summary.append({
                "rank": rank,
                "key": key,
                "name": track.name,
                "color": track.color,
                "target_time": track.target_travel_time,
                "physical_time": track.physical_travel_time,
                "arc_length": track.total_arc_length,
                "final_speed": final_speed,
            })
        return summary
