"""
Continuum Lab — Classical Mechanics & Nonlinear Dynamics
Module: Inverted Kapitza Pendulum Physical Model & Numerical Solvers
Division: 02 Dinamica y Vibraciones / 03 Pendulo Invertido Kapitza

Theoretical Foundations:
-----------------------
Governing Equation:
    theta'' + b * theta' + (g/L - (a*omega^2)/L * cos(omega*t)) * sin(theta) + tau_ext(t) = 0

Kapitza-Bogoliubov Averaging Method:
    Decomposition: theta(t) = Theta(t) + xi(t)
    Fast vibrational component: xi(t) = -(a/L) * sin(Theta) * cos(omega*t)
    Averaged Landau-Kapitza Effective Potential:
        V_eff(Theta) = m*g*L*(1 - cos(Theta)) + (m * a^2 * omega^2 / 4) * sin^2(Theta)
    Kapitza Dynamic Stability Condition:
        (a * omega)^2 > 2 * g * L
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple
import numpy as np
from scipy.integrate import solve_ivp
from scipy.ndimage import uniform_filter1d


@dataclass
class KapitzaConfig:
    """Rigorous physical parameters for Kapitza's inverted pendulum."""
    # Physical system
    m: float = 0.5          # Mass of bob (kg)
    L: float = 1.0          # Length of rigid rod (m)
    g: float = 9.81         # Gravitational acceleration (m/s^2)
    b: float = 0.85         # Viscous damping coefficient (s^-1)

    # Base excitation parameters
    a: float = 0.04         # Amplitude of pivot vibration (m) = 4.0 cm
    f: float = 55.0         # Fast base frequency (Hz)
    
    # Simulation timing
    t_total: float = 15.0   # Total animation duration (s)
    fps: int = 60           # Framerate
    
    # Event timestamps
    t_pert_start: float = 4.0       # Perturbation start time (s)
    t_pert_end: float = 4.25        # Perturbation end time (s)
    target_deflection_deg: float = 35.0  # Desired lateral deflection (deg)
    tau_pert_amplitude: float = 41.5     # Calibrated torque amplitude (N*m / (m*L^2))
    
    t_shutdown: float = 8.0         # Vibration shutdown start (s)
    t_shutdown_tau: float = 0.035   # Exponential decay constant for shutdown (s)

    @property
    def omega(self) -> float:
        """Angular frequency of excitation (rad/s)."""
        return 2.0 * np.pi * self.f

    @property
    def dynamic_factor(self) -> float:
        """(a * omega)^2 (m^2/s^2)."""
        return (self.a * self.omega) ** 2

    @property
    def stability_threshold(self) -> float:
        """2 * g * L (m^2/s^2)."""
        return 2.0 * self.g * self.L

    @property
    def stability_ratio(self) -> float:
        """Ratio (a * omega)^2 / (2 * g * L). Must be > 1 for stability."""
        return self.dynamic_factor / self.stability_threshold

    @property
    def f_crit(self) -> float:
        """Minimum critical base frequency for upright stability (Hz)."""
        omega_crit = np.sqrt(2.0 * self.g * self.L) / self.a
        return omega_crit / (2.0 * np.pi)

    @property
    def basin_half_width_deg(self) -> float:
        """Half-width of attraction basin around upright vertical (deg)."""
        cos_crit = - (2.0 * self.g * self.L) / self.dynamic_factor
        cos_crit = np.clip(cos_crit, -1.0, 1.0)
        theta_crit = np.arccos(cos_crit)
        return float(180.0 - np.degrees(theta_crit))


@dataclass
class KapitzaSolution:
    """Precomputed trajectory and physical telemetry arrays."""
    t: np.ndarray
    theta: np.ndarray               # Full instantaneous angle (rad)
    theta_deg: np.ndarray           # Full angle (deg)
    theta_dot: np.ndarray           # Angular velocity (rad/s)
    theta_slow: np.ndarray          # Averaged Kapitza angle Theta (rad)
    theta_slow_deg: np.ndarray      # Averaged angle (deg)
    y_base: np.ndarray              # Pivot displacement y0(t) (m)
    a_base: np.ndarray              # Pivot acceleration y0''(t) (m/s^2)
    omega_inst: np.ndarray          # Instantaneous base angular frequency (rad/s)
    f_inst: np.ndarray              # Instantaneous base frequency (Hz)
    is_stable: np.ndarray           # Boolean condition per frame
    v_eff_instant: np.ndarray       # Effective potential at theta_slow (J)
    tau_ext: np.ndarray             # External torque applied (N*m / I)
    phase_id: np.ndarray            # 1, 2, or 3
    phase_label: list               # Human readable phase description
    n_frames: int = field(init=False)

    def __post_init__(self):
        self.n_frames = len(self.t)


def compute_effective_potential(
    theta: np.ndarray,
    omega: float,
    config: KapitzaConfig
) -> np.ndarray:
    """
    Computes Landau-Kapitza effective potential:
        V_eff(Theta) = m*g*L*(1 - cos(Theta)) + (m * a^2 * omega^2 / 4) * sin^2(Theta)
    """
    term_gravity = config.m * config.g * config.L * (1.0 - np.cos(theta))
    term_vibrational = (config.m * (config.a ** 2) * (omega ** 2) / 4.0) * (np.sin(theta) ** 2)
    return term_gravity + term_vibrational


