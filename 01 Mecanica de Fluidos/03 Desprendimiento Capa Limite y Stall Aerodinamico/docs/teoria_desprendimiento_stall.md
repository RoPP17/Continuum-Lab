# CONTINUUM LAB // FUNDAMENTOS TEÓRICOS: DESPRENDIMIENTO DE CAPA LÍMITE Y STALL AERODINÁMICO

**Módulo:** 01 Mecánica de Fluidos / 03 Desprendimiento Capa Límite y Stall Aerodinámico  
**Ecuaciones Gobernantes:** Navier-Stokes incompresible, Ecuaciones de Capa Límite de Prandtl, Integral de von Kármán, Polinomios de Pohlhausen  
**Perfil de Estudio:** NACA 0012 ($c = 1.0\text{ m}$, $U_\infty = 50\text{ m/s}$, $Re_c = 1.0 \times 10^6$)

---

## 1. Ecuaciones Gobernantes de la Mecánica de Fluidos

Para un flujo bidimensional incompresible de un fluido newtoniano con densidad constante $\rho$ y viscosidad cinemática $\nu = \mu / \rho$, las ecuaciones de Navier-Stokes y de continuidad se expresan como:

$$\frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} = 0$$

$$\frac{\partial u}{\partial t} + u\frac{\partial u}{\partial x} + v\frac{\partial u}{\partial y} = -\frac{1}{\rho}\frac{\partial p}{\partial x} + \nu \left( \frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2} \right)$$

$$\frac{\partial v}{\partial t} + u\frac{\partial v}{\partial x} + v\frac{\partial v}{\partial y} = -\frac{1}{\rho}\frac{\partial p}{\partial y} + \nu \left( \frac{\partial^2 v}{\partial x^2} + \frac{\partial^2 v}{\partial y^2} \right)$$

---

## 2. Reducción de Capa Límite de Ludwig Prandtl ($Re \gg 1$)

A números de Reynolds elevados ($Re = U_\infty c / \nu \gg 1$), los efectos viscosos quedan confinados a una delgada región adyacente a la superficie sólida de espesor $\delta(x) \ll c$:

$$\frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} = 0$$

$$u\frac{\partial u}{\partial x} + v\frac{\partial u}{\partial y} = U_e(x)\frac{dU_e}{dx} + \nu \frac{\partial^2 u}{\partial y^2}$$

$$\frac{\partial p}{\partial y} \approx 0 \implies p(x,y) = p_e(x)$$

Donde la relación de Euler en el borde exterior relaciona la velocidad potencial $U_e(x)$ con el gradiente de presión impuesto:

$$-\frac{1}{\rho}\frac{dp}{dx} = U_e(x)\frac{dU_e}{dx}$$

Condiciones de contorno en la pared sólida ($y = 0$):
$$u(x,0) = 0, \quad v(x,0) = 0 \quad (\text{No-deslizamiento})$$

En el infinito exterior ($y \to \infty$):
$$\lim_{y \to \infty} u(x,y) = U_e(x)$$

---

## 3. Dinámica del Gradiente Adverso de Presión ($\partial p / \partial x > 0$)

Evaluando la ecuación de momento de Prandtl exactamente en la pared ($y = 0$), donde $u = v = 0$:

$$\left.\nu \frac{\partial^2 u}{\partial y^2}\right|_{y=0} = \frac{1}{\rho}\frac{dp}{dx} = -U_e\frac{dU_e}{dx}$$

Esta condición de curvatura fija de manera unívoca la topología del perfil de velocidades:
1. **Gradiente Favorable** ($\partial p / \partial x < 0$):
   $$\left.\frac{\partial^2 u}{\partial y^2}\right|_{w} < 0$$
   El perfil es completamente convexo en todo el espesor. No existen puntos de inflexión.
