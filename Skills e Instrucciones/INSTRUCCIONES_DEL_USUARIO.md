# CONTINUUM LAB — REGISTRO MAESTRO DE INSTRUCCIONES DEL USUARIO
**Entorno:** Continuum Lab (Investigación Computacional & Ingeniería Visual)  
**Actualizado:** 2026-09-24  

---

## 1. Misión Central y Objetivo
* **Objetivo principal:** Generar una gran cantidad de videos científicos y simulaciones físicas de clase mundial, con rigor matemático impecable y estética visual hipnótica.
* **Fase actual:** Pruebas y calibración rigurosa de estabilidad, precisión numérica, rendimiento en la RTX 5070 y pipelines gráficos antes de entrar a producción masiva.

---

## 2. Organización de Carpetas (Regla Estricta)
1. **Cero guiones bajos (`_`):** Todas las carpetas principales y subcarpetas deben tener nombres limpios con espacios normales (por ejemplo: `01 Mecanica de Fluidos`, `01 LBM D2Q9 Karman Vortex`, `02 Dinamica y Vibraciones`).
2. **Carpeta `RENDERS` (Enumeración + Descripción):**
   - La carpeta de resultados de videos y entregables finales se llama estrictamente **`RENDERS`** (en la raíz).
   - Dentro de `RENDERS`, cada subcarpeta debe incluir su **número secuencial y el tema de la simulación**, sin guiones bajos:
     - `RENDERS/1 Vortices de von Karman/`
     - `RENDERS/2 Pendulo Triple Trayectoria Caotica/`
     - `RENDERS/3 ...`
   - En cada subcarpeta se almacenan sus videos, capturas y modelos de datos, totalmente separados del código fuente.
3. **Jerarquía Taxonómica de Código:**
   - Cada rama de la física tiene su carpeta dedicada (`01 Mecanica de Fluidos`, `02 Dinamica y Vibraciones`, etc.).
   - Cada nuevo proyecto o simulación se aloja en una subcarpeta dedicada y autocontenida con su propio `src/`, `tests/`, `docs/`, `main.py` y `run.bat`.

---

## 3. Formato y Dinámica de Videos: TikTok 9:16 y Calidad Vectorizada
1. **Duración:** Videos de **15 a 30 segundos**.
2. **Contenido:** Deben mostrar fenómenos **curiosos, hipnóticos y llamativos** desde los primeros segundos (vórtices desprendiéndose, trayectorias caóticas fractales, bifurcaciones de fase, atractores extraños).
3. **PROHIBIDO el título del proyecto:**
   - **No poner el título del proyecto en ninguna parte del video.** Cero rótulos como "Continuum Lab", "LBM D2Q9", "Triple Pendulum", etc.
   - La pantalla debe dedicarse a la pura visualización física, telemetría matemática limpia y trayectorias.
4. **Formato TikTok / Shorts / Reels:**
   - Relación de aspecto vertical **9:16** (1080 x 1920 píxeles a 60 FPS).
5. **Videos Vectorizados:**
   - Todo diagrama, línea de corriente, partícula, flecha de campo vectorial o trayectoria debe generarse con renderizado vectorial de ultra-alta definición (utilizando Manim, Cairo/Skia o pipelines gráficos con antialiasing subpixel), sin artefactos de compresión ni pixelación.
6. **Safe Zones de TikTok (Márgenes Seguros de Pantalla):**
   - **Margen Superior:** 160 px libres (para que la interfaz de búsqueda y pestañas de TikTok no tape nada).
   - **Margen Inferior:** 320 px libres (para no chocar con la descripción, nombre de cuenta, hashtags y selector de audio).
   - **Margen Lateral Derecho:** 130 px libres (para evitar colisión con los botones de like, comentarios, compartir y perfil).
   - **Zona Visual Activa:** Bounding box centrado de $1080 \times 1440$ px.

---

## 4. Estándar Visual: Cero Solapamiento de Texto (Regla Crítica)
* **El enemigo número uno es el texto solapado.**
* Prohibido que un texto tape a otro texto, tape bordes de tarjetas, tape diagramas geométricos o tape la física relevante de la simulación.
* Todos los textos y HUDs deben calcularse con *bounding boxes* estrictos, espaciado generoso y padding matemático garantizado.

---

## 5. Privacidad Absoluta y Anonimato
* No debe aparecer ningún nombre personal, apellido, alias personal ni referencias institucionales en el código, videos, HUDs, licencias ni documentación.
* Todo se firma y presenta exclusivamente bajo el sello técnico neutral de **Continuum Lab**.

---

## 6. Autonomía Total y Trabajo en Segundo Plano
* **Autorización permanente concedida:** Licencia técnica absoluta para crear, mover, editar, simular, testear y renderizar sin pedir confirmación ni permisos intermedios.
* Trabajo autónomo en segundo plano: tomar la decisión técnica óptima y ejecutar hasta completar la meta.
