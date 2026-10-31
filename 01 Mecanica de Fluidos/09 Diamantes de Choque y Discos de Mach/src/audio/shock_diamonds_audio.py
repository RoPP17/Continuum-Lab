"""
Continuum Lab - Procedural Cinematic Audio Generator for Supersonic Shock Diamonds
Module: 01 Mecanica de Fluidos / 09 Diamantes de Choque y Discos de Mach
File: src/audio/shock_diamonds_audio.py

Generates 44.1 kHz 16-bit stereo master soundtrack:
  - Deep Rocket Combustion Sub-bass Drone (38 - 55 Hz) with 2nd/3rd harmonics
  - Supersonic Turbulent Shear Noise (bandpassed colored noise)
  - Powell Screech Tone (Acoustic feedback loop between nozzle lip & shock diamonds)
  - Resonant Mach Disk Celesta / Crystalline Chimes
  - Seamless 16.0s loop envelope
"""

import os
import math
import numpy as np
from scipy.io import wavfile


def generate_shock_diamonds_audio(
    output_wav: str,
    duration: float = 16.0,
    sample_rate: int = 44100
) -> str:
    os.makedirs(os.path.dirname(output_wav), exist_ok=True)
    n_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    # 1. Rocket Combustion Sub-Bass Drone (38 Hz -> 48 Hz breathing)
    f_sub = 42.0 + 4.0 * np.sin(2.0 * np.pi * t / duration)
    phase_sub = 2.0 * np.pi * np.cumsum(f_sub) / sample_rate
    sub_drone = (
        0.55 * np.sin(phase_sub) +
        0.28 * np.sin(2.0 * phase_sub) +
        0.14 * np.sin(3.0 * phase_sub)
    )
    # Warm soft-clipping saturation
    sub_drone = np.tanh(sub_drone * 1.5) * 0.40

    # 2. Supersonic Jet Shear Noise (Turbulent mixing layer)
    rng = np.random.default_rng(42)
    white_noise = rng.standard_normal(n_samples)
    # Simple IIR lowpass/bandpass smoothing for pink-like rumble
    b_noise = np.zeros(n_samples)
    alpha = 0.08
    for i in range(1, n_samples):
        b_noise[i] = alpha * white_noise[i] + (1.0 - alpha) * b_noise[i - 1]

    # Modulate noise amplitude with jet breathing
    noise_env = 0.28 + 0.08 * np.sin(2.0 * np.pi * t / duration)
    shear_noise_L = b_noise * noise_env
    shear_noise_R = np.roll(b_noise, int(0.002 * sample_rate)) * noise_env

    # 3. Screech Tones (Acoustic feedback loop between shock diamonds & nozzle lip)
    # Screech frequency typically 1,200 - 1,800 Hz
    f_screech = 1420.0 + 120.0 * np.sin(2.0 * np.pi * t / duration)
    phase_screech = 2.0 * np.pi * np.cumsum(f_screech) / sample_rate
    screech = 0.06 * np.sin(phase_screech) + 0.03 * np.sin(2.0 * phase_screech)

    # 4. Mach Disk Incandescent Chimes / Celesta Resonance
    # Trigger subtle crystalline accents at peak compression phases
    chimes_L = np.zeros(n_samples)
    chimes_R = np.zeros(n_samples)
    accent_times = [1.2, 4.0, 7.5, 9.8, 12.4, 14.8]
    accent_freqs = [880.0, 1046.5, 1318.5, 1567.9, 1174.6, 987.7]  # Pentatonic celestial scale

    for at, f_chime in zip(accent_times, accent_freqs):
        start_idx = int(at * sample_rate)
        decay_samples = int(1.4 * sample_rate)
        if start_idx + decay_samples < n_samples:
            t_decay = np.linspace(0, 1.4, decay_samples)
            env_chime = np.exp(-t_decay * 3.5) * np.sin(2.0 * np.pi * f_chime * t_decay)
            pan = 0.5 + 0.3 * np.sin(at * 2.0)
            chimes_L[start_idx:start_idx + decay_samples] += env_chime * pan * 0.15
            chimes_R[start_idx:start_idx + decay_samples] += env_chime * (1.0 - pan) * 0.15

    # Master mix
    left = sub_drone + shear_noise_L + screech * 0.85 + chimes_L
    right = sub_drone + shear_noise_R + screech * 1.05 + chimes_R

    # Loop fade-in / fade-out (0.08s smooth window for clicks elimination)
    fade_len = int(0.08 * sample_rate)
    fade_in = 0.5 * (1.0 - np.cos(np.pi * np.linspace(0, 1, fade_len)))
    fade_out = 0.5 * (1.0 + np.cos(np.pi * np.linspace(0, 1, fade_len)))

    left[:fade_len] *= fade_in
    right[:fade_len] *= fade_in
    left[-fade_len:] *= fade_out
    right[-fade_len:] *= fade_out

    # Normalize to -1.0 dB
    peak = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-4)
    target = 0.88
    left = left * (target / peak)
    right = right * (target / peak)

    audio_stereo = np.column_stack((left, right))
    audio_int16 = (audio_stereo * 32767.0).astype(np.int16)

    wavfile.write(output_wav, sample_rate, audio_int16)
    print(f"[OK] Master audio successfully generated: {output_wav}")
    return output_wav


if __name__ == "__main__":
    test_wav = r"C:\Users\andre\OneDrive\Desktop\Continuum Lab\RENDERS\25 Diamantes de Choque y Discos de Mach Aerodinamicos\extra\audio\shock_diamonds_cinematic_audio.wav"
    generate_shock_diamonds_audio(test_wav)
