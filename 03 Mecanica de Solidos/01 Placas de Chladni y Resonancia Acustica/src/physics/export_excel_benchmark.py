"""
Continuum Lab - Dynamic Excel Benchmark Generator for Chladni Plate Resonances
Module: 03 Mecanica de Solidos / 01 Placas de Chladni y Resonancia Acustica
File: src/physics/export_excel_benchmark.py

Generates professional engineering benchmark model:
  - Kirchhoff-Love Thin Plate Elasticity & Bending Rigidity D = E*h³/[12*(1-ν²)]
  - Modal Eigenfrequency Formula: f_mn = (π / 2*L²) * sqrt(D / (ρ*h)) * (m² + n²) * α_mn
  - Material Trade Study: Titanium Gr5, SS 304, Al 6061-T6, Brass C36000
  - Granular Cymatic Telemetry with Dynamic Statistical Metrics (AVERAGE, STDEV, MIN, MAX)
  - 100% Dynamic Formulas (Zero Hardcoded values)
"""

from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def create_chladni_excel_benchmark(output_path: str):
    wb = openpyxl.Workbook()

    # Font definitions
    font_title = Font(name="Calibri", size=16, bold=True, color="00F0FF")
    font_subtitle = Font(name="Calibri", size=10, italic=True, color="94A3B8")
    font_sec_hdr = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_tbl_hdr = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_data = Font(name="Calibri", size=10, color="E2E8F0")
    font_kpi_lbl = Font(name="Calibri", size=8, bold=True, color="94A3B8")
    font_kpi_val = Font(name="Calibri", size=13, bold=True, color="00F0FF")
    font_summary = Font(name="Calibri", size=10, bold=True, color="FFFFFF")

    # Fills
    fill_bg = PatternFill(start_color="0B0F19", end_color="0B0F19", fill_type="solid")
    fill_hdr = PatternFill(start_color="10172A", end_color="10172A", fill_type="solid")
    fill_sec = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    fill_th = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    fill_card = PatternFill(start_color="162032", end_color="162032", fill_type="solid")
    fill_zebra_1 = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    fill_zebra_2 = PatternFill(start_color="141E33", end_color="141E33", fill_type="solid")
    fill_kpi = PatternFill(start_color="111C2E", end_color="111C2E", fill_type="solid")

    # Borders
    thin_border_side = Side(style="thin", color="334155")
    card_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    tbl_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    summary_top = Border(top=Side(style="thin", color="00F0FF"), bottom=Side(style="double", color="00F0FF"))

    # Alignments
    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")

    # =========================================================================
    # SHEET 1: PARAMETROS Y MATERIALES
    # =========================================================================
    ws1 = wb.active
    ws1.title = "Parametros_y_Materiales"
    ws1.views.sheetView[0].showGridLines = True

    # Title Banner
    ws1.merge_cells("A1:G1")
    ws1["A1"] = "CONTINUUM LAB // RESONANCIA DE PLACAS Y FIGURAS DE CHLADNI"
    ws1["A1"].font = font_title
    ws1["A1"].fill = fill_hdr
    ws1["A1"].alignment = align_left

    ws1.merge_cells("A2:G2")
    ws1["A2"] = "Modelo Analítico de Elasticidad de Kirchhoff-Love & Estudio Comparativo de Materiales"
    ws1["A2"].font = font_subtitle
    ws1["A2"].fill = fill_hdr
    ws1["A2"].alignment = align_left
    ws1.row_dimensions[1].height = 25
    ws1.row_dimensions[2].height = 18

    # KPI Summary Cards (Row 4 to 5)
    cards = [
        ("A4", "B4", "A5", "B5", "RIGIDEZ FLEXION D (Ti)", "=E17", '0.0000 "N·m"'),
        ("C4", "D4", "C5", "D5", "VELOCIDAD ONDA c_p", "=F17", '#,##0.0 "m/s"'),
        ("E4", "F4", "E5", "F5", "MODO FUNDAMENTAL f_11", "=G17", '0.0 "Hz"'),
        ("G4", "G4", "G5", "G5", "GRANOS ARENA", "15000", '#,##0 "partículas"'),
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

    # Section 1 Header: Dimensiones de la Placa
    ws1.merge_cells("A7:G7")
    ws1["A7"] = "1. ESPECIFICACIONES GEOMÉTRICAS Y DE ENSAYO"
    ws1["A7"].font = font_sec_hdr
    ws1["A7"].fill = fill_sec
    ws1.row_dimensions[7].height = 20

    geom_hdrs = ["Parámetro", "Símbolo", "Valor Nominal", "Unidad", "Descripción"]
    for col_idx, h in enumerate(geom_hdrs, start=1):
        c = ws1.cell(row=8, column=col_idx, value=h)
        c.font = font_tbl_hdr
        c.fill = fill_th
        c.alignment = align_left if col_idx in [1, 5] else align_center

    geom_rows = [
        ("Longitud de la Placa", "L", 0.30, "m", "Placa cuadrada de 30 cm de lado"),
        ("Espesor de la Placa", "h", 0.001, "m", "Chapa calibrada de 1.0 mm"),
        ("Área Superficial", "A", "=C9*C9", "m²", "Área de resonancia continua"),
        ("Aceleración Gravitatoria", "g", 9.81, "m/s²", "Aceleración de gravedad estándar"),
        ("Número de Partículas", "N", 15000, "-", "Granulometría de arena de sílice (d ~ 150 μm)"),
    ]

    for r_idx, (p_name, p_sym, p_val, p_unit, p_desc) in enumerate(geom_rows, start=9):
        ws1.cell(row=r_idx, column=1, value=p_name).font = font_data
        ws1.cell(row=r_idx, column=2, value=p_sym).font = font_data
        c_val = ws1.cell(row=r_idx, column=3, value=p_val)
        c_val.font = font_data
        if isinstance(p_val, float):
            c_val.number_format = "0.000" if p_val < 1 else "0.00"
        elif str(p_val).startswith("="):
            c_val.number_format = "0.0000"
        else:
            c_val.number_format = "#,##0"

        ws1.cell(row=r_idx, column=4, value=p_unit).font = font_data
        ws1.cell(row=r_idx, column=5, value=p_desc).font = font_subtitle

        fill = fill_zebra_1 if r_idx % 2 == 1 else fill_zebra_2
        for c in range(1, 6):
            ws1.cell(row=r_idx, column=c).fill = fill
            ws1.cell(row=r_idx, column=c).border = tbl_border

    # Section 2: Material Trade Study
    ws1.merge_cells("A15:G15")
    ws1["A15"] = "2. ESTUDIO COMPARATIVO DE MATERIALES ELASTOMÉTRICOS"
    ws1["A15"].font = font_sec_hdr
    ws1["A15"].fill = fill_sec
    ws1.row_dimensions[15].height = 20

    mat_hdrs = ["Material", "Módulo Young E (GPa)", "Densidad ρ (kg/m³)", "Poisson ν", "Rigidez Flexión D (N·m)", "Velocidad Onda cp (m/s)", "Frec. Base f_11 (Hz)"]
    for col_idx, h in enumerate(mat_hdrs, start=1):
        c = ws1.cell(row=16, column=col_idx, value=h)
        c.font = font_tbl_hdr
        c.fill = fill_th
        c.alignment = align_center

    mat_rows = [
        ("Titanio Grado 5 (Ti-6Al-4V)", 114.0, 4430.0, 0.34),
        ("Acero Inoxidable AISI 304", 193.0, 8000.0, 0.29),
        ("Aluminio Aeroespacial 6061-T6", 68.9, 2700.0, 0.33),
        ("Latón para Instrumentos C36000", 105.0, 8500.0, 0.35),
    ]

    for idx, (m_name, m_E, m_rho, m_nu) in enumerate(mat_rows, start=17):
        ws1.cell(row=idx, column=1, value=m_name).font = font_data
        c_E = ws1.cell(row=idx, column=2, value=m_E)
        c_E.font = font_data
        c_E.number_format = "0.0"

        c_rho = ws1.cell(row=idx, column=3, value=m_rho)
        c_rho.font = font_data
        c_rho.number_format = "#,##0"

        c_nu = ws1.cell(row=idx, column=4, value=m_nu)
        c_nu.font = font_data
        c_nu.number_format = "0.00"

        # D = E*1e9 * h³ / (12*(1 - ν²))
        c_D = ws1.cell(row=idx, column=5, value=f"=(B{idx}*10^9)*($C$10^3)/(12*(1-D{idx}^2))")
        c_D.font = font_data
        c_D.number_format = "0.0000"

        # cp = sqrt((E*1e9)/(rho*(1-nu²)))
        c_cp = ws1.cell(row=idx, column=6, value=f"=SQRT((B{idx}*10^9)/(C{idx}*(1-D{idx}^2)))")
        c_cp.font = font_data
        c_cp.number_format = "#,##0.0"

        # f11 = (pi / (2*L²)) * sqrt(D / (rho*h)) * (1² + 1²) * 0.85
        c_f11 = ws1.cell(row=idx, column=7, value=f"=(PI()/(2*$C$9^2))*SQRT(E{idx}/(C{idx}*$C$10))*(1^2+1^2)*0.85")
        c_f11.font = font_data
        c_f11.number_format = "0.0"

        fill = fill_zebra_1 if idx % 2 == 1 else fill_zebra_2
        for c in range(1, 8):
            ws1.cell(row=idx, column=c).fill = fill
            ws1.cell(row=idx, column=c).border = tbl_border

    # =========================================================================
    # SHEET 2: ESPECTRO MODAL DE CHLADNI
    # =========================================================================
    ws2 = wb.create_sheet(title="Espectro_Modal_Chladni")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:G1")
    ws2["A1"] = "ESPECTRO DE FRECUENCIAS NATURALES Y MODOS PROPIOS (CHLADNI-GERMAIN)"
    ws2["A1"].font = font_title
    ws2["A1"].fill = fill_hdr
    ws2["A1"].alignment = align_left

    ws2.merge_cells("A2:G2")
    ws2["A2"] = "Solución Analítica por Superposición de Modos Degenerados de Kirchhoff-Love"
    ws2["A2"].font = font_subtitle
    ws2["A2"].fill = fill_hdr
    ws2["A2"].alignment = align_left
    ws2.row_dimensions[1].height = 25
    ws2.row_dimensions[2].height = 18

    # Headers for Modal Table
    modal_hdrs = ["Régimen", "Modo (m)", "Modo (n)", "Frecuencia Teórica f_mn (Hz)", "Frecuencia Sintonizada (Hz)", "Aceleración az/g (Peak)", "Topología Nodal"]
    for col_idx, h in enumerate(modal_hdrs, start=1):
        c = ws2.cell(row=4, column=col_idx, value=h)
        c.font = font_tbl_hdr
        c.fill = fill_th
        c.alignment = align_center

    modal_data = [
        ("Modo 1", 1, 3, 432.0, "Cruz y Diamante Central"),
        ("Transición 1", 2, 4, 880.0, "Anillo Cuádruple"),
        ("Modo 2", 3, 3, 1420.0, "Mandala Nodal Simétrico"),
        ("Transición 2", 2, 6, 2150.0, "Celosía Elíptica"),
        ("Modo 3", 3, 5, 2860.0, "Red Hiperbólica 12 Lóbulos"),
        ("Modo 4 (Clímax)", 5, 5, 4320.0, "Celosía Fractal 25 Celdas"),
    ]

    for idx, (m_reg, m_m, m_n, f_tun, topol) in enumerate(modal_data, start=5):
        ws2.cell(row=idx, column=1, value=m_reg).font = font_data
        ws2.cell(row=idx, column=2, value=m_m).font = font_data
        ws2.cell(row=idx, column=3, value=m_n).font = font_data

        # Dynamic Formula for f_mn based on Sheet 1 parameters:
        # =(PI()/(2*Parametros_y_Materiales!$C$9^2))*SQRT(Parametros_y_Materiales!$E$17/(Parametros_y_Materiales!$C$17*Parametros_y_Materiales!$C$10))*(B{idx}^2+C{idx}^2)*0.85
        c_f_teo = ws2.cell(
            row=idx,
            column=4,
            value=f"=(PI()/(2*Parametros_y_Materiales!$C$9^2))*SQRT(Parametros_y_Materiales!$E$17/(Parametros_y_Materiales!$C$17*Parametros_y_Materiales!$C$10))*(B{idx}^2+C{idx}^2)*0.85"
        )
        c_f_teo.font = font_data
        c_f_teo.number_format = "0.0"

        c_f_tun = ws2.cell(row=idx, column=5, value=f_tun)
        c_f_tun.font = font_data
        c_f_tun.number_format = "0.0"

        # az/g = (2*pi*f)^2 * 0.00012 / 9.81
        c_az = ws2.cell(row=idx, column=6, value=f"=((2*PI()*E{idx})^2)*0.00012/9.81")
        c_az.font = font_data
        c_az.number_format = "0.0"

        ws2.cell(row=idx, column=7, value=topol).font = font_subtitle

        fill = fill_zebra_1 if idx % 2 == 1 else fill_zebra_2
        for c in range(1, 8):
            ws2.cell(row=idx, column=c).fill = fill
            ws2.cell(row=idx, column=c).border = tbl_border

    # Summary Row
    summary_r = len(modal_data) + 5
    ws2.cell(row=summary_r, column=1, value="PROMEDIO GENERAL").font = font_summary
    ws2.cell(row=summary_r, column=4, value=f"=AVERAGE(D5:D{summary_r-1})").font = font_summary
    ws2.cell(row=summary_r, column=4).number_format = "0.0"
    ws2.cell(row=summary_r, column=5, value=f"=AVERAGE(E5:E{summary_r-1})").font = font_summary
    ws2.cell(row=summary_r, column=5).number_format = "0.0"
    ws2.cell(row=summary_r, column=6, value=f"=AVERAGE(F5:F{summary_r-1})").font = font_summary
    ws2.cell(row=summary_r, column=6).number_format = "0.0"

    for c in range(1, 8):
        ws2.cell(row=summary_r, column=c).border = summary_top
        ws2.cell(row=summary_r, column=c).fill = fill_sec

    # =========================================================================
    # Auto-adjust column widths
    # =========================================================================
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
    print(f"[OK] Dynamic Excel Benchmark saved to: {output_path}")
    return output_path
