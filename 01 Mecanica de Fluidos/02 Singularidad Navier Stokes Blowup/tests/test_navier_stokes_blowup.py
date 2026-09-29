"""
Continuum Lab — Unit Tests for Navier-Stokes Finite-Time Singularity Physics
Verifies scaling exponents, anisotropic contraction, velocity divergence,
finite kinetic energy bound, annular stress support, and pressure balance.
"""

import pytest
import numpy as np
from src.physics.navier_stokes_blowup import NavierStokesBlowupSimulation, BlowupParameters


@pytest.fixture
def sim():
    return NavierStokesBlowupSimulation()


def test_scaling_exponents(sim):
    """Verifies that the exponents conform to the paper constraints."""
    assert 0.0 < sim.params.h < 0.01, "Exponent h must be in (0, 0.01)"
    assert sim.params.A == 0.5 + sim.params.h
    assert sim.params.D == 0.5 - sim.params.h
    assert np.isclose(sim.params.A + sim.params.D, 1.0)


def test_concentration_scale_q(sim):
    """Verifies Newton solver for q(z, tau) on and off the axis."""
    tau = 0.04
    q_axis = sim.solve_concentration_scale_q(0.0, tau)
    assert np.isclose(q_axis, tau, atol=1e-6), "At z=0, q must equal tau"

    z_vals = np.array([0.0, 0.1, 0.5])
    q_vals = sim.solve_concentration_scale_q(z_vals, tau)
    assert np.all(q_vals > 0), "q must be strictly positive"
    assert q_vals[1] > q_vals[0], "q must increase with |z|"
    assert q_vals[2] > q_vals[1]


def test_anisotropic_needle_contraction(sim):
    """Verifies that the core contracts faster radially than axially (slender needle)."""
    m1 = sim.length_scales(t=0.0)
    m2 = sim.length_scales(t=0.9)
    m3 = sim.length_scales(t=0.999)

    assert m3["l_r"] < m2["l_r"] < m1["l_r"], "Radial radius must shrink"
    assert m3["l_z"] < m2["l_z"] < m1["l_z"], "Axial height must shrink"
    assert m3["aspect_ratio"] < m2["aspect_ratio"] < m1["aspect_ratio"], "l_r / l_z must tend to 0"


def test_velocity_divergence_finite_energy(sim):
    """
    Core theorem test:
    - Maximum velocity diverges to +infinity as t -> 1
    - Total kinetic energy remains uniformly bounded!
    """
    times = [0.0, 0.5, 0.9, 0.99, 0.999]
    metrics = [sim.compute_global_metrics(t) for t in times]

    u_maxes = [m["u_max"] for m in metrics]
    e_totals = [m["energy_total"] for m in metrics]

    # Velocity diverges monotonically
    for i in range(len(u_maxes) - 1):
        assert u_maxes[i + 1] > u_maxes[i], f"Velocity must increase: {u_maxes[i+1]} > {u_maxes[i]}"

    # Energy is bounded
    assert max(e_totals) < 5.0, "Total kinetic energy must remain uniformly bounded"
    assert min(e_totals) > 0.0, "Kinetic energy must be positive"


def test_radial_profile_and_pressure_crater(sim):
    """Verifies smooth vortex velocity at axis and deep pressure minimum."""
    t = 0.95
    r = np.array([0.0, 0.1, 0.5, 1.5])
    theta = np.zeros_like(r)
    z = np.zeros_like(r)

    vel = sim.evaluate_velocity_field(r, theta, z, t)
    # At r = 0, azimuthal velocity must vanish (regularity on axis)
    assert np.isclose(vel["u_theta"][0], 0.0, atol=1e-4), "Azimuthal velocity must vanish at r=0"

    # Pressure must be minimum at axis
    p = sim.evaluate_pressure(r, z, t)
    assert p[0] < p[1] < p[2] < p[3], "Pressure must increase monotonically from the axis crater"


def test_annular_stress_support(sim):
    """Verifies that annular stress is compactly supported in [X_a, X_b]."""
    t = 0.95
    tau = sim.get_tau(t)
    q = tau

    # Coordinates in core, annulus, and exterior
    X_core = 0.1
    X_annulus = 1.6
    X_ext = 5.0

    r_core = np.sqrt(2.0 * q * X_core)
    r_annulus = np.sqrt(2.0 * q * X_annulus)
    r_ext = np.sqrt(2.0 * q * X_ext)

    r_test = np.array([r_core, r_annulus, r_ext])
    theta_test = np.zeros(3)
    z_test = np.zeros(3)

    stress = sim.evaluate_annular_stress_and_pulses(r_test, theta_test, z_test, t)

    assert stress["T_r_theta"][1] > 10.0 * stress["T_r_theta"][0], "Annular stress must be much larger in annulus than in core"
    assert stress["T_r_theta"][1] > 10.0 * stress["T_r_theta"][2], "Annular stress must be much larger in annulus than in exterior"
