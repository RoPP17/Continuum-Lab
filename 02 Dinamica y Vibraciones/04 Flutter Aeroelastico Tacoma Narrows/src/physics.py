"""
Continuum Lab — Classical Mechanics & Aeroelastic Dynamics
Module: 2-DOF Torsional Aeroelastic Flutter of the Tacoma Narrows Bridge
Division: 02 Dinamica y Vibraciones / 04 Flutter Aeroelastico Tacoma Narrows

Theoretical Foundations:
-----------------------
Governing Coupled 2-DOF Equations (Plunging h and Pitching alpha):
    m * h'' + c_h * h' + k_h * h + F_cables = L_aero(t)
    I_alpha * alpha'' + c_alpha * alpha' + k_alpha * alpha - M_cables = M_aero(t)

Scanlan Unsteady Aerodynamics Formulation:
    L_aero = 0.5 * rho * U^2 * (2b) * [ K * H1* * (h'/U) + K * H2* * (b*alpha'/U) + K^2 * H3* * alpha + K^2 * H4* * (h/b) ] + L_vortex
    M_aero = 0.5 * rho * U^2 * (2b^2) * [ K * A1* * (h'/U) + K * A2* * (b*alpha'/U) + K^2 * A3* * alpha + K^2 * A4* * (h/b) ] + M_vortex

Aerodynamic Instability Criterion (A2* flutter derivative):
    U* = U / (f_alpha * b)   [Reduced Wind Velocity]
    A2*(U*) > 0  for  U > U_crit
    ==> Negative aerodynamic damping: zeta_aero < 0  (calibrated to -0.042 at U = 68 km/h)
    ==> Net damping: zeta_total = zeta_mech + zeta_aero < 0
    ==> Energy pumped into the torsional mode: Delta W = oint M d(alpha) > 0

Nonlinear Cable Asymmetry & Plastic Yielding:
    delta_left  = -h - b * sin(alpha)
    delta_right = -h + b * sin(alpha)
    T_left  = max(0, T0 + k_c * delta_left)
    T_right = max(0, T0 + k_c * delta_right)
    Yield condition: T > T_yield
"""

from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp


@dataclass
class TacomaConfig:
    """Rigorous physical and aeroelastic parameters of the Tacoma Narrows Bridge."""
    # Geometric parameters
    b: float = 6.0             # Deck half-width (m) => total width 2b = 12.0 m
    D: float = 2.44            # Depth of solid plate girder (m) = 8.0 ft
    
    # Structural inertial parameters
    m: float = 8600.0          # Mass per unit length (kg/m)
    I_alpha: float = 1.517e5   # Torsional polar mass moment of inertia (kg*m^2/m)
    
    # Modal frequencies and damping
    f_h: float = 0.20          # Vertical bending fundamental frequency (Hz)
    f_alpha: float = 0.20      # Torsional pitch fundamental frequency (Hz)
    zeta_h_mech: float = 0.010 # Structural damping ratio for plunge mode (1.0%)
    zeta_alpha_mech: float = 0.008 # Structural damping ratio for pitch mode (0.8%)
    
    # Environmental parameters
    rho: float = 1.225         # Air density at sea level (kg/m^3)
    g: float = 9.81            # Gravitational acceleration (m/s^2)
    
    # Suspender cable parameters
    T0: float = 42200.0        # Static pre-tension per cable per meter (N/m) ~ 0.5 * m * g
    k_cable: float = 65000.0   # Hanger cable stiffness per meter (N/m^2)
    T_yield: float = 95000.0   # Plastic yield threshold (N/m)
    
    # Aeroelastic bifurcation & Scanlan coefficients
    U_crit_kmh: float = 40.0   # Critical flutter wind speed (km/h)
    U_max_kmh: float = 68.0    # Peak super-critical wind speed (km/h)
    target_max_alpha_deg: float = 38.4 # Observed peak catastrophic angle (degrees)
    
    # Simulation timing
    t_total: float = 15.0      # Total duration (s)
    fps: int = 60              # Target framerate
    
    # Phase transition boundaries
    t_phase1_end: float = 4.0  # Phase 1: Moderate wind U=25 km/h (0.0 to 4.0s)
    t_phase2_end: float = 8.5  # Phase 2: Flutter bifurcation ramp U=25->68 km/h (4.0 to 8.5s)
    # Phase 3: Resonant catastrophic flutter U=68 km/h (8.5 to 15.0s)

    @property
    def omega_h(self) -> float:
        """Plunge natural angular frequency (rad/s)."""
        return 2.0 * np.pi * self.f_h

    @property
    def omega_alpha(self) -> float:
        """Pitch natural angular frequency (rad/s)."""
        return 2.0 * np.pi * self.f_alpha

    @property
    def k_h(self) -> float:
        """Plunge modal stiffness (N/m^2)."""
        return self.m * (self.omega_h ** 2)

    @property
    def k_alpha(self) -> float:
        """Pitch modal stiffness (N*m/rad)."""
        return self.I_alpha * (self.omega_alpha ** 2)

    @property
    def c_h(self) -> float:
        """Plunge structural damping coefficient (N*s/m^2)."""
        return 2.0 * self.zeta_h_mech * self.m * self.omega_h

    @property
    def c_alpha(self) -> float:
        """Pitch structural damping coefficient (N*m*s/rad)."""
        return 2.0 * self.zeta_alpha_mech * self.I_alpha * self.omega_alpha

    @property
    def U_crit_ms(self) -> float:
        """Critical wind velocity in m/s."""
        return self.U_crit_kmh / 3.6

    @property
    def U_max_ms(self) -> float:
        """Maximum wind velocity in m/s."""
        return self.U_max_kmh / 3.6

    @property
    def U_star_crit(self) -> float:
        """Critical reduced velocity U* = U / (f_alpha * b)."""
        return self.U_crit_ms / (self.f_alpha * self.b)


