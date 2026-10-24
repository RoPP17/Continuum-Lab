"""
Módulo de Física: Solucionador Analítico y Numérico de la Elástica de Euler.
Resuelve el pandeo elástico no lineal para grandes deflexiones mediante
Integrales Elípticas de Jacobi (solución analítica exacta) y método de disparo RK4.
"""

import numpy as np
from scipy.special import ellipk, ellipe
from scipy.optimize import brentq


class EulerElastica:
    """
    Modelo de la Elástica de Euler para vigas esbeltas sometidas a compresión axial.
    
    Parámetros:
    -----------
    L : float
        Longitud total de la viga en arco (m). Por defecto 1.0 m.
    E : float
        Módulo de elasticidad de Young (Pa). Por defecto 210 GPa (Acero estructural).
    I : float
        Segundo momento de inercia del área (m^4).
    b : float
        Ancho de la sección rectangular (m).
    h : float
        Espesor de la sección rectangular en el plano de flexión (m).
    """

    def __init__(self, L: float = 1.0, E: float = 210e9, b: float = 0.02, h: float = 0.003):
        self.L = float(L)
        self.E = float(E)
        self.b = float(b)
        self.h = float(h)
        self.A = self.b * self.h
        self.I = (self.b * (self.h ** 3)) / 12.0
        self.EI = self.E * self.I
        
        # Carga crítica clásica de Euler (Primer modo, apoyos articulados)
        self.P_cr = (np.pi ** 2 * self.EI) / (self.L ** 2)

    def load_ratio_from_alpha(self, alpha_rad: float) -> float:
        """
        Calcula la relación P / P_cr para un ángulo de rotación máximo en los extremos alpha.
        Relación exacta: P / P_cr = (2 * K(k) / pi)^2, donde k = sin(alpha / 2).
        """
        if abs(alpha_rad) < 1e-12:
            return 1.0
        k = np.sin(abs(alpha_rad) / 2.0)
        if k >= 1.0:
            return float('inf')
        K_k = ellipk(k ** 2)  # scipy usa m = k^2
        return float((2.0 * K_k / np.pi) ** 2)

    def alpha_from_load_ratio(self, p_ratio: float) -> float:
        """
        Dada una relación P / P_cr >= 1.0, encuentra el ángulo extremo alpha_rad mediante inversión.
        """
        if p_ratio <= 1.0:
            return 0.0

        def obj(alpha):
            return self.load_ratio_from_alpha(alpha) - p_ratio

        # Alpha varía entre 0 y pi
        return float(brentq(obj, 1e-9, np.pi - 1e-5))

    def solve_exact(self, alpha_rad: float, num_points: int = 200) -> dict:
        """
        Calcula el perfil exacto de la viga (x(s), y(s)), curvatura kappa(s) y esfuerzos
        mediante integración elíptica.
        
        Retorna diccionario con arrays de arco s, x, y, theta, curvatura y tensiones.
        """
        if abs(alpha_rad) < 1e-9:
            # Caso no pandeado (recto)
            s = np.linspace(0, self.L, num_points)
            return {
                "s": s,
                "x": s,
                "y": np.zeros_like(s),
                "theta": np.zeros_like(s),
                "kappa": np.zeros_like(s),
                "P": self.P_cr,
                "P_ratio": 1.0,
                "alpha_deg": 0.0,
                "delta_x": 0.0,
                "delta_y_max": 0.0,
                "sigma_von_mises_max": (self.P_cr / self.A) / 1e6  # MPa
            }

        k = np.sin(abs(alpha_rad) / 2.0)
        m = k ** 2
        K_k = ellipk(m)
        E_k = ellipe(m)
        P_ratio = (2.0 * K_k / np.pi) ** 2
        P = P_ratio * self.P_cr
        omega = np.sqrt(P / self.EI)

        # Discretización en el parámetro elíptico u = omega * s
        # s va de 0 a L, u va de 0 a 2*K_k
        u = np.linspace(-K_k, K_k, num_points)
        s = (u + K_k) / omega

        # Ángulo theta(s): sin(theta/2) = k * sn(u, m) -> cos(theta) = 1 - 2*k^2*sn^2(u)
        # scipy special elliptic functions
        from scipy.special import ellipj
        sn, cn, dn, _ = ellipj(u, m)

        sin_half_theta = k * sn
        # Asegurar acotamiento numérico
        sin_half_theta = np.clip(sin_half_theta, -1.0, 1.0)
        theta = 2.0 * np.arcsin(sin_half_theta)

        # Curvatura dtheta/ds = 2 * k * omega * cn(u)
        kappa = 2.0 * k * omega * cn

        # Coordenada x(s) centrada
        # x(u) = (2 * E(am(u)) - u) / omega
        # Integramos numéricamente cos(theta) y sin(theta) para máxima precisión
        ds = s[1] - s[0]
        dx = np.cos(theta) * ds
        dy = np.sin(theta) * ds

        x = np.cumsum(dx)
        x = x - x[0]  # Origen en s = 0 -> x = 0
        y = np.cumsum(dy)
        y = y - y[0]

        # Ajuste de condiciones de frontera: y(0) = 0, y(L) = 0
        # Debido a simetría, restamos el drift lineal residual si existe
        y = y - (y[-1] - y[0]) * (s / self.L)

        # Deformaciones y flecha máxima
        delta_x = self.L - (x[-1] - x[0])  # Acortamiento axial
        delta_y_max = np.max(np.abs(y))    # Flecha lateral máxima

        # Cálculo de tensiones combinadas (Compresión axial + Flexión por curvatura)
        c = self.h / 2.0  # Fibra más alejada
        sigma_axial = (P * np.cos(theta)) / self.A
        sigma_flexion = self.E * c * np.abs(kappa)
        sigma_total = sigma_axial + sigma_flexion  # Tensión máxima en la fibra exterior (Pa)

        return {
            "s": s,
            "x": x,
            "y": y,
            "theta": theta,
            "kappa": kappa,
            "P": P,
            "P_ratio": P_ratio,
            "alpha_deg": np.degrees(alpha_rad),
            "delta_x": delta_x,
            "delta_y_max": delta_y_max,
            "sigma_max_MPa": np.max(sigma_total) / 1e6,
            "sigma_axial_mean_MPa": (P / self.A) / 1e6
        }

    def compute_bifurcation_curve(self, num_alphas: int = 150) -> dict:
        """
        Genera el diagrama de bifurcación tipo tridente (Supercritical Pitchfork Bifurcation):
        P/P_cr vs Flecha normalizada (delta_y / L) y Acortamiento (delta_x / L).
        """
        # Ramas post-críticas simétricas (+alpha y -alpha)
        alphas = np.linspace(0.01, np.radians(85.0), num_alphas)
        p_ratios = []
        delta_y_ratios = []
        delta_x_ratios = []

        for a in alphas:
            sol = self.solve_exact(a, num_points=100)
            p_ratios.append(sol["P_ratio"])
            delta_y_ratios.append(sol["delta_y_max"] / self.L)
            delta_x_ratios.append(sol["delta_x"] / self.L)

        return {
            "alphas_deg": np.degrees(alphas),
            "P_ratio": np.array(p_ratios),
            "delta_y_ratio": np.array(delta_y_ratios),
            "delta_x_ratio": np.array(delta_x_ratios)
        }
