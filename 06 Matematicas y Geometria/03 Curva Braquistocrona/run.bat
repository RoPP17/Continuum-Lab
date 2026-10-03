@echo off
chcp 65001 > nul
cls
echo ===============================================================================
echo                CONTINUUM LAB // CALCULO DE VARIACIONES
echo                 06 Matematicas y Geometria / 03 Curva Braquistocrona
echo ===============================================================================
echo.
python main.py
echo.
echo Presiona 1 para Renderizar Video (1080x1920 @ 60 FPS)
echo Presiona 2 para Exportar Benchmark Excel (.xlsx)
echo Presiona 3 para Ejecutar Pruebas Unitarias (pytest)
echo Presiona 4 para Salir
echo.
set /p opt="Selecciona una opcion [1-4]: "

if "%opt%"=="1" (
    python main.py --render
) else if "%opt%"=="2" (
    python main.py --benchmark
) else if "%opt%"=="3" (
    python main.py --test
) else (
    echo Saliendo...
)
pause
