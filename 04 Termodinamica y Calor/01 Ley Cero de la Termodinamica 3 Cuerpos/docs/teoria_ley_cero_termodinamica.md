# Continuum Lab — Física Térmica y Transferencia de Calor
## 01 Ley Cero de la Termodinámica: Equilibrio Térmico en Sistema de 3 Cuerpos en Contacto

---

### 1. Contexto Histórico y Fundamento Epistemológico

La **Ley Cero de la Termodinámica** es la piedra angular sobre la que descansa toda la física térmica y la metrología de temperaturas. Aunque las leyes Primera (conservación de energía) y Segunda (entropía e irreversibilidad) fueron formuladas a mediados del siglo XIX por Rudolf Clausius, William Thomson (Lord Kelvin) y James Prescott Joule, se asumía tácitamente la existencia del concepto de "temperatura" sin una base lógica rigurosa.

En **1935**, el físico y astrónomo británico **Ralph H. Fowler** (al revisar el texto clásico de E. A. Guggenheim) formalizó el postulado:
> *"Si dos cuerpos A y B están individualmente en equilibrio térmico con un tercer cuerpo C, entonces están en equilibrio térmico entre sí."*

Dado que este principio precede conceptualmente a la Primera Ley (al definir qué es una temperatura antes de cuantificar calor y trabajo), no podía llamarse "Tercera Ley" (nombre ya asignado al teorema de Nernst en 1906). Por tanto, Fowler y Guggenheim le asignaron el nombre universal de **Ley Cero**.

---

### 2. Formulación Matemática de la Relación de Equivalencia

En teoría de conjuntos y física matemática, el contacto térmico define una **relación de equivalencia** $\sim_T$ sobre el espacio de estados termodinámicos de los sistemas macroscópicos:

1. **Reflexividad**: Todo sistema térmico está en equilibrio consigo mismo:
   $$A \sim_T A$$
2. **Simetría**: Si $A$ está en equilibrio con $B$, $B$ está en equilibrio con $A$:
   $$A \sim_T B \iff B \sim_T A$$
3. **Transitividad (Postulado de Fowler)**:
   $$A \sim_T C \quad \land \quad B \sim_T C \implies A \sim_T B$$

Por el **Teorema Fundamental de las Relaciones de Equivalencia**, esta relación particiona el espacio de estados en clases de equivalencia disjuntas llamadas **isotermas**. A cada clase se le asigna un número real único $T$: la **Temperatura Empírica**. El tercer cuerpo $C$ actúa precisamente como el **termómetro** o patrón de referencia.

---

### 3. Modelo Físico de Transporte: Conducción 2D Multimaterial

En el continuo espacial $\Omega \subset \mathbb{R}^2$, la transferencia de energía interna dentro de un ensamble de 3 sólidos en contacto íntimo se rige por la **Ecuación Diferencial de Difusión de Calor**:

$$\rho(\mathbf{x}) c_p(\mathbf{x}) \frac{\partial T(\mathbf{x}, t)}{\partial t} = \nabla \cdot \big( k(\mathbf{x}) \nabla T(\mathbf{x}, t) \big)$$

donde:
- $T(\mathbf{x}, t)$ es el campo escalar de temperatura en el punto $\mathbf{x} = (x, y)$ y tiempo $t$ [$\text{K}$ o $^\circ\text{C}$].
- $k(\mathbf{x})$ es la conductividad térmica local [$\text{W}/(\text{m}\cdot\text{K})$].
- $\rho(\mathbf{x})$ es la densidad de masa [$\text{kg}/\text{m}^3$].
- $c_p(\mathbf{x})$ es el calor específico a presión constante [$\text{J}/(\text{kg}\cdot\text{K})$].

El vector de **flujo de calor por conducción** está dado por la **Ley de Fourier**:
$$\mathbf{q}(\mathbf{x}, t) = -k(\mathbf{x}) \nabla T(\mathbf{x}, t) \quad \left[\frac{\text{W}}{\text{m}^2}\right]$$

---

### 4. Propiedades Termofísicas de los 3 Cuerpos

El simulador implementa un sistema tribloque compuesto por materiales de ingeniería reales:

