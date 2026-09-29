# Continuum Lab — 02 Singularidad de Navier-Stokes en Tiempo Finito

Simulación computacional, modelo analítico y producción audiovisual de la ruptura de regularidad en tiempo finito para las ecuaciones de Navier-Stokes incompresibles 3D, basada en el descubrimiento histórico de OpenAI (2024/2025) que resuelve la **Alternativa (C)** del Problema del Milenio del Instituto Clay formulado por Charles Fefferman.

---

## 🔬 Fundamento Físico y Matemático

Para cualquier viscosidad cinemática $\nu > 0$, la solución construida parte del reposo ($\mathbf{u}(\cdot, 0) = \mathbf{0}$) y bajo una fuerza suave de soporte compacto $\mathbf{f} \in C_c^\infty(\mathbb{R}^3 \times (0,\infty); \mathbb{R}^3)$ desarrolla velocidad no acotada en tiempo finito $T_* = 1$:
$$\lim_{t \to 1^-} \|\mathbf{u}(t)\|_{L^\infty(\mathbb{R}^3)} = +\infty$$
manteniendo al mismo tiempo su energía cinética total uniformemente acotada:
$$\sup_{0 \le t < 1} \frac{1}{2} \int_{\mathbb{R}^3} |\mathbf{u}(x,t)|^2 dx < \infty$$

### Características Clave de la Solución
1. **Contracción Anisótropa:** El radio del núcleo se contrae como $\ell_r \sim \tau^{1/2}$, mientras que la altura se contrae como $\ell_z \sim \tau^{1/2 - h}$ ($0 < h < 0.01$). La razón de aspecto $\ell_r / \ell_z \sim \tau^h \to 0$ forma una **aguja singular infinitamente esbelta** sobre el eje $z$.
2. **Estructura de Tres Zonas:**
   - **Núcleo Interno ($0 \le X \le X_a$):** Vórtice espiral acelerado con fuerte succión radial hacia el eje ($u_r < 0$) y eyección axial en jets opuestos ($u_z$). El cráter de presión centripeta cae como $p(0) \sim -\tau^{-2A}$.
   - **Anillo de Cizalladura y Pulsos Ondulatorios ($X_a \le X \le X_b$):** Dos familias de pulsos de alta frecuencia ($\sigma = \pm 1$) extraen energía de la cizalladura del fondo y generan un tensor de tensiones de Reynolds $\langle \mathbf{w} \otimes \mathbf{w} \rangle$ cuyos flujos $\langle w_r w_\theta \rangle$ y $\langle w_r w_z \rangle$ cancelan de forma exacta la parte singular del residuo de momento de Navier-Stokes.
   - **Exterior de Difusión Pura ($X \ge X_b$):** Flujo azimutal laminar puro que satisface exactamente la ecuación del calor radial, permitiendo truncar suavemente el campo a soporte compacto en todo $\mathbb{R}^3$.

---

## 📂 Estructura del Módulo
```
01 Mecanica de Fluidos/02 Singularidad Navier Stokes Blowup/
├── src/
│   ├── physics/
│   │   ├── navier_stokes_blowup.py      # Motor de física analítica y coordenadas autosimilares
│   │   └── export_benchmarks.py         # Generador de modelo Excel dinámico (.xlsx)
│   ├── audio/
│   │   └── blowup_audio_synth.py        # Síntesis procedural hidro-acústica estéreo
│   └── visualization/
│       ├── render_blowup_video.py       # Renderizador Manim 60 FPS 9:16 vertical bilingüe
│       └── generate_hero_previews.py    # Generador de capturas científicas y GIF animado
├── tests/
│   └── test_navier_stokes_blowup.py     # Suite de pruebas unitarias pytest
├── docs/
│   └── navier_stokes_blowup_theory.md   # Documento teórico completo y derivaciones
├── main.py                              # Entrada CLI unificada
└── run.bat                              # Script de ejecución rápida en Windows
```

---

## 🚀 Modos de Ejecución

```bash
# 1. Resumen analítico en consola
python main.py

# 2. Ejecutar suite de pruebas unitarias
pytest tests/

# 3. Generar modelo Excel dinámico (.xlsx)
python main.py --benchmark

# 4. Generar capturas de alta definición y GIF
python main.py --visuals

# 5. Renderizar videos vectorizados TikTok 9:16 a 60 FPS con audio
python main.py --render
```

---

## 🎬 Entregables Finales en `RENDERS/`

Los entregables generados se ubican en `RENDERS/5 Singularidad Navier Stokes/`:
* **`videos/`**:
  * `Singularidad Navier Stokes ES.mp4` (Versión en Español, 1080x1920 @ 60 FPS, audio reactivo multiplexado AAC 192k)
  * `Navier Stokes Singularity EN.mp4` (Versión en Inglés, 1080x1920 @ 60 FPS, audio reactivo multiplexado AAC 192k)
* **`extra/capturas/`**:
  * `navier_stokes_blowup_hero.png` (Composición científica de alta resolución 3 paneles)
  * `reynolds_stress_cancellation.png` (Diagrama de cancelación de flujo de tensiones de Reynolds)
  * `navier_stokes_blowup_preview.gif` (GIF animado de la contracción y rotación singular)
* **`extra/benchmarks/`**:
  * `Navier_Stokes_Singularity_Benchmark.xlsx` (Cuaderno Excel dinámico con fórmulas y KPIs)
