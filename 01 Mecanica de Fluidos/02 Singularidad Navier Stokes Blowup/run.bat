@echo off
REM =========================================================================
REM CONTINUUM LAB // FLUID MECHANICS & NONLINEAR PDES
REM Execution Script: 02 Singularidad Navier Stokes Blowup
REM =========================================================================

echo [CONTINUUM LAB] Initializing Navier-Stokes Singularity Simulation...
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
echo To render full 60 FPS TikTok videos, run: python main.py --render
echo =========================================================================
pause
