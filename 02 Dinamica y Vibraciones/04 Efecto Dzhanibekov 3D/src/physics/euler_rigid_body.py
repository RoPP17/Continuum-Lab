"""
Continuum Lab — Classical Mechanics & Dynamical Systems
Division: 02 Dinamica y Vibraciones / 04 Efecto Dzhanibekov 3D
Module: Rigid Body Dynamics & Euler Torque-Free Equations

Theoretical Physics Formulation:
- Asymmetric rigid body with principal moments of inertia: I1 < I2 < I3.
- Free rotational motion under microgravity (zero external torque: tau = 0).
- State space integration via Runge-Kutta 8th order (DOP853).
- Dual strict conservation: Rotational Energy T_rot = const, Angular Momentum |L| = const.
- Attitude kinematics via unit quaternions q(t) in SO(3).
"""

from dataclasses import dataclass
from typing import Tuple, Dict, Any
import numpy as np
from scipy.integrate import solve_ivp


@dataclass
class RigidBodyParams:
    """Principal inertia moments and geometry parameters of the T-handle."""
    I1: float = 1.0  # kg*m^2 (Minor axis - Stable center)
    I2: float = 2.4  # kg*m^2 (Intermediate axis - Hyperbolic saddle / UNSTABLE)
    I3: float = 4.2  # kg*m^2 (Major axis - Stable center)
    mass: float = 3.5  # kg total mass
    shaft_length: float = 2.4  # m
    shaft_radius: float = 0.12  # m
    crossbar_length: float = 1.8  # m
    crossbar_radius: float = 0.10  # m


