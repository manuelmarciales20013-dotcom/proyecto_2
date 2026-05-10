import pandas as pd
from typing import Dict, Any


class Analizador:
    """Analizador de métricas a partir de un DataFrame de ventas.

    Se espera un DataFrame con columnas: ['producto','cantidad','precio_unitario','total']
    """

    def __init__(self, df: pd.DataFrame):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Analizador requiere un pandas.DataFrame.")
        self.df = df.copy()
        required = {"producto", "cantidad", "precio_unitario", "total"}
        missing = required - set(self.df.columns)
        if missing:
            raise ValueError(f"Faltan columnas requeridas en el DataFrame: {missing}")

    def total_ventas(self) -> float:
        return float(self.df["total"].sum()) if not self.df.empty else 0.0

    def producto_mas_vendido(self) -> pd.Series:
        grouped = self.df.groupby("producto")["cantidad"].sum().sort_values(ascending=False)
        return grouped.head(1)

    def producto_menos_demanda(self) -> pd.Series:
        grouped = self.df.groupby("producto")["cantidad"].sum().sort_values(ascending=True)
        return grouped.head(1)

    def ingreso_promedio_por_venta(self) -> float:
        return float(self.df["total"].mean()) if not self.df.empty else 0.0

    def ingreso_promedio_por_producto(self) -> pd.Series:
        return self.df.groupby("producto")["total"].mean().sort_values(ascending=False)

    def resumen_general(self, imprimir: bool = True) -> Dict[str, Any]:
        total = self.total_ventas()
        mas = self.producto_mas_vendido()
        menos = self.producto_menos_demanda()
        ingreso_prom_prom = self.ingreso_promedio_por_venta()
        ingreso_por_producto = self.ingreso_promedio_por_producto()

        resumen = {
            "total_ventas": total,
            "producto_mas_vendido": mas,
            "producto_menos_demandado": menos,
            "ingreso_promedio_por_venta": ingreso_prom_prom,
            "ingreso_promedio_por_producto": ingreso_por_producto,
        }

        if imprimir:
            print(f"Total ventas: ${total:,.2f}")
            if not mas.empty:
                idx = mas.index[0]
                print(f"Producto más vendido: {idx} ({int(mas.iloc[0])} unidades)")
            if not menos.empty:
                idx2 = menos.index[0]
                print(f"Producto con menos demanda: {idx2} ({int(menos.iloc[0])} unidades)")
            print(f"Ingreso promedio por venta: ${ingreso_prom_prom:,.2f}")
            print("Ingreso promedio por producto:")
            print(ingreso_por_producto.to_string())

        return resumen
