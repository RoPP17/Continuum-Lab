---
name: p5js-simulations
description: |
  Trigger when: (1) User mentions "p5.js" or "p5js" or "canvas simulation", (2) User wants 2D/3D algorithmic art, particle systems, vector flow fields, cellular automata, or mathematical wave simulations, (3) User needs interactive HTML canvas simulations or generative animations exportable to vertical video (9:16) or high-resolution frames.
  
  Provides best practices, modern ES6+ p5.js patterns, responsive 9:16 / 16:9 canvas scaling, frame-accurate animation loops, and MediaRecorder/CCapture video export pipelines.
---

# P5.js Simulations & Generative Canvas (`p5js-simulations`)

This skill equips the agent to write, compile, and preview high-performance, aesthetically refined 2D and 3D p5.js simulations.

---

## 🎨 Architectural Standards

### 1. Standalone Interactive HTML Canvas
Always structure p5.js implementations as self-contained HTML files (or markdown-embedded artifacts) importing p5.js from a fast CDN:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>P5.js Physical Simulation</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.4/p5.min.js"></script>
  <style>
    body { margin: 0; padding: 0; background: #0a0a0c; overflow: hidden; display: flex; justify-content: center; align-items: center; height: 100vh; }
    canvas { box-shadow: 0 0 30px rgba(0, 240, 255, 0.2); }
  </style>
</head>
<body>
<script>
let width = 1080;
let height = 1920; // 9:16 TikTok / Vertical or windowWidth / windowHeight

function setup() {
  createCanvas(windowWidth, windowHeight);
  pixelDensity(displayDensity());
  frameRate(60);
  background(10, 10, 12);
}

function draw() {
  // Physics updates and rendering
}
</script>
</body>
</html>
```

### 2. High-Precision Vector Mechanics
- Use `p5.Vector` for velocities, accelerations, and field evaluations.
- Implement Verlet or Runge-Kutta 4th order (RK4) integration for chaotic or stiff physical systems.
- Leverage layered Perlin noise (`noise(x, y, z)`) with octaves for natural turbulence and fluid-like advection.

### 3. Video & Frame Export
- Use the HTML5 `canvas.captureStream(60)` API and `MediaRecorder` with `video/webm;codecs=vp9` or `video/mp4` to record flawless 60 FPS simulation videos directly from the canvas.
