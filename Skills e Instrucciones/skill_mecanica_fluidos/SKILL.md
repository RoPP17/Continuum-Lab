---
name: mecanica-fluidos-avanzada
description: Advanced analytical and numerical fluid mechanics foundations (Navier-Stokes, Lattice Boltzmann D2Q9, BGK collision, Chapman-Enskog expansion, boundary layers, lubrication, vorticity dynamics, and hydrodynamic force telemetry).
---

# Mecánica de Fluidos Avanzada (`mecanica-fluidos-avanzada`)

Esta skill resume las directrices físico-matemáticas rigurosas para la simulación en Continuum Lab.

---

## 1. Ecuaciones Fundamentales

### 1.1 Navier-Stokes Incompresible
$$\nabla \cdot \mathbf{u} = 0$$
$$\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u}\cdot\nabla)\mathbf{u} = -\frac{1}{\rho_0}\nabla p + \nu \nabla^2 \mathbf{u}$$

### 1.2 Transporte de Vorticidad ($\boldsymbol{\omega} = \nabla \times \mathbf{u}$)
En flujo 2D plano, el término de estiramiento y torsión de vórtices se anula idénticamente:
$$\frac{D\omega_z}{Dt} = \nu \nabla^2 \omega_z$$

---

## 2. Lattice Boltzmann D2Q9-BGK

### 2.1 Ecuación Cinética Discreta
$$f_i(\mathbf{x} + \mathbf{c}_i \Delta t, t + \Delta t) = f_i(\mathbf{x}, t) - \frac{1}{\tau}\left[f_i(\mathbf{x}, t) - f_i^{(eq)}(\mathbf{x}, t)\right]$$

### 2.2 Relajación y Viscosidad Reticular
$$\nu = \frac{2\tau - 1}{6} \iff \tau = 3\nu + 0.5 \quad (\tau > 0.505 \text{ para estabilidad})$$

### 2.3 Equilibrio de Maxwell-Boltzmann
$$f_i^{(eq)} = w_i \rho \left[1 + 3(\mathbf{c}_i \cdot \mathbf{u}) + \frac{9}{2}(\mathbf{c}_i \cdot \mathbf{u})^2 - \frac{3}{2}|\mathbf{u}|^2\right]$$

### 2.4 Telemetría de Fuerzas (Momentum Exchange Method)
$$\mathbf{F}_{MEM} = \sum_{\text{enlaces}} 2\,\mathbf{c}_i\,f_i^*(\mathbf{x}_{\text{fluido}}, t)$$
$$C_D = \frac{F_x}{\frac{1}{2}\rho_0 U_\infty^2 D}, \quad C_L = \frac{F_y}{\frac{1}{2}\rho_0 U_\infty^2 D}$$

---

## 3. Escalamiento Adimensional
* **Número de Reynolds:** $Re = \frac{U_\infty D}{\nu}$
* **Número de Mach:** $Ma = \frac{U_\infty}{c_s} < 0.15$ (condición incompresible)
* **Número de Strouhal:** $St = \frac{f_s D}{U_\infty} \approx 0.18 - 0.20$ a $Re = 150$
