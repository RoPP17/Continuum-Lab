# 01 Pendulo Triple Caotico — Simulación Dinámica Lagrangiana

<div align="center">

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Manim Community](https://img.shields.io/badge/Manim-0.21.0-FF4500.svg?style=for-the-badge)](https://www.manim.community/)
[![Tests](https://img.shields.io/badge/Tests-100%25%20Passing-brightgreen.svg?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](../../LICENSE)

<br/>

**Simulación no lineal de 3 grados de libertad gobernada por las ecuaciones de Euler-Lagrange.**  
*Trazado de trayectorias caóticas continuas en formato TikTok 9:16 (1080x1920 @ 60 FPS) con conservación de energía hamiltoniana.*

</div>

---

## 🔬 Ecuaciones de Movimiento

$$\mathcal{L}(\boldsymbol{\theta}, \dot{\boldsymbol{\theta}}) = T - V$$

$$\mathbf{M}(\boldsymbol{\theta})\,\ddot{\boldsymbol{\theta}} = \mathbf{F}(\boldsymbol{\theta}, \dot{\boldsymbol{\theta}})$$

* **Integrador:** Runge-Kutta de 4to Orden (RK4) con sub-stepping para conservación de energía $\Delta E / E_0 < 10^{-5}$.
* **Salidas:** Enrutadas automáticamente a `RENDERS/2 Pendulo Triple Trayectoria Caotica/`.
