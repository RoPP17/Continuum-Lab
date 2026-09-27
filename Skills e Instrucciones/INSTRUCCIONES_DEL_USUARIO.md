# CONTINUUM LAB — REGISTRO MAESTRO DE INSTRUCCIONES DEL USUARIO
**Entorno:** Continuum Lab (Investigación Computacional & Ingeniería Visual)  
**Actualizado:** 2026-09-25  

---

## 1. Misión Central y Objetivo
* **Objetivo principal:** Generar una gran cantidad de videos científicos y simulaciones físicas de clase mundial, con rigor matemático impecable y estética visual hipnótica.
* **Fase actual:** Producción de simulaciones físicas con audio reactivo de alta fidelidad, dinámicas interactivas y entrega bilingüe.

---

## 2. Organización de Carpetas (Regla Estricta)
1. **Cero guiones bajos (`_`):** Todas las carpetas principales y subcarpetas deben tener nombres limpios con espacios normales (por ejemplo: `01 Mecanica de Fluidos`, `01 LBM D2Q9 Karman Vortex`, `02 Dinamica y Vibraciones`).
2. **Carpeta `RENDERS` (Enumeración + Tema + Partición Estricta):**
   - La carpeta de resultados de videos y entregables finales se llama estrictamente **`RENDERS`** (en la raíz).
   - Dentro de `RENDERS`, cada subcarpeta incluye su **número secuencial y el tema de la simulación**, sin guiones bajos:
     - `RENDERS/1 Vortices de von Karman/`
     - `RENDERS/2 Pendulo Triple Trayectoria Caotica/`
     - `RENDERS/3 ...`
   - **Partición interna obligatoria en cada subcarpeta de `RENDERS`:**
     - `videos/`: Almacena exclusivamente los videos finales generados (`.mp4`).
     - `extra/`: Subcarpeta que agrupa todo material complementario:
       - `extra/capturas/`: Imágenes de alta resolución (`.png`, hero previews, GIFs).
       - `extra/benchmarks/`: Modelos dinámicos de Excel (`.xlsx`), métricas y datos numéricos.
3. **Jerarquía Taxonómica de Código:**
   - Cada rama de la física tiene su carpeta dedicada (`01 Mecanica de Fluidos`, `02 Dinamica y Vibraciones`, etc.).
   - Cada proyecto se aloja en una subcarpeta dedicada y autocontenida con su propio `src/`, `tests/`, `docs/`, `main.py` y `run.bat`.

---

## 3. Formato y Dinámica de Videos: TikTok 9:16 y Calidad Vectorizada
1. **Duración:** Videos de **15 a 30 segundos** (típicamente 18.0 s a 60 FPS = 1080 fotogramas).
2. **Contenido:** Deben mostrar fenómenos **curiosos, hipnóticos y llamativos** desde los primeros segundos:
   - En fluidos: la bolita/esfera central debe **moverse e interferir activamente** con el fluido, generando perturbaciones, desprendimiento dinámico de vórtices y acoplamiento fluido-estructura.
   - En sistemas caóticos: el péndulo triple dibuja su trayectoria fractal completa y envolvente.
3. **PROHIBIDO el título del proyecto en la pantalla:**
   - **No poner el título del proyecto ni branding en ninguna parte del video.** Cero rótulos como "Continuum Lab", "LBM D2Q9", "Triple Pendulum", etc.
   - La pantalla se reserva al 100% para ecuaciones físicas fundamentales, telemetría matemática limpia y trayectorias.
4. **Entrega Bilingüe Obligatoria (ES / EN):**
   - Cada proyecto genera dos versiones de video:
     - Versión en **Español** (`... ES.mp4`): textos, subtítulos y unidades en español.
     - Versión en **Inglés** (`... EN.mp4`): textos, subtítulos y unidades en inglés.
   - Los nombres de archivo incluyen el título del proyecto y el sufijo de idioma, por ejemplo:
     - `RENDERS/1 Vortices de von Karman/videos/Vortices de von Karman ES.mp4`
     - `RENDERS/1 Vortices de von Karman/videos/von Karman Vortices EN.mp4`
     - `RENDERS/2 Pendulo Triple Trayectoria Caotica/videos/Pendulo Triple Caotico ES.mp4`
     - `RENDERS/2 Pendulo Triple Trayectoria Caotica/videos/Chaotic Triple Pendulum EN.mp4`
5. **Formato TikTok / Shorts / Reels:**
   - Relación de aspecto vertical **9:16** (1080 x 1920 píxeles a 60 FPS).
6. **Videos Vectorizados:**
   - Todo diagrama, línea de corriente, partícula, flecha de campo vectorial o trayectoria debe generarse con renderizado vectorial de ultra-alta definición (Manim / Cairo con subpixel antialiasing).
7. **Safe Zones de TikTok (Márgenes Seguros de Pantalla):**
   - **Margen Superior:** 160 px libres (HUD centrado en $y \approx 5.8$).
   - **Margen Inferior:** 320 px libres (HUD centrado en $y \approx -5.6$).
   - **Margen Lateral Derecho:** 130 px libres.

