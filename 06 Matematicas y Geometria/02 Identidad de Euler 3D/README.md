# Continuum Lab — Identidad de Euler en el Espacio Tridimensional $\mathbb{R}^3$ y Proyecciones Canónicas 2D

**División:** 06 Matemáticas y Geometría  
**Módulo:** 02 Identidad de Euler en el Espacio 3D  
**Entregables:** Videos TikTok 9:16 ($1080 \times 1920$ @ 60 FPS), Modelo dinámico en Excel (.xlsx), capturas en ultra-alta resolución, suite de pruebas unitarias.  

---

## 1. Fundamento Matemático y Geométrico

La fórmula de Euler:

$$e^{i \theta} = \cos(\theta) + i \sin(\theta)$$

admite una representación tridimensional exacta como una **hélice circular** que se propaga a lo largo del eje del parámetro $\theta$:

$$\mathbf{r}(\theta) = \begin{pmatrix} X \\ Y \\ Z \end{pmatrix} = \begin{pmatrix} \theta \\ \text{Re}(e^{i\theta}) \\ \text{Im}(e^{i\theta}) \end{pmatrix} = \begin{pmatrix} \theta \\ \cos(\theta) \\ \sin(\theta) \end{pmatrix}$$

### Proyecciones Canónicas y Vistas Ortogonales

1. **Espiral 3D en la misma zona:**
   La hélice se dibuja en el espacio tridimensional mientras proyecta simultáneamente sus sombras ortogonales sobre los planos coordenados mediante líneas guía dinámicas.

2. **Visualización Individual en el Plano Real $XY$:**
   $$\mathbf{P}_{XY} \mathbf{r}(\theta) = (\theta, \cos\theta, 0)^T \implies y = \cos(x)$$
   Al alinear la cámara en vista cenital ($\phi = 0^\circ, \theta = -90^\circ$), la componente imaginaria colapsa y se aprecia la **onda coseno pura**.

3. **Visualización Individual en el Plano Imaginario $XZ$:**
   $$\mathbf{P}_{XZ} \mathbf{r}(\theta) = (\theta, 0, \sin\theta)^T \implies z = \sin(x)$$
   Al alinear la cámara en vista lateral ($\phi = 90^\circ, \theta = -90^\circ$), la componente real colapsa y se aprecia la **onda seno pura**.

4. **Visualización Individual en el Plano Complejo $YZ$:**
   $$\mathbf{P}_{YZ} \mathbf{r}(\theta) = (0, \cos\theta, \sin\theta)^T \implies y^2 + z^2 = 1$$
   Al observar a lo largo del eje de propagación ($\phi = 90^\circ, \theta = 0^\circ$), la hélice colapsa en el **círculo unitario de radio 1**.

5. **Identidad de Euler en $\theta = \pi$:**
   $$\mathbf{r}(\pi) = (\pi, -1, 0)^T \implies e^{i\pi} + 1 = 0$$

---

## 2. Estructura de Entregables en `RENDERS`

```text
RENDERS/4 Identidad de Euler 3D/
├── videos/
│   ├── Identidad de Euler 3D ES.mp4   (27.5s | 1080x1920 @ 60 FPS | Lo-Fi Chill Synth)
│   └── Euler Identity 3D EN.mp4        (27.5s | 1080x1920 @ 60 FPS | Lo-Fi Chill Synth)
└── extra/
    ├── capturas/
    │   ├── euler_3d_hero.png          (Captura del clímax en theta = pi)
    │   └── euler_3d_projections.png   (Captura de la vista ortogonal 2D)
    └── benchmarks/
        └── Euler_Identity_Complex_Benchmark.xlsx  (Modelo dinámico de 3 pestañas con fórmulas abiertas)
```

---

## 3. Modos de Ejecución

```bash
# Resumen matemático y cálculo diferencial
python main.py

# Generación del modelo dinámico de Excel
python main.py --benchmark

# Renderizado de videos bilingües y capturas HD
python main.py --render

# Ejecución de pruebas unitarias
python -m pytest tests/
```
