"""
Continuum Lab — Classical Mechanics & Dynamical Systems
Exact Lagrangian Equations of Motion for the Non-Linear Triple Pendulum
Division: 02 Dinamica y Vibraciones / 01 Pendulo Triple Caotico
"""

from dataclasses import dataclass
from typing import Tuple, List
import numpy as np


@dataclass
class TriplePendulumParams:
    """Physical parameters for the triple pendulum."""
    l1: float = 1.0   # Length of rod 1 [m]
    l2: float = 1.0   # Length of rod 2 [m]
    l3: float = 1.0   # Length of rod 3 [m]
    m1: float = 1.0   # Mass of bob 1 [kg]
    m2: float = 1.0   # Mass of bob 2 [kg]
    m3: float = 1.0   # Mass of bob 3 [kg]
    g: float = 9.80665 # Gravitational acceleration [m/s^2]


class TriplePendulumSimulator:
    """
    Precision Non-Linear Integrator for the 3-DOF Chaotic Triple Pendulum.
    Solves M(theta) * ddot_theta = F(theta, dot_theta) via Runge-Kutta 4th Order (RK4).
    """

    def __init__(self, params: TriplePendulumParams = None):
        self.p = params or TriplePendulumParams()
        # State vector: [theta1, theta2, theta3, omega1, omega2, omega3]
        self.state = np.zeros(6, dtype=np.float64)
        self.time = 0.0

        # Cached masses
        self.mu1 = self.p.m1 + self.p.m2 + self.p.m3
        self.mu2 = self.p.m2 + self.p.m3
        self.mu3 = self.p.m3

    def set_initial_state(self, angles: Tuple[float, float, float], angular_velocities: Tuple[float, float, float] = (0.0, 0.0, 0.0)):
        """Sets initial angular configuration (in radians) and velocities."""
        self.state[0:3] = angles
        self.state[3:6] = angular_velocities
        self.time = 0.0

    def compute_derivatives(self, state: np.ndarray) -> np.ndarray:
        """
        Evaluates state derivative d/dt [theta, omega] = [omega, alpha].
        Inverts the 3x3 positive-definite generalized mass matrix M.
        """
        th1, th2, th3 = state[0], state[1], state[2]
        w1, w2, w3 = state[3], state[4], state[5]

        l1, l2, l3 = self.p.l1, self.p.l2, self.p.l3
        g = self.p.g
        mu1, mu2, mu3 = self.mu1, self.mu2, self.mu3

        # Mass Matrix M(theta)
        d12 = th1 - th2
        d13 = th1 - th3
        d23 = th2 - th3

        c12 = np.cos(d12)
        c13 = np.cos(d13)
        c23 = np.cos(d23)

        M = np.array([
            [mu1 * l1**2,        mu2 * l1 * l2 * c12, mu3 * l1 * l3 * c13],
            [mu2 * l1 * l2 * c12, mu2 * l2**2,        mu3 * l2 * l3 * c23],
            [mu3 * l1 * l3 * c13, mu3 * l2 * l3 * c23, mu3 * l3**2       ]
        ], dtype=np.float64)

        # Generalized RHS Force Vector F(theta, omega)
        s12 = np.sin(d12)
        s13 = np.sin(d13)
        s23 = np.sin(d23)

        F = np.array([
            -mu2 * l1 * l2 * (w2**2) * s12 - mu3 * l1 * l3 * (w3**2) * s13 - mu1 * g * l1 * np.sin(th1),
             mu2 * l1 * l2 * (w1**2) * s12 - mu3 * l2 * l3 * (w3**2) * s23 - mu2 * g * l2 * np.sin(th2),
             mu3 * l1 * l3 * (w1**2) * s13 + mu3 * l2 * l3 * (w2**2) * s23 - mu3 * g * l3 * np.sin(th3)
        ], dtype=np.float64)

        # Solve for angular accelerations: alpha = M^(-1) * F
        alpha = np.linalg.solve(M, F)

        # Return [w1, w2, w3, a1, a2, a3]
        return np.array([w1, w2, w3, alpha[0], alpha[1], alpha[2]], dtype=np.float64)

    def step_rk4(self, dt: float) -> None:
        """Classical 4th Order Runge-Kutta Integrator Step."""
        s = self.state
        k1 = self.compute_derivatives(s)
        k2 = self.compute_derivatives(s + 0.5 * dt * k1)
        k3 = self.compute_derivatives(s + 0.5 * dt * k2)
        k4 = self.compute_derivatives(s + dt * k3)

        self.state += (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        self.time += dt

    def get_cartesian_positions(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Computes 2D Cartesian coordinates (x, y) of the 3 bobs.
        Origin (0,0) is the fixed top pivot.
        """
        th1, th2, th3 = self.state[0], self.state[1], self.state[2]
        l1, l2, l3 = self.p.l1, self.p.l2, self.p.l3

        x1 = l1 * np.sin(th1)
        y1 = -l1 * np.cos(th1)

        x2 = x1 + l2 * np.sin(th2)
        y2 = y1 - l2 * np.cos(th2)

        x3 = x2 + l3 * np.sin(th3)
        y3 = y2 - l3 * np.cos(th3)

        return np.array([x1, y1]), np.array([x2, y2]), np.array([x3, y3])

    def total_energy(self) -> float:
        """Calculates total Hamiltonian mechanical energy E = T + V."""
        th1, th2, th3 = self.state[0], self.state[1], self.state[2]
        w1, w2, w3 = self.state[3], self.state[4], self.state[5]
        l1, l2, l3 = self.p.l1, self.p.l2, self.p.l3
        m1, m2, m3 = self.p.m1, self.p.m2, self.p.m3
        g = self.p.g

        # Kinetic energy
        v1_sq = (l1 * w1)**2
        v2_sq = v1_sq + (l2 * w2)**2 + 2.0 * l1 * l2 * w1 * w2 * np.cos(th1 - th2)
        v3_sq = v2_sq + (l3 * w3)**2 + 2.0 * l1 * l3 * w1 * w3 * np.cos(th1 - th3) + 2.0 * l2 * l3 * w2 * w3 * np.cos(th2 - th3)

        T = 0.5 * (m1 * v1_sq + m2 * v2_sq + m3 * v3_sq)

        # Potential energy (reference y=0 at pivot)
        y1 = -l1 * np.cos(th1)
        y2 = y1 - l2 * np.cos(th2)
        y3 = y2 - l3 * np.cos(th3)
        V = g * (m1 * y1 + m2 * y2 + m3 * y3)

        return T + V
