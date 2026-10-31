"""
Continuum Lab - Dynamic Excel Benchmark Generator for Supersonic Shock Diamonds
Module: 01 Mecanica de Fluidos / 09 Diamantes de Choque y Discos de Mach
File: src/physics/export_excel_benchmark.py

Generates a professional engineering spreadsheet conforming to Continuum Lab standards:
  - Dynamic uppercase formulas (no hardcoded calculated values)
  - Cohesive design palette: Deep Navy / Aerodynamic Cyan & Solar Gold
  - Visible gridlines, explicit number formatting, and auto-adjusted column widths
  - 5 comprehensive worksheets:
      1. Resumen Ejecutivo (Executive Summary & Thermodynamic Constants)
      2. Nozzle & Prandtl-Meyer (Isentropic Gas Dynamics & Expansion Fans)
      3. Sweep Parametrico NPR (Nozzle Pressure Ratio from 2 to 80)
      4. Saltos Rankine-Hugoniot (Normal & Oblique Shock Waves)
      5. Telemetria Dinamica 16s (Time series matching the 60 FPS master video)
"""

import os
import math
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def generate_shock_diamonds_excel_benchmark(output_path: str) -> str:
    wb = openpyxl.Workbook()
    # Remove default sheet
    if "Sheet" in wb.sheetnames:
        wb.remove(wb["Sheet"])

    # -------------------------------------------------------------------------
    # Styles & Palette (Navy & Aerodynamic Cyan)
    # -------------------------------------------------------------------------
    font_title = Font(name="Segoe UI", size=16, bold=True, color="00F0FF")
    font_subtitle = Font(name="Segoe UI", size=10, italic=True, color="A0AAB5")
    font_section = Font(name="Segoe UI", size=12, bold=True, color="0B132B")
    font_header = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    font_data = Font(name="Segoe UI", size=9, color="1C2541")
    font_bold = Font(name="Segoe UI", size=9, bold=True, color="0B132B")

    fill_banner = PatternFill(start_color="0B132B", end_color="0B132B", fill_type="solid")
    fill_header = PatternFill(start_color="1C2541", end_color="1C2541", fill_type="solid")
    fill_sub_header = PatternFill(start_color="3A506B", end_color="3A506B", fill_type="solid")
    fill_zebra = PatternFill(start_color="F4F7FB", end_color="F4F7FB", fill_type="solid")
    fill_highlight = PatternFill(start_color="E0F7FA", end_color="E0F7FA", fill_type="solid")
    fill_gold = PatternFill(start_color="FFF8E1", end_color="FFF8E1", fill_type="solid")

    thin_border = Border(
        left=Side(style="thin", color="D0D7DE"),
        right=Side(style="thin", color="D0D7DE"),
        top=Side(style="thin", color="D0D7DE"),
        bottom=Side(style="thin", color="D0D7DE")
    )
    double_bottom_border = Border(
        left=Side(style="thin", color="D0D7DE"),
        right=Side(style="thin", color="D0D7DE"),
        top=Side(style="thin", color="D0D7DE"),
        bottom=Side(style="double", color="0B132B")
    )

    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")

    # =========================================================================
    # Sheet 1: Resumen Ejecutivo
    # =========================================================================
    ws1 = wb.create_sheet("Resumen Ejecutivo")
    ws1.views.sheetView[0].showGridLines = True

    ws1.merge_cells("A1:G2")
    ws1["A1"] = "CONTINUUM LAB // DIAMANTES DE CHOQUE Y DISCOS DE MACH EN JETS HIPERSÓNICOS"
    ws1["A1"].font = font_title
    ws1["A1"].fill = fill_banner
    ws1["A1"].alignment = align_center

    ws1["A3"] = "Módulo 01: Mecánica de Fluidos | Entrega #25 | Modelo Gasdinámico Compresible (Navier-Stokes / Euler)"
    ws1["A3"].font = font_subtitle

    # Metadata & Physical Constants
    constants = [
        ("Constante Físico-Termodinámica", "Símbolo", "Valor Numérico", "Unidades", "Descripción Técnica"),
        ("Razón de Calores Específicos", "gamma", 1.28, "-", "Gas de combustión hidrocarburo-oxígeno (Methalox/Kerolox)"),
        ("Constante Específica del Gas", "R_spec", 320.0, "J/(kg·K)", "Constante individual para mezcla de escape"),
        ("Presión de Cámara (Estancamiento)", "p_0", 7000000.0, "Pa", "Presión en cámara de combustión (70.0 bar)"),
        ("Temperatura de Cámara (Total)", "T_0", 3400.0, "K", "Temperatura de combustión adiabática"),
        ("Presión Atmosférica Ambiente", "p_a", 101325.0, "Pa", "Nivel del mar estándar (1.00 atm)"),
        ("Temperatura Ambiente", "T_a", 293.15, "K", "20.0 °C"),
        ("Diámetro de Salida de Tobera", "d_e", 0.45, "m", "Tobera convergente-divergente de Laval"),
        ("Radio de Salida de Tobera", "r_e", "=C9/2", "m", "Radio geométrico de garganta a salida"),
        ("Número de Mach de Diseño (Salida)", "M_e", 2.45, "-", "Mach nominal en la sección de salida"),
        ("Razón de Presión de Tobera Nominal", "NPR_nom", "=C5/C7", "-", "Nozzle Pressure Ratio nominal (p0 / pa)"),
    ]

    r_start = 5
    for row_idx, row_data in enumerate(constants):
        is_hdr = (row_idx == 0)
        curr_r = r_start + row_idx
        for col_idx, val in enumerate(row_data):
            cell = ws1.cell(row=curr_r, column=col_idx + 1, value=val)
            cell.font = font_header if is_hdr else (font_bold if col_idx in [1, 2] else font_data)
            cell.fill = fill_header if is_hdr else (fill_zebra if row_idx % 2 == 1 else PatternFill(fill_type=None))
            cell.border = thin_border
            cell.alignment = align_center if col_idx in [1, 3] else (align_right if col_idx == 2 and not is_hdr else align_left)
            if not is_hdr and col_idx == 2:
                if row_idx in [3, 5]:
                    cell.number_format = "#,##0"
                elif row_idx in [2, 4, 6]:
                    cell.number_format = "#,##0.0"
                else:
                    cell.number_format = "0.00"

    # =========================================================================
    # Sheet 2: Nozzle & Prandtl-Meyer
    # =========================================================================
    ws2 = wb.create_sheet("Nozzle & Prandtl-Meyer")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:G1")
    ws2["A1"] = "RELACIONES ISENTRÓPICAS Y FUNCIÓN DE EXPANSIÓN DE PRANDTL-MEYER"
    ws2["A1"].font = font_title
    ws2["A1"].fill = fill_banner
    ws2["A1"].alignment = align_center

    ws2["A2"] = "Ecuaciones gobernantes: T/T0 = (1 + 0.5*(gamma-1)*M^2)^(-1) | p/p0 = (T/T0)^(gamma/(gamma-1)) | nu(M)"
    ws2["A2"].font = font_subtitle

    headers_pm = [
        "Mach M",
        "T / T0",
        "p / p0",
        "rho / rho0",
        "Presión Estática [kPa]",
        "Temp Estática [K]",
        "Ángulo Prandtl-Meyer nu(M) [°]"
    ]

    for col_idx, h in enumerate(headers_pm, start=1):
        c = ws2.cell(row=4, column=col_idx, value=h)
        c.font = font_header
        c.fill = fill_header
        c.alignment = align_center
        c.border = thin_border

    mach_vals = [1.00, 1.20, 1.40, 1.60, 1.80, 2.00, 2.20, 2.40, 2.45, 2.60, 2.80, 3.00, 3.20, 3.50, 4.00, 4.50, 5.00]
    for idx, m in enumerate(mach_vals, start=5):
        ws2.cell(row=idx, column=1, value=m).number_format = "0.00"
        # Dynamic formula references to Sheet 1 constants: gamma = 'Resumen Ejecutivo'!$C$6, p0 = 'Resumen Ejecutivo'!$C$8, T0 = 'Resumen Ejecutivo'!$C$9
        ws2.cell(row=idx, column=2, value=f"=1/(1 + 0.5*('Resumen Ejecutivo'!$C$6 - 1)*A{idx}^2)").number_format = "0.0000"
        ws2.cell(row=idx, column=3, value=f"=B{idx}^('Resumen Ejecutivo'!$C$6/('Resumen Ejecutivo'!$C$6 - 1))").number_format = "0.00000"
        ws2.cell(row=idx, column=4, value=f"=B{idx}^(1/('Resumen Ejecutivo'!$C$6 - 1))").number_format = "0.0000"
        ws2.cell(row=idx, column=5, value=f"=C{idx} * 'Resumen Ejecutivo'!$C$8 / 1000").number_format = "#,##0.0"
        ws2.cell(row=idx, column=6, value=f"=B{idx} * 'Resumen Ejecutivo'!$C$9").number_format = "#,##0.0"
        # Prandtl-Meyer analytical approximation in degrees:
        ws2.cell(
            row=idx, column=7,
            value=f"=DEGREES(SQRT(('Resumen Ejecutivo'!$C$6+1)/('Resumen Ejecutivo'!$C$6-1))*ATAN(SQRT(('Resumen Ejecutivo'!$C$6-1)/('Resumen Ejecutivo'!$C$6+1)*MAX(0.0001, A{idx}^2-1))) - ATAN(SQRT(MAX(0.0001, A{idx}^2-1))))"
        ).number_format = "0.00°"

        for col_idx in range(1, 8):
            cell = ws2.cell(row=idx, column=col_idx)
            cell.font = font_bold if m == 2.45 else font_data
            cell.fill = fill_highlight if m == 2.45 else (fill_zebra if idx % 2 == 1 else PatternFill(fill_type=None))
            cell.border = thin_border
            cell.alignment = align_right if col_idx > 1 else align_center

    # =========================================================================
    # Sheet 3: Sweep Paramétrico NPR
    # =========================================================================
    ws3 = wb.create_sheet("Sweep Parametrico NPR")
    ws3.views.sheetView[0].showGridLines = True

    ws3.merge_cells("A1:H1")
    ws3["A1"] = "BARRIDO PARAMÉTRICO DE RAZÓN DE PRESIÓN DE TOBERA (NPR = p0 / pa)"
    ws3["A1"].font = font_title
    ws3["A1"].fill = fill_banner
    ws3["A1"].alignment = align_center

    ws3["A2"] = "Cálculo analítico del tamaño de celda de choque (Fórmula de Prandtl-Pack) y diámetro del Disco de Mach"
    ws3["A2"].font = font_subtitle

    headers_npr = [
        "NPR (p0/pa)",
        "p0 [bar]",
        "p_exit [kPa]",
        "Razón p_exit / pa",
        "Régimen de Expansión",
        "Espaciado Diamante L_d [m]",
        "Diámetro Disco Mach [m]",
        "Temp Núcleo Disco Mach [K]"
    ]

    for col_idx, h in enumerate(headers_npr, start=1):
        c = ws3.cell(row=4, column=col_idx, value=h)
        c.font = font_header
        c.fill = fill_header
        c.alignment = align_center
        c.border = thin_border

    npr_list = [5.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 69.1, 80.0, 100.0, 120.0]
    for idx, npr in enumerate(npr_list, start=5):
        ws3.cell(row=idx, column=1, value=npr).number_format = "0.0"
        ws3.cell(row=idx, column=2, value=f"=A{idx} * 'Resumen Ejecutivo'!$C$10 / 100000").number_format = "0.00"
        ws3.cell(row=idx, column=3, value=f"=(B{idx} * 100000) * (1 + 0.5*('Resumen Ejecutivo'!$C$6-1)*'Resumen Ejecutivo'!$C$14^2)^(-'Resumen Ejecutivo'!$C$6/('Resumen Ejecutivo'!$C$6-1)) / 1000").number_format = "#,##0.0"
        ws3.cell(row=idx, column=4, value=f"=(C{idx} * 1000) / 'Resumen Ejecutivo'!$C$10").number_format = "0.00"
        ws3.cell(row=idx, column=5, value=f'=IF(D{idx}<0.95, "Sobreevpandido", IF(D{idx}>1.05, "Subexpandido", "Adaptado (Óptimo)"))')
        # Prandtl-Pack formula: L_d = 1.306 * d_e * sqrt(Me^2 - 1) * sqrt(pe/pa)
        ws3.cell(row=idx, column=6, value=f"=1.306 * 'Resumen Ejecutivo'!$C$12 * SQRT(MAX(0.1, 'Resumen Ejecutivo'!$C$14^2 - 1)) * SQRT(MAX(0.5, D{idx}))").number_format = "0.000 m"
        # Mach disk diameter: D_disk = d_e * 0.38 * sqrt(max(0, pe/pa - 1))
        ws3.cell(row=idx, column=7, value=f"='Resumen Ejecutivo'!$C$12 * 0.38 * SQRT(MAX(0, D{idx} - 1))").number_format = "0.000 m"
        # Core stagnation temperature spike
        ws3.cell(row=idx, column=8, value=f"='Resumen Ejecutivo'!$C$9 * (0.82 + 0.12 * MIN(1.0, D{idx}/4))").number_format = "#,##0 K"

        for col_idx in range(1, 9):
            cell = ws3.cell(row=idx, column=col_idx)
            is_nom = abs(npr - 69.1) < 0.2
            cell.font = font_bold if is_nom else font_data
            cell.fill = fill_highlight if is_nom else (fill_zebra if idx % 2 == 1 else PatternFill(fill_type=None))
            cell.border = thin_border
            cell.alignment = align_center if col_idx in [1, 5] else align_right

    # =========================================================================
    # Sheet 4: Saltos Rankine-Hugoniot
    # =========================================================================
    ws4 = wb.create_sheet("Saltos Rankine-Hugoniot")
    ws4.views.sheetView[0].showGridLines = True

    ws4.merge_cells("A1:G1")
    ws4["A1"] = "RELACIONES DE SALTO DE ONDA DE CHOQUE NORMAL (RANKINE-HUGONIOT)"
    ws4["A1"].font = font_title
    ws4["A1"].fill = fill_banner
    ws4["A1"].alignment = align_center

    ws4["A2"] = "Leyes de conservación unidimensionales de masa, cantidad de movimiento y energía en choque normal"
    ws4["A2"].font = font_subtitle

    headers_rh = [
        "Mach Incidente M1",
        "Mach Detrás M2",
        "Salto Presión p2 / p1",
        "Salto Temperatura T2 / T1",
        "Salto Densidad rho2 / rho1",
        "Pérdida Presión Estancamiento p02 / p01",
        "Incremento de Entropía Delta s [J/kg·K]"
    ]

    for col_idx, h in enumerate(headers_rh, start=1):
        c = ws4.cell(row=4, column=col_idx, value=h)
        c.font = font_header
        c.fill = fill_header
        c.alignment = align_center
        c.border = thin_border

    m1_vals = [1.00, 1.20, 1.40, 1.60, 1.80, 2.00, 2.20, 2.45, 2.70, 3.00, 3.50, 4.00, 4.50, 5.00]
    for idx, m1 in enumerate(m1_vals, start=5):
        ws4.cell(row=idx, column=1, value=m1).number_format = "0.00"
        # M2: SQRT(((gamma-1)*M1^2 + 2) / (2*gamma*M1^2 - (gamma-1)))
        ws4.cell(row=idx, column=2, value=f"=SQRT((('Resumen Ejecutivo'!$C$6-1)*A{idx}^2 + 2) / (2*'Resumen Ejecutivo'!$C$6*A{idx}^2 - ('Resumen Ejecutivo'!$C$6-1)))").number_format = "0.000"
        # p2/p1: 1 + 2*gamma/(gamma+1)*(M1^2 - 1)
        ws4.cell(row=idx, column=3, value=f"=1 + (2*'Resumen Ejecutivo'!$C$6/('Resumen Ejecutivo'!$C$6+1))*(A{idx}^2 - 1)").number_format = "0.00"
        # rho2/rho1: (gamma+1)*M1^2 / ((gamma-1)*M1^2 + 2)
        ws4.cell(row=idx, column=5, value=f"=(('Resumen Ejecutivo'!$C$6+1)*A{idx}^2) / (('Resumen Ejecutivo'!$C$6-1)*A{idx}^2 + 2)").number_format = "0.00"
        # T2/T1: (p2/p1) / (rho2/rho1)
        ws4.cell(row=idx, column=4, value=f"=C{idx} / E{idx}").number_format = "0.00"
        # p02/p01
        ws4.cell(
            row=idx, column=6,
            value=f"=(E{idx}^('Resumen Ejecutivo'!$C$6/('Resumen Ejecutivo'!$C$6-1))) * (('Resumen Ejecutivo'!$C$6+1)/(2*'Resumen Ejecutivo'!$C$6*A{idx}^2 - ('Resumen Ejecutivo'!$C$6-1)))^(1/('Resumen Ejecutivo'!$C$6-1))"
        ).number_format = "0.0000"
        # Delta s = - R_spec * ln(p02/p01)
        ws4.cell(row=idx, column=7, value=f"=-'Resumen Ejecutivo'!$C$7 * LN(F{idx})").number_format = "#,##0.0"

        for col_idx in range(1, 8):
            cell = ws4.cell(row=idx, column=col_idx)
            is_nom = abs(m1 - 2.45) < 0.02
            cell.font = font_bold if is_nom else font_data
            cell.fill = fill_highlight if is_nom else (fill_zebra if idx % 2 == 1 else PatternFill(fill_type=None))
            cell.border = thin_border
            cell.alignment = align_right if col_idx > 1 else align_center

    # =========================================================================
    # Sheet 5: Telemetría Dinámica 16s
    # =========================================================================
    ws5 = wb.create_sheet("Telemetria Dinamica 16s")
    ws5.views.sheetView[0].showGridLines = True

    ws5.merge_cells("A1:H1")
    ws5["A1"] = "SERIE TEMPORAL DE TELEMETRÍA DINÁMICA DE VÍDEO (16.0s SEAMLESS LOOP)"
    ws5["A1"].font = font_title
    ws5["A1"].fill = fill_banner
    ws5["A1"].alignment = align_center

    ws5["A2"] = "Evolución periódica del jet supersónico sincronizada frame a frame con la animación a 60 FPS"
    ws5["A2"].font = font_subtitle

    headers_dyn = [
        "Tiempo t [s]",
        "Fase [rad]",
        "Presión Cámara p0 [MPa]",
        "NPR Dinámico (p0/pa)",
        "Razón Expansión pe/pa",
        "Espaciado Diamante L_d [m]",
        "Radio Disco Mach [cm]",
        "Temp Incandescente [K]"
    ]

    for col_idx, h in enumerate(headers_dyn, start=1):
        c = ws5.cell(row=4, column=col_idx, value=h)
        c.font = font_header
        c.fill = fill_header
        c.alignment = align_center
        c.border = thin_border

    time_steps = [round(t, 2) for t in [i * 0.5 for i in range(33)]]  # 0.0 to 16.0s
    for idx, t_val in enumerate(time_steps, start=5):
        ws5.cell(row=idx, column=1, value=t_val).number_format = "0.00"
        ws5.cell(row=idx, column=2, value=f"=2 * PI() * (A{idx} / 16.0)").number_format = "0.00"
        # Dynamic p0 [MPa] = 7.0 * (1 + 0.16 * SIN(B{idx}))
        ws5.cell(row=idx, column=3, value=f"=('Resumen Ejecutivo'!$C$8 / 1e6) * (1.0 + 0.16 * SIN(B{idx}))").number_format = "0.000 MPa"
        # NPR = (p0 * 1e6) / pa
        ws5.cell(row=idx, column=4, value=f"=(C{idx} * 1000000) / 'Resumen Ejecutivo'!$C$10").number_format = "0.0"
        # pe / pa
        ws5.cell(row=idx, column=5, value=f"=(C{idx} * 1000000 * (1 + 0.5*('Resumen Ejecutivo'!$C$6-1)*'Resumen Ejecutivo'!$C$14^2)^(-'Resumen Ejecutivo'!$C$6/('Resumen Ejecutivo'!$C$6-1))) / 'Resumen Ejecutivo'!$C$10").number_format = "0.00"
        # L_d [m]
        ws5.cell(row=idx, column=6, value=f"=1.306 * 'Resumen Ejecutivo'!$C$12 * SQRT('Resumen Ejecutivo'!$C$14^2 - 1) * SQRT(MAX(0.5, E{idx}))").number_format = "0.000 m"
        # Mach disk radius [cm]
        ws5.cell(row=idx, column=7, value=f"='Resumen Ejecutivo'!$C$13 * 0.38 * SQRT(MAX(0.1, E{idx} - 1)) * 100").number_format = "0.00 cm"
        # T_incandescent [K]
        ws5.cell(row=idx, column=8, value=f"=2650 + 280 * SIN(B{idx})").number_format = "#,##0 K"

        for col_idx in range(1, 9):
            cell = ws5.cell(row=idx, column=col_idx)
            cell.font = font_data
            cell.fill = fill_zebra if idx % 2 == 1 else PatternFill(fill_type=None)
            cell.border = thin_border
            cell.alignment = align_right if col_idx > 1 else align_center

    # =========================================================================
    # Auto-adjust column widths across all sheets
    # =========================================================================
    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = str(cell.value or "")
                if not val.startswith("="):
                    max_len = max(max_len, len(val))
                else:
                    max_len = max(max_len, 10)
            sheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

    # Save workbook
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    print(f"[OK] Dynamic Excel benchmark successfully generated: {output_path}")
    return output_path


if __name__ == "__main__":
    test_out = r"C:\Users\andre\OneDrive\Desktop\Continuum Lab\RENDERS\25 Diamantes de Choque y Discos de Mach Aerodinamicos\Supersonic_Shock_Diamonds_Mach_Disk_Benchmark.xlsx"
    generate_shock_diamonds_excel_benchmark(test_out)
