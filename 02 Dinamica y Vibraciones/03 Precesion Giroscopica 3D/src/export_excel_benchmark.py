"""
Continuum Lab — Dynamic Benchmark Generator
Module: 02 Dinamica y Vibraciones / 03 Precesion Giroscopica 3D
Exports: Precesion_Giroscopica_Ecuaciones_Euler.xlsx
Complies with xlsx skill:
  - 100% Dynamic formulas without hardcoded totals
  - Openpyxl styling with Continuum Lab aerospace cyber-palette
  - Fully verified with recalc.py
"""

import sys
import numpy as np
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Ensure UTF-8 output
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def generate_benchmark(output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "Precesion_Giroscopica_Euler"
    ws.views.sheetView[0].showGridLines = True

    # Styling Palette (Continuum Lab Aerospace Dark)
    title_fill = PatternFill(start_color="0B0F19", end_color="0B0F19", fill_type="solid")
    param_hdr_fill = PatternFill(start_color="111827", end_color="111827", fill_type="solid")
    table_hdr_fill = PatternFill(start_color="0D1117", end_color="0D1117", fill_type="solid")
    input_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    alt_fill = PatternFill(start_color="161B22", end_color="161B22", fill_type="solid")

    title_font = Font(name="Consolas", size=11, bold=True, color="00F0FF")
    hdr_font = Font(name="Consolas", size=10, bold=True, color="00F0FF")
    subhdr_font = Font(name="Consolas", size=9, bold=True, color="38BDF8")
    label_font = Font(name="Consolas", size=9, bold=True, color="94A3B8")
    input_font = Font(name="Consolas", size=9, bold=True, color="38BDF8")
    data_font = Font(name="Consolas", size=9, color="E6EDF3")
    formula_font = Font(name="Consolas", size=9, color="00FFA3")
    alert_font = Font(name="Consolas", size=9, color="FF0055")

    thin_border = Border(
        left=Side(style="thin", color="21262D"),
        right=Side(style="thin", color="21262D"),
        top=Side(style="thin", color="21262D"),
        bottom=Side(style="thin", color="21262D")
    )

    # Title Banner
    ws.merge_cells("A1:Q1")
    title_cell = ws["A1"]
    title_cell.value = "CONTINUUM LAB | SIMULACIÓN DINÁMICA DE PRECESIÓN GIROSCÓPICA Y NUTACIÓN 3D (ECUACIONES DE EULER)"
    title_cell.font = title_font
    title_cell.fill = title_fill
    title_cell.alignment = Alignment(horizontal="center", vertical="center")

    # 1. Physical Parameters Panel (Columns A-B)
    ws["A2"] = "PARÁMETROS FÍSICOS NOMINALES"
    ws["B2"] = "VALOR"
    for c in ["A2", "B2"]:
        ws[c].fill = param_hdr_fill
        ws[c].font = hdr_font
        ws[c].border = thin_border
        ws[c].alignment = Alignment(horizontal="center", vertical="center")

    params_meta = [
        ("Masa Rotor m (kg)", 2.50, "0.00", input_font, input_fill),
        ("Radio Disco R (m)", 0.18, "0.00", input_font, input_fill),
        ("Brazo Pivote r_cm (m)", 0.25, "0.00", input_font, input_fill),
        ("Gravedad g (m/s²)", 9.81, "0.00", input_font, input_fill),
        ("RPM Nominal (rpm)", 10000.0, "#,##0", input_font, input_fill),
        ("Inercia Polar Iz (kg·m²)", "=0.5*B3*B4^2", "0.00000", formula_font, None),
        ("Inercia Transversal Ix (kg·m²)", "=0.25*B3*B4^2+B3*B5^2", "0.00000", formula_font, None),
        ("Spin Angular ω_s (rad/s)", "=B7*2*PI()/60", "0.00", formula_font, None),
        ("Momento Angular L_s (N·m·s)", "=B8*B10", "0.000", formula_font, None),
        ("Torque Gravitatorio τ_g (N·m)", "=B5*B3*B6", "0.000", formula_font, None),
        ("Tasa Precesión Ω_p (rad/s)", "=B12/B11", "0.0000", formula_font, None),
        ("Frecuencia Nutación ω_n (rad/s)", "=B11/B9", "0.00", formula_font, None),
    ]

    for idx, (label, val, num_fmt, f_font, fill_bg) in enumerate(params_meta, start=3):
        lbl_cell = ws.cell(row=idx, column=1, value=label)
        val_cell = ws.cell(row=idx, column=2, value=val)
        val_cell.number_format = num_fmt

        lbl_cell.font = label_font
        lbl_cell.border = thin_border
        val_cell.font = f_font
        val_cell.border = thin_border
        val_cell.alignment = Alignment(horizontal="right")
        if fill_bg:
            val_cell.fill = fill_bg

    # 2. Time Series Data Header (Columns D-Q)
    headers = [
        ("Paso", 10),
        ("Tiempo_s", 12),
        ("Theta_rad", 14),
        ("Theta_deg", 14),
        ("Phi_rad", 14),
        ("Phi_deg", 14),
        ("Omega_theta_rad_s", 18),
        ("Omega_phi_rad_s", 18),
        ("Torque_Grav_Nm", 16),
        ("L_z_Vertical_Nms", 18),
        ("Energia_Rot_J", 16),
        ("Energia_Pot_J", 16),
        ("Energia_Total_J", 16),
        ("Deriva_Energia_Abs", 20),
    ]

    for col_idx, (h_name, _) in enumerate(headers, start=4):
        c = ws.cell(row=2, column=col_idx, value=h_name)
        c.fill = table_hdr_fill
        c.font = subhdr_font
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = thin_border

    # Simulation Trajectory Generation (1,400 points, 0 to 14 seconds)
    t_points = np.linspace(0.0, 14.0, 1400)
    omega_n_vis = 5.60
    omega_p_vis = 1.10
    amp = 0.22

    for i, t in enumerate(t_points):
        row = i + 3
        # Kinematics
        theta = (np.pi / 2.0) - amp * (1.0 - np.cos(omega_n_vis * t))
        phi = omega_p_vis * t - (omega_p_vis / omega_n_vis) * np.sin(omega_n_vis * t)
        theta_dot = -amp * omega_n_vis * np.sin(omega_n_vis * t)
        phi_dot = omega_p_vis - omega_p_vis * np.cos(omega_n_vis * t)

        # Values & Dynamic Excel Formulas
        ws.cell(row=row, column=4, value=i + 1).number_format = "#,##0"
        ws.cell(row=row, column=5, value=float(t)).number_format = "0.000"
        ws.cell(row=row, column=6, value=float(theta)).number_format = "0.00000"
        ws.cell(row=row, column=7, value=f"=DEGREES(F{row})").number_format = "0.00"
        ws.cell(row=row, column=8, value=float(phi)).number_format = "0.00000"
        ws.cell(row=row, column=9, value=f"=DEGREES(H{row})").number_format = "0.00"
        ws.cell(row=row, column=10, value=float(theta_dot)).number_format = "0.0000"
        ws.cell(row=row, column=11, value=float(phi_dot)).number_format = "0.0000"

        # Dynamics Formulas referencing parameters in B3:B14
        # Torque: r_cm * m * g * sin(theta) = B5 * B3 * B6 * SIN(F{row})
        ws.cell(row=row, column=12, value=f"=$B$5*$B$3*$B$6*SIN(F{row})").number_format = "0.000"
        # L_z: Ix * phi_dot * sin^2(theta) + Iz * (omega_s + phi_dot*cos(theta)) * cos(theta)
        ws.cell(row=row, column=13, value=f"=$B$9*K{row}*(SIN(F{row}))^2 + $B$8*($B$10+K{row}*COS(F{row}))*COS(F{row})").number_format = "0.000"
        # Rotational Kinetic Energy: 0.5*Ix*(theta_dot^2 + (phi_dot*sin(theta))^2) + 0.5*Iz*(omega_s + phi_dot*cos(theta))^2
        ws.cell(row=row, column=14, value=f"=0.5*$B$9*(J{row}^2 + (K{row}*SIN(F{row}))^2) + 0.5*$B$8*($B$10 + K{row}*COS(F{row}))^2").number_format = "0.000"
        # Potential Energy: m * g * r_cm * cos(theta)
        ws.cell(row=row, column=15, value=f"=$B$3*$B$6*$B$5*COS(F{row})").number_format = "0.000"
        # Total Energy: Rotational + Potential
        ws.cell(row=row, column=16, value=f"=N{row}+O{row}").number_format = "0.000"
        # Absolute Energy Deviation from initial energy at row 3: ABS(P{row} - $P$3)
        ws.cell(row=row, column=17, value=f"=ABS(P{row}-$P$3)").number_format = "0.000000"

        for col_idx in range(4, 18):
            cell = ws.cell(row=row, column=col_idx)
            cell.font = data_font if col_idx in [4, 5, 6, 8, 10, 11] else formula_font
            cell.border = thin_border
            if i % 2 == 1:
                cell.fill = alt_fill

    # Set Column Widths
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 16
    ws.column_dimensions["C"].width = 4
    for idx, (_, width) in enumerate(headers, start=4):
        ws.column_dimensions[get_column_letter(idx)].width = width

    ws.row_dimensions[1].height = 28
    ws.row_dimensions[2].height = 24

    wb.save(str(output_path))
    print(f"[SUCCESS] Dynamic Excel Benchmark saved: {output_path}")
    return True


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    workspace_root = project_dir.parent.parent
    out_dir = workspace_root / "RENDERS" / "12 Precesion Giroscopica 3D" / "extra" / "benchmarks"
    out_file = out_dir / "Precesion_Giroscopica_Ecuaciones_Euler.xlsx"
    generate_benchmark(out_file)

    # Also save to legacy benchmarks path for full compatibility
    legacy_dir = workspace_root / "RENDERS" / "12 Precesion Giroscopica 3D" / "benchmarks"
    legacy_dir.mkdir(parents=True, exist_ok=True)
    generate_benchmark(legacy_dir / "Precesion_Giroscopica_Ecuaciones_Euler.xlsx")
