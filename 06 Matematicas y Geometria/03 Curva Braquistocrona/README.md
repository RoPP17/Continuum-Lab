# Continuum Lab — La Paradoja de la Curva Braquistócrona (Johann Bernoulli, 1696)
### *División 06: Matemáticas y Geometría // Dinámica Analítica y Cálculo de Variaciones*

---

## 🌌 Visión General y Resumen del Proyecto

Este módulo de **Continuum Lab** modela, simula y renderiza en ultra-alta definición vectorial (**1080x1920 a 60 FPS**, formato 9:16 vertical para TikTok / Shorts / Reels) la célebre carrera de la **Curva Braquistócrona** propuesta por Johann Bernoulli en 1696.

Demuestra de forma matemática y visual rigurosa por qué **la línea recta (el camino geométrico más corto) NO es el camino más rápido** bajo un campo gravitatorio constante, resolviendo la paradoja cinemática mediante el **Cálculo de Variaciones** y la formulación de **Euler-Lagrange**.

---

## 📐 Fundamentación Matemática y Física Teórica

### 1. El Problema Variacional de Bernoulli
Sean dos puntos fijos en el plano vertical:
- **Punto Inicial (A):** $(x_A, y_A) = (0.0, 4.0)\text{ m}$ (partiendo del reposo $v_0 = 0$)
- **Punto Final (B):** $(x_B, y_B) = (7.0, -3.0)\text{ m}$
- **Aceleración Gravitatoria:** $g = 9.81\text{ m/s}^2$ (hacia abajo, $-\hat{j}$)

Por la conservación de la energía mecánica total en un sistema sin fricción:
$$E = m g y_A = m g y + \frac{1}{2} m v^2 \implies v(y) = \sqrt{2 g (y_A - y)}$$

