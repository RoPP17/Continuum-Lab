# 08 Colapso de Cavitación y Sonoluminiscencia

<div align="center">

![Cavitation Sonoluminescence Hero](../../RENDERS/24%20Colapso%20de%20Cavitacion%20y%20Sonoluminiscencia/extra/capturas/cavitation_hero_es.png)

[![Discipline: Fluid Mechanics](https://img.shields.io/badge/Discipline-Fluid%20Mechanics-00F0FF.svg?style=for-the-badge)](../../01%20Mecanica%20de%20Fluidos)
[![Physics: Rayleigh--Plesset & Keller--Miksis](https://img.shields.io/badge/Physics-Keller--Miksis%20Singularity-FF007F.svg?style=for-the-badge)](https://en.wikipedia.org/wiki/Rayleigh%E2%80%93Plesset_equation)
[![Thermodynamics: Sonoluminescence](https://img.shields.io/badge/Plasma-Sonoluminescence%20(T%20%3E%2018%2C000%20K)-FFE600.svg?style=for-the-badge)](https://en.wikipedia.org/wiki/Sonoluminescence)
[![Status: Verified](https://img.shields.io/badge/Tests-9%2F9%20Passing-brightgreen.svg?style=for-the-badge)](tests/test_cavitation.py)

</div>

---

## 🔬 Fundamentación Física y Teórica

El colapso de una burbuja de cavitación es uno de los fenómenos más energéticos y concentrados de la física de medios continuos. Durante la fase inercial final, la energía acústica distribuida en varios centímetros cúbicos de líquido se concentra en un volumen submicrométrico, alcanzando velocidades de pared transónicas, temperaturas más elevadas que la fotosfera solar ($T > 18,000\text{ K}$) y presiones de choque del orden de gigapascales ($> 15,000\text{ bar}$).

### 1. Ecuaciones Gobernantes de la Dinámica Radial

#### Ecuación de Rayleigh-Plesset (Líquido Incompresible)
Para una burbuja esférica en un fluido newtoniano incompresible:

$$R \ddot{R} + \frac{3}{2}\dot{R}^2 = \frac{1}{\rho_L} \left[ p_B(t) - p_\infty(t) - \frac{2\sigma}{R} - \frac{4\mu_L \dot{R}}{R} \right]$$

Donde la presión interior de la burbuja es $p_B(t) = p_v + p_g(t)$, combinando la presión de vapor saturado $p_v$ y la presión del gas no condensable $p_g(t)$.

#### Corrección de Keller-Miksis (Compresibilidad Acústica a Mach Alto)
Cuando la pared de la burbuja colapsa a velocidades comparables a la velocidad del sonido en el líquido ($c_s \approx 1482\text{ m/s}$), la radiación acústica disipa una fracción masiva de la energía cinética. La ecuación de **Keller-Miksis** modela esta radiación con orden $O(M)$:

$$\left(1 - \frac{\dot{R}}{c_s}\right) R \ddot{R} + \frac{3}{2}\left(1 - \frac{\dot{R}}{3 c_s}\right) \dot{R}^2 = \frac{1}{\rho_L} \left(1 + \frac{\dot{R}}{c_s}\right) [p_L - p_\infty(t)] + \frac{R}{\rho_L c_s}\frac{d p_L}{dt}$$

con la presión en la interfaz líquida:

$$p_L(R, \dot{R}) = p_g(R) + p_v - \frac{2\sigma}{R} - \frac{4\mu_L \dot{R}}{R}$$

---

### 2. Termodinámica Extrema y Sonoluminiscencia ("Star in a Jar")

Bajo compresión adiabática con gas monoatómico o diatómico sujeto al radio de exclusión molecular de van der Waals ($h_{vdw} \approx 0.05 R_0$):

$$p_g(R) = p_{g0} \left( \frac{R_0^3 - h_{vdw}^3}{R^3 - h_{vdw}^3} \right)^\gamma$$

$$T(R) = T_0 \left( \frac{R_0^3 - h_{vdw}^3}{R^3 - h_{vdw}^3} \right)^{\gamma - 1}$$

- Para un colapso con relación de compresión $R_0 / R_{min} \approx 20$, la relación de volumen es $V_0 / V_{min} \approx 8,000$.
- La temperatura interior alcanza $T_{max} \approx 18,500\text{ K}$, superando por más de tres veces la superficie del Sol ($5,778\text{ K}$).
- A estas temperaturas, los átomos de gas se ionizan parcialmente produciendo radiación de **Bremsstrahlung térmico** y recombinación electrónica, emitiendo un pulso ultracorto de luz visible y ultravioleta conocido como **Sonoluminiscencia** ($\Delta t \sim 100 - 300\text{ ps}$).

---

### 3. Ondas de Choque Esféricas y Micro-Jet Destructor

1. **Onda de Choque Acústica de Kirkwood-Bethe**:
   En el rebote inercial, se radia una onda de choque esférica cuya presión decae en campo lejano como:
   $$p_{shock}(r, t) \approx \rho_L \frac{R}{r} \left( 2\dot{R}^2 + R\ddot{R} \right)$$
   alcanzando presiones de frente de onda superiores a $16,000\text{ bar}$.

2. **Formación de Micro-Jet Asimétrico**:
   Cerca de un contorno rígido o gradiente de presión transversal, la simetría esférica se rompe. El polo distal de la burbuja colapsa hacia adentro formando una aguja líquida supersónica ($v_{jet} \approx 1,050\text{ m/s}$) que perfora la burbuja transformándola en un anillo vorticial toroidal. La presión de impacto (*water hammer*) sobre superficies sólidas:
   $$p_{wh} = \rho_L c_s v_{jet} \approx (1000)(1482)(1050) \approx 1.55\text{ GPa} \approx 15,500\text{ bar}$$
   es la causa física del picado por cavitación en hélices navales y turbinas hidráulicas, así como el mecanismo de choque del camarón pistola (*Alpheus heterochaelis*).

---

## 📊 Estructura de Entregables del Módulo

```
01 Mecanica de Fluidos/08 Colapso de Cavitacion y Sonoluminiscencia/
├── main.py                                      # Master CLI & Orchestrator
├── README.md                                    # Documentación técnica completa
├── src/
│   ├── physics/
│   │   ├── cavitation_sim.py                    # Ecuaciones Keller-Miksis & Termodinámica
│   │   └── export_excel_benchmark.py            # Generador dinámico .xlsx
│   ├── audio/
│   │   └── cavitation_audio.py                  # Síntesis procedural estéreo 44.1 kHz
│   └── visualization/
│       ├── render_cavitation_video.py           # Renderer 9:16 UHD 60 FPS (ES & EN)
│       └── render_cavitation_poster.py          # Póster científico 16:9
└── tests/
    └── test_cavitation.py                       # 9 pruebas unitarias y físicas (100% Passing)
```
