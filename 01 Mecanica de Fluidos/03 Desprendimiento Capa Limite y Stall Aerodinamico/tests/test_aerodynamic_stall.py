"""
Continuum Lab — Verification & Unit Test Suite
Module: 01 Mecanica de Fluidos / 03 Desprendimiento Capa Limite y Stall Aerodinamico
Physics & Mathematics Test Engine
"""

import os
import pytest
import numpy as np
from pathlib import Path
import openpyxl

from src.physics.aerodynamic_stall import AerodynamicStallSimulation, AirfoilParameters
from src.physics.export_benchmarks import create_stall_benchmark_workbook
from src.audio.stall_audio_synth import synthesize_stall_audio


@pytest.fixture
def sim():
    return AerodynamicStallSimulation()


def test_naca_airfoil_geometry(sim):
    """
    Validates NACA 0012 geometry:
    - Chord normalization [0, 1]
    - Maximum thickness t/c = 0.12 near 30% chord
    - Symmetry around chord line
    """
    xc = np.linspace(0.0, 1.0, 100)
    yt = sim.naca_thickness(xc)

    # Thickness at leading edge must be 0
    assert np.isclose(yt[0], 0.0, atol=1e-5)
    # Trailing edge near zero
    assert yt[-1] < 0.005

    # Maximum thickness location (~30% chord)
    max_idx = np.argmax(yt)
    assert 0.25 <= xc[max_idx] <= 0.35
    # Maximum semi-thickness should be t/2 = 0.06
    assert np.isclose(np.max(yt), 0.06, atol=0.005)

    # Check closed polygon coordinates
    x_poly, y_poly = sim.get_airfoil_polygon(n_points=120)
    assert len(x_poly) == 120
    assert np.all(x_poly >= -1e-6) and np.all(x_poly <= 1.0 + 1e-6)


def test_thin_airfoil_theory_lift_slope(sim):
    """
    Verifies thin airfoil theory:
      C_L = 2*pi*(alpha - alpha_0)
      dC_L/d(alpha) = 2*pi rad^-1 ~ 0.1097 deg^-1
    """
    cl_0 = sim.thin_airfoil_lift(0.0)
    assert np.isclose(cl_0, 0.0, atol=1e-6)

    cl_4 = sim.thin_airfoil_lift(4.0)
    expected_cl_4 = 2.0 * np.pi * np.radians(4.0)
    assert np.isclose(cl_4, expected_cl_4, atol=1e-5)
    assert np.isclose(cl_4, 0.4386, atol=1e-3)


def test_aerodynamic_stall_collapse(sim):
    """
    Verifies that:
      1. At alpha = 4 deg: C_L ~ 0.44 (linear thin airfoil regime)
      2. At alpha = 15.5 deg: C_L reaches maximum peak ~ 1.55
      3. At alpha = 18.5 deg: C_L collapses by exactly 74% down to ~ 0.403
    """
    cl_4 = sim.lift_coefficient(4.0)
    assert np.isclose(cl_4, 0.4386, atol=0.01)

    cl_stall = sim.lift_coefficient(15.5)
    assert np.isclose(cl_stall, 1.55, atol=0.01)

    cl_18 = sim.lift_coefficient(18.5)
    expected_cl_18 = 1.55 * (1.0 - 0.74)  # 0.403
    assert np.isclose(cl_18, expected_cl_18, atol=0.01)

    # Relative collapse calculation
    collapse_pct = (cl_stall - cl_18) / cl_stall
    assert np.isclose(collapse_pct, 0.74, atol=0.005)


def test_drag_polar_explosion(sim):
    """
    Verifies drag divergence and stall buffet drag surge:
      - Low attached drag at alpha = 4 deg: C_D < 0.025
      - Exploding form drag at alpha = 18.5 deg: C_D > 0.25 (>14x increase)
    """
    cd_4 = sim.drag_coefficient(4.0)
    cd_18 = sim.drag_coefficient(18.5)

    assert cd_4 < 0.025
    assert cd_18 > 0.250
    drag_surge_ratio = cd_18 / cd_4
    assert drag_surge_ratio > 14.0


