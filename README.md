# CONTINUUM LAB — Senior Computational Physics & Visual Engineering Architecture

<div align="center">

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![NVIDIA CUDA](https://img.shields.io/badge/GPU%20Acceleration-NVIDIA%20RTX%205070-76B900.svg?style=for-the-badge&logo=nvidia&logoColor=white)](https://www.nvidia.com/)
[![Taichi Lang](https://img.shields.io/badge/JIT%20Compiler-Taichi%20Lang-FF4500.svg?style=for-the-badge)](https://www.taichi-lang.org/)
[![Tests](https://img.shields.io/badge/Tests-100%25%20Passing-brightgreen.svg?style=for-the-badge&logo=pytest&logoColor=white)](01_Mecanica_de_Fluidos/01_LBM_D2Q9_Karman_Vortex/tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<br/>

**A mathematically rigorous, GPU-accelerated computational physics and continuum mechanics suite.**  
*Simulates incompressible Navier-Stokes flows, kinetic Boltzmann schemes, dynamic vibrations, and solid mechanics.*

<br/>

![Continuum Lab LBM Simulation Preview](00_Resultados_y_Renders/01_Mecanica_de_Fluidos/01_LBM_D2Q9_Karman_Vortex/capturas/karman_vortex_preview.gif)

</div>

---

## 🏛️ Repository Architecture & Discipline Taxonomy

All simulations and experiments are strictly classified into decoupled, self-contained domain folders, with all media and analytical outputs segregated into dedicated result directories:

```text
Continuum-Lab/
├── 00_Resultados_y_Renders/                 # Centralized storage for media & data exports
│   └── 01_Mecanica_de_Fluidos/
│       └── 01_LBM_D2Q9_Karman_Vortex/
│           ├── videos/                      # 16:9 4K & 9:16 Vertical MP4 renders
│           ├── benchmarks/                  # Dynamic Excel models (.xlsx)
│           └── capturas/                    # Animated GIFs and high-resolution screenshots
│
├── 01_Mecanica_de_Fluidos/                  # Fluid mechanics, aerodynamics, mesoscopic kinetics
│   └── 01_LBM_D2Q9_Karman_Vortex/           # LBM D2Q9 von Kármán vortex shedding & MEM telemetry
│       ├── src/                             # MVC Architecture (physics, simulation, visualization)
│       ├── tests/                           # Automated pytest verification suite
│       ├── docs/                            # Analytical proofs and technical reports
│       ├── main.py                          # CLI entry point (interactive & render modes)
│       ├── run.bat / setup.bat              # One-click Windows launchers
│       └── README.md                        # Module documentation
│
├── 02_Dinamica_y_Vibraciones/               # Multi-body dynamics, modal analysis, chaos
├── 03_Mecanica_de_Solidos/                  # Elasticity, plasticity, fracture mechanics, FEM
├── 04_Termodinamica_y_Calor/                # Conjugate heat transfer, phase change, radiation
├── 05_Metodos_Numericos_y_CAE/              # Boundary element methods, spectral solvers, PINNs
│
├── requirements.txt                         # Global dependency manifest
├── LICENSE                                  # MIT License
└── README.md                                # Master documentation
```

---

## 🎨 Visual Philosophy: Zero Clutter & Zero Overlap

Continuum Lab enforces a strict visual standard for every scientific simulation:
1. **Zero Text Overlap:** All telemetry cards, labels, and graphs reside in mathematically isolated bounding boxes with fixed padding (`safe zones`), ensuring no typography ever intersects with another or obstructs physical phenomena.
2. **Cybernetic Laboratory Palette:**
   - **Deep Space Void (`#0a0a0c`):** Lattice background.
   - **Electric Cyan (`#00f0ff`):** Counter-clockwise vorticity ($\omega_z > 0$).
   - **Vorticity Magenta (`#ff007f`):** Clockwise vorticity ($\omega_z < 0$).
   - **Kinetic Amber (`#ffaa00`):** Pressure extrema & stagnation points.
3. **Hyperbolic Contrast Compression:** Non-linear scaling ($\tilde{\omega}_z = \tanh(\omega_z / \omega_0)$) illuminates fine turbulent filaments without saturating boundary layers.

---

## 💻 Hardware & Compute Environment

Optimized natively for high-performance scientific computing:
* **GPU:** NVIDIA GeForce RTX 5070 Laptop GPU (8 GB GDDR7, CUDA Cores, Tensor Cores).
* **CPU:** AMD Ryzen 9 270 (8 Cores, 16 Threads @ 4.0+ GHz).
* **RAM:** 32 GB DDR5 @ 5600 MHz Dual-Channel.
* **Storage:** Crucial P310 2 TB NVMe PCIe 4.0 SSD.
* **OS:** Windows 11 Pro 64-bit.

---

## 🚀 Active Modules & Quick Links

* [**01_Mecanica_de_Fluidos / 01_LBM_D2Q9_Karman_Vortex**](01_Mecanica_de_Fluidos/01_LBM_D2Q9_Karman_Vortex/): Lattice Boltzmann D2Q9 von Kármán vortex shedding with real-time Momentum Exchange Method aerodynamic force telemetry ($C_D$, $C_L$) and limit cycle phase portraits.

---

## 📜 License
Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for complete terms.
