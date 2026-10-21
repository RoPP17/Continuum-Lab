@echo off
echo ========================================================================
echo CONTINUUM LAB // 07 ATRACTOR DE LORENZ Y EFECTO MARIPOSA 3D
echo ========================================================================
python -m pytest tests -v
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Unit tests failed.
    exit /b %ERRORLEVEL%
)
python main.py --all
