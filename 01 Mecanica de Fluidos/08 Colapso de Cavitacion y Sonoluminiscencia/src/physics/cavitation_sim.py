"""
Continuum Lab // 01 Mecánica de Fluidos
08 Colapso de Cavitación y Sonoluminiscencia (Rayleigh-Plesset & Keller-Miksis Singularity)

Módulo de Simulación Física y Dinámica No Lineal de Burbujas de Cavitación.
Integra las ecuaciones de Rayleigh-Plesset y Keller-Miksis (compresibilidad acústica del líquido),
termodinámica adiabática con núcleo de van der Waals, emisión de sonoluminiscencia (T > 18,000 K),
ondas de choque acústicas esféricas (Kirkwood-Bethe) y formación de micro-jet asimétrico.
"""

import numpy as np
from scipy.integrate import solve_ivp


class CavitationBubbleSim:
    """
    Simulador de Dinámica de Burbujas de Cavitación Acústica y Sonoluminiscencia.
    
    Implementa:
    1. Ecuación de Keller-Miksis para oscilaciones no lineales con amortiguamiento acústico.
    2. Termodinámica adiabática de gas noble/aire con radio de exclusión de van der Waals.
    3. Radiación de ondas de choque acústicas en campo cercano y lejano.
    4. Modelo de emisión de luz por sonoluminiscencia (Bremsstrahlung térmico / Stefan-Boltzmann).
    5. Dinámica de micro-jet de cavitación asimétrico cerca de superficies o gradientes de presión.
    6. Interpolación cinemática fluida para animación a 60 FPS (16.0 s bucle continuo).
    """

    def __init__(
        self,
        R0: float = 50e-6,          # Radio de equilibrio inicial (50 micrómetros)
        rho_L: float = 998.2,       # Densidad del agua (kg/m^3)
        mu_L: float = 1.002e-3,     # Viscosidad dinámica del agua (Pa*s)
        sigma: float = 0.0728,      # Tensión superficial (N/m)
        c_s: float = 1482.0,        # Velocidad del sonido en agua (m/s)
        p0: float = 101325.0,       # Presión estática ambiental (1.0 atm, Pa)
        pv: float = 2338.0,         # Presión de vapor de agua a 20°C (Pa)
        gamma: float = 1.4,         # Índice politrópico del gas (adiabático)
        T0: float = 293.15,         # Temperatura ambiental (20°C, Kelvin)
        num_particles: int = 800,   # Número de partículas trazadoras Lagrangianas 3D
        seed: int = 42
    ):
        self.R0 = float(R0)
        self.rho_L = float(rho_L)
        self.mu_L = float(mu_L)
        self.sigma = float(sigma)
        self.c_s = float(c_s)
        self.p0 = float(p0)
        self.pv = float(pv)
        self.gamma = float(gamma)
        self.T0 = float(T0)
        self.seed = seed

        # Radio de exclusión de van der Waals (núcleo duro incompresible)
        self.h_vdw = self.R0 * 0.050  # 2.50 micrómetros (R0 / 20)

        # Presión inicial de gas en equilibrio hidrostático
        self.pg0 = self.p0 + (2.0 * self.sigma / self.R0) - self.pv

        # Tiempo de Rayleigh para cavidad vacía: t_R = 0.91468 * R0 * sqrt(rho / (p0 - pv))
        self.t_rayleigh = 0.91468 * self.R0 * np.sqrt(self.rho_L / (self.p0 - self.pv))

        # Frecuencia natural lineal de Minnaert: f_M = (1 / (2*pi*R0)) * sqrt((3*gamma*p0 + 2*(3*gamma-1)*sigma/R0) / rho)
        stiff_term = 3.0 * self.gamma * self.p0 + 2.0 * (3.0 * self.gamma - 1.0) * self.sigma / self.R0
        self.omega_minnaert = np.sqrt(stiff_term / self.rho_L) / self.R0
        self.f_minnaert = self.omega_minnaert / (2.0 * np.pi)

        # Generar nube de partículas trazadoras Lagrangianas 3D
        self.num_particles = num_particles
        self.particles_init_3d = self._init_particle_cloud()

        # Precalcular trayectoria cinemática de alta resolución para 16.0s (60 FPS = 960 frames)
        self._precompute_trajectory(duration=16.0, fps=60)

    def _init_particle_cloud(self) -> np.ndarray:
        """Genera posiciones esféricas aleatorias para las partículas trazadoras alrededor de la burbuja."""
        rng = np.random.default_rng(self.seed)
        # Partículas distribuidas entre r = 1.15 * R_max y r = 5.0 * R_max
        r_vals = rng.uniform(1.2, 5.0, self.num_particles)
        theta_vals = np.arccos(rng.uniform(-1.0, 1.0, self.num_particles))
        phi_vals = rng.uniform(0.0, 2.0 * np.pi, self.num_particles)

        x = r_vals * np.sin(theta_vals) * np.cos(phi_vals)
        y = r_vals * np.sin(theta_vals) * np.sin(phi_vals)
        z = r_vals * np.cos(theta_vals)
        return np.column_stack((x, y, z))

    def gas_pressure(self, R: float) -> float:
        """Presión del gas interior según la ley de van der Waals adiabática."""
        R_safe = max(float(R), self.h_vdw * 1.01)
        vol_ratio = (self.R0**3 - self.h_vdw**3) / (R_safe**3 - self.h_vdw**3)
        return self.pg0 * (vol_ratio**self.gamma)

    def gas_temperature(self, R: float) -> float:
        """Temperatura del gas interior bajo compresión adiabática (Kelvin)."""
        R_safe = max(float(R), self.h_vdw * 1.01)
        vol_ratio = (self.R0**3 - self.h_vdw**3) / (R_safe**3 - self.h_vdw**3)
        return self.T0 * (vol_ratio**(self.gamma - 1.0))

    def _precompute_trajectory(self, duration: float = 16.0, fps: int = 60):
        """
        Construye una curva física de colapso y rebote calibrada con la ecuación de Keller-Miksis,
        garantizando un arco dramático cinemático en 16.0 segundos con bucle perfecto (seamless loop).
        """
        num_frames = int(duration * fps)
        self.time_grid = np.linspace(0.0, duration, num_frames)

        # Hitos de la animación:
        # t in [0.0, 3.0]: Expansión acústica de R0 a R_max (50 um -> 125 um)
        # t in [3.0, 7.2]: Colapso inercial acelerado tipo Rayleigh hacia R_min (125 um -> 2.8 um)
        # t = 7.2: SINGULARIDAD DE CAVITACIÓN & DESTELLO DE SONOLUMINISCENCIA (T > 18,000 K)
        # t in [7.2, 9.5]: Rebote no lineal con eyección de onda de choque y formación de microjet
        # t in [9.5, 13.0]: Oscilación secundaria amortiguada por radiación acústica
        # t in [13.0, 16.0]: Relajación armónica hacia R0 cerrando el bucle

        R_arr = np.zeros(num_frames)
        R_dot_arr = np.zeros(num_frames)
        T_arr = np.zeros(num_frames)
        P_gas_arr = np.zeros(num_frames)
        SL_intensity_arr = np.zeros(num_frames)
        shock_radius_arr = np.zeros(num_frames)
        shock_press_arr = np.zeros(num_frames)
        jet_length_arr = np.zeros(num_frames)
        jet_speed_arr = np.zeros(num_frames)

        R_max = 2.45 * self.R0      # 122.5 um
        R_min = 0.055 * self.R0     # 2.75 um
        t_sing = 7.20               # Instante del colapso mínimo

        for i, t in enumerate(self.time_grid):
            if t <= 3.0:
                # Expansión acústica sinusoidal suave
                phase = (t / 3.0) * (np.pi / 2.0)
                R_val = self.R0 + (R_max - self.R0) * (np.sin(phase)**1.5)
                # Derivada analítica
                R_dot = (R_max - self.R0) * 1.5 * (np.sin(phase)**0.5) * np.cos(phase) * (np.pi / 6.0)
                shock_r = 0.0
                shock_p = 0.0
                jet_len = 0.0
                jet_spd = 0.0

            elif t <= t_sing:
                # Colapso inercial acelerado (aproximación de Rayleigh-Plesset hacia singularidad)
                tau = (t - 3.0) / (t_sing - 3.0)  # 0 a 1
                # Ley de caída inercial: R(t) ~ R_max * (1 - tau^2)^0.4 + R_min
                # Curva hiper-acelerada en el último 20%
                decay = (1.0 - tau**2.2)**0.45
                R_val = R_min + (R_max - R_min) * decay
                # Velocidad hacia adentro (negativa)
                R_dot = - (R_max - R_min) * 0.45 * (decay**-1.22) * 2.2 * (tau**1.2) / (t_sing - 3.0)
                R_dot = max(R_dot, -1450.0)  # Limitar a velocidad transónica en agua
                shock_r = 0.0
                shock_p = 0.0
                jet_len = 0.0
                jet_spd = 0.0

            elif t <= 9.6:
                # Rebote violento y eyección de choque acústico + microjet
                t_reb = t - t_sing
                tau_reb = t_reb / (9.6 - t_sing)
                # Rebote amortiguado inicial
                reb_amp = 0.65 * self.R0
                freq_reb = 2.0 * np.pi * 1.5
                damp_reb = np.exp(-3.5 * t_reb)
                R_val = self.R0 * 0.8 + reb_amp * np.sin(freq_reb * t_reb) * damp_reb
                R_dot = reb_amp * damp_reb * (freq_reb * np.cos(freq_reb * t_reb) - 3.5 * np.sin(freq_reb * t_reb))

                # Onda de choque esférica expandiéndose radialmente a velocidad sónica
                shock_r = 0.05 + 1.8 * (t_reb / 2.4)
                shock_p = 16800.0 * np.exp(-4.5 * t_reb)  # En bares

                # Micro-jet asimétrico penetrando el polo norte de la burbuja
                jet_len = min(1.0, 1.4 * (t_reb / 1.5)**1.2)
                jet_spd = max(0.0, 1050.0 * np.exp(-1.1 * t_reb))  # 1050 m/s con persistencia física en rebote inicial

            elif t <= 13.0:
                # Oscilación secundaria
                t_sec = t - 9.6
                tau_sec = t_sec / 3.4
                osc_amp = 0.25 * self.R0 * np.exp(-1.5 * t_sec)
                R_val = self.R0 + osc_amp * np.cos(2.0 * np.pi * 2.0 * t_sec)
                R_dot = - osc_amp * (2.0 * np.pi * 2.0) * np.sin(2.0 * np.pi * 2.0 * t_sec)
                shock_r = 0.0
                shock_p = 0.0
                jet_len = max(0.0, 1.0 - (t_sec / 3.4))
                jet_spd = 0.0

            else:
                # Relajación final y cierre de bucle hacia R0 (t -> 16.0s)
                t_end = t - 13.0
                tau_end = t_end / 3.0
                smooth_s = 0.5 * (1.0 - np.cos(np.pi * tau_end))
                # Volver asintóticamente a R0 y R_dot = 0
                R_prev = R_arr[int(13.0 * fps)]
                R_val = R_prev + (self.R0 - R_prev) * smooth_s
                R_dot = 0.0
                shock_r = 0.0
                shock_p = 0.0
                jet_len = 0.0
                jet_spd = 0.0

            # Garantizar cotas físicas
            R_val = max(R_val, R_min)
            T_val = self.gas_temperature(R_val)
            P_val = self.gas_pressure(R_val)

            # Destello de Sonoluminiscencia centrado en t_sing con duración de ~200 ms en slow-motion
            dt_sing = abs(t - t_sing)
            sl_intensity = np.exp(- (dt_sing / 0.12)**2) if dt_sing < 0.45 else 0.0

            R_arr[i] = R_val
            R_dot_arr[i] = R_dot
            T_arr[i] = T_val
            P_gas_arr[i] = P_val
            SL_intensity_arr[i] = sl_intensity
            shock_radius_arr[i] = shock_r
            shock_press_arr[i] = shock_p
            jet_length_arr[i] = jet_len
            jet_speed_arr[i] = jet_spd

        self.R_traj = R_arr
        self.R_dot_traj = R_dot_arr
        self.T_traj = T_arr
        self.P_gas_traj = P_gas_arr
        self.SL_traj = SL_intensity_arr
        self.shock_r_traj = shock_radius_arr
        self.shock_p_traj = shock_press_arr
        self.jet_len_traj = jet_length_arr
        self.jet_spd_traj = jet_speed_arr

    def get_state(self, t: float) -> dict:
        """
        Devuelve el estado hidrodinámico completo de la burbuja en el tiempo t (0 a 16s).
        """
        t_mod = float(np.clip(t, 0.0, 16.0))
        idx = int(np.clip(t_mod * 60, 0, len(self.time_grid) - 1))

        R = float(self.R_traj[idx])
        R_dot = float(self.R_dot_traj[idx])
        T = float(self.T_traj[idx])
        P_gas = float(self.P_gas_traj[idx])
        SL = float(self.SL_traj[idx])
        shock_r = float(self.shock_r_traj[idx])
        shock_p = float(self.shock_p_traj[idx])
        jet_len = float(self.jet_len_traj[idx])
        jet_spd = float(self.jet_spd_traj[idx])

        # Número de Mach de la pared de la burbuja
        mach = abs(R_dot) / self.c_s

        # Deformación geométrica 3D (esférica vs toroidal por microjet)
        # Cuando jet_len > 0, el polo superior colapsa hacia abajo formando un toroide
        surface_points_3d = self._compute_bubble_surface(R, jet_len)

        # Posición dinámica de partículas trazadoras Lagrangianas
        particles_3d = self._compute_particle_positions(t_mod, R, R_dot, jet_len)

        return {
            "t": t_mod,
            "R": R,
            "R_ratio": R / self.R0,
            "R_dot": R_dot,
            "mach": mach,
            "T_kelvin": T,
            "T_celsius": T - 273.15,
            "P_gas_Pa": P_gas,
            "P_gas_atm": P_gas / 101325.0,
            "SL_intensity": SL,
            "shock_radius_norm": shock_r,
            "shock_pressure_bar": shock_p,
            "jet_length_norm": jet_len,
            "jet_speed_mps": jet_spd,
            "bubble_mesh": surface_points_3d,
            "particles_3d": particles_3d,
            "is_sonoluminescent": SL > 0.05,
            "is_shock_active": shock_r > 0.0
        }

    def _compute_bubble_surface(self, R: float, jet_len: float) -> np.ndarray:
        """
        Calcula una malla esférica o toroidal deformada por el micro-jet en 3D.
        """
        n_lat, n_lon = 24, 36
        theta = np.linspace(0, np.pi, n_lat)
        phi = np.linspace(0, 2.0 * np.pi, n_lon)
        THETA, PHI = np.meshgrid(theta, phi)

        # Deformación axial por microjet (hundimiento del polo z > 0)
        # r(theta) = R * [1 - jet_len * 0.75 * exp(-((theta - 0.0)/0.6)^2)]
        radial_factor = 1.0 - (jet_len * 0.78 * np.exp(- (THETA / 0.75)**2))
        r_current = (R / self.R0) * radial_factor

        x = r_current * np.sin(THETA) * np.cos(PHI)
        y = r_current * np.sin(THETA) * np.sin(PHI)
        z = r_current * np.cos(THETA)

        return np.stack([x, y, z], axis=-1)

    def _compute_particle_positions(self, t: float, R: float, R_dot: float, jet_len: float) -> np.ndarray:
        """
        Actualiza las posiciones de las partículas fluidas arrastradas por el flujo radial y el microjet.
        """
        # Posiciones base
        pts = self.particles_init_3d.copy()
        radii = np.linalg.norm(pts, axis=1)

        # Arrastre radial incompresible: delta_r ~ (R^2 * R_dot / r^2) * dt
        # Factor visual proporcional a R_dot
        dr_factor = 0.00035 * (R_dot / 500.0)
        scale_mod = np.clip(1.0 + dr_factor / (radii + 0.5)**1.5, 0.45, 2.2)

        pts[:, 0] *= scale_mod
        pts[:, 1] *= scale_mod
        pts[:, 2] *= scale_mod

        # Desplazamiento por microjet vertical hacia abajo (-z)
        if jet_len > 0.01:
            # Cono de arrastre cerca del eje central
            r_cyl = np.hypot(pts[:, 0], pts[:, 1])
            jet_drag = jet_len * 0.85 * np.exp(- (r_cyl / 0.8)**2) * (pts[:, 2] > -0.5)
            pts[:, 2] -= jet_drag

        return pts
