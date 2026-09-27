---
name: vpython-physics
description: |
  Trigger when: (1) User mentions "vpython" or "VPython" or "GlowScript", (2) User wants 3D physics simulations of molecular dynamics, planetary orbits, rigid body mechanics, robotic arms, gyroscopes, or electromagnetic fields, (3) User needs interactive 3D physical modeling in Python with real-time vector calculus.
  
  Provides best practices for VPython 7 (GlowScript 3D engine), true vector-based dynamics, real-time rate stepping, collision detection, and scene recording.
---

# VPython 3D Physics Simulation (`vpython-physics`)

This skill provides comprehensive patterns for interactive, mathematically rigorous 3D physics modeling using Python and VPython (GlowScript WebGL engine).

---

## 🔬 Core Standards

### 1. Structure of a Real-Time VPython Simulation

```python
from vpython import canvas, vector, sphere, arrow, cylinder, box, rate, color

# 1. Canvas Setup
scene = canvas(
    title="3D Molecular & Mechanical Physics",
    width=1080,
    height=1080,
    background=vector(0.04, 0.04, 0.05),
    center=vector(0, 0, 0),
    forward=vector(0, -0.3, -1)
)

# 2. Physical Entities with Vector Attributes
body = sphere(
    pos=vector(0, 2, 0),
    radius=0.5,
    color=color.cyan,
    make_trail=True,
    trail_type="curve",
    retain=200
)
body.v = vector(1.5, 0, 0)
body.m = 1.0

# 3. Dynamic Simulation Loop
dt = 0.01
t = 0
g = vector(0, -9.81, 0)

while t < 20:
    rate(100) # Enforce 100 Hz simulation pacing
    
    # Physics computation
    F_net = body.m * g
    body.v += (F_net / body.m) * dt
    body.pos += body.v * dt
    
    # Ground collision
    if body.pos.y <= body.radius:
        body.v.y = -body.v.y * 0.85 # Restitution
        body.pos.y = body.radius
        
    t += dt
```

### 2. High-Performance Mechanics Modules
- **Molecular Dynamics**: Lennard-Jones potential $V(r) = 4\epsilon \left[ \left(\frac{\sigma}{r}\right)^{12} - \left(\frac{\sigma}{r}\right)^6 \right]$ with periodic boundary conditions.
- **Electromagnetism**: Lorentz force $\mathbf{F} = q(\mathbf{E} + \mathbf{v} \times \mathbf{B})$ with 3D field vector arrows.
- **Orbital Mechanics**: $N$-body gravitational integration with Runge-Kutta 4th order.
