---
name: video-vector-tiktok
description: Production of mathematically rigorous, vectorized scientific animations in vertical TikTok 9:16 format (1080x1920 @ 60 FPS) using Manim, Cairo vector graphics, and streamlined HUD overlays with zero text overlap.
---

# Video Vector TikTok (`video-vector-tiktok`)

Esta skill define la metodología de producción de videos científicos vectoriales para TikTok, Reels y Shorts en Continuum Lab.

---

## 1. Configuración de Lienzo Manim (9:16 Vertical)

En Manim, para renderizar en $1080 \times 1920$ a 60 FPS con calidad de producción:

```python
from manim import *

# Configuración obligatoria de renderizado vertical 9:16
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#0a0a0c"  # Deep space void
```

---

## 2. Componentes de la Animación Vectorial

1. **Campo Vectorial de Velocidad:**
   - Usar `ArrowVectorField` o `StreamLines` con funciones analíticas $\mathbf{u}(x, y)$.
   - Colores con gradientes dinámicos (`#00f0ff` a `#ff007f`).
2. **Ecuaciones en LaTeX (`MathTex`):**
   - Centradas en la zona media-superior ($y \approx 4.5$ a $6.0$ en coordenadas Manim).
   - Fondo o sombra sutil para contraste nítido.
3. **Tarjeta HUD de Telemetría:**
   - Construida con rectángulos vectoriales `RoundedRectangle`.
   - Textos alineados con `arrange(DOWN, aligned_edge=LEFT, buff=0.25)`.
   - Prohibido cualquier texto solapado.

---

## 3. Línea de Comando para Renderizado Rápido
```bash
manim -qh --format=mp4 -o render_tiktok.mp4 scene_script.py TikTokScene
```
* `-qh`: Calidad alta (1080p).
* Las salidas se dirigen siempre a la carpeta `RENDERS/<numero>/videos/`.
