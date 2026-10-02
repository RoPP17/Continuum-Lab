@echo off
title Continuum Lab - Mecanismo Coriolis Collarin
echo =======================================================================
echo    CONTINUUM LAB - MECANISMO CON ACELERACION DE CORIOLIS
echo    Sistema de 2 Barras con Collarin Deslizante (Guia Ranurada)
echo =======================================================================
echo Seleccione el modo de ejecucion:
echo [1] Simulador Web Interactivo Hipnotico (120 FPS, Canvas, Vector Bloom)
echo [2] Aplicacion de Escritorio Pygame (60 FPS, Teclado, Capturas)
echo [3] Compilar Video MP4 Cinematografico (60 FPS, 1080p, H.264)
echo [4] Generar Graficos Diagnosticos de Publicacion (300 DPI)
echo [5] Exportar Modelo Excel Dinamico (XLSX OpenPyXL)
echo [6] Ejecutar Suite de Tests (Pytest)
echo [7] Ejecutar TODO y Abrir Simulador
echo =======================================================================
set /p opt="Opcion [1-7, default 1]: "

if "%opt%"=="" set opt=1
if "%opt%"=="1" python main.py --web
if "%opt%"=="2" python main.py --pygame
if "%opt%"=="3" python main.py --video
if "%opt%"=="4" python main.py --plots
if "%opt%"=="5" python main.py --excel
if "%opt%"=="6" python main.py --test
if "%opt%"=="7" python main.py --all

pause
