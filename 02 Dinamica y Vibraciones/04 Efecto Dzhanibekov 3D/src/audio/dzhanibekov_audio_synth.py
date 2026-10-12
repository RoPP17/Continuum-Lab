"""
Procedural Spacecraft Audio Engine — Dzhanibekov Effect 3D
Module: 02 Dinamica y Vibraciones / 04 Efecto Dzhanibekov 3D

Acoustic Architecture:
  1. Microgravity Station Drone: Low-frequency 60 Hz hum with space station ventilation hiss.
  2. Intermediate Axis Spin Tone: Harmonic rotational whistle (~115 Hz fundamental + 230 Hz harmonic).
  3. Homoclinic Inversion Whooshes: Dramatic pitch slides and Doppler sweeps during the two 180° flips:
     - Flip 1: t ~ 3.5s - 5.2s
     - Flip 2: t ~ 8.8s - 10.5s
  4. Vector Phase Shockwave: Sub-bass resonance pulse upon completing each 180° flip.
"""

import numpy as np
from scipy.io import wavfile
from pathlib import Path


def synthesize_dzhanibekov_audio(
    duration: float = 14.0,
    fs: int = 44100,
    output_path: str = "dzhanibekov_audio.wav"
) -> str:
    n_samples = int(duration * fs)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    # 1. Microgravity Station Ambience (60 Hz hum + gentle stereo ventilation)
    station_hum = (
        0.18 * np.sin(2.0 * np.pi * 60.0 * t) +
        0.08 * np.sin(2.0 * np.pi * 120.0 * t) +
        0.04 * np.sin(2.0 * np.pi * 180.0 * t)
    )

    # Ventilation noise
    noise = np.random.randn(n_samples) * 0.035

    # 2. Rotational Spin Whine (Body spin rate ~ 1.9 Hz modulation)
    # The intermediate axis spins rapidly with ~12 rad/s (1.91 rev/s)
    spin_freq = 115.0  # Hz base acoustic tone
    spin_carrier = (
        0.20 * np.sin(2.0 * np.pi * spin_freq * t) +
        0.12 * np.sin(2.0 * np.pi * (spin_freq * 2.0) * t)
    )
    # Rhythmic pulse corresponding to T-handle wing passing
    spin_pulse = 0.75 + 0.25 * np.cos(2.0 * np.pi * 1.91 * 2.0 * t)
    spin_audio = spin_carrier * spin_pulse

    # 3. Dynamic Homoclinic Flips (Pitch-slide whooshes)
    # Flip 1: centered at t = 4.3s, Flip 2: centered at t = 9.6s
    def flip_whoosh(center_t, dur=1.8):
        dt = t - center_t
        env = np.exp(-(dt ** 2) / (2.0 * (dur / 3.0) ** 2))
        # Pitch descends and rises through singularity
        f_inst = 220.0 + 380.0 * np.sin(np.pi * (dt / dur + 0.5)) * env
        phase = 2.0 * np.pi * np.cumsum(np.clip(f_inst, 60.0, 800.0)) / fs
        whoosh_carrier = np.sin(phase) + 0.5 * np.sin(phase * 1.5)
        # Deep sub-bass pulse at center
        sub_pulse = np.sin(2.0 * np.pi * 48.0 * dt) * np.exp(-abs(dt) * 4.0)
        return whoosh_carrier * env * 0.35 + sub_pulse * 0.40

    flip1 = flip_whoosh(4.35)
    flip2 = flip_whoosh(9.65)

    # 4. Composite Stereo Mix
    left_channel = station_hum * 0.4 + noise + spin_audio * 0.35 + flip1 * 0.5 + flip2 * 0.45
    right_channel = station_hum * 0.4 + noise + spin_audio * 0.35 + flip1 * 0.45 + flip2 * 0.5

    # Master envelope
    fade_in = np.clip(t / 0.5, 0.0, 1.0)
    fade_out = np.clip((duration - t) / 0.8, 0.0, 1.0)
    left_channel = left_channel * fade_in * fade_out
    right_channel = right_channel * fade_in * fade_out

    # Normalize to -1.0 dB
    peak = max(np.max(np.abs(left_channel)), np.max(np.abs(right_channel))) + 1e-8
    left_channel = (left_channel / peak) * 0.88
    right_channel = (right_channel / peak) * 0.88

    left_int16 = (left_channel * 32767.0).astype(np.int16)
    right_int16 = (right_channel * 32767.0).astype(np.int16)
    stereo = np.column_stack((left_int16, right_int16))

    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(str(out_file), fs, stereo)
    return str(out_file)


if __name__ == "__main__":
    synthesize_dzhanibekov_audio(14.0, 44100, "test_dzhanibekov.wav")
    print("Synthesized Dzhanibekov audio successfully.")
