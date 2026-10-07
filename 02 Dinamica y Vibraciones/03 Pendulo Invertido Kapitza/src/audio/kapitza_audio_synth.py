"""
Continuum Lab — Procedural Audio Engine
Module: 02 Dinamica y Vibraciones / 03 Pendulo Invertido Kapitza
Cinematic Musical & Acoustic Design:
  1. Ambient Polyphonic Musical Pad: D-minor cinematic harmonic bed with rich synth chords
  2. Melodic Celesta / Bell Arpeggios: D-minor pentatonic motifs reflecting dynamic stability
  3. High-Frequency Motor Hum & Shaker Table Carrier (55 Hz harmonic buzz)
  4. Sub-Bass Hydraulic Ground Rumble
  5. External Perturbation Strike at t = 4.0s (punchy transient + acoustic resonance)
  6. Emergency Motor Shutdown at t = 8.0s (power relay snap + servo pitch dive)
  7. Gravitational Swing Whooshes as pendulum tumbles down at t = 8.3s - 15.0s
  8. Master Stereo Spatialization and Warm Limiting
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
from pathlib import Path


def butter_bandpass(lowcut: float, highcut: float, fs: int, order: int = 2):
    nyq = 0.5 * fs
    low = max(lowcut / nyq, 0.0005)
    high = min(highcut / nyq, 0.9990)
    b, a = butter(order, [low, high], btype='band')
    return b, a


def bandpass_filter(data: np.ndarray, lowcut: float, highcut: float, fs: int, order: int = 2) -> np.ndarray:
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    return lfilter(b, a, data)


def synthesize_kapitza_audio(
    duration: float = 15.0,
    fs: int = 44100,
    output_path: str = "kapitza_audio.wav"
) -> str:
    """
    Synthesizes the complete procedural soundscape (melody + SFX) for Kapitza's Pendulum.
    """
    num_samples = int(duration * fs)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    # =========================================================================
    # PART 1: CINEMATIC MELODIC SCORE & HARMONIC AMBIENCE
    # =========================================================================
    # Chord frequencies:
    # 0.0s - 4.0s (Phase 1): Dm (D3 146.83, F3 174.61, A3 220.00, C4 261.63, E4 329.63)
    # 4.0s - 8.0s (Phase 2): Bbmaj7 / Gm7 (Bb2 116.54, D3 146.83, F3 174.61, A3 220.00)
    # 8.0s - 15.0s (Phase 3): Dm low descending to resolve (D2 73.42, A2 110.00, D3 146.83, F3 174.61)

    pad_left = np.zeros(num_samples)
    pad_right = np.zeros(num_samples)

    chord_phases = [
        # (t_start, t_end, [freqs], gain)
        (0.0, 4.2, [146.83, 220.00, 261.63, 329.63], 0.08),     # Dm9
        (3.8, 8.2, [116.54, 174.61, 220.00, 293.66], 0.09),     # Bbmaj9 / tension
        (7.8, 15.0, [73.42, 110.00, 146.83, 174.61], 0.09),     # Dm deep descent
    ]

    for t_s, t_e, freqs, gain in chord_phases:
        env = np.clip((t - t_s) / 0.8, 0.0, 1.0) * np.clip((t_e - t) / 0.8, 0.0, 1.0)
        for i, f in enumerate(freqs):
            # Rich sawtooth/sine warm hybrid
            tone_l = 0.65 * np.sin(2.0 * np.pi * f * t) + 0.20 * np.sin(4.0 * np.pi * f * t)
            tone_r = 0.65 * np.sin(2.0 * np.pi * f * t + 0.45 * (i + 1)) + 0.20 * np.sin(4.0 * np.pi * f * t + 0.8)
            pad_left += gain * env * tone_l
            pad_right += gain * env * tone_r

    # Melodic Celesta / Glass Bells Motif (Pentatonic D-minor: D4, F4, G4, A4, C5, D5, F5, A5)
    bell_scale = [293.66, 349.23, 392.00, 440.00, 523.25, 587.33, 698.46, 880.00]
    # Melody timeline: (timestamp, note_index, volume)
    melody_events = [
        # Phase 1: Majestic steady ascent
        (0.4, 0, 0.18), (0.9, 2, 0.19), (1.4, 3, 0.21), (2.0, 5, 0.24), (2.6, 4, 0.20), (3.2, 5, 0.25),
        # Phase 2: Tense quick arpeggios after impact
        (4.1, 7, 0.30), (4.5, 5, 0.26), (5.0, 6, 0.28), (5.5, 4, 0.24), (6.1, 3, 0.22), (6.8, 5, 0.24), (7.4, 4, 0.22),
        # Phase 3: Fading melancholic drops
        (8.5, 5, 0.20), (9.2, 3, 0.16), (10.1, 1, 0.14), (11.5, 0, 0.12), (13.0, 0, 0.08)
    ]

    mel_left = np.zeros(num_samples)
    mel_right = np.zeros(num_samples)

    for note_t, note_idx, note_vol in melody_events:
        idx_start = int(note_t * fs)
        note_freq = bell_scale[note_idx % len(bell_scale)]
        note_dur = 1.2
        n_note = min(int(note_dur * fs), num_samples - idx_start)
        if n_note <= 0:
            continue
        tn = np.linspace(0, note_dur, n_note, endpoint=False)
        # Bell envelope (fast attack, exponential decay)
        note_env = np.exp(-tn / 0.35)
        # Add harmonic overtones (fundamental + octaves + 3rd harmonic)
        wave = note_env * (
            0.60 * np.sin(2.0 * np.pi * note_freq * tn)
            + 0.25 * np.sin(4.0 * np.pi * note_freq * tn)
            + 0.15 * np.sin(6.0 * np.pi * note_freq * tn)
        )
        # Stereo pan based on note pitch (higher notes pan slightly right)
        pan = 0.5 + 0.35 * (note_idx / (len(bell_scale) - 1) - 0.5)
        mel_left[idx_start:idx_start + n_note] += note_vol * (1.0 - pan) * wave
        mel_right[idx_start:idx_start + n_note] += note_vol * pan * wave

    # =========================================================================
    # PART 2: MECHANICAL & PHYSICAL SOUND EFFECTS (SFX)
    # =========================================================================

    # 1. High-frequency 55 Hz Shaker Motor Carrier with Rich Harmonics (active t <= 8.0s)
    motor_active = np.clip((8.0 - t) / 0.15, 0.0, 1.0)
    # Fundamental 55 Hz + 110 Hz + 220 Hz + 330 Hz + 440 Hz
    buzz_55 = 0.30 * np.sin(2.0 * np.pi * 55.0 * t)
    buzz_110 = 0.20 * np.sin(2.0 * np.pi * 110.0 * t + 0.3)
    buzz_220 = 0.12 * np.sin(2.0 * np.pi * 220.0 * t + 0.6)
    buzz_330 = 0.08 * np.sin(2.0 * np.pi * 330.0 * t + 0.9)
    # High-frequency electrical stator hum (1650 Hz subtle whine)
    stator_whine = 0.04 * np.sin(2.0 * np.pi * 55.0 * 30 * t)
    # Mechanical vibration noise
    jitter = 0.05 * np.random.randn(num_samples)
    jitter_filtered = bandpass_filter(jitter, 80, 500, fs, order=2)

    motor_sfx = (buzz_55 + buzz_110 + buzz_220 + buzz_330 + stator_whine + jitter_filtered) * motor_active

    # 2. Sub-Bass Hydraulic Ground Rumble (38 Hz)
    sub_drone = 0.20 * np.sin(2.0 * np.pi * 38.0 * t) * motor_active

    # 3. External Perturbation Strike at t = 4.0s
    t_pert = 4.0
    pert_mask = t >= t_pert
    dt_pert = np.maximum(0, t - t_pert)
    pert_strike = 0.70 * np.sin(2.0 * np.pi * 210.0 * dt_pert) * np.exp(-18.0 * dt_pert) * pert_mask
    pert_sub = 0.50 * np.sin(2.0 * np.pi * 65.0 * dt_pert) * np.exp(-10.0 * dt_pert) * pert_mask
    pert_noise = 0.35 * bandpass_filter(np.random.randn(num_samples), 150, 1200, fs, order=2) * np.exp(-14.0 * dt_pert) * pert_mask
    pert_sfx = pert_strike + pert_sub + pert_noise

    # 4. Emergency Motor Shutdown at t = 8.0s (Breaker snap + Servo dive)
    t_shut = 8.0
    shut_mask = (t >= t_shut) & (t <= t_shut + 2.5)
    dt_shut = np.maximum(0, t - t_shut)
    # Relay click
    click_sfx = 0.60 * np.exp(-120.0 * dt_shut) * (t >= t_shut)
    # Frequency drops from 330 Hz down to 25 Hz exponentially
    freq_slide = 330.0 * np.exp(-3.8 * dt_shut)
    phase_slide = 2.0 * np.pi * np.cumsum(freq_slide) / fs
    shut_whine = 0.35 * np.sin(phase_slide) * np.exp(-2.2 * dt_shut) * shut_mask
    shut_sfx = click_sfx + shut_whine

    # 5. Gravitational Collapse Whooshes (Pendulum swings at t = 8.3s - 15.0s)
    swing_sfx = np.zeros(num_samples)
    for swing_t in [8.4, 9.7, 11.0, 12.3, 13.5, 14.6]:
        if swing_t < duration:
            sw_env = np.exp(-((t - swing_t) ** 2) / (2.0 * (0.22 ** 2)))
            decay = np.exp(-0.28 * (swing_t - 8.4))
            sw_noise = bandpass_filter(np.random.randn(num_samples), 100, 750, fs, order=2)
            swing_sfx += 0.40 * decay * sw_noise * sw_env

    # =========================================================================
    # PART 3: MASTER MIX & STEREO SPATIALIZATION
    # =========================================================================
    left_mix = (
        pad_left * 0.90
        + mel_left * 1.10
        + motor_sfx * 0.40
        + sub_drone * 0.25
        + pert_sfx * 0.60
        + shut_sfx * 0.50
        + swing_sfx * 0.35
    )
    right_mix = (
        pad_right * 0.90
        + mel_right * 1.10
        + motor_sfx * 0.40
        + sub_drone * 0.25
        + pert_sfx * 0.70  # Perturbation hits from right!
        + shut_sfx * 0.50
        + swing_sfx * 0.35
    )

    # Master Fade In / Out
    fade_in = np.clip(t / 0.35, 0.0, 1.0)
    fade_out = np.clip((duration - t) / 0.60, 0.0, 1.0)
    left_mix *= fade_in * fade_out
    right_mix *= fade_in * fade_out

    # Normalize to -1.0 dB
    peak = max(np.max(np.abs(left_mix)), np.max(np.abs(right_mix))) + 1e-8
    target_peak = 0.89  # ~ -1.0 dBFS
    left_mix = (left_mix / peak) * target_peak
    right_mix = (right_mix / peak) * target_peak

    stereo_int16 = np.vstack([
        (left_mix * 32767).astype(np.int16),
        (right_mix * 32767).astype(np.int16)
    ]).T

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(output_path, fs, stereo_int16)
    return str(output_path)


if __name__ == "__main__":
    out = synthesize_kapitza_audio(duration=15.0, output_path="test_kapitza_audio.wav")
    print(f"Kapitza audio generated successfully: {out}")
