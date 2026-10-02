"""
Continuum Lab — Classical Mechanics & Dynamical Systems
Division: 02 Dinamica y Vibraciones / 02 Mecanismo Coriolis Collarin
Test Suite: test_coriolis.py

Rigorous automated verification of kinematic constraints,
analytical derivatives, vector orthogonality, and acceleration decomposition.
"""

import sys
from pathlib import Path
import pytest
import numpy as np

# Ensure project root is in sys.path
proj_dir = Path(__file__).resolve().parent.parent
if str(proj_dir) not in sys.path:
    sys.path.insert(0, str(proj_dir))

from src.physics.coriolis_kinematics import CoriolisMechanismParams, CoriolisKinematicsSolver


@pytest.fixture
def standard_solver():
    params = CoriolisMechanismParams(L1=1.0, d=1.5, omega1=2.5, alpha1=0.0)
    return CoriolisKinematicsSolver(params)


@pytest.fixture
def rotating_whitworth_solver():
    # d < L1 -> rotación continua de la barra ranurada 2
    params = CoriolisMechanismParams(L1=1.5, d=0.8, omega1=3.0, alpha1=0.5)
    return CoriolisKinematicsSolver(params)


def test_crank_geometric_constraint(standard_solver):
    """Verifica que el punto A pertenezca exactamente a la circunferencia de radio L1."""
    for th in np.linspace(0, 2 * np.pi, 50, endpoint=False):
        state = standard_solver.solve(th)
        norm_rA = np.linalg.norm(state.r_A - np.array([standard_solver.params.x_O1, standard_solver.params.y_O1]))
        assert np.isclose(norm_rA, standard_solver.params.L1, atol=1e-14)


def test_slotted_arm_loop_closure(standard_solver):
    """Verifica el cierre de lazo geométrico: r_O2 + r2 * u_r2 == r_A."""
    for th in np.linspace(0, 2 * np.pi, 50, endpoint=False):
        state = standard_solver.solve(th)
        reconstructed_A = state.r_O2 + state.r2 * state.u_r2
        assert np.allclose(reconstructed_A, state.r_A, atol=1e-14)


def test_velocity_decomposition(standard_solver):
    """Verifica la descomposición de velocidad relativa v_A = v_rel * u_r + (r2 * w2) * u_theta."""
    for th in np.linspace(0, 2 * np.pi, 50, endpoint=False):
        state = standard_solver.solve(th)
        v_recon = state.v_rel_vec + state.v_transverse_vec
        assert np.allclose(v_recon, state.v_A, atol=1e-14)


def test_coriolis_orthogonality(standard_solver):
    """
    Teorema cinemático: La aceleración de Coriolis a_cor = 2 * (omega x v_rel)
    es estrictamente ortogonal a la dirección de deslizamiento de la barra ranurada.
    """
    for th in np.linspace(0, 2 * np.pi, 50, endpoint=False):
        state = standard_solver.solve(th)
        dot_product = np.dot(state.a_coriolis_vec, state.u_r2)
        assert np.isclose(dot_product, 0.0, atol=1e-14)


def test_acceleration_four_term_decomposition_exact(standard_solver):
    """
    Verifica que la aceleración absoluta a_A sea idéntica a la suma de los 4 términos:
    a_A = a_euler + a_centripetal + a_coriolis + a_rel
    Residual residual_error < 1e-13.
    """
    for th in np.linspace(0, 2 * np.pi, 100, endpoint=False):
        state = standard_solver.solve(th)
        assert state.residual_error < 1e-13
        assert np.allclose(state.a_A, state.a_reconstructed, atol=1e-13)


def test_whitworth_regime_acceleration(rotating_whitworth_solver):
    """Verifica la descomposición en régimen de retorno rápido Whitworth (d < L1)."""
    for th in np.linspace(0, 2 * np.pi, 100, endpoint=False):
        state = rotating_whitworth_solver.solve(th)
        assert state.residual_error < 1e-13


def test_analytical_derivatives_vs_finite_differences(standard_solver):
    """
    Compara las derivadas analíticas (v_rel, omega2, a_rel, alpha2)
    contra diferencias finitas de alta precisión.
    """
    dt = 1e-6
    w1 = standard_solver.params.omega1
    t0 = 0.8523
    th0 = w1 * t0

    state0 = standard_solver.solve(th0, time=t0)
    state_plus = standard_solver.solve(w1 * (t0 + dt), time=t0 + dt)
    state_minus = standard_solver.solve(w1 * (t0 - dt), time=t0 - dt)

    # Derivada primera dr2/dt
    dr2_num = (state_plus.r2 - state_minus.r2) / (2.0 * dt)
    assert np.isclose(dr2_num, state0.v_rel, rtol=1e-7, atol=1e-7)

    # Derivada primera dtheta2/dt
    dth2_num = (state_plus.theta2 - state_minus.theta2) / (2.0 * dt)
    assert np.isclose(dth2_num, state0.omega2, rtol=1e-7, atol=1e-7)

    # Derivada segunda d2r2/dt2
    d2r2_num = (state_plus.r2 - 2.0 * state0.r2 + state_minus.r2) / (dt**2)
    assert np.isclose(d2r2_num, state0.a_rel, rtol=1e-4, atol=1e-4)

    # Derivada segunda d2theta2/dt2
    d2th2_num = (state_plus.theta2 - 2.0 * state0.theta2 + state_minus.theta2) / (dt**2)
    assert np.isclose(d2th2_num, state0.alpha2, rtol=1e-4, atol=1e-4)


def test_cyclic_periodicity(standard_solver):
    """Verifica que el movimiento sea perfectamente periódico y continuo en [0, 2pi]."""
    s_start = standard_solver.solve(0.0)
    s_end = standard_solver.solve(2.0 * np.pi)

    assert np.allclose(s_start.r_A, s_end.r_A, atol=1e-14)
    assert np.allclose(s_start.v_A, s_end.v_A, atol=1e-14)
    assert np.allclose(s_start.a_coriolis_vec, s_end.a_coriolis_vec, atol=1e-14)
    assert np.isclose(s_start.v_rel, s_end.v_rel, atol=1e-14)
    assert np.isclose(s_start.omega2, s_end.omega2, atol=1e-14)
