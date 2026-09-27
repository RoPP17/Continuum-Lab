"""
Continuum Lab - VPython Mechanical & Molecular Physics Simulation
Demonstrating real-time 3D vector kinetics, collision response, and trajectory tracing.
"""
from vpython import canvas, vector, sphere, box, color, rate
import math

def run_simulation(duration_seconds=5.0):
    scene = canvas(
        title="Continuum Lab // VPython 3D Coupled Oscillator",
        width=800,
        height=600,
        background=vector(0.04, 0.05, 0.07),
        center=vector(0, 0, 0),
        forward=vector(0, -0.2, -1)
    )

    # Floor boundary
    floor = box(pos=vector(0, -2, 0), size=vector(10, 0.2, 10), color=vector(0.15, 0.2, 0.3))

    # Two interacting bodies
    p1 = sphere(pos=vector(-2, 1, 0), radius=0.4, color=color.cyan, make_trail=True, retain=150)
    p2 = sphere(pos=vector(2, 1, 0), radius=0.4, color=color.magenta, make_trail=True, retain=150)

    p1.v = vector(0, 0, 1.5)
    p2.v = vector(0, 0, -1.5)
    p1.m = 1.0
    p2.m = 1.0

    k = 8.0 # Spring constant
    r0 = 2.5 # Equilibrium length
    dt = 0.01
    t = 0

    print("Running VPython physics iteration loop...")
    while t < duration_seconds:
        rate(100) # 100 Hz physical stepping
        
        # Spring force between p1 and p2
        r_vec = p2.pos - p1.pos
        dist = math.sqrt(r_vec.x**2 + r_vec.y**2 + r_vec.z**2)
        if dist > 0.001:
            f_mag = -k * (dist - r0)
            f_dir = r_vec / dist
            f_spring = f_mag * f_dir
        else:
            f_spring = vector(0, 0, 0)
            
        # Update velocities and positions
        p1.v += (-f_spring / p1.m) * dt
        p2.v += (f_spring / p2.m) * dt
        
        p1.pos += p1.v * dt
        p2.pos += p2.v * dt
        
        t += dt

    print(f"Simulation completed successfully: {t:.2f} s elapsed.")

if __name__ == "__main__":
    run_simulation(duration_seconds=2.0)
