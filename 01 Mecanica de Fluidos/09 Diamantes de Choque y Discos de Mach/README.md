# 09 Diamantes de Choque y Discos de Mach en Jets Hipersónicos

<div align="center">

![Shock Diamonds Hero](../../RENDERS/25%20Diamantes%20de%20Choque%20y%20Discos%20de%20Mach%20Aerodinamicos/extra/capturas/shock_diamonds_hero_es.png)

[![Discipline: Fluid Mechanics](https://img.shields.io/badge/Discipline-Compressible%20Aerodynamics-00F0FF.svg?style=for-the-badge)](../../01%20Mecanica%20de%20Fluidos)
[![Physics: Method of Characteristics & Rankine--Hugoniot](https://img.shields.io/badge/Physics-Mach%20Reflection%20Singularity-FF007F.svg?style=for-the-badge)](https://en.wikipedia.org/wiki/Shock_diamond)
[![Thermodynamics: Radical Reignition](https://img.shields.io/badge/Incandescence-Reignition%20(T%20%3E%202%2C850%20K)-FFE600.svg?style=for-the-badge)](https://en.wikipedia.org/wiki/Mach_disk)
[![Status: Verified](https://img.shields.io/badge/Tests-10%2F10%20Passing-brightgreen.svg?style=for-the-badge)](tests/test_shock_diamonds.py)

</div>

---

## 🔬 Fundamentación Física y Aerodinámica Teórica

Los **diamantes de choque** (*shock diamonds* o *Mach diamonds*) y los **discos de Mach** son patrones periódicos de ondas estacionarias que se forman en el escape supersónico e hipersónico de motores cohete (SpaceX Raptor, Falcon 9 Merlin, SSME del Transbordador Espacial) y turborreactores con postcombustión (SR-71 Blackbird). 

Este fenómeno es la manifestación visible del intento del fluido de reconciliar la diferencia entre la presión estática de salida de la tobera $p_e$ y la presión atmosférica del entorno $p_a$.

---

### 1. Dinámica de Gases Isentrópica y Expansión de Prandtl-Meyer

Para una tobera convergente-divergente de Laval alimentada por una cámara de combustión a presión de estancamiento $p_0$ y temperatura $T_0$, el flujo se acelera a la velocidad del sonido en la garganta ($M=1$) y se expande supersónicamente en la campana divergente hasta alcanzar el número de Mach de salida $M_e$:

$$\frac{p_0}{p_e} = \left( 1 + \frac{\gamma - 1}{2} M_e^2 \right)^{\frac{\gamma}{\gamma - 1}}, \qquad \frac{T_0}{T_e} = 1 + \frac{\gamma - 1}{2} M_e^2$$

#### Chorro Subexpandido ($p_e > p_a$)
Cuando la presión de salida supera la presión ambiental, el gas no puede continuar confinado por la pared sólida y se expande bruscamente hacia la atmósfera a través de un **abanico de expansión de Prandtl-Meyer** centrado en el labio de la tobera.

La función de Prandtl-Meyer $\nu(M)$ gobierna el giro del flujo:

$$\nu(M) = \sqrt{\frac{\gamma + 1}{\gamma - 1}} \arctan\left( \sqrt{\frac{\gamma - 1}{\gamma + 1}(M^2 - 1)} \right) - \arctan\left( \sqrt{M^2 - 1} \right)$$

El ángulo de giro hacia afuera es $\theta = \nu(M_j) - \nu(M_e)$, donde $M_j$ es el número de Mach en la frontera del chorro donde la presión estática cae hasta la presión ambiental $p_a$.

---

### 2. Reflexión en la Frontera Libre y Formación de Ondas de Choque Oblicuas

En la frontera de contacto entre el chorro supersónico y el aire ambiental en reposo, la condición de contorno exige continuidad de presión:

$$p_{borde} = p_a = \text{constante}$$

Debido a esta condición de contorno isobárica:
1. Las ondas de expansión incidentes que chocan contra la frontera libre **se reflejan como ondas de compresión**.
2. A medida que viajan hacia el eje de simetría del chorro, las ondas de compresión se coalescen formando una **onda de choque oblicua** inclinada con ángulo $\beta$.
3. La relación $\theta$-$\beta$-$M$ gobierna la inclinación del choque:

$$\tan\theta = 2 \cot\beta \, \frac{M_1^2 \sin^2\beta - 1}{M_1^2 (\gamma + \cos 2\beta) + 2}$$

---

### 3. La Bifurcación de von Neumann y el Disco de Mach (Reflexión Regular vs Mach)

Cuando las ondas de choque oblicuas convergen hacia el eje de simetría:
- Si el ángulo de inclinación $\beta$ permite que la deflexión requerida sea menor al ángulo máximo de desprendimiento $\theta_{max}$, se produce una **reflexión regular**: los choques se cruzan limpiamente en un punto nodal formando el diamante agudo.
- Sin embargo, a altas razones de presión ($NPR = p_0 / p_a \gg 1$), la reflexión regular es matemáticamente imposible (criterio de von Neumann). Para reconciliar el flujo, la naturaleza inserta una onda de choque normal en el eje: **El Disco de Mach**.

A través del disco de Mach, aplican las ecuaciones de salto de **Rankine-Hugoniot**:

$$M_2 = \sqrt{\frac{(\gamma - 1)M_1^2 + 2}{2\gamma M_1^2 - (\gamma - 1)}} < 1.0 \quad \text{(Flujo bruscamente subsónico)}$$

$$\frac{p_2}{p_1} = 1 + \frac{2\gamma}{\gamma + 1}(M_1^2 - 1)$$

$$\frac{T_2}{T_1} = \frac{p_2}{p_1} \cdot \left[ \frac{(\gamma - 1)M_1^2 + 2}{(\gamma + 1)M_1^2} \right]$$

#### Re-ignición Incandescente de Radicales
Debido a la desaceleración abrupta de Mach 2.45 a subsónico, la energía cinética se reconvierte en entalpía estática. La temperatura en el núcleo del disco de Mach se dispara por encima de **$2,850\text{ K}$**, provocando la combustión espontánea de radicales de combustible no quemados ($\text{CO} + \text{OH} \to \text{CO}_2 + \text{H}$), creando el nodo blanco incandescente visible como una esfera de fuego estelar.

---

### 4. Longitud de Onda Periódica de Prandtl-Pack

El flujo subsónico tras el disco de Mach vuelve a acelerarse a través de la tobera virtual formada por el flujo anular supersónico circundante, repitiendo el ciclo de expansión y compresión en una cadena cuasi-periódica. La longitud de celda de diamante viene dada por la fórmula analítica de Prandtl-Pack:

$$L_d \approx 1.306 \cdot d_e \sqrt{M_e^2 - 1} \cdot \sqrt{\frac{p_e}{p_a}}$$

---

## 📊 Estructura de Entregables del Módulo

```
01 Mecanica de Fluidos/09 Diamantes de Choque y Discos de Mach/
├── main.py                                      # Master CLI & Orchestrator
├── README.md                                    # Documentación técnica completa
├── src/
│   ├── physics/
│   │   ├── shock_diamonds_sim.py                # Modelo compresible (Euler/Rankine-Hugoniot)
│   │   └── export_excel_benchmark.py            # Generador dinámico .xlsx con openpyxl
│   ├── audio/
│   │   └── shock_diamonds_audio.py              # Síntesis procedural estéreo 44.1 kHz
│   └── visualization/
│       ├── render_shock_diamonds_video.py       # Renderer 9:16 UHD 60 FPS (ES & EN)
│       └── render_shock_diamonds_poster.py      # Póster científico 16:9
└── tests/
    └── test_shock_diamonds.py                   # 10 pruebas unitarias y físicas (100% Passing)
```
