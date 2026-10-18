"""
Continuum Lab - Procedural Acoustic Synthesis for Chladni Plate Cymatics
Module: 03 Mecanica de Solidos / 01 Placas de Chladni y Resonancia Acustica
File: src/audio/chladni_audio.py

Synthesizes 44.1 kHz 16-bit stereo PCM soundtrack:
  - Swept acoustic carrier matching exact modal frequencies:
      432 Hz -> 880 Hz -> 1420 Hz -> 2150 Hz -> 2860 Hz -> 4320 Hz
  - Warm mechanical plate resonance with harmonic saturation (tanh drive)
  - Granular silica sand friction & impact scattering noise (15,000 grains)
  - Seamless spatial stereo panning
"""

import wave
from pathlib import Path
import numpy as np


def synthesize_chladni_soundtrack(output_wav: str, duration: float = 18.0, sample_rate: int = 44100):
    num_samples = int(duration * sample_rate)
    t = np.linspace(0.0, duration, num_samples, endpoint=False)

    # 1. Frequency trajectory f(t) corresponding to simulation schedule
    # 0.0 - 3.8s: 432 Hz
    # 3.8 - 4.8s: chirp 432 -> 1420 Hz
    # 4.8 - 9.2s: 1420 Hz
    # 9.2 - 10.2s: chirp 1420 -> 2860 Hz
    # 10.2 - 14.2s: 2860 Hz
    # 14.2 - 15.0s: chirp 2860 -> 4320 Hz
    # 15.0 - 18.0s: 4320 Hz
    freq = np.zeros_like(t)

    regimes = [
        (0.0, 3.8, 432.0, 432.0),
        (3.8, 4.8, 432.0, 1420.0),
        (4.8, 9.2, 1420.0, 1420.0),
        (9.2, 10.2, 1420.0, 2860.0),
        (10.2, 14.2, 2860.0, 2860.0),
        (14.2, 15.0, 2860.0, 4320.0),
        (15.0, 18.0, 4320.0, 4320.0),
    ]

    for t0, t1, f0, f1 in regimes:
        mask = (t >= t0) & (t < t1)
        if np.any(mask):
            sub_t = t[mask]
            tau = (sub_t - t0) / (t1 - t0)
            # Smooth cosine interpolation for chirp transitions
            tau_smooth = 0.5 * (1.0 - np.cos(np.pi * tau))
            freq[mask] = (1.0 - tau_smooth) * f0 + tau_smooth * f1

    # End boundary
    freq[t >= 18.0] = 4320.0

    # 2. Integrate instantaneous phase phi(t) = 2*pi * integral(f(tau) dtau)
    phase = 2.0 * np.pi * np.cumsum(freq) / sample_rate

    # 3. Fundamental modal tone with harmonic plate overtones
    fundamental = np.sin(phase)
    second_harmonic = 0.28 * np.sin(2.0 * phase + 0.35)
    third_harmonic = 0.12 * np.sin(3.0 * phase + 0.70)
    subharmonic = 0.15 * np.sin(0.5 * phase)

    plate_raw = fundamental + second_harmonic + third_harmonic + subharmonic
    # Warm analog saturation
    plate_saturated = np.tanh(1.35 * plate_raw)

    # 4. Granular sand scattering noise (excited during frequency shifts)
    # Granular excitation intensity is proportional to |df/dt| + base level
    df_dt = np.abs(np.gradient(freq, t))
    granular_envelope = 0.08 + 0.35 * np.clip(df_dt / 1000.0, 0.0, 1.0)

    # Multi-band granular friction noise
    rng = np.random.default_rng(123)
    white_noise = rng.normal(0.0, 1.0, num_samples)

    # High-pass acoustic filter approximation for sand grain impacts
    # Difference filter: y[n] = x[n] - 0.85*x[n-1]
    sand_hiss = np.zeros_like(white_noise)
    sand_hiss[1:] = white_noise[1:] - 0.82 * white_noise[:-1]

    # Modulate sand with random micro-bursts (individual grain bouncing)
    micro_clicks = (rng.uniform(0.0, 1.0, num_samples) > 0.985).astype(float) * rng.normal(0.0, 1.0, num_samples)
    granular_audio = (sand_hiss * 0.7 + micro_clicks * 0.3) * granular_envelope

    # 5. Master Mix & Spatial Stereo Panning
    # Left channel has slight phase offset and pan drift
    pan_l = 0.5 + 0.25 * np.sin(2.0 * np.pi * 0.35 * t)
    pan_r = 1.0 - pan_l

    left_ch = (plate_saturated * 0.72 + granular_audio * 0.28) * (0.8 + 0.2 * pan_l)
    right_ch = (plate_saturated * 0.72 + granular_audio * 0.28) * (0.8 + 0.2 * pan_r)

    # Overall Fade-in (0.25s) and Fade-out (0.4s) to prevent speaker pops
    fade_in_len = int(0.25 * sample_rate)
    fade_out_len = int(0.40 * sample_rate)
    left_ch[:fade_in_len] *= np.linspace(0.0, 1.0, fade_in_len)
    right_ch[:fade_in_len] *= np.linspace(0.0, 1.0, fade_in_len)
    left_ch[-fade_out_len:] *= np.linspace(1.0, 0.0, fade_out_len)
    right_ch[-fade_out_len:] *= np.linspace(1.0, 0.0, fade_out_len)

    # Normalize to -1.2 dBFS peak
    peak = max(np.max(np.abs(left_ch)), np.max(np.abs(right_ch)))
    if peak > 0:
        left_ch = (left_ch / peak) * 0.88
        right_ch = (right_ch / peak) * 0.88

    # Convert to 16-bit signed PCM
    left_int16 = (left_ch * 32767.0).astype(np.int16)
    right_int16 = (right_ch * 32767.0).astype(np.int16)

    # Interleave stereo
    stereo = np.empty((num_samples * 2,), dtype=np.int16)
    stereo[0::2] = left_int16
    stereo[1::2] = right_int16

    Path(output_wav).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(output_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(stereo.tobytes())

    print(f"[OK] Procedural stereo audio synthesized: {output_wav} ({duration:.1f}s @ 44.1kHz)")
    return output_wav
