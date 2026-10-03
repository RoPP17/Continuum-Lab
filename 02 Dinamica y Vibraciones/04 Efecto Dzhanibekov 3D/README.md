# Continuum Lab — Efecto Dzhanibekov 3D (Teorema de la Raqueta de Tenis)

Simulación cinemática y dinámica 3D de ultra-alta definición (**1080x1920 a 60 FPS**, formato 9:16 vertical) que modela el **Efecto Dzhanibekov** (Inestabilidad del Eje Intermedio de Euler) en microgravedad, desarrollada con **Manim Community Edition** y **SciPy (DOP853)**.

---

## 1. Fundamentación Física y Matemática Rigurosa

### 1.1 Dinámica de Rotación Libre de Cuerpos Rígidos Asimétricos
En ausencia de torques externos ($\vec{\tau} = \vec{0}$, microgravedad), la variación temporal del momento angular en el sistema ligado al cuerpo rígido (sistema móvil principal de inercia) se rige por las **Ecuaciones de Euler**:

$$I_1 \frac{d\omega_1}{dt} = (I_2 - I_3) \omega_2 \omega_3$$

$$I_2 \frac{d\omega_2}{dt} = (I_3 - I_1) \omega_3 \omega_1$$

$$I_3 \frac{d\omega_3}{dt} = (I_1 - I_2) \omega_1 \omega_2$$

Donde los momentos principales de inercia verifican la jerarquía asimétrica estricta:
$$I_1 = 1.0\ \text{kg}\cdot\text{m}^2 \quad<\quad I_2 = 2.4\ \text{kg}\cdot\text{m}^2 \quad<\quad I_3 = 4.2\ \text{kg}\cdot\text{m}^2$$

### 1.2 Demostración Analítica de la Inestabilidad del Eje Intermedio
Supongamos una rotación estacionaria perturbada alrededor del eje intermedio ($\hat{e}_2$):
$$\vec{\omega}(t) = \begin{pmatrix} \delta\omega_1(t) \\ \Omega_0 + \delta\omega_2(t) \\ \delta\omega_3(t) \end{pmatrix}, \qquad |\delta\omega_1|, |\delta\omega_3| \ll \Omega_0$$

Linealizando las ecuaciones para las perturbaciones de primer orden:
$$\frac{d(\delta\omega_1)}{dt} \approx \frac{I_2 - I_3}{I_1} \Omega_0 \delta\omega_3$$
$$\frac{d(\delta\omega_3)}{dt} \approx \frac{I_1 - I_2}{I_3} \Omega_0 \delta\omega_1$$

Derivando la primera ecuación y sustituyendo en la segunda:
$$\frac{d^2(\delta\omega_1)}{dt^2} = \left[ \frac{(I_2 - I_3)(I_1 - I_2)}{I_1 I_3} \Omega_0^2 \right] \delta\omega_1$$

Evaluando los factores de inercia con los parámetros del modelo:
$$(I_2 - I_3) = 2.4 - 4.2 = -1.8 < 0$$
$$(I_1 - I_2) = 1.0 - 2.4 = -1.4 < 0$$
$$(I_2 - I_3)(I_1 - I_2) = (-1.8)(-1.4) = +2.52 > 0$$

Dado que el producto de los dos factores negativos es **estrictamente positivo**, la ecuación diferencial tiene la forma:
$$\frac{d^2(\delta\omega_1)}{dt^2} = +\lambda^2 \delta\omega_1, \qquad \lambda = \Omega_0 \sqrt{\frac{(I_2 - I_1)(I_3 - I_2)}{I_1 I_3}} = \Omega_0 \sqrt{\frac{1.4 \times 1.8}{1.0 \times 4.2}} = \Omega_0 \sqrt{0.6} \approx 0.7746 \Omega_0$$

La solución contiene modos hiperbólicos crecientes:
$$\delta\omega_1(t) = C_1 e^{+\lambda t} + C_2 e^{-\lambda t}$$

