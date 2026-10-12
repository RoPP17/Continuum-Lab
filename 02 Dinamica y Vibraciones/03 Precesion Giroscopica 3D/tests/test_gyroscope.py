"""
Continuum Lab - Tests for 3D Gyroscopic Precession & Nutation
Verifies analytical Euler rigid body mechanics, Steiner inertia tensors,
precession rate, and nutation frequencies.
"""

import pytest
import numpy as np


def test_moments_of_inertia():
    m = 2.5
    r = 0.18
    r_cm = 0.25

    # Polar inertia (solid disk around cylinder symmetry axis)
    i_z = 0.5 * m * (r ** 2)
    assert np.isclose(i_z, 0.0405, rtol=1e-4)

    # Transverse inertia through pivot (Steiner theorem)
    i_x_cm = 0.25 * m * (r ** 2)
    i_x = i_x_cm + m * (r_cm ** 2)
    assert np.isclose(i_x, 0.1765, rtol=1e-4)


def test_gravitational_torque_and_precession():
    m = 2.5
    g = 9.81
    r_cm = 0.25
    theta = np.pi / 2  # Horizontal axis

    # Gravitational torque tau = r x F
    tau_g = r_cm * m * g * np.sin(theta)
    assert np.isclose(tau_g, 6.13125, rtol=1e-3)

    # Spin at 10,000 RPM
    rpm = 10000.0
    omega_s = (rpm * 2.0 * np.pi) / 60.0
    i_z = 0.0405
    angular_momentum_spin = i_z * omega_s

    # Fast-gyroscope approximation for precession rate Omega_p = tau / L
    omega_p = tau_g / angular_momentum_spin
    assert omega_p > 0.1
    assert np.isclose(omega_p, 0.1445, rtol=1e-2)


def test_nutation_frequency():
    m = 2.5
    r = 0.18
    r_cm = 0.25
    rpm = 10000.0
    omega_s = (rpm * 2.0 * np.pi) / 60.0
    i_z = 0.5 * m * (r ** 2)
    i_x = 0.25 * m * (r ** 2) + m * (r_cm ** 2)

    # Regular nutation frequency in symmetric top: omega_n = I_z * omega_s / I_x
    omega_n = (i_z * omega_s) / i_x
    assert omega_n > omega_s * 0.1
    # Ratio omega_n / omega_s is exactly I_z / I_x = 0.0405 / 0.1765 ~ 0.2294
    assert np.isclose(omega_n / omega_s, i_z / i_x, rtol=1e-4)
