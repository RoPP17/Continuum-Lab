# CONTINUUM LAB — Senior Computational Physics & Visual Engineering Architecture

<div align="center">

<img src="RENDERS/1%20Vortices%20de%20von%20Karman/extra/capturas/karman_vortex_hud_hero.png" width="680" alt="Continuum Lab Computational Physics"/>

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
│   ├── 01 LBM D2Q9 Karman Vortex/           # LBM D2Q9 shedding, moving cylinder & reactive audio
│   └── 05 Efecto Magnus y Rotor Flettner/   # Kutta-Joukowski lift, stagnation bifurcation & Flettner ship
├── 02 Dinamica y Vibraciones/               # Non-linear dynamics, chaos & multi-body mechanics
│   ├── 01 Pendulo Triple Caotico/           # 6-DOF Lagrangian integrator & FM reactive synthesis
│   ├── 04 Efecto Dzhanibekov 3D/            # Euler intermediate axis instability & Tennis Racket theorem
│   ├── 05 Mecanismo Peaucellier Lipkin/     # 1864 exact straight line, complex inversion & zero error
│   ├── 06 Problema de los Tres Cuerpos Caotico/ # Moore-Chenciner figure-8, non-integrability, chaos & rogue star ejection
│   └── 07 Atractor de Lorenz y Efecto Mariposa 3D/ # 1963 atmospheric convection chaos, Liouville contraction & D_KY=2.0621
├── 03 Mecanica de Solidos/                  # Elasticity, plate theory & structural dynamics
│   └── 01 Placas de Chladni y Resonancia Acustica/ # Kirchhoff-Love biharmonic elastodynamics & 15,000 granular particles
├── 04 Termodinamica y Calor/                # Thermodynamics, conduction, heat diffusion & entropy
│   └── 01 Ley Cero de la Termodinamica 3 Cuerpos/ # Multi-material 3-body conduction, Zeroth law proof
├── 06 Matematicas y Geometria/              # Pure & applied mathematics, geometry, complex analysis
│   ├── 01 Series de Fourier Geometricas/    # Complex epicycle decomposition (Circle, Star, Octagon)
│   └── 02 Identidad de Euler 3D/            # Helix on complex cylinder, Taylor convergence & projections
├── CARRUSELES/                              # High-impact educational carousels (4:5 format for IG / TikTok)
│   ├── 1 Dinamica Analitica y Mecanica Lagrangiana/
│   └── 2 Ecuacion de Navier Stokes/
├── RENDERS/                                 # Numerical benchmarks & high-resolution captures
│   ├── 1 Vortices de von Karman/extra/      # Dynamic Excel models (.xlsx), telemetry & screenshots
│   ├── 2 Pendulo Triple Trayectoria Caotica/extra/
│   ├── 3 Series de Fourier Geometricas/extra/
│   ├── 4 Identidad de Euler 3D/extra/
│   ├── 10 Efecto Dzhanibekov 3D/extra/      # 1080x1920 covers, dynamic Excel benchmark & 60 FPS video
│   └── 14 Ley Cero Termodinamica 3 Cuerpos/ # 1080x1920 covers, dynamic Excel benchmark & GIF preview
├── run_tests.py                             # Global verification test runner (all tests green)
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

### 5. [Thermodynamics: Zeroth Law & Multi-Material Heat Diffusion](04%20Termodinamica%20y%20Calor/01%20Ley%20Cero%20de%20la%20Termodinamica%203%20Cuerpos)
- **Physics:** 2D finite-volume Fourier heat equation $\rho c_p \frac{\partial T}{\partial t} = \nabla \cdot (k \nabla T)$ across 3 contiguous solids: Copper ($100^\circ\text{C}$), Stainless Steel ($25^\circ\text{C}$), and Aluminum ($0^\circ\text{C}$). Conservative harmonic interface conductividades $k_{int} = \frac{2 k_1 k_2}{k_1 + k_2}$.
- **Features:** Closed-form First Law benchmark ($T_{eq} = 46.2^\circ\text{C}$), dynamic heat flux arrows ($\mathbf{q} = -k\nabla T$), kinetic phonon streamlets, exact energy conservation ($\Delta E/E_0 < 10^{-5}$), and synchronized 84 BPM cinematic ambient science soundtrack with equilibrium resolution chime.

### 6. [Rotational Dynamics: Dzhanibekov Effect & Tennis Racket Theorem](02%20Dinamica%20y%20Vibraciones/04%20Efecto%20Dzhanibekov%203D)
- **Physics:** Rigid-body Euler rotational equations with principal moments $I_1 = 1.0 < I_2 = 2.4 < I_3 = 4.2\text{ kg}\cdot\text{m}^2$.
- **Features:** Intermediate axis hyperbolic instability, Poinsot homoclinic separatrix, periodic 180° acrobatic flips under zero external torque ($\tau = 0$), exact energy and angular momentum conservation ($|\mathbf{L}| = 28.80\text{ N}\cdot\text{m}\cdot\text{s}$, $E_{rot} = 172.8\text{ J}$), and procedural microgravity reactive audio.

### 7. [Classical Mechanics: 3D Gyroscopic Precession & Nutation](02%20Dinamica%20y%20Vibraciones/03%20Precesion%20Giroscopica%203D)
- **Physics:** Heavy symmetric top on a point pivot governed by Euler's rotational equations $\boldsymbol{\tau}_g = \mathbf{r}_{cm} \times (m\mathbf{g}) = \frac{d\mathbf{L}}{dt}$.
- **Features:** 10,000 RPM high-speed rotor ($I_z = 0.04050\text{ kg}\cdot\text{m}^2$, $I_x = 0.17650\text{ kg}\cdot\text{m}^2$), torque-induced steady horizontal precession ($\Omega_p = 1.10\text{ rad/s}$), transient cycloidal nutation cusps ($\omega_n = 5.60\text{ rad/s}$), and 14.0s procedural turbine whine + nutation acoustic synthesis.

