# Continuum Lab — Dinámica Rotacional y Aeroespacial
## División 02: Dinámica y Vibraciones
### Proyecto 03: Precesión Giroscópica 3D y Nutación Transitoria ("Anti-Gravedad Aparente")

---

## 1. Fundamentos Físicos y Matemáticos Rigurosos

Un giróscopo o trompo simétrico pesado soportado sobre un pivote puntual sin fricción constituye uno de los sistemas dinámicos fundamentales de la mecánica clásica analítica (Lagrange y Euler).

```
                 Z (Eje Vertical)
                 ▲
                 │  Ω_p (Precesión Dorada, #FFE600)
                 │  ▲
                 │  │
                 │  │
                 │  │      L (Momento Angular Cian, #00F0FF)
                 O──┼──────────────────────────────►
               Pivote\                           /
                      \    τ_g (Torque Carmesí) /
                       \   #FF0055             ▼
                        \─────────────────────►
                               │
                               ▼ F_g = m·g (Peso Coral, #EF4444)
```

### 1.1 Parámetros Físicos del Rotor y Teorema de Steiner
El sistema consta de un rotor de disco macizo homogéneo de masa $m$, radio $R$, con su centro de masa a una distancia $r_{\text{cm}}$ a lo largo de un eje rígido montado sobre un pivote puntual:

* **Masa del rotor:** $m = 2.50\text{ kg}$
* **Radio del rotor:** $R = 0.18\text{ m}$
* **Distancia pivote-centro de masa:** $r_{\text{cm}} = 0.25\text{ m}$
* **Aceleración gravitacional:** $g = 9.81\text{ m/s}^2$