El punto fijo $(\omega_1, \omega_2, \omega_3) = (0, \Omega_0, 0)$ es un **punto de silla hiperbólico inestable** en el espacio de fases tridimensional. Por el contrario, la linealización alrededor de los ejes menor ($I_1$) y mayor ($I_3$) produce autovalores puramente imaginarios ($\pm i \omega$), constituyendo **centros elípticos estables de Lyapunov**.

### 1.3 Construcción Geométrica de Poinsot y la Separatriz Homoclínica
El movimiento libre conserva dos integrales primeras escalares:
1. **Energía Cinética Rotacional**:
   $$2 T_{\text{rot}} = I_1 \omega_1^2 + I_2 \omega_2^2 + I_3 \omega_3^2 = \text{cte} = 172.80\ \text{J}$$
   *(Define el Elipsoide de Inercia de Poinsot en $\mathbb{R}^3$)*

2. **Magnitud del Momento Angular**:
   $$|\vec{L}|^2 = I_1^2 \omega_1^2 + I_2^2 \omega_2^2 + I_3^2 \omega_3^2 = \text{cte} = 829.44\ \text{N}^2\cdot\text{m}^2\cdot\text{s}^2$$
   *(Define el Elipsoide de Momento Angular en $\mathbb{R}^3$)*

La intersección de ambas superficies cuadráticas define la curva de fase trazada por $\vec{\omega}(t)$ sobre el cuerpo rígido, denominada **polhoda** (*polhode*). Cuando la energía coincide con la del eje intermedio ($2 T I_2 = |\vec{L}|^2$), las dos ramas se cruzan en el punto de silla formando una **figura en ocho homoclínica** (separatriz).

Al perturbar infinitesimalmente el estado, la trayectoria recorre la separatriz: permanece largo tiempo en la vecindad de $+\Omega_0 \hat{e}_2$, luego es expelida rápidamente a lo largo de la variedad inestable, cruza el plano ecuatorial ($\omega_2 = 0$) y converge transitoriamente hacia la vecindad de $-\Omega_0 \hat{e}_2$. Este tránsito no lineal es el **salto acrobático espontáneo de 180°**.

---

## 2. Cinemática de Actitud en $SO(3)$ y Conservación en el Espacio Inercial

Para representar la orientación tridimensional del cuerpo rígido sin singularidades cinemáticas (*gimbal lock*), se integran sincrónicamente las ecuaciones cinemáticas de cuaterniones unitarios $q(t) = [q_w, q_x, q_y, q_z]^T \in S^3$:

$$\frac{dq}{dt} = \frac{1}{2} q \otimes \begin{pmatrix} 0 \\ \vec{\omega}_b \end{pmatrix}$$

La matriz de rotación ortogonal $R(q) \in SO(3)$ mapea cualquier vector del sistema del cuerpo al sistema inercial de laboratorio:
$$\vec{r}_{\text{espacio}}(t) = R(q(t)) \vec{r}_{\text{cuerpo}}$$

En el sistema inercial, el principio de conservación de momento angular dicta:
$$\vec{L}_s(t) = R(q(t)) \mathbf{I}_b \vec{\omega}_b(t) = \vec{L}_s(0) \equiv \text{constante}$$

En la simulación:
- **Vector $\vec{L}_s$** (flecha cian `#00F0FF`): Se mantiene **rigurosamente inmóvil** en el espacio inercial.
- **Vector $\vec{\omega}_s(t)$** (flecha carmesí `#FF0055`): Precesa sobre el plano invariable de Poinsot y se voltea de orientación durante el flip.

---

## 3. Cronograma Cinemático de la Simulación (14.0 s / 840 frames @ 60 FPS)

