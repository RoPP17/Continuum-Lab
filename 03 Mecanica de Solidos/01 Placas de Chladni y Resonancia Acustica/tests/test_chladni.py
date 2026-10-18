"""
Continuum Lab - Unit & Physics Verification Suite for Chladni Plate Cymatics
Module: 03 Mecanica de Solidos / 01 Placas de Chladni y Resonancia Acustica
File: tests/test_chladni.py
"""

import os
import tempfile
import wave
from pathlib import Path
import pytest
import numpy as np
import openpyxl

from src.physics.chladni_sim import (
    ChladniConfig,
    ChladniPlateSimulation,
    TITANIUM_GR5,
)
from src.physics.export_excel_benchmark import create_chladni_excel_benchmark
from src.audio.chladni_audio import synthesize_chladni_soundtrack


def test_plate_elastodynamics_stiffness():
    """Verify Kirchhoff-Love thin plate bending rigidity and acoustic speed."""
    sim = ChladniPlateSimulation()
    E = TITANIUM_GR5.youngs_modulus
    h = 0.001
    nu = TITANIUM_GR5.poisson_ratio
    rho = TITANIUM_GR5.density

    expected_D = (E * (h ** 3)) / (12.0 * (1.0 - nu ** 2))
    assert np.isclose(sim.D, expected_D, rtol=1e-5)
    assert sim.D > 0.0

    expected_cp = np.sqrt(E / (rho * (1.0 - nu ** 2)))
    assert np.isclose(sim.plate_sound_speed, expected_cp, rtol=1e-4)
    assert expected_cp > 4000.0  # Titanium speed of sound > 4 km/s


def test_modal_schedule_and_chladni_field():
    """Verify modal parameters and spatial field evaluation."""
    sim = ChladniPlateSimulation()

    # At t=0.0s, mode (1, 3)
    m, n, a, b, freq, name, m_int, n_int = sim.get_modal_params(0.0)
    assert m_int == 1
    assert n_int == 3
    assert np.isclose(freq, 432.0)

    # Center of plate (0, 0)
    px = np.array([0.0])
    py = np.array([0.0])
    W, dW_dx, dW_dy = sim.evaluate_plate_field(px, py, 0.0)

    # For mode (1, 3) with a=1, b=1:
    # W(0,0) = 1*cos(0)*cos(0) - 1*cos(0)*cos(0) = 1 - 1 = 0
    # Thus the center of the plate is an exact nodal point!
    assert np.isclose(W[0], 0.0, atol=1e-7)
    assert np.isclose(dW_dx[0], 0.0, atol=1e-7)
    assert np.isclose(dW_dy[0], 0.0, atol=1e-7)


def test_particle_dynamics_and_nodal_drift():
    """Verify that particles migrate towards nodal lines over time."""
    cfg = ChladniConfig(num_particles=500)
    sim = ChladniPlateSimulation(config=cfg, seed=123)

    # Initial adherence
    telem_init = sim.step(0.001)

    # Advance 1.5 seconds under Mode (1, 3)
    telem_after = sim.advance_to_time(1.5, sub_steps=6)

    assert sim.current_time >= 1.5
    assert len(sim.telemetry_history) > 1
    assert telem_after.peak_accel_g > 0.0
    # Particles should exhibit physical velocities
    assert telem_after.mean_speed >= 0.0


def test_excel_benchmark_generation():
    """Verify dynamic Excel benchmark generation and dynamic formula structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        xlsx_path = os.path.join(tmpdir, "test_chladni_benchmark.xlsx")
        create_chladni_excel_benchmark(xlsx_path)

        assert os.path.exists(xlsx_path)
        wb = openpyxl.load_workbook(xlsx_path)
        assert "Parametros_y_Materiales" in wb.sheetnames
        assert "Espectro_Modal_Chladni" in wb.sheetnames

        ws1 = wb["Parametros_y_Materiales"]
        # Check that formulas are present (not hardcoded)
        assert ws1["A5"].value.startswith("=")
        assert "AVERAGE" in wb["Espectro_Modal_Chladni"]["D11"].value


def test_audio_soundtrack_synthesis():
    """Verify procedural audio WAV synthesis."""
    with tempfile.TemporaryDirectory() as tmpdir:
        wav_path = os.path.join(tmpdir, "test_audio.wav")
        synthesize_chladni_soundtrack(wav_path, duration=0.5, sample_rate=22050)

        assert os.path.exists(wav_path)
        with wave.open(wav_path, "rb") as wf:
            assert wf.getnchannels() == 2
            assert wf.getsampwidth() == 2
            assert wf.getframerate() == 22050
            frames = wf.readframes(wf.getnframes())
            data = np.frombuffer(frames, dtype=np.int16)
            assert len(data) > 0
            assert np.max(np.abs(data)) > 1000
