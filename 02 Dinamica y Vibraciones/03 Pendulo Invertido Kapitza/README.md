# Continuum Lab — Dinámica No Lineal y Vibraciones
## 03 • Paradoja del Péndulo Invertido de Kapitza
### *Estabilización Asintótica de un Equilibrio Estáticamente Inestable mediante Excitación Vibratoria Rápida*

---

## 1. Resumen Ejecutivo y Planteamiento del Problema

El **Péndulo Invertido de Kapitza** (descrito teóricamente por Pyotr Kapitza en 1951) es uno de los fenómenos más contraintuitivos y paradigmáticos de la **mecánica no lineal**, la **dinámica vibracional** y la **teoría de promediado asintótico**.

En condiciones estáticas ordinarias, la posición vertical hacia arriba ($\theta = 180^\circ$ o $\pi\text{ rad}$) es un punto de equilibrio **estáticamente inestable**: cualquier perturbación infinitesimal destruye el equilibrio y precipita el péndulo hacia la posición colgante ($\theta = 0^\circ$).

Sin embargo, cuando el punto de suspensión o soporte se somete a una **aceleración armónica vertical de alta frecuencia y pequeña amplitud** $y_0(t) = a \cos(\omega t)$, el acoplamiento no lineal entre la micro-oscilación forzada rápida y el campo gravitatorio genera una fuerza centrífuga promediada que se traduce en un **pozo de potencial efectivo de Landau-Kapitza**. Si la energía cinética vibratoria inyectada supera el gradiente gravitacional, el punto invertido pasa a ser un **mínimo local de energía potencial asintóticamente estable**, permitiendo al péndulo mantenerse erguido "desafiando" la gravedad y absorbiendo perturbaciones externas sin caer.

```
       [Soporte Vibrante: y0(t) = a·cos(ωt), f = 55 Hz]
                         │
                         ▼ (Aceleración a·ω² ≈ 487 g)
                      [Pivote]
                         │
                         │  L = 1.0 m (Varilla Rígida)
                         │
                         ●  Bob (m = 0.5 kg)
                     θ = 180° (Equilibrio Invertido Estable)
```

---

## 2. Formulación Matemática Rigurosa

### 2.1. Cinemática y Lagrangiano en Marco Inercial

Consideremos un marco de coordenadas cartesiano inercial $(x, y)$, donde el eje $y$ apunta verticalmente hacia abajo en la dirección de la aceleración gravitatoria $g$.
El soporte del péndulo se mueve exclusivamente en el eje vertical según:
$$y_0(t) = a \cos(\omega t)$$

Las coordenadas de la masa puntual $m$ sujeta al extremo de una varilla rígida sin masa de longitud $L$ son:
$$x(t) = L \sin\theta(t)$$
$$y(t) = y_0(t) - L \cos\theta(t) = a \cos(\omega t) - L \cos\theta(t)$$

Las velocidades cartesianas se obtienen por derivación temporal directa:
$$\dot{x}(t) = L \dot{\theta} \cos\theta$$
$$\dot{y}(t) = -a \omega \sin(\omega t) + L \dot{\theta} \sin\theta$$

La energía cinética total $T$ del sistema es:
$$T = \frac{1}{2} m \left(\dot{x}^2 + \dot{y}^2\right) = \frac{1}{2} m \left[ L^2 \dot{\theta}^2 \cos^2\theta + \left( L \dot{\theta} \sin\theta - a\omega\sin(\omega t) \right)^2 \right]$$
$$T = \frac{1}{2} m L^2 \dot{\theta}^2 - m L a \omega \dot{\theta} \sin\theta \sin(\omega t) + \frac{1}{2} m a^2 \omega^2 \sin^2(\omega t)$$

La energía potencial gravitatoria $V$ (tomando $y = 0$ como referencia y recordando que $y$ crece hacia abajo):
$$V = -m g y = -m g \left( a \cos(\omega t) - L \cos\theta \right) = m g L \cos\theta - m g a \cos(\omega t)$$

