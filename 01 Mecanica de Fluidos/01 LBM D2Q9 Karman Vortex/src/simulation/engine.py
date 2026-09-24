"""
Continuum Lab — Simulation Engine
Manages 60 FPS temporal execution, backend selection, benchmark recording,
and multi-format video rendering (9:16 Vertical for Shorts & 16:9 Widescreen).
Division: Computational Fluid Dynamics & GPU Computing
"""

import time
import os
from typing import Optional
import cv2
import numpy as np

from src.physics.lbm_d2q9 import LBMConfig, LBMD2Q9Solver
from src.visualization.renderer import VisualRenderer


class SimulationEngine:
    """
    Core Controller for Continuum Lab Fluid Dynamics Simulations.
    """

    def __init__(self, config: Optional[LBMConfig] = None, use_gpu: bool = True):
        self.config = config or LBMConfig()
        self.use_gpu = use_gpu

        # Initialize Solver Backend
        self.solver = None
        self.backend_name = "CPU Vectorized"

        if self.use_gpu:
            try:
                from src.physics.lbm_taichi_cuda import LBMD2Q9TaichiCUDA
                self.solver = LBMD2Q9TaichiCUDA(self.config)
                self.backend_name = self.solver.backend
                print(f"[CONTINUUM LAB] Initialized GPU Solver: {self.backend_name}")
            except Exception as e:
                print(f"[CONTINUUM LAB WARNING] Failed GPU init ({e}), falling back to CPU.")
                self.solver = LBMD2Q9Solver(self.config)
                self.backend_name = "CPU Vectorized"
        else:
            self.solver = LBMD2Q9Solver(self.config)
            self.backend_name = "CPU Vectorized"

        # Frame renderer
        self.renderer = VisualRenderer(width=1280, height=512)

        # Performance counters
        self.current_fps: float = 60.0
        self.step_count: int = 0
        self.is_running: bool = False

    def step(self) -> dict:
        """Executes one simulation step and returns real-time telemetry."""
        t0 = time.perf_counter()
        self.solver.step()
        dt = time.perf_counter() - t0

        if dt > 0:
            instant_fps = 1.0 / dt
            self.current_fps = 0.9 * self.current_fps + 0.1 * instant_fps

        self.step_count = self.solver.time_step

        return {
            "step": self.step_count,
            "reynolds": self.config.reynolds,
            "mach": self.config.mach_number,
            "cd": self.solver.cd,
            "cl": self.solver.cl,
            "fps": self.current_fps,
            "backend": self.backend_name
        }

    def get_fields(self):
        """Retrieves vorticity and solid mask from the active solver."""
        if hasattr(self.solver, "get_vorticity_np"):
            wz = self.solver.get_vorticity_np()
            mask = self.solver.get_solid_mask_np()
        else:
            wz = self.solver.vorticity
            mask = self.solver.solid_mask
        return wz, mask

    def render_current_frame(self) -> np.ndarray:
        """Generates a fully composite visual frame with HUD telemetry."""
        wz, mask = self.get_fields()
        telemetry = {
            "step": self.step_count,
            "reynolds": self.config.reynolds,
            "mach": self.config.mach_number,
            "cd": self.solver.cd,
            "cl": self.solver.cl,
            "fps": self.current_fps,
            "backend": self.backend_name
        }
        return self.renderer.render_frame(wz, mask, telemetry)

    def run_interactive(self, window_title: str = "Continuum Lab — LBM D2Q9 Vortex Shedding") -> None:
        """Runs the real-time simulation with OpenCV window display."""
        print(f"[CONTINUUM LAB] Starting real-time simulation. Press 'q' or ESC to exit.")
        cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)

        try:
            while True:
                # Advance 4 simulation sub-steps per visual frame for smooth fluid evolution
                for _ in range(4):
                    self.step()

                frame = self.render_current_frame()
                cv2.imshow(window_title, frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:
                    break
                elif key == ord('r'):
                    print("[CONTINUUM LAB] Resetting simulation state...")
                    self.solver.reset()
        finally:
            cv2.destroyAllWindows()
            print("[CONTINUUM LAB] Simulation stopped.")

    def export_video(
        self,
        output_path: str,
        num_frames: int = 360,
        sub_steps_per_frame: int = 4,
        fps: int = 60,
        format_mode: str = "16:9"
    ) -> None:
        """
        Renders and exports a high-definition video render.
        format_mode:
          - '16:9': 1920x1080 (Horizontal Presentation)
          - '9:16': 1080x1920 (Vertical for YouTube Shorts / Reels)
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        if format_mode == "9:16":
            render_w, render_h = 1080, 1920
        else:
            render_w, render_h = 1920, 1080

        custom_renderer = VisualRenderer(width=render_w, height=render_h)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (render_w, render_h))

        print(f"[CONTINUUM LAB] Rendering {num_frames} frames ({format_mode} @ {fps} FPS) -> {output_path}")

        try:
            for f in range(num_frames):
                for _ in range(sub_steps_per_frame):
                    self.step()

                wz, mask = self.get_fields()
                telemetry = {
                    "step": self.step_count,
                    "reynolds": self.config.reynolds,
                    "mach": self.config.mach_number,
                    "cd": self.solver.cd,
                    "cl": self.solver.cl,
                    "fps": self.current_fps,
                    "backend": self.backend_name
                }
                frame = custom_renderer.render_frame(wz, mask, telemetry)
                writer.write(frame)

                if (f + 1) % 60 == 0 or f == num_frames - 1:
                    print(f"  Frame {f+1}/{num_frames} completed...")
        finally:
            writer.release()
            print(f"[CONTINUUM LAB] Video export complete: {output_path}")