| Intervalo | Tiempo | Dinámica del Espacio de Fases | Estado Visual en Pantalla |
|---|---|---|---|
| **Fase 1** | $0.0\text{ s} - 3.5\text{ s}$ | Giro cuasi-estable cerca del punto de silla $+\Omega_2$. | Giro uniforme de alta velocidad en orientación upright (+Y). |
| **Fase 2** | $3.5\text{ s} - 5.0\text{ s}$ | **Flip homoclínico acrobático de 180°** ($\omega_2$ cruza por cero en $t = 4.57\text{ s}$). | El vástago se invierte en el aire sin fuerzas externas. Los extremos oro/cian intercambian posiciones. |
| **Fase 3** | $5.0\text{ s} - 8.5\text{ s}$ | Giro invertido cuasi-estable cerca de $-\Omega_2$. | El cuerpo continúa girando establemente en orientación invertida (-Y). |
| **Fase 4** | $8.5\text{ s} - 10.0\text{ s}$ | **Segundo flip homoclínico de reversión** ($\omega_2$ cruza por cero en $t = 8.67\text{ s}$). | Segundo salto acrobático que retorna la manija a su orientación original. |
| **Fase 5** | $10.0\text{ s} - 14.0\text{ s}$ | Restablecimiento de la periodicidad orbital. | Giro continuo en orientación inicial, demostrando la naturaleza conservativa del sistema. |

---

## 4. Estructura del Código y Módulos

```
04 Efecto Dzhanibekov 3D/
├── src/
│   ├── physics/
│   │   ├── __init__.py
│   │   └── euler_rigid_body.py      # Integrador DOP853, métricas de conservación y SO(3)
│   └── visualization/
│       ├── __init__.py
│       └── dzhanibekov_scene.py     # ThreeDScene en Manim Community (9:16 vertical)
├── tests/
│   ├── __init__.py
│   └── test_dzhanibekov.py          # Suite de verificación unitaria con pytest
├── docs/                            # Documentación técnica adicional
├── main.py                          # CLI principal: render, preview, benchmark y diagnósticos
├── run.bat                          # Launcher rápido para Windows PowerShell/CMD
└── README.md                        # Documento técnico completo
```

---

## 5. Instrucciones de Uso y Ejecución

### 5.1 Ejecución Rápida mediante Batch (Windows)
```cmd
# Verificación teórica y exportación de benchmark XLSX
run.bat

# Ejecutar suite de pruebas unitarias
run.bat test

# Renderizar preview rápido de Manim (-ql)
run.bat preview

# Renderizar video final en ultra-alta definición 1080x1920 @ 60 FPS (-qh)
run.bat render
```

### 5.2 Comandos CLI Directos en Python
```bash
# Diagnóstico físico teórico en consola
python main.py --diagnostics

# Exportar modelo dinámico Excel openpyxl (.xlsx)
python main.py --benchmark

# Renderizar con Manim directamente
python -m manim -qh "src/visualization/dzhanibekov_scene.py" DzhanibekovScene -o "efecto_dzhanibekov_1080x1920.mp4"
```

---

## 6. Resultados de Conservación y Benchmarking

Las pruebas unitarias y de integración numérica con método **Runge-Kutta de orden 8 (DOP853)** arrojan las siguientes tolerancias de conservación:

- **Deriva de Energía Cinética Rotacional**:
  $$\frac{\Delta T_{\text{rot}}}{T_0} = 2.24 \times 10^{-11} \ll 10^{-9}$$
- **Deriva de Magnitud de Momento Angular**:
  $$\frac{\Delta |\vec{L}|}{|\vec{L}_0|} = 1.12 \times 10^{-11} \ll 10^{-9}$$
- **Deriva Vectorial Inercial de $\vec{L}_s$**:
  $$\max \|\vec{L}_s(t) - \vec{L}_s(0)\| = 7.42 \times 10^{-10}\ \text{N}\cdot\text{m}\cdot\text{s}$$
- **Ortogonalidad de Matrices $R(q)$**:
  $$\|R^T R - I\|_\infty < 1.0 \times 10^{-13}$$
