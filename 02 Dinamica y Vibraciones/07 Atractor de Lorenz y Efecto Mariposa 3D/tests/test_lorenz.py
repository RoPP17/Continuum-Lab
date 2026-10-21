"""
Continuum Lab - Unit & Mathematical Verification Suite for 3D Lorenz Strange Attractor
Module: 02 Dinamica y Vibraciones / 07 Atractor de Lorenz y Efecto Mariposa 3D
File: tests/test_lorenz.py
"""

import os
import tempfile
import wave
import numpy as np
import openpyxl

from src.physics.lorenz_sim import (
    LorenzConfig,
    LorenzSimulation,
)
from src.physics.export_excel_benchmark import create_lorenz_excel_benchmark
from src.audio.lorenz_audio import synthesize_lorenz_soundtrack


def test_fixed_points_equilibrium_exactness():
    """
    Verify that the origin O(0,0,0) and convective wing centers C_± = (±sqrt(β(ρ-1)), ±sqrt(β(ρ-1)), ρ-1)
    have identically zero time derivatives F(x,y,z) = 0.
    """
    sim = LorenzSimulation()
    f_origin = sim.derivatives(sim.fixed_point_origin)
    f_plus = sim.derivatives(sim.fixed_point_plus)
    f_minus = sim.derivatives(sim.fixed_point_minus)

    assert np.allclose(f_origin, 0.0, atol=1e-12)
    assert np.allclose(f_plus, 0.0, atol=1e-12)
    assert np.allclose(f_minus, 0.0, atol=1e-12)


def test_liouville_contraction_and_kaplan_yorke_dimension():
    """
    Verify dissipative phase-volume contraction ∇·F = -(σ + 1 + β) = -41/3
    and Kaplan-Yorke fractal dimension D_KY ≈ 2.0621.
    """
    sim = LorenzSimulation()
    expected_div = -(10.0 + 1.0 + 8.0 / 3.0)
    assert np.isclose(sim.liouville_div, expected_div, atol=1e-10)
    assert sim.liouville_div < 0.0
    assert 2.05 < sim.kaplan_yorke < 2.08


def test_butterfly_divergence_and_opposite_wings():
    """
    Verify that twin orbits A and B start micro-separated and diverge onto opposite wings C_- and C_+.
    """
    sim = LorenzSimulation()
    telem_init = sim.step(0.01)
    assert telem_init.euclidean_divergence < 0.5

    # Advance to t = 7.5s where saddle bifurcation has separated A and B
    saw_opposite_wings = False
    max_div = 0.0
    for t_step in np.linspace(1.0, 10.0, 45):
        telem = sim.advance_to_time(float(t_step))
        max_div = max(max_div, telem.euclidean_divergence)
        if telem.opposite_wings:
            saw_opposite_wings = True

    assert saw_opposite_wings
    assert max_div > 12.0


def test_excel_benchmark_dynamic_formulas():
    """
    Verify that the Excel benchmark file generates cleanly and uses dynamic Excel formulas.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        xlsx_path = os.path.join(tmpdir, "test_lorenz_benchmark.xlsx")
        create_lorenz_excel_benchmark(xlsx_path)

        assert os.path.exists(xlsx_path)
        wb = openpyxl.load_workbook(xlsx_path)
        assert "Parametros_Invariantes_Lorenz" in wb.sheetnames
        assert "Divergencia_Lyapunov_1963" in wb.sheetnames

        ws1 = wb["Parametros_Invariantes_Lorenz"]
        assert str(ws1["A5"].value).startswith("=")
        assert str(ws1["D12"].value).startswith("=")
        assert "SQRT" in str(ws1["D14"].value)

        ws2 = wb["Divergencia_Lyapunov_1963"]
        assert "EXP" in str(ws2["B6"].value)
        assert "MIN" in str(ws2["D6"].value)


def test_binaural_audio_synthesis():
    """
    Verify 44.1 kHz stereo WAV generation.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = os.path.join(tmpdir, "test_lorenz_audio.wav")
        synthesize_lorenz_soundtrack(wav_path, duration=0.6, sample_rate=22050)

        assert os.path.exists(wav_path)
        with wave.open(wav_path, "rb") as wf:
            assert wf.getnchannels() == 2
            assert wf.getsampwidth() == 2
            assert wf.getframerate() == 22050
            data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
            assert len(data) > 0
            assert np.max(np.abs(data)) > 1500
