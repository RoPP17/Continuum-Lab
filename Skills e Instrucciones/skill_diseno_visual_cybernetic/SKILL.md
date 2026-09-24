---
name: diseno-visual-cybernetic
description: Aesthetic art direction, Cybernetic Laboratory dark palette, non-linear hyperbolic contrast mapping, and strict collision-free bounding box mathematics for scientific HUD overlays.
---

# Diseño Visual Cybernetic (`diseno-visual-cybernetic`)

Esta skill rige la composición estética de Continuum Lab para lograr visualizaciones hipnóticas y limpias.

---

## 1. Paleta de Color "Cybernetic Laboratory"

| Identificador | Código HEX | Rol Físico / Visual |
| :--- | :--- | :--- |
| **Deep Space Void** | `#0a0a0c` | Fondo base de la simulación y límites asintóticos. |
| **Slate Substrate** | `#0d1117` | Fondo opaco de tarjetas HUD y leyendas. |
| **Electric Cyan** | `#00f0ff` | Vorticidad positiva ($\omega_z > 0$, giro antihorario) y bordes de tarjeta. |
| **Vorticity Magenta** | `#ff007f` | Vorticidad negativa ($\omega_z < 0$, giro horario) y fase $C_L$. |
| **Kinetic Amber** | `#ffaa00` | Puntos de estancamiento, gradientes de presión extrema. |
| **Phosphor Lime** | `#39ff14` | Partículas de alta velocidad y marcadores de estado. |
| **Borde / Separador** | `#1f2937` | Líneas divisorias sutiles. |

---

## 2. Algoritmo de Contraste Hiperbólico

Para revelar filamentos lejanos sin sobreexponer las capas límite cercanas al sólido:
$$\tilde{\omega}_z = \tanh\left(\frac{\omega_z}{\omega_0}\right) \in [-1, 1]$$
* $\omega_0 \approx 0.03 - 0.05$ (umbral característico de disipación).

---

## 3. Reglas Matemáticas Anti-Solapamiento (Zero-Overlap)

1. **Aislamiento por Bounding Box:** Todo texto reside dentro de un rectángulo de fondo opaco (`#0d1117`) con borde visible.
2. **Padding Mínimo:** 18 px respecto a cualquier borde exterior.
3. **Paso Interlineal:** $Y_{k+1} = Y_k + 23$ px para fuentes `FONT_HERSHEY_PLAIN` de escala $1.0$ (altura de texto 13 px $\implies$ 10 px de espacio vacío garantizado).
4. **Margen Derecho de Seguridad:** El ancho de tarjeta ($W$) debe superar la longitud máxima calculada del texto en al menos 40 px:
   $$W > \max(\text{text\_width}) + 40\text{ px}$$
