# CONTINUUM LAB — MANUAL DE PRODUCCIÓN DE VIDEOS VECTORIALES (TIKTOK 9:16)

Este documento fija los estándares matemáticos y de composición visual para todos los videos orientados a TikTok, Instagram Reels y YouTube Shorts generados por Continuum Lab.

---

## 1. Especificaciones Técnicas del Formato

| Parámetro | Valor Estándar | Justificación Técnica |
| :--- | :--- | :--- |
| **Relación de Aspecto** | `9:16` Vertical | Estándar de consumo móvil a pantalla completa. |
| **Resolución** | `1080 x 1920` px | Nitidez Full HD sin distorsión de escala. |
| **Tasa de Cuadros (FPS)** | `60 FPS` | Movimiento fluido de vórtices y líneas de corriente. |
| **Codec de Video** | `H.264 / MP4` (`yuv420p`) | Máxima compatibilidad con algoritmos de compresión móvil. |
| **Bitrate** | `12 - 18 Mbps` | Evita artefactos de macrobloques en gradientes oscuros. |

---

## 2. Safe Zones (Zonas Seguras de la Interfaz de TikTok)

Las interfaces móviles de TikTok colocan iconos interactivos y textos sobre el video. Para que ningún elemento quede tapado, se definen las siguientes coordenadas absolutas sobre el lienzo de $1080 \times 1920$:

```text
(0, 0) ┌───────────────────────────┐ (1080, 0)
       │     TOP SAFE ZONE (160px)  │ -> Pestañas 'Siguiendo/Para ti' y Búsqueda
       ├───────────────────────────┤
       │                           │
       │                           │
       │    ZONA ACTIVA VISUAL     │ -> HUD Telemetría, Fórmulas LaTeX,
       │    (1080 x 1440 px)       │    Simulación de Vórtices,
       │                           │    Líneas de corriente vectoriales
       │                           │
       │                     [Icon]│ -> 130px Margen Derecho (Likes/Shares)
       ├───────────────────────────┤
       │   BOTTOM SAFE ZONE (320px)│ -> Título, Audio, Caption, Nombre Cuenta
(0,1920) └───────────────────────────┘ (1080, 1920)
```

* **Zona Segura Superior:** $Y \in [0, 160]$ px (Cero información crítica).
* **Zona Segura Inferior:** $Y \in [1600, 1920]$ px (Cero información crítica).
* **Margen Lateral Derecho:** $X \in [950, 1080]$ px (Evitar ubicar tarjetas HUD en esta franja).
* **Zona Óptima de Información y Telemetría:**
  - HUD principal: Centrado superior en $Y \in [180, 480]$, ancho máx. $920$ px.
  - Simulación física / Diagrama central: Centrado en $Y \in [480, 1380]$.
  - Gráfica de fases / Diagrama auxiliar: $Y \in [1380, 1580]$.

---

## 3. Principios de Video Vectorizado

1. **Primitivas Matemáticas Continuas:**
   - Todo trazador, curva cerrada, vector de velocidad o línea de corriente debe calcularse a partir de funciones paramétricas continuas $\mathbf{r}(t)$ o mallas vectoriales.
   - Usar **Manim Community** para gráficos paramétricos, flechas de campo vectorial y renderizado de fórmulas con LaTeX (`MathTex`).
2. **Antialiasing Subpixel:**
   - Cero bordes dentados (*aliasing*). Los contornos de obstáculos y vórtices se renderizan con muestreo suavizado bicúbico o trazado analítico vectorial.
3. **Cero Texto Solapado:**
   - La distancia vertical entre líneas de texto debe ser de al menos $1.5 \times$ la altura del glifo.
   - Cada caja de texto tiene un relleno (*padding*) mínimo de 20 px respecto a cualquier borde de tarjeta.
   - Prohibido renderizar texto sobre el cuerpo de un obstáculo o dentro de la zona de estela turbulenta sin una tarjeta opaca de fondo.
