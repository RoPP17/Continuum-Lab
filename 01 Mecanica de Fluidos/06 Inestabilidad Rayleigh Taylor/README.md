# 06 Inestabilidad Rayleigh-Taylor y Plumas Gravitatorias

<div align="center">

![Inestabilidad Rayleigh-Taylor Hero Cover](../../RENDERS/21%20Inestabilidad%20Rayleigh%20Taylor%20y%20Plumas%20Gravitatorias/extra/capturas/rayleigh_taylor_hero.png)

[![Discipline: Fluid Mechanics](https://img.shields.io/badge/Discipline-Fluid%20Mechanics-00F0FF.svg?style=for-the-badge)](../../01%20Mecanica%20de%20Fluidos)
[![Physics: Baroclinic Vorticity](https://img.shields.io/badge/Physics-Baroclinic%20Torque-FF007F.svg?style=for-the-badge)](https://en.wikipedia.org/wiki/Rayleigh%E2%80%93Taylor_instability)
[![Turbulence: Dimonte Mixing](https://img.shields.io/badge/Model-Dimonte--Schneider%20Law-00FF88.svg?style=for-the-badge)](https://doi.org/10.1063/1.870309)
[![Status: Verified](https://img.shields.io/badge/Tests-7%2F7%20Passing-brightgreen.svg?style=for-the-badge)](tests/test_rayleigh_taylor.py)

</div>

---

## 🔬 Fundamentación Física y Teórica

La **Inestabilidad de Rayleigh-Taylor (RTI)** ocurre cuando un fluido de mayor densidad ($\rho_2$) reposa sobre un fluido más ligero ($\rho_1$) en presencia de un campo gravitatorio vertical descendente $\mathbf{g} = -g \hat{\mathbf{j}}$ (o cuando un fluido ligero acelera empujando a uno pesado).

### 1. Ecuaciones Gobernantes y Torque Baroclínico
Bajo la aproximación de Boussinesq para fluidos incompresibles con densidad variable $\rho(x, y, t) = \rho_1 + (\rho_2 - \rho_1) C(x, y, t)$, la ecuación de transporte de vorticidad $\boldsymbol{\omega} = \nabla \times \mathbf{u} = \omega \hat{\mathbf{k}}$ es:

$$\frac{\partial \omega}{\partial t} + (\mathbf{u} \cdot \nabla)\omega = \underbrace{\frac{1}{\rho^2} (\nabla\rho \times \nabla p)_z}_{\text{Torque Baroclínico}} + \nu \nabla^2 \omega$$

Sustituyendo el gradiente hidrostático de presión $\nabla p \approx -\bar{\rho} g \hat{\mathbf{j}}$ y el número de Atwood $A = \frac{\rho_2 - \rho_1}{\rho_2 + \rho_1}$:

$$\frac{\partial \omega}{\partial t} + (\mathbf{u} \cdot \nabla)\omega = - 2 A g \frac{\partial C}{\partial x} + \nu \nabla^2 \omega$$

$$\frac{\partial C}{\partial t} + (\mathbf{u} \cdot \nabla)C = D \nabla^2 C$$

$$\nabla^2 \psi = -\omega, \quad u = \frac{\partial \psi}{\partial y}, \quad v = -\frac{\partial \psi}{\partial x}$$

El término $-2 A g \frac{\partial C}{\partial x}$ inyecta pares de vórtices contra-rotativos en los flancos de cualquier perturbación interfacial:
- Donde $\frac{\partial C}{\partial x} > 0$: Se genera vorticidad horaria ($\omega < 0$).
- Donde $\frac{\partial C}{\partial x} < 0$: Se genera vorticidad anti-horaria ($\omega > 0$).
Este dipolo vorticial induce una corriente descendente que proyecta el fluido pesado hacia abajo formando **dedos o picos penetrantes** (*spikes*), mientras el fluido ligero asciende formando **burbujas** (*bubbles*).

### 2. Análisis de Dispersión Lineal (Chandrasekhar 1961)
Para una perturbación interfacial $\eta(x, t) = \hat{\eta} e^{\gamma t + i k x}$ con tensión interfacial $\sigma$ y viscosidad $\nu$:

$$\gamma^2(k) = A g k - \frac{\sigma k^3}{\rho_1 + \rho_2}$$

- **Número de onda de corte capilar ($k_c$):**
  $$k_c = \sqrt{\frac{(\rho_2 - \rho_1) g}{\sigma}}, \quad \lambda_c = 2\pi \sqrt{\frac{\sigma}{(\rho_2 - \rho_1) g}}$$
- **Número de onda más inestable ($k_{max}$):**
  $$k_{max} = \frac{k_c}{\sqrt{3}} = \sqrt{\frac{(\rho_2 - \rho_1) g}{3\sigma}}, \quad \lambda_{max} = \sqrt{3} \lambda_c$$
- **Tasa máxima de crecimiento lineal ($\gamma_{max}$):**
  $$\gamma_{max} = \left[ \frac{4}{27} \frac{(A g)^3 (\rho_1 + \rho_2)}{\sigma} \right]^{1/4}$$

### 3. Régimen No-Lineal e Inestabilidad Secundaria Kelvin-Helmholtz
Cuando la amplitud supera $\eta \sim 0.1 \lambda$:
1. **Velocidad terminal de las burbujas (Fórmula de Davies-Taylor):**
   $$v_b = C \sqrt{A g \lambda}, \quad C \approx 0.23 - 0.30$$
2. **Plumas de Champiñón:**
   La cizalladura vertical extrema entre los dedos pesados que caen y el fluido ligero que asciende desestabiliza la interfaz mediante **Inestabilidad de Kelvin-Helmholtz secundaria**, enrollando los extremos en vórtices espirales con silueta de champiñón.

### 4. Régimen Turbulento y Ley de Dimonte-Schneider
En la etapa tardía, las escalas se mezclan turbulentamente y el espesor de la capa de mezcla $h(t)$ sigue una ley auto-similar cuadrática:

$$h(t) = \alpha A g t^2$$

donde $\alpha \approx 0.05 - 0.07$ es el coeficiente universal de mezcla interfacial medido experimentalmente y en simulaciones numéricas directas (DNS).

---

## 📊 Arquitectura del Módulo

```text
06 Inestabilidad Rayleigh Taylor/
├── README.md                           # Fundamentación teórica y documentación
├── main.py                             # Master CLI y pipeline de renderizado
├── src/
│   ├── __init__.py
│   ├── physics/
│   │   ├── __init__.py
│   │   ├── rayleigh_taylor_sim.py      # Solucionador pseudo-espectral 2D con torque baroclínico
│   │   └── export_excel_benchmark.py   # Benchmark dinámico Excel (.xlsx) con fórmulas dinámicas
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── render_rayleigh_taylor.py   # Renderizador 1080x1920 @ 60 FPS con HUD cyber
│   └── audio/
│       ├── __init__.py
│       └── rayleigh_taylor_audio.py    # Síntesis procedural estéreo 44.1 kHz (drone + celesta)
└── tests/
    ├── __init__.py
    └── test_rayleigh_taylor.py         # Suite completa de verificación física (7/7 green)
```
