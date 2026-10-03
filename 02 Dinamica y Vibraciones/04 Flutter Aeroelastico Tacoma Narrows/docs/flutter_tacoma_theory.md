# Aeroelasticidad Avanzada: Aleteo Torsional y Colapso del Puente de Tacoma Narrows

**División**: 02 Dinámica y Vibraciones  
**Proyecto**: 04 Flutter Aeroelástico Tacoma Narrows  
**Autor**: Continuum Lab / Roberto Andrés Pepe Sánchez  
**Resolución Visual**: Ultra-HD 1080x1920 (9:16 Vertical, 60 FPS)  

---

## 1. Introducción Histórica y Desmitificación Física

El colapso del Puente de Tacoma Narrows el 7 de noviembre de 1940 representa uno de los hitos más trascendentales en la historia de la ingeniería estructural y la dinámica de fluidos. Durante décadas, manuales introductorios de física atribuyeron erróneamente la catástrofe a una "resonancia mecánica forzada por el desprendimiento periódico de vórtices de von Kármán".

Sin embargo, las investigaciones pioneras de **Robert H. Scanlan y J.J. Tomko (1971)**, consolidadas por **K. Yusuf Billah y Robert H. Scanlan (1991)** en el célebre artículo *"Resonance, Tacoma Narrows bridge failure, and undergraduate physics textbooks"* (American Journal of Physics), demostraron de manera concluyente que el colapso no fue una resonancia pasiva forzada, sino un **fenómeno de autoexcitación aeroelástica: Aleteo Torsional (Torsional Flutter)** con acoplamiento no lineal de desprendimiento vorticoso en régimen de bloqueo (*lock-in*).

---

## 2. Formulación Matemática de 2 Grados de Libertad (2-DOF)

El tablero del puente se modela mediante una sección transversal rígida representativa (viga cajón en H con vigas de alma llena de $D = 2.44\text{ m}$ y semiancho $b = 6.0\text{ m}$), con dos grados de libertad acoplados:
1. **Desplazamiento vertical de flexión (plunging)**: $h(t)$ [m].
2. **Ángulo de torsión o cabeceo (pitching)**: $\alpha(t)$ [rad].

### 2.1 Ecuaciones Diferenciales de Movimiento

$$\begin{aligned}
m \ddot{h}(t) + c_h \dot{h}(t) + k_h h(t) + F_{\text{cables}}(t) &= L_{\text{aero}}(t) \\
I_\alpha \ddot{\alpha}(t) + c_\alpha \dot{\alpha}(t) + k_\alpha \alpha(t) - M_{\text{cables}}(t) &= M_{\text{aero}}(t)
\end{aligned}$$

Donde:
- $m$: Masa por unidad de longitud ($m = 8600.0\text{ kg/m}$).
- $I_\alpha$: Momento polar de inercia másico por unidad de longitud ($I_\alpha = 1.517 \times 10^5\text{ kg}\cdot\text{m}^2/\text{m}$).
- $k_h = m \omega_h^2$: Rigidez modal a flexión vertical ($\omega_h = 2\pi f_h$, con $f_h = 0.20\text{ Hz}$).
- $k_\alpha = I_\alpha \omega_\alpha^2$: Rigidez modal torsional ($\omega_\alpha = 2\pi f_\alpha$, con $f_\alpha = 0.20\text{ Hz}$).
- $c_h = 2 \zeta_{h, \text{mech}} m \omega_h$: Coeficiente de amortiguamiento estructural vertical ($\zeta_{h, \text{mech}} = 0.010$).
- $c_\alpha = 2 \zeta_{\alpha, \text{mech}} I_\alpha \omega_\alpha$: Coeficiente de amortiguamiento estructural torsional ($\zeta_{\alpha, \text{mech}} = 0.008$).

---

## 3. Fuerzas No Estacionarias de Scanlan y Amortiguamiento Negativo

