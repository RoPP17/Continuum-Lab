"""
Continuum Lab — Fluid Mechanics & Nonlinear PDEs
Module: 01 Mecanica de Fluidos / 02 Singularidad Navier Stokes Blowup
Benchmark Generator: Dynamic Excel Model (.xlsx)

Follows strictly the 'xlsx' skill principles:
  - Professional typography & cohesive color hierarchy (Deep Cybernetic Slate & Cobalt)
  - Dynamic formulas without hardcoded calculations (SUM, AVERAGE, MAX, MIN, SQRT, POWER)
  - Visible gridlines explicitly enabled
  - Proper number formatting (scientific notation for asymptotic blowup, decimals for energies)
  - Auto-fitted column widths and generous row heights
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import numpy as np
from pathlib import Path


def create_singularity_benchmark_workbook(output_path: str):
    wb = openpyxl.Workbook()

    # Styling Palette
    COLOR_PRIMARY = "0F172A"       # Deep Slate 900
    COLOR_HEADER = "1E293B"        # Slate 800
    COLOR_ACCENT = "0284C7"        # Electric Sky Blue
    COLOR_ACCENT_LIGHT = "E0F2FE"  # Sky Light Fill
    COLOR_ZEBRA = "F8FAFC"         # Ultra Light Slate
    COLOR_CARD_FILL = "F1F5F9"     # Slate 100
    COLOR_BORDER = "CBD5E1"        # Slate 300
    COLOR_TEXT = "0F172A"          # Slate 900
    COLOR_MUTED = "64748B"         # Slate 500
    COLOR_HIGHLIGHT = "FEF08A"     # Soft Yellow alert

    font_title = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    font_subtitle = Font(name="Calibri", size=10, italic=True, color="94A3B8")
    font_section = Font(name="Calibri", size=12, bold=True, color=COLOR_PRIMARY)
    font_tbl_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_data = Font(name="Calibri", size=10, color=COLOR_TEXT)
    font_bold = Font(name="Calibri", size=10, bold=True, color=COLOR_TEXT)
    font_kpi_num = Font(name="Calibri", size=14, bold=True, color=COLOR_ACCENT)
    font_kpi_label = Font(name="Calibri", size=9, bold=True, color=COLOR_MUTED)

    fill_title = PatternFill(start_color=COLOR_PRIMARY, end_color=COLOR_PRIMARY, fill_type="solid")
    fill_header = PatternFill(start_color=COLOR_HEADER, end_color=COLOR_HEADER, fill_type="solid")
    fill_zebra = PatternFill(start_color=COLOR_ZEBRA, end_color=COLOR_ZEBRA, fill_type="solid")
    fill_card = PatternFill(start_color=COLOR_CARD_FILL, end_color=COLOR_CARD_FILL, fill_type="solid")
    fill_accent = PatternFill(start_color=COLOR_ACCENT_LIGHT, end_color=COLOR_ACCENT_LIGHT, fill_type="solid")

    thin_border_side = Side(border_style="thin", color=COLOR_BORDER)
    double_border_side = Side(border_style="double", color=COLOR_PRIMARY)
    thick_bottom_side = Side(border_style="medium", color=COLOR_PRIMARY)

    border_data = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    border_total = Border(top=thin_border_side, bottom=double_border_side)
    border_card = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)

    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")

    # =========================================================================
    # SHEET 1: Escalas_Singularidad
    # =========================================================================
    ws1 = wb.active
    ws1.title = "Escalas_Singularidad"
    ws1.views.sheetView[0].showGridLines = True

    # Title Block
    ws1.merge_cells("A1:K1")
    title_cell = ws1["A1"]
    title_cell.value = "CONTINUUM LAB // NAVIER-STOKES FINITE-TIME BLOWUP BENCHMARK"
    title_cell.font = font_title
    title_cell.fill = fill_title
    title_cell.alignment = align_left
    ws1.row_dimensions[1].height = 36

    ws1.merge_cells("A2:K2")
    sub_cell = ws1["A2"]
    sub_cell.value = "Anisotropic Core Contraction, Velocity Divergence & Uniform Kinetic Energy Boundedness (OpenAI Alternative C)"
    sub_cell.font = font_subtitle
    sub_cell.fill = fill_title
    sub_cell.alignment = align_left
    ws1.row_dimensions[2].height = 20

    # Model Parameters Block (A4:D7)
    ws1["A4"] = "MODEL PARAMETERS"
    ws1["A4"].font = font_section
    params_data = [
        ("Singular Time T*", 1.0, "s", "Fixed blowup horizon"),
        ("Scaling Exponent h", 0.008, "-", "0 < h < 0.01 (Paper constraint)"),
        ("Velocity Exponent A = 1/2 + h", "=0.5+B6", "-", "Radial/Azimuthal velocity divergence scale"),
        ("Axial Exponent D = 1/2 - h", "=0.5-B6", "-", "Axial coordinate contraction scale"),
    ]
    for row_idx, (label, val, unit, note) in enumerate(params_data, start=5):
        ws1[f"A{row_idx}"] = label
        ws1[f"A{row_idx}"].font = font_bold
        ws1[f"B{row_idx}"] = val
        ws1[f"B{row_idx}"].font = font_bold
        ws1[f"B{row_idx}"].alignment = align_right
        ws1[f"C{row_idx}"] = unit
        ws1[f"C{row_idx}"].font = font_data
        ws1[f"D{row_idx}"] = note
        ws1[f"D{row_idx}"].font = font_data
    ws1["B5"].number_format = "0.000"
    ws1["B6"].number_format = "0.0000"
    ws1["B7"].number_format = "0.0000"
    ws1["B8"].number_format = "0.0000"

    # KPI Summary Cards (F4:K7)
    cards = [
        ("F4:G5", "F4", "F5", "MAX VELOCITY (T -> 1)", "=MAX(G11:G31)", "0.00E+00", "Diverges to +Infinity"),
        ("H4:I5", "H4", "H5", "TOTAL ENERGY SUP_T", "=MAX(I11:I31)", "0.0000", "Uniformly Bounded!"),
        ("J4:K5", "J4", "J5", "FINAL SLENDERNESS lr/lz", "=K31", "0.00E+00", "Forms Infinite Needle")
    ]
    for merge_range, top_c, bot_c, title_text, form_text, num_fmt, note_text in cards:
        ws1[top_c] = title_text
        ws1[top_c].font = font_kpi_label
        ws1[top_c].alignment = align_center
        ws1[top_c].fill = fill_card
        ws1[bot_c] = form_text
        ws1[bot_c].font = font_kpi_num
        ws1[bot_c].alignment = align_center
        ws1[bot_c].fill = fill_card
        ws1[bot_c].number_format = num_fmt

    # Main Dynamic Table Headers
    headers_s1 = [
        ("A10", "Tiempo t [s]"),
        ("B10", "tau = T* - t [s]"),
        ("C10", "Escala q(0,tau)"),
        ("D10", "Radio lr ~ tau^1/2 [m]"),
        ("E10", "Altura lz ~ tau^D [m]"),
        ("F10", "Esbeltez lr / lz [-]"),
        ("G10", "Velocidad Max ||u|| [m/s]"),
        ("H10", "Vorticidad Max ||w|| [1/s]"),
        ("I10", "Energia Cinetica E_tot [J]"),
        ("J10", "Enstrofia Omega [1/s^2]"),
        ("K10", "Reynolds Azimutal Re_th [-]")
    ]
    ws1.row_dimensions[10].height = 28
    for pos, h_title in headers_s1:
        cell = ws1[pos]
        cell.value = h_title
        cell.font = font_tbl_header
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = border_data

    # Populate Data Rows (11 to 31) - Dynamic times approaching 1.0
    times = [
        0.000, 0.100, 0.200, 0.300, 0.400, 0.500, 0.600, 0.700, 0.800, 0.850,
        0.900, 0.930, 0.950, 0.970, 0.980, 0.990, 0.995, 0.998, 0.999, 0.9995, 0.9999
    ]

    for idx, t_val in enumerate(times, start=11):
        ws1.row_dimensions[idx].height = 20
        row_fill = fill_zebra if idx % 2 == 0 else PatternFill(fill_type=None)

        ws1[f"A{idx}"] = t_val
        ws1[f"B{idx}"] = f"=$B$5-A{idx}"
        ws1[f"C{idx}"] = f"=B{idx}"
        ws1[f"D{idx}"] = f"=SQRT(B{idx})"
        ws1[f"E{idx}"] = f"=POWER(B{idx}, $B$8)"
        ws1[f"F{idx}"] = f"=D{idx}/E{idx}"
        ws1[f"G{idx}"] = f"=1.968*POWER(B{idx}, -$B$7)"
        ws1[f"H{idx}"] = f"=6.0*POWER(B{idx}, -(1.0+$B$6))"
        ws1[f"I{idx}"] = f"=0.45*POWER(B{idx}, (0.5-3.0*$B$6))+2.50"
        ws1[f"J{idx}"] = f"=1.85*POWER(B{idx}, -(0.5+3.0*$B$6))"
        ws1[f"K{idx}"] = f"=POWER(B{idx}, -$B$6)"

        # Formats
        ws1[f"A{idx}"].number_format = "0.0000"
        ws1[f"B{idx}"].number_format = "0.00E+00"
        ws1[f"C{idx}"].number_format = "0.00E+00"
        ws1[f"D{idx}"].number_format = "0.0000"
        ws1[f"E{idx}"].number_format = "0.0000"
        ws1[f"F{idx}"].number_format = "0.0000"
        ws1[f"G{idx}"].number_format = "0.00E+00"
        ws1[f"H{idx}"].number_format = "0.00E+00"
        ws1[f"I{idx}"].number_format = "0.0000"
        ws1[f"J{idx}"].number_format = "0.00E+00"
        ws1[f"K{idx}"].number_format = "0.00"

        for col_letter in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]:
            c = ws1[f"{col_letter}{idx}"]
            c.font = font_data
            c.border = border_data
            if row_fill.fill_type:
                c.fill = row_fill
            c.alignment = align_right if col_letter != "A" else align_center

    # Total / Summary Row (32)
    ws1.row_dimensions[32].height = 22
    ws1["A32"] = "PROMEDIO / TOTAL"
    ws1["A32"].font = font_bold
    ws1["A32"].alignment = align_center
    ws1["A32"].border = border_total

    ws1["B32"] = "=AVERAGE(B11:B31)"
    ws1["B32"].number_format = "0.00E+00"
    ws1["C32"] = "=AVERAGE(C11:C31)"
    ws1["C32"].number_format = "0.00E+00"
    ws1["D32"] = "=AVERAGE(D11:D31)"
    ws1["D32"].number_format = "0.0000"
    ws1["E32"] = "=AVERAGE(E11:E31)"
    ws1["E32"].number_format = "0.0000"
    ws1["F32"] = "=AVERAGE(F11:F31)"
    ws1["F32"].number_format = "0.0000"
    ws1["G32"] = "=MAX(G11:G31)"
    ws1["G32"].number_format = "0.00E+00"
    ws1["H32"] = "=MAX(H11:H31)"
    ws1["H32"].number_format = "0.00E+00"
    ws1["I32"] = "=MAX(I11:I31)"
    ws1["I32"].number_format = "0.0000"
    ws1["J32"] = "=MAX(J11:J31)"
    ws1["J32"].number_format = "0.00E+00"
    ws1["K32"] = "=MAX(K11:K31)"
    ws1["K32"].number_format = "0.00"

    for col_letter in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]:
        c = ws1[f"{col_letter}32"]
        c.font = font_bold
        c.border = border_total

    # =========================================================================
    # SHEET 2: Perfil_Radial_Core_Annulus
    # =========================================================================
    ws2 = wb.create_sheet(title="Perfil_Radial_Core_Annulus")
    ws2.views.sheetView[0].showGridLines = True

    # Title Block
    ws2.merge_cells("A1:J1")
    t2 = ws2["A1"]
    t2.value = "CONTINUUM LAB // RADIAL PROFILE & REYNOLDS STRESS IN THE ANNULUS (t = 0.95 s)"
    t2.font = font_title
    t2.fill = fill_title
    t2.alignment = align_left
    ws2.row_dimensions[1].height = 36

    ws2.merge_cells("A2:J2")
    s2 = ws2["A2"]
    s2.value = "Inner Core Vortex (0 <= X <= Xa), Oscillatory Pulse Annulus (Xa <= X <= Xb), and Viscous Heat Exterior (X >= Xb)"
    s2.font = font_subtitle
    s2.fill = fill_title
    s2.alignment = align_left
    ws2.row_dimensions[2].height = 20

    # Headers for Sheet 2
    headers_s2 = [
        ("A5", "Radio r [m]"),
        ("B5", "Coord X = r^2/2q"),
        ("C5", "Perfil E(X, 0)"),
        ("D5", "Vel Azimutal u_theta [m/s]"),
        ("E5", "Vel Radial u_r [m/s]"),
        ("F5", "Presion p(r, 0) [Pa]"),
        ("G5", "Stress Tr_theta [Pa]"),
        ("H5", "Stress Tr_z [Pa]"),
        ("I5", "Amplitud Pulso A_wave"),
        ("J5", "Zona Hidrodinamica")
    ]
    ws2.row_dimensions[5].height = 26
    for pos, h_title in headers_s2:
        cell = ws2[pos]
        cell.value = h_title
        cell.font = font_tbl_header
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = border_data

    # Evaluated at tau = 0.05, q = 0.05, q^(-A) = 0.05^(-0.508) = 4.60
    r_samples = np.linspace(0.001, 1.20, 25)
    q_ref = 0.05
    scale_vel_ref = q_ref**(-0.508)
    scale_press_ref = q_ref**(-1.016)

    for idx, r_val in enumerate(r_samples, start=6):
        ws2.row_dimensions[idx].height = 20
        row_fill = fill_zebra if idx % 2 == 0 else PatternFill(fill_type=None)

        X_val = (r_val**2) / (2.0 * q_ref)
        if X_val < 0.5:
            zone_name = "1. Inner Core"
        elif X_val <= 2.8:
            zone_name = "2. Annulus Pulses"
        else:
            zone_name = "3. Heat Exterior"

        ws2[f"A{idx}"] = r_val
        ws2[f"B{idx}"] = f"=(A{idx}^2)/(2*0.05)"
        ws2[f"C{idx}"] = f"=3.0*SQRT(2*B{idx})*EXP(-0.85*B{idx})"
        ws2[f"D{idx}"] = f"={scale_vel_ref:.4f}*C{idx}"
        ws2[f"E{idx}"] = f"=-1.5*0.42/SQRT(0.05)*(1-EXP(-B{idx}))/SQRT(2*B{idx})"
        ws2[f"F{idx}"] = f"=-{scale_press_ref:.4f}*0.45*EXP(-1.5*B{idx})"
        ws2[f"G{idx}"] = f"=IF(AND(B{idx}>=0.5, B{idx}<=2.8), 0.35*POWER(0.05, -1.008)*EXP(-((B{idx}-1.65)/0.8)^4), 0)"
        ws2[f"H{idx}"] = f"=IF(AND(B{idx}>=0.5, B{idx}<=2.8), 0.22*POWER(0.05, -1.008)*0.05*EXP(-((B{idx}-1.65)/0.8)^4), 0)"
        ws2[f"I{idx}"] = f"=SQRT(G{idx}+ABS(H{idx}))"
        ws2[f"J{idx}"] = zone_name

        # Number formatting
        ws2[f"A{idx}"].number_format = "0.0000"
        ws2[f"B{idx}"].number_format = "0.0000"
        ws2[f"C{idx}"].number_format = "0.0000"
        ws2[f"D{idx}"].number_format = "0.000"
        ws2[f"E{idx}"].number_format = "0.000"
        ws2[f"F{idx}"].number_format = "0.000"
        ws2[f"G{idx}"].number_format = "0.000"
        ws2[f"H{idx}"].number_format = "0.000"
        ws2[f"I{idx}"].number_format = "0.000"

        for col_letter in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]:
            c = ws2[f"{col_letter}{idx}"]
            c.font = font_data
            c.border = border_data
            if row_fill.fill_type:
                c.fill = row_fill
            c.alignment = align_right if col_letter not in ["A", "J"] else align_center

    # Auto-adjust column widths for both sheets
    for ws in [ws1, ws2]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = str(cell.value or "")
                if len(val) > max_len and not cell.coordinate in ["A1", "A2"]:
                    max_len = len(val)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    # Save workbook
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    print(f"[CONTINUUM LAB] Dynamic Excel Benchmark saved to: {output_path}")


if __name__ == "__main__":
    benchmark_file = Path(__file__).resolve().parent.parent.parent.parent.parent / "RENDERS" / "5 Singularidad Navier Stokes" / "extra" / "benchmarks" / "Navier_Stokes_Singularity_Benchmark.xlsx"
    create_singularity_benchmark_workbook(str(benchmark_file))
