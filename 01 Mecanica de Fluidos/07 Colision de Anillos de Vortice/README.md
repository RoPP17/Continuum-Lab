# Continuum Lab — 01 Mecánica de Fluidos: 07 Colisión de Anillos de Vórtice

Simulación computacional de alta fidelidad y visualización cinematográfica 9:16 (1080x1920 @ 60 FPS) de la **Colisión Frontal Coaxial de Anillos de Vórtice, Inestabilidad Azimutal de Widnall ($m = 12$) y Cascada de Reconexión Topológica**.

---

## 🌊 1. Fundamentos Físicos y Formulación Matemática

Basado en el currículo de Mecánica de Fluidos Intermedia y Avanzada (**Purdue University ME 50900**, Prof. Ivan C. Christov):

### 1.1 Velocidad Auto-Inducida (Kelvin-Hicks-Lamb)
Un filamento anular aislado de radio $R(t)$, circulación $\Gamma_0$ y radio de núcleo $a(t)$ auto-propulsa axialmente con velocidad:
$$U_{self}(R, a) = \frac{\Gamma_0}{4\pi R} \left[ \ln\left(\frac{8R}{a}\right) - \frac{1}{4} + \beta \right]$$
donde $\beta = 0.058$ modela un núcleo con distribución gaussiana de vorticidad (núcleo de Lamb-Oseen).

### 1.2 Inducción Mutua Coaxial (Ley de Biot-Savart)
La interacción entre los dos anillos opuestos a distancia $z_{sep} = 2z(t)$ induce una velocidad radial de estiramiento y una desaceleración axial calculadas analíticamente mediante integrales elípticas completas $K(m)$ y $E(m)$:
$$m = \frac{4 R^2}{4 R^2 + z_{sep}^2 + 2.5 a^2}$$
$$u_r = \frac{\Gamma_0}{2\pi \sqrt{4R^2 + z_{sep}^2 + 2.5a^2}} \frac{z_{sep}}{R} \left[ -K(m) + \frac{2 - m}{2(1 - m)} E(m) \right]$$

### 1.3 Conservación de Volumen de Núcleo y Estiramiento de Vorticidad
Por incompresibilidad y el teorema de circulación de Kelvin:
$$V_{core} = 2\pi^2 R(t) a(t)^2 = \text{constante} \implies a(t) = a_0 \sqrt{\frac{R_0}{R(t)}}$$
La vorticidad máxima en el centro del núcleo se amplifica conforme el anillo se ensancha radialmente:
$$\omega_{max}(t) = \frac{\Gamma_0}{\pi a(t)^2} \propto R(t)$$

### 1.4 Inestabilidad de Widnall y Reconexión Topológica
El campo de deformación tangencial $\dot{\varepsilon} = \frac{1}{R}\frac{dR}{dt}$ desencadena la inestabilidad azimutal de Widnall con número de onda $m = 12$:
$$\tilde{r}(\theta, t) = R(t) + A_w(t) \cos(12\theta)$$
Alcanzado el umbral $A_w \sim a$, los núcleos se tocan en el plano $z = 0$, sufriendo aniquilación viscosa de vorticidad y reconectándose topológicamente en **12 anillos secundarios** que auto-propulsan radialmente hacia el exterior.

---

## 🚀 2. Ejecución del Pipeline

```bash
# Ejecutar suite completa (Benchmark Excel, Póster 16:9, Audio 44.1 kHz, Videos 9:16 ES y EN):
python main.py --all

# Solo renderizar video en español:
python main.py --video --lang ES

# Solo generar el libro dinámico Excel:
python main.py --benchmark
```

---

## 📊 3. Entregables Generados

* **Videos Verticales 9:16:** `RENDERS/23 Colision de Anillos de Vortice y Cascada de Reconexion/videos/`
* **Miniaturas y Póster Científico:** `RENDERS/23 Colision de Anillos de Vortice y Cascada de Reconexion/extra/capturas/`
* **Audio Cinematográfico:** `RENDERS/23 Colision de Anillos de Vortice y Cascada de Reconexion/extra/audio/`
* **Libro de Benchmarks:** `RENDERS/23 Colision de Anillos de Vortice y Cascada de Reconexion/Vortex_Rings_Collision_Benchmark.xlsx`
