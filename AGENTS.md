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
