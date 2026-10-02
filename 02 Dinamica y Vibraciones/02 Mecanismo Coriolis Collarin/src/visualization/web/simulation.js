/**
 * Continuum Lab — Classical Mechanics & Dynamical Systems
 * Division: 02 Dinamica y Vibraciones / 02 Mecanismo Coriolis Collarin
 * Module: simulation.js
 * Hypnotic 120 FPS Canvas Renderer, Dynamic Phosphor Trails, Vector Bloom & Real-time Telemetry.
 */

import { CoriolisPhysicsEngine, CoriolisMechanismParams } from './physics_engine.js';

class CoriolisHypnoticVisualizer {
  constructor() {
    this.canvas = document.getElementById('sim-canvas');
    this.ctx = this.canvas.getContext('2d');

    this.scopeCanvas = document.getElementById('scope-canvas');
    this.scopeCtx = this.scopeCanvas ? this.scopeCanvas.getContext('2d') : null;

    this.phaseCanvas = document.getElementById('phase-canvas');
    this.phaseCtx = this.phaseCanvas ? this.phaseCanvas.getContext('2d') : null;

    // Parametros fisicos iniciales
    this.params = new CoriolisMechanismParams({
      L1: 1.0,
      d: 1.5,
      omega1: 2.2,
      armExtension: 1.7
    });
    this.engine = new CoriolisPhysicsEngine(this.params);

    // Estado de la simulacion
    this.theta1 = 0.0;
    this.time = 0.0;
    this.isRunning = true;
    this.timeScale = 1.0;
    this.baseScale = 95; // Pixeles por metro base
    this.scale = 95;
    this.vectorScale = 22.0;

    // Camara y Pan
    this.basePanX = 0;
    this.basePanY = 120;
    this.panX = 0;
    this.panY = 120;
    this.isDragging = false;
    this.lastMouse = { x: 0, y: 0 };

    // Modo Zoom Cinemático & Slow-Motion
    this.cinematicZoomEnabled = true;
    this.currentZoomWeight = 0.0;

    // Trazas persistentes hipnoticas (buffers)
    this.collarTrail = [];
    this.stylusTrail = [];
    this.coriolisTrail = [];
    this.maxTrailLength = 500;
    this.trailFadeRate = 0.05; // 0.00 = persistencia infinita

    // Buffer de osciloscopio
    this.scopeBuffer = [];
    this.maxScopeSamples = 200;

    // Toggles de vectores visuales
    this.showVectors = {
      coriolis: true,
      vrel: true,
      centripetal: false,
      euler: false,
      total: false
    };

    // Modos visuales
    this.activeTheme = 'neon'; // 'neon', 'blueprint', 'gold', 'aurora'
    this.spirographMode = true;

    this.setupResize();
    this.setupInteractivity();
    this.initUI();
    this.lastFrameTime = performance.now();
    requestAnimationFrame((t) => this.loop(t));
  }

  setupResize() {
    const resize = () => {
      const rect = this.canvas.parentElement.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      this.canvas.width = rect.width * dpr;
      this.canvas.height = rect.height * dpr;
      this.ctx.resetTransform();
      this.ctx.scale(dpr, dpr);
      this.width = rect.width;
      this.height = rect.height;

      if (this.scopeCanvas) {
        const sr = this.scopeCanvas.getBoundingClientRect();
        this.scopeCanvas.width = sr.width * dpr;
        this.scopeCanvas.height = sr.height * dpr;
        this.scopeCtx.resetTransform();
        this.scopeCtx.scale(dpr, dpr);
      }

      if (this.phaseCanvas) {
        const pr = this.phaseCanvas.getBoundingClientRect();
        this.phaseCanvas.width = pr.width * dpr;
        this.phaseCanvas.height = pr.height * dpr;
        this.phaseCtx.resetTransform();
        this.phaseCtx.scale(dpr, dpr);
      }
    };

    window.addEventListener('resize', resize);
    resize();
  }