En aerodinámica de puentes, las fuerzas no estacionarias inducidas por el viento se expresan mediante las **derivadas de Scanlan** en función de la velocidad reducida $U^*$ y la frecuencia reducida $K$:

$$U^* = \frac{U}{f_\alpha b}, \quad K = \frac{\omega b}{U} = \frac{2\pi}{U^*}$$

$$\begin{aligned}
L_{\text{aero}} &= \frac{1}{2}\rho U^2 (2b) \left[ K H_1^*(U^*) \frac{\dot{h}}{U} + K H_2^*(U^*) \frac{b\dot{\alpha}}{U} + K^2 H_3^*(U^*) \alpha + K^2 H_4^*(U^*) \frac{h}{b} \right] + L_{\text{vortex}} \\
M_{\text{aero}} &= \frac{1}{2}\rho U^2 (2b^2) \left[ K A_1^*(U^*) \frac{\dot{h}}{U} + K A_2^*(U^*) \frac{b\dot{\alpha}}{U} + K^2 A_3^*(U^*) \alpha + K^2 A_4^*(U^*) \frac{h}{b} \right] + M_{\text{vortex}}
\end{aligned}$$

### 3.1 La Derivada Crítica $A_2^*(U^*)$ y el Amortiguamiento Negativo

El término dominante en la estabilidad torsional es $A_2^*(U^*)$, que multiplica a la velocidad angular $\dot{\alpha}$:

$$M_{\text{damping}} = \frac{1}{2}\rho U^2 (2b^2) \left[ K A_2^*(U^*) \frac{b\dot{\alpha}}{U} \right] = \rho b^4 \omega A_2^*(U^*) \dot{\alpha}$$

El amortiguamiento torsional total del sistema es:

$$c_{\alpha, \text{total}} = c_\alpha - \rho b^4 \omega A_2^*(U^*)$$

En términos de fracción de amortiguamiento crítico:

$$\zeta_{\text{total}} = \zeta_{\alpha, \text{mech}} - \frac{\rho b^4}{2 I_\alpha} A_2^*(U^*)$$

- **Para perfiles aerodinámicos esbeltos**: $A_2^* < 0$ para todo $U^*$, lo que añade amortiguamiento disipativo positivo ($\zeta_{\text{total}} > 0$).
- **Para la viga en H de Tacoma (perfil romo con placas laterales macizas de 8 pies)**:
  - Cuando $U < U_{\text{crit}} \approx 40\text{ km/h}$ ($U^* < U^*_{\text{crit}} \approx 6.8$): $A_2^* < 0$ (amortiguamiento positivo, oscilaciones estables).
  - Cuando $U > U_{\text{crit}}$ ($U = 68\text{ km/h}$, $U^* \approx 15.7$): **$A_2^*(U^*) > 0$**.
  - El amortiguamiento aerodinámico se vuelve **estrictamente negativo**:
    $$\zeta_{\text{aero}} = -0.042 \implies \zeta_{\text{total}} = 0.008 - 0.042 = -0.034 < 0$$

Al ser $\zeta_{\text{total}} < 0$, el flujo de aire deja de disipar energía y se convierte en un **inyector activo de energía mecánica** que bombea trabajo al modo torsional en cada semiciclo de vibración.

---

## 4. Desprendimiento Vorticoso No Lineal, Fenómeno de Lock-In y Trabajo Eólico

A medida que el viento alcanza $U = 68\text{ km/h}$, el flujo que incide sobre las aristas afiladas de la viga frontal en H sufre un desprendimiento masivo de capa límite.

### 4.1 Resonancia en Sincronismo (Lock-In)
La frecuencia de desprendimiento de vórtices se desengancha de la ley clásica de Strouhal ($f_s = St \cdot U / D$) y queda **atrapada (lock-in)** por la frecuencia natural torsional de la estructura:

$$f_{\text{vortex}} = f_\alpha = 0.20\text{ Hz}$$

