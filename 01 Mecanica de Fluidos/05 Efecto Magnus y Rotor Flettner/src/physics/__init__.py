"""
Physical and analytical modules for the Magnus Effect & Flettner Rotor.
"""
from .magnus_sim import MagnusConfig, MagnusSimulation, MagnusTelemetry
from .export_excel_benchmark import create_magnus_excel_benchmark

__all__ = [
    "MagnusConfig",
    "MagnusSimulation",
    "MagnusTelemetry",
    "create_magnus_excel_benchmark",
]
