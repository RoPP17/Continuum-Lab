@echo off
REM ===============================================================================
REM Continuum Lab — Batch Execution for Fourier Geometry Module
REM ===============================================================================

echo [CONTINUUM LAB] Running Mathematical Analysis...
python main.py

echo.
echo [CONTINUUM LAB] Generating Dynamic Excel Benchmark...
python main.py --benchmark

echo.
echo [CONTINUUM LAB] Running Test Suite...
python -m pytest tests/

echo.
echo [CONTINUUM LAB] Complete.
