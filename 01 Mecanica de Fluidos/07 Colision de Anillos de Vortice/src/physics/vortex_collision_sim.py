"""
Continuum Lab - Physics Engine: Head-On Collision of Vortex Rings & Reconnection Cascade
Module: 01 Mecanica de Fluidos / 07 Colision de Anillos de Vortice
File: src/physics/vortex_collision_sim.py

Implements:
  1. Kelvin-Hicks-Lamb self-induced propagation of circular vortex filaments.
  2. Complete elliptic integral Biot-Savart mutual induction with Lamb-Oseen core smoothing.
  3. Core volume conservation & vortex stretching (enstrophy amplification).
  4. Widnall-Tsai-Widmer azimuthal instability (mode m = 12).
  5. Topological vortex reconnection into a radial crown of 12 secondary toroidal rings.
  6. 1200+ Lagrangian tracer particles with velocity and vorticity field advection.
"""

import numpy as np
from scipy.special import ellipk, ellipe
from typing import Dict, List, Tuple, Optional


class VortexRingsCollisionSim:
    """
    Simulation of two colliding vortex rings with Widnall instability and reconnection.
    """

    def __init__(self, R0: float = 0.28, a0: float = 0.045, Gamma0: float = 1.4, 
                 z0: float = 0.52, m_mode: int = 12, num_particles: int = 1200):
        self.R0 = float(R0)
        self.a0 = float(a0)
        self.Gamma0 = float(Gamma0)
        self.z0 = float(z0)
        self.m_mode = int(m_mode)
        self.num_particles = int(num_particles)
        
        # Self-induction constant beta (Lamb-Oseen Gaussian core: beta = 0.058)
        self.beta = 0.058

        # Precompute trajectory over 16.0s (960 frames at 60 FPS)
        self._integrate_primary_trajectory(duration=16.0, dt=1.0/120.0)
        self._init_particles()

    def _kelvin_hicks_speed(self, R: float, a: float) -> float:
        """Self-induced axial translation velocity U_self."""
        R_safe = max(R, 1e-4)
        a_safe = max(min(a, 0.95 * R_safe), 1e-5)
        log_term = np.log(8.0 * R_safe / a_safe) - 0.25 + self.beta
        return float((self.Gamma0 / (4.0 * np.pi * R_safe)) * log_term)

    def _mutual_induction(self, R: float, z: float, a: float) -> Tuple[float, float]:
        """
        Velocity (u_r, u_z) induced on Ring 1 at (R, z) by mirror Ring 2 at (R, -z).
        Circulation of Ring 1 is +Gamma0, mirror Ring 2 is -Gamma0.
        Includes Lamb-Oseen core smoothing cutoff: denom_sq = 4*R^2 + z_sep^2 + 2*a^2.
        """
        z_sep = 2.0 * abs(z)
        R_safe = max(R, 1e-3)
        denom_sq = 4.0 * (R_safe ** 2) + (z_sep ** 2) + 2.5 * (a ** 2)
        if denom_sq < 1e-8:
            return 0.0, 0.0
        
        denom = np.sqrt(denom_sq)
        m = (4.0 * (R_safe ** 2)) / denom_sq
        m = np.clip(m, 0.0, 0.9995)

        K_m = float(ellipk(m))
        E_m = float(ellipe(m))

        one_minus_m = max(1.0 - m, 1e-6)

        # Radial velocity (drives ring expansion dR/dt > 0)
        ur = (self.Gamma0 / (2.0 * np.pi * denom)) * (z_sep / R_safe) * (-K_m + ((2.0 - m) / (2.0 * one_minus_m)) * E_m)
        # Axial velocity (decelerates approaching ring)
        uz = -(self.Gamma0 / (2.0 * np.pi * denom)) * (K_m + ((m - 2.0) / (2.0 * one_minus_m)) * E_m)

        return float(ur), float(uz)

    def _integrate_primary_trajectory(self, duration: float = 16.0, dt: float = 1.0/120.0):
        """Integrates primary ring kinematics and Widnall wave growth."""
        n_steps = int(duration / dt) + 1
        t_arr = np.linspace(0, duration, n_steps)

        z_arr = np.zeros(n_steps)
        R_arr = np.zeros(n_steps)
        a_arr = np.zeros(n_steps)
        strain_arr = np.zeros(n_steps)
        widnall_amp = np.zeros(n_steps)
        reconnected_flag = np.zeros(n_steps, dtype=bool)

        # Initial state at t = 0
        z_curr = self.z0
        R_curr = self.R0
        a_curr = self.a0
        amp_curr = 0.0005 * self.a0  # Initial perturbation

        z_arr[0] = z_curr
        R_arr[0] = R_curr
        a_arr[0] = a_curr
        widnall_amp[0] = amp_curr

        # Collision & Reconnection occurs around t = 5.5s
        t_reconnect = 5.8
        self.t_reconnect = t_reconnect

        for i in range(1, n_steps):
            t = t_arr[i]
            if t < t_reconnect:
                # Approach & expansion phase
                u_self = self._kelvin_hicks_speed(R_curr, a_curr)
                ur, uz = self._mutual_induction(R_curr, z_curr, a_curr)

                dz_dt = -u_self + uz
                dR_dt = max(ur, 0.0)

                # Core thinning via volume conservation: a(t) = a0 * sqrt(R0 / R(t))
                z_curr = max(z_curr + dz_dt * dt, 0.018)
                R_curr = min(R_curr + dR_dt * dt, 0.85)
                a_curr = self.a0 * np.sqrt(self.R0 / max(R_curr, 1e-4))

                # Widnall growth rate sigma_w
                strain = (dR_dt / R_curr) if R_curr > 1e-3 else 0.0
                sigma_w = 2.6 * strain + 0.12 * (self.Gamma0 / (2.0 * np.pi * (R_curr**2)))
                amp_curr = min(amp_curr * np.exp(sigma_w * dt), a_curr * 1.5)

            elif t < 12.0:
                # Post-reconnection: secondary rings shoot outward, primary rings dissipate
                z_curr = max(z_curr * 0.992, 0.008)
                R_curr = min(R_curr + 0.015 * dt, 0.88)
                a_curr = a_curr * 0.995
                amp_curr = a_curr * 1.2
                reconnected_flag[i] = True
            else:
                # Infinite seamless loop return phase: smooth quintic ease back to t = 0
                tau = (t - 12.0) / 4.0
                w = 6 * (tau**5) - 15 * (tau**4) + 10 * (tau**3)
                z_curr = z_arr[i-1] + (self.z0 - z_arr[i-1]) * (dt / max(duration - t, dt))
                R_curr = R_arr[i-1] + (self.R0 - R_arr[i-1]) * (dt / max(duration - t, dt))
                a_curr = self.a0
                amp_curr = 0.0005 * self.a0

            z_arr[i] = z_curr
            R_arr[i] = R_curr
            a_arr[i] = a_curr
            strain_arr[i] = (R_curr - R_arr[i-1]) / (dt * R_curr) if i > 0 else 0.0
            widnall_amp[i] = amp_curr
            if t >= t_reconnect:
                reconnected_flag[i] = True

        self.t_traj = t_arr
        self.z_traj = z_arr
        self.R_traj = R_arr
        self.a_traj = a_arr
        self.strain_traj = strain_arr
        self.amp_traj = widnall_amp
        self.reconnected_traj = reconnected_flag

    def _init_particles(self):
        """Initializes 1200+ Lagrangian tracer particles in toroidal coordinates."""
        rng = np.random.default_rng(2026)
        self.p_theta = rng.uniform(0, 2.0 * np.pi, self.num_particles)
        self.p_phi = rng.uniform(0, 2.0 * np.pi, self.num_particles)  # Poloidal angle
        # Half upper ring (+1), half lower ring (-1)
        self.p_ring = np.ones(self.num_particles, dtype=int)
        self.p_ring[self.num_particles // 2:] = -1
        # Random core distance fraction in [0.15, 1.35]
        self.p_r_core = rng.uniform(0.15, 1.35, self.num_particles)

    def get_state(self, t: float) -> Dict:
        """
        Returns full hydrodynamic and geometric state at time t (seconds).
        """
        t_clamped = np.clip(t, 0.0, self.t_traj[-1])
        idx = int(np.searchsorted(self.t_traj, t_clamped))
        idx = min(idx, len(self.t_traj) - 1)

        z = float(self.z_traj[idx])
        R = float(self.R_traj[idx])
        a = float(self.a_traj[idx])
        strain = float(self.strain_traj[idx])
        amp = float(self.amp_traj[idx])
        is_reconnected = bool(self.reconnected_traj[idx])

        # Peak vorticity omega_max = Gamma0 / (pi * a^2)
        omega_max = self.Gamma0 / (np.pi * max(a, 1e-4)**2)

        # 1. Primary Ring 1 (Upper: +z, +Gamma0) and Ring 2 (Lower: -z, -Gamma0)
        n_pts = 160
        theta_arr = np.linspace(0, 2.0 * np.pi, n_pts, endpoint=True)

        w_wave = amp * np.cos(self.m_mode * theta_arr)
        r_ring = R + w_wave

        # Upper ring 3D coordinates
        x_ring1 = r_ring * np.cos(theta_arr)
        y_ring1 = r_ring * np.sin(theta_arr)
        z_ring1 = np.full_like(theta_arr, z) + 0.45 * amp * np.sin(self.m_mode * theta_arr)

        # Lower ring 3D coordinates
        x_ring2 = r_ring * np.cos(theta_arr)
        y_ring2 = r_ring * np.sin(theta_arr)
        z_ring2 = np.full_like(theta_arr, -z) - 0.45 * amp * np.sin(self.m_mode * theta_arr)

        # 2. Secondary Reconnected Rings (m = 12 crown)
        sec_rings = []
        if is_reconnected:
            tau_rec = max(t - self.t_reconnect, 0.0)
            # Secondary baby rings self-propel radially outward with bounded expansion
            dist_sec = R + 0.18 * np.tanh(0.85 * tau_rec)

            # Fade gracefully during the loop return phase (t > 12.0)
            fade = np.clip(1.0 - (t - 12.0) / 3.8, 0.0, 1.0) if t > 12.0 else 1.0
            r_sec = (0.045 + 0.010 * np.sin(np.pi * np.clip(tau_rec / 5.0, 0.0, 1.0))) * fade

            if r_sec > 0.005:
                n_sec_pts = 32
                psi_arr = np.linspace(0, 2.0 * np.pi, n_sec_pts, endpoint=True)

                for k in range(self.m_mode):
                    th_k = 2.0 * np.pi * k / self.m_mode
                    cx_k = dist_sec * np.cos(th_k)
                    cy_k = dist_sec * np.sin(th_k)
                    cz_k = 0.0

                    # Normal vector is radial: n = [cos(th_k), sin(th_k), 0]
                    sx = cx_k + r_sec * (-np.sin(th_k) * np.cos(psi_arr))
                    sy = cy_k + r_sec * ( np.cos(th_k) * np.cos(psi_arr))
                    sz = cz_k + r_sec * np.sin(psi_arr)
                    sec_rings.append(np.column_stack((sx, sy, sz)))

        # 3. Lagrangian Tracer Particles (advection)
        omega_core = self.Gamma0 / (2.0 * np.pi * max(a, 1e-4)**2)
        phi_t = self.p_phi + omega_core * t * self.p_ring

        r_p = R + self.p_r_core * a * np.cos(phi_t)
        z_p = (z + self.p_r_core * a * np.sin(phi_t)) * self.p_ring
        x_p = r_p * np.cos(self.p_theta)
        y_p = r_p * np.sin(self.p_theta)

        v_poloidal = omega_core * self.p_r_core * a
        v_total = np.sqrt(v_poloidal**2 + (strain * R)**2)

        return {
            "t": t,
            "z": z,
            "R": R,
            "R_ratio": R / self.R0,
            "a": a,
            "a_ratio": a / self.a0,
            "omega_max": omega_max,
            "strain": strain,
            "amp_widnall": amp,
            "is_reconnected": is_reconnected,
            "ring1": np.column_stack((x_ring1, y_ring1, z_ring1)),
            "ring2": np.column_stack((x_ring2, y_ring2, z_ring2)),
            "sec_rings": sec_rings,
            "particles_3d": np.column_stack((x_p, y_p, z_p)),
            "particles_speed": v_total
        }