| Propiedad Termofísica | Cuerpo A (Hot Reservoir) | Cuerpo C (Sonda Mediadora) | Cuerpo B (Cold Reservoir) |
| :--- | :---: | :---: | :---: |
| **Material Base** | Cobre Electrolítico (Cu) | Acero Inox Austenítico | Aluminio Grado Aero (Al) |
| **Conductividad $k$ [$\text{W}/(\text{m}\cdot\text{K})$]** | $401.0$ | $54.0$ | $205.0$ |
| **Densidad $\rho$ [$\text{kg}/\text{m}^3$]** | $8960.0$ | $7900.0$ | $2700.0$ |
| **Calor Específico $c_p$ [$\text{J}/(\text{kg}\cdot\text{K})$]** | $385.0$ | $500.0$ | $900.0$ |
| **Cap. Volumétrica $\rho c_p$ [$\text{J}/(\text{m}^3\cdot\text{K})$]** | $3,449,600$ | $3,950,000$ | $2,430,000$ |
| **Difusividad Térmica $\alpha$ [$\text{m}^2/\text{s}$]** | $1.162 \times 10^{-4}$ | $1.367 \times 10^{-5}$ | $8.436 \times 10^{-5}$ |
| **Temperatura Inicial $T_0$** | $+100.0^\circ\text{C}$ ($373.15\text{ K}$) | $+25.0^\circ\text{C}$ ($298.15\text{ K}$) | $0.0^\circ\text{C}$ ($273.15\text{ K}$) |

---

### 5. Conservación de la Energía y Solución Analítica Global ($T_{eq}$)

Dado que el ensamble está térmicamente aislado del entorno exterior (fronteras adiabáticas de Neumann, $\mathbf{q} \cdot \mathbf{n} = 0$ en $\partial \Omega$):

$$\frac{d E_{tot}}{dt} = \frac{d}{dt} \iint_{\Omega} \rho(\mathbf{x}) c_p(\mathbf{x}) T(\mathbf{x}, t) \, d\Omega = \oint_{\partial \Omega} -k \nabla T \cdot \mathbf{n} \, ds = 0$$

Por tanto, la energía interna total $E_{tot}$ permanece estrictamente constante en el tiempo (Primera Ley de la Termodinámica).

La **Temperatura de Equilibrio Global Invariante** $T_{eq}$ cuando $t \to \infty$ y $\nabla T \to 0$ se deriva en forma cerrada como la media ponderada por capacitancia térmica:

$$T_{eq} = \frac{\iint_{\Omega} \rho(\mathbf{x}) c_p(\mathbf{x}) T(\mathbf{x}, 0) \, d\Omega}{\iint_{\Omega} \rho(\mathbf{x}) c_p(\mathbf{x}) \, d\Omega} = \frac{C_A T_{A,0} + C_C T_{C,0} + C_B T_{B,0}}{C_A + C_C + C_B}$$

donde $C_i = m_i c_{p,i} = \rho_i c_{p,i} V_i$ es la capacitancia térmica integral del cuerpo $i$.
Para la geometría calibrada del simulador:
$$T_{eq} = 46.20^\circ\text{C} \quad (319.35\text{ K})$$

---

### 6. Estabilidad de Lyapunov y Generación de Entropía

Para demostrar que el estado uniforme $T(\mathbf{x}) = T_{eq}$ es un **atractor global asintóticamente estable**, definimos el funcional de energía de Lyapunov:

$$V[T] = \frac{1}{2} \iint_{\Omega} \rho c_p \big(T(\mathbf{x}, t) - T_{eq}\big)^2 \, d\Omega \ge 0$$

Diferenciando respecto al tiempo y aplicando el Teorema de la Divergencia de Gauss con condiciones adiabáticas:

$$\frac{dV}{dt} = \iint_{\Omega} (T - T_{eq}) \nabla \cdot (k \nabla T) \, d\Omega = -\iint_{\Omega} k \|\nabla T\|^2 \, d\Omega \le 0$$

Dado que $k > 0$, $\frac{dV}{dt} = 0$ ocurre **únicamente** si $\|\nabla T\| = 0$ en todo el dominio, lo cual exige $T(\mathbf{x}) \equiv T_{eq}$.

Simultáneamente, la **tasa de generación de entropía** $\dot{S}_{gen}$ debida a la irreversibilidad de la conducción es:

$$\dot{S}_{gen} = \iint_{\Omega} \frac{k \|\nabla T\|^2}{T^2} \, d\Omega \ge 0$$

A medida que el calor se difunde y el gradiente térmico se atenúa, $\dot{S}_{gen}(t) \to 0$, marcando la consecución irreversible del equilibrio térmico y demostrando la compatibilidad perfecta entre la Ley Cero y la Segunda Ley de la Termodinámica.

---

### 7. Formulación Numérica: Volúmenes Finitos Conservativos

Para garantizar que el flujo de calor a través de las interfaces cobre-acero y acero-aluminio no sufra discontinuidades numéricas ni pérdidas de energía, se emplea la **media armónica interfacial** de conductividades:

$$k_{i+1/2, j} = \frac{2 \, k_{i, j} \, k_{i+1, j}}{k_{i, j} + k_{i+1, j}}$$

El paso temporal explícito respeta estrictamente el límite de estabilidad de Von Neumann (CFL):

$$\Delta t_{stable} \le \frac{1}{4 \alpha_{max}} \min(\Delta x, \Delta y)^2$$

El algoritmo ejecuta subciclado automático continuo, asegurando estabilidad incondicional y renderizado submilimétrico sin pixeles toscos.
