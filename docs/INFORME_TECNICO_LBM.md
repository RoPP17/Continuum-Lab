# CONTINUUM LAB — INFORME TÉCNICO Y DERIVACIÓN FÍSICA
## Dinámica de Fluidos Computacional: Método de Lattice Boltzmann (LBM D2Q9-BGK)
**Autor:** Roberto Andrés Pepe Sánchez (@RoPP17)  
**Institución:** Universidad Técnica de Ambato (UTA) — Facultad de Ingeniería Civil y Mecánica  
**División:** Continuum Lab / Simulación y Modelado Computacional  

---

### 1. Marco Teórico y Ecuaciones de Gobierno
El comportamiento de un fluido incompresible, isotermo y homogéneo con densidad constante $\rho_0$ y viscosidad cinemática $\nu = \mu / \rho_0$ está gobernado por las ecuaciones diferenciales en derivadas parciales de Navier-Stokes:

$$\nabla \cdot \mathbf{u} = 0$$

$$\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u} = -\frac{1}{\rho_0}\nabla p + \nu \nabla^2 \mathbf{u} + \mathbf{g}$$

En lugar de discretizar el continuo espacial y temporalmente mediante métodos tradicionales (FVM, FEM o FDM con acoplamiento presión-velocidad tipo SIMPLE/PISO), el **Método de Lattice Boltzmann (LBM)** opera en una escala mesoscópica a través de la evolución cinética de las funciones de distribución de probabilidad de partículas $f_i(\mathbf{x}, t)$.

---

### 2. Formulación D2Q9 y Operador de Relajación BGK
En un mallado bidimensional con 9 velocidades discretas (**D2Q9**), las partículas se desplazan a lo largo de un conjunto discreto de vectores de velocidad $\mathbf{c}_i \in \mathbb{R}^2$ ($i = 0, \dots, 8$):

$$\mathbf{c}_0 = (0, 0)$$
$$\mathbf{c}_{1,2,3,4} = (\pm 1, 0), (0, \pm 1) \quad (\text{Direcciones ortogonales, peso } w_i = 1/9)$$
$$\mathbf{c}_{5,6,7,8} = (\pm 1, \pm 1) \quad (\text{Direcciones diagonales, peso } w_i = 1/36)$$
$$w_0 = 4/9$$

La velocidad del sonido en la red reticular es $c_s = 1/\sqrt{3}$, por lo que $c_s^2 = 1/3$.

La ecuación cinética con la aproximación de relajación de un solo tiempo de Bhatnagar-Gross-Krook (BGK) se expresa como:

$$f_i(\mathbf{x} + \mathbf{c}_i \Delta t, t + \Delta t) - f_i(\mathbf{x}, t) = -\frac{1}{\tau} \left[ f_i(\mathbf{x}, t) - f_i^{(eq)}(\mathbf{x}, t) \right]$$

donde la función de distribución de equilibrio local $f_i^{(eq)}$ corresponde al desarrollo de segundo orden de Maxwell-Boltzmann truncado para flujo incompresible:

$$f_i^{(eq)}(\rho, \mathbf{u}) = w_i \rho \left[ 1 + \frac{\mathbf{c}_i \cdot \mathbf{u}}{c_s^2} + \frac{(\mathbf{c}_i \cdot \mathbf{u})^2}{2 c_s^4} - \frac{|\mathbf{u}|^2}{2 c_s^2} \right]$$

Sustituyendo $c_s^2 = 1/3$:

$$f_i^{(eq)}(\rho, \mathbf{u}) = w_i \rho \left[ 1 + 3(\mathbf{c}_i \cdot \mathbf{u}) + \frac{9}{2}(\mathbf{c}_i \cdot \mathbf{u})^2 - \frac{3}{2}|\mathbf{u}|^2 \right]$$

---

### 3. Recuperación de Navier-Stokes (Expansión de Chapman-Enskog)
A través de un análisis asintótico multiescala (expansión de Chapman-Enskog en potencias del número de Knudsen $Kn \ll 1$):

