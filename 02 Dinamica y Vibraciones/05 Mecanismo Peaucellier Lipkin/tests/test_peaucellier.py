"""
Continuum Lab — Verification Test Suite
Module: 02 Dinamica y Vibraciones / 05 Mecanismo Peaucellier Lipkin
File: test_peaucellier.py
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# Ensure src is importable
MODULE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MODULE_ROOT))

from src.kinematics.peaucellier_kinematics import PeaucellierParameters, PeaucellierSolver
from src.audio.peaucellier_audio_synth import synthesize_peaucellier_audio


class TestPeaucellierKinematics:
    @pytest.fixture
    def solver(self):
        params = PeaucellierParameters(
            x_O1=-2.00,
            y_O1=0.0,
            r_crank=0.85,
            R_arm=2.80,
            l_rhombus=1.60,
            omega_crank=0.95
        )
        return PeaucellierSolver(params)

    def test_inversion_constant(self, solver):
        k_expected = 2.80**2 - 1.60**2  # 7.84 - 2.56 = 5.28
        assert np.isclose(solver.params.inversion_constant, k_expected, atol=1e-9)

    def test_theoretical_line_x(self, solver):
        x_exact = -2.00 + 5.28 / (2.0 * 0.85)  # -2.00 + 3.10588235... = 1.10588235...
        assert np.isclose(solver.params.exact_line_x, x_exact, atol=1e-9)

    def test_straightness_error_across_stroke(self, solver):
        thetas = np.linspace(-np.radians(60), np.radians(60), 50)
        exact_x = solver.params.exact_line_x
        
        for th in thetas:
            joints = solver.solve_joint_positions(th)
            Pp = joints["Pp"]
            # Euclidean straight line error must be smaller than 1e-12 mm
            assert np.isclose(Pp[0], exact_x, atol=1e-12), f"Failed at theta={th}: Pp[0]={Pp[0]}, exact={exact_x}"
            assert joints["error_x"] < 1e-12

    def test_rigid_link_constraints(self, solver):
        thetas = [-np.radians(45), -np.radians(20), 0.0, np.radians(20), np.radians(45)]
        R = solver.params.R_arm
        l = solver.params.l_rhombus
        r = solver.params.r_crank
        O1 = solver.params.O1
        O2 = solver.params.O2

        for th in thetas:
            j = solver.solve_joint_positions(th)
            
            # Crank length
            assert np.isclose(np.linalg.norm(j["P"] - O2), r, atol=1e-7)
            # Long arms
            assert np.isclose(np.linalg.norm(j["A"] - O1), R, atol=1e-7)
            assert np.isclose(np.linalg.norm(j["B"] - O1), R, atol=1e-7)
            # Rhombus links
            assert np.isclose(np.linalg.norm(j["A"] - j["P"]), l, atol=1e-7)
            assert np.isclose(np.linalg.norm(j["B"] - j["P"]), l, atol=1e-7)
            assert np.isclose(np.linalg.norm(j["A"] - j["Pp"]), l, atol=1e-7)
            assert np.isclose(np.linalg.norm(j["B"] - j["Pp"]), l, atol=1e-7)

    def test_trajectory_time_history(self, solver):
        t_arr = np.linspace(0, 5.0, 100)
        data = solver.solve_trajectory(t_arr, theta_max_deg=55.0)
        assert len(data["time"]) == 100
        assert np.all(data["error_x"] < 1e-12)
        assert np.max(np.abs(data["Pp_y"])) > 1.5  # Significant vertical excursion


class TestPeaucellierAudio:
    def test_audio_synthesis(self, tmp_path):
        out_wav = tmp_path / "test_audio.wav"
        res = synthesize_peaucellier_audio(duration=2.0, fs=22050, output_path=str(out_wav))
        assert Path(res).exists()
        assert Path(res).stat().st_size > 1000