---

## 4. Audio Físico y Reactivo de Alta Fidelidad (Regla Obligatoria)
* **Todo video debe incluir un diseño sonoro llamativo y de alta fidelidad:**
  - **Mecánica de Fluidos:** Sonido hidrodinámico continuo (ruido rosa filtrado pasa-banda), oleadas y whooshes proporcionales a la velocidad y aceleración del obstáculo móvil, silbato acústico de Strouhal (Aeolian tone) con paneo estéreo alternado según el desprendimiento de vórtices.
  - **Sistemas Caóticos / Péndulo:** Síntesis FM reactiva cuya frecuencia portadora $f_c(t)$ sigue continuamente la velocidad del extremo libre, armónicos metálicos que brillan con la aceleración caótica, campanas/chimes en picos cinéticos y paneo espacial estéreo que sigue la coordenada horizontal $x_3(t)$.
* **Multiplexación:** Audio PCM estéreo 44.1 kHz multiplexado con FFmpeg en codec AAC a 192 kbps.

---

## 5. Estándar Visual: Cero Solapamiento de Texto (Regla Crítica)
* **El enemigo número uno es el texto solapado.**
* Prohibido que un texto tape a otro texto, tape bordes de tarjetas, tape diagramas geométricos o tape la física relevante de la simulación.
* Todos los textos y HUDs deben calcularse con *bounding boxes* estrictos, espaciado generoso y padding matemático garantizado.

---

## 6. Privacidad Absoluta y Anonimato
* No debe aparecer ningún nombre personal, apellido, alias personal ni referencias institucionales en el código, videos, HUDs, licencias ni documentación.
* Todo se firma y presenta exclusivamente bajo el sello técnico neutral de **Continuum Lab**.

---

## 7. Autonomía Total y Trabajo en Segundo Plano
* **Autorización permanente concedida:** Licencia técnica absoluta para crear, mover, editar, simular, testear y renderizar sin pedir confirmación ni permisos intermedios.
* Trabajo autónomo en segundo plano: tomar la decisión técnica óptima y ejecutar hasta completar la meta.

---

## 8. Estrategia de Viralidad, Interacción Comunitaria y Despliegue Bilingüe Escalonado
* **Objetivo Primario Absoluto:** Maximizar la repercusión algorítmica, interacción de la audiencia y retención de comunidad técnica global.
* **Fase 1 (Alcance Global en Inglés):**
  - Todas las publicaciones iniciales en redes sociales (TikTok, Instagram Reels, YouTube Shorts), títulos, descripciones, hashtags y repositorios se despliegan **exclusivamente en inglés**.
  - Razón técnica: los algoritmos internacionales de STEM (EE.UU., Europa, Asia) concentran el mayor volumen de descubrimiento orgánico y retención técnica para simulaciones matemáticas complejas.
* **Fase 2 (Expansión y Liderazgo Hispano):**
  - Una vez consolidada la masa crítica y la autoridad algorítmica, se introduce el contenido en español (versiones `... ES.mp4`, hilos técnicos en español y tutoriales) para liderar el nicho de ingeniería computacional hispanohablante.
* **Fórmula de Retención & Interacción en Videos:**
  - **Hook Hipnótico (0.0s - 2.5s):** Inicio instantáneo en movimiento rápido con fenómeno visual de alto impacto (nunca intros lentas ni títulos estáticos).
  - **Evolución y Clímax (2.5s - 14.0s):** Desarrollo del fenómeno con fórmulas matemáticas exactas, audio reactivo y cambios armónicos.
  - **Call to Action (CTA) Provocativo Obligatorio (14.0s - 18.0s):** Cada descripción y cierre de video debe incluir una pregunta abierta o reto matemático para obligar al espectador a comentar (e.g. *"What chaotic boundary condition should we simulate next? Drop it below."* / *"Can you spot the harmonic frequency where resonance breaks?"*).
* **Funnel de Conversión hacia Código Abierto:**
  - Las publicaciones deben referenciar el repositorio abierto en GitHub (`github.com/RoPP17/Continuum-Lab`) para que los usuarios clonen el código, verifiquen la física, dejen estrellas (⭐) y participen en debates de código.

---

## 9. Sincronización Continua del Repositorio en GitHub
* **Regla de Sincronización:** Cada vez que se publique o actualice un proyecto en redes sociales, el repositorio local debe quedar automáticamente sincronizado y empujado a GitHub en `https://github.com/RoPP17/Continuum-Lab`.
* **Higiene Estricta del Repositorio:**
  - Cero credenciales ni tokens en commits (`.gitignore` auditado de forma permanente).
  - Cero archivos de video pesados (`.mp4`, `.mov`) en el árbol de git; se versionan exclusivamente scripts, benchmarks en Excel, capturas de alta definición y documentación.
  - Organización modular y limpia, con tests unitarios pasando y READMEs descriptivos.

