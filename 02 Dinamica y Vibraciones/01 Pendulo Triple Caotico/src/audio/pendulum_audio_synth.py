"""
Continuum Lab — Friendly & Musical Chaotic Pendulum Audio Engine
Transforms chaotic dynamical trajectories into an enchanting, musical soundscape.
Replaces dark/spooky theremin dissonance with:
  1. Musical Pentatonic Chimes & Celesta notes mapped to instantaneous pendulum speed.
  2. Dynamic Cascades: Fast chaotic swings trigger sparkling, rapid harmonic arpeggios.
  3. Spatial Stereo Panning: Notes gently pan left and right tracking the physical bob position.
  4. Warm Ambient Harmonic Support (F-major / C-major uplifting foundation).
"""

import numpy as np
from scipy.io import wavfile
import os


def synthesize_pendulum_audio(
    time_points: np.ndarray,
    p3_trajectory: np.ndarray,
    velocities: np.ndarray,
    duration: float = 18.5,
    fs: int = 44100,
    output_path: str = "pendulum_audio_friendly.wav"
) -> str:
    num_samples = int(duration * fs)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    x3_interp = np.interp(t, time_points, p3_trajectory[:, 0])
    speed_interp = np.interp(t, time_points, velocities)

    # Normalize speed [0, 1]
    max_speed = np.max(speed_interp) + 1e-6
    speed_norm = speed_interp / max_speed

    # 1. Warm Ambient Base Pad (F major / C major soft harmonic bed)
    # Frequencies: F3 (174.61), C4 (261.63), A4 (440.00), C5 (523.25)
    pad_left = np.zeros(num_samples)
    pad_right = np.zeros(num_samples)
    pad_freqs = [174.61, 220.00, 261.63, 349.23, 440.00]
    for pf in pad_freqs:
        pad_left += 0.035 * np.sin(2 * np.pi * pf * t)
        pad_right += 0.035 * np.sin(2 * np.pi * pf * t + 0.5)

    # 2. Pentatonic Musical Scale for Reactive Chimes (F Major Pentatonic across 3 octaves)
    scale = [
        174.61, 196.00, 220.00, 261.63, 293.66,   # F3, G3, A3, C4, D4
        349.23, 392.00, 440.00, 523.25, 587.33,   # F4, G4, A4, C5, D5
        698.46, 783.99, 880.00, 1046.50, 1174.66  # F5, G5, A5, C6, D6
    ]
    num_notes = len(scale)

    # 3. Trigger Musical Notes at regular intervals modulated by chaotic speed
    # Interval between notes shrinks when pendulum moves fast (rhythmic cascades)
    chimes_left = np.zeros(num_samples)
    chimes_right = np.zeros(num_samples)

    current_sample = int(0.3 * fs)  # start shortly after intro
    while current_sample < num_samples - int(0.5 * fs):
        curr_t = current_sample / fs
        s_val = float(np.interp(curr_t, t, speed_norm))
        x_val = float(np.interp(curr_t, t, x3_interp))

        # Select note from scale based on speed (higher speed = higher register)
        note_idx = int(np.clip(s_val * (num_notes - 1), 0, num_notes - 1))
        # Add slight variation
        if np.random.rand() > 0.6 and note_idx > 0:
            note_idx -= 1
        freq = scale[note_idx]

        # Note duration & decay
        note_dur = 0.35 + 0.15 * (1.0 - s_val)
        n_samples = min(int(note_dur * fs), num_samples - current_sample)
        t_note = np.linspace(0, note_dur, n_samples, endpoint=False)

        # Gentle bell / celesta waveform: fundamental + soft 2nd harmonic + soft 3rd harmonic
        env = np.exp(-t_note / (0.08 + 0.12 * (1.0 - s_val)))
        note_wave = env * (
            0.18 * np.sin(2 * np.pi * freq * t_note) +
            0.08 * np.sin(2 * np.pi * (2 * freq) * t_note) +
            0.03 * np.sin(2 * np.pi * (3 * freq) * t_note)
        )

        # Spatial stereo panning based on x3 coordinate ([-2.5, 2.5] -> [0.1, 0.9])
        pan = np.clip((x_val + 2.5) / 5.0, 0.1, 0.9)
        gain_l = np.cos(pan * np.pi / 2.0)
        gain_r = np.sin(pan * np.pi / 2.0)

        chimes_left[current_sample:current_sample + n_samples] += note_wave * gain_l
        chimes_right[current_sample:current_sample + n_samples] += note_wave * gain_r

        # Time to next note: fast motions trigger rapid cascading arpeggios (50ms - 180ms)
        dt_next = 0.06 + 0.18 * (1.0 - s_val)**1.5
        current_sample += int(dt_next * fs)

    # 4. Soft melodic whistling glide following kinetic energy
    # Very gentle sine wave with vibrato for continuous motion perception
    f_continuous = 349.23 + 280.0 * (speed_norm**1.3)
    phase_cont = 2.0 * np.pi * np.cumsum(f_continuous) / fs
    continuous_glide = 0.035 * np.sin(phase_cont)

    # Combine channels
    audio_l = pad_left * 0.45 + chimes_left + continuous_glide * 0.5
    audio_r = pad_right * 0.45 + chimes_right + continuous_glide * 0.5

    # Master fade in and fade out
    fade_len = int(0.4 * fs)
    audio_l[:fade_len] *= np.linspace(0.0, 1.0, fade_len)
    audio_r[:fade_len] *= np.linspace(0.0, 1.0, fade_len)
    audio_l[-fade_len:] *= np.linspace(1.0, 0.0, fade_len)
    audio_r[-fade_len:] *= np.linspace(1.0, 0.0, fade_len)

    # Peak normalization to -1.5 dB
    peak = max(np.max(np.abs(audio_l)), np.max(np.abs(audio_r))) + 1e-6
    audio_l = (audio_l / peak) * 0.86
    audio_r = (audio_r / peak) * 0.86

    stereo_audio = np.stack([audio_l, audio_r], axis=1)
    stereo_int16 = (stereo_audio * 32767.0).astype(np.int16)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    wavfile.write(output_path, fs, stereo_int16)
    print(f"[CONTINUUM LAB] Friendly musical pendulum audio synthesized -> {output_path}")
    return output_path
