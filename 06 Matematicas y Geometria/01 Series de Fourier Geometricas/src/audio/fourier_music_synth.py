"""
Continuum Lab — Generic Chill Science Music Synthesis Engine
Synthesizes a gentle, upbeat, and universally catchy lo-fi ambient science background track.
Designed to capture and hold attention without overpowering narration or visual focus.

Musical Structure:
  - Tempo: 112 BPM (relaxing, steady lo-fi groove).
  - Chord Progression: Cmaj7 -> Gmaj -> Amin7 -> Fmaj7.
  - Instrumentation:
      1. Warm Mellow Electric Piano / Rhodes chords with gentle tremolo.
      2. Soft Acoustic Lo-Fi Beat (warm rounded kick on 1 & 3, finger-snap on 2 & 4, subtle shaker).
      3. Deep Warm Sub-Bass following chord roots.
      4. Subtle Crystalline Arpeggiated Bells / Lead for intellectual curiosity.
  - Mix Level: Gentle / Moderate ("leve"), master peak normalized to -2.0 dB.
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


def generate_noise(n_samples: int) -> np.ndarray:
    return np.random.randn(n_samples)


def synthesize_fourier_background_music(
    duration: float = 21.0,
    fs: int = 44100,
    bpm: float = 112.0,
    output_path: str = "fourier_music_bg.wav"
) -> str:
    num_samples = int(duration * fs)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    beat_len = 60.0 / bpm            # ~0.5357 s per quarter note
    bar_len = beat_len * 4.0          # ~2.1428 s per bar (4 beats)

    # --------------------------------------------------------
    # 1. Harmonic Chords (Cmaj7 -> Gmaj -> Amin7 -> Fmaj7)
    # --------------------------------------------------------
    chord_roots = [
        # Cmaj7: C3, G3, B3, E4
        [130.81, 196.00, 246.94, 329.63],
        # Gmaj: G2, D3, G3, B3, D4
        [98.00, 146.83, 196.00, 246.94, 293.66],
        # Amin7: A2, E3, A3, C4, E4
        [110.00, 164.81, 220.00, 261.63, 329.63],
        # Fmaj7: F2, C3, F3, A3, C4, E4
        [87.31, 130.81, 174.61, 220.00, 261.63, 329.63],
    ]
    sub_bass_roots = [65.41, 49.00, 55.00, 43.65]  # Sub-bass frequencies (C2, G1, A1, F1)

    rhodes_left = np.zeros(num_samples)
    rhodes_right = np.zeros(num_samples)
    bass_track = np.zeros(num_samples)

    total_bars = int(np.ceil(duration / bar_len))

    for bar_idx in range(total_bars):
        chord_idx = bar_idx % 4
        bar_start_t = bar_idx * bar_len
        bar_start_s = int(bar_start_t * fs)

        # Sub-bass tone for the bar
        sub_freq = sub_bass_roots[chord_idx]
        bar_samples = min(int(bar_len * fs), num_samples - bar_start_s)
        if bar_samples <= 0:
            break
        t_bar = np.linspace(0, bar_samples / fs, bar_samples, endpoint=False)
        bass_env = np.exp(-t_bar / (bar_len * 0.9))
        bass_wave = 0.22 * np.sin(2 * np.pi * sub_freq * t_bar) * bass_env
        bass_track[bar_start_s:bar_start_s + bar_samples] += bass_wave

        # Rhodes chords: played gently on beat 1 and beat 2.5 (syncopated)
        chord_hit_offsets = [0.0, beat_len * 1.5]
        for hit_offset in chord_hit_offsets:
            hit_start_s = bar_start_s + int(hit_offset * fs)
            hit_len = min(int(beat_len * 2.2 * fs), num_samples - hit_start_s)
            if hit_len <= 0:
                continue
            t_hit = np.linspace(0, hit_len / fs, hit_len, endpoint=False)
            hit_env = np.exp(-t_hit / 0.75) * (0.85 + 0.15 * np.sin(2 * np.pi * 5.0 * t_hit))

            chord_wave_l = np.zeros(hit_len)
            chord_wave_r = np.zeros(hit_len)
            for f_note in chord_roots[chord_idx]:
                # Electric piano: fundamental + warm 2nd harmonic + subtle 3rd harmonic
                w = (
                    0.09 * np.sin(2 * np.pi * f_note * t_hit) +
                    0.04 * np.sin(2 * np.pi * (2 * f_note) * t_hit) +
                    0.015 * np.sin(2 * np.pi * (3 * f_note) * t_hit)
                )
                chord_wave_l += w * hit_env
                chord_wave_r += w * hit_env * (1.0 + 0.1 * np.sin(2 * np.pi * 0.5 * t_hit))

            rhodes_left[hit_start_s:hit_start_s + hit_len] += chord_wave_l
            rhodes_right[hit_start_s:hit_start_s + hit_len] += chord_wave_r

    # --------------------------------------------------------
    # 2. Gentle Lo-Fi Beat (Kick, Soft Snap, Shaker)
    # --------------------------------------------------------
    drums_left = np.zeros(num_samples)
    drums_right = np.zeros(num_samples)

    total_beats = int(duration / beat_len)
    for b_idx in range(total_beats):
        beat_start_s = int(b_idx * beat_len * fs)
        beat_in_bar = b_idx % 4

        # A. Soft Lo-Fi Kick on beats 0 and 2 (or 0 and 2.5)
        if beat_in_bar in [0, 2]:
            k_len = min(int(0.18 * fs), num_samples - beat_start_s)
            if k_len > 0:
                tk = np.linspace(0, 0.18, k_len, endpoint=False)
                # Pitch sweep from 90 Hz down to 42 Hz
                fk = 42.0 + 48.0 * np.exp(-tk / 0.035)
                kick_env = np.exp(-tk / 0.065)
                phase_k = 2 * np.pi * np.cumsum(fk) / fs
                kick = 0.32 * np.sin(phase_k) * kick_env
                drums_left[beat_start_s:beat_start_s + k_len] += kick
                drums_right[beat_start_s:beat_start_s + k_len] += kick

        # B. Soft Finger-Snap / Rimshot on beats 1 and 3
        if beat_in_bar in [1, 3]:
            s_len = min(int(0.08 * fs), num_samples - beat_start_s)
            if s_len > 0:
                ts = np.linspace(0, 0.08, s_len, endpoint=False)
                snap_noise = generate_noise(s_len)
                snap_filtered = bandpass_filter(snap_noise, 1800, 5500, fs, order=2)
                snap_env = np.exp(-ts / 0.02)
                snap = 0.14 * snap_filtered * snap_env
                drums_left[beat_start_s:beat_start_s + s_len] += snap * 0.9
                drums_right[beat_start_s:beat_start_s + s_len] += snap * 1.1

        # C. Shaker on every eighth note
        for sub_step in [0.0, 0.5]:
            sh_start_s = beat_start_s + int(sub_step * beat_len * fs)
            sh_len = min(int(0.04 * fs), num_samples - sh_start_s)
            if sh_len > 0:
                tsh = np.linspace(0, 0.04, sh_len, endpoint=False)
                sh_noise = generate_noise(sh_len)
                sh_filtered = bandpass_filter(sh_noise, 4500, 12000, fs, order=2)
                sh_env = np.exp(-tsh / 0.012)
                sh = 0.045 * sh_filtered * sh_env
                drums_left[sh_start_s:sh_start_s + sh_len] += sh * 0.8
                drums_right[sh_start_s:sh_start_s + sh_len] += sh * 1.0

    # --------------------------------------------------------
    # 3. Sparkling Pentatonic Lead Arpeggio (Intellectual Sparkle)
    # --------------------------------------------------------
    lead_left = np.zeros(num_samples)
    lead_right = np.zeros(num_samples)

    lead_scale = [523.25, 587.33, 659.25, 783.99, 880.00, 1046.50]  # C5 to C6 pentatonic
    step_eighth = beat_len * 0.5
    total_eighths = int(duration / step_eighth)

    for eighth_idx in range(total_eighths):
        # Arpeggio pattern
        note_f = lead_scale[(eighth_idx * 3) % len(lead_scale)]
        l_start_s = int(eighth_idx * step_eighth * fs)
        l_len = min(int(0.35 * fs), num_samples - l_start_s)
        if l_len > 0:
            tl = np.linspace(0, 0.35, l_len, endpoint=False)
            l_env = np.exp(-tl / 0.09)
            l_wave = 0.06 * np.sin(2 * np.pi * note_f * tl) * l_env
            pan_l = 0.5 * (1.0 + np.sin(eighth_idx * 0.8))
            lead_left[l_start_s:l_start_s + l_len] += l_wave * pan_l
            lead_right[l_start_s:l_start_s + l_len] += l_wave * (1.0 - pan_l)

    # --------------------------------------------------------
    # 4. Master Mix & Conditioning
    # --------------------------------------------------------
    mix_left = rhodes_left * 0.65 + bass_track * 0.60 + drums_left * 0.70 + lead_left * 0.50
    mix_right = rhodes_right * 0.65 + bass_track * 0.60 + drums_right * 0.70 + lead_right * 0.50

    # Master gentle fade-in (1.0s) and fade-out (1.2s)
    fade_in_len = int(1.0 * fs)
    fade_out_len = int(1.2 * fs)
    mix_left[:fade_in_len] *= np.linspace(0.0, 1.0, fade_in_len)
    mix_right[:fade_in_len] *= np.linspace(0.0, 1.0, fade_in_len)
    mix_left[-fade_out_len:] *= np.linspace(1.0, 0.0, fade_out_len)
    mix_right[-fade_out_len:] *= np.linspace(1.0, 0.0, fade_out_len)

    # Peak normalization to -2.0 dB
    peak = max(np.max(np.abs(mix_left)), np.max(np.abs(mix_right))) + 1e-6
    mix_left = (mix_left / peak) * 0.80
    mix_right = (mix_right / peak) * 0.80

    stereo_audio = np.stack([mix_left, mix_right], axis=1)
    stereo_int16 = (stereo_audio * 32767.0).astype(np.int16)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    wavfile.write(output_path, fs, stereo_int16)
    print(f"[CONTINUUM LAB] Catchy lo-fi science background music synthesized -> {output_path}")
    return output_path


if __name__ == "__main__":
    synthesize_fourier_background_music(duration=21.0, output_path="test_fourier_music.wav")