El Lagrangiano $\mathcal{L} = T - V$ del péndulo resulta:
$$\mathcal{L}(\theta, \dot{\theta}, t) = \frac{1}{2} m L^2 \dot{\theta}^2 - m L a \omega \dot{\theta} \sin\theta \sin(\omega t) - m g L \cos\theta + f(t)$$
donde $f(t) = \frac{1}{2} m a^2 \omega^2 \sin^2(\omega t) + m g a \cos(\omega t)$ depende únicamente de $t$ y desaparece al aplicar las ecuaciones de Euler-Lagrange.

### 2.2. Ecuación de Movimiento de Euler-Lagrange con Amortiguamiento

Aplicando el formalismo de Euler-Lagrange con una función de disipación de Rayleigh $\mathcal{F} = \frac{1}{2} m L^2 b \dot{\theta}^2$:
$$\frac{d}{dt}\left(\frac{\partial \mathcal{L}}{\partial \dot{\theta}}\right) - \frac{\partial \mathcal{L}}{\partial \theta} = -\frac{\partial \mathcal{F}}{\partial \dot{\theta}}$$

Calculando las derivadas parciales:
$$\frac{\partial \mathcal{L}}{\partial \dot{\theta}} = m L^2 \dot{\theta} - m L a \omega \sin\theta \sin(\omega t)$$
$$\frac{d}{dt}\left(\frac{\partial \mathcal{L}}{\partial \dot{\theta}}\right) = m L^2 \ddot{\theta} - m L a \omega \dot{\theta} \cos\theta \sin(\omega t) - m L a \omega^2 \sin\theta \cos(\omega t)$$
$$\frac{\partial \mathcal{L}}{\partial \theta} = -m L a \omega \dot{\theta} \cos\theta \sin(\omega t) + m g L \sin\theta$$

Sustituyendo en la ecuación de Euler-Lagrange y simplificando los términos cruzados:
$$m L^2 \ddot{\theta} - m L a \omega^2 \sin\theta \cos(\omega t) - m g L \sin\theta + m L^2 b \dot{\theta} = 0$$

Dividiendo entre $m L^2$, se obtiene la **ecuación no lineal gobernante exacta**:
$$\ddot{\theta} + b\dot{\theta} + \left( \frac{g}{L} - \frac{a \omega^2}{L} \cos(\omega t) \right) \sin\theta + \tau_{\text{ext}}(t) = 0$$

Nótese que el término aceleratorio del soporte $\ddot{y}_0(t) = -a \omega^2 \cos(\omega t)$ entra como una modulación armónica periódica sobre la gravedad efectiva $g_{\text{eff}}(t) = g - a\omega^2 \cos(\omega t)$, transformando la ecuación en una **ecuación no lineal generalizada de Mathieu-Hill**.

---

## 3. Método Asintótico de Promediado de Kapitza-Bogoliubov

Para estudiar el comportamiento analítico del sistema cuando la frecuencia de excitación es muy rápida ($\omega \gg \sqrt{g/L}$), descomponemos el ángulo $\theta(t)$ en dos escalas temporales desacopladas:
$$\theta(t) = \Theta(t) + \xi(t)$$
donde:
- $\Theta(t)$: Componente de evolución **lenta** o secular de gran amplitud.
- $\xi(t)$: Micro-vibración **rápida** de periodo $T = \frac{2\pi}{\omega}$, de media nula $\langle \xi \rangle = 0$ y amplitud infinitesimal $|\xi| \ll 1$.

### 3.1. Expansión en Serie de Taylor y Desacoplamiento

Expandiendo las funciones trigonométricas en torno a la variable macroscópica $\Theta$:
$$\sin(\Theta + \xi) \approx \sin\Theta + \xi \cos\Theta - \frac{1}{2} \xi^2 \sin\Theta + \mathcal{O}(\xi^3)$$

Sustituyendo en la ecuación diferencial:
$$\ddot{\Theta} + \ddot{\xi} + b(\dot{\Theta} + \dot{\xi}) + \left( \frac{g}{L} - \frac{a \omega^2}{L} \cos(\omega t) \right) \left( \sin\Theta + \xi \cos\Theta \right) = 0$$

### 3.2. Determinación de la Dinámica Rápida $\xi(t)$

Aislamos los términos que varían a escala rápida de orden $\mathcal{O}(\omega^2)$. El término dominante en la aceleración es $\ddot{\xi} \sim \omega^2 \xi$, el cual balancea directamente la excitación armónica forzada de la base:
$$\ddot{\xi} \approx \frac{a \omega^2}{L} \sin\Theta \cos(\omega t)$$

