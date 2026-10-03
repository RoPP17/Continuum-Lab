"""
Unit tests for Continuum Lab: Curva Braquistocrona
Verification of Variational Calculus, Boundary Conditions, and Energy Conservation.
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.physics.brachistochrone_models import (
    StraightTrack,
    CycloidTrack,
    ParabolicTrack,
    CircularTrack,
    BrachistochroneSimulator,
)


class TestBrachistochronePhysics:
    @pytest.fixture(autouse=True)
    def setup_tracks(self):
        self.g = 9.81
        self.sim = BrachistochroneSimulator(g=self.g)
        self.expected_v_final = np.sqrt(2.0 * self.g * 7.0)  # ~11.7192 m/s

    def test_boundary_conditions(self):
        """All 4 tracks must strictly start at A(0, 4.0) and end at B(7.0, -3.0)."""
        for key, track in self.sim.tracks.items():
            start_pt = track.get_point_by_param(0.0)
            end_pt = track.get_point_by_param(1.0)
            assert np.isclose(start_pt[0], 0.0, atol=1e-4), f"{track.name} start x failed"
            assert np.isclose(start_pt[1], 4.0, atol=1e-4), f"{track.name} start y failed"
            assert np.isclose(end_pt[0], 7.0, atol=1e-4), f"{track.name} end x failed"
            assert np.isclose(end_pt[1], -3.0, atol=1e-4), f"{track.name} end y failed"

    def test_travel_time_ordering(self):
        """
        Proof of Bernoulli & Euler-Lagrange:
        Cycloid must strictly have the shortest physical travel time among all smooth curves!
        T_cycloid < T_circ < T_parab < T_rect
        """
        t_braq = self.sim.tracks["braq"].physical_travel_time
        t_circ = self.sim.tracks["circ"].physical_travel_time
        t_parab = self.sim.tracks["parab"].physical_travel_time
        t_rect = self.sim.tracks["rect"].physical_travel_time

        assert t_braq < t_circ, f"Cycloid ({t_braq:.4f}) should be faster than circle ({t_circ:.4f})"
        assert t_circ < t_parab, f"Circle ({t_circ:.4f}) should be faster than parabola ({t_parab:.4f})"
        assert t_parab < t_rect, f"Parabola ({t_parab:.4f}) should be faster than straight line ({t_rect:.4f})"

        # Also verify target times order
        tgt_braq = self.sim.tracks["braq"].target_travel_time
        tgt_circ = self.sim.tracks["circ"].target_travel_time
        tgt_parab = self.sim.tracks["parab"].target_travel_time
        tgt_rect = self.sim.tracks["rect"].target_travel_time
        assert tgt_braq < tgt_circ < tgt_parab < tgt_rect == 1.62

    def test_energy_conservation_and_final_speeds(self):
        """
        Conservation of mechanical energy:
        In the absence of friction, all 4 spheres must arrive at point B with the EXACT SAME speed:
        v_final = sqrt(2 * g * Delta_y) = sqrt(2 * 9.81 * 7) = 11.7192 m/s.
        """
        for key, track in self.sim.tracks.items():
            state_start = track.get_state(0.0)
            assert np.isclose(state_start.speed, 0.0, atol=1e-5)

            # At arrival time
            t_finish = track.target_travel_time
            state_end = track.get_state(t_finish)
            assert np.isclose(state_end.speed, self.expected_v_final, atol=1e-3), (
                f"{track.name} final speed mismatch: {state_end.speed:.4f} vs {self.expected_v_final:.4f}"
            )

    def test_brachistochrone_paradox_arc_length(self):
        """
        The geometric paradox:
        Straight line has the MINIMUM Euclidean distance L = 7*sqrt(2) ~ 9.8995 m,
        while Cycloid has a longer trajectory L ~ 10.364 m,
        yet the Cycloid wins the race!
        """
        l_rect = self.sim.tracks["rect"].total_arc_length
        l_braq = self.sim.tracks["braq"].total_arc_length

        assert l_rect < l_braq, f"Straight line arc ({l_rect:.3f}) must be shorter than cycloid ({l_braq:.3f})"
        assert self.sim.tracks["braq"].target_travel_time < self.sim.tracks["rect"].target_travel_time

    def test_kinematic_continuity(self):
        """Test continuous state evaluation with zero NaN or discontinuities."""
        time_samples = np.linspace(0.0, 2.0, 100)
        for t in time_samples:
            states = self.sim.get_all_states(t)
            for key, state in states.items():
                assert not np.isnan(state.x), f"NaN in x for {key} at t={t}"
                assert not np.isnan(state.y), f"NaN in y for {key} at t={t}"
                assert not np.isnan(state.speed), f"NaN in speed for {key} at t={t}"
                assert state.speed >= 0.0, f"Negative speed for {key} at t={t}"
                assert 0.0 <= state.x <= 7.0 + 1e-4
                assert -3.0 - 1e-4 <= state.y <= 4.0 + 1e-4
