"""
Continuum Lab — Procedural Hydro/Aero-Acoustic Audio Engine
Module: 01 Mecanica de Fluidos / 03 Desprendimiento Capa Limite y Stall Aerodinamico
Acoustic Design: Laminar Flow Rush, Boundary Layer Separation, Violent Stall Buffet & Cockpit Alert

Layers:
  1. Laminar Airflow Rush: Clean, high-velocity aerodynamic wind hiss (bandpass pink noise 600-2400 Hz).
  2. Adverse Pressure Gradient Shift: Turbulence spectrum broadening and low-pass softening.
  3. Aerodynamic Stall Buffet Rumble: Sub-bass 35-85 Hz chaotic turbulence shaking the airframe.
  4. Acoustic Stall Warning Alert: Aeronautical cockpit horn pulses (880 Hz / 980 Hz) during stall onset.
  5. Cybernetic Ambient Pad: Deep minor chords grounding the scientific exposition.
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


def generate_pink_noise(num_samples: int) -> np.ndarray:
    white = np.random.randn(num_samples)
    fft_white = np.fft.rfft(white)
    frequencies = np.fft.rfftfreq(num_samples)
    frequencies[0] = 1.0
    fft_pink = fft_white / np.sqrt(frequencies)
    fft_pink[0] = 0.0
    pink = np.fft.irfft(fft_pink, n=num_samples)
    return pink / (np.max(np.abs(pink)) + 1e-8)


def synthesize_stall_audio(
    duration: float = 18.0,
    fs: int = 44100,
    output_path: str = "aerodynamic_stall_audio.wav"
) -> str:
    """
    Synthesizes the complete multi-layer aero-acoustic soundtrack for the 18s video.
    """
    num_samples = int(duration * fs)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    progress = t / duration

    # Angle of attack progression: 4.0 deg -> 18.5 deg
    # 0.0s - 3.0s: alpha = 4.0 deg (steady laminar)
    # 3.0s - 13.0s: pitching smoothly from 4.0 deg to 18.5 deg
    # 13.0s - 18.0s: deep stall & CTA
    alpha_t = np.where(
        t < 3.0,
        4.0,
        np.where(
            t < 13.0,
            4.0 + (18.5 - 4.0) * (0.5 - 0.5 * np.cos(np.pi * (t - 3.0) / 10.0)),
            18.5
        )
    )

    # -------------------------------------------------------------------------
    # 1. Laminar Airflow Wind Rush (Clean Aerodynamic Hiss)
    # -------------------------------------------------------------------------
    pink_l = generate_pink_noise(num_samples)
    pink_r = generate_pink_noise(num_samples)

    # Dynamic filter frequency: drops from high hiss (clean) to broader rumble
    laminar_l = bandpass_filter(pink_l, 500, 2800, fs, order=2)
    laminar_r = bandpass_filter(pink_r, 550, 3000, fs, order=2)

    # Intensity peaks early then transitions into turbulent wake
    laminar_amp = np.where(t < 8.0, 0.28, 0.28 * np.exp(-(t - 8.0) / 4.0) + 0.08)
    wind_l = laminar_l * laminar_amp
    wind_r = laminar_r * laminar_amp

    # -------------------------------------------------------------------------
    # 2. Aerodynamic Stall Buffet (Violent Low-Frequency Airframe Shaking)
    # -------------------------------------------------------------------------
    # Buffet kicks in as alpha crosses 13 deg (t ~ 7.5s) and peaks at 18.5 deg
    buffet_mask = np.clip((alpha_t - 12.0) / (18.5 - 12.0), 0.0, 1.0) ** 1.8

    # Low frequency rumble (35 - 90 Hz)
    sub_pink = generate_pink_noise(num_samples)
    buffet_raw = bandpass_filter(sub_pink, 32, 95, fs, order=3)

    # Periodic vortex shedding modulation: ~15 Hz buffeting pulsations
    buffet_mod = 1.0 + 0.65 * np.sin(2.0 * np.pi * 16.0 * t + 0.3 * np.sin(2.0 * np.pi * 3.5 * t))
    buffet_shaking = buffet_raw * buffet_mask * buffet_mod * 0.70

    # Non-linear saturation for airframe shudder
    buffet_shaking = np.tanh(buffet_shaking * 2.2) * 0.45

    # -------------------------------------------------------------------------
    # 3. Cockpit Stall Warning Alert (Aeronautical Pulsed Tone: 880 Hz / 980 Hz)
    # -------------------------------------------------------------------------
    horn_tone = np.zeros(num_samples)
    horn_start = 8.5   # Starts right as separation reaches 50% chord
    horn_end = 15.0    # Silenced as debate CTA takes over

    # Pulsing: 3 beeps per second (beep duration 0.20s, silence 0.13s)
    pulse_period = 0.33
    beep_duty = 0.60
    horn_active = (t >= horn_start) & (t <= horn_end)

    mod_phase = (t % pulse_period) / pulse_period
    beep_gate = (mod_phase < beep_duty).astype(float)

    # Smooth the square gate edges to prevent clicks
    window_len = int(0.015 * fs)
    window = np.hanning(window_len * 2)
    beep_gate = np.convolve(beep_gate, window / np.sum(window), mode='same')

    # Dual frequency warning horn
    f_horn1 = 880.0
    f_horn2 = 988.0
    horn_signal = 0.5 * np.sin(2.0 * np.pi * f_horn1 * t) + 0.5 * np.sin(2.0 * np.pi * f_horn2 * t)
    # Add slight 2nd harmonic
    horn_signal += 0.25 * np.sin(2.0 * np.pi * (2.0 * f_horn1) * t)

    horn_tone = horn_signal * beep_gate * horn_active * 0.22

    # -------------------------------------------------------------------------
    # 4. Cinematic Sci-Tech Atmospheric Drone (Cm9 -> Abmaj7 -> Fm9)
    # -------------------------------------------------------------------------
    chord_drone = np.zeros(num_samples)
    # Fundamental bass drone at 65.4 Hz (C2)
    f_root = 65.4
    drone_raw = (
        0.35 * np.sin(2.0 * np.pi * f_root * t) +
        0.20 * np.sin(2.0 * np.pi * (f_root * 1.5) * t) +
        0.12 * np.sin(2.0 * np.pi * (f_root * 2.0) * t) +
        0.08 * np.sin(2.0 * np.pi * (f_root * 3.0) * t)
    )
    # Breathing envelope
    drone_env = 0.18 + 0.12 * np.sin(2.0 * np.pi * 0.12 * t)
    drone_out = drone_raw * drone_env * 0.35

    # -------------------------------------------------------------------------
    # 5. Master Stereo Bus Mix & Panning
    # -------------------------------------------------------------------------
    left = wind_l + buffet_shaking * 0.9 + horn_tone * 0.85 + drone_out
    right = wind_r + buffet_shaking * 1.05 + horn_tone * 0.85 + drone_out

    # Global envelope: fast attack, smooth decay at CTA end
    envelope = np.ones(num_samples)
    # 0.15s attack
    attack_samples = int(0.15 * fs)
    envelope[:attack_samples] = np.linspace(0.0, 1.0, attack_samples)
    # 1.5s release at the end
    release_samples = int(1.5 * fs)
    envelope[-release_samples:] = np.linspace(1.0, 0.05, release_samples)

    left *= envelope
    right *= envelope

    # Soft master limiter
    peak = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-6)
    if peak > 0.92:
        left = np.tanh(left * (0.92 / peak))
        right = np.tanh(right * (0.92 / peak))

    # Convert to 16-bit PCM
    left_int16 = (np.clip(left, -0.98, 0.98) * 32767.0).astype(np.int16)
    right_int16 = (np.clip(right, -0.98, 0.98) * 32767.0).astype(np.int16)
    stereo_data = np.stack([left_int16, right_int16], axis=-1)

    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(str(out_file), fs, stereo_data)
    print(f"[CONTINUUM LAB] Aerodynamic Stall Audio Synthesized: {out_file} ({duration:.1f}s @ {fs} Hz)")
    return str(out_file)


if __name__ == "__main__":
    synthesize_stall_audio(duration=18.0, output_path="test_stall_audio.wav")
