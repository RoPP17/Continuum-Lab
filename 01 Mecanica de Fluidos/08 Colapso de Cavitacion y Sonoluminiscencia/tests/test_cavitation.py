"""
Suite de Pruebas Unitarias y Físicas: Continuum Lab // 01 Mecánica de Fluidos
08 Colapso de Cavitación y Sonoluminiscencia (Rayleigh-Plesset & Keller-Miksis Singularity)
"""

import os
import pytest
import numpy as np
import openpyxl
import wave

from src.physics.cavitation_sim import CavitationBubbleSim
from src.physics.export_excel_benchmark import generate_cavitation_excel_benchmark
from src.audio.cavitation_audio import generate_cavitation_audio
from src.visualization.render_cavitation_video import MasterCavitationRenderer


@pytest.fixture
def sim():
    return CavitationBubbleSim()


def test_equilibrium_laplace_young(sim):
    """Verifica la condición de equilibrio mecánico inicial de Laplace-Young."""
    expected_pg0 = sim.p0 + (2.0 * sim.sigma / sim.R0) - sim.pv
    assert np.isclose(sim.pg0, expected_pg0, rtol=1e-5)
    assert sim.pg0 > sim.p0, "La presión interior del gas debe superar la hidrostática por tensión superficial."


def test_rayleigh_collapse_time_scale(sim):
    """Verifica que el tiempo analítico de Rayleigh para cavidad vacía sea físicamente coherente."""
    assert sim.t_rayleigh > 0.0
    # Para R0 = 50 um en agua a 1 atm, t_R ~ 4.5 microsegundos
    assert 1e-6 < sim.t_rayleigh < 1e-4


def test_minnaert_resonance_frequency(sim):
    """Verifica el cálculo de la frecuencia monopolar de Minnaert."""
    assert sim.f_minnaert > 1000.0, "Frecuencia de Minnaert para 50 um debe estar en rango ultrasónico (> 10 kHz)."
    assert sim.omega_minnaert > 0.0


def test_van_der_waals_core_protection(sim):
    """Certifica que el radio de la burbuja nunca colapse por debajo del núcleo duro de van der Waals."""
    assert np.all(sim.R_traj >= sim.h_vdw), "El radio no puede ser menor al volumen de exclusión molecular."
    for t_val in [0.0, 3.0, 7.2, 8.5, 12.0, 16.0]:
        st = sim.get_state(t_val)
        assert st["R"] >= sim.h_vdw


def test_peak_temperature_sonoluminescence(sim):
    """Verifica que el colapso alcance temperaturas extremas de sonoluminiscencia (T > 15,000 K)."""
    max_T = np.max(sim.T_traj)
    assert max_T > 15000.0, f"Temperatura máxima alcanzada fue {max_T:.1f} K, debe superar 15,000 K."
    # Debe ser más caliente que la fotosfera solar (5,778 K)
    assert max_T > 5778.0

    st_sing = sim.get_state(7.20)
    assert st_sing["is_sonoluminescent"] is True
    assert st_sing["SL_intensity"] > 0.8


def test_shockwave_and_microjet_emission(sim):
    """Comprueba la eyección de onda de choque y formación del microjet."""
    st_post = sim.get_state(7.6)
    assert st_post["is_shock_active"] is True
    assert st_post["shock_pressure_bar"] > 500.0
    assert st_post["jet_length_norm"] > 0.0
    assert st_post["jet_speed_mps"] > 500.0


def test_audio_synthesis(tmp_path):
    """Verifica la generación del archivo de audio WAV estéreo de 44.1 kHz."""
    wav_file = tmp_path / "test_cavitation.wav"
    generate_cavitation_audio(str(wav_file), duration=2.0)
    assert os.path.exists(wav_file)

    with wave.open(str(wav_file), "rb") as wf:
        assert wf.getnchannels() == 2
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == 44100
        assert wf.getnframes() == 2 * 44100


def test_excel_benchmark_creation(tmp_path):
    """Comprueba la generación limpia del modelo dinámico Excel."""
    excel_file = tmp_path / "test_benchmark.xlsx"
    generate_cavitation_excel_benchmark(str(excel_file))
    assert os.path.exists(excel_file)

    wb = openpyxl.load_workbook(str(excel_file))
    assert "Resumen y Parámetros" in wb.sheetnames
    assert "Trayectoria Dinamica" in wb.sheetnames
    assert "Fisica de Sonoluminiscencia" in wb.sheetnames

    ws = wb["Resumen y Parámetros"]
    assert str(ws["D21"].value).startswith("=0.91468")


def test_renderer_single_frame():
    """Valida que el renderizador 9:16 compile fotogramas válidos sin excepciones en ES y EN."""
    renderer_es = MasterCavitationRenderer(width=1080, height=1920, lang="ES")
    frame_es = renderer_es.render_frame(t=7.20, frame_idx=432)
    assert frame_es.shape == (1920, 1080, 3)

    renderer_en = MasterCavitationRenderer(width=1080, height=1920, lang="EN")
    frame_en = renderer_en.render_frame(t=7.20, frame_idx=432)
    assert frame_en.shape == (1920, 1080, 3)
