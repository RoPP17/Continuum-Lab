"""
Continuum Lab — Verification & Quality Assurance Suite
Physical tests for the Non-Linear Triple Pendulum Integrator.
Division: 02 Dinamica y Vibraciones / 01 Pendulo Triple Caotico
"""

import sys
from pathlib import Path
import numpy as np
import pytest

# Ensure project root is in sys.path
proj_dir = Path(__file__).resolve().parent.parent
if str(proj_dir) not in sys.path:
    sys.path.insert(0, str(proj_dir))

from src.physics.triple_pendulum import TriplePendulumSimulator, TriplePendulumParams


def test_energy_conservation():
    """Verifies that total Hamiltonian mechanical energy is conserved within 0.01% over 5 seconds."""
    sim = TriplePendulumSimulator()
    # High energy release: [120 deg, 90 deg, 45 deg]
    sim.set_initial_state((2.094, 1.571, 0.785), (0.0, 0.0, 0.0))

    initial_energy = sim.total_energy()
    dt = 0.001

    for _ in range(5000):  # 5 seconds of motion
        sim.step_rk4(dt)

    final_energy = sim.total_energy()
    rel_error = abs(final_energy - initial_energy) / abs(initial_energy)

    assert rel_error < 1e-4, f"Energy conservation failed with error: {rel_error:.6e}"


def test_chaotic_divergence_lyapunov():
    """
    Verifies chaotic sensitivity to initial conditions (butterfly effect):
    Two trajectories starting 1e-5 rad apart must diverge exponentially.
    """
    sim1 = TriplePendulumSimulator()
    sim2 = TriplePendulumSimulator()

    th_init = (np.pi / 2.0, np.pi / 2.0, np.pi / 2.0)
    delta = 1e-5

    sim1.set_initial_state(th_init)
    sim2.set_initial_state((th_init[0] + delta, th_init[1], th_init[2]))

    dt = 0.002
    for _ in range(4000):  # 8 seconds
        sim1.step_rk4(dt)
        sim2.step_rk4(dt)

    pos1_p3 = sim1.get_cartesian_positions()[2]
    pos2_p3 = sim2.get_cartesian_positions()[2]

    distance = np.linalg.norm(pos1_p3 - pos2_p3)
    growth_ratio = distance / delta
    # Exponential amplification of initial perturbation: distance / delta >> 1
    assert growth_ratio > 25.0, f"Perturbation failed to amplify exponentially: growth = {growth_ratio:.2f}"


def test_stable_equilibrium_small_oscillations():
    """Verifies small angle oscillations near stable downward equilibrium (0, 0, 0)."""
    sim = TriplePendulumSimulator()
    sim.set_initial_state((0.05, 0.0, 0.0))  # ~2.8 deg

    dt = 0.002
    for _ in range(1000):
        sim.step_rk4(dt)

    th = sim.state[0:3]
    # In small oscillations, angles must remain strictly bounded near 0
    assert np.all(np.abs(th) < 0.2), "Small oscillation bounded test failed"
