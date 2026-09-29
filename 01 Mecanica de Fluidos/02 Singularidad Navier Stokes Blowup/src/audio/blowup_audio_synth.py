"""
Continuum Lab — Procedural Hydro-Acoustic Audio Engine
Module: 01 Mecanica de Fluidos / 02 Singularidad Navier Stokes Blowup
Acoustic Design: Fluid Vortex Acceleration, Pulse Wave Resonance & Pressure Eye Implosion

Layers:
  1. Vortex Spin-up Tone: Accelerating harmonic shear frequency tracking omega_max(t).
  2. Implosive Sub-bass Drone: Deep 45-55 Hz foundation modulated by central pressure depth.
  3. Dynamic Hydrodynamic Noise: Pink noise shaped by radial inflow and axial jetting.
  4. Annular Pulse Packets: Stereo ping-pong high-frequency wave bursts (sigma = +/-1).
  5. Cinematic Ambient Pad: Dm9 -> Bbmaj7 -> Gm9 -> Dsus4 progression evoking deep physics mystery.
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


def synthesize_blowup_audio(
    duration: float = 18.5,
    fs: int = 44100,
    output_path: str = "navier_stokes_blowup_audio.wav"
) -> str:
    num_samples = int(duration * fs)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    progress = t / duration

    # -------------------------------------------------------------------------
    # 1. Vortex Spin-Up Tone: Tracks physical vortex acceleration
    # -------------------------------------------------------------------------
    # Frequency ramps from 85 Hz to 520 Hz following power law
    f_inst = 85.0 + 435.0 * (progress**2.1)
    phase_spin = 2.0 * np.pi * np.cumsum(f_inst) / fs

    # Harmonics (fundamental + 2nd + 3rd + 4th)
    vortex_tone = (
        0.30 * np.sin(phase_spin) +
        0.18 * np.sin(2.0 * phase_spin + 0.3) +
        0.10 * np.sin(3.0 * phase_spin + 0.7) +
        0.05 * np.sin(4.0 * phase_spin + 1.1)
    )
    # Gentle amplitude swell toward the climax
    amp_spin = 0.20 + 0.40 * (progress**1.6)
    vortex_l = vortex_tone * amp_spin * (0.8 + 0.2 * np.sin(2.0 * np.pi * 0.4 * t))
    vortex_r = vortex_tone * amp_spin * (0.8 - 0.2 * np.sin(2.0 * np.pi * 0.4 * t))

    # -------------------------------------------------------------------------
    # 2. Implosive Sub-Bass Drone (Pressure Crater Eye)
    # -------------------------------------------------------------------------
    f_sub = 46.0 + 8.0 * np.sin(2.0 * np.pi * 0.15 * t)
    phase_sub = 2.0 * np.pi * np.cumsum(f_sub) / fs
    sub_drone = np.sin(phase_sub) * (0.35 + 0.25 * (progress**1.8))
    # Soft saturation for warm low-end harmonics
    sub_drone = np.tanh(sub_drone * 1.5) * 0.28

    # -------------------------------------------------------------------------
    # 3. Hydrodynamic Inflow & Swirling Noise (Filtered Pink Noise)
    # -------------------------------------------------------------------------
    raw_pink_l = generate_pink_noise(num_samples)
    raw_pink_r = generate_pink_noise(num_samples)

    # Dynamic filter that opens up over time
    flow_l = bandpass_filter(raw_pink_l, 180, 1600, fs, order=2) * (0.16 + 0.20 * progress)
    flow_r = bandpass_filter(raw_pink_r, 220, 1800, fs, order=2) * (0.16 + 0.20 * progress)

    # -------------------------------------------------------------------------
    # 4. Annular Pulse Packets (Wave Stresses sigma = +/- 1)
    # -------------------------------------------------------------------------
    pulses_l = np.zeros(num_samples)
    pulses_r = np.zeros(num_samples)

    # Burst intervals throughout the 18s timeline
    pulse_times = np.linspace(1.5, 17.0, 14)
    for i, pt in enumerate(pulse_times):
        idx = int(pt * fs)
        p_len = int(0.18 * fs)
        if idx + p_len < num_samples:
            tp = np.linspace(0, 0.18, p_len, endpoint=False)
            fp = 850.0 + 350.0 * (pt / duration)
            pulse_env = np.sin(np.pi * tp / 0.18)**2
            pulse_sig = np.sin(2.0 * np.pi * fp * tp) * pulse_env * 0.14
            if i % 2 == 0:
                pulses_l[idx:idx + p_len] += pulse_sig * 1.2
                pulses_r[idx:idx + p_len] += pulse_sig * 0.3
            else:
                pulses_l[idx:idx + p_len] += pulse_sig * 0.3
                pulses_r[idx:idx + p_len] += pulse_sig * 1.2

    # -------------------------------------------------------------------------
    # 5. Cinematic Ambient Pad (Dm9 -> Bbmaj7 -> Gm9 -> Dsus4)
    # -------------------------------------------------------------------------
    chord_times = [0.0, 4.5, 9.0, 13.5, 18.5]
    chords = [
        [146.83, 220.00, 261.63, 293.66, 329.63],  # Dm9 (D3, A3, C4, D4, E4)
        [116.54, 174.61, 220.00, 261.63, 293.66],  # Bbmaj7 (Bb2, F3, A3, C4, D4)
        [98.00, 146.83, 196.00, 220.00, 293.66],   # Gm9 (G2, D3, G3, A3, D4)
        [146.83, 220.00, 293.66, 392.00]           # Dsus4 (D3, A3, D4, G4)
    ]

    pad_l = np.zeros(num_samples)
    pad_r = np.zeros(num_samples)

    for i in range(len(chords)):
        t_start = chord_times[i]
        t_end = chord_times[i + 1]
        mask = (t >= t_start) & (t < t_end)
        t_segment = t[mask] - t_start
        dur_seg = t_end - t_start

        env = np.sin(np.pi * t_segment / dur_seg) ** 1.3
        chord_wave_l = np.zeros(len(t_segment))
        chord_wave_r = np.zeros(len(t_segment))

        for note_f in chords[i]:
            detune = 1.002
            chord_wave_l += np.sin(2.0 * np.pi * note_f * t_segment) * 0.05
            chord_wave_r += np.sin(2.0 * np.pi * (note_f * detune) * t_segment) * 0.05

        pad_l[mask] += chord_wave_l * env
        pad_r[mask] += chord_wave_r * env

    pad_l = bandpass_filter(pad_l, 80, 2500, fs, order=2)
    pad_r = bandpass_filter(pad_r, 80, 2500, fs, order=2)

    # -------------------------------------------------------------------------
    # 6. Master Mix & Soft Limiter
    # -------------------------------------------------------------------------
    # Fade in / Fade out
    fade_len = int(0.3 * fs)
    fade_in = np.linspace(0, 1, fade_len)
    fade_out = np.linspace(1, 0, fade_len)

    master_l = vortex_l + sub_drone + flow_l + pulses_l + pad_l
    master_r = vortex_r + sub_drone + flow_r + pulses_r + pad_r

    master_l[:fade_len] *= fade_in
    master_r[:fade_len] *= fade_in
    master_l[-fade_len:] *= fade_out
    master_r[-fade_len:] *= fade_out

    # Soft limiter (tanh saturation)
    peak = max(np.max(np.abs(master_l)), np.max(np.abs(master_r)), 1e-6)
    master_l = np.tanh((master_l / peak) * 1.1) * 0.92
    master_r = np.tanh((master_r / peak) * 1.1) * 0.92

    # Convert to 16-bit PCM
    stereo_data = np.vstack([master_l, master_r]).T
    stereo_int16 = (stereo_data * 32767).astype(np.int16)

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(output_path, fs, stereo_int16)
    print(f"[CONTINUUM LAB] Hydro-acoustic procedural audio saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    synthesize_blowup_audio(duration=18.5, output_path="test_blowup_audio.wav")
