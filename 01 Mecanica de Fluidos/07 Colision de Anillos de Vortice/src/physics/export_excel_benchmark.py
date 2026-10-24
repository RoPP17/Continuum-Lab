"""
Continuum Lab - Dynamic Excel Benchmark Generator
Module: 01 Mecanica de Fluidos / 07 Colision de Anillos de Vortice
File: src/physics/export_excel_benchmark.py

Generates professional Excel workbook: Vortex_Rings_Collision_Benchmark.xlsx
Following Continuum Lab standards & openpyxl dynamic modeling:
  - Sheet 1: 'KPI & Hydrodynamic Summary' (Executive summary, KPI cards, parameters)
  - Sheet 2: 'Kinematic Time Series' (Detailed 120-step trajectory with dynamic formulas)
"""

import os
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from .vortex_collision_sim import VortexRingsCollisionSim


def generate_vortex_excel_benchmark(output_path: str):
    sim = VortexRingsCollisionSim()
    wb = openpyxl.Workbook()

    # Sheet 1: Dashboard
    ws_dash = wb.active
    ws_dash.title = "Vortex Collision KPI"
    ws_dash.views.sheetView[0].showGridLines = True

    # Sheet 2: Detailed Data
    ws_data = wb.create_sheet(title="Kinematic Trajectory")
    ws_data.views.sheetView[0].showGridLines = True

    # Palette
    NAVY_HDR = PatternFill(start_color="0A192F", end_color="0A192F", fill_type="solid")
    CARD_FILL = PatternFill(start_color="EBF3FA", end_color="EBF3FA", fill_type="solid")
    ZEBRA_FILL = PatternFill(start_color="F4F7FB", end_color="F4F7FB", fill_type="solid")
    WHITE_FILL = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    CYAN_FILL = PatternFill(start_color="00F0FF", end_color="00F0FF", fill_type="solid")

    FONT_TITLE = Font(name="Segoe UI", size=16, bold=True, color="0A192F")
    FONT_SUBTITLE = Font(name="Segoe UI", size=10, italic=True, color="555555")
    FONT_HDR = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    FONT_BOLD = Font(name="Segoe UI", size=10, bold=True, color="0A192F")
    FONT_BODY = Font(name="Segoe UI", size=10, color="111111")
    FONT_KPI_VAL = Font(name="Segoe UI", size=18, bold=True, color="0A192F")
    FONT_KPI_LBL = Font(name="Segoe UI", size=9, bold=True, color="666666")

    BORDER_THIN = Border(
        left=Side(style='thin', color='D0D7DE'),
        right=Side(style='thin', color='D0D7DE'),
        top=Side(style='thin', color='D0D7DE'),
        bottom=Side(style='thin', color='D0D7DE')
    )

    # -------------------------------------------------------------
    # Sheet 2: Kinematic Data Setup
    # -------------------------------------------------------------
    headers = [
        "Tiempo t (s)", "Posición Axial z (m)", "Radio Anillo R (m)", "Radio Núcleo a (m)",
        "Expansión R/R₀", "Adelgazamiento a/a₀", "Vorticidad Máx ω (s⁻¹)", 
        "Tasa de Deformación (s⁻¹)", "Amplitud Widnall (m)", "Estado Topológico"
    ]

    ws_data.row_dimensions[1].height = 28
    for col_idx, h in enumerate(headers, 1):
        cell = ws_data.cell(row=1, column=col_idx, value=h)
        cell.font = FONT_HDR
        cell.fill = NAVY_HDR
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_THIN

    # Sample trajectory at 120 points
    t_samples = np.linspace(0, 16.0, 120)
    row_idx = 2

    for t_val in t_samples:
        st = sim.get_state(t_val)
        fill = ZEBRA_FILL if row_idx % 2 == 0 else WHITE_FILL
        ws_data.row_dimensions[row_idx].height = 20

        # Numeric values
        c1 = ws_data.cell(row=row_idx, column=1, value=round(t_val, 3))
        c1.number_format = "0.00"

        c2 = ws_data.cell(row=row_idx, column=2, value=round(st["z"], 4))
        c2.number_format = "0.0000"

        c3 = ws_data.cell(row=row_idx, column=3, value=round(st["R"], 4))
        c3.number_format = "0.0000"

        c4 = ws_data.cell(row=row_idx, column=4, value=round(st["a"], 5))
        c4.number_format = "0.00000"

        # Dynamic formulas
        # R / R0 (Col C / C2)
        c5 = ws_data.cell(row=row_idx, column=5, value=f"=C{row_idx}/C$2")
        c5.number_format = "0.00%"

        # a / a0 (Col D / D2)
        c6 = ws_data.cell(row=row_idx, column=6, value=f"=D{row_idx}/D$2")
        c6.number_format = "0.00%"

        # Vorticity
        c7 = ws_data.cell(row=row_idx, column=7, value=round(st["omega_max"], 1))
        c7.number_format = "#,##0.0"

        # Strain rate
        c8 = ws_data.cell(row=row_idx, column=8, value=round(st["strain"], 4))
        c8.number_format = "0.0000"

        # Widnall amplitude
        c9 = ws_data.cell(row=row_idx, column=9, value=round(st["amp_widnall"], 5))
        c9.number_format = "0.00000"

        # Topological State
        state_str = "RECONECTADO (CROWN m=12)" if st["is_reconnected"] else "APROXIMACIÓN & ESTIRAMIENTO"
        c10 = ws_data.cell(row=row_idx, column=10, value=state_str)

        for col in range(1, 11):
            cell = ws_data.cell(row=row_idx, column=col)
            cell.font = FONT_BODY
            cell.fill = fill
            cell.border = BORDER_THIN
            if col in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                cell.alignment = Alignment(horizontal="right", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="center", vertical="center")

        row_idx += 1

    # Auto-adjust column widths
    for col in ws_data.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_data.column_dimensions[col_letter].width = max(max_len + 4, 14)

    # -------------------------------------------------------------
    # Sheet 1: KPI Dashboard Setup
    # -------------------------------------------------------------
    ws_dash.merge_cells("B2:G2")
    ws_dash["B2"] = "CONTINUUM LAB // COLISIÓN DE ANILLOS DE VÓRTICE & RECONEXIÓN"
    ws_dash["B2"].font = FONT_TITLE

    ws_dash.merge_cells("B3:G3")
    ws_dash["B3"] = "Benchmark Hidrodinámico de Vorticidad, Inestabilidad de Widnall (m = 12) y Ley de Biot-Savart"
    ws_dash["B3"].font = FONT_SUBTITLE

    # KPI Summary Cards
    cards = [
        ("B5", "C6", "CIRCULACIÓN INICIAL Γ₀", "1.40 m²/s", "B7", "C8"),
        ("D5", "E6", "EXPANSIÓN MÁXIMA R/R₀", f"='Kinematic Trajectory'!E{row_idx-1}", "D7", "E8"),
        ("F5", "G6", "VORTICIDAD PICO ω_max", f"='Kinematic Trajectory'!G{row_idx-1}", "F7", "G8")
    ]

    for top_l, bot_r, label, formula_val, val_top, val_bot in cards:
        ws_dash.merge_cells(f"{top_l}:{bot_r}")
        ws_dash[top_l].value = label
        ws_dash[top_l].font = FONT_KPI_LBL
        ws_dash[top_l].alignment = Alignment(horizontal="center", vertical="center")
        ws_dash[top_l].fill = CARD_FILL

        ws_dash.merge_cells(f"{val_top}:{val_bot}")
        ws_dash[val_top].value = formula_val
        ws_dash[val_top].font = FONT_KPI_VAL
        ws_dash[val_top].alignment = Alignment(horizontal="center", vertical="center")
        ws_dash[val_top].fill = WHITE_FILL

        # Apply borders
        for r in range(int(top_l[1]), int(val_bot[1]) + 1):
            for c_char in [top_l[0], bot_r[0]]:
                col_i = openpyxl.utils.column_index_from_string(c_char)
                ws_dash.cell(row=r, column=col_i).border = BORDER_THIN

    # Parameters Table (B10 to G16)
    ws_dash.merge_cells("B10:G10")
    ws_dash["B10"] = "PARÁMETROS FÍSICOS Y CONDICIONES DE FRONTERA"
    ws_dash["B10"].font = FONT_HDR
    ws_dash["B10"].fill = NAVY_HDR
    ws_dash["B10"].alignment = Alignment(horizontal="left", vertical="center", indent=1)

    params = [
        ("Radio Inicial del Anillo R₀", f"{sim.R0:.3f} m", "Distancia al plano z₀", f"{sim.z0:.3f} m"),
        ("Radio Inicial del Núcleo a₀", f"{sim.a0:.3f} m", "Número de Onda Azimutal m", f"{sim.m_mode}"),
        ("Circulación de Kelvin Γ₀", f"{sim.Gamma0:.2f} m²/s", "Constante de Lamb-Oseen β", f"{sim.beta:.3f}"),
        ("Tiempo Crítico de Reconexión", f"{sim.t_reconnect:.1f} s", "Anillos Secundarios Formados", "12 bucles radiales"),
        ("Esquema de Integración", "RK4 Simbólico + Biot-Savart Elíptico", "Conservación de Volumen", "2π² · R(t) · a(t)² = const")
    ]

    for p_idx, (p1_lbl, p1_val, p2_lbl, p2_val) in enumerate(params, 11):
        ws_dash.row_dimensions[p_idx].height = 22
        fill = ZEBRA_FILL if p_idx % 2 == 0 else WHITE_FILL

        ws_dash.cell(row=p_idx, column=2, value=p1_lbl).font = FONT_BOLD
        ws_dash.cell(row=p_idx, column=3, value=p1_val).font = FONT_BODY
        ws_dash.cell(row=p_idx, column=4, value=p2_lbl).font = FONT_BOLD
        ws_dash.cell(row=p_idx, column=5, value=p2_val).font = FONT_BODY

        for c_idx in range(2, 6):
            cell = ws_dash.cell(row=p_idx, column=c_idx)
            cell.fill = fill
            cell.border = BORDER_THIN

    # Insights box
    ws_dash.merge_cells("B18:G18")
    ws_dash["B18"] = "FUNDAMENTO CIENTÍFICO Y CONCLUSIONES COMPUTACIONALES"
    ws_dash["B18"].font = FONT_HDR
    ws_dash["B18"].fill = NAVY_HDR
    ws_dash["B18"].alignment = Alignment(horizontal="left", vertical="center", indent=1)

    insights = [
        ("1. Estiramiento de Vorticidad:", "Al aproximarse los dos anillos coaxiales, la inducción mutua desacelera el movimiento axial y estira el radio transversal en más de 250%, concentrando la enstrofia pico."),
        ("2. Inestabilidad de Widnall (m = 12):", "El gradiente de deformación strain rate activa el modo azimutal m = 12, curvando los filamentos toroidales en ondas sinusoidales simétricas."),
        ("3. Reconexión Topológica:", "Los filamentos de vorticidad opuesta se cancelan por difusión viscosa en los puntos de contacto, reconectándose en una corona de 12 anillos secundarios que auto-propulsan radialmente."),
        ("4. Relevancia Aplicada:", "Este fenómeno gobierna la cascada de turbulencia en toberas de propulsión de cohetes, cámaras de combustión y mezcla molecular en chorros sintéticos.")
    ]

    for i_idx, (title, text) in enumerate(insights, 19):
        ws_dash.merge_cells(f"B{i_idx}:G{i_idx}")
        cell = ws_dash[f"B{i_idx}"]
        cell.value = f"{title} {text}"
        cell.font = FONT_BODY
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        cell.fill = ZEBRA_FILL
        ws_dash.row_dimensions[i_idx].height = 26

    # Column widths for dashboard
    for col_l in ["B", "C", "D", "E", "F", "G"]:
        ws_dash.column_dimensions[col_l].width = 18

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    print(f"[+] Dynamic Excel benchmark generated: {output_path}")
    return output_path
