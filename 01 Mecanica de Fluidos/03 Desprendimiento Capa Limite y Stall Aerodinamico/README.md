# CONTINUUM LAB // 03 DESPRENDIMIENTO DE CAPA LÍMITE Y STALL AERODINÁMICO

Módulo computacional y de simulación visual de alta fidelidad dedicado a la mecánica del desprendimiento de capa límite, gradiente adverso de presión ($\partial p / \partial x > 0$) y colapso de sustentación en régimen de entrada en pérdida (aerodynamic stall).

---

## 🚀 Especificaciones Técnicas

| Parámetro | Valor | Justificación Física |
| :--- | :--- | :--- |
| **Perfil Aerodinámico** | NACA 0012 | Perfil simétrico estándar de referencia aeronáutica |
| **Longitud de Cuerda ($c$)** | $1.0\text{ m}$ | Escala de referencia estándar |
| **Velocidad Asintótica ($U_\infty$)** | $50.0\text{ m/s}$ ($180\text{ km/h}$) | Régimen subsónico incompresible estándar |
| **Número de Reynolds ($Re_c$)** | $1.0 \times 10^6$ | Flujo aerodinámico incompresible turbulento |
| **Ángulo de Ataque Crucero** | $\alpha = 4.0^\circ$ | Régimen adherido: $C_L = 2\pi\alpha = 0.439$ |
| **Ángulo de Pérdida Crítica** | $\alpha = 18.5^\circ$ | Colapso del $74\%$ en $C_L$ ($1.55 \to 0.403$) |
| **Incremento de Arrastre ($C_D$)** | $> 1400\%$ | Explosión de resistencia de forma y estela turbulenta |
| **Condición de Separación** | $(\partial u / \partial y)_{\mathrm{wall}} = 0$ | Cizalladura superficial nula ($\tau_w = 0$, $\Lambda = -12$) |

---

## 📁 Estructura del Módulo

```text
03 Desprendimiento Capa Limite y Stall Aerodinamico/
├── docs/
│   └── teoria_desprendimiento_stall.md    # Formulación matemática rigurosa
├── src/
│   ├── physics/
│   │   ├── aerodynamic_stall.py           # Motor físico de geometría, polar y Pohlhausen
│   │   └── export_benchmarks.py           # Generador dinámico de Excel (.xlsx)
│   ├── audio/
│   │   └── stall_audio_synth.py           # Sintetizador aeroacústico procedimental
│   └── visualization/
│       ├── generate_hero_previews.py      # Diagramas de alta resolución y GIF animado
│       └── render_stall_video.py          # Motor Manim 9:16 60 FPS bilingüe
├── tests/
│   └── test_aerodynamic_stall.py          # Batería de 9 pruebas unitarias
├── main.py                                # CLI unificado de ejecución
├── README.md                              # Documentación del proyecto
└── run.bat                                # Script de arranque rápido en Windows
```

---

## 🛠️ Modos de Ejecución

```bash
# 1. Resumen físico en consola
python main.py

# 2. Batería de pruebas unitarias
pytest tests/ -v

# 3. Exportar modelo dinámico de Excel (.xlsx)
python main.py --benchmark

# 4. Generar diagramas de alta resolución y GIF animado
python main.py --visuals

# 5. Renderizar videos 9:16 a 60 FPS con audio aeroacústico
python main.py --render

# 6. Pipeline completo
python main.py --all
```

---

## 📊 Entregables Generados

Todos los artefactos visuales, benchmarks y videos se ubican en:
`RENDERS/7 Desprendimiento Capa Limite y Stall Aerodinamico/`

* **Videos:**
  - `videos/Desprendimiento Capa Limite y Stall ES.mp4` (Español)
  - `videos/Aerodynamic Stall Boundary Layer Separation EN.mp4` (Inglés)
* **Capturas y Diagramas:**
  - `extra/capturas/aerodynamic_stall_hero.png` (Poster diagnóstico 300 DPI)
  - `extra/capturas/stall_9_16_hero.png` (Portada vertical 1080x1920)
  - `extra/capturas/boundary_layer_velocity_profiles.png` (Perfiles Pohlhausen)
  - `extra/capturas/boundary_layer_separation_preview.gif` (GIF animado de desprendimiento)
* **Benchmarks:**
  - `extra/benchmarks/Aerodynamic_Stall_Boundary_Layer_Benchmark.xlsx` (Modelo Excel con fórmulas 100% dinámicas)
