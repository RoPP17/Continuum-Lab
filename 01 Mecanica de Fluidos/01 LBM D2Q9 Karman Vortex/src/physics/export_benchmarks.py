"""
Continuum Lab — Hydrodynamic Benchmark & Engineering Excel Model
Generates dynamic Excel model (.xlsx) using openpyxl with zero hardcoded formulas.
Division: Computational Fluid Dynamics & Quantitative Benchmarks
"""

import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def export_lbm_benchmark_excel(
    file_path: str,
    time_series: list[dict],
    reynolds: float,
    mach: float,
    diameter: float,
    nu: float
) -> str:
    """
    Exports simulation time-series and dynamic hydrodynamic force analysis into an Excel model.
    Enforces native Excel formulas for all statistical, dimensionless, and error metrics.
    """
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    wb = Workbook()

    # ----------------------------------------------------
    # Styles & Palette (Cybernetic Laboratory Theme)
    # ----------------------------------------------------
    header_fill = PatternFill(start_color="0D1117", end_color="0D1117", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="00F0FF")
    title_font = Font(name="Segoe UI", size=14, bold=True, color="00F0FF")
    sub_font = Font(name="Segoe UI", size=10, italic=True, color="8B949E")
    bold_font = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    regular_font = Font(name="Segoe UI", size=10, color="E6EDF3")
    accent_fill = PatternFill(start_color="161B22", end_color="161B22", fill_type="solid")
    card_fill = PatternFill(start_color="1F242C", end_color="1F242C", fill_type="solid")

    thin_border = Border(
        left=Side(style="thin", color="30363D"),
        right=Side(style="thin", color="30363D"),
        top=Side(style="thin", color="30363D"),
        bottom=Side(style="thin", color="30363D")
    )

    # ----------------------------------------------------
    # Sheet 1: Raw Telemetry Data
    # ----------------------------------------------------
    ws_data = wb.active
    ws_data.title = "Telemetry_Data"
    ws_data.views.sheetView[0].showGridLines = True

    # Header Row
    headers = ["Step", "Time_sec", "Drag_Coeff_Cd", "Lift_Coeff_Cl", "Abs_Lift_AbsCl"]
    for col_idx, h_text in enumerate(headers, 1):
        cell = ws_data.cell(row=1, column=col_idx, value=h_text)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    # Data Rows
    row_count = len(time_series)
    for r_idx, item in enumerate(time_series, 2):
        ws_data.cell(row=r_idx, column=1, value=item["step"]).number_format = "#,##0"
        ws_data.cell(row=r_idx, column=2, value=item["time"]).number_format = "0.0000"
        ws_data.cell(row=r_idx, column=3, value=item["cd"]).number_format = "0.0000"
        ws_data.cell(row=r_idx, column=4, value=item["cl"]).number_format = "+0.0000;-0.0000;0.0000"
        # Dynamic formula for Abs_Lift
        ws_data.cell(row=r_idx, column=5, value=f"=ABS(D{r_idx})").number_format = "0.0000"

        for col_idx in range(1, 6):
            c = ws_data.cell(row=r_idx, column=col_idx)
            c.font = regular_font
            c.border = thin_border
            if r_idx % 2 == 0:
                c.fill = accent_fill

    # ----------------------------------------------------
    # Sheet 2: Hydrodynamic Analysis & Engineering Model
    # ----------------------------------------------------
    ws_analysis = wb.create_sheet(title="Hydrodynamic_Analysis")
    ws_analysis.views.sheetView[0].showGridLines = True

    # Title Banner
    ws_analysis["A1"] = "CONTINUUM LAB // HYDRODYNAMIC FORCE ANALYSIS"
    ws_analysis["A1"].font = title_font
    ws_analysis["A2"] = "Lattice Boltzmann D2Q9 Vortex Shedding Benchmark (Continuum Lab Architecture)"
    ws_analysis["A2"].font = sub_font

    # Section 1: Flow Parameters
    ws_analysis["A4"] = "FLOW & GRID PARAMETERS"
    ws_analysis["A4"].font = bold_font
    ws_analysis["A4"].fill = header_fill

    params = [
        ("Reynolds Number (Re)", reynolds, "0.0"),
        ("Mach Number (Ma)", mach, "0.000"),
        ("Obstacle Diameter (D) [nodes]", diameter, "0.0"),
        ("Kinematic Viscosity (nu) [lattice]", nu, "0.00000"),
        ("Total Recorded Steps", f"=COUNT(Telemetry_Data!A2:A{row_count + 1})", "#,##0"),
    ]

    for idx, (lbl, val, fmt) in enumerate(params, 5):
        ws_analysis[f"A{idx}"] = lbl
        ws_analysis[f"A{idx}"].font = regular_font
        ws_analysis[f"A{idx}"].border = thin_border

        cell_b = ws_analysis[f"B{idx}"]
        cell_b.value = val
        cell_b.font = bold_font
        cell_b.number_format = fmt
        cell_b.border = thin_border
        cell_b.alignment = Alignment(horizontal="right")

    # Section 2: Hydrodynamic Force Coefficients (Dynamic Formulas)
    ws_analysis["A11"] = "CALCULATED HYDRODYNAMIC METRICS"
    ws_analysis["A11"].font = bold_font
    ws_analysis["A11"].fill = header_fill

    metrics = [
        ("Mean Drag Coefficient (Cd_bar)", f"=AVERAGE(Telemetry_Data!C2:C{row_count + 1})", "0.0000"),
        ("Peak Drag Coefficient (Cd_max)", f"=MAX(Telemetry_Data!C2:C{row_count + 1})", "0.0000"),
        ("Minimum Drag Coefficient (Cd_min)", f"=MIN(Telemetry_Data!C2:C{row_count + 1})", "0.0000"),
        ("Drag Fluctuation Amplitude (Delta_Cd)", "=B13-B14", "0.0000"),
        ("Peak Lift Coefficient (Cl_max)", f"=MAX(Telemetry_Data!D2:D{row_count + 1})", "0.0000"),
        ("RMS Lift Coefficient (Cl_rms)", f"=SQRT(SUMSQ(Telemetry_Data!D2:D{row_count + 1})/COUNT(Telemetry_Data!D2:D{row_count + 1}))", "0.0000"),
        ("Empirical Circular Cylinder Cd (Henderson)", "=1.0 + 10.0/(B5^0.66)", "0.0000"),
        ("Relative Discrepancy vs Empirical", "=ABS(B12-B18)/B18", "0.00%"),
    ]

    for idx, (lbl, formula_str, fmt) in enumerate(metrics, 12):
        ws_analysis[f"A{idx}"] = lbl
        ws_analysis[f"A{idx}"].font = regular_font
        ws_analysis[f"A{idx}"].border = thin_border

        cell_b = ws_analysis[f"B{idx}"]
        cell_b.value = formula_str
        cell_b.font = bold_font
        cell_b.number_format = fmt
        cell_b.border = thin_border
        cell_b.alignment = Alignment(horizontal="right")
        cell_b.fill = card_fill

    # Auto-fit column widths
    for sheet in [ws_data, ws_analysis]:
        for col in sheet.columns:
            max_len = max(len(str(c.value or "")) for c in col)
            col_letter = get_column_letter(col[0].column)
            sheet.column_dimensions[col_letter].width = max(max_len + 4, 16)

    wb.save(file_path)
    return file_path