### 8. [Kinematics & Machine Theory: Peaucellier-Lipkin Exact Straight-Line Mechanism](02%20Dinamica%20y%20Vibraciones/05%20Mecanismo%20Peaucellier%20Lipkin)
- **Physics:** Planar inversion geometry in the complex plane: $OP \cdot OP' = R^2 - l^2 = k = 5.28\text{ cm}^2$.
- **Features:** 8-bar linkage (7 moving links + 1 ground) with zero sliding guides, converts circular crank rotation of $P$ into a mathematically exact Euclidean straight line traced by $P'$ ($x = 1.1059\text{ cm}$), zero linear deviation ($\varepsilon = 0.00000000\text{ mm}$), strict mobile safe-zone HUD, and procedural mechanical linkage + laser crystallization audio @ 60 FPS.

### 9. [Solid Mechanics: Chladni Plate Cymatics & Kirchhoff-Love Elastodynamics](03%20Mecanica%20de%20Solidos/01%20Placas%20de%20Chladni%20y%20Resonancia%20Acustica)
- **Physics:** 4th-order biharmonic plate equation $D \nabla^4 w + \rho h \frac{\partial^2 w}{\partial t^2} = 0$, bending rigidity $D = \frac{E h^3}{12(1-\nu^2)}$.
- **Features:** Modal sweep from Mode $(1, 3)$ ($432\text{ Hz}$) to Mode $(5, 5)$ ($4320\text{ Hz}$), acoustic radiation pressure driving 15,000 Lagrangian particles strictly towards zero-displacement nodal lines $w(x, y) = 0$, dynamic Excel trade study across Titanium Gr5, SS 304, Al 6061-T6, and procedural 44.1 kHz stereo resonance soundtrack.

### 10. [Chaos & Celestial Mechanics: The Gravitational Three-Body Problem](02%20Dinamica%20y%20Vibraciones/06%20Problema%20de%20los%20Tres%20Cuerpos%20Caotico)
- **Physics:** Newtonian 3-body gravitational interaction $\mathbf{F}_i = \sum_{j \neq i} G \frac{m_i m_j}{|\mathbf{r}_j - \mathbf{r}_i|^3}(\mathbf{r}_j - \mathbf{r}_i)$, Poincaré non-integrability, and Hamiltonian conservation $E = T + V = \text{const}$.
- **Features:** Moore-Chenciner (2000) Figure-8 periodic choreography, micro-perturbation ($\Delta r = 10^{-4}$) triggering Lyapunov exponential divergence, dynamic gravitational force vector lasers, hyper-velocity slingshot encounters, and escape velocity ejection of an interstellar rogue star @ 60 FPS.

### 11. [Non-Linear Chaos Theory: 3D Lorenz Strange Attractor & The Butterfly Effect (1963)](02%20Dinamica%20y%20Vibraciones/07%20Atractor%20de%20Lorenz%20y%20Efecto%20Mariposa%203D)
- **Physics:** Edward N. Lorenz's 1963 thermal convection system ($\dot{x} = \sigma(y-x)$, $\dot{y} = x(\rho-z)-y$, $\dot{z} = xy-\beta z$) with $\sigma = 10, \rho = 28, \beta = 8/3$, Liouville phase-space contraction $\nabla \cdot \mathbf{F} = -41/3 \approx -13.67\text{ s}^{-1}$, and Kaplan-Yorke fractal dimension $D_{KY} = 2.0621$.
- **Features:** Twin micro-perturbed orbits ($\Delta_0 = 10^{-4}$ reproducing Lorenz's Royal McBee rounding truncation) plus a 60-particle golden ensemble, 3D perspective camera rotation, live Lorenz $x(t)$ dual-waveform oscilloscope, and binaural stereo FM sound synthesis @ 60 FPS.

### 12. [Fluid Dynamics & Aerodynamics: The Magnus Effect & Flettner Rotor](01%20Mecanica%20de%20Fluidos/05%20Efecto%20Magnus%20y%20Rotor%20Flettner)
- **Physics:** Potential flow with circulation $w(z) = U_\infty(z + R^2/z) - \frac{i\Gamma}{2\pi}\ln(z/R)$, Kutta-Joukowski Lift Theorem $L' = \rho_\infty U_\infty \Gamma$, and stagnation point topological bifurcation from surface dual points ($\alpha < 2$) to detached hyperbolic saddle point ($\alpha > 2$).
- **Features:** 2,400 velocity-colored particle tracers, rotating cylinder with dynamic spokes and boundary layer slip, live surface pressure $C_p(\theta)$ polar oscilloscope, industrial fuel-saving benchmark for a 50,000 DWT Flettner bulk carrier, and procedural wind + motor whine stereo audio @ 60 FPS.

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

---

## 📚 Academic Citation & Research Software

If you use **Continuum-Lab** in your academic research, university coursework, or engineering simulations, please cite it as:

``bibtex
@software{pepe_sanchez_2026_continuum_lab,
  author       = {Pepe Sánchez, Roberto Andrés},
  title        = {Continuum-Lab: High-Performance GPU-Accelerated Computational Physics and Continuum Mechanics Suite},
  month        = oct,
  year         = 2026,
  publisher    = {Zenodo},
  version      = {v1.0.0},
  url          = {https://github.com/RoPP17/Continuum-Lab}
}
``

You can also cite this project automatically through GitHub's **"Cite this repository"** button or via [CITATION.cff](./CITATION.cff).
