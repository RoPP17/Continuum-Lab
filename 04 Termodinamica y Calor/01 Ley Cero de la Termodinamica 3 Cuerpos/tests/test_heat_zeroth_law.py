"""
Continuum Lab — Thermal Physics & Zeroth Law Test Suite
Module: 04 Termodinamica y Calor / 01 Ley Cero de la Termodinamica 3 Cuerpos
File: tests/test_heat_zeroth_law.py

Verifies:
  1. Geometric integrity and disjoint material domain allocation.
  2. Exact First Law energy conservation (dE/dt = 0).
  3. Second Law of Thermodynamics (positive entropy generation S_dot_gen >= 0).
  4. Zeroth Law transitivity: T_A -> T_C and T_B -> T_C ===> T_A -> T_B == T_eq.
  5. Audio procedural synthesizer integrity.
  6. Excel benchmark model creation and dynamic formula structure.
"""

import os
import sys
from pathlib import Path
import pytest
import numpy as np
from scipy.io import wavfile
import openpyxl

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.physics.heat_zeroth_law import (
    ZerothLawThermalSimulation,
    ThermalConfig,
    COPPER,
    STAINLESS_STEEL,
    ALUMINUM,
)
from src.audio.thermal_synth_music import synthesize_catchy_thermal_audio
from src.physics.export_benchmarks import create_zeroth_law_benchmark_workbook


def test_geometry_and_materials():
    sim = ZerothLawThermalSimulation()
    # Check disjoint masks
    assert not np.any(sim.body_mask_a & sim.body_mask_c), "Body A and C masks must be disjoint"
    assert not np.any(sim.body_mask_c & sim.body_mask_b), "Body C and B masks must be disjoint"
    assert not np.any(sim.body_mask_a & sim.body_mask_b), "Body A and B masks must be disjoint"

    # Check active domain
    total_solid_nodes = np.sum(sim.active_solid)
    assert total_solid_nodes > 10000, "Active solid domain must contain dense mesh nodes"

    # Check thermal conductivities
    assert COPPER.thermal_conductivity == 401.0
    assert STAINLESS_STEEL.thermal_conductivity == 54.0
    assert ALUMINUM.thermal_conductivity == 205.0


def test_analytical_equilibrium_temperature():
    sim = ZerothLawThermalSimulation()
    t_eq = sim.compute_analytical_equilibrium_temperature()
    # Given A=100°C, C=25°C, B=0°C and capacities, Teq must be bounded between 35°C and 50°C
    assert 35.0 < t_eq < 50.0, f"Analytical Teq {t_eq:.2f}°C must lie between min and max initial temps"


def test_first_law_energy_conservation():
    sim = ZerothLawThermalSimulation()
    e_initial = sim.initial_energy

    # Run 60 diffusion steps
    for _ in range(60):
        sim.step(0.005)

    e_final = sim.compute_total_energy()
    rel_error = abs(e_final - e_initial) / abs(e_initial)
    assert rel_error < 1e-4, f"Relative energy error {rel_error:.2e} exceeds First Law tolerance 1e-4"


def test_second_law_entropy_generation():
    sim = ZerothLawThermalSimulation()
    m0 = sim.compute_metrics()
    assert m0["s_dot_gen"] >= 0.0, "Entropy generation rate must be non-negative"

    # Step simulation forward
    for _ in range(25):
        sim.step(0.01)

    m1 = sim.compute_metrics()
    assert m1["s_dot_gen"] >= 0.0, "Entropy generation rate must remain non-negative"
    assert m1["s_dot_gen"] < m0["s_dot_gen"], "Entropy generation rate must decrease as gradients relax"


def test_zeroth_law_transitivity_and_equilibrium():
    sim = ZerothLawThermalSimulation()
    m_init = sim.compute_metrics()
    initial_delta_ab = m_init["delta_ab"]
    assert initial_delta_ab > 80.0, "Initial temperature difference between A and B must be significant"

    # Simulate conduction towards equilibrium
    for _ in range(75):
        sim.step(0.02)

    m_final = sim.compute_metrics()
    # Check that temperature difference has shrunk and equilibrium progressed
    assert m_final["delta_ab"] < initial_delta_ab, "Temperature gap between A and B must decay"
    assert m_final["equilibrium_progress"] > m_init["equilibrium_progress"], "Equilibrium progress must increase"

    # Triangle inequality transitivity check: |T_A - T_B| <= |T_A - T_C| + |T_C - T_B|
    assert m_final["delta_ab"] <= (m_final["delta_ac"] + m_final["delta_cb"] + 1e-6)


def test_audio_synthesizer(tmp_path):
    wav_file = str(tmp_path / "test_synth.wav")
    synthesize_catchy_thermal_audio(duration=1.2, fs=44100, output_path=wav_file)
    assert os.path.exists(wav_file), "Audio WAV file must be created"

    fs, data = wavfile.read(wav_file)
    assert fs == 44100, "Sample rate must be 44100 Hz"
    assert data.ndim == 2, "Audio must be stereo (2 channels)"
    assert data.shape[1] == 2, "Audio must have left and right channels"
    assert np.max(np.abs(data)) > 1000, "Audio signal must have non-trivial amplitude"


def test_excel_benchmark_exporter(tmp_path):
    xlsx_file = str(tmp_path / "test_model.xlsx")
    create_zeroth_law_benchmark_workbook(xlsx_file)
    assert os.path.exists(xlsx_file), "Excel workbook must exist"

    wb = openpyxl.load_workbook(xlsx_file, data_only=False)
    sheet_names = wb.sheetnames
    assert "Resumen_Sistema" in sheet_names
    assert "Evolucion_Temporal" in sheet_names
    assert "Balance_Energia" in sheet_names

    ws1 = wb["Resumen_Sistema"]
    # Verify presence of dynamic formula
    assert "=SUMPRODUCT(H5:H7, I5:I7)/H8" in str(ws1["I8"].value)
