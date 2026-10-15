"""
Continuum Lab — Procedural Audio Engine
Module: 02 Dinamica y Vibraciones / 05 Mecanismo Peaucellier Lipkin
File: peaucellier_audio_synth.py

Procedural High-Fidelity Acoustic Design for Peaucellier-Lipkin Linkage:
  1. Mechanical bearing whisper & smooth hydro-sliding glide modulated by tracer speed |v_y(t)|.
  2. Harmonic laser crystallization tone (~520 Hz with subtle FM glide) tracking vertical tracer P'.
  3. Resonant Celesta & glass bell accents when crossing centerline (y = 0) and at motion extrema.
  4. Deep cybernetic sub-bass carrier (55 Hz) giving immense weight and industrial elegance.
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


def synthesize_peaucellier_audio(
    duration: float = 14.0,
    fs: int = 44100,
    output_path: str = "peaucellier_audio.wav"
) -> str:
    num_samples = int(duration * fs)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    # Kinematic oscillation frequency (omega = 0.95 rad/s -> f = 0.95 / (2*pi) ~= 0.151 Hz, period ~6.6s)
    omega_kin = 0.95
    vel_mod = np.abs(np.cos(omega_kin * t))  # Max velocity at centerline
    pos_mod = np.sin(omega_kin * t)          # Position
    
    # 1. Mechanical Bearing Whisper & Linkage Glide
    noise = np.random.randn(num_samples)
    glide_raw = bandpass_filter(noise, 650, 2400, fs, order=2)
    glide_env = 0.15 + 0.25 * vel_mod
    glide_audio = glide_raw * glide_env
    
    # 2. Pure Laser Tracer Harmonic (528 Hz Solfeggio / Crystal tone)
    # Pitch bends slightly with tracer position
    laser_f0 = 528.0 + 35.0 * pos_mod
    laser_phase = 2.0 * np.pi * np.cumsum(laser_f0) / fs
    laser_synth = 0.18 * np.sin(laser_phase) + 0.08 * np.sin(2.0 * laser_phase + 0.3)
    
    # 3. Sub-Bass Foundation Bed (55 Hz - A1 note)
    sub_bass = 0.26 * np.sin(2.0 * np.pi * 55.0 * t) + 0.12 * np.sin(2.0 * np.pi * 110.0 * t)
    
    # 4. Celesta Chime Accents (Centerline crossings y=0 and turnarounds)
    chimes = np.zeros(num_samples)
    # Sample zero-crossings (every half period T/2 = pi / omega_kin ~= 3.307s)
    period_half = np.pi / omega_kin
    crossing_times = np.arange(period_half / 2.0, duration - 0.5, period_half)
    
    for t_hit in crossing_times:
        hit_idx = int(t_hit * fs)
        if 0 <= hit_idx < num_samples:
            env_len = int(1.2 * fs)
            t_env = np.linspace(0, 1.2, env_len, endpoint=False)
            decay = np.exp(-4.5 * t_env)
            bell = (
                0.35 * np.sin(2.0 * np.pi * 880.0 * t_env) +
                0.20 * np.sin(2.0 * np.pi * 1760.0 * t_env) +
                0.12 * np.sin(2.0 * np.pi * 2640.0 * t_env)
            ) * decay
            
            end_idx = min(num_samples, hit_idx + env_len)
            chimes[hit_idx:end_idx] += bell[:end_idx - hit_idx]
            
    # Master Mix
    mix_mono = (
        0.30 * glide_audio +
        0.32 * laser_synth +
        0.25 * sub_bass +
        0.28 * chimes
    )
    
    # Smooth fade-in (0.5s) and fade-out (0.8s)
    fade_in_len = int(0.5 * fs)
    fade_out_len = int(0.8 * fs)
    mix_mono[:fade_in_len] *= np.linspace(0, 1, fade_in_len)
    mix_mono[-fade_out_len:] *= np.linspace(1, 0, fade_out_len)
    
    # Stereo Spatial Panning tracking tracer position
    pan_l = np.clip(0.5 - 0.35 * pos_mod, 0.15, 0.85)
    pan_r = np.clip(0.5 + 0.35 * pos_mod, 0.15, 0.85)
    
    stereo = np.column_stack([mix_mono * pan_l, mix_mono * pan_r])
    
    # Normalization (-1.0 dB headroom)
    max_val = np.max(np.abs(stereo))
    if max_val > 1e-6:
        stereo = stereo / max_val * 0.89
        
    audio_int16 = (stereo * 32767).astype(np.int16)
    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(str(out_file), fs, audio_int16)
    print(f"[AUDIO] Procedural soundtrack generated: {out_file} ({duration}s @ {fs} Hz)")
    return str(out_file)


if __name__ == "__main__":
    synthesize_peaucellier_audio(duration=14.0, output_path="peaucellier_audio.wav")