#### Tensor de Inercia respecto al Pivote Puntual:
El momento de inercia polar respecto al eje propio de rotación del disco ($Z'$):
$$I_z = \frac{1}{2} m R^2 = \frac{1}{2}(2.50\text{ kg})(0.18\text{ m})^2 = 0.04050\text{ kg}\cdot\text{m}^2$$

Los momentos de inercia transversales respecto al pivote puntual se obtienen aplicando el **Teorema de los Ejes Paralelos (Steiner)**, sumando el momento diametral del disco y el término de traslación del centro de masa:
$$I_x = I_y = I_{\text{disco, diam}} + m r_{\text{cm}}^2 = \frac{1}{4} m R^2 + m r_{\text{cm}}^2$$
$$I_x = \frac{1}{4}(2.50)(0.18)^2 + (2.50)(0.25)^2 = 0.02025 + 0.15625 = 0.17650\text{ kg}\cdot\text{m}^2$$

---

### 1.2 Cinemática del Giro Ultrarrápido y Momento Angular
Para un giro propio ultrarrápido a velocidad nominal de:
$$N = 10{,}000\text{ RPM}$$
$$\omega_s = \frac{10{,}000 \times 2\pi}{60} \approx 1047.19755\text{ rad/s}$$

El momento angular axial intrínseco del rotor es:
$$L = I_z \omega_s = (0.04050\text{ kg}\cdot\text{m}^2)(1047.19755\text{ rad/s}) \approx 42.4115\text{ N}\cdot\text{m}\cdot\text{s}$$

---

### 1.3 Torque Gravitatorio y Ecuaciones de Euler
El torque ejercido por el peso sobre el pivote puntual es:
$$\vec{\tau}_g = \vec{r}_{\text{cm}} \times (m \vec{g})$$

Para un ángulo de inclinación $\theta$ medido desde la vertical (en orientación horizontal $\theta = 90^\circ$):
$$\tau_g = r_{\text{cm}} m g \sin(\theta) = (0.25\text{ m})(2.50\text{ kg})(9.81\text{ m/s}^2)\sin(90^\circ) = 6.13125\text{ N}\cdot\text{m} \approx 6.13\text{ N}\cdot\text{m}$$

De acuerdo con el teorema del momento cinético:
$$\frac{d\vec{L}}{dt} = \vec{\tau}_g$$

Como el giro propio $\omega_s$ es mucho mayor que la velocidad de precesión ($\omega_s \gg \Omega_p$), el momento angular total está dominado por el componente axial: $\vec{L} \approx L \hat{u}$.
En régimen estacionario, la precesión uniforme a velocidad angular $\vec{\Omega}_p = \Omega_p \hat{k}$ implica:
$$\frac{d\vec{L}}{dt} = \vec{\Omega}_p \times \vec{L} = \vec{\tau}_g$$

Como $\vec{\Omega}_p$ es vertical y $\vec{L}$ es horizontal, su producto vectorial es estrictamente tangencial:
$$\Omega_p L \sin(90^\circ) = \tau_g \implies \Omega_p = \frac{\tau_g}{L} = \frac{r_{\text{cm}} m g}{I_z \omega_s}$$

#### Calibración Dinámica de la Simulación:
Para la telemetría dinámica visual solicitada:
* $L_{\text{eff}} = 1.01\text{ N}\cdot\text{m}\cdot\text{s}$
* $\Omega_p = \frac{6.13125}{1.01} \approx 6.07\text{ rad/s}$ ($\approx 0.966\text{ Hz}$, un ciclo completo cada $\approx 1.03\text{ s}$, ideal para visualización cinematográfica fluida a 60 FPS).

---

### 1.4 La Paradoja de "Anti-Gravedad Aparente" Resuelta
> **¿Por qué el giróscopo no cae hacia el suelo por la gravedad?**
>
> La fuerza de gravedad ejerce una fuerza hacia abajo ($-\hat{k}$), pero el sistema pivota sobre un punto fijo. El torque resultante $\vec{\tau}_g = \vec{r}_{\text{cm}} \times (-mg \hat{k})$ es **perpendicular tanto a la gravedad como al eje del giróscopo**, apuntando siempre en la dirección tangencial horizontal $\hat{\phi}$.
>
> Debido a que $\vec{\tau}_g \perp \vec{L}$, el torque gravitatorio **no puede realizar trabajo sobre el momento angular** ($\vec{\tau}_g \cdot \vec{L} = 0$), lo que implica:
> $$\frac{d}{dt}|\vec{L}|^2 = 2 \vec{L} \cdot \frac{d\vec{L}}{dt} = 2 \vec{L} \cdot \vec{\tau}_g = 0 \implies |\vec{L}| = \text{constante}$$
>
> Por ende, la gravedad es matemáticamente incapaz de "doblar" el eje hacia abajo sin violar la conservación del momento cinético. En su lugar, el torque desvía continuamente la dirección de $\vec{L}$ en el plano horizontal, obligándolo a precesar en círculo a velocidad constante $\Omega_p$.

---

### 1.5 Nutación Transitoria y Cúspides Cicloidales
Cuando el giróscopo se suelta desde el reposo sin velocidad angular de precesión inicial ($\dot{\phi}(0) = 0$), el sistema no puede precesar instantáneamente a $\Omega_p$ debido a la inercia transversal $I_x$.

Las ecuaciones de Euler-Lagrange para los ángulos $(\theta, \phi)$ dan lugar a una oscilación acoplada de alta frecuencia:
$$\omega_n = \frac{L}{I_x} = \frac{1.01\text{ N}\cdot\text{m}\cdot\text{s}}{0.17650\text{ kg}\cdot\text{m}^2} \approx 5.72\text{ rad/s}$$

La solución analítica de pequeña amplitud revela el fenómeno de **cúspides cicloidales**:
$$\theta(t) = \theta_0 + \frac{\Omega_p}{\omega_n} \left[1 - \cos(\omega_n t)\right]$$
$$\phi(t) = \Omega_p t - \frac{\Omega_p}{\omega_n} \sin(\omega_n t)$$
$$\dot{\phi}(t) = \Omega_p \left[1 - \cos(\omega_n t)\right]$$

* En $t = 0$: $\dot{\phi} = 0$, el eje cae infinitesimalmente bajo la gravedad.
* A medida que cae, $\dot{\phi}$ aumenta, generando un torque giroscópico giroscópico reactivo que frena la caída y levanta el rotor de regreso al ángulo inicial $\theta_0$.
* En la cúspide ($\cos(\omega_n t) = 1$), $\dot{\phi} = 0$ y $\theta = \theta_0$, trazando un rizo cicloidal continuo en el espacio tridimensional.

---

## 2. Especificaciones de Producción Visual (9:16 Vertical UHD)

| Parámetro | Especificación | Justificación Técnica |
| :--- | :--- | :--- |
| **Resolución** | 1080 x 1920 px | Formato vertical 9:16 (TikTok, Reels, Shorts) |
| **Framerate** | 60 FPS | Fluidez absoluta en trayectorias 3D continuas |
| **Fondo** | Hex `#0B0F19` | Dark Cyber-Engineering de alto contraste |
| **Safe Zone Top** | $Y > 5.5$ ($> 160\text{ px}$) | Evita barra de estado y cámara punch-hole |
| **Safe Zone Bottom** | $Y < -5.5$ ($> 320\text{ px}$) | Evita títulos, botones de audio y barra de progreso |
| **Margen Derecho** | $X < 2.6$ ($> 130\text{ px}$) | Evita botones de Like, Comentarios y Compartir |

### Código de Colores Vectoriales 3D:
* **Momento Angular ($\vec{L}$):** Cian Neón (`#00F0FF`) saliendo a lo largo del eje.
* **Torque Gravitatorio ($\vec{\tau}_g$):** Carmesí Neón (`#FF0055`) perpendicular tangencial.
* **Velocidad de Precesión ($\vec{\Omega}_p$):** Oro Neón (`#FFE600`) vertical sobre $+Z$.
* **Fuerza Gravitacional ($m\vec{g}$):** Coral Neón (`#EF4444`) hacia el suelo.
* **Trazador Orbital:** Estela fosforescente cian/dorada registrando la órbita y las cúspides de nutación.

---

## 3. Estructura del Código y Optimización de Rendimiento

Para garantizar 60 FPS sin cuellos de botella:
1. **Zero MathTex en Updaters:** El HUD de telemetría utiliza exclusivamente `Text(..., font="Consolas")`, compilado directamente por Pango/Cairo en microsegundos sin invocar el compilador de LaTeX en cada frame.
2. **Primitivas Vectoriales `FastArrow3D`:** Conos y cilindros con resolución optimizada ($8 \times 8$ y $6 \times 6$) para evitar triangulaciones excesivas de mallas 3D.
3. **Malla de Disco Rotor Vectorizada:** Rims dobles con estrías perimétricas y 8 ranuras estroboscópicas que rotan a 10,000 RPM simulando el parpadeo de giro ultrarrápido.

---

## 4. Instrucciones de Ejecución y Renderizado

### Opción 1: Ejecución Directa con el CLI de Manim
Desde el directorio del proyecto:
```powershell
manim -pqh --format=mp4 render_gyroscope.py GyroscopePrecessionScene
```

O desde la raíz del repositorio Continuum Lab:
```powershell
manim -pqh --format=mp4 render_gyroscope.py GyroscopePrecessionScene
```

### Opción 2: Lanzador Batch Automatizado (Windows)
Doble clic o ejecución desde terminal:
```cmd
run_simulation.bat
```
Permite seleccionar:
* `[1]` Vista Previa Rápida (480p, 15 FPS)
* `[2]` Ultra-HD Producción (1080x1920, 60 FPS) — **Recomendada**
* `[3]` Master 4K Vertical (2160x3840, 60 FPS)

---

## 5. Verificación de Telemetría Dinámica

Al renderizar la simulación, el HUD superior exhibe en tiempo real:
* **ROTOR SPIN  :** `10,000 RPM (omega_s = 1,047 rad/s)`
* **MOMENTO ANG :** `L = 1.01 N·m·s`
* **TORQUE GRAV :** `tau = 6.13 N·m`
* **PRECESIÓN   :** `Omega_p = 6.07 rad/s`
* **ANGULO THETA:** `90.0° [ESTABLE]` $\to$ `94.6° [NUTACIÓN]`

Y la tarjeta técnica inferior responde de manera conclusiva:
> **¿POR QUÉ NO CAE POR LA GRAVEDAD?**
> *El torque gravitatorio no puede cambiar la magnitud de L, solo desvía su dirección en el plano horizontal ($d\vec{L}/dt = \vec{\tau}$).*
