"""
Continuum Lab - Dynamic Excel Benchmark Generator
Module: 01 Mecanica de Fluidos / 06 Inestabilidad Rayleigh Taylor
File: src/physics/export_excel_benchmark.py

Strictly adheres to Continuum Lab xlsx skill standards:
  - 100% dynamic uppercase Excel formulas (no hardcoded computed values)
  - Cohesive professional styling (Navy/Cyan Continuum Dark theme)
  - Grid lines enabled explicitly on all sheets
  - Auto-fitted column widths with safety padding
  - Comprehensive linear dispersion, non-linear mixing, and multi-system benchmarks
"""

import os
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def create_rayleigh_taylor_excel_benchmark(output_path: str) -> str:
    """Creates a comprehensive, fully dynamic Excel benchmark for Rayleigh-Taylor instability."""
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # Remove default blank sheet

    # Typography & Colors
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
    # SHEET 1: Parametros_Fisicos
    # =========================================================================
    ws1 = wb.create_sheet(title="Parametros_Fisicos")
    ws1.views.sheetView[0].showGridLines = True

    ws1["A1"] = "CONTINUUM LAB // MECÁNICA DE FLUIDOS AVANZADA"
    ws1["A1"].font = font_section
    ws1["A2"] = "MODELO DE INESTABILIDAD RAYLEIGH-TAYLOR Y PLUMAS GRAVITATORIAS"
    ws1["A2"].font = font_title
    ws1["A3"] = "Parámetros de Interfaz, Gravedad, Dispersión Lineal y Régimen No-Lineal"
    ws1["A3"].font = font_italic

    headers1 = ["Parámetro Físico", "Símbolo", "Valor / Fórmula Dinámica", "Unidad", "Descripción y Base Teórica"]
    for col_idx, h in enumerate(headers1, 1):
        cell = ws1.cell(row=5, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws1.row_dimensions[5].height = 24

    params_data = [
        ("Densidad del Fluido Pesado (Superior)", "rho_2", 1200.0, "kg/m³", "Capa superior inestable sometida a gravedad"),
        ("Densidad del Fluido Ligero (Inferior)", "rho_1", 400.0, "kg/m³", "Capa inferior que soporta el gradiente hidrostático"),
        ("Número de Atwood", "Atwood", "=(C6-C7)/(C6+C7)", "-", "A = (rho_2 - rho_1) / (rho_2 + rho_1)"),
        ("Aceleración de la Gravedad", "g", 9.81, "m/s²", "Vector gravedad vertical descendente"),
        ("Tensión Superficial Interfacial", "sigma", 0.045, "N/m", "Fuerza estabilizadora capilar a altas frecuencias"),
        ("Viscosidad Cinemática Media", "nu", 0.00018, "m²/s", "Difusión de cantidad de movimiento baroclínico"),
        ("Difusividad de Masa", "D", 0.00018, "m²/s", "Difusión de la concentración escalar C(x,y)"),
        ("Espesor Inicial de la Interfaz", "delta_0", 0.030, "m", "Grosor de la capa de transición hiperbólica inicial"),
        ("Número de Onda Capilar Crítico", "k_c", "=SQRT(((C6-C7)*C9)/C10)", "rad/m", "k_c = SQRT((rho_2 - rho_1)*g / sigma)"),
        ("Longitud de Onda Crítica de Corte", "lambda_c", "=(2*PI())/C14", "m", "Longitudes de onda menores a lambda_c son estables"),
        ("Número de Onda de Máximo Crecimiento", "k_max", "=C14/SQRT(3)", "rad/m", "k_max = k_c / SQRT(3)"),
        ("Longitud de Onda Más Inestable", "lambda_max", "=(2*PI())/C16", "m", "Modo dominante en la formación de plumas"),
        ("Tasa Máxima de Crecimiento Lineal", "gamma_max", "=SQRT(C8*C9*C16 - (C10*C16^3)/(C6+C7))", "s⁻¹", "Máxima amplificación exponencial e^(gamma*t)"),
        ("Constante de Mezcla de Dimonte-Schneider", "alpha_mix", 0.06, "-", "Crecimiento cuadrático de la zona de mezcla h(t)"),
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

    # =========================================================================
    # SHEET 2: Dispersion_y_Crecimiento
    # =========================================================================
    ws2 = wb.create_sheet(title="Dispersion_y_Crecimiento")
    ws2.views.sheetView[0].showGridLines = True

    ws2["A1"] = "CONTINUUM LAB // ESPECTRO DE DISPERSIÓN LINEAL DE RAYLEIGH-TAYLOR"
    ws2["A1"].font = font_section
    ws2["A2"] = "Tasa de Crecimiento vs. Número de Onda (Efectos Capilar y Viscoso)"
    ws2["A2"].font = font_title

    headers2 = [
        "Número de Onda k [rad/m]",
        "Longitud de Onda λ [m]",
        "Tasa Inválida (No-Viscosa) γ_inv [s⁻¹]",
        "Tasa con Tensión Superficial γ_cap [s⁻¹]",
        "Tasa Completa (Viscosa-Capilar) γ_visc [s⁻¹]",
        "Tiempo de Duplicación τ [s]",
        "Régimen de Estabilidad"
    ]
    for col_idx, h in enumerate(headers2, 1):
        cell = ws2.cell(row=4, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws2.row_dimensions[4].height = 24

    k_values = [0.2, 0.5, 1.0, 2.0, 3.5, 5.0, 7.5, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 60.0]
    for row_idx, k_val in enumerate(k_values, 5):
        c_k = ws2.cell(row=row_idx, column=1, value=k_val)
        c_lam = ws2.cell(row=row_idx, column=2, value=f"=(2*PI())/A{row_idx}")
        # gamma_inv = SQRT(A * g * k)
        c_ginv = ws2.cell(row=row_idx, column=3, value=f"=SQRT(Parametros_Fisicos!$C$8*Parametros_Fisicos!$C$9*A{row_idx})")
        # gamma_cap = SQRT(MAX(0, A*g*k - (sigma*k^3)/(rho1+rho2)))
        c_gcap = ws2.cell(row=row_idx, column=4, value=(
            f"=SQRT(MAX(0, Parametros_Fisicos!$C$8*Parametros_Fisicos!$C$9*A{row_idx} - "
            f"(Parametros_Fisicos!$C$10*A{row_idx}^3)/(Parametros_Fisicos!$C$6+Parametros_Fisicos!$C$7)))"
        ))
        # gamma_visc = SQRT(MAX(0, D{row_idx}^2 + Parametros_Fisicos!$C$11^2*A{row_idx}^4)) - Parametros_Fisicos!$C$11*A{row_idx}^2
        c_gvisc = ws2.cell(row=row_idx, column=5, value=(
            f"=MAX(0, SQRT(MAX(0, D{row_idx}^2 + (Parametros_Fisicos!$C$11^2)*(A{row_idx}^4))) - "
            f"Parametros_Fisicos!$C$11*(A{row_idx}^2))"
        ))
        # tau = 1 / gamma
        c_tau = ws2.cell(row=row_idx, column=6, value=f"=IF(E{row_idx}>0.001, 1/E{row_idx}, 9999.0)")
        c_reg = ws2.cell(row=row_idx, column=7, value=f'=IF(D{row_idx}>0.001, "INESTABLE // CRECIMIENTO", "ESTABLE // AMORTIGUADO")')

        for cell in (c_k, c_lam, c_ginv, c_gcap, c_gvisc, c_tau, c_reg):
            cell.font = font_data
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="right", vertical="center")
        c_reg.alignment = Alignment(horizontal="center", vertical="center")
        if row_idx % 2 == 0:
            for cell in (c_k, c_lam, c_ginv, c_gcap, c_gvisc, c_tau, c_reg):
                cell.fill = fill_zebra

    # =========================================================================
    # SHEET 3: Evolucion_Temporal
    # =========================================================================
    ws3 = wb.create_sheet(title="Evolucion_Temporal")
    ws3.views.sheetView[0].showGridLines = True

    ws3["A1"] = "CONTINUUM LAB // TRAYECTORIA TEMPORAL Y ZONA DE MEZCLA"
    ws3["A1"].font = font_section
    ws3["A2"] = "Evolución No-Lineal: Penetración de Picos, Ascenso de Burbujas y Ley Cuadrática"
    ws3["A2"].font = font_title

    headers3 = [
        "Tiempo t [s]",
        "Amplitud Lineal η(t) [m]",
        "Velocidad Terminal Burbuja v_b [m/s]",
        "Profundidad de Pico y_spike [m]",
        "Altura de Burbuja y_bubble [m]",
        "Ancho Zona de Mezcla h(t) [m]",
        "Teoría Dimonte α·A·g·t² [m]",
        "Energía Cinética Escalar E_k [J/m]",
        "Fase Fenomenológica"
    ]
    for col_idx, h in enumerate(headers3, 1):
        cell = ws3.cell(row=4, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws3.row_dimensions[4].height = 24

    times = [i * 0.5 for i in range(33)]  # 0.0 to 16.0 s
    for r_idx, t_val in enumerate(times, 5):
        c_t = ws3.cell(row=r_idx, column=1, value=t_val)
        # eta(t) = eta_0 * COSH(gamma * t)
        c_eta = ws3.cell(row=r_idx, column=2, value=f"=Parametros_Fisicos!$C$13*COSH(MIN(15, Parametros_Fisicos!$C$18*A{r_idx}))")
        # v_bubble = 0.23 * SQRT(A * g * lambda_max)
        c_vb = ws3.cell(row=r_idx, column=3, value="=0.23*SQRT(Parametros_Fisicos!$C$8*Parametros_Fisicos!$C$9*Parametros_Fisicos!$C$17)")
        # y_spike(t) = - 0.5 * alpha * A * g * t^2 * (1 + A)
        c_yspike = ws3.cell(row=r_idx, column=4, value=(
            f"=-0.5*Parametros_Fisicos!$C$19*Parametros_Fisicos!$C$8*Parametros_Fisicos!$C$9*(A{r_idx}^2)*(1+Parametros_Fisicos!$C$8)"
        ))
        # y_bubble(t) = 0.5 * alpha * A * g * t^2 * (1 - A)
        c_ybubble = ws3.cell(row=r_idx, column=5, value=(
            f"=0.5*Parametros_Fisicos!$C$19*Parametros_Fisicos!$C$8*Parametros_Fisicos!$C$9*(A{r_idx}^2)*(1-Parametros_Fisicos!$C$8) + C{r_idx}*MIN(A{r_idx}, 2.0)"
        ))
        # h(t) = y_bubble - y_spike
        c_h = ws3.cell(row=r_idx, column=6, value=f"=E{r_idx}-D{r_idx}")
        # h_theory = alpha * A * g * t^2
        c_htheory = ws3.cell(row=r_idx, column=7, value=f"=Parametros_Fisicos!$C$19*Parametros_Fisicos!$C$8*Parametros_Fisicos!$C$9*(A{r_idx}^2)")
        # E_k = 0.5 * rho * (alpha * A * g * t)^2 * h
        c_ek = ws3.cell(row=r_idx, column=8, value=(
            f"=0.5*0.5*(Parametros_Fisicos!$C$6+Parametros_Fisicos!$C$7)*(Parametros_Fisicos!$C$19*Parametros_Fisicos!$C$8*Parametros_Fisicos!$C$9*A{r_idx})^2*F{r_idx}"
        ))
        # Phase text
        c_phase = ws3.cell(row=r_idx, column=9, value=(
            f'=IF(A{r_idx}<3.5, "Lineal: Perturbación", IF(A{r_idx}<8.0, "No-Lineal: Picos y Burbujas", '
            f'IF(A{r_idx}<12.5, "Secundaria: Vórtices Champiñón", "Turbulento: Mezcla Auto-similar")))'
        ))

        for cell in (c_t, c_eta, c_vb, c_yspike, c_ybubble, c_h, c_htheory, c_ek, c_phase):
            cell.font = font_data
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="right", vertical="center")
        c_phase.alignment = Alignment(horizontal="center", vertical="center")
        if r_idx % 2 == 0:
            for cell in (c_t, c_eta, c_vb, c_yspike, c_ybubble, c_h, c_htheory, c_ek, c_phase):
                cell.fill = fill_zebra

    # =========================================================================
    # SHEET 4: Comparativa_Sistemas
    # =========================================================================
    ws4 = wb.create_sheet(title="Comparativa_Sistemas")
    ws4.views.sheetView[0].showGridLines = True

    ws4["A1"] = "CONTINUUM LAB // COMPARATIVA MULTI-SISTEMA DE RAYLEIGH-TAYLOR"
    ws4["A1"].font = font_section
    ws4["A2"] = "Astrosfísica, Fusión Nuclear (ICF), Geofísica e Industria Química"
    ws4["A2"].font = font_title

    headers4 = [
        "Sistema / Aplicación",
        "Densidad Pesada ρ₂ [kg/m³]",
        "Densidad Ligera ρ₁ [kg/m³]",
        "Gravedad g [m/s²]",
        "Atwood Dinámico A",
        "Longitud Escala L [m]",
        "Tasa de Crecimiento γ [s⁻¹]",
        "Tiempo de Duplicación τ [s]",
        "Impacto Físico y Relevancia"
    ]
    for col_idx, h in enumerate(headers4, 1):
        cell = ws4.cell(row=4, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws4.row_dimensions[4].height = 24

    systems_data = [
        ("Agua sobre Aceite (Laboratorio)", 1000.0, 850.0, 9.81, 0.05, "Modo interfacial clásico con tensión superficial"),
        ("Agua sobre Aire (Gotas e Interfaz)", 1000.0, 1.225, 9.81, 0.10, "Colapso de películas descendentes y atomización"),
        ("Fusión Nuclear ICF (NIF Pellet)", 10000.0, 200.0, 1000000000000.0, 0.001, "Aceleración de cápsulas de deuterio-tritio"),
        ("Supernova 1987A (Capa He/H)", 1000.0, 10.0, 500000.0, 1000000000.0, "Expulsión de manto estelar y mezcla de elementos pesados"),
        ("Pluma Volcánica / Piroclástica", 1500.0, 1.2, 9.81, 100.0, "Colapso gravitacional de columnas densas de ceniza"),
        ("Derrame de Petróleo Submarino", 920.0, 1025.0, 9.81, 5.0, "Flotabilidad invertida y plumas de dispersión marina"),
    ]

    for s_idx, (sys_name, rho2, rho1, grav, scale_l, note) in enumerate(systems_data, 5):
        c_name = ws4.cell(row=s_idx, column=1, value=sys_name)
        c_r2 = ws4.cell(row=s_idx, column=2, value=rho2)
        c_r1 = ws4.cell(row=s_idx, column=3, value=rho1)
        c_g = ws4.cell(row=s_idx, column=4, value=grav)
        c_atw = ws4.cell(row=s_idx, column=5, value=f"=ABS((B{s_idx}-C{s_idx})/(B{s_idx}+C{s_idx}))")
        c_l = ws4.cell(row=s_idx, column=6, value=scale_l)
        # gamma = SQRT(A * g * (2*PI() / L))
        c_gam = ws4.cell(row=s_idx, column=7, value=f"=SQRT(E{s_idx}*D{s_idx}*((2*PI())/F{s_idx}))")
        c_tau = ws4.cell(row=s_idx, column=8, value=f"=IF(G{s_idx}>0, 1/G{s_idx}, 9999.0)")
        c_note = ws4.cell(row=s_idx, column=9, value=note)

        for cell in (c_name, c_r2, c_r1, c_g, c_atw, c_l, c_gam, c_tau, c_note):
            cell.font = font_data
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="right", vertical="center")
        c_name.alignment = Alignment(horizontal="left", vertical="center")
        c_note.alignment = Alignment(horizontal="left", vertical="center")

        if s_idx % 2 == 0:
            for cell in (c_name, c_r2, c_r1, c_g, c_atw, c_l, c_gam, c_tau, c_note):
                cell.fill = fill_zebra

    # =========================================================================
    # Auto-fit Column Widths across all sheets
    # =========================================================================
    for ws in [ws1, ws2, ws3, ws4]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = cell.value
                if val is not None:
                    s_val = str(val)
                    if not s_val.startswith("="):
                        max_len = max(max_len, len(s_val))
                    else:
                        max_len = max(max_len, 14)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    wb.save(output_path)
    return output_path