2. **Gradiente Adverso** ($\partial p / \partial x > 0$):
   $$\left.\frac{\partial^2 u}{\partial y^2}\right|_{w} > 0$$
   Dado que asintóticamente hacia el borde exterior $\partial^2 u / \partial y^2 < 0$, **debe existir necesariamente un punto de inflexión** interior $y_i$ tal que:
   $$\left.\frac{\partial^2 u}{\partial y^2}\right|_{y_i} = 0$$
   Por el **Teorema del Punto de Inflexión de Rayleigh**, cualquier flujo con un punto de inflexión en su perfil de velocidad es dinámicamente inestable a perturbaciones no viscosas (inviscid instability), promoviendo la transición y el desprendimiento turbulento.

---

## 4. Método Integral de Pohlhausen y Criterio de Desprendimiento

Aproximando el perfil de velocidad adimensionado mediante un polinomio de cuarto grado en $\eta = y / \delta$:

$$\frac{u(y)}{U_e} = 2\eta - 2\eta^3 + \eta^4 + \frac{\Lambda}{6}\eta(1 - \eta)^3$$

Donde el parámetro adimensional de Pohlhausen $\Lambda$ se define como:

$$\Lambda = \frac{\delta^2}{\nu}\frac{dU_e}{dx} = -\frac{\delta^2}{\mu U_e}\frac{dp}{dx}$$

La tensión de cizalladura en la pared $\tau_w$ es:

$$\tau_w = \left.\mu \frac{\partial u}{\partial y}\right|_{y=0} = \frac{\mu U_e}{\delta} \left( 2 + \frac{\Lambda}{6} \right)$$

### El Criterio Exacto de Separación:
El flujo se desprende de la pared cuando la cizalladura superficial se anula ($\tau_w = 0$):

$$2 + \frac{\Lambda}{6} = 0 \implies \Lambda_{\mathrm{sep}} = -12.0$$

* Para $\Lambda > -12$: Flujo adherido con $\tau_w > 0$.
* Para $\Lambda = -12$: **Punto de desprendimiento de capa límite**.
* Para $\Lambda < -12$: **Flujo inverso** (recirculación y vórtices retrógrados en la pared, $(\partial u / \partial y)_w < 0$).

---

## 5. Teoría de Perfil Delgado vs Colapso de Entrada en Pérdida

En régimen adherido lineal ($\alpha \le 8^\circ$):

$$C_L = 2\pi(\alpha - \alpha_0)$$

Para un perfil simétrico NACA 0012 a $\alpha = 4.0^\circ = 0.06981\text{ rad}$:
$$C_L(4^\circ) = 2\pi \times 0.06981 = 0.4386 \approx 0.44$$

Al incrementar el ángulo de ataque:
* **$\alpha = 15.5^\circ$**: El coeficiente de sustentación alcanza su cota máxima $C_{L,\max} \approx 1.55$.
* **$\alpha = 18.5^\circ$ (Stall Profundo)**: El punto de desprendimiento $x_{\mathrm{sep}} / c$ colapsa hacia adelante, situándose en el $15\%$ de la cuerda. La burbuja de recirculación desprendida rompe la circulación de Kutta-Joukowski $\Gamma$, provocando el **colapso del $74\%$ de la sustentación**:
  $$C_L(18.5^\circ) = 1.55 \times (1 - 0.74) = 0.403 \approx 0.40$$
* El arrastre $C_D$ se dispara de $0.015$ a $0.288$ ($>1400\%$), excitando el fenómeno aeroelástico de **stall buffet** (vibraciones estructurales severas inducidas por desprendimiento de vórtices).

---

## 6. Soluciones de Ingeniería para Retrasar la Pérdida

1. **Generadores de Vórtices (VGs):** Pequeñas aletas triangulares o rectangulares que transfieren momento cinético de la corriente libre hacia el interior de la capa límite, energizando el perfil de velocidad y retrasando $\tau_w \to 0$.
2. **Succión Activa de Capa Límite:** Aspiración del fluido de baja energía en la pared a través de ranuras o superficies porosas, eliminando el fluido frenado antes de que ocurra la inversión de velocidad.
3. **Soplado Tangencial (Coanda Effect):** Inyección de chorros de alta velocidad paralelos a la superficie para revitalizar el gradiente superficial.
4. **Slats y Flaps Ranurados:** Creación de conductos convergentes que aceleran el aire del intradós hacia el extradós, inyectando energía fresca en la zona de máximo gradiente adverso.
