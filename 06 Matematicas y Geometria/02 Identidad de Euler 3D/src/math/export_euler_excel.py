"""
Continuum Lab — Mathematical Physics & Complex Geometry
Dynamic Excel Model Exporter for Euler's Identity 3D Helix and Canonical Projections.

Follows strict professional openpyxl and Continuum Lab standards:
  - Dynamic Excel formulas throughout (COS, SIN, SQRT, ATAN2, AVERAGE, MAX, MIN, SUM).
  - No hardcoded calculation values.
  - Classic Navy / Steel Blue theme, clear visual hierarchy, explicit column widths, visible gridlines.
  - Multi-tab structure: Trajectory Coordinates & Projections, Landmark Identity Points, Taylor Convergence.
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import os
import math
import numpy as np


def export_euler_benchmark_excel(file_path: str) -> str:
    """
    Generates a dynamic multi-tab Excel model verifying Euler's Formula:
      e^{i theta} = cos(theta) + i sin(theta)
    with 3D coordinates, orthogonal 2D projections, dynamic formulas, and geometric benchmarks.
    """
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    wb = openpyxl.Workbook()

    # Style definitions
    font_title = Font(name="Calibri", size=15, bold=True, color="FFFFFF")
    font_section = Font(name="Calibri", size=11, bold=True, color="1E293B")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_body = Font(name="Calibri", size=10, color="0F172A")
    font_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
    font_kpi_num = Font(name="Calibri", size=13, bold=True, color="1E3A8A")
    font_kpi_label = Font(name="Calibri", size=9, bold=False, color="64748B")

    fill_title = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_total = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
    fill_kpi = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    fill_highlight = PatternFill(start_color="FEF08A", end_color="FEF08A", fill_type="solid")

    thin_border_side = Side(border_style="thin", color="CBD5E1")
    double_border_side = Side(border_style="double", color="475569")
    cell_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    total_border = Border(top=thin_border_side, bottom=double_border_side, left=thin_border_side, right=thin_border_side)

    # ----------------------------------------------------
    # TAB 1: Espiral 3D y Proyecciones Canónicas
    # ----------------------------------------------------
    ws1 = wb.active
    ws1.title = "Espiral 3D y Proyecciones"
    ws1.views.sheetView[0].showGridLines = True

    # Title Block
    ws1.merge_cells("A1:J1")
    ws1["A1"] = "CONTINUUM LAB // IDENTIDAD DE EULER EN EL ESPACIO 3D Y PROYECCIONES CANÓNICAS"
    ws1["A1"].font = font_title
    ws1["A1"].fill = fill_title
    ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[1].height = 36

    ws1["A2"] = "Eje X: Ángulo theta | Eje Y: Parte Real cos(theta) | Eje Z: Parte Imaginaria sin(theta) | Proyecciones XY (Coseno) y XZ (Seno)"
    ws1["A2"].font = Font(name="Calibri", size=10, italic=True, color="64748B")

    # KPI summary cards
    kpis = [
        ("B4:C4", "B5:C5", "MODULUS TEÓRICO |z|", "=AVERAGE(G8:G72)", "0.0000"),
        ("E4:F4", "E5:F5", "ERROR MÁXIMO UNITARIO", "=MAX(H8:H72)", "0.000000"),
        ("H4:I4", "H5:I5", "TASA DE TRAYECTORIA TOTAL", "=MAX(B8:B72)", "0.00 rad"),
    ]
    for m_label, m_val, label_text, formula, num_fmt in kpis:
        ws1.merge_cells(m_label)
        ws1.merge_cells(m_val)
        top_left_label = m_label.split(":")[0]
        top_left_val = m_val.split(":")[0]

        ws1[top_left_label] = label_text
        ws1[top_left_label].font = font_kpi_label
        ws1[top_left_label].fill = fill_kpi
        ws1[top_left_label].alignment = Alignment(horizontal="center", vertical="center")

        ws1[top_left_val] = formula
        ws1[top_left_val].font = font_kpi_num
        ws1[top_left_val].fill = fill_kpi
        ws1[top_left_val].alignment = Alignment(horizontal="center", vertical="center")
        ws1[top_left_val].number_format = num_fmt

    # Table 1: Discretized 3D Helix Points
    headers1 = [
        "Paso k",
        "Ángulo theta [rad]",
        "Ángulo [deg]",
        "Eje X (theta)",
        "Eje Y Re(z) = cos(theta)",
        "Eje Z Im(z) = sin(theta)",
        "Módulo |z| = sqrt(Y^2+Z^2)",
        "Desviación ||z|-1|",
        "Proy XY (t, cos, 0)",
        "Proy XZ (t, 0, sin)"
    ]

    header_row = 7
    ws1.row_dimensions[header_row].height = 24
    for col_idx, h_text in enumerate(headers1, start=1):
        cell = ws1.cell(row=header_row, column=col_idx, value=h_text)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = cell_border

    # Populate 64 discretized points from 0 to 4*pi (step pi/16)
    num_steps = 64
    d_theta = (4.0 * math.pi) / num_steps

    for i in range(num_steps + 1):
        r = header_row + 1 + i
        t_val = round(i * d_theta, 6)
        ws1.row_dimensions[r].height = 19
        zebra = fill_zebra if (i % 2 == 1) else None

        # Step k
        c_k = ws1.cell(row=r, column=1, value=i)
        c_k.alignment = Alignment(horizontal="center")

        # Theta [rad] - input value
        c_th = ws1.cell(row=r, column=2, value=t_val)
        c_th.number_format = "0.0000"
        c_th.alignment = Alignment(horizontal="right")

        # Theta [deg] = DEGREES(B{r})
        c_deg = ws1.cell(row=r, column=3, value=f"=DEGREES(B{r})")
        c_deg.number_format = "0.00"
        c_deg.alignment = Alignment(horizontal="right")

        # X = B{r}
        c_x = ws1.cell(row=r, column=4, value=f"=B{r}")
        c_x.number_format = "0.0000"
        c_x.alignment = Alignment(horizontal="right")

        # Y = COS(B{r})
        c_y = ws1.cell(row=r, column=5, value=f"=COS(B{r})")
        c_y.number_format = "0.00000"
        c_y.alignment = Alignment(horizontal="right")

        # Z = SIN(B{r})
        c_z = ws1.cell(row=r, column=6, value=f"=SIN(B{r})")
        c_z.number_format = "0.00000"
        c_z.alignment = Alignment(horizontal="right")

        # Modulus = SQRT(E{r}^2 + F{r}^2)
        c_mod = ws1.cell(row=r, column=7, value=f"=SQRT(E{r}^2+F{r}^2)")
        c_mod.number_format = "0.000000"
        c_mod.alignment = Alignment(horizontal="right")

        # Deviation = ABS(G{r} - 1)
        c_err = ws1.cell(row=r, column=8, value=f"=ABS(G{r}-1)")
        c_err.number_format = "0.000000"
        c_err.alignment = Alignment(horizontal="right")

        # Proy XY = E{r} (Cosine component on XY floor)
        c_pxy = ws1.cell(row=r, column=9, value=f"=E{r}")
        c_pxy.number_format = "0.00000"
        c_pxy.alignment = Alignment(horizontal="right")

        # Proy XZ = F{r} (Sine component on XZ wall)
        c_pxz = ws1.cell(row=r, column=10, value=f"=F{r}")
        c_pxz.number_format = "0.00000"
        c_pxz.alignment = Alignment(horizontal="right")

        for col_idx in range(1, 11):
            cell = ws1.cell(row=r, column=col_idx)
            cell.font = font_body
            cell.border = cell_border
            if zebra:
                cell.fill = zebra

    # Summary Row
    summary_r = header_row + num_steps + 2
    ws1.row_dimensions[summary_r].height = 22
    ws1.cell(row=summary_r, column=1, value="PROMEDIO").font = font_bold
    ws1.cell(row=summary_r, column=1).alignment = Alignment(horizontal="center")
    ws1.cell(row=summary_r, column=1).fill = fill_total

    for c_idx in range(2, 11):
        c_let = get_column_letter(c_idx)
        cell = ws1.cell(row=summary_r, column=c_idx, value=f"=AVERAGE({c_let}8:{c_let}{summary_r-1})")
        cell.font = font_bold
        cell.fill = fill_total
        cell.border = total_border
        cell.alignment = Alignment(horizontal="right")
        cell.number_format = "0.0000"

    # Auto-adjust column widths
    for col in ws1.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(cell.value or "")) for cell in col)
        ws1.column_dimensions[col_letter].width = max(max_len + 4, 13)

    # ----------------------------------------------------
    # TAB 2: Identidad de Euler y Puntos Notables
    # ----------------------------------------------------
    ws2 = wb.create_sheet(title="Identidad y Puntos Notables")
    ws2.views.sheetView[0].showGridLines = True

    # Title Block
    ws2.merge_cells("A1:H1")
    ws2["A1"] = "CONTINUUM LAB // HITOS CARDINALES DE LA FÓRMULA E IDENTIDAD DE EULER"
    ws2["A1"].font = font_title
    ws2["A1"].fill = fill_title
    ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[1].height = 36

    ws2["A2"] = "Evaluación exacta en múltiplos de pi/4: Demostración de e^{i pi} + 1 = 0"
    ws2["A2"].font = Font(name="Calibri", size=10, italic=True, color="64748B")

    headers2 = [
        "Hito",
        "Ángulo theta",
        "Valor Numérico [rad]",
        "Re(z) = cos(theta)",
        "Im(z) = sin(theta)",
        "Forma Compleja z = x + iy",
        "Identidad e^{i theta} + 1",
        "Significado Geométrico / Físico"
    ]

    h_row2 = 4
    ws2.row_dimensions[h_row2].height = 24
    for col_idx, h_text in enumerate(headers2, start=1):
        cell = ws2.cell(row=h_row2, column=col_idx, value=h_text)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = cell_border

    notable_points = [
        ("P0", "0", 0.0, "Inicio en el eje Real positivo"),
        ("P1", "pi / 4", round(0.25 * math.pi, 6), "Bisectriz primer cuadrante (cos = sin = 1/sqrt(2))"),
        ("P2", "pi / 2", round(0.5 * math.pi, 6), "Unidad Imaginaria pura +i"),
        ("P3", "3*pi / 4", round(0.75 * math.pi, 6), "Bisectriz segundo cuadrante"),
        ("P4 [EULER]", "pi", round(math.pi, 6), "IDENTIDAD DE EULER: e^{i pi} = -1 ==> e^{i pi} + 1 = 0"),
        ("P5", "5*pi / 4", round(1.25 * math.pi, 6), "Bisectriz tercer cuadrante"),
        ("P6", "3*pi / 2", round(1.5 * math.pi, 6), "Unidad Imaginaria pura negativa -i"),
        ("P7", "7*pi / 4", round(1.75 * math.pi, 6), "Bisectriz cuarto cuadrante"),
        ("P8 [PERIODO]", "2*pi", round(2.0 * math.pi, 6), "Ciclo cerrado completo: e^{i 2 pi} = 1"),
    ]

    for idx, (label, th_str, th_val, desc) in enumerate(notable_points):
        r = h_row2 + 1 + idx
        ws2.row_dimensions[r].height = 22
        is_euler = ("EULER" in label)

        c_lbl = ws2.cell(row=r, column=1, value=label)
        c_lbl.alignment = Alignment(horizontal="center")

        c_str = ws2.cell(row=r, column=2, value=th_str)
        c_str.alignment = Alignment(horizontal="center")

        c_val = ws2.cell(row=r, column=3, value=th_val)
        c_val.number_format = "0.00000"
        c_val.alignment = Alignment(horizontal="right")

        c_re = ws2.cell(row=r, column=4, value=f"=COS(C{r})")
        c_re.number_format = "0.00000"
        c_re.alignment = Alignment(horizontal="right")

        c_im = ws2.cell(row=r, column=5, value=f"=SIN(C{r})")
        c_im.number_format = "0.00000"
        c_im.alignment = Alignment(horizontal="right")

        # Complex form formatted as string formula
        c_comp = ws2.cell(row=r, column=6, value=f'=TEXT(D{r}, "0.000") & " + " & TEXT(E{r}, "0.000") & " i"')
        c_comp.alignment = Alignment(horizontal="center")

        # Euler identity residual: |z + 1| = SQRT((D{r}+1)^2 + E{r}^2)
        c_res = ws2.cell(row=r, column=7, value=f"=SQRT((D{r}+1)^2 + E{r}^2)")
        c_res.number_format = "0.000000"
        c_res.alignment = Alignment(horizontal="right")

        c_desc = ws2.cell(row=r, column=8, value=desc)
        c_desc.alignment = Alignment(horizontal="left")

        for col_idx in range(1, 9):
            cell = ws2.cell(row=r, column=col_idx)
            cell.font = font_bold if is_euler else font_body
            cell.border = cell_border
            if is_euler:
                cell.fill = fill_highlight

    for col in ws2.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(cell.value or "")) for cell in col)
        ws2.column_dimensions[col_letter].width = max(max_len + 4, 15)

    # ----------------------------------------------------
    # TAB 3: Serie de Taylor y Convergencia Polinomial
    # ----------------------------------------------------
    ws3 = wb.create_sheet(title="Convergencia Taylor")
    ws3.views.sheetView[0].showGridLines = True

    # Title Block
    ws3.merge_cells("A1:I1")
    ws3["A1"] = "CONTINUUM LAB // DEMOSTRACIÓN DE LA FÓRMULA DE EULER VÍA SERIES DE TAYLOR"
    ws3["A1"].font = font_title
    ws3["A1"].fill = fill_title
    ws3["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws3.row_dimensions[1].height = 36

    ws3["A2"] = "e^{it} = sum_{k=0}^infty (it)^k / k! = [1 - t^2/2! + t^4/4! - ...] + i [t - t^3/3! + t^5/5! - ...]"
    ws3["A2"].font = Font(name="Calibri", size=10, italic=True, color="64748B")

    headers3 = [
        "Paso",
        "t [rad]",
        "cos(t) Exacto",
        "cos Orden 2 (1-t^2/2)",
        "cos Orden 4 (P2+t^4/24)",
        "sin(t) Exacto",
        "sin Orden 3 (t-t^3/6)",
        "sin Orden 5 (P3+t^5/120)",
        "Error Residual Modulus"
    ]

    h_row3 = 4
    ws3.row_dimensions[h_row3].height = 24
    for col_idx, h_text in enumerate(headers3, start=1):
        cell = ws3.cell(row=h_row3, column=col_idx, value=h_text)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = cell_border

    # Sample points from 0 to 2*pi
    t_test_points = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, round(math.pi, 5)]
    for i, t_val in enumerate(t_test_points):
        r = h_row3 + 1 + i
        ws3.row_dimensions[r].height = 20
        zebra = fill_zebra if (i % 2 == 1) else None

        ws3.cell(row=r, column=1, value=i).alignment = Alignment(horizontal="center")
        c_t = ws3.cell(row=r, column=2, value=t_val)
        c_t.alignment = Alignment(horizontal="right")
        c_t.number_format = "0.0000"

        # Exact cos
        c_cos_ex = ws3.cell(row=r, column=3, value=f"=COS(B{r})")
        c_cos_ex.number_format = "0.00000"
        c_cos_ex.alignment = Alignment(horizontal="right")

        # Taylor cos order 2: 1 - t^2 / 2
        c_cos_p2 = ws3.cell(row=r, column=4, value=f"=1 - (B{r}^2)/2")
        c_cos_p2.number_format = "0.00000"
        c_cos_p2.alignment = Alignment(horizontal="right")

        # Taylor cos order 4: 1 - t^2/2 + t^4/24
        c_cos_p4 = ws3.cell(row=r, column=5, value=f"=1 - (B{r}^2)/2 + (B{r}^4)/24")
        c_cos_p4.number_format = "0.00000"
        c_cos_p4.alignment = Alignment(horizontal="right")

        # Exact sin
        c_sin_ex = ws3.cell(row=r, column=6, value=f"=SIN(B{r})")
        c_sin_ex.number_format = "0.00000"
        c_sin_ex.alignment = Alignment(horizontal="right")

        # Taylor sin order 3: t - t^3/6
        c_sin_p3 = ws3.cell(row=r, column=7, value=f"=B{r} - (B{r}^3)/6")
        c_sin_p3.number_format = "0.00000"
        c_sin_p3.alignment = Alignment(horizontal="right")

        # Taylor sin order 5: t - t^3/6 + t^5/120
        c_sin_p5 = ws3.cell(row=r, column=8, value=f"=B{r} - (B{r}^3)/6 + (B{r}^5)/120")
        c_sin_p5.number_format = "0.00000"
        c_sin_p5.alignment = Alignment(horizontal="right")

        # Residual modulus error between order 4/5 approximation and 1:
        # SQRT(E{r}^2 + H{r}^2) - 1
        c_res = ws3.cell(row=r, column=9, value=f"=ABS(SQRT(E{r}^2 + H{r}^2) - 1)")
        c_res.number_format = "0.00000"
        c_res.alignment = Alignment(horizontal="right")

        for col_idx in range(1, 10):
            cell = ws3.cell(row=r, column=col_idx)
            cell.font = font_body
            cell.border = cell_border
            if zebra:
                cell.fill = zebra

    for col in ws3.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(cell.value or "")) for cell in col)
        ws3.column_dimensions[col_letter].width = max(max_len + 4, 15)

    wb.save(file_path)
    return file_path
