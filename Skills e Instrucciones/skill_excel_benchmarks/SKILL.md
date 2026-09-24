---
name: excel-benchmarks-dinamicos
description: Automated openpyxl engineering spreadsheet generation with native Excel formulas, zero hardcoded values, professional cybernetic styling, and dynamic statistical models.
---

# Excel Benchmarks Dinámicos (`excel-benchmarks-dinamicos`)

Esta skill estandariza la exportación de modelos cuantitativos en formato `.xlsx` dentro de Continuum Lab.

---

## 1. Principio Fundamental
* **Prohibido el *hardcoding* de resultados calculados:** Todo valor estadístico, promedio, máximo, mínimo, desviación estándar, amplitud, error o porcentaje debe calcularse mediante **fórmulas nativas de Excel** (`=AVERAGE()`, `=MAX()`, `=MIN()`, `=SQRT()`, `=ABS()`, `=COUNT()`).
* La hoja `Telemetry_Data` almacena la serie temporal cruda.
* La hoja `Hydrodynamic_Analysis` referencia dinámicamente el rango mediante fórmulas vivas.

---

## 2. Paleta de Estilo en Spreadsheets
* **Cabeceras:** Relleno `#0D1117`, Fuente Negrita `#00F0FF` (Segoe UI 11pt).
* **Filas pares/impares:** Alternancia con `#161B22` para lectura descansada.
* **Bordes:** Finos de color `#30363D`.
* **Celdas de resultados clave:** Relleno `#1F242C`, fuente blanca negrita, formatos de número explícitos (`0.0000` o `0.00%`).
* **Auto-ajuste de columnas:** Calcular el ancho de cada columna dinámicamente sumando un margen de seguridad de 4 caracteres.