  setupInteractivity() {
    this.canvas.addEventListener('mousedown', (e) => {
      this.isDragging = true;
      this.lastMouse = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener('mousemove', (e) => {
      if (this.isDragging) {
        this.panX += e.clientX - this.lastMouse.x;
        this.panY += e.clientY - this.lastMouse.y;
        this.lastMouse = { x: e.clientX, y: e.clientY };
      }
    });

    window.addEventListener('mouseup', () => {
      this.isDragging = false;
    });

    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.08 : 0.92;
      this.scale = Math.max(40, Math.min(400, this.scale * zoomFactor));
    }, { passive: false });
  }

  initUI() {
    // Sliders
    const linkSlider = (id, badgeId, prop, fmt, callback) => {
      const el = document.getElementById(id);
      const badge = document.getElementById(badgeId);
      if (!el) return;
      el.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        this.params[prop] = val;
        if (badge) badge.textContent = fmt(val);
        if (callback) callback(val);
      });
    };

    linkSlider('slider-omega', 'val-omega', 'omega1', v => `${v.toFixed(1)} rad/s`);
    linkSlider('slider-d', 'val-d', 'd', v => `${v.toFixed(2)} m`, () => this.clearTrails());
    linkSlider('slider-l1', 'val-l1', 'L1', v => `${v.toFixed(2)} m`, () => this.clearTrails());
    linkSlider('slider-ext', 'val-ext', 'armExtension', v => `${v.toFixed(1)}x`, () => this.clearTrails());

    const trailSlider = document.getElementById('slider-trails');
    if (trailSlider) {
      trailSlider.addEventListener('input', (e) => {
        this.maxTrailLength = parseInt(e.target.value);
        document.getElementById('val-trails').textContent = this.maxTrailLength;
      });
    }

    // Play/Pause
    const playBtn = document.getElementById('btn-play');
    if (playBtn) {
      playBtn.addEventListener('click', () => {
        this.isRunning = !this.isRunning;
        playBtn.textContent = this.isRunning ? '⏸ Pausa' : '▶ Reanudar';
        playBtn.classList.toggle('active', this.isRunning);
      });
    }

    // Step Forward
    const stepBtn = document.getElementById('btn-step');
    if (stepBtn) {
      stepBtn.addEventListener('click', () => {
        this.isRunning = false;
        if (playBtn) {
          playBtn.textContent = '▶ Reanudar';
          playBtn.classList.remove('active');
        }
        this.advancePhysics(0.016);
      });
    }

    // Reset Trails
    const clearBtn = document.getElementById('btn-clear');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => this.clearTrails());
    }

    // Presets
    document.querySelectorAll('.preset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const preset = btn.dataset.preset;
        this.applyPreset(preset);
      });
    });

    // Vector toggles
    document.querySelectorAll('.vector-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        const vKey = pill.dataset.vector;
        this.showVectors[vKey] = !this.showVectors[vKey];
        pill.classList.toggle('active', this.showVectors[vKey]);
      });
    });

    // Time scales
    document.querySelectorAll('.speed-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.timeScale = parseFloat(btn.dataset.speed);
      });
    });

    // Toggle Modo Zoom Cinemático & Slow-Motion
    const cinBtn = document.getElementById('btn-cinematic');
    if (cinBtn) {
      cinBtn.addEventListener('click', () => {
        this.cinematicZoomEnabled = !this.cinematicZoomEnabled;
        cinBtn.classList.toggle('active', this.cinematicZoomEnabled);
        if (!this.cinematicZoomEnabled) {
          this.scale = this.baseScale;
          this.panX = this.basePanX;
          this.panY = this.basePanY;
          const badge = document.getElementById('camera-status-text');
          if (badge) badge.textContent = "VISTA GLOBAL 1.0x";
        }
      });
    }
  }

  applyPreset(preset) {
    this.clearTrails();
    if (preset === 'harmonic') {
      this.params.L1 = 1.0;
      this.params.d = 1.55;
      this.params.omega1 = 2.2;
      this.params.armExtension = 1.6;
    } else if (preset === 'whitworth') {
      this.params.L1 = 1.35;
      this.params.d = 0.85; // d < L1 -> rotacion completa continua
      this.params.omega1 = 2.0;
      this.params.armExtension = 1.4;
    } else if (preset === 'resonant') {
      this.params.L1 = 1.0;
      this.params.d = 1.15; // Cercano a punto singular, gran aceleracion Coriolis
      this.params.omega1 = 1.8;
      this.params.armExtension = 1.8;
    } else if (preset === 'spirograph') {
      this.params.L1 = 1.1;
      this.params.d = 1.7;
      this.params.omega1 = 3.0;
      this.params.armExtension = 2.2;
    }

    // Actualizar sliders del DOM
    const updateInput = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.value = val;
    };
    updateInput('slider-omega', this.params.omega1);
    updateInput('slider-d', this.params.d);
    updateInput('slider-l1', this.params.L1);
    updateInput('slider-ext', this.params.armExtension);

    document.getElementById('val-omega').textContent = `${this.params.omega1.toFixed(1)} rad/s`;
    document.getElementById('val-d').textContent = `${this.params.d.toFixed(2)} m`;
    document.getElementById('val-l1').textContent = `${this.params.L1.toFixed(2)} m`;
    document.getElementById('val-ext').textContent = `${this.params.armExtension.toFixed(1)}x`;
  }

  clearTrails() {
    this.collarTrail = [];
    this.stylusTrail = [];
    this.coriolisTrail = [];
  }

  advancePhysics(dt) {
    this.theta1 += this.params.omega1 * dt;
    this.time += dt;

    if (this.theta1 > Math.PI * 2) {
      this.theta1 -= Math.PI * 2;
    }
  }

  loop(currentTime) {
    const rawDt = Math.min((currentTime - this.lastFrameTime) / 1000, 0.05);
    this.lastFrameTime = currentTime;

    // 1. CÁLCULO DE SLOW-MOTION & ZOOM CINEMÁTICO
    let wZoom = 0;
    if (this.cinematicZoomEnabled) {
      let distCrit = Math.abs(this.theta1 - 1.5 * Math.PI);
      if (distCrit > Math.PI) distCrit = 2 * Math.PI - distCrit;
      wZoom = Math.exp(-(distCrit * distCrit) / (2 * (0.36 * 0.36)));
    }
    this.currentZoomWeight = wZoom;

    // Ralentización temporal suave durante la zona de inversión de Coriolis
    const slowFactor = 1.0 + 3.6 * wZoom;
    const effectiveDt = (rawDt * this.timeScale) / slowFactor;

    if (this.isRunning) {
      this.advancePhysics(effectiveDt);
    }

    const state = this.engine.solve(this.theta1, this.time);

    // 2. INTERPOLACIÓN SUAVE DE CÁMARA (ZOOM Y SEGUIMIENTO DEL COLLARÍN)
    if (this.cinematicZoomEnabled && !this.isDragging) {
      const targetScale = this.baseScale * (1.0 + 1.45 * wZoom);
      const targetPanX = this.basePanX - state.rA[0] * this.scale * (wZoom * 0.85);
      const targetPanY = this.basePanY + (state.rA[1] * this.scale + 30 - this.basePanY) * (wZoom * 0.85);

      this.scale += (targetScale - this.scale) * 0.12;
      this.panX += (targetPanX - this.panX) * 0.12;
      this.panY += (targetPanY - this.panY) * 0.12;

      const badge = document.getElementById('camera-status-text');
      if (badge) {
        if (wZoom > 0.12) {
          badge.textContent = `ZOOM CINEMÁTICO ${(this.scale / this.baseScale).toFixed(1)}x • CÁMARA LENTA ${(1.0 / slowFactor).toFixed(2)}x`;
        } else {
          badge.textContent = `VISTA GLOBAL ${(this.scale / this.baseScale).toFixed(1)}x`;
        }
      }
    }

    // Registrar puntos para trazas hipnoticas
    this.updateTrails(state);
    this.updateTelemetry(state);
    this.draw(state);
    this.drawOscilloscope(state);
    this.drawPhaseSpace(state);

    requestAnimationFrame((t) => this.loop(t));
  }

  updateTrails(state) {
    this.collarTrail.push({ x: state.rA[0], y: state.rA[1] });
    if (this.collarTrail.length > this.maxTrailLength) this.collarTrail.shift();

    this.stylusTrail.push({
      x: state.stylus[0],
      y: state.stylus[1],
      corMag: state.a_cor_mag
    });
    if (this.stylusTrail.length > this.maxTrailLength * 1.5) this.stylusTrail.shift();

    // Hodógrafo / punta del vector Coriolis
    this.coriolisTrail.push({
      x: state.rA[0] + (state.a_cor_vec[0] / this.scale) * this.vectorScale,
      y: state.rA[1] + (state.a_cor_vec[1] / this.scale) * this.vectorScale
    });
    if (this.coriolisTrail.length > this.maxTrailLength) this.coriolisTrail.shift();

    // Buffer osciloscopio
    this.scopeBuffer.push(state.a_cor_mag);
    if (this.scopeBuffer.length > this.maxScopeSamples) this.scopeBuffer.shift();
  }

  updateTelemetry(state) {
    const setTxt = (id, txt) => {
      const el = document.getElementById(id);
      if (el) el.textContent = txt;
    };

    setTxt('telem-cor', `${state.a_cor_mag >= 0 ? '+' : ''}${state.a_cor_mag.toFixed(3)} m/s²`);
    setTxt('telem-vrel', `${state.v_rel.toFixed(3)} m/s`);
    setTxt('telem-w2', `${state.omega2.toFixed(3)} rad/s`);
    setTxt('telem-alpha2', `${state.alpha2.toFixed(3)} rad/s²`);
    setTxt('telem-r2', `${state.r2.toFixed(3)} m`);
    setTxt('telem-arel', `${state.a_rel.toFixed(3)} m/s²`);
    setTxt('telem-regime', this.params.isOscillating ? 'Oscilante' : 'Rotación Continua (Whitworth)');
  }

  toScreen(x, y) {
    const originX = this.width / 2 + this.panX;
    const originY = this.height / 2 + this.panY;
    return {
      x: originX + x * this.scale,
      y: originY - y * this.scale // Canvas Y invertido
    };
  }

  draw(state) {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.width, this.height);

    // Fondo reticular e ingenieril
    this.drawEngineeringGrid();

    // Trazas hipnóticas
    this.drawHypnoticTrails();

    // Geometría del Mecanismo
    this.drawMechanism(state);

    // Vectores dinámicos
    this.drawVectors(state);
  }

  drawEngineeringGrid() {
    const ctx = this.ctx;
    const originX = this.width / 2 + this.panX;
    const originY = this.height / 2 + this.panY;

    ctx.save();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.035)';
    ctx.lineWidth = 1;

    const gridSize = this.scale * 0.5; // cada 0.5 m
    const startX = (originX % gridSize) - gridSize;
    const startY = (originY % gridSize) - gridSize;

    ctx.beginPath();
    for (let x = startX; x < this.width + gridSize; x += gridSize) {
      ctx.moveTo(x, 0);
      ctx.lineTo(x, this.height);
    }
    for (let y = startY; y < this.height + gridSize; y += gridSize) {
      ctx.moveTo(0, y);
      ctx.lineTo(this.width, y);
    }
    ctx.stroke();

    // Circunferencias polares tenues
    ctx.strokeStyle = 'rgba(0, 240, 255, 0.04)';
    for (let r = 1; r <= 4; r++) {
      ctx.beginPath();
      ctx.arc(originX, originY, r * this.scale, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Ejes principales
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
    ctx.beginPath();
    ctx.moveTo(originX, 0);
    ctx.lineTo(originX, this.height);
    ctx.moveTo(0, originY);
    ctx.lineTo(this.width, originY);
    ctx.stroke();

    ctx.restore();
  }

  drawHypnoticTrails() {
    const ctx = this.ctx;

    // 1. Traza hipnótica del Stylus en la punta de la barra (Spirograph fosforescente)
    if (this.stylusTrail.length > 2) {
      ctx.save();
      for (let i = 1; i < this.stylusTrail.length; i++) {
        const p1 = this.toScreen(this.stylusTrail[i - 1].x, this.stylusTrail[i - 1].y);
        const p2 = this.toScreen(this.stylusTrail[i].x, this.stylusTrail[i].y);
        const alpha = (i / this.stylusTrail.length) * 0.75;
        const corVal = Math.abs(this.stylusTrail[i].corMag);

        // Modulación de color hipnótica según Coriolis
        ctx.strokeStyle = `hsla(${270 + Math.min(corVal * 20, 90)}, 100%, 65%, ${alpha})`;
        ctx.lineWidth = 1.5;
        ctx.shadowColor = 'rgba(168, 85, 247, 0.6)';
        ctx.shadowBlur = 8;

        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
      }
      ctx.restore();
    }

    // 2. Traza orbital del collarín (Círculo de la manivela 1)
    if (this.collarTrail.length > 2) {
      ctx.save();
      ctx.beginPath();
      const p0 = this.toScreen(this.collarTrail[0].x, this.collarTrail[0].y);
      ctx.moveTo(p0.x, p0.y);
      for (let i = 1; i < this.collarTrail.length; i++) {
        const p = this.toScreen(this.collarTrail[i].x, this.collarTrail[i].y);
        ctx.lineTo(p.x, p.y);
      }
      ctx.strokeStyle = 'rgba(0, 240, 255, 0.25)';
      ctx.lineWidth = 2;
      ctx.setLineDash([4, 4]);
      ctx.stroke();
      ctx.restore();
    }

    // 3. Traza del hodógrafo de Coriolis (bucle cerrado cardioide)
    if (this.showVectors.coriolis && this.coriolisTrail.length > 2) {
      ctx.save();
      ctx.beginPath();
      const h0 = this.toScreen(this.coriolisTrail[0].x, this.coriolisTrail[0].y);
      ctx.moveTo(h0.x, h0.y);
      for (let i = 1; i < this.coriolisTrail.length; i++) {
        const h = this.toScreen(this.coriolisTrail[i].x, this.coriolisTrail[i].y);
        ctx.lineTo(h.x, h.y);
      }
      ctx.strokeStyle = 'rgba(255, 0, 127, 0.45)';
      ctx.lineWidth = 1.8;
      ctx.shadowColor = '#ff007f';
      ctx.shadowBlur = 10;
      ctx.stroke();
      ctx.restore();
    }
  }

  drawMechanism(state) {
    const ctx = this.ctx;

    const pO1 = this.toScreen(state.rO1[0], state.rO1[1]);
    const pO2 = this.toScreen(state.rO2[0], state.rO2[1]);
    const pA = this.toScreen(state.rA[0], state.rA[1]);
    const pTip = this.toScreen(state.tip[0], state.tip[1]);
    const pStylus = this.toScreen(state.stylus[0], state.stylus[1]);

    // 1. BARRA 2: GUÍA RANURADA (SLOTTED ARM)
    ctx.save();
    // Eje central de la ranura
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
    ctx.lineWidth = 20;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(pO2.x, pO2.y);
    ctx.lineTo(pTip.x, pTip.y);
    ctx.stroke();

    // Rieles luminosos de la ranura
    ctx.strokeStyle = 'rgba(88, 166, 255, 0.7)';
    ctx.lineWidth = 2.5;
    ctx.shadowColor = 'rgba(88, 166, 255, 0.8)';
    ctx.shadowBlur = 12;

    const dx = pTip.x - pO2.x;
    const dy = pTip.y - pO2.y;
    const len = Math.hypot(dx, dy);
    const nx = -dy / len;
    const ny = dx / len;
    const railOffset = 9;

    // Riel izquierdo
    ctx.beginPath();
    ctx.moveTo(pO2.x + nx * railOffset, pO2.y + ny * railOffset);
    ctx.lineTo(pTip.x + nx * railOffset, pTip.y + ny * railOffset);
    ctx.stroke();

    // Riel derecho
    ctx.beginPath();
    ctx.moveTo(pO2.x - nx * railOffset, pO2.y - ny * railOffset);
    ctx.lineTo(pTip.x - nx * railOffset, pTip.y - ny * railOffset);
    ctx.stroke();

    // Estilo Stylus en la punta
    ctx.strokeStyle = '#a855f7';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(pTip.x, pTip.y);
    ctx.lineTo(pStylus.x, pStylus.y);
    ctx.stroke();

    ctx.fillStyle = '#a855f7';
    ctx.shadowColor = '#a855f7';
    ctx.shadowBlur = 14;
    ctx.beginPath();
    ctx.arc(pStylus.x, pStylus.y, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // 2. BARRA 1: MANIVELA IMPULSORA (CRANK O1 - A)
    ctx.save();
    ctx.strokeStyle = 'rgba(230, 237, 243, 0.85)';
    ctx.lineWidth = 5;
    ctx.lineCap = 'round';
    ctx.shadowColor = 'rgba(0, 0, 0, 0.6)';
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.moveTo(pO1.x, pO1.y);
    ctx.lineTo(pA.x, pA.y);
    ctx.stroke();

    // Núcleo brillante de la manivela
    ctx.strokeStyle = '#00f0ff';
    ctx.lineWidth = 1.8;
    ctx.stroke();
    ctx.restore();

    // 3. COLLARÍN DESLIZANTE (SLIDER / COLLAR) EN PUNTO A
    ctx.save();
    ctx.translate(pA.x, pA.y);
    ctx.rotate(-state.theta2); // Alinear el collarín con la barra ranurada

    // Cuerpo mecanizado del collarín (bloque con reflejo metálico)
    const collarW = 28;
    const collarH = 20;
    const grad = ctx.createLinearGradient(-collarW / 2, -collarH / 2, collarW / 2, collarH / 2);
    grad.addColorStop(0, '#ffd700');
    grad.addColorStop(0.5, '#b8860b');
    grad.addColorStop(1, '#ffec8b');

    ctx.fillStyle = grad;
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1.5;
    ctx.shadowColor = 'rgba(255, 215, 0, 0.6)';
    ctx.shadowBlur = 12;

    ctx.beginPath();
    ctx.roundRect(-collarW / 2, -collarH / 2, collarW, collarH, 4);
    ctx.fill();
    ctx.stroke();

    // Pulso lumínico del collarín sincronizado con la aceleración de Coriolis
    const corPulse = Math.min(Math.abs(state.a_cor_mag) / 8.0, 1.0);
    ctx.fillStyle = `rgba(0, 240, 255, ${0.2 + corPulse * 0.7})`;
    ctx.shadowColor = '#00f0ff';
    ctx.shadowBlur = 15 * corPulse;
    ctx.beginPath();
    ctx.arc(0, 0, 5 + corPulse * 3, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();

    // Pasador central A
    ctx.save();
    ctx.fillStyle = '#ffffff';
    ctx.shadowColor = '#ffffff';
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.arc(pA.x, pA.y, 3.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // 4. PIVOTES FIJOS O1 Y O2 (CHASIS / BANCADA)
    this.drawPivot(pO1, 'O₁ (Manivela)', '#00f0ff');
    this.drawPivot(pO2, 'O₂ (Guía)', '#58a6ff');
  }

  drawPivot(pos, label, color) {
    const ctx = this.ctx;
    ctx.save();
    // Soporte triangular de chasis
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.25)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
    ctx.lineTo(pos.x - 12, pos.y + 16);
    ctx.lineTo(pos.x + 12, pos.y + 16);
    ctx.closePath();
    ctx.stroke();

    // Rayado de bancada fija
    ctx.beginPath();
    ctx.moveTo(pos.x - 16, pos.y + 17);
    ctx.lineTo(pos.x + 16, pos.y + 17);
    ctx.stroke();

    // Cojinete central
    ctx.fillStyle = '#0d1117';
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.shadowColor = color;
    ctx.shadowBlur = 10;
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Etiqueta
    ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
    ctx.font = '10px JetBrains Mono, monospace';
    ctx.textAlign = 'center';
    ctx.fillText(label, pos.x, pos.y + 30);
    ctx.restore();
  }

  drawVectors(state) {
    const ctx = this.ctx;
    const pA = this.toScreen(state.rA[0], state.rA[1]);
    const isZooming = this.currentZoomWeight > 0.12;

    // Vector Coriolis: 2 * (omega2 x v_rel)
    if (this.showVectors.coriolis || isZooming) {
      const vCor = [
        (state.a_cor_vec[0] / this.scale) * this.vectorScale,
        (state.a_cor_vec[1] / this.scale) * this.vectorScale
      ];
      const corLbl = isZooming 
        ? `a_cor: ${state.a_cor_mag >= 0 ? '+' : ''}${state.a_cor_mag.toFixed(2)} m/s² (Coriolis)` 
        : '2ω₂ × v_rel (Coriolis)';
      this.drawArrow(pA, vCor, '#00f0ff', corLbl, true);
    }

    // Vector Velocidad Relativa de deslizamiento: v_rel * u_r2
    if (this.showVectors.vrel || isZooming) {
      const vRel = [
        (state.v_rel_vec[0] / this.scale) * (this.vectorScale * 1.5),
        (state.v_rel_vec[1] / this.scale) * (this.vectorScale * 1.5)
      ];
      const relLbl = isZooming 
        ? `v_rel: ${state.v_rel.toFixed(2)} m/s` 
        : 'v_rel (Deslizamiento)';
      this.drawArrow(pA, vRel, '#39ff14', relLbl, false);
    }

    // Vector Centrípeta de arrastre: -(omega2^2 * r2) * u_r2
    if (this.showVectors.centripetal || isZooming) {
      const vCent = [
        (state.a_cent_vec[0] / this.scale) * this.vectorScale,
        (state.a_cent_vec[1] / this.scale) * this.vectorScale
      ];
      const centLbl = isZooming 
        ? `a_n: ${(-state.omega2 * state.omega2 * state.r2).toFixed(2)} m/s²` 
        : 'a_n (Centrípeta O₂)';
      this.drawArrow(pA, vCent, '#ffb800', centLbl, false);
    }

    // Vector Euler / Aceleración Tangencial de arrastre: (alpha2 * r2) * u_theta2
    if (this.showVectors.euler || isZooming) {
      const vEuler = [
        (state.a_euler_vec[0] / this.scale) * this.vectorScale,
        (state.a_euler_vec[1] / this.scale) * this.vectorScale
      ];
      const eulerLbl = isZooming 
        ? `α₂ × r₂: ${(state.alpha2 * state.r2).toFixed(2)} m/s²` 
        : 'α₂ × r₂ (Euler)';
      this.drawArrow(pA, vEuler, '#ff007f', eulerLbl, false);
    }

    // Vector Aceleración Total Absoluta: a_A
    if (this.showVectors.total) {
      const vTot = [
        (state.aA[0] / this.scale) * this.vectorScale,
        (state.aA[1] / this.scale) * this.vectorScale
      ];
      this.drawArrow(pA, vTot, '#ffffff', 'a_A (Total)', false);
    }
  }

  drawArrow(origin, vec, color, label, isMajor = false) {
    const len = Math.hypot(vec[0], vec[1]);
    if (len < 1.0) return;

    const ctx = this.ctx;
    const destX = origin.x + vec[0] * this.scale;
    const destY = origin.y - vec[1] * this.scale; // Y invertido

    ctx.save();
    ctx.strokeStyle = color;
    ctx.fillStyle = color;
    ctx.lineWidth = isMajor ? 3.0 : 2.0;

    if (isMajor) {
      ctx.shadowColor = color;
      ctx.shadowBlur = 14;
    }

    // Linea principal
    ctx.beginPath();
    ctx.moveTo(origin.x, origin.y);
    ctx.lineTo(destX, destY);
    ctx.stroke();

    // Flecha de cabeza (arrowhead)
    const angle = Math.atan2(destY - origin.y, destX - origin.x);
    const arrowSize = isMajor ? 12 : 8;

    ctx.beginPath();
    ctx.moveTo(destX, destY);
    ctx.lineTo(
      destX - arrowSize * Math.cos(angle - Math.PI / 6),
      destY - arrowSize * Math.sin(angle - Math.PI / 6)
    );
    ctx.lineTo(
      destX - arrowSize * Math.cos(angle + Math.PI / 6),
      destY - arrowSize * Math.sin(angle + Math.PI / 6)
    );
    ctx.closePath();
    ctx.fill();

    // Etiqueta flotante
    ctx.font = isMajor ? 'bold 11px JetBrains Mono' : '10px JetBrains Mono';
    ctx.textAlign = 'left';
    ctx.fillText(` ${label}`, destX + 4, destY - 4);
    ctx.restore();
  }

  drawOscilloscope(state) {
    if (!this.scopeCtx) return;
    const ctx = this.scopeCtx;
    const w = this.scopeCanvas.width / (window.devicePixelRatio || 1);
    const h = this.scopeCanvas.height / (window.devicePixelRatio || 1);

    ctx.clearRect(0, 0, w, h);

    // Linea central de cero
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, h / 2);
    ctx.lineTo(w, h / 2);
    ctx.stroke();

    if (this.scopeBuffer.length < 2) return;

    // Trazo de onda de aceleracion de Coriolis a_cor(t)
    ctx.save();
    ctx.strokeStyle = '#00f0ff';
    ctx.lineWidth = 2;
    ctx.shadowColor = '#00f0ff';
    ctx.shadowBlur = 8;

    const maxAmp = 8.0; // Escala vertical
    const stepX = w / (this.maxScopeSamples - 1);

    ctx.beginPath();
    for (let i = 0; i < this.scopeBuffer.length; i++) {
      const val = this.scopeBuffer[i];
      const y = h / 2 - (val / maxAmp) * (h / 2 - 6);
      const x = i * stepX;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Cursor actual
    const curVal = this.scopeBuffer[this.scopeBuffer.length - 1];
    const curY = h / 2 - (curVal / maxAmp) * (h / 2 - 6);
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(w - 4, curY, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  drawPhaseSpace(state) {
    if (!this.phaseCtx) return;
    const ctx = this.phaseCtx;
    const w = this.phaseCanvas.width / (window.devicePixelRatio || 1);
    const h = this.phaseCanvas.height / (window.devicePixelRatio || 1);

    ctx.clearRect(0, 0, w, h);

    // Reticula del plano de fase (v_rel vs omega2)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(w / 2, 0); ctx.lineTo(w / 2, h);
    ctx.moveTo(0, h / 2); ctx.lineTo(w, h / 2);
    ctx.stroke();

    // Rango de fase
    const scaleV = (w / 2 - 12) / 3.0; // v_rel max ~ 3 m/s
    const scaleW = (h / 2 - 12) / 3.0; // w2 max ~ 3 rad/s

    // Trazo de la orbita completa de fase (ciclo limite analitico)
    ctx.save();
    ctx.strokeStyle = 'rgba(0, 240, 255, 0.5)';
    ctx.lineWidth = 1.8;
    ctx.shadowColor = '#00f0ff';
    ctx.shadowBlur = 6;

    ctx.beginPath();
    const numPts = 120;
    for (let i = 0; i <= numPts; i++) {
      const th = (i / numPts) * Math.PI * 2;
      const s = this.engine.solve(th);
      const px = w / 2 + s.v_rel * scaleV;
      const py = h / 2 - s.omega2 * scaleW;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.stroke();

    // Punto de operacion actual
    const curX = w / 2 + state.v_rel * scaleV;
    const curY = h / 2 - state.omega2 * scaleW;

    ctx.fillStyle = '#ff007f';
    ctx.shadowColor = '#ff007f';
    ctx.shadowBlur = 10;
    ctx.beginPath();
    ctx.arc(curX, curY, 4.5, 0, Math.PI * 2);
    ctx.fill();

    // Etiquetas de ejes
    ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.font = '9px JetBrains Mono';
    ctx.textAlign = 'right';
    ctx.fillText('v_rel →', w - 4, h / 2 - 4);
    ctx.textAlign = 'left';
    ctx.fillText('↑ ω₂', w / 2 + 4, 12);
    ctx.restore();
  }
}

// Iniciar al cargar el DOM
window.addEventListener('DOMContentLoaded', () => {
  new CoriolisHypnoticVisualizer();
});
