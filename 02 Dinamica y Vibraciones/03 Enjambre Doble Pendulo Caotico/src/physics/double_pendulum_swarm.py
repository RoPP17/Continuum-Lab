"""
Continuum Lab — Dinámica No Lineal y Sistemas Caóticos
Módulo de Física Computacional: Enjambre de Doble Péndulo Hamiltoniano
Resolución numérica de alta fidelidad mediante DOP853 (Runge-Kutta orden 8(5,3))
"""

from dataclasses import dataclass
from typing import Tuple, Dict, Any
import numpy as np
from scipy.integrate import solve_ivp


@dataclass
class SwarmParameters:
    """Parámetros físicos y de configuración del enjambre de doble péndulo."""
    m1: float = 1.0          # Masa 1 (kg)
    m2: float = 1.0          # Masa 2 (kg)
    L1: float = 1.5          # Longitud barra 1 (m)
    L2: float = 1.5          # Longitud barra 2 (m)
    g: float = 9.81          # Aceleración gravitatoria (m/s^2)
    num_pendulums: int = 50  # Tamaño del enjambre
    theta1_0_deg: float = 120.0  # Ángulo inicial base barra 1 (grados)
    theta2_0_deg: float = -60.0  # Ángulo inicial base barra 2 (grados)
    delta_theta: float = 1.0e-6  # Perturbación infinitesimal por péndulo (rad)
    duration: float = 15.0       # Duración total de la simulación (s)
    fps: int = 60                # Cuadros por segundo para muestreo
    rtol: float = 1.0e-9         # Tolerancia relativa del integrador DOP853
    atol: float = 1.0e-12        # Tolerancia absoluta del integrador DOP853