class RigidBodySimulator:
    """
    Solves coupled Euler equations of motion and quaternion attitude kinematics.
    """

    def __init__(self, params: RigidBodyParams = None):
        self.params = params or RigidBodyParams()
        self.I1 = self.params.I1
        self.I2 = self.params.I2
        self.I3 = self.params.I3

    @staticmethod
    def quaternion_to_matrix(q: np.ndarray) -> np.ndarray:
        """
        Converts unit quaternion q = [qw, qx, qy, qz] to 3x3 rotation matrix R.
        Maps body coordinates to space coordinates: r_space = R @ r_body.
        """
        qw, qx, qy, qz = q / np.linalg.norm(q)
        return np.array([
            [1.0 - 2.0 * (qy**2 + qz**2), 2.0 * (qx * qy - qz * qw), 2.0 * (qx * qz + qy * qw)],
            [2.0 * (qx * qy + qz * qw), 1.0 - 2.0 * (qx**2 + qz**2), 2.0 * (qy * qz - qx * qw)],
            [2.0 * (qx * qz - qy * qw), 2.0 * (qy * qz + qx * qw), 1.0 - 2.0 * (qx**2 + qy**2)]
        ], dtype=float)

    def euler_derivatives(self, t: float, state: np.ndarray) -> np.ndarray:
        """
        Coupled first-order ODEs:
        state = [omega_1, omega_2, omega_3, q_w, q_x, q_y, q_z]
        """
        w1, w2, w3 = state[0:3]
        qw, qx, qy, qz = state[3:7]

        # Euler equations without external torque
        dw1 = (self.I2 - self.I3) / self.I1 * w2 * w3
        dw2 = (self.I3 - self.I1) / self.I2 * w3 * w1
        dw3 = (self.I1 - self.I2) / self.I3 * w1 * w2

        # Quaternion kinematics: q_dot = 0.5 * q (x) [0, w_body]
        dqw = 0.5 * (-qx * w1 - qy * w2 - qz * w3)
        dqx = 0.5 * ( qw * w1 + qy * w3 - qz * w2)
        dqy = 0.5 * ( qw * w2 + qz * w1 - qx * w3)
        dqz = 0.5 * ( qw * w3 + qx * w2 - qy * w1)

        return np.array([dw1, dw2, dw3, dqw, dqx, dqy, dqz], dtype=float)

    def kinetic_energy(self, omega: np.ndarray) -> float:
        """Rotational kinetic energy: T = 0.5 * (I1*w1^2 + I2*w2^2 + I3*w3^2)"""
        return 0.5 * (self.I1 * omega[0]**2 + self.I2 * omega[1]**2 + self.I3 * omega[2]**2)

    def angular_momentum_body(self, omega: np.ndarray) -> np.ndarray:
        """Angular momentum in body frame: L_b = [I1*w1, I2*w2, I3*w3]"""
        return np.array([self.I1 * omega[0], self.I2 * omega[1], self.I3 * omega[2]], dtype=float)

    def angular_momentum_magnitude(self, omega: np.ndarray) -> float:
        """Magnitude |L| = sqrt((I1*w1)^2 + (I2*w2)^2 + (I3*w3)^2)"""
        lb = self.angular_momentum_body(omega)
        return float(np.linalg.norm(lb))

    def angular_momentum_space(self, omega: np.ndarray, q: np.ndarray) -> np.ndarray:
        """Angular momentum vector in inertial space frame: L_s = R(q) @ L_b"""
        R = self.quaternion_to_matrix(q)
        return R @ self.angular_momentum_body(omega)

    def get_optimal_perturbation(self, w2_init: float = 12.0) -> np.ndarray:
        """
        Calculates initial angular velocity with precise micro-perturbation
        tuned to match the cinematic timeline:
        - 0.0 - 3.5s: Stable spin around intermediate axis
        - 3.5 - 5.0s: Spontaneous homoclinic acrobatic flip
        - 5.0 - 8.5s: Inverted spin
        - 8.5 - 10.0s: Second flip returning to upright orientation
        """
        # Exact separatrix ratio: sqrt( (I3*(I3-I2)) / (I1*(I2-I1)) )
        ratio = np.sqrt((self.I3 * (self.I3 - self.I2)) / (self.I1 * (self.I2 - self.I1)))
        delta1 = 2.0e-5
        delta3 = (delta1 / ratio) * (1.0 - 1.0e-12)
        return np.array([delta1, w2_init, delta3], dtype=float)

    def simulate(
        self,
        t_span: Tuple[float, float] = (0.0, 14.0),
        fps: int = 60,
        omega0: np.ndarray = None,
        q0: np.ndarray = None,
        method: str = "DOP853",
        rtol: float = 1e-11,
        atol: float = 1e-13
    ) -> Dict[str, Any]:
        """
        Integrates the complete motion and attitude over t_span.
        Returns time array, omega, orientation matrices, and conservation metrics.
        """
        if omega0 is None:
            omega0 = self.get_optimal_perturbation(12.0)
        if q0 is None:
            q0 = np.array([1.0, 0.0, 0.0, 0.0], dtype=float)

        total_frames = int(round((t_span[1] - t_span[0]) * fps)) + 1
        t_eval = np.linspace(t_span[0], t_span[1], total_frames)

        state0 = np.concatenate([omega0, q0])

        sol = solve_ivp(
            fun=self.euler_derivatives,
            t_span=t_span,
            y0=state0,
            method=method,
            t_eval=t_eval,
            rtol=rtol,
            atol=atol
        )

        time_arr = sol.t
        omega_body = sol.y[0:3].T  # Shape: (N, 3)
        quats = sol.y[3:7].T       # Shape: (N, 4)

        # Normalize quaternions to prevent numerical drift
        norms = np.linalg.norm(quats, axis=1, keepdims=True)
        quats = quats / norms

        rot_matrices = np.zeros((len(time_arr), 3, 3), dtype=float)
        omega_space = np.zeros_like(omega_body)
        l_space = np.zeros_like(omega_body)
        energy_arr = np.zeros(len(time_arr), dtype=float)
        l_mag_arr = np.zeros(len(time_arr), dtype=float)

        for i in range(len(time_arr)):
            R = self.quaternion_to_matrix(quats[i])
            rot_matrices[i] = R
            omega_space[i] = R @ omega_body[i]
            l_b = self.angular_momentum_body(omega_body[i])
            l_space[i] = R @ l_b
            energy_arr[i] = self.kinetic_energy(omega_body[i])
            l_mag_arr[i] = np.linalg.norm(l_b)

        # Conservation deviations
        delta_E = np.max(np.abs(energy_arr - energy_arr[0])) / energy_arr[0]
        delta_L_mag = np.max(np.abs(l_mag_arr - l_mag_arr[0])) / l_mag_arr[0]
        l_space_dev = np.max(np.linalg.norm(l_space - l_space[0], axis=1))

        return {
            "time": time_arr,
            "omega_body": omega_body,
            "omega_space": omega_space,
            "quaternions": quats,
            "rot_matrices": rot_matrices,
            "l_space": l_space,
            "l_magnitude": l_mag_arr,
            "kinetic_energy": energy_arr,
            "initial_energy": energy_arr[0],
            "initial_l_mag": l_mag_arr[0],
            "rel_energy_drift": delta_E,
            "rel_momentum_drift": delta_L_mag,
            "space_momentum_drift": l_space_dev,
            "total_frames": len(time_arr)
        }