### 4.2 Desfase de 90° e Inyección Neta de Energía
El momento aerodinámico resultante adquiere un desfase de $\approx 90^\circ$ respecto a la posición angular $\alpha(t)$, sincronizándose exactamente con la velocidad angular $\dot{\alpha}(t)$:

$$M(t) \propto \dot{\alpha}(t)$$

El trabajo neto transferido por el viento al puente por ciclo cerrado es estrictamente positivo:

$$\Delta W = \oint M(t) \, d\alpha = \int_0^T M(t) \dot{\alpha}(t) \, dt > 0$$

Este trabajo eólico acumulado acelera exponencialmente la amplitud torsional hasta superar los límites mecánicos del acero estructural.

---

## 5. No Linealidades Estructurales: Asimetría de Cables y Cedencia Plástica

Los tirantes verticales de suspensión (cables de acero de alta resistencia) presentan una no linealidad geométrica fundamental: **tienen rigidez nula a compresión** (se destensan y forman catenarias holgadas si el desplazamiento relativo es negativo):

$$\begin{aligned}
\Delta y_{\text{izq}} &= -h - b \sin\alpha \\
\Delta y_{\text{der}} &= -h + b \sin\alpha \\
T_{\text{izq}} &= \max(0, T_0 + k_{\text{cable}} \Delta y_{\text{izq}}) \\
T_{\text{der}} &= \max(0, T_0 + k_{\text{cable}} \Delta y_{\text{der}})
\end{aligned}$$

Donde:
- $T_0 = 42.2\text{ kN/m}$: Tensión nominal estática.
- $k_{\text{cable}} = 65.0\text{ kN/m}^2$: Rigidez axial del conjunto de péndolas.
- $T_{\text{yield}} = 95.0\text{ kN/m}$: Límite elástico de fluencia o cedencia plástica.

Cuando $\alpha$ supera $\approx 22^\circ$:
- El cable del lado elevado entra en **destensado total ($T = 0$)**.
- El cable del lado descendente soporta toda la carga más el impacto inercial dinámico, superando $T_{\text{yield}}$, entrando en **cedencia plástica irreversible** y provocando la rotura en cadena observada en las grabaciones originales de 1940.

---

## 6. Secuencia Cinemática de los 15 Segundos de Simulación

| Fase | Intervalo Temporal | Velocidad Viento $U$ | Derivada $A_2^*$ | Amortiguamiento $\zeta_{\text{total}}$ | Comportamiento Dinámico |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Fase 1: Flexión Estable** | $0.0\text{s} - 4.0\text{s}$ | $25\text{ km/h}$ | $-0.015$ | $+0.010$ (Estable) | Oscilación vertical pura ($h \approx \pm 0.25\text{ m}$), torsión despreciable ($\alpha \le 0.5^\circ$). |
| **Fase 2: Bifurcación Flutter** | $4.0\text{s} - 8.5\text{s}$ | $25 \to 68\text{ km/h}$ | $-0.015 \to +0.078$ | $+0.010 \to -0.034$ | Bifurcación de Hopf: acoplamiento flexión-torsión, crecimiento exponencial. |
| **Fase 3: Colapso Resonante** | $8.5\text{s} - 15.0\text{s}$ | $68\text{ km/h}$ | $+0.078$ | $-0.034$ (Bomba neta) | Ciclo límite violento no lineal ($\alpha = \pm 38.4^\circ$), cedencia plástica y rotura de tirantes. |

---

## 7. Implementación y Verificación Computacional

El sistema está desacoplado numéricamente mediante un integrador de paso adaptativo Runge-Kutta de orden 4/5 (`scipy.integrate.solve_ivp` con tolerancias estrictas $\text{rtol}=10^{-7}$, $\text{atol}=10^{-9}$), garantizando estabilidad incondicional y 60 FPS exactos sin sobrecarga en la GPU/CPU durante el renderizado vectorial en Manim Community.
