# 01_LBM_D2Q9_Karman_Vortex — Lattice Boltzmann Simulation Module

<div align="center">

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![NVIDIA CUDA](https://img.shields.io/badge/GPU%20Acceleration-NVIDIA%20RTX%205070-76B900.svg?style=for-the-badge&logo=nvidia&logoColor=white)](https://www.nvidia.com/)
[![Taichi Lang](https://img.shields.io/badge/JIT%20Compiler-Taichi%20Lang-FF4500.svg?style=for-the-badge)](https://www.taichi-lang.org/)
[![Tests](https://img.shields.io/badge/Tests-100%25%20Passing-brightgreen.svg?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](../../LICENSE)

<br/>

**Simulación mesoscópica de la calle de vórtices de von Kármán sobre obstáculos sumergidos a $Re = 150$.**  
*Telemetría de fuerzas en tiempo real con el Método de Intercambio de Momento (MEM) y renderizado HUD libre de solapamientos.*

<br/>

![Vista Previa LBM](../../00_Resultados_y_Renders/01_Mecanica_de_Fluidos/01_LBM_D2Q9_Karman_Vortex/capturas/karman_vortex_preview.gif)

</div>

---

## 📁 Estructura del Módulo

```text
01_LBM_D2Q9_Karman_Vortex/
├── src/
│   ├── physics/             # Modelos LBM D2Q9, integradores cinéticos, MEM
│   │   ├── lbm_d2q9.py      # Solucionador vectorial puro en NumPy (CPU)
│   │   ├── lbm_taichi_cuda.py# Solucionador JIT masivo en CUDA (RTX 5070)
│   │   └── export_benchmarks.py# Modelo dinámico openpyxl con fórmulas nativas
│   ├── simulation/          # Bucle temporal de 60 FPS y control de estado
│   │   └── engine.py        # Gestor de backends GPU/CPU
│   ├── visualization/       # Pipeline gráfico y teoría del color cibernética
│   │   ├── colormaps.py     # Compresión hiperbólica tanh(w/w0)
│   │   └── renderer.py      # Renderizador HUD con bounding boxes aislados
│   └── ui/                  # Componentes de interfaz gráfica
├── tests/                   # Suite de verificación unitaria con pytest
│   └── test_lbm_physics.py  # Invariantes tensoriales, momentos y conservación
├── docs/
│   ├── INFORME_TECNICO_LBM.md # Demostraciones analíticas y expansión de Chapman-Enskog
│   └── DISTRIBUTION_SNIPPETS.md# Plantillas de divulgación técnica
├── run.bat / setup.bat      # Lanzadores automáticos para Windows
├── main.py                  # Punto de entrada CLI con modos interactivo y render
└── README.md                # Documentación del módulo
```

---

## 🚀 Modos de Ejecución

1. **Modo Interactivo en Tiempo Real (CUDA 60 FPS):**
   ```bash
   python main.py
   ```
2. **Generación de Modelo Excel Dinámico:**
   ```bash
   python main.py --benchmark
   ```
   *Destino:* `00_Resultados_y_Renders/01_Mecanica_de_Fluidos/01_LBM_D2Q9_Karman_Vortex/benchmarks/`
3. **Renderizado de Video (Widescreen 16:9 & Vertical 9:16):**
   ```bash
   python main.py --mode render --format 16:9
   python main.py --mode render --format 9:16
   ```
   *Destino:* `00_Resultados_y_Renders/01_Mecanica_de_Fluidos/01_LBM_D2Q9_Karman_Vortex/videos/`
4. **Verificación de Pruebas Unitarias:**
   ```bash
   python -m pytest tests/ -v
   ```
