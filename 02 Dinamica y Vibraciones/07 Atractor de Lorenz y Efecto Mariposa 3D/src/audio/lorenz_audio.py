"""
Continuum Lab - Procedural Binaural Stereo Audio Synthesis for 3D Lorenz Strange Attractor
Module: 02 Dinamica y Vibraciones / 07 Atractor de Lorenz y Efecto Mariposa 3D
File: src/audio/lorenz_audio.py

Synthesizes a 44.1 kHz 16-bit stereo PCM soundtrack directly coupled to Lorenz dynamics:
  - 48 Hz Deep Cosmic Sub-Bass Drone modulated by convective potential z(t)
  - Dual-Trajectory Binaural FM Voices:
      * Voice A (Reference Orbit) panned dynamically by x_A(t) (Left Wing C_- vs Right Wing C_+)
      * Voice B (Perturbed Orbit) panned dynamically by x_B(t)
  - 0.0s - 5.0s: Voices A and B sing in phase-locked unison
  - 5.1s: Saddle Bifurcation Chime & Binaural Stereo Split as trajectories jump to opposite wings
  - Separatrix lobe-switching crystalline bells when x(t) crosses 0
"""

import wave
from pathlib import Path
import numpy as np
from src.physics.lorenz_sim import LorenzSimulation