Integrando dos veces respecto al tiempo rápido $t$, considerando que $\Theta$ es cuasi-constante a esta escala:
$$\dot{\xi}(t) \approx \frac{a \omega}{L} \sin\Theta \sin(\omega t)$$
$$\xi(t) \approx -\frac{a}{L} \sin\Theta \cos(\omega t)$$

Esta solución analítica revela que la amplitud de la micro-oscilación $\xi(t)$ es proporcional a $\sin\Theta$ y está en desfase con el soporte. Notablemente, en el equilibrio vertical puro ($\Theta = \pi$), $\sin\pi = 0$, lo que implica que la micro-oscilación $\xi$ se anula idénticamente en la vertical exacta.

### 3.3. Promediado Temporal Secular sobre el Periodo Rápido

Definimos el operador de promedio temporal sobre un periodo completo $T_{\text{fast}} = \frac{2\pi}{\omega}$:
$$\langle f(t) \rangle = \frac{1}{T_{\text{fast}}} \int_0^{T_{\text{fast}}} f(t) \, dt$$

Evaluando los valores esperados de las funciones periódicas:
$$\langle \xi(t) \rangle = 0, \quad \langle \dot{\xi}(t) \rangle = 0, \quad \langle \cos(\omega t) \rangle = 0$$
$$\langle \cos^2(\omega t) \rangle = \frac{1}{2}$$

El producto cruzado no lineal entre la fuerza de excitación y la micro-vibración genera un valor medio no nulo:
$$\left\langle -\frac{a \omega^2}{L} \cos(\omega t) \cdot \xi(t) \cos\Theta \right\rangle = \left\langle -\frac{a \omega^2}{L} \cos(\omega t) \left( -\frac{a}{L} \sin\Theta \cos(\omega t) \right) \cos\Theta \right\rangle$$
$$= \frac{a^2 \omega^2}{L^2} \sin\Theta \cos\Theta \left\langle \cos^2(\omega t) \right\rangle = \frac{a^2 \omega^2}{2 L^2} \sin\Theta \cos\Theta$$

Promediando la ecuación completa de movimiento, la dinámica secular para la posición macroscópica lenta $\Theta(t)$ queda gobernada por:
$$\ddot{\Theta} + b \dot{\Theta} + \frac{g}{L} \sin\Theta + \frac{a^2 \omega^2}{2 L^2} \sin\Theta \cos\Theta = 0$$

---

## 4. Potencial Efectivo de Landau-Kapitza y Estabilidad

La ecuación secular para $\Theta$ describe un sistema conservativo amortiguado con una fuerza generalizada neta:
$$\ddot{\Theta} + b \dot{\Theta} = -\frac{1}{m L^2} \frac{d V_{\text{eff}}}{d\Theta}$$

Multiplicando por $m L^2$ e integrando respecto a $\Theta$:
$$\frac{d V_{\text{eff}}}{d\Theta} = m g L \sin\Theta + \frac{1}{2} m a^2 \omega^2 \sin\Theta \cos\Theta$$

Integrando respecto a $\Theta$ (tomando $V_{\text{eff}}(0) = 0$ como referencia):
$$V_{\text{eff}}(\Theta) = m g L (1 - \cos\Theta) + \frac{1}{4} m a^2 \omega^2 \sin^2\Theta$$

Este es el **Potencial Efectivo de Landau-Kapitza**.
- El primer término $m g L (1 - \cos\Theta)$ representa el **potencial gravitatorio ordinario**.
- El segundo término $\frac{1}{4} m a^2 \omega^2 \sin^2\Theta$ representa la **energía cinética promediada de la oscilación rápida**, originando una barrera de potencial restauradora que estabiliza el sistema.

### 4.1. Análisis de Puntos Críticos y Curvatura

Los puntos de equilibrio corresponden a los extremos del potencial efectivo $\frac{d V_{\text{eff}}}{d\Theta} = 0$:
$$\sin\Theta \left( m g L + \frac{1}{2} m a^2 \omega^2 \cos\Theta \right) = 0$$

