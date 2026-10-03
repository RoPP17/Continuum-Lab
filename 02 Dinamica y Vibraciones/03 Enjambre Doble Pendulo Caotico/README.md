# Continuum Lab — Caos Determinista: Enjambre de 50 Doble Péndulos Planos

**División**: `02 Dinamica y Vibraciones / 03 Enjambre Doble Pendulo Caotico`  
**Autor**: Roberto Andrés Pepe Sánchez & Continuum Lab  
**Formato de Salida**: Video Vectorial Ultra-HD 1080x1920 a 60 FPS (9:16 Vertical)  
**Duración**: 15.00 segundos exactos (900 cuadros)  

---

## 1. Fundamentación Física y Ecuaciones de Euler-Lagrange

El doble péndulo plano sin fricción es uno de los sistemas físicos más emblemáticos de la **Dinámica Hamiltoniana No Lineal**, exhibiendo una transición radical desde el movimiento regular hasta el caos determinista a energías moderadas y altas.

### Coordenadas Generalizadas y Posiciones Cartesianas
Sean $q = (\theta_1, \theta_2)^T$ los ángulos de desviación respecto a la vertical descendente:
- **Masa 1 ($m_1 = 1.0\text{ kg}, L_1 = 1.5\text{ m}$)**:
  $$x_1 = L_1 \sin\theta_1, \quad y_1 = -L_1 \cos\theta_1$$
- **Masa 2 ($m_2 = 1.0\text{ kg}, L_2 = 1.5\text{ m}$)**:
  $$x_2 = x_1 + L_2 \sin\theta_2, \quad y_2 = y_1 - L_2 \cos\theta_2$$

### Lagrangiano del Sistema
$$\mathcal{L} = T - V$$

Donde la energía cinética $T$ y la energía potencial gravitatoria $V$ son:
$$T = \frac{1}{2}(m_1 + m_2) L_1^2 \dot{\theta}_1^2 + \frac{1}{2}m_2 L_2^2 \dot{\theta}_2^2 + m_2 L_1 L_2 \dot{\theta}_1 \dot{\theta}_2 \cos(\theta_1 - \theta_2)$$
$$V = -(m_1 + m_2)g L_1 \cos\theta_1 - m_2 g L_2 \cos\theta_2$$

### Ecuaciones de Movimiento No Lineales
Aplicando las ecuaciones de Euler-Lagrange $\frac{d}{dt}\left(\frac{\partial \mathcal{L}}{\partial \dot{\theta}_i}\right) - \frac{\partial \mathcal{L}}{\partial \theta_i} = 0$:

$$\begin{aligned}
\ddot{\theta}_1 &= \frac{-g\big[(m_1 + m_2)\sin\theta_1 - m_2\sin\theta_2\cos\Delta\theta\big] - m_2\sin\Delta\theta\big(L_2\dot{\theta}_2^2 + L_1\dot{\theta}_1^2\cos\Delta\theta\big)}{L_1\big(m_1 + m_2\sin^2\Delta\theta\big)} \\
\ddot{\theta}_2 &= \frac{\sin\Delta\theta\big[(m_1 + m_2)L_1\dot{\theta}_1^2 + m_2 L_2\dot{\theta}_2^2\cos\Delta\theta\big] + (m_1 + m_2)g\big(\sin\theta_1\cos\Delta\theta - \sin\theta_2\big)}{L_2\big(m_1 + m_2\sin^2\Delta\theta\big)}
\end{aligned}$$

Donde $\Delta\theta = \theta_1 - \theta_2$.

---

## 2. Enjambre de Péndulos y Sensibilidad a Condiciones Iniciales

Se modela un enjambre de $N = 50$ sistemas desacoplados ($k = 0, 1, \dots, 49$), donde cada péndulo $k$ se inicializa con una perturbación infinitesimal respecto al péndulo base:

$$\theta_{1,k}(0) = \theta_{1,0} + k \cdot \Delta\theta_0, \quad \text{con } \theta_{1,0} = 120.0^\circ \, (2.0944\text{ rad}), \quad \Delta\theta_0 = 1.0 \times 10^{-6}\text{ rad}$$
$$\theta_{2,k}(0) = \theta_{2,0} = -60.0^\circ \, (-1.0472\text{ rad}), \quad \dot{\theta}_{1,k}(0) = \dot{\theta}_{2,k}(0) = 0$$

- La diferencia angular entre péndulos adyacentes es de apenas **$0.000057^\circ$** ($5.7 \times 10^{-5}$ grados).
- La separación espacial inicial entre el péndulo $0$ y el péndulo $49$ en la masa terminal $m_2$ es de apenas **$0.0735\text{ mm}$** ($73.5\text{ \mu m}$), totalmente invisible para el ojo humano.

