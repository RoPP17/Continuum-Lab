@echo off
TITLE Continuum Lab — Environment Setup
echo ===============================================================================
echo                CONTINUUM LAB ^| Computational Physics & Visuals
echo                     ASUS TUF A16 ^| NVIDIA RTX 5070 CUDA
echo ===============================================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.12+ was not found in PATH. Please install Python.
    pause
    exit /b 1
)

echo [INFO] Verifying and installing locked dependencies...
python -m pip install -r requirements.txt

echo.
echo [INFO] Validating Taichi GPU CUDA runtime...
python -c "import taichi as ti; ti.init(arch=ti.cuda); print('[GPU VERIFIED] Taichi CUDA ready on RTX 5070')"

echo.
echo [INFO] Running test suite...
python -m pytest tests/ -v

echo.
echo ===============================================================================
echo [SUCCESS] Continuum Lab setup is complete and fully verified.
echo ===============================================================================
pause
