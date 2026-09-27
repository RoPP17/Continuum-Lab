"""
Continuum Lab — Mathematical Physics & Complex Geometry
Module: 06 Matematicas y Geometria / 02 Identidad de Euler 3D
Analytical Engine for Euler's Formula and 3D Complex Helix Dynamics.

Mathematical Foundation:
  Euler's Formula establishes the profound equivalence:
      e^{i theta} = cos(theta) + i sin(theta)

  In 3D Euclidean space R^3 with axes (X: parameter theta, Y: Real part, Z: Imaginary part):
      r(t) = (t, cos(t), sin(t))^T

  Orthogonal Projections:
    1. Projection onto XY plane (Z = 0):
       P_XY r(t) = (t, cos(t), 0)^T  --> Pure Cosine Wave
    2. Projection onto XZ plane (Y = 0):
       P_XZ r(t) = (t, 0, sin(t))^T  --> Pure Sine Wave
    3. Projection onto YZ plane (X = 0):
       P_YZ r(t) = (0, cos(t), sin(t))^T  --> Complex Unit Circle |z| = 1

  Euler's Identity:
    At theta = pi:
      e^{i pi} = cos(pi) + i sin(pi) = -1 + 0i
      ==> e^{i pi} + 1 = 0
"""

import numpy as np
from typing import Dict, List, Tuple, Any
import math


class EulerHelixAnalysis:
    """
    Analytical and numerical engine for the 3D complex helical representation
    of Euler's formula and its canonical projections.
    """

    def __init__(self, t_max: float = 4.0 * np.pi, num_points: int = 500):
        self.t_max = float(t_max)
        self.num_points = int(num_points)
        self.t_vals = np.linspace(0.0, self.t_max, self.num_points)

    def evaluate_point(self, t: float) -> Dict[str, Any]:
        """
        Evaluates exact 3D coordinates, projections, and complex properties at parameter t.
        """
        re_val = math.cos(t)
        im_val = math.sin(t)
        z_complex = complex(re_val, im_val)
        modulus = abs(z_complex)
        phase = math.atan2(im_val, re_val)

        return {
            "t": t,
            "coords_3d": np.array([t, re_val, im_val]),
            "proj_xy": np.array([t, re_val, 0.0]),      # Cosine wave
            "proj_xz": np.array([t, 0.0, im_val]),      # Sine wave
            "proj_yz": np.array([0.0, re_val, im_val]),  # Unit circle in complex plane
            "re": re_val,
            "im": im_val,
            "modulus": modulus,
            "phase_rad": phase,
            "phase_deg": math.degrees(phase),
            "euler_identity_residual": abs(z_complex + 1.0) if math.isclose(t, math.pi, abs_tol=1e-5) else None,
        }

    def get_trajectory_arrays(self) -> Dict[str, np.ndarray]:
        """
        Returns full numpy arrays of the trajectory and all canonical projections.
        """
        x = self.t_vals
        y = np.cos(self.t_vals)
        z = np.sin(self.t_vals)

        return {
            "t": x,
            "re": y,
            "im": z,
            "curve_3d": np.column_stack([x, y, z]),
            "proj_xy": np.column_stack([x, y, np.zeros_like(x)]),
            "proj_xz": np.column_stack([x, np.zeros_like(x), z]),
            "proj_yz": np.column_stack([np.zeros_like(x), y, z]),
            "modulus": np.sqrt(y**2 + z**2),
        }

    def differential_properties(self, t: float) -> Dict[str, Any]:
        """
        Calculates differential geometry quantities for the circular helix:
        Tangent vector, normal vector, binormal vector, curvature, and torsion.
        """
        # r(t) = (t, cos t, sin t)
        # v(t) = (1, -sin t, cos t)
        v = np.array([1.0, -np.sin(t), np.cos(t)])
        speed = np.linalg.norm(v)  # sqrt(1 + sin^2 + cos^2) = sqrt(2)

        # a(t) = (0, -cos t, -sin t)
        a = np.array([0.0, -np.cos(t), -np.sin(t)])
        a_norm = np.linalg.norm(a)  # 1.0

        # v x a = (sin^2 + cos^2, sin t, -cos t) = (1, sin t, -cos t)
        v_cross_a = np.cross(v, a)
        v_cross_a_norm = np.linalg.norm(v_cross_a)  # sqrt(1 + 1) = sqrt(2)

        # Curvature: kappa = |v x a| / |v|^3 = sqrt(2) / (sqrt(2))^3 = 1/2 = 0.5
        curvature = v_cross_a_norm / (speed**3)

        # a'(t) = (0, sin t, -cos t)
        a_prime = np.array([0.0, np.sin(t), -np.cos(t)])
        # Torsion: tau = (v x a) . a' / |v x a|^2 = (0 + sin^2 + cos^2) / 2 = 1/2 = 0.5
        torsion = np.dot(v_cross_a, a_prime) / (v_cross_a_norm**2)

        tangent = v / speed
        binormal = v_cross_a / v_cross_a_norm
        normal = np.cross(binormal, tangent)

        return {
            "t": t,
            "speed": speed,
            "curvature": curvature,
            "torsion": torsion,
            "tangent": tangent,
            "normal": normal,
            "binormal": binormal,
        }

    def key_landmarks(self) -> List[Dict[str, Any]]:
        """
        Returns cardinal angles showcasing the geometric milestones of Euler's formula.
        """
        angles = [
            (0.0, "0", "1 + 0i", "Inicio en Eje Real Positivo"),
            (0.5 * np.pi, r"\pi/2", "0 + 1i", "Paso por Unidad Imaginaria +i"),
            (np.pi, r"\pi", "-1 + 0i", "Identidad de Euler: e^{i pi} = -1"),
            (1.5 * np.pi, r"3\pi/2", "0 - 1i", "Paso por Unidad Imaginaria -i"),
            (2.0 * np.pi, r"2\pi", "1 + 0i", "Periodo Completo: e^{i 2 pi} = 1"),
        ]

        results = []
        for val, name, comp_str, desc in angles:
            p_info = self.evaluate_point(val)
            p_info["angle_symbol"] = name
            p_info["complex_str"] = comp_str
            p_info["description"] = desc
            results.append(p_info)
        return results

    def taylor_approximation(self, t: float, order: int = 5) -> Dict[str, float]:
        """
        Computes truncated Taylor series polynomial for exp(it):
        cos(t) ~ 1 - t^2/2! + t^4/4! - ...
        sin(t) ~ t - t^3/3! + t^5/5! - ...
        """
        cos_approx = 0.0
        sin_approx = 0.0

        for n in range(order + 1):
            term_cos = ((-1)**n) * (t**(2 * n)) / math.factorial(2 * n)
            cos_approx += term_cos
            term_sin = ((-1)**n) * (t**(2 * n + 1)) / math.factorial(2 * n + 1)
            sin_approx += term_sin

        return {
            "order": order,
            "t": t,
            "cos_exact": math.cos(t),
            "cos_approx": cos_approx,
            "cos_error": abs(math.cos(t) - cos_approx),
            "sin_exact": math.sin(t),
            "sin_approx": sin_approx,
            "sin_error": abs(math.sin(t) - sin_approx),
        }