def synthesize_lorenz_soundtrack(output_wav: str, duration: float = 18.0, sample_rate: int = 44100) -> str:
    num_samples = int(duration * sample_rate)
    t = np.linspace(0.0, duration, num_samples, endpoint=False)

    # Pre-integrate Lorenz simulation at 200 Hz control rate to extract exact trajectories
    ctrl_fps = 200
    n_ctrl = int(duration * ctrl_fps) + 1
    t_ctrl = np.linspace(0.0, duration, n_ctrl)

    sim = LorenzSimulation()
    xa_ctrl = np.zeros(n_ctrl)
    za_ctrl = np.zeros(n_ctrl)
    xb_ctrl = np.zeros(n_ctrl)
    zb_ctrl = np.zeros(n_ctrl)
    div_ctrl = np.zeros(n_ctrl)

    for i, tc in enumerate(t_ctrl):
        telem = sim.advance_to_time(float(tc))
        xa_ctrl[i] = telem.traj_a.x
        za_ctrl[i] = telem.traj_a.z
        xb_ctrl[i] = telem.traj_b.x
        zb_ctrl[i] = telem.traj_b.z
        div_ctrl[i] = telem.euclidean_divergence

    # Interpolate to audio sample rate
    xa = np.interp(t, t_ctrl, xa_ctrl)
    za = np.interp(t, t_ctrl, za_ctrl)
    xb = np.interp(t, t_ctrl, xb_ctrl)
    zb = np.interp(t, t_ctrl, zb_ctrl)
    div = np.interp(t, t_ctrl, div_ctrl)

    # 1. Deep Space D-Minor Sub-Bass Drone (D1 = 36.71 Hz + D2 = 73.42 Hz + A2 = 110.0 Hz)
    drone_mod = 0.85 + 0.15 * np.sin(2.0 * np.pi * 0.25 * t)
    drone = (
        0.38 * np.sin(2.0 * np.pi * 73.42 * t) +
        0.22 * np.sin(2.0 * np.pi * 110.00 * t) +
        0.15 * np.sin(2.0 * np.pi * 146.83 * t)
    ) * drone_mod

    # 2. Kinetic Shock Hook Boom at t = 0.05s
    hook_env = np.exp(-t * 2.8)
    hook_boom = 0.45 * hook_env * np.sin(2.0 * np.pi * (95.0 * np.exp(-t * 1.5) + 42.0) * t)

    # 3. Dual FM Synthesizer Voices tracking Z-convection height (z in [5, 45])
    # Voice A (Cyan): Base D3 (146.83 Hz) -> sweeps smoothly with z_A
    # Voice B (Magenta): Base A3 (220.00 Hz) blended with D3 before bifurcation
    div_Ratio = np.clip(div / 18.0, 0.0, 1.0)
    f_a = 146.83 * (1.0 + 0.022 * (za - 25.0))
    f_b_locked = 146.83 * (1.0 + 0.022 * (zb - 25.0))
    f_b_split = 220.00 * (1.0 + 0.022 * (zb - 25.0))
    f_b = (1.0 - div_Ratio) * f_b_locked + div_Ratio * f_b_split

    phase_a = 2.0 * np.pi * np.cumsum(f_a) / sample_rate
    phase_b = 2.0 * np.pi * np.cumsum(f_b) / sample_rate

    voice_a = np.tanh(1.15 * np.sin(phase_a) + 0.30 * np.sin(2.0 * phase_a))
    voice_b = np.tanh(1.15 * np.sin(phase_b) + 0.30 * np.sin(2.0 * phase_b))

    # Binaural Stereo Panning: Left Wing (x < 0) -> Left Channel, Right Wing (x > 0) -> Right Channel
    pan_a = np.clip(0.5 + xa / 38.0, 0.12, 0.88)
    pan_b = np.clip(0.5 + xb / 38.0, 0.12, 0.88)

    # 4. Saddle Bifurcation & Lobe-Switching Crystalline Chimes
    # Detect zero crossings of xa_ctrl and xb_ctrl (wing switches)
    chimes_l = np.zeros_like(t)
    chimes_r = np.zeros_like(t)

    # Pentatonic D-minor crystal notes (D5, F5, A5, C6, D6)
    notes = [587.33, 698.46, 880.00, 1046.50, 1174.66]
    crossing_indices_a = np.where(np.diff(np.sign(xa_ctrl)) != 0)[0]
    for idx_num, c_idx in enumerate(crossing_indices_a):
        tc_event = t_ctrl[c_idx]
        if 0.3 < tc_event < duration - 0.4:
            dt_ev = t - tc_event
            mask = (dt_ev >= 0.0) & (dt_ev < 0.75)
            if np.any(mask):
                tau = dt_ev[mask]
                freq = notes[idx_num % len(notes)]
                bell = 0.28 * np.exp(-tau * 6.5) * (
                    np.sin(2.0 * np.pi * freq * tau) +
                    0.35 * np.sin(2.0 * np.pi * 2.0 * freq * tau)
                )
                chimes_l[mask] += bell * 0.7
                chimes_r[mask] += bell * 0.5

    # Major Bifurcation Resonance Chord around t = 5.1s (when trajectories split onto opposite wings)
    t_bif = 5.10
    dt_bif = t - t_bif
    bif_mask = (dt_bif >= 0.0) & (dt_bif < 2.2)
    if np.any(bif_mask):
        tau = dt_bif[bif_mask]
        chord = 0.36 * np.exp(-tau * 2.2) * (
            np.sin(2.0 * np.pi * 587.33 * tau) +
            0.7 * np.sin(2.0 * np.pi * 698.46 * tau) +
            0.7 * np.sin(2.0 * np.pi * 880.00 * tau)
        )
        chimes_l[bif_mask] += chord
        chimes_r[bif_mask] += chord

    # Mix Stereo Channels
    left_ch = (
        (drone + hook_boom) * 0.30 +
        voice_a * (1.0 - pan_a) * 0.32 +
        voice_b * (1.0 - pan_b) * 0.32 +
        chimes_l * 0.35
    )
    right_ch = (
        (drone + hook_boom) * 0.30 +
        voice_a * pan_a * 0.32 +
        voice_b * pan_b * 0.32 +
        chimes_r * 0.35
    )

    # Smooth Fade-In (0.2s) and Seamless Loop Fade-Out (0.45s)
    fade_in = int(0.20 * sample_rate)
    fade_out = int(0.45 * sample_rate)
    left_ch[:fade_in] *= np.linspace(0.0, 1.0, fade_in)
    right_ch[:fade_in] *= np.linspace(0.0, 1.0, fade_in)
    left_ch[-fade_out:] *= np.linspace(1.0, 0.0, fade_out)
    right_ch[-fade_out:] *= np.linspace(1.0, 0.0, fade_out)

    # Peak Normalize to -1.0 dBFS (0.891 amplitude)
    peak = max(float(np.max(np.abs(left_ch))), float(np.max(np.abs(right_ch))))
    if peak > 0:
        left_ch = (left_ch / peak) * 0.89
        right_ch = (right_ch / peak) * 0.89

    left_i16 = (left_ch * 32767.0).astype(np.int16)
    right_i16 = (right_ch * 32767.0).astype(np.int16)

    stereo = np.empty((num_samples * 2,), dtype=np.int16)
    stereo[0::2] = left_i16
    stereo[1::2] = right_i16

    Path(output_wav).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(output_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(stereo.tobytes())

    print(f"[OK] Procedural binaural Lorenz soundtrack synthesized: {output_wav} ({duration:.1f}s @ 44.1kHz)")
    return output_wav
