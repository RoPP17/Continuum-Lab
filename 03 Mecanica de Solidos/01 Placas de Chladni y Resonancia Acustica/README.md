# Placas de Chladni y Resonancia Acústica — Teoría de Placas Delgadas de Kirchhoff-Love

<div align="center">

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Physics](https://img.shields.io/badge/Physics-Solid%20Mechanics%20%26%20Elastodynamics-0284C7.svg?style=for-the-badge)](https://github.com/RoPP17/Continuum-Lab)
[![Resolution](https://img.shields.io/badge/Resolution-1080x1920%20(9:16)-00F0FF.svg?style=for-the-badge)](RENDERS/17%20Placas%20de%20Chladni%20y%20Resonancia%20Acustica/videos/)
[![Tests](https://img.shields.io/badge/Tests-5%2F5%20Passing-brightgreen.svg?style=for-the-badge)](tests/test_chladni.py)

**Simulación elastodinámica de alta precisión de placas delgadas vibrantes y auto-organización granular cimática de 15,000 partículas de arena bajo ondas acústicas estacionarias.**

</div>

---

## 🏛️ Fundamento Teórico y Físico (Mecánica de Sólidos & Elastodinámica)

El fenómeno de las figuras de Chladni (Ernst Chladni, 1787; Sophie Germain, 1816) describe la auto-organización de partículas granulares sobre placas elásticas bi-dimensionales excitadas armónicamente por ondas estacionarias.

### 1. Ecuación Diferencial Biarmónica de Kirchhoff-Love
Para una placa homogénea e isótropa de espesor constante $h$, densidad $\rho$, módulo de Young $E$ y coeficiente de Poisson $\nu$:

$$D \nabla^4 w(x, y, t) + \rho h \frac{\partial^2 w(x, y, t)}{\partial t^2} = 0$$

donde el operador biarmónico es:
$$\nabla^4 = \nabla^2 \nabla^2 = \frac{\partial^4}{\partial x^4} + 2\frac{\partial^4}{\partial x^2 \partial y^4} + \frac{\partial^4}{\partial y^4}$$

y la rigidez a la flexión de la placa $D$ está dada por:
$$D = \frac{E h^3}{12 (1 - \nu^2)}$$

### 2. Modos Propios y Solución Analítica de Chladni-Germain
Para una placa cuadrada con bordes libres sujeta a excitación armónica transversal $w(x, y, t) = W(x, y) \cos(\omega t)$, el desplazamiento modal normalizado $W_{mn}(x, y)$ en el dominio $[-L/2, L/2] \times [-L/2, L/2]$ se obtiene mediante la superposición de modos degenerados:

$$W_{mn}(x, y) = a \cos\left(\frac{m \pi x}{L}\right) \cos\left(\frac{n \pi y}{L}\right) - b \cos\left(\frac{n \pi x}{L}\right) \cos\left(\frac{m \pi y}{L}\right)$$

La condición que define las líneas nodales observables (donde la amplitud transversal de oscilación es idénticamente nula) es:

$$W_{mn}(x, y) = 0$$

Las frecuencias naturales discretas correspondientes son:

$$f_{mn} = \frac{\pi}{2 L^2} \sqrt{\frac{D}{\rho h}} (m^2 + n^2) \cdot \alpha_{mn}$$

### 3. Dinámica Granular y Fuerza de Radiación Acústica
Cuando la placa vibra verticalmente con aceleración $a_z(x, y, t) = -\omega^2 W(x, y) \cos(\omega t)$, las partículas de arena de sílice pierden contacto cuando la aceleración descendente supera a la gravedad:

$$a_z(x, y) > g$$

Durante el tiempo de vuelo y rebote inelástico continuo con la placa, el gradiente cuadrático efectivo induce una fuerza de arrastre acústico neta orientada hacia los mínimos de energía de vibración:

$$\vec{F}_{\text{drift}}(x, y) = -\kappa \nabla \left( W_{mn}(x, y)^2 \right) = -2 \kappa W \nabla W$$

Dado que en las líneas nodales $W(x, y) = 0$, la aceleración se anula y la fuerza de arrastre converge a cero, confinando de forma ultra-estable a las 15,000 partículas a lo largo de las curvas geométricas exactas.

---

## ⚙️ Estructura del Módulo

```
03 Mecanica de Solidos/01 Placas de Chladni y Resonancia Acustica/
├── main.py                          # CLI maestro de ejecución y renderizado
├── README.md                        # Documentación teórica y experimental
├── src/
│   ├── physics/
│   │   ├── chladni_sim.py           # Motor elastodinámico y física granular
│   │   └── export_excel_benchmark.py# Generador dinámico de benchmark (.xlsx)
│   ├── audio/
│   │   └── chladni_audio.py         # Síntesis acústica procedural estéreo 44.1 kHz
│   └── visualization/
│       └── render_chladni.py        # Renderizador UHD 9:16 (1080x1920 @ 60 FPS)
└── tests/
    └── test_chladni.py              # Suite de verificación unitaria
```

---

## 🚀 Comandos de Ejecución

### Ejecución completa (Audio, Excel, Videos ES/EN, Capturas Hero):
```bash
python main.py --all
```

### Ejecutar suite de pruebas unitarias:
```bash
pytest tests/ -v
```
