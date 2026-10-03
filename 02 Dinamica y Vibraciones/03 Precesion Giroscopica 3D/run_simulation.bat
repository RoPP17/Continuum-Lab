@echo off
REM ===========================================================================
REM Continuum Lab — Classical Mechanics & Aerospace Dynamical Systems
REM Simulation: 3D Gyroscopic Precession & Nutation
REM Division  : 02 Dinamica y Vibraciones / 03 Precesion Giroscopica 3D
REM ===========================================================================

echo ===========================================================================
echo   CONTINUUM LAB ^| 3D GYROSCOPIC PRECESSION ^& NUTATION (MANIM 9:16 UHD)
echo ===========================================================================
echo.
echo Selecciona la calidad de renderizado:
echo   [1] Vista Previa Rapida (480p, 15 FPS)    -- Render rapido de prueba
echo   [2] Alta Definicion Ultra (1080x1920, 60 FPS) -- PRODUCCION RECOMENDADA
echo   [3] Ultra 4K Vertical (2160x3840, 60 FPS)   -- Master Ultra-Res
echo   [4] Salir
echo.

set /p opt="Opcion [1-4] (default 2): "
if "%opt%"=="" set opt=2

if "%opt%"=="1" (
    echo.
    echo [*] Renderizando Vista Previa (Low Quality)...
    manim -pql --format=mp4 render_gyroscope.py GyroscopePrecessionScene
    goto end
)

if "%opt%"=="2" (
    echo.
    echo [*] Renderizando Ultra-HD Produccion (1080x1920 @ 60 FPS)...
    manim -pqh --format=mp4 render_gyroscope.py GyroscopePrecessionScene
    goto end
)

if "%opt%"=="3" (
    echo.
    echo [*] Renderizando Master 4K (2160x3840 @ 60 FPS)...
    manim -pqk --format=mp4 render_gyroscope.py GyroscopePrecessionScene
    goto end
)

if "%opt%"=="4" (
    echo Cancelado por el usuario.
    goto end
)

:end
echo.
echo ===========================================================================
echo   Continuum Lab ^| Proceso finalizado.
echo ===========================================================================
pause
