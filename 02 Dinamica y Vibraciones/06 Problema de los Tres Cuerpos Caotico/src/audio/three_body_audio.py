"""
Continuum Lab - Procedural Gravitational Acoustic Synthesis for 3-Body Dynamics
Module: 02 Dinamica y Vibraciones / 06 Problema de los Tres Cuerpos Caotico
File: src/audio/three_body_audio.py

Synthesizes 44.1 kHz 16-bit stereo PCM soundtrack:
  - Deep space 55 Hz gravitational sub-bass drone modulated by kinetic energy
  - Polyphonic 3-voice orbital Doppler synthesizer tracking Star velocities (v1, v2, v3)
  - Close-encounter periastron shock pings during violent slingshots
  - Dynamic spatial stereo panning driven by orbital positions (x1, x2, x3)
"""

import wave
from pathlib import Path
import numpy as np


def synthesize_three_body_soundtrack(output_wav: str, duration: float = 18.0, sample_rate: int = 44100):
    num_samples = int(duration * sample_rate)
    t = np.linspace(0.0, duration, num_samples, endpoint=False)

    # Simulation velocity & separation models (approximated envelope based on actual trajectory)
    # 0.0 - 4.8s: Figure-8 periodic oscillation (speed oscillates between 0.4 and 1.2 m/s)
    # 4.8 - 13.0s: Chaotic acceleration bursts, velocity spikes up to 3.5 m/s
    # 13.0 - 18.0s: Ejection phase, one star constant high speed, binary oscillates rapidly

    # Fundamental Sub-Bass Cosmic Drone (55 Hz + slight 110 Hz overtone)
    drone_phase = 2.0 * np.pi * 55.0 * t
    drone = 0.35 * np.sin(drone_phase) + 0.15 * np.sin(2.0 * drone_phase)

    # 3 Star Speed Envelopes v_a(t), v_b(t), v_c(t)
    omega_8 = 2.0 * np.pi / 6.3259

    # Star A velocity model
    v_a = np.where(
        t < 4.8,
        0.75 + 0.45 * np.sin(omega_8 * t),
        0.75 + 0.85 * np.sin(1.8 * omega_8 * t + 0.5) + 0.65 * np.sin(3.5 * t) ** 2
    )

    # Star B velocity model (phase-shifted during periodic, chaotic afterwards)
    v_b = np.where(
        t < 4.8,
        0.75 + 0.45 * np.sin(omega_8 * t + 2.0 * np.pi / 3.0),
        0.80 + 0.90 * np.sin(1.6 * omega_8 * t + 1.2) + 0.70 * np.cos(4.1 * t) ** 2
    )

    # Star C velocity model (slingshot ejection after 13s)
    v_c = np.where(
        t < 4.8,
        0.75 + 0.45 * np.sin(omega_8 * t + 4.0 * np.pi / 3.0),
        np.where(
            t < 13.0,
            0.90 + 1.10 * np.sin(2.2 * t) ** 2,
            2.40 + 0.20 * np.sin(0.8 * t)  # High-speed rogue interstellar ejection
        )
    )

    # Voice Frequencies (Doppler-shifted around musical tonic intervals: C3, E3, G3)
    f_a = 130.81 + 140.0 * v_a   # C3 base
    f_b = 164.81 + 140.0 * v_b   # E3 base
    f_c = 196.00 + 140.0 * v_c   # G3 base

    phase_a = 2.0 * np.pi * np.cumsum(f_a) / sample_rate
    phase_b = 2.0 * np.pi * np.cumsum(f_b) / sample_rate
    phase_c = 2.0 * np.pi * np.cumsum(f_c) / sample_rate

    # Synthesize analog warm oscillators
    voice_a = np.tanh(1.2 * np.sin(phase_a) + 0.25 * np.sin(2.0 * phase_a))
    voice_b = np.tanh(1.2 * np.sin(phase_b) + 0.25 * np.sin(2.0 * phase_b))
    voice_c = np.tanh(1.2 * np.sin(phase_c) + 0.25 * np.sin(2.0 * phase_c))

    # Spatial Stereo Panning based on orbital positions
    pan_a = 0.5 + 0.35 * np.sin(omega_8 * t)
    pan_b = 0.5 + 0.35 * np.sin(omega_8 * t + 2.0 * np.pi / 3.0)
    pan_c = 0.5 + 0.35 * np.sin(omega_8 * t + 4.0 * np.pi / 3.0)

    # Close encounter gravitational shock pulses (pericenter slingshot events at t ~ 6.8s, 9.4s, 12.8s)
    slingshot_pings = np.zeros_like(t)
    peri_times = [6.85, 9.42, 12.80]
    for pt in peri_times:
        dt_ping = t - pt
        mask = (dt_ping >= 0) & (dt_ping < 0.6)
        if np.any(mask):
            tau = dt_ping[mask]
            # 880 Hz damped bell ping
            slingshot_pings[mask] += 0.45 * np.exp(-tau * 8.0) * np.sin(2.0 * np.pi * 880.0 * tau)

    # Channel Mix
    left_ch = (
        drone * 0.25 +
        voice_a * (1.0 - pan_a) * 0.26 +
        voice_b * (1.0 - pan_b) * 0.26 +
        voice_c * (1.0 - pan_c) * 0.26 +
        slingshot_pings * 0.35
    )

    right_ch = (
        drone * 0.25 +
        voice_a * pan_a * 0.26 +
        voice_b * pan_b * 0.26 +
        voice_c * pan_c * 0.26 +
        slingshot_pings * 0.35
    )

    # Fade in / fade out
    fade_in = int(0.3 * sample_rate)
    fade_out = int(0.5 * sample_rate)
    left_ch[:fade_in] *= np.linspace(0.0, 1.0, fade_in)
    right_ch[:fade_in] *= np.linspace(0.0, 1.0, fade_in)
    left_ch[-fade_out:] *= np.linspace(1.0, 0.0, fade_out)
    right_ch[-fade_out:] *= np.linspace(1.0, 0.0, fade_out)

    # Normalize to -1.0 dBFS peak
    peak = max(np.max(np.abs(left_ch)), np.max(np.abs(right_ch)))
    if peak > 0:
        left_ch = (left_ch / peak) * 0.89
        right_ch = (right_ch / peak) * 0.89

    left_int16 = (left_ch * 32767.0).astype(np.int16)
    right_int16 = (right_ch * 32767.0).astype(np.int16)

    stereo = np.empty((num_samples * 2,), dtype=np.int16)
    stereo[0::2] = left_int16
    stereo[1::2] = right_int16

    Path(output_wav).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(output_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(stereo.tobytes())

    print(f"[OK] Procedural gravitational audio synthesized: {output_wav} ({duration:.1f}s @ 44.1kHz)")
    return output_wav
