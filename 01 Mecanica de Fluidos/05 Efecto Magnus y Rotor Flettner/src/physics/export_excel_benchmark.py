"""
Continuum Lab - Dynamic Excel Benchmark Generator
Module: 01 Mecanica de Fluidos / 05 Efecto Magnus y Rotor Flettner
File: src/physics/export_excel_benchmark.py

Strictly adheres to Continuum Lab xlsx skill standards:
  - 100% dynamic uppercase Excel formulas (no hardcoded outputs)
  - Cohesive professional styling (Navy/Cyan Continuum Dark theme)
  - Grid lines enabled explicitly
  - Auto-fitted column widths with padding
  - Comprehensive potential flow theory, Kutta-Joukowski theorem, and Flettner ship case study
"""

import os
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def create_magnus_excel_benchmark(output_path: str) -> str:
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # Styling definitions
    font_title = Font(name="Segoe UI", size=16, bold=True, color="0F172A")
    font_section = Font(name="Segoe UI", size=12, bold=True, color="0369A1")
    font_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    font_data = Font(name="Segoe UI", size=10, color="1E293B")
    font_bold = Font(name="Segoe UI", size=10, bold=True, color="0F172A")
    font_italic = Font(name="Segoe UI", size=9, italic=True, color="64748B")

    fill_header = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    fill_subheader = PatternFill(start_color="0284C7", end_color="0284C7", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_highlight = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")

    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1")
    )
    double_bottom_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="double", color="0F172A")
    )

    # =========================================================================
    # SHEET 1: Parametros_del_Rotor
    # =========================================================================
    ws1 = wb.create_sheet(title="Parametros_del_Rotor")
    ws1.views.sheetView[0].showGridLines = True

    ws1["A1"] = "CONTINUUM LAB // MECÁNICA DE FLUIDOS Y AERODINÁMICA"
    ws1["A1"].font = font_section
    ws1["A2"] = "MODELO DE EFECTO MAGNUS Y ROTOR FLETTNER"
    ws1["A2"].font = font_title
    ws1["A3"] = "Parámetros del Fluido, Geometría del Cilindro y Condiciones de Flujo"
    ws1["A3"].font = font_italic

    headers1 = ["Parámetro Físico", "Símbolo", "Valor / Fórmula Dinámica", "Unidad", "Descripción y Referencia"]
    for col_idx, h in enumerate(headers1, 1):
        cell = ws1.cell(row=5, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws1.row_dimensions[5].height = 24

    params_data = [
        ("Densidad del Aire", "rho", 1.225, "kg/m³", "Densidad atmosférica ISA a nivel del mar"),
        ("Viscosidad Cinemática del Aire", "nu", 0.000015, "m²/s", "Viscosidad a 15°C y 1 atm"),
        ("Velocidad de Flujo Libre", "U_inf", 10.0, "m/s", "Velocidad del viento relativo incidente"),
        ("Radio del Cilindro", "R", 1.0, "m", "Radio exterior del rotor"),
        ("Diámetro del Cilindro", "D", "=2*C9", "m", "Diámetro nominal D = 2*R"),
        ("Longitud / Altura del Rotor", "H", 10.0, "m", "Envergadura del rotor"),
        ("Área Frontal Proyectada", "A_proj", "=C10*C11", "m²", "Área de referencia A = D * H"),
        ("Presión Dinámica del Flujo", "q_inf", "=0.5*C6*C8^2", "Pa", "q = 0.5 * rho * U_inf²"),
        ("Número de Reynolds", "Re", "=(C8*C10)/C7", "-", "Re = (U_inf * D) / nu (Flujo turbulento)"),
        ("Velocidad Angular Base", "omega_ref", 20.0, "rad/s", "Velocidad de rotación angular de referencia"),
        ("RPM de Referencia", "RPM_ref", "=(C15*60)/(2*PI())", "RPM", "Frecuencia de rotación en revoluciones/min"),
    ]

    for idx, (name, sym, val, unit, desc) in enumerate(params_data, 6):
        c1 = ws1.cell(row=idx, column=1, value=name)
        c2 = ws1.cell(row=idx, column=2, value=sym)
        c3 = ws1.cell(row=idx, column=3, value=val)
        c4 = ws1.cell(row=idx, column=4, value=unit)
        c5 = ws1.cell(row=idx, column=5, value=desc)

        c1.font = font_data
        c2.font = font_bold
        c3.font = font_bold if str(val).startswith("=") else font_data
        c4.font = font_italic
        c5.font = font_data

        c1.border = thin_border
        c2.border = thin_border
        c3.border = thin_border
        c4.border = thin_border
        c5.border = thin_border

        if str(val).startswith("="):
            c3.fill = fill_highlight
        elif idx % 2 == 0:
            for cell in (c1, c2, c3, c4, c5):
                cell.fill = fill_zebra

        if sym in ["rho", "nu", "U_inf", "R", "D", "H", "A_proj", "q_inf"]:
            c3.number_format = "#,##0.000" if sym == "nu" else "#,##0.00"
        elif sym == "Re":
            c3.number_format = "#,##0"
        elif sym in ["omega_ref", "RPM_ref"]:
            c3.number_format = "#,##0.0"

    ws1.row_dimensions[17].height = 20

    # =========================================================================
    # SHEET 2: Analisis_Potencial_vs_Real
    # =========================================================================
    ws2 = wb.create_sheet(title="Analisis_Potencial_vs_Real")
    ws2.views.sheetView[0].showGridLines = True

    ws2["A1"] = "BARRIDO DE PARÁMETRO DE GIRO (SPIN RATIO ALPHA) Y SUSTENTACIÓN"
    ws2["A1"].font = font_section
    ws2["A2"] = "Comparativa Teórica Kutta-Joukowski vs Sustentación Real Viscosa Saturada"
    ws2["A2"].font = font_italic

    headers2 = [
        "Spin Ratio (alpha)", "Omega (rad/s)", "Rotor (RPM)", "Circulación Gamma (m²/s)",
        "CL Ideal (2*pi*alpha)", "CL Real (Viscoso)", "CD Real", "Eficiencia L/D",
        "Sustentación L (kN)", "Resistencia D (kN)", "Estado Estancamiento", "Ángulo Theta (°)", "Radio Silla (rs/R)"
    ]

    for col_idx, h in enumerate(headers2, 1):
        cell = ws2.cell(row=4, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
    ws2.row_dimensions[4].height = 28

    alphas = [0.0, 0.2, 0.5, 0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.2, 2.5, 2.8, 3.0, 3.2, 3.5, 4.0]
    for row_idx, a_val in enumerate(alphas, 5):
        # A: alpha
        ws2.cell(row=row_idx, column=1, value=a_val)
        # B: Omega = alpha * U_inf / R
        ws2.cell(row=row_idx, column=2, value=f"=A{row_idx}*Parametros_del_Rotor!$C$8/Parametros_del_Rotor!$C$9")
        # C: RPM = Omega * 60 / (2 * PI())
        ws2.cell(row=row_idx, column=3, value=f"=(B{row_idx}*60)/(2*PI())")
        # D: Gamma = 2 * PI() * R * U_inf * alpha
        ws2.cell(row=row_idx, column=4, value=f"=2*PI()*Parametros_del_Rotor!$C$9*Parametros_del_Rotor!$C$8*A{row_idx}")
        # E: CL Ideal = 2 * PI() * alpha
        ws2.cell(row=row_idx, column=5, value=f"=2*PI()*A{row_idx}")
        # F: CL Real = (2 * PI() * alpha) / (1 + 0.16 * (alpha^1.32))
        ws2.cell(row=row_idx, column=6, value=f"=IF(A{row_idx}=0, 0, (2*PI()*A{row_idx})/(1+0.16*(A{row_idx}^1.32)))")
        # G: CD Real = 0.48 + 0.32 * (alpha^1.22)
        ws2.cell(row=row_idx, column=7, value=f"=0.48+0.32*(A{row_idx}^1.22)")
        # H: L/D = CL_real / CD_real
        ws2.cell(row=row_idx, column=8, value=f"=F{row_idx}/G{row_idx}")
        # I: Lift kN = 0.5 * rho * U_inf^2 * Area * CL_real / 1000
        ws2.cell(row=row_idx, column=9, value=f"=(Parametros_del_Rotor!$C$13*Parametros_del_Rotor!$C$12*F{row_idx})/1000")
        # J: Drag kN = 0.5 * rho * U_inf^2 * Area * CD_real / 1000
        ws2.cell(row=row_idx, column=10, value=f"=(Parametros_del_Rotor!$C$13*Parametros_del_Rotor!$C$12*G{row_idx})/1000")
        # K: Estado Estancamiento
        ws2.cell(row=row_idx, column=11, value=f'=IF(A{row_idx}<1.99, "SUPERFICIE (DOBLE)", IF(A{row_idx}<=2.05, "CRÍTICO (FONDO)", "DESPRENDIDO (SILLA)"))')
        # L: Ángulo Theta (grados)
        ws2.cell(row=row_idx, column=12, value=f'=IF(A{row_idx}<=2, -DEGREES(ASIN(A{row_idx}/2)), "-")')
        # M: Radio Silla rs/R
        ws2.cell(row=row_idx, column=13, value=f'=IF(A{row_idx}>2, (A{row_idx}+SQRT(A{row_idx}^2-4))/2, 1.0)')

        for col in range(1, 14):
            c = ws2.cell(row=row_idx, column=col)
            c.font = font_data
            c.border = thin_border
            if row_idx % 2 == 0:
                c.fill = fill_zebra

        ws2.cell(row=row_idx, column=1).number_format = "0.0"
        ws2.cell(row=row_idx, column=2).number_format = "0.00"
        ws2.cell(row=row_idx, column=3).number_format = "0.0"
        ws2.cell(row=row_idx, column=4).number_format = "0.00"
        ws2.cell(row=row_idx, column=5).number_format = "0.00"
        ws2.cell(row=row_idx, column=6).number_format = "0.00"
        ws2.cell(row=row_idx, column=7).number_format = "0.00"
        ws2.cell(row=row_idx, column=8).number_format = "0.00"
        ws2.cell(row=row_idx, column=9).number_format = "0.00"
        ws2.cell(row=row_idx, column=10).number_format = "0.00"
        ws2.cell(row=row_idx, column=12).number_format = "0.0"
        ws2.cell(row=row_idx, column=13).number_format = "0.00"

    # =========================================================================
    # SHEET 3: Caso_Buque_Carga_Flettner
    # =========================================================================
    ws3 = wb.create_sheet(title="Caso_Buque_Carga_Flettner")
    ws3.views.sheetView[0].showGridLines = True

    ws3["A1"] = "CASO INDUSTRIAL // PROPULSIÓN EÓLICA EN BUQUE ULTRAMAX 50,000 DWT"
    ws3["A1"].font = font_section
    ws3["A2"] = "Ahorro de Combustible, Potencia Propulsiva y Descarbonización Marina"
    ws3["A2"].font = font_title
    ws3["A3"] = "Cálculo Dinámico de Ahorro con 4 Rotores Flettner de 30m x 5m"
    ws3["A3"].font = font_italic

    headers3 = ["Parámetro Operativo / Económico", "Símbolo", "Valor / Fórmula Dinámica", "Unidad", "Descripción"]
    for col_idx, h in enumerate(headers3, 1):
        cell = ws3.cell(row=5, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws3.row_dimensions[5].height = 24

    flettner_ship_data = [
        ("Número de Rotores Flettner Instalados", "N_rot", 4, "unidades", "Cuatro rotores en cubierta"),
        ("Altura de Cada Rotor", "H_rot", 30.0, "m", "Altura del cilindro vertical"),
        ("Diámetro de Cada Rotor", "D_rot", 5.0, "m", "Diámetro exterior"),
        ("Área Frontal por Rotor", "A_rot", "=C7*C8", "m²", "Área proyectada H * D = 150 m²"),
        ("Área Total de Rotores", "A_total", "=C6*C9", "m²", "Área total 4 rotores = 600 m²"),
        ("Velocidad de Crucero del Buque", "V_ship_kn", 14.0, "nudos", "Velocidad de crucero comercial"),
        ("Velocidad de Crucero en m/s", "V_ship_ms", "=C11*0.514444", "m/s", "Conversión a m/s (7.20 m/s)"),
        ("Viento Aparente Relativo Incident", "V_wind", 12.0, "m/s", "Viento aparente (Fuerza 6 Beaufort)"),
        ("Ángulo de Viento Aparente", "Beta_wind", 90.0, "grados", "Viento de través puro (máximo empuje)"),
        ("Spin Ratio Operativo Objetivo", "alpha_target", 3.2, "-", "Punto de máxima eficiencia aerodinámica"),
        ("Coeficiente de Sustentación CL", "CL_ship", "=(2*PI()*C15)/(1+0.16*(C15^1.32))", "-", "CL saturado viscoso a alpha=3.2"),
        ("Fuerza de Sustentación Neta", "L_total_kN", "=(0.5*Parametros_del_Rotor!$C$6*C13^2*C10*C16)/1000", "kN", "Sustentación total 4 rotores"),
        ("Potencia Propulsiva Aportada", "P_prop_kW", "=C17*C12", "kW", "P = Empuje * V_ship"),
        ("Potencia del Motor Principal (MCR)", "P_engine_MCR", 7200.0, "kW", "Potencia nominal motor 2 tiempos diésel"),
        ("Fracción de Potencia Ahorrada", "Frac_ahorro", "=C18/C19", "%", "Porcentaje de potencia diésel reemplazada"),
        ("Consumo Específico de Combustible (SFOC)", "SFOC", 165.0, "g/kWh", "Consumo motor marino VLSFO"),
        ("Ahorro de Combustible Diario", "Fuel_day_ton", "=(C18*C21*24)/1000000", "t/día", "Toneladas de combustible ahorradas por día"),
        ("Días de Navegación por Año", "Days_year", 260.0, "días", "Días efectivos en alta mar al año"),
        ("Ahorro de Combustible Anual", "Fuel_year_ton", "=C22*C23", "t/año", "Toneladas de fuel ahorradas anualmente"),
        ("Precio del Combustible Marino (VLSFO)", "Price_fuel", 650.0, "$/ton", "Precio medio de búnker por tonelada"),
        ("Ahorro Financiero Anual", "Cost_savings_yr", "=C24*C25", "$/año", "Ahorro directo en combustible por año"),
        ("Factor de Emisión de CO2", "EF_CO2", 3.114, "t CO2/t fuel", "Factor OMI para fuelóleo marino"),
        ("Reducción de Emisiones CO2 Anual", "CO2_reduction_yr", "=C24*C27", "t CO2/año", "Huella de carbono eliminada"),
    ]

    for idx, (name, sym, val, unit, desc) in enumerate(flettner_ship_data, 6):
        c1 = ws3.cell(row=idx, column=1, value=name)
        c2 = ws3.cell(row=idx, column=2, value=sym)
        c3 = ws3.cell(row=idx, column=3, value=val)
        c4 = ws3.cell(row=idx, column=4, value=unit)
        c5 = ws3.cell(row=idx, column=5, value=desc)

        c1.font = font_data
        c2.font = font_bold
        c3.font = font_bold if str(val).startswith("=") else font_data
        c4.font = font_italic
        c5.font = font_data

        c1.border = thin_border
        c2.border = thin_border
        c3.border = thin_border
        c4.border = thin_border
        c5.border = thin_border

        if str(val).startswith("="):
            c3.fill = fill_highlight
        elif idx % 2 == 0:
            for cell in (c1, c2, c3, c4, c5):
                cell.fill = fill_zebra

        if sym in ["Cost_savings_yr"]:
            c3.number_format = "$#,##0"
        elif sym in ["P_prop_kW", "P_engine_MCR", "Fuel_year_ton", "CO2_reduction_yr", "L_total_kN"]:
            c3.number_format = "#,##0.0"
        elif sym in ["Fuel_day_ton", "CL_ship", "alpha_target", "V_ship_ms"]:
            c3.number_format = "#,##0.00"
        elif sym == "Frac_ahorro":
            c3.number_format = "0.0%"

    # =========================================================================
    # SHEET 4: Distribucion_Presion_Cp
    # =========================================================================
    ws4 = wb.create_sheet(title="Distribucion_Presion_Cp")
    ws4.views.sheetView[0].showGridLines = True

    ws4["A1"] = "DISTRIBUCIÓN DEL COEFICIENTE DE PRESIÓN SUPERFICIAL CP(THETA)"
    ws4["A1"].font = font_section
    ws4["A2"] = "Cp(theta) = 1 - (-2*sin(theta) - alpha)^2"
    ws4["A2"].font = font_italic

    headers4 = ["Ángulo Theta (°)", "Theta (rad)", "Cp (alpha=0.0 Estático)", "Cp (alpha=1.0)", "Cp (alpha=2.0 Crítico)", "Cp (alpha=3.0 Supercrítico)"]
    for col_idx, h in enumerate(headers4, 1):
        cell = ws4.cell(row=4, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws4.row_dimensions[4].height = 24

    for r_idx, deg in enumerate(range(0, 361, 10), 5):
        # A: deg
        ws4.cell(row=r_idx, column=1, value=deg)
        # B: rad
        ws4.cell(row=r_idx, column=2, value=f"=RADIANS(A{r_idx})")
        # C: alpha = 0.0
        ws4.cell(row=r_idx, column=3, value=f"=1-(-2*SIN(B{r_idx})-0.0)^2")
        # D: alpha = 1.0
        ws4.cell(row=r_idx, column=4, value=f"=1-(-2*SIN(B{r_idx})-1.0)^2")
        # E: alpha = 2.0
        ws4.cell(row=r_idx, column=5, value=f"=1-(-2*SIN(B{r_idx})-2.0)^2")
        # F: alpha = 3.0
        ws4.cell(row=r_idx, column=6, value=f"=1-(-2*SIN(B{r_idx})-3.0)^2")

        for c_idx in range(1, 7):
            c = ws4.cell(row=r_idx, column=c_idx)
            c.font = font_data
            c.border = thin_border
            if r_idx % 2 == 0:
                c.fill = fill_zebra

        ws4.cell(row=r_idx, column=1).number_format = "0"
        ws4.cell(row=r_idx, column=2).number_format = "0.000"
        ws4.cell(row=r_idx, column=3).number_format = "0.00"
        ws4.cell(row=r_idx, column=4).number_format = "0.00"
        ws4.cell(row=r_idx, column=5).number_format = "0.00"
        ws4.cell(row=r_idx, column=6).number_format = "0.00"

    # Auto-adjust column widths for all sheets
    for ws in wb.worksheets:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = str(cell.value or "")
                if val.startswith("="):
                    max_len = max(max_len, 14)
                else:
                    max_len = max(max_len, len(val))
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    wb.save(output_path)
    return output_path
