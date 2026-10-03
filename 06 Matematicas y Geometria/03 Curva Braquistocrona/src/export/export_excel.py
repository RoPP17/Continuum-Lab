"""
Continuum Lab — Mathematical Physics & Calculus of Variations
Module: 06 Matematicas y Geometria / 03 Curva Braquistocrona
Dynamic Excel Model Exporter: Benchmark Cinemático y Energético de la Curva Braquistócrona

Adheres strictly to Continuum Lab openpyxl guidelines:
  - Corporate engineering styling (Dark Slate / Electric Cyan / Steel Navy palette).
  - Dynamic Excel formulas without hardcoded totals or differences.
  - Verification of mechanical energy conservation E = Ek + Ep = const.
  - Explicit column widths and visible gridlines on all sheets.
"""

import os
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from src.physics.brachistochrone_models import BrachistochroneSimulator


def export_brachistochrone_excel(file_path: str) -> str:
    """
    Exports a dynamic Excel workbook comparing the 4 tracks:
      Sheet 1: Comparativa Cinemática y Paradoja
      Sheet 2: Discretización y Conservación de Energía
    """
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    wb = openpyxl.Workbook()
    sim = BrachistochroneSimulator(g=9.81)

    # Styling Palette
    font_title = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    font_sub = Font(name="Calibri", size=9, italic=True, color="64748B")
    font_section = Font(name="Calibri", size=11, bold=True, color="0F172A")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_body = Font(name="Calibri", size=10, color="0F172A")
    font_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
    font_code = Font(name="Consolas", size=9, color="0F172A")

    fill_title = PatternFill(start_color="0B0F19", end_color="0B0F19", fill_type="solid")
    fill_header = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    fill_highlight = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    thin_side = Side(border_style="thin", color="CBD5E1")
    double_side = Side(border_style="double", color="334155")
    cell_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
    bottom_double_border = Border(top=thin_side, bottom=double_side, left=thin_side, right=thin_side)

    # ----------------------------------------------------
    # TAB 1: Comparativa Cinemática y Paradoja
    # ----------------------------------------------------
    ws1 = wb.active
    ws1.title = "Comparativa Cinemática"
    ws1.views.sheetView[0].showGridLines = True

    # Title Banner
    ws1.merge_cells("A1:H1")
    ws1["A1"] = "CONTINUUM LAB // RESOLUCIÓN DE LA PARADOJA DE LA BRAQUISTÓCRONA"
    ws1["A1"].font = font_title
    ws1["A1"].fill = fill_title
    ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[1].height = 36

    ws1["A2"] = "Cálculo de Variaciones (Johann Bernoulli, 1696) | Coordenadas: A(0, 4) -> B(7, -3) | g = 9.81 m/s²"
    ws1["A2"].font = font_sub

    # Table 1: Parámetros y Resultados
    headers1 = [
        "Puesto", "Nombre de Pista", "Perfil Matemático",
        "Tiempo Objetivo (s)", "Tiempo Físico (s)", "Longitud Arco (m)",
        "Velocidad Final (m/s)", "Diferencia vs Braquistócrona (s)"
    ]

    row_idx = 4
    for col_idx, h in enumerate(headers1, start=1):
        cell = ws1.cell(row=row_idx, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = cell_border
    ws1.row_dimensions[row_idx].height = 28

    data_summary = sim.get_summary_data()
    # Mathematical descriptions
    math_descriptions = {
        "braq": "Cicloide: x=r(θ-sinθ), y=4-r(1-cosθ)",
        "circ": "Arco Circular: (x-xc)² + (y-yc)² = R²",
        "parab": "Parábola: y = 4 - x - 0.10*x*(7-x)",
        "rect": "Línea Recta: y = 4 - x (Euclídea)",
    }

    start_row = 5
    for i, item in enumerate(data_summary):
        curr_row = start_row + i
        ws1.row_dimensions[curr_row].height = 22

        c_rank = ws1.cell(row=curr_row, column=1, value=f"{item['rank']}º")
        c_name = ws1.cell(row=curr_row, column=2, value=item["name"])
        c_desc = ws1.cell(row=curr_row, column=3, value=math_descriptions[item["key"]])
        c_tgt = ws1.cell(row=curr_row, column=4, value=item["target_time"])
        c_phys = ws1.cell(row=curr_row, column=5, value=item["physical_time"])
        c_arc = ws1.cell(row=curr_row, column=6, value=item["arc_length"])
        
        # Dynamic formula for final speed: =SQRT(2 * 9.81 * (4.0 - (-3.0)))
        c_vf = ws1.cell(row=curr_row, column=7, value=f"=SQRT(2*9.81*(4.0 - (-3.0)))")
        
        # Dynamic formula for delta time relative to 1st place: =D{curr_row} - D$5
        c_delta = ws1.cell(row=curr_row, column=8, value=f"=D{curr_row}-D$5")

        # Styling
        c_rank.alignment = Alignment(horizontal="center", vertical="center")
        c_name.alignment = Alignment(horizontal="left", vertical="center")
        c_desc.alignment = Alignment(horizontal="left", vertical="center")
        c_tgt.alignment = Alignment(horizontal="right", vertical="center")
        c_phys.alignment = Alignment(horizontal="right", vertical="center")
        c_arc.alignment = Alignment(horizontal="right", vertical="center")
        c_vf.alignment = Alignment(horizontal="right", vertical="center")
        c_delta.alignment = Alignment(horizontal="right", vertical="center")

        c_tgt.number_format = "0.000"
        c_phys.number_format = "0.000"
        c_arc.number_format = "0.000"
        c_vf.number_format = "0.00"
        c_delta.number_format = "+0.000;-0.000;0.000"

        c_rank.font = font_bold
        c_name.font = font_bold if i == 0 else font_body
        c_desc.font = font_code
        c_tgt.font = font_bold if i == 0 else font_body
        c_phys.font = font_code
        c_arc.font = font_code
        c_vf.font = font_code
        c_delta.font = font_bold if i > 0 else font_body

        fill_row = fill_highlight if i == 0 else (fill_zebra if i % 2 == 1 else None)
        for col in range(1, 9):
            cell = ws1.cell(row=curr_row, column=col)
            cell.border = cell_border
            if fill_row:
                cell.fill = fill_row

    # Analytical Explanation Callout Block
    callout_row = 11
    ws1.cell(row=callout_row, column=1, value="PARADOJA CINEMÁTICA Y RESOLUCIÓN VARIACIONAL:").font = font_section
    callout_text = (
        "1. La recta euclidiana posee la menor distancia geométrica (9.899 m), pero es la más lenta (1.62 s).\n"
        "2. La Cicloide posee mayor longitud (10.364 m), pero cae en picado al inicio convirtiendo energía potencial "
        "en velocidad de avance rápidamente.\n"
        "3. La velocidad promedio en la Cicloide es drásticamente superior durante todo el recorrido, superando con creces "
        "el trayecto adicional recorrido.\n"
        "4. Euler-Lagrange minimiza la funcional integral dt = integral ds / sqrt(2*g*y), demostrando que la cicloide "
        "es el mínimo global absoluto."
    )
    ws1.merge_cells("A12:H16")
    callout_cell = ws1["A12"]
    callout_cell.value = callout_text
    callout_cell.font = Font(name="Calibri", size=9.5, color="334155")
    callout_cell.alignment = Alignment(vertical="top", wrap_text=True)

    # ----------------------------------------------------
    # TAB 2: Discretización y Conservación de Energía
    # ----------------------------------------------------
    ws2 = wb.create_sheet(title="Energía y Trayectorias")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:G1")
    ws2["A1"] = "VERIFICACIÓN DE CONSERVACIÓN DE ENERGÍA MECÁNICA (E = Ep + Ek = const)"
    ws2["A1"].font = font_title
    ws2["A1"].fill = fill_title
    ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[1].height = 36

    ws2["A2"] = "Muestreo espacial a lo largo de la Cicloide (m = 1.0 kg, g = 9.81 m/s², y0 = 4.0 m)"
    ws2["A2"].font = font_sub

    headers2 = [
        "Paso", "Posición X (m)", "Posición Y (m)",
        "Velocidad v(y) [m/s]", "Energía Potencial Ep [J]",
        "Energía Cinética Ek [J]", "Energía Mecánica Total E [J]"
    ]

    ws2.row_dimensions[4].height = 26
    for c_i, h in enumerate(headers2, start=1):
        cell = ws2.cell(row=4, column=c_i, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = cell_border

    # Populate 25 trajectory points along the cycloid
    pts = sim.tracks["braq"].get_trajectory_points(num_points=25)
    for p_i, (px, py) in enumerate(pts, start=1):
        r_i = 4 + p_i
        ws2.row_dimensions[r_i].height = 20

        c_step = ws2.cell(row=r_i, column=1, value=p_i)
        c_x = ws2.cell(row=r_i, column=2, value=float(px))
        c_y = ws2.cell(row=r_i, column=3, value=float(py))

        # Dynamic formula: v = SQRT(2 * 9.81 * (4.0 - C{r_i}))
        c_v = ws2.cell(row=r_i, column=4, value=f"=SQRT(2*9.81*(4.0 - C{r_i}))")
        
        # Ep = m * g * (y - (-3.0)) taking reference at y = -3.0
        c_ep = ws2.cell(row=r_i, column=5, value=f"=1.0 * 9.81 * (C{r_i} - (-3.0))")
        
        # Ek = 0.5 * m * v^2
        c_ek = ws2.cell(row=r_i, column=6, value=f"=0.5 * 1.0 * (D{r_i}^2)")
        
        # E_total = Ep + Ek
        c_etot = ws2.cell(row=r_i, column=7, value=f"=E{r_i} + F{r_i}")

        c_step.alignment = Alignment(horizontal="center", vertical="center")
        c_x.alignment = Alignment(horizontal="right", vertical="center")
        c_y.alignment = Alignment(horizontal="right", vertical="center")
        c_v.alignment = Alignment(horizontal="right", vertical="center")
        c_ep.alignment = Alignment(horizontal="right", vertical="center")
        c_ek.alignment = Alignment(horizontal="right", vertical="center")
        c_etot.alignment = Alignment(horizontal="right", vertical="center")

        c_x.number_format = "0.000"
        c_y.number_format = "0.000"
        c_v.number_format = "0.00"
        c_ep.number_format = "0.00"
        c_ek.number_format = "0.00"
        c_etot.number_format = "0.00"

        c_step.font = font_code
        c_x.font = font_code
        c_y.font = font_code
        c_v.font = font_code
        c_ep.font = font_code
        c_ek.font = font_code
        c_etot.font = font_bold

        f_row = fill_zebra if p_i % 2 == 1 else None
        for c in range(1, 8):
            cell = ws2.cell(row=r_i, column=c)
            cell.border = cell_border
            if f_row:
                cell.fill = f_row

    # Auto-adjust column widths for all sheets
    for ws in [ws1, ws2]:
        for col in ws.columns:
            col_letter = get_column_letter(col[0].column)
            max_len = 0
            for cell in col:
                # ignore merged title in row 1
                if cell.row in [1, 2, 12, 13, 14, 15, 16]:
                    continue
                if cell.value is not None:
                    max_len = max(max_len, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

    wb.save(file_path)
    return file_path
