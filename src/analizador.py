"""analizador.py
Clase Analizador — calcula métricas sobre el DataFrame de ventas.
Usa pandas y numpy para los cálculos.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any


class Analizador:
    """Recibe el DataFrame del SistemaDeVentas y calcula métricas.

    Columnas esperadas: ['producto', 'categoria', 'cantidad',
                         'precio_unitario', 'total', 'temporada']
    """

    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Analizador requiere un pandas.DataFrame.")
        self.df = df.copy()
        # Validar que estén las columnas necesarias
        required = {"producto", "categoria", "cantidad", "precio_unitario", "total", "temporada"}
        missing = required - set(self.df.columns)
        if missing:
            raise ValueError(f"Faltan columnas requeridas en el DataFrame: {missing}")

    # ── Métricas generales ────────────────────────────────────────

    def total_ventas(self) -> float:
        """Suma total de todas las ventas."""
        return float(self.df["total"].sum()) if not self.df.empty else 0.0

    def producto_mas_vendido(self) -> pd.Series:
        """Producto con más unidades vendidas (groupby + sum)."""
        grouped = self.df.groupby("producto")["cantidad"].sum().sort_values(ascending=False)
        return grouped.head(1)

    def producto_menos_demanda(self) -> pd.Series:
        """Producto con menos unidades vendidas."""
        grouped = self.df.groupby("producto")["cantidad"].sum().sort_values(ascending=True)
        return grouped.head(1)

    def ingreso_promedio_por_venta(self) -> float:
        """Ingreso promedio por venta usando numpy.mean."""
        return float(np.mean(self.df["total"])) if not self.df.empty else 0.0

    def ingreso_promedio_por_producto(self) -> pd.Series:
        """Ingreso promedio agrupado por producto."""
        return self.df.groupby("producto")["total"].mean().sort_values(ascending=False)

    # ── Métricas por categoría ────────────────────────────────────

    def ventas_por_categoria(self) -> pd.Series:
        """Total de dinero vendido por categoría."""
        return self.df.groupby("categoria")["total"].sum().sort_values(ascending=False)

    def unidades_por_categoria(self) -> pd.Series:
        """Unidades vendidas por categoría."""
        return self.df.groupby("categoria")["cantidad"].sum().sort_values(ascending=False)

    # ── Métricas por temporada ────────────────────────────────────

    def ventas_por_temporada(self) -> pd.Series:
        """Total de ventas agrupado por temporada (Season)."""
        return self.df.groupby("temporada")["total"].sum().sort_values(ascending=False)

    # ── Resumen general ───────────────────────────────────────────

    def resumen_general(self, imprimir: bool = True) -> Dict[str, Any]:
        total = self.total_ventas()
        mas = self.producto_mas_vendido()
        menos = self.producto_menos_demanda()
        prom_venta = self.ingreso_promedio_por_venta()
        prom_producto = self.ingreso_promedio_por_producto()

        resumen = {
            "total_ventas":                total,
            "producto_mas_vendido":        mas,
            "producto_menos_demandado":    menos,
            "ingreso_promedio_por_venta":  prom_venta,
            "ingreso_promedio_por_producto": prom_producto,
            "ventas_por_categoria":        self.ventas_por_categoria(),
            "ventas_por_temporada":        self.ventas_por_temporada(),
            "unidades_por_categoria":      self.unidades_por_categoria(),
        }

        if imprimir:
            print(f"Total ventas: ${total:,.2f}")
            if not mas.empty:
                print(f"Producto más vendido: {mas.index[0]} ({int(mas.iloc[0])} unidades)")
            if not menos.empty:
                print(f"Producto menos demandado: {menos.index[0]} ({int(menos.iloc[0])} unidades)")
            print(f"Ingreso promedio por venta: ${prom_venta:,.2f}")
            print("\nVentas por categoría:")
            print(self.ventas_por_categoria().to_string())
            print("\nVentas por temporada:")
            print(self.ventas_por_temporada().to_string())

        return resumen