class DoublePendulumSwarmSimulator:
    """
    Simulador vectorial para un enjambre de N dobles péndulos planos no lineales.
    Resuelve el sistema de ecuaciones diferenciales acopladas de Euler-Lagrange
    conservando la energía hamiltoniana con un error relativo menor a 1e-7.
    """

    def __init__(self, params: SwarmParameters = None):
        self.params = params if params is not None else SwarmParameters()
        self.theta1_0 = np.radians(self.params.theta1_0_deg)
        self.theta2_0 = np.radians(self.params.theta2_0_deg)
        self.total_frames = int(self.params.duration * self.params.fps)
        self.t_eval = np.linspace(0.0, self.params.duration, self.total_frames + 1)

    def _equations_of_motion(self, t: float, y_flat: np.ndarray) -> np.ndarray:
        """
        Ecuaciones de movimiento vectorizadas para los N péndulos simultáneamente.
        y_flat: arreglo 1D de longitud 4 * N_pendulums.
        Estructura de Y:
            Y[0]: theta1 (N,)
            Y[1]: theta2 (N,)
            Y[2]: omega1 (N,)
            Y[3]: omega2 (N,)
        """
        n = self.params.num_pendulums
        y = y_flat.reshape(4, n)
        th1 = y[0]
        th2 = y[1]
        w1 = y[2]
        w2 = y[3]

        m1 = self.params.m1
        m2 = self.params.m2
        l1 = self.params.L1
        l2 = self.params.L2
        g = self.params.g

        dth = th1 - th2
        sin_dth = np.sin(dth)
        cos_dth = np.cos(dth)
        sin2_dth = sin_dth * sin_dth

        common_den = m1 + m2 * sin2_dth

        # Aceleración angular 1: d(w1)/dt
        den1 = l1 * common_den
        num1 = (
            -g * ((m1 + m2) * np.sin(th1) - m2 * np.sin(th2) * cos_dth)
            - m2 * sin_dth * (l2 * (w2 * w2) + l1 * (w1 * w1) * cos_dth)
        )
        alpha1 = num1 / den1

        # Aceleración angular 2: d(w2)/dt
        den2 = l2 * common_den
        num2 = (
            sin_dth * ((m1 + m2) * l1 * (w1 * w1) + m2 * l2 * (w2 * w2) * cos_dth)
            + (m1 + m2) * g * (np.sin(th1) * cos_dth - np.sin(th2))
        )
        alpha2 = num2 / den2

        dy_dt = np.empty_like(y)
        dy_dt[0] = w1
        dy_dt[1] = w2
        dy_dt[2] = alpha1
        dy_dt[3] = alpha2

        return dy_dt.ravel()

    def compute_energy(
        self, th1: np.ndarray, th2: np.ndarray, w1: np.ndarray, w2: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calcula la energía cinética (T), potencial (V) y hamiltoniana total (E = T + V).
        """
        m1 = self.params.m1
        m2 = self.params.m2
        l1 = self.params.L1
        l2 = self.params.L2
        g = self.params.g

        t_kin = (
            0.5 * (m1 + m2) * (l1 * l1) * (w1 * w1)
            + 0.5 * m2 * (l2 * l2) * (w2 * w2)
            + m2 * l1 * l2 * w1 * w2 * np.cos(th1 - th2)
        )
        v_pot = -(m1 + m2) * g * l1 * np.cos(th1) - m2 * g * l2 * np.cos(th2)
        e_total = t_kin + v_pot
        return t_kin, v_pot, e_total

    def run_simulation(self) -> Dict[str, Any]:
        """
        Ejecuta la integración numérica DOP853 de alta precisión para los 50 péndulos.
        Retorna diccionario con estados, posiciones cartesianas, energías y métricas de caos.
        """
        n = self.params.num_pendulums
        y0 = np.zeros((4, n), dtype=np.float64)

        # Condición inicial para cada péndulo k: perturbación infinitesimal
        for k in range(n):
            y0[0, k] = self.theta1_0 + k * self.params.delta_theta
            y0[1, k] = self.theta2_0
            y0[2, k] = 0.0
            y0[3, k] = 0.0

        sol = solve_ivp(
            fun=self._equations_of_motion,
            t_span=(0.0, self.params.duration),
            y0=y0.ravel(),
            method="DOP853",
            t_eval=self.t_eval,
            rtol=self.params.rtol,
            atol=self.params.atol,
        )

        if not sol.success:
            raise RuntimeError(f"Error en la integración DOP853: {sol.message}")

        # Reestructurar solución: forma (4, N_pendulums, N_frames)
        y_sol = sol.y.reshape(4, n, len(self.t_eval))
        th1 = y_sol[0]
        th2 = y_sol[1]
        w1 = y_sol[2]
        w2 = y_sol[3]

        l1 = self.params.L1
        l2 = self.params.L2

        # Coordenadas cartesianas respecto al pivote
        # Bob 1: (x1, y1)
        x1 = l1 * np.sin(th1)
        y1 = -l1 * np.cos(th1)

        # Bob 2: (x2, y2)
        x2 = x1 + l2 * np.sin(th2)
        y2 = y1 - l2 * np.cos(th2)

        # Cálculo de energías para verificación hamiltoniana
        t_kin, v_pot, e_tot = self.compute_energy(th1, th2, w1, w2)
        e0 = e_tot[:, 0, None]
        rel_energy_err = np.abs(e_tot - e0) / np.abs(e0)
        max_energy_err = float(np.max(rel_energy_err))

        # Divergencia máxima del enjambre (distancia entre extremos del enjambre)
        # delta_x_max(t) = max_i,j || r2_i(t) - r2_j(t) ||
        # Para el enjambre ordenado por perturbación monotónica: distancia entre péndulo 0 y 49
        r2_x_span = np.max(x2, axis=0) - np.min(x2, axis=0)
        r2_y_span = np.max(y2, axis=0) - np.min(y2, axis=0)
        swarm_span = np.sqrt(r2_x_span**2 + r2_y_span**2)

        # Estimación del exponente de Lyapunov máximo en fase caótica (t > 0)
        # lambda(t) = 1/t * ln( |Delta_X(t)| / |Delta_X(0)| )
        d0 = swarm_span[0]
        with np.errstate(divide="ignore", invalid="ignore"):
            lyapunov_curve = np.where(
                self.t_eval > 0.05,
                (1.0 / self.t_eval) * np.log(np.maximum(swarm_span, 1e-12) / d0),
                0.0
            )

        return {
            "t": self.t_eval,
            "th1": th1,
            "th2": th2,
            "w1": w1,
            "w2": w2,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "energy_kin": t_kin,
            "energy_pot": v_pot,
            "energy_total": e_tot,
            "max_energy_rel_error": max_energy_err,
            "swarm_span": swarm_span,
            "lyapunov_curve": lyapunov_curve,
            "params": self.params,
        }