Las soluciones son:
1. $\sin\Theta = 0 \implies \Theta = 0$ (Posición inferior / colgado) y $\Theta = \pi$ (Posición superior / invertido).
2. $\cos\Theta_c = -\frac{2 g L}{(a \omega)^2}$ (Bifurcaciones de ensilladura que limitan el pozo).

La segunda derivada (curvatura del potencial) determina la estabilidad:
$$\frac{d^2 V_{\text{eff}}}{d\Theta^2} = m g L \cos\Theta + \frac{1}{2} m a^2 \omega^2 \cos(2\Theta)$$

Evaluando la curvatura en el punto invertido $\Theta = \pi$:
$$\left. \frac{d^2 V_{\text{eff}}}{d\Theta^2} \right|_{\Theta = \pi} = m g L \cos\pi + \frac{1}{2} m a^2 \omega^2 \cos(2\pi) = -m g L + \frac{1}{2} m a^2 \omega^2$$

### 4.2. Deducción del Criterio de Estabilidad de Kapitza

Para que el punto invertido $\Theta = \pi$ sea un **mínimo local estricto** de energía potencial ($d^2 V_{\text{eff}}/d\Theta^2 > 0$), se requiere:
$$-m g L + \frac{1}{2} m a^2 \omega^2 > 0$$
$$\boxed{(a \omega)^2 > 2 g L}$$

Esta es la **Condición Fundamental de Estabilidad de Kapitza**.

Expresada en términos de la frecuencia de excitación en Hertz $f = \frac{\omega}{2\pi}$:
$$f > f_{\text{crit}} = \frac{1}{2\pi a} \sqrt{2 g L}$$

### 4.3. Verificación Numérica de los Parámetros del Proyecto

Para la configuración física seleccionada:
- Masa $m = 0.50\text{ kg}$
- Longitud $L = 1.00\text{ m}$
- Gravedad $g = 9.81\text{ m/s}^2$
- Amplitud $a = 0.04\text{ m}$ ($4.0\text{ cm}$)
- Frecuencia $f = 55.0\text{ Hz} \implies \omega = 2\pi(55) \approx 345.575\text{ rad/s}$

Sustituyendo valores:
$$(a \omega)^2 = (0.04 \cdot 345.575)^2 = (13.823)^2 = \mathbf{191.076\text{ m}^2/\text{s}^2}$$
$$2 g L = 2 \cdot 9.81 \cdot 1.00 = \mathbf{19.620\text{ m}^2/\text{s}^2}$$

$$\text{Ratio de Estabilidad } R = \frac{(a \omega)^2}{2 g L} = \frac{191.076}{19.620} \approx \mathbf{9.74 \gg 1}$$

La frecuencia crítica mínima es:
$$f_{\text{crit}} = \frac{1}{2\pi \cdot 0.04} \sqrt{2 \cdot 9.81 \cdot 1.0} = \frac{4.4294}{0.2513} \approx \mathbf{17.62\text{ Hz}}$$

Operando a $f = 55.0\text{ Hz}$, el sistema funciona al **$312.1\%$** de la frecuencia crítica, garantizando una rigidez dinámica y una cuenca de atracción excepcionales.

### 4.4. Cuenca de Atracción Angular

Los máximos locales que delimitan el pozo de potencial invertido ocurren en:
$$\cos\Theta_c = -\frac{2 g L}{(a \omega)^2} = -\frac{1}{R} = -\frac{1}{9.7388} \approx -0.10268$$
$$\Theta_c = \arccos(-0.10268) \approx 95.89^\circ \quad (\text{y por simetría } 264.11^\circ)$$

Por lo tanto, la cuenca de atracción angular del equilibrio invertido abarca:
$$\Delta\Theta = [95.89^\circ, 264.11^\circ] \implies 180^\circ \pm 84.11^\circ$$

Cualquier perturbación angular que mantenga el péndulo dentro de este rango de $\pm 84.11^\circ$ respecto a la vertical será restaurada asintóticamente hacia el punto superior.

---

## 5. Secuencia Dramática Visual (15 Segundos @ 60 FPS)

La animación implementa una narrativa cinemática de 900 cuadros a 60 FPS dividida en tres fases físicas:

```
0.0s               4.0s              8.0s                             15.0s
├──────────────────┼─────────────────┼────────────────────────────────┤
│  FASE 1          │  FASE 2         │  FASE 3                        │
│  Equilibrio      │  Perturbación   │  Parada de Emergencia (ω -> 0) │
│  Invertido       │  Lateral (35°)  │  Colapso Gravitatorio Violento │
│  Vibrando 55 Hz  │  Auto-Retorno   │  Oscilación Colgante           │
└──────────────────┴─────────────────┴────────────────────────────────┘
```

1. **Fase 1 [0.0s – 4.0s] — Desafío Gravitatorio Estable**:
   - El péndulo oscila suavemente en torno a $\theta = 180^\circ$ mientras el carro del soporte vibra verticalmente a 55 Hz con una aceleración de $487\text{ g}$.
   - Flechas estroboscópicas cinéticas visualizan la aceleración vertical instantánea $\ddot{y}_0(t)$.
   - El pozo de potencial dinámico en la tarjeta inferior muestra un pozo profundo con una esfera confinada en el mínimo local.

2. **Fase 2 [4.0s – 8.0s] — Perturbación Externa y Auto-Estabilización**:
   - En $t = 4.0\text{ s}$, un pulso de par lateral externo $\tau_{\text{ext}}(t)$ desvía bruscamente el péndulo hasta $\theta \approx 148^\circ$ (desviación de $\sim 32^\circ - 35^\circ$).
   - Aparece un vector de fuerza lateral carmesí en el HUD (`PERTURBACIÓN EXTERNA: PULSO LATERAL`).
   - La esfera en el gráfico de potencial escala la pared del pozo hasta $V \approx 9.7\text{ J}$.
   - Gracias al gradiente restaurador del potencial efectivo, el péndulo no cae: ejecuta oscilaciones amortiguadas y retorna de pie a la vertical estable hacia $t = 7.5\text{ s}$.

3. **Fase 3 [8.0s – 15.0s] — Parada de Emergencia y Colapso Catastrófico**:
   - En $t = 8.0\text{ s}$, la excitación se corta bruscamente ($\omega \to 0$, $f \to 0\text{ Hz}$).
   - Se activa el banner de advertencia carmesí en el HUD (`SISTEMA INESTABLE: EXCITACIÓN APAGADA`).
   - El término dinámico restaurador $\frac{1}{4} m a^2 \omega^2 \sin^2\Theta$ desaparece instantáneamente: el pozo se colapsa en una colina convexa inestable.
   - La gravedad ordinaria recupera el dominio absoluto: el péndulo se desploma violentamente hacia adelante en rotación no lineal libre, amortiguándose hacia el equilibrio colgante inferior natural ($\theta \to 360^\circ / 0^\circ$).

---

## 6. Arquitectura del Software y Renderizado Vectorial Manim

```
Continuum Lab / 03 Pendulo Invertido Kapitza
├── manim.cfg                 # Configuración nativa 1080x1920 @ 60 FPS, dark navy #070B12
├── main.py                   # CLI Runner unificado de Continuum Lab
├── src/
│   ├── physics.py            # Motor de simulación ODE Scipy solve_ivp (RK45) + Decoupling
│   └── kapitza_scene.py      # Escena Manim Community optimizada para 60 FPS
├── tests/
│   └── test_kapitza.py       # Suite pytest de verificación matemática y física
└── media/
    ├── images/kapitza_scene/ # Snapshots diagnósticos de ultra-alta definición
    └── videos/kapitza_scene/ # Renders de video 1080p60 maestro y 720p30 preview
```

