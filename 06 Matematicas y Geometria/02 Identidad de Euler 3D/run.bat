@echo off
REM ===============================================================================
REM CONTINUUM LAB // MATHEMATICS & GEOMETRY
REM Module: 02 Identidad de Euler 3D
REM ===============================================================================

echo [CONTINUUM LAB] Running Mathematical Verification Suite...
python -m pytest tests/

echo [CONTINUUM LAB] Generating Dynamic Excel Benchmark...
python main.py --benchmark

echo [CONTINUUM LAB] Rendering 3D Bilingual Videos (1080x1920 @ 60 FPS)...
python main.py --render

echo [CONTINUUM LAB] Execution Complete! Check RENDERS/4 Identidad de Euler 3D
pause
