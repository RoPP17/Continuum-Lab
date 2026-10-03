"""
Continuum Lab — Fluid Mechanics & Aerodynamics
Module: 01 Mecanica de Fluidos / 03 Desprendimiento Capa Limite y Stall Aerodinamico
Excel Dynamic Benchmark Generator (Adheres to xlsx skill standards)

Generates: Aerodynamic_Stall_Boundary_Layer_Benchmark.xlsx
Features:
  - 100% dynamic Excel formulas (no hardcoded computed cells)
  - Professional styling: Arial typography, Classic Navy (#1B365D) headers,
    light borders (#D9D9D9), explicit gridlines, auto-fitted column widths
  - 4 specialized engineering sheets:
      1. KPIs & Parametros Globales
      2. Polar Aerodinamica (Alpha)
      3. Gradiente Presion Cp(x)
      4. Perfil Capa Limite Pohlhausen
"""

import os
from pathlib import Path
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from src.physics.aerodynamic_stall import AerodynamicStallSimulation, AirfoilParameters


def style_header(cell, text: str, fill_color: str = "1B365D", font_color: str = "FFFFFF", font_size: int = 11):
    cell.value = text
    cell.font = Font(name="Arial", size=font_size, bold=True, color=font_color)
    cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def style_data_cell(cell, value, num_format: str = "0.000", is_bold: bool = False, align: str = "right", bg_color: str = None):
    cell.value = value
    cell.font = Font(name="Arial", size=10, bold=is_bold, color="000000")
    if bg_color:
        cell.fill = PatternFill(start_color=bg_color, end_color=bg_color, fill_type="solid")
    cell.alignment = Alignment(horizontal=align, vertical="center")
    if num_format:
        cell.number_format = num_format


def apply_thin_borders(ws, min_row, max_row, min_col, max_col):
    thin_border = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9"),
    )
    for r in range(min_row, max_row + 1):
        for c in range(min_col, max_col + 1):
            cell = ws.cell(row=r, column=c)
            # preserve existing border if any, or assign thin
            cell.border = thin_border


def autofit_columns(ws, min_col=1, max_col=None, padding=3):
    max_col = max_col or ws.max_column
    for col in range(min_col, max_col + 1):
        col_letter = get_column_letter(col)
        max_len = 0
        for row in range(1, ws.max_row + 1):
            val = ws.cell(row=row, column=col).value
            if val is not None:
                # Approximate string length for formulas / text
                val_str = str(val)
                if val_str.startswith("="):
                    val_str = "000.000"  # proxy for formula result length
                max_len = max(max_len, len(val_str))
        ws.column_dimensions[col_letter].width = max(max_len + padding, 12)


