# Continuum Lab - Directrices de Ingeniería, Animación y Simulación

## 1. Obligatoriedad de Simulaciones y Animaciones de Alto Nivel
En cualquier desarrollo, ejercicio, módulo o entrega dentro de **Continuum-Lab**:
- **Prohibido entregar soluciones puramente estáticas o de texto simple**. Cada fenómeno físico o mecánico analizado debe contar con su correspondiente animación o simulación visual de alto nivel.
- **Manim CE & Formato Vertical 9:16 (`tiktok-vector-video`)**:
  - Animaciones vectoriales matemáticas (1080x1920 @ 60 FPS o 1920x1080) para derivaciones teóricas, campos de velocidades, perfiles de capa límite y trayectorias cinemáticas.
- **VPython 3D (`vpython-physics`)**:
  - Simulaciones espaciales en tiempo real para dinámica de cuerpos rígidos, análisis giroscópico, mecanismos articulados y respuesta a vibraciones forzadas.
- **Simuladores Interactivos en Web (`generative_ui` / Three.js / Canvas)**:
  - Generación de interfaces interactivas donde el usuario pueda variar parámetros (viscosidad $\mu$, densidad $\rho$, rigidez $k$, amortiguamiento $c$) y visualizar gráficos dinámicos o geometrías deformables en tiempo real.

## 2. Rigor Científico y Mecánica de Medios Continuos
- Aplicar obligatoriamente las directrices y soluciones analíticas rigurosas de `intermediate-fluid-mechanics` (Purdue ME 50900) para fluidos viscosos, Navier-Stokes, capa límite y lubricación.
- Para sólidos y dinámica: integración temporal con esquemas numéricos de orden superior (RK4 / Dormand-Prince) y control estricto de conservación de energía y masa.

## 3. Organización y Almacenamiento de Renders
- Los códigos de animación y scripts generadores deben residir en el módulo temático correspondiente:
  - `01 Mecanica de Fluidos/`
  - `02 Dinamica y Vibraciones/`
  - `03 Mecanica de Solidos/`
  - `04 Termodinamica y Calor/`
  - `05 Metodos Numericos y CAE/`
  - `06 Matematicas y Geometria/`
- Los archivos renderizados finales (`.mp4`, `.gif`, `.png`) deben exportarse y guardarse en `RENDERS/` o en la carpeta designada del módulo sin dispersión de archivos.

## 4. Tipografía Matemática TeX y Cero Guiones Bajos (`_`)
- **Prohibición de código crudo en pantalla:** En ninguna animación o tarjeta HUD se deben mostrar nombres de variables con guiones bajos (`T_core`, `p_0`, `M_exit`, `L_d`) ni expresiones en pseudocódigo (`sqrt(...)`, `pe / pa`).
- **Renderizado tipográfico auténtico:** Toda métrica, subíndice o fórmula debe renderizarse con tipografía matemática TeX real ($T_{\mathrm{core}}$, $p_0$, $M_e$, $L_d$, $\theta$, $\beta$, $\nu$) mediante el motor de [`skill_continuum_cinematic_video`](Skills%20e%20Instrucciones/skill_continuum_cinematic_video/SKILL.md) o Manim `MathTex`.

## 5. Estética Cinematográfica y Personalidad Visual
- **Superación del monocromatismo robótico:** Sustituir el cian neón plano por las 4 Armonías Atmosféricas de Estudio (Solar Incandescent, Oceanic Bioluminescence, Quantum Indigo, Kinetic Editorial), iluminación con viñetas radiales y tarjetas *frosted glass* con sombras suaves.
- **Eficiencia de Render:** Modelos analítico-numéricos vectorizados para ejecución y renderizado fluido (<60-90 segundos a 60 FPS).
