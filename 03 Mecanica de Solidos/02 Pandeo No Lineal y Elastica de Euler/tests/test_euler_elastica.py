"""
Suite de Pruebas Unitarias y Verificación Física para la Elástica de Euler.
Ejecutar con: pytest tests/test_euler_elastica.py
"""

import numpy as np
import pytest
from scipy.special import ellipk

from src.physics.euler_elastica_sim import EulerElastica


class TestEulerElastica:
    @pytest.fixture
    def elastica(self):
        return EulerElastica(L=1.0, E=210e9, b=0.02, h=0.003)

    def test_01_critical_load_asymptotic_limit(self, elastica):
        """
        Verifica que cuando el ángulo de deflexión tiende a 0, la carga coincide
        exactamente con la carga crítica lineal de Euler: P_cr = pi^2 * EI / L^2.
        """
        ratio_zero = elastica.load_ratio_from_alpha(0.0)
        assert pytest.approx(ratio_zero, rel=1e-7) == 1.0

        # Pequeña perturbación 0.01 rad (0.57 grados)
        ratio_small = elastica.load_ratio_from_alpha(0.01)
        assert ratio_small > 1.0
        assert ratio_small < 1.0001  # Desviación menor al 0.01%

    def test_02_supercritical_load_capacity_at_90_degrees(self, elastica):
        """
        Para alpha = 90 grados (k = sin(45°) = 1/sqrt(2)), K(0.5) = 1.85407468.
        La relación teórica P / P_cr = (2 * K / pi)^2 = (2 * 1.85407468 / pi)^2 = 1.393164.
        """
        alpha_90 = np.radians(90.0)
        ratio_90 = elastica.load_ratio_from_alpha(alpha_90)
        expected = (2.0 * 1.85407468 / np.pi) ** 2
        assert pytest.approx(ratio_90, rel=1e-5) == expected
        assert pytest.approx(ratio_90, abs=1e-3) == 1.393

    def test_03_monotonic_bifurcation(self, elastica):
        """
        Verifica que la curva de bifurcación sea monótona creciente: a mayor ángulo,
        mayor carga requerida para el equilibrio en régimen elástico.
        """
        angles = np.radians([10.0, 25.0, 45.0, 60.0, 80.0])
        ratios = [elastica.load_ratio_from_alpha(a) for a in angles]
        for i in range(len(ratios) - 1):
            assert ratios[i] < ratios[i + 1]

    def test_04_arc_length_conservation(self, elastica):
        """
        Garantiza que la longitud total del arco s integrado coincida con L (incompresibilidad de arco).
        """
        sol = elastica.solve_exact(np.radians(45.0), num_points=300)
        x = sol["x"]
        y = sol["y"]
        dx = np.diff(x)
        dy = np.diff(y)
        total_length = np.sum(np.sqrt(dx ** 2 + dy ** 2))
        assert pytest.approx(total_length, rel=0.01) == elastica.L

    def test_05_boundary_conditions(self, elastica):
        """
        Verifica los apoyos fijos/articulados: y(0) = 0 y y(L) = 0.
        """
        sol = elastica.solve_exact(np.radians(60.0), num_points=200)
        assert pytest.approx(sol["y"][0], abs=1e-5) == 0.0
        assert pytest.approx(sol["y"][-1], abs=1e-5) == 0.0

    def test_06_maximum_deflection_at_midpoint(self, elastica):
        """
        Por simetría del primer modo de pandeo, la flecha máxima lateral delta_y
        debe ocurrir exactamente en el punto medio x_mid = L_ef / 2.
        """
        sol = elastica.solve_exact(np.radians(50.0), num_points=201)
        mid_idx = len(sol["y"]) // 2
        max_idx = np.argmax(np.abs(sol["y"]))
        assert abs(mid_idx - max_idx) <= 1

    def test_07_stress_increase_with_curvature(self, elastica):
        """
        Comprueba que la tensión máxima en la fibra extrema exterior aumente
        a medida que la curvatura crece con grandes deflexiones.
        """
        sol_low = elastica.solve_exact(np.radians(15.0))
        sol_high = elastica.solve_exact(np.radians(70.0))
        assert sol_high["sigma_max_MPa"] > sol_low["sigma_max_MPa"]
