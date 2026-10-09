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
    PROJECT_ROOT / "01 Mecanica de Fluidos" / "03 Desprendimiento Capa Limite y Stall Aerodinamico" / "tests",
    PROJECT_ROOT / "02 Dinamica y Vibraciones" / "01 Pendulo Triple Caotico" / "tests",
    PROJECT_ROOT / "02 Dinamica y Vibraciones" / "02 Mecanismo Coriolis Collarin" / "tests",
    PROJECT_ROOT / "02 Dinamica y Vibraciones" / "03 Enjambre Doble Pendulo Caotico" / "tests",
    PROJECT_ROOT / "02 Dinamica y Vibraciones" / "03 Pendulo Invertido Kapitza" / "tests",
    PROJECT_ROOT / "02 Dinamica y Vibraciones" / "03 Precesion Giroscopica 3D" / "tests",
    PROJECT_ROOT / "02 Dinamica y Vibraciones" / "04 Efecto Dzhanibekov 3D" / "tests",
    PROJECT_ROOT / "02 Dinamica y Vibraciones" / "04 Flutter Aeroelastico Tacoma Narrows" / "tests",
    PROJECT_ROOT / "04 Termodinamica y Calor" / "01 Ley Cero de la Termodinamica 3 Cuerpos" / "tests",
    PROJECT_ROOT / "06 Matematicas y Geometria" / "01 Series de Fourier Geometricas" / "tests",
    PROJECT_ROOT / "06 Matematicas y Geometria" / "02 Identidad de Euler 3D" / "tests",
    PROJECT_ROOT / "06 Matematicas y Geometria" / "03 Curva Braquistocrona" / "tests",
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
            [sys.executable, "-m", "pytest", "tests", "-v"],
            cwd=str(suite.parent)
        )
        if result.returncode != 0:
            print(f"[FAIL] {rel_path} encountered errors.")
            total_failed += 1
        else:
            print(f"[PASS] {rel_path} passed successfully.")

    print("\n" + "=" * 60)
    if total_failed == 0:
        print(" ALL SUITES PASSED (All physical and mathematical tests green)")
        print("=" * 60)
        return 0
    else:
        print(f" {total_failed} SUITE(S) FAILED")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
