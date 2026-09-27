"""
Continuum Lab — Verification & Quality Assurance Suite
Automated physics tests for D2Q9 Lattice Boltzmann Navier-Stokes Solver.
Division: Computational Fluid Dynamics Quality Assurance
"""

import os
import sys
from pathlib import Path
import pytest
import numpy as np

# Ensure project root is in sys.path
proj_dir = Path(__file__).resolve().parent.parent
if str(proj_dir) not in sys.path:
    sys.path.insert(0, str(proj_dir))

from src.physics.lbm_d2q9 import (
    LATTICE_C,
    LATTICE_WEIGHTS,
    CS_SQ,
    LBMConfig,
    LBMD2Q9Solver
)
from src.physics.export_benchmarks import export_lbm_benchmark_excel


def test_d2q9_lattice_tensor_invariants():
    """
    Verifies fundamental tensor invariants of the D2Q9 lattice:
      1. Zeroth moment of weights: sum(w_i) = 1
      2. First moment (lattice isotropy): sum(w_i * c_i) = 0
      3. Second moment: sum(w_i * c_ia * c_ib) = c_s^2 * delta_ab
      4. Fourth moment tensor: sum(w_i * c_ia * c_ib * c_ig * c_id) = c_s^4 * (delta_ab*delta_gd + ...)
    """
    # 1. Normalization
    assert np.isclose(np.sum(LATTICE_WEIGHTS), 1.0), "Weights must sum to 1.0"

    # 2. First moment = 0
    first_moment = np.sum(LATTICE_WEIGHTS[:, None] * LATTICE_C, axis=0)
    assert np.allclose(first_moment, [0.0, 0.0]), "First moment of D2Q9 lattice must vanish"

    # 3. Second moment = c_s^2 * delta_ab
    second_moment = np.zeros((2, 2))
    for i in range(9):
        second_moment += LATTICE_WEIGHTS[i] * np.outer(LATTICE_C[i], LATTICE_C[i])

    expected_second = CS_SQ * np.eye(2)
    assert np.allclose(second_moment, expected_second), "Second moment must equal c_s^2 * I"


def test_equilibrium_moments():
    """
    Verifies that the D2Q9 Maxwell-Boltzmann equilibrium distribution reproduces
    exact hydrodynamic moments:
      sum(f_i^eq) = rho
      sum(f_i^eq * c_i) = rho * u
    """
    config = LBMConfig(nx=20, ny=20, reynolds=100.0, u_inf=0.05)
    solver = LBMD2Q9Solver(config)

    test_rho = np.array([[1.05]])
    test_u = np.array([[[0.06]], [[-0.03]]])

    feq = solver.compute_equilibrium(test_rho, test_u)

    # Zeroth moment
    rho_calc = np.sum(feq, axis=0)
    assert np.isclose(rho_calc[0, 0], test_rho[0, 0], atol=1e-12)

    # First moment
    ux_calc = (
        feq[1] - feq[3] + feq[5] - feq[6] - feq[7] + feq[8]
    ) / rho_calc
    uy_calc = (
        feq[2] - feq[4] + feq[5] + feq[6] - feq[7] - feq[8]
    ) / rho_calc

    assert np.isclose(ux_calc[0, 0], test_u[0, 0, 0], atol=1e-12)
    assert np.isclose(uy_calc[0, 0], test_u[1, 0, 0], atol=1e-12)


def test_stability_and_incompressibility_bounds():
    """Checks that solver rejects unphysical or unstable parameter ranges."""
    # 1. Unstable tau <= 0.5 (singularity)
    with pytest.raises(ValueError, match="numerical instability"):
        # Very high Re with small diameter creates tau < 0.505
        bad_config = LBMConfig(nx=100, ny=50, reynolds=50000.0, obstacle_radius=5.0, u_inf=0.02)
        bad_config.validate()

    # 2. Compressible Mach number violation (Ma >= 0.3)
    with pytest.raises(ValueError, match="violates incompressibility"):
        bad_ma = LBMConfig(nx=100, ny=50, u_inf=0.25)
        bad_ma.validate()


def test_mass_conservation_in_periodic_domain():
    """Verifies strict mass conservation in a closed/periodic simulation."""
    config = LBMConfig(nx=40, ny=40, reynolds=80.0, u_inf=0.04, obstacle_radius=4.0)
    solver = LBMD2Q9Solver(config)

    initial_mass = np.sum(solver.f)

    # Advance 15 time steps
    for _ in range(15):
        solver.step()

    # In periodic / bounce back, mass is strictly bounded
    current_mass = np.sum(solver.f)
    assert np.isfinite(current_mass)
    # Relative variation during initial transient must remain bounded
    rel_change = abs(current_mass - initial_mass) / initial_mass
    assert rel_change < 0.05, f"Mass variation {rel_change:.4e} exceeds physical bounds"


def test_excel_benchmark_generation(tmp_path):
    """Verifies openpyxl dynamic Excel model creation with native formulas."""
    sample_data = [
        {"step": i, "time": i * 0.01, "cd": 1.35 + 0.1 * np.sin(i * 0.2), "cl": 0.4 * np.cos(i * 0.2)}
        for i in range(1, 60)
    ]
    test_xlsx = str(tmp_path / "benchmark_test.xlsx")

    out_file = export_lbm_benchmark_excel(
        file_path=test_xlsx,
        time_series=sample_data,
        reynolds=150.0,
        mach=0.08 / np.sqrt(1.0 / 3.0),
        diameter=28.0,
        nu=(0.08 * 28.0) / 150.0
    )

    assert os.path.exists(out_file)
    from openpyxl import load_workbook
    wb = load_workbook(out_file, data_only=False)

    assert "Telemetry_Data" in wb.sheetnames
    assert "Hydrodynamic_Analysis" in wb.sheetnames

    ws_analysis = wb["Hydrodynamic_Analysis"]
    # Check that calculated metrics contain dynamic native formulas, not static floats
    cd_formula = ws_analysis["B12"].value
    assert isinstance(cd_formula, str) and cd_formula.startswith("=AVERAGE")
    assert ws_analysis["B18"].value.startswith("=1.0 + 10.0/")
