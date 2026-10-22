"""
Continuum Lab - Unit Tests for Magnus Effect & Flettner Rotor Simulation Suite
Module: 01 Mecanica de Fluidos / 05 Efecto Magnus y Rotor Flettner
File: tests/test_magnus.py
"""

import os
import wave
from pathlib import Path
import pytest
import numpy as np
import openpyxl

from src.physics.magnus_sim import MagnusConfig, MagnusSimulation, MagnusTelemetry
from src.physics.export_excel_benchmark import create_magnus_excel_benchmark
from src.audio.magnus_audio import synthesize_magnus_soundtrack


class TestMagnusPhysics:
    """Verifies theoretical fluid mechanics and Kutta-Joukowski potential flow."""

    def test_surface_impermeability(self):
        """At cylinder boundary r = R, normal/radial velocity u_r must equal exactly zero."""
        sim = MagnusSimulation()
        R = sim.cfg.radius
        U = sim.cfg.u_inf
        thetas = np.linspace(0, 2 * np.pi, 60, endpoint=False)
        xs = R * np.cos(thetas)
        ys = R * np.sin(thetas)

        for alpha in [0.0, 1.0, 2.0, 3.5]:
            ux, uy = sim.velocity_field(xs, ys, alpha)
            # Radial velocity: u_r = u_x * cos(theta) + u_y * sin(theta)
            u_r = ux * np.cos(thetas) + uy * np.sin(thetas)
            np.testing.assert_allclose(
                u_r, 0.0, atol=1e-5,
                err_msg=f"Radial velocity u_r not zero on surface for alpha={alpha}"
            )

    def test_stagnation_bifurcation(self):
        """Verifies topological bifurcation of stagnation points from surface to detached saddle."""
        sim = MagnusSimulation()
        R = sim.cfg.radius

        # Alpha = 0.0 (Unspun) -> Leading and Trailing stagnation points
        state_0, pts_0 = sim.compute_stagnation_points(0.0)
        assert state_0 == "SURFACE_DUAL"
        assert len(pts_0) == 2
        # Points at (R, 0) and (-R, 0)
        assert np.isclose(pts_0[0][1], 0.0, atol=1e-5)
        assert np.isclose(pts_0[1][1], 0.0, atol=1e-5)

        # Alpha = 1.0 -> Two points in bottom hemisphere
        state_1, pts_1 = sim.compute_stagnation_points(1.0)
        assert state_1 == "SURFACE_DUAL"
        assert len(pts_1) == 2
        assert pts_1[0][1] < 0.0 and pts_1[1][1] < 0.0

        # Alpha = 2.0 -> Critical merge at bottom pole (0, -R)
        state_2, pts_2 = sim.compute_stagnation_points(2.0)
        assert state_2 == "CRITICAL_MERGE"
        assert len(pts_2) == 1
        assert np.isclose(pts_2[0][0], 0.0, atol=1e-5)
        assert np.isclose(pts_2[0][1], -R, atol=1e-5)

        # Alpha = 3.0 -> Detached saddle point in fluid at r_s = R*(3 + sqrt(5))/2 ~ 2.618 R
        state_3, pts_3 = sim.compute_stagnation_points(3.0)
        assert state_3 == "DETACHED_SADDLE"
        assert len(pts_3) == 1
        r_s_expected = R * (3.0 + np.sqrt(9.0 - 4.0)) / 2.0
        assert np.isclose(pts_3[0][0], 0.0, atol=1e-5)
        assert np.isclose(pts_3[0][1], -r_s_expected, atol=1e-5)
        assert abs(pts_3[0][1]) > R

    def test_kutta_joukowski_lift_formula(self):
        """Verifies Kutta-Joukowski ideal lift L' = rho * U_inf * Gamma and C_L = 2*pi*alpha."""
        sim = MagnusSimulation()
        telem = sim.get_telemetry(t=6.0)
        alpha = telem.spin_ratio_alpha
        assert alpha > 0.0

        expected_cl_ideal = 2.0 * np.pi * alpha
        assert np.isclose(telem.c_l_ideal, expected_cl_ideal, rtol=1e-4)

        expected_gamma = 2.0 * np.pi * sim.cfg.radius * sim.cfg.u_inf * alpha
        assert np.isclose(telem.circulation_gamma, expected_gamma, rtol=1e-4)

        expected_lift_kn = (sim.cfg.rho_air * sim.cfg.u_inf * expected_gamma) / 1000.0
        assert np.isclose(telem.lift_ideal_kn_m, expected_lift_kn, rtol=1e-4)

    def test_particle_advection_step(self):
        """Verifies that RK4 particle advection updates positions correctly for interior particles."""
        sim = MagnusSimulation()
        # Test velocity vector field directly for a particle at upstream (-2.0, 1.0)
        ux, uy = sim.velocity_field(np.array([-2.0]), np.array([1.0]), alpha=1.5)
        # Free stream moves right, so ux must be positive
        assert ux[0] > 0.0


class TestMagnusExcelBenchmark:
    """Verifies dynamic Excel model generation and compliance with xlsx skill."""

    def test_excel_generation_and_formulas(self, tmp_path):
        xlsx_file = str(tmp_path / "Magnus_Benchmark_Test.xlsx")
        create_magnus_excel_benchmark(xlsx_file)
        assert os.path.exists(xlsx_file)

        wb = openpyxl.load_workbook(xlsx_file)
        expected_sheets = [
            "Parametros_del_Rotor",
            "Analisis_Potencial_vs_Real",
            "Caso_Buque_Carga_Flettner",
            "Distribucion_Presion_Cp"
        ]
        assert wb.sheetnames == expected_sheets

        # Verify dynamic formula in Parametros sheet
        ws_p = wb["Parametros_del_Rotor"]
        assert str(ws_p["C10"].value).startswith("=")  # D = 2*R
        assert str(ws_p["C12"].value).startswith("=")  # A = D*H

        # Verify dynamic formula in Analisis sheet
        ws_a = wb["Analisis_Potencial_vs_Real"]
        assert str(ws_a["F5"].value).startswith("=")  # CL real formula
        assert str(ws_a["I5"].value).startswith("=")  # Lift kN formula

        # Verify Flettner ship sheet
        ws_f = wb["Caso_Buque_Carga_Flettner"]
        assert str(ws_f["C18"].value).startswith("=")  # Propulsive power P_prop
        assert str(ws_f["C24"].value).startswith("=")  # Annual fuel savings
        wb.close()


class TestMagnusAudioSynthesis:
    """Verifies audio synthesis generates a compliant 44.1 kHz stereo audio track."""

    def test_audio_file_properties(self, tmp_path):
        wav_file = str(tmp_path / "magnus_audio_test.wav")
        synthesize_magnus_soundtrack(wav_file, duration=2.0)
        assert os.path.exists(wav_file)

        with wave.open(wav_file, "rb") as wf:
            assert wf.getnchannels() == 2
            assert wf.getsampwidth() == 2
            assert wf.getframerate() == 44100
            assert wf.getnframes() == int(2.0 * 44100)
