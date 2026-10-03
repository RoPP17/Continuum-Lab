"""
Continuum Lab — Verification & Pytest Suite
Test: Kapitza Inverted Pendulum Dynamics & Stability Criteria
Division: 02 Dinamica y Vibraciones / 03 Pendulo Invertido Kapitza
"""

import sys
from pathlib import Path
import numpy as np
import pytest

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.physics import (
    KapitzaConfig,
    compute_effective_potential,
    compute_potential_curvature,
    solve_kapitza_dynamics,
)


def test_kapitza_stability_criterion():
    """Verify analytical Kapitza condition (a*omega)^2 > 2*g*L."""
    config = KapitzaConfig()
    dynamic_factor = config.dynamic_factor
    threshold = config.stability_threshold
    
    assert dynamic_factor > threshold, f"Kapitza criterion failed: {dynamic_factor} <= {threshold}"
    assert pytest.approx(dynamic_factor, rel=1e-2) == 191.08
    assert pytest.approx(threshold, rel=1e-2) == 19.62
    assert config.stability_ratio > 9.0


def test_critical_frequency():
    """Verify analytical minimum critical frequency is ~17.62 Hz."""
    config = KapitzaConfig()
    f_crit = config.f_crit
    expected_f_crit = np.sqrt(2.0 * 9.81 * 1.0) / 0.04 / (2.0 * np.pi)
    assert pytest.approx(f_crit, rel=1e-3) == expected_f_crit
    assert pytest.approx(f_crit, abs=0.1) == 17.62


def test_effective_potential_curvature():
    """Verify that Theta = pi is a local minimum when vibration is active."""
    config = KapitzaConfig()
    
    # Active high-frequency vibration
    d2V_active = compute_potential_curvature(np.pi, config.omega, config)
    assert d2V_active > 0.0, "Theta = pi must be a local potential minimum (stable) when active"
    
    # Static base (omega = 0)
    d2V_static = compute_potential_curvature(np.pi, 0.0, config)
    assert d2V_static < 0.0, "Theta = pi must be a potential maximum (unstable) when static"


def test_attraction_basin_width():
    """Verify half-width of inverted basin of attraction is ~84.1 deg."""
    config = KapitzaConfig()
    basin_deg = config.basin_half_width_deg
    assert basin_deg > 80.0, f"Basin too small: {basin_deg} deg"
    assert pytest.approx(basin_deg, abs=0.5) == 84.11


def test_solve_kapitza_full_trajectory():
    """Verify full 15-second trajectory across all three phases."""
    config = KapitzaConfig()
    sol = solve_kapitza_dynamics(config)
    
    assert sol.n_frames == 901
    assert len(sol.t) == 901
    
    # Phase 1: Near upright vertical
    mask_phase1 = (sol.t >= 1.0) & (sol.t <= 3.5)
    mean_theta_phase1 = np.mean(sol.theta_slow_deg[mask_phase1])
    assert pytest.approx(mean_theta_phase1, abs=2.0) == 180.0
    
    # Phase 2: Lateral perturbation deflection reaches ~35 deg
    mask_pert = (sol.t >= 4.0) & (sol.t <= 5.5)
    min_theta_deg = np.min(sol.theta_deg[mask_pert])
    max_deflection = 180.0 - min_theta_deg
    assert 30.0 <= max_deflection <= 40.0, f"Deflection was {max_deflection} deg, expected ~35 deg"
    
    # Phase 2 end: Recovers to upright vertical before shutdown
    idx_8s = np.argmin(np.abs(sol.t - 7.9))
    assert pytest.approx(sol.theta_slow_deg[idx_8s], abs=8.0) == 180.0
    
    # Phase 3: Plunges downwards and rotates/settles toward hanging down (360 / 0 deg)
    idx_15s = -1
    final_theta = sol.theta_slow_deg[idx_15s] % 360.0
    assert (final_theta < 30.0) or (final_theta > 330.0), f"Pendulum did not hang down at end: {final_theta} deg"
