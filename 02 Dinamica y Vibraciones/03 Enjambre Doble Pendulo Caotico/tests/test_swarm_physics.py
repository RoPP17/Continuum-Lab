"""
Continuum Lab — Tests de Verificación de Física Computacional
Enjambre de Doble Péndulo Caótico
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import numpy as np
from src.physics.double_pendulum_swarm import SwarmParameters, DoublePendulumSwarmSimulator


@pytest.fixture
def sim_results():
    """Instancia y corre la simulación para los tests."""
    params = SwarmParameters(
        duration=15.0,
        fps=60,
        num_pendulums=50,
        delta_theta=1.0e-6,
    )
    sim = DoublePendulumSwarmSimulator(params)
    return sim.run_simulation()


def test_swarm_dimensions(sim_results):
    """Verifica que las dimensiones del enjambre coincidan exactamente con la especificación."""
    res = sim_results
    assert res["t"].shape == (901,)
    assert res["th1"].shape == (50, 901)
    assert res["th2"].shape == (50, 901)
    assert res["x1"].shape == (50, 901)
    assert res["y1"].shape == (50, 901)
    assert res["x2"].shape == (50, 901)
    assert res["y2"].shape == (50, 901)
    assert res["energy_total"].shape == (50, 901)


def test_initial_conditions(sim_results):
    """Verifica las condiciones iniciales y la perturbación infinitesimal."""
    res = sim_results
    th1_0 = np.radians(120.0)
    th2_0 = np.radians(-60.0)

    for k in range(50):
        expected_th1 = th1_0 + k * 1.0e-6
        assert np.isclose(res["th1"][k, 0], expected_th1, atol=1e-12)
        assert np.isclose(res["th2"][k, 0], th2_0, atol=1e-12)
        assert np.isclose(res["w1"][k, 0], 0.0, atol=1e-12)
        assert np.isclose(res["w2"][k, 0], 0.0, atol=1e-12)


def test_hamiltonian_energy_conservation(sim_results):
    """Garantiza la conservación estricta de la energía hamiltoniana (error relativo < 1e-6)."""
    res = sim_results
    max_err = res["max_energy_rel_error"]
    assert max_err < 1.0e-6, f"Error relativo de energía excesivo: {max_err}"


def test_chaotic_divergence_phases(sim_results):
    """Verifica las 3 fases dinámicas: orden aparente, bifurcación y explosión caótica."""
    res = sim_results
    span = res["swarm_span"]

    # t = 0 s (frame 0): enjambre infinitesimalmente agrupado
    assert span[0] < 1.0e-4

    # t = 5.5 s (frame 330): orden aparente (separación milimétrica)
    assert span[330] < 1.0e-2

    # t = 15.0 s (frame 900): divergencia caótica macroscópica masiva (> 4 metros)
    assert span[900] > 4.0


def test_geometric_safe_bounds(sim_results):
    """Verifica que los extremos no sobrepasen las dimensiones de la pantalla vertical 9:16."""
    res = sim_results
    x2 = res["x2"]
    y2 = res["y2"]

    scale = 1.30
    pivot_y = 0.65

    screen_x = x2 * scale
    screen_y = pivot_y + y2 * scale

    # La pantalla 9:16 tiene X en [-4.5, 4.5]
    assert np.all(screen_x >= -4.2)
    assert np.all(screen_x <= 4.2)

    # Las safe zones dejan libre Y entre -5.4 y +5.3
    assert np.all(screen_y >= -5.2)
    assert np.all(screen_y <= 5.2)
