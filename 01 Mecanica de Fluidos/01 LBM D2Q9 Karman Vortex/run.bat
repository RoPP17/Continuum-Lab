@echo off
TITLE Continuum Lab — Simulation Engine
echo ===============================================================================
echo                CONTINUUM LAB ^| 60 FPS CUDA Simulation Engine
echo                Module: 01_Mecanica_de_Fluidos / LBM D2Q9
echo ===============================================================================
echo.

python main.py %*

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Simulation exited with error code %errorlevel%.
    pause
)
