# Mecánica Analítica: Mecanismo de 2 Barras con Collarín Deslizante y Aceleración de Coriolis

<div align="center">

**Continuum Lab — División 02: Dinámica y Vibraciones**  
*Formulación Cinemática Vectorial Rigurosa en Marcos de Referencia Móviles*

</div>

---

## 1. Geometría del Mecanismo y Marcos de Coordenadas

El mecanismo consta de:
1. **Bancada Fija (Eslabón 0):** Dos pivotes fijos en el plano cartesiano inercial:
   - $O_1 = (0, 0)$: Centro de rotación de la manivela impulsora.
   - $O_2 = (0, -d)$: Centro de rotación del balancín / guía ranurada.
2. **Manivela Impulsora (Barra 1, $O_1 A$):**
   - Longitud fija $L_1$.
   - Gira con ángulo $\theta_1(t)$ a velocidad angular $\omega_1 = \dot{\theta}_1$ y aceleración angular $\alpha_1 = \ddot{\theta}_1$.
3. **Collarín Deslizante (Slider en $A$):**
   - Articulado mediante un pasador al extremo $A$ de la manivela 1.
   - Desliza libremente a lo largo de la ranura mecanizada de la Barra 2.
4. **Guía Ranurada (Barra 2, $O_2 B$):**
   - Pivota en $O_2$ con ángulo $\theta_2(t)$, velocidad angular $\vec{\omega}_2 = \dot{\theta}_2 \hat{k}$ y aceleración angular $\vec{\alpha}_2 = \ddot{\theta}_2 \hat{k}$.

```
                 Y
                 ▲
                 │        Punto A (Collarín)
                 │       ┌───┐
                 │      /│ A │/
                 │     / └───┘
                 │    /  /  ▲
                 │   /  /   │ Barra 1 (Manivela L1)
                 │  /  /    │
                 │ /  / θ1  │
      ───────────O1─────────┼───────► X
                 │ \  \
                 │  \  \    Barra 2 (Guía ranurada)
                 │   \  \
                 │    \  \
                 │  d  \  \
                 │      \  \
                 ▼       \  \
                O2────────┴──┴────
```

---

## 2. Cinemática Absoluta del Pasador $A$ (Visto desde la Manivela 1)

El vector de posición de $A$ respecto al pivote fijo $O_1$ es:

$$\vec{r}_A = L_1 \cos\theta_1\,\hat{i} + L_1 \sin\theta_1\,\hat{j}$$

Derivando con respecto al tiempo:

$$\vec{v}_A = -L_1 \omega_1 \sin\theta_1\,\hat{i} + L_1 \omega_1 \cos\theta_1\,\hat{j}$$

$$\vec{a}_A = \left(-L_1 \omega_1^2 \cos\theta_1 - L_1 \alpha_1 \sin\theta_1\right)\hat{i} + \left(-L_1 \omega_1^2 \sin\theta_1 + L_1 \alpha_1 \cos\theta_1\right)\hat{j}$$

Cuando la velocidad de la manivela es constante ($\alpha_1 = 0$):

$$\vec{a}_A = -\omega_1^2 \vec{r}_A = -L_1 \omega_1^2 \left(\cos\theta_1\,\hat{i} + \sin\theta_1\,\hat{j}\right)$$

---

## 3. Cinemática en el Marco Móvil de la Barra Ranurada (Barra 2)

Definimos un sistema coordenado polar móvil con origen en $O_2 = (0, -d)$ y base ortonormal solidaria a la Barra 2:

$$\vec{r}_{A/O_2} = \vec{r}_A - \vec{r}_{O_2} = L_1 \cos\theta_1\,\hat{i} + (L_1 \sin\theta_1 + d)\,\hat{j}$$

La distancia radial $r_2$ y la orientación angular $\theta_2$ son:

$$r_2 = |\vec{r}_{A/O_2}| = \sqrt{L_1^2 \cos^2\theta_1 + (L_1 \sin\theta_1 + d)^2} = \sqrt{L_1^2 + d^2 + 2 L_1 d \sin\theta_1}$$

$$\theta_2 = \operatorname{atan2}(L_1 \sin\theta_1 + d,\; L_1 \cos\theta_1)$$

Los vectores unitarios radial y transversal son:

$$\hat{u}_{r2} = \cos\theta_2\,\hat{i} + \sin\theta_2\,\hat{j} = \frac{\vec{r}_{A/O_2}}{r_2}$$

$$\hat{u}_{\theta 2} = -\sin\theta_2\,\hat{i} + \cos\theta_2\,\hat{j} = \hat{k} \times \hat{u}_{r2}$$

---

## 4. Descomposición de Velocidades y Deslizamiento Relativo

La velocidad del punto $A$ observada desde el marco rotativo de la Barra 2 satisface la ecuación de transporte:

$$\vec{v}_A = \vec{v}_{O_2} + \vec{\omega}_2 \times \vec{r}_{A/O_2} + \vec{v}_{rel}$$

Como $O_2$ es un punto fijo, $\vec{v}_{O_2} = \vec{0}$.
- Velocidad de transporte rotacional: $\vec{\omega}_2 \times \vec{r}_{A/O_2} = (\dot{\theta}_2 \hat{k}) \times (r_2 \hat{u}_{r2}) = r_2 \dot{\theta}_2\,\hat{u}_{\theta 2}$.
- Velocidad de deslizamiento relativo a lo largo de la ranura: $\vec{v}_{rel} = \dot{r}_2\,\hat{u}_{r2}$.

Por lo tanto:

$$\vec{v}_A = \dot{r}_2\,\hat{u}_{r2} + r_2 \omega_2\,\hat{u}_{\theta 2}$$

