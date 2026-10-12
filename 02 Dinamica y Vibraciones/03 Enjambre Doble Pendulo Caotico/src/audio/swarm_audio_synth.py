"""
Hypnotic & Catchy Procedural Audio Engine — Chaotic Double Pendulum
Module: 02 Dinamica y Vibraciones / 03 Enjambre Doble Pendulo Caotico

Acoustic Architecture (Viral Retention Optimized):
  1. Phase 1 (t = 0..2.5s): Hypnotic ASMR Pendulum Ticks (120 BPM) + Deep D-Minor Ambient Pad + Sub Riser.
  2. The Drop (t = 2.5s): Cinematic Sub-Bass Drop + Crystalline Chime marking the Double Pendulum creation.
  3. Phase 2 & 3 (t = 2.5..15s): Addictive Synthwave Arpeggio (Dm - Bb - F - A) + Pulsing Cyber Bassline + Stereo Delay.
  4. Chaotic Polyphonic Shimmer: 16 stereo micro-voices mapping the 50-pendulum Lyapunov divergence.
"""

import numpy as np
from scipy.io import wavfile
from pathlib import Path


def synthesize_swarm_audio(
    duration: float = 15.0,
    fs: int = 44100,
    output_path: str = "swarm_audio.wav"
) -> str:
    n_samples = int(duration * fs)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    left = np.zeros(n_samples)
    right = np.zeros(n_samples)

    # =========================================================================
    # 1. METRÓNOMO HIPNÓTICO / TICKS ASMR DEL PÉNDULO SIMPLE (0 a 2.5s)
    # =========================================================================
    for tick_t in [0.0, 0.5, 1.0, 1.5, 2.0]:
        idx = int(tick_t * fs)
        dur_tk = int(0.08 * fs)
        if idx + dur_tk < n_samples:
            t_tk = np.linspace(0, 0.08, dur_tk)
            env = np.exp(-t_tk / 0.015)
            tk = (
                np.sin(2 * np.pi * 880.0 * t_tk) * 0.4 +
                np.sin(2 * np.pi * 1760.0 * t_tk) * 0.2 +
                np.sin(2 * np.pi * 130.81 * t_tk) * 0.8
            ) * env
            left[idx : idx + dur_tk] += tk * 0.35
            right[idx : idx + dur_tk] += tk * 0.35

    # =========================================================================
    # 2. PAD ANALÓGICO PROFUNDO (Re menor / Cybernetic Void)
    # =========================================================================
    pad = (
        0.18 * np.sin(2 * np.pi * 73.42 * t) +   # D2
        0.14 * np.sin(2 * np.pi * 146.83 * t) +  # D3
        0.10 * np.sin(2 * np.pi * 220.0 * t) +   # A3
        0.07 * np.sin(2 * np.pi * 349.23 * t)    # F4
    )
    left += pad * 0.42
    right += pad * 0.42

    # =========================================================================
    # 3. RISER CINEMATOGRÁFICO DE TENSIÓN (1.7s a 2.5s)
    # =========================================================================
    idx_r1 = int(1.7 * fs)
    idx_r2 = int(2.5 * fs)
    t_r = np.linspace(0, 0.8, idx_r2 - idx_r1)
    f_r = np.linspace(160.0, 780.0, len(t_r))
    phi_r = 2 * np.pi * np.cumsum(f_r) / fs
    riser = np.sin(phi_r) * (np.linspace(0, 1.0, len(t_r)) ** 2.2) * 0.28
    left[idx_r1:idx_r2] += riser * 0.85
    right[idx_r1:idx_r2] += riser * 1.0

    # =========================================================================
    # 4. IMPACTO DEL DROP A LOS 2.5s (CREACIÓN DEL PÉNDULO DOBLE)
    # =========================================================================
    idx_drop = int(2.5 * fs)
    dur_imp = int(0.85 * fs)
    t_imp = np.linspace(0, 0.85, dur_imp)
    f_imp = 140.0 * np.exp(-t_imp / 0.16) + 40.0
    phi_imp = 2 * np.pi * np.cumsum(f_imp) / fs
    sub_drop = np.sin(phi_imp) * np.exp(-t_imp / 0.20) * 0.75
    chime = (
        np.sin(2 * np.pi * 1174.66 * t_imp) +
        0.5 * np.sin(2 * np.pi * 2349.32 * t_imp) +
        0.3 * np.sin(2 * np.pi * 3520.0 * t_imp)
    ) * np.exp(-t_imp / 0.10) * 0.40
    impact = sub_drop + chime
    left[idx_drop : idx_drop + dur_imp] += impact * 0.95
    right[idx_drop : idx_drop + dur_imp] += impact * 0.95

    # =========================================================================
    # 5. ARPEGIADOR SINTETIZADOR HIPNÓTICO Y PEGAJOSO (2.5s a 15.0s)
    # Patrón melódico en semicorcheas (120 BPM): Dm -> Bb -> F -> A
    # =========================================================================
    notes = [
        293.66, 349.23, 440.00, 523.25, 587.33, 523.25, 440.00, 349.23,  # Dm
        392.00, 466.16, 587.33, 698.46, 659.25, 523.25, 440.00, 349.23   # Bb - F - A
    ]
    note_dur = 0.125  # 16th note a 120 BPM
    n_notes_total = int((duration - 2.5) / note_dur)

    arp_raw = np.zeros(n_samples)
    for n_idx in range(n_notes_total):
        t_start = 2.5 + n_idx * note_dur
        if t_start >= duration:
            break
        idx_s = int(t_start * fs)
        freq = notes[n_idx % len(notes)]
        dur_n = int(note_dur * 1.35 * fs)
        if idx_s + dur_n > n_samples:
            dur_n = n_samples - idx_s
        t_n = np.linspace(0, dur_n / fs, dur_n)
        env_n = np.exp(-t_n / 0.055)
        wave = (
            np.sin(2 * np.pi * freq * t_n) +
            0.45 * np.sin(2 * np.pi * 2 * freq * t_n) +
            0.18 * np.sin(2 * np.pi * 3 * freq * t_n)
        ) * env_n
        arp_raw[idx_s : idx_s + dur_n] += wave * 0.32

    # Paneo dinámico y estéreo
    pan_l = 0.65 + 0.30 * np.sin(2 * np.pi * 1.5 * t)
    pan_r = 0.65 - 0.30 * np.sin(2 * np.pi * 1.5 * t)
    left += arp_raw * pan_l
    right += arp_raw * pan_r

    # Delay Ping-Pong espacial
    delay_samples = int(0.1875 * fs)
    del_l = np.roll(arp_raw, delay_samples) * 0.24
    del_l[:delay_samples] = 0.0
    del_r = np.roll(arp_raw, int(delay_samples * 1.5)) * 0.22
    del_r[: int(delay_samples * 1.5)] = 0.0
    left += del_r
    right += del_l

    # =========================================================================
    # 6. BASSLINE PULSANTE SUB-BASS (2.5s a 15.0s, corcheas en D2 / C2)
    # =========================================================================
    n_bass_beats = int((duration - 2.5) / 0.25)
    for b_idx in range(n_bass_beats):
        t_b = 2.5 + b_idx * 0.25
        idx_b = int(t_b * fs)
        dur_b = int(0.20 * fs)
        if idx_b + dur_b > n_samples:
            dur_b = n_samples - idx_b
        t_bass = np.linspace(0, dur_b / fs, dur_b)
        env_b = np.exp(-t_bass / 0.08)
        bass_freq = 73.42 if (b_idx % 8 < 6) else 65.41
        bass_wave = (
            np.sin(2 * np.pi * bass_freq * t_bass) +
            0.35 * np.sin(2 * np.pi * 2 * bass_freq * t_bass)
        ) * env_b
        left[idx_b : idx_b + dur_b] += bass_wave * 0.42
        right[idx_b : idx_b + dur_b] += bass_wave * 0.42

    # =========================================================================
    # 7. SHIMMER POLIFÓNICO DEL ENJAMBRE CAÓTICO (t > 3.5s)
    # =========================================================================
    chaos_prog = np.clip((t - 3.5) / 4.0, 0.0, 1.0) ** 1.6
    for idx_v in range(16):
        f_c = 440.0 * (2.0 ** ((idx_v - 8) / 12.0))
        detune = 4.0 * np.sin(2 * np.pi * (0.3 + 0.08 * idx_v) * t) * chaos_prog
        phi_c = 2 * np.pi * np.cumsum(f_c + detune) / fs
        pan_v = idx_v / 15.0
        voice_amp = 0.022 * chaos_prog * (1.0 + 0.35 * np.sin(2 * np.pi * 0.8 * t))
        left += np.sin(phi_c) * voice_amp * (1.0 - pan_v)
        right += np.sin(phi_c) * voice_amp * pan_v

    # =========================================================================
    # 8. MASTERIZACIÓN FINAL: ENVOLVENTES Y LIMITADOR / NORMALIZADOR
    # =========================================================================
    fade_in = np.clip(t / 0.15, 0.0, 1.0)
    fade_out = np.clip((duration - t) / 0.6, 0.0, 1.0)
    left = left * fade_in * fade_out
    right = right * fade_in * fade_out

    peak = max(np.max(np.abs(left)), np.max(np.abs(right))) + 1e-8
    left = (left / peak) * 0.90
    right = (right / peak) * 0.90

    l_int16 = (left * 32767.0).astype(np.int16)
    r_int16 = (right * 32767.0).astype(np.int16)
    stereo = np.column_stack((l_int16, r_int16))

    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(str(out_file), fs, stereo)
    return str(out_file)


if __name__ == "__main__":
    synthesize_swarm_audio(15.0, 44100, "test_swarm.wav")
    print("Hypnotic Swarm Audio synthesized successfully.")
