"""
Continuum Lab — Classical Mechanics & Dynamical Systems
Entry Point: Mechanism with Coriolis Acceleration (2 Bars + Sliding Collar)
Division: 02 Dinamica y Vibraciones / 02 Mecanismo Coriolis Collarin
"""

import sys
import os
import argparse
import webbrowser
import http.server
import socketserver
import threading
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.visualization.generate_plots import render_kinematic_diagnostics
from src.excel.export_coriolis_benchmark import export_coriolis_benchmark
from src.visualization.render_gif import generate_hypnotic_gif
from src.visualization.render_video import render_hypnotic_video


def run_tests():
    """Runs automated pytest verification suite."""
    import pytest
    tests_path = project_root / "tests"
    print("\n[CONTINUUM LAB] Running Kinematic Verification Suite (Pytest)...")
    res = pytest.main([str(tests_path), "-v", "--tb=short"])
    return res == 0


def launch_web_server(port: int = 8085):
    """Spins up a lightweight Python HTTP server and opens the browser."""
    web_dir = project_root / "src" / "visualization" / "web"
    os.chdir(str(web_dir))

    handler = http.server.SimpleHTTPRequestHandler
    
    # Intentar puertos si está ocupado
    for p in range(port, port + 10):
        try:
            httpd = socketserver.TCPServer(("", p), handler)
            actual_port = p
            break
        except OSError:
            continue
    else:
        print("[ERROR] Could not find an open port.")
        return

    url = f"http://localhost:{actual_port}/index.html"
    print(f"\n[CONTINUUM LAB] Hypnotic Coriolis Web Simulator running at:")
    print(f"               >>> {url} <<<")
    print("Press Ctrl+C to terminate the local server.\n")

    # Abrir navegador automáticamente
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[CONTINUUM LAB] Server stopped.")
        httpd.server_close()


def launch_pygame():
    """Launches the desktop Pygame 60 FPS visualizer."""
    from src.visualization.pygame_app import launch_pygame_app
    print("\n[CONTINUUM LAB] Launching Pygame Desktop Visualizer...")
    launch_pygame_app()


def main():
    parser = argparse.ArgumentParser(
        description="Continuum Lab — Mecanismo con Aceleración de Coriolis (2 Barras + Collarín)"
    )
    parser.add_argument("--web", action="store_true", help="Lanza el simulador web interactivo hipnótico en el navegador")
    parser.add_argument("--video", action="store_true", help="Compila el video cinematográfico en MP4 (60 FPS, 1080p)")
    parser.add_argument("--plots", action="store_true", help="Genera gráficos analíticos de alta resolución (300 DPI)")
    parser.add_argument("--gif", action="store_true", help="Renderiza animación GIF cíclica")
    parser.add_argument("--excel", action="store_true", help="Exporta el modelo cinemático dinámico en Excel (XLSX)")
    parser.add_argument("--test", action="store_true", help="Ejecuta la suite de verificación cinemática con Pytest")
    parser.add_argument("--all", action="store_true", help="Ejecuta tests, genera gráficos, exporta Excel y abre web")

    args = parser.parse_args()

    if len(sys.argv) == 1 or args.all:
        print("=" * 72)
        print("   MECANISMO CON ACELERACIÓN DE CORIOLIS")
        print("   Sistema Cinemático de 2 Barras con Collarín Deslizante")
        print("=" * 72)

        # 1. Tests
        tests_passed = run_tests()
        if not tests_passed:
            print("[WARNING] Some kinematic tests failed.")

        # 2. Plots
        print("\n[1/3] Generating publication-grade 300 DPI analytical diagnostics...")
        render_kinematic_diagnostics()

        # 3. Excel
        print("\n[2/3] Exporting dynamic openpyxl engineering benchmark...")
        export_coriolis_benchmark()

        # 4. Web simulator
        print("\n[3/3] Opening Hypnotic Web Simulation...")
        launch_web_server()
        return

    if args.test:
        run_tests()
    if args.video:
        render_hypnotic_video()
    if args.plots:
        render_kinematic_diagnostics()
    if args.gif:
        generate_hypnotic_gif()
    if args.excel:
        export_coriolis_benchmark()
    if args.pygame:
        launch_pygame()
    if args.web:
        launch_web_server()


if __name__ == "__main__":
    main()
