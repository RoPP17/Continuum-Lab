"""
Unit & Integration Tests: Vortex Rings Collision & Reconnection Pipeline
Module: 01 Mecanica de Fluidos / 07 Colision de Anillos de Vortice
File: tests/test_vortex_collision.py
"""

import os
import sys
from pathlib import Path
import pytest
import numpy as np

module_root = str(Path(__file__).resolve().parent.parent)
if module_root not in sys.path:
    sys.path.insert(0, module_root)

from src.physics.vortex_collision_sim import VortexRingsCollisionSim
from src.physics.export_excel_benchmark import generate_vortex_excel_benchmark


def test_sim_initialization():
    sim = VortexRingsCollisionSim(R0=0.28, a0=0.045, Gamma0=1.4)
    assert sim.R0 == 0.28
    assert sim.a0 == 0.045
    assert sim.Gamma0 == 1.4
    assert sim.m_mode == 12
    assert sim.num_particles >= 1000


def test_kelvin_hicks_speed():
    sim = VortexRingsCollisionSim(R0=0.28, a0=0.045, Gamma0=1.4)
    u_self = sim._kelvin_hicks_speed(sim.R0, sim.a0)
    # Expected self-induced velocity ~ 1.0 - 2.0 m/s
    assert 0.50 < u_self < 2.50


def test_mutual_induction_radial_expansion():
    sim = VortexRingsCollisionSim()
    # At small separation z = 0.08m, mutual induction must drive strong radial expansion
    ur, uz = sim._mutual_induction(sim.R0, 0.08, sim.a0)
    assert ur > 0.40  # Radial expansion > 0.4 m/s
    assert uz > 0.0   # Upward velocity induced by image ring that opposes downward approach


def test_core_volume_conservation():
    sim = VortexRingsCollisionSim()
    st0 = sim.get_state(0.0)
    st_mid = sim.get_state(4.0)
    # Volume proportional to R * a^2
    vol0 = st0["R"] * (st0["a"] ** 2)
    vol_mid = st_mid["R"] * (st_mid["a"] ** 2)
    assert np.isclose(vol0, vol_mid, rtol=0.05)


def test_reconnection_crown_count():
    sim = VortexRingsCollisionSim()
    st_pre = sim.get_state(2.0)
    assert not st_pre["is_reconnected"]
    assert len(st_pre["sec_rings"]) == 0

    st_post = sim.get_state(7.5)
    assert st_post["is_reconnected"]
    assert len(st_post["sec_rings"]) == 12  # Exact 12 secondary baby rings


def test_particles_advection_bounds():
    sim = VortexRingsCollisionSim()
    st = sim.get_state(5.0)
    pts = st["particles_3d"]
    speeds = st["particles_speed"]
    assert pts.shape == (1200, 3)
    assert np.all(np.isfinite(pts))
    assert np.all(speeds > 0.0)
    assert np.max(speeds) < 1e5


def test_benchmark_excel_generation(tmp_path):
    test_excel = str(tmp_path / "test_vortex_benchmark.xlsx")
    out = generate_vortex_excel_benchmark(test_excel)
    assert os.path.exists(out)
    assert os.path.getsize(out) > 5000