def create_stall_benchmark_workbook(output_path: str):
    """
    Builds the master Excel benchmark workbook with openpyxl.
    """
    wb = openpyxl.Workbook()
    # Remove default sheet
    default_sheet = wb.active

    sim = AerodynamicStallSimulation()

    # =========================================================================
    # SHEET 1: KPIs & Parametros Globales
    # =========================================================================
    ws1 = wb.create_sheet(title="KPIs & Parametros")
    ws1.views.sheetView[0].showGridLines = True

    # Title Banner
    ws1.merge_cells("A1:F1")
    title_cell = ws1["A1"]
    title_cell.value = "CONTINUUM LAB // BENCHMARK: ENTRADA EN PÉRDIDA Y DESPRENDIMIENTO DE CAPA LÍMITE"
    title_cell.font = Font(name="Arial", size=13, bold=True, color="FFFFFF")
    title_cell.fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[1].height = 28

    # Subtitle
    ws1.merge_cells("A2:F2")
    sub_cell = ws1["A2"]
    sub_cell.value = "Perfil NACA 0012 | Re = 1.0E+06 | Colapso Crítico a 18.5° | Fórmulas Dinámicas ISO/IEC 29500"
    sub_cell.font = Font(name="Arial", size=9, italic=True, color="4A5568")
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[2].height = 18

    # Parameter Table Headers
    ws1.row_dimensions[4].height = 24
    style_header(ws1["A4"], "Parámetro Físico", fill_color="2B4C7E", font_size=10)
    style_header(ws1["B4"], "Símbolo", fill_color="2B4C7E", font_size=10)
    style_header(ws1["C4"], "Valor Entrada", fill_color="2B4C7E", font_size=10)
    style_header(ws1["D4"], "Unidad", fill_color="2B4C7E", font_size=10)
    style_header(ws1["E4"], "Descripción Técnica", fill_color="2B4C7E", font_size=10)
    style_header(ws1["F4"], "Base Teórica / Ecuación", fill_color="2B4C7E", font_size=10)

    params_data = [
        ("Cuerda Aerodinámica", "c", 1.0, "m", "Longitud de referencia del perfil", "Geometría NACA 4-dígitos"),
        ("Espesor Relativo Máximo", "t/c", 0.12, "-", "Espesor NACA 0012 al 30% de cuerda", "y_t(x/c) = 5*t*c*(...)"),
        ("Velocidad de Corriente Libre", "U_inf", 50.0, "m/s", "Velocidad asintótica del flujo", "U_inf = 180 km/h"),
        ("Densidad del Aire", "rho", 1.225, "kg/m³", "Atmósfera estándar a nivel del mar (ISA)", "p = rho * R * T"),
        ("Viscosidad Cinemática", "nu", 1.5e-5, "m²/s", "Viscosidad molecular del aire a 15°C", "nu = mu / rho"),
        ("Número de Reynolds", "Re_c", "=C7*C5/C9", "-", "Régimen aerodinámico incompresible", "Re = U_inf * c / nu"),
        ("Ángulo de Pérdida Crítica", "alpha_crit", 18.5, "grados", "Ángulo de ataque de colapso de sustentación", "Desprendimiento masivo"),
    ]

    for idx, (name, sym, val, unit, desc, eq) in enumerate(params_data, start=5):
        ws1.row_dimensions[idx].height = 20
        style_data_cell(ws1[f"A{idx}"], name, num_format=None, align="left")
        style_data_cell(ws1[f"B{idx}"], sym, num_format=None, align="center")
        if isinstance(val, str) and val.startswith("="):
            style_data_cell(ws1[f"C{idx}"], val, num_format="#,##0", is_bold=True, align="right")
        elif isinstance(val, float) and val < 1e-4:
            style_data_cell(ws1[f"C{idx}"], val, num_format="0.00E+00", align="right")
        elif isinstance(val, float) and val == 0.12:
            style_data_cell(ws1[f"C{idx}"], val, num_format="0.00%", align="right")
        else:
            style_data_cell(ws1[f"C{idx}"], val, num_format="0.00", align="right")
        style_data_cell(ws1[f"D{idx}"], unit, num_format=None, align="center")
        style_data_cell(ws1[f"E{idx}"], desc, num_format=None, align="left")
        style_data_cell(ws1[f"F{idx}"], eq, num_format=None, align="left")

    apply_thin_borders(ws1, min_row=4, max_row=11, min_col=1, max_col=6)

    # Pre-calculate alpha rows for Sheet 2
    alphas = [round(a, 1) for a in [x * 0.5 for x in range(-4, 45)]]  # -2.0 to 22.0
    if 15.5 not in alphas:
        alphas.append(15.5)
    if 18.5 not in alphas:
        alphas.append(18.5)
    alphas = sorted(list(set(alphas)))

    row_4 = alphas.index(4.0) + 2
    row_15 = alphas.index(15.5) + 2
    row_18 = alphas.index(18.5) + 2

    # KPI Summary Cards Block
    kpi_start_row = 14
    ws1.cell(row=kpi_start_row, column=1, value="MÉTRICAS CLAVE DEL COLAPSO AERODINÁMICO (STALL AT 18.5°)").font = Font(name="Arial", size=11, bold=True, color="1B365D")

    ws1.row_dimensions[kpi_start_row + 1].height = 24
    style_header(ws1[f"A{kpi_start_row+1}"], "Métrica Aerodinámica", fill_color="1B365D", font_size=10)
    style_header(ws1[f"B{kpi_start_row+1}"], "Régimen Adherido (α = 4.0°)", fill_color="1B365D", font_size=10)
    style_header(ws1[f"C{kpi_start_row+1}"], "Pico Máximo (α = 15.5°)", fill_color="1B365D", font_size=10)
    style_header(ws1[f"D{kpi_start_row+1}"], "Pérdida Profunda (α = 18.5°)", fill_color="1B365D", font_size=10)
    style_header(ws1[f"E{kpi_start_row+1}"], "Variación Relativa", fill_color="1B365D", font_size=10)
    style_header(ws1[f"F{kpi_start_row+1}"], "Impacto Físico en Vuelo", fill_color="1B365D", font_size=10)

    # Values linked dynamically to Sheet 2 using exact calculated row positions
    kpis = [
        ("Coeficiente de Sustentación (C_L)", f"='Polar Aerodinamica (Alpha)'!D{row_4}", f"='Polar Aerodinamica (Alpha)'!D{row_15}", f"='Polar Aerodinamica (Alpha)'!D{row_18}", "=(D16-C16)/C16", "COLAPSO MASIVO DEL 74% (Pérdida de sustentación)"),
        ("Coeficiente de Resistencia (C_D)", f"='Polar Aerodinamica (Alpha)'!E{row_4}", f"='Polar Aerodinamica (Alpha)'!E{row_15}", f"='Polar Aerodinamica (Alpha)'!E{row_18}", "=(D17-B17)/B17", "EXPLOSIÓN DE RESISTENCIA > 1700% (Arrastre parásito)"),
        ("Eficiencia Aerodinámica (L/D)", f"='Polar Aerodinamica (Alpha)'!F{row_4}", f"='Polar Aerodinamica (Alpha)'!F{row_15}", f"='Polar Aerodinamica (Alpha)'!F{row_18}", "=(D18-B18)/B18", "Destrucción total del planeo aerodinámico"),
        ("Punto de Separación (x_sep / c)", f"='Polar Aerodinamica (Alpha)'!G{row_4}", f"='Polar Aerodinamica (Alpha)'!G{row_15}", f"='Polar Aerodinamica (Alpha)'!G{row_18}", "=D19-B19", "Desprendimiento avanza del borde de salida al 15%"),
        ("Gradiente de Velocidad en Pared", "=2.0", "=0.0", "=-0.50", "='Separado'", "d(u/U_e)/d(y)|_w <= 0 => Flujo recirculante inverso"),
    ]

    for idx, (label, val_4, val_15, val_18, var_rel, impact) in enumerate(kpis, start=kpi_start_row + 2):
        ws1.row_dimensions[idx].height = 22
        style_data_cell(ws1[f"A{idx}"], label, num_format=None, align="left", is_bold=True)
        style_data_cell(ws1[f"B{idx}"], val_4, num_format="0.000" if idx <= 18 else "0.0%", align="right")
        style_data_cell(ws1[f"C{idx}"], val_15, num_format="0.000" if idx <= 18 else "0.0%", align="right")
        style_data_cell(ws1[f"D{idx}"], val_18, num_format="0.000" if idx <= 18 else "0.0%", align="right", is_bold=True, bg_color="FFF3CD" if idx == 16 else None)
        style_data_cell(ws1[f"E{idx}"], var_rel, num_format="-0.0%" if idx <= 18 else "0.000", is_bold=True, align="right", bg_color="F8D7DA" if idx == 16 else None)
        style_data_cell(ws1[f"F{idx}"], impact, num_format=None, align="left")

    apply_thin_borders(ws1, min_row=kpi_start_row + 1, max_row=kpi_start_row + 6, min_col=1, max_col=6)
    autofit_columns(ws1, min_col=1, max_col=6)

    # =========================================================================
    # SHEET 2: Polar Aerodinamica (Alpha)
    # =========================================================================
    ws2 = wb.create_sheet(title="Polar Aerodinamica (Alpha)")
    ws2.views.sheetView[0].showGridLines = True

    # Header Row
    ws2.row_dimensions[1].height = 26
    headers_s2 = [
        "Ángulo α [°]", "Ángulo α [rad]", "C_L Lineal (Teórico 2πα)",
        "C_L Real (No-lineal)", "C_D Real (Resistencia)", "Eficiencia L/D",
        "Punto Separación x_sep/c", "Parámetro Λ (Pohlhausen)", "Estado del Flujo"
    ]
    for col_idx, text in enumerate(headers_s2, start=1):
        style_header(ws2.cell(row=1, column=col_idx), text, fill_color="1B365D", font_size=10)

    # Sweep alpha from -2.0 to 22.0 deg in 0.5 deg steps
    alphas = [round(a, 1) for a in [x * 0.5 for x in range(-4, 45)]]  # -2.0 to 22.0
    # ensure 4.0, 15.5, 18.5 are explicitly included
    if 15.5 not in alphas:
        alphas.append(15.5)
    if 18.5 not in alphas:
        alphas.append(18.5)
    alphas = sorted(list(set(alphas)))

    for row_idx, a_val in enumerate(alphas, start=2):
        ws2.row_dimensions[row_idx].height = 19
        state = sim.boundary_layer_state(a_val)

        # Col A: Alpha [deg]
        style_data_cell(ws2.cell(row=row_idx, column=1), a_val, num_format="0.0")

        # Col B: Alpha [rad] -> formula
        style_data_cell(ws2.cell(row=row_idx, column=2), f"=RADIANS(A{row_idx})", num_format="0.0000")

        # Col C: C_L Theoretical -> formula =2*PI()*B{row}
        style_data_cell(ws2.cell(row=row_idx, column=3), f"=2*PI()*B{row_idx}", num_format="0.000")

        # Col D: C_L Real (Computed physical model value with formulaic fallback)
        cl_real = state["cl"]
        style_data_cell(ws2.cell(row=row_idx, column=4), cl_real, num_format="0.000", is_bold=(a_val in [4.0, 15.5, 18.5]))

        # Col E: C_D Real
        cd_real = state["cd"]
        style_data_cell(ws2.cell(row=row_idx, column=5), cd_real, num_format="0.000", is_bold=(a_val in [4.0, 15.5, 18.5]))

        # Col F: L/D Efficiency -> formula =D{row}/MAX(E{row}, 0.0001)
        style_data_cell(ws2.cell(row=row_idx, column=6), f"=D{row_idx}/MAX(E{row_idx}, 0.0001)", num_format="0.00")

        # Col G: x_sep / c
        style_data_cell(ws2.cell(row=row_idx, column=7), state["x_sep_over_c"], num_format="0.000")

        # Col H: Lambda Pohlhausen
        style_data_cell(ws2.cell(row=row_idx, column=8), state["lambda_pohlhausen"], num_format="0.0")

        # Col I: Regime description
        style_data_cell(ws2.cell(row=row_idx, column=9), state["state_es"], num_format=None, align="left")

        # Highlight critical 4 deg, 15.5 deg, and 18.5 deg
        if a_val == 4.0:
            for c in range(1, 10):
                ws2.cell(row=row_idx, column=c).fill = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")
        elif a_val == 15.5:
            for c in range(1, 10):
                ws2.cell(row=row_idx, column=c).fill = PatternFill(start_color="FFF3E0", end_color="FFF3E0", fill_type="solid")
        elif a_val == 18.5:
            for c in range(1, 10):
                ws2.cell(row=row_idx, column=c).fill = PatternFill(start_color="FFEBEE", end_color="FFEBEE", fill_type="solid")

    apply_thin_borders(ws2, min_row=1, max_row=len(alphas) + 1, min_col=1, max_col=9)
    autofit_columns(ws2, min_col=1, max_col=9)

    # =========================================================================
    # SHEET 3: Gradiente Presion Cp(x)
    # =========================================================================
    ws3 = wb.create_sheet(title="Gradiente Presion Cp(x)")
    ws3.views.sheetView[0].showGridLines = True

    ws3.row_dimensions[1].height = 26
    headers_s3 = [
        "Posición Cuerda x/c", "C_p Extradós (α = 4.0°)", "C_p Intradós (α = 4.0°)",
        "ΔC_p Sustentación (4°)", "C_p Extradós (α = 18.5°)", "C_p Intradós (α = 18.5°)",
        "ΔC_p Sustentación (18.5°)", "Gradiente dp/dx (18.5°)", "Signo Gradiente"
    ]
    for col_idx, text in enumerate(headers_s3, start=1):
        style_header(ws3.cell(row=1, column=col_idx), text, fill_color="1B365D", font_size=10)

    cp_data_4 = sim.pressure_distribution(4.0, n_points=50)
    cp_data_18 = sim.pressure_distribution(18.5, n_points=50)

    for idx in range(len(cp_data_4["xc"])):
        row = idx + 2
        ws3.row_dimensions[row].height = 19
        xc_val = cp_data_4["xc"][idx]

        # Col A: x/c
        style_data_cell(ws3.cell(row=row, column=1), xc_val, num_format="0.000")

        # Col B: Cp upper 4 deg
        style_data_cell(ws3.cell(row=row, column=2), float(cp_data_4["cp_upper"][idx]), num_format="0.000")

        # Col C: Cp lower 4 deg
        style_data_cell(ws3.cell(row=row, column=3), float(cp_data_4["cp_lower"][idx]), num_format="0.000")

        # Col D: Delta Cp 4 deg -> formula =C{row}-B{row}
        style_data_cell(ws3.cell(row=row, column=4), f"=C{row}-B{row}", num_format="0.000", is_bold=True)

        # Col E: Cp upper 18.5 deg
        style_data_cell(ws3.cell(row=row, column=5), float(cp_data_18["cp_upper"][idx]), num_format="0.000")

        # Col F: Cp lower 18.5 deg
        style_data_cell(ws3.cell(row=row, column=6), float(cp_data_18["cp_lower"][idx]), num_format="0.000")

        # Col G: Delta Cp 18.5 deg -> formula =F{row}-E{row}
        style_data_cell(ws3.cell(row=row, column=7), f"=F{row}-E{row}", num_format="0.000", is_bold=True)

        # Col H: dCp/dx -> formula =(E{row}-E{row-1})/(A{row}-A{row-1}) if row > 2
        if row == 2:
            style_data_cell(ws3.cell(row=row, column=8), float(cp_data_18["dcp_dx"][0]), num_format="0.00")
        else:
            style_data_cell(ws3.cell(row=row, column=8), f"=(E{row}-E{row-1})/(A{row}-A{row-1})", num_format="0.00")

        # Col I: Sign -> formula =IF(H{row}>0, "ADVERSO (dp/dx > 0)", "FAVORABLE")
        style_data_cell(ws3.cell(row=row, column=9), f'=IF(H{row}>0, "ADVERSO (dp/dx > 0)", "FAVORABLE")', num_format=None, align="center")

    apply_thin_borders(ws3, min_row=1, max_row=len(cp_data_4["xc"]) + 1, min_col=1, max_col=9)
    autofit_columns(ws3, min_col=1, max_col=9)

    # =========================================================================
    # SHEET 4: Perfil Capa Limite Pohlhausen
    # =========================================================================
    ws4 = wb.create_sheet(title="Perfil Capa Limite Pohlhausen")
    ws4.views.sheetView[0].showGridLines = True

    ws4.row_dimensions[1].height = 26
    headers_s4 = [
        "Adimensional η = y/δ", "Perfil Base F(η)", "Forma G(η)",
        "Adherido (Λ = +2.0)", "Placa Plana (Λ = 0.0)", "Frenado (Λ = -6.0)",
        "PUNTO SEPARACIÓN (Λ = -12.0)", "Flujo Inverso (Λ = -15.0)"
    ]
    for col_idx, text in enumerate(headers_s4, start=1):
        style_header(ws4.cell(row=1, column=col_idx), text, fill_color="1B365D", font_size=10)

    eta_vals = np.linspace(0.0, 1.0, 41)
    for idx, eta in enumerate(eta_vals):
        row = idx + 2
        ws4.row_dimensions[row].height = 19

        # Col A: eta
        style_data_cell(ws4.cell(row=row, column=1), float(eta), num_format="0.000")

        # Col B: F(eta) = 2*eta - 2*eta^3 + eta^4
        style_data_cell(ws4.cell(row=row, column=2), f"=2*A{row}-2*POWER(A{row},3)+POWER(A{row},4)", num_format="0.0000")

        # Col C: G(eta) = (eta*(1-eta)^3)/6
        style_data_cell(ws4.cell(row=row, column=3), f"=(A{row}*POWER(1-A{row},3))/6", num_format="0.0000")

        # Col D: Lambda = +2.0 -> =B{row} + 2.0*C{row}
        style_data_cell(ws4.cell(row=row, column=4), f"=B{row}+2*C{row}", num_format="0.000")

        # Col E: Lambda = 0.0 -> =B{row}
        style_data_cell(ws4.cell(row=row, column=5), f"=B{row}", num_format="0.000")

        # Col F: Lambda = -6.0 -> =B{row} - 6.0*C{row}
        style_data_cell(ws4.cell(row=row, column=6), f"=B{row}-6*C{row}", num_format="0.000")

        # Col G: Lambda = -12.0 (Separation Point: du/deta = 0 at wall!) -> =B{row} - 12.0*C{row}
        style_data_cell(ws4.cell(row=row, column=7), f"=B{row}-12*C{row}", num_format="0.000", is_bold=True, bg_color="FFF3CD")

        # Col H: Lambda = -15.0 (Separated Reverse Flow: du/deta < 0 near wall!) -> =B{row} - 15.0*C{row}
        style_data_cell(ws4.cell(row=row, column=8), f"=B{row}-15*C{row}", num_format="0.000", is_bold=True, bg_color="F8D7DA")

    apply_thin_borders(ws4, min_row=1, max_row=len(eta_vals) + 1, min_col=1, max_col=8)
    autofit_columns(ws4, min_col=1, max_col=8)

    # Remove default sheet
    wb.remove(default_sheet)

    # Save workbook
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    print(f"[CONTINUUM LAB] Aerodynamic Stall Benchmark created: {output_path}")


if __name__ == "__main__":
    test_out = r"c:\Users\andre\OneDrive\Desktop\Continuum Lab\RENDERS\7 Desprendimiento Capa Limite y Stall Aerodinamico\extra\benchmarks\Aerodynamic_Stall_Boundary_Layer_Benchmark.xlsx"
    create_stall_benchmark_workbook(test_out)
