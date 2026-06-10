"""exportador.py
Módulo de exportación de reportes.
Soporta: CSV (datos completos), TXT (resumen métricas), PNG (gráficas).
"""
import os
import datetime
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # no necesita pantalla para guardar PNG
import matplotlib.pyplot as plt
from typing import Optional

from exceptions import ExportacionError


def _timestamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def exportar_csv(df: pd.DataFrame, carpeta: str = ".") -> str:
    """Guarda el DataFrame completo como CSV.
    Retorna la ruta del archivo generado."""
    if df.empty:
        raise ExportacionError("No hay datos para exportar.", "DataFrame vacío.")
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"reporte_ventas_{_timestamp()}.csv")
    try:
        df.to_csv(ruta, index=False, encoding="utf-8-sig")
    except OSError as e:
        raise ExportacionError("No se pudo guardar el CSV.", str(e))
    return ruta


def exportar_txt(resumen: dict, carpeta: str = ".") -> str:
    """Guarda las métricas del Analizador como un reporte de texto."""
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"resumen_metricas_{_timestamp()}.txt")
    lineas = [
        "=" * 60,
        f"  REPORTE DE MÉTRICAS DE VENTAS",
        f"  Generado: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        "=" * 60,
        "",
    ]

    def _serie(label: str, s):
        lineas.append(f"\n{label}")
        lineas.append("-" * 40)
        if isinstance(s, pd.Series) and not s.empty:
            for k, v in s.items():
                try:
                    lineas.append(f"  {str(k):30s}  ${float(v):>12,.2f}")
                except (ValueError, TypeError):
                    lineas.append(f"  {str(k):30s}  {v}")
        elif isinstance(s, dict):
            for k, v in s.items():
                lineas.append(f"  {str(k):30s}  {v}")

    stats = resumen.get("estadisticas_precio", {})
    if stats:
        lineas += [
            f"  Total ventas:           ${stats.get('total', 0):,.2f}",
            f"  Ticket promedio:        ${stats.get('media', 0):,.2f}",
            f"  Mediana:                ${stats.get('mediana', 0):,.2f}",
            f"  Desv. estándar:         ${stats.get('std', 0):,.2f}",
            f"  Mín / Máx:              ${stats.get('min', 0):,.2f} / ${stats.get('max', 0):,.2f}",
            f"  IQR:                    ${stats.get('rango_iqr', 0):,.2f}",
        ]

    desc = resumen.get("uso_descuentos", {})
    if desc:
        lineas += [
            "",
            f"  % ventas con descuento: {desc.get('pct_con_descuento', 0)}%",
            f"  Ticket c/ descuento:    ${desc.get('ticket_con_descuento', 0):,.2f}",
            f"  Ticket s/ descuento:    ${desc.get('ticket_sin_descuento', 0):,.2f}",
        ]

    fid = resumen.get("fidelizacion", {})
    if fid:
        lineas += [
            "",
            f"  % clientes recurrentes: {fid.get('pct_recurrentes', 0)}%",
            f"  Ticket recurrente:      ${fid.get('ticket_recurrente', 0):,.2f}",
            f"  Ticket nuevo:           ${fid.get('ticket_nuevo', 0):,.2f}",
        ]

    for key, label in [
        ("ventas_por_categoria",   "VENTAS POR CATEGORÍA"),
        ("ventas_por_temporada",   "VENTAS POR TEMPORADA"),
        ("ventas_por_genero",      "VENTAS POR GÉNERO"),
        ("ventas_por_metodo_pago", "VENTAS POR MÉTODO DE PAGO"),
        ("top_ubicaciones",        "TOP 10 UBICACIONES"),
        ("top_productos_ingreso",  "TOP 10 PRODUCTOS POR INGRESO"),
    ]:
        if key in resumen:
            _serie(label, resumen[key])

    lineas.append("\n" + "=" * 60)

    try:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("\n".join(lineas))
    except OSError as e:
        raise ExportacionError("No se pudo guardar el TXT.", str(e))
    return ruta


def exportar_grafica_png(fig, nombre_base: str, carpeta: str = ".") -> str:
    """Guarda una figura matplotlib como PNG de alta resolución.
    Retorna la ruta del archivo."""
    os.makedirs(carpeta, exist_ok=True)
    nombre = f"{nombre_base}_{_timestamp()}.png"
    ruta = os.path.join(carpeta, nombre)
    try:
        fig.savefig(ruta, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
    except Exception as e:
        raise ExportacionError("No se pudo guardar la gráfica.", str(e))
    return ruta


def exportar_todas_graficas(figuras: dict, carpeta: str = ".") -> list[str]:
    """Recibe un dict {nombre: figura} y exporta cada una como PNG.
    Retorna la lista de rutas generadas."""
    rutas = []
    for nombre, fig in figuras.items():
        ruta = exportar_grafica_png(fig, nombre, carpeta)
        rutas.append(ruta)
    return rutas
