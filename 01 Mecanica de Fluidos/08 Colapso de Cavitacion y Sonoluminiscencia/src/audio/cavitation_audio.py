"""
Continuum Lab // 01 Mecánica de Fluidos
08 Colapso de Cavitación y Sonoluminiscencia (Rayleigh-Plesset & Keller-Miksis Singularity)

Módulo de Síntesis de Audio Procedural de Alta Fidelidad (44.1 kHz, 16-bit estéreo WAV).
Genera un paisaje sonoro inmersivo multicapa sincronizado fotograma a fotograma:
1. Sub-bass Drone hidrostático subacuático (35 Hz - 55 Hz).
2. Whoosh acelerado de colapso con chirp Doppler ascendente (100 Hz -> 1100 Hz).
3. Impacto de singularidad y caída de subgraves a 45 Hz en t = 7.20s.
4. Campana cristalina de picosegundos (4200 Hz, 6800 Hz) para el destello óptico de sonoluminiscencia.
5. Chasquido de choque supersónico (Kirkwood-Bethe) y estallido acústico.
6. Paneo estéreo binaural para el micro-jet axial de 1050 m/s.
"""

import numpy as np
import wave
import struct
import os


def generate_cavitation_audio(output_wav_path: str, duration: float = 16.0, sample_rate: int = 44100):
    total_samples = int(duration * sample_rate)
    t = np.linspace(0.0, duration, total_samples, endpoint=False)

    left_channel = np.zeros(total_samples, dtype=np.float64)
    right_channel = np.zeros(total_samples, dtype=np.float64)

    t_sing = 7.20  # Instante exacto del colapso y destello

    # -------------------------------------------------------------------------
    # CAPA 1: Drone Hidrostático Subacuático Profundo (38 Hz + 58 Hz)
    # -------------------------------------------------------------------------
    sub_drone = (
        0.28 * np.sin(2.0 * np.pi * 38.0 * t) +
        0.18 * np.sin(2.0 * np.pi * 58.0 * t) +
        0.08 * np.sin(2.0 * np.pi * 76.0 * t)
    )
    # Modulación sutil de amplitud (pulsación acústica de baja frecuencia)
    drone_lfo = 0.85 + 0.15 * np.sin(2.0 * np.pi * 0.5 * t)
    sub_drone *= drone_lfo

    left_channel += sub_drone * 0.95
    right_channel += sub_drone * 1.05

    # -------------------------------------------------------------------------
    # CAPA 2: Whoosh Acelerado de Colapso con Chirp Doppler (t: 3.0s -> 7.2s)
    # -------------------------------------------------------------------------
    mask_collapse = (t >= 3.0) & (t <= t_sing)
    t_c = t[mask_collapse] - 3.0
    dur_c = t_sing - 3.0  # 4.2 s
    tau_c = t_c / dur_c

    # Frecuencia exponencialmente creciente de 90 Hz a 950 Hz
    f_chirp = 90.0 * np.exp(tau_c * 2.35)
    phase_chirp = 2.0 * np.pi * np.cumsum(f_chirp) / sample_rate
    env_chirp = (tau_c**2.5) * 0.45

    noise_burst = (np.random.default_rng(101).uniform(-1.0, 1.0, len(t_c))) * (tau_c**3.0) * 0.25
    whoosh_signal = (np.sin(phase_chirp) + noise_burst) * env_chirp

    left_channel[mask_collapse] += whoosh_signal * 0.9
    right_channel[mask_collapse] += whoosh_signal * 1.1

    # -------------------------------------------------------------------------
    # CAPA 3: Impacto de Singularidad & Sub-Bass Drop a 45 Hz (t >= 7.20s)
    # -------------------------------------------------------------------------
    mask_impact = (t >= t_sing) & (t <= t_sing + 3.5)
    t_imp = t[mask_impact] - t_sing

    # Caída senoidal de graves con decaimiento exponencial
    f_impact = 48.0 * np.exp(-t_imp * 0.8)
    phase_impact = 2.0 * np.pi * np.cumsum(f_impact) / sample_rate
    env_impact = np.exp(-t_imp * 1.8) * 0.65
    impact_wave = np.sin(phase_impact) * env_impact

    left_channel[mask_impact] += impact_wave
    right_channel[mask_impact] += impact_wave

    # -------------------------------------------------------------------------
    # CAPA 4: Destello de Sonoluminiscencia (Campanas Cristalinas de Picosegundos)
    # Frecuencias altas brillantes: 4200 Hz, 6800 Hz, 9400 Hz
    # -------------------------------------------------------------------------
    mask_flash = (t >= t_sing) & (t <= t_sing + 2.8)
    t_fl = t[mask_flash] - t_sing

    ping_4200 = np.sin(2.0 * np.pi * 4200.0 * t_fl) * np.exp(-t_fl * 4.5) * 0.28
    ping_6800 = np.sin(2.0 * np.pi * 6800.0 * t_fl) * np.exp(-t_fl * 6.5) * 0.22
    ping_9400 = np.sin(2.0 * np.pi * 9400.0 * t_fl) * np.exp(-t_fl * 9.0) * 0.16

    flash_total = ping_4200 + ping_6800 + ping_9400
    left_channel[mask_flash] += flash_total * 1.05
    right_channel[mask_flash] += flash_total * 0.95

    # -------------------------------------------------------------------------
    # CAPA 5: Onda de Choque Acústica Supersónica (Crack de Cavitación)
    # -------------------------------------------------------------------------
    mask_shock = (t >= t_sing) & (t <= t_sing + 0.35)
    t_sh = t[mask_shock] - t_sing
    rng_shock = np.random.default_rng(202)
    shock_noise = rng_shock.uniform(-1.0, 1.0, len(t_sh)) * np.exp(-t_sh * 22.0) * 0.55

    left_channel[mask_shock] += shock_noise
    right_channel[mask_shock] += shock_noise

    # -------------------------------------------------------------------------
    # CAPA 6: Micro-Jet de Cavitación Axial con Paneo Dinámico (t: 7.3s -> 10.5s)
    # -------------------------------------------------------------------------
    mask_jet = (t >= t_sing + 0.1) & (t <= 10.5)
    t_jet = t[mask_jet] - (t_sing + 0.1)
    dur_jet = 10.5 - (t_sing + 0.1)

    f_jet = 320.0 - 180.0 * (t_jet / dur_jet)
    phase_jet = 2.0 * np.pi * np.cumsum(f_jet) / sample_rate
    env_jet = np.sin(np.pi * (t_jet / dur_jet)) * 0.22

    # Paneo estéreo descendente (izquierda a derecha)
    pan_l = 0.5 * (1.0 + np.cos(np.pi * (t_jet / dur_jet)))
    pan_r = 0.5 * (1.0 - np.cos(np.pi * (t_jet / dur_jet)))

    left_channel[mask_jet] += np.sin(phase_jet) * env_jet * pan_l
    right_channel[mask_jet] += np.sin(phase_jet) * env_jet * pan_r

    # -------------------------------------------------------------------------
    # MASTERIZACIÓN, LIMITADOR SUAVE Y EXPORTACIÓN A WAV (16-bit PCM)
    # -------------------------------------------------------------------------
    # Fade in / Fade out de 0.25 s para bucle suave
    fade_len = int(0.25 * sample_rate)
    fade_in = np.linspace(0.0, 1.0, fade_len)
    fade_out = np.linspace(1.0, 0.0, fade_len)

    left_channel[:fade_len] *= fade_in
    right_channel[:fade_len] *= fade_in
    left_channel[-fade_len:] *= fade_out
    right_channel[-fade_len:] *= fade_out

    # Normalización para evitar saturación digital (Peak headroom a -1.2 dB = 0.87)
    peak = max(np.max(np.abs(left_channel)), np.max(np.abs(right_channel)))
    if peak > 1e-6:
        gain = 0.87 / peak
        left_channel *= gain
        right_channel *= gain

    # Cuantización a 16 bits
    left_int16 = np.clip(left_channel * 32767.0, -32768.0, 32767.0).astype(np.int16)
    right_int16 = np.clip(right_channel * 32767.0, -32768.0, 32767.0).astype(np.int16)

    # Interleave estéreo
    stereo_interleaved = np.empty((total_samples * 2,), dtype=np.int16)
    stereo_interleaved[0::2] = left_int16
    stereo_interleaved[1::2] = right_int16

    os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)
    with wave.open(output_wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(stereo_interleaved.tobytes())

    print(f"[OK] Audio cinematográfico generado con éxito: {output_wav_path} ({duration:.1f}s)")