---

## 3. Dinámica del Caos y Exponente de Lyapunov

En sistemas caóticos hamiltonianos, dos trayectorias que comienzan a una distancia infinitesimal $|\Delta \mathbf{X}_0|$ divergen exponencialmente con el tiempo:

$$|\Delta \mathbf{X}(t)| \approx |\Delta \mathbf{X}_0| \, e^{\lambda t}$$

Donde $\lambda \approx 1.42\text{ s}^{-1}$ es el **Exponente Máximo de Lyapunov**.

### Las Tres Fases de la Secuencia (15.0 segundos):
1. **Fase 1 [0.0s - 5.5s] (Orden Aparente)**:
   - La separación $|\Delta \mathbf{X}(t)|$ permanece por debajo de $2\text{ mm}$.
   - Los 50 péndulos se encuentran perfectamente superpuestos; la masa visual parece una sola barra metálica blanca.
2. **Fase 2 [5.5s - 7.5s] (Bifurcación de Lyapunov)**:
   - Se alcanza el horizonte de predictibilidad $t_L = \frac{1}{\lambda}\ln\left(\frac{\Delta_{macro}}{\Delta_0}\right)$.
   - La separación cruza el umbral del centímetro ($1.18\text{ cm}$).
   - La barra blanca sufre una transición de fase iridiscente, fragmentándose en una cinta prismática multicolor.
3. **Fase 3 [7.5s - 15.0s] (Explosión Caótica en Abanico)**:
   - La divergencia exponencial domina por completo: $|\Delta \mathbf{X}| > 0.81\text{ m}$ a los $10\text{ s}$, alcanzando hasta **$6.84\text{ metros}$** de dispersión espacial a los $15\text{ s}$.
   - Los 50 péndulos se abren en un abanico cromático fluorescente que barre el lienzo con estelas de luz continua.

---

## 4. Integración Numérica DOP853 y Conservación Hamiltoniana

Para garantizar rigor físico absoluto y descartar cualquier artefacto espurio de disipación o inestabilidad numérica:
- **Método**: Runge-Kutta de orden 8(5,3) Dormand-Prince (`DOP853`).
- **Tolerancias**: `rtol = 1e-9`, `atol = 1e-12`.
- **Conservación de Energía**:
  $$\frac{|\Delta E(t)|}{E_0} < 7.65 \times 10^{-8} \quad (\text{Conservación del 99.99999\%})$$

---

## 5. Arquitectura Visual y Safe Zones (9:16 Vertical)

- **Fondo**: Deep Cosmic Void (`#0B0F19`).
- **Safe Zone Superior ($Y > 5.5$)**:
  - Telemetría en tiempo real renderizada con fuente monoespaciada `Consolas`.
  - Despliegue de métricas: tamaño del enjambre, perturbación angular, exponente de Lyapunov, divergencia teórica y separación métrica en vivo.
- **Safe Zone Inferior ($Y < -5.5$)**:
  - Callout de alto impacto para retención móvil:
    > *"SEGUNDO 0 AL 5: PARECEN UN SOLO PÉNDULO."*  
    > *"SEGUNDO 7: LA MARIPOSA DESTRUYE EL ORDEN."*
- **Paleta Cromática Cyberpunk**:
  - Cian Neón (`#00F0FF`) $\to$ Azul Eléctrico (`#0070F3`) $\to$ Violeta Profundo (`#7928CA`) $\to$ Magenta Carmesí (`#FF0055`) $\to$ Amarillo Neón (`#FFE600`).
- **Trazadores de Punta (Estelas Cometa)**:
  - Longitud de 36 cuadros (~0.60 s) con degradado continuo de opacidad ($0.90 \to 0.03$).

---

## 6. Estructura del Proyecto

```
03 Enjambre Doble Pendulo Caotico/
├── benchmarks/
│   └── Doble_Pendulo_Conservacion_Energia.xlsx    # Benchmark dinámico con fórmulas vivas
├── src/
│   ├── physics/
│   │   ├── double_pendulum_swarm.py               # Solucionador vectorial DOP853
│   │   └── export_excel_benchmark.py              # Exportador analítico OpenPyXL
│   └── visualization/
│       └── manim_swarm_scene.py                   # Escena vectorial Manim 9:16
├── tests/
│   └── test_swarm_physics.py                      # Suite de tests físicos con pytest
├── main.py                                        # Orquestador general
├── README.md                                      # Documentación técnica
└── run.bat                                        # Lanzador rápido en Windows
```

---

## 7. Ejecución

Para correr las pruebas físicas, generar el benchmark en Excel y compilar el video:

```powershell
python main.py
```
