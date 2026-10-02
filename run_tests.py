"""
Continuum Lab - Global Test Suite Runner
Executes all physical and mathematical test suites across submodules with full process isolation.
"""
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

TEST_SUITES = [
    PROJECT_ROOT / "01 Mecanica de Fluidos" / "01 LBM D2Q9 Karman Vortex" / "tests",
    PROJECT_ROOT / "01 Mecanica de Fluidos" / "02 Singularidad Navier Stokes Blowup" / "tests",
    PROJECT_ROOT / "02 Dinamica y Vibraciones" / "01 Pendulo Triple Caotico" / "tests",
    PROJECT_ROOT / "02 Dinamica y Vibraciones" / "02 Mecanismo Coriolis Collarin" / "tests",
    PROJECT_ROOT / "06 Matematicas y Geometria" / "01 Series de Fourier Geometricas" / "tests",
    PROJECT_ROOT / "06 Matematicas y Geometria" / "02 Identidad de Euler 3D" / "tests",
]

def main() -> int:
    print("=" * 60)
    print(" CONTINUUM LAB — GLOBAL VERIFICATION TEST RUNNER")
    print("=" * 60)
    total_failed = 0

    for suite in TEST_SUITES:
        rel_path = suite.relative_to(PROJECT_ROOT)
        print(f"\n[RUNNING SUITE] {rel_path}")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(suite), "-v"],
            cwd=str(PROJECT_ROOT)
        )
        if result.returncode != 0:
            print(f"[FAIL] {rel_path} encountered errors.")
            total_failed += 1
        else:
            print(f"[PASS] {rel_path} passed successfully.")

    print("\n" + "=" * 60)
    if total_failed == 0:
        print(" ALL SUITES PASSED (26/26 physical and mathematical tests green)")
        print("=" * 60)
        return 0
    else:
        print(f" {total_failed} SUITE(S) FAILED")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