def compute_potential_curvature(
    theta: float,
    omega: float,
    config: KapitzaConfig
) -> float:
    """
    Computes second derivative d^2 V_eff / d Theta^2.
    At Theta = pi:
        d^2 V_eff / d Theta^2 (pi) = - m*g*L + m * a^2 * omega^2 / 2
    """
    d2V = (
        config.m * config.g * config.L * np.cos(theta)
        + (config.m * (config.a ** 2) * (omega ** 2) / 2.0) * np.cos(2.0 * theta)
    )
    return float(d2V)


def solve_kapitza_dynamics(config: KapitzaConfig) -> KapitzaSolution:
    """
    Integrates the exact governing nonlinear ODE with decoupled high-precision
    temporal solver and samples onto the exact 60 FPS animation grid.
    """
    n_frames = int(config.t_total * config.fps) + 1
    t_eval = np.linspace(0.0, config.t_total, n_frames)

    omega0 = config.omega
    a0 = config.a
    g = config.g
    L = config.L
    b = config.b

    def base_kinematics(t: float) -> Tuple[float, float, float, float]:
        """Returns amplitude, omega, y0(t), and y0''(t)."""
        if t < config.t_shutdown:
            w = omega0
            amp = a0
        else:
            decay = np.exp(-(t - config.t_shutdown) / config.t_shutdown_tau)
            w = omega0 * decay
            amp = a0 * decay

        if amp > 1e-5:
            # y0(t) = a * cos(omega * t)
            # y0''(t) = - a * omega^2 * cos(omega * t)
            y0 = amp * np.cos(w * t)
            y0_ddot = - amp * (w ** 2) * np.cos(w * t)
        else:
            y0 = 0.0
            y0_ddot = 0.0
        return amp, w, y0, y0_ddot

    def external_torque(t: float) -> float:
        """Calibrated lateral disturbance pulse during Phase 2."""
        if config.t_pert_start <= t <= config.t_pert_end:
            dt = config.t_pert_end - config.t_pert_start
            return - config.tau_pert_amplitude * np.sin(np.pi * (t - config.t_pert_start) / dt)
        return 0.0

    def ode_system(t: float, y: np.ndarray) -> np.ndarray:
        theta, theta_dot = y
        amp, w, y0, a_base = base_kinematics(t)
        tau = external_torque(t)

        # Full nonlinear equation of motion:
        # theta'' + b*theta' + ((g + a_base)/L)*sin(theta) + tau = 0
        # where a_base = y0''(t)
        theta_ddot = - b * theta_dot - ((g + a_base) / L) * np.sin(theta) + tau
        return np.array([theta_dot, theta_ddot])

    # Initial condition: exactly inverted with tiny numerical seed to test stability
    y0_init = [np.pi, 0.0]

    # Use RK45 with dense internal sub-stepping to capture the 55 Hz carrier
    sol = solve_ivp(
        ode_system,
        (0.0, config.t_total),
        y0_init,
        t_eval=t_eval,
        method="RK45",
        max_step=1.5e-4,
        rtol=1e-7,
        atol=1e-7,
    )

    t_arr = sol.t
    theta_arr = sol.y[0]
    theta_dot_arr = sol.y[1]

    # Compute slow trajectory Theta(t) via moving average over fast carrier
    # Window size 7 frames at 60 fps filters out 55 Hz stroboscopic modulation
    theta_slow = uniform_filter1d(theta_arr, size=7)

    # Precalculate per-frame kinematic and diagnostic arrays
    y_base = np.zeros(n_frames)
    a_base = np.zeros(n_frames)
    omega_inst = np.zeros(n_frames)
    f_inst = np.zeros(n_frames)
    tau_ext = np.zeros(n_frames)
    is_stable = np.zeros(n_frames, dtype=bool)
    phase_id = np.zeros(n_frames, dtype=int)
    phase_label = []
    v_eff_instant = np.zeros(n_frames)

    for i, t in enumerate(t_arr):
        amp, w, y0_val, a_base_val = base_kinematics(t)
        tau_val = external_torque(t)

        y_base[i] = y0_val
        a_base[i] = a_base_val
        omega_inst[i] = w
        f_inst[i] = w / (2.0 * np.pi)
        tau_ext[i] = tau_val

        condition_met = ((amp * w) ** 2) > (2.0 * g * L)
        is_stable[i] = condition_met

        if t < config.t_pert_start:
            phase_id[i] = 1
            phase_label.append("FASE 1: ESTABILIZACIÓN ACTIVA")
        elif t < config.t_shutdown:
            phase_id[i] = 2
            phase_label.append("FASE 2: PERTURBACIÓN EXTERNA")
        else:
            phase_id[i] = 3
            phase_label.append("FASE 3: PARADA DE EMERGENCIA / DESPLOME")

        # Instantaneous effective potential at slow angle
        v_eff_instant[i] = compute_effective_potential(
            np.array([theta_slow[i]]), w, config
        )[0]

    return KapitzaSolution(
        t=t_arr,
        theta=theta_arr,
        theta_deg=np.degrees(theta_arr),
        theta_dot=theta_dot_arr,
        theta_slow=theta_slow,
        theta_slow_deg=np.degrees(theta_slow),
        y_base=y_base,
        a_base=a_base,
        omega_inst=omega_inst,
        f_inst=f_inst,
        is_stable=is_stable,
        v_eff_instant=v_eff_instant,
        tau_ext=tau_ext,
        phase_id=phase_id,
        phase_label=phase_label,
    )
