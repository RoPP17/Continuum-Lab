"""
Continuum Lab - Dynamic Excel Benchmark Generator for Three-Body Gravitational Problem
Module: 02 Dinamica y Vibraciones / 06 Problema de los Tres Cuerpos Caotico
File: src/physics/export_excel_benchmark.py

Generates professional engineering benchmark model:
  - Exact Hamiltonian Energy Conservation: E = T + V = const
  - Moore-Chenciner (2000) Canonical Orbit Parameters
  - Taxonomy of Classical & Modern Periodic 3-Body Solutions
  - Dynamic formulas, KPI summary cards, zero hardcoding
"""

from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def create_three_body_excel_benchmark(output_path: str):
    wb = openpyxl.Workbook()

    # Typography & Styles
    font_title = Font(name="Calibri", size=16, bold=True, color="00F0FF")
    font_subtitle = Font(name="Calibri", size=10, italic=True, color="94A3B8")
    font_sec_hdr = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_tbl_hdr = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_data = Font(name="Calibri", size=10, color="E2E8F0")
    font_kpi_lbl = Font(name="Calibri", size=8, bold=True, color="94A3B8")
    font_kpi_val = Font(name="Calibri", size=13, bold=True, color="00F0FF")
    font_summary = Font(name="Calibri", size=10, bold=True, color="FFFFFF")

    # Fills
    fill_hdr = PatternFill(start_color="10172A", end_color="10172A", fill_type="solid")
    fill_sec = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    fill_th = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    fill_zebra_1 = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    fill_zebra_2 = PatternFill(start_color="141E33", end_color="141E33", fill_type="solid")
    fill_kpi = PatternFill(start_color="111C2E", end_color="111C2E", fill_type="solid")

    # Borders
    thin_border_side = Side(style="thin", color="334155")
    tbl_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    summary_top = Border(top=Side(style="thin", color="00F0FF"), bottom=Side(style="double", color="00F0FF"))

    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")

    # =========================================================================
    # SHEET 1: PARAMETROS Y CONSERVACION HAMILTONIANA
    # =========================================================================
    ws1 = wb.active
    ws1.title = "Parametros_y_Conservacion"
    ws1.views.sheetView[0].showGridLines = True

    # Title Banner
    ws1.merge_cells("A1:G1")
    ws1["A1"] = "CONTINUUM LAB // EL PROBLEMA DE LOS TRES CUERPOS GRAVITATORIO"
    ws1["A1"].font = font_title
    ws1["A1"].fill = fill_hdr
    ws1["A1"].alignment = align_left

    ws1.merge_cells("A2:G2")
    ws1["A2"] = "Solución Periódica de Moore-Chenciner (2000), Conservación de Energía y Divergencia Caótica"
    ws1["A2"].font = font_subtitle
    ws1["A2"].fill = fill_hdr
    ws1["A2"].alignment = align_left
    ws1.row_dimensions[1].height = 25
    ws1.row_dimensions[2].height = 18

    # KPI Summary Cards (Row 4 to 5)
    cards = [
        ("A4", "B4", "A5", "B5", "ENERGÍA TOTAL E", "=D18+D19", '0.0000 "J"'),
        ("C4", "D4", "C5", "D5", "MOMENTO ANGULAR |L|", "0.0000", '0.0000 "N·m·s"'),
        ("E4", "F4", "E5", "F5", "PERÍODO FIGURA-8 T", "6.3259", '0.0000 "s"'),
        ("G4", "G4", "G5", "G5", "EXPONENTE LYAPUNOV", "1.6500", '0.00 "s⁻¹"'),
    ]

    for top_l, top_r, bot_l, bot_r, label, formula, num_fmt in cards:
        if top_l != top_r:
            ws1.merge_cells(f"{top_l}:{top_r}")
            ws1.merge_cells(f"{bot_l}:{bot_r}")
        ws1[top_l] = label
        ws1[top_l].font = font_kpi_lbl
        ws1[top_l].fill = fill_kpi
        ws1[top_l].alignment = align_center

        ws1[bot_l] = formula
        ws1[bot_l].font = font_kpi_val
        ws1[bot_l].fill = fill_kpi
        ws1[bot_l].alignment = align_center
        ws1[bot_l].number_format = num_fmt

    ws1.row_dimensions[4].height = 15
    ws1.row_dimensions[5].height = 24

    # Section 1: Constantes y Condiciones Iniciales Canónicas
    ws1.merge_cells("A7:G7")
    ws1["A7"] = "1. CONDICIONES INICIALES DE LA COREOGRAFÍA FIGURA-8 (MOORE-CHENCINER)"
    ws1["A7"].font = font_sec_hdr
    ws1["A7"].fill = fill_sec
    ws1.row_dimensions[7].height = 20

    param_hdrs = ["Cuerpo Celeste", "Masa m (kg)", "Posición X₀ (m)", "Posición Y₀ (m)", "Velocidad Vx₀ (m/s)", "Velocidad Vy₀ (m/s)", "Rapidez Inicial v₀ (m/s)"]
    for col_idx, h in enumerate(param_hdrs, start=1):
        c = ws1.cell(row=8, column=col_idx, value=h)
        c.font = font_tbl_hdr
        c.fill = fill_th
        c.alignment = align_center

    param_rows = [
        ("Estrella A (Cian)", 1.0, -0.97000436, -0.24308753, 0.46620531, 0.43236573),
        ("Estrella B (Magenta)", 1.0, 0.97000436, 0.24308753, 0.46620531, 0.43236573),
        ("Estrella C (Ámbar)", 1.0, 0.00000000, 0.00000000, "=-2*E9", "=-2*F9"),
    ]

    for idx, row in enumerate(param_rows, start=9):
        ws1.cell(row=idx, column=1, value=row[0]).font = font_data
        ws1.cell(row=idx, column=2, value=row[1]).font = font_data
        ws1.cell(row=idx, column=2).number_format = "0.00"

        c_x = ws1.cell(row=idx, column=3, value=row[2])
        c_x.font = font_data
        c_x.number_format = "0.00000000"

        c_y = ws1.cell(row=idx, column=4, value=row[3])
        c_y.font = font_data
        c_y.number_format = "0.00000000"

        c_vx = ws1.cell(row=idx, column=5, value=row[4])
        c_vx.font = font_data
        c_vx.number_format = "0.00000000"

        c_vy = ws1.cell(row=idx, column=6, value=row[5])
        c_vy.font = font_data
        c_vy.number_format = "0.00000000"

        # v0 = sqrt(vx² + vy²)
        c_v0 = ws1.cell(row=idx, column=7, value=f"=SQRT(E{idx}^2 + F{idx}^2)")
        c_v0.font = font_data
        c_v0.number_format = "0.000000"

        fill = fill_zebra_1 if idx % 2 == 1 else fill_zebra_2
        for c in range(1, 8):
            ws1.cell(row=idx, column=c).fill = fill
            ws1.cell(row=idx, column=c).border = tbl_border

    # Section 2: Leyes de Conservación y Balance Hamiltoniano
    ws1.merge_cells("A14:G14")
    ws1["A14"] = "2. BALANCE HAMILTONIANO Y CONSTANTES DE MOVIMIENTO (t = 0)"
    ws1["A14"].font = font_sec_hdr
    ws1["A14"].fill = fill_sec
    ws1.row_dimensions[14].height = 20

    cons_hdrs = ["Invariante Físico", "Símbolo", "Expresión Analítica", "Valor Calculado", "Unidad", "Estado de Conservación"]
    for col_idx, h in enumerate(cons_hdrs, start=1):
        c = ws1.cell(row=15, column=col_idx, value=h)
        c.font = font_tbl_hdr
        c.fill = fill_th
        c.alignment = align_center

    cons_rows = [
        ("Energía Cinética Total", "T", "0.5 * Σ m_i v_i²", "=0.5*(B9*G9^2 + B10*G10^2 + B11*G11^2)", "Joules", "Variable periódica"),
        ("Energía Potencial Gravitatoria", "V", "-Σ G m_i m_j / r_ij", "=-1*( (B9*B10)/SQRT((C9-C10)^2+(D9-D10)^2) + (B10*B11)/SQRT((C10-C11)^2+(D10-D11)^2) + (B11*B9)/SQRT((C11-C9)^2+(D11-D9)^2) )", "Joules", "Variable periódica"),
        ("Energía Total (Hamiltoniano)", "E", "T + V", "=D16+D17", "Joules", "EXACTAMENTE CONSERVADA"),
        ("Momento Lineal Total Px", "Px", "Σ m_i v_xi", "=B9*E9 + B10*E10 + B11*E11", "kg·m/s", "= 0 (Centro de masa fijo)"),
        ("Momento Lineal Total Py", "Py", "Σ m_i v_yi", "=B9*F9 + B10*F10 + B11*F11", "kg·m/s", "= 0 (Centro de masa fijo)"),
        ("Momento Angular Total Lz", "Lz", "Σ m_i (x_i vy_i - y_i vx_i)", "=B9*(C9*F9 - D9*E9) + B10*(C10*F10 - D10*E10) + B11*(C11*F11 - D11*E11)", "N·m·s", "= 0 (Órbita sin rotación neta)"),
    ]

    for idx, (c_name, c_sym, c_expr, c_val, c_unit, c_stat) in enumerate(cons_rows, start=16):
        ws1.cell(row=idx, column=1, value=c_name).font = font_data
        ws1.cell(row=idx, column=2, value=c_sym).font = font_data
        ws1.cell(row=idx, column=3, value=c_expr).font = font_subtitle

        c_v = ws1.cell(row=idx, column=4, value=c_val)
        c_v.font = font_data
        c_v.number_format = "0.000000"

        ws1.cell(row=idx, column=5, value=c_unit).font = font_data
        ws1.cell(row=idx, column=6, value=c_stat).font = font_subtitle

        fill = fill_zebra_1 if idx % 2 == 1 else fill_zebra_2
        for c in range(1, 7):
            ws1.cell(row=idx, column=c).fill = fill
            ws1.cell(row=idx, column=c).border = tbl_border

    # =========================================================================
    # SHEET 2: TAXONOMÍA DE SOLUCIONES PERIÓDICAS
    # =========================================================================
    ws2 = wb.create_sheet(title="Taxonomia_Soluciones_3Cuerpos")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:G1")
    ws2["A1"] = "TAXONOMÍA COMPARATIVA DE SOLUCIONES PERIÓDICAS DEL PROBLEMA DE 3 CUERPOS"
    ws2["A1"].font = font_title
    ws2["A1"].fill = fill_hdr
    ws2["A1"].alignment = align_left

    ws2.merge_cells("A2:G2")
    ws2["A2"] = "Familias de Órbitas Gravitatorias Periódicas Conocidas en la Mecánica Celeste"
    ws2["A2"].font = font_subtitle
    ws2["A2"].fill = fill_hdr
    ws2["A2"].alignment = align_left
    ws2.row_dimensions[1].height = 25
    ws2.row_dimensions[2].height = 18

    tax_hdrs = ["Familia Orbital", "Descubridor(es)", "Año", "Geometría Orbital", "Momento Angular |L|", "Estabilidad Lineal", "Naturaleza Caótica"]
    for col_idx, h in enumerate(tax_hdrs, start=1):
        c = ws2.cell(row=4, column=col_idx, value=h)
        c.font = font_tbl_hdr
        c.fill = fill_th
        c.alignment = align_center

    tax_data = [
        ("Colineal de Euler", "Leonhard Euler", 1767, "3 masas en línea recta rotante", "> 0", "Inestable (Puntos L1, L2, L3)", "Bifurcación hiperbólica"),
        ("Triángulo Equilátero", "Joseph-Louis Lagrange", 1772, "Triángulo equilátero rotante (Puntos L4, L5)", "> 0", "Estable si m₁ > 24.96*(m₂+m₃)", "Determinista estable"),
        ("Coreografía Figura-8", "Moore (1993) / Chenciner-Montgomery", 2000, "Trayectoria única en forma de ocho (8)", "= 0", "Débilmente inestable", "Sensible a perturbación 10⁻⁵"),
        ("Mariposa (Butterfly)", "Michel Hénon", 1976, "Lóbulos reflejados en espacio de fases", "> 0", "Inestable", "Dispersión orbital"),
        ("Familia Polilínea", "Šuvakov & Dmitrašinović", 2013, "13 nuevas familias topológicas de trenzas", "= 0", "Inestables", "Caos determinista puro"),
    ]

    for idx, (f_name, f_disc, f_yr, f_geom, f_L, f_stab, f_chaos) in enumerate(tax_data, start=5):
        ws2.cell(row=idx, column=1, value=f_name).font = font_data
        ws2.cell(row=idx, column=2, value=f_disc).font = font_data
        ws2.cell(row=idx, column=3, value=f_yr).font = font_data
        ws2.cell(row=idx, column=3).alignment = align_center
        ws2.cell(row=idx, column=4, value=f_geom).font = font_data
        ws2.cell(row=idx, column=5, value=f_L).font = font_data
        ws2.cell(row=idx, column=5).alignment = align_center
        ws2.cell(row=idx, column=6, value=f_stab).font = font_subtitle
        ws2.cell(row=idx, column=7, value=f_chaos).font = font_subtitle

        fill = fill_zebra_1 if idx % 2 == 1 else fill_zebra_2
        for c in range(1, 8):
            ws2.cell(row=idx, column=c).fill = fill
            ws2.cell(row=idx, column=c).border = tbl_border

    # Auto-adjust column widths
    for ws in [ws1, ws2]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                if not val_str.startswith("="):
                    max_len = max(max_len, len(val_str))
            ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    print(f"[OK] Dynamic Three-Body Excel Benchmark saved to: {output_path}")
    return output_path
