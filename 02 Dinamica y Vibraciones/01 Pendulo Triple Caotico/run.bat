@echo off
TITLE Continuum Lab — Chaotic Triple Pendulum
echo ===============================================================================
echo                CONTINUUM LAB ^| Chaotic Triple Pendulum Engine
echo                Module: 02 Dinamica y Vibraciones
echo ===============================================================================
echo.

python main.py %*

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Execution failed with error code %errorlevel%.
    pause
)
