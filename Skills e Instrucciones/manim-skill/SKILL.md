---
name: manim-skill
description: |
  Trigger when: (1) User mentions "manim" or "manim-skill" or "manim skills repository" or "3Blue1Brown animation", (2) User wants to create mathematical or scientific animations with Manim, (3) User needs best practices, templates, examples, or planning for Manim Community Edition (ManimCE) or ManimGL (3b1b version).
  
  Comprehensive Manim skills suite incorporating:
  - manim-composer: Video planning, narrative arc, scene-by-scene storyboarding (scenes.md)
  - manimce-best-practices: Production-grade Manim Community Edition code, LaTeX, 3D scenes, custom updaters, CLI flags
  - manimgl-best-practices: 3Blue1Brown original OpenGL engine, interactive development (-se flag), shaders, t2c color mapping
---

# Manim Skills Suite (`manim-skill`)

Repository source: [Manim Skills Repository (GitHub: adithya-s-k/manim_skill)](https://github.com/adithya-s-k/manim_skill) / [SourceForge Mirror](https://sourceforge.net/projects/manim-skills-repository.mirror/)

This skill suite equips the agent with production-grade patterns, templates, and reference implementations for creating mathematical, physical, and engineering animations in the 3Blue1Brown style.

---

## 🧭 The 3 Component Skills

### 1. `manim-composer`
* **Purpose**: Video planning and narrative structure before code generation.
* **When to use**: Translating abstract concepts or explanations into a formal `scenes.md` storyboard with visual hooks, narrative arcs, and timing.
* **Location**: `skills/manim-composer/SKILL.md`

### 2. `manimce-best-practices` (Community Edition)
* **Import**: `from manim import *`
* **CLI**: `manim -qh scene_file.py SceneName`
* **Strengths**: Stable, comprehensive documentation, broad ecosystem, export to MP4/GIF/SVG, excellent for scientific pipelines.
* **Location**: `skills/manimce-best-practices/SKILL.md`
* **Submodules**:
  - `rules/`: scenes, mobjects, animations, creation-animations, transform-animations, latex, colors, styling, axes, graphing, 3d, timing, updaters, camera, cli, config.
  - `examples/`: basic_animations, math_visualization, graph_plotting, 3d_visualization, updater_patterns, etc.
  - `templates/`: basic_scene, math_scene, 3d_scene.

### 3. `manimgl-best-practices` (3Blue1Brown / Grant Sanderson)
* **Import**: `from manimlib import *`
* **CLI**: `manimgl scene_file.py SceneName`
* **Strengths**: Real-time OpenGL rendering, interactive keyboard/mouse controls (`-se` flag), live IPython embedding (`self.embed()`), advanced GLSL shaders, `tex_to_color_map` (t2c).
* **Location**: `skills/manimgl-best-practices/SKILL.md`
* **Submodules**:
  - `rules/`: scenes, mobjects, animations, tex, t2c, 3d, camera, interactive, frame, embedding, cli, config.
  - `examples/`: extensive library of 3b1b video scenes (quantum gates, damped ODEs, spring-mass, wave amplitude, etc.).

---

## ⚙️ Quick Reference Workflow

1. **Plan the Animation**:
   Use `manim-composer` to establish the visual hook, mathematical intuition, and scene progression.

2. **Select the Engine**:
   - For batch rendering, vertical 9:16 TikTok/Reels, or robust headless execution $\rightarrow$ **ManimCE** (`manimce-best-practices`).
   - For live visual exploration, interactive inspection, or OpenGL shader effects $\rightarrow$ **ManimGL** (`manimgl-best-practices`).

3. **Render**:
   - Community Edition: `manim -qh -o output.mp4 script.py SceneClass`
   - ManimGL: `manimgl script.py SceneClass -w -o`