El tiempo infinitesimal de viaje $dt$ a lo largo de un elemento diferencial de arco $ds = \sqrt{dx^2 + dy^2} = \sqrt{1 + y'^2} dx$ viene dado por:
$$dt = \frac{ds}{v} = \frac{\sqrt{1 + y'(x)^2}}{\sqrt{2 g (y_A - y)}} dx$$

El tiempo total de recorrido es la funcional de acción:
$$T[y] = \int_{x_A}^{x_B} \frac{\sqrt{1 + y'(x)^2}}{\sqrt{2 g (y_A - y)}} dx$$

### 2. La Ecuación de Euler-Lagrange y la Identidad de Beltrami
Queremos encontrar la curva $y(x)$ que minimiza $T[y]$, es decir, $\delta T[y] = 0$:
$$\frac{\partial F}{\partial y} - \frac{d}{dx}\left(\frac{\partial F}{\partial y'}\right) = 0, \quad \text{donde } F(y, y') = \frac{\sqrt{1 + y'^2}}{\sqrt{2 g (y_A - y)}}$$

Dado que el integrando $F(y, y')$ no depende explícitamente de $x$ ($\frac{\partial F}{\partial x} = 0$), se aplica la **Identidad de Beltrami**:
$$F - y' \frac{\partial F}{\partial y'} = C = \text{constante}$$

Sustituyendo $F$ y simplificando:
$$\frac{\sqrt{1 + y'^2}}{\sqrt{2 g (y_A - y)}} - y' \frac{y'}{\sqrt{2 g (y_A - y)}\sqrt{1 + y'^2}} = \frac{1}{\sqrt{2 g (y_A - y)}\sqrt{1 + y'^2}} = \frac{1}{\sqrt{2 k}}$$

Elevando al cuadrado y reordenando:
$$(y_A - y)(1 + y'^2) = 2 r = \text{constante}$$

### 3. Solución Paramétrica: La Cicloide Invertida
Efectuando el cambio de variable $y' = -\tan\left(\frac{\theta}{2}\right)$, se obtienen las ecuaciones paramétricas exactas de la **cicloide generada por una rueda de radio $r$ rodando por debajo de la recta $y = y_A$**:
$$x(\theta) = r (\theta - \sin\theta)$$
$$y(\theta) = y_A - r (1 - \cos\theta)$$

Ajustando los parámetros de contorno para pasar exactamente por el punto final $B(7.0, -3.0)$:
$$\frac{x(\theta_{\max})}{y_A - y(\theta_{\max})} = \frac{r(\theta_{\max} - \sin\theta_{\max})}{r(1 - \cos\theta_{\max})} = \frac{7.0}{7.0} = 1.0$$

Resolviendo numéricamente mediante el método de Brent/bisección:
$$\theta_{\max} \approx 2.412011\text{ rad} \quad (138.20^\circ)$$
$$r = \frac{7.0}{1 - \cos(\theta_{\max})} \approx 4.010486\text{ m}$$

### 4. Evolución Cinemática Exacta $\theta(t)$
El diferencial de longitud de arco sobre la cicloide es:
$$ds = 2 r \sin\left(\frac{\theta}{2}\right) d\theta$$
La velocidad instantánea es:
$$v = \sqrt{2 g (y_A - y)} = 2 \sqrt{g r} \sin\left(\frac{\theta}{2}\right)$$
Por tanto:
$$\frac{ds}{dt} = v \implies 2 r \sin\left(\frac{\theta}{2}\right) \frac{d\theta}{dt} = 2 \sqrt{g r} \sin\left(\frac{\theta}{2}\right) \implies \frac{d\theta}{dt} = \sqrt{\frac{g}{r}} = \text{constante}!$$

¡La velocidad angular de fase $\omega = \sqrt{g/r}$ es **estrictamente constante**!
$$\theta(t) = \sqrt{\frac{g}{r}} \cdot t$$
Y el tiempo total de recorrido físico es exacto:
$$T_{\text{cicloide}} = \theta_{\max} \sqrt{\frac{r}{g}} \approx 1.5422\text{ s}$$

---

## 🏁 Comparativa de las 4 Pistas en Competencia

| Puesto | Pista | Modelo Matemático | Longitud $L$ (m) | Tiempo Físico (s) | Tiempo Calibrado (s) | $v_{\text{final}}$ (m/s) |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| 🥇 **1º** | **Cicloide (Braquistócrona)** | $x = r(\theta - \sin\theta), \; y = 4 - r(1 - \cos\theta)$ | $10.364\text{ m}$ | **$1.542\text{ s}$** | **$1.320\text{ s}$** | $11.72\text{ m/s}$ |
| 🥈 **2º** | **Círculo (Arco)** | $(x - x_c)^2 + (y - y_c)^2 = R^2$ | $10.125\text{ m}$ | **$1.550\text{ s}$** | **$1.390\text{ s}$** | $11.72\text{ m/s}$ |
| 🥉 **3º** | **Parábola** | $y = 4 - x - 0.10 x(7 - x)$ | $10.041\text{ m}$ | **$1.583\text{ s}$** | **$1.450\text{ s}$** | $11.72\text{ m/s}$ |
| ❌ **4º** | **Recta (Euclídea)** | $y = 4 - x$ | $9.899\text{ m}$ | **$1.689\text{ s}$** | **$1.620\text{ s}$** | $11.72\text{ m/s}$ |

### 💡 Resolución de la Paradoja:
1. **La Pista Recta** tiene la distancia euclidiana mínima ($9.899\text{ m}$), pero su aceleración inicial es baja ($a = g\sin(45^\circ) = 6.94\text{ m/s}^2$). Permanece demasiado tiempo a velocidades reducidas.
2. **La Pista Cicloide** tiene un camino más largo ($10.364\text{ m}$, un $+4.7\%$ más de trayectoria), pero su pendiente inicial es cuasi-vertical ($y' \to -\infty$), permitiendo una caída libre instantánea que transforma la energía potencial gravitatoria en energía cinética inmediata.
3. La velocidad promedio en la Cicloide es tan superior que aventaja a todas las demás pistas y llega en **primer lugar indiscutible**.
4. Por el principio de conservación de la energía mecánica, **todas las esferas llegan con la MISMA velocidad final**:
$$v_{\text{meta}} = \sqrt{2 g \Delta h} = \sqrt{2 \times 9.81 \times 7.0} = 11.719\text{ m/s}$$

---

## 🎨 Especificaciones Visuales y Cinemáticas (9:16 Vertical)

- **Resolución:** $1080 \times 1920$ a **60 FPS**.
- **Fondo:** `#0B0F19` (Cybernetic Deep Navy).
- **Zonas Seguras:**
  - Superior: $> 160\text{ px}$ ($Y < 6.67$).
  - Inferior: $> 320\text{ px}$ ($Y > -5.33$).
- **Paleta Neón:**
  - Cicloide: Cian Neón `#00F0FF` con estela de partículas chispeantes.
  - Círculo: Violeta Neón `#7928CA`.
  - Parábola: Oro Ámbar `#FFE600`.
  - Recta: Rojo Carmesí `#FF0055`.
  - Meta & Victoria: Verde Neón `#00FF66`.
- **Telemetría HUD:**
  - Tipografía digital monoespaciada en fuente `Consolas`.
  - Cronómetros digitales en milisegundos reales para cada esfera.
  - Velocímetro instantáneo $v(t)$ en $\text{m/s}$.

---

## 🚀 Guía de Ejecución

Desde la terminal en el directorio del proyecto:

```bash
# 1. Resumen analítico en consola
python main.py

# 2. Renderizado de video completo 1080x1920 a 60 FPS
python main.py --render

# 3. Renderizado en baja resolución para previsualización rápida
python main.py --preview

# 4. Generación del modelo dinámico Excel (.xlsx) con fórmulas nativas
python main.py --benchmark

# 5. Ejecución de la suite completa de pruebas unitarias
python main.py --test
```
