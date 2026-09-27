"""
Continuum Lab — Lo-Fi Chill Science Audio Synthesizer
Module: 06 Matematicas y Geometria / 02 Identidad de Euler 3D
Synthesizes a bespoke, elegant, and contemplative lo-fi ambient science background track.

Musical Architecture:
  - Tempo: 108 BPM (relaxed intellectual groove)
  - Progression: Fmaj9 -> G6/9 -> Emin7 -> Amin9 (Contemplative Neo-Soul/Lo-Fi)
  - Instrumentation:
      1. Warm Vintage Rhodes / Electric Piano with subtle stereo chorus & tremolo
      2. Mellow Vinyl-Textured Beats (organic kick, finger snap, soft vinyl crackle)
      3. Deep Warm 808-style Sub-Bass following harmonic roots
      4. Crystalline Celesta / Bell Arpeggios reflecting mathematical resonance
  - Mastering: Master peak normalized to -2.0 dB, low-pass warmth filter.
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
import os


def bandpass_filter(data, lowcut, highcut, fs, order=2):
    nyq = 0.5 * fs
    low = max(lowcut / nyq, 0.001)
    high = min(highcut / nyq, 0.999)
    b, a = butter(order, [low, high], btype='band')
    return lfilter(b, a, data)


def lowpass_filter(data, cutoff, fs, order=2):
    nyq = 0.5 * fs
    cut = min(cutoff / nyq, 0.999)
    b, a = butter(order, cut, btype='low')
    return lfilter(b, a, data)


def synthesize_euler_background_music(
    duration: float = 27.0,
    fs: int = 44100,
    bpm: float = 108.0,
    output_path: str = "euler_music_bg.wav"
) -> str:
    """
    Synthesizes a 27-second lo-fi science soundtrack for the 3D Euler animation.
    """
    num_samples = int(duration * fs)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    beat_len = 60.0 / bpm            # ~0.555 s per beat
    bar_len = beat_len * 4.0          # ~2.222 s per bar

    # 1. Harmonic Chords: Fmaj9, G6/9, Emin7, Amin9
    chord_frequencies = [
        # Fmaj9: F3 (174.61), A3 (220.00), C4 (261.63), E4 (329.63), G4 (392.00)
        [174.61, 220.00, 261.63, 329.63, 392.00],
        # G6/9: G3 (196.00), B3 (246.94), D4 (293.66), E4 (329.63), A4 (440.00)
        [196.00, 246.94, 293.66, 329.63, 440.00],
        # Emin7: E3 (164.81), G3 (196.00), B3 (246.94), D4 (293.66), F#4 (369.99)
        [164.81, 196.00, 246.94, 293.66, 369.99],
        # Amin9: A3 (220.00), C4 (261.63), E4 (329.63), G4 (392.00), B4 (493.88)
        [220.00, 261.63, 329.63, 392.00, 493.88],
    ]
    bass_roots = [87.31, 98.00, 82.41, 110.00]  # F2, G2, E2, A2

    # Electric Piano / Rhodes track
    rhodes_track = np.zeros(num_samples)
    tremolo_rate = 4.2  # Hz

    total_bars = int(np.ceil(duration / bar_len))
    for b_idx in range(total_bars):
        chord_idx = b_idx % len(chord_frequencies)
        chord_notes = chord_frequencies[chord_idx]
        bar_start_sample = int(b_idx * bar_len * fs)
        bar_samples = int(bar_len * fs)

        if bar_start_sample >= num_samples:
            break

        actual_len = min(bar_samples, num_samples - bar_start_sample)
        t_chord = np.linspace(0, actual_len / fs, actual_len, endpoint=False)

        # Decay envelope
        env = np.exp(-t_chord * 0.95)
        # Gentle tremolo
        trem = 0.82 + 0.18 * np.sin(2.0 * np.pi * tremolo_rate * t_chord)

        chord_audio = np.zeros(actual_len)
        for freq in chord_notes:
            # Fundamental + soft 2nd and 3rd harmonics
            note_wave = (
                1.00 * np.sin(2.0 * np.pi * freq * t_chord) +
                0.28 * np.sin(2.0 * np.pi * 2.0 * freq * t_chord) +
                0.08 * np.sin(2.0 * np.pi * 3.0 * freq * t_chord)
            )
            chord_audio += note_wave

        rhodes_track[bar_start_sample : bar_start_sample + actual_len] += chord_audio * env * trem * 0.14

    # 2. Sub-Bass Track
    sub_bass_track = np.zeros(num_samples)
    for b_idx in range(total_bars):
        root_f = bass_roots[b_idx % len(bass_roots)]
        bar_start_sample = int(b_idx * bar_len * fs)
        bar_samples = int(bar_len * fs)

        if bar_start_sample >= num_samples:
            break

        actual_len = min(bar_samples, num_samples - bar_start_sample)
        t_bass = np.linspace(0, actual_len / fs, actual_len, endpoint=False)
        env_bass = np.exp(-t_bass * 0.6)

        # Warm saturated sub-bass
        bass_wave = np.sin(2.0 * np.pi * root_f * t_bass) + 0.22 * np.sin(2.0 * np.pi * 2.0 * root_f * t_bass)
        bass_wave = np.tanh(1.3 * bass_wave)  # Gentle tube saturation
        sub_bass_track[bar_start_sample : bar_start_sample + actual_len] += bass_wave * env_bass * 0.24

    # 3. Lo-Fi Beat (Kick on 1 & 3, Snap on 2 & 4, subtle vinyl shaker)
    beat_track = np.zeros(num_samples)
    total_beats = int(np.ceil(duration / beat_len))

    for beat_idx in range(total_beats):
        beat_start_sample = int(beat_idx * beat_len * fs)
        if beat_start_sample >= num_samples:
            break

        bar_beat = beat_idx % 4  # 0, 1, 2, 3

        # Kick on 0 and 2
        if bar_beat in [0, 2]:
            k_len = int(0.22 * fs)
            actual_k = min(k_len, num_samples - beat_start_sample)
            t_k = np.linspace(0, actual_k / fs, actual_k, endpoint=False)
            freq_k = 110.0 * np.exp(-t_k * 30.0) + 45.0
            phase_k = 2.0 * np.pi * np.cumsum(freq_k) / fs
            env_k = np.exp(-t_k * 18.0)
            kick_audio = np.sin(phase_k) * env_k * 0.32
            beat_track[beat_start_sample : beat_start_sample + actual_k] += kick_audio

        # Finger Snap / Rim on 1 and 3
        if bar_beat in [1, 3]:
            s_len = int(0.09 * fs)
            actual_s = min(s_len, num_samples - beat_start_sample)
            t_s = np.linspace(0, actual_s / fs, actual_s, endpoint=False)
            noise_snap = np.random.randn(actual_s)
            snap_filtered = bandpass_filter(noise_snap, 1200, 7500, fs, order=2)
            env_s = np.exp(-t_s * 55.0)
            snap_tone = np.sin(2.0 * np.pi * 880.0 * t_s) * np.exp(-t_s * 70.0)
            snap_audio = (snap_filtered * 0.7 + snap_tone * 0.3) * env_s * 0.22
            beat_track[beat_start_sample : beat_start_sample + actual_s] += snap_audio

    # Shaker on 16th notes (4 per beat)
    sixteenth_len = beat_len / 4.0
    total_sixteenths = int(np.ceil(duration / sixteenth_len))
    for s_idx in range(total_sixteenths):
        s_start = int(s_idx * sixteenth_len * fs)
        if s_start >= num_samples:
            break
        sh_len = int(0.04 * fs)
        actual_sh = min(sh_len, num_samples - s_start)
        t_sh = np.linspace(0, actual_sh / fs, actual_sh, endpoint=False)
        noise_sh = np.random.randn(actual_sh)
        sh_filt = bandpass_filter(noise_sh, 4500, 14000, fs, order=2)
        env_sh = np.exp(-t_sh * 90.0)
        accent = 1.3 if (s_idx % 4 == 2) else 0.8
        beat_track[s_start : s_start + actual_sh] += sh_filt * env_sh * 0.05 * accent

    # 4. Crystalline Bells Arpeggio
    bell_track = np.zeros(num_samples)
    bell_pentatonic = [523.25, 659.25, 783.99, 987.77, 1046.50, 1318.51]  # C5, E5, G5, B5, C6, E6
    eighth_len = beat_len / 2.0
    total_eighths = int(np.ceil(duration / eighth_len))
    for e_idx in range(total_eighths):
        # Arpeggiate notes gracefully
        if e_idx % 2 == 1:
            note_f = bell_pentatonic[(e_idx // 2) % len(bell_pentatonic)]
            b_start = int(e_idx * eighth_len * fs)
            if b_start >= num_samples:
                break
            b_dur = int(0.4 * fs)
            act_b = min(b_dur, num_samples - b_start)
            t_b = np.linspace(0, act_b / fs, act_b, endpoint=False)
            env_b = np.exp(-t_b * 6.5)
            bell_audio = (
                np.sin(2.0 * np.pi * note_f * t_b) +
                0.3 * np.sin(2.0 * np.pi * 2.0 * note_f * t_b)
            ) * env_b * 0.07
            bell_track[b_start : b_start + act_b] += bell_audio

    # 5. Vinyl crackle / warm tape texture
    vinyl_noise = np.random.randn(num_samples) * 0.006
    vinyl_filtered = bandpass_filter(vinyl_noise, 400, 5000, fs, order=2)

    # Sum all tracks
    mix = rhodes_track + sub_bass_track + beat_track + bell_track + vinyl_filtered

    # Fade in (1.0 s) & Fade out (2.0 s)
    fade_in_len = int(1.0 * fs)
    fade_out_len = int(2.0 * fs)
    fade_in = np.linspace(0.0, 1.0, fade_in_len)
    fade_out = np.linspace(1.0, 0.0, fade_out_len)

    mix[:fade_in_len] *= fade_in
    mix[-fade_out_len:] *= fade_out

    # Normalize to -2.0 dB
    peak = np.max(np.abs(mix))
    if peak > 0:
        target_peak = 10.0 ** (-2.0 / 20.0)  # ~0.794
        mix = mix * (target_peak / peak)

    audio_int16 = (mix * 32767.0).astype(np.int16)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    wavfile.write(output_path, fs, audio_int16)

    return output_path
