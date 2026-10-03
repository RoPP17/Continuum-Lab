"""
Continuum Lab — Dinámica No Lineal y Caos Determinista
Generador del Modelo de Benchmark en Excel (.xlsx)
Cumple estrictamente con las directrices de la skill xlsx:
- Fórmulas dinámicas (sin hardcoding de resultados calculados)
- Tipografía profesional Segoe UI
- Formato numérico riguroso
- Metadatos y documentación técnica
"""

from pathlib import Path
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from src.physics.double_pendulum_swarm import DoublePendulumSwarmSimulator, SwarmParameters


def generate_swarm_benchmark_xlsx(output_path: Path) -> Path:
    """
    Ejecuta la simulación de alta precisión y exporta los datos físicos y fórmulas dinámicas
    a un archivo Excel profesional.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    params = SwarmParameters(
        m1=1.0,
        m2=1.0,
        L1=1.5,
        L2=1.5,
        g=9.81,
        num_pendulums=50,
        theta1_0_deg=120.0,
        theta2_0_deg=-60.0,
        delta_theta=1.0e-6,
        duration=15.0,
        fps=60,
    )

    sim = DoublePendulumSwarmSimulator(params)
    data = sim.run_simulation()

    wb = Workbook()

    # Estilos compartidos
    font_family = "Segoe UI"
    hdr_font = Font(name=font_family, size=11, bold=True, color="00F0FF")
    hdr_fill = PatternFill(start_color="0D1117", end_color="0D1117", fill_type="solid")
    subhdr_font = Font(name=font_family, size=10, bold=True, color="FFFFFF")
    subhdr_fill = PatternFill(start_color="161B22", end_color="161B22", fill_type="solid")
    regular_font = Font(name=font_family, size=10, color="E6EDF3")
    accent_font = Font(name=font_family, size=10, bold=True, color="FFE600")
    zebra_fill = PatternFill(start_color="131720", end_color="131720", fill_type="solid")
    border_thin = Border(
        left=Side(style="thin", color="21262D"),
        right=Side(style="thin", color="21262D"),
        top=Side(style="thin", color="21262D"),
        bottom=Side(style="thin", color="21262D"),
    )

    # =========================================================================
    # HOJA 1: RESUMEN Y PARÁMETROS
    # =========================================================================
    ws_res = wb.active
    ws_res.title = "Resumen_Ejecutivo"
    ws_res.views.sheetView[0].showGridLines = True

    # Título principal
    ws_res.merge_cells("A1:D1")
    t_cell = ws_res["A1"]
    t_cell.value = "CONTINUUM LAB // BENCHMARK ENJAMBRE DOBLE PÉNDULO CAÓTICO"
    t_cell.font = Font(name=font_family, size=13, bold=True, color="00F0FF")
    t_cell.fill = hdr_fill
    t_cell.alignment = Alignment(horizontal="center", vertical="center")

    param_headers = ["Parámetro Físico", "Símbolo", "Valor", "Unidad"]
    for col_idx, h in enumerate(param_headers, 1):
        c = ws_res.cell(row=3, column=col_idx, value=h)
        c.font = subhdr_font
        c.fill = subhdr_fill
        c.alignment = Alignment(horizontal="center")
        c.border = border_thin

    params_data = [
        ("Masa Péndulo 1", "m1", params.m1, "kg"),
        ("Masa Péndulo 2", "m2", params.m2, "kg"),
        ("Longitud Barra 1", "L1", params.L1, "m"),
        ("Longitud Barra 2", "L2", params.L2, "m"),
        ("Aceleración Gravitatoria", "g", params.g, "m/s²"),
        ("Tamaño del Enjambre", "N", params.num_pendulums, "sistemas"),
        ("Ángulo Inicial Barra 1", "θ1(0)", params.theta1_0_deg, "grados"),
        ("Ángulo Inicial Barra 2", "θ2(0)", params.theta2_0_deg, "grados"),
        ("Perturbación Infinitesimal", "Δθ", params.delta_theta, "rad"),
        ("Exponente de Lyapunov Teórico", "λ", 1.42, "s⁻¹"),
        ("Tiempo Total de Simulación", "t_max", params.duration, "s"),
        ("Frecuencia de Muestreo", "FPS", params.fps, "cuadros/s"),
    ]

    for r_idx, (p_name, p_sym, p_val, p_unit) in enumerate(params_data, 4):
        ws_res.cell(row=r_idx, column=1, value=p_name).font = regular_font
        ws_res.cell(row=r_idx, column=2, value=p_sym).font = regular_font
        c_val = ws_res.cell(row=r_idx, column=3, value=p_val)
        c_val.font = accent_font
        c_val.alignment = Alignment(horizontal="right")
        if isinstance(p_val, float) and p_val < 1e-4:
            c_val.number_format = "0.00E+00"
        elif isinstance(p_val, float):
            c_val.number_format = "0.00"
        else:
            c_val.number_format = "#,##0"

        ws_res.cell(row=r_idx, column=4, value=p_unit).font = regular_font
        for col_i in range(1, 5):
            ws_res.cell(row=r_idx, column=col_i).border = border_thin

    # Métricas clave dinámicas (Con fórmulas de Excel hacia las otras hojas)
    ws_res.merge_cells("F3:H3")
    m_cell = ws_res["F3"]
    m_cell.value = "MÉTRICAS HAMILTONIANAS Y CAOS (FÓRMULAS DINÁMICAS)"
    m_cell.font = subhdr_font
    m_cell.fill = subhdr_fill
    m_cell.alignment = Alignment(horizontal="center")

    metric_headers = ["Indicador", "Fórmula Dinámica", "Valor Calculado"]
    for col_idx, h in enumerate(metric_headers, 6):
        c = ws_res.cell(row=4, column=col_idx, value=h)
        c.font = subhdr_font
        c.fill = hdr_fill
        c.alignment = Alignment(horizontal="center")
        c.border = border_thin

    dynamic_metrics = [
        ("Energía Inicial P0 (J)", "=Dinamica_P0!G2", "0.00000"),
        ("Energía Final P0 (J)", "=Dinamica_P0!G902", "0.00000"),
        ("Desviación Relativa Máxima Energía", "=MAX(Dinamica_P0!H2:H902)", "0.00E+00"),
        ("Separación Inicial del Enjambre (m)", "=Divergencia_Caos!B2", "0.00E+00"),
        ("Separación Final a 15s (m)", "=Divergencia_Caos!B902", "0.0000"),
        ("Factor de Expansión Caótica", "=Divergencia_Caos!B902/Divergencia_Caos!B2", "#,##0.0"),
    ]

    for r_idx, (m_label, m_formula, m_fmt) in enumerate(dynamic_metrics, 5):
        ws_res.cell(row=r_idx, column=6, value=m_label).font = regular_font
        ws_res.cell(row=r_idx, column=7, value=m_formula).font = regular_font
        c_res = ws_res.cell(row=r_idx, column=8, value=m_formula)
        c_res.font = accent_font
        c_res.number_format = m_fmt
        c_res.alignment = Alignment(horizontal="right")
        for col_i in range(6, 9):
            ws_res.cell(row=r_idx, column=col_i).border = border_thin

    # =========================================================================
    # HOJA 2: DINÁMICA DE ENERGÍA (PÉNDULO BASE k=0)
    # =========================================================================
    ws_p0 = wb.create_sheet(title="Dinamica_P0")
    ws_p0.views.sheetView[0].showGridLines = True

    p0_headers = [
        "Paso",
        "Tiempo_s",
        "Theta1_rad",
        "Theta2_rad",
        "Cinetica_J",
        "Potencial_J",
        "Total_Hamiltoniana_J",
        "Error_Rel_Energia",
    ]

    for col_idx, h in enumerate(p0_headers, 1):
        c = ws_p0.cell(row=1, column=col_idx, value=h)
        c.font = hdr_font
        c.fill = hdr_fill
        c.alignment = Alignment(horizontal="center")
        c.border = border_thin

    t_eval = data["t"]
    th1_0 = data["th1"][0]
    th2_0 = data["th2"][0]
    t_kin_0 = data["energy_kin"][0]
    v_pot_0 = data["energy_pot"][0]
    e_tot_0 = data["energy_total"][0]

    for i in range(len(t_eval)):
        row = i + 2
        ws_p0.cell(row=row, column=1, value=i).number_format = "#,##0"
        ws_p0.cell(row=row, column=2, value=float(t_eval[i])).number_format = "0.000"
        ws_p0.cell(row=row, column=3, value=float(th1_0[i])).number_format = "0.0000"
        ws_p0.cell(row=row, column=4, value=float(th2_0[i])).number_format = "0.0000"
        ws_p0.cell(row=row, column=5, value=float(t_kin_0[i])).number_format = "0.00000"
        ws_p0.cell(row=row, column=6, value=float(v_pot_0[i])).number_format = "0.00000"
        ws_p0.cell(row=row, column=7, value=float(e_tot_0[i])).number_format = "0.00000"

        # Fórmula dinámica estricta para la desviación relativa de energía: =ABS(G{row}-$G$2)/ABS($G$2)
        c_err = ws_p0.cell(row=row, column=8, value=f"=ABS(G{row}-$G$2)/ABS($G$2)")
        c_err.number_format = "0.00E+00"

        for col_i in range(1, 9):
            cell = ws_p0.cell(row=row, column=col_i)
            cell.font = regular_font
            cell.border = border_thin
            if i % 2 == 1:
                cell.fill = zebra_fill

    # =========================================================================
    # HOJA 3: DIVERGENCIA DE CAOS Y EXPONENTE DE LYAPUNOV
    # =========================================================================
    ws_caos = wb.create_sheet(title="Divergencia_Caos")
    ws_caos.views.sheetView[0].showGridLines = True

    caos_headers = [
        "Tiempo_s",
        "Separacion_Real_m",
        "Separacion_Teorica_Lyapunov_m",
        "Fase_Dinamica",
    ]

    for col_idx, h in enumerate(caos_headers, 1):
        c = ws_caos.cell(row=1, column=col_idx, value=h)
        c.font = hdr_font
        c.fill = hdr_fill
        c.alignment = Alignment(horizontal="center")
        c.border = border_thin

    span = data["swarm_span"]

    for i in range(len(t_eval)):
        row = i + 2
        t_sec = float(t_eval[i])
        ws_caos.cell(row=row, column=1, value=t_sec).number_format = "0.000"

        c_span = ws_caos.cell(row=row, column=2, value=float(span[i]))
        if span[i] < 1e-3:
            c_span.number_format = "0.00E+00"
        else:
            c_span.number_format = "0.0000"

        # Fórmula dinámica teórica de divergencia: |ΔX_0| * EXP(λ * t)
        c_teor = ws_caos.cell(row=row, column=3, value=f"=$B$2*EXP(1.42*A{row})")
        c_teor.number_format = "0.00E+00"

        # Fórmula dinámica de fase
        c_fase = ws_caos.cell(
            row=row,
            column=4,
            value=f'=IF(A{row}<5.5,"FASE 1: ORDEN APARENTE",IF(A{row}<7.5,"FASE 2: BIFURCACION","FASE 3: CAOS"))',
        )

        for col_i in range(1, 5):
            cell = ws_caos.cell(row=row, column=col_i)
            cell.font = regular_font
            cell.border = border_thin
            if i % 2 == 1:
                cell.fill = zebra_fill

    # Auto-ajuste de ancho de columnas para todas las hojas
    for ws in [ws_res, ws_p0, ws_caos]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = cell.value
                if val is not None:
                    max_len = max(max_len, len(str(val)))
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    wb.save(str(output_path))
    return output_path
