# CONTINUUM LAB — DISTRIBUTION & SOCIAL DISSEMINATION KIT
**Project:** Lattice Boltzmann D2Q9 Vortex Shedding Engine (von Kármán Street)  
**Author:** Roberto Andrés Pepe Sánchez (@RoPP17)  
**License:** MIT  

---

## 1. REDDIT POSTS

### Subreddit: `r/Python`
**Title:** I built a real-time CUDA Lattice Boltzmann fluid simulation in Python with live aerodynamic force telemetry (RTX 5070 + Taichi Lang) [Open Source]

**Body:**
```markdown
Hey everyone! Over the past few weeks, I've been developing **Continuum Lab**, an open-source computational physics project focused on simulating continuum mechanics and fluid dynamics directly on the GPU using Python.

This project implements a 2D 9-velocity (**D2Q9-BGK**) Lattice Boltzmann solver that directly recovers the incompressible Navier-Stokes equations at low Mach numbers. 

### Key Highlights:
- **NVIDIA CUDA Acceleration via Taichi:** Computes millions of lattice nodes in parallel on an RTX 5070 at 60+ FPS.
- **Aerodynamic Telemetry (MEM):** Computes instantaneous lift ($C_L$) and drag ($C_D$) forces using the Momentum Exchange Method across the solid boundary.
- **Live Phase Portrait:** Displays the limit cycle bifurcation in real-time as von Kármán vortex shedding develops ($Re = 150$).
- **Cybernetic Visuals:** Custom colormap mapping with non-linear hyperbolic contrast ($\tanh(\omega_z / \omega_0)$) so delicate vortex filaments remain visible without saturating boundary layers.
- **Pure NumPy CPU Fallback:** Works on any machine without GPU requirements.
- **100% Test Coverage:** Verified with pytest for lattice tensor moments and mass conservation.

GitHub Repository: https://github.com/RoPP17/Continuum-Lab

Would love to hear your thoughts, CFD tips, or feature requests!
```

---

### Subreddit: `r/physicsgifs` or `r/simulated`
**Title:** [OC] Real-time von Kármán vortex street past a circular cylinder at Re=150 with live drag/lift phase portrait (Lattice Boltzmann D2Q9)

**Comment to pin:**
```markdown
Simulated using an in-house Lattice Boltzmann D2Q9 solver written in Python and compiled to CUDA via Taichi. 

Vorticity fields are color-mapped using a cybernetic dark theme: electric cyan represents counter-clockwise rotation, while magenta represents clockwise shedding. The bottom-right card tracks the $(C_D, C_L)$ limit cycle in real time.

Code and derivations: https://github.com/RoPP17/Continuum-Lab
```

---

## 2. LINKEDIN POST

```markdown
🚀 Excited to unveil **Continuum Lab**: an open-source computational physics and visual engineering framework developed in Python, designed to simulate and visualize fluid dynamics with mathematical rigor.

Our first module simulates the classical **von Kármán Vortex Street** past a circular cylinder using the **Lattice Boltzmann Method (LBM D2Q9-BGK)** accelerated on NVIDIA CUDA cores:

🔹 **Mesoscopic Kinetic Modeling:** Solving kinetic particle distributions ($f_i$) to recover the incompressible Navier-Stokes equations without costly Poisson pressure solves.
🔹 **Dynamic Force Telemetry:** Computing instantaneous lift ($C_L$) and drag ($C_D$) coefficients via the Momentum Exchange Method (MEM) at the fluid-solid boundary.
🔹 **GPU Compute:** Leveraging Taichi Lang to execute JIT-compiled CUDA kernels on an NVIDIA RTX 5070 GPU.
🔹 **Autonomous Engineering Pipeline:** Includes automated pytest suites and dynamic Excel benchmark models (`openpyxl`) with zero hardcoded formulas.

As a mechanical engineering student at Universidad Técnica de Ambato, I believe scientific software should be both mathematically transparent and visually compelling.

Check out the code, technical report, and benchmarks on GitHub:
🔗 https://github.com/RoPP17/Continuum-Lab

#MechanicalEngineering #CFD #Python #CUDA #Simulation #FluidMechanics #DataVisualization #OpenSource
```

---

## 3. X / TWITTER POST (Thread Starter)

```markdown
Real-time von Kármán vortex street past a cylinder at Re=150 simulated with Lattice Boltzmann (D2Q9) in Python + CUDA 🌊⚡

Features live aerodynamic force telemetry ($C_D$ & $C_L$) via Momentum Exchange, hyperbolic vorticity mapping, and 60 FPS GPU streaming.

Full open-source repo: https://github.com/RoPP17/Continuum-Lab

#Python #CFD #GPU #Physics
```

---

## 4. YOUTUBE SHORTS / INSTAGRAM REELS (9:16 Vertical Video)

**Title:** Real-Time Fluid Dynamics on GPU: von Kármán Vortex Street (Python + CUDA)  
**Description:**
```markdown
Simulating turbulent vortex shedding past a cylinder using the Lattice Boltzmann Method (D2Q9-BGK) running on an NVIDIA RTX 5070 GPU. 

Watch the aerodynamic lift ($C_L$) and drag ($C_D$) form a limit cycle in the live HUD phase portrait.

Full code on GitHub: @RoPP17 / Continuum-Lab

#physics #simulation #fluidmechanics #coding #python #engineering #stem
```
