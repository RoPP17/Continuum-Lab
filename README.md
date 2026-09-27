# CONTINUUM LAB — Senior Computational Physics & Visual Engineering Architecture

<div align="center">

<img src="Identidad Visual/logo_master_lockup.png" width="480" alt="Continuum Lab Logo"/>

<br/>

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![NVIDIA CUDA](https://img.shields.io/badge/GPU%20Acceleration-NVIDIA%20RTX%205070-76B900.svg?style=for-the-badge&logo=nvidia&logoColor=white)](https://www.nvidia.com/)
[![Taichi Lang](https://img.shields.io/badge/JIT%20Compiler-Taichi%20Lang-FF4500.svg?style=for-the-badge)](https://www.taichi-lang.org/)
[![Tests](https://img.shields.io/badge/Tests-20%2F20%20Passing-brightgreen.svg?style=for-the-badge&logo=pytest&logoColor=white)](run_tests.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<br/>

[![Instagram](https://img.shields.io/badge/Instagram-@continuumlab__-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/continuumlab_/)
[![TikTok](https://img.shields.io/badge/TikTok-@continuum.lab-000000?style=for-the-badge&logo=tiktok&logoColor=white)](https://www.tiktok.com/@continuum.lab)
[![GitHub](https://img.shields.io/badge/GitHub-RoPP17-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/RoPP17)

<br/>

**A mathematically rigorous, GPU-accelerated computational physics and continuum mechanics suite.**  
*Simulating incompressible Navier-Stokes flows, non-linear chaotic dynamics, geometric Fourier epicycles, and complex analysis at 60 FPS.*

</div>

---

## 🏛️ Repository Architecture & Discipline Taxonomy

Every experiment is fully decoupled, mathematically verified, and organized without underscores:

```text
Continuum Lab/
├── 01 Mecanica de Fluidos/                  # Fluid dynamics, aerodynamics, mesoscopic kinetics
│   └── 01 LBM D2Q9 Karman Vortex/           # LBM D2Q9 shedding, moving cylinder & reactive audio
├── 02 Dinamica y Vibraciones/               # Non-linear dynamics, chaos & multi-body mechanics
│   └── 01 Pendulo Triple Caotico/           # 6-DOF Lagrangian integrator & FM reactive synthesis
├── 06 Matematicas y Geometria/              # Pure & applied mathematics, geometry, complex analysis
│   ├── 01 Series de Fourier Geometricas/    # Complex epicycle decomposition (Circle, Star, Octagon)
│   └── 02 Identidad de Euler 3D/            # Helix on complex cylinder, Taylor convergence & projections
├── Automatizacion y Redes/                  # Autonomous headless publishing suite (IG, TikTok, YouTube)
├── Identidad Visual/                        # Vector branding, master lockups, banners & HUD specs
├── RENDERS/                                 # Centralized video captures, benchmarks & media
│   ├── 1 Vortices de von Karman/extra/      # Benchmarks (.xlsx), screenshots, telemetry
│   ├── 2 Pendulo Triple Trayectoria Caotica/extra/
│   ├── 3 Series de Fourier Geometricas/extra/
│   └── 4 Identidad de Euler 3D/extra/
├── run_tests.py                             # Global verification test runner (20/20 passing)
└── README.md                                # Master documentation
```

---

## 🔬 Active Simulation Modules

### 1. [Fluid Dynamics: LBM D2Q9 Vortex Shedding](01%20Mecanica%20de%20Fluidos/01%20LBM%20D2Q9%20Karman%20Vortex)
- **Physics:** 2D 9-velocity Lattice Boltzmann method (D2Q9-BGK) solving incompressible Navier-Stokes.
- **Features:** Dynamic moving bluff body, Momentum Exchange Method (MEM) for aerodynamic lift $C_L$ and drag $C_D$, Strouhal vortex shedding whistle, stereo-panned Aeolian tone.

### 2. [Chaos Theory: Non-Linear Triple Pendulum](02%20Dinamica%20y%20Vibraciones/01%20Pendulo%20Triple%20Caotico)
- **Physics:** Euler-Lagrange equations of motion for 3 coupled rigid bars ($6\times 6$ mass-inertia matrix).
- **Features:** Symplectic/adaptive RK45 integration, Lyapunov divergence verification, FM synthesis tracking velocity $f_c(t)$ and kinetic shock chimes.

### 3. [Mathematics: Geometric Complex Fourier Series](06%20Matematicas%20y%20Geometria/01%20Series%20de%20Fourier%20Geometricas)
- **Physics:** Complex analysis $c_n = \frac{1}{T} \oint \gamma(t) e^{-i n \omega_0 t} dt$, nested epicycle orbits.
- **Features:** Smooth closed-curve decomposition for regular circles, 5-point hypocycloid stars, and symmetric octagons. Progressive harmonic superposition.

### 4. [Complex Analysis: 3D Euler Identity](06%20Matematicas%20y%20Geometria/02%20Identidad%20de%20Euler%203D)
- **Physics:** $e^{i\theta} = \cos\theta + i\sin\theta$, $e^{i\pi} + 1 = 0$, helical geometry in $\mathbb{R} \times \mathbb{C}$.
- **Features:** 3D rotational camera views, orthogonal Euclidean projections, Taylor series convergence comparison, and reactive audio pitch modulation.

---

## 🎨 Visual Standard: Cybernetic HUD & Zero Text Overlap

- **Mathematical Padding:** All HUD telemetry cards, formulas, and labels use strict bounding box calculation to ensure $0\%$ overlap with physical phenomena.
- **Vertical 9:16 Optimization:** Designed natively for TikTok, Instagram Reels, and YouTube Shorts (1080x1920 @ 60 FPS) respecting UI safe zones.
- **High-Contrast Palette:**
  - Deep Space Lattice: `#0a0a0c`
  - Electric Cyan: `#00f0ff`
  - Vorticity / Kinetic Magenta: `#ff007f`
  - Euler Amber: `#ffaa00`
  - Emerald Resonance: `#00ff88`

---

## 🧪 Global Verification & Unit Testing

Execute all 20 physics, mathematics, and benchmark test suites across submodules in isolated environments:

```bash
python run_tests.py
```

```text
============================================================
 CONTINUUM LAB — GLOBAL VERIFICATION TEST RUNNER
============================================================

[RUNNING SUITE] 01 Mecanica de Fluidos\01 LBM D2Q9 Karman Vortex\tests
[PASS] 01 Mecanica de Fluidos\01 LBM D2Q9 Karman Vortex\tests passed successfully.

[RUNNING SUITE] 02 Dinamica y Vibraciones\01 Pendulo Triple Caotico\tests
[PASS] 02 Dinamica y Vibraciones\01 Pendulo Triple Caotico\tests passed successfully.

[RUNNING SUITE] 06 Matematicas y Geometria\01 Series de Fourier Geometricas\tests
[PASS] 06 Matematicas y Geometria\01 Series de Fourier Geometricas\tests passed successfully.

[RUNNING SUITE] 06 Matematicas y Geometria\02 Identidad de Euler 3D\tests
[PASS] 06 Matematicas y Geometria\02 Identidad de Euler 3D\tests passed successfully.

============================================================
 ALL SUITES PASSED (20/20 physical and mathematical tests green)
============================================================
```

---

## 📜 License & Community

- **License:** MIT Open Source License. See [`LICENSE`](LICENSE) for details.
- **Maintainer Profile:** [RoPP17 on GitHub](https://github.com/RoPP17)
- **Repository:** [Continuum-Lab](https://github.com/RoPP17/Continuum-Lab)
- **Official Socials:**
  - Instagram: [@continuumlab_](https://www.instagram.com/continuumlab_/)
  - TikTok: [@continuum.lab](https://www.tiktok.com/@continuum.lab)