$$f_i = f_i^{(0)} + \epsilon f_i^{(1)} + \epsilon^2 f_i^{(2)} + \dots$$
$$\frac{\partial}{\partial t} = \epsilon \frac{\partial}{\partial t_1} + \epsilon^2 \frac{\partial}{\partial t_2}, \quad \nabla = \epsilon \nabla_1$$

Se demuestra rigurosamente que las ecuaciones macroscópicas recuperan exactamente la ecuación de Navier-Stokes incompresible con un error cuadrático en el número de Mach $\mathcal{O}(Ma^2)$, con una viscosidad cinemática reticular dada por:

$$\nu = c_s^2 \left(\tau - \frac{1}{2}\right) \Delta t = \frac{2\tau - 1}{6} \implies \tau = 3\nu + 0.5$$

Para garantizar estabilidad numérica y positividad en la disipación entrópica, se debe verificar estrictamente que:
$$\tau > 0.5 \quad \text{y} \quad Ma = \frac{U_\infty}{c_s} < 0.15 \ll 0.3$$

---

### 4. Telemetría de Fuerzas: Método de Intercambio de Momento (MEM)
Para calcular las fuerzas dinámicas de sustentación ($F_L$) y arrastre ($F_D$) que el fluido ejerce sobre cuerpos sumergidos arbitrarios sin necesidad de integrar gradientes de presión espurios en paredes escalonadas, se implementa el **Método de Intercambio de Momento** (*Momentum Exchange Method*, MEM).

Por cada enlace que cruza la interfaz sólido-fluido desde un nodo de fluido $\mathbf{x}_f$ hacia un nodo sólido $\mathbf{x}_s$ en la dirección $\mathbf{c}_i$:

$$\mathbf{F}_{MEM}(t) = \sum_{\text{enlaces}} \left[ \mathbf{c}_i f_i^*(\mathbf{x}_f, t) - \mathbf{c}_{\bar{i}} f_{\bar{i}}(\mathbf{x}_f, t + \Delta t) \right]$$

Bajo la condición de rebote de pared no deslizante (*bounce-back* estándar) $f_{\bar{i}}(\mathbf{x}_f, t + \Delta t) = f_i^*(\mathbf{x}_f, t)$ y sabiendo que $\mathbf{c}_{\bar{i}} = -\mathbf{c}_i$:

$$\mathbf{F}_{MEM}(t) = \sum_{\text{enlaces}} 2\,\mathbf{c}_i f_i^*(\mathbf{x}_f, t)$$

Las componentes de fuerza y coeficientes adimensionales son:
$$F_D = \mathbf{F}_{MEM} \cdot \hat{\mathbf{i}}, \quad F_L = \mathbf{F}_{MEM} \cdot \hat{\mathbf{j}}$$
$$C_D(t) = \frac{F_D(t)}{\frac{1}{2}\rho_0 U_\infty^2 D}, \quad C_L(t) = \frac{F_L(t)}{\frac{1}{2}\rho_0 U_\infty^2 D}$$

---

### 5. Validación Adimensional y Fenomenología de Desprendimiento
Para el flujo sobre un cilindro circular en el régimen laminar $47 < Re < 188$, el flujo experimenta una **Bifurcación de Hopf supercrítica**, rompiendo la simetría estacionaria y dando origen a la **Calle de Vórtices de von Kármán**.

A $Re = 150$:
- La frecuencia de desprendimiento de vórtices $f_s$ está parametrizada por el **Número de Strouhal**:
  $$St = \frac{f_s D}{U_\infty} \approx 0.18 - 0.19$$
- El coeficiente de arrastre oscila al doble de la frecuencia de sustentación ($f_{C_D} = 2 f_{C_L}$), originando el ciclo límite cerrado en el espacio de fase $(C_D, C_L)$ monitoreado en tiempo real en el HUD de Continuum Lab.
