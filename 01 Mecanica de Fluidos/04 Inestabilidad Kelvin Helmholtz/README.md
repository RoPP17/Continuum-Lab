# Inestabilidad de Kelvin-Helmholtz (KHI) — Navier-Stokes 2D & Dinámica de Vórtices

<div align="center">

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Physics](https://img.shields.io/badge/Physics-Intermediate%20Fluid%20Mechanics-0284C7.svg?style=for-the-badge)](https://github.com/ichristov/intermediate-fluid-mechanics)
[![Resolution](https://img.shields.io/badge/Resolution-1080x1920%20(9:16)-00F0FF.svg?style=for-the-badge)](RENDERS/16%20Inestabilidad%20Kelvin%20Helmholtz/videos/)
[![Tests](https://img.shields.io/badge/Tests-7%2F7%20Passing-brightgreen.svg?style=for-the-badge)](tests/test_kelvin_helmholtz.py)

**Simulación numérica de alta fidelidad de la inestabilidad de cizalladura de Kelvin-Helmholtz mediante integración pseudoespectral RK4 de las ecuaciones de Navier-Stokes incompresibles.**

</div>

---

## 🏛️ Fundamento Teórico y Físico (Mecánica de Fluidos II)

La inestabilidad de Kelvin-Helmholtz (KHI) se origina en la interfaz de dos capas de fluido con velocidades tangenciales relativas ($\Delta U = 2 U_0$). 

### 1. Ecuaciones de Gobierno (Vorticidad - Función de Corriente)
Para un fluido newtoniano incompresible bidimensional ($\nabla \cdot \mathbf{u} = 0$):

$$\frac{\partial \omega}{\partial t} + (\mathbf{u} \cdot \nabla)\omega = \nu \nabla^2 \omega$$

$$\nabla^2 \psi = -\omega, \quad u = \frac{\partial \psi}{\partial y}, \quad v = -\frac{\partial \psi}{\partial x}$$

### 2. Perfil Base de Capa de Cizalladura y Teorema de Rayleigh
El flujo medio corresponde a un perfil de tangente hiperbólica:

$$U(y) = U_0 \tanh\left(\frac{y}{\delta_0}\right)$$

La vorticidad base distribuida es:

$$\omega_0(y) = -\frac{dU}{dy} = -\frac{U_0}{\delta_0} \operatorname{sech}^2\left(\frac{y}{\delta_0}\right)$$

* **Teorema del Punto de Inflexión de Rayleigh:** Un flujo cortante no viscoso paralelo solo puede ser inestable si el perfil de velocidad contiene al menos un punto de inflexión $U''(y_s) = 0$. En $y = 0$:
  $$U''(0) = -\frac{2 U_0}{\delta_0^2} \operatorname{sech}^2(0)\tanh(0) = 0$$
* **Criterio de Fjørtoft:** Condición necesaria de inestabilidad satisfecha:
  $$U''(y) [U(y) - U(0)] < 0 \quad \forall y \neq 0$$

### 3. Criterio de Miles-Howard (Estratificación y Número de Richardson)
Para fluidos con pequeña estratificación de densidad vertical bajo gravedad $g$:

$$Ri(y) = -\frac{g}{\rho} \frac{\frac{\partial \rho}{\partial y}}{\left(\frac{\partial u}{\partial y}\right)^2}$$

* **Teorema de Miles-Howard (1961):** Una condición necesaria para la existencia de modos inestables es:
  $$Ri_{min} < \frac{1}{4} = 0.25$$
  Si $Ri \ge 0.25$ en todo el dominio, la energía potencial gravitatoria estabiliza el flujo e inhibe completamente el crecimiento de vórtices. En nuestra simulación, $Ri \approx 0.142 < 0.25$, activando el régimen inestable.

---

## ⚙️ Arquitectura Numérica y Algorítmica

1. **Inversión de Poisson Espectral:**
   $$\hat{\psi}(\mathbf{k}) = \frac{\hat{\omega}(\mathbf{k})}{|\mathbf{k}|^2}, \quad \hat{u} = i k_y \hat{\psi}, \quad \hat{v} = -i k_x \hat{\psi}$$
   con regla de des-aliasing 2/3 para garantizar estabilidad no lineal estricta.
2. **Integrador Temporal Runge-Kutta de 4to Orden (RK4):**
   Avanza el término advectivo no lineal $-(\mathbf{u}\cdot\nabla)\omega$ y el término de difusión viscosa $\nu \nabla^2 \omega$ con paso de tiempo $dt = 0.003\text{ s}$ respetando la condición CFL ($CFL < 0.4$).
3. **Trazadores Lagrangianos Pasivos:**
   400 partículas de fluido advectadas por interpolación bilineal de velocidad $d\mathbf{x}_p/dt = \mathbf{u}(\mathbf{x}_p)$ con esquema predictor-corrector RK2.
4. **Diseño Sonoro Reactivo (44.1 kHz Estéreo):**
   Sintetizador físico procedural en `src/audio/kelvin_helmholtz_audio.py` que modula viento de cizalla estéreo, resonancia sub-grave con la enstrofia y campanas celestes en los momentos de enrollamiento vórtice.

---

## 📊 Estándar Visual Cybernetic HUD (1080x1920 @ 60 FPS)

* **Zona Segura Superior:** $> 160\text{ px}$ libres para elementos de navegación móvil.
* **Zona Segura Inferior:** $> 220\text{ px}$ libres para subtítulos nativos y barra de progreso.
* **Paleta de Color de Alto Contraste:**
  * Fondo: Deep Space Void `#0a0a0c`
  * Vorticidad antihoraria ($\omega > 0$): Cyan Eléctrico `#00f0ff`
  * Vorticidad horaria ($\omega < 0$): Magenta Neón `#ff007f`
  * Filamentos de cizalla (Braid): Ámbar Cinético `#ffaa00`
  * Curva de Enstrofia: Verde Esmeralda Fosforoso `#20ff3c`

---

## 🧪 Pruebas Unitarias y Verificación

Ejecutar la suite física completa:

```bash
pytest tests/test_kelvin_helmholtz.py -v
```

Ejecutar pipeline maestro:

```bash
python main.py --all
```
