# CONTINUUM LAB — Pipeline de Automatización y Publicación en Redes

Este módulo gestiona la distribución multicanal automatizada de simulaciones científicas en formato vertical 9:16 (Shorts, Reels, TikTok), aplicando estrictos controles de seguridad para publicar **únicamente** en los canales de **Continuum Lab** y protegiendo cuentas personales.

---

## 🛡️ Reglas de Seguridad y Filtros de Cuenta

1. **Instagram Reels (`subir_instagram.py`)**:
   - Cuenta activa obligatoria: `@continuumlab_`.
   - Si la sesión de Meta cambiara accidentalmente a una cuenta personal, el script aborta inmediatamente con un error de seguridad `PermissionError`.
2. **YouTube Shorts (`subir_youtube.py` y `autorizar_youtube.py`)**:
   - Canal obligatorio: **Continuum Lab** (canal secundario).
   - Verifica el nombre del canal mediante la API de Google antes de guardar el token o publicar cualquier video.
3. **TikTok (`subir_tiktok.py`)**:
   - Publicación headless mediante Playwright Chromium utilizando `tiktok_cookies.txt`.

---

## 📁 Archivos y Scripts

| Archivo | Función |
| :--- | :--- |
| `publicador_universal.py` | Orquestador maestro. Publica en todas las plataformas simultáneamente con un solo comando. |
| `publicador_metadata.py` | Generador algorítmico de títulos virales, descripciones educativas en inglés y pools de hashtags optimizados para STEM/Física. |
| `subir_instagram.py` | Publicador nativo de Instagram Reels vía `instagrapi` con soporte de portadas y etiquetas. |
| `subir_tiktok.py` | Publicador automatizado para TikTok vía Playwright headless. |
| `subir_youtube.py` | Publicador oficial de YouTube Shorts vía Google Data API v3. |
| `autorizar_youtube.py` | Asistente de un solo paso para autorizar el canal secundario en Google OAuth. |
| `hashtags_master.json` | Catálogo de hashtags y palabras clave SEO indexadas por tópico (`fourier_series`, `lbm_karman`, `airfoil_aerodynamics`). |

---

## 🚀 Comandos de Uso

### 1. Publicar a Instagram y TikTok simultáneamente:
```bash
python publicador_universal.py --platforms instagram,tiktok --title "Drawing Any Shape with Rotating Circles" --topic fourier_series
```

### 2. Publicar a todas las redes (incluyendo YouTube Shorts):
```bash
python publicador_universal.py --platforms all --title "Drawing Any Shape with Rotating Circles" --topic fourier_series
```

### 3. Autorizar canal de YouTube por primera vez:
```bash
python autorizar_youtube.py
```
*(Se abrirá el navegador; selecciona el canal secundario **Continuum Lab** y el token quedará guardado para siempre en `token.json`).*
