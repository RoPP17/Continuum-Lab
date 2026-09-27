"""
Continuum Lab — Friendly & Satisfying Hydrodynamic Audio Engine
Synthesizes a relaxing, crisp, and scientifically satisfying water/fluid soundscape.
Replaces dark/spooky rumbles with:
  1. Crisp, clear, relaxing mountain stream / laminar fluid flow.
  2. Soft, velvety liquid whooshes modulated by cylinder displacement.
  3. Delicate water micro-droplets and gentle bubbling textures.
  4. A warm, comforting, friendly ambient harmonic pad (uplifting C-major / F-major harmony).
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
import os


def butter_bandpass(lowcut, highcut, fs, order=2):
    nyq = 0.5 * fs
    low = max(lowcut / nyq, 0.001)
    high = min(highcut / nyq, 0.999)
    b, a = butter(order, [low, high], btype='band')
    return b, a


def bandpass_filter(data, lowcut, highcut, fs, order=2):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    return lfilter(b, a, data)


def generate_pink_noise(num_samples: int) -> np.ndarray:
    white = np.random.randn(num_samples)
    fft_white = np.fft.rfft(white)
    frequencies = np.fft.rfftfreq(num_samples)
    frequencies[0] = 1.0
    fft_pink = fft_white / np.sqrt(frequencies)
    fft_pink[0] = 0.0
    pink = np.fft.irfft(fft_pink, n=num_samples)
    return pink / (np.max(np.abs(pink)) + 1e-8)


def synthesize_fluid_audio(
    duration: float = 18.5,
    fs: int = 44100,
    output_path: str = "fluid_audio_friendly.wav"
) -> str:
    num_samples = int(duration * fs)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    # 1. Obstacle velocity profile (matches cylinder oscillation)
    omega_y = 1.6
    vy = 1.1 * omega_y * np.cos(omega_y * t)
    speed = np.abs(vy)
    speed_norm = speed / (np.max(speed) + 1e-6)

    # 2. Crisp, soothing flowing water (Pink noise shaped to 350 - 2400 Hz)
    pink_l = generate_pink_noise(num_samples)
    pink_r = generate_pink_noise(num_samples)

    water_l = bandpass_filter(pink_l, 350, 2200, fs, order=2) * 0.22
    water_r = bandpass_filter(pink_r, 380, 2400, fs, order=2) * 0.22

    # 3. Soft velvety liquid displacement (gentle water whoosh when cylinder moves)
    whoosh_raw = generate_pink_noise(num_samples)
    whoosh_filtered = bandpass_filter(whoosh_raw, 450, 1600, fs, order=2)
    whoosh_env = (speed_norm**1.5) * 0.28
    pan_w = 0.5 * (1.0 + np.sin(omega_y * t))
    whoosh_l = whoosh_filtered * whoosh_env * (0.4 + 0.6 * pan_w)
    whoosh_r = whoosh_filtered * whoosh_env * (0.4 + 0.6 * (1.0 - pan_w))

    # 4. Delicate water droplet bubbles (soft ASMR liquid texture)
    bubbles_l = np.zeros(num_samples)
    bubbles_r = np.zeros(num_samples)
    np.random.seed(42)
    num_bubbles = int(duration * 12)  # ~12 soft bubbles per second
    bubble_times = np.random.uniform(0.5, duration - 0.5, num_bubbles)
    for bt in bubble_times:
        idx = int(bt * fs)
        b_len = int(0.04 * fs)  # 40 ms bubble
        if idx + b_len < num_samples:
            tb = np.linspace(0, 0.04, b_len, endpoint=False)
            fb = np.random.uniform(700, 1400)
            # Gentle pitch glide up (characteristic water droplet)
            freq_glide = fb + 400 * (tb / 0.04)
            b_wave = np.sin(2 * np.pi * freq_glide * tb) * np.exp(-tb / 0.012) * 0.06
            if np.random.rand() > 0.5:
                bubbles_l[idx:idx + b_len] += b_wave
            else:
                bubbles_r[idx:idx + b_len] += b_wave

    # 5. Warm, uplifting ambient pad (Cmaj9 -> Fmaj7 -> Gsus4 -> Cmaj)
    # Provides friendly, comforting scientific atmosphere
    chord_times = [0.0, 4.5, 9.0, 13.5, 18.5]
    # Chords (frequencies in Hz):
    # Cmaj9: C3, G3, B3, D4, E4
    # Fmaj7: F3, A3, C4, E4
    # Gsus4: G3, C4, D4, G4
    # Cmaj: C3, E3, G3, C4, E4
    chords = [
        [130.81, 196.00, 246.94, 293.66, 329.63],
        [174.61, 220.00, 261.63, 329.63],
        [196.00, 261.63, 293.66, 392.00],
        [130.81, 164.81, 196.00, 261.63, 329.63],
    ]
    pad_signal = np.zeros(num_samples)
    for c_idx in range(len(chords)):
        t_start = chord_times[c_idx]
        t_end = chord_times[c_idx + 1]
        mask = (t >= t_start) & (t < t_end)
        t_segment = t[mask] - t_start
        seg_len = len(t_segment)
        if seg_len == 0:
            continue
        seg_wave = np.zeros(seg_len)
        for freq in chords[c_idx]:
            seg_wave += (0.025 / len(chords[c_idx])) * (
                np.sin(2 * np.pi * freq * t_segment) +
                0.3 * np.sin(2 * np.pi * (2 * freq) * t_segment)
            )
        # Smooth crossfade
        env = np.ones(seg_len)
        fade = min(int(0.5 * fs), seg_len // 4)
        if fade > 0:
            env[:fade] = np.linspace(0.0, 1.0, fade)
            env[-fade:] = np.linspace(1.0, 0.0, fade)
        pad_signal[mask] += seg_wave * env

    # Combine all elements
    audio_left = water_l + whoosh_l + bubbles_l + pad_signal * 0.8
    audio_right = water_r + whoosh_r + bubbles_r + pad_signal * 0.8

    # Smooth master fade-in and fade-out
    fade_len = int(0.4 * fs)
    audio_left[:fade_len] *= np.linspace(0.0, 1.0, fade_len)
    audio_right[:fade_len] *= np.linspace(0.0, 1.0, fade_len)
    audio_left[-fade_len:] *= np.linspace(1.0, 0.0, fade_len)
    audio_right[-fade_len:] *= np.linspace(1.0, 0.0, fade_len)

    # Normalize to -1.5 dB peak
    peak = max(np.max(np.abs(audio_left)), np.max(np.abs(audio_right))) + 1e-6
    audio_left = (audio_left / peak) * 0.85
    audio_right = (audio_right / peak) * 0.85

    stereo_audio = np.stack([audio_left, audio_right], axis=1)
    stereo_int16 = (stereo_audio * 32767.0).astype(np.int16)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    wavfile.write(output_path, fs, stereo_int16)
    print(f"[CONTINUUM LAB] Friendly hydrodynamic audio synthesized -> {output_path}")
    return output_path


if __name__ == "__main__":
    synthesize_fluid_audio(output_path="test_friendly_fluid.wav")
