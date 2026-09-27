# Continuum Lab — Series de Fourier de Formas Geométricas (Círculo, Estrella, Octógono)

**División:** 06 Matemáticas y Geometría  
**Módulo:** 01 Series de Fourier Geométricas  
**Entregables:** Videos TikTok 9:16 ($1080 \times 1920$ @ 60 FPS), Modelos Excel dinámicos, capturas en alta resolución.

---

## 1. Fundamento Matemático

Toda curva cerrada continua en el plano complejo $z(t) = x(t) + i y(t)$ con periodo $T = 2\pi$ admite una representación en Serie Compleja de Fourier:

$$z(t) = \sum_{n=-\infty}^{\infty} c_n \, e^{i n \omega_0 t}$$

donde los coeficientes espectrales $c_n \in \mathbb{C}$ corresponden a los radios y fases de fasores/epiciclos rotatorios:

$$c_n = \frac{1}{T} \int_0^T z(t) \, e^{-i n \omega_0 t} \, dt$$

### Formas Canónicas Analizadas

1. **Círculo ($SO(2)$):**
   $$z(t) = R \, e^{i t}$$
   Posee un único armónico fundamental ($N = 1$). Es el bloque generador elemental de la transformada de Fourier.

2. **Estrella Regular de 5 Puntas ($D_5$):**
   Debido a la simetría diédrica $D_5$, únicamente los armónicos con $n \equiv 1 \pmod 5$ y $n \equiv -4 \pmod 5$ tienen coeficientes no nulos:
   $$z_N(t) \approx r_0 \left[ e^{i t} + \frac{1}{4} e^{-i 4 t} + \frac{1}{9} e^{i 6 t} + \dots \right]$$
   El armónico retrógrado $e^{-i 4 t}$ genera las 5 cúspides afiladas al rotar en sentido inverso 4 veces más rápido.

3. **Octógono Regular ($D_8$):**
   Por simetría diédrica $D_8$, sólo sobreviven armónicos $n \equiv \pm 1 \pmod 8$ ($n \in \{1, -7, 9, -15, 17, \dots\}$), decayendo cuadráticamente como $1/n^2$ debido a la continuidad $C^0$ con derivadas discontinuas en los 8 vértices:
   $$z_N(t) = R_0 \left[ e^{i t} + \frac{1}{49} e^{-i 7 t} + \frac{1}{81} e^{i 9 t} + \dots \right]$$

---

## 2. Estructura de Entregables en `RENDERS`

```text
RENDERS/3 Series de Fourier Geometricas/
├── videos/
│   ├── Series de Fourier Geometricas ES.mp4   (22.0s | 1080x1920 @ 60 FPS | Música Lo-Fi Chill | 3 Pistas +X)
│   └── Geometric Fourier Series EN.mp4        (22.0s | 1080x1920 @ 60 FPS | Lo-Fi Chill Music | 3 Tracks +X)
└── extra/
    ├── capturas/
    │   └── fourier_shapes_hero.png
    └── benchmarks/
        └── Fourier_Harmonics_Geometric_Benchmark.xlsx
```

---

## 3. Ejecución y Pruebas

```bash
# Ejecutar análisis matemático
python main.py

# Generar modelo dinámico de Excel
python main.py --benchmark

# Renderizar videos bilingües
python main.py --render

# Ejecutar suite de pruebas unitarias
python -m pytest tests/
```
