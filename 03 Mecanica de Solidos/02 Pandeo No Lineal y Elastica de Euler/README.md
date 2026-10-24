# 02 Pandeo No Lineal y Elástica de Euler

<div align="center">

[![Discipline: Solid Mechanics](https://img.shields.io/badge/Discipline-Solid%20Mechanics-00F0FF.svg?style=for-the-badge)](../../03%20Mecanica%20de%20Solidos)
[![Physics: Non--Linear Elasticity](https://img.shields.io/badge/Physics-Jacobi%20Elliptic%20Elastica-FF007F.svg?style=for-the-badge)](https://en.wikipedia.org/wiki/Euler%27s_elastica)
[![Bifurcation: Pitchfork](https://img.shields.io/badge/Bifurcation-Supercritical%20Pitchfork-00FF88.svg?style=for-the-badge)](https://doi.org/10.1007/978-1-4612-4206-2)
[![Status: Verified](https://img.shields.io/badge/Tests-7%2F7%20Passing-brightgreen.svg?style=for-the-badge)](tests/test_euler_elastica.py)

</div>

---

## 🔬 Fundamentación Física y Teórica

El pandeo elástico clásico de columnas (Leonhard Euler, 1744) predice la carga crítica bifurcatoria:

$$P_{cr} = \frac{\pi^2 E I}{L^2}$$

Sin embargo, el modelo clásico linealizado aproxima la curvatura mediante la derivada segunda espacial $\kappa \approx \frac{d^2 y}{dx^2}$, asumiendo pendientes infinitesimales $(\frac{dy}{dx})^2 \ll 1$. Dicha hipótesis colapsa de forma catastrófica cuando $P > P_{cr}$, prediciendo flechas infinitas.

En la realidad física de grandes deflexiones, la viga permanece perfectamente elástica y estable en una configuración flexionada finita gobernada por la **Elástica de Euler no lineal exacta**.

---

### 1. Ecuación Diferencial Exacta de la Curvatura
Sea $s \in [0, L]$ la coordenada de longitud de arco y $\theta(s)$ el ángulo que forma la tangente local a la viga con el eje horizontal de compresión. La curvatura geométrica exacta es:

$$\kappa(s) = \frac{d\theta}{ds}$$

Por la ley constitutiva de Bernoulli-Euler para flexión pura:

$$M(s) = E I \frac{d\theta}{ds}$$

Diferenciando con respecto a la longitud de arco $s$ y considerando el equilibrio estático ante una carga de compresión axial $P$:

$$\frac{d M}{ds} = -P \sin\theta(s) \implies E I \frac{d^2\theta}{ds^2} + P \sin\theta = 0$$

> **Isomorfismo Matemático Fundamental:** Esta ecuación diferencial de segundo orden no lineal es **idéntica a la ecuación del péndulo simple gravitatorio no lineal** $\ddot{\theta} + \omega^2 \sin\theta = 0$, donde la longitud de arco $s$ juega el papel del tiempo $t$, y la rigidez normalizada $\sqrt{P / EI}$ actúa como la frecuencia angular $\omega$.

---

### 2. Primera Integral y Conservación de Energía Elástica
Multiplicando por $\frac{d\theta}{ds}$ e integrando respecto a $s$:

$$\frac{1}{2} E I \left(\frac{d\theta}{ds}\right)^2 - P \cos\theta = \text{constante} = -P \cos\alpha$$

donde $\alpha = \theta(0) = -\theta(L)$ representa el ángulo de inclinación máximo en los extremos articulados de la viga (donde el momento flector $M = 0 \implies \frac{d\theta}{ds} = 0$).

Despejando la curvatura:

$$\frac{d\theta}{ds} = \pm \sqrt{\frac{2 P}{E I} (\cos\theta - \cos\alpha)}$$

Utilizando la identidad trigonométrica $\cos\theta = 1 - 2\sin^2(\theta/2)$:

$$\cos\theta - \cos\alpha = 2 \left( \sin^2\frac{\alpha}{2} - \sin^2\frac{\theta}{2} \right) = 2 \left( k^2 - \sin^2\frac{\theta}{2} \right)$$

donde $k = \sin(\alpha / 2) \in (0, 1)$ es el **módulo elíptico**.

---

### 3. Solución Analítica en Integrales Elípticas de Jacobi
Introduciendo la transformación de variable $\sin(\theta/2) = k \sin\phi$, con $\phi \in [-\pi/2, \pi/2]$:

$$\frac{d\phi}{ds} = \sqrt{\frac{P}{E I}} \sqrt{1 - k^2 \sin^2\phi}$$

Integrando a lo largo de media viga ($s \in [0, L/2]$, donde $\phi$ va de $-\pi/2$ a $0$):

$$\sqrt{\frac{P}{E I}} \frac{L}{2} = \int_0^{\pi/2} \frac{d\phi}{\sqrt{1 - k^2 \sin^2\phi}} = K(k)$$

donde $K(k)$ es la **Integral Elíptica Completa de Primera Especie**. Por tanto:

$$\sqrt{\frac{P}{E I}} L = 2 K(k)$$

Elevando al cuadrado y dividiendo entre la carga crítica lineal $P_{cr} = \frac{\pi^2 E I}{L^2}$:

$$\frac{P}{P_{cr}} = \left( \frac{2 K(k)}{\pi} \right)^2$$

* **Límite asintótico de pequeñas deflexiones ($\alpha \to 0 \implies k \to 0$):**
  Dado que $K(0) = \frac{\pi}{2}$, se obtiene:
  $$\lim_{k \to 0} \frac{P}{P_{cr}} = \left( \frac{2 (\pi/2)}{\pi} \right)^2 = 1.000$$
  Demostrando de manera analítica rigurosa cómo la carga crítica de Euler emerge como el punto de bifurcación exacto del sistema no lineal.
* **Capacidad post-pandeo para grandes ángulos:**
  Para $\alpha = 90^\circ$ ($k = \frac{\sqrt{2}}{2} \approx 0.7071$, $K \approx 1.8541$):
  $$\frac{P}{P_{cr}} = \left( \frac{2 \times 1.8541}{\pi} \right)^2 \approx 1.3932$$
  La viga es capaz de soportar hasta un **$39.3\%$ de sobrecarga axial** en equilibrio elástico estable sin colapso.

---

### 4. Coordenadas Cartesianas Paramétricas $(x(s), y(s))$
A partir de la función amplitud de Jacobi $\phi(u) = \text{am}(u, k)$ y las funciones elípticas $\text{sn}, \text{cn}, \text{dn}$:

$$x(s) = \int_0^s \cos\theta(s') ds' = \frac{1}{\omega} \left[ 2 E(\text{am}(u, k), k) - u \right]$$

$$y(s) = \int_0^s \sin\theta(s') ds' = \frac{2 k}{\omega} \left[ 1 - \text{cn}(u, k) \right]$$

donde $\omega = \sqrt{P / EI}$, $u = \omega s - K(k)$, y $E(\phi, k)$ es la Integral Elíptica Incompleta de Segunda Especie.

---

### 5. Estado de Tensiones Combinadas
La fibra exterior crítica soporta tensión normal originada por compresión directa más flexión pura:

$$\sigma_{max}(s) = \underbrace{\frac{P \cos\theta(s)}{A}}_{\text{Compresión Axial}} + \underbrace{E \cdot \left(\frac{h}{2}\right) \cdot \left| \frac{d\theta}{ds} \right|}_{\text{Flexión por Curvatura Local}}$$

---

## 📊 Arquitectura del Módulo

```text
02 Pandeo No Lineal y Elastica de Euler/
├── README.md                           # Fundamentación matemática y formulación elíptica
├── main.py                             # Master CLI y orquestador del módulo
├── output/                             # Entregables generados (PNG, XLSX, WAV)
│   ├── euler_elastica_hero_poster.png  # Póster científico de 3 paneles (Dark Slate / Cyan)
│   ├── Euler_Elastica_Nonlinear_Benchmark.xlsx # Benchmark dinámico con fórmulas nativas
│   └── euler_elastica_bifurcation.wav  # Audio procedural estéreo (44.1 kHz)
├── src/
│   ├── __init__.py
│   ├── physics/
│   │   ├── __init__.py
│   │   ├── euler_elastica_sim.py      # Solucionador elíptico exacto de Jacobi
│   │   └── export_excel_benchmark.py  # Exportador Excel dinámico (openpyxl)
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── render_elastica.py         # Renderizador de perfiles, bifurcación y plano de fase
│   └── audio/
│       ├── __init__.py
│       └── elastica_audio.py          # Síntesis procedural de tono de ablandamiento
└── tests/
    ├── __init__.py
    └── test_euler_elastica.py         # Suite completa de verificación física (7/7 tests)
```

---

## 🚀 Ejecución y Reproducibilidad

1. **Ejecutar suite de verificación física:**
   ```bash
   pytest tests/test_euler_elastica.py -v
   ```

2. **Generar informe y todos los entregables en lote:**
   ```bash
   python main.py --all
   ```
