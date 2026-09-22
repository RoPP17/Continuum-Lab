"""
Continuum Lab — Visual Rendering & Telemetry HUD Pipeline
Cybernetic Laboratory Presentation Architecture
Author: Roberto Andrés Pepe Sánchez (@RoPP17) & Continuum Lab Agent
"""

import cv2
import numpy as np
from src.visualization.colormaps import (
    map_vorticity_to_rgb,
    HEX_CYAN,
    HEX_MAGENTA,
    HEX_AMBER,
    HEX_PHOSPHOR,
    HEX_VOID,
    HEX_SLATE,
    HEX_WHITE,
)


class VisualRenderer:
    """
    High-Definition Visual Rendering Engine with HUD Telemetry Overlays.
    Supports real-time display and headless video/image exports.
    """

    def __init__(self, width: int = 1280, height: int = 720):
        self.width = width
        self.height = height
        # Persistent particle tracer buffer for motion blur / particle streak lines
        self.tracer_buffer = np.zeros((height, width, 3), dtype=np.float32)
        # History buffers for HUD phase diagram (Cd vs Cl)
        self.cd_history: list[float] = []
        self.cl_history: list[float] = []
        self.max_history = 300

    def render_frame(
        self,
        vorticity: np.ndarray,
        solid_mask: np.ndarray,
        telemetry: dict,
        omega_0: float = 0.04
    ) -> np.ndarray:
        """
        Renders a composite engineering frame:
          - Field: Cybernetic Vorticity with tanh hyperbolic compression.
          - Solid: Dark metallic cylinder with luminous cyan/magenta rim glow.
          - HUD: Real-time scientific telemetry cards.
        """
        # 1. Base Vorticity Field to RGB
        rgb_raw = map_vorticity_to_rgb(vorticity, omega_0=omega_0)

        # Scale to target display resolution using bicubic interpolation
        frame = cv2.resize(rgb_raw, (self.width, self.height), interpolation=cv2.INTER_CUBIC)

        # 2. Mask out Solid Obstacle with Glowing Rim
        mask_resized = cv2.resize(
            solid_mask.T.astype(np.uint8),
            (self.width, self.height),
            interpolation=cv2.INTER_NEAREST
        ).astype(bool)

        # Draw dark metallic body inside solid
        frame[mask_resized] = [18, 22, 28]  # Deep charcoal

        # Draw obstacle glowing rim
        contours, _ = cv2.findContours(
            mask_resized.astype(np.uint8),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(frame, contours, -1, (255, 240, 0), 2, cv2.LINE_AA)  # Cyan glow in BGR

        # 3. Telemetry HUD Overlay
        self._overlay_hud(frame, telemetry)

        return frame

    def _overlay_hud(self, frame: np.ndarray, telem: dict) -> None:
        """Draws non-intrusive cybernetic HUD cards with telemetry."""
        # Top Header Banner
        cv2.rectangle(frame, (20, 20), (450, 240), (13, 17, 23), -1)  # Card background
        cv2.rectangle(frame, (20, 20), (450, 240), (0, 240, 255), 1)  # Card border

        # Title
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_mono = cv2.FONT_HERSHEY_PLAIN

        cv2.putText(frame, "CONTINUUM LAB // LBM-D2Q9", (35, 48), font, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "DIRECTOR: R. A. PEPE SANCHEZ", (35, 70), font_mono, 0.9, (120, 140, 160), 1, cv2.LINE_AA)

        # Line separator
        cv2.line(frame, (35, 82), (435, 82), (40, 50, 65), 1)

        # Telemetry metrics
        re_val = telem.get("reynolds", 0.0)
        ma_val = telem.get("mach", 0.0)
        cd_val = telem.get("cd", 0.0)
        cl_val = telem.get("cl", 0.0)
        fps_val = telem.get("fps", 0.0)
        step_val = telem.get("step", 0)
        backend = telem.get("backend", "GPU CUDA")

        cv2.putText(frame, f"REYNOLDS (Re):   {re_val:.1f}", (35, 110), font_mono, 1.1, (0, 240, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, f"MACH NUMBER (Ma):{ma_val:.3f} (Incomp)", (35, 130), font_mono, 1.1, (0, 255, 150), 1, cv2.LINE_AA)
        cv2.putText(frame, f"DRAG COEFF (Cd): {cd_val:.3f}", (35, 155), font_mono, 1.1, (0, 170, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, f"LIFT COEFF (Cl): {cl_val:+.3f}", (35, 175), font_mono, 1.1, (255, 0, 127), 1, cv2.LINE_AA)
        cv2.putText(frame, f"TIME STEP:       {step_val:06d}", (35, 200), font_mono, 1.0, (180, 180, 180), 1, cv2.LINE_AA)
        cv2.putText(frame, f"SOLVER:          {backend} [{fps_val:.1f} FPS]", (35, 222), font_mono, 1.0, (57, 255, 20), 1, cv2.LINE_AA)

        # Record history for phase plot
        self.cd_history.append(cd_val)
        self.cl_history.append(cl_val)
        if len(self.cd_history) > self.max_history:
            self.cd_history.pop(0)
            self.cl_history.pop(0)

        # Mini Phase Plot Card (Bottom-Right: Cd vs Cl Limit Cycle)
        self._overlay_phase_card(frame)

    def _overlay_phase_card(self, frame: np.ndarray) -> None:
        """Plots the limit cycle trajectory (Cd, Cl) showing Hopf bifurcation and vortex shedding."""
        x0, y0, w, h = self.width - 260, self.height - 180, 240, 160
        cv2.rectangle(frame, (x0, y0), (x0 + w, y0 + h), (13, 17, 23), -1)
        cv2.rectangle(frame, (x0, y0), (x0 + w, y0 + h), (127, 0, 255), 1)

        cv2.putText(
            frame, "PHASE PORTRAIT (Cd vs Cl)",
            (x0 + 12, y0 + 20),
            cv2.FONT_HERSHEY_PLAIN, 0.85, (255, 255, 255), 1, cv2.LINE_AA
        )

        if len(self.cd_history) < 5:
            return

        cds = np.array(self.cd_history)
        cls = np.array(self.cl_history)

        cd_min, cd_max = np.min(cds) - 0.05, np.max(cds) + 0.05
        cl_min, cl_max = -1.2, 1.2

        if cd_max - cd_min < 0.01:
            cd_max = cd_min + 0.1

        # Map to plot sub-window
        plot_pts = []
        for c_d, c_l in zip(cds, cls):
            px = int(x0 + 20 + (c_d - cd_min) / (cd_max - cd_min) * (w - 40))
            py = int(y0 + h - 20 - (c_l - cl_min) / (cl_max - cl_min) * (h - 45))
            plot_pts.append((px, py))

        for k in range(len(plot_pts) - 1):
            alpha = float(k) / len(plot_pts)
            # Gradient color from violet to cyan
            b = int(255 * alpha)
            g = int(200 * alpha)
            r = int(255 * (1.0 - alpha))
            cv2.line(frame, plot_pts[k], plot_pts[k + 1], (b, g, r), 1, cv2.LINE_AA)

        # Current state indicator
        if plot_pts:
            cv2.circle(frame, plot_pts[-1], 3, (0, 240, 255), -1, cv2.LINE_AA)
