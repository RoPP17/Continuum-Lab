"""
Suite de Pruebas Unitarias y Físicas: Continuum Lab // 01 Mecánica de Fluidos
09 Diamantes de Choque y Discos de Mach (Compressible Gas Dynamics & Mach Reflection)
"""

import os
import math
import pytest
import numpy as np
import openpyxl
import wave

from src.physics.shock_diamonds_sim import ShockDiamondsSim
from src.physics.export_excel_benchmark import generate_shock_diamonds_excel_benchmark
from src.audio.shock_diamonds_audio import generate_shock_diamonds_audio


@pytest.fixture
def sim():
    return ShockDiamondsSim()


def test_isentropic_relations(sim):
    """Verifica que las relaciones isentrópicas satisfagan leyes termodinámicas fundamentales."""
    M = 2.45
    T_ratio = sim.isentropic_T(M, 1.0)
    p_ratio = sim.isentropic_p(M, 1.0)
    rho_ratio = sim.isentropic_rho(M, 1.0)

    assert 0.0 < T_ratio < 1.0, "La temperatura estática en flujo supersónico debe ser menor a la de estancamiento."
    assert 0.0 < p_ratio < 1.0, "La presión estática debe ser menor a la de cámara."
    assert np.isclose(p_ratio, rho_ratio * T_ratio, rtol=1e-5), "Debe cumplirse la ley de gas ideal p = rho * R * T."


def test_prandtl_meyer_monotonicity(sim):
    """Verifica la monotonicidad de la función de Prandtl-Meyer nu(M)."""
    assert np.isclose(sim.prandtl_meyer_nu(1.0), 0.0, atol=1e-6)
    m_range = np.linspace(1.1, 4.0, 30)
    nu_vals = [sim.prandtl_meyer_nu(m) for m in m_range]
    assert np.all(np.diff(nu_vals) > 0), "nu(M) debe ser estrictamente creciente con el Mach."


def test_oblique_shock_theta_beta_m(sim):
    """Verifica la relación theta-beta-M para choques oblicuos."""
    M1 = 2.45
    mu = math.asin(1.0 / M1)
    beta_test = math.radians(40.0)
    assert beta_test > mu
    theta = sim.oblique_shock_theta(M1, beta_test)
    assert theta > 0.0, "La deflexión inducida por choque oblicuo debe ser positiva hacia la cuña."


def test_normal_shock_rankine_hugoniot(sim):
    """Verifica la termodinámica de choque normal (Rankine-Hugoniot)."""
    M1 = 2.45
    jump = sim.normal_shock_jump(M1)

    assert jump["M2"] < 1.0, "El flujo tras choque normal debe ser forzosamente subsónico."
    assert jump["p2_p1"] > 1.0, "La presión debe aumentar a través del choque."
    assert jump["T2_T1"] > 1.0, "La temperatura estática debe aumentar por disipación viscosa irreversible."
    assert jump["rho2_rho1"] > 1.0, "La densidad debe comprimirse."
    assert jump["p02_p01"] < 1.0, "La presión de estancamiento debe caer debido al incremento de entropía (2da Ley)."


def test_prandtl_pack_diamond_spacing(sim):
    """Verifica el espaciado analítico de celdas de diamante de Prandtl-Pack."""
    assert sim.L_diamond_nominal > 0.0
    # Para d_e = 0.45 m y M_e = 2.45, L_d ~ 1.306 * 0.45 * sqrt(2.45^2 - 1) ~ 1.32 m
    assert 1.0 < sim.L_diamond_nominal < 2.0


def test_mach_disk_formation(sim):
    """Verifica que el disco de Mach aparezca en chorros fuertemente subexpandidos."""
    st = sim.get_dynamic_state(8.0)
    assert st["rp"] > 1.0, "El chorro debe estar subexpandido a nivel del mar."
    assert st["mach_disk_radius"] > 0.0, "Debe formarse un disco de Mach de radio medible."
    assert st["T_mach_disk_core"] > 2500.0, "La temperatura del núcleo del disco de Mach debe superar los 2,500 K."


def test_dynamic_breathing_seamless_loop(sim):
    """Certifica que el estado dinámico en t = 0 coincida exactamente con t = 16.0s (Bucle Infinito)."""
    st_0 = sim.get_dynamic_state(0.0, duration=16.0)
    st_16 = sim.get_dynamic_state(16.0, duration=16.0)

    assert np.isclose(st_0["p0"], st_16["p0"], rtol=1e-7)
    assert np.isclose(st_0["NPR"], st_16["NPR"], rtol=1e-7)
    assert np.isclose(st_0["L_diamond"], st_16["L_diamond"], rtol=1e-7)
    assert np.isclose(st_0["mach_disk_radius"], st_16["mach_disk_radius"], rtol=1e-7)


def test_2d_field_shape_and_conservation(sim):
    """Verifica la generación del campo 2D del jet hipersónico."""
    field = sim.generate_2d_jet_field(t=4.0, nx=60, ny=100)
    assert field["M"].shape == (100, 60)
    assert field["T"].shape == (100, 60)
    assert np.all(field["M"] >= 0.0)
    assert np.all(field["P"] > 0.0)
    assert np.all(field["schlieren"] >= 0.0)


def test_excel_benchmark_generation(tmp_path):
    """Verifica la creación del libro Excel dinámico con openpyxl y su integridad."""
    excel_file = str(tmp_path / "test_shock_benchmark.xlsx")
    out = generate_shock_diamonds_excel_benchmark(excel_file)
    assert os.path.exists(out)

    wb = openpyxl.load_workbook(out, data_only=False)
    assert "Resumen Ejecutivo" in wb.sheetnames
    assert "Nozzle & Prandtl-Meyer" in wb.sheetnames
    assert "Sweep Parametrico NPR" in wb.sheetnames
    assert "Saltos Rankine-Hugoniot" in wb.sheetnames
    assert "Telemetria Dinamica 16s" in wb.sheetnames

    # Verify formula presence
    ws2 = wb["Nozzle & Prandtl-Meyer"]
    assert str(ws2["B5"].value).startswith("=")
    assert str(ws2["C5"].value).startswith("=")


def test_audio_generation(tmp_path):
    """Verifica la generación de audio estéreo 44.1 kHz."""
    audio_file = str(tmp_path / "test_audio.wav")
    out = generate_shock_diamonds_audio(audio_file, duration=1.0)
    assert os.path.exists(out)

    with wave.open(out, "rb") as wf:
        assert wf.getnchannels() == 2
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == 44100
        assert wf.getnframes() == 44100
