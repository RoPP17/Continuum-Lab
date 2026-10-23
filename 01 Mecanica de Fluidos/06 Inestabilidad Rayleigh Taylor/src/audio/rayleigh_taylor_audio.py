"""
Continuum Lab - Procedural Audio Synthesizer for Rayleigh-Taylor Instability
Module: 01 Mecanica de Fluidos / 06 Inestabilidad Rayleigh Taylor
File: src/audio/rayleigh_taylor_audio.py

Synthesizes a 44.1 kHz 16-bit stereo cinematic science soundtrack:
  - Deep gravitational potential sub-bass drone (42 Hz - 55 Hz)
  - Hydrodynamic interfacial rush (pink noise swell scaling with mixing kinetic energy)
  - Mushroom plume roll-up celesta chimes (crystalline harmonic bells at t ~ 8-12s)
  - Turbulent bubble cascade & granular particle drops
"""

import os
import wave
import struct
import numpy as np


def synthesize_rayleigh_taylor_soundtrack(
    output_wav: str,
    duration: float = 16.0,
    sample_rate: int = 44100
) -> str:
    """Generates a complete 44.1 kHz stereo soundtrack matching the RT simulation dynamics."""
    total_samples = int(duration * sample_rate)
    t = np.linspace(0.0, duration, total_samples, endpoint=False)

    # 1. Physical Evolution Scaling Envelope
    # Kinetic energy scales as ~ t^3 in self-similar mixing
    tau = np.clip(t / duration, 0.0, 1.0)
    kinetic_env = 0.15 + 0.85 * (tau ** 2.2)

    # 2. Deep Gravitational Sub-Bass Drone (44 Hz / F0 - 55 Hz / A1)
    bass_freq = 44.0 + 8.0 * (tau ** 1.5)
    bass_phase = 2.0 * np.pi * np.cumsum(bass_freq) / sample_rate
    bass_harm1 = np.sin(bass_phase)
    bass_harm2 = 0.35 * np.sin(2.0 * bass_phase)
    bass_harm3 = 0.15 * np.sin(3.0 * bass_phase)
    bass_sub = 0.40 * np.sin(0.5 * bass_phase)

    bass_pulse = (bass_harm1 + bass_harm2 + bass_harm3 + bass_sub) * (0.12 + 0.18 * kinetic_env)
    bass_l = bass_pulse * 0.95
    bass_r = bass_pulse * 0.95

    # 3. Hydrodynamic Interfacial Rush (Stereo Filtered Pink Noise)
    rng = np.random.default_rng(2026)
    raw_noise = rng.normal(0.0, 0.30, total_samples)

    # Low-pass filter for smooth rushing fluid sound
    alpha_filter = 0.035
    fluid_left = np.zeros(total_samples)
    for i in range(1, total_samples):
        fluid_left[i] = fluid_left[i - 1] + alpha_filter * (raw_noise[i] - fluid_left[i - 1])

    fluid_right = np.roll(fluid_left, 160) * 0.92 + raw_noise * 0.02
    fluid_env = 0.10 + 0.22 * kinetic_env
    fluid_left *= fluid_env
    fluid_right *= fluid_env

    # 4. Secondary Kelvin-Helmholtz Mushroom Plume Celesta Chimes
    # Harmonic notes: D4 (293.7 Hz), F4 (349.2 Hz), A4 (440.0 Hz), C5 (523.3 Hz), D5 (587.3 Hz), F5 (698.5 Hz)
    chime_times = [7.5, 8.2, 9.0, 9.8, 10.6, 11.4, 12.2]
    chime_freqs = [293.66, 349.23, 440.00, 523.25, 587.33, 698.46, 880.00]
    chimes_l = np.zeros(total_samples)
    chimes_r = np.zeros(total_samples)

    for ct, cf in zip(chime_times, chime_freqs):
        dt_c = t - ct
        mask = dt_c >= 0.0
        if np.any(mask):
            decay = np.exp(-dt_c[mask] * 3.2)
            osc = np.sin(2.0 * np.pi * cf * dt_c[mask]) + 0.25 * np.sin(4.0 * np.pi * cf * dt_c[mask])
            pan = 0.3 + 0.4 * np.sin(cf * 0.1)
            chimes_l[mask] += osc * decay * 0.14 * pan
            chimes_r[mask] += osc * decay * 0.14 * (1.0 - pan)

    # 5. Granular Bubble / Plume Cascade (Micro-droplet resonance clicks)
    cascade_l = np.zeros(total_samples)
    cascade_r = np.zeros(total_samples)
    for step_sec in np.linspace(6.0, 15.5, 38):
        dt_p = t - step_sec
        mask_p = (dt_p >= 0.0) & (dt_p < 0.15)
        if np.any(mask_p):
            p_freq = rng.uniform(550.0, 1400.0)
            p_decay = np.exp(-dt_p[mask_p] * 35.0)
            p_osc = np.sin(2.0 * np.pi * p_freq * dt_p[mask_p])
            p_pan = rng.uniform(0.1, 0.9)
            cascade_l[mask_p] += p_osc * p_decay * 0.05 * p_pan
            cascade_r[mask_p] += p_osc * p_decay * 0.05 * (1.0 - p_pan)

    # Master Sum
    mix_left = bass_l + fluid_left + chimes_l + cascade_l
    mix_right = bass_r + fluid_right + chimes_r + cascade_r

    # Master Envelope (0.5s fade in, 0.5s fade out)
    fade_in_len = int(0.5 * sample_rate)
    fade_out_len = int(0.5 * sample_rate)
    fade_in = np.sin(np.linspace(0.0, np.pi / 2.0, fade_in_len))
    fade_out = np.cos(np.linspace(0.0, np.pi / 2.0, fade_out_len))

    mix_left[:fade_in_len] *= fade_in
    mix_right[:fade_in_len] *= fade_in
    mix_left[-fade_out_len:] *= fade_out
    mix_right[-fade_out_len:] *= fade_out

    # Peak Normalization to -1.0 dBFS (0.89 amplitude)
    max_peak = max(np.max(np.abs(mix_left)), np.max(np.abs(mix_right)), 1e-6)
    norm_factor = 0.88 / max_peak
    mix_left = np.clip(mix_left * norm_factor, -0.99, 0.99)
    mix_right = np.clip(mix_right * norm_factor, -0.99, 0.99)

    # Quantize to 16-bit PCM
    samples_l = (mix_left * 32767).astype(np.int16)
    samples_r = (mix_right * 32767).astype(np.int16)

    interleaved = np.empty((total_samples * 2,), dtype=np.int16)
    interleaved[0::2] = samples_l
    interleaved[1::2] = samples_r

    os.makedirs(os.path.dirname(output_wav), exist_ok=True)
    with wave.open(output_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(interleaved.tobytes())

    return output_wav
