"""
Continuum Lab — Procedural Audio Engine
Module: 02 Dinamica y Vibraciones / 03 Precesion Giroscopica 3D
Acoustic Design:
  1. 10,000 RPM high-speed gyroscopic turbine whine (modulating harmonic carrier ~450 Hz)
  2. Aerodynamic rotor blade shearing whoosh
  3. Cycloidal nutation rhythmic pulses (pitch & volume dip synchronized with up-and-down motion)
  4. Subtle sci-fi gyroscopic stabilizer hum
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


def synthesize_gyroscope_audio(
    duration: float = 14.0,
    fs: int = 44100,
    output_path: str = "gyroscope_audio.wav"
) -> str:
    """
    Synthesizes the procedural soundscape for 3D Gyroscopic Precession & Nutation.
    """
    num_samples = int(duration * fs)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    # 1. High-Speed Turbine Whine (10,000 RPM -> f0 = 166.7 Hz, 2nd harm = 333 Hz, 3rd = 500 Hz)
    f_rotor = 166.7
    # Periodic nutation modulation at ~1.0 Hz (up and down motion)
    omega_nut = 2.0 * np.pi * 1.0  # 1 Hz cycloidal bobbing
    nut_mod = 1.0 + 0.15 * np.cos(omega_nut * t)

    carrier1 = 0.35 * np.sin(2.0 * np.pi * (f_rotor * nut_mod) * t)
    carrier2 = 0.22 * np.sin(2.0 * np.pi * (2.0 * f_rotor * nut_mod) * t + 0.4)
    carrier3 = 0.12 * np.sin(2.0 * np.pi * (3.0 * f_rotor * nut_mod) * t + 0.8)

    # 2. Rotor Shearing Air Hiss
    noise = np.random.randn(num_samples)
    air_hiss = bandpass_filter(noise, 800, 3200, fs, order=2) * (0.18 + 0.08 * np.sin(omega_nut * t))

    # 3. Deep Precessional Gyroscopic Hum (58 Hz sub-bass)
    sub_hum = 0.28 * np.sin(2.0 * np.pi * 58.0 * t)

    # 4. Cycloidal Whoosh Accents (every time gyro dips and rises)
    accents = np.zeros(num_samples)
    for dip_t in np.arange(1.0, duration - 0.5, 1.0):
        accent_env = np.exp(-((t - dip_t) ** 2) / (2.0 * (0.16 ** 2)))
        accent_noise = bandpass_filter(np.random.randn(num_samples), 200, 1100, fs, order=2)
        accents += 0.25 * accent_noise * accent_env

    # Master Mix
    mix = (carrier1 + carrier2 + carrier3) * 0.45 + air_hiss * 0.35 + sub_hum * 0.40 + accents * 0.30

    # Smooth Fade In / Out
    fade_in = np.clip(t / 0.3, 0.0, 1.0)
    fade_out = np.clip((duration - t) / 0.5, 0.0, 1.0)
    mix = mix * fade_in * fade_out

    # Normalize to -1.0 dB
    peak = np.max(np.abs(mix)) + 1e-8
    mix = (mix / peak) * 0.89

    audio_int16 = (mix * 32767).astype(np.int16)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(output_path, fs, audio_int16)
    return str(output_path)


if __name__ == "__main__":
    out = synthesize_gyroscope_audio(duration=14.0, output_path="test_gyro.wav")
    print(f"Gyroscope audio generated: {out}")
