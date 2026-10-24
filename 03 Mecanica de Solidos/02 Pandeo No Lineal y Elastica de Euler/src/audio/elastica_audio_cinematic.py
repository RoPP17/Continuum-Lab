"""
Continuum Lab - Master Cinematic Audio Synthesizer for Euler's Nonlinear Elastica
Module: 03 Mecanica de Solidos / 02 Pandeo No Lineal y Elastica de Euler
File: src/audio/elastica_audio_cinematic.py

Produces 44.1 kHz 16-bit Stereo PCM Audio:
  - Sub-bass tension riser (45 Hz -> 85 Hz)
  - Accelerating mechanical pulse ticks leading up to critical bifurcation
  - Kinetic mechanical snap / acoustic impact at P = P_cr (t = 2.5s)
  - Cyberpunk ambient resonant chords (D minor9) modulated by beam curvature
  - Spatial stereo panning synchronized to lateral beam deflection
  - Seamless loop envelope for continuous replay
"""

import os
import wave
import numpy as np


def generate_cinematic_elastica_audio(output_wav: str, duration: float = 16.0, sample_rate: int = 44100):
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    # Kinematic timeline:
    # 0.0 - 2.5s: Pre-critical compression (P/P_cr from 0.2 to 1.0)
    # 2.5 - 7.5s: Buckling ramp to alpha = 82 deg (P/P_cr ~ 1.5)
    # 7.5 - 9.5s: Extreme deflection hold
    # 9.5 - 12.5s: Symmetry transition to negative branch (alpha = -55 deg)
    # 12.5 - 16.0s: Return to straight neutral state

    # 1. Base Sub-bass Drone
    # Frequency ramps slightly as compression increases
    freq_drone = 50.0 + 35.0 * np.clip(t / 2.5, 0.0, 1.0)
    phase_drone = 2.0 * np.pi * np.cumsum(freq_drone) / sample_rate
    drone = 0.28 * np.sin(phase_drone) + 0.12 * np.sin(2.0 * phase_drone)
    # Soft saturation
    drone = np.tanh(drone * 1.5)

    # 2. Tension Acceleration Ticks (leading up to t = 2.5s)
    ticks = np.zeros(n_samples)
    tick_times = [0.3, 0.8, 1.3, 1.7, 2.0, 2.2, 2.35, 2.45]
    for tt in tick_times:
        idx = int(tt * sample_rate)
        tick_len = int(0.025 * sample_rate)
        if idx + tick_len < n_samples:
            decay = np.exp(-np.linspace(0, 15, tick_len))
            tick_wave = np.sin(2.0 * np.pi * 1200.0 * np.linspace(0, 0.025, tick_len)) * decay
            ticks[idx:idx + tick_len] += 0.22 * tick_wave

    # 3. Critical Bifurcation Snap at t = 2.5s (Impact Hit)
    snap = np.zeros(n_samples)
    snap_idx = int(2.5 * sample_rate)
    snap_dur = int(0.8 * sample_rate)
    if snap_idx + snap_dur < n_samples:
        st = np.linspace(0, 0.8, snap_dur)
        # Low punch (65 Hz) + Metallic mid (520 Hz) + Noise burst
        punch = np.sin(2.0 * np.pi * 65.0 * np.exp(-st * 4.0) * st) * np.exp(-st * 5.0)
        metallic = np.sin(2.0 * np.pi * 520.0 * st) * np.exp(-st * 8.0)
        noise = (np.random.default_rng(42).uniform(-1, 1, snap_dur)) * np.exp(-st * 16.0)
        snap[snap_idx:snap_idx + snap_dur] = 0.55 * punch + 0.35 * metallic + 0.25 * noise

    # 4. Secondary Symmetry Snap at t = 10.5s (Branch Crossing)
    snap2_idx = int(10.5 * sample_rate)
    snap2_dur = int(0.5 * sample_rate)
    if snap2_idx + snap2_dur < n_samples:
        st2 = np.linspace(0, 0.5, snap2_dur)
        metallic2 = np.sin(2.0 * np.pi * 680.0 * st2) * np.exp(-st2 * 9.0)
        punch2 = np.sin(2.0 * np.pi * 75.0 * np.exp(-st2 * 5.0) * st2) * np.exp(-st2 * 6.0)
        snap[snap2_idx:snap2_idx + snap2_dur] += 0.40 * metallic2 + 0.30 * punch2

    # 5. Ambient Resonant Chords (D minor9: D3=146.83, F3=174.61, A3=220.00, C4=261.63, E4=329.63)
    # Swells when beam is bent (from t = 2.6 to 14.5)
    pad_envelope = np.zeros(n_samples)
    for i in range(n_samples):
        ti = t[i]
        if 2.5 <= ti <= 9.0:
            pad_envelope[i] = np.sin(np.pi * (ti - 2.5) / (2.0 * 6.5)) ** 2
        elif 9.0 < ti <= 14.5:
            pad_envelope[i] = np.cos(np.pi * (ti - 9.0) / (2.0 * 5.5)) ** 2

    chord_freqs = [146.83, 174.61, 220.00, 261.63, 329.63]
    pad = np.zeros(n_samples)
    for cf in chord_freqs:
        # Subtle detuning and slow vibrato
        vibrato = 1.0 + 0.003 * np.sin(2.0 * np.pi * 3.5 * t)
        phase_cf = 2.0 * np.pi * cf * np.cumsum(vibrato) / sample_rate
        pad += 0.07 * np.sin(phase_cf)
    pad *= pad_envelope

    # 6. High-Frequency Harmonic Celesta Bells (at inflection moments: t = 5.0, 7.5, 11.5)
    bells = np.zeros(n_samples)
    bell_times = [5.0, 7.5, 11.5]
    bell_freqs = [1046.5, 1318.5, 1567.98]  # C6, E6, G6
    for bt, bf in zip(bell_times, bell_freqs):
        b_idx = int(bt * sample_rate)
        b_len = int(1.2 * sample_rate)
        if b_idx + b_len < n_samples:
            bt_arr = np.linspace(0, 1.2, b_len)
            b_wave = np.sin(2.0 * np.pi * bf * bt_arr) * np.exp(-bt_arr * 3.5)
            bells[b_idx:b_idx + b_len] += 0.18 * b_wave

    # 7. Spatial Panning Profile (Beam bows right, then left, then centers)
    # Pan: -1.0 (hard left) to +1.0 (hard right)
    pan = np.zeros(n_samples)
    for i in range(n_samples):
        ti = t[i]
        if 2.5 <= ti <= 8.5:
            pan[i] = 0.55 * np.sin(np.pi * (ti - 2.5) / 6.0)
        elif 8.5 < ti <= 13.0:
            pan[i] = -0.45 * np.sin(np.pi * (ti - 8.5) / 4.5)
        else:
            pan[i] = 0.0

    # Combine into Left and Right channels
    # Left channel = (1 - pan)/2, Right channel = (1 + pan)/2
    gain_l = np.sqrt(0.5 * (1.0 - pan))
    gain_r = np.sqrt(0.5 * (1.0 + pan))

    mono_core = drone + ticks + snap + pad + bells

    # Add stereo chorus widening to ambient pad
    pad_stereo_offset = int(0.015 * sample_rate)  # 15 ms Haas effect
    pad_r = np.roll(pad, pad_stereo_offset)

    left_raw = (drone + ticks + snap + bells) * gain_l + pad * 0.75
    right_raw = (drone + ticks + snap + bells) * gain_r + pad_r * 0.75

    # 8. Seamless Loop Enveloping (Fade at extreme 0.08s edges to prevent any pop on loop)
    loop_fade_len = int(0.08 * sample_rate)
    loop_in = np.linspace(0.0, 1.0, loop_fade_len)
    loop_out = np.linspace(1.0, 0.0, loop_fade_len)

    left_raw[:loop_fade_len] *= loop_in
    left_raw[-loop_fade_len:] *= loop_out
    right_raw[:loop_fade_len] *= loop_in
    right_raw[-loop_fade_len:] *= loop_out

    # Master Limiter / Normalization
    peak = max(np.max(np.abs(left_raw)), np.max(np.abs(right_raw)), 1e-6)
    left_norm = np.int16(np.clip(left_raw / peak * 0.92, -0.98, 0.98) * 32767)
    right_norm = np.int16(np.clip(right_raw / peak * 0.92, -0.98, 0.98) * 32767)

    os.makedirs(os.path.dirname(output_wav), exist_ok=True)
    with wave.open(output_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)

        stereo = np.empty((n_samples * 2,), dtype=np.int16)
        stereo[0::2] = left_norm
        stereo[1::2] = right_norm
        wf.writeframes(stereo.tobytes())

    print(f"[+] Master cinematic audio created: {output_wav} ({duration:.1f}s @ {sample_rate}Hz stereo)")
    return output_wav


if __name__ == "__main__":
    test_wav = "output/test_cinematic_audio.wav"
    generate_cinematic_elastica_audio(test_wav)
