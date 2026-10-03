@echo off
REM =========================================================================
REM CONTINUUM LAB // FLUID MECHANICS & AERODYNAMICS
REM Execution Script: 03 Desprendimiento Capa Limite y Stall Aerodinamico
REM =========================================================================

echo [CONTINUUM LAB] Initializing Aerodynamic Stall Simulation...
python main.py

echo.
echo [CONTINUUM LAB] Running Verification Unit Tests...
pytest tests/

echo.
echo [CONTINUUM LAB] Generating Dynamic Excel Benchmark...
python main.py --benchmark

echo.
echo [CONTINUUM LAB] Generating Visual Assets & Previews...
python main.py --visuals

echo.
echo =========================================================================
echo To render full 60 FPS TikTok / Shorts videos, run: python main.py --render
echo =========================================================================
pause
