@echo off
setlocal
echo ===============================================================================
echo       CONTINUUM LAB // LEY CERO DE LA TERMODINAMICA 3 CUERPOS
echo ===============================================================================
echo.
echo Seleccione el modo de ejecucion:
echo  [1] Ejecutar Resumen Fisico Analitico (Terminal)
echo  [2] Ejecutar Suite de Pruebas Unitarias (pytest)
echo  [3] Exportar Modelo Dinamico de Excel (.xlsx)
echo  [4] Generar Portadas HD y GIF Animado
echo  [5] Renderizar Vista Previa Rapida de Video (6.0s @ 30 FPS)
echo  [6] RENDERIZAR VIDEO OFICIAL COMPLETO (1080x1920 @ 60 FPS con Audio)
echo  [7] EJECUTAR TODO (Benchmark + Visuales + Video Oficial)
echo.
set /p opt="Ingrese su opcion [1-7]: "

if "%opt%"=="1" python main.py
if "%opt%"=="2" python main.py --test
if "%opt%"=="3" python main.py --benchmark
if "%opt%"=="4" python main.py --visuals
if "%opt%"=="5" python main.py --preview
if "%opt%"=="6" python main.py --render
if "%opt%"=="7" python main.py --all

pause
