"""
Procedural Audio Synthesis Engine — Brachistochrone Race
Module: 06 Matematicas y Geometria / 03 Curva Braquistocrona

Acoustic Architecture:
  1. Ambient Scientific Pad: Clean harmonic atmosphere grounding the exposition.
  2. Countdown Beeps & Release: Mechanical latch release at t = 3.0s.
  3. Rolling Gravity Whoosh: Accelerating frequency slide as spheres gain kinetic velocity (t = 3.0s to 7.8s).
  4. Arrival Impact & Chimes:
     - 1st Cycloid Victory Chime @ t = 6.9s (C6, 1046.5 Hz)
     - 2nd Circle @ t = 7.1s (A5, 880.0 Hz)
     - 3rd Parabola @ t = 7.3s (G5, 784.0 Hz)
     - 4th Straight Line @ t = 7.8s (Low thud, 440 Hz)
  5. Scientific Resolution & Leaderboard Theme (t = 8.0s to 14.5s): Warm harmonic synthesizer.
"""

import numpy as np
from scipy.io import wavfile
from pathlib import Path


def synthesize_brachistochrone_audio(
    duration: float = 14.5,
    fs: int = 44100,
    output_path: str = "brachistochrone_audio.wav"
) -> str:
    n_samples = int(duration * fs)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    # 1. Harmonic Ambient Drone (A minor / Cybernetic Neon Pad)
    pad = (
        0.18 * np.sin(2.0 * np.pi * 110.0 * t) +
        0.12 * np.sin(2.0 * np.pi * 165.0 * t) +
        0.08 * np.sin(2.0 * np.pi * 261.63 * t) +
        0.04 * np.sin(2.0 * np.pi * 329.63 * t)
    )
    pad *= 0.7 + 0.3 * np.sin(2.0 * np.pi * 0.35 * t)

    sfx = np.zeros(n_samples)

    def add_tone(t_start, dur, freq, amp):
        idx_start = int(t_start * fs)
        idx_end = min(idx_start + int(dur * fs), n_samples)
        if idx_start < n_samples:
            dt = t[idx_start:idx_end] - t_start
            envelope = np.exp(-dt * 18.0)
            sfx[idx_start:idx_end] += amp * np.sin(2.0 * np.pi * freq * dt) * envelope

    # Countdown beeps (t = 2.2s, 2.5s, 2.8s) and Release Clack (t = 3.0s)
    add_tone(2.2, 0.12, 587.33, 0.20)
    add_tone(2.5, 0.12, 659.25, 0.25)
    add_tone(2.8, 0.15, 880.00, 0.35)
    # Mechanical Release Clack at 3.0s
    add_tone(3.0, 0.25, 440.0, 0.55)
    add_tone(3.0, 0.08, 1760.0, 0.35)

    # 2. Rolling Acceleration Whoosh (t = 3.0s to 7.8s)
    t_race = np.clip(t - 3.0, 0.0, 4.8)
    race_mask = (t >= 3.0) & (t <= 8.0)
    v_freq = 140.0 + 380.0 * (t_race / 4.8) ** 1.6
    phase_v = 2.0 * np.pi * np.cumsum(v_freq) / fs
    whoosh = 0.24 * np.sin(phase_v) * race_mask * (t_race / 4.8)

    # 3. Resonant Bells at Finish Line Crossings
    def add_bell(t_start, freq, amp):
        idx_start = int(t_start * fs)
        dur = 2.5
        idx_end = min(idx_start + int(dur * fs), n_samples)
        if idx_start < n_samples:
            dt = t[idx_start:idx_end] - t_start
            env = np.exp(-dt * 3.2)
            bell = (
                np.sin(2.0 * np.pi * freq * dt) +
                0.5 * np.sin(2.0 * np.pi * freq * 2.0 * dt) +
                0.25 * np.sin(2.0 * np.pi * freq * 3.01 * dt)
            )
            sfx[idx_start:idx_end] += amp * bell * env

    # 1st Place: Cycloid Bell (Golden high chime @ 1046.5 Hz - C6) at t = 6.9s
    add_bell(6.9, 1046.5, 0.70)
    # 2nd Place: Circle (880 Hz - A5) at t = 7.1s
    add_bell(7.1, 880.0, 0.32)
    # 3rd Place: Parabola (784 Hz - G5) at t = 7.3s
    add_bell(7.3, 783.99, 0.26)
    # 4th Place: Straight line (Low finish @ 440 Hz - A4) at t = 7.8s
    add_bell(7.8, 440.0, 0.35)

    # 4. Scientific Resolution Theme (t = 8.0s to 14.5s)
    t_res = t - 8.0
    res_mask = np.clip((t - 8.0) / 0.5, 0.0, 1.0) * (t >= 8.0)
    # Warm chords: F maj (174.6 Hz, 220 Hz, 261.6 Hz) -> C maj (130.8 Hz, 164.8 Hz, 196 Hz)
    chord_f = 0.14 * (np.sin(2.0 * np.pi * 174.61 * t) + np.sin(2.0 * np.pi * 220.0 * t) + np.sin(2.0 * np.pi * 261.63 * t))
    chord_c = 0.14 * (np.sin(2.0 * np.pi * 130.81 * t) + np.sin(2.0 * np.pi * 164.81 * t) + np.sin(2.0 * np.pi * 196.0 * t))
    switch = np.clip((t - 11.5) / 0.8, 0.0, 1.0)
    resolution_theme = ((1.0 - switch) * chord_f + switch * chord_c) * res_mask

    # 5. Master Mix
    audio = pad * 0.30 + sfx + whoosh + resolution_theme

    # Master envelope
    fade_in = np.clip(t / 0.4, 0.0, 1.0)
    fade_out = np.clip((duration - t) / 0.8, 0.0, 1.0)
    audio = audio * fade_in * fade_out

    # Normalize to -1.0 dB
    peak = np.max(np.abs(audio)) + 1e-8
    audio = (audio / peak) * 0.88

    audio_int16 = (audio * 32767.0).astype(np.int16)
    stereo = np.column_stack((audio_int16, audio_int16))

    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(str(out_file), fs, stereo)
    return str(out_file)

