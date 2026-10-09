"""
Continuum Lab — Cinematic Physics Audio Synthesizer
Module: 04 Termodinamica y Calor / 01 Ley Cero de la Termodinamica 3 Cuerpos
Track: "THERMAL HARMONY" — 84 BPM Cinematic Ambient Science & Acoustic-Electronic Soundtrack

Acoustic & Musical Architecture:
  1. Evolving Ambient Science Pad: Rich detuned polyphonic chords moving from Dm9 (thermal tension)
     to radiant D Major (perfect thermodynamic equilibrium).
  2. Sub-Bass Drone & Harmonic Warmth: Saturated 50-70 Hz sub-bass anchor providing cinematic gravity.
  3. Phonon Marimba / Kinetic Arpeggio: Delicate, crystal-clear rhythmic plucks modeling molecular vibrations.
  4. Organic Heartbeat Pulse: Soft, warm, low-passed cinematic pulse (no harsh EDM kicks).
  5. Celestial Equilibrium Chime: Pure resonant bell/glockenspiel cascade at t = 13.5s when T_A = T_B = T_C.
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
from pathlib import Path


def midi_to_freq(note: float) -> float:
    """Converts MIDI note number to frequency in Hz."""
    return 440.0 * (2.0 ** ((note - 69.0) / 12.0))


def butter_filter(data: np.ndarray, cutoff: float, fs: int, btype: str = 'low', order: int = 2) -> np.ndarray:
    """Butterworth filter wrapper with stability clamping."""
    nyq = 0.5 * fs
    norm_cut = max(0.001, min(0.990, cutoff / nyq))
    b, a = butter(order, norm_cut, btype=btype)
    return lfilter(b, a, data)


def apply_reverb_delay(signal: np.ndarray, delay_sec: float, decay: float, fs: int) -> np.ndarray:
    """Simple high-quality recursive feedback delay / ambient space emulator."""
    out = np.copy(signal)
    delay_samples = int(delay_sec * fs)
    if delay_samples < len(signal):
        for tap, gain in [(delay_samples, decay), (int(delay_samples * 1.5), decay * 0.6), (int(delay_samples * 2.2), decay * 0.35)]:
            if tap < len(signal):
                out[tap:] += signal[:-tap] * gain
    return out


def synthesize_warm_pad_chord(
    notes: list[float],
    duration: float,
    fs: int,
    attack: float = 0.8,
    release: float = 1.0,
    detune_cents: float = 8.0
) -> tuple[np.ndarray, np.ndarray]:
    """
    Synthesizes a lush, warm polyphonic analog ambient pad with stereo chorus.
    """
    num_samples = int(duration * fs)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    sig_l = np.zeros(num_samples)
    sig_r = np.zeros(num_samples)

    # Envelope
    env = np.ones(num_samples)
    att_samples = int(attack * fs)
    rel_samples = int(release * fs)
    if att_samples > 0:
        env[:att_samples] = np.sin(np.linspace(0, np.pi / 2, att_samples)) ** 2
    if rel_samples > 0:
        env[-rel_samples:] = np.cos(np.linspace(0, np.pi / 2, rel_samples)) ** 2

    for midi_note in notes:
        f0 = midi_to_freq(midi_note)
        f_left = f0 * (2.0 ** (-detune_cents / 1200.0))
        f_right = f0 * (2.0 ** (detune_cents / 1200.0))

        # Additive warm rich harmonics (fundamental + soft harmonics)
        # Left channel
        osc_l = (
            1.00 * np.sin(2.0 * np.pi * f_left * t) +
            0.50 * np.sin(2.0 * np.pi * 2.0 * f_left * t + 0.3) +
            0.25 * np.sin(2.0 * np.pi * 3.0 * f_left * t + 0.7) +
            0.12 * np.sin(2.0 * np.pi * 4.0 * f_left * t + 1.2)
        )
        # Right channel
        osc_r = (
            1.00 * np.sin(2.0 * np.pi * f_right * t) +
            0.50 * np.sin(2.0 * np.pi * 2.0 * f_right * t + 0.8) +
            0.25 * np.sin(2.0 * np.pi * 3.0 * f_right * t + 1.4) +
            0.12 * np.sin(2.0 * np.pi * 4.0 * f_right * t + 0.2)
        )

        sig_l += osc_l
        sig_r += osc_r

    # Warm lowpass filter to remove harshness
    sig_l = butter_filter(sig_l * env, 1200.0, fs, 'low', order=2)
    sig_r = butter_filter(sig_r * env, 1200.0, fs, 'low', order=2)

    return sig_l, sig_r


def synthesize_marimba_pluck(freq: float, duration: float, fs: int) -> np.ndarray:
    """
    Synthesizes a delicate, organic marimba/kalimba pluck modeling thermal phonon oscillations.
    """
    num_samples = int(duration * fs)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    # Fast transient strike
    strike = np.sin(2.0 * np.pi * freq * t) * np.exp(-t * 22.0)
    body = 0.6 * np.sin(2.0 * np.pi * 2.756 * freq * t) * np.exp(-t * 32.0)  # Wood overtone
    warmth = 0.4 * np.sin(2.0 * np.pi * freq * 0.5 * t) * np.exp(-t * 15.0)

    pluck = strike + body + warmth
    return np.tanh(pluck * 1.2)


def synthesize_celestial_bell(freq: float, duration: float, fs: int) -> np.ndarray:
    """
    Synthesizes a crystalline orchestral chime / singing bowl note for equilibrium climax.
    """
    num_samples = int(duration * fs)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    # Harmonic series with gentle metallic inharmonicity
    partials = [1.0, 2.0, 3.01, 4.18, 5.43]
    amplitudes = [1.0, 0.45, 0.25, 0.12, 0.06]
    decay_rates = [1.8, 2.5, 3.8, 5.2, 7.0]

    bell = np.zeros(num_samples)
    for p_ratio, p_amp, p_dec in zip(partials, amplitudes, decay_rates):
        p_freq = freq * p_ratio
        if p_freq < fs * 0.45:
            bell += p_amp * np.sin(2.0 * np.pi * p_freq * t) * np.exp(-t * p_dec)

    return bell * 0.85


def synthesize_soft_pulse(duration: float, fs: int) -> np.ndarray:
    """
    Synthesizes a deep, cinematic heartbeat pulse (no harsh clicks).
    """
    num_samples = int(duration * fs)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    # Pitch drops smoothly from 75 Hz to 35 Hz
    f_env = 35.0 + 40.0 * np.exp(-t * 18.0)
    phase = 2.0 * np.pi * np.cumsum(f_env) / fs
    amp = np.sin(np.pi * np.clip(t / duration, 0, 1)) * np.exp(-t * 8.0)
    pulse = np.sin(phase) * amp
    return butter_filter(pulse, 120.0, fs, 'low', order=2)


def synthesize_catchy_thermal_audio(
    duration: float = 18.0,
    fs: int = 44100,
    output_path: str = "thermal_equilibrium_music.wav"
) -> str:
    """
    Renders the complete cinematic, atmospheric science soundtrack perfectly synchronized
    to the Zeroth Law of Thermodynamics video timeline.
    """
    bpm = 84.0
    beat_sec = 60.0 / bpm         # ~0.7143 s per beat
    half_beat = beat_sec * 0.5    # ~0.3571 s (8th note)
    total_samples = int(duration * fs)
    t_global = np.linspace(0, duration, total_samples, endpoint=False)

    # Stereo buses
    bus_pad_l = np.zeros(total_samples)
    bus_pad_r = np.zeros(total_samples)
    bus_bass_l = np.zeros(total_samples)
    bus_bass_r = np.zeros(total_samples)
    bus_pluck_l = np.zeros(total_samples)
    bus_pluck_r = np.zeros(total_samples)
    bus_pulse_l = np.zeros(total_samples)
    bus_pulse_r = np.zeros(total_samples)
    bus_chime_l = np.zeros(total_samples)
    bus_chime_r = np.zeros(total_samples)

    # -------------------------------------------------------------------------
    # 1. HARMONIC PROGRESSION & AMBIENT PADS
    # Progression:
    #   0.0s - 4.5s:  Dm9    [D3, F3, A3, C4, E4]   (Thermal Disequilibrium)
    #   4.5s - 9.0s:  Bbmaj7 [Bb2, D3, F3, A3, D4]  (Irreversible Fourier Flow)
    #   9.0s - 13.5s: Fmaj9  [F2, A2, C3, E3, G3]   (Mediator C Equalizing)
    #  13.5s - 18.0s: D Major / Dadd9 [D3, F#3, A3, D4, E4] (EQUILIBRIUM ACHIEVED!)
    # -------------------------------------------------------------------------
    pad_sections = [
        (0.0, 4.8, [50, 53, 57, 60, 64], 45.0),    # Dm9, Bass D2
        (4.4, 9.2, [46, 50, 53, 57, 62], 46.0),    # Bbmaj7, Bass Bb1
        (8.8, 13.8, [41, 48, 52, 55, 59], 41.0),   # Fmaj9, Bass F1
        (13.4, 18.0, [50, 54, 57, 62, 64], 50.0),  # D Major / Dadd9 (Golden Equilibrium)
    ]

    for start_t, end_t, chord_notes, bass_root in pad_sections:
        chord_dur = end_t - start_t
        pad_l, pad_r = synthesize_warm_pad_chord(
            chord_notes, chord_dur, fs, attack=0.9, release=1.2, detune_cents=7.5
        )
        s_idx = int(start_t * fs)
        e_idx = s_idx + len(pad_l)
        actual_e = min(total_samples, e_idx)
        n_copy = actual_e - s_idx
        if n_copy > 0:
            bus_pad_l[s_idx:actual_e] += pad_l[:n_copy] * 0.45
            bus_pad_r[s_idx:actual_e] += pad_r[:n_copy] * 0.45

        # Sub-bass root tone
        f_bass = midi_to_freq(bass_root)
        t_sub = np.linspace(0, chord_dur, len(pad_l), endpoint=False)
        sub_tone = np.sin(2.0 * np.pi * f_bass * t_sub) + 0.3 * np.sin(2.0 * np.pi * 2.0 * f_bass * t_sub)
        sub_env = np.clip(np.sin(np.pi * np.linspace(0, 1, len(pad_l))), 0, 1) ** 0.5
        sub_bass = np.tanh(sub_tone * sub_env * 1.5) * 0.40
        sub_bass_filt = butter_filter(sub_bass, 140.0, fs, 'low', order=2)
        if n_copy > 0:
            bus_bass_l[s_idx:actual_e] += sub_bass_filt[:n_copy]
            bus_bass_r[s_idx:actual_e] += sub_bass_filt[:n_copy]

    # -------------------------------------------------------------------------
    # 2. RHYTHMIC PHONON PLUCK ARPEGGIO (Molecular Vibration Motif)
    # -------------------------------------------------------------------------
    # Melodic notes cycling through scale tones in 8th notes
    arpeggio_patterns = [
        # Dm9 pattern (0.0 to 4.5s)
        (0.0, 4.4, [62, 65, 69, 72, 69, 65, 64, 60]),
        # Bbmaj7 pattern (4.5 to 9.0s)
        (4.4, 8.8, [58, 62, 65, 69, 65, 62, 65, 69]),
        # Fmaj9 pattern (9.0 to 13.5s)
        (8.8, 13.4, [60, 64, 67, 71, 67, 64, 62, 60]),
        # D Major / Dadd9 resolution pattern (13.5 to 18.0s)
        (13.4, 17.6, [62, 66, 69, 74, 76, 74, 69, 66]),
    ]

    for start_t, end_t, note_cycle in arpeggio_patterns:
        curr_t = start_t
        pat_idx = 0
        while curr_t < end_t:
            midi_pitch = note_cycle[pat_idx % len(note_cycle)]
            freq = midi_to_freq(midi_pitch)
            dur_note = min(0.65, end_t - curr_t)
            if dur_note > 0.05:
                pluck = synthesize_marimba_pluck(freq, dur_note, fs) * 0.32
                s_i = int(curr_t * fs)
                e_i = min(total_samples, s_i + len(pluck))
                n_c = e_i - s_i
                # Stereo pan alternating subtly left/right
                pan_r = 0.5 + 0.25 * np.sin(pat_idx * 1.2)
                pan_l = 1.0 - pan_r
                if n_c > 0:
                    bus_pluck_l[s_i:e_i] += pluck[:n_c] * pan_l
                    bus_pluck_r[s_i:e_i] += pluck[:n_c] * pan_r
            curr_t += half_beat
            pat_idx += 1

    # Apply stereo ambient delay to plucks
    bus_pluck_l = apply_reverb_delay(bus_pluck_l, delay_sec=0.28, decay=0.38, fs=fs)
    bus_pluck_r = apply_reverb_delay(bus_pluck_r, delay_sec=0.36, decay=0.35, fs=fs)

    # -------------------------------------------------------------------------
    # 3. CINEMATIC PULSE (Gentle Sub Heartbeat on Beats 1 and 3)
    # Starts at t = 2.0s and fades smoothly before the final equilibrium chime
    # -------------------------------------------------------------------------
    pulse_sample = synthesize_soft_pulse(duration=0.45, fs=fs)
    pulse_len = len(pulse_sample)

    beat_idx = 0
    curr_beat_t = 0.0
    while curr_beat_t < 13.5:
        # Pulse on beat 0 and beat 2 of each 4-beat measure
        if beat_idx % 2 == 0 and curr_beat_t >= 1.4:
            s_i = int(curr_beat_t * fs)
            e_i = min(total_samples, s_i + pulse_len)
            n_c = e_i - s_i
            # Velocity increases slightly during active diffusion
            vel = 0.28 if curr_beat_t < 4.5 else 0.38
            if n_c > 0:
                bus_pulse_l[s_i:e_i] += pulse_sample[:n_c] * vel
                bus_pulse_r[s_i:e_i] += pulse_sample[:n_c] * vel
        curr_beat_t += beat_sec
        beat_idx += 1

    # -------------------------------------------------------------------------
    # 4. CELESTIAL EQUILIBRIUM CHIMES & GLOCKENSPIEL CASCADE (t >= 13.5s)
    # Radiant D Major cascade: D5, F#5, A5, D6, E6
    # -------------------------------------------------------------------------
    climax_t = 13.6
    chime_notes = [74, 78, 81, 86, 88]  # D5, F#5, A5, D6, E6
    for c_idx, c_midi in enumerate(chime_notes):
        c_time = climax_t + c_idx * 0.18
        c_freq = midi_to_freq(c_midi)
        chime = synthesize_celestial_bell(c_freq, duration=3.8, fs=fs) * 0.40
        s_i = int(c_time * fs)
        e_i = min(total_samples, s_i + len(chime))
        n_c = e_i - s_i
        pan_r = 0.3 + 0.1 * c_idx
        pan_l = 1.0 - pan_r
        if n_c > 0:
            bus_chime_l[s_i:e_i] += chime[:n_c] * pan_l
            bus_chime_r[s_i:e_i] += chime[:n_c] * pan_r

    # Reverb on chimes
    bus_chime_l = apply_reverb_delay(bus_chime_l, delay_sec=0.42, decay=0.45, fs=fs)
    bus_chime_r = apply_reverb_delay(bus_chime_r, delay_sec=0.55, decay=0.42, fs=fs)

    # -------------------------------------------------------------------------
    # 5. MASTERING, MIXING & DYNAMIC LIMITER
    # -------------------------------------------------------------------------
    mix_l = bus_pad_l + bus_bass_l + bus_pluck_l + bus_pulse_l + bus_chime_l
    mix_r = bus_pad_r + bus_bass_r + bus_pluck_r + bus_pulse_r + bus_chime_r

    # Smooth master fade-in and fade-out
    fade_in_len = int(0.6 * fs)
    fade_out_len = int(1.2 * fs)
    fade_in = np.sin(np.linspace(0, np.pi / 2, fade_in_len)) ** 2
    fade_out = np.cos(np.linspace(0, np.pi / 2, fade_out_len)) ** 2

    mix_l[:fade_in_len] *= fade_in
    mix_r[:fade_in_len] *= fade_in
    mix_l[-fade_out_len:] *= fade_out
    mix_r[-fade_out_len:] *= fade_out

    # Gentle tape warmth & brickwall soft limiter
    master_l = np.tanh(mix_l * 1.15)
    master_r = np.tanh(mix_r * 1.15)

    # Normalize to -0.5 dB peak
    peak = max(float(np.max(np.abs(master_l))), float(np.max(np.abs(master_r))), 1e-4)
    target_peak = 0.94
    master_l = (master_l / peak) * target_peak
    master_r = (master_r / peak) * target_peak

    # Convert to 16-bit PCM WAV
    audio_int16 = np.zeros((total_samples, 2), dtype=np.int16)
    audio_int16[:, 0] = (master_l * 32767.0).astype(np.int16)
    audio_int16[:, 1] = (master_r * 32767.0).astype(np.int16)

    out_path = Path(output_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(str(out_path), fs, audio_int16)

    print(f"[CONTINUUM LAB] Pista musical cinematográfica de ciencia generada: {out_path} ({duration:.1f}s @ 84 BPM)")
    return str(out_path)


if __name__ == "__main__":
    synthesize_catchy_thermal_audio(duration=18.0, output_path="test_cinematic_thermal_audio.wav")
