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

## 6. Encuadre Físico Completo (Toda la Geometría Dentro de Pantalla)
- **Cero cortes de elementos físicos:** En ningún proyecto se debe cortar la tobera, cilindro, péndulo o aparato fuera de los bordes superior o laterales del lienzo.
- **Zona activa y margen de respiro:** Toda la estructura física y sus puntos de anclaje deben quedar completamente dentro de la zona activa ($Y \in [370, 1500]$, $X \in [70, 1010]$), guardando al menos 25-35 px de separación respecto a las tarjetas HUD superiores.

## 7. Diseño Sonoro Llamativo de Alto Impacto (Apto para Música de Fondo)
- **Sonidos atractivos y contundentes:** Cero ruidos monótonos o apagados. Incorporar transientes de impacto nítidos (ataque rápido), subgraves viscerales modulados (`np.tanh`), barridos estéreo (*whooshes*) reactivos y campanillas/resonancias agudas en picos físicos.
- **Espacio para música de fondo (*Headroom*):** Ecualización limpia con vaciado del rango medio para permitir incorporar música de fondo sin ensuciar la mezcla.

## 8. Máxima Limpieza Visual e Interlineado Generoso (Prioridad de Aire sobre Saturación)
- **Preferir limpieza y espacio a exceso de información:** Es preferible mostrar **2 o 3 métricas clave** con amplio interlineado y diseño espacioso, antes que 5 líneas apretadas.
- **Interlineado vertical amplio:** Separación generosa entre renglones (mínimo 34 a 42 px entre filas de fórmulas TeX).
- **Cero solapamientos o sensación de amontonamiento:** Las tarjetas deben respirar, con márgenes interiores amplios (padding $\ge 20$ px) y jerarquía clara.