def test_boundary_layer_separation_progression(sim):
    """
    Verifies that separation location x_sep / c progresses upstream:
      - Fully attached at alpha <= 6 deg (x_sep/c = 1.0)
      - Advances forward as alpha increases
      - Reaches ~ 15% chord at deep stall alpha = 18.5 deg
    """
    assert sim.separation_point(4.0) == 1.0
    assert sim.separation_point(6.0) == 1.0

    x_sep_10 = sim.separation_point(10.0)
    assert 0.70 < x_sep_10 < 0.95

    x_sep_15 = sim.separation_point(15.5)
    assert 0.25 < x_sep_15 < 0.50

    x_sep_18 = sim.separation_point(18.5)
    assert np.isclose(x_sep_18, 0.15, atol=0.02)


def test_pohlhausen_separation_criterion(sim):
    """
    Verifies Pohlhausen boundary layer velocity profile and wall shear condition:
      (d(u/U_e)/d(eta))|_0 = 2 + Lambda / 6
      - Lambda = 0   => Slope = +2.0 (Blasius)
      - Lambda = -12 => Slope = 0.0  (Boundary layer separation point: tau_w = 0)
      - Lambda = -15 => Slope = -0.5 (Reverse flow / recirculation)
    """
    eta = np.linspace(0.0, 1.0, 500)
    d_eta = eta[1] - eta[0]

    # 1. Lambda = 0 (Attached)
    u_0 = sim.pohlhausen_velocity_profile(eta, lambda_param=0.0)
    wall_slope_0 = (u_0[1] - u_0[0]) / d_eta
    assert np.isclose(wall_slope_0, 2.0, atol=0.01)

    # 2. Lambda = -12 (Separation point)
    u_sep = sim.pohlhausen_velocity_profile(eta, lambda_param=-12.0)
    wall_slope_sep = (u_sep[1] - u_sep[0]) / d_eta
    assert np.isclose(wall_slope_sep, 0.0, atol=0.02)

    # 3. Lambda = -15 (Separated backflow)
    u_rev = sim.pohlhausen_velocity_profile(eta, lambda_param=-15.0)
    wall_slope_rev = (u_rev[1] - u_rev[0]) / d_eta
    assert wall_slope_rev < -0.3
    # Check that velocity is negative near the wall
    assert np.any(u_rev[1:10] < 0.0)


def test_pressure_gradient_adverse(sim):
    """
    Verifies that upper surface exhibits an adverse pressure gradient (dp/dx > 0)
    downstream of the suction peak.
    """
    cp_dict = sim.pressure_distribution(18.5, n_points=50)
    dcp_dx = cp_dict["dcp_dx"]
    xc = cp_dict["xc"]

    # Past the leading edge suction peak (x/c > 0.10), dCp/dx must be positive (adverse)
    downstream_mask = (xc > 0.15) & (xc < 0.85)
    assert np.all(dcp_dx[downstream_mask] >= 0.0)


def test_excel_benchmark_generation(tmp_path):
    """
    Verifies dynamic Excel benchmark file structure:
      - Valid openpyxl file
      - 4 designated sheets
      - Dynamic formulas present
    """
    bench_file = tmp_path / "test_benchmark.xlsx"
    create_stall_benchmark_workbook(str(bench_file))

    assert bench_file.exists()
    wb = openpyxl.load_workbook(str(bench_file))
    expected_sheets = [
        "KPIs & Parametros",
        "Polar Aerodinamica (Alpha)",
        "Gradiente Presion Cp(x)",
        "Perfil Capa Limite Pohlhausen"
    ]
    assert wb.sheetnames == expected_sheets

    # Verify formula existence in Sheet 1
    ws1 = wb["KPIs & Parametros"]
    assert str(ws1["C10"].value).startswith("=")
    assert "Polar Aerodinamica" in str(ws1["B16"].value)
    assert "Polar Aerodinamica" in str(ws1["D16"].value)
    assert str(ws1["E16"].value) == "=(D16-C16)/C16"


def test_audio_synthesis(tmp_path):
    """
    Verifies aero-acoustic synthesizer output:
      - Valid WAV file written
      - Exact 2-channel stereo
      - No infinities or NaNs
    """
    audio_path = tmp_path / "test_stall_audio.wav"
    synthesize_stall_audio(duration=2.0, fs=22050, output_path=str(audio_path))

    assert audio_path.exists()
    import scipy.io.wavfile as wf
    rate, data = wf.read(str(audio_path))
    assert rate == 22050
    assert data.shape[1] == 2
    assert len(data) == int(2.0 * 22050)
    assert not np.isnan(data).any()
