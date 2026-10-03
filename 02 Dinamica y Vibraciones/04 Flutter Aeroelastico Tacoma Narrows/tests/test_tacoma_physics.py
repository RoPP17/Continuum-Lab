"""
Continuum Lab — Test Suite
Module: Aeroelastic Flutter Physics & Scanlan Derivations (Tacoma Narrows)
Division: 02 Dinamica y Vibraciones / 04 Flutter Aeroelastico Tacoma Narrows
"""

import sys
from pathlib import Path
import pytest
import numpy as np

# Ensure project modules are importable
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.physics import (
    TacomaConfig,
    TacomaSolution,
    wind_velocity_profile,
    scanlan_A2_derivative,
    solve_tacoma_dynamics,
)


class TestTacomaFlutterPhysics:
    """Rigorous physical verification of the aeroelastic model."""

    @pytest.fixture
    def config(self) -> TacomaConfig:
        return TacomaConfig()

    @pytest.fixture
    def solution(self, config: TacomaConfig) -> TacomaSolution:
        return solve_tacoma_dynamics(config)

    def test_structural_dimensions_and_inertia(self, config: TacomaConfig):
        """Verify bridge geometry and structural modal properties."""
        assert config.b == 6.0, "Half-width must be 6.0 m (2b = 12.0 m)"
        assert config.D == 2.44, "Girder depth must be 2.44 m (8 ft)"
        assert config.m == 8600.0, "Deck mass must be 8600 kg/m"
        assert config.I_alpha == 1.517e5, "Torsional inertia must match"
        assert config.f_h == 0.20, "Vertical frequency must be 0.20 Hz"
        assert config.f_alpha == 0.20, "Torsional frequency must be 0.20 Hz"
        
        # Check derived stiffnesses
        omega = 2.0 * np.pi * 0.20
        assert np.isclose(config.k_h, 8600.0 * (omega ** 2), rtol=1e-5)
        assert np.isclose(config.k_alpha, 1.517e5 * (omega ** 2), rtol=1e-5)

    def test_wind_velocity_profile(self, config: TacomaConfig):
        """Verify the 3-phase wind velocity profile."""
        # Phase 1: U = 25 km/h
        U_p1 = wind_velocity_profile(2.0, config) * 3.6
        assert np.isclose(U_p1, 25.0, atol=1e-3)

        # Boundary at 4.0s
        U_p1_end = wind_velocity_profile(4.0, config) * 3.6
        assert np.isclose(U_p1_end, 25.0, atol=1e-3)

        # Phase 2 ramp: strictly increasing
        U_mid = wind_velocity_profile(6.25, config) * 3.6
        assert 25.0 < U_mid < 68.0

        # Phase 3: U = 68 km/h
        U_p3 = wind_velocity_profile(10.0, config) * 3.6
        assert np.isclose(U_p3, 68.0, atol=1e-3)

    def test_scanlan_A2_derivative_sign_change(self, config: TacomaConfig):
        """
        Verify that Scanlan's A2* derivative changes sign at U*_crit.
        A2* < 0 for U < U_crit (dissipative)
        A2* > 0 for U > U_crit (self-exciting aerodynamic damping)
        """
        U_crit = config.U_star_crit

        # Below flutter speed: dissipative
        A2_sub = scanlan_A2_derivative(0.5 * U_crit, config)
        assert A2_sub < 0, f"A2* must be negative below U_crit, got {A2_sub}"

        # Exactly at flutter speed: zero
        A2_crit = scanlan_A2_derivative(U_crit, config)
        assert np.isclose(A2_crit, 0.0, atol=1e-6)

        # Above flutter speed: positive self-excitation
        A2_super = scanlan_A2_derivative(1.5 * U_crit, config)
        assert A2_super > 0, f"A2* must be positive above U_crit, got {A2_super}"

    def test_negative_aerodynamic_damping(self, solution: TacomaSolution):
        """Verify that aerodynamic damping reaches negative value zeta_aero = -0.042."""
        # Minimum aerodynamic damping must reach -0.042
        min_zeta = float(np.min(solution.zeta_aero))
        assert np.isclose(min_zeta, -0.042, atol=1e-3), f"Expected -0.042, got {min_zeta}"

        # Total damping during Phase 3 must be strictly negative (unstable)
        p3_mask = solution.phase_idx == 3
        zeta_tot_p3 = solution.zeta_total[p3_mask]
        assert np.all(zeta_tot_p3 < 0), "Total damping must be negative in Phase 3"

    def test_phase1_vertical_vibration_without_torsion(self, solution: TacomaSolution):
        """Verify Phase 1: Pure vertical plunge with negligible torsion."""
        p1_mask = solution.phase_idx == 1
        max_alpha_p1 = np.max(np.abs(solution.alpha_deg[p1_mask]))
        max_h_p1 = np.max(np.abs(solution.h[p1_mask]))

        # Torsion should be tiny (<= 1.0 degrees in phase 1)
        assert max_alpha_p1 <= 1.0, f"Phase 1 torsion should be negligible, got {max_alpha_p1} deg"
        # Plunge should be active (vibrating)
        assert max_h_p1 > 0.05, f"Phase 1 vertical plunge should be active, got {max_h_p1} m"

    def test_phase2_flutter_bifurcation_growth(self, solution: TacomaSolution):
        """Verify Phase 2: Exponential aeroelastic growth and pitch-plunge coupling."""
        p2_mask = solution.phase_idx == 2
        alpha_p2 = np.abs(solution.alpha_deg[p2_mask])

        # Beginning of Phase 2 vs End of Phase 2
        alpha_start = alpha_p2[0]
        alpha_end = alpha_p2[-1]
        assert alpha_end > alpha_start * 5.0, "Phase 2 should exhibit strong aeroelastic amplification"

    def test_phase3_catastrophic_limit_cycle_amplitude(self, solution: TacomaSolution):
        """Verify Phase 3: Catastrophic aeroelastic limit cycle reaches target range (> 35 deg)."""
        p3_mask = solution.phase_idx == 3
        max_alpha_p3 = float(np.max(solution.alpha_deg[p3_mask]))
        min_alpha_p3 = float(np.min(solution.alpha_deg[p3_mask]))

        # Target catastrophic flutter amplitude is in the range of 35-50 degrees
        assert 35.0 <= max_alpha_p3 <= 50.0, f"Expected catastrophic +amplitude in [35, 50] deg, got {max_alpha_p3}"
        assert -50.0 <= min_alpha_p3 <= -35.0, f"Expected catastrophic -amplitude in [-50, -35] deg, got {min_alpha_p3}"


    def test_cable_slackening_and_yielding(self, solution: TacomaSolution, config: TacomaConfig):
        """Verify that cables alternate between slackening (T ~ 0) and yielding (T > T_yield)."""
        p3_mask = solution.phase_idx == 3

        # Both left and right cables must experience yielding in Phase 3
        assert np.any(solution.left_yield[p3_mask]), "Left cable must reach yield threshold in Phase 3"
        assert np.any(solution.right_yield[p3_mask]), "Right cable must reach yield threshold in Phase 3"

        # Both left and right cables must experience slackening in Phase 3
        assert np.any(solution.left_slack[p3_mask]), "Left cable must slacken in Phase 3"
        assert np.any(solution.right_slack[p3_mask]), "Right cable must slacken in Phase 3"

        # Max tension must exceed T_yield
        assert np.max(solution.T_left) > config.T_yield
        assert np.max(solution.T_right) > config.T_yield

    def test_net_aerodynamic_energy_injection(self, solution: TacomaSolution):
        """Verify that aerodynamic work is continuously injected (Delta W > 0)."""
        # Work integral must accumulate positively
        assert solution.work_accum[-1] > solution.work_accum[0], "Work must increase over time"
        assert solution.work_accum[-1] > 1e4, "Significant wind energy must be injected"

    def test_solution_array_consistency_and_framerate(self, solution: TacomaSolution, config: TacomaConfig):
        """Verify array dimensions match 901 points (15s @ 60 FPS) without NaN/Inf."""
        expected_len = int(config.t_total * config.fps) + 1
        assert solution.n_frames == expected_len
        assert len(solution.t) == expected_len
        assert not np.any(np.isnan(solution.alpha)), "Alpha must not contain NaN"
        assert not np.any(np.isinf(solution.alpha)), "Alpha must not contain Inf"
        assert not np.any(np.isnan(solution.h)), "Plunge h must not contain NaN"
