"""
Continuum Lab - Master Cinematic Audio Synthesizer: Vortex Rings Collision & Reconnection
Module: 01 Mecanica de Fluidos / 07 Colision de Anillos de Vortice
File: src/audio/vortex_collision_audio.py

Produces 44.1 kHz 16-bit Stereo PCM Audio:
  - Dual hydrodynamic approach whoosh & rising resonant filter cutoff
  - Sub-bass cavitation impact hit at collision (t = 3.2s)
  - Secondary topological reconnection snap at t = 5.8s
  - 12 circularly panned celesta chimes (representing the 12 secondary baby rings)
  - Deep F-minor ambient synthesizer pad modulated by enstrophy
  - Seamless loop fade envelope for infinite replay
"""

import os
import wave
import numpy as np


def generate_vortex_collision_audio(output_wav: str, duration: float = 16.0, sample_rate: int = 44100):
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    rng = np.random.default_rng(2026)

    # 1. Hydrodynamic Pink Noise Rush (Approach of two vortex rings)
    # Filter cutoff modulates from 80 Hz to 450 Hz during approach (0 to 3.5s)
    white_noise = rng.uniform(-1.0, 1.0, n_samples)
    # Simple IIR low-pass filter approximation for pink noise
    b0 = 0.05
    pink = np.zeros(n_samples)
    for i in range(1, n_samples):
        pink[i] = pink[i-1] + b0 * (white_noise[i] - pink[i-1])

    # Filter envelope: swells up to t = 3.5s and then during reconnection t = 5.8s
    flow_envelope = np.zeros(n_samples)
    for i in range(n_samples):
        ti = t[i]
        if ti < 3.2:
            flow_envelope[i] = 0.15 + 0.65 * (ti / 3.2)**2
        elif ti < 6.0:
            flow_envelope[i] = 0.80 - 0.35 * ((ti - 3.2) / 2.8)
        elif ti < 12.0:
            flow_envelope[i] = 0.45 + 0.20 * np.sin(np.pi * (ti - 6.0) / 6.0)
        else:
            flow_envelope[i] = 0.35 * (1.0 - (ti - 12.0) / 4.0)

    hydro_rush = pink * flow_envelope * 0.45

    # 2. Sub-bass Tension Drone (45 Hz -> 75 Hz)
    freq_drone = 48.0 + 26.0 * np.clip(t / 3.5, 0.0, 1.0)
    phase_drone = 2.0 * np.pi * np.cumsum(freq_drone) / sample_rate
    sub_drone = 0.26 * np.sin(phase_drone) + 0.10 * np.sin(2.0 * phase_drone)
    sub_drone = np.tanh(sub_drone * 1.6)

    # 3. Collision Impact Hit at t = 3.2s
    hit = np.zeros(n_samples)
    hit_idx = int(3.2 * sample_rate)
    hit_dur = int(0.75 * sample_rate)
    if hit_idx + hit_dur < n_samples:
        ht = np.linspace(0, 0.75, hit_dur)
        punch = np.sin(2.0 * np.pi * 55.0 * np.exp(-ht * 5.0) * ht) * np.exp(-ht * 4.5)
        metallic = np.sin(2.0 * np.pi * 480.0 * ht) * np.exp(-ht * 9.0)
        hit[hit_idx:hit_idx + hit_dur] += 0.58 * punch + 0.32 * metallic

    # 4. Topological Reconnection Snap at t = 5.8s
    snap = np.zeros(n_samples)
    snap_idx = int(5.8 * sample_rate)
    snap_dur = int(0.60 * sample_rate)
    if snap_idx + snap_dur < n_samples:
        st = np.linspace(0, 0.60, snap_dur)
        crack = np.sin(2.0 * np.pi * 840.0 * st) * np.exp(-st * 12.0)
        sub_crack = np.sin(2.0 * np.pi * 70.0 * np.exp(-st * 6.0) * st) * np.exp(-st * 5.0)
        snap[snap_idx:snap_idx + snap_dur] += 0.42 * crack + 0.38 * sub_crack

    # 5. 12 Rotating Spatial Celesta Chimes (Secondary Vortex Crown m = 12)
    # Plays cascading notes as the 12 secondary rings reconnect and shoot outward
    bells_l = np.zeros(n_samples)
    bells_r = np.zeros(n_samples)
    bell_freqs = [
        659.25, 783.99, 880.00, 987.77, 1046.50, 1174.66,
        1318.51, 1396.91, 1567.98, 1760.00, 1975.53, 2093.00
    ]  # E5 to C7
    for k in range(12):
        bell_time = 5.85 + k * 0.18  # Rapid cascading arpeggio
        b_idx = int(bell_time * sample_rate)
        b_dur = int(0.95 * sample_rate)
        if b_idx + b_dur < n_samples:
            bt_arr = np.linspace(0, 0.95, b_dur)
            bf = bell_freqs[k]
            bell_sound = np.sin(2.0 * np.pi * bf * bt_arr) * np.exp(-bt_arr * 4.2)
            # Circular stereo panning: pan = cos(2*pi*k/12)
            pan_k = np.cos(2.0 * np.pi * k / 12.0)
            gain_l = np.sqrt(0.5 * (1.0 - pan_k))
            gain_r = np.sqrt(0.5 * (1.0 + pan_k))
            bells_l[b_idx:b_idx + b_dur] += 0.16 * bell_sound * gain_l
            bells_r[b_idx:b_idx + b_dur] += 0.16 * bell_sound * gain_r

    # 6. Ambient Synthesizer Pad (F minor: F3=174.61, Ab3=207.65, C4=261.63, Eb4=311.13)
    pad = np.zeros(n_samples)
    pad_freqs = [174.61, 207.65, 261.63, 311.13]
    for pf in pad_freqs:
        vib = 1.0 + 0.003 * np.sin(2.0 * np.pi * 3.2 * t)
        phase_pf = 2.0 * np.pi * pf * np.cumsum(vib) / sample_rate
        pad += 0.065 * np.sin(phase_pf)

    # Pad swells when rings expand (t in [3.0, 13.5])
    pad_env = np.zeros(n_samples)
    for i in range(n_samples):
        ti = t[i]
        if 3.0 <= ti <= 8.5:
            pad_env[i] = np.sin(np.pi * (ti - 3.0) / (2.0 * 5.5)) ** 2
        elif 8.5 < ti <= 14.5:
            pad_env[i] = np.cos(np.pi * (ti - 8.5) / (2.0 * 6.0)) ** 2
    pad *= pad_env

    # Haas stereo widening for pad
    pad_stereo_offset = int(0.018 * sample_rate)
    pad_r = np.roll(pad, pad_stereo_offset)

    # Combine mono stems
    center_stem = hydro_rush + sub_drone + hit + snap

    left_raw = center_stem * 0.70 + bells_l + pad * 0.85
    right_raw = center_stem * 0.70 + bells_r + pad_r * 0.85

    # 7. Seamless Loop Fade (0.08s at boundaries)
    fade_len = int(0.08 * sample_rate)
    fade_in = np.linspace(0.0, 1.0, fade_len)
    fade_out = np.linspace(1.0, 0.0, fade_len)

    left_raw[:fade_len] *= fade_in
    left_raw[-fade_len:] *= fade_out
    right_raw[:fade_len] *= fade_in
    right_raw[-fade_len:] *= fade_out

    # Master Limiter & 16-bit Normalization
    peak = max(np.max(np.abs(left_raw)), np.max(np.abs(right_raw)), 1e-5)
    left_int16 = np.int16(np.clip(left_raw / peak * 0.92, -0.98, 0.98) * 32767)
    right_int16 = np.int16(np.clip(right_raw / peak * 0.92, -0.98, 0.98) * 32767)

    out_dir = os.path.dirname(output_wav)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with wave.open(output_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)

        stereo = np.empty((n_samples * 2,), dtype=np.int16)
        stereo[0::2] = left_int16
        stereo[1::2] = right_int16
        wf.writeframes(stereo.tobytes())

    print(f"[+] Master cinematic audio created: {output_wav}")
    return output_wav


if __name__ == "__main__":
    generate_vortex_collision_audio("test_vortex_audio.wav")
