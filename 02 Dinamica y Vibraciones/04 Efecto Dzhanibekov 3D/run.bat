@echo off
setlocal
echo ======================================================================
echo  Continuum Lab -- 04 Efecto Dzhanibekov 3D (Teorema Raqueta de Tenis)
echo ======================================================================

if "%1"=="test" (
    echo [RUN] Ejecutando pruebas fisicas unitarias con pytest...
    pytest tests\test_dzhanibekov.py -v
    goto end
)

if "%1"=="preview" (
    echo [RUN] Compilando preview rapido de Manim (-ql)...
    python main.py --preview
    goto end
)

if "%1"=="render" (
    echo [RUN] Compilando video final 1080x1920 @ 60 FPS (-qh)...
    python main.py --render
    goto end
)

if "%1"=="benchmark" (
    echo [RUN] Exportando modelo Excel XLSX con formulas dinamicas...
    python main.py --benchmark
    goto end
)

if "%1"=="diagnostics" (
    echo [RUN] Ejecutando diagnostico teorico de Euler...
    python main.py --diagnostics
    goto end
)

echo [RUN] Ejecutando diagnostico teorico y exportacion de benchmark...
python main.py --diagnostics
python main.py --benchmark

echo.
echo Para renderizar el video completo en 1080x1920 @ 60 FPS ejecuta:
echo    run.bat render
echo Para preview rapido:
echo    run.bat preview
echo Para pruebas:
echo    run.bat test

:end
endlocal
