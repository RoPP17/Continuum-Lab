"""
Continuum Lab — Visual Art Direction & Aesthetic Color Theory
Cybernetic Laboratory / Dark Engineering Palette
Division: Scientific Visualization & Graphical Shaders

Palette Specification:
  - Deep Space Void:     #0a0a0c (Lattice background & domain boundaries)
  - Dark Slate Substrate:#0d1117 (HUD panels and telemetry cards)
  - Vorticity Negative:  #ff007f (Vorticity Magenta / Clockwise shedding)
  - Vorticity Zero:      #0a0a0c (Subdued equilibrium void)
  - Vorticity Positive:  #00f0ff (Electric Cyan / Counter-clockwise shedding)
  - Streamline Tracers:  #39ff14 (Phosphor Lime / High-kinetic particles)
  - Stagnation & Shock:  #ffaa00 (Kinetic Amber / Pressure extrema)
"""

import numpy as np
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap

# Cybernetic Laboratory Color Codes
HEX_VOID = "#0a0a0c"
HEX_SLATE = "#0d1117"
HEX_CYAN = "#00f0ff"
HEX_AMBER = "#ffaa00"
HEX_MAGENTA = "#ff007f"
HEX_PHOSPHOR = "#39ff14"
HEX_WHITE = "#ffffff"
HEX_GRID_LINE = "#1f2937"

# Linear Segmented Colormap for Vorticity: Magenta (-) -> Void (0) -> Cyan (+)
VORTICITY_COLORS = [
    (0.0, "#ff007f"),   # Maximum clockwise vorticity (Vorticity Magenta)
    (0.25, "#7a003f"),  # Intermediate decay
    (0.48, "#15101a"),  # Subdued edge
    (0.5, "#0a0a0c"),   # Neutral zero vorticity (Deep Void)
    (0.52, "#0a1924"),  # Subdued edge
    (0.75, "#007a8a"),  # Intermediate decay
    (1.0, "#00f0ff")    # Maximum counter-clockwise vorticity (Electric Cyan)
]

CMAP_VORTICITY = LinearSegmentedColormap.from_list(
    "cybernetic_vorticity",
    [(pos, col) for pos, col in VORTICITY_COLORS],
    N=1024
)

# Colormap for Velocity / Kinetic Energy Magnitude: Void -> Amber -> Phosphor Lime
SPEED_COLORS = [
    (0.0, "#0a0a0c"),   # Stagnation / Solid wall
    (0.3, "#1a1202"),
    (0.6, "#ffaa00"),   # Kinetic Amber
    (0.85, "#9eff00"),
    (1.0, "#39ff14")    # Phosphor Lime peak kinetic speed
]

CMAP_SPEED = LinearSegmentedColormap.from_list(
    "cybernetic_speed",
    [(pos, col) for pos, col in SPEED_COLORS],
    N=1024
)


def apply_hyperbolic_mapping(vorticity: np.ndarray, omega_0: float = 0.04) -> np.ndarray:
    """
    Applies non-linear hyperbolic tangent contrast mapping:
      normalized_w = tanh(w_z / w_0) in [-1.0, 1.0]
    This boosts distant subtle vortex filaments while preventing boundary layer blowout.
    """
    return np.tanh(vorticity / (omega_0 + 1e-12))


def map_vorticity_to_rgb(vorticity: np.ndarray, omega_0: float = 0.04) -> np.ndarray:
    """
    Converts 2D scalar vorticity field into (ny, nx, 3) uint8 RGB image
    using the Cybernetic Laboratory palette and hyperbolic compression.
    """
    # Normalize with hyperbolic mapping: mapped to [0, 1]
    mapped = 0.5 * (apply_hyperbolic_mapping(vorticity, omega_0) + 1.0)
    # Transpose from (nx, ny) to (ny, nx) for standard image coordinates
    mapped_2d = np.clip(mapped.T, 0.0, 1.0)

    # Sample colormap
    rgba = CMAP_VORTICITY(mapped_2d)
    rgb = (rgba[:, :, :3] * 255.0).astype(np.uint8)
    return rgb