Proyectando mediante producto punto sobre la base $\{\hat{u}_{r2}, \hat{u}_{\theta 2}\}$:

$$\dot{r}_2 = v_{rel} = \vec{v}_A \cdot \hat{u}_{r2} = v_{Ax} \cos\theta_2 + v_{Ay} \sin\theta_2$$

$$\omega_2 = \dot{\theta}_2 = \frac{\vec{v}_A \cdot \hat{u}_{\theta 2}}{r_2} = \frac{-v_{Ax} \sin\theta_2 + v_{Ay} \cos\theta_2}{r_2}$$

---

## 5. Teorema de Coriolis y los 5 Términos de Aceleración

Diferenciando la velocidad absoluta en el marco rotativo se obtiene la ecuación fundamental de los 5 términos:

$$\vec{a}_A = \vec{a}_{O_2} + \vec{a}_{\text{Euler}} + \vec{a}_{\text{centrípeta}} + \vec{a}_{\text{Coriolis}} + \vec{a}_{rel}$$

donde:
1. **Aceleración del origen:** $\vec{a}_{O_2} = \vec{0}$
2. **Aceleración de Euler (tangencial):** $\vec{a}_{\text{Euler}} = \vec{\alpha}_2 \times \vec{r}_{A/O_2} = r_2 \alpha_2\,\hat{u}_{\theta 2}$
3. **Aceleración Centrípeta de arrastre:** $\vec{a}_{\text{centrípeta}} = \vec{\omega}_2 \times (\vec{\omega}_2 \times \vec{r}_{A/O_2}) = -\omega_2^2 r_2\,\hat{u}_{r2}$
4. **Aceleración de Coriolis:** $\vec{a}_{\text{Coriolis}} = 2\,\vec{\omega}_2 \times \vec{v}_{rel} = 2\,\omega_2 \dot{r}_2\,\hat{u}_{\theta 2}$
5. **Aceleración Relativa del collarín:** $\vec{a}_{rel} = \ddot{r}_2\,\hat{u}_{r2}$

Agrupando por componentes ortogonales:

$$\vec{a}_A = \left(\ddot{r}_2 - \omega_2^2 r_2\right)\hat{u}_{r2} + \left(r_2 \alpha_2 + 2 \omega_2 \dot{r}_2\right)\hat{u}_{\theta 2}$$

### ¿Por qué existe el factor 2 en Coriolis?
La aceleración de Coriolis $2 \vec{\omega}_2 \times \vec{v}_{rel}$ surge de **dos contribuciones físicas idénticas**:
1. **Variación de la velocidad de transporte debido al cambio de radio:** Al deslizar el collarín con velocidad $\dot{r}_2$, se traslada a radios con mayor o menor velocidad circunferencial $\omega_2 r_2$. La derivada temporal aporta $\omega_2 \dot{r}_2\,\hat{u}_{\theta 2}$.
2. **Variación de la orientación del vector velocidad relativa:** El vector $\vec{v}_{rel} = \dot{r}_2 \hat{u}_{r2}$ cambia continuamente de dirección al girar el marco a velocidad $\vec{\omega}_2$. La derivada temporal aporta $\dot{r}_2 \frac{d\hat{u}_{r2}}{dt} = \dot{r}_2 (\omega_2 \hat{u}_{\theta 2})$.

Sumando ambas contribuciones independientes:

$$\vec{a}_{\text{Coriolis}} = \omega_2 \dot{r}_2\,\hat{u}_{\theta 2} + \omega_2 \dot{r}_2\,\hat{u}_{\theta 2} = 2 \omega_2 \dot{r}_2\,\hat{u}_{\theta 2}$$

---

## 6. Solución Analítica de las Incógnitas

Igualando los componentes de $\vec{a}_A$ conocidos desde la manivela:

$$a_{r2} = \vec{a}_A \cdot \hat{u}_{r2} = a_{Ax} \cos\theta_2 + a_{Ay} \sin\theta_2 = \ddot{r}_2 - \omega_2^2 r_2$$

$$a_{\theta 2} = \vec{a}_A \cdot \hat{u}_{\theta 2} = -a_{Ax} \sin\theta_2 + a_{Ay} \cos\theta_2 = r_2 \alpha_2 + 2 \omega_2 \dot{r}_2$$

Despejando de forma analítica exacta:

$$\ddot{r}_2 = a_{rel} = \vec{a}_A \cdot \hat{u}_{r2} + \omega_2^2 r_2$$

$$\alpha_2 = \frac{\vec{a}_A \cdot \hat{u}_{\theta 2} - 2 \omega_2 \dot{r}_2}{r_2}$$

Y el vector de Coriolis resulta:

$$\vec{a}_{\text{Coriolis}} = 2 \omega_2 \dot{r}_2 \begin{pmatrix} -\sin\theta_2 \\ \cos\theta_2 \end{pmatrix}$$

Esta formulación garantiza un error de reconstrucción idéntico a cero ($\|\vec{a}_A - \vec{a}_{\text{rec}}\| \approx 10^{-15}$).

---

## 7. Bifurcación Cinemática de Regímenes

- **Régimen Oscilante ($d > L_1$):**  
  La barra ranurada oscila como balancín en el sector angular $[-\theta_{max}, +\theta_{max}]$, donde $\theta_{max} = \arcsin(L_1/d)$. La velocidad angular $\omega_2$ se anula en los extremos y la aceleración de Coriolis cambia periódicamente de signo, generando una oscilación armónica limpia.

- **Régimen de Rotación Continua Whitworth ($d < L_1$):**  
  La barra ranurada efectúa rotaciones completas de 360°. Presenta una carrera lenta de trabajo y una carrera rápida de retorno, característica de los mecanismos industriales de limadoras.
