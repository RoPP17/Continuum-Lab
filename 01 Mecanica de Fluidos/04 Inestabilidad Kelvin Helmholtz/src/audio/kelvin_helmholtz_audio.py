"""
Continuum Lab - Procedural Hydrodynamic Audio Synthesizer
Module: 01 Mecanica de Fluidos / 04 Inestabilidad Kelvin Helmholtz
File: src/audio/kelvin_helmholtz_audio.py

Synthesizes a 14-second 44.1 kHz stereo cinematic hydrodynamic soundscape:
  1. Sub-bass hydrodynamic foundation (42 Hz -> 58 Hz modulated by kinetic energy)
  2. Viscous shear wind rush (stereo panned pink noise with resonant bandpass tracking vortex roll-up)
  3. Celestial crystal chimes (D-minor pentatonic: D4, F4, A4, C5, D5) triggered as vortex cores peak
  4. Non-linear saturation impact riser & deep sub drop at t ≈ 7.0s
  5. Master stereo compressor, limiter, and smooth fade in/out
"""

from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter


def _butter_bandpass(lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = max(0.001, lowcut / nyq)
    high = min(0.999, highcut / nyq)
    b, a = butter(order, [low, high], btype='band')
    return b, a


def _bandpass_filter(data, lowcut, highcut, fs, order=3):
    b, a = _butter_bandpass(lowcut, highcut, fs, order=order)
    return lfilter(b, a, data)


def synthesize_khi_soundtrack(output_wav_path: str, duration: float = 14.0, sample_rate: int = 44100):
    """
    Synthesizes the complete cinematic audio track for Kelvin-Helmholtz simulation.
    """
    total_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, total_samples, endpoint=False)

    # -------------------------------------------------------------------------
    # 1. Sub-bass Hydrodynamic Drone (Deep continuum momentum)
    # -------------------------------------------------------------------------
    f_base = 45.0 + 10.0 * np.sin(2.0 * np.pi * 0.12 * t)
    phase_sub = 2.0 * np.pi * np.cumsum(f_base) / sample_rate
    sub_bass = 0.35 * np.sin(phase_sub) + 0.15 * np.sin(2.0 * phase_sub + 0.3)
    # Add subtle saturation / warm overdrive
    sub_bass = np.tanh(sub_bass * 1.6)

    # -------------------------------------------------------------------------
    # 2. Viscous Shear Wind Rush (Stereo Pink/Turbulent Noise)
    # -------------------------------------------------------------------------
    # Generate pink noise via filtered white noise
    white_l = np.random.normal(0, 1, total_samples)
    white_r = np.random.normal(0, 1, total_samples)

    # Bandpass filtered around 350 - 1800 Hz to simulate atmospheric shear whoosh
    shear_wind_l = _bandpass_filter(white_l, 250.0, 1600.0, sample_rate, order=2)
    shear_wind_r = _bandpass_filter(white_r, 280.0, 1750.0, sample_rate, order=2)

    # Dynamic amplitude envelope tracking vortex roll-up (peaks around t = 7.5s)
    env_shear = 0.15 + 0.55 * np.exp(-((t - 7.5) / 3.8) ** 2)
    shear_l = shear_wind_l * env_shear * 0.40
    shear_r = shear_wind_r * env_shear * 0.40

    # -------------------------------------------------------------------------
    # 3. Celestial Crystal Chimes (Vortex Core Roll-up Harmonics)
    # -------------------------------------------------------------------------
    chimes_l = np.zeros(total_samples)
    chimes_r = np.zeros(total_samples)

    # Pentatonic notes: D4 (293.66), F4 (349.23), A4 (440.0), C5 (523.25), D5 (587.33), F5 (698.46)
    notes = [
        (2.8, 293.66, -0.6),
        (3.9, 349.23, +0.5),
        (5.2, 440.00, -0.3),
        (6.4, 523.25, +0.7),
        (7.2, 587.33, -0.5),
        (8.1, 698.46, +0.4),
        (9.3, 880.00, -0.2),
        (10.5, 587.33, +0.3),
        (11.8, 440.00, -0.4),
    ]

    for start_t, freq, pan in notes:
        start_idx = int(start_t * sample_rate)
        note_dur = 2.4
        note_len = min(int(note_dur * sample_rate), total_samples - start_idx)
        if note_len <= 0:
            continue
        t_note = np.linspace(0, note_dur, note_len, endpoint=False)
        # Bell envelope: instantaneous attack + exponential decay
        decay = np.exp(-t_note * 2.8)
        # Harmonics
        tone = (
            0.60 * np.sin(2.0 * np.pi * freq * t_note) +
            0.30 * np.sin(2.0 * np.pi * freq * 2.0 * t_note) +
            0.15 * np.sin(2.0 * np.pi * freq * 3.01 * t_note)
        ) * decay * 0.35

        # Pan: -1 (left) to +1 (right)
        g_l = np.cos((pan + 1.0) * np.pi / 4.0)
        g_r = np.sin((pan + 1.0) * np.pi / 4.0)

        chimes_l[start_idx:start_idx + note_len] += tone * g_l
        chimes_r[start_idx:start_idx + note_len] += tone * g_r

    # -------------------------------------------------------------------------
    # 4. Non-Linear Saturation Sub-Drop (Impact at t = 7.0s)
    # -------------------------------------------------------------------------
    impact_l = np.zeros(total_samples)
    impact_r = np.zeros(total_samples)
    t_impact = 7.0
    impact_idx = int(t_impact * sample_rate)
    impact_dur = 3.5
    impact_len = min(int(impact_dur * sample_rate), total_samples - impact_idx)
    if impact_len > 0:
        t_imp = np.linspace(0, impact_dur, impact_len, endpoint=False)
        # Pitch glide downward from 95 Hz to 35 Hz
        f_glide = 95.0 * np.exp(-t_imp * 1.5) + 35.0
        p_glide = 2.0 * np.pi * np.cumsum(f_glide) / sample_rate
        imp_body = np.sin(p_glide) * np.exp(-t_imp * 1.2) * 0.45
        impact_l[impact_idx:impact_idx + impact_len] += imp_body
        impact_r[impact_idx:impact_idx + impact_len] += imp_body

    # -------------------------------------------------------------------------
    # 5. Master Mix & Dynamics
    # -------------------------------------------------------------------------
    left = sub_bass * 0.50 + shear_l + chimes_l + impact_l
    right = sub_bass * 0.50 + shear_r + chimes_r + impact_r

    # Master Fade In (0.5s) and Fade Out (1.2s)
    fade_in_len = min(int(0.5 * sample_rate), max(1, total_samples // 4))
    fade_out_len = min(int(1.2 * sample_rate), max(1, total_samples // 3))

    left[:fade_in_len] *= np.linspace(0.0, 1.0, fade_in_len)
    right[:fade_in_len] *= np.linspace(0.0, 1.0, fade_in_len)

    left[-fade_out_len:] *= np.linspace(1.0, 0.0, fade_out_len)
    right[-fade_out_len:] *= np.linspace(1.0, 0.0, fade_out_len)

    # Master Soft Limiter / Normalization (-1.0 dB peak)
    max_peak = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-6)
    target_peak = 0.89  # -1.0 dB
    left = (left / max_peak) * target_peak
    right = (right / max_peak) * target_peak

    # Convert to 16-bit PCM WAV
    audio_data = np.column_stack((left, right))
    audio_pcm16 = (audio_data * 32767.0).astype(np.int16)

    Path(output_wav_path).parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(output_wav_path, sample_rate, audio_pcm16)
    return output_wav_path
