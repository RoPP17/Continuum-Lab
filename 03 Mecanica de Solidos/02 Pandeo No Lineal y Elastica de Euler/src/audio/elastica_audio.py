"""
Módulo de Audio Procedural: Genera síntesis sonora WAV de 44.1 kHz estéreo
representando el aumento de tensión mecánica, la frecuencia de corte y la bifurcación.
"""

import os
import wave
import struct
import numpy as np


def generate_elastica_audio(output_path: str, duration_sec: float = 6.0):
    """
    Genera un archivo de audio WAV estéreo evocando la transición de estabilidad elástica:
    - Frecuencia base de deformación axial (drone subsónico 55 Hz).
    - Descenso de la frecuencia natural de vibración flexional f_n = f_0 * sqrt(1 - P/P_cr) hasta cero en la bifurcación.
    - Crecimiento de armónicos no lineales post-pandeo.
    """
    sample_rate = 44100
    n_samples = int(sample_rate * duration_sec)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)

    # Carga P normalizada variando suavemente de 0.5 a 1.3
    # Transición crítica P = 1.0 ocurre en t = duration_sec * 0.5
    P_ratio = 0.5 + 0.8 * (t / duration_sec)

    # 1. Frecuencia natural fundamental que se ablanda: f_n -> 0 cuando P -> P_cr
    f0 = 120.0  # Hz
    fn_profile = np.where(
        P_ratio < 1.0, 
        f0 * np.sqrt(np.maximum(1.0 - P_ratio, 0.001)), 
        25.0 + 80.0 * np.sqrt(np.maximum(P_ratio - 1.0, 0.0))
    )
    phase_fn = 2.0 * np.pi * np.cumsum(fn_profile) / sample_rate

    # 2. Resonancia de deformación (Sub-bass drone a 55 Hz)
    phase_sub = 2.0 * np.pi * 55.0 * t

    # 3. Transitorio acústico de chasquido de bifurcación (en t = 3.0 s)
    click_envelope = np.exp(-((t - 3.0) ** 2) / (2 * (0.05 ** 2)))
    click_sound = np.sin(2.0 * np.pi * 440.0 * t) * click_envelope

    # Mezcla estéreo
    left_channel = 0.35 * np.sin(phase_fn) + 0.3 * np.sin(phase_sub) + 0.35 * click_sound
    right_channel = 0.35 * np.cos(phase_fn + 0.2) + 0.3 * np.sin(phase_sub * 2.0) + 0.35 * click_sound

    # Envolvente suave de fade-in y fade-out
    envelope = np.minimum(t / 0.3, 1.0) * np.minimum((duration_sec - t) / 0.5, 1.0)
    left_channel *= envelope
    right_channel *= envelope

    # Normalización a 16-bit PCM
    left_int16 = np.int16(np.clip(left_channel, -0.95, 0.95) * 32767)
    right_int16 = np.int16(np.clip(right_channel, -0.95, 0.95) * 32767)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with wave.open(output_path, 'wb') as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        # Interleave estéreo
        stereo_data = np.empty((n_samples * 2,), dtype=np.int16)
        stereo_data[0::2] = left_int16
        stereo_data[1::2] = right_int16
        wav_file.writeframes(stereo_data.tobytes())

    return output_path
