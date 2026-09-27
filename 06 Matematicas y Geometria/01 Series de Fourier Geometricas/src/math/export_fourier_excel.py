"""
Continuum Lab — Mathematical Physics & Fourier Geometry
Dynamic Excel Model Exporter for Geometric Fourier Series Analysis.
Follows strict openpyxl professional formatting guidelines:
  - Formatted numerical columns with dynamic Excel formulas (no hardcoding of totals or errors).
  - Clean corporate engineering visual hierarchy (Classic Navy / Steel Blue theme).
  - Explicit column widths, visible gridlines, formatted percentage & scientific cells.
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import os
from pathlib import Path


def export_fourier_benchmark_excel(file_path: str) -> str:
    """
    Generates a multi-tab dynamic Excel model comparing Fourier harmonic convergence
    for Circle, Star (D5), and Octagon (D8).
    """
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    wb = openpyxl.Workbook()

    # Themes & Styles
    font_title = Font(name="Calibri", size=15, bold=True, color="FFFFFF")
    font_section = Font(name="Calibri", size=11, bold=True, color="1E293B")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_body = Font(name="Calibri", size=10, color="0F172A")
    font_total = Font(name="Calibri", size=10, bold=True, color="0F172A")

    fill_title = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_total = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")

    thin_border_side = Side(border_style="thin", color="CBD5E1")
    double_border_side = Side(border_style="double", color="475569")

    cell_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    total_border = Border(top=thin_border_side, bottom=double_border_side)

    # ----------------------------------------------------
    # TAB 1: Resumen de Convergencia Espectral
    # ----------------------------------------------------
    ws1 = wb.active
    ws1.title = "Convergencia Espectral"
    ws1.views.sheetView[0].showGridLines = True

    # Title Block
    ws1.merge_cells("A1:G1")
    ws1["A1"] = "CONTINUUM LAB // ANÁLISIS DE SERIES DE FOURIER GEOMÉTRICAS"
    ws1["A1"].font = font_title
    ws1["A1"].fill = fill_title
    ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[1].height = 36

    ws1["A2"] = "Descomposición en epiciclos rotatorios y aproximación de formas canónicas 2D"
    ws1["A2"].font = Font(name="Calibri", size=10, italic=True, color="64748B")

    # Table 1: Circle
    headers = ["Figura", "Orden k", "Armónico n", "Amplitud |c_n|", "Fase [rad]", "% Energía", "Energía Acumulada"]
    row_idx = 4

    shapes_data = [
        ("CÍRCULO (SO(2))", [
            (1, 1, 1.0000, 0.0),
        ]),
        ("ESTRELLA (D5)", [
            (1, 1, 0.68695, 0.0),
            (2, -4, 0.16611, 0.0),
            (3, 6, 0.07383, 0.0),
            (4, -14, 0.01356, 0.0),
            (5, 16, 0.01038, 0.0),
            (6, -9, 0.00848, 0.0),
            (7, 11, 0.00568, 0.0),
        ]),
        ("OCTÓGONO (D8)", [
            (1, 1, 0.94964, 0.0),
            (2, -7, 0.01938, 0.0),
            (3, 9, 0.01172, 0.0),
            (4, -15, 0.00422, 0.0),
            (5, 17, 0.00329, 0.0),
            (6, -23, 0.00180, 0.0),
            (7, 25, 0.00152, 0.0),
        ])
    ]

    for shape_title, harmonics in shapes_data:
        # Section Header
        ws1.cell(row=row_idx, column=1, value=shape_title).font = font_section
        row_idx += 1

        # Table Header
        for col_idx, h_text in enumerate(headers, 1):
            cell = ws1.cell(row=row_idx, column=col_idx, value=h_text)
            cell.font = font_header
            cell.fill = fill_header
            cell.alignment = Alignment(horizontal="center" if col_idx > 1 else "left", vertical="center")
        ws1.row_dimensions[row_idx].height = 22
        start_data_row = row_idx + 1
        row_idx += 1

        # Data Rows
        for k_idx, (k, n, amp, phase) in enumerate(harmonics):
            curr_row = row_idx
            ws1.cell(row=curr_row, column=1, value=shape_title.split()[0]).font = font_body
            ws1.cell(row=curr_row, column=2, value=k).font = font_body
            ws1.cell(row=curr_row, column=3, value=n).font = font_body
            
            c_amp = ws1.cell(row=curr_row, column=4, value=amp)
            c_amp.font = font_body
            c_amp.number_format = "0.0000"

            c_phase = ws1.cell(row=curr_row, column=5, value=phase)
            c_phase.font = font_body
            c_phase.number_format = "0.000"

            # Dynamic Formulas:
            # Energy % = POWER(D{curr_row}, 2) / SUMPRODUCT(POWER(D{start}:D{end}, 2))
            end_row = start_data_row + len(harmonics) - 1
            c_pct = ws1.cell(row=curr_row, column=6)
            c_pct.value = f"=POWER(D{curr_row}, 2) / SUMPRODUCT(POWER(D${start_data_row}:D${end_row}, 2))"
            c_pct.font = font_body
            c_pct.number_format = "0.00%"

            # Cumulative Energy = SUM(F$start:Fcurr)
            c_cum = ws1.cell(row=curr_row, column=7)
            c_cum.value = f"=SUM(F${start_data_row}:F{curr_row})"
            c_cum.font = font_body
            c_cum.number_format = "0.00%"

            for c in range(1, 8):
                cell = ws1.cell(row=curr_row, column=c)
                cell.border = cell_border
                if k_idx % 2 == 1:
                    cell.fill = fill_zebra
                if c in [2, 3]:
                    cell.alignment = Alignment(horizontal="center")
                elif c in [4, 5, 6, 7]:
                    cell.alignment = Alignment(horizontal="right")

            row_idx += 1

        # Total Row
        tot_row = row_idx
        ws1.cell(row=tot_row, column=1, value="TOTAL ESPECTRAL").font = font_total
        ws1.cell(row=tot_row, column=6, value=f"=SUM(F{start_data_row}:F{tot_row-1})").font = font_total
        ws1.cell(row=tot_row, column=6).number_format = "0.00%"
        ws1.cell(row=tot_row, column=7, value=f"=MAX(G{start_data_row}:G{tot_row-1})").font = font_total
        ws1.cell(row=tot_row, column=7).number_format = "0.00%"

        for c in range(1, 8):
            cell = ws1.cell(row=tot_row, column=c)
            cell.border = total_border
            cell.fill = fill_total
            if c >= 6:
                cell.alignment = Alignment(horizontal="right")

        row_idx += 2  # spacing between shapes

    # Auto-fit columns
    for col in ws1.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws1.column_dimensions[col_letter].width = max(max_len + 4, 13)

    wb.save(file_path)
    print(f"[CONTINUUM LAB] Dynamic Excel Fourier Benchmark saved -> {file_path}")
    return file_path


if __name__ == "__main__":
    export_fourier_benchmark_excel("test_fourier.xlsx")
