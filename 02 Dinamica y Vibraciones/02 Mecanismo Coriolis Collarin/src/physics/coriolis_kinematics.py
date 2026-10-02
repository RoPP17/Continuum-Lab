"""
Continuum Lab — Classical Mechanics & Dynamical Systems
Division: 02 Dinamica y Vibraciones / 02 Mecanismo Coriolis Collarin
Module: coriolis_kinematics.py

Rigorous Analytical Kinematics & Coriolis Acceleration Solver
for a 2-Bar Mechanism with Sliding Collar (Inverted Slotted Link / Quick-Return).
"""

from dataclasses import dataclass
from typing import Tuple, List, Dict, Any
import numpy as np


@dataclass
class CoriolisMechanismParams:
    """Geometric and kinematic parameters for the 2-bar mechanism."""
    L1: float = 1.0               # Longitud de la manivela impulsora O1-A [m]
    d: float = 1.5                # Separación vertical entre pivotes fijos O1 y O2 [m]
    omega1: float = 2.0           # Velocidad angular de la manivela [rad/s]
    alpha1: float = 0.0           # Aceleración angular de la manivela [rad/s^2]
    arm_extension: float = 1.8    # Longitud total de la barra ranurada respecto a r2_max
    x_O1: float = 0.0             # Coordenada X del pivote O1 [m]
    y_O1: float = 0.0             # Coordenada Y del pivote O1 [m]

    @property
    def x_O2(self) -> float:
        return self.x_O1

    @property
    def y_O2(self) -> float:
        return self.y_O1 - self.d

    @property
    def is_oscillating(self) -> bool:
        """Retorna True si d > L1 (régimen oscilante de balancín ranurado)."""
        return self.d > self.L1

    @property
    def max_rocker_angle(self) -> float:
        """Ángulo máximo de oscilación (semi-amplitud) en régimen oscilante."""
        if self.is_oscillating:
            return float(np.arcsin(self.L1 / self.d))
        return float(np.pi)


@dataclass
class KinematicState:
    """Estado cinemático vectorial completo en un instante t o ángulo theta1."""
    time: float
    theta1: float                 # Ángulo manivela [rad]
    omega1: float                 # Velocidad angular manivela [rad/s]
    alpha1: float                 # Aceleración angular manivela [rad/s^2]

    # Coordenadas y cinemática absoluta del punto A (collarín en manivela)
    r_A: np.ndarray               # Vector posición [xA, yA]
    v_A: np.ndarray               # Vector velocidad [vxA, vyA]
    a_A: np.ndarray               # Vector aceleración [axA, ayA]

    # Geometría de la barra ranurada 2 (pivote O2)
    r_O2: np.ndarray              # Vector posición de O2
    r_A_rel_O2: np.ndarray        # Vector r_(A/O2)
    r2: float                     # Distancia O2 a collarín [m]
    theta2: float                 # Ángulo de la barra ranurada [rad]
    u_r2: np.ndarray              # Vector unitario radial a lo largo de la barra 2
    u_theta2: np.ndarray          # Vector unitario transversal perpendicular a barra 2

    # Cinemática del marco móvil (Barra 2) y movimiento relativo
    omega2: float                 # Velocidad angular de la barra 2 [rad/s]
    alpha2: float                 # Aceleración angular de la barra 2 [rad/s^2]
    v_rel: float                  # Rapidez de deslizamiento dr2/dt [m/s]
    a_rel: float                  # Aceleración de deslizamiento d2r2/dt2 [m/s^2]

    # Vectores de descomposición cinemática de aceleración
    v_rel_vec: np.ndarray         # v_rel * u_r2
    v_transverse_vec: np.ndarray  # (omega2 * r2) * u_theta2
    
    a_euler_vec: np.ndarray       # (alpha2 * r2) * u_theta2 (aceleración tangencial/Euler)
    a_centripetal_vec: np.ndarray # -(omega2^2 * r2) * u_r2 (aceleración normal hacia O2)
    a_coriolis_vec: np.ndarray    # 2 * (omega2 x v_rel) = (2 * omega2 * v_rel) * u_theta2
    a_rel_vec: np.ndarray         # a_rel * u_r2 (aceleración relativa del collarín)
    a_coriolis_mag: float         # 2 * omega2 * v_rel (magnitud con signo en u_theta2)

    # Reconstrucción y verificación analítica
    a_reconstructed: np.ndarray   # Suma de los 4 términos
    residual_error: float         # ||a_A - a_reconstructed||

    # Extremo decorativo / trazador hipnótico de la barra 2
    r_tip_arm: np.ndarray         # Posición del extremo de la barra ranurada
    r_coriolis_tip: np.ndarray    # Posición en el plano del vector Coriolis (para hodógrafo)


