"""
Continuum Lab — Verification & Quality Assurance Suite
Mathematical tests for Complex Fourier Series analysis of canonical shapes.
Division: 06 Matematicas y Geometria / 01 Series de Fourier Geometricas
"""

import sys
from pathlib import Path
import numpy as np
import pytest

# Ensure project root is in sys.path
proj_dir = Path(__file__).resolve().parent.parent
if str(proj_dir) not in sys.path:
    sys.path.insert(0, str(proj_dir))

from src.math.fourier_shapes import ShapeFourierSeries
from src.math.export_fourier_excel import export_fourier_benchmark_excel


def test_circle_fourier_exactness():
    """Verifies that a circle consists of exactly one fundamental harmonic."""
    f_circle = ShapeFourierSeries("circle", radius=1.5)
    assert len(f_circle.harmonics) == 1, "Circle must contain exactly 1 harmonic"
    freq, amp, phase = f_circle.harmonics[0]
    assert freq == 1, "Circle fundamental frequency must be 1"
    assert np.isclose(amp, 1.5), "Circle amplitude must match radius"

    # Position at t = 0 and t = pi/2
    z0 = f_circle.evaluate_point(0.0)
    z_pi2 = f_circle.evaluate_point(np.pi / 2.0)
    assert np.isclose(z0, 1.5 + 0j), "At t=0, z = R"
    assert np.isclose(z_pi2, 0.0 + 1.5j), "At t=pi/2, z = i*R"


def test_star_dihedral_symmetry():
    """Verifies D5 dihedral symmetry in star Fourier coefficients."""
    f_star = ShapeFourierSeries("star", radius=1.0)
    # Check that all harmonic frequencies obey 5-fold rotational symmetry: n % 5 == 1
    for freq, amp, phase in f_star.harmonics:
        rem = freq % 5
        assert rem == 1, f"Frequency {freq} violates 5-fold symmetry: rem = {rem}"


def test_octagon_dihedral_symmetry():
    """Verifies D8 dihedral symmetry and 1/n^2 power decay in regular octagon harmonics."""
    f_oct = ShapeFourierSeries("octagon", radius=1.0)
    for freq, amp, phase in f_oct.harmonics:
        # Frequencies must satisfy n % 8 == 1 or n % 8 == 7 (i.e. n = +-1 mod 8)
        rem = abs(freq) % 8
        assert rem in [1, 7], f"Frequency {freq} violates 8-fold symmetry: rem = {rem}"

    # Amplitude of n = -7 must be close to a0 / 49
    a0 = f_oct.harmonics[0][1]
    a_m7 = f_oct.harmonics[1][1]
    expected_ratio = 1.0 / 49.0
    assert np.isclose(a_m7 / a0, expected_ratio, rtol=0.05), "Octagon harmonics must decay as 1/n^2"


def test_epicycle_kinematics_consistency():
    """Verifies that the tip of the epicycle chain matches z(t) directly."""
    f_star = ShapeFourierSeries("star", radius=1.0)
    for t_test in [0.0, 1.2, 3.4, 5.1]:
        z_direct = f_star.evaluate_point(t_test)
        epicycles = f_star.get_epicycles_kinematics(t_test)
        z_tip = epicycles[-1]["tip"]
        z_tip_complex = z_tip[0] + 1j * z_tip[1]
        assert np.isclose(z_direct, z_tip_complex, atol=1e-5), "Epicycle chain tip must match z(t)"


def test_excel_benchmark_generation(tmp_path):
    """Verifies successful generation of the dynamic openpyxl model."""
    excel_file = str(tmp_path / "test_fourier.xlsx")
    out = export_fourier_benchmark_excel(excel_file)
    assert Path(out).exists(), "Excel file must be generated"
    assert Path(out).stat().st_size > 4000, "Excel file must contain valid spreadsheet data"
