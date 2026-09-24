"""
Continuum Lab — Visual Rendering & Telemetry HUD Pipeline
Cybernetic Laboratory Presentation Architecture
Division: Scientific Visualization & Graphical Shaders
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
    High-Definition Visual Rendering Engine with Non-Overlapping HUD Telemetry Overlays.
    Enforces strict bounding box margins and collision-free typography.
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
          - Solid: Dark metallic body with luminous cyan rim glow.
          - HUD: Strictly bounded telemetry cards (zero overlap).
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
        frame[mask_resized] = [16, 20, 24]  # Deep slate charcoal

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
        """
        Draws non-overlapping cybernetic HUD cards with strict bounding box isolation.
        No text collides with other text, borders, or active visual dynamics.
        """
        card_x0, card_y0 = 20, 20
        card_w, card_h = 520, 225
        card_x1, card_y1 = card_x0 + card_w, card_y0 + card_h

        # Solid background card with subtle cybernetic cyan border
        cv2.rectangle(frame, (card_x0, card_y0), (card_x1, card_y1), (13, 17, 23), -1)
        cv2.rectangle(frame, (card_x0, card_y0), (card_x1, card_y1), (0, 240, 255), 1)

        # Typography configuration
        font_head = cv2.FONT_HERSHEY_SIMPLEX
        font_mono = cv2.FONT_HERSHEY_PLAIN

        # Header Title
        cv2.putText(frame, "CONTINUUM LAB // LBM-D2Q9", (card_x0 + 18, card_y0 + 28), font_head, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, "VORTEX DYNAMICS & TELEMETRY", (card_x0 + 18, card_y0 + 46), font_mono, 0.90, (140, 160, 180), 1, cv2.LINE_AA)

        # Horizontal accent rule
        cv2.line(frame, (card_x0 + 18, card_y0 + 56), (card_x1 - 18, card_y0 + 56), (40, 50, 65), 1)

        # Extract Telemetry
        re_val = telem.get("reynolds", 0.0)
        ma_val = telem.get("mach", 0.0)
        cd_val = telem.get("cd", 0.0)
        cl_val = telem.get("cl", 0.0)
        fps_val = telem.get("fps", 0.0)
        step_val = telem.get("step", 0)
        backend = telem.get("backend", "CUDA RTX 5070")

        # Telemetry Metrics (Exact non-overlapping vertical spacing: 23px delta)
        text_x = card_x0 + 18
        y_cursor = card_y0 + 78

        cv2.putText(frame, f"REYNOLDS (Re):     {re_val:.1f}", (text_x, y_cursor), font_mono, 1.05, (0, 240, 255), 1, cv2.LINE_AA)
        y_cursor += 23
        cv2.putText(frame, f"MACH NUMBER (Ma):  {ma_val:.3f} (Incompressible)", (text_x, y_cursor), font_mono, 1.05, (0, 255, 150), 1, cv2.LINE_AA)
        y_cursor += 23
        cv2.putText(frame, f"DRAG COEFF (Cd):   {cd_val:.3f}", (text_x, y_cursor), font_mono, 1.05, (0, 170, 255), 1, cv2.LINE_AA)
        y_cursor += 23
        cv2.putText(frame, f"LIFT COEFF (Cl):   {cl_val:+.3f}", (text_x, y_cursor), font_mono, 1.05, (255, 0, 127), 1, cv2.LINE_AA)
        y_cursor += 23
        cv2.putText(frame, f"TIME STEP:         {step_val:06d}", (text_x, y_cursor), font_mono, 1.00, (180, 180, 180), 1, cv2.LINE_AA)
        y_cursor += 23
        cv2.putText(frame, f"SOLVER:            {backend}  |  {fps_val:.0f} FPS", (text_x, y_cursor), font_mono, 1.00, (57, 255, 20), 1, cv2.LINE_AA)

        # Record history for limit cycle phase portrait
        self.cd_history.append(cd_val)
        self.cl_history.append(cl_val)
        if len(self.cd_history) > self.max_history:
            self.cd_history.pop(0)
            self.cl_history.pop(0)

        # Isolated Phase Plot Card (Bottom-Right: Cd vs Cl Limit Cycle)
        self._overlay_phase_card(frame)

    def _overlay_phase_card(self, frame: np.ndarray) -> None:
        """Plots the limit cycle trajectory (Cd, Cl) showing Hopf bifurcation and vortex shedding."""
        x0, y0, w, h = self.width - 260, self.height - 180, 240, 160
        cv2.rectangle(frame, (x0, y0), (x0 + w, y0 + h), (13, 17, 23), -1)
        cv2.rectangle(frame, (x0, y0), (x0 + w, y0 + h), (127, 0, 255), 1)

        cv2.putText(
            frame, "PHASE PORTRAIT (Cd vs Cl)",
            (x0 + 14, y0 + 22),
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
            py = int(y0 + h - 20 - (c_l - cl_min) / (cl_max - cl_min) * (h - 48))
            plot_pts.append((px, py))

        for k in range(len(plot_pts) - 1):
            alpha = float(k) / len(plot_pts)
            b = int(255 * alpha)
            g = int(200 * alpha)
            r = int(255 * (1.0 - alpha))
            cv2.line(frame, plot_pts[k], plot_pts[k + 1], (b, g, r), 1, cv2.LINE_AA)

        # Current state indicator
        if plot_pts:
            cv2.circle(frame, plot_pts[-1], 3, (0, 240, 255), -1, cv2.LINE_AA)
