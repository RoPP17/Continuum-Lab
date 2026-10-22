"""
Continuum Lab - Procedural Audio Synthesizer for Magnus Effect & Flettner Rotor
Module: 01 Mecanica de Fluidos / 05 Efecto Magnus y Rotor Flettner
File: src/audio/magnus_audio.py

Synthesizes a 44.1 kHz stereo cinematic science soundtrack:
  - Aerodynamic wind rush (turbulent filtered noise)
  - Rotor rotational hum & electric motor whine scaling with spin ratio alpha(t)
  - Bernoulli low-frequency suction pulse scaling with lift force L'(t)
  - Stagnation point bifurcation chime (crystalline celesta chord at alpha = 2.0)
"""

import os
import wave
import struct
import numpy as np


def synthesize_magnus_soundtrack(output_wav: str, duration: float = 18.0, sample_rate: int = 44100):
    total_samples = int(duration * sample_rate)
    t = np.linspace(0.0, duration, total_samples, endpoint=False)

    # 1. Spin Ratio alpha(t) profile matching simulation
    alpha = np.zeros_like(t)
    mask1 = (t > 3.0) & (t <= 8.0)
    tau1 = (t[mask1] - 3.0) / 5.0
    alpha[mask1] = 1.6 * (3.0 * tau1**2 - 2.0 * tau1**3)

    mask2 = (t > 8.0) & (t <= 12.0)
    tau2 = (t[mask2] - 8.0) / 4.0
    alpha[mask2] = 1.6 + (2.4 - 1.6) * (3.0 * tau2**2 - 2.0 * tau2**3)

    mask3 = t > 12.0
    tau3 = np.clip((t[mask3] - 12.0) / 6.0, 0.0, 1.0)
    alpha[mask3] = 2.4 + (3.6 - 2.4) * (3.0 * tau3**2 - 2.0 * tau3**3)

    # 2. Aerodynamic Wind Rush (Filtered White/Pink Noise)
    rng = np.random.default_rng(2026)
    raw_noise = rng.normal(0.0, 0.35, total_samples)
    # Simple low-pass filter
    wind_left = np.zeros(total_samples)
    wind_right = np.zeros(total_samples)
    alpha_filter = 0.04
    for i in range(1, total_samples):
        wind_left[i] = wind_left[i - 1] + alpha_filter * (raw_noise[i] - wind_left[i - 1])
    # Gentle stereo variation
    wind_right = np.roll(wind_left, 120) * 0.95 + raw_noise * 0.02
    # Wind volume envelope: ambient base + slight swell with alpha
    wind_env = 0.18 + 0.12 * (alpha / 3.6)
    wind_left *= wind_env
    wind_right *= wind_env

    # 3. Rotor Motor Whine (Harmonic Electric Sine with Frequency proportional to alpha)
    # Base frequency: 90 Hz -> up to 380 Hz at alpha=3.6
    rotor_freq = 95.0 + 78.0 * alpha
    phase = 2.0 * np.pi * np.cumsum(rotor_freq) / sample_rate
    rotor_harm1 = np.sin(phase)
    rotor_harm2 = 0.35 * np.sin(2.0 * phase)
    rotor_harm3 = 0.15 * np.sin(3.0 * phase)
    rotor_sub = 0.40 * np.sin(0.5 * phase)

    rotor_tone = rotor_harm1 + rotor_harm2 + rotor_harm3 + rotor_sub
    # Rotor volume ramps up smoothly as rotor spins
    rotor_amp = np.clip(alpha / 3.0, 0.0, 1.0) * 0.22
    # Slight stereo panning modulation based on rotation
    pan_mod = 0.5 + 0.15 * np.sin(phase * 0.05)
    rotor_l = rotor_tone * rotor_amp * pan_mod
    rotor_r = rotor_tone * rotor_amp * (1.0 - pan_mod)

    # 4. Bernoulli Low-Frequency Suction Pulse (Deep Bass drone at 55 Hz / A1)
    bass_freq = 55.0
    bass_phase = 2.0 * np.pi * bass_freq * t
    bass_pulse = (np.sin(bass_phase) + 0.3 * np.sin(2.0 * bass_phase)) * (0.05 + 0.25 * (alpha / 3.6)**1.5)
    bass_l = bass_pulse * 0.9
    bass_r = bass_pulse * 0.9

    # 5. Stagnation Point Bifurcation Chimes (at t ~ 10.0s when alpha crosses 2.0)
    # Harmonic chords: D4 (293.7 Hz), F4 (349.2 Hz), A4 (440.0 Hz), C5 (523.3 Hz), D5 (587.3 Hz)
    bell_l = np.zeros(total_samples)
    bell_r = np.zeros(total_samples)
    
    t_chime = 9.8  # Critical bifurcation moment
    idx_start = int(t_chime * sample_rate)
    chime_len = int(5.5 * sample_rate)
    if idx_start < total_samples:
        n_pts = min(chime_len, total_samples - idx_start)
        t_loc = np.linspace(0.0, n_pts / sample_rate, n_pts, endpoint=False)
        envelope = np.exp(-t_loc / 1.4)

        chord_freqs = [293.66, 349.23, 440.00, 523.25, 587.33]
        for idx, f in enumerate(chord_freqs):
            weight = 0.22 / (idx + 1)**0.5
            chime_wave = np.sin(2.0 * np.pi * f * t_loc) * envelope * weight
            pan_val = 0.3 + 0.4 * (idx / len(chord_freqs))
            bell_l[idx_start:idx_start + n_pts] += chime_wave * pan_val
            bell_r[idx_start:idx_start + n_pts] += chime_wave * (1.0 - pan_val)

    # 6. Master Mix and Soft Clipping
    master_l = wind_left + rotor_l + bass_l + bell_l
    master_r = wind_right + rotor_r + bass_r + bell_r

    # Fade in (first 0.8s) and fade out (last 1.0s)
    fade_in = np.clip(t / 0.8, 0.0, 1.0)
    fade_out = np.clip((duration - t) / 1.0, 0.0, 1.0)
    fade_envelope = fade_in * fade_out

    master_l *= fade_envelope
    master_r *= fade_envelope

    # Soft tanh saturation limiter to avoid harsh digital clipping
    master_l = np.tanh(master_l * 1.8) * 0.88
    master_r = np.tanh(master_r * 1.8) * 0.88

    # Convert to 16-bit PCM WAV
    int_l = (master_l * 32767).astype(np.int16)
    int_r = (master_r * 32767).astype(np.int16)

    # Interleave stereo channels
    stereo_interleaved = np.empty((total_samples * 2,), dtype=np.int16)
    stereo_interleaved[0::2] = int_l
    stereo_interleaved[1::2] = int_r

    out_dir = os.path.dirname(output_wav)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with wave.open(output_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(stereo_interleaved.tobytes())

    return output_wav