class CoriolisKinematicsSolver:
    """
    Solucionador analítico riguroso del mecanismo de retorno rápido con ranura.
    Resuelve la cinemática directa y la aceleración de Coriolis en cada ciclo.
    """

    def __init__(self, params: CoriolisMechanismParams = None):
        self.params = params if params is not None else CoriolisMechanismParams()

    def solve(self, theta1: float, time: float = 0.0) -> KinematicState:
        """
        Calcula de manera cerrada y analítica el estado cinemático para un ángulo theta1.
        """
        p = self.params
        L1 = p.L1
        w1 = p.omega1
        a1 = p.alpha1
        x_O1, y_O1 = p.x_O1, p.y_O1
        x_O2, y_O2 = p.x_O2, p.y_O2
        r_O2 = np.array([x_O2, y_O2], dtype=np.float64)

        # 1. Cinemática absoluta del punto A (pasador del collarín sobre la manivela 1)
        cos1 = np.cos(theta1)
        sin1 = np.sin(theta1)

        xA = x_O1 + L1 * cos1
        yA = y_O1 + L1 * sin1
        r_A = np.array([xA, yA], dtype=np.float64)

        vxA = -L1 * w1 * sin1
        vyA = L1 * w1 * cos1
        v_A = np.array([vxA, vyA], dtype=np.float64)

        axA = -L1 * (w1**2) * cos1 - L1 * a1 * sin1
        ayA = -L1 * (w1**2) * sin1 + L1 * a1 * cos1
        a_A = np.array([axA, ayA], dtype=np.float64)

        # 2. Vector posición relativo respecto al pivote O2
        r_A_rel_O2 = r_A - r_O2
        rx, ry = r_A_rel_O2[0], r_A_rel_O2[1]
        r2 = float(np.sqrt(rx**2 + ry**2))

        # Ángulo de la barra ranurada 2
        theta2 = float(np.arctan2(ry, rx))

        # Base de vectores unitarios polar de la barra 2
        cos2 = np.cos(theta2)
        sin2 = np.sin(theta2)
        u_r2 = np.array([cos2, sin2], dtype=np.float64)
        u_theta2 = np.array([-sin2, cos2], dtype=np.float64)

        # 3. Cinemática de velocidades: Descomposición en marco rotativo de la Barra 2
        # v_A = v_rel * u_r2 + (r2 * omega2) * u_theta2
        v_rel = float(np.dot(v_A, u_r2))
        omega2 = float(np.dot(v_A, u_theta2) / r2)

        v_rel_vec = v_rel * u_r2
        v_transverse_vec = (omega2 * r2) * u_theta2

        # 4. Cinemática de aceleraciones y término de Coriolis
        # a_A = (a_rel - omega2^2 * r2) * u_r2 + (alpha2 * r2 + 2 * omega2 * v_rel) * u_theta2
        a_r2_comp = float(np.dot(a_A, u_r2))
        a_theta2_comp = float(np.dot(a_A, u_theta2))

        # Despeje analítico de incógnitas en el marco móvil:
        a_rel = a_r2_comp + (omega2**2) * r2
        alpha2 = (a_theta2_comp - 2.0 * omega2 * v_rel) / r2

        # Cuatro componentes exactas de aceleración
        a_euler_vec = (alpha2 * r2) * u_theta2
        a_centripetal_vec = -(omega2**2 * r2) * u_r2
        a_coriolis_mag = 2.0 * omega2 * v_rel
        a_coriolis_vec = a_coriolis_mag * u_theta2
        a_rel_vec = a_rel * u_r2

        # Reconstrucción y verificación formal
        a_reconstructed = a_euler_vec + a_centripetal_vec + a_coriolis_vec + a_rel_vec
        residual_error = float(np.linalg.norm(a_A - a_reconstructed))

        # 5. Geometría visual extendida y punta del hodógrafo
        arm_total_length = max(L1 + p.d, r2 * 1.3) * p.arm_extension * 0.7
        r_tip_arm = r_O2 + arm_total_length * u_r2

        # Posición para visualización de punta de vector Coriolis (con factor de escala visual)
        r_coriolis_tip = r_A + a_coriolis_vec * 0.15

        return KinematicState(
            time=time,
            theta1=theta1,
            omega1=w1,
            alpha1=a1,
            r_A=r_A,
            v_A=v_A,
            a_A=a_A,
            r_O2=r_O2,
            r_A_rel_O2=r_A_rel_O2,
            r2=r2,
            theta2=theta2,
            u_r2=u_r2,
            u_theta2=u_theta2,
            omega2=omega2,
            alpha2=alpha2,
            v_rel=v_rel,
            a_rel=a_rel,
            v_rel_vec=v_rel_vec,
            v_transverse_vec=v_transverse_vec,
            a_euler_vec=a_euler_vec,
            a_centripetal_vec=a_centripetal_vec,
            a_coriolis_vec=a_coriolis_vec,
            a_rel_vec=a_rel_vec,
            a_coriolis_mag=a_coriolis_mag,
            a_reconstructed=a_reconstructed,
            residual_error=residual_error,
            r_tip_arm=r_tip_arm,
            r_coriolis_tip=r_coriolis_tip,
        )

    def generate_cycle(self, num_points: int = 1000) -> List[KinematicState]:
        """Genera una trayectoria periódica completa de 0 a 2*pi para la manivela."""
        theta_vals = np.linspace(0.0, 2.0 * np.pi, num_points, endpoint=False)
        cycle_states = []
        period = 2.0 * np.pi / abs(self.params.omega1) if self.params.omega1 != 0 else 1.0

        for idx, th1 in enumerate(theta_vals):
            t = (th1 / (2.0 * np.pi)) * period
            state = self.solve(th1, time=t)
            cycle_states.append(state)

        return cycle_states
