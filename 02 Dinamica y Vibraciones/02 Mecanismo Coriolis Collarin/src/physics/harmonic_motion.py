"""
Continuum Lab — Classical Mechanics & Dynamical Systems
Division: 02 Dinamica y Vibraciones / 02 Mecanismo Coriolis Collarin
Module: harmonic_motion.py

Harmonic Decomposition, Phase Space Orbit, and Hypnotic Hodograph Generators.
"""

from typing import Dict, Any, List
import numpy as np
from .coriolis_kinematics import CoriolisKinematicsSolver, CoriolisMechanismParams, KinematicState


class HarmonicCoriolisAnalyzer:
    """
    Analiza el contenido espectral armónico y las trayectorias de fase
    hipnóticas inducidas por el acoplamiento no lineal de Coriolis.
    """

    def __init__(self, solver: CoriolisKinematicsSolver):
        self.solver = solver

    def compute_cyclic_harmonics(self, n_points: int = 1024) -> Dict[str, Any]:
        """
        Calcula la serie de Fourier / FFT de la aceleración de Coriolis
        para cuantificar los armónicos cíclicos inducidos por el collarín.
        """
        states = self.solver.generate_cycle(n_points)
        theta_arr = np.array([s.theta1 for s in states])
        time_arr = np.array([s.time for s in states])
        
        a_cor_arr = np.array([s.a_coriolis_mag for s in states])
        v_rel_arr = np.array([s.v_rel for s in states])
        omega2_arr = np.array([s.omega2 for s in states])
        r2_arr = np.array([s.r2 for s in states])

        # Espectro de frecuencias (FFT)
        fft_cor = np.fft.rfft(a_cor_arr) / n_points
        freqs = np.fft.rfftfreq(n_points, d=(time_arr[1] - time_arr[0]))
        amplitudes = 2.0 * np.abs(fft_cor)

        # Primeros 6 armónicos dominantes
        top_indices = np.argsort(amplitudes[1:])[-6:][::-1] + 1
        dominant_harmonics = [
            {"harmonic_order": int(idx), "frequency_hz": float(freqs[idx]), "amplitude": float(amplitudes[idx])}
            for idx in top_indices
        ]

        # Órbitas de fase y hodógrafo
        coriolis_hodograph_x = np.array([s.a_coriolis_vec[0] for s in states])
        coriolis_hodograph_y = np.array([s.a_coriolis_vec[1] for s in states])

        return {
            "theta_rad": theta_arr,
            "time_sec": time_arr,
            "a_coriolis": a_cor_arr,
            "v_rel": v_rel_arr,
            "omega2": omega2_arr,
            "r2": r2_arr,
            "dominant_harmonics": dominant_harmonics,
            "hodograph_x": coriolis_hodograph_x,
            "hodograph_y": coriolis_hodograph_y,
            "max_coriolis": float(np.max(np.abs(a_cor_arr))),
            "rms_coriolis": float(np.sqrt(np.mean(a_cor_arr**2))),
        }