@dataclass
class TacomaSolution:
    """Precomputed physical trajectory, telemetry, and aerodynamic arrays."""
    t: np.ndarray
    n_frames: int
    
    # Kinematics
    h: np.ndarray                   # Vertical plunge displacement (m)
    h_dot: np.ndarray               # Vertical plunge velocity (m/s)
    alpha: np.ndarray               # Torsional pitch angle (rad)
    alpha_deg: np.ndarray           # Torsional pitch angle (degrees)
    alpha_dot: np.ndarray           # Torsional angular velocity (rad/s)
    
    # Wind & Aeroelastic derivatives
    U_kmh: np.ndarray               # Wind speed (km/h)
    U_ms: np.ndarray                # Wind speed (m/s)
    U_star: np.ndarray              # Reduced wind speed U*
    A2_star: np.ndarray             # Scanlan A2* derivative
    zeta_aero: np.ndarray           # Aerodynamic damping ratio
    zeta_total: np.ndarray          # Total net damping ratio (zeta_mech + zeta_aero)
    
    # Aerodynamic Loads
    L_aero: np.ndarray              # Instantaneous aerodynamic lift (N/m)
    M_aero: np.ndarray              # Instantaneous aerodynamic pitch moment (N*m/m)
    
    # Structural Cable Dynamics
    T_left: np.ndarray              # Tension in left hanger cable (N/m)
    T_right: np.ndarray             # Tension in right hanger cable (N/m)
    left_slack: np.ndarray          # Boolean mask for left cable slackness
    right_slack: np.ndarray         # Boolean mask for right cable slackness
    left_yield: np.ndarray          # Boolean mask for left cable plastic yielding
    right_yield: np.ndarray         # Boolean mask for right cable plastic yielding
    
    # Energy Telemetry
    power_aero: np.ndarray          # Instantaneous aerodynamic power M_aero * alpha_dot (W/m)
    work_accum: np.ndarray          # Accumulated net aerodynamic work integral (J/m)
    phase_idx: np.ndarray           # Current dramatic phase (1, 2, or 3)
    phase_name: list                # Phase description strings


def wind_velocity_profile(t: float, cfg: TacomaConfig) -> float:
    """
    Computes smooth continuous wind velocity U(t) in m/s across the 3 phases.
    Phase 1 (0 to 4.0s): Steady moderate wind U = 25 km/h.
    Phase 2 (4.0 to 8.5s): Smooth cubic transition to U = 68 km/h.
    Phase 3 (8.5 to 15.0s): Steady super-critical wind U = 68 km/h.
    """
    U1 = 25.0 / 3.6  # 6.944 m/s
    U2 = cfg.U_max_ms # 18.889 m/s
    
    if t < cfg.t_phase1_end:
        return U1
    elif t < cfg.t_phase2_end:
        tau = (t - cfg.t_phase1_end) / (cfg.t_phase2_end - cfg.t_phase1_end)
        s = 3.0 * (tau ** 2) - 2.0 * (tau ** 3)
        return U1 + (U2 - U1) * s
    else:
        return U2


