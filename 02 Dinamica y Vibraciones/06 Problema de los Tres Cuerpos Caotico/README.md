# El Problema de los Tres Cuerpos — Dinámica Gravitatoria No Lineal, Coreografía Figura-8 & Caos Determinista

<div align="center">

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Physics](https://img.shields.io/badge/Physics-Celestial%20Mechanics%20%26%20Chaos%20Theory-0284C7.svg?style=for-the-badge)](https://github.com/RoPP17/Continuum-Lab)
[![Resolution](https://img.shields.io/badge/Resolution-1080x1920%20(9:16)-00F0FF.svg?style=for-the-badge)](RENDERS/18%20Problema%20de%20los%20Tres%20Cuerpos%20Caotico/videos/)
[![Tests](https://img.shields.io/badge/Tests-5%2F5%20Passing-brightgreen.svg?style=for-the-badge)](tests/test_three_body.py)

**Simulación gravitatoria de alta precisión del problema de los tres cuerpos: desde la coreografía periódica en figura de ocho (Moore-Chenciner) hasta la divergencia caótica, el efecto honda gravitatoria (slingshot) y la eyección estelar hiperbólica.**

</div>

---

## 🏛️ Fundamento Teórico y Mecánica Celeste

El problema gravitatorio de los tres cuerpos constituye el nacimiento formal de la **Teoría del Caos**. En 1887, el matemático Henri Poincaré demostró que para $N \ge 3$ cuerpos gravitatorios no existen integrales primeras algebraicas suficientes para resolver el sistema de forma analítica cerrada mediante cuadraturas (Teorema de No-Integrabilidad de Poincaré).

### 1. Ecuaciones de Movimiento Newtoniano
Para 3 masas puntuales $m_1, m_2, m_3$ bajo interacción gravitatoria mutua:

$$m_i \frac{d^2 \mathbf{r}_i}{dt^2} = \sum_{j \neq i}^3 G \frac{m_i m_j}{|\mathbf{r}_j - \mathbf{r}_i|^3} (\mathbf{r}_j - \mathbf{r}_i), \quad i \in \{1, 2, 3\}$$

### 2. Invariantes Integrales y Conservación Hamiltoniana
El sistema admite 10 integrales primeras clásicas:
* **Conservación del Momento Lineal (Baricentro en reposo):**
  $$\mathbf{P} = \sum_{i=1}^3 m_i \dot{\mathbf{r}}_i = \mathbf{0}, \quad \mathbf{R}_{cm} = \mathbf{0}$$
* **Conservación del Momento Angular Total:**
  $$\mathbf{L} = \sum_{i=1}^3 m_i (\mathbf{r}_i \times \dot{\mathbf{r}}_i) = \mathbf{0}$$
* **Conservación de la Energía Mecánica Total (Hamiltoniano):**
  $$E = T + V = \frac{1}{2} \sum_{i=1}^3 m_i |\dot{\mathbf{r}}_i|^2 - \sum_{1 \le i < j \le 3} \frac{G m_i m_j}{|\mathbf{r}_i - \mathbf{r}_j|} = \text{constante}$$

### 3. La Coreografía Periódica en Figura de Ocho (Moore 1993, Chenciner & Montgomery 2000)
Para 3 masas idénticas ($m_1 = m_2 = m_3 = 1.0$), existe una solución periódica exacta donde las tres estrellas persiguen la misma trayectoria plana en forma de ocho con momento angular nulo $\mathbf{L} = \mathbf{0}$. Las condiciones iniciales canónicas son:

$$\mathbf{r}_1(0) = (-x_0, -y_0), \quad \mathbf{r}_2(0) = (x_0, y_0), \quad \mathbf{r}_3(0) = (0, 0)$$
$$\mathbf{v}_1(0) = (v_x, v_y), \quad \mathbf{v}_2(0) = (v_x, v_y), \quad \mathbf{v}_3(0) = (-2v_x, -2v_y)$$

con $x_0 = 0.97000436$, $y_0 = -0.24308753$, $v_x = 0.46620531$, $v_y = 0.43236573$, y período $T \approx 6.3259\text{ s}$.

### 4. Sensibilidad Extrema a las Condiciones Iniciales y Eyección Hiperbólica
Al perturbar la posición de la Estrella C en apenas $\Delta \mathbf{r}_3 \sim 10^{-4}\text{ m}$:
1. La coreografía se desestabiliza con exponente positivo de Lyapunov $\lambda \approx 1.65\text{ s}^{-1}$.
2. Los cuerpos experimentan sucesivos encuentros cercanos de alta velocidad angular (slingshots gravitatorios).
3. La interacción a tres cuerpos transfiere energía cinética suficiente a una de las masas para que su energía específica sea positiva ($E_3 > 0$), escapando hacia el espacio interestelar como **estrella fugitiva (rogue star)**, mientras las dos restantes forman una binaria excéntrica gravitacionalmente ligada.

---

## ⚙️ Estructura del Módulo

```
02 Dinamica y Vibraciones/06 Problema de los Tres Cuerpos Caotico/
├── main.py                          # CLI maestro de ejecución y renderizado
├── README.md                        # Fundamento matemático y experimental
├── src/
│   ├── physics/
│   │   ├── three_body_sim.py        # Integrador RK4 gravitatorio y telemetría
│   │   └── export_excel_benchmark.py# Modelo dinámico de benchmark (.xlsx)
│   ├── audio/
│   │   └── three_body_audio.py      # Síntesis procedural gravitatoria 44.1 kHz
│   └── visualization/
│       └── render_three_body.py     # Renderizador UHD 9:16 (1080x1920 @ 60 FPS)
└── tests/
    └── test_three_body.py           # Suite de verificación unitaria
```

---

## 🚀 Comandos de Uso

### Ejecución del pipeline completo:
```bash
python main.py --all
```

### Ejecutar pruebas unitarias:
```bash
pytest tests/ -v
```
