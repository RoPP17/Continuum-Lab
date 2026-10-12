"""
Procedural Aeroelastic Audio Engine — Tacoma Narrows Flutter
Module: 02 Dinamica y Vibraciones / 04 Flutter Aeroelastico Tacoma Narrows

Acoustic Architecture:
  1. Ambient Wind & Aero Rush: Pink noise bandpass filtered with speed-dependent cutoff.
  2. Aeroelastic Whistle / Vortex Lock-In: Tonal whistling matching shedding frequency.
  3. Structural Torsional Shudder: Low-frequency sub-bass throbbing synchronized with deck roll.
  4. Steel Cable Creak & Snap: Metallic tension chirps during extreme torsional excursions.
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
from pathlib import Path


def _butter_bandpass(lowcut: float, highcut: float, fs: int, order: int = 2):
    nyq = 0.5 * fs
    low = max(lowcut / nyq, 0.0005)
    high = min(highcut / nyq, 0.9990)
    b, a = butter(order, [low, high], btype="band")
    return b, a


def _bandpass(data: np.ndarray, lowcut: float, highcut: float, fs: int, order: int = 2) -> np.ndarray:
    b, a = _butter_bandpass(lowcut, highcut, fs, order=order)
    return lfilter(b, a, data)


def _pink_noise(n_samples: int) -> np.ndarray:
    white = np.random.randn(n_samples)
    fft_white = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n_samples)
    freqs[0] = 1.0
    fft_pink = fft_white / np.sqrt(freqs)
    fft_pink[0] = 0.0
    pink = np.fft.irfft(fft_pink, n=n_samples)
    return pink / (np.max(np.abs(pink)) + 1e-8)


def synthesize_tacoma_audio(
    duration: float = 15.0,
    fs: int = 44100,
    output_path: str = "tacoma_flutter_audio.wav"
) -> str:
    n_samples = int(duration * fs)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    # 1. Dynamic Wind Rush (Wind increases from 25 km/h to 68 km/h at t=4..8.5s)
    wind_intensity = np.where(
        t < 4.0,
        0.35,
        np.where(
            t < 8.5,
            0.35 + 0.55 * (t - 4.0) / 4.5,
            0.90 + 0.10 * np.sin(2.0 * np.pi * 0.3 * t)
        )
    )

    pink_raw = _pink_noise(n_samples)
    wind_gust = _bandpass(pink_raw, 180, 2200, fs, order=2) * wind_intensity * 0.35

    # 2. Aeroelastic Whistle / Strouhal Vortex Shedding Whine (450 - 680 Hz)
    whistle_freq = 480.0 + 160.0 * np.clip((t - 4.0) / 4.5, 0.0, 1.0)
    whistle_phase = 2.0 * np.pi * np.cumsum(whistle_freq) / fs
    whistle_amp = np.clip((t - 3.5) / 5.0, 0.0, 1.0) * 0.08
    # Modulate whistle with bridge twist period (~0.2 Hz)
    whistle_mod = 0.6 + 0.4 * np.sin(2.0 * np.pi * 0.22 * t)
    whistle = np.sin(whistle_phase) * whistle_amp * whistle_mod

    # 3. Violent Torsional Rumble & Structural Stress (Phase 3: t >= 8.5s)
    flutter_mask = np.clip((t - 7.5) / 2.0, 0.0, 1.0)
    deck_osc_freq = 0.22  # Hz torsional resonance
    deck_tilt = np.sin(2.0 * np.pi * deck_osc_freq * t)

    # Sub-bass structural shudder (35-85 Hz)
    sub_pink = _pink_noise(n_samples)
    sub_rumble = _bandpass(sub_pink, 32, 88, fs, order=3)
    sub_stress = sub_rumble * flutter_mask * (np.abs(deck_tilt) ** 1.5) * 0.55

    # 4. Cable Creaks & Metallic Groans at peak deck angle
    cable_creak = np.zeros(n_samples)
    # Peak twisting occurs when |deck_tilt| > 0.85
    strain_mask = (np.abs(deck_tilt) > 0.82) * flutter_mask
    creak_carrier = np.sin(2.0 * np.pi * 1450.0 * t) + 0.5 * np.sin(2.0 * np.pi * 2100.0 * t)
    creak_noise = _bandpass(_pink_noise(n_samples), 1200, 3800, fs, order=2)
    cable_creak = (creak_carrier * 0.4 + creak_noise * 0.6) * strain_mask * 0.18

    # 5. Composite Mix & Limiting
    audio = wind_gust + whistle + sub_stress + cable_creak

    # Fade-in and fade-out envelope
    fade_in = np.clip(t / 0.5, 0.0, 1.0)
    fade_out = np.clip((duration - t) / 0.6, 0.0, 1.0)
    audio = audio * fade_in * fade_out

    # Normalize to -1.0 dB
    peak = np.max(np.abs(audio)) + 1e-8
    audio = (audio / peak) * 0.88

    # Convert to 16-bit PCM stereo
    audio_int16 = (audio * 32767.0).astype(np.int16)
    stereo = np.column_stack((audio_int16, audio_int16))

    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(str(out_file), fs, stereo)
    return str(out_file)


if __name__ == "__main__":
    synthesize_tacoma_audio(15.0, 44100, "test_tacoma.wav")
    print("Synthesized Tacoma audio successfully.")
