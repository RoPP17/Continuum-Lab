# 02 Mecanismo con Aceleración de Coriolis — 2 Barras con Collarín Deslizante

<div align="center">

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![HTML5 Canvas](https://img.shields.io/badge/Canvas-120%20FPS-00F0FF.svg?style=for-the-badge&logo=html5&logoColor=white)](src/visualization/web/)
[![Pygame](https://img.shields.io/badge/Pygame-2.6.1-brightgreen.svg?style=for-the-badge&logo=python&logoColor=white)](src/visualization/pygame_app.py)
[![Tests Passing](https://img.shields.io/badge/Tests-100%25%20Passing-brightgreen.svg?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![Excel Benchmark](https://img.shields.io/badge/OpenPyXL-Dynamic%20XLSX-107C41.svg?style=for-the-badge&logo=microsoftexcel&logoColor=white)](src/excel/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](../../LICENSE)

<br/>

**Simulación cinemática rigurosa y visualización hipnótica de un mecanismo de retorno rápido con aceleración de Coriolis.**  
*Descomposición vectorial completa de los 5 términos de aceleración en marcos móviles, estelas fosforescentes persistentes, osciloscopio en tiempo real y modelo dinámico en Excel.*

</div>

---

## 🔬 Formulación Analítica de la Aceleración de Coriolis

La aceleración absoluta del collarín $A$ articulado a la manivela $O_1 A$ observada desde el marco rotativo solidario a la barra ranurada $O_2 B$ (rotando a $\vec{\omega}_2 = \dot{\theta}_2 \hat{k}$) se rige por:

$$\vec{a}_A = \vec{a}_{O_2} + \underbrace{\vec{\alpha}_2 \times \vec{r}_{A/O_2}}_{\vec{a}_{\text{Euler}}} + \underbrace{\vec{\omega}_2 \times (\vec{\omega}_2 \times \vec{r}_{A/O_2})}_{\vec{a}_{\text{centrípeta}}} + \underbrace{2\,\vec{\omega}_2 \times \vec{v}_{rel}}_{\vec{a}_{\text{Coriolis}}} + \underbrace{\vec{a}_{rel}}_{\ddot{r}_2\,\hat{u}_{r2}}$$

### Componente Exacto de Coriolis:
$$\vec{a}_{\text{Coriolis}} = 2\,\omega_2\,\dot{r}_2\,\hat{u}_{\theta 2} = 2\,\omega_2\,\dot{r}_2 \begin{pmatrix} -\sin\theta_2 \\ \cos\theta_2 \end{pmatrix}$$

* **Ortogonalidad rigurosa:** $\vec{a}_{\text{Coriolis}} \cdot \hat{u}_{r2} \equiv 0$ (siempre perpendicular a la barra ranurada).
* **Precisión de máquina:** Error residual $\|\vec{a}_A - \vec{a}_{\text{rec}}\| < 10^{-14}\,\mathrm{m/s^2}$.

---

## 🚀 Arquitectura y Módulos

```
02 Mecanismo Coriolis Collarin/
├── src/
│   ├── physics/
│   │   ├── coriolis_kinematics.py     # Solucionador analítico vectorial exacto
│   │   └── harmonic_motion.py         # Análisis armónico FFT y órbitas en plano de fase
│   ├── visualization/
│   │   ├── pygame_app.py              # Visualizador de escritorio a 60 FPS con estelas
│   │   ├── generate_plots.py          # Gráficos diagnósticos de publicación a 300 DPI
│   │   └── web/                       # Simulador Web interactivo e hipnótico (120 FPS)
│   │       ├── index.html             # Interfaz HUD Cyberpunk Obsidian
│   │       ├── style.css              # Estilos futuristas con degradados y glow
│   │       ├── simulation.js          # Renderizador Canvas con floración de vectores
│   │       └── physics_engine.js      # Port analítico en JavaScript ES6
│   └── excel/
│       └── export_coriolis_benchmark.py # Modelo dinámico en Excel (OpenPyXL)
├── tests/
│   └── test_coriolis.py               # Suite de 8 tests unitarios rigurosos (Pytest)
├── docs/
│   └── TEORIA_MECANISMO_CORIOLIS.md   # Deducción matemática detallada paso a paso
├── main.py                            # Orquestador maestro de la simulación
├── run.bat                            # Lanzador directo de un clic para Windows
└── README.md                          # Este documento
```

---

## 💻 Modos de Ejecución

### 1. Simulador Web Interactivo Hipnótico (Recomendado)
Abre un servidor local ultraligero y despliega la aplicación web en tu navegador:
```bash
python main.py --web
```
* Control de velocidad en tiempo real ($\omega_1$), separación ($d$), longitud ($L_1$) y extensión de estela.
* Presets: *Oscilador Armónico*, *Retorno Whitworth*, *Vórtice Crítico*, *Espirógrafo Sagrado*.
* Capas vectoriales activables con bloom luminiscente: Coriolis, Deslizamiento, Centrípeta, Euler y Total.
* Osciloscopio y retrato de fase ($\dot{r}_2$ vs $\omega_2$) en vivo.

### 2. Aplicación de Escritorio Pygame (60 FPS)
```bash
python main.py --pygame
```
* **Controles:**
  * `[ESPACIO]`: Pausar / Reanudar.
  * `[↑ / ↓]`: Ajustar velocidad angular de manivela.
  * `[← / →]`: Modificar distancia $d$ entre pivotes.
  * `[1, 2, 3, 4]`: Alternar entre presets cinemáticos.
  * `[C / V / A]`: Alternar visibilidad de vectores.
  * `[S]`: Guardar captura en alta resolución en `RENDERS/Coriolis_Mechanism/`.

### 3. Generación de Gráficos de Publicación (300 DPI)
```bash
python main.py --plots
```
Genera un panel diagnóstico de 6 cuadrantes guardado en `RENDERS/Coriolis_Mechanism/Coriolis_Kinematics_Diagnostic_300DPI.png`.

### 4. Exportación del Modelo Dinámico de Excel (XLSX)
```bash
python main.py --excel
```
Genera el libro de cálculo con fórmulas dinámicas nativas (`COS`, `SIN`, `SQRT`, `ATAN2`, `MAX`, `AVERAGE`), formato oscuro profesional y compatibilidad completa con Microsoft Excel.

### 5. Verificación de Tests Automatizados
```bash
python main.py --test
```
Ejecuta los 8 tests matemáticos de cierre de lazo, ortogonalidad de Coriolis y derivadas analíticas contra diferencias finitas.
