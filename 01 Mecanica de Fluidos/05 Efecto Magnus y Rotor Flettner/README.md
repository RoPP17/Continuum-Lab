# 05 Efecto Magnus y Rotor Flettner Aerodinámico

<div align="center">

![Efecto Magnus y Rotor Flettner Hero Cover](../../RENDERS/20%20Efecto%20Magnus%20y%20Rotor%20Flettner%20Aerodinamico/extra/capturas/magnus_flettner_hero.png)

[![Discipline: Fluid Mechanics](https://img.shields.io/badge/Discipline-Fluid%20Mechanics-00F0FF.svg?style=for-the-badge)](../../01%20Mecanica%20de%20Fluidos)
[![Physics: Kutta-Joukowski](https://img.shields.io/badge/Physics-Kutta--Joukowski%20Theorem-FF007F.svg?style=for-the-badge)](https://en.wikipedia.org/wiki/Kutta%E2%80%93Joukowski_theorem)
[![Application: Green Shipping](https://img.shields.io/badge/Application-Flettner%20Rotor%20Sails-00FF88.svg?style=for-the-badge)](https://en.wikipedia.org/wiki/Flettner_rotor)
[![Status: Verified](https://img.shields.io/badge/Tests-6%2F6%20Passing-brightgreen.svg?style=for-the-badge)](tests/test_magnus.py)

</div>

---

## 🔬 Fundamentación Física y Teórica

El **Efecto Magnus** es el fenómeno por el cual un cilindro o esfera que gira dentro de una corriente fluida experimenta una fuerza de sustentación perpendicular a la dirección del flujo incidente y al eje de rotación.

### 1. Potencial Complejo con Circulación
Bajo la hipótesis de flujo potencial incomprensible e irrotacional en el plano complejo $z = x + iy = r e^{i\theta}$, el potencial complejo $w(z) = \phi + i\psi$ para un cilindro de radio $R$ inmerso en una corriente uniforme $U_\infty$ con circulación horaria $\Gamma$ está dado por:

$$w(z) = U_\infty \left( z + \frac{R^2}{z} \right) - \frac{i\Gamma}{2\pi} \ln\left(\frac{z}{R}\right)$$

Separando la función de corriente $\psi(r, \theta)$:

$$\psi(r, \theta) = U_\infty \left( r - \frac{R^2}{r} \right) \sin\theta - \frac{\Gamma}{2\pi} \ln\left(\frac{r}{R}\right)$$

### 2. Campo de Velocidades y Presión de Bernoulli
Las componentes de velocidad polar son:

$$u_r(r, \theta) = \frac{1}{r}\frac{\partial\psi}{\partial\theta} = U_\infty \left( 1 - \frac{R^2}{r^2} \right) \cos\theta$$

$$u_\theta(r, \theta) = -\frac{\partial\psi}{\partial r} = -U_\infty \left( 1 + \frac{R^2}{r^2} \right) \sin\theta - \frac{\Gamma}{2\pi r}$$

En la superficie del cilindro ($r = R$):
- Impermeabilidad exacta: $u_r(R, \theta) = 0$.
- Velocidad tangencial: $u_\theta(R, \theta) = -2 U_\infty \sin\theta - \frac{\Gamma}{2\pi R} = U_\infty (-2\sin\theta - \alpha)$, donde $\alpha = \frac{\omega R}{U_\infty}$ es el **Spin Ratio**.
- Coeficiente de presión superficial $C_p(\theta)$ según la ecuación de Bernoulli:
  $$C_p(\theta) = 1 - \left(\frac{u_\theta}{U_\infty}\right)^2 = 1 - (-2\sin\theta - \alpha)^2$$

### 3. Teorema de Kutta-Joukowski y Fuerza de Sustentación
Integrando la distribución de presión a lo largo del perímetro del cilindro:

$$L' = \oint -p \, \sin\theta \, R \, d\theta = \rho_\infty U_\infty \Gamma$$

$$C_{L,ideal} = \frac{L'}{\frac{1}{2}\rho_\infty U_\infty^2 (2R)} = 2\pi \alpha$$

En flujo viscoso real sobre rotores Flettner industriales, la capa límite turbulenta suprime el desprendimiento en la cara superior y satura la sustentación en $C_{L,real} \approx 9.5 - 10.0$ a $\alpha \approx 3.2 - 3.5$, lo que representa hasta **10 veces más sustentación** que un perfil alar convencional ($C_L \approx 1.2 - 1.5$).

### 4. Bifurcación Topológica de los Puntos de Estancamiento
Los puntos donde la velocidad del fluido se anula ($\mathbf{u} = \mathbf{0}$) evolucionan según el parámetro de giro $\alpha$:

1. **Subcrítico ($\alpha < 2.0$):** Dos puntos de estancamiento independientes sobre la superficie inferior del cilindro:
   $$\sin\theta_s = -\frac{\alpha}{2} \implies \theta_1 = -\arcsin(\alpha/2), \quad \theta_2 = -\pi + \arcsin(\alpha/2)$$
2. **Crítico ($\alpha = 2.0$):** Los dos puntos colisionan en el polo inferior del cilindro ($\theta = -\pi/2$).
3. **Supercrítico ($\alpha > 2.0$):** El punto de estancamiento se desprende de la superficie y flota en el fluido exterior como un **punto de silla hiperbólico aislado** a una distancia radial:
   $$r_s = R \left( \frac{\alpha + \sqrt{\alpha^2 - 4}}{2} \right) > R$$
   Dentro de la línea de corriente que pasa por este punto se forma un manto de vórtice atrapado (*vortex cloak*) que gira indefinidamente junto al cilindro.

---

## 🚢 Aplicación en Ingeniería: Rotores Flettner en Buques de Carga

En la hoja de cálculo complementaria [`Efecto_Magnus_Rotor_Flettner_Benchmark.xlsx`](../../RENDERS/20%20Efecto%20Magnus%20y%20Rotor%20Flettner%20Aerodinamico/benchmarks/Efecto_Magnus_Rotor_Flettner_Benchmark.xlsx), se modela un buque de carga ultramax de 50,000 DWT equipado con 4 rotores de $30\text{ m} \times 5\text{ m}$:
- Empuje aerodinámico neto: $1,150\text{ kN}$ a $12\text{ m/s}$ de viento aparente.
- Potencia propulsiva transferida: $8,280\text{ kW}$.
- Ahorro de combustible: hasta $18.5\text{ toneladas/día}$ de VLSFO.
- Reducción de emisiones: $> 14,000\text{ toneladas de CO}_2/\text{año}$.

---

## 🛠️ Ejecución de la Simulación y Renders

```bash
# Ejecutar pipeline completo (Audio, Excel y Videos 1080x1920 @ 60 FPS)
python main.py --all

# Ejecutar pruebas unitarias físicas
pytest tests -v
```