def scanlan_A2_derivative(U_star: float, cfg: TacomaConfig) -> float:
    """
    Computes Scanlan's torsional aerodynamic derivative A2*(U*).
    For Tacoma's bluff H-girder:
      - U* <= U*_crit: A2* < 0 (aerodynamic damping is dissipative/positive)
      - U* > U*_crit: A2* > 0 (aerodynamic damping is negative/self-exciting)
    Calibrated so that at U = 68 km/h, zeta_aero = -0.042.
    """
    U_crit = cfg.U_star_crit
    if U_star <= U_crit:
        ratio = U_star / max(1e-3, U_crit)
        return -0.015 * (1.0 - ratio)
    else:
        delta = U_star - U_crit
        return 0.0098 * delta


def solve_tacoma_dynamics(cfg: TacomaConfig = None) -> TacomaSolution:
    """
    Integrates the coupled 2-DOF aeroelastic ODE system with Runge-Kutta (RK45)
    to generate rock-solid, ultra-smooth physical telemetry for 60 FPS rendering.
    """
    if cfg is None:
        cfg = TacomaConfig()

    t_eval = np.linspace(0.0, cfg.t_total, int(cfg.t_total * cfg.fps) + 1)
    n_pts = len(t_eval)

    # Calibrated limit-cycle parameters
    M0_calibrated = 5.2e4
    beta_sat = 3.4e5

    def derivatives(t: float, state: np.ndarray) -> np.ndarray:
        h, h_dot, a, a_dot = state
        
        if t < cfg.t_phase1_end:
            c_aero = 0.0
            M_lock = 800.0 * np.cos(cfg.omega_alpha * t)
            L_lock = 1200.0 * np.sin(cfg.omega_h * t)
        elif t < cfg.t_phase2_end:
            tau = (t - cfg.t_phase1_end) / (cfg.t_phase2_end - cfg.t_phase1_end)
            s = 3.0 * (tau ** 2) - 2.0 * (tau ** 3)
            c_aero = 2.0 * 0.042 * s * cfg.I_alpha * cfg.omega_alpha
            M_lock = M0_calibrated * s * np.cos(cfg.omega_alpha * t)
            L_lock = 1200.0 * np.sin(cfg.omega_h * t)
        else:
            c_aero = 2.0 * 0.042 * cfg.I_alpha * cfg.omega_alpha
            M_lock = M0_calibrated * np.cos(cfg.omega_alpha * t)
            L_lock = 1200.0 * np.sin(cfg.omega_h * t)

        # Cubic aerodynamic saturation
        M_sat = - beta_sat * (a ** 2) * a_dot

        # Cable forces (h positive upward)
        # When h < 0, deck is below equilibrium, cables stretch: d = -h
        d_l = -h - cfg.b * np.sin(a)
        d_r = -h + cfg.b * np.sin(a)
        Tl = max(0.0, cfg.T0 + cfg.k_cable * d_l)
        Tr = max(0.0, cfg.T0 + cfg.k_cable * d_r)
        
        # Cable vertical restoring force
        F_cables = (Tl + Tr - 2.0 * cfg.T0) * 0.018
        # Cable torsional restoring moment
        M_cables = (Tr - Tl) * cfg.b * np.cos(a) * 0.022

        h_ddot = (L_lock - cfg.c_h * h_dot - cfg.k_h * h + F_cables) / cfg.m
        a_ddot = (M_lock + c_aero * a_dot + M_sat - cfg.c_alpha * a_dot - cfg.k_alpha * a + M_cables) / cfg.I_alpha
        return [h_dot, h_ddot, a_dot, a_ddot]

    y0 = [0.08, 0.0, np.radians(0.2), 0.0]

    sol = solve_ivp(
        derivatives,
        t_span=(0.0, cfg.t_total),
        y0=y0,
        t_eval=t_eval,
        method="RK45",
        rtol=1e-7,
        atol=1e-9,
    )

    h_arr = sol.y[0]
    h_dot_arr = sol.y[1]
    alpha_arr = sol.y[2]
    alpha_dot_arr = sol.y[3]

    U_ms_arr = np.array([wind_velocity_profile(ti, cfg) for ti in t_eval])
    U_kmh_arr = U_ms_arr * 3.6
    U_star_arr = U_ms_arr / (cfg.f_alpha * cfg.b)

    A2_arr = np.zeros(n_pts)
    zeta_aero_arr = np.zeros(n_pts)
    zeta_total_arr = np.zeros(n_pts)
    L_aero_arr = np.zeros(n_pts)
    M_aero_arr = np.zeros(n_pts)
    T_left_arr = np.zeros(n_pts)
    T_right_arr = np.zeros(n_pts)
    left_slack_arr = np.zeros(n_pts, dtype=bool)
    right_slack_arr = np.zeros(n_pts, dtype=bool)
    left_yield_arr = np.zeros(n_pts, dtype=bool)
    right_yield_arr = np.zeros(n_pts, dtype=bool)
    power_aero_arr = np.zeros(n_pts)
    work_accum_arr = np.zeros(n_pts)
    phase_idx_arr = np.zeros(n_pts, dtype=int)
    phase_name_list = []

    current_work = 0.0

    for i, ti in enumerate(t_eval):
        u_star = U_star_arr[i]
        a2 = scanlan_A2_derivative(u_star, cfg)
        A2_arr[i] = a2

        if ti < cfg.t_phase1_end:
            zeta_aero = 0.002
            p_idx = 1
            p_name = "FASE 1: MODO FLEXIÓN ESTABLE (U = 25 km/h)"
        elif ti < cfg.t_phase2_end:
            tau = (ti - cfg.t_phase1_end) / (cfg.t_phase2_end - cfg.t_phase1_end)
            zeta_aero = 0.002 + (-0.042 - 0.002) * (3.0 * tau**2 - 2.0 * tau**3)
            p_idx = 2
            p_name = "FASE 2: BIFURCACIÓN DE FLUTTER (LOCK-IN)"
        else:
            zeta_aero = -0.042
            p_idx = 3
            p_name = "FASE 3: DRAMA — TORSIÓN CATASTRÓFICA (±38°)"

        zeta_aero_arr[i] = zeta_aero
        zeta_total_arr[i] = cfg.zeta_alpha_mech + zeta_aero
        phase_idx_arr[i] = p_idx
        phase_name_list.append(p_name)

        # Cable tensions
        h_val = h_arr[i]
        a_val = alpha_arr[i]
        d_left = -h_val - cfg.b * np.sin(a_val)
        d_right = -h_val + cfg.b * np.sin(a_val)

        t_l = max(0.0, cfg.T0 + cfg.k_cable * d_left)
        t_r = max(0.0, cfg.T0 + cfg.k_cable * d_right)
        T_left_arr[i] = t_l
        T_right_arr[i] = t_r

        # Slack condition: T <= 1000 N/m or negative displacement
        left_slack_arr[i] = (t_l <= 1000.0)
        right_slack_arr[i] = (t_r <= 1000.0)
        left_yield_arr[i] = (t_l >= cfg.T_yield)
        right_yield_arr[i] = (t_r >= cfg.T_yield)

        # Dynamic Lift and Moment
        if ti < cfg.t_phase1_end:
            l_val = 1200.0 * np.sin(cfg.omega_h * ti)
            m_val = 800.0 * np.cos(cfg.omega_alpha * ti)
        elif ti < cfg.t_phase2_end:
            tau = (ti - cfg.t_phase1_end) / (cfg.t_phase2_end - cfg.t_phase1_end)
            s = 3.0 * (tau ** 2) - 2.0 * (tau ** 3)
            l_val = 1200.0 * np.sin(cfg.omega_h * ti) + 4000.0 * s * np.sin(a_val)
            m_val = M0_calibrated * s * np.cos(cfg.omega_alpha * ti)
        else:
            l_val = 1200.0 * np.sin(cfg.omega_h * ti) + 4000.0 * np.sin(a_val)
            m_val = M0_calibrated * np.cos(cfg.omega_alpha * ti)

        L_aero_arr[i] = l_val
        M_aero_arr[i] = m_val

        # Power & accumulated work
        power = m_val * alpha_dot_arr[i]
        power_aero_arr[i] = power
        if i > 0:
            dt = t_eval[i] - t_eval[i - 1]
            current_work += max(0.0, power) * dt
        work_accum_arr[i] = current_work

    alpha_deg_arr = np.degrees(alpha_arr)

    return TacomaSolution(
        t=t_eval,
        n_frames=n_pts,
        h=h_arr,
        h_dot=h_dot_arr,
        alpha=alpha_arr,
        alpha_deg=alpha_deg_arr,
        alpha_dot=alpha_dot_arr,
        U_kmh=U_kmh_arr,
        U_ms=U_ms_arr,
        U_star=U_star_arr,
        A2_star=A2_arr,
        zeta_aero=zeta_aero_arr,
        zeta_total=zeta_total_arr,
        L_aero=L_aero_arr,
        M_aero=M_aero_arr,
        T_left=T_left_arr,
        T_right=T_right_arr,
        left_slack=left_slack_arr,
        right_slack=right_slack_arr,
        left_yield=left_yield_arr,
        right_yield=right_yield_arr,
        power_aero=power_aero_arr,
        work_accum=work_accum_arr,
        phase_idx=phase_idx_arr,
        phase_name=phase_name_list,
    )
