"""
Continuum Lab — Mathematical Physics & Complex Geometry
Unit Tests for Euler 3D Analytical Engine and Projections.
"""

import pytest
import numpy as np
import math
import os
from pathlib import Path
import tempfile

from src.math.euler_math import EulerHelixAnalysis
from src.math.export_euler_excel import export_euler_benchmark_excel


@pytest.fixture
def euler_engine():
    return EulerHelixAnalysis(t_max=4.0 * np.pi, num_points=200)


def test_modulus_is_identically_unity(euler_engine):
    """Verifies |e^{it}| = 1 for all t in [0, 4*pi]."""
    arrays = euler_engine.get_trajectory_arrays()
    moduli = arrays["modulus"]
    assert np.allclose(moduli, 1.0, atol=1e-12), "Modulus of complex exponential must identically equal 1.0"


def test_euler_identity_pi(euler_engine):
    """Verifies Euler's Identity: e^{i*pi} = -1 ==> e^{i*pi} + 1 = 0."""
    p_pi = euler_engine.evaluate_point(math.pi)
    assert math.isclose(p_pi["re"], -1.0, abs_tol=1e-12)
    assert math.isclose(p_pi["im"], 0.0, abs_tol=1e-12)
    assert math.isclose(p_pi["euler_identity_residual"], 0.0, abs_tol=1e-12)


def test_projections_orthogonality(euler_engine):
    """Verifies that projections onto XY and XZ are true orthogonal projections."""
    arrays = euler_engine.get_trajectory_arrays()
    curve_3d = arrays["curve_3d"]
    proj_xy = arrays["proj_xy"]
    proj_xz = arrays["proj_xz"]

    # In XY projection, Z coordinate must be identically 0
    assert np.allclose(proj_xy[:, 2], 0.0, atol=1e-12)
    # In XZ projection, Y coordinate must be identically 0
    assert np.allclose(proj_xz[:, 1], 0.0, atol=1e-12)

    # Difference vector r - P_XY r must be parallel to Z-axis
    diff_xy = curve_3d - proj_xy
    assert np.allclose(diff_xy[:, 0], 0.0, atol=1e-12)
    assert np.allclose(diff_xy[:, 1], 0.0, atol=1e-12)
    assert np.allclose(diff_xy[:, 2], arrays["im"], atol=1e-12)

    # Difference vector r - P_XZ r must be parallel to Y-axis
    diff_xz = curve_3d - proj_xz
    assert np.allclose(diff_xz[:, 0], 0.0, atol=1e-12)
    assert np.allclose(diff_xz[:, 1], arrays["re"], atol=1e-12)
    assert np.allclose(diff_xz[:, 2], 0.0, atol=1e-12)


def test_differential_geometry_helix(euler_engine):
    """
    Verifies Frenet-Serret apparatus for unit circular helix:
    Speed = sqrt(2), Curvature = 0.5, Torsion = 0.5, Orthogonality of T, N, B.
    """
    test_angles = [0.0, 0.5 * math.pi, math.pi, 2.0 * math.pi, 3.14159]
    for th in test_angles:
        diff = euler_engine.differential_properties(th)
        assert math.isclose(diff["speed"], math.sqrt(2.0), abs_tol=1e-12)
        assert math.isclose(diff["curvature"], 0.5, abs_tol=1e-12)
        assert math.isclose(diff["torsion"], 0.5, abs_tol=1e-12)

        # Orthonormal basis
        assert math.isclose(np.dot(diff["tangent"], diff["normal"]), 0.0, abs_tol=1e-12)
        assert math.isclose(np.dot(diff["tangent"], diff["binormal"]), 0.0, abs_tol=1e-12)
        assert math.isclose(np.dot(diff["normal"], diff["binormal"]), 0.0, abs_tol=1e-12)
        assert math.isclose(np.linalg.norm(diff["tangent"]), 1.0, abs_tol=1e-12)
        assert math.isclose(np.linalg.norm(diff["normal"]), 1.0, abs_tol=1e-12)
        assert math.isclose(np.linalg.norm(diff["binormal"]), 1.0, abs_tol=1e-12)


def test_cardinal_landmarks(euler_engine):
    """Verifies the 5 cardinal milestones of Euler's formula."""
    landmarks = euler_engine.key_landmarks()
    assert len(landmarks) == 5

    # 0 -> 1 + 0i
    assert math.isclose(landmarks[0]["re"], 1.0, abs_tol=1e-12)
    assert math.isclose(landmarks[0]["im"], 0.0, abs_tol=1e-12)

    # pi/2 -> 0 + 1i
    assert math.isclose(landmarks[1]["re"], 0.0, abs_tol=1e-12)
    assert math.isclose(landmarks[1]["im"], 1.0, abs_tol=1e-12)

    # pi -> -1 + 0i
    assert math.isclose(landmarks[2]["re"], -1.0, abs_tol=1e-12)
    assert math.isclose(landmarks[2]["im"], 0.0, abs_tol=1e-12)

    # 3pi/2 -> 0 - 1i
    assert math.isclose(landmarks[3]["re"], 0.0, abs_tol=1e-12)
    assert math.isclose(landmarks[3]["im"], -1.0, abs_tol=1e-12)

    # 2pi -> 1 + 0i
    assert math.isclose(landmarks[4]["re"], 1.0, abs_tol=1e-12)
    assert math.isclose(landmarks[4]["im"], 0.0, abs_tol=1e-12)


def test_taylor_convergence(euler_engine):
    """Verifies that increasing order of Taylor expansion decreases error."""
    t_val = 1.0  # 1 radian
    res_ord1 = euler_engine.taylor_approximation(t_val, order=1)
    res_ord3 = euler_engine.taylor_approximation(t_val, order=3)
    res_ord5 = euler_engine.taylor_approximation(t_val, order=5)

    assert res_ord3["cos_error"] < res_ord1["cos_error"]
    assert res_ord5["cos_error"] < res_ord3["cos_error"]
    assert res_ord3["sin_error"] < res_ord1["sin_error"]
    assert res_ord5["sin_error"] < res_ord3["sin_error"]


def test_excel_export():
    """Verifies that the Excel benchmark generation produces a valid .xlsx file."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "test_euler.xlsx"
        export_euler_benchmark_excel(str(tmp_file))
        assert tmp_file.exists()
        assert tmp_file.stat().st_size > 5000  # Non-trivial workbook
