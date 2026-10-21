# 07. 3D Lorenz Strange Attractor & The Butterfly Effect (1963)

**Division:** `02 Dinamica y Vibraciones / 07 Atractor de Lorenz y Efecto Mariposa 3D`  
**Render ID:** `RENDERS / 19 Atractor de Lorenz Efecto Mariposa 3D`  
**Format:** `1080x1920` (9:16 Vertical UHD @ 60 FPS)

---

## 1. Physical & Mathematical Formulation

In 1963, meteorologist **Edward N. Lorenz** derived a simplified 3-mode spectral truncation of the Saltzman-Rayleigh-Bénard thermal convection equations (*Deterministic Nonperiodic Flow*, *Journal of the Atmospheric Sciences*, 20, 130–141):

$$\begin{aligned}
\frac{dx}{dt} &= \sigma (y - x) \\
\frac{dy}{dt} &= x (\rho - z) - y \\
\frac{dz}{dt} &= x y - \beta z
\end{aligned}$$

### Canonical Parameters & Topological Invariants
- **Prandtl Number:** $\sigma = 10.0$
- **Normalized Rayleigh Number:** $\rho = 28.0 > \rho_H = \frac{\sigma(\sigma+\beta+3)}{\sigma-\beta-1} \approx 24.7368$
- **Geometric Aspect Factor:** $\beta = \frac{8}{3} \approx 2.6667$
- **Convective Wing Equilibrium Cores:**
  $$C_{\pm} = \left(\pm\sqrt{\beta(\rho-1)}, \;\pm\sqrt{\beta(\rho-1)}, \;\rho-1\right) = (\pm 8.4853, \;\pm 8.4853, \;27.0)$$
- **Liouville Phase-Volume Contraction:**
  $$\nabla \cdot \mathbf{F} = \frac{\partial \dot{x}}{\partial x} + \frac{\partial \dot{y}}{\partial y} + \frac{\partial \dot{z}}{\partial z} = -(\sigma + 1 + \beta) = -\frac{41}{3} \approx -13.6667\text{ s}^{-1} < 0$$
- **Lyapunov Spectrum & Kaplan-Yorke Fractal Dimension:**
  $$\lambda_1 \approx +0.9056\text{ s}^{-1}, \quad \lambda_2 = 0.0000\text{ s}^{-1}, \quad \lambda_3 \approx -14.5723\text{ s}^{-1}$$
  $$D_{KY} = 2 + \frac{\lambda_1 + \lambda_2}{|\lambda_3|} \approx 2.0621$$

---

## 2. Execution & Verification

```bash
# Run unit & mathematical tests
pytest tests -v

# Execute complete master pipeline (Audio, Excel Benchmark, ES/EN 60 FPS Videos & Enhanced Covers)
python main.py --all
```
