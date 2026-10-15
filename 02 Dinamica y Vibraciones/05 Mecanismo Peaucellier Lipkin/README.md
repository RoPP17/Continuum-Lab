# Continuum Lab — Mecanismo de Peaucellier-Lipkin (Línea Recta Exacta de 1864)

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Manim Community](https://img.shields.io/badge/Manim-v0.18%2B-orange.svg)](https://www.manim.community/)
[![Resolution](https://img.shields.io/badge/Resolution-1080x1920%20(9%3A16)-purple.svg)](#)
[![FPS](https://img.shields.io/badge/Framerate-60%20FPS-green.svg)](#)
[![Status](https://img.shields.io/badge/Tests-6%2F6%20Passing-brightgreen.svg)](tests/)

---

## 🔬 1. Introducción Histórica & Teorema de Inversión Geométrica

En 1784, **James Watt** introdujo el paralelogramo de Watt en las máquinas de vapor de doble efecto. Aunque lograba aproximar una trayectoria rectilínea en un tramo corto con un error residual de orden polinomial $\mathcal{O}(x^4)$, durante más de 80 años los matemáticos e ingenieros creyeron que era **imposible** convertir una rotación circular pura en una línea recta exacta utilizando únicamente eslabonamientos articulados con pasadores rotatorios (pares cinemáticos de revolución $R$), sin recurrir a guías prismáticas o rieles deslizantes.

En 1864, el ingeniero militar francés **Charles-Nicolas Peaucellier** (y de forma independiente en 1871, el matemático lituano-ruso **Lipman Lipkin**) resolvieron el problema histórico mediante la **inversión geométrica en el plano complejo** utilizando un mecanismo planar de 8 eslabones (7 barras móviles + 1 bancada fija).

---

## 📐 2. Formulación Matemática Rigurosa

Sean:
- $O_1$: Polo fijo de inversión situado en $(x_{O1}, y_{O1}) = (-2.00, 0.00)\text{ cm}$.
- $O_2$: Pivote fijo de la manivela guía situado a distancia $r$ de $O_1$: $(x_{O2}, y_{O2}) = (-1.15, 0.00)\text{ cm}$.
- $r$: Radio de la manivela conductora $O_2P = 0.85\text{ cm}$.
- $R$: Longitud de las dos barras principales $O_1A = O_1B = 2.80\text{ cm}$.
- $l$: Lado del rombo articulado $AP = BP = AP' = BP' = 1.60\text{ cm}$.

### 2.1 Demostración de la Potencia de Inversión Constante ($k$)
Consideremos el rombo articulado $APBP'$. Por simetría planar respecto a la recta diagonal $O_1PP'$:
- Las diagonales $AB$ y $PP'$ se intersecan perpendicularmente en su punto medio común $M$.
- En el triángulo rectángulo $\triangle O_1MA$:
  $$O_1A^2 = O_1M^2 + MA^2 \implies R^2 = O_1M^2 + MA^2$$
- En el triángulo rectángulo $\triangle PMA$:
  $$PA^2 = PM^2 + MA^2 \implies l^2 = PM^2 + MA^2$$

Restando ambas ecuaciones:
$$R^2 - l^2 = O_1M^2 - PM^2 = (O_1M - PM)(O_1M + PM)$$

Dado que $O_1M - PM = O_1P$ y $O_1M + PM = O_1P'$:
$$O_1P \cdot O_1P' = R^2 - l^2 = k \quad (\text{Constante de Inversión})$$

Con nuestros parámetros de diseño:
$$k = 2.80^2 - 1.60^2 = 7.84 - 2.56 = 5.2800\text{ cm}^2$$

### 2.2 Transformación Conforme de Círculo en Recta Euclídea
El extremo de la manivela $P$ se desplaza sobre una circunferencia de radio $r$ que pasa exactamente por el polo de inversión $O_1$:
$$(x - (x_{O1} + r))^2 + y^2 = r^2$$
En coordenadas polares relativas al polo $O_1$ con ángulo rayo $\phi$:
$$O_1P(\phi) = 2r \cos\phi$$

Sustituyendo en la ley de inversión:
$$O_1P'(\phi) = \frac{k}{O_1P(\phi)} = \frac{k}{2r \cos\phi}$$

La coordenada horizontal $x$ del trazador $P'$ respecto a $O_1$ es:
$$x_{rel} = O_1P'(\phi) \cos\phi = \left( \frac{k}{2r \cos\phi} \right) \cos\phi = \frac{k}{2r} = \text{CONSTANTE}$$

Por lo tanto, la coordenada global del punto trazador $P'$ es estrictamente invariable:
$$x_{P'} = x_{O1} + \frac{R^2 - l^2}{2r} = -2.00 + \frac{5.28}{2(0.85)} = -2.00 + 3.10588 = +1.1059\text{ cm}$$

$$\varepsilon_{\text{lineal}} = |x_{P'}(t) - x_{\text{exacta}}| = 0.000000000\text{ mm} \quad (\text{Error Absoluto } = 0.00\%)$$

---

## 🎨 3. Arquitectura Visual & Safe Zones (TikTok 9:16)

El renderizador de Continuum Lab aplica los estándares más estrictos para pantallas de teléfonos móviles:
- **Relación de aspecto:** 9:16 Vertical (`1080x1920` px @ 60 FPS).
- **Zona Segura Superior:** Margen libre $> 160\text{ px}$ para botones de búsqueda y pestañas nativas.
- **Zona Segura Inferior:** Margen libre $> 380\text{ px}$ para nombre de cuenta, caption multilinea, selector de audio y scrubber de progreso.
- **Margen Lateral Derecho:** Margen libre $> 150\text{ px}$ evitando interacción con los iconos de perfil, likes, comentarios y compartidos.
- **Zero Text Overlap:** Aislamiento total de cajas de texto con tarjetas de contraste opacas (`#10172A`) y tipografía monoespaciada `Consolas`.

---

## 🚀 4. Comandos de Ejecución

```bash
# Verificación teórica y resumen analítico
python main.py

# Ejecución de la suite completa de pruebas unitarias (6 tests verdes)
python main.py --test

# Exportación del modelo dinámico de benchmark en Excel (.xlsx)
python main.py --benchmark

# Compilación de los videos verticales 9:16 bilingües en calidad de producción (60 FPS)
python main.py --render
```
