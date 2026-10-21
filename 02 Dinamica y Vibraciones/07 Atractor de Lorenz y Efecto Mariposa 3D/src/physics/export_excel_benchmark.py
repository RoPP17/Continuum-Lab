"""
Continuum Lab - Dynamic Excel Benchmark Generator for 3D Lorenz Strange Attractor
Module: 02 Dinamica y Vibraciones / 07 Atractor de Lorenz y Efecto Mariposa 3D
File: src/physics/export_excel_benchmark.py

Generates a professional, formula-driven Excel benchmark model (.xlsx):
  - Sheet 1: Parametros_Invariantes_Lorenz (Canonical parameters, Hopf bifurcation threshold,
             Fixed points C_±, Liouville volume contraction, Lyapunov spectrum & Kaplan-Yorke dimension)
  - Sheet 2: Divergencia_Lyapunov_1963 (Dynamic exponential divergence model |Δr(t)| = Δ₀ exp(λ₁ t)
             vs saturation diameter of the strange attractor)
"""

from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def create_lorenz_excel_benchmark(output_path: str) -> str:
    wb = openpyxl.Workbook()

    # Professional Typography (Arial per xlsx skill guidelines + Continuum Lab dark cybernetic theme)
    font_title = Font(name="Arial", size=15, bold=True, color="00F0FF")
    font_subtitle = Font(name="Arial", size=10, italic=True, color="94A3B8")
    font_sec_hdr = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    font_tbl_hdr = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    font_input = Font(name="Arial", size=10, bold=True, color="38BDF8")   # Distinct blue for inputs
    font_formula = Font(name="Arial", size=10, color="E2E8F0")            # Formula cells
    font_kpi_lbl = Font(name="Arial", size=8, bold=True, color="94A3B8")
    font_kpi_val = Font(name="Arial", size=13, bold=True, color="00F0FF")

    # Fills
    fill_hdr = PatternFill(start_color="10172A", end_color="10172A", fill_type="solid")
    fill_sec = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    fill_th = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    fill_zebra_1 = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    fill_zebra_2 = PatternFill(start_color="141E33", end_color="141E33", fill_type="solid")
    fill_kpi = PatternFill(start_color="111C2E", end_color="111C2E", fill_type="solid")

    # Borders
    thin_side = Side(style="thin", color="334155")
    tbl_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")

    # =========================================================================
    # SHEET 1: PARAMETROS E INVARIANTES TOPOLOGICOS DE LORENZ (1963)
    # =========================================================================
    ws1 = wb.active
    ws1.title = "Parametros_Invariantes_Lorenz"
    ws1.views.sheetView[0].showGridLines = True

    ws1.merge_cells("A1:F1")
    ws1["A1"] = "CONTINUUM LAB // ATRACTOR EXTRAÑO DE LORENZ 3D Y EFECTO MARIPOSA (1963)"
    ws1["A1"].font = font_title
    ws1["A1"].fill = fill_hdr
    ws1["A1"].alignment = align_left

    ws1.merge_cells("A2:F2")
    ws1["A2"] = "Convección Atmosférica de Rayleigh-Bénard, Contracción de Liouville y Dimensión Fractal de Kaplan-Yorke"
    ws1["A2"].font = font_subtitle
    ws1["A2"].fill = fill_hdr
    ws1["A2"].alignment = align_left
    ws1.row_dimensions[1].height = 25
    ws1.row_dimensions[2].height = 18

    # KPI Summary Cards (Rows 4-5)
    cards = [
        ("A4", "B4", "A5", "B5", "DIVERGENCIA DE LIOUVILLE (∇·F)", "=D12", '0.0000 "s⁻¹"'),
        ("C4", "D4", "C5", "D5", "DIMENSIÓN FRACTAL D_KY", "=D21", "0.0000"),
        ("E4", "E4", "E5", "E5", "UMBRAL HOPF CRÍTICO ρ_H", "=D13", "0.0000"),
        ("F4", "F4", "F5", "F5", "HORIZONTE DE LYAPUNOV T_L", "=D22", '0.0000 "s"'),
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

    # Section 1: Parámetros Físicos Adimensionales y Bifurcación
    ws1.merge_cells("A7:F7")
    ws1["A7"] = "1. PARÁMETROS CANÓNICOS DE CONVECCIÓN Y PUNTOS FIJOS DE EQUILIBRIO (C_±)"
    ws1["A7"].font = font_sec_hdr
    ws1["A7"].fill = fill_sec
    ws1.row_dimensions[7].height = 20

    hdrs_1 = ["Parámetro / Invariante", "Símbolo", "Expresión / Fuente", "Valor", "Unidad", "Significado Físico (Lorenz 1963)"]
    for col_idx, h in enumerate(hdrs_1, start=1):
        c = ws1.cell(row=8, column=col_idx, value=h)
        c.font = font_tbl_hdr
        c.fill = fill_th
        c.alignment = align_center

    rows_1 = [
        ("Número de Prandtl", "σ", "Input Canónico (Lorenz 1963)", 10.0, "adim", "Razón viscosidad cinemática / difusividad térmica", True, "0.0000"),
        ("Número de Rayleigh Normalizado", "ρ", "Input Canónico (Supercrítico)", 28.0, "adim", "Gradiente térmico vertical impulsando convección", True, "0.0000"),
        ("Factor Geométrico de Celda", "β", "=8/3", "=8/3", "adim", "Geometría espacial del rollo convectivo", False, "0.0000"),
        ("Divergencia del Campo Vectorial", "∇·F", "=-(σ + 1 + β)", "=-(D9+1+D11)", "s⁻¹", "Contracción exponencial del volumen de fases (Liouville)", False, "0.0000"),
        ("Rayleigh Crítico de Bifurcación de Hopf", "ρ_H", "=σ(σ+β+3)/(σ-β-1)", "=D9*(D9+D11+3)/(D9-D11-1)", "adim", "Límite donde los puntos fijos C_± pierden estabilidad", False, "0.0000"),
        ("Coordenada X,Y de Centros de Ala C_±", "x_c, y_c", "=SQRT(β*(ρ-1))", "=SQRT(D11*(D10-1))", "adim", "Centros de rotación de las dos alas de la mariposa", False, "0.0000"),
        ("Coordenada Z de Centros de Ala C_±", "z_c", "=ρ - 1", "=D10-1", "adim", "Altura convectiva estacionaria de los lóbulos", False, "0.0000"),
    ]

    for idx, (p_name, p_sym, p_expr, p_val, p_unit, p_desc, is_inp, n_fmt) in enumerate(rows_1, start=9):
        ws1.cell(row=idx, column=1, value=p_name).font = font_formula
        ws1.cell(row=idx, column=2, value=p_sym).font = font_formula
        ws1.cell(row=idx, column=2).alignment = align_center
        ws1.cell(row=idx, column=3, value=p_expr).font = font_subtitle

        c_v = ws1.cell(row=idx, column=4, value=p_val)
        c_v.font = font_input if is_inp else font_formula
        c_v.number_format = n_fmt
        c_v.alignment = align_right

        ws1.cell(row=idx, column=5, value=p_unit).font = font_formula
        ws1.cell(row=idx, column=5).alignment = align_center
        ws1.cell(row=idx, column=6, value=p_desc).font = font_subtitle

        fill = fill_zebra_1 if idx % 2 == 1 else fill_zebra_2
        for col_i in range(1, 7):
            ws1.cell(row=idx, column=col_i).fill = fill
            ws1.cell(row=idx, column=col_i).border = tbl_border

    # Section 2: Espectro de Exponentes de Lyapunov y Geometría Fractal
    ws1.merge_cells("A17:F17")
    ws1["A17"] = "2. ESPECTRO DE LYAPUNOV Y DIMENSIÓN FRACTAL DE KAPLAN-YORKE (ATRACTOR EXTRAÑO)"
    ws1["A17"].font = font_sec_hdr
    ws1["A17"].fill = fill_sec
    ws1.row_dimensions[17].height = 20

    rows_2 = [
        ("Exponente de Lyapunov Máximo", "λ₁", "Integración Variacional QR", 0.9056, "s⁻¹", "Estiramiento exponencial (Caos determinista λ₁ > 0)", True, "0.0000"),
        ("Exponente de Lyapunov Central", "λ₂", "Invariancia Temporal Autónoma", 0.0, "s⁻¹", "Dirección tangente al flujo de la trayectoria", True, "0.0000"),
        ("Exponente de Lyapunov de Contracción", "λ₃", "= ∇·F - λ₁ - λ₂", "=D12-D18-D19", "s⁻¹", "Plegado hiper-disipativo hacia la variedad fractal", False, "0.0000"),
        ("Dimensión Fractal de Kaplan-Yorke", "D_KY", "= 2 + (λ₁ + λ₂)/|λ₃|", "=2+(D18+D19)/ABS(D20)", "dim", "Geometría intermedia entre superficie 2D y volumen 3D", False, "0.0000"),
        ("Tiempo de E-Folding de Lyapunov", "T_L", "= 1 / λ₁", "=1/D18", "s", "Escala temporal en que el error se multiplica por e (2.718x)", False, "0.0000"),
        ("Perturbación de Redondeo (Lorenz 1963)", "Δ₀", "0.506127 vs 0.506000", 0.000127, "adim", "Truncamiento de 6 a 3 decimales en Royal McBee LGP-30", True, "0.000000"),
        ("Diámetro de Saturación del Atractor", "D_max", "= 4 * SQRT(β*(ρ-1))", "=4*D14", "adim", "Distancia máxima entre extremos de las dos alas C₋ y C₊", False, "0.0000"),
    ]

    for idx, (p_name, p_sym, p_expr, p_val, p_unit, p_desc, is_inp, n_fmt) in enumerate(rows_2, start=18):
        ws1.cell(row=idx, column=1, value=p_name).font = font_formula
        ws1.cell(row=idx, column=2, value=p_sym).font = font_formula
        ws1.cell(row=idx, column=2).alignment = align_center
        ws1.cell(row=idx, column=3, value=p_expr).font = font_subtitle

        c_v = ws1.cell(row=idx, column=4, value=p_val)
        c_v.font = font_input if is_inp else font_formula
        c_v.number_format = n_fmt
        c_v.alignment = align_right

        ws1.cell(row=idx, column=5, value=p_unit).font = font_formula
        ws1.cell(row=idx, column=5).alignment = align_center
        ws1.cell(row=idx, column=6, value=p_desc).font = font_subtitle

        fill = fill_zebra_1 if idx % 2 == 1 else fill_zebra_2
        for col_i in range(1, 7):
            ws1.cell(row=idx, column=col_i).fill = fill
            ws1.cell(row=idx, column=col_i).border = tbl_border

    # =========================================================================
    # SHEET 2: MODELO DINAMICO DE DIVERGENCIA Y CONTRACCION DE FASES
    # =========================================================================
    ws2 = wb.create_sheet(title="Divergencia_Lyapunov_1963")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:F1")
    ws2["A1"] = "EVOLUCIÓN TEMPORAL DEL EFECTO MARIPOSA Y CONTRACCIÓN DE VOLUMEN DE LIOUVILLE"
    ws2["A1"].font = font_title
    ws2["A1"].fill = fill_hdr
    ws2["A1"].alignment = align_left

    ws2.merge_cells("A2:F2")
    ws2["A2"] = "Crecimiento exponencial de la perturbación |Δr(t)| = MIN(D_max, Δ₀·e^(λ₁·t)) vs Contracción V(t)/V₀ = e^(∇·F·t)"
    ws2["A2"].font = font_subtitle
    ws2["A2"].fill = fill_hdr
    ws2["A2"].alignment = align_left
    ws2.row_dimensions[1].height = 25
    ws2.row_dimensions[2].height = 18

    hdrs_t = [
        "Tiempo t (s)",
        "Factor Lyapunov e^(λ₁·t)",
        "Divergencia Lineal Δ₀·e^(λ₁·t)",
        "Divergencia Saturada |Δr(t)|",
        "Pérdida Predictibilidad (%)",
        "Volumen de Fases V(t)/V₀"
    ]
    for col_idx, h in enumerate(hdrs_t, start=1):
        c = ws2.cell(row=4, column=col_idx, value=h)
        c.font = font_tbl_hdr
        c.fill = fill_th
        c.alignment = align_center

    for i in range(19):
        r_idx = 5 + i
        t_val = float(i)
        c_t = ws2.cell(row=r_idx, column=1, value=t_val)
        c_t.font = font_input
        c_t.number_format = "0.0"
        c_t.alignment = align_center

        # Col 2: EXP(λ₁ * t)
        c_exp = ws2.cell(row=r_idx, column=2, value=f"=EXP(Parametros_Invariantes_Lorenz!$D$18 * A{r_idx})")
        c_exp.font = font_formula
        c_exp.number_format = "#,##0.00"

        # Col 3: Δ₀ * EXP(λ₁ * t)
        c_lin = ws2.cell(row=r_idx, column=3, value=f"=Parametros_Invariantes_Lorenz!$D$23 * B{r_idx}")
        c_lin.font = font_formula
        c_lin.number_format = "0.000000"

        # Col 4: MIN(D_max, Δ₀ * EXP(λ₁ * t))
        c_sat = ws2.cell(row=r_idx, column=4, value=f"=MIN(Parametros_Invariantes_Lorenz!$D$24, C{r_idx})")
        c_sat.font = font_formula
        c_sat.number_format = "0.0000"

        # Col 5: Predictability Loss Ratio = D{r_idx} / D_max (formatted as 0.0%)
        c_pct = ws2.cell(row=r_idx, column=5, value=f"=D{r_idx}/Parametros_Invariantes_Lorenz!$D$24")
        c_pct.font = font_formula
        c_pct.number_format = "0.0%"

        # Col 6: Phase Volume Ratio V(t)/V0 = EXP(∇·F * t)
        c_vol = ws2.cell(row=r_idx, column=6, value=f"=EXP(Parametros_Invariantes_Lorenz!$D$12 * A{r_idx})")
        c_vol.font = font_formula
        c_vol.number_format = "0.00E+00"

        fill = fill_zebra_1 if r_idx % 2 == 1 else fill_zebra_2
        for col_i in range(1, 7):
            ws2.cell(row=r_idx, column=col_i).fill = fill
            ws2.cell(row=r_idx, column=col_i).border = tbl_border

    # Summary Row at Row 24
    ws2.cell(row=24, column=1, value="PROMEDIO / MÁX").font = font_tbl_hdr
    ws2.cell(row=24, column=2, value="=MAX(B5:B23)").font = font_tbl_hdr
    ws2.cell(row=24, column=2).number_format = "#,##0.00"
    ws2.cell(row=24, column=3, value="=MAX(C5:C23)").font = font_tbl_hdr
    ws2.cell(row=24, column=3).number_format = "0.0000"
    ws2.cell(row=24, column=4, value="=MAX(D5:D23)").font = font_tbl_hdr
    ws2.cell(row=24, column=4).number_format = "0.0000"
    ws2.cell(row=24, column=5, value="=AVERAGE(E5:E23)").font = font_tbl_hdr
    ws2.cell(row=24, column=5).number_format = "0.0%"
    ws2.cell(row=24, column=6, value="=MIN(F5:F23)").font = font_tbl_hdr
    ws2.cell(row=24, column=6).number_format = "0.00E+00"
    for col_i in range(1, 7):
        ws2.cell(row=24, column=col_i).fill = fill_sec
        ws2.cell(row=24, column=col_i).border = tbl_border

    # Auto-adjust column widths
    for ws in [ws1, ws2]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                if not val_str.startswith("="):
                    max_len = max(max_len, len(val_str))
            ws.column_dimensions[col_letter].width = max(max_len + 4, 15)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    print(f"[OK] Dynamic Lorenz Excel Benchmark saved to: {output_path}")
    return output_path