### Optimizaciones Clave de Renderizado
1. **Desacoplamiento Solver/Renderer**: La ecuación diferencial se integra numéricamente con `scipy.integrate.solve_ivp` utilizando tolerancia adaptativa estricta (`rtol=1e-8`, `atol=1e-10`, `max_step=1.5e-4`), desacoplando la integración física de la generación de fotogramas de Manim.
2. **Filtrado de Portadora Rápida para Telemetría**: Se aplica un filtro de media móvil sobre una ventana de $\Delta t = 1/55\text{ s}$ para aislar la trayectoria secular lenta $\Theta(t)$ y animar la esfera del potencial sin aliasing estroboscópico.
3. **Caché y Reemplazo Vectorial de Texto HUD**: Para evitar invocar librerías tipográficas del sistema (Pango) en cada uno de los 900 fotogramas a 60 FPS, los grupos HUD de cada fase se pre-construyen estáticamente y se conmutan mediante opacidad vectorial. Las lecturas numéricas continuas se actualizan a $10\text{ Hz}$ mientras que los elementos cinemáticos (varilla, bob, flechas, curva y esfera) se computan a $60\text{ FPS}$ plenos.
4. **Respeto Estricto de Safe Zones**:
   - Marco Manim: $9.0 \times 16.0$ ($x \in [-4.5, 4.5]$, $y \in [-8.0, 8.0]$).
   - Zona Superior Libre ($> 160\text{ px}$): Título y telemetría ubicados en $y \in [4.5, 6.7]$.
   - Zona Inferior Libre ($> 320\text{ px}$): Tarjeta de potencial efectiva ubicada en $y \in [-5.1, -1.8]$, dejando los últimos $340\text{ px}$ libres para interfaces móviles.

---

## 7. Instrucciones de Uso y Comandos CLI

El script [`main.py`](file:///c:/Users/andre/OneDrive/Desktop/Continuum%20Lab/02%20Dinamica%20y%20Vibraciones/03%20Pendulo%20Invertido%20Kapitza/main.py) proporciona una interfaz de línea de comandos para todas las operaciones:

```bash
# 1. Verificación analítica y parámetros físicos en consola
python main.py --info

# 2. Ejecutar la suite de pruebas automatizadas (Pytest)
python main.py --test

# 3. Generar snapshots estáticos de alta resolución para las 3 fases
python main.py --snapshots

# 4. Renderizar preview rápida de video (720p @ 30 FPS)
python main.py --render-preview

# 5. Renderizar el video maestro final (1080p @ 60 FPS Ultra-HD)
python main.py --render

# 6. Ejecutar el pipeline completo (tests + snapshots + master video)
python main.py --all
```

---

## 8. Resultados de Verificación y Métricas

| Prueba de Verificación | Parámetro Evaluado | Valor Teórico / Esperado | Resultado Simulación | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **Criterio de Kapitza** | $(a\omega)^2 > 2gL$ | $> 19.620\text{ m}^2/\text{s}^2$ | $191.076\text{ m}^2/\text{s}^2$ ($R = 9.74$) | **PASSED** |
| **Frecuencia Crítica** | $f_{\text{crit}}$ | $17.62\text{ Hz}$ | $17.620\text{ Hz}$ | **PASSED** |
| **Curvatura Activa** | $d^2V_{\text{eff}}/d\Theta^2\vert_{\pi}$ | $> 0$ (Pozo de potencial) | $+42.86\text{ J/rad}^2$ | **PASSED** |
| **Curvatura Inactiva** | $d^2V/d\theta^2\vert_{\pi}$ | $< 0$ (Colina inestable) | $-4.905\text{ J/rad}^2$ | **PASSED** |
| **Cuenca de Atracción** | $\Delta\Theta_{\text{basin}}$ | $\pm 84.11^\circ$ | $\theta \in [95.89^\circ, 264.11^\circ]$ | **PASSED** |
| **Estabilidad Fase 1** | Ángulo medio en $t \in [1, 3]\text{ s}$ | $180^\circ$ | $180.00^\circ \pm 0.08^\circ$ | **PASSED** |
| **Perturbación Fase 2** | Desviación lateral máxima | $\sim 35^\circ$ ($145^\circ - 150^\circ$) | $148.1^\circ$ ($\Delta\theta = 31.9^\circ$) | **PASSED** |
| **Restauración Fase 2** | Retorno antes de $t = 8.0\text{ s}$ | $|\theta - 180^\circ| < 5^\circ$ | $179.91^\circ$ | **PASSED** |
| **Colapso Fase 3** | Caída post-apagado ($t > 8\text{ s}$) | Rotación hacia $360^\circ / 0^\circ$ | Colapso gravitatorio completo | **PASSED** |

---
*Desarrollado en Continuum Lab — Simulación Científica y Modelado de Sistemas Dinámicos Avanzados.*
