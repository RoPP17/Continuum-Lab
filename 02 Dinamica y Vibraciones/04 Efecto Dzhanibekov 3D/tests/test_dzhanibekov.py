"""
Continuum Lab — Classical Mechanics & Dynamical Systems
Division: 02 Dinamica y Vibraciones / 04 Efecto Dzhanibekov 3D
Unit Tests: Euler Torque-Free Rigid Body Dynamics & Conservation Laws
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Ensure package root is in sys.path
pkg_root = Path(__file__).resolve().parent.parent
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

from src.physics.euler_rigid_body import RigidBodyParams, RigidBodySimulator


class TestEulerRigidBodyDynamics:

    @pytest.fixture
    def sim_results(self):
        params = RigidBodyParams(I1=1.0, I2=2.4, I3=4.2)
        sim = RigidBodySimulator(params)
        res = sim.simulate(t_span=(0.0, 14.0), fps=60, method="DOP853")
        return sim, res

    def test_principal_moments_ordering(self):
        """Verifies strict intermediate axis condition: I1 < I2 < I3."""
        params = RigidBodyParams(I1=1.0, I2=2.4, I3=4.2)
        assert params.I1 < params.I2 < params.I3

        # Hyperbolic eigenvalue coefficient around intermediate axis must be positive
        coeff_intermediate = (params.I2 - params.I3) * (params.I1 - params.I2) / (params.I1 * params.I3)
        assert coeff_intermediate > 0, "Intermediate axis must be dynamically unstable!"

        # Centers around minor and major axes must be negative
        coeff_minor = (params.I1 - params.I2) * (params.I3 - params.I1) / (params.I2 * params.I3)
        coeff_major = (params.I3 - params.I1) * (params.I2 - params.I3) / (params.I1 * params.I2)
        assert coeff_minor < 0, "Minor axis must be elliptic (stable center)!"
        assert coeff_major < 0, "Major axis must be elliptic (stable center)!"

    def test_conservation_of_energy(self, sim_results):
        """Verifies rotational kinetic energy conservation to ultra-high precision."""
        sim, res = sim_results
        drift = res["rel_energy_drift"]
        assert drift < 1e-9, f"Energy drift too high: {drift}"

    def test_conservation_of_angular_momentum_magnitude(self, sim_results):
        """Verifies magnitude of angular momentum is conserved."""
        sim, res = sim_results
        drift = res["rel_momentum_drift"]
        assert drift < 1e-9, f"Angular momentum magnitude drift too high: {drift}"

    def test_conservation_of_space_angular_momentum_vector(self, sim_results):
        """Verifies vector L_s stays strictly stationary in inertial space frame."""
        sim, res = sim_results
        space_drift = res["space_momentum_drift"]
        assert space_drift < 1e-8, f"Space angular momentum vector drift too high: {space_drift}"

    def test_dzhanibekov_flips_timing(self, sim_results):
        """Verifies the occurrence and timing of 180-degree flips."""
        sim, res = sim_results
        t = res["time"]
        w2 = res["omega_body"][:, 1]

        # Find zero crossings
        cross_idx = np.where(np.diff(np.signbit(w2)))[0]
        assert len(cross_idx) >= 2, "Must undergo at least two flips in 14 seconds!"

        flip1_time = t[cross_idx[0]]
        flip2_time = t[cross_idx[1]]

        # Flip 1 should occur within [3.5, 5.0]s
        assert 3.5 <= flip1_time <= 5.0, f"Flip 1 outside expected window: {flip1_time:.2f}s"
        # Flip 2 should occur within [8.5, 10.0]s
        assert 8.5 <= flip2_time <= 10.0, f"Flip 2 outside expected window: {flip2_time:.2f}s"

    def test_quaternion_orthogonality(self, sim_results):
        """Verifies all rotation matrices R(q) are strictly orthogonal."""
        sim, res = sim_results
        rot_matrices = res["rot_matrices"]

        # Sample 20 random frames
        sample_indices = np.linspace(0, len(rot_matrices) - 1, 20, dtype=int)
        identity = np.eye(3)

        for idx in sample_indices:
            R = rot_matrices[idx]
            err = np.max(np.abs(R.T @ R - identity))
            assert err < 1e-12, f"Rotation matrix not orthogonal at frame {idx}: err={err}"
            det = np.linalg.det(R)
            assert np.isclose(det, 1.0, atol=1e-12), f"Determinant of R not 1.0: det={det}"
