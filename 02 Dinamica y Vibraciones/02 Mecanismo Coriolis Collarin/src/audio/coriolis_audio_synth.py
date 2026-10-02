"""
Continuum Lab — Classical Mechanics & Dynamical Systems
Division: 02 Dinamica y Vibraciones / 02 Mecanismo Coriolis Collarin
Module: coriolis_audio_synth.py

Procedural High-Fidelity Acoustic Engine for 2-Bar Quick-Return Mechanism with Coriolis Acceleration.
Synthesizes:
  1. Mechanical Sliding Hydro-dynamic Whoosh modulated by relative velocity |v_rel(t)|.
  2. Dynamic Coriolis Carrier Tone modulated by |a_coriolis(t)| and omega2(t).
  3. Resonant Inversion Chimes at Coriolis direction flips (a_cor crossing zero).
  4. Spatial Stereo Panning tracking collar horizontal position x_A(t).
  5. Cybernetic Ambient Foundation bed in D-minor / A-minor.
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
import os


def butter_bandpass(lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = max(lowcut / nyq, 0.001)
    high = min(highcut / nyq, 0.999)
    b, a = butter(order, [low, high], btype='band')
    return b, a


def bandpass_filter(data, lowcut, highcut, fs, order=3):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    return lfilter(b, a, data)


def synthesize_coriolis_audio(
    time_points: np.ndarray,
    collar_x: np.ndarray,
    v_rel: np.ndarray,
    a_cor: np.ndarray,
    omega2: np.ndarray,
    duration: float = 18.5,
    fs: int = 44100,
    output_path: str = "coriolis_audio_synth.wav"
) -> str:
    num_samples = int(duration * fs)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    x_interp = np.interp(t, time_points, collar_x)
    vrel_interp = np.interp(t, time_points, v_rel)
    acor_interp = np.interp(t, time_points, a_cor)
    w2_interp = np.interp(t, time_points, omega2)

    # Normalizaciones cinemáticas
    vrel_abs = np.abs(vrel_interp)
    max_vrel = np.max(vrel_abs) + 1e-6
    vrel_norm = vrel_abs / max_vrel

    acor_abs = np.abs(acor_interp)
    max_acor = np.max(acor_abs) + 1e-6
    acor_norm = acor_abs / max_acor

    # Coeficiente de paneo espacial [-1 (izq) a +1 (der)]
    pan = np.clip(x_interp / 1.2, -0.9, 0.9)
    left_gain = np.sqrt(0.5 * (1.0 - pan))
    right_gain = np.sqrt(0.5 * (1.0 + pan))

    # 1. Warm Ambient Cybernetic Pad (D minor / F / A foundation)
    pad_left = np.zeros(num_samples)
    pad_right = np.zeros(num_samples)
    pad_freqs = [146.83, 220.00, 261.63, 329.63, 440.00]  # D3, A3, C4, E4, A4
    for idx, pf in enumerate(pad_freqs):
        phase = idx * 0.4
        pad_left += 0.032 * np.sin(2 * np.pi * pf * t + phase)
        pad_right += 0.032 * np.sin(2 * np.pi * pf * t + phase + 0.6)

    # 2. Mechanical Sliding Kinetic Noise (Whoosh filtered by v_rel)
    raw_noise = np.random.normal(0, 1, num_samples)
    filtered_noise = bandpass_filter(raw_noise, 400, 2200, fs, order=2)
    # Suavizar modulación
    sliding_envelope = 0.08 * (vrel_norm ** 1.3)
    sliding_left = filtered_noise * sliding_envelope * left_gain
    sliding_right = filtered_noise * sliding_envelope * right_gain

    # 3. Dynamic Coriolis Carrier Tone
    # Portadora variable con pitch modulado por la magnitud de Coriolis (220 Hz a 580 Hz)
    carrier_freq = 220.0 + 360.0 * acor_norm
    # Fase acumulada para modulación continua de frecuencia
    phase_coriolis = 2 * np.pi * np.cumsum(carrier_freq) / fs
    # Modulación armónica pura
    tone_coriolis = np.sin(phase_coriolis) * (0.045 + 0.075 * acor_norm)
    # Segundo armónico sutil
    tone_coriolis += 0.02 * np.sin(2 * phase_coriolis) * acor_norm

    cor_left = tone_coriolis * left_gain
    cor_right = tone_coriolis * right_gain

    # 4. Zero-Crossing / Acceleration Peak Musical Chimes (Celesta Bells)
    # Escala pentatónica para acentos armónicos: D, F, G, A, C
    scale = [293.66, 349.23, 392.00, 440.00, 523.25, 587.33, 698.46, 880.00]
    chimes_left = np.zeros(num_samples)
    chimes_right = np.zeros(num_samples)

    # Detectar picos de Coriolis para disparar campanas
    diff_acor = np.diff(np.sign(np.diff(acor_abs)))
    peak_indices = np.where(diff_acor < 0)[0] + 1

    for p_idx in peak_indices:
        if p_idx > num_samples - int(0.6 * fs) or p_idx < int(0.2 * fs):
            continue
        p_val = acor_norm[p_idx]
        if p_val < 0.65:
            continue  # solo picos relevantes
        n_idx = int(p_val * (len(scale) - 1))
        freq = scale[n_idx]

        dur_bell = 0.55
        n_bell = min(int(dur_bell * fs), num_samples - p_idx)
        t_bell = np.linspace(0, dur_bell, n_bell, endpoint=False)
        bell_env = np.exp(-t_bell / 0.12)
        bell_signal = 0.06 * np.sin(2 * np.pi * freq * t_bell) * bell_env
        bell_signal += 0.025 * np.sin(2 * np.pi * (freq * 2.756) * t_bell) * np.exp(-t_bell / 0.06)

        p_gain_l = left_gain[p_idx]
        p_gain_r = right_gain[p_idx]
        chimes_left[p_idx:p_idx + n_bell] += bell_signal * p_gain_l
        chimes_right[p_idx:p_idx + n_bell] += bell_signal * p_gain_r

    # Mezcla final estéreo
    master_left = pad_left + sliding_left + cor_left + chimes_left
    master_right = pad_right + sliding_right + cor_right + chimes_right

    # Fade in / Fade out
    fade_len = int(0.25 * fs)
    fade_in = np.linspace(0, 1, fade_len)
    fade_out = np.linspace(1, 0, fade_len)
    master_left[:fade_len] *= fade_in
    master_right[:fade_len] *= fade_in
    master_left[-fade_len:] *= fade_out
    master_right[-fade_len:] *= fade_out

    # Normalizar a pico -1.5 dB (0.84)
    peak = max(np.max(np.abs(master_left)), np.max(np.abs(master_right)), 1e-6)
    target_peak = 0.85
    master_left = (master_left / peak) * target_peak
    master_right = (master_right / peak) * target_peak

    # Convertir a 16-bit PCM estéreo
    stereo_out = np.column_stack([
        (master_left * 32767).astype(np.int16),
        (master_right * 32767).astype(np.int16)
    ])

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    wavfile.write(output_path, fs, stereo_out)
    return output_path


if __name__ == "__main__":
    t_test = np.linspace(0, 18.0, 1080)
    x_test = np.sin(t_test * 2)
    v_test = 2 * np.cos(t_test * 2)
    a_test = -4 * np.sin(t_test * 2)
    w_test = np.ones_like(t_test)
    out = synthesize_coriolis_audio(t_test, x_test, v_test, a_test, w_test, duration=18.0)
    print("Test synth saved to:", out)
