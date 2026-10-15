"""
Continuum Lab — Classical Mechanics & Mechanical Engineering Division
Module: 02 Dinamica y Vibraciones / 05 Mecanismo Peaucellier Lipkin
File: peaucellier_kinematics.py

Rigorous Analytical Kinematics of the Peaucellier-Lipkin Exact Straight-Line Linkage (1864).
Proves geometric inversion in the complex plane:
    OP · OP' = R^2 - l^2 = k  (Inversion Constant)
    x_P' = (R^2 - l^2) / (2 * r) = CONSTANT (Euclidean Straight Line)
    Linear Deviation Error: epsilon = 0.000000000 mm (Machine Precision).
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, List


@dataclass
class PeaucellierParameters:
    """Geometric and kinematic design parameters for Peaucellier-Lipkin linkage."""
    # Origin of fixed inversion pole O1
    x_O1: float = -2.00
    y_O1: float = 0.0
    
    # Distance between fixed pivots O1 and O2 equals crank radius r
    r_crank: float = 0.85
    
    # Length of main long arms O1-A and O1-B
    R_arm: float = 2.80
    
    # Side length of the rhombus APBP' (AP = BP = AP' = BP' = l)
    l_rhombus: float = 1.60
    
    # Driving crank angular speed (rad/s)
    omega_crank: float = 0.95
    
    @property
    def O1(self) -> np.ndarray:
        return np.array([self.x_O1, self.y_O1], dtype=float)
    
    @property
    def O2(self) -> np.ndarray:
        return np.array([self.x_O1 + self.r_crank, self.y_O1], dtype=float)
    
    @property
    def inversion_constant(self) -> float:
        """k = R^2 - l^2"""
        return self.R_arm**2 - self.l_rhombus**2
    
    @property
    def exact_line_x(self) -> float:
        """x_world = x_O1 + (R^2 - l^2) / (2 * r)"""
        return self.x_O1 + self.inversion_constant / (2.0 * self.r_crank)


class PeaucellierSolver:
    """
    Computes closed-form positions, velocities, and straightness errors
    for all 7 moving links and 6 revolute joints.
    """
    def __init__(self, params: PeaucellierParameters = None):
        self.params = params or PeaucellierParameters()
        
    def solve_joint_positions(self, theta: float) -> Dict[str, np.ndarray]:
        """
        Solves analytical coordinates of joints O1, O2, P, P', A, B, and midpoint M
        given crank angle theta (measured from horizontal axis O1->O2).
        """
        O1 = self.params.O1
        O2 = self.params.O2
        r = self.params.r_crank
        R = self.params.R_arm
        l = self.params.l_rhombus
        k = self.params.inversion_constant
        
        # 1. Crank Tip P (Point on circle passing through O1)
        # Vector O2 -> P: r * [cos(theta), sin(theta)]
        P = O2 + r * np.array([np.cos(theta), np.sin(theta)], dtype=float)
        
        # Vector O1 -> P
        v_O1_P = P - O1
        dist_OP = np.linalg.norm(v_O1_P)
        if dist_OP < 1e-9:
            dist_OP = 1e-9
            
        phi = np.arctan2(v_O1_P[1], v_O1_P[0])  # Note: phi = theta / 2
        u_ray = np.array([np.cos(phi), np.sin(phi)], dtype=float)
        n_perp = np.array([-np.sin(phi), np.cos(phi)], dtype=float)
        
        # 2. Inverted Point P' (Tracer of exact vertical straight line)
        dist_OPp = k / dist_OP
        Pp = O1 + dist_OPp * u_ray
        
        # 3. Rhombus Midpoint M (Intersection of diagonals AB and PP')
        # M is midway between P and P'
        dist_OM = 0.5 * (dist_OP + dist_OPp)
        M = O1 + dist_OM * u_ray
        
        # 4. Rhombus Lateral Joints A and B
        # In right triangle O1-M-A: O1A^2 = OM^2 + MA^2 => MA = sqrt(R^2 - OM^2)
        # Equivalently in triangle P-M-A: PA^2 = PM^2 + MA^2 => MA = sqrt(l^2 - PM^2)
        half_diag_P = 0.5 * abs(dist_OPp - dist_OP)
        under_sqrt = l**2 - half_diag_P**2
        if under_sqrt < 0:
            under_sqrt = 0.0
        h_AM = np.sqrt(under_sqrt)
        
        A = M + h_AM * n_perp
        B = M - h_AM * n_perp
        
        # Verify theoretical straight line error
        exact_x = self.params.exact_line_x
        error_x = abs(Pp[0] - exact_x)
        
        return {
            "O1": O1,
            "O2": O2,
            "P": P,
            "Pp": Pp,
            "A": A,
            "B": B,
            "M": M,
            "phi": phi,
            "theta": theta,
            "dist_OP": dist_OP,
            "dist_OPp": dist_OPp,
            "error_x": error_x,
            "exact_x": exact_x
        }
        
    def solve_trajectory(self, t_array: np.ndarray, theta_max_deg: float = 62.0) -> Dict[str, np.ndarray]:
        """
        Computes time-history trajectory under harmonic oscillatory sweeping
        theta(t) = theta_max * sin(omega * t).
        """
        theta_max = np.radians(theta_max_deg)
        omega = self.params.omega_crank
        
        num_steps = len(t_array)
        data = {
            "time": t_array,
            "theta": np.zeros(num_steps),
            "P_x": np.zeros(num_steps), "P_y": np.zeros(num_steps),
            "Pp_x": np.zeros(num_steps), "Pp_y": np.zeros(num_steps),
            "A_x": np.zeros(num_steps), "A_y": np.zeros(num_steps),
            "B_x": np.zeros(num_steps), "B_y": np.zeros(num_steps),
            "v_Pp_y": np.zeros(num_steps),
            "error_x": np.zeros(num_steps)
        }
        
        for i, t in enumerate(t_array):
            th = theta_max * np.sin(omega * t)
            joints = self.solve_joint_positions(th)
            data["theta"][i] = th
            data["P_x"][i], data["P_y"][i] = joints["P"]
            data["Pp_x"][i], data["Pp_y"][i] = joints["Pp"]
            data["A_x"][i], data["A_y"][i] = joints["A"]
            data["B_x"][i], data["B_y"][i] = joints["B"]
            data["error_x"][i] = joints["error_x"]
            
        # Differentiate tracer vertical velocity
        dt = t_array[1] - t_array[0] if num_steps > 1 else 1e-3
        data["v_Pp_y"] = np.gradient(data["Pp_y"], dt)
        
        return data
