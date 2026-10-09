# Continuum Lab — Ley Cero de la Termodinámica (Sistema de 3 Cuerpos)

[![Python 3.12](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Status: Production](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()
[![Division: 04 Termodinamica y Calor](https://img.shields.io/badge/Division-04%20Termodin%C3%A1mica%20y%20Calor-orange.svg)]()
[![Physics: 2D Heat Diffusion](https://img.shields.io/badge/Physics-2D%20Continuous%20Fourier-red.svg)]()
[![Resolution: 1080x1920 60 FPS](https://img.shields.io/badge/Video-1080x1920%20%40%2060%20FPS-purple.svg)]()

> **Simulador de Alta Fidelidad y Motor de Producción Audiovisual Científica**  
> Demostración experimental y matemática de la **Ley Cero de la Termodinámica** mediante conducción continua de calor en 2D entre tres cuerpos sólidos en contacto físico perfecto, con telemetría en tiempo real, trazadores cinéticos de flujo de calor y banda sonora electro-synthwave procedural.

<div align="center">
  <img src="../../RENDERS/14%20Ley%20Cero%20Termodinamica%203%20Cuerpos/cover/preview_ley_cero_termodinamica.gif" width="420" alt="Ley Cero Termodinamica Preview GIF"/>
</div>

---

## 1. Fundamento Científico: La Ley Cero de la Termodinámica

La **Ley Cero de la Termodinámica** (formalizada por Ralph H. Fowler en 1935) establece que:

$$\text{Si } T_A = T_C \quad \text{y} \quad T_B = T_C \implies T_A = T_B \equiv T_{eq}$$

Este postulado fundamenta la existencia de la **Temperatura** como una propiedad intrínseca del estado termodinámico y garantiza que el equilibrio térmico es una relación de equivalencia transitiva.

### Ecuaciones Gobernantes de Transporte

1. **Ecuación de Difusión de Calor en 2D (Medio Multimaterial Heterogéneo):**
   $$\rho(\mathbf{x}) c_p(\mathbf{x}) \frac{\partial T}{\partial t} = \nabla \cdot \big( k(\mathbf{x}) \nabla T \big)$$

2. **Vector de Densidad de Flujo Térmico de Fourier:**
   $$\mathbf{q}(\mathbf{x}, t) = -k(\mathbf{x}) \nabla T(\mathbf{x}, t) \quad \left[\frac{\text{W}}{\text{m}^2}\right]$$

3. **Temperatura de Equilibrio Global Invariante ($T_{eq}$):**
   $$T_{eq} = \frac{\sum_{i \in \{A, C, B\}} C_i T_{i,0}}{\sum_{i \in \{A, C, B\}} C_i} = 46.20^\circ\text{C}$$
   donde $C_i = \rho_i c_{p,i} V_i$ es la capacitancia calorífica total de cada sólido.

4. **Irreversibilidad y Segunda Ley (Generación de Entropía):**
   $$\dot{S}_{gen}(t) = \iint_{\Omega} \frac{k(\mathbf{x}) \|\nabla T\|^2}{T(\mathbf{x}, t)^2} \, d\Omega \ge 0 \quad \xrightarrow{t \to \infty} 0$$

---

## 2. Características del Simulador y Renderizador

- **Transferencia Térmica Continua Submilimétrica:** Malla densa 2D ($360 \times 180$, $\Delta x = 0.833\text{ mm}$) con interpolación bicúbica continua; cero pixelado tosco, difusión fluida y gradual.
- **Vectores de Flujo Térmico Dinámicos ($\mathbf{q} = -k\nabla T$):** Flechas luminosas que pulsan y muestran la dirección del transporte de calor a través de las interfaces, extinguiéndose suavemente al alcanzarse el equilibrio.
- **Trazadores Cinéticos Fonónicos:** Partículas que viajan activamente a lo largo de las líneas de flujo de calor, desacelerando suavemente hasta el reposo total en el equilibrio.
- **Marcadores Digitales de Temperatura en Tiempo Real:** Tres paneles superiores legibles sobre cada bloque con actualización numérica en vivo.
- **Diseño Cyberpunk Limpio Sin Solapamientos:** Safe zones móviles para TikTok/Reels/Shorts, lecturas de flujos interfaciales $\dot{Q}_{AC}$ y $\dot{Q}_{CB}$, balance de energía de la Primera Ley ($\Delta E = 0.000\%$) y tasa de entropía $\dot{S}_{gen}$.
- **Gráfico Dinámico de Convergencia:** Curvas en vivo de $T_A(t)$, $T_C(t)$ y $T_B(t)$ convergiendo asintóticamente a la línea de equilibrio $T_{eq}$.
- **Banda Sonora Cinematográfica de Ciencia "Thermal Harmony" (84 BPM):** Pista atmosférica con pads analógicos en evolución, arpegios de marimba/fonón en estéreo y campana celestial de resolución armónica en el equilibrio.

---

## 3. Arquitectura del Proyecto

```
01 Ley Cero de la Termodinamica 3 Cuerpos/
├── docs/
│   └── teoria_ley_cero_termodinamica.md       # Tratado teórico y derivación matemática
├── src/
│   ├── physics/
│   │   ├── heat_zeroth_law.py                # Solver 2D de difusión y volúmenes finitos
│   │   └── export_benchmarks.py              # Exportador a modelo dinámico de Excel (.xlsx)
│   ├── audio/
│   │   └── thermal_synth_music.py            # Sintetizador procedural 124 BPM pegajoso
│   └── visualization/
│       ├── render_zeroth_law_video.py        # Renderizador 1080x1920 60 FPS y HUD
│       └── generate_hero_previews.py         # Generador de portadas PNG y GIF animado
├── tests/
│   └── test_heat_zeroth_law.py               # Suite de 7 pruebas unitarias pytest
├── main.py                                   # CLI unificado multimodo
├── README.md                                 # Documentación técnica principal
└── run.bat                                   # Script ejecutor automático en Windows
```

---

## 4. Guía de Ejecución Rápida (CLI)

```bash
# 1. Resumen físico analítico y tabla asintótica
python main.py

# 2. Renderizar video oficial 1080x1920 @ 60 FPS con música (Full HD)
python main.py --render

# 3. Vista previa ultrarrápida (6.0s @ 30 FPS)
python main.py --preview

# 4. Generar modelo dinámico de Excel (.xlsx)
python main.py --benchmark

# 5. Generar portadas PNG en alta resolución y GIF animado
python main.py --visuals

# 6. Ejecutar suite de pruebas unitarias pytest
python main.py --test

# 7. Ejecutar todos los pasos (benchmark + portadas + render completo)
python main.py --all
```

---

## 5. Salidas Generadas (RENDERS)

Los archivos resultantes se almacenan de forma organizada en:
`RENDERS/14 Ley Cero Termodinamica 3 Cuerpos/`
- `videos/Ley Cero Termodinamica Equilibrio 3 Cuerpos ES.mp4` (1080x1920 @ 60 FPS con audio).
- `cover/cover_ley_cero_es_1080x1920.png` (Portada en Español).
- `cover/cover_zeroth_law_en_1080x1920.png` (Portada en Inglés).
- `cover/preview_ley_cero_termodinamica.gif` (Vista previa animada).
- `benchmarks/Ley_Cero_Termodinamica_Benchmark.xlsx` (Libro dinámico de Excel con fórmulas).
